from __future__ import annotations

from abc import ABC, abstractmethod

from searchops.config import get_settings
from searchops.retrieval.hits import ScoredHit
from searchops.retrieval.keyword import tokenize


class Reranker(ABC):
    name: str = "base"

    @abstractmethod
    async def rerank(self, query: str, hits: list[ScoredHit], top_k: int) -> list[ScoredHit]:
        raise NotImplementedError


class NoOpReranker(Reranker):
    name = "noop"

    async def rerank(self, query: str, hits: list[ScoredHit], top_k: int) -> list[ScoredHit]:
        for i, hit in enumerate(hits[:top_k], start=1):
            hit.rank = i
            hit.rerank_score = hit.final_score
        return hits[:top_k]


class HeuristicReranker(Reranker):
    """Term overlap + metadata match. Local stand-in for a cross-encoder."""

    name = "heuristic"

    async def rerank(self, query: str, hits: list[ScoredHit], top_k: int) -> list[ScoredHit]:
        q_terms = set(tokenize(query))
        scored: list[ScoredHit] = []
        for hit in hits:
            doc_terms = set(tokenize(hit.title + " " + hit.content))
            overlap = len(q_terms & doc_terms) / max(1, len(q_terms))
            meta_boost = 0.0
            title = hit.title.lower()
            if any(term in title for term in q_terms):
                meta_boost += 0.08
            if hit.metadata.get("category") and str(hit.metadata["category"]).lower() in query.lower():
                meta_boost += 0.05
            rerank = 0.7 * hit.final_score + 0.25 * overlap + meta_boost
            hit.rerank_score = rerank
            hit.final_score = rerank
            hit.retrieval_method = "hybrid_rerank"
            hit.explanation["rerank"] = {
                "type": "heuristic",
                "term_overlap": overlap,
                "metadata_boost": meta_boost,
            }
            scored.append(hit)
        scored.sort(key=lambda h: h.final_score, reverse=True)
        for i, hit in enumerate(scored[:top_k], start=1):
            hit.rank = i
        return scored[:top_k]


class CrossEncoderReranker(Reranker):
    name = "cross_encoder"
    _model = None

    async def rerank(self, query: str, hits: list[ScoredHit], top_k: int) -> list[ScoredHit]:
        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            return await HeuristicReranker().rerank(query, hits, top_k)
        if self._model is None:
            CrossEncoderReranker._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [(query, f"{h.title}\n{h.content}") for h in hits]
        scores = self._model.predict(pairs)
        for hit, score in zip(hits, scores, strict=True):
            hit.rerank_score = float(score)
            hit.final_score = float(score)
            hit.retrieval_method = "hybrid_rerank"
            hit.explanation["rerank"] = {"type": "cross_encoder", "model": "ms-marco-MiniLM-L-6-v2"}
        hits.sort(key=lambda h: h.final_score, reverse=True)
        for i, hit in enumerate(hits[:top_k], start=1):
            hit.rank = i
        return hits[:top_k]


class LLMReranker(Reranker):
    name = "llm"

    async def rerank(self, query: str, hits: list[ScoredHit], top_k: int) -> list[ScoredHit]:
        # LLM rerank is optional. Invalid/unavailable models fall back.
        return await HeuristicReranker().rerank(query, hits, top_k)


def get_reranker(name: str | None = None) -> Reranker:
    settings = get_settings()
    choice = (name or settings.reranker).lower()
    mapping: dict[str, type[Reranker]] = {
        "noop": NoOpReranker,
        "heuristic": HeuristicReranker,
        "cross_encoder": CrossEncoderReranker,
        "llm": LLMReranker,
    }
    cls = mapping.get(choice, HeuristicReranker)
    return cls()
