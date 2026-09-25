# Architecture

SearchOps splits **product UI**, **HTTP/API**, **retrieval**, and **model providers**.

```
apps/web          Next.js dashboard (search is the product, not chat)
apps/api          FastAPI process
  searchops/
    api/          HTTP adapters
    ingestion/    loaders, cleaner, chunker, repository
    retrieval/    BM25, dense, filters
    ranking/      fusion, rerankers
    evaluation/   IR metrics + benchmark runner
    providers/    embeddings + LLM (no business logic here)
    recommend/    content / hybrid recommenders
    demo/         catalog + labels
```

## Data model

- `Tenant` owns `User`, `Document`, `Chunk`, eval cases, traces.
- `Document` holds title/content/source/metadata.
- `Chunk` holds text + embedding JSON + metadata.
- `SearchQuery` / `SearchResultRow` persist explainable rankings.
- `EvaluationCase` / `EvaluationRun` store labels and measured metrics.
- `SearchTrace` stores span timings for a request.

## Request path

1. JWT → `tenant_id` (unauthorized requests never search).
2. Optional query understanding → Pydantic `ExtractedQuery`; invalid model output falls back to the raw query.
3. Cache key = tenant + query + filters + top_k + method + alpha.
4. Retrievers run independently, then fusion, then rerank.
5. Trace spans: `search_request` → `query_parse` → `keyword_search` → `vector_search` → `fusion` → `rerank` → `response`.

## Provider swap

`EMBEDDING_PROVIDER=hashed|mock|openai|gemini|huggingface`

`RERANKER=noop|heuristic|cross_encoder|llm`

`LLM_PROVIDER=none|heuristic|openai`

Ranking code never imports a vendor SDK.
