"""Security agent — scans code for vulnerabilities and compliance issues."""

from __future__ import annotations

import re

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class SecurityAgent(BaseAgent):
    """Performs static security analysis on generated code."""

    SENSITIVE_PATTERNS: list[tuple[str, str, str]] = [
        (
            r"(?i)(password|secret|token|api_key)\s*=\s*['\"][^'\"]+['\"]",
            "HARDCODED_SECRET",
            "high",
        ),
        (r"eval\s*\(", "EVAL_USAGE", "critical"),
        (r"exec\s*\(", "EXEC_USAGE", "critical"),
        (r"subprocess\.call\(.*shell\s*=\s*True", "SHELL_INJECTION", "critical"),
        (r"(?i)import\s+pickle", "UNSAFE_DESERIALIZATION", "high"),
        (r"(?i)#\s*TODO.*security", "SECURITY_TODO", "medium"),
        (r"(?i)(http://)", "INSECURE_HTTP", "medium"),
        (r"verify\s*=\s*False", "SSL_VERIFICATION_DISABLED", "high"),
    ]

    def __init__(self) -> None:
        super().__init__(AgentRole.SECURITY)

    async def execute(self, context: AgentContext) -> AgentResult:
        code_files = context.code_files
        if not code_files:
            return AgentResult(
                agent_role=self.role,
                success=True,
                output={"message": "No code files to scan"},
            )

        findings = self._scan_code(code_files)
        context.security_findings = findings

        critical_count = sum(1 for f in findings if f["severity"] == "critical")

        return AgentResult(
            agent_role=self.role,
            success=critical_count == 0,
            output={
                "total_findings": len(findings),
                "critical": critical_count,
                "high": sum(1 for f in findings if f["severity"] == "high"),
                "medium": sum(1 for f in findings if f["severity"] == "medium"),
                "findings": findings,
            },
            errors=[f"Found {critical_count} critical security issues"] if critical_count else [],
        )

    def _scan_code(self, code_files: dict[str, str]) -> list[dict]:
        """Run pattern-based security scans on all code files."""
        findings: list[dict] = []

        for filepath, content in code_files.items():
            for line_num, line in enumerate(content.splitlines(), start=1):
                for pattern, vuln_type, severity in self.SENSITIVE_PATTERNS:
                    if re.search(pattern, line):
                        findings.append(
                            {
                                "file": filepath,
                                "line": line_num,
                                "type": vuln_type,
                                "severity": severity,
                                "description": f"{vuln_type} detected in {filepath}:{line_num}",
                                "recommendation": self._recommendation(vuln_type),
                            }
                        )

        return findings

    @staticmethod
    def _recommendation(vuln_type: str) -> str:
        recommendations: dict[str, str] = {
            "HARDCODED_SECRET": "Move secrets to environment variables or a vault.",
            "EVAL_USAGE": "Replace eval() with safe alternatives like ast.literal_eval().",
            "EXEC_USAGE": "Avoid exec(); use structured function calls instead.",
            "SHELL_INJECTION": "Use subprocess with shell=False and a list of arguments.",
            "UNSAFE_DESERIALIZATION": "Use json or msgpack instead of pickle for untrusted data.",
            "SECURITY_TODO": "Address the security-related TODO before shipping.",
            "INSECURE_HTTP": "Use HTTPS instead of HTTP.",
            "SSL_VERIFICATION_DISABLED": "Enable SSL certificate verification.",
        }
        return recommendations.get(vuln_type, "Review and remediate this finding.")
