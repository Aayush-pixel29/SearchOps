from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_slug: str = "demo"


class RegisterRequest(BaseModel):
    email: str
    password: str
    tenant_name: str
    tenant_slug: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    email: str


class DocumentCreate(BaseModel):
    title: str
    content: str
    source: str = "api"
    metadata: dict[str, Any] = Field(default_factory=dict)
    id: str | None = None


class DocumentBulkCreate(BaseModel):
    documents: list[DocumentCreate]


class SearchRequest(BaseModel):
    q: str
    top_k: int = Field(default=10, ge=1, le=50)
    filters: dict[str, Any] = Field(default_factory=dict)
    retrieval_method: str = "hybrid"
    alpha: float | None = Field(default=None, ge=0, le=1)
    understand_query: bool = True


class RecommendRequest(BaseModel):
    item_id: str
    top_k: int = 5
    mode: str = "hybrid"


class EvalRunRequest(BaseModel):
    methods: list[str] | None = None
    top_k: int = 10
