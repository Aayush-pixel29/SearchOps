from __future__ import annotations

import math
from typing import Any

from searchops.retrieval.hits import ScoredHit


def recall_at_k(relevant: list[str], ranked_ids: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(ranked_ids[:k]) & set(relevant)) / len(set(relevant))


def mrr(relevant: list[str], ranked_ids: list[str]) -> float:
    rel = set(relevant)
    for idx, doc_id in enumerate(ranked_ids, start=1):
        if doc_id in rel:
            return 1.0 / idx
    return 0.0


def dcg(grades: list[float]) -> float:
    return sum((2**g - 1) / math.log2(i + 1) for i, g in enumerate(grades, start=1))


def ndcg_at_k(relevance_labels: dict[str, int], ranked_ids: list[str], k: int) -> float:
    gains = [float(relevance_labels.get(doc_id, 0)) for doc_id in ranked_ids[:k]]
    ideal = sorted((float(v) for v in relevance_labels.values()), reverse=True)[:k]
    if not ideal or dcg(ideal) == 0:
        # If only binary relevant_documents were provided, synthesize labels.
        if not relevance_labels:
            return 0.0
        return 0.0 if dcg(ideal) == 0 else dcg(gains) / dcg(ideal)
    return dcg(gains) / dcg(ideal)


def labels_from_case(relevant_documents: list[str], relevance_labels: dict[str, int] | None) -> dict[str, int]:
    if relevance_labels:
        return {str(k): int(v) for k, v in relevance_labels.items()}
    return {doc_id: 1 for doc_id in relevant_documents}


def metrics_for_ranking(
    relevant_documents: list[str],
    relevance_labels: dict[str, int] | None,
    hits: list[ScoredHit],
) -> dict[str, float]:
    ranked_ids: list[str] = []
    seen: set[str] = set()
    for hit in hits:
        if hit.document_id not in seen:
            ranked_ids.append(hit.document_id)
            seen.add(hit.document_id)
    labels = labels_from_case(relevant_documents, relevance_labels)
    return {
        "recall_at_5": recall_at_k(relevant_documents, ranked_ids, 5),
        "recall_at_10": recall_at_k(relevant_documents, ranked_ids, 10),
        "mrr": mrr(relevant_documents, ranked_ids),
        "ndcg_at_10": ndcg_at_k(labels, ranked_ids, 10),
    }


def mean_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    if not rows:
        return {"recall_at_5": 0.0, "recall_at_10": 0.0, "mrr": 0.0, "ndcg_at_10": 0.0}
    keys = rows[0].keys()
    return {k: sum(r[k] for r in rows) / len(rows) for k in keys}


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def format_benchmark_table(results: dict[str, dict[str, Any]]) -> str:
    lines = [
        "SearchOps Benchmark",
        "",
        f"{'Method':<20} {'Recall@5':>10} {'Recall@10':>10} {'MRR':>8} {'nDCG@10':>10} {'p50':>8} {'p95':>8}",
        "-" * 80,
    ]
    for method, row in results.items():
        r5 = row.get("recall_at_5", 0.0)
        r10 = row.get("recall_at_10", 0.0)
        m = row.get("mrr", 0.0)
        ndcg = row.get("ndcg_at_10", 0.0)
        p50 = row.get("p50_ms", 0.0)
        p95 = row.get("p95_ms", 0.0)
        lines.append(
            f"{method:<20} {r5:>10.3f} {r10:>10.3f} {m:>8.3f} "
            f"{ndcg:>10.3f} {p50:>7.1f}ms {p95:>7.1f}ms"
        )
    return "\n".join(lines)
