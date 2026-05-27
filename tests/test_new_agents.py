"""Tests for new agents: DevOps, Performance, Accessibility."""

from __future__ import annotations

import pytest

from backend.agents.accessibility import AccessibilityAgent
from backend.agents.base import AgentContext, AgentRole
from backend.agents.devops import DevOpsAgent
from backend.agents.performance import PerformanceAgent


@pytest.fixture
def context_with_architecture() -> AgentContext:
    return AgentContext(
        requirements="Build a web API with frontend and database",
        architecture={
            "components": [
                {"name": "api_layer", "type": "service", "description": "REST API"},
                {"name": "frontend", "type": "application", "description": "Web dashboard"},
                {"name": "database", "type": "infrastructure", "description": "Data persistence"},
            ],
            "patterns": ["REST API"],
            "tech_stack": {"frameworks": ["FastAPI", "React"], "databases": ["PostgreSQL"]},
        },
    )


@pytest.fixture
def context_with_code() -> AgentContext:
    return AgentContext(
        requirements="Build a web app",
        architecture={
            "components": [
                {"name": "api_layer", "type": "service", "description": "REST API"},
            ]
        },
        code_files={
            "app.py": "from fastapi import FastAPI\napp = FastAPI()\ntime.sleep(1)\n",
            "main.tsx": '<div onClick={() => {}}><img src="test.png"><button></button></div>',
        },
    )


class TestDevOpsAgent:
    @pytest.mark.asyncio
    async def test_role(self) -> None:
        agent = DevOpsAgent()
        assert agent.role == AgentRole.DEVOPS

    @pytest.mark.asyncio
    async def test_generates_config(self, context_with_architecture: AgentContext) -> None:
        agent = DevOpsAgent()
        result = await agent.run(context_with_architecture)
        assert result.success
        assert "ci_pipeline" in result.output
        assert "docker_services" in result.output
        assert "deployment" in result.output
        assert "monitoring" in result.output

    @pytest.mark.asyncio
    async def test_ci_stages(self, context_with_architecture: AgentContext) -> None:
        agent = DevOpsAgent()
        result = await agent.run(context_with_architecture)
        stages = result.output["ci_pipeline"]["stages"]
        assert "lint" in stages
        assert "test" in stages
        assert "deploy" in stages

    @pytest.mark.asyncio
    async def test_docker_services(self, context_with_architecture: AgentContext) -> None:
        agent = DevOpsAgent()
        result = await agent.run(context_with_architecture)
        service_names = [s["name"] for s in result.output["docker_services"]]
        assert "backend" in service_names
        assert "frontend" in service_names
        assert "redis" in service_names

    @pytest.mark.asyncio
    async def test_fails_without_architecture(self) -> None:
        agent = DevOpsAgent()
        result = await agent.run(AgentContext(requirements="test"))
        assert not result.success


class TestPerformanceAgent:
    @pytest.mark.asyncio
    async def test_role(self) -> None:
        agent = PerformanceAgent()
        assert agent.role == AgentRole.PERFORMANCE

    @pytest.mark.asyncio
    async def test_detects_blocking_sleep(self, context_with_code: AgentContext) -> None:
        agent = PerformanceAgent()
        result = await agent.run(context_with_code)
        assert result.success
        issues = result.output["findings"]
        sleep_issues = [f for f in issues if f.get("category") == "async"]
        assert len(sleep_issues) > 0

    @pytest.mark.asyncio
    async def test_returns_recommendations(self, context_with_code: AgentContext) -> None:
        agent = PerformanceAgent()
        result = await agent.run(context_with_code)
        assert len(result.output["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_returns_score(self, context_with_code: AgentContext) -> None:
        agent = PerformanceAgent()
        result = await agent.run(context_with_code)
        assert 0 <= result.output["score"] <= 100


class TestAccessibilityAgent:
    @pytest.mark.asyncio
    async def test_role(self) -> None:
        agent = AccessibilityAgent()
        assert agent.role == AgentRole.ACCESSIBILITY

    @pytest.mark.asyncio
    async def test_detects_issues(self, context_with_code: AgentContext) -> None:
        agent = AccessibilityAgent()
        result = await agent.run(context_with_code)
        assert result.success
        assert result.output["total_issues"] > 0

    @pytest.mark.asyncio
    async def test_wcag_compliance(self, context_with_code: AgentContext) -> None:
        agent = AccessibilityAgent()
        result = await agent.run(context_with_code)
        assert "wcag_compliance" in result.output

    @pytest.mark.asyncio
    async def test_empty_when_no_frontend(self) -> None:
        agent = AccessibilityAgent()
        ctx = AgentContext(
            requirements="Backend only",
            code_files={"server.py": "import fastapi"},
        )
        result = await agent.run(ctx)
        assert result.success
        assert result.output["findings"] == []
