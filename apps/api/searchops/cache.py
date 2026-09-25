from __future__ import annotations

import json
from typing import Any

from searchops.config import get_settings
from searchops.observability import metrics

_memory: dict[str, str] = {}
_redis = None
_redis_failed = False


async def get_redis():
    global _redis, _redis_failed
    if _redis_failed:
        return None
    if _redis is not None:
        return _redis
    try:
        from redis.asyncio import Redis

        settings = get_settings()
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        _redis = client
        return _redis
    except Exception:
        _redis_failed = True
        metrics.increment("redis_failure")
        return None


async def cache_get(key: str) -> dict[str, Any] | None:
    client = await get_redis()
    raw = None
    if client is not None:
        try:
            raw = await client.get(key)
        except Exception:
            metrics.increment("redis_failure")
            raw = _memory.get(key)
    else:
        raw = _memory.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_set(key: str, value: dict[str, Any], ttl: int | None = None) -> None:
    settings = get_settings()
    payload = json.dumps(value)
    client = await get_redis()
    if client is not None:
        try:
            await client.set(key, payload, ex=ttl or settings.cache_ttl_seconds)
            return
        except Exception:
            metrics.increment("redis_failure")
    _memory[key] = payload


def reset_cache_state() -> None:
    global _redis, _redis_failed
    _memory.clear()
    _redis = None
    _redis_failed = False
