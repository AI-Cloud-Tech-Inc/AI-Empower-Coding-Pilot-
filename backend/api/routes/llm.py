"""LLM integration endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.llm.client import get_llm_client

router = APIRouter(prefix="/llm", tags=["llm"])


class LLMGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    agent_role: str = ""
    system_prompt: str = "You are a helpful AI coding assistant."


class LLMGenerateResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    latency_ms: float
    cached: bool


@router.post("/generate", response_model=LLMGenerateResponse)
async def generate(req: LLMGenerateRequest) -> LLMGenerateResponse:
    client = get_llm_client()
    if req.agent_role:
        result = await client.generate_for_agent(req.agent_role, req.prompt)
    else:
        result = await client.generate(req.prompt, system_prompt=req.system_prompt)
    return LLMGenerateResponse(
        content=result.content,
        model=result.model,
        tokens_used=result.tokens_used,
        latency_ms=result.latency_ms,
        cached=result.cached,
    )


@router.get("/status")
async def llm_status() -> dict:
    from backend.config import settings

    has_key = bool(settings.openai_api_key and not settings.openai_api_key.startswith("sk-test"))
    return {
        "provider": "openai" if has_key else "fallback",
        "model": settings.openai_model,
        "api_key_configured": has_key,
    }
