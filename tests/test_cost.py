"""Tests for cost optimization."""

from __future__ import annotations

from backend.cost.optimizer import CostOptimizer


def test_record_tokens() -> None:
    optimizer = CostOptimizer()
    record = optimizer.record_tokens(1000)
    assert record.tokens == 1000
    assert record.estimated_cost > 0


def test_total_cost() -> None:
    optimizer = CostOptimizer()
    optimizer.record_tokens(1000)
    optimizer.record_tokens(2000)
    assert optimizer.get_total_tokens() == 3000
    assert optimizer.get_total_cost() > 0


def test_budget_check() -> None:
    optimizer = CostOptimizer()
    assert optimizer.is_over_budget() is False
    assert optimizer.is_approaching_budget() is False


def test_report() -> None:
    optimizer = CostOptimizer()
    optimizer.record_tokens(500, model="gpt-4o")
    report = optimizer.get_report()

    assert report["total_tokens"] == 500
    assert report["total_cost_usd"] > 0
    assert report["budget_usd"] > 0
    assert "recommendations" in report
