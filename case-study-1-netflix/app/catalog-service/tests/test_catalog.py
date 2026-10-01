"""Unit tests for Netflix catalog-service."""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app

client = TestClient(app)


def test_health_returns_healthy():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "catalog-service"


def test_list_catalog_returns_movies():
    resp = client.get("/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "movies" in data
    assert data["total"] > 0


def test_list_catalog_genre_filter():
    resp = client.get("/catalog?genre=Sci-Fi")
    assert resp.status_code == 200
    data = resp.json()
    for movie in data["movies"]:
        assert movie["genre"] == "Sci-Fi"


def test_get_existing_movie():
    resp = client.get("/catalog/m001")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Stranger Things"


def test_get_nonexistent_movie_returns_404():
    resp = client.get("/catalog/m999")
    assert resp.status_code == 404


def test_search_catalog():
    resp = client.get("/catalog/search/Squid")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any("Squid" in m["title"] for m in results)


def test_catalog_limit():
    resp = client.get("/catalog?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()["movies"]) <= 2
