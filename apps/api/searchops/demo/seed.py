from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.auth import hash_password
from searchops.config import get_settings
from searchops.demo.catalog import EVAL_CASES, build_catalog
from searchops.ingestion.service import IngestionService
from searchops.models import Document, EvaluationCase, Tenant, User


async def ensure_demo_data(session: AsyncSession) -> None:
    settings = get_settings()
    if not settings.demo_seed:
        return
    tenant = (await session.execute(select(Tenant).where(Tenant.slug == "demo"))).scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(name="SearchOps Demo", slug="demo")
        session.add(tenant)
        await session.flush()
    user = (
        await session.execute(select(User).where(User.tenant_id == tenant.id, User.email == settings.demo_email))
    ).scalar_one_or_none()
    if user is None:
        session.add(
            User(
                tenant_id=tenant.id,
                email=settings.demo_email,
                password_hash=hash_password(settings.demo_password),
            )
        )
        await session.commit()

    count = (
        await session.execute(select(func.count(Document.id)).where(Document.tenant_id == tenant.id))
    ).scalar_one()
    if count:
        return

    service = IngestionService(session)
    for item in build_catalog():
        await service.ingest_text(
            tenant_id=tenant.id,
            title=item["title"],
            content=item["content"],
            source=item["source"],
            metadata=item["metadata"],
            document_id=item["id"],
        )
    for case in EVAL_CASES:
        session.add(
            EvaluationCase(
                id=case["id"],
                tenant_id=tenant.id,
                query=case["query"],
                relevant_documents=case["relevant_documents"],
                relevance_labels=case["relevance_labels"],
            )
        )
    await session.commit()
