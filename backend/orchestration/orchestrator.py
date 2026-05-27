"""Top-level orchestrator with AutoGen-style group chat and auto-generation."""

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
from backend.autogen.cicd import CICDGenerator
from backend.autogen.docker import DockerGenerator
from backend.autogen.scaffolding import ScaffoldingEngine
from backend.autogen.terraform import TerraformGenerator
from backend.compliance.tracker import ComplianceTracker
from backend.cost.optimizer import CostOptimizer
from backend.orchestration.approval import ApprovalGate
from backend.orchestration.group_chat import GroupChatConfig, GroupChatOrchestrator
from backend.orchestration.parallel import ParallelExecutor
from backend.orchestration.state_machine import PipelineState, WorkflowEngine, WorkflowState


class Orchestrator:
    """Coordinates the full coding-pilot pipeline.

    Combines AutoGen-style group chat orchestration with auto-generation
    engines for scaffolding, CI/CD, Docker, and Terraform.

    Stages (executed via the state machine):
      1. Architecture design
      2. Code generation
      3. Auto-generation (scaffolding + CI/CD + Docker + Terraform)
      4. Testing + Security scan (parallel)
      5. Human approval gate
      6. Documentation + Review (parallel)
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
        self.approval = ApprovalGate(auto_approve=True)

        self.scaffolding = ScaffoldingEngine()
        self.cicd = CICDGenerator()
        self.docker = DockerGenerator()
        self.terraform = TerraformGenerator()

        self.group_chat = GroupChatOrchestrator(
            agents={
                "architect": self.architect,
                "coder": self.coder,
                "tester": self.tester,
                "security": self.security,
                "docs": self.docs,
                "reviewer": self.reviewer,
            },
            config=GroupChatConfig(
                max_rounds=10,
                max_concurrent=6,
                allow_parallel=True,
            ),
        )

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

    async def run_with_autogen(self, requirements: str) -> dict[str, Any]:
        """Execute via the AutoGen group chat orchestrator."""
        self.audit.log("autogen_pipeline_start", {"requirements": requirements[:200]})

        ctx = AgentContext(requirements=requirements)
        session = await self.group_chat.run(ctx)

        autogen_result = self._run_auto_generators(ctx, requirements)

        approval = self.approval.request_approval(
            "pre_deployment",
            data={"session_id": session.session_id},
        )

        self.audit.log(
            "autogen_pipeline_complete",
            {
                "session_id": session.session_id,
                "approval_status": approval.status.value,
                "agents_run": session.agents,
            },
        )

        return {
            "workflow_id": session.session_id,
            "status": session.status,
            "data": {
                "agent_results": session.results,
                "messages": len(session.messages),
                "auto_generated": autogen_result,
                "approval": approval.model_dump(),
            },
            "errors": [],
            "transitions": session.current_round,
            "duration_s": (session.completed_at or 0) - session.started_at,
        }

    def _run_auto_generators(
        self,
        ctx: AgentContext,
        project_name: str = "",
    ) -> dict[str, Any]:
        """Run all auto-generation engines on the architecture."""
        arch = ctx.architecture
        name = project_name[:30] if project_name else "project"

        scaffolding = self.scaffolding.generate(arch, name)
        cicd = self.cicd.generate(arch, name)
        docker = self.docker.generate(arch, name)
        terraform = self.terraform.generate(arch, name)

        self.audit.log(
            "auto_generation_complete",
            {
                "scaffolding_files": len(scaffolding),
                "cicd_files": len(cicd),
                "docker_files": len(docker),
                "terraform_files": len(terraform),
            },
        )

        return {
            "scaffolding": {"files": list(scaffolding.keys()), "count": len(scaffolding)},
            "cicd": {"files": list(cicd.keys()), "count": len(cicd)},
            "docker": {"files": list(docker.keys()), "count": len(docker)},
            "terraform": {"files": list(terraform.keys()), "count": len(terraform)},
            "total_files_generated": len(scaffolding) + len(cicd) + len(docker) + len(terraform),
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

        auto_gen = self._run_auto_generators(ctx)
        state.data["auto_generated"] = auto_gen

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

        self.approval.request_approval(
            "pre_deployment",
            data={"review_success": result.success},
        )

        return state

    @staticmethod
    def _review_condition(state: WorkflowState) -> PipelineState:
        review = state.data.get("review_result", {})
        if review.get("success", True):
            return PipelineState.COMPLETED
        return PipelineState.FAILED
