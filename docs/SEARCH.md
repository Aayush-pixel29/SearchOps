# Search

## BM25

Implemented in `searchops/retrieval/keyword.py`. Classic Robertson/Sparck-Jones BM25 with k1=1.5, b=0.75 over tokenized chunk text plus document title.

## Dense

`HashedEmbeddingProvider` builds a 384-d signed hashed n-gram vector (reproducible, no network). Cosine similarity ranks chunks that already have embeddings.

OpenAI, Gemini, and sentence-transformers adapters exist behind the same interface.

## Hybrid

`searchops/ranking/fusion.py`

1. Collect union of BM25 and dense hits by `chunk_id`.
2. Min-max normalize each score list independently (per query).
3. `hybrid = alpha * dense + (1-alpha) * keyword`.

Default `alpha=0.6`.

## Rerank

- `NoOpReranker` — keep hybrid order
- `HeuristicReranker` — term overlap + title/category boost (default local)
- `CrossEncoderReranker` — `cross-encoder/ms-marco-MiniLM-L-6-v2` if sentence-transformers is installed
- `LLMReranker` — currently delegates to heuristic so a missing API cannot brick search

If rerank throws, the service logs the error and returns hybrid ranks.

## Filters

Supported keys: `category`, `source`, `language`, `tags`, `price_min`, `price_max`, `ram_gb`, `date_from`, `date_to`.

Tenant id is always applied in SQL. Metadata predicates run on the tenant-scoped row set so SQLite tests and Postgres behave the same.

## Explainability

Each hit includes `keyword_score`, `dense_score`, `hybrid_score`, `rerank_score`, `final_score`, `metadata`, and `explanation` (fusion formula, overlap, matched chunk).
