"""
Netflix Catalog Service
Exposes movie catalog with health and Prometheus metrics endpoints.
Theme: Resilience — this service is designed to be killed by Chaos Monkey
and recovered automatically by Kubernetes self-healing.
"""
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Optional
import time

app = FastAPI(
    title="Netflix Catalog Service",
    description="Catalog microservice for Netflix CA-II demo",
    version="1.0.0",
)

# Attach Prometheus metrics — exposes /metrics endpoint automatically
Instrumentator().instrument(app).expose(app)

# --- In-memory catalog (simulates a database) ---
CATALOG: dict[str, dict] = {
    "m001": {"id": "m001", "title": "Stranger Things", "genre": "Sci-Fi", "rating": 8.7, "year": 2016},
    "m002": {"id": "m002", "title": "The Crown", "genre": "Drama", "rating": 8.6, "year": 2016},
    "m003": {"id": "m003", "title": "Squid Game", "genre": "Thriller", "rating": 8.0, "year": 2021},
    "m004": {"id": "m004", "title": "Wednesday", "genre": "Comedy-Horror", "rating": 7.8, "year": 2022},
    "m005": {"id": "m005", "title": "Ozark", "genre": "Crime-Drama", "rating": 8.4, "year": 2017},
}


@app.get("/health", tags=["ops"])
def health_check():
    """Kubernetes liveness/readiness probe endpoint."""
    return {"status": "healthy", "service": "catalog-service", "timestamp": time.time()}


@app.get("/", tags=["ops"])
def root():
    return {"service": "catalog-service", "version": "1.0.0", "docs": "/docs"}


@app.get("/catalog", tags=["catalog"])
def list_catalog(genre: Optional[str] = None, limit: int = 10):
    """Return all movies, optionally filtered by genre."""
    movies = list(CATALOG.values())
    if genre:
        movies = [m for m in movies if m["genre"].lower() == genre.lower()]
    return {"total": len(movies), "movies": movies[:limit]}


@app.get("/catalog/{movie_id}", tags=["catalog"])
def get_movie(movie_id: str):
    """Return a single movie by ID."""
    if movie_id not in CATALOG:
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")
    return CATALOG[movie_id]


@app.get("/catalog/search/{query}", tags=["catalog"])
def search_catalog(query: str):
    """Search movies by title (case-insensitive substring)."""
    results = [m for m in CATALOG.values() if query.lower() in m["title"].lower()]
    return {"query": query, "results": results}
