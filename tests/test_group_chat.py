"""Tests for AutoGen-style group chat orchestration."""

from __future__ import annotations

import pytest

from backend.agents.architect import ArchitectAgent
from backend.agents.base import AgentContext
from backend.agents.coder import CoderAgent
from backend.agents.tester import TesterAgent
from backend.orchestration.group_chat import GroupChatConfig, GroupChatOrchestrator


@pytest.mark.asyncio
async def test_group_chat_runs() -> None:
    agents = {
        "architect": ArchitectAgent(),
        "coder": CoderAgent(),
    }
    orchestrator = GroupChatOrchestrator(agents)
    ctx = AgentContext(requirements="Build a REST API")

    session = await orchestrator.run(ctx, stages=[["architect"], ["coder"]])

    assert session.status == "completed"
    assert session.completed_at is not None
    assert len(session.messages) > 0
    assert "architect" in session.results
    assert "coder" in session.results


@pytest.mark.asyncio
async def test_group_chat_parallel_stage() -> None:
    agents = {
        "architect": ArchitectAgent(),
        "coder": CoderAgent(),
        "tester": TesterAgent(),
    }
    config = GroupChatConfig(allow_parallel=True, max_concurrent=3)
    orchestrator = GroupChatOrchestrator(agents, config)
    ctx = AgentContext(requirements="Build a REST API with tests")

    session = await orchestrator.run(ctx, stages=[["architect"], ["coder", "tester"]])

    assert session.status == "completed"
    assert len(session.results) >= 2


@pytest.mark.asyncio
async def test_group_chat_session_tracking() -> None:
    agents = {"architect": ArchitectAgent()}
    orchestrator = GroupChatOrchestrator(agents)
    ctx = AgentContext(requirements="test")

    session = await orchestrator.run(ctx, stages=[["architect"]])

    retrieved = orchestrator.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id

    sessions_list = orchestrator.list_sessions()
    assert len(sessions_list) == 1
