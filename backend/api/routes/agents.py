"""Agent management and status endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.agents import (
    AccessibilityAgent,
    ArchitectAgent,
    CoderAgent,
    DevOpsAgent,
    DocsAgent,
    PerformanceAgent,
    ReviewerAgent,
    SecurityAgent,
    TesterAgent,
)
from backend.api.schemas import AgentStatusResponse

router = APIRouter(prefix="/agents", tags=["agents"])

_AGENTS = [
    ArchitectAgent(),
    CoderAgent(),
    TesterAgent(),
    SecurityAgent(),
    DocsAgent(),
    ReviewerAgent(),
    DevOpsAgent(),
    PerformanceAgent(),
    AccessibilityAgent(),
]


@router.get("", response_model=list[AgentStatusResponse])
async def list_agents() -> list[AgentStatusResponse]:
    return [
        AgentStatusResponse(
            role=agent.role.value,
            agent_id=agent.agent_id,
            status="idle",
        )
        for agent in _AGENTS
    ]


@router.get("/{role}", response_model=AgentStatusResponse)
async def get_agent(role: str) -> AgentStatusResponse:
    for agent in _AGENTS:
        if agent.role.value == role:
            return AgentStatusResponse(
                role=agent.role.value,
                agent_id=agent.agent_id,
                status="idle",
            )
    return AgentStatusResponse(role=role, agent_id="", status="not_found")
