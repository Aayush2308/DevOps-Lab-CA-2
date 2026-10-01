"""Unit tests for Amazon orders-service."""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app, ORDERS

client = TestClient(app)


def setup_function():
    ORDERS.clear()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "orders-service"


def test_create_order():
    payload = {
        "product_id": "P001",
        "quantity": 2,
        "customer_id": "CUST-001",
        "shipping_address": "123 Main St, Pune"
    }
    resp = client.post("/orders", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "CONFIRMED"
    assert data["order_id"].startswith("ORD-")
    assert data["product_id"] == "P001"


def test_get_order():
    payload = {"product_id": "P002", "quantity": 1, "customer_id": "CUST-002", "shipping_address": "Pune"}
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["order_id"]
    resp = client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["order_id"] == order_id


def test_get_nonexistent_order_returns_404():
    resp = client.get("/orders/ORD-FAKE")
    assert resp.status_code == 404


def test_list_orders():
    for i in range(3):
        client.post("/orders", json={"product_id": f"P00{i}", "quantity": 1,
                                      "customer_id": "CUST-LIST", "shipping_address": "Test"})
    resp = client.get("/orders?customer_id=CUST-LIST")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


def test_update_order_status():
    create_resp = client.post("/orders", json={"product_id": "P001", "quantity": 1,
                                                "customer_id": "CUST-STATUS", "shipping_address": "Test"})
    order_id = create_resp.json()["order_id"]
    resp = client.patch(f"/orders/{order_id}/status?status=SHIPPED")
    assert resp.status_code == 200
    assert resp.json()["status"] == "SHIPPED"


def test_invalid_status_rejected():
    create_resp = client.post("/orders", json={"product_id": "P001", "quantity": 1,
                                                "customer_id": "CUST-X", "shipping_address": "Test"})
    order_id = create_resp.json()["order_id"]
    resp = client.patch(f"/orders/{order_id}/status?status=EXPLODED")
    assert resp.status_code == 400
