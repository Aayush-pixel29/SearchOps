from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from searchops.config import get_settings
from searchops.providers.embeddings import estimate_tokens


class ExtractedQuery(BaseModel):
    semantic_query: str
    keywords: list[str] = Field(default_factory=list)
    intent: str = "search"
    filters: dict[str, Any] = Field(default_factory=dict)


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def complete_json(self, prompt: str) -> dict[str, Any]:
        raise NotImplementedError


class HeuristicLLMProvider(LLMProvider):
    """Structured extraction without an external model. Used as the default local path."""

    name = "heuristic"

    async def complete_json(self, prompt: str) -> dict[str, Any]:
        from searchops.query.understanding import heuristic_extract

        query = prompt.rsplit("Query:", 1)[-1].strip()
        extracted = heuristic_extract(query)
        return extracted.model_dump()


class OpenAILLMProvider(LLMProvider):
    name = "openai"

    async def complete_json(self, prompt: str) -> dict[str, Any]:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_chat_model,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)


def get_llm_provider(name: str | None = None) -> LLMProvider:
    settings = get_settings()
    choice = (name or settings.llm_provider).lower()
    if choice in {"none", "heuristic", ""}:
        return HeuristicLLMProvider()
    if choice == "openai":
        return OpenAILLMProvider()
    return HeuristicLLMProvider()


async def extract_query_structured(query: str, provider: LLMProvider | None = None) -> ExtractedQuery:
    provider = provider or get_llm_provider()
    prompt = (
        "Extract search intent as JSON with keys semantic_query, keywords, intent, filters. "
        "filters may include category, source, language, tags, price_max, price_min, ram_gb, date_from, date_to.\n"
        f"Query: {query}"
    )
    try:
        raw = await provider.complete_json(prompt)
        parsed = ExtractedQuery.model_validate(raw)
        if not parsed.semantic_query:
            parsed.semantic_query = query
        return parsed
    except (ValidationError, json.JSONDecodeError, KeyError, TypeError, RuntimeError, ValueError):
        return ExtractedQuery(semantic_query=query, keywords=query.split())


def prompt_token_estimate(query: str) -> int:
    return estimate_tokens(query)
