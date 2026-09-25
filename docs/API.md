# API

OpenAPI: `http://localhost:8000/docs`

## Auth

- `POST /auth/register` `{email, password, tenant_name, tenant_slug}`
- `POST /auth/login` `{email, password, tenant_slug}`
- Header: `Authorization: Bearer <jwt>`

## Documents

- `POST /documents` `{title, content, source?, metadata?, id?}`
- `POST /documents/bulk`
- `GET /documents`
- `GET /documents/{id}`
- `DELETE /documents/{id}`

## Search

`GET /search?q=python+backend&retrieval_method=dense&top_k=10`

`POST /search`

```json
{
  "q": "laptops under 80000",
  "top_k": 10,
  "filters": {"category": "laptop"},
  "retrieval_method": "hybrid_rerank",
  "alpha": 0.6,
  "understand_query": true
}
```

`retrieval_method`: `keyword` | `bm25` | `dense` | `hybrid` | `hybrid_rerank`

## Recommend

`GET /recommend/{item_id}?mode=hybrid|content&top_k=5`

## Eval / ops

- `POST /eval/run`
- `GET /eval/runs`
- `GET /eval/runs/{id}`
- `GET /metrics`
- `GET /health`
- `GET /ready`
- `GET /admin/tenant`
