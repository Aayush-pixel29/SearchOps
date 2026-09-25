from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from searchops.config import get_settings
from searchops.models import Base

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_engine(url: str | None = None):
    global engine, SessionLocal
    settings = get_settings()
    database_url = url or settings.database_url
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Clean query parameters for asyncpg if needed
    if "postgresql+asyncpg://" in database_url and "channel_binding=" in database_url:
        import urllib.parse
        parsed = urllib.parse.urlparse(database_url)
        q = urllib.parse.parse_qs(parsed.query)
        # asyncpg accepts ssl in connect_args or ssl parameter
        q.pop("channel_binding", None)
        new_query = urllib.parse.urlencode(q, doseq=True)
        database_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

    engine = create_async_engine(database_url, echo=False, connect_args=connect_args)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return engine


async def create_tables() -> None:
    if engine is None:
        init_engine()
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    if SessionLocal is None:
        init_engine()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session
