"""Unit tests for Amazon payments-service."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app, PAYMENTS

client = TestClient(app)


def setup_function():
    PAYMENTS.clear()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "payments-service"


def test_process_payment_success():
    """Force success by patching random.random to always return > 0.05."""
    with patch("main.random.random", return_value=0.99):
        resp = client.post("/payments", json={
            "order_id": "ORD-001",
            "amount": 29.99,
            "currency": "USD",
            "payment_method": "card",
            "customer_id": "CUST-001"
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["payment_id"].startswith("PAY-")


def test_process_payment_failure():
    """Force failure by patching random.random to always return < 0.05."""
    with patch("main.random.random", return_value=0.01):
        resp = client.post("/payments", json={
            "order_id": "ORD-002",
            "amount": 99.99,
            "currency": "USD",
            "payment_method": "upi",
            "customer_id": "CUST-002"
        })
    assert resp.status_code == 402


def test_get_payment():
    with patch("main.random.random", return_value=0.99):
        create_resp = client.post("/payments", json={
            "order_id": "ORD-003", "amount": 10.0, "currency": "USD",
            "payment_method": "wallet", "customer_id": "CUST-003"
        })
    pay_id = create_resp.json()["payment_id"]
    resp = client.get(f"/payments/{pay_id}")
    assert resp.status_code == 200
    assert resp.json()["payment_id"] == pay_id


def test_get_nonexistent_payment_404():
    resp = client.get("/payments/PAY-FAKE")
    assert resp.status_code == 404


def test_refund_payment():
    with patch("main.random.random", return_value=0.99):
        create_resp = client.post("/payments", json={
            "order_id": "ORD-004", "amount": 50.0, "currency": "USD",
            "payment_method": "card", "customer_id": "CUST-004"
        })
    pay_id = create_resp.json()["payment_id"]
    resp = client.post(f"/payments/{pay_id}/refund")
    assert resp.status_code == 200
    assert resp.json()["refund_status"] == "REFUNDED"
