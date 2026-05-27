"""Central compliance tracker that aggregates all framework checks."""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field

from backend.compliance.gdpr import GDPRChecker
from backend.compliance.hipaa import HIPAAChecker
from backend.compliance.pci import PCIChecker
from backend.compliance.soc2 import SOC2Checker


class ComplianceResult(BaseModel):
    """Result of a compliance check across all enabled frameworks."""

    timestamp: float = Field(default_factory=time.time)
    hipaa: dict[str, Any] = Field(default_factory=dict)
    pci: dict[str, Any] = Field(default_factory=dict)
    soc2: dict[str, Any] = Field(default_factory=dict)
    gdpr: dict[str, Any] = Field(default_factory=dict)
    overall_compliant: bool = True
    violations: list[dict[str, Any]] = Field(default_factory=list)


class ComplianceTracker:
    """Runs HIPAA, PCI-DSS, SOC 2, and GDPR checks against security scan results."""

    def __init__(self) -> None:
        self.hipaa = HIPAAChecker()
        self.pci = PCIChecker()
        self.soc2 = SOC2Checker()
        self.gdpr = GDPRChecker()
        self._history: list[ComplianceResult] = []

    def check_results(self, security_output: dict[str, Any]) -> ComplianceResult:
        """Run all compliance frameworks against security scan output."""
        findings = security_output.get("findings", [])

        hipaa_result = self.hipaa.check(findings)
        pci_result = self.pci.check(findings)
        soc2_result = self.soc2.check(findings)
        gdpr_result = self.gdpr.check(findings)

        violations: list[dict[str, Any]] = []
        violations.extend(hipaa_result.get("violations", []))
        violations.extend(pci_result.get("violations", []))
        violations.extend(soc2_result.get("violations", []))
        violations.extend(gdpr_result.get("violations", []))

        result = ComplianceResult(
            hipaa=hipaa_result,
            pci=pci_result,
            soc2=soc2_result,
            gdpr=gdpr_result,
            overall_compliant=len(violations) == 0,
            violations=violations,
        )

        self._history.append(result)
        return result

    def get_report(self) -> dict[str, Any]:
        """Return the latest compliance status."""
        if not self._history:
            return {"status": "no_checks_run", "compliant": True}

        latest = self._history[-1]
        return {
            "status": "checked",
            "compliant": latest.overall_compliant,
            "total_violations": len(latest.violations),
            "hipaa": latest.hipaa,
            "pci": latest.pci,
            "soc2": latest.soc2,
            "gdpr": latest.gdpr,
            "checks_run": len(self._history),
        }
