from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from searchops.cache import cache_get, cache_set
from searchops.config import get_settings
from searchops.models import SearchQuery, SearchResultRow, SearchTrace
from searchops.observability import SearchTraceRecorder, cache_key, metrics
from searchops.providers.llm import extract_query_structured
from searchops.ranking.fusion import merge_retriever_lists
from searchops.ranking.rerank import NoOpReranker, get_reranker
from searchops.retrieval.dense import DenseRetriever
from searchops.retrieval.hits import ScoredHit
from searchops.retrieval.keyword import KeywordRetriever


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.keyword = KeywordRetriever(session)
        self.dense = DenseRetriever(session)

    async def search(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
        retrieval_method: str = "hybrid",
        alpha: float | None = None,
        understand_query: bool = True,
        use_cache: bool = True,
        persist: bool = True,
    ) -> dict[str, Any]:
        settings = get_settings()
        alpha = settings.hybrid_alpha if alpha is None else alpha
        trace = SearchTraceRecorder(query)
        trace.start("search_request")

        parsed_filters = dict(filters or {})
        semantic_query = query
        parse_info: dict[str, Any] = {"fallback": True}
        trace.start("query_parse")
        if understand_query:
            extracted = await extract_query_structured(query)
            semantic_query = extracted.semantic_query or query
            for key, value in extracted.filters.items():
                parsed_filters.setdefault(key, value)
            parse_info = extracted.model_dump()
            parse_info["fallback"] = False
        trace.end("query_parse", parsed=parse_info)

        key = cache_key(
            {
                "tenant": tenant_id,
                "q": query,
                "filters": parsed_filters,
                "top_k": top_k,
                "method": retrieval_method,
                "alpha": alpha,
            }
        )
        if use_cache:
            cached = await cache_get(key)
            if cached:
                trace.cache_hit = True
                metrics.increment("cache_hit")
                metrics.observe("search_cached", 0.5)
                trace.end("search_request", cache="hit")
                cached["trace"] = trace.to_dict()
                cached["cache_hit"] = True
                return cached
            metrics.increment("cache_miss")

        keyword_hits: list[ScoredHit] = []
        dense_hits: list[ScoredHit] = []
        method = retrieval_method.lower()
        candidate_k = max(top_k * 4, 20)

        if method in {"keyword", "bm25", "hybrid", "hybrid_rerank"}:
            trace.start("keyword_search")
            try:
                keyword_hits = await self.keyword.search(tenant_id, semantic_query, candidate_k, parsed_filters)
            except Exception as exc:
                trace.errors.append(f"keyword_search failed: {exc}")
            trace.end("keyword_search", hits=len(keyword_hits))

        if method in {"dense", "vector", "hybrid", "hybrid_rerank"}:
            trace.start("vector_search")
            try:
                dense_hits = await self.dense.search(tenant_id, semantic_query, candidate_k, parsed_filters)
            except Exception as exc:
                trace.errors.append(f"vector_search failed: {exc}")
                if method == "dense":
                    keyword_hits = await self.keyword.search(tenant_id, semantic_query, candidate_k, parsed_filters)
                    method = "keyword"
            trace.end("vector_search", hits=len(dense_hits))

        trace.start("fusion")
        if method in {"keyword", "bm25"}:
            hits = keyword_hits[:top_k]
            for i, hit in enumerate(hits, start=1):
                hit.rank = i
                hit.final_score = hit.keyword_score
                hit.retrieval_method = "keyword"
        elif method in {"dense", "vector"}:
            hits = dense_hits[:top_k]
            for i, hit in enumerate(hits, start=1):
                hit.rank = i
                hit.final_score = hit.dense_score
                hit.retrieval_method = "dense"
        else:
            hits = merge_retriever_lists(keyword_hits, dense_hits, alpha)[:candidate_k]
        trace.end("fusion", hits=len(hits), alpha=alpha)

        trace.start("rerank")
        reranker_used = "none"
        if method == "hybrid_rerank":
            reranker = get_reranker()
            try:
                hits = await reranker.rerank(semantic_query, hits, top_k)
                reranker_used = reranker.name
            except Exception as exc:
                trace.errors.append(f"reranker failed: {exc}")
                hits = await NoOpReranker().rerank(semantic_query, hits, top_k)
                reranker_used = "noop_fallback"
        else:
            hits = hits[:top_k]
            for i, hit in enumerate(hits, start=1):
                hit.rank = i
        trace.end("rerank", reranker=reranker_used)

        payload = {
            "query": query,
            "semantic_query": semantic_query,
            "filters": parsed_filters,
            "query_understanding": parse_info,
            "retrieval_method": method,
            "alpha": alpha,
            "cache_hit": False,
            "results": [h.to_api() for h in hits],
        }
        trace.end("response", result_count=len(hits))
        trace.end("search_request")
        payload["trace"] = trace.to_dict()

        total = payload["trace"]["total_ms"]
        metrics.observe("search_uncached", total)
        metrics.observe("search", total)
        for name, span in payload["trace"]["spans"].items():
            metrics.observe(name, span["duration_ms"])

        if persist:
            logged = SearchQuery(
                tenant_id=tenant_id,
                query=query,
                filters=parsed_filters,
                retrieval_method=method,
            )
            self.session.add(logged)
            await self.session.flush()
            for hit in hits:
                self.session.add(
                    SearchResultRow(
                        search_query_id=logged.id,
                        document_id=hit.document_id,
                        chunk_id=hit.chunk_id,
                        score=hit.final_score,
                        rank=hit.rank,
                        retrieval_method=hit.retrieval_method,
                        extra_metadata=hit.to_api(),
                    )
                )
            self.session.add(
                SearchTrace(
                    tenant_id=tenant_id,
                    query=query,
                    cache_hit=0,
                    token_usage=trace.token_usage,
                    estimated_cost_usd=trace.estimated_cost_usd,
                    spans=payload["trace"],
                )
            )
            await self.session.commit()

        if use_cache:
            await cache_set(key, {k: v for k, v in payload.items() if k != "trace"})
        return payload
