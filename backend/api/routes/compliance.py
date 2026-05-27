"""Compliance reporting endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas import ComplianceReportResponse
from backend.compliance.tracker import ComplianceTracker

router = APIRouter(prefix="/compliance", tags=["compliance"])

_tracker = ComplianceTracker()


@router.get("", response_model=ComplianceReportResponse)
async def get_compliance_report() -> ComplianceReportResponse:
    report = _tracker.get_report()
    return ComplianceReportResponse(**report)


@router.get("/frameworks")
async def list_frameworks() -> dict:
    return {
        "frameworks": [
            {"name": "HIPAA", "description": "Health Insurance Portability and Accountability Act"},
            {"name": "PCI-DSS", "description": "Payment Card Industry Data Security Standard"},
            {"name": "SOC2", "description": "Service Organization Control 2"},
        ]
    }
