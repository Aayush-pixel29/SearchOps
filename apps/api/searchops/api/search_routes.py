from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.db import get_session
from searchops.deps import get_current_user
from searchops.evaluation.engine import EvaluationEngine
from searchops.models import EvaluationRun, User
from searchops.observability import metrics
from searchops.recommend.engine import RecommendationEngine
from searchops.schemas import EvalRunRequest, RecommendRequest, SearchRequest
from searchops.services.search import SearchService

router = APIRouter(tags=["search"])


@router.post("/search")
async def search_post(
    body: SearchRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = SearchService(session)
    return await service.search(
        tenant_id=user.tenant_id,
        query=body.q,
        top_k=body.top_k,
        filters=body.filters,
        retrieval_method=body.retrieval_method,
        alpha=body.alpha,
        understand_query=body.understand_query,
    )


@router.get("/search")
async def search_get(
    q: str,
    top_k: int = 10,
    retrieval_method: str = "hybrid",
    category: str | None = None,
    source: str | None = None,
    language: str | None = None,
    price_max: float | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    filters: dict[str, Any] = {}
    if category:
        filters["category"] = category
    if source:
        filters["source"] = source
    if language:
        filters["language"] = language
    if price_max is not None:
        filters["price_max"] = price_max
    return await SearchService(session).search(
        tenant_id=user.tenant_id,
        query=q,
        top_k=top_k,
        filters=filters,
        retrieval_method=retrieval_method,
    )


@router.get("/recommend/{item_id}")
async def recommend_get(
    item_id: str,
    top_k: int = 5,
    mode: str = "hybrid",
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await RecommendationEngine(session).recommend(user.tenant_id, item_id, top_k, mode)


@router.post("/recommend")
async def recommend_post(
    body: RecommendRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await RecommendationEngine(session).recommend(user.tenant_id, body.item_id, body.top_k, body.mode)


@router.post("/eval/run")
async def eval_run(
    body: EvalRunRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    engine = EvaluationEngine(session)
    run = await engine.run(user.tenant_id, methods=body.methods, top_k=body.top_k)
    return {"id": run.id, "metrics": run.metrics, "table": engine.render(run)}


@router.get("/eval/runs")
async def eval_runs(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = (
        await session.execute(
            select(EvaluationRun)
            .where(EvaluationRun.tenant_id == user.tenant_id)
            .order_by(EvaluationRun.created_at.desc())
        )
    ).scalars().all()
    return [{"id": r.id, "metrics": r.metrics, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]


@router.get("/eval/runs/{run_id}")
async def eval_run_get(run_id: str, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    run = (
        await session.execute(
            select(EvaluationRun).where(EvaluationRun.id == run_id, EvaluationRun.tenant_id == user.tenant_id)
        )
    ).scalar_one_or_none()
    if run is None:
        return {"error": "not found"}
    return {"id": run.id, "metrics": run.metrics, "table": EvaluationEngine.render(run)}


@router.get("/metrics")
async def get_metrics(user: User = Depends(get_current_user)):
    return metrics.snapshot()
