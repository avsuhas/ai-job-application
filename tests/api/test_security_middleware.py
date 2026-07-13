"""Tests for the local-only, CSRF, and security-header middleware (docs/12)."""




class TestSecurityHeaders:
    def test_headers_present_on_every_response(self, client):
        response = client.get("/api/health")
        assert response.headers["content-security-policy"].startswith("default-src 'none'")
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "no-referrer"

    def test_dashboard_csp_forbids_external_sources(self, client):
        response = client.get("/")
        csp = response.headers["content-security-policy"]
        assert "default-src 'none'" in csp
        assert "frame-ancestors 'none'" in csp


class TestCSRF:
    def test_same_origin_mutation_allowed(self, client):
        response = client.post(
            "/api/history",
            json={"company": "A", "job_title": "Engineer", "job_id": "1"},
            headers={"origin": "http://localhost:8000"},
        )
        assert response.status_code == 201

    def test_cross_origin_mutation_rejected(self, client):
        response = client.post(
            "/api/history",
            json={"company": "A", "job_title": "Engineer", "job_id": "1"},
            headers={"origin": "https://evil.example.com"},
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "csrf_blocked"

    def test_safe_method_cross_origin_allowed(self, client):
        # GETs are not CSRF-sensitive and must still work with any origin
        response = client.get(
            "/api/health", headers={"origin": "https://evil.example.com"}
        )
        assert response.status_code == 200


class TestLocalOnly:
    def test_non_local_host_rejected(self, client):
        response = client.get("/api/health", headers={"host": "example.com"})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "local_only"

    def test_localhost_host_allowed(self, client):
        response = client.get("/api/health", headers={"host": "localhost:8000"})
        assert response.status_code == 200
