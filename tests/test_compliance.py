"""Tests for compliance tracking."""

from __future__ import annotations

from backend.compliance.gdpr import GDPRChecker
from backend.compliance.hipaa import HIPAAChecker
from backend.compliance.pci import PCIChecker
from backend.compliance.soc2 import SOC2Checker
from backend.compliance.tracker import ComplianceTracker


def test_hipaa_clean() -> None:
    checker = HIPAAChecker()
    result = checker.check([])
    assert result["compliant"] is True


def test_hipaa_violation() -> None:
    checker = HIPAAChecker()
    result = checker.check([{"type": "HARDCODED_SECRET", "recommendation": "fix"}])
    assert result["compliant"] is False
    assert len(result["violations"]) == 1


def test_pci_clean() -> None:
    checker = PCIChecker()
    result = checker.check([])
    assert result["compliant"] is True


def test_pci_violation() -> None:
    checker = PCIChecker()
    result = checker.check([{"type": "EVAL_USAGE", "recommendation": "fix"}])
    assert result["compliant"] is False


def test_soc2_clean() -> None:
    checker = SOC2Checker()
    result = checker.check([])
    assert result["compliant"] is True


def test_gdpr_clean() -> None:
    checker = GDPRChecker()
    result = checker.check([])
    assert result["compliant"] is True
    assert result["framework"] == "GDPR"


def test_gdpr_violation() -> None:
    checker = GDPRChecker()
    result = checker.check([{"type": "INSECURE_HTTP", "recommendation": "fix"}])
    assert result["compliant"] is False
    assert len(result["violations"]) == 1
    assert result["violations"][0]["article"] == "Art. 32 — Security of Processing"


def test_compliance_tracker() -> None:
    tracker = ComplianceTracker()
    result = tracker.check_results({"findings": []})
    assert result.overall_compliant is True

    report = tracker.get_report()
    assert report["status"] == "checked"
    assert report["compliant"] is True


def test_compliance_tracker_with_violations() -> None:
    tracker = ComplianceTracker()
    result = tracker.check_results(
        {"findings": [{"type": "HARDCODED_SECRET", "recommendation": "fix"}]}
    )
    assert result.overall_compliant is False
    assert len(result.violations) > 0
