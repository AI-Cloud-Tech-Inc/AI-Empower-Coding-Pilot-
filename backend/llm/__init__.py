"""LLM integration with OpenAI-compatible backends."""

from backend.llm.client import LLMClient, get_llm_client

__all__ = ["LLMClient", "get_llm_client"]
