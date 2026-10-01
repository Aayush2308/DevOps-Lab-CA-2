"""Unit tests for Amazon inventory-service."""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app, INVENTORY
import copy

client = TestClient(app)

ORIGINAL_INVENTORY = None


def setup_function():
    # Reset inventory to initial state before each test
    INVENTORY.clear()
    INVENTORY.update({
        "P001": {"product_id": "P001", "name": "Echo Dot", "stock": 500, "reserved": 0, "warehouse": "US-WEST"},
        "P002": {"product_id": "P002", "name": "Kindle", "stock": 250, "reserved": 10, "warehouse": "US-EAST"},
    })


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "inventory-service"


def test_list_inventory():
    resp = client.get("/inventory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_products"] == 2
    for item in data["items"]:
        assert "available" in item


def test_get_product_stock():
    resp = client.get("/inventory/P001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] == 500  # stock - reserved


def test_get_nonexistent_product_returns_404():
    resp = client.get("/inventory/P999")
    assert resp.status_code == 404


def test_reserve_stock_success():
    resp = client.put("/inventory/P001/reserve", json={"quantity": 10, "order_id": "ORD-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["reserved_qty"] == 10
    assert data["remaining_available"] == 490


def test_reserve_stock_insufficient():
    resp = client.put("/inventory/P001/reserve", json={"quantity": 9999, "order_id": "ORD-FAIL"})
    assert resp.status_code == 409


def test_release_stock():
    # Reserve first
    client.put("/inventory/P001/reserve", json={"quantity": 50, "order_id": "ORD-RELEASE"})
    resp = client.put("/inventory/P001/release", json={"quantity": 50, "order_id": "ORD-RELEASE"})
    assert resp.status_code == 200
    assert resp.json()["released_qty"] == 50
