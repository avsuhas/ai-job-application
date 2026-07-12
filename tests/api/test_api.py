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
