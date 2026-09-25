from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from searchops.models import Chunk
from searchops.providers.embeddings import EmbeddingProvider, cosine, get_embedding_provider
from searchops.retrieval.filters import chunk_matches_filters, filtered_chunk_query
from searchops.retrieval.hits import ScoredHit, _hit_from_chunk


class DenseRetriever:
    def __init__(self, session: AsyncSession, embedder: EmbeddingProvider | None = None) -> None:
        self.session = session
        self.embedder = embedder or get_embedding_provider()

    async def search(
        self, tenant_id: str, query: str, top_k: int, filters: dict[str, Any] | None = None
    ) -> list[ScoredHit]:
        query_vec = (await self.embedder.embed([query]))[0]
        result = await self.session.execute(filtered_chunk_query(tenant_id, filters))
        chunks = [
            c
            for c in result.scalars().unique().all()
            if c.embedding and chunk_matches_filters(c, filters)
        ]
        scored: list[tuple[Chunk, float]] = []
        for chunk in chunks:
            scored.append((chunk, cosine(query_vec, chunk.embedding)))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            _hit_from_chunk(chunk, dense_score=score, method="dense")
            for chunk, score in scored[:top_k]
        ]
