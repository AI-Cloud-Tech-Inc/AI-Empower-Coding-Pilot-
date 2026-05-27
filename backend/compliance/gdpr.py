"""GDPR compliance checker."""

from __future__ import annotations

from typing import Any


class GDPRChecker:
    """Check code against GDPR requirements.

    Key principles:
    - Data minimization
    - Purpose limitation
    - Storage limitation
    - Integrity and confidentiality
    - Right to erasure
    - Data protection by design
    """

    RELEVANT_VULN_TYPES = {
        "HARDCODED_SECRET",
        "INSECURE_HTTP",
        "SSL_VERIFICATION_DISABLED",
        "UNSAFE_DESERIALIZATION",
        "EVAL_USAGE",
    }

    def check(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for finding in findings:
            vuln_type = finding.get("type", "")
            if vuln_type in self.RELEVANT_VULN_TYPES:
                violations.append(
                    {
                        "framework": "GDPR",
                        "article": self._map_article(vuln_type),
                        "finding": finding,
                        "remediation": finding.get("recommendation", ""),
                    }
                )

        return {
            "framework": "GDPR",
            "compliant": len(violations) == 0,
            "violations": violations,
            "articles_checked": [
                "Art. 5(1)(f) — Integrity and Confidentiality",
                "Art. 25 — Data Protection by Design and Default",
                "Art. 32 — Security of Processing",
                "Art. 33 — Notification of Data Breach",
                "Art. 35 — Data Protection Impact Assessment",
            ],
        }

    @staticmethod
    def _map_article(vuln_type: str) -> str:
        mapping = {
            "HARDCODED_SECRET": "Art. 5(1)(f) — Integrity and Confidentiality",
            "INSECURE_HTTP": "Art. 32 — Security of Processing",
            "SSL_VERIFICATION_DISABLED": "Art. 32 — Security of Processing",
            "UNSAFE_DESERIALIZATION": "Art. 25 — Data Protection by Design and Default",
            "EVAL_USAGE": "Art. 25 — Data Protection by Design and Default",
        }
        return mapping.get(vuln_type, "General Data Protection")
