"""Tests for orchestration and state machine."""

from __future__ import annotations

import pytest

from backend.orchestration.orchestrator import Orchestrator
from backend.orchestration.state_machine import PipelineState, WorkflowEngine, WorkflowState


@pytest.mark.asyncio
async def test_workflow_engine_linear() -> None:
    engine = WorkflowEngine()

    async def init_node(state: WorkflowState) -> WorkflowState:
        state.data["step"] = "init"
        return state

    async def work_node(state: WorkflowState) -> WorkflowState:
        state.data["step"] = "work"
        return state

    engine.add_node(PipelineState.INIT, init_node)
    engine.add_node(PipelineState.ARCHITECTURE, work_node)

    engine.add_edge(PipelineState.INIT, PipelineState.ARCHITECTURE)
    engine.add_edge(PipelineState.ARCHITECTURE, PipelineState.COMPLETED)

    engine.set_entry_point(PipelineState.INIT)
    result = await engine.run()

    assert result.current_state == PipelineState.COMPLETED
    assert result.data["step"] == "work"
    assert len(result.history) == 2


@pytest.mark.asyncio
async def test_workflow_engine_conditional_edge() -> None:
    engine = WorkflowEngine()

    async def check_node(state: WorkflowState) -> WorkflowState:
        state.data["ok"] = True
        return state

    def condition(state: WorkflowState) -> PipelineState:
        if state.data.get("ok"):
            return PipelineState.COMPLETED
        return PipelineState.FAILED

    engine.add_node(PipelineState.INIT, check_node)
    engine.add_conditional_edge(PipelineState.INIT, condition)
    engine.set_entry_point(PipelineState.INIT)

    result = await engine.run()
    assert result.current_state == PipelineState.COMPLETED


@pytest.mark.asyncio
async def test_orchestrator_full_pipeline() -> None:
    orchestrator = Orchestrator()
    result = await orchestrator.run("Build a REST API with user authentication")

    assert result["status"] in ("completed", "failed")
    assert "workflow_id" in result
    assert result["transitions"] > 0
