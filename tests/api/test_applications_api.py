"""API tests for the application preparation endpoints (Phase 3)."""

import httpx
import pytest
import respx

from tests.api.conftest import GREENHOUSE_URL


@pytest.fixture
def ranked_search(client, greenhouse_payload):
    """Run a search so ranked jobs exist, return (search_id, first job id)."""
    with respx.mock:
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
    jobs = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"]
    return search_id, jobs[0]["job"]["id"]


class TestPrepareEndpoint:
    def test_prepare_creates_ready_package(self, client, ranked_search):
        search_id, job_id = ranked_search
        response = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": job_id},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "ready"
        assert body["company"] == "ExampleCo"
        assert body["selected_resume"] == "resume/tailored_resume.md"

    def test_prepare_unknown_job_returns_404(self, client, ranked_search):
        search_id, _ = ranked_search
        response = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": "job_nope"},
        )
        assert response.status_code == 404

    def test_list_and_detail_endpoints(self, client, ranked_search):
        search_id, job_id = ranked_search
        package_id = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": job_id},
        ).json()["package_id"]

        listing = client.get("/api/applications").json()
        assert listing["count"] == 1
        assert listing["applications"][0]["package_id"] == package_id

        detail = client.get(f"/api/applications/{package_id}").json()
        assert detail["is_stale"] is False
        assert "job/job.json" in detail["artifacts"]
        assert "plan/application_plan.json" in detail["artifacts"]

    def test_artifact_content_endpoint(self, client, ranked_search):
        search_id, job_id = ranked_search
        package_id = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": job_id},
        ).json()["package_id"]

        artifact = client.get(
            f"/api/applications/{package_id}/artifacts/resume/tailored_resume.md"
        ).json()
        assert "PROFESSIONAL SUMMARY" in artifact["content"]

    def test_artifact_path_traversal_rejected(self, client, ranked_search):
        search_id, job_id = ranked_search
        package_id = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": job_id},
        ).json()["package_id"]

        response = client.get(
            f"/api/applications/{package_id}/artifacts/..%2F..%2F..%2Ftracker.csv"
        )
        assert response.status_code == 404

    def test_stale_detection_after_candidate_edit(self, client, ranked_search, tmp_path):
        search_id, job_id = ranked_search
        package_id = client.post(
            "/api/applications/prepare",
            json={"search_id": search_id, "job_id": job_id},
        ).json()["package_id"]

        rules = tmp_path / "user_data" / "candidate" / "profile" / "rules.md"
        rules.write_text("Never apply on Fridays.")
        client.post("/api/candidate/reload")

        detail = client.get(f"/api/applications/{package_id}").json()
        assert detail["is_stale"] is True
        assert "profile/rules" in detail["stale_sources"]

    def test_cover_letter_option_flows_through(self, client, ranked_search):
        search_id, job_id = ranked_search
        body = client.post(
            "/api/applications/prepare",
            json={
                "search_id": search_id,
                "job_id": job_id,
                "generate_cover_letter": True,
            },
        ).json()
        assert body["cover_letter"] == "cover_letter/cover_letter.md"
