from __future__ import annotations

import re

from searchops.providers.llm import ExtractedQuery

PRICE_RE = re.compile(r"(?:under|below|less than|<|<=)\s*(?:₹|rs\.?|inr)?\s*([0-9][0-9,]*)", re.I)
RAM_RE = re.compile(r"(\d+)\s*gb\s*ram", re.I)
CATEGORY_HINTS = {
    "laptop": ["laptop", "notebook", "macbook"],
    "framework": ["framework", "django", "fastapi", "flask", "express"],
    "database": ["postgres", "postgresql", "mysql", "redis", "sqlite", "database"],
    "search": ["search", "bm25", "retrieval", "rerank", "vector"],
}


def heuristic_extract(query: str) -> ExtractedQuery:
    filters: dict = {}
    q = query.lower()
    if match := PRICE_RE.search(query.replace(",", "")):
        filters["price_max"] = float(match.group(1))
    if match := RAM_RE.search(q):
        filters["ram_gb"] = float(match.group(1))
    for category, hints in CATEGORY_HINTS.items():
        if any(h in q for h in hints):
            filters["category"] = category
            break
    semantic = re.sub(PRICE_RE, "", query)
    semantic = re.sub(r"under\s*₹?\s*[0-9,]+", "", semantic, flags=re.I)
    semantic = re.sub(r"\s+", " ", semantic).strip() or query
    keywords = re.findall(r"[a-zA-Z0-9]+", semantic)
    return ExtractedQuery(
        semantic_query=semantic,
        keywords=keywords,
        intent="product_search" if "price_max" in filters or "category" in filters else "search",
        filters=filters,
    )
