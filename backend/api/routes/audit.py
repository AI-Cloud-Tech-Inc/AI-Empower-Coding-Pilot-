"""Audit log endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.api.schemas import AuditSummaryResponse
from backend.audit.logger import AuditLogger

router = APIRouter(prefix="/audit", tags=["audit"])

_logger = AuditLogger()


@router.get("/summary", response_model=AuditSummaryResponse)
async def get_audit_summary() -> AuditSummaryResponse:
    summary = _logger.get_summary()
    return AuditSummaryResponse(**summary)


@router.get("/entries")
async def get_audit_entries(
    event_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    entries = _logger.get_entries(event_type=event_type, limit=limit, offset=offset)
    return {
        "entries": [e.model_dump() for e in entries],
        "total": len(entries),
    }


@router.get("/export")
async def export_audit_log() -> dict:
    return {"data": _logger.export_json()}
