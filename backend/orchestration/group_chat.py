"""AutoGen-inspired group chat orchestration for multi-agent collaboration."""

from __future__ import annotations

import asyncio
import time
import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.base import AgentContext, AgentResult, BaseAgent


class MessageRole(StrEnum):
    """Who sent the message in the group chat."""

    SYSTEM = "system"
    AGENT = "agent"
    HUMAN = "human"


class ChatMessage(BaseModel):
    """A single message in the group chat."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = MessageRole.AGENT
    sender: str = ""
    content: str = ""
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GroupChatConfig(BaseModel):
    """Configuration for the group chat session."""

    max_rounds: int = 10
    max_concurrent: int = 6
    allow_parallel: bool = True
    require_approval: bool = False
    timeout_seconds: int = 300


class GroupChatSession(BaseModel):
    """State of a group chat session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[ChatMessage] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)
    current_round: int = 0
    status: str = "active"
    started_at: float = Field(default_factory=time.time)
    completed_at: float | None = None
    results: dict[str, Any] = Field(default_factory=dict)


class GroupChatOrchestrator:
    """AutoGen-style group chat that coordinates multiple agents.

    Agents communicate through a shared message history. The orchestrator
    manages turn-taking, parallel execution of independent agents, and
    aggregation of results.

    Execution stages:
      Stage 1: Architect (sequential — sets the foundation)
      Stage 2: Coder (sequential — depends on architecture)
      Stage 3: Tester + Security (parallel — independent analysis)
      Stage 4: Docs + Reviewer (parallel — independent outputs)
    """

    def __init__(
        self,
        agents: dict[str, BaseAgent],
        config: GroupChatConfig | None = None,
    ) -> None:
        self.agents = agents
        self.config = config or GroupChatConfig()
        self._sessions: dict[str, GroupChatSession] = {}

    async def run(
        self,
        context: AgentContext,
        stages: list[list[str]] | None = None,
    ) -> GroupChatSession:
        """Execute the group chat across stages.

        Each stage is a list of agent names to run. Agents within a stage
        run in parallel when ``config.allow_parallel`` is True.
        """
        session = GroupChatSession(agents=list(self.agents.keys()))
        self._sessions[session.session_id] = session

        session.messages.append(
            ChatMessage(
                role=MessageRole.SYSTEM,
                sender="orchestrator",
                content=f"Starting group chat with {len(self.agents)} agents",
                metadata={"requirements": context.requirements[:500]},
            )
        )

        if stages is None:
            stages = [
                ["architect"],
                ["coder"],
                ["tester", "security"],
                ["docs", "reviewer"],
            ]

        for stage_idx, stage_agents in enumerate(stages):
            session.current_round = stage_idx + 1

            session.messages.append(
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    sender="orchestrator",
                    content=f"Stage {stage_idx + 1}: Running {', '.join(stage_agents)}",
                )
            )

            if self.config.allow_parallel and len(stage_agents) > 1:
                results = await self._run_parallel(stage_agents, context)
            else:
                results = await self._run_sequential(stage_agents, context)

            for agent_name, result in results.items():
                session.results[agent_name] = result.model_dump()
                session.messages.append(
                    ChatMessage(
                        role=MessageRole.AGENT,
                        sender=agent_name,
                        content=self._summarize_result(result),
                        metadata={
                            "success": result.success,
                            "tokens_used": result.tokens_used,
                            "execution_time_ms": result.execution_time_ms,
                        },
                    )
                )

                if not result.success:
                    session.messages.append(
                        ChatMessage(
                            role=MessageRole.SYSTEM,
                            sender="orchestrator",
                            content=f"Agent {agent_name} reported errors: {result.errors}",
                        )
                    )

        session.status = "completed"
        session.completed_at = time.time()
        return session

    async def _run_parallel(
        self,
        agent_names: list[str],
        context: AgentContext,
    ) -> dict[str, AgentResult]:
        """Run multiple agents concurrently."""
        sem = asyncio.Semaphore(self.config.max_concurrent)

        async def _run_one(name: str) -> tuple[str, AgentResult]:
            async with sem:
                agent = self.agents[name]
                result = await agent.run(context)
                return name, result

        pairs = await asyncio.gather(
            *[_run_one(name) for name in agent_names if name in self.agents]
        )
        return dict(pairs)

    async def _run_sequential(
        self,
        agent_names: list[str],
        context: AgentContext,
    ) -> dict[str, AgentResult]:
        """Run agents one at a time."""
        results: dict[str, AgentResult] = {}
        for name in agent_names:
            if name not in self.agents:
                continue
            agent = self.agents[name]
            results[name] = await agent.run(context)
        return results

    @staticmethod
    def _summarize_result(result: AgentResult) -> str:
        if result.success:
            keys = list(result.output.keys())[:5]
            return f"Completed successfully. Output keys: {keys}"
        return f"Failed with errors: {result.errors}"

    def get_session(self, session_id: str) -> GroupChatSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[dict[str, Any]]:
        return [
            {
                "session_id": s.session_id,
                "status": s.status,
                "agents": s.agents,
                "rounds": s.current_round,
                "messages": len(s.messages),
                "started_at": s.started_at,
            }
            for s in self._sessions.values()
        ]
