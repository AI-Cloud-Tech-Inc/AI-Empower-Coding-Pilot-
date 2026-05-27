"""Auto-generation endpoints for scaffolding, CI/CD, Docker, and Terraform."""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas import AutoGenResponse, GenerateRequest
from backend.autogen.cicd import CICDGenerator
from backend.autogen.docker import DockerGenerator
from backend.autogen.scaffolding import ScaffoldingEngine
from backend.autogen.terraform import TerraformGenerator

router = APIRouter(prefix="/autogen", tags=["auto-generation"])

_scaffolding = ScaffoldingEngine()
_cicd = CICDGenerator()
_docker = DockerGenerator()
_terraform = TerraformGenerator()


@router.post("/generate", response_model=AutoGenResponse)
async def generate_all(body: GenerateRequest) -> AutoGenResponse:
    """Generate scaffolding, CI/CD, Docker, and Terraform from architecture."""
    arch = body.architecture
    name = body.project_name

    scaffolding = _scaffolding.generate(arch, name)
    cicd = _cicd.generate(arch, name)
    docker = _docker.generate(arch, name)
    terraform = _terraform.generate(arch, name)

    return AutoGenResponse(
        scaffolding={"files": list(scaffolding.keys()), "count": len(scaffolding)},
        cicd={"files": list(cicd.keys()), "count": len(cicd)},
        docker={"files": list(docker.keys()), "count": len(docker)},
        terraform={"files": list(terraform.keys()), "count": len(terraform)},
        total_files_generated=len(scaffolding) + len(cicd) + len(docker) + len(terraform),
    )


@router.post("/scaffolding")
async def generate_scaffolding(body: GenerateRequest) -> dict:
    """Generate project scaffolding files."""
    files = _scaffolding.generate(body.architecture, body.project_name)
    return {"files": {path: content for path, content in files.items()}, "count": len(files)}


@router.post("/cicd")
async def generate_cicd(body: GenerateRequest) -> dict:
    """Generate CI/CD pipeline files."""
    files = _cicd.generate(body.architecture, body.project_name)
    return {"files": {path: content for path, content in files.items()}, "count": len(files)}


@router.post("/docker")
async def generate_docker(body: GenerateRequest) -> dict:
    """Generate Docker configuration files."""
    files = _docker.generate(body.architecture, body.project_name)
    return {"files": {path: content for path, content in files.items()}, "count": len(files)}


@router.post("/terraform")
async def generate_terraform(body: GenerateRequest) -> dict:
    """Generate Terraform IaC files."""
    files = _terraform.generate(body.architecture, body.project_name)
    return {"files": {path: content for path, content in files.items()}, "count": len(files)}


@router.get("/capabilities")
async def get_capabilities() -> dict:
    """List available auto-generation capabilities."""
    return {
        "engines": [
            {
                "name": "scaffolding",
                "templates": _scaffolding.get_supported_templates(),
                "description": "Project structure and boilerplate generation",
            },
            {
                "name": "cicd",
                "platforms": CICDGenerator.get_supported_platforms(),
                "description": "CI/CD pipeline YAML generation",
            },
            {
                "name": "docker",
                "runtimes": DockerGenerator.get_supported_runtimes(),
                "description": "Dockerfile and docker-compose generation",
            },
            {
                "name": "terraform",
                "providers": TerraformGenerator.get_supported_providers(),
                "description": "Infrastructure as Code (Terraform HCL) generation",
            },
        ]
    }
