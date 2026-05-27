"""Top-level orchestrator that wires agents into a LangGraph workflow."""

from __future__ import annotations

from typing import Any

from backend.agents.architect import ArchitectAgent
from backend.agents.base import AgentContext
from backend.agents.coder import CoderAgent
from backend.agents.docs import DocsAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.security import SecurityAgent
from backend.agents.tester import TesterAgent
from backend.audit.logger import AuditLogger
from backend.compliance.tracker import ComplianceTracker
from backend.cost.optimizer import CostOptimizer
from backend.orchestration.parallel import ParallelExecutor
from backend.orchestration.state_machine import PipelineState, WorkflowEngine, WorkflowState


class Orchestrator:
    """Coordinates the full coding-pilot pipeline.

    Stages (executed via the state machine):
      1. Architecture design
      2. Code generation
      3. Testing + Security scan  (parallel)
      4. Documentation + Review    (parallel)
    """

    def __init__(self) -> None:
        self.architect = ArchitectAgent()
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.security = SecurityAgent()
        self.docs = DocsAgent()
        self.reviewer = ReviewerAgent()

        self.parallel = ParallelExecutor()
        self.audit = AuditLogger()
        self.compliance = ComplianceTracker()
        self.cost = CostOptimizer()

        self.engine = self._build_workflow()

    def _build_workflow(self) -> WorkflowEngine:
        engine = WorkflowEngine()

        engine.add_node(PipelineState.INIT, self._node_init)
        engine.add_node(PipelineState.ARCHITECTURE, self._node_architecture)
        engine.add_node(PipelineState.CODING, self._node_coding)
        engine.add_node(PipelineState.TESTING, self._node_testing)
        engine.add_node(PipelineState.SECURITY_SCAN, self._node_security)
        engine.add_node(PipelineState.DOCUMENTATION, self._node_docs)
        engine.add_node(PipelineState.REVIEW, self._node_review)

        engine.add_edge(PipelineState.INIT, PipelineState.ARCHITECTURE)
        engine.add_edge(PipelineState.ARCHITECTURE, PipelineState.CODING)
        engine.add_edge(PipelineState.CODING, PipelineState.TESTING)
        engine.add_edge(PipelineState.TESTING, PipelineState.SECURITY_SCAN)
        engine.add_edge(PipelineState.SECURITY_SCAN, PipelineState.DOCUMENTATION)
        engine.add_edge(PipelineState.DOCUMENTATION, PipelineState.REVIEW)

        engine.add_conditional_edge(PipelineState.REVIEW, self._review_condition)

        engine.set_entry_point(PipelineState.INIT)
        return engine

    async def run(self, requirements: str) -> dict[str, Any]:
        """Execute the full pipeline for the given requirements."""
        self.audit.log("pipeline_start", {"requirements": requirements[:200]})

        result = await self.engine.run({"requirements": requirements})

        self.audit.log(
            "pipeline_complete",
            {
                "workflow_id": result.workflow_id,
                "state": result.current_state.value,
                "errors": result.errors,
            },
        )

        return {
            "workflow_id": result.workflow_id,
            "status": result.current_state.value,
            "data": result.data,
            "errors": result.errors,
            "transitions": len(result.history),
            "duration_s": (result.completed_at or 0) - result.started_at,
        }

    # ---- node handlers ----

    async def _node_init(self, state: WorkflowState) -> WorkflowState:
        requirements = state.data.get("requirements", "")
        state.data["context"] = AgentContext(requirements=requirements).model_dump()
        return state

    async def _node_architecture(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.architect.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["architecture_result"] = result.model_dump()
        self.cost.record_tokens(result.tokens_used)
        if not result.success:
            state.errors.extend(result.errors)
        return state

    async def _node_coding(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.coder.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["coding_result"] = result.model_dump()
        self.cost.record_tokens(result.tokens_used)
        if not result.success:
            state.errors.extend(result.errors)
        return state

    async def _node_testing(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.tester.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["testing_result"] = result.model_dump()
        self.cost.record_tokens(result.tokens_used)
        return state

    async def _node_security(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.security.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["security_result"] = result.model_dump()
        self.compliance.check_results(result.output)
        return state

    async def _node_docs(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.docs.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["docs_result"] = result.model_dump()
        return state

    async def _node_review(self, state: WorkflowState) -> WorkflowState:
        ctx = AgentContext(**state.data["context"])
        result = await self.reviewer.run(ctx)
        state.data["context"] = ctx.model_dump()
        state.data["review_result"] = result.model_dump()
        return state

    @staticmethod
    def _review_condition(state: WorkflowState) -> PipelineState:
        review = state.data.get("review_result", {})
        if review.get("success", True):
            return PipelineState.COMPLETED
        return PipelineState.FAILED
