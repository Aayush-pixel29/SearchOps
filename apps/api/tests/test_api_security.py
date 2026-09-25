import pytest



@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_unauthorized(client):
    resp = await client.get("/documents")
    assert resp.status_code == 401
    resp = await client.get("/search", params={"q": "x"}, headers={"Authorization": "Bearer not-a-token"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_search_flow(client):
    reg = await client.post(
        "/auth/register",
        json={"email": "dev@searchops.dev", "password": "secret12", "tenant_name": "Acme", "tenant_slug": "acme"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post(
        "/documents",
        json={"title": "Redis Cache", "content": "Redis caches search results by query hash", "metadata": {"category": "database"}},
        headers=headers,
    )
    assert created.status_code == 200
    search = await client.get("/search", params={"q": "redis cache", "retrieval_method": "hybrid", "top_k": 5}, headers=headers)
    assert search.status_code == 200
    body = search.json()
    assert body["query"] == "redis cache"
    assert body["results"]
    assert "score" in body["results"][0]
    assert "rank" in body["results"][0]


@pytest.mark.asyncio
async def test_injection_filters_do_not_500(client):
    reg = await client.post(
        "/auth/register",
        json={"email": "inj@searchops.dev", "password": "secret12", "tenant_name": "Inj", "tenant_slug": "inj"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/documents",
        json={"title": "Doc", "content": "hello world python", "metadata": {"category": "knowledge"}},
        headers=headers,
    )
    payload = {
        "q": "python'; DROP TABLE documents;--",
        "filters": {"category": "knowledge OR 1=1", "price_max": "not-a-number"},
        "retrieval_method": "keyword",
        "top_k": 5,
    }
    # price_max invalid type should 422 from pydantic if sent as search POST with wrong type;
    # string in filters dict is allowed and ignored by float parser.
    payload["filters"]["price_max"] = "1; select 1"
    resp = await client.post("/search", json=payload, headers=headers)
    assert resp.status_code == 200
    listed = await client.get("/documents", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
