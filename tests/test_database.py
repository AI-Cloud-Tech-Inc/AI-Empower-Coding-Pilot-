"""Tests for database models and configuration."""

from __future__ import annotations

from backend.config import Settings
from backend.models.db_models import (
    AuditLogDB,
    CostRecordDB,
    PipelineRunDB,
    ProjectDB,
    UserDB,
)


class TestDBModels:
    def test_user_model_tablename(self) -> None:
        assert UserDB.__tablename__ == "users"

    def test_project_model_tablename(self) -> None:
        assert ProjectDB.__tablename__ == "projects"

    def test_audit_log_model_tablename(self) -> None:
        assert AuditLogDB.__tablename__ == "audit_logs"

    def test_cost_record_model_tablename(self) -> None:
        assert CostRecordDB.__tablename__ == "cost_records"

    def test_pipeline_run_model_tablename(self) -> None:
        assert PipelineRunDB.__tablename__ == "pipeline_runs"


class TestSettings:
    def test_anthropic_settings(self) -> None:
        s = Settings()
        assert s.anthropic_api_key == ""
        assert "claude" in s.anthropic_model

    def test_rate_limit_settings(self) -> None:
        s = Settings()
        assert s.rate_limit_requests == 100
        assert s.rate_limit_window_seconds == 60

    def test_db_pool_settings(self) -> None:
        s = Settings()
        assert s.db_pool_size == 10
        assert s.db_max_overflow == 20
