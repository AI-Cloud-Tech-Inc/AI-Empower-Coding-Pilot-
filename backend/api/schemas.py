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


class ApprovalActionRequest(BaseModel):
    request_id: str
    action: str = Field(..., pattern="^(approve|reject)$")
    reason: str = ""


class GenerateRequest(BaseModel):
    architecture: dict[str, Any] = Field(default_factory=dict)
    project_name: str = "my-project"


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
    gdpr: dict[str, Any] = Field(default_factory=dict)


class CostReportResponse(BaseModel):
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    budget_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_used_pct: float = 0.0
    is_over_budget: bool = False
    alert_triggered: bool = False
    total_records: int = 0
    recommendations: list[str] = Field(default_factory=list)


class AuditSummaryResponse(BaseModel):
    total_entries: int = 0
    event_counts: dict[str, int] = Field(default_factory=dict)
    integrity: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, str] = Field(default_factory=dict)


class ApprovalResponse(BaseModel):
    total_requests: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    gates: list[str] = Field(default_factory=list)
    requests: list[dict[str, Any]] = Field(default_factory=list)


class AutoGenResponse(BaseModel):
    scaffolding: dict[str, Any] = Field(default_factory=dict)
    cicd: dict[str, Any] = Field(default_factory=dict)
    docker: dict[str, Any] = Field(default_factory=dict)
    terraform: dict[str, Any] = Field(default_factory=dict)
    total_files_generated: int = 0
