"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import __version__
from backend.api.middleware import RateLimitMiddleware, RequestTrackingMiddleware
from backend.api.routes import (
    agents,
    approvals,
    audit,
    auth,
    autogen,
    compliance,
    cost,
    health,
    llm,
    projects,
)
from backend.config import settings
from backend.database import init_db
from backend.websocket.manager import ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    await init_db()
    yield


app = FastAPI(
    title="AI-Empower-Coding-Pilot",
    description=(
        "Enterprise-grade autonomous AI coding system with AutoGen multi-agent orchestration, "
        "auto-scaffolding, CI/CD generation, Terraform IaC, HIPAA/PCI/SOC2/GDPR compliance, "
        "immutable audit logging, cost tracking, human approval gates, real-time WebSocket updates, "
        "and multi-provider LLM integration."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.add_middleware(RateLimitMiddleware)

# --- Routes ---
app.include_router(health.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(cost.router, prefix="/api")
app.include_router(autogen.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(llm.router, prefix="/api")

# --- WebSocket ---
app.include_router(ws_router)


@app.get("/")
async def root() -> dict:
    return {
        "name": "AI-Empower-Coding-Pilot",
        "version": __version__,
        "docs": "/docs",
        "features": [
            "AutoGen multi-agent orchestration",
            "Project scaffolding",
            "CI/CD pipeline generation",
            "Docker config generation",
            "Terraform IaC generation",
            "HIPAA/PCI/SOC2/GDPR compliance",
            "Immutable audit logging",
            "Cost tracking & token budgeting",
            "Human approval gates",
            "Real-time WebSocket updates",
            "Multi-provider LLM integration",
            "Database persistence",
            "Redis caching & rate limiting",
        ],
    }
