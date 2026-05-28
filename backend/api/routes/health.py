"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend import __version__
from backend.api.schemas import HealthResponse
from backend.cache import cache_health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    redis_status = await cache_health()
    return HealthResponse(
        status="healthy",
        version=__version__,
        services={
            "api": "running",
            "orchestrator": "ready",
            "vector_store": "ready",
            "cache": redis_status.get("status", "unavailable"),
        },
    )


@router.get("/readiness")
async def readiness() -> dict:
    return {"ready": True}
