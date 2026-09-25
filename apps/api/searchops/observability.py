from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Span:
    name: str
    started_at: float
    ended_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.ended_at if self.ended_at is not None else time.perf_counter()
        return (end - self.started_at) * 1000


class SearchTraceRecorder:
    def __init__(self, query: str) -> None:
        self.query = query
        self.spans: dict[str, Span] = {}
        self.token_usage = 0
        self.estimated_cost_usd = 0.0
        self.cache_hit = False
        self.errors: list[str] = []

    def start(self, name: str, **metadata: Any) -> None:
        self.spans[name] = Span(name=name, started_at=time.perf_counter(), metadata=metadata)

    def end(self, name: str, **metadata: Any) -> None:
        span = self.spans.get(name)
        if span is None:
            self.start(name)
            span = self.spans[name]
        span.ended_at = time.perf_counter()
        span.metadata.update(metadata)

    def add_tokens(self, tokens: int, cost_usd: float = 0.0) -> None:
        self.token_usage += tokens
        self.estimated_cost_usd += cost_usd

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "cache_hit": self.cache_hit,
            "token_usage": self.token_usage,
            "estimated_cost_usd": self.estimated_cost_usd,
            "errors": self.errors,
            "spans": {
                name: {
                    "duration_ms": round(span.duration_ms, 3),
                    "metadata": span.metadata,
                }
                for name, span in self.spans.items()
            },
            "total_ms": round(sum(s.duration_ms for s in self.spans.values() if s.ended_at), 3),
        }


class MetricsStore:
    """In-process latency histograms. Enough to explain p50/p95 without a metrics vendor."""

    def __init__(self) -> None:
        self.samples: dict[str, list[float]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)

    def observe(self, name: str, value_ms: float) -> None:
        self.samples[name].append(value_ms)
        if len(self.samples[name]) > 5000:
            self.samples[name] = self.samples[name][-2500:]

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] += amount

    def percentile(self, name: str, p: float) -> float | None:
        values = sorted(self.samples.get(name, []))
        if not values:
            return None
        idx = min(len(values) - 1, max(0, int(round((p / 100) * (len(values) - 1)))))
        return values[idx]

    def snapshot(self) -> dict[str, Any]:
        cache_hits = self.counters.get("cache_hit", 0)
        cache_miss = self.counters.get("cache_miss", 0)
        total = cache_hits + cache_miss
        return {
            "counters": dict(self.counters),
            "cache_hit_rate": (cache_hits / total) if total else None,
            "latencies_ms": {
                name: {
                    "count": len(vals),
                    "p50": self.percentile(name, 50),
                    "p95": self.percentile(name, 95),
                    "mean": sum(vals) / len(vals) if vals else None,
                }
                for name, vals in self.samples.items()
            },
        }


metrics = MetricsStore()


def cache_key(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return "searchops:" + hashlib.sha256(raw.encode()).hexdigest()
