from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from searchops.models import Chunk


@dataclass
class ScoredHit:
    document_id: str
    chunk_id: str
    title: str
    content: str
    source: str
    metadata: dict[str, Any]
    keyword_score: float = 0.0
    dense_score: float = 0.0
    hybrid_score: float = 0.0
    rerank_score: float | None = None
    final_score: float = 0.0
    rank: int = 0
    retrieval_method: str = "keyword"
    explanation: dict[str, Any] = field(default_factory=dict)

    def to_api(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "score": round(self.final_score, 6),
            "rank": self.rank,
            "retrieval_method": self.retrieval_method,
            "keyword_score": round(self.keyword_score, 6),
            "dense_score": round(self.dense_score, 6),
            "hybrid_score": round(self.hybrid_score, 6),
            "rerank_score": None if self.rerank_score is None else round(self.rerank_score, 6),
            "final_score": round(self.final_score, 6),
            "metadata": self.metadata,
            "explanation": self.explanation,
        }


def _hit_from_chunk(
    chunk: Chunk,
    keyword_score: float = 0.0,
    dense_score: float = 0.0,
    method: str = "keyword",
) -> ScoredHit:
    doc = chunk.document
    return ScoredHit(
        document_id=chunk.document_id,
        chunk_id=chunk.id,
        title=doc.title if doc else "",
        content=chunk.content,
        source=doc.source if doc else chunk.extra_metadata.get("source", ""),
        metadata=dict(doc.extra_metadata if doc else chunk.extra_metadata or {}),
        keyword_score=keyword_score,
        dense_score=dense_score,
        hybrid_score=0.0,
        final_score=keyword_score if method == "keyword" else dense_score,
        retrieval_method=method,
        explanation={
            "matched_chunk": chunk.content[:280],
            "document_title": doc.title if doc else "",
        },
    )
