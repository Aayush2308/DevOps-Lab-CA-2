"""
Netflix Recommendation Service
Demonstrates circuit-breaker / fallback pattern:
- Tries to call catalog-service for enriched recommendations
- If catalog is down (Chaos Monkey killed it), falls back to cached static data
- This is the core resilience pattern from the Netflix case study
"""
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Netflix Recommendation Service",
    description="Recommendation microservice with circuit-breaker fallback",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8001")

# Fallback cached recommendations (used when catalog-service is down)
FALLBACK_RECOMMENDATIONS = [
    {"id": "m001", "title": "Stranger Things", "reason": "Trending (cached)", "fallback": True},
    {"id": "m003", "title": "Squid Game", "reason": "Popular globally (cached)", "fallback": True},
    {"id": "m005", "title": "Ozark", "reason": "Critically acclaimed (cached)", "fallback": True},
]

# Simple in-memory circuit state
_circuit_open = False
_failure_count = 0
FAILURE_THRESHOLD = 3


def _record_failure():
    global _circuit_open, _failure_count
    _failure_count += 1
    if _failure_count >= FAILURE_THRESHOLD:
        _circuit_open = True
        logger.warning("Circuit OPEN: catalog-service unreachable, using fallback")


def _record_success():
    global _circuit_open, _failure_count
    _circuit_open = False
    _failure_count = 0


@app.get("/health", tags=["ops"])
def health_check():
    return {
        "status": "healthy",
        "service": "recommendation-service",
        "circuit_open": _circuit_open,
        "failure_count": _failure_count,
        "timestamp": time.time(),
    }


@app.get("/", tags=["ops"])
def root():
    return {"service": "recommendation-service", "version": "1.0.0", "docs": "/docs"}


@app.get("/recommendations/{user_id}", tags=["recommendations"])
async def get_recommendations(user_id: str):
    """
    Fetch recommendations for a user.
    Primary path: calls catalog-service for live data.
    Fallback path (circuit open): returns cached recommendations.
    This mimics Netflix Hystrix fallback behaviour.
    """
    if _circuit_open:
        logger.info(f"[user={user_id}] Circuit open — serving fallback recommendations")
        return {
            "user_id": user_id,
            "source": "fallback_cache",
            "recommendations": FALLBACK_RECOMMENDATIONS,
            "circuit_status": "OPEN",
        }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{CATALOG_URL}/catalog?limit=3")
            resp.raise_for_status()
            movies = resp.json().get("movies", [])
            _record_success()
            enriched = [
                {"id": m["id"], "title": m["title"], "reason": "Live recommendation", "fallback": False}
                for m in movies
            ]
            return {
                "user_id": user_id,
                "source": "catalog_service",
                "recommendations": enriched,
                "circuit_status": "CLOSED",
            }
    except Exception as exc:
        logger.error(f"[user={user_id}] Catalog call failed: {exc}")
        _record_failure()
        return {
            "user_id": user_id,
            "source": "fallback_cache",
            "recommendations": FALLBACK_RECOMMENDATIONS,
            "circuit_status": f"OPENING ({_failure_count}/{FAILURE_THRESHOLD})",
        }


@app.post("/circuit/reset", tags=["ops"])
def reset_circuit():
    """Manually reset the circuit breaker (for demo purposes)."""
    global _circuit_open, _failure_count
    _circuit_open = False
    _failure_count = 0
    return {"message": "Circuit reset to CLOSED"}
