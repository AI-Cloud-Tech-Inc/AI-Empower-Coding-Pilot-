"""Task model."""

from __future__ import annotations

import time
import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """A unit of work executed by an agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    agent_role: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    tokens_used: int = 0
    execution_time_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)
    completed_at: float | None = None
