from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from axiomdoc.pipeline import parse_document


@dataclass
class EvaluationSummary:
    heading_precision: float
    heading_recall: float
    table_precision: float
    table_recall: float


def evaluate_fixture(document_path: Path, label_path: Path) -> dict[str, Any]:
    document = parse_document(document_path)
    labels = json.loads(label_path.read_text(encoding="utf-8"))

    expected_headings = {(item["text"], item.get("level")) for item in labels.get("headings", [])}
    actual_headings = {
        (block.text, block.level)
        for block in document.blocks
        if block.kind == "heading"
    }

    expected_tables = {
        tuple(tuple(str(cell) for cell in row) for row in table["rows"])
        for table in labels.get("tables", [])
    }
    actual_tables = {
        tuple(tuple(str(cell) for cell in row) for row in block.metadata.get("table_rows", []))
        for block in document.blocks
        if block.kind == "table" and isinstance(block.metadata.get("table_rows"), list)
    }

    summary = EvaluationSummary(
        heading_precision=_precision(actual_headings, expected_headings),
        heading_recall=_recall(actual_headings, expected_headings),
        table_precision=_precision(actual_tables, expected_tables),
        table_recall=_recall(actual_tables, expected_tables),
    )

    return {
        "document": str(document_path),
        "labels": str(label_path),
        "summary": asdict(summary),
        "actual_headings": sorted({"text": text, "level": level} for text, level in actual_headings),
        "actual_table_count": len(actual_tables),
    }


def _precision(actual: set[Any], expected: set[Any]) -> float:
    if not actual:
        return 1.0 if not expected else 0.0
    return len(actual & expected) / len(actual)


def _recall(actual: set[Any], expected: set[Any]) -> float:
    if not expected:
        return 1.0
    return len(actual & expected) / len(expected)
