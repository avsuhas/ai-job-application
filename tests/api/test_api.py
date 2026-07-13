"""API integration tests: full discover → rank → history workflow with the
mock provider and mocked ATS HTTP endpoints. Fixtures live in conftest.py."""

import httpx
import respx

from tests.api.conftest import GREENHOUSE_URL


class TestSystem:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["provider"] == "mock"
        assert body["companies_configured"] == 2

    def test_settings_excludes_secrets(self, client):
        body = client.get("/api/settings").json()
        assert "anthropic_api_key" not in body
        assert body["applications"]["automation_mode"] == "review"


class TestCandidate:
    def test_status_reports_resumes(self, client):
        body = client.get("/api/candidate/status").json()
        assert body["ok"] is True
        assert body["resumes"][0]["id"] == "backend"
        assert "rules" in body["documents"]

    def test_reload_picks_up_new_files(self, client, tmp_path):
        profile = tmp_path / "user_data" / "candidate" / "profile"
        (profile / "publications.md").write_text("New paper")
        body = client.post("/api/candidate/reload").json()
        assert "publications" in body["documents"]


class TestCompanies:
    def test_list_companies_with_detected_ats(self, client):
        body = client.get("/api/companies").json()
        by_id = {c["id"]: c for c in body}
        assert by_id["exampleco"]["detected_ats"] == "greenhouse"
        assert by_id["unsupported"]["detected_ats"] == "unsupported"


class TestSearchWorkflow:
    @respx.mock
    def test_full_search_and_ranking_workflow(self, client, greenhouse_payload):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))

        create = client.post(
            "/api/searches?wait=true",
            json={"filters": {"keywords": ["engineer"]}},
        )
        assert create.status_code == 202
        search_id = create.json()["search_id"]
        assert create.json()["status"] == "complete"

        status = client.get(f"/api/searches/{search_id}").json()
        assert status["job_count"] == 3
        assert status["ranked_count"] == 3
        outcomes = {o["source_id"]: o for o in status["source_outcomes"]}
        assert outcomes["exampleco"]["job_count"] == 3
        assert outcomes["unsupported"]["error"] is not None

        jobs = client.get(f"/api/searches/{search_id}/jobs").json()
        assert jobs["count"] == 3
        scores = [j["score"] for j in jobs["jobs"]]
        assert scores == sorted(scores, reverse=True)
        top = jobs["jobs"][0]
        assert top["match"]["suggested_resume"] == "backend"
        assert "raw" not in top["job"]

    @respx.mock
    def test_search_filters_and_sorting(self, client, greenhouse_payload):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]

        us_only = client.get(
            f"/api/searches/{search_id}/jobs", params={"country": "United States"}
        ).json()
        assert us_only["count"] == 2

        by_title = client.get(
            f"/api/searches/{search_id}/jobs", params={"sort": "title"}
        ).json()
        titles = [j["job"]["title"] for j in by_title["jobs"]]
        assert titles == sorted(titles)

    @respx.mock
    def test_already_applied_jobs_are_hidden(self, client, greenhouse_payload):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        record = {
            "company": "ExampleCo",
            "job_title": "Senior Backend Engineer",
            "job_id": "4001",
            "application_url": "https://boards.greenhouse.io/exampleco/jobs/4001",
        }
        assert client.post("/api/history", json=record).status_code == 201

        search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
        jobs = client.get(f"/api/searches/{search_id}/jobs").json()
        titles = [j["job"]["title"] for j in jobs["jobs"]]
        assert "Senior Backend Engineer" not in titles
        assert jobs["count"] == 2

    def test_unknown_search_returns_404(self, client):
        response = client.get("/api/searches/search_doesnotexist")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "storage_error"


class TestHistory:
    def test_record_and_list_history(self, client):
        record = {"company": "A", "job_title": "Engineer", "job_id": "1"}
        assert client.post("/api/history", json=record).status_code == 201
        body = client.get("/api/history").json()
        assert body["count"] == 1
        assert body["applications"][0]["company"] == "A"

    def test_duplicate_application_rejected_with_409(self, client):
        record = {"company": "A", "job_title": "Engineer", "job_id": "1"}
        client.post("/api/history", json=record)
        response = client.post("/api/history", json=record)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "duplicate_application"


class TestBrowserHealth:
    def test_browser_health_endpoint(self, client):
        body = client.get("/api/browser/health").json()
        assert "healthy" in body
        assert "chromium_installed" in body
        assert isinstance(body["problems"], list)


class TestATSAdapters:
    def test_adapter_listing(self, client):
        body = client.get("/api/ats/adapters").json()
        greenhouse = next(a for a in body if a["adapter_id"] == "greenhouse")
        assert greenhouse["status"] == "beta"
        assert greenhouse["capabilities"]["submission"] == "simulated_only"


