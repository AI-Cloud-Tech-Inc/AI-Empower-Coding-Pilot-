"""Performance agent — analyses code for performance issues and suggests optimizations."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class PerformanceAgent(BaseAgent):
    """Analyses generated code for performance bottlenecks and optimizations."""

    def __init__(self) -> None:
        super().__init__(AgentRole.PERFORMANCE)

    async def execute(self, context: AgentContext) -> AgentResult:
        code_files = context.code_files
        if not code_files:
            return AgentResult(
                agent_role=self.role,
                success=True,
                output={"message": "No code files to analyse", "findings": []},
            )

        findings = self._analyse_performance(code_files, context.architecture)
        context.metadata["performance"] = findings

        return AgentResult(
            agent_role=self.role,
            success=True,
            output=findings,
            tokens_used=0,
        )

    def _analyse_performance(self, code_files: dict[str, str], architecture: dict) -> dict:
        findings: list[dict] = []
        recommendations: list[str] = []

        for path, content in code_files.items():
            lines = content.split("\n") if isinstance(content, str) else []

            if "SELECT *" in content.upper():
                findings.append(
                    {
                        "file": path,
                        "severity": "warning",
                        "issue": "SELECT * detected — specify columns explicitly",
                        "category": "database",
                    }
                )

            if "time.sleep" in content:
                findings.append(
                    {
                        "file": path,
                        "severity": "warning",
                        "issue": "Blocking sleep in async context — use asyncio.sleep",
                        "category": "async",
                    }
                )

            if len(lines) > 500:
                findings.append(
                    {
                        "file": path,
                        "severity": "info",
                        "issue": f"Large file ({len(lines)} lines) — consider splitting",
                        "category": "maintainability",
                    }
                )

            for i, line in enumerate(lines):
                if "for " in line and "for " in "".join(lines[max(0, i - 5) : i]):
                    findings.append(
                        {
                            "file": path,
                            "severity": "warning",
                            "issue": f"Nested loop detected near line {i + 1}",
                            "category": "complexity",
                        }
                    )
                    break

        components = architecture.get("components", [])
        has_db = any(c.get("type") == "infrastructure" for c in components)

        if has_db:
            recommendations.append("Enable database connection pooling")
            recommendations.append("Add query result caching with Redis")

        recommendations.extend(
            [
                "Implement response compression (gzip/brotli)",
                "Add CDN for static assets",
                "Enable HTTP/2 for multiplexed requests",
            ]
        )

        return {
            "findings": findings,
            "total_issues": len(findings),
            "recommendations": recommendations,
            "score": max(0, 100 - len(findings) * 10),
        }
