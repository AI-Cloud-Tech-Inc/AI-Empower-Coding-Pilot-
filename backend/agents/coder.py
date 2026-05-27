"""Coder agent — generates production-ready code from architecture plans."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class CoderAgent(BaseAgent):
    """Transforms an architecture plan into code files."""

    def __init__(self) -> None:
        super().__init__(AgentRole.CODER)

    async def execute(self, context: AgentContext) -> AgentResult:
        architecture = context.architecture
        if not architecture:
            return AgentResult(
                agent_role=self.role,
                success=False,
                errors=["No architecture provided — run the architect agent first"],
            )

        generated_files = self._generate_code(architecture)
        context.code_files.update(generated_files)

        return AgentResult(
            agent_role=self.role,
            success=True,
            output={
                "files_generated": list(generated_files.keys()),
                "total_lines": sum(f.count("\n") + 1 for f in generated_files.values()),
            },
        )

    def _generate_code(self, architecture: dict) -> dict[str, str]:
        """Generate boilerplate code files based on the architecture."""
        files: dict[str, str] = {}
        components = architecture.get("components", [])

        for component in components:
            comp_name = component.get("name", "module")
            comp_type = component.get("type", "service")

            if comp_type == "service":
                files[f"{comp_name}/main.py"] = self._service_template(comp_name)
                files[f"{comp_name}/__init__.py"] = f'"""{comp_name} service."""\n'
            elif comp_type == "application":
                files[f"{comp_name}/App.tsx"] = self._frontend_template(comp_name)
            elif comp_type == "infrastructure":
                files[f"{comp_name}/schema.sql"] = self._database_template(comp_name)

        return files

    @staticmethod
    def _service_template(name: str) -> str:
        return (
            f'"""{name} service implementation."""\n\n'
            f"from fastapi import APIRouter\n\n"
            f'router = APIRouter(prefix="/{name}", tags=["{name}"])\n\n\n'
            f'@router.get("/health")\n'
            f"async def health_check() -> dict:\n"
            f'    return {{"service": "{name}", "status": "healthy"}}\n'
        )

    @staticmethod
    def _frontend_template(name: str) -> str:
        return (
            f"import React from 'react';\n\n"
            f"export default function {name.title().replace('_', '')}() {{\n"
            f"  return (\n"
            f'    <div className="p-4">\n'
            f"      <h1>{name.replace('_', ' ').title()}</h1>\n"
            f"    </div>\n"
            f"  );\n"
            f"}}\n"
        )

    @staticmethod
    def _database_template(name: str) -> str:
        return (
            f"-- {name} schema\n"
            f"CREATE TABLE IF NOT EXISTS {name} (\n"
            f"    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            f"    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),\n"
            f"    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()\n"
            f");\n"
        )
