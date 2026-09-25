from __future__ import annotations

from searchops.retrieval.keyword import ScoredHit


def min_max_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [1.0 if v > 0 else 0.0 for v in values]
    return [(v - lo) / (hi - lo) for v in values]


def fuse_linear(keyword: float, dense: float, alpha: float) -> float:
    alpha = min(1.0, max(0.0, alpha))
    return alpha * dense + (1.0 - alpha) * keyword


def fuse_hits(hits_by_chunk: dict[str, ScoredHit], alpha: float) -> list[ScoredHit]:
    keyword_raw = [h.keyword_score for h in hits_by_chunk.values()]
    dense_raw = [h.dense_score for h in hits_by_chunk.values()]
    keyword_norm = min_max_normalize(keyword_raw)
    dense_norm = min_max_normalize(dense_raw)
    fused: list[ScoredHit] = []
    for hit, k_n, d_n in zip(hits_by_chunk.values(), keyword_norm, dense_norm, strict=True):
        hit.keyword_score = k_n
        hit.dense_score = d_n
        hit.hybrid_score = fuse_linear(k_n, d_n, alpha)
        hit.final_score = hit.hybrid_score
        hit.retrieval_method = "hybrid"
        hit.explanation["fusion"] = {
            "strategy": "linear",
            "alpha": alpha,
            "formula": "alpha * dense + (1-alpha) * keyword",
            "keyword_normalized": k_n,
            "dense_normalized": d_n,
        }
        fused.append(hit)
    fused.sort(key=lambda h: h.final_score, reverse=True)
    return fused


def merge_retriever_lists(
    keyword_hits: list[ScoredHit], dense_hits: list[ScoredHit], alpha: float
) -> list[ScoredHit]:
    combined: dict[str, ScoredHit] = {}
    for hit in keyword_hits:
        combined[hit.chunk_id] = hit
    for hit in dense_hits:
        if hit.chunk_id in combined:
            existing = combined[hit.chunk_id]
            existing.dense_score = hit.dense_score
        else:
            combined[hit.chunk_id] = hit
    return fuse_hits(combined, alpha)
