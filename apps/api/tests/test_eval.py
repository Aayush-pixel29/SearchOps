import pytest

from searchops.ingestion.service import IngestionService
from searchops.evaluation.engine import EvaluationEngine
from searchops.evaluation.metrics import metrics_for_ranking
from searchops.retrieval.hits import ScoredHit
from tests.conftest import make_user


def test_metrics_perfect_ranking():
    hits = [
        ScoredHit("a", "c1", "A", "x", "s", {}, final_score=1, rank=1),
        ScoredHit("b", "c2", "B", "x", "s", {}, final_score=0.5, rank=2),
    ]
    m = metrics_for_ranking(["a", "b"], {"a": 3, "b": 2}, hits)
    assert m["recall_at_5"] == 1.0
    assert m["mrr"] == 1.0
    assert m["ndcg_at_10"] == 1.0


@pytest.mark.asyncio
async def test_eval_run(db_session):
    tenant, _, _ = await make_user(db_session, "ev", "e@x.com")
    ingest = IngestionService(db_session)
    await ingest.ingest_text(tenant.id, "FastAPI", "Python async backend framework", "s", {}, document_id="fw-fastapi")
    await ingest.ingest_text(tenant.id, "Clay pots", "Gardening ceramics", "s", {}, document_id="garden-1")
    from searchops.models import EvaluationCase

    db_session.add(
        EvaluationCase(
            tenant_id=tenant.id,
            query="python backend framework",
            relevant_documents=["fw-fastapi"],
            relevance_labels={"fw-fastapi": 3},
        )
    )
    await db_session.commit()
    run = await EvaluationEngine(db_session).run(tenant.id, methods=["keyword", "dense"], top_k=5)
    assert "BM25" in run.metrics
    assert run.metrics["BM25"]["recall_at_10"] >= 0
    table = EvaluationEngine.render(run)
    assert "SearchOps Benchmark" in table
