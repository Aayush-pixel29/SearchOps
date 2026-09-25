from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.evaluation.metrics import format_benchmark_table, mean_metrics, metrics_for_ranking, percentile
from searchops.models import EvaluationCase, EvaluationRun
from searchops.services.search import SearchService

METHODS = ["keyword", "dense", "hybrid", "hybrid_rerank"]
METHOD_LABELS = {
    "keyword": "BM25",
    "dense": "Dense",
    "hybrid": "Hybrid",
    "hybrid_rerank": "Hybrid + Reranker",
}


class EvaluationEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.search = SearchService(session)

    async def load_file(self, tenant_id: str, path: Path) -> int:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cases = payload["cases"] if isinstance(payload, dict) else payload
        count = 0
        for case in cases:
            kwargs = {
                "tenant_id": tenant_id,
                "query": case["query"],
                "relevant_documents": case.get("relevant_documents") or [],
                "relevance_labels": case.get("relevance_labels") or {},
            }
            if case.get("id"):
                kwargs["id"] = case["id"]
            self.session.add(EvaluationCase(**kwargs))
            count += 1
        await self.session.commit()
        return count

    async def run(self, tenant_id: str, methods: list[str] | None = None, top_k: int = 10) -> EvaluationRun:
        methods = methods or METHODS
        result = await self.session.execute(
            select(EvaluationCase).where(EvaluationCase.tenant_id == tenant_id)
        )
        cases = list(result.scalars().all())
        per_method: dict[str, dict[str, Any]] = {}
        for method in methods:
            metric_rows = []
            latencies = []
            details = []
            for case in cases:
                started = time.perf_counter()
                response = await self.search.search(
                    tenant_id=tenant_id,
                    query=case.query,
                    top_k=top_k,
                    retrieval_method=method,
                    use_cache=False,
                    persist=False,
                    understand_query=False,
                )
                elapsed = (time.perf_counter() - started) * 1000
                latencies.append(elapsed)
                hits = []
                from searchops.retrieval.hits import ScoredHit

                for item in response["results"]:
                    hits.append(
                        ScoredHit(
                            document_id=item["document_id"],
                            chunk_id=item["chunk_id"],
                            title=item.get("title", ""),
                            content=item.get("content", ""),
                            source=item.get("source", ""),
                            metadata=item.get("metadata") or {},
                            final_score=item["score"],
                            rank=item["rank"],
                            retrieval_method=item["retrieval_method"],
                        )
                    )
                row = metrics_for_ranking(case.relevant_documents, case.relevance_labels, hits)
                metric_rows.append(row)
                details.append(
                    {
                        "query": case.query,
                        "metrics": row,
                        "ranked": [h.document_id for h in hits],
                        "relevant": case.relevant_documents,
                    }
                )
            averaged = mean_metrics(metric_rows)
            per_method[METHOD_LABELS.get(method, method)] = {
                **averaged,
                "p50_ms": percentile(latencies, 50),
                "p95_ms": percentile(latencies, 95),
                "n_queries": len(cases),
                "details": details,
            }
        run = EvaluationRun(
            tenant_id=tenant_id,
            status="completed",
            methods=methods,
            metrics=per_method,
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    @staticmethod
    def render(run: EvaluationRun) -> str:
        compact = {
            method: {
                "recall_at_10": row["recall_at_10"],
                "mrr": row["mrr"],
                "ndcg_at_10": row["ndcg_at_10"],
                "p95_ms": row["p95_ms"],
            }
            for method, row in run.metrics.items()
        }
        return format_benchmark_table(compact)
