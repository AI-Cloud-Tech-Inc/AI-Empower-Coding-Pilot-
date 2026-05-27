"""In-memory vector store with optional persistence."""

from __future__ import annotations

import json
import os
from typing import Any

from backend.rag.embeddings import EmbeddingService


class VectorStoreManager:
    """Simple vector store backed by an in-memory index.

    Supports add, search (k-NN via cosine similarity), and persistence
    to a JSON file so the system works without external dependencies.
    """

    def __init__(
        self,
        persist_dir: str = "./data/vectors",
        collection_name: str = "default",
    ) -> None:
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embeddings = EmbeddingService()
        self._documents: list[dict[str, Any]] = []
        self._vectors: list[list[float]] = []

    def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> int:
        """Add documents to the store and return the count of new entries."""
        vectors = self.embeddings.embed_batch(texts)
        metadatas = metadatas or [{}] * len(texts)
        ids = ids or [f"doc_{len(self._documents) + i}" for i in range(len(texts))]

        for doc_id, text, meta, vec in zip(ids, texts, metadatas, vectors):
            self._documents.append({"id": doc_id, "text": text, "metadata": meta})
            self._vectors.append(vec)

        return len(texts)

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Return the top-*k* most similar documents."""
        if not self._documents:
            return []

        query_vec = self.embeddings.embed_text(query)
        scored = [
            (idx, self.embeddings.similarity(query_vec, vec))
            for idx, vec in enumerate(self._vectors)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[dict[str, Any]] = []
        for idx, score in scored[:k]:
            doc = self._documents[idx].copy()
            doc["score"] = round(score, 4)
            results.append(doc)
        return results

    def delete(self, doc_id: str) -> bool:
        for i, doc in enumerate(self._documents):
            if doc["id"] == doc_id:
                self._documents.pop(i)
                self._vectors.pop(i)
                return True
        return False

    def persist(self) -> str:
        """Save the store to disk."""
        os.makedirs(self.persist_dir, exist_ok=True)
        path = os.path.join(self.persist_dir, f"{self.collection_name}.json")
        payload = {
            "collection": self.collection_name,
            "documents": self._documents,
            "vectors": self._vectors,
        }
        with open(path, "w") as f:
            json.dump(payload, f)
        return path

    def load(self) -> bool:
        """Load the store from disk if a snapshot exists."""
        path = os.path.join(self.persist_dir, f"{self.collection_name}.json")
        if not os.path.exists(path):
            return False
        with open(path) as f:
            payload = json.load(f)
        self._documents = payload.get("documents", [])
        self._vectors = payload.get("vectors", [])
        return True

    def get_stats(self) -> dict[str, Any]:
        return {
            "collection": self.collection_name,
            "total_documents": len(self._documents),
            "persist_dir": self.persist_dir,
        }
