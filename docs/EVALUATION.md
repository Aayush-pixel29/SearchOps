# Evaluation

## Dataset

Eight labeled queries over the demo catalog (laptops, frameworks, IR notes, infra). IDs are stable (`fw-fastapi`, `ir-hybrid`, …).

Source of truth: `apps/api/searchops/demo/catalog.py` (`EVAL_CASES`). Export:

```bash
python scripts/export_catalog.py
```

## Metrics

- **Recall@K** — fraction of relevant document ids appearing in the unique top-K document list.
- **MRR** — 1 / rank of first relevant document (0 if none).
- **nDCG@10** — DCG of model grades vs ideal DCG from `relevance_labels` (1–3).

Implementation: `searchops/evaluation/metrics.py` with unit tests.

## Running

```bash
python -m searchops.cli eval
# or POST /eval/run with a JWT
```

Methods compared: BM25, Dense, Hybrid, Hybrid + Reranker.

Results are stored as `EvaluationRun.metrics` and optionally `evals/last_run.json`. They are computed, never authored by hand.

## Reproducibility

Hashed embeddings are deterministic. Heuristic rerank is deterministic. Same SQLite/Postgres corpus + same cases ⇒ same ranking metrics (latency will vary).
