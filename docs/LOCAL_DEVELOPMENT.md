# Local Development Guide

This guide walks through setting up SearchOps locally on a clean machine for development, testing, and benchmarking.

---

## 1. Prerequisites
- **Python**: Version 3.11 or newer
- **Node.js**: Version 20 LTS or newer
- **Git**
- *(Optional)* **Docker & Docker Compose**

---

## 2. Fast Setup (Zero-External Dependencies)

SearchOps is configured to run fully offline using async SQLite and deterministic hashed embeddings by default.

### Backend (FastAPI)
```bash
cd apps/api

# 1. Create and activate a Python virtual environment
python -m venv .venv
# On Windows (PowerShell/CMD):
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 2. Install package in editable mode with development dependencies
pip install -e ".[dev]"

# 3. Configure environment variables (SQLite mode)
# Windows (PowerShell):
$env:DATABASE_URL="sqlite+aiosqlite:///./searchops.db"
$env:EMBEDDING_PROVIDER="hashed"
$env:DEMO_SEED="true"
# Unix/macOS:
export DATABASE_URL="sqlite+aiosqlite:///./searchops.db"
export EMBEDDING_PROVIDER="hashed"
export DEMO_SEED="true"

# 4. Start the development server
python -m uvicorn searchops.main:app --reload --port 8000
```

### Frontend (Next.js 14)
```bash
cd apps/web

# 1. Install Node dependencies
npm install

# 2. Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## 3. Running with Transformer Embeddings (MiniLM)

To run high-accuracy semantic embeddings with local Sentence-Transformers:

```bash
cd apps/api

# Run evaluation with MiniLM embeddings:
python -m searchops.cli eval --provider huggingface --reseed
```

---

## 4. Running Test Suites

### Backend Unit & Integration Tests (Pytest)
```bash
cd apps/api
python -m pytest -q
```

### Backend Linter (Ruff)
```bash
cd apps/api
python -m ruff check searchops tests
```

### Frontend Typechecking & Production Build
```bash
cd apps/web
npm run lint
npm run build
```

### Frontend End-to-End Tests (Playwright)
```bash
cd apps/web
npx playwright test
```

---

## 5. Docker Full Stack Setup

```bash
# Start PostgreSQL (with pgvector), Redis, FastAPI API, and Next.js Web:
docker compose up --build

# Stop all services:
docker compose down
```
