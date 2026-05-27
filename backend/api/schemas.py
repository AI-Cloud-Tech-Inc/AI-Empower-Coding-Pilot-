"""Pydantic request / response schemas for the API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ---- Requests ----


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    requirements: str = Field(..., min_length=1)


class RunPipelineRequest(BaseModel):
    requirements: str = Field(..., min_length=1)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(default=5, ge=1, le=50)


# ---- Responses ----


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    created_at: float
    updated_at: float


class PipelineResultResponse(BaseModel):
    workflow_id: str
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    transitions: int = 0
    duration_s: float = 0.0


class AgentStatusResponse(BaseModel):
    role: str
    agent_id: str
    status: str = "idle"


class ComplianceReportResponse(BaseModel):
    status: str
    compliant: bool
    total_violations: int = 0
    hipaa: dict[str, Any] = Field(default_factory=dict)
    pci: dict[str, Any] = Field(default_factory=dict)
    soc2: dict[str, Any] = Field(default_factory=dict)


class CostReportResponse(BaseModel):
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    budget_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_used_pct: float = 0.0
    is_over_budget: bool = False
    recommendations: list[str] = Field(default_factory=list)


class AuditSummaryResponse(BaseModel):
    total_entries: int = 0
    event_counts: dict[str, int] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, str] = Field(default_factory=dict)
