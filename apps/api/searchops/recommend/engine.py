from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from searchops.models import Document
from searchops.providers.embeddings import cosine


class RecommendationEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def recommend(
        self,
        tenant_id: str,
        item_id: str,
        top_k: int = 5,
        mode: str = "hybrid",
    ) -> dict[str, Any]:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.tenant_id == tenant_id, Document.id == item_id)
        )
        source = result.scalar_one_or_none()
        if source is None:
            return {"item_id": item_id, "recommendations": []}

        others = await self.session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.tenant_id == tenant_id, Document.id != item_id)
        )
        candidates = list(others.scalars().unique().all())
        source_vec = _doc_embedding(source)
        scored = []
        for cand in candidates:
            semantic = cosine(source_vec, _doc_embedding(cand)) if source_vec and _doc_embedding(cand) else 0.0
            meta = _metadata_similarity(source.extra_metadata or {}, cand.extra_metadata or {})
            pop = min(1.0, (cand.popularity or 0) / 100.0)
            if mode == "content":
                score = 0.8 * semantic + 0.2 * meta
            else:
                score = 0.6 * semantic + 0.25 * meta + 0.15 * pop
            scored.append(
                {
                    "document_id": cand.id,
                    "title": cand.title,
                    "score": round(score, 6),
                    "semantic_similarity": round(semantic, 6),
                    "metadata_similarity": round(meta, 6),
                    "popularity": cand.popularity,
                    "metadata": cand.extra_metadata,
                }
            )
        scored.sort(key=lambda row: row["score"], reverse=True)
        return {"item_id": item_id, "mode": mode, "recommendations": scored[:top_k]}


def _doc_embedding(doc: Document) -> list[float] | None:
    for chunk in doc.chunks or []:
        if chunk.embedding:
            return chunk.embedding
    return None


def _metadata_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    score = 0.0
    checks = 0
    if a.get("category") or b.get("category"):
        checks += 1
        if a.get("category") == b.get("category"):
            score += 1
    tags_a = set(map(str, a.get("tags") or []))
    tags_b = set(map(str, b.get("tags") or []))
    if tags_a or tags_b:
        checks += 1
        score += (len(tags_a & tags_b) / len(tags_a | tags_b)) if (tags_a | tags_b) else 0
    return score / checks if checks else 0.0
