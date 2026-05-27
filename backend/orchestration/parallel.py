"""Parallel execution engine for running multiple agents concurrently."""

from __future__ import annotations

import asyncio
from typing import Any

from backend.agents.base import AgentContext, AgentResult, BaseAgent
from backend.config import settings


class ParallelExecutor:
    """Run a set of agents in parallel with bounded concurrency."""

    def __init__(self, max_concurrency: int | None = None) -> None:
        self.max_concurrency = max_concurrency or settings.max_parallel_agents
        self._semaphore: asyncio.Semaphore | None = None

    async def execute(
        self,
        agents: list[BaseAgent],
        context: AgentContext,
    ) -> list[AgentResult]:
        """Run *agents* concurrently, returning results in the same order."""
        self._semaphore = asyncio.Semaphore(self.max_concurrency)

        tasks = [self._run_with_semaphore(agent, context) for agent in agents]
        return await asyncio.gather(*tasks)

    async def _run_with_semaphore(
        self,
        agent: BaseAgent,
        context: AgentContext,
    ) -> AgentResult:
        if self._semaphore is None:
            return await agent.run(context)
        async with self._semaphore:
            return await agent.run(context)

    async def execute_stages(
        self,
        stages: list[list[BaseAgent]],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Run groups of agents sequentially; within each group, run in parallel."""
        all_results: list[AgentResult] = []
        stage_summaries: list[dict] = []

        for idx, stage_agents in enumerate(stages):
            results = await self.execute(stage_agents, context)
            all_results.extend(results)

            stage_summaries.append(
                {
                    "stage": idx,
                    "agents": [a.role.value for a in stage_agents],
                    "success": all(r.success for r in results),
                    "errors": [e for r in results for e in r.errors],
                }
            )

            if not all(r.success for r in results):
                break

        return {
            "total_agents": sum(len(s) for s in stages),
            "stages_completed": len(stage_summaries),
            "all_success": all(s["success"] for s in stage_summaries),
            "stage_summaries": stage_summaries,
            "results": [r.model_dump() for r in all_results],
        }
