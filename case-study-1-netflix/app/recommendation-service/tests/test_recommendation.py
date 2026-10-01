"""Unit tests for Netflix recommendation-service."""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app, _record_failure, _record_success, FAILURE_THRESHOLD
import main as svc

client = TestClient(app)


def setup_function():
    """Reset circuit before each test."""
    svc._circuit_open = False
    svc._failure_count = 0


def test_health_returns_healthy():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "recommendation-service"
    assert "circuit_open" in data


def test_circuit_reset_endpoint():
    svc._circuit_open = True
    svc._failure_count = 5
    resp = client.post("/circuit/reset")
    assert resp.status_code == 200
    assert svc._circuit_open is False
    assert svc._failure_count == 0


def test_recommendations_fallback_when_circuit_open():
    """When circuit is open, service must return fallback recommendations."""
    svc._circuit_open = True
    resp = client.get("/recommendations/user123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "fallback_cache"
    assert data["circuit_status"] == "OPEN"
    assert len(data["recommendations"]) > 0
    # All fallback entries must be marked
    for rec in data["recommendations"]:
        assert rec["fallback"] is True


def test_recommendations_fallback_served_when_catalog_down():
    """
    Catalog-service is not running in unit test context.
    The service must return fallback gracefully (not crash).
    """
    svc._circuit_open = False
    svc._failure_count = 0
    resp = client.get("/recommendations/user456")
    assert resp.status_code == 200
    data = resp.json()
    # Either live or fallback is acceptable — must not 500
    assert data["user_id"] == "user456"
    assert "recommendations" in data
