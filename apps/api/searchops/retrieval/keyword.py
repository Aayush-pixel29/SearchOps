from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from searchops.models import Chunk
from searchops.retrieval.filters import chunk_matches_filters, filtered_chunk_query
from searchops.retrieval.hits import ScoredHit, _hit_from_chunk


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs: list[Chunk] = []
        self.doc_len: list[int] = []
        self.avgdl = 0.0
        self.df: dict[str, int] = defaultdict(int)
        self.tf: list[Counter[str]] = []
        self.n = 0

    def build(self, chunks: list[Chunk]) -> None:
        self.docs = chunks
        self.tf = []
        self.doc_len = []
        self.df = defaultdict(int)
        for chunk in chunks:
            tokens = tokenize(chunk.content + " " + (chunk.document.title if chunk.document else ""))
            counts = Counter(tokens)
            self.tf.append(counts)
            self.doc_len.append(len(tokens) or 1)
            for term in counts:
                self.df[term] += 1
        self.n = len(chunks)
        self.avgdl = sum(self.doc_len) / self.n if self.n else 1.0

    def score(self, query: str) -> list[tuple[Chunk, float]]:
        q_tokens = tokenize(query)
        if not q_tokens or not self.n:
            return []
        hits: list[tuple[Chunk, float]] = []
        for i, chunk in enumerate(self.docs):
            score = 0.0
            dl = self.doc_len[i]
            for term in q_tokens:
                if term not in self.tf[i]:
                    continue
                df = self.df[term]
                idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
                freq = self.tf[i][term]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                score += idf * (freq * (self.k1 + 1)) / denom
            if score > 0:
                hits.append((chunk, score))
        hits.sort(key=lambda item: item[1], reverse=True)
        return hits


class KeywordRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self, tenant_id: str, query: str, top_k: int, filters: dict[str, Any] | None = None
    ) -> list[ScoredHit]:
        result = await self.session.execute(filtered_chunk_query(tenant_id, filters))
        chunks = [c for c in result.scalars().unique().all() if chunk_matches_filters(c, filters)]
        index = BM25Index()
        index.build(chunks)
        ranked = index.score(query)[:top_k]
        return [_hit_from_chunk(chunk, keyword_score=score, method="keyword") for chunk, score in ranked]
