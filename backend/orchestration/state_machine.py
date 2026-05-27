"""LangGraph-inspired state machine for multi-agent workflow orchestration."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PipelineState(StrEnum):
    """States in the coding-pilot workflow."""

    INIT = "init"
    ARCHITECTURE = "architecture"
    CODING = "coding"
    TESTING = "testing"
    SECURITY_SCAN = "security_scan"
    PARALLEL_ANALYSIS = "parallel_analysis"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


class StateTransition(BaseModel):
    """Record of a single state transition."""

    from_state: PipelineState
    to_state: PipelineState
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    """Full mutable state carried through the graph."""

    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_state: PipelineState = PipelineState.INIT
    history: list[StateTransition] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    started_at: float = Field(default_factory=time.time)
    completed_at: float | None = None


NodeFn = Callable[[WorkflowState], Awaitable[WorkflowState]]
ConditionFn = Callable[[WorkflowState], PipelineState]


class WorkflowEngine:
    """Directed-graph execution engine inspired by LangGraph.

    Nodes are async functions that receive and return ``WorkflowState``.
    Edges define transitions; conditional edges choose the next node at
    runtime based on the state.
    """

    def __init__(self) -> None:
        self._nodes: dict[PipelineState, NodeFn] = {}
        self._edges: dict[PipelineState, PipelineState] = {}
        self._conditional_edges: dict[PipelineState, ConditionFn] = {}
        self._entry_point: PipelineState = PipelineState.INIT

    def add_node(self, state: PipelineState, fn: NodeFn) -> None:
        self._nodes[state] = fn

    def add_edge(self, from_state: PipelineState, to_state: PipelineState) -> None:
        self._edges[from_state] = to_state

    def add_conditional_edge(self, from_state: PipelineState, condition: ConditionFn) -> None:
        self._conditional_edges[from_state] = condition

    def set_entry_point(self, state: PipelineState) -> None:
        self._entry_point = state

    async def run(self, initial_data: dict[str, Any] | None = None) -> WorkflowState:
        """Execute the workflow graph from the entry point to completion."""
        state = WorkflowState(current_state=self._entry_point, data=initial_data or {})

        max_steps = 50
        step = 0

        while state.current_state not in (PipelineState.COMPLETED, PipelineState.FAILED):
            step += 1
            if step > max_steps:
                state.errors.append("Max steps exceeded — possible infinite loop")
                state.current_state = PipelineState.FAILED
                break

            current = state.current_state
            node_fn = self._nodes.get(current)

            if node_fn is None:
                state.errors.append(f"No handler registered for state {current.value}")
                state.current_state = PipelineState.FAILED
                break

            state = await node_fn(state)

            next_state = self._resolve_next(current, state)
            if next_state is None:
                state.errors.append(f"No transition defined from {current.value}")
                state.current_state = PipelineState.FAILED
                break

            transition = StateTransition(from_state=current, to_state=next_state)
            state.history.append(transition)
            state.current_state = next_state

        state.completed_at = time.time()
        return state

    def _resolve_next(self, current: PipelineState, state: WorkflowState) -> PipelineState | None:
        if current in self._conditional_edges:
            return self._conditional_edges[current](state)
        return self._edges.get(current)
