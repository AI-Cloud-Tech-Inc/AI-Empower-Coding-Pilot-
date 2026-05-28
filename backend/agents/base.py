"""Base agent class that every specialised agent extends."""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(StrEnum):
    """Roles available in the multi-agent system."""

    ARCHITECT = "architect"
    CODER = "coder"
    TESTER = "tester"
    SECURITY = "security"
    DOCS = "docs"
    REVIEWER = "reviewer"
    DEVOPS = "devops"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"


class AgentContext(BaseModel):
    """Shared context passed between agents during a workflow."""

    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requirements: str = ""
    architecture: dict[str, Any] = Field(default_factory=dict)
    code_files: dict[str, str] = Field(default_factory=dict)
    test_results: dict[str, Any] = Field(default_factory=dict)
    security_findings: list[dict[str, Any]] = Field(default_factory=list)
    documentation: dict[str, str] = Field(default_factory=dict)
    review_comments: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Standardised result returned by every agent."""

    agent_role: AgentRole
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    tokens_used: int = 0
    execution_time_ms: float = 0.0


class BaseAgent(ABC):
    """Abstract base for all agents in the orchestration pipeline."""

    def __init__(self, role: AgentRole) -> None:
        self.role = role
        self.agent_id = str(uuid.uuid4())

    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's task, recording timing and catching errors."""
        start = time.perf_counter()
        try:
            result = await self.execute(context)
            result.execution_time_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return AgentResult(
                agent_role=self.role,
                success=False,
                errors=[str(exc)],
                execution_time_ms=elapsed,
            )

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Subclasses implement domain-specific logic here."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} role={self.role.value}>"
