from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class BoundingBox:
    page_number: int | None = None
    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None


@dataclass(slots=True)
class Provenance:
    source_path: str
    mime_type: str | None = None
    parser_name: str | None = None
    checksum: str | None = None


@dataclass(slots=True)
class Span:
    text: str
    role: str = "body"
    bbox: BoundingBox | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Block:
    block_id: str
    kind: str
    text: str
    level: int | None = None
    page_number: int | None = None
    bbox: BoundingBox | None = None
    spans: list[Span] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentSection:
    title: str
    level: int
    block_ids: list[str] = field(default_factory=list)
    children: list["DocumentSection"] = field(default_factory=list)


@dataclass(slots=True)
class CanonicalDocument:
    doc_id: str
    source_name: str
    source_format: str
    provenance: Provenance
    metadata: dict[str, Any] = field(default_factory=dict)
    blocks: list[Block] = field(default_factory=list)
    sections: list[DocumentSection] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(block.text for block in self.blocks if block.text.strip())

    @classmethod
    def empty(cls, path: str | Path, source_format: str, parser_name: str) -> "CanonicalDocument":
        source = Path(path)
        return cls(
            doc_id=source.stem,
            source_name=source.name,
            source_format=source_format,
            provenance=Provenance(
                source_path=str(source),
                parser_name=parser_name,
            ),
        )
