# Architecture Decision Records (ADRs) & Engineering Tradeoffs

This document outlines key architectural decisions, rationale, and explicit engineering tradeoffs made in SearchOps.

---

### ADR 01: Hashed N-Gram Embeddings as Default Baseline
- **Decision**: Use a deterministic 384-dimensional hashed n-gram embedding algorithm as the default zero-config provider.
- **Rationale**: Enables instant offline execution, predictable testing, and GitHub Actions CI without requiring paid cloud API keys or downloading massive models during initial setup.
- **Tradeoff**: Hashed vectors lack true semantic deep learning representation (which is why dense retrieval underperforms BM25 under this provider). To achieve full semantic quality, developers can swap `EMBEDDING_PROVIDER=huggingface` (`all-MiniLM-L6-v2`) or cloud providers.

---

### ADR 02: Linear Convex Fusion vs. Reciprocal Rank Fusion (RRF)
- **Decision**: Implement min-max normalized linear convex combination ($\alpha$-fusion) as the primary hybrid search mechanism.
- **Rationale**: Linear $\alpha$-fusion yields directly interpretable continuous scores ($s \in [0, 1]$) that can be clearly decomposed and audited in the SearchOps Ranking Inspector.
- **Tradeoff**: Min-max normalization is sensitive to outlier scores in sparse BM25 lists. RRF is less sensitive to score distributions but discards relative score magnitudes.

---

### ADR 03: Fail-Open Resilience Patterns
- **Decision**:
  1. **Redis Cache Fallback**: If Redis is unreachable or crashes, the system transparently falls back to an in-memory TTL dictionary cache without raising an exception.
  2. **Reranker Fallback**: If an advanced Cross-Encoder or neural reranker fails (e.g. CUDA OOM or network timeout), the pipeline falls back to hybrid ranking and records `noop_fallback` in the telemetry trace.
- **Rationale**: Search retrieval in production systems must prioritize uptime and availability over non-critical enhancements.

---

### ADR 04: Multi-Tenant Partitioning at Storage Layer
- **Decision**: Every document, chunk, query log, evaluation case, and trace explicitly carries a foreign key `tenant_id`. All database queries strictly filter by `tenant_id`.
- **Rationale**: Prevents accidental data leaks across different corporate or application tenants.
- **Tradeoff**: Requires passing tenant context through all repository queries rather than relying purely on global indices.

---

### ADR 05: Database Portability (Async SQLite & PostgreSQL pgvector)
- **Decision**: Support both async SQLite (`sqlite+aiosqlite`) for local development/testing and PostgreSQL (`postgresql+asyncpg`) for containerized production.
- **Rationale**: Allows developers to run tests in seconds without requiring Docker, while preserving the exact same SQLAlchemy data models in production.
- **Tradeoff**: In SQLite mode, vector similarity is computed via in-memory NumPy cosine dot products across the tenant chunks rather than database-native vector index ANN. For production scale (>100k chunks per tenant), pgvector HNSW/IVFFlat indexing is recommended.
