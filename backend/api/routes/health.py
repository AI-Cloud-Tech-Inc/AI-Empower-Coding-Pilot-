"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend import __version__
from backend.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=__version__,
        services={
            "api": "running",
            "orchestrator": "ready",
            "vector_store": "ready",
        },
    )


@router.get("/readiness")
async def readiness() -> dict:
    return {"ready": True}