class TestHistoryExport:
    def test_xlsx_export_and_events(self, client):
        record = {"company": "A", "job_title": "Engineer", "job_id": "9"}
        client.post("/api/history", json=record)
        export = client.get("/api/history/export").json()
        assert export["format"] == "xlsx"
        assert export["records"] == 1

        from pathlib import Path
        assert Path(export["path"]).exists()

    def test_submission_status_endpoint_requires_package(self, client):
        assert client.get("/api/applications/nope_1_2/submission").status_code == 404


class TestPhase10Endpoints:
    def test_ui_dashboard_served(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Job Platform" in response.text
        assert "/api/applications" in response.text

    def test_backup_and_audit(self, client):
        backup = client.post("/api/system/backup")
        assert backup.status_code == 201
        assert backup.json()["file_count"] > 0
        listing = client.get("/api/system/backups").json()
        assert listing["count"] == 1

        audit = client.get("/api/system/audit").json()
        assert audit["ok"] is True

    def test_approve_requires_reviewed_execution(self, client, greenhouse_payload):
        import httpx as _httpx
        import respx as _respx
        with _respx.mock:
            _respx.get(GREENHOUSE_URL).mock(
                return_value=_httpx.Response(200, json=greenhouse_payload)
            )
            search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
        job_id = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"][0]["job"]["id"]
        package_id = client.post(
            "/api/applications/prepare", json={"search_id": search_id, "job_id": job_id}
        ).json()["package_id"]

        # No review-mode execution has happened -> approval refused with 409
        response = client.post(f"/api/applications/{package_id}/approve", json={})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "approval_error"


class TestPhase11Endpoints:
    def test_system_health_and_disk(self, client):
        health = client.get("/api/system/health").json()
        assert "healthy" in health
        assert any(c["name"] == "audit_trail" for c in health["components"])
        disk = client.get("/api/system/disk").json()
        assert disk["free_bytes"] > 0

    def test_diagnostics_bundle_is_sanitized(self, client):
        body = client.get("/api/system/diagnostics").json()
        text = client.get("/api/system/diagnostics").text
        assert "sk-ant-" not in text
        assert "counts" in body
        assert "anthropic_api_key_configured" in body

    def test_restore_missing_backup_is_404(self, client):
        response = client.post(
            "/api/system/restore", json={"backup_name": "backup_nope.zip"},
            headers={"origin": "http://localhost"},
        )
        assert response.status_code == 404

    def test_backup_then_restore_roundtrip(self, client):
        name = client.post("/api/system/backup").json()["path"].split("/")[-1]
        restored = client.post(
            "/api/system/restore", json={"backup_name": name},
            headers={"origin": "http://localhost"},
        )
        assert restored.status_code == 200
        assert restored.json()["safety_copy"]

    def test_audit_reports_chain_validity(self, client):
        client.post("/api/history", json={"company": "A", "job_title": "E", "job_id": "1"})
        audit = client.get("/api/system/audit").json()
        assert "chain_valid" in audit


class TestAutomaticModeAPI:
    def test_disabled_by_default(self, client):
        body = client.get("/api/automatic-mode").json()
        assert body["settings"]["enabled"] is False
        assert body["effective_enabled"] is False

    def test_enable_and_kill_switch(self, client):
        client.put("/api/automatic-mode",
                   json={"enabled": True, "adapter_allowlist": ["greenhouse"]})
        body = client.get("/api/automatic-mode").json()
        assert body["settings"]["enabled"] is True
        assert body["effective_enabled"] is True

        client.post("/api/automatic-mode/kill", json={"reason": "test incident"})
        body = client.get("/api/automatic-mode").json()
        assert body["kill_switch_engaged"] is True
        assert body["effective_enabled"] is False  # kill switch overrides enabled

        client.post("/api/automatic-mode/release")
        assert client.get("/api/automatic-mode").json()["kill_switch_engaged"] is False

    def test_automatic_queue_rejected_when_disabled(self, client, greenhouse_payload):
        import httpx as _httpx
        import respx as _respx
        with _respx.mock:
            _respx.get(GREENHOUSE_URL).mock(
                return_value=_httpx.Response(200, json=greenhouse_payload)
            )
            search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
        job_id = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"][0]["job"]["id"]
        package_id = client.post(
            "/api/applications/prepare", json={"search_id": search_id, "job_id": job_id}
        ).json()["package_id"]
        response = client.post(
            "/api/queue", json={"package_ids": [package_id], "mode": "automatic"}
        )
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "configuration_error"

    def test_metrics_endpoint(self, client):
        metrics = client.get("/api/automatic-mode/metrics").json()
        assert metrics["auto_submitted"] == 0
        assert metrics["downgraded_to_review"] == 0
