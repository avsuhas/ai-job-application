"""API tests for Phase 4: review, readiness, manual handoff, answer editing,
and manual submission recording."""

import httpx
import pytest
import respx

from tests.api.conftest import GREENHOUSE_URL


@pytest.fixture
def package_id(client, greenhouse_payload):
    """Prepare a package through the API and return its id."""
    with respx.mock:
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
    job_id = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"][0]["job"]["id"]
    return client.post(
        "/api/applications/prepare", json={"search_id": search_id, "job_id": job_id}
    ).json()["package_id"]


class TestReviewEndpoints:
    def test_run_and_fetch_review(self, client, package_id):
        response = client.post(f"/api/applications/{package_id}/review")
        assert response.status_code == 200
        report = response.json()
        assert report["package_id"] == package_id
        assert report["status"] in ("approved", "approved_with_warnings")

        fetched = client.get(f"/api/applications/{package_id}/review").json()
        assert fetched["review_id"] == report["review_id"]

    def test_review_before_run_returns_404(self, client, package_id):
        assert client.get(f"/api/applications/{package_id}/review").status_code == 404


class TestReadinessEndpoint:
    def test_readiness_requires_review_first(self, client, package_id):
        report = client.post(f"/api/applications/{package_id}/readiness").json()
        assert report["status"] == "blocked"
        assert report["next_allowed_action"] == "run_review"

    def test_reviewed_package_becomes_ready(self, client, package_id):
        client.post(f"/api/applications/{package_id}/review")
        report = client.post(f"/api/applications/{package_id}/readiness").json()
        assert report["status"] in ("ready", "ready_with_warnings")
        assert report["next_allowed_action"] == "manual_completion"
        checks = {c["check_id"]: c["status"] for c in report["checks"]}
        assert checks["review_completed"] == "passed"
        assert checks["duplicate_application"] == "passed"


class TestManualHandoff:
    def test_manual_package_contains_checklists(self, client, package_id):
        payload = client.get(f"/api/applications/{package_id}/manual-package").json()
        assert payload["application_url"]
        assert payload["upload_checklist"]
        assert payload["completion_checklist"]
        assert "# Manual application:" in payload["markdown"]

    def test_edit_answer_and_reflect_in_handoff(self, client, package_id):
        edited = client.put(
            f"/api/applications/{package_id}/answers/employment.notice_period",
            json={"answer": "Two weeks", "question": "What is your notice period?"},
        )
        assert edited.status_code == 200
        assert edited.json()["approved"] is True

        payload = client.get(f"/api/applications/{package_id}/manual-package").json()
        families = {a["question_family"]: a for a in payload["answers"]}
        assert families["employment.notice_period"]["answer"] == "Two weeks"
        assert not any("notice_period" in m for m in payload["missing_answers"])

    def test_edit_with_save_for_reuse_updates_candidate_answers(
        self, client, package_id, tmp_path
    ):
        client.put(
            f"/api/applications/{package_id}/answers/preferences.start_date",
            json={
                "answer": "August 1, 2026",
                "question": "When can you start?",
                "save_for_reuse": True,
            },
        )
        answers_md = tmp_path / "user_data" / "candidate" / "profile" / "answers.md"
        assert "When can you start?" in answers_md.read_text()

    def test_edit_unknown_answer_returns_404(self, client, package_id):
        response = client.put(
            f"/api/applications/{package_id}/answers/nonexistent.family",
            json={"answer": "x"},
        )
        assert response.status_code == 404


class TestManualSubmission:
    def test_mark_submitted_records_history(self, client, package_id):
        response = client.post(
            f"/api/applications/{package_id}/mark-submitted",
            json={"notes": "submitted from my browser"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "submitted"
        assert "manual submission" in body["tracker_record"]["notes"]

        history = client.get("/api/history").json()
        assert history["count"] == 1
        detail = client.get(f"/api/applications/{package_id}").json()
        assert detail["status"] == "submitted"

    def test_double_submission_rejected(self, client, package_id):
        client.post(f"/api/applications/{package_id}/mark-submitted", json={})
        response = client.post(f"/api/applications/{package_id}/mark-submitted", json={})
        assert response.status_code == 409

    def test_submitted_job_excluded_from_new_searches(
        self, client, package_id, greenhouse_payload
    ):
        client.post(f"/api/applications/{package_id}/mark-submitted", json={})
        with respx.mock:
            respx.get(GREENHOUSE_URL).mock(
                return_value=httpx.Response(200, json=greenhouse_payload)
            )
            search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
        jobs = client.get(f"/api/searches/{search_id}/jobs").json()
        assert jobs["count"] == 2  # one of the three fixture jobs now applied
