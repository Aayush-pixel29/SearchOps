# Decisions

## Hashed embeddings as default

CI and first-run demos must work without API keys. Hashing trick embeddings are weak semantically but deterministic. Provider remains an interface.

## SQLite for tests, Postgres for compose

Tests should not require Docker. The domain model is the same. pgvector ANN is intentionally not required for correctness of cosine ranking on <1k chunks.

## Linear fusion, not RRF, as the first hybrid

Linear alpha is easier to explain in the inspector (`alpha * dense + (1-alpha) * keyword`). Reciprocal rank fusion is a follow-up experiment, not the baseline.

## Heuristic reranker as the local cross-encoder stand-in

A 22M cross-encoder is optional. Shipping a broken default that downloads 100MB on `pytest` would make the repo hostile. The heuristic is documented as a stand-in; traces record which reranker ran.

## Tenant on every row

`tenant_id` on documents, chunks, queries, evals, traces. Tokens carry `tenant_id`. Tests assert cross-tenant search cannot see foreign titles.

## JWT + PBKDF2, not OAuth

The goal is authorization wiring, not IAM. Email/password + signed JWT is enough to protect routes.

## In-process metrics

Prometheus is the right next step. A ring buffer is enough to populate the Performance page and traces without extra containers in the default path.
