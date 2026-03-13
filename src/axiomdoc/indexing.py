from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from axiomdoc.models import CanonicalDocument


@dataclass(slots=True)
class IndexChunk:
    chunk_id: str
    text: str
    section_path: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def build_index_manifest(document: CanonicalDocument) -> dict[str, Any]:
    chunks: list[IndexChunk] = []
    current_path: list[str] = []
    chunk_counter = 1

    for block in document.blocks:
        if block.kind == "heading":
            level = max(1, block.level or 1)
            current_path = current_path[: level - 1]
            current_path.append(block.text)
            continue

        if not block.text.strip():
            continue

        if block.kind == "table" and isinstance(block.metadata.get("table_rows"), list):
            for row_index, row in enumerate(block.metadata["table_rows"], start=1):
                row_text = " | ".join(str(cell) for cell in row)
                chunks.append(
                    IndexChunk(
                        chunk_id=f"{document.doc_id}-c{chunk_counter}",
                        text=row_text,
                        section_path=current_path.copy(),
                        metadata={
                            "kind": block.kind,
                            "page_number": block.page_number,
                            "block_id": block.block_id,
                            "row_index": row_index,
                        },
                    )
                )
                chunk_counter += 1
            continue

        chunks.append(
            IndexChunk(
                chunk_id=f"{document.doc_id}-c{chunk_counter}",
                text=block.text,
                section_path=current_path.copy(),
                metadata={
                    "kind": block.kind,
                    "page_number": block.page_number,
                    "block_id": block.block_id,
                },
            )
        )
        chunk_counter += 1

    return {
        "doc_id": document.doc_id,
        "source_name": document.source_name,
        "source_format": document.source_format,
        "chunks": [asdict(chunk) for chunk in chunks],
    }
