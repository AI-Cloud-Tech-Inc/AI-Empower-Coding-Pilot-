"""Structured audit logging for compliance and observability."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """A single immutable audit log entry."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    actor: str = "system"
    source: str = "ai-empower-coding-pilot"


class AuditLogger:
    """Append-only audit logger with in-memory buffer and optional file sink."""

    def __init__(self, log_file: str | None = None) -> None:
        self._entries: list[AuditEntry] = []
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
        """Record an audit event."""
        entry = AuditEntry(event_type=event_type, data=data or {}, actor=actor)
        self._entries.append(entry)
        self._logger.info(entry.model_dump_json())
        return entry

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

        return {
            "total_entries": len(self._entries),
            "event_counts": event_counts,
            "earliest": self._entries[0].timestamp if self._entries else None,
            "latest": self._entries[-1].timestamp if self._entries else None,
        }

    def export_json(self) -> str:
        """Export all entries as a JSON string."""
        return json.dumps([e.model_dump() for e in self._entries], indent=2)

    def clear(self) -> int:
        """Clear the in-memory buffer (returns count of cleared entries)."""
        count = len(self._entries)
        self._entries.clear()
        return count
