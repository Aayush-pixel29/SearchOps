from __future__ import annotations

import re
from dataclasses import dataclass


class TextCleaner:
    def clean(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


@dataclass
class Chunk:
    content: str
    index: int
    metadata: dict


class Chunker:
    def __init__(self, size: int = 700, overlap: int = 120) -> None:
        self.size = size
        self.overlap = overlap

    def split(self, text: str, extra_metadata: dict | None = None) -> list[Chunk]:
        cleaned = text.strip()
        if not cleaned:
            return []
        if len(cleaned) <= self.size:
            return [Chunk(content=cleaned, index=0, metadata=extra_metadata or {})]
        chunks: list[Chunk] = []
        start = 0
        index = 0
        while start < len(cleaned):
            end = min(len(cleaned), start + self.size)
            piece = cleaned[start:end].strip()
            if piece:
                meta = dict(extra_metadata or {})
                meta["chunk_index"] = index
                chunks.append(Chunk(content=piece, index=index, metadata=meta))
                index += 1
            if end >= len(cleaned):
                break
            start = max(end - self.overlap, start + 1)
        return chunks
