"""
Tests for backend/server.py — FastAPI endpoint integration tests.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.server import app
import backend.storage as storage


@pytest.fixture(autouse=True)
def _isolate_db(tmp_path):
    """Every API test gets its own temp database."""
    original_path = storage.DB_PATH
    storage.DB_PATH = str(tmp_path / "test_api.db")
    storage.init_db()
    yield
    storage.DB_PATH = original_path


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")
        assert "checks" in data

    def test_health_checks_analyzer(self, client):
        resp = client.get("/api/health")
        checks = resp.json()["checks"]
        assert checks["analyzer"] == "ok"
        assert checks["regulatory_sources"] >= 10


class TestSourcesEndpoint:
    def test_list_sources(self, client):
        resp = client.get("/api/sources")
        assert resp.status_code == 200
        sources = resp.json()["sources"]
        assert len(sources) >= 10
        assert all("id" in s and "title" in s for s in sources)


class TestProductsEndpoint:
    def test_list_products(self, client):
        resp = client.get("/api/products")
        assert resp.status_code == 200
        products = resp.json()["products"]
        assert "ws_invest" in products
        assert "ws_trade" in products
        assert "ws_crypto" in products


class TestControlsEndpoint:
    def test_list_controls(self, client):
        resp = client.get("/api/controls")
        assert resp.status_code == 200
        controls = resp.json()["controls"]
        assert "ctrl_kyc_onboarding" in controls


class TestAnalysisEndpoint:
    def test_run_analysis(self, client):
        resp = client.post("/api/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert "obligations" in data
        assert "conflicts" in data
        assert "stats" in data
        assert data["stats"]["total_obligations"] > 50

    def test_get_analysis_auto_seeds(self, client):
        resp = client.get("/api/analysis")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_obligations"] > 0
        # Check dynamic metadata
        assert "sources_count" in data
        assert "patterns_count" in data

    def test_analyze_unknown_source_404(self, client):
        resp = client.post("/api/analyze?source_id=NONEXISTENT")
        assert resp.status_code == 404


class TestReviewEndpoint:
    def test_approve_with_valid_role(self, client):
        # Seed analysis first
        client.post("/api/analyze")
        analysis = client.get("/api/analysis").json()
        ob_id = analysis["obligations"][0]["id"]

        resp = client.post("/api/review", json={
            "obligation_id": ob_id,
            "reviewer": "officer@ws.com",
            "action": "approve",
            "role": "compliance_officer",
            "notes": "Verified",
        })
        assert resp.status_code == 200

    def test_approve_with_analyst_role_403(self, client):
        client.post("/api/analyze")
        analysis = client.get("/api/analysis").json()
        ob_id = analysis["obligations"][0]["id"]

        resp = client.post("/api/review", json={
            "obligation_id": ob_id,
            "reviewer": "analyst@ws.com",
            "action": "approve",
            "role": "analyst",
        })
        assert resp.status_code == 403

    def test_review_nonexistent_obligation_404(self, client):
        client.post("/api/analyze")
        resp = client.post("/api/review", json={
            "obligation_id": "nonexistent",
            "reviewer": "officer@ws.com",
            "action": "approve",
            "role": "compliance_officer",
        })
        assert resp.status_code == 404


class TestReviewHistoryEndpoint:
    def test_get_history(self, client):
        client.post("/api/analyze")
        analysis = client.get("/api/analysis").json()
        ob_id = analysis["obligations"][0]["id"]

        # Make a review
        client.post("/api/review", json={
            "obligation_id": ob_id,
            "reviewer": "officer@ws.com",
            "action": "approve",
            "role": "compliance_officer",
        })

        resp = client.get(f"/api/review/history/{ob_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1


class TestRevertEndpoint:
    def test_admin_can_revert(self, client):
        client.post("/api/analyze")
        analysis = client.get("/api/analysis").json()
        ob_id = analysis["obligations"][0]["id"]

        client.post("/api/review", json={
            "obligation_id": ob_id,
            "reviewer": "officer@ws.com",
            "action": "approve",
            "role": "compliance_officer",
        })

        resp = client.post("/api/review/revert", json={
            "obligation_id": ob_id,
            "admin_user": "admin@ws.com",
            "admin_role": "admin",
        })
        assert resp.status_code == 200

    def test_non_admin_revert_403(self, client):
        client.post("/api/analyze")
        analysis = client.get("/api/analysis").json()
        ob_id = analysis["obligations"][0]["id"]

        client.post("/api/review", json={
            "obligation_id": ob_id,
            "reviewer": "officer@ws.com",
            "action": "approve",
            "role": "compliance_officer",
        })

        resp = client.post("/api/review/revert", json={
            "obligation_id": ob_id,
            "admin_user": "officer@ws.com",
            "admin_role": "compliance_officer",
        })
        assert resp.status_code == 403


class TestAnalyzeTextEndpoint:
    def test_analyze_text_deterministic(self, client):
        resp = client.post("/api/analyze-text", json={
            "text": "Reporting entities must file a suspicious transaction report with "
                    "FINTRAC when there are reasonable grounds to suspect money laundering.",
            "use_llm": False,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_obligations"] > 0

    def test_analyze_text_too_short(self, client):
        resp = client.post("/api/analyze-text", json={
            "text": "short",
            "use_llm": False,
        })
        assert resp.status_code == 422  # Pydantic validation error


class TestEvalEndpoint:
    def test_run_eval(self, client):
        resp = client.get("/api/eval/run")
        assert resp.status_code == 200
        data = resp.json()
        assert "metrics" in data
        assert data["metrics"]["total_test_cases"] >= 70
        # All metrics should be 100% if our eval suite is correct
        assert data["metrics"]["obligation_extraction_accuracy"] == 100.0

    def test_eval_snippet(self, client):
        resp = client.post("/api/eval/test-snippet", json={
            "snippet": "The dealer must verify the identity of each client using know your client procedures before any recommendations.",
            "expected_domains": ["KYC"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "KYC" in data["extracted"]["domains"]
        assert data["accuracy"]["domain_accuracy"] == 100.0


class TestRolesEndpoint:
    def test_get_roles(self, client):
        resp = client.get("/api/roles")
        assert resp.status_code == 200
        roles = resp.json()["roles"]
        assert "admin" in roles
        assert "compliance_officer" in roles


class TestRateLimiting:
    def test_rate_limit_returns_429(self, client, monkeypatch):
        """When RATE_LIMIT_RPM=5, the 6th request should get 429."""
        import backend.server as srv
        monkeypatch.setattr(srv, "RATE_LIMIT_RPM", 5)
        srv._rate_buckets.clear()
        for i in range(5):
            resp = client.get("/api/health")
            assert resp.status_code == 200, f"Request {i+1} failed unexpectedly"
        resp = client.get("/api/health")
        assert resp.status_code == 429
        assert "Rate limit" in resp.json()["detail"]
