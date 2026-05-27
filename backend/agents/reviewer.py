"""Reviewer agent — performs code review and quality checks."""

from __future__ import annotations

import re

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviews generated code for quality, style, and best practices."""

    def __init__(self) -> None:
        super().__init__(AgentRole.REVIEWER)

    async def execute(self, context: AgentContext) -> AgentResult:
        code_files = context.code_files
        if not code_files:
            return AgentResult(
                agent_role=self.role,
                success=True,
                output={"message": "No code to review"},
            )

        comments = self._review_code(code_files)
        context.review_comments = comments

        blocking = [c for c in comments if c["severity"] == "blocking"]

        return AgentResult(
            agent_role=self.role,
            success=len(blocking) == 0,
            output={
                "total_comments": len(comments),
                "blocking": len(blocking),
                "warnings": len([c for c in comments if c["severity"] == "warning"]),
                "suggestions": len([c for c in comments if c["severity"] == "suggestion"]),
                "comments": comments,
            },
            errors=[f"{len(blocking)} blocking issue(s) found"] if blocking else [],
        )

    def _review_code(self, code_files: dict[str, str]) -> list[dict]:
        """Run quality checks on all code files."""
        comments: list[dict] = []

        for filepath, content in code_files.items():
            comments.extend(self._check_file(filepath, content))

        return comments

    def _check_file(self, filepath: str, content: str) -> list[dict]:
        checks: list[dict] = []
        lines = content.splitlines()

        # Check file length
        if len(lines) > 500:
            checks.append(
                {
                    "file": filepath,
                    "line": 1,
                    "severity": "warning",
                    "message": f"File has {len(lines)} lines — consider splitting into modules.",
                }
            )

        for line_num, line in enumerate(lines, start=1):
            # Long lines
            if len(line) > 120:
                checks.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "severity": "suggestion",
                        "message": "Line exceeds 120 characters.",
                    }
                )

            # TODO / FIXME
            if re.search(r"(?i)\b(TODO|FIXME|HACK|XXX)\b", line):
                checks.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "severity": "warning",
                        "message": "Unresolved TODO/FIXME comment.",
                    }
                )

            # Bare except
            if re.search(r"except\s*:", line):
                checks.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "severity": "blocking",
                        "message": "Bare except clause — catch specific exceptions.",
                    }
                )

        # Docstring check for Python files
        if filepath.endswith(".py") and not content.strip().startswith(('"""', "'''")):
            checks.append(
                {
                    "file": filepath,
                    "line": 1,
                    "severity": "suggestion",
                    "message": "Module-level docstring is missing.",
                }
            )

        return checks
