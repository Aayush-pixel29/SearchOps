from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.auth import create_access_token, hash_password, verify_password
from searchops.db import get_session
from searchops.deps import get_current_user
from searchops.models import Document, Tenant, User
from searchops.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(Tenant).where(Tenant.slug == body.tenant_slug))
    tenant = existing.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(name=body.tenant_name, slug=body.tenant_slug)
        session.add(tenant)
        await session.flush()
    user = User(tenant_id=tenant.id, email=body.email.lower(), password_hash=hash_password(body.password))
    session.add(user)
    await session.commit()
    token = create_access_token(user.id, tenant.id)
    return TokenResponse(access_token=token, tenant_id=tenant.id, email=user.email)


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    tenant = (
        await session.execute(select(Tenant).where(Tenant.slug == body.tenant_slug))
    ).scalar_one_or_none()
    if tenant is None and body.tenant_slug == "demo":
        from searchops.demo.seed import ensure_demo_data
        await ensure_demo_data(session)
        tenant = (
            await session.execute(select(Tenant).where(Tenant.slug == body.tenant_slug))
        ).scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=401, detail="unknown tenant")
    user = (
        await session.execute(
            select(User).where(User.tenant_id == tenant.id, User.email == body.email.lower())
        )
    ).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(user.id, tenant.id)
    return TokenResponse(access_token=token, tenant_id=tenant.id, email=user.email)


@router.get("/admin/tenant")
async def tenant_admin(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    doc_count = (
        await session.execute(select(func.count(Document.id)).where(Document.tenant_id == user.tenant_id))
    ).scalar_one()
    return {
        "tenant_id": user.tenant_id,
        "email": user.email,
        "document_count": doc_count,
    }
