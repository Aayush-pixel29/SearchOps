from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

import numpy as np

from searchops.config import get_settings


class EmbeddingProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @property
    def dim(self) -> int:
        return get_settings().embedding_dim


class HashedEmbeddingProvider(EmbeddingProvider):
    """Deterministic hashed n-gram embeddings. No API key, reproducible for evals."""

    name = "hashed"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        dim = self.dim
        out: list[list[float]] = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            tokens = _tokenize(text)
            grams = tokens + [" ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]
            for gram in grams:
                digest = hashlib.sha256(gram.encode("utf-8")).digest()
                idx = int.from_bytes(digest[:4], "little") % dim
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm:
                vec = vec / norm
            out.append(vec.tolist())
        return out


class OpenAIEmbeddingProvider(EmbeddingProvider):
    name = "openai"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_embedding_model, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            return [row["embedding"] for row in sorted(data, key=lambda r: r["index"])]


class GeminiEmbeddingProvider(EmbeddingProvider):
    name = "gemini"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        import httpx

        vectors: list[list[float]] = []
        async with httpx.AsyncClient(timeout=30) as client:
            for text in texts:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{settings.gemini_embedding_model}:embedContent?key={settings.gemini_api_key}"
                )
                resp = await client.post(url, json={"content": {"parts": [{"text": text}]}})
                resp.raise_for_status()
                vectors.append(resp.json()["embedding"]["values"])
        return vectors


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    name = "huggingface"
    _model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("sentence-transformers not installed") from exc
        if self._model is None:
            HuggingFaceEmbeddingProvider._model = SentenceTransformer(settings.hf_embedding_model)
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]


class MockEmbeddingProvider(HashedEmbeddingProvider):
    name = "mock"


def get_embedding_provider(name: str | None = None) -> EmbeddingProvider:
    settings = get_settings()
    choice = (name or settings.embedding_provider).lower()
    mapping = {
        "hashed": HashedEmbeddingProvider,
        "mock": MockEmbeddingProvider,
        "openai": OpenAIEmbeddingProvider,
        "gemini": GeminiEmbeddingProvider,
        "huggingface": HuggingFaceEmbeddingProvider,
        "hf": HuggingFaceEmbeddingProvider,
    }
    cls = mapping.get(choice)
    if cls is None:
        raise ValueError(f"unknown embedding provider: {choice}")
    return cls()


def cosine(a: list[float], b: list[float]) -> float:
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def l2_normalize(vec: list[float]) -> list[float]:
    arr = np.asarray(vec, dtype=np.float32)
    n = float(np.linalg.norm(arr))
    if n == 0:
        return vec
    return (arr / n).tolist()


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))
