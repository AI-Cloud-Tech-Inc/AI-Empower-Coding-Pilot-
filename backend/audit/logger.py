"""Immutable audit logging with cryptographic integrity chain."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """A single immutable audit log entry with integrity hash."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sequence: int = 0
    timestamp: float = Field(default_factory=time.time)
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    actor: str = "system"
    source: str = "ai-empower-coding-pilot"
    prev_hash: str = ""
    entry_hash: str = ""


def _compute_hash(entry: AuditEntry) -> str:
    """Compute SHA-256 hash of the entry's content for tamper detection."""
    payload = (
        f"{entry.entry_id}:{entry.sequence}:{entry.timestamp}:"
        f"{entry.event_type}:{json.dumps(entry.data, sort_keys=True)}:"
        f"{entry.actor}:{entry.prev_hash}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class AuditLogger:
    """Append-only audit logger with cryptographic hash chain.

    Each entry links to the previous via SHA-256 hash, forming an
    immutable chain. Any tampering breaks the chain and is detectable
    via ``verify_integrity()``.
    """

    def __init__(self, log_file: str | None = None) -> None:
        self._entries: list[AuditEntry] = []
        self._sequence = 0
        self._last_hash = "genesis"
        self._logger = logging.getLogger("audit")

        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def log(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> AuditEntry:
        """Record an immutable audit event."""
        self._sequence += 1

        entry = AuditEntry(
            sequence=self._sequence,
            event_type=event_type,
            data=data or {},
            actor=actor,
            prev_hash=self._last_hash,
        )
        entry.entry_hash = _compute_hash(entry)
        self._last_hash = entry.entry_hash

        self._entries.append(entry)
        self._logger.info(entry.model_dump_json())
        return entry

    def verify_integrity(self) -> dict[str, Any]:
        """Verify the entire hash chain is intact."""
        if not self._entries:
            return {"valid": True, "entries_checked": 0}

        expected_prev = "genesis"
        for idx, entry in enumerate(self._entries):
            if entry.prev_hash != expected_prev:
                return {
                    "valid": False,
                    "broken_at": idx,
                    "entry_id": entry.entry_id,
                    "reason": "prev_hash mismatch",
                }

            recomputed = _compute_hash(entry)
            if entry.entry_hash != recomputed:
                return {
                    "valid": False,
                    "broken_at": idx,
                    "entry_id": entry.entry_id,
                    "reason": "entry_hash tampered",
                }

            expected_prev = entry.entry_hash

        return {"valid": True, "entries_checked": len(self._entries)}

    def get_entries(
        self,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """Query audit entries with optional filtering."""
        filtered = self._entries
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        return filtered[offset : offset + limit]

    def get_summary(self) -> dict[str, Any]:
        """Return aggregate statistics."""
        event_counts: dict[str, int] = {}
        for entry in self._entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1

        integrity = self.verify_integrity()
        return {
            "total_entries": len(self._entries),
            "event_counts": event_counts,
            "earliest": self._entries[0].timestamp if self._entries else None,
            "latest": self._entries[-1].timestamp if self._entries else None,
            "integrity": integrity,
        }

    def export_json(self) -> str:
        """Export all entries as a JSON string."""
        return json.dumps([e.model_dump() for e in self._entries], indent=2)

    def clear(self) -> int:
        """Clear the in-memory buffer (returns count of cleared entries)."""
        count = len(self._entries)
        self._entries.clear()
        self._sequence = 0
        self._last_hash = "genesis"
        return count
