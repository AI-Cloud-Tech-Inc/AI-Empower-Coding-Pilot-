"""DevOps agent — generates CI/CD pipelines, Docker configs, and deployment strategies."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class DevOpsAgent(BaseAgent):
    """Generates deployment configurations and infrastructure automation."""

    def __init__(self) -> None:
        super().__init__(AgentRole.DEVOPS)

    async def execute(self, context: AgentContext) -> AgentResult:
        architecture = context.architecture
        if not architecture:
            return AgentResult(
                agent_role=self.role,
                success=False,
                errors=["No architecture provided — run Architect agent first"],
            )

        devops_output = self._generate_devops_config(architecture, context.requirements)
        context.metadata["devops"] = devops_output

        return AgentResult(
            agent_role=self.role,
            success=True,
            output=devops_output,
            tokens_used=0,
        )

    def _generate_devops_config(self, architecture: dict, requirements: str) -> dict:
        components = architecture.get("components", [])
        has_api = any(c.get("type") == "service" for c in components)
        has_frontend = any(c.get("name") == "frontend" for c in components)
        has_db = any(c.get("type") == "infrastructure" for c in components)

        ci_stages = ["lint", "test", "build"]
        if has_api:
            ci_stages.append("api-integration-test")
        if has_frontend:
            ci_stages.append("e2e-test")
        ci_stages.extend(["security-scan", "deploy"])

        docker_services = []
        if has_api:
            docker_services.append({"name": "backend", "image": "python:3.11-slim", "port": 8000})
        if has_frontend:
            docker_services.append({"name": "frontend", "image": "node:20-alpine", "port": 3000})
        if has_db:
            docker_services.append(
                {"name": "postgres", "image": "postgres:16-alpine", "port": 5432}
            )
        docker_services.append({"name": "redis", "image": "redis:7-alpine", "port": 6379})

        return {
            "ci_pipeline": {
                "stages": ci_stages,
                "triggers": ["push", "pull_request"],
                "environment": {"python": "3.11", "node": "20"},
            },
            "docker_services": docker_services,
            "deployment": {
                "strategy": "blue-green",
                "health_check": "/api/health",
                "replicas": 2,
                "auto_scaling": {"min": 1, "max": 5, "cpu_threshold": 70},
            },
            "monitoring": {
                "metrics": ["cpu", "memory", "request_latency", "error_rate"],
                "alerts": ["high_cpu", "high_error_rate", "disk_full"],
                "dashboards": ["application", "infrastructure"],
            },
        }
