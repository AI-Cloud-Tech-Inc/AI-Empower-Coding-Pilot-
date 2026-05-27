"""Cost tracking and optimization for LLM token usage."""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field

from backend.config import settings

# Approximate pricing per 1K tokens (input / output) for common models
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


class UsageRecord(BaseModel):
    """Single token-usage data point."""

    timestamp: float = Field(default_factory=time.time)
    tokens: int = 0
    estimated_cost: float = 0.0
    model: str = ""


class CostOptimizer:
    """Track token usage and estimated costs; enforce budgets."""

    def __init__(self) -> None:
        self._records: list[UsageRecord] = []
        self.budget = settings.max_cost_per_project
        self.alert_threshold = settings.cost_alert_threshold

    def record_tokens(self, tokens: int, model: str | None = None) -> UsageRecord:
        """Record a token usage event and return the record."""
        model = model or settings.openai_model
        cost = self._estimate_cost(tokens, model)

        record = UsageRecord(tokens=tokens, estimated_cost=cost, model=model)
        self._records.append(record)
        return record

    def get_total_cost(self) -> float:
        return sum(r.estimated_cost for r in self._records)

    def get_total_tokens(self) -> int:
        return sum(r.tokens for r in self._records)

    def is_over_budget(self) -> bool:
        return self.get_total_cost() >= self.budget

    def is_approaching_budget(self) -> bool:
        return self.get_total_cost() >= self.budget * self.alert_threshold

    def get_report(self) -> dict[str, Any]:
        total_cost = self.get_total_cost()
        total_tokens = self.get_total_tokens()

        return {
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "budget_usd": self.budget,
            "budget_remaining_usd": round(self.budget - total_cost, 6),
            "budget_used_pct": round((total_cost / self.budget) * 100, 2) if self.budget else 0,
            "is_over_budget": self.is_over_budget(),
            "alert_triggered": self.is_approaching_budget(),
            "total_records": len(self._records),
            "recommendations": self._get_recommendations(total_tokens, total_cost),
        }

    def _get_recommendations(self, total_tokens: int, total_cost: float) -> list[str]:
        recs: list[str] = []

        if self.is_approaching_budget():
            recs.append("Consider reducing prompt sizes or switching to a cheaper model.")

        if total_tokens > 100_000:
            recs.append("High token usage detected — enable response caching.")

        current_model = settings.openai_model
        if current_model in ("gpt-4o", "gpt-4-turbo"):
            recs.append(f"Using {current_model}; consider gpt-4o-mini for non-critical tasks.")

        return recs

    @staticmethod
    def _estimate_cost(tokens: int, model: str) -> float:
        pricing = MODEL_PRICING.get(model, {"input": 0.005, "output": 0.015})
        avg_rate = (pricing["input"] + pricing["output"]) / 2
        return (tokens / 1000) * avg_rate
