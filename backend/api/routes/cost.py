"""Cost tracking and budget management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas import CostReportResponse
from backend.cost.optimizer import CostOptimizer

router = APIRouter(prefix="/cost", tags=["cost"])

_optimizer = CostOptimizer()


@router.get("", response_model=CostReportResponse)
async def get_cost_report() -> CostReportResponse:
    report = _optimizer.get_report()
    return CostReportResponse(**report)


@router.post("/record")
async def record_usage(tokens: int = 100, model: str = "gpt-4o") -> dict:
    """Record token usage for a model."""
    record = _optimizer.record_tokens(tokens, model)
    return {
        "recorded": True,
        "tokens": record.tokens,
        "estimated_cost": record.estimated_cost,
        "model": record.model,
    }
