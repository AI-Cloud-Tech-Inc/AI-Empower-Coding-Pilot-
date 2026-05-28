"""Optional Redis cache layer for RAG results and LLM responses."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)

_redis_client: Any | None = None
_redis_available = False


async def _get_redis() -> Any | None:
    global _redis_client, _redis_available
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as aioredis

        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis cache connected at %s", settings.redis_url)
        return _redis_client
    except Exception:
        _redis_available = False
        _redis_client = None
        return None


def _cache_key(prefix: str, data: str) -> str:
    h = hashlib.sha256(data.encode()).hexdigest()[:16]
    return f"aiecp:{prefix}:{h}"


async def cache_get(prefix: str, key_data: str) -> dict[str, Any] | None:
    """Get a cached value. Returns None on miss or if Redis is unavailable."""
    client = await _get_redis()
    if client is None:
        return None
    try:
        raw = await client.get(_cache_key(prefix, key_data))
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


async def cache_set(prefix: str, key_data: str, value: dict[str, Any], ttl: int = 300) -> bool:
    """Set a cached value with TTL in seconds. Returns False if Redis is unavailable."""
    client = await _get_redis()
    if client is None:
        return False
    try:
        await client.setex(_cache_key(prefix, key_data), ttl, json.dumps(value))
        return True
    except Exception:
        return False


async def cache_health() -> dict[str, Any]:
    """Return cache status for the health endpoint."""
    client = await _get_redis()
    if client is None:
        return {"status": "unavailable", "provider": "redis"}
    try:
        info = await client.info("server")
        return {
            "status": "connected",
            "provider": "redis",
            "version": info.get("redis_version", "unknown"),
        }
    except Exception:
        return {"status": "error", "provider": "redis"}
