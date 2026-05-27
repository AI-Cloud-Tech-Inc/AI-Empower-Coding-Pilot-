"""Audit log record model."""

from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class AuditLogRecord(BaseModel):
    """Persistent audit log entry."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    actor: str = "system"
    data: dict[str, Any] = Field(default_factory=dict)
    source: str = "ai-empower-coding-pilot"
    timestamp: float = Field(default_factory=time.time)
