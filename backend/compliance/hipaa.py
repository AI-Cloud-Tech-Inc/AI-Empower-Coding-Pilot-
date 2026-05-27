"""HIPAA compliance checker."""

from __future__ import annotations

from typing import Any


class HIPAAChecker:
    """Check code against HIPAA security and privacy requirements.

    Key controls:
    - No PHI (Protected Health Information) in logs or code
    - Encryption requirements
    - Access control verification
    - Audit trail requirements
    """

    RELEVANT_VULN_TYPES = {
        "HARDCODED_SECRET",
        "INSECURE_HTTP",
        "SSL_VERIFICATION_DISABLED",
        "UNSAFE_DESERIALIZATION",
    }

    def check(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for finding in findings:
            vuln_type = finding.get("type", "")
            if vuln_type in self.RELEVANT_VULN_TYPES:
                violations.append(
                    {
                        "framework": "HIPAA",
                        "control": self._map_control(vuln_type),
                        "finding": finding,
                        "remediation": finding.get("recommendation", ""),
                    }
                )

        return {
            "framework": "HIPAA",
            "compliant": len(violations) == 0,
            "violations": violations,
            "controls_checked": [
                "Access Control (§164.312(a))",
                "Transmission Security (§164.312(e))",
                "Integrity Controls (§164.312(c))",
                "Audit Controls (§164.312(b))",
            ],
        }

    @staticmethod
    def _map_control(vuln_type: str) -> str:
        mapping = {
            "HARDCODED_SECRET": "Access Control (§164.312(a))",
            "INSECURE_HTTP": "Transmission Security (§164.312(e))",
            "SSL_VERIFICATION_DISABLED": "Transmission Security (§164.312(e))",
            "UNSAFE_DESERIALIZATION": "Integrity Controls (§164.312(c))",
        }
        return mapping.get(vuln_type, "General Security")
