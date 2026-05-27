"""Project management endpoints."""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    CreateProjectRequest,
    PipelineResultResponse,
    ProjectResponse,
    RunPipelineRequest,
)
from backend.models.project import Project, ProjectStatus
from backend.orchestration.orchestrator import Orchestrator

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory store (swap for DB in production)
_projects: dict[str, Project] = {}
_orchestrator = Orchestrator()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(body: CreateProjectRequest) -> ProjectResponse:
    project = Project(
        name=body.name,
        description=body.description,
        requirements=body.requirements,
    )
    _projects[project.id] = project
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status.value,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects() -> list[ProjectResponse]:
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            status=p.status.value,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in _projects.values()
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    project = _projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status.value,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/{project_id}/run", response_model=PipelineResultResponse)
async def run_pipeline(project_id: str) -> PipelineResultResponse:
    project = _projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = ProjectStatus.IN_PROGRESS
    project.updated_at = time.time()

    result = await _orchestrator.run(project.requirements)

    project.status = (
        ProjectStatus.COMPLETED if result["status"] == "completed" else ProjectStatus.FAILED
    )
    project.updated_at = time.time()

    return PipelineResultResponse(**result)


@router.post("/run", response_model=PipelineResultResponse)
async def run_pipeline_ad_hoc(body: RunPipelineRequest) -> PipelineResultResponse:
    """Run the pipeline without creating a persistent project."""
    result = await _orchestrator.run(body.requirements)
    return PipelineResultResponse(**result)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str) -> None:
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    del _projects[project_id]
