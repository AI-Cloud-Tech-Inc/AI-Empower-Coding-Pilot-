"""Embedding service for converting text into vector representations."""

from __future__ import annotations

import hashlib
from typing import Any


class EmbeddingService:
    """Manages text embeddings for RAG.

    Uses a local hashing fallback when no LLM provider is configured,
    making the system testable without API keys.
    """

    def __init__(self, model: str = "text-embedding-3-small", dimension: int = 256) -> None:
        self.model = model
        self.dimension = dimension
        self._cache: dict[str, list[float]] = {}

    def embed_text(self, text: str) -> list[float]:
        """Return a deterministic embedding vector for *text*."""
        if text in self._cache:
            return self._cache[text]

        vector = self._hash_embed(text)
        self._cache[text] = vector
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]

    def _hash_embed(self, text: str) -> list[float]:
        """Deterministic pseudo-embedding via SHA-256 expansion."""
        digest = hashlib.sha256(text.encode()).hexdigest()
        values: list[float] = []
        idx = 0
        while len(values) < self.dimension:
            chunk = digest[idx % len(digest) : idx % len(digest) + 2] or digest[:2]
            values.append((int(chunk, 16) / 255.0) * 2 - 1)
            idx += 2
            if idx >= len(digest):
                digest = hashlib.sha256(digest.encode()).hexdigest()
                idx = 0
        return values[: self.dimension]

    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = sum(a * a for a in vec_a) ** 0.5
        mag_b = sum(b * b for b in vec_b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def get_stats(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "dimension": self.dimension,
            "cached_embeddings": len(self._cache),
        }
