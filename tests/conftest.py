"""Shared test fixtures."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from backend.agents.base import AgentContext
from backend.main import app


@pytest.fixture
def context() -> AgentContext:
    return AgentContext(requirements="Build a REST API with user authentication and a dashboard")


@pytest.fixture
def context_with_architecture(context: AgentContext) -> AgentContext:
    context.architecture = {
        "components": [
            {"name": "api_layer", "type": "service", "description": "REST API"},
            {"name": "frontend", "type": "application", "description": "Dashboard"},
        ],
        "patterns": ["REST API"],
        "tech_stack": {"frameworks": ["FastAPI", "React"]},
    }
    return context


@pytest.fixture
def context_with_code(context_with_architecture: AgentContext) -> AgentContext:
    context_with_architecture.code_files = {
        "main.py": '"""Main module."""\nfrom fastapi import FastAPI\napp = FastAPI()\n',
        "utils.py": "def helper():\n    return True\n",
    }
    return context_with_code


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
