from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from searchops.ingestion.loaders import LoadedDocument, loader_for
from searchops.ingestion.pipeline import Chunker, TextCleaner
from searchops.models import Chunk, Document
from searchops.providers.embeddings import EmbeddingProvider, get_embedding_provider


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        tenant_id: str,
        title: str,
        content: str,
        source: str,
        metadata: dict[str, Any],
        chunks: list[tuple[str, list[float] | None, dict[str, Any]]],
        document_id: str | None = None,
    ) -> Document:
        kwargs: dict[str, Any] = {
            "tenant_id": tenant_id,
            "title": title,
            "content": content,
            "source": source,
            "extra_metadata": metadata,
            "popularity": int(metadata.get("popularity") or 0),
        }
        if document_id:
            kwargs["id"] = document_id
        doc = Document(**kwargs)
        self.session.add(doc)
        await self.session.flush()
        for text, embedding, meta in chunks:
            self.session.add(
                Chunk(
                    tenant_id=tenant_id,
                    document_id=doc.id,
                    content=text,
                    embedding=embedding,
                    extra_metadata=meta,
                )
            )
        return doc

    async def list_documents(self, tenant_id: str) -> list[Document]:
        result = await self.session.execute(select(Document).where(Document.tenant_id == tenant_id))
        return list(result.scalars().all())

    async def get(self, tenant_id: str, document_id: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.tenant_id == tenant_id, Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, tenant_id: str, document_id: str) -> bool:
        doc = await self.get(tenant_id, document_id)
        if doc is None:
            return False
        await self.session.delete(doc)
        return True


class IngestionService:
    def __init__(
        self,
        session: AsyncSession,
        embedder: EmbeddingProvider | None = None,
        cleaner: TextCleaner | None = None,
        chunker: Chunker | None = None,
    ) -> None:
        self.repo = DocumentRepository(session)
        self.session = session
        self.embedder = embedder or get_embedding_provider()
        self.cleaner = cleaner or TextCleaner()
        self.chunker = chunker or Chunker()

    async def ingest_loaded(
        self,
        tenant_id: str,
        loaded: LoadedDocument,
        document_id: str | None = None,
    ) -> Document:
        content = self.cleaner.clean(loaded.content)
        if not content:
            raise ValueError("document content is empty after cleaning")
        pieces = self.chunker.split(content, extra_metadata=dict(loaded.metadata))
        embeddings = await self.embedder.embed([c.content for c in pieces])
        packed = [(c.content, embeddings[i], c.metadata) for i, c in enumerate(pieces)]
        doc = await self.repo.add(
            tenant_id=tenant_id,
            title=loaded.title,
            content=content,
            source=loaded.source,
            metadata=loaded.metadata,
            chunks=packed,
            document_id=document_id,
        )
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def ingest_text(
        self,
        tenant_id: str,
        title: str,
        content: str,
        source: str = "api",
        metadata: dict[str, Any] | None = None,
        document_id: str | None = None,
    ) -> Document:
        loaded = LoadedDocument(title=title, content=content, source=source, metadata=metadata or {})
        return await self.ingest_loaded(tenant_id, loaded, document_id=document_id)

    async def ingest_path(self, tenant_id: str, path: Path) -> list[Document]:
        docs = loader_for(path).load(path)
        stored: list[Document] = []
        for loaded in docs:
            stored.append(await self.ingest_loaded(tenant_id, loaded))
        return stored
