from __future__ import annotations

import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_searchops.db")
os.environ["DEMO_SEED"] = "false"
os.environ["EMBEDDING_PROVIDER"] = "hashed"
os.environ["RERANKER"] = "heuristic"
os.environ["LLM_PROVIDER"] = "none"
os.environ["SEARCHOPS_SECRET_KEY"] = "test-secret"

from searchops.config import get_settings
from searchops import db as database
from searchops.main import create_app
from searchops.models import Tenant, User
from searchops.auth import hash_password, create_access_token


@pytest_asyncio.fixture
async def db_session(tmp_path: Path) -> AsyncIterator[AsyncSession]:
    get_settings.cache_clear()
    url = f"sqlite+aiosqlite:///{tmp_path.as_posix()}/searchops.db"
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    database.init_engine(url)
    await database.create_tables()
    assert database.SessionLocal is not None
    async with database.SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    get_settings.cache_clear()
    url = f"sqlite+aiosqlite:///{tmp_path.as_posix()}/api.db"
    os.environ["DATABASE_URL"] = url
    os.environ["DEMO_SEED"] = "false"
    get_settings.cache_clear()
    database.init_engine(url)
    await database.create_tables()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def make_user(session: AsyncSession, slug: str, email: str) -> tuple[Tenant, User, str]:
    tenant = Tenant(name=slug, slug=slug)
    session.add(tenant)
    await session.flush()
    user = User(tenant_id=tenant.id, email=email, password_hash=hash_password("pw"))
    session.add(user)
    await session.commit()
    token = create_access_token(user.id, tenant.id)
    return tenant, user, token
