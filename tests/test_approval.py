"""Tests for human approval gates."""

from __future__ import annotations

from backend.orchestration.approval import ApprovalGate, ApprovalStatus


def test_approval_auto_approve() -> None:
    gate = ApprovalGate(auto_approve=True)
    req = gate.request_approval("pre_deployment")
    assert req.status == ApprovalStatus.AUTO_APPROVED
    assert gate.is_approved(req.request_id)


def test_approval_manual_mode() -> None:
    gate = ApprovalGate(auto_approve=False)
    req = gate.request_approval("pre_deployment")
    assert req.status == ApprovalStatus.PENDING
    assert not gate.is_approved(req.request_id)


def test_approval_approve() -> None:
    gate = ApprovalGate(auto_approve=False)
    req = gate.request_approval("security_review")
    result = gate.approve(req.request_id, reason="Looks good")
    assert result is not None
    assert result.status == ApprovalStatus.APPROVED
    assert gate.is_approved(req.request_id)


def test_approval_reject() -> None:
    gate = ApprovalGate(auto_approve=False)
    req = gate.request_approval("production_release")
    result = gate.reject(req.request_id, reason="Not ready")
    assert result is not None
    assert result.status == ApprovalStatus.REJECTED
    assert not gate.is_approved(req.request_id)


def test_approval_report() -> None:
    gate = ApprovalGate(auto_approve=False)
    gate.request_approval("pre_deployment")
    gate.request_approval("security_review")
    report = gate.get_report()
    assert report["total_requests"] == 2
    assert report["pending"] == 2
    assert len(report["gates"]) == 4


def test_approval_pending_list() -> None:
    gate = ApprovalGate(auto_approve=False)
    gate.request_approval("pre_deployment")
    req2 = gate.request_approval("security_review")
    gate.approve(req2.request_id)
    pending = gate.get_pending()
    assert len(pending) == 1
