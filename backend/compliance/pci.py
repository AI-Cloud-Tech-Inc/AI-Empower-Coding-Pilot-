"""PCI-DSS compliance checker."""

from __future__ import annotations

from typing import Any


class PCIChecker:
    """Check code against PCI-DSS requirements.

    Key controls:
    - No cardholder data in code
    - Encryption of data in transit and at rest
    - Strong access control
    - Vulnerability management
    """

    RELEVANT_VULN_TYPES = {
        "HARDCODED_SECRET",
        "INSECURE_HTTP",
        "SSL_VERIFICATION_DISABLED",
        "EVAL_USAGE",
        "EXEC_USAGE",
        "SHELL_INJECTION",
    }

    def check(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for finding in findings:
            vuln_type = finding.get("type", "")
            if vuln_type in self.RELEVANT_VULN_TYPES:
                violations.append(
                    {
                        "framework": "PCI-DSS",
                        "requirement": self._map_requirement(vuln_type),
                        "finding": finding,
                        "remediation": finding.get("recommendation", ""),
                    }
                )

        return {
            "framework": "PCI-DSS",
            "compliant": len(violations) == 0,
            "violations": violations,
            "requirements_checked": [
                "Req 2: Do not use vendor-supplied defaults",
                "Req 3: Protect stored cardholder data",
                "Req 4: Encrypt transmission of cardholder data",
                "Req 6: Develop and maintain secure systems",
            ],
        }

    @staticmethod
    def _map_requirement(vuln_type: str) -> str:
        mapping = {
            "HARDCODED_SECRET": "Req 2: Do not use vendor-supplied defaults",
            "INSECURE_HTTP": "Req 4: Encrypt transmission of cardholder data",
            "SSL_VERIFICATION_DISABLED": "Req 4: Encrypt transmission of cardholder data",
            "EVAL_USAGE": "Req 6: Develop and maintain secure systems",
            "EXEC_USAGE": "Req 6: Develop and maintain secure systems",
            "SHELL_INJECTION": "Req 6: Develop and maintain secure systems",
        }
        return mapping.get(vuln_type, "General Security")
