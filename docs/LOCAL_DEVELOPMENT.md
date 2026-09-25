# Local development

## Fast path (SQLite, no Redis)

1. `pip install -e ".[dev]"` in `apps/api`
2. `uvicorn searchops.main:app --reload`
3. `npm install && npm run dev` in `apps/web`

Demo seed runs on API startup when `DEMO_SEED=true` (default).

## With Docker infrastructure only

```bash
docker compose up postgres redis
```

Set `DATABASE_URL=postgresql+asyncpg://searchops:searchops@localhost:5432/searchops` and `REDIS_URL=redis://localhost:6379/0`.

## Commands

| Command | Purpose |
| --- | --- |
| `python -m searchops.cli seed` | Ingest demo catalog |
| `python -m searchops.cli eval` | Benchmark retrievers |
| `python -m pytest -q` | Tests (hashed embeddings, no paid APIs) |
| `make up` | Full compose stack |

## Optional models

```
EMBEDDING_PROVIDER=huggingface
RERANKER=cross_encoder
pip install 'sentence-transformers'
```

Hardware permitting, that enables a real MiniLM bi-encoder and MS MARCO MiniLM cross-encoder.
