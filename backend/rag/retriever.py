"""RAG retriever — combines vector search with context assembly."""

from __future__ import annotations

from typing import Any

from backend.rag.vector_store import VectorStoreManager


class RAGRetriever:
    """Retrieval-Augmented Generation retriever.

    Indexes code files and documentation, then retrieves relevant
    context to augment LLM prompts.
    """

    def __init__(self, collection_name: str = "codebase") -> None:
        self.store = VectorStoreManager(collection_name=collection_name)

    def index_codebase(self, files: dict[str, str]) -> dict[str, Any]:
        """Index a set of code files into the vector store."""
        texts: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ids: list[str] = []

        for filepath, content in files.items():
            chunks = self._chunk_text(content, filepath)
            for i, chunk in enumerate(chunks):
                texts.append(chunk["text"])
                metadatas.append(chunk["metadata"])
                ids.append(f"{filepath}::chunk_{i}")

        count = self.store.add_documents(texts, metadatas, ids)
        return {"files_indexed": len(files), "chunks_created": count}

    def retrieve(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Retrieve relevant code context for a query."""
        return self.store.search(query, k=k)

    def get_context_for_prompt(self, query: str, k: int = 5) -> str:
        """Build a formatted context string suitable for LLM prompts."""
        results = self.retrieve(query, k=k)
        if not results:
            return "No relevant context found."

        parts: list[str] = []
        for r in results:
            source = r.get("metadata", {}).get("source", "unknown")
            parts.append(f"--- {source} (score: {r['score']}) ---\n{r['text']}")

        return "\n\n".join(parts)

    @staticmethod
    def _chunk_text(
        content: str,
        filepath: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[dict[str, Any]]:
        """Split text into overlapping chunks with metadata."""
        lines = content.splitlines()
        chunks: list[dict[str, Any]] = []

        current_chunk: list[str] = []
        current_len = 0

        for line_num, line in enumerate(lines, start=1):
            current_chunk.append(line)
            current_len += len(line)

            if current_len >= chunk_size:
                chunk_text = "\n".join(current_chunk)
                chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": {
                            "source": filepath,
                            "start_line": line_num - len(current_chunk) + 1,
                            "end_line": line_num,
                        },
                    }
                )
                # Keep overlap
                overlap_lines = max(1, len(current_chunk) * overlap // chunk_size)
                current_chunk = current_chunk[-overlap_lines:]
                current_len = sum(len(line) for line in current_chunk)

        if current_chunk:
            chunks.append(
                {
                    "text": "\n".join(current_chunk),
                    "metadata": {
                        "source": filepath,
                        "start_line": len(lines) - len(current_chunk) + 1,
                        "end_line": len(lines),
                    },
                }
            )

        return chunks
