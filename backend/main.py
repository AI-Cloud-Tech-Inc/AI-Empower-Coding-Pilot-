"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import __version__
from backend.api.middleware import RequestTrackingMiddleware
from backend.api.routes import agents, audit, compliance, health, projects
from backend.config import settings

app = FastAPI(
    title="AI-Empower-Coding-Pilot",
    description=(
        "Enterprise-grade autonomous AI coding system with multi-agent orchestration, "
        "RAG, compliance tracking, audit logging, and cost optimization."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTrackingMiddleware)

# --- Routes ---
app.include_router(health.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


@app.get("/")
async def root() -> dict:
    return {
        "name": "AI-Empower-Coding-Pilot",
        "version": __version__,
        "docs": "/docs",
    }
