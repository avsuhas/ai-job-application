"""API tests for queue endpoints. Workflow execution itself is covered by
the browser E2E suite; here we verify creation, admission surfacing, and
control endpoints through the API."""

import httpx
import pytest
import respx

from tests.api.conftest import GREENHOUSE_URL


@pytest.fixture
def ready_package_id(client, greenhouse_payload):
    with respx.mock:
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
    job_id = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"][0]["job"]["id"]
    package_id = client.post(
        "/api/applications/prepare", json={"search_id": search_id, "job_id": job_id}
    ).json()["package_id"]
    client.post(f"/api/applications/{package_id}/review")
    return package_id


class TestQueueAPI:
    def test_create_queue_with_admission(self, client, ready_package_id):
        response = client.post("/api/queue", json={"package_ids": [ready_package_id]})
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "ready"
        assert body["items"][0]["status"] == "admitted"
        assert body["items"][0]["admission"]["status"] == "admitted"
        assert any(e["event_type"] == "queue_created" for e in body["events"])

    def test_unready_package_rejected_with_reasons(self, client, greenhouse_payload):
        with respx.mock:
            respx.get(GREENHOUSE_URL).mock(
                return_value=httpx.Response(200, json=greenhouse_payload)
            )
            search_id = client.post("/api/searches?wait=true", json={}).json()["search_id"]
        job_id = client.get(f"/api/searches/{search_id}/jobs").json()["jobs"][1]["job"]["id"]
        package_id = client.post(
            "/api/applications/prepare", json={"search_id": search_id, "job_id": job_id}
        ).json()["package_id"]
        # no review run -> not ready for the queue
        body = client.post("/api/queue", json={"package_ids": [package_id]}).json()
        assert body["items"][0]["status"] == "rejected"
        assert body["items"][0]["error"]

    def test_queue_lifecycle_endpoints(self, client, ready_package_id):
        queue_id = client.post(
            "/api/queue", json={"package_ids": [ready_package_id]}
        ).json()["queue_id"]

        listing = client.get("/api/queue").json()
        assert listing["count"] == 1

        detail = client.get(f"/api/queue/{queue_id}").json()
        assert detail["queue_id"] == queue_id

        assert client.post(f"/api/queue/{queue_id}/pause").json()["pause_requested"]
        assert client.post(f"/api/queue/{queue_id}/cancel").json()["cancel_requested"]

        skipped = client.post(
            f"/api/queue/{queue_id}/items/{ready_package_id}/skip"
        ).json()
        assert skipped["items"][0]["status"] == "skipped"

    def test_unknown_queue_returns_404(self, client):
        assert client.get("/api/queue/queue_missing").status_code == 404
