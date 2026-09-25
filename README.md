# SearchOps

Search, retrieval, and recommendation engineering platform.

SearchOps is **not** a RAG chatbot. It is a system for ingesting documents, running competing retrievers, inspecting why a document ranked, and measuring ranking quality with standard IR metrics.

## Problem

Product and knowledge search fails in ways a chat box cannot show:

- Keyword search misses paraphrases.
- Dense search misses exact SKUs, prices, and identifiers.
- Hybrid fusion and rerankers change the top-10 in ways that must be measured, not narrated.
- Metadata filters (price, RAM, tenant) belong in the retrieval layer, not in a prompt.

A chatbot that “answers from context” hides all of that. SearchOps makes the pipeline visible.

## Why a normal RAG demo is insufficient

RAG demos typically ship one embedding model, one vector store, and a prompt. They rarely expose BM25 vs dense vs hybrid, rarely compute Recall@K / MRR / nDCG, and rarely isolate tenants. Those are the jobs of a retrieval engineer.

## Architecture

```
Browser (Next.js)
    → FastAPI
         → Query understanding (heuristic / optional LLM, Pydantic-validated)
         → Keyword BM25
         → Dense cosine (hashed embeddings by default)
         → Linear fusion (alpha)
         → Reranker (heuristic / optional cross-encoder)
         → Postgres (documents, chunks, traces) + Redis cache
         → Evaluation engine
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Search pipeline

Query → normalize / extract filters → BM25 + dense → hybrid score → rerank → tenant-scoped results with per-stage scores.

## Retrieval methods

| Method | What it does |
| --- | --- |
| `keyword` | BM25 over chunk text + title |
| `dense` | Cosine similarity on chunk embeddings |
| `hybrid` | `alpha * dense_norm + (1-alpha) * keyword_norm` |
| `hybrid_rerank` | Hybrid candidates passed to a reranker |

`alpha` is configurable (`HYBRID_ALPHA`, request body `alpha`). Ranking code lives in `searchops/ranking/`, not inside the FastAPI route.

## Evaluation methodology

Labeled queries live in `evals/demo_cases.json` (same cases as `searchops.demo.catalog.EVAL_CASES`).

Metrics: Recall@5, Recall@10, MRR, nDCG@10. Latency p50/p95 is measured on the same run.

```bash
cd apps/api && python -m searchops.cli eval
```

### Measured run (hashed embeddings, heuristic reranker, SQLite, 8 queries)

Recorded on 2026-09-25 by `python -m searchops.cli eval`. Reproduce instead of trusting this table if the corpus or embedder changed. Full dump: `evals/last_run.json`.

```text
SearchOps Benchmark

Method                  Recall@10      MRR    nDCG@10  p95 latency
------------------------------------------------------------------
BM25                        0.859    1.000      0.870       16.7ms
Dense                       0.703    0.581      0.537       14.2ms
Hybrid                      0.766    0.812      0.705       27.4ms
Hybrid + Reranker           0.781    0.938      0.792       28.0ms
```

Dense underperforms BM25 here because the default embedder is a hashing trick, not a transformer. That is expected and is why the inspector exists. Swap `EMBEDDING_PROVIDER` before claiming semantic gains.

## Setup (local, no Docker)

Python 3.11+ and Node 20+.

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -e ".[dev]"
set DATABASE_URL=sqlite+aiosqlite:///./searchops.db
set EMBEDDING_PROVIDER=hashed
set DEMO_SEED=true
python -m uvicorn searchops.main:app --reload --port 8000
```

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000. Demo login is `demo@searchops.dev` / `demo-password` (seeded on API startup).

Copy `.env.example` to `.env` when you add Redis/Postgres/API keys. Keys are optional; hashed embeddings and the heuristic reranker need none.

## Docker

```bash
docker compose up --build
```

- API: http://localhost:8000/docs
- Web: http://localhost:3000
- Postgres (pgvector image) and Redis included

Health: `GET /health`, readiness: `GET /ready`.

## Demo flow (about two minutes)

1. Open **Ranking compare**.
2. Run `lightweight laptops for programming under ₹80,000` and `best python backend framework`.
3. Compare BM25 vs dense vs hybrid vs hybrid+rerank lists.
4. Open **Search**, click rank #1, read keyword / dense / rerank / final scores.
5. Open **Evaluation** → Run benchmark. Read Recall@10, MRR, nDCG@10, p95.

## Engineering tradeoffs

- Default embeddings are **hashed n-grams**, not a foundation model. They make CI and laptops work without paid APIs. They are weaker than MiniLM/OpenAI; swap `EMBEDDING_PROVIDER`.
- Metadata filters are applied after a **tenant-scoped SQL fetch**. That is correct isolation and portable across SQLite/Postgres. It is not an ANN+payload index; pgvector IVF/HNSW is a later milestone.
- Redis failures degrade to an in-process dict. Search still returns.
- Reranker failures fall back to hybrid order (`noop_fallback` in the trace).

## Limitations

- Not production-ready: single-process metrics, `create_all` instead of migrations, demo JWT secret.
- No PDF parser yet.
- Cross-encoder and cloud embeddings are adapters, not the default path.
- Brute-force cosine over chunks does not scale to millions of vectors.
- Frontend e2e is manual in v0.1 (API tests cover search).

## Roadmap

1. pgvector ANN + JSONB payload filters pushed into SQL
2. Learned sparse (SPLADE-style) baseline
3. PDF/HTML loaders and better chunking
4. Persistent metrics backend
5. Query-by-query error analysis UI (misses vs false positives)

## Tests

```bash
cd apps/api && python -m pytest -q
```

CI (GitHub Actions): ruff, pytest with mocked/hashed providers, Next.js build, Docker image builds. No paid AI APIs.
