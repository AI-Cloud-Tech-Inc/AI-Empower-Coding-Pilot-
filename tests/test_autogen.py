"""Tests for auto-generation engines."""

from __future__ import annotations

from backend.autogen.cicd import CICDGenerator
from backend.autogen.docker import DockerGenerator
from backend.autogen.scaffolding import ScaffoldingEngine
from backend.autogen.terraform import TerraformGenerator

SAMPLE_ARCH = {
    "components": [
        {"name": "api_layer", "type": "service", "description": "REST API"},
        {"name": "frontend", "type": "application", "description": "Dashboard"},
        {"name": "database", "type": "infrastructure", "description": "Data store"},
    ],
    "tech_stack": {
        "frameworks": ["FastAPI", "React"],
        "databases": ["PostgreSQL"],
        "languages": ["Python"],
        "infrastructure": [],
    },
}


def test_scaffolding_generates_files() -> None:
    engine = ScaffoldingEngine()
    files = engine.generate(SAMPLE_ARCH, "test-app")
    assert len(files) > 0
    assert any("main.py" in k for k in files)
    assert "README.md" in files
    assert ".env.example" in files


def test_scaffolding_supported_templates() -> None:
    engine = ScaffoldingEngine()
    templates = engine.get_supported_templates()
    assert "fastapi" in templates
    assert "react" in templates


def test_cicd_generates_workflows() -> None:
    gen = CICDGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    assert ".github/workflows/ci.yml" in files
    assert ".github/workflows/cd.yml" in files
    assert ".github/workflows/frontend.yml" in files


def test_cicd_ci_content() -> None:
    gen = CICDGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    ci = files[".github/workflows/ci.yml"]
    assert "pytest" in ci
    assert "ruff" in ci


def test_docker_generates_files() -> None:
    gen = DockerGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    assert "Dockerfile" in files
    assert "docker-compose.yml" in files
    assert ".dockerignore" in files


def test_docker_compose_content() -> None:
    gen = DockerGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    compose = files["docker-compose.yml"]
    assert "backend" in compose
    assert "frontend" in compose
    assert "postgres" in compose.lower()


def test_terraform_generates_files() -> None:
    gen = TerraformGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    assert "terraform/main.tf" in files
    assert "terraform/variables.tf" in files
    assert "terraform/outputs.tf" in files
    assert "terraform/networking.tf" in files


def test_terraform_with_database() -> None:
    gen = TerraformGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    assert "terraform/rds.tf" in files


def test_terraform_with_services() -> None:
    gen = TerraformGenerator()
    files = gen.generate(SAMPLE_ARCH, "test-app")
    assert "terraform/ecs.tf" in files
    ecs = files["terraform/ecs.tf"]
    assert "aws_ecs_cluster" in ecs
