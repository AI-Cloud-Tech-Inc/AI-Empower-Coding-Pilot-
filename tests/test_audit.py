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


def test_audit_integrity_valid() -> None:
    logger = AuditLogger()
    logger.log("event_1")
    logger.log("event_2")
    logger.log("event_3")
    integrity = logger.verify_integrity()
    assert integrity["valid"] is True
    assert integrity["entries_checked"] == 3


def test_audit_integrity_hash_chain() -> None:
    logger = AuditLogger()
    e1 = logger.log("first")
    e2 = logger.log("second")
    assert e2.prev_hash == e1.entry_hash
    assert e1.prev_hash == "genesis"


def test_audit_summary_includes_integrity() -> None:
    logger = AuditLogger()
    logger.log("check")
    summary = logger.get_summary()
    assert "integrity" in summary
    assert summary["integrity"]["valid"] is True


def test_audit_clear() -> None:
    logger = AuditLogger()
    logger.log("to_clear")
    count = logger.clear()
    assert count == 1
    assert logger.get_summary()["total_entries"] == 0
