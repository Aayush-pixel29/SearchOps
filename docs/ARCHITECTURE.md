# System Architecture

SearchOps is structured as a decoupled, production-grade retrieval platform designed for search experimentation, multi-tenant indexing, and Information Retrieval (IR) benchmarking.

---

## 1. High-Level Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Next.js 14 Web Frontend                         │
│   (Search Playground, Ranking Compare, Evaluation, Documents, Admin)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON
                                    │ (Bearer JWT / Tenant Scoped)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Gateway & API                         │
│  - JWT Authentication & Multi-Tenant Context Resolution               │
│  - Request Validation (Pydantic v2 schemas)                            │
│  - Query Understanding & Filter Extraction                            │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
       ┌────────────▼────────────┐     ┌────────────▼────────────┐
       │     Retrieval Engine    │     │   Redis Response Cache  │
       │ - BM25 Lexical Search   │     │ (With In-Memory Fallback│
       │ - Dense Cosine Search   │     └─────────────────────────┘
       │ - Linear Hybrid Fusion  │
       │ - Candidate Reranker    │
       └────────────┬────────────┘
                    │
       ┌────────────▼────────────┐
       │   Persistence Layer     │
       │ - PostgreSQL / SQLite   │
       │ - Chunks & Embeddings   │
       │ - Traces & Eval Runs    │
       └─────────────────────────┘
```

---

## 2. Directory Structure & Modular Separation

```
searchops/
├── apps/
│   ├── api/                           # FastAPI Application & Retrieval Backend
│   │   ├── searchops/
│   │   │   ├── api/                   # HTTP Route Controllers (auth, docs, search)
│   │   │   ├── ingestion/             # File loaders, text chunkers, ingestion pipeline
│   │   │   ├── retrieval/             # BM25, dense vector cosine, metadata filtering
│   │   │   ├── ranking/               # Linear alpha fusion and candidate rerankers
│   │   │   ├── query/                 # Query parsing and rule-based understanding
│   │   │   ├── evaluation/            # IR metrics (Recall@K, MRR, nDCG@10) & benchmarks
│   │   │   ├── recommend/             # Content-based & hybrid recommendation engine
│   │   │   ├── providers/             # Pluggable embeddings & LLM interfaces (no vendor lock)
│   │   │   ├── demo/                  # Seed catalog and labeled evaluation cases
│   │   │   ├── db.py / models.py      # Async SQLAlchemy ORM & PostgreSQL/SQLite schemas
│   │   │   ├── auth.py / cache.py     # JWT hashing and Redis TTL caching layer
│   │   │   └── cli.py                 # CLI for seeding, export, and running benchmarks
│   │   └── tests/                     # 18 Pytest unit and integration tests
│   └── web/                           # Next.js 14 Dashboard (TypeScript + Tailwind CSS)
│       ├── app/                       # 6 Interactive App Pages (Search, Compare, Eval, etc.)
│       ├── components/                # Reusable navigation and UI components
│       ├── lib/                       # API clients, authentication helpers, and types
│       └── tests/                     # Playwright E2E end-to-end test suite
├── evals/                             # Labeled query datasets & JSON benchmark dumps
├── data/raw/                          # Seed e-commerce / product catalog export
├── docs/                              # Deep technical specifications & screenshots
├── docker-compose.yml                 # Multi-container orchestration
└── .github/workflows/ci.yml           # Automated CI workflow
```

---

## 3. Core Data Models

- **`Tenant`**: Root isolation partition owning all users, documents, chunks, queries, evaluation cases, and telemetry traces.
- **`User`**: Tenant-bound user with hashed passwords (bcrypt) and JWT credentials.
- **`Document`**: Parent document record (title, source, full raw content, metadata JSON).
- **`Chunk`**: Searchable fragment with token count, chunk index, metadata attributes, and embedded dense vector.
- **`SearchQuery` & `SearchResultRow`**: Full historical search log recording queries, applied filters, retrieval methods, returned hits, and score explanations.
- **`EvaluationCase`**: Ground truth labeled test query containing relevant document IDs and graded relevance judgements (0–3 scale).
- **`EvaluationRun`**: Persisted benchmark run storing aggregated metrics per retrieval method.
- **`SearchTrace`**: Telemetry log recording latency spans (`query_parse`, `bm25`, `dense_vector`, `fusion`, `rerank`).

---

## 4. End-to-End Query Lifecycle

1. **Authentication & Multi-Tenant Scoping**: The incoming JWT token is validated; the authenticated `tenant_id` is injected into the request state. All database queries strictly filter by `tenant_id`.
2. **Query Understanding**: The raw query is passed through a deterministic heuristic parser (or optional LLM) to identify intent, price bounds, category filters, and brand keywords.
3. **Cache Lookup**: A deterministic cache key (`tenant:query:method:alpha:top_k:filters`) is checked in Redis. If found, cached results are returned immediately with `cache_hit=true`.
4. **Candidate Retrieval**:
   - **BM25 Retriever**: Tokenizes the query and corpus chunks, calculating BM25 term weights across titles and bodies.
   - **Dense Retriever**: Generates a query vector via the configured embedding provider and computes cosine similarity against stored chunk vectors.
5. **Score Normalization & Linear Fusion**: Lexical and dense scores are min-max normalized into $[0, 1]$ and fused using the configurable parameter $\alpha$:
   $$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{dense}} + (1 - \alpha) \cdot \text{Score}_{\text{BM25}}$$
6. **Candidate Reranking**: The top candidate window is reranked using lexical overlap, metadata attribute bonuses, and cross-encoder scoring.
7. **Trace & Response**: Stage timings are recorded into a `SearchTrace` span and the ranked list is returned with complete score breakdowns.
