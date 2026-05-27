"""SOC 2 compliance checker."""

from __future__ import annotations

from typing import Any


class SOC2Checker:
    """Check code against SOC 2 Trust Service Criteria.

    Criteria:
    - Security: Protection against unauthorized access
    - Availability: System availability for operation
    - Processing Integrity: Complete and accurate processing
    - Confidentiality: Protection of confidential information
    - Privacy: Personal information handling
    """

    RELEVANT_VULN_TYPES = {
        "HARDCODED_SECRET",
        "EVAL_USAGE",
        "EXEC_USAGE",
        "SHELL_INJECTION",
        "UNSAFE_DESERIALIZATION",
        "SSL_VERIFICATION_DISABLED",
        "INSECURE_HTTP",
    }

    def check(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for finding in findings:
            vuln_type = finding.get("type", "")
            if vuln_type in self.RELEVANT_VULN_TYPES:
                violations.append(
                    {
                        "framework": "SOC2",
                        "criterion": self._map_criterion(vuln_type),
                        "finding": finding,
                        "remediation": finding.get("recommendation", ""),
                    }
                )

        return {
            "framework": "SOC2",
            "compliant": len(violations) == 0,
            "violations": violations,
            "criteria_checked": [
                "CC6.1 — Logical and Physical Access Controls",
                "CC6.6 — System Boundary Security",
                "CC6.7 — Restrict Transmission of Data",
                "CC7.2 — Monitor System Components",
                "CC8.1 — Change Management",
            ],
        }

    @staticmethod
    def _map_criterion(vuln_type: str) -> str:
        mapping = {
            "HARDCODED_SECRET": "CC6.1 — Logical and Physical Access Controls",
            "EVAL_USAGE": "CC8.1 — Change Management",
            "EXEC_USAGE": "CC8.1 — Change Management",
            "SHELL_INJECTION": "CC6.6 — System Boundary Security",
            "UNSAFE_DESERIALIZATION": "CC6.6 — System Boundary Security",
            "SSL_VERIFICATION_DISABLED": "CC6.7 — Restrict Transmission of Data",
            "INSECURE_HTTP": "CC6.7 — Restrict Transmission of Data",
        }
        return mapping.get(vuln_type, "General Security")
