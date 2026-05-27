"""Tests for the FastAPI endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "AI-Empower-Coding-Pilot"


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness(client: AsyncClient) -> None:
    res = await client.get("/api/readiness")
    assert res.status_code == 200
    assert res.json()["ready"] is True


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient) -> None:
    res = await client.get("/api/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) == 9
    roles = {a["role"] for a in agents}
    assert "architect" in roles
    assert "coder" in roles


@pytest.mark.asyncio
async def test_create_and_list_projects(client: AsyncClient) -> None:
    res = await client.post(
        "/api/projects",
        json={"name": "Test Project", "description": "test", "requirements": "Build an API"},
    )
    assert res.status_code == 201
    project = res.json()
    assert project["name"] == "Test Project"

    res = await client.get("/api/projects")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_compliance_report(client: AsyncClient) -> None:
    res = await client.get("/api/compliance")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_audit_summary(client: AsyncClient) -> None:
    res = await client.get("/api/audit/summary")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_run_pipeline_ad_hoc(client: AsyncClient) -> None:
    res = await client.post(
        "/api/projects/run",
        json={"requirements": "Build a simple calculator API"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "workflow_id" in data
    assert data["status"] in ("completed", "failed")
