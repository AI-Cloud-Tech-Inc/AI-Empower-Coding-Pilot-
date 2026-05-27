"""Tests for multi-provider LLM client."""

from __future__ import annotations

import pytest

from backend.llm.client import LLMClient, LLMProvider


class TestLLMProvider:
    def test_provider_values(self) -> None:
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.ANTHROPIC == "anthropic"
        assert LLMProvider.FALLBACK == "fallback"


class TestLLMClientFallback:
    @pytest.mark.asyncio
    async def test_fallback_architect(self) -> None:
        client = LLMClient()
        response = await client.generate("Design the architecture")
        assert "Architecture Design" in response.content
        assert response.provider == LLMProvider.FALLBACK

    @pytest.mark.asyncio
    async def test_fallback_test(self) -> None:
        client = LLMClient()
        response = await client.generate("Write test cases")
        assert "Test Plan" in response.content

    @pytest.mark.asyncio
    async def test_fallback_security(self) -> None:
        client = LLMClient()
        response = await client.generate("Run security scan")
        assert "Security Analysis" in response.content

    @pytest.mark.asyncio
    async def test_fallback_review(self) -> None:
        client = LLMClient()
        response = await client.generate("Code review")
        assert "Code Review" in response.content

    @pytest.mark.asyncio
    async def test_fallback_devops(self) -> None:
        client = LLMClient()
        response = await client.generate("Configure devops pipeline")
        assert "DevOps" in response.content

    @pytest.mark.asyncio
    async def test_fallback_performance(self) -> None:
        client = LLMClient()
        response = await client.generate("Optimize performance")
        assert "Performance" in response.content

    @pytest.mark.asyncio
    async def test_fallback_accessibility(self) -> None:
        client = LLMClient()
        response = await client.generate("Check accessibility")
        assert "Accessibility" in response.content

    @pytest.mark.asyncio
    async def test_fallback_default(self) -> None:
        client = LLMClient()
        response = await client.generate("Generate some code")
        assert "Generated Code" in response.content
        assert response.model == "fallback"

    def test_get_status(self) -> None:
        client = LLMClient()
        status = client.get_status()
        assert "provider" in status
        assert "providers_available" in status
        assert status["providers_available"]["fallback"] is True
