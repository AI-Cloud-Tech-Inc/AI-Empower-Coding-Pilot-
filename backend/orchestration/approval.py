"""Human approval gates for workflow checkpoints."""

from __future__ import annotations

import time
import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalStatus(StrEnum):
    """Status of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    TIMED_OUT = "timed_out"


class ApprovalRequest(BaseModel):
    """A checkpoint requiring human approval before proceeding."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    checkpoint: str = ""
    description: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: float = Field(default_factory=time.time)
    resolved_at: float | None = None
    resolver: str | None = None
    reason: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 3600


class ApprovalGate:
    """Manages human approval gates in the CI/CD workflow.

    Gates can be placed at key checkpoints:
      - Pre-deployment: Review generated code before deployment
      - Security review: Approve after security scan findings
      - Compliance sign-off: Confirm compliance report
      - Production release: Final approval before production push
    """

    GATE_DEFINITIONS: dict[str, dict[str, str]] = {
        "pre_deployment": {
            "description": "Review generated artifacts before deployment",
            "stage": "after_review",
        },
        "security_review": {
            "description": "Approve security scan results before proceeding",
            "stage": "after_security",
        },
        "compliance_signoff": {
            "description": "Sign off on compliance report",
            "stage": "after_compliance",
        },
        "production_release": {
            "description": "Final approval for production release",
            "stage": "final",
        },
    }

    def __init__(self, auto_approve: bool = True) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self.auto_approve = auto_approve

    def request_approval(
        self,
        checkpoint: str,
        description: str = "",
        data: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        """Create an approval request at a checkpoint."""
        gate_info = self.GATE_DEFINITIONS.get(checkpoint, {})
        desc = description or gate_info.get("description", checkpoint)

        request = ApprovalRequest(
            checkpoint=checkpoint,
            description=desc,
            data=data or {},
        )

        if self.auto_approve:
            request.status = ApprovalStatus.AUTO_APPROVED
            request.resolved_at = time.time()
            request.resolver = "auto"
            request.reason = "Auto-approved (approval gates in demo mode)"

        self._requests[request.request_id] = request
        return request

    def approve(
        self,
        request_id: str,
        resolver: str = "human",
        reason: str = "",
    ) -> ApprovalRequest | None:
        """Approve a pending request."""
        req = self._requests.get(request_id)
        if req is None or req.status != ApprovalStatus.PENDING:
            return None
        req.status = ApprovalStatus.APPROVED
        req.resolved_at = time.time()
        req.resolver = resolver
        req.reason = reason
        return req

    def reject(
        self,
        request_id: str,
        resolver: str = "human",
        reason: str = "",
    ) -> ApprovalRequest | None:
        """Reject a pending request."""
        req = self._requests.get(request_id)
        if req is None or req.status != ApprovalStatus.PENDING:
            return None
        req.status = ApprovalStatus.REJECTED
        req.resolved_at = time.time()
        req.resolver = resolver
        req.reason = reason
        return req

    def is_approved(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req is None:
            return False
        return req.status in (ApprovalStatus.APPROVED, ApprovalStatus.AUTO_APPROVED)

    def get_pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]

    def get_all(self) -> list[ApprovalRequest]:
        return list(self._requests.values())

    def get_report(self) -> dict[str, Any]:
        all_reqs = list(self._requests.values())
        return {
            "total_requests": len(all_reqs),
            "pending": len([r for r in all_reqs if r.status == ApprovalStatus.PENDING]),
            "approved": len(
                [
                    r
                    for r in all_reqs
                    if r.status in (ApprovalStatus.APPROVED, ApprovalStatus.AUTO_APPROVED)
                ]
            ),
            "rejected": len([r for r in all_reqs if r.status == ApprovalStatus.REJECTED]),
            "gates": list(self.GATE_DEFINITIONS.keys()),
            "requests": [r.model_dump() for r in all_reqs],
        }
