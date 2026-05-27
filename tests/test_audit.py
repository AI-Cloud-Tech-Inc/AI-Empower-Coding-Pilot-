"""Tests for audit logging."""

from __future__ import annotations

from backend.audit.logger import AuditLogger


def test_audit_log_entry() -> None:
    logger = AuditLogger()
    entry = logger.log("test_event", {"key": "value"})
    assert entry.event_type == "test_event"
    assert entry.data == {"key": "value"}


def test_audit_get_entries() -> None:
    logger = AuditLogger()
    logger.log("event_a")
    logger.log("event_b")
    logger.log("event_a")

    all_entries = logger.get_entries()
    assert len(all_entries) == 3

    filtered = logger.get_entries(event_type="event_a")
    assert len(filtered) == 2


def test_audit_summary() -> None:
    logger = AuditLogger()
    logger.log("type_1")
    logger.log("type_1")
    logger.log("type_2")

    summary = logger.get_summary()
    assert summary["total_entries"] == 3
    assert summary["event_counts"]["type_1"] == 2
    assert summary["event_counts"]["type_2"] == 1


def test_audit_export_json() -> None:
    logger = AuditLogger()
    logger.log("export_test")
    json_str = logger.export_json()
    assert "export_test" in json_str


def test_audit_clear() -> None:
    logger = AuditLogger()
    logger.log("to_clear")
    count = logger.clear()
    assert count == 1
    assert logger.get_summary()["total_entries"] == 0
