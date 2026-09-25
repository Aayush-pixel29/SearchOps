.PHONY: help install api web test lint eval seed up down ci

help:
	@echo "SearchOps targets:"
	@echo "  make install  - install API + web deps"
	@echo "  make api      - run FastAPI locally"
	@echo "  make web      - run Next.js locally"
	@echo "  make test     - pytest (SQLite, mocked providers)"
	@echo "  make eval     - run retrieval benchmark"
	@echo "  make seed     - ingest demo catalog"
	@echo "  make up       - docker compose up"
	@echo "  make down     - docker compose down"
	@echo "  make ci       - lint + typecheck + tests + web build"

install:
	cd apps/api && python -m pip install -e ".[dev]"
	cd apps/web && npm install

api:
	cd apps/api && python -m uvicorn searchops.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev

test:
	cd apps/api && python -m pytest -q

lint:
	cd apps/api && python -m ruff check searchops tests
	cd apps/web && npm run lint

eval:
	cd apps/api && python -m searchops.cli eval

seed:
	cd apps/api && python -m searchops.cli seed

up:
	docker compose up --build

down:
	docker compose down

ci:
	cd apps/api && python -m ruff check searchops tests
	cd apps/api && python -m pytest -q
	cd apps/web && npm install && npm run build
