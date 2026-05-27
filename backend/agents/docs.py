"""Documentation agent — generates project documentation from code."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class DocsAgent(BaseAgent):
    """Generates comprehensive documentation for the project."""

    def __init__(self) -> None:
        super().__init__(AgentRole.DOCS)

    async def execute(self, context: AgentContext) -> AgentResult:
        architecture = context.architecture
        code_files = context.code_files

        docs = self._generate_docs(architecture, code_files, context.requirements)
        context.documentation = docs

        return AgentResult(
            agent_role=self.role,
            success=True,
            output={
                "documents_generated": list(docs.keys()),
                "total_sections": sum(doc.count("##") for doc in docs.values()),
            },
        )

    def _generate_docs(
        self,
        architecture: dict,
        code_files: dict[str, str],
        requirements: str,
    ) -> dict[str, str]:
        """Produce markdown documentation artifacts."""
        docs: dict[str, str] = {}

        docs["README.md"] = self._generate_readme(architecture, requirements)
        docs["API.md"] = self._generate_api_docs(code_files)
        docs["ARCHITECTURE.md"] = self._generate_architecture_doc(architecture)

        return docs

    @staticmethod
    def _generate_readme(architecture: dict, requirements: str) -> str:
        components = architecture.get("components", [])
        tech = architecture.get("tech_stack", {})

        sections = [
            "# Project Documentation\n",
            "## Overview\n",
            f"{requirements[:300]}\n",
            "## Components\n",
        ]

        for comp in components:
            sections.append(f"- **{comp['name']}** ({comp['type']}): {comp['description']}\n")

        sections.append("\n## Tech Stack\n")
        for category, items in tech.items():
            if items:
                sections.append(f"- **{category.title()}**: {', '.join(items)}\n")

        sections.extend(
            [
                "\n## Getting Started\n",
                "1. Clone the repository\n",
                "2. Install dependencies: `pip install -r requirements.txt`\n",
                "3. Copy `.env.example` to `.env` and configure\n",
                "4. Run the application: `uvicorn backend.main:app --reload`\n",
            ]
        )

        return "\n".join(sections)

    @staticmethod
    def _generate_api_docs(code_files: dict[str, str]) -> str:
        sections = ["# API Documentation\n\n"]

        for filepath, content in code_files.items():
            if "router" in content.lower() or "endpoint" in content.lower():
                sections.append(f"## {filepath}\n\n")
                for line in content.splitlines():
                    if line.strip().startswith(("@router.", "@app.")):
                        sections.append(f"- `{line.strip()}`\n")
                sections.append("\n")

        if len(sections) == 1:
            sections.append("No API endpoints detected.\n")

        return "".join(sections)

    @staticmethod
    def _generate_architecture_doc(architecture: dict) -> str:
        sections = [
            "# Architecture Documentation\n\n",
            "## System Components\n\n",
        ]

        for comp in architecture.get("components", []):
            sections.append(f"### {comp['name']}\n")
            sections.append(f"- **Type**: {comp['type']}\n")
            sections.append(f"- **Description**: {comp['description']}\n\n")

        patterns = architecture.get("patterns", [])
        if patterns:
            sections.append("## Design Patterns\n\n")
            for p in patterns:
                sections.append(f"- {p}\n")

        return "".join(sections)
