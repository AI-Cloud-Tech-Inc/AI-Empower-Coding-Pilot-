"""Tests for the RAG subsystem."""

from __future__ import annotations

from backend.rag.embeddings import EmbeddingService
from backend.rag.retriever import RAGRetriever
from backend.rag.vector_store import VectorStoreManager


def test_embedding_deterministic() -> None:
    svc = EmbeddingService(dimension=64)
    vec_a = svc.embed_text("hello world")
    vec_b = svc.embed_text("hello world")
    assert vec_a == vec_b
    assert len(vec_a) == 64


def test_embedding_similarity() -> None:
    svc = EmbeddingService(dimension=64)
    vec_a = svc.embed_text("python code")
    vec_b = svc.embed_text("python code")
    vec_c = svc.embed_text("completely different text")

    assert svc.similarity(vec_a, vec_b) == 1.0
    assert svc.similarity(vec_a, vec_c) < 1.0


def test_vector_store_add_and_search() -> None:
    store = VectorStoreManager(collection_name="test")
    store.add_documents(
        ["fastapi endpoint", "react component", "database migration"],
        [{"type": "api"}, {"type": "frontend"}, {"type": "db"}],
    )

    results = store.search("api endpoint", k=2)
    assert len(results) == 2
    assert all("score" in r for r in results)


def test_vector_store_delete() -> None:
    store = VectorStoreManager(collection_name="test_del")
    store.add_documents(["doc one"], ids=["d1"])
    assert store.delete("d1") is True
    assert store.delete("nonexistent") is False
    assert store.get_stats()["total_documents"] == 0


def test_rag_retriever_index_and_retrieve() -> None:
    retriever = RAGRetriever(collection_name="test_rag")
    stats = retriever.index_codebase(
        {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n",
            "utils.py": "def helper():\n    pass\n",
        }
    )
    assert stats["files_indexed"] == 2

    results = retriever.retrieve("FastAPI application", k=3)
    assert len(results) > 0


def test_rag_context_for_prompt() -> None:
    retriever = RAGRetriever(collection_name="test_prompt")
    retriever.index_codebase({"file.py": "x = 1\n"})

    context = retriever.get_context_for_prompt("variable")
    assert "file.py" in context
