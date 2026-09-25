import pytest

from searchops.ingestion.service import IngestionService
from searchops.services.search import SearchService
from tests.conftest import make_user


@pytest.mark.asyncio
async def test_keyword_and_dense_and_hybrid(db_session):
    tenant, _, _ = await make_user(db_session, "t1", "a@x.com")
    ingest = IngestionService(db_session)
    await ingest.ingest_text(tenant.id, "FastAPI Guide", "FastAPI is a Python async backend framework with OpenAPI", "s", {"category": "framework"})
    await ingest.ingest_text(tenant.id, "Garden Soil", "How to grow tomatoes in clay soil during monsoon", "s", {"category": "garden"})
    await ingest.ingest_text(tenant.id, "Django Book", "Django is a batteries included Python web framework", "s", {"category": "framework"})

    service = SearchService(db_session)
    kw = await service.search(tenant.id, "python backend framework", 5, retrieval_method="keyword", use_cache=False, persist=False, understand_query=False)
    dense = await service.search(tenant.id, "python backend framework", 5, retrieval_method="dense", use_cache=False, persist=False, understand_query=False)
    hybrid = await service.search(tenant.id, "python backend framework", 5, retrieval_method="hybrid", use_cache=False, persist=False, understand_query=False)
    rerank = await service.search(tenant.id, "python backend framework", 5, retrieval_method="hybrid_rerank", use_cache=False, persist=False, understand_query=False)

    assert kw["results"]
    assert dense["results"]
    assert hybrid["results"]
    assert rerank["results"]
    titles = " ".join(r["title"] for r in kw["results"][:3]).lower()
    assert "fastapi" in titles or "django" in titles
    assert rerank["results"][0]["explanation"].get("rerank") or rerank["results"][0]["rerank_score"] is not None


@pytest.mark.asyncio
async def test_price_filter(db_session):
    tenant, _, _ = await make_user(db_session, "t2", "b@x.com")
    ingest = IngestionService(db_session)
    await ingest.ingest_text(tenant.id, "Cheap Laptop", "budget laptop", "s", {"category": "laptop", "price": 40000, "ram_gb": 8})
    await ingest.ingest_text(tenant.id, "Pricey Laptop", "premium laptop", "s", {"category": "laptop", "price": 150000, "ram_gb": 32})
    service = SearchService(db_session)
    res = await service.search(
        tenant.id,
        "laptop",
        10,
        filters={"price_max": 80000},
        retrieval_method="keyword",
        use_cache=False,
        persist=False,
        understand_query=False,
    )
    ids = [r["title"] for r in res["results"]]
    assert "Cheap Laptop" in ids
    assert "Pricey Laptop" not in ids


@pytest.mark.asyncio
async def test_tenant_isolation(db_session):
    t1, _, _ = await make_user(db_session, "iso1", "one@x.com")
    t2, _, _ = await make_user(db_session, "iso2", "two@x.com")
    ingest = IngestionService(db_session)
    await ingest.ingest_text(t1.id, "Secret Alpha", "confidential alpha document about nuclear snacks", "s", {})
    await ingest.ingest_text(t2.id, "Public Beta", "public beta document about python", "s", {})
    service = SearchService(db_session)
    r1 = await service.search(t1.id, "document", 10, retrieval_method="keyword", use_cache=False, persist=False, understand_query=False)
    r2 = await service.search(t2.id, "document", 10, retrieval_method="keyword", use_cache=False, persist=False, understand_query=False)
    titles1 = {r["title"] for r in r1["results"]}
    titles2 = {r["title"] for r in r2["results"]}
    assert "Secret Alpha" in titles1
    assert "Public Beta" not in titles1
    assert "Secret Alpha" not in titles2


@pytest.mark.asyncio
async def test_recommend(db_session):
    tenant, _, _ = await make_user(db_session, "rec", "r@x.com")
    ingest = IngestionService(db_session)
    a = await ingest.ingest_text(tenant.id, "FastAPI", "python api framework", "s", {"category": "framework", "tags": ["python"]})
    await ingest.ingest_text(tenant.id, "Django", "python web framework", "s", {"category": "framework", "tags": ["python"]})
    await ingest.ingest_text(tenant.id, "Tomato", "vegetable garden", "s", {"category": "garden", "tags": ["food"]})
    from searchops.recommend.engine import RecommendationEngine

    recs = await RecommendationEngine(db_session).recommend(tenant.id, a.id, 5, "hybrid")
    assert recs["recommendations"]
    assert recs["recommendations"][0]["title"] == "Django"
