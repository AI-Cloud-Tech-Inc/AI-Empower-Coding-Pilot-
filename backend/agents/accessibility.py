"""Accessibility agent — checks generated code for WCAG compliance and a11y best practices."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class AccessibilityAgent(BaseAgent):
    """Scans frontend code for accessibility issues and WCAG 2.1 compliance."""

    def __init__(self) -> None:
        super().__init__(AgentRole.ACCESSIBILITY)

    async def execute(self, context: AgentContext) -> AgentResult:
        code_files = context.code_files
        frontend_files = {
            k: v for k, v in code_files.items() if k.endswith((".tsx", ".jsx", ".html", ".vue"))
        }

        if not frontend_files:
            return AgentResult(
                agent_role=self.role,
                success=True,
                output={"message": "No frontend files to scan", "findings": []},
            )

        findings = self._scan_accessibility(frontend_files)
        context.metadata["accessibility"] = findings

        return AgentResult(
            agent_role=self.role,
            success=True,
            output=findings,
            tokens_used=0,
        )

    def _scan_accessibility(self, files: dict[str, str]) -> dict:
        findings: list[dict] = []

        for path, content in files.items():
            content_str = content if isinstance(content, str) else ""

            if "<img" in content_str and "alt=" not in content_str:
                findings.append(
                    {
                        "file": path,
                        "rule": "WCAG 1.1.1",
                        "severity": "error",
                        "issue": "Image missing alt attribute",
                    }
                )

            if "<button" in content_str and "aria-label" not in content_str:
                if ">" not in content_str.split("<button")[1].split("</button>")[0]:
                    findings.append(
                        {
                            "file": path,
                            "rule": "WCAG 4.1.2",
                            "severity": "warning",
                            "issue": "Button may lack accessible name",
                        }
                    )

            if "onClick" in content_str and "<div" in content_str:
                findings.append(
                    {
                        "file": path,
                        "rule": "WCAG 2.1.1",
                        "severity": "warning",
                        "issue": "Clickable div — use button or anchor for keyboard access",
                    }
                )

            if "color:" in content_str or "bg-" in content_str:
                findings.append(
                    {
                        "file": path,
                        "rule": "WCAG 1.4.3",
                        "severity": "info",
                        "issue": "Verify colour contrast ratio meets 4.5:1 minimum",
                    }
                )

            if "<form" in content_str and "aria-" not in content_str:
                findings.append(
                    {
                        "file": path,
                        "rule": "WCAG 1.3.1",
                        "severity": "warning",
                        "issue": "Form missing ARIA landmarks or labels",
                    }
                )

        wcag_levels = {
            "A": len([f for f in findings if f["severity"] == "error"]) == 0,
            "AA": len([f for f in findings if f["severity"] in ("error", "warning")]) <= 2,
            "AAA": len(findings) == 0,
        }

        return {
            "findings": findings,
            "total_issues": len(findings),
            "wcag_compliance": wcag_levels,
            "score": max(0, 100 - len(findings) * 8),
        }
