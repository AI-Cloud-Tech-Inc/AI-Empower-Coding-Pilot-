"""Human approval gate endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ApprovalActionRequest, ApprovalResponse
from backend.orchestration.approval import ApprovalGate

router = APIRouter(prefix="/approvals", tags=["approvals"])

_gate = ApprovalGate(auto_approve=True)


@router.get("", response_model=ApprovalResponse)
async def get_approvals() -> ApprovalResponse:
    report = _gate.get_report()
    return ApprovalResponse(**report)


@router.post("/action")
async def process_approval(body: ApprovalActionRequest) -> dict:
    """Approve or reject a pending approval request."""
    if body.action == "approve":
        result = _gate.approve(body.request_id, reason=body.reason)
    else:
        result = _gate.reject(body.request_id, reason=body.reason)

    if result is None:
        raise HTTPException(
            status_code=404, detail="Approval request not found or already resolved"
        )

    return {
        "request_id": result.request_id,
        "status": result.status.value,
        "resolved_at": result.resolved_at,
    }


@router.get("/gates")
async def list_gates() -> dict:
    """List available approval gates."""
    return {
        "gates": [{"name": name, **info} for name, info in ApprovalGate.GATE_DEFINITIONS.items()]
    }
