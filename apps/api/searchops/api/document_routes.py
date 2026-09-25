from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.db import get_session
from searchops.deps import get_current_user
from searchops.ingestion.service import IngestionService
from searchops.models import User
from searchops.schemas import DocumentBulkCreate, DocumentCreate

router = APIRouter(tags=["documents"])


@router.post("/documents")
async def create_document(
    body: DocumentCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = IngestionService(session)
    try:
        doc = await service.ingest_text(
            tenant_id=user.tenant_id,
            title=body.title,
            content=body.content,
            source=body.source,
            metadata=body.metadata,
            document_id=body.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ingestion failed: {exc}") from exc
    return {"id": doc.id, "title": doc.title, "source": doc.source, "metadata": doc.extra_metadata}


@router.post("/documents/bulk")
async def bulk_documents(
    body: DocumentBulkCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = IngestionService(session)
    created = []
    for item in body.documents:
        doc = await service.ingest_text(
            tenant_id=user.tenant_id,
            title=item.title,
            content=item.content,
            source=item.source,
            metadata=item.metadata,
            document_id=item.id,
        )
        created.append(doc.id)
    return {"created": created}


@router.get("/documents")
async def list_documents(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    docs = await IngestionService(session).repo.list_documents(user.tenant_id)
    return [
        {
            "id": d.id,
            "title": d.title,
            "source": d.source,
            "metadata": d.extra_metadata,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    doc = await IngestionService(session).repo.get(user.tenant_id, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="not found")
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "source": doc.source,
        "metadata": doc.extra_metadata,
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    ok = await IngestionService(session).repo.delete(user.tenant_id, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    await session.commit()
    return {"deleted": document_id}
