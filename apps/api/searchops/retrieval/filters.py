from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from searchops.models import Chunk, Document


def tenant_chunk_query(tenant_id: str) -> Select:
    return (
        select(Chunk)
        .options(selectinload(Chunk.document))
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.tenant_id == tenant_id, Document.tenant_id == tenant_id)
    )


def filtered_chunk_query(tenant_id: str, filters: dict[str, Any] | None) -> Select:
    """Tenant isolation is always enforced in SQL. Metadata predicates are applied after fetch
    with typed comparisons so SQLite and Postgres behave the same way."""
    return tenant_chunk_query(tenant_id)


def chunk_matches_filters(chunk: Chunk, filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    doc = chunk.document
    meta = dict(doc.extra_metadata or {}) if doc else dict(chunk.extra_metadata or {})
    source = doc.source if doc else meta.get("source")
    created_at = doc.created_at if doc else None
    if category := filters.get("category"):
        if str(meta.get("category", "")).lower() != str(category).lower():
            return False
    if source_f := filters.get("source"):
        if str(source) != str(source_f):
            return False
    if language := filters.get("language"):
        if str(meta.get("language", "")).lower() != str(language).lower():
            return False
    if tags := filters.get("tags"):
        tag_list = tags if isinstance(tags, list) else [tags]
        hay = {str(t).lower() for t in (meta.get("tags") or [])} if isinstance(meta.get("tags"), list) else {
            str(meta.get("tags", "")).lower()
        }
        if not any(str(t).lower() in hay for t in tag_list):
            return False
    if (price_max := filters.get("price_max")) is not None:
        price = _as_float(meta.get("price"))
        if price is None or price > float(price_max):
            return False
    if (price_min := filters.get("price_min")) is not None:
        price = _as_float(meta.get("price"))
        if price is None or price < float(price_min):
            return False
    if (ram_gb := filters.get("ram_gb")) is not None:
        ram = _as_float(meta.get("ram_gb"))
        if ram is None or ram < float(ram_gb):
            return False
    if date_from := filters.get("date_from"):
        parsed = _parse_date(date_from)
        if parsed and created_at and created_at < parsed:
            return False
    if date_to := filters.get("date_to"):
        parsed = _parse_date(date_to)
        if parsed and created_at and created_at > parsed:
            return False
    return True


def _as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
