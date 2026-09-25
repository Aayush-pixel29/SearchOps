from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from searchops.api.auth_routes import router as auth_router
from searchops.api.document_routes import router as document_router
from searchops.api.search_routes import router as search_router
from searchops.cache import get_redis
from searchops.config import get_settings
from searchops.db import SessionLocal, create_tables, engine, init_engine
from searchops.demo.seed import ensure_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    await create_tables()
    if SessionLocal is not None:
        async with SessionLocal() as session:
            await ensure_demo_data(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SearchOps",
        description="Search, retrieval, and recommendation engineering platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router)
    app.include_router(document_router)
    app.include_router(search_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/ready")
    async def ready():
        db_ok = engine is not None
        redis_client = await get_redis()
        return {
            "status": "ready" if db_ok else "degraded",
            "database": db_ok,
            "redis": redis_client is not None,
            "embedding_provider": get_settings().embedding_provider,
            "reranker": get_settings().reranker,
        }

    return app


app = create_app()
