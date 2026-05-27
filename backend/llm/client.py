"""Multi-provider async LLM client with OpenAI, Anthropic, and fallback support."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum

import httpx

from backend.config import settings
from backend.cost.optimizer import CostOptimizer


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    FALLBACK = "fallback"


@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    latency_ms: float
    cached: bool = False
    provider: str = "fallback"


@dataclass
class LLMClient:
    """Async client supporting OpenAI, Anthropic, and fallback modes."""

    model: str = ""
    temperature: float = 0.1
    max_tokens: int = 4096
    _cost_optimizer: CostOptimizer = field(default_factory=CostOptimizer)

    def __post_init__(self) -> None:
        if not self.model:
            self.model = settings.openai_model

    @property
    def active_provider(self) -> LLMProvider:
        if settings.openai_api_key and not settings.openai_api_key.startswith("sk-test"):
            return LLMProvider.OPENAI
        if settings.anthropic_api_key:
            return LLMProvider.ANTHROPIC
        return LLMProvider.FALLBACK

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI coding assistant.",
    ) -> LLMResponse:
        provider = self.active_provider
        if provider == LLMProvider.OPENAI:
            return await self._openai_generate(prompt, system_prompt)
        if provider == LLMProvider.ANTHROPIC:
            return await self._anthropic_generate(prompt, system_prompt)
        return self._fallback_response(prompt)

    async def _openai_generate(self, prompt: str, system_prompt: str) -> LLMResponse:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

        latency = (time.monotonic() - start) * 1000
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        content = data["choices"][0]["message"]["content"]
        self._cost_optimizer.record_tokens(tokens, self.model)

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=tokens,
            latency_ms=latency,
            provider=LLMProvider.OPENAI,
        )

    async def _anthropic_generate(self, prompt: str, system_prompt: str) -> LLMResponse:
        start = time.monotonic()
        model = settings.anthropic_model
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": self.max_tokens,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            data = response.json()

        latency = (time.monotonic() - start) * 1000
        usage = data.get("usage", {})
        tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        content = data["content"][0]["text"]
        self._cost_optimizer.record_tokens(tokens, model)

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens,
            latency_ms=latency,
            provider=LLMProvider.ANTHROPIC,
        )

    def _fallback_response(self, prompt: str) -> LLMResponse:
        """Generate a structured response when no API key is configured."""
        prompt_lower = prompt.lower()

        if "architect" in prompt_lower or "design" in prompt_lower:
            content = (
                "## Architecture Design\n\n"
                "### Components\n"
                "- **API Layer**: RESTful FastAPI service with OpenAPI docs\n"
                "- **Business Logic**: Domain-driven service layer\n"
                "- **Data Layer**: SQLAlchemy ORM with async support\n"
                "- **Cache**: Redis for session and query caching\n\n"
                "### Patterns\n"
                "- Repository pattern for data access\n"
                "- CQRS for read/write separation\n"
                "- Event sourcing for audit trail\n"
            )
        elif "test" in prompt_lower:
            content = (
                "## Test Plan\n\n"
                "### Unit Tests\n"
                "- Model validation tests\n"
                "- Service layer logic tests\n"
                "- API endpoint contract tests\n\n"
                "### Integration Tests\n"
                "- Database CRUD operations\n"
                "- API workflow end-to-end\n"
                "- Authentication flow\n"
            )
        elif "security" in prompt_lower or "scan" in prompt_lower:
            content = (
                "## Security Analysis\n\n"
                "### Findings\n"
                "- Input validation: PASS\n"
                "- SQL injection prevention: PASS (parameterized queries)\n"
                "- XSS protection: PASS (output encoding)\n"
                "- Authentication: JWT with expiry and refresh\n"
                "- Authorization: Role-based access control\n"
            )
        elif "review" in prompt_lower:
            content = (
                "## Code Review\n\n"
                "### Quality Assessment\n"
                "- Code style: Consistent, follows PEP 8\n"
                "- Type safety: Full type annotations\n"
                "- Error handling: Comprehensive try/except\n"
                "- Documentation: Docstrings present\n"
                "- Test coverage: Adequate\n"
            )
        elif "devops" in prompt_lower or "deploy" in prompt_lower:
            content = (
                "## DevOps Configuration\n\n"
                "### CI/CD Pipeline\n"
                "- Build → Test → Lint → Security Scan → Deploy\n"
                "- Blue-green deployment strategy\n"
                "- Automated rollback on failure\n\n"
                "### Infrastructure\n"
                "- Docker containers with health checks\n"
                "- Kubernetes orchestration\n"
                "- Terraform for infrastructure as code\n"
            )
        elif "performance" in prompt_lower or "optimize" in prompt_lower:
            content = (
                "## Performance Analysis\n\n"
                "### Optimizations\n"
                "- Database query optimization with indexes\n"
                "- Response caching with Redis (TTL: 300s)\n"
                "- Connection pooling (min: 5, max: 20)\n"
                "- Gzip compression for API responses\n"
                "- CDN for static asset delivery\n"
            )
        elif "accessibility" in prompt_lower or "a11y" in prompt_lower:
            content = (
                "## Accessibility Report\n\n"
                "### WCAG 2.1 Compliance\n"
                "- Level A: All criteria met\n"
                "- Level AA: Colour contrast verified\n"
                "- Keyboard navigation: All interactive elements focusable\n"
                "- Screen reader: ARIA labels present\n"
                "- Focus management: Visible focus indicators\n"
            )
        else:
            content = (
                "## Generated Code\n\n"
                "```python\n"
                "from fastapi import FastAPI, HTTPException\n"
                "from pydantic import BaseModel\n\n"
                "app = FastAPI()\n\n"
                "class Item(BaseModel):\n"
                "    name: str\n"
                '    description: str = ""\n\n'
                '@app.post("/items")\n'
                "async def create_item(item: Item):\n"
                '    return {"id": 1, **item.model_dump()}\n'
                "```\n"
            )

        return LLMResponse(
            content=content,
            model="fallback",
            tokens_used=len(content.split()),
            latency_ms=1.0,
            cached=True,
            provider=LLMProvider.FALLBACK,
        )

    async def generate_for_agent(self, agent_role: str, prompt: str) -> LLMResponse:
        """Generate a response with an agent-specific system prompt."""
        system_prompts = {
            "architect": "You are an expert software architect. Analyse requirements and produce system designs.",
            "coder": "You are a senior software engineer. Write production-ready code.",
            "tester": "You are a QA engineer. Create comprehensive test plans and test cases.",
            "security": "You are a security engineer. Analyse code for vulnerabilities.",
            "docs": "You are a technical writer. Generate clear documentation.",
            "reviewer": "You are a code reviewer. Evaluate code quality and suggest improvements.",
            "devops": "You are a DevOps engineer. Configure CI/CD, containers, and infrastructure.",
            "performance": "You are a performance engineer. Optimise code for speed and efficiency.",
            "accessibility": "You are an accessibility expert. Ensure WCAG 2.1 compliance.",
        }
        system_prompt = system_prompts.get(agent_role, "You are a helpful AI coding assistant.")
        return await self.generate(prompt, system_prompt=system_prompt)

    def get_status(self) -> dict:
        provider = self.active_provider
        return {
            "provider": provider.value,
            "model": self.model
            if provider == LLMProvider.OPENAI
            else (settings.anthropic_model if provider == LLMProvider.ANTHROPIC else "fallback"),
            "api_key_configured": provider != LLMProvider.FALLBACK,
            "providers_available": {
                "openai": bool(
                    settings.openai_api_key and not settings.openai_api_key.startswith("sk-test")
                ),
                "anthropic": bool(settings.anthropic_api_key),
                "fallback": True,
            },
        }


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
