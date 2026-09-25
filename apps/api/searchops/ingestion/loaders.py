from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LoadedDocument:
    title: str
    content: str
    source: str
    metadata: dict[str, Any]


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, path: Path) -> list[LoadedDocument]:
        raise NotImplementedError


class TxtLoader(DocumentLoader):
    def load(self, path: Path) -> list[LoadedDocument]:
        text = path.read_text(encoding="utf-8")
        return [LoadedDocument(title=path.stem, content=text, source=str(path), metadata={"format": "txt"})]


class MarkdownLoader(DocumentLoader):
    def load(self, path: Path) -> list[LoadedDocument]:
        text = path.read_text(encoding="utf-8")
        title = path.stem
        heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if heading:
            title = heading.group(1).strip()
        return [LoadedDocument(title=title, content=text, source=str(path), metadata={"format": "md"})]


class JsonLoader(DocumentLoader):
    def load(self, path: Path) -> list[LoadedDocument]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else [payload]
        docs: list[LoadedDocument] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("name") or path.stem)
            content = str(item.get("content") or item.get("description") or json.dumps(item))
            meta = {k: v for k, v in item.items() if k not in {"title", "name", "content", "description"}}
            meta["format"] = "json"
            docs.append(LoadedDocument(title=title, content=content, source=str(path), metadata=meta))
        return docs


class CsvLoader(DocumentLoader):
    def load(self, path: Path) -> list[LoadedDocument]:
        import csv

        docs: list[LoadedDocument] = []
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                title = row.get("title") or row.get("name") or path.stem
                content = row.get("content") or row.get("description") or " ".join(row.values())
                meta = {k: v for k, v in row.items() if k not in {"title", "name", "content", "description"}}
                meta["format"] = "csv"
                docs.append(LoadedDocument(title=str(title), content=str(content), source=str(path), metadata=meta))
        return docs


def loader_for(path: Path) -> DocumentLoader:
    suffix = path.suffix.lower()
    mapping = {".txt": TxtLoader, ".md": MarkdownLoader, ".markdown": MarkdownLoader, ".json": JsonLoader, ".csv": CsvLoader}
    cls = mapping.get(suffix)
    if cls is None:
        raise ValueError(f"unsupported document type: {suffix}")
    return cls()
