# REST API Reference

The SearchOps backend exposes a structured, RESTful API documented automatically via OpenAPI / Swagger UI at `http://localhost:8000/docs`.

---

## 1. Authentication & Tenant Authorization

### `POST /auth/login`
Authenticates a user and returns an access token containing tenant claims.

**Request Body**:
```json
{
  "email": "demo@searchops.dev",
  "password": "demo-password",
  "tenant_slug": "demo"
}
```

**Response (`200 OK`)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tenant_id": "tenant-demo-1234",
  "tenant_slug": "demo"
}
```

---

## 2. Search & Retrieval

### `POST /search` or `GET /search`
Executes search across the tenant corpus using the specified retrieval and ranking pipeline.

**Request Body**:
```json
{
  "q": "lightweight laptops for programming under ₹80,000",
  "top_k": 10,
  "retrieval_method": "hybrid_rerank",
  "alpha": 0.6,
  "filters": {
    "category": "Laptops",
    "price_max": 80000
  },
  "understand_query": true,
  "use_cache": true
}
```

**Response (`200 OK`)**:
```json
{
  "query": "lightweight laptops for programming under ₹80,000",
  "retrieval_method": "hybrid_rerank",
  "alpha": 0.6,
  "cache_hit": false,
  "results": [
    {
      "document_id": "laptop-zenbook-14",
      "chunk_id": "laptop-zenbook-14_c0",
      "title": "ASUS ZenBook 14 OLED",
      "content": "Ultra-lightweight 1.2kg laptop powered by Intel Core Ultra 7...",
      "source": "catalog",
      "rank": 1,
      "score": 0.938,
      "keyword_score": 0.812,
      "dense_score": 0.840,
      "hybrid_score": 0.829,
      "rerank_score": 0.938,
      "final_score": 0.938,
      "metadata": {
        "price": 76990,
        "category": "Laptops",
        "brand": "ASUS",
        "weight_kg": 1.2
      },
      "explanation": {
        "rerank": {
          "type": "heuristic",
          "term_overlap": 0.75,
          "metadata_boost": 0.13
        }
      }
    }
  ],
  "trace": {
    "spans": {
      "query_parse": 0.4,
      "bm25": 1.2,
      "dense_vector": 8.5,
      "fusion": 0.3,
      "rerank": 1.1
    },
    "total_ms": 11.5
  }
}
```

---

## 3. Documents & Ingestion

- **`POST /documents`**: Ingest a single document text with metadata.
- **`POST /documents/batch`**: Bulk ingest multiple documents with chunking and embeddings.
- **`POST /documents/upload`**: Upload JSON, CSV, Markdown, or TXT file catalogs.
- **`GET /documents`**: List tenant documents with pagination.
- **`DELETE /documents/{id}`**: Remove a document and all corresponding chunks from the index.

---

## 4. Recommendations & Evaluation

- **`GET /recommend/{id}?mode=hybrid|content&top_k=5`**: Generates related item recommendations based on content similarity and vector embeddings.
- **`POST /eval/run`**: Triggers a benchmark run across all labeled evaluation cases and returns Recall@5, Recall@10, MRR, nDCG@10, and latency metrics.
- **`GET /eval/runs`**: Lists past historical benchmark evaluation runs.
- **`GET /metrics`**: Real-time performance statistics, p50/p95 latency counters, and cache hit ratios.
- **`GET /health`**: Health check endpoint (`{"status": "ok"}`).
