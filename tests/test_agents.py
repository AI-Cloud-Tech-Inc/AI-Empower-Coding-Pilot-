"""Tests for the agent system."""

from __future__ import annotations

import pytest

from backend.agents.architect import ArchitectAgent
from backend.agents.base import AgentContext, AgentRole
from backend.agents.coder import CoderAgent
from backend.agents.docs import DocsAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.security import SecurityAgent
from backend.agents.tester import TesterAgent


@pytest.mark.asyncio
async def test_architect_agent_success() -> None:
    agent = ArchitectAgent()
    ctx = AgentContext(requirements="Build a REST API with database")
    result = await agent.run(ctx)

    assert result.success is True
    assert result.agent_role == AgentRole.ARCHITECT
    assert "architecture" in result.output
    assert len(ctx.architecture["components"]) > 0


@pytest.mark.asyncio
async def test_architect_agent_no_requirements() -> None:
    agent = ArchitectAgent()
    ctx = AgentContext(requirements="")
    result = await agent.run(ctx)

    assert result.success is False


@pytest.mark.asyncio
async def test_coder_agent_success() -> None:
    agent = CoderAgent()
    ctx = AgentContext(requirements="test")
    ctx.architecture = {
        "components": [{"name": "api", "type": "service", "description": "API"}],
    }
    result = await agent.run(ctx)

    assert result.success is True
    assert result.agent_role == AgentRole.CODER
    assert len(ctx.code_files) > 0


@pytest.mark.asyncio
async def test_coder_agent_no_architecture() -> None:
    agent = CoderAgent()
    ctx = AgentContext(requirements="test")
    result = await agent.run(ctx)

    assert result.success is False


@pytest.mark.asyncio
async def test_tester_agent() -> None:
    agent = TesterAgent()
    ctx = AgentContext(requirements="test")
    ctx.code_files = {"main.py": "def hello():\n    return 'hi'\n"}
    result = await agent.run(ctx)

    assert result.success is True
    assert result.agent_role == AgentRole.TESTER
    assert ctx.test_results["total_tests"] > 0


@pytest.mark.asyncio
async def test_security_agent_clean() -> None:
    agent = SecurityAgent()
    ctx = AgentContext(requirements="test")
    ctx.code_files = {"clean.py": "import os\nx = os.getenv('KEY')\n"}
    result = await agent.run(ctx)

    assert result.success is True
    assert result.output["total_findings"] == 0


@pytest.mark.asyncio
async def test_security_agent_finds_issues() -> None:
    agent = SecurityAgent()
    ctx = AgentContext(requirements="test")
    ctx.code_files = {"bad.py": "password = 'secret123'\neval(input())\n"}
    result = await agent.run(ctx)

    assert result.output["total_findings"] > 0


@pytest.mark.asyncio
async def test_docs_agent() -> None:
    agent = DocsAgent()
    ctx = AgentContext(requirements="Build an API")
    ctx.architecture = {"components": [], "tech_stack": {}, "patterns": []}
    ctx.code_files = {"app.py": "@router.get('/test')\nasync def test(): pass\n"}
    result = await agent.run(ctx)

    assert result.success is True
    assert "README.md" in ctx.documentation


@pytest.mark.asyncio
async def test_reviewer_agent() -> None:
    agent = ReviewerAgent()
    ctx = AgentContext(requirements="test")
    ctx.code_files = {"ok.py": '"""Module."""\nx = 1\n'}
    result = await agent.run(ctx)

    assert result.success is True
    assert result.agent_role == AgentRole.REVIEWER
