"""Architect agent — analyses requirements and produces system design."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class ArchitectAgent(BaseAgent):
    """Transforms natural-language requirements into an architecture plan."""

    def __init__(self) -> None:
        super().__init__(AgentRole.ARCHITECT)

    async def execute(self, context: AgentContext) -> AgentResult:
        requirements = context.requirements
        if not requirements:
            return AgentResult(
                agent_role=self.role,
                success=False,
                errors=["No requirements provided"],
            )

        architecture = self._design_architecture(requirements)
        context.architecture = architecture

        return AgentResult(
            agent_role=self.role,
            success=True,
            output={"architecture": architecture},
        )

    def _design_architecture(self, requirements: str) -> dict:
        """Generate architecture based on requirement analysis."""
        components: list[dict] = []
        patterns: list[str] = []
        tech_stack: dict[str, list[str]] = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "infrastructure": [],
        }

        req_lower = requirements.lower()

        # Detect API requirements
        if any(kw in req_lower for kw in ("api", "rest", "endpoint", "backend")):
            components.append(
                {"name": "api_layer", "type": "service", "description": "REST API layer"}
            )
            patterns.append("REST API")
            tech_stack["frameworks"].append("FastAPI")

        # Detect frontend requirements
        if any(kw in req_lower for kw in ("frontend", "ui", "dashboard", "web")):
            components.append(
                {"name": "frontend", "type": "application", "description": "Web dashboard"}
            )
            tech_stack["frameworks"].append("React")

        # Detect database requirements
        if any(kw in req_lower for kw in ("database", "storage", "persist", "data")):
            components.append(
                {"name": "database", "type": "infrastructure", "description": "Data persistence"}
            )
            tech_stack["databases"].append("PostgreSQL")

        # Detect authentication requirements
        if any(kw in req_lower for kw in ("auth", "login", "user", "security")):
            components.append(
                {"name": "auth_service", "type": "service", "description": "Authentication"}
            )
            patterns.append("JWT Authentication")

        # Default minimal architecture when nothing specific is detected
        if not components:
            components.append(
                {"name": "core_service", "type": "service", "description": "Core application"}
            )
            tech_stack["languages"].append("Python")

        return {
            "components": components,
            "patterns": patterns,
            "tech_stack": tech_stack,
            "requirements_summary": requirements[:500],
        }
