from __future__ import annotations

from axiomdoc.models import CanonicalDocument


def document_to_markdown(document: CanonicalDocument) -> str:
    lines: list[str] = []

    title = document.metadata.get("title")
    if isinstance(title, str) and title.strip():
        lines.append(f"# {title.strip()}")
        lines.append("")

    for block in document.blocks:
        text = block.text.strip()
        if not text:
            continue

        if block.kind == "heading":
            level = min(max(block.level or 1, 1), 6)
            lines.append(f"{'#' * level} {text}")
        elif block.kind == "list_item":
            lines.append(f"- {text}")
        elif block.kind == "table":
            lines.extend(_table_to_markdown(block.metadata.get("table_rows"), text))
        else:
            lines.append(text)

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _table_to_markdown(table_rows: object, fallback_text: str) -> list[str]:
    if not isinstance(table_rows, list) or not table_rows:
        return fallback_text.splitlines() or [fallback_text]

    normalized_rows = [
        [str(cell).strip() for cell in row]
        for row in table_rows
        if isinstance(row, list) and any(str(cell).strip() for cell in row)
    ]
    if not normalized_rows:
        return fallback_text.splitlines() or [fallback_text]

    width = max(len(row) for row in normalized_rows)
    padded = [row + [""] * (width - len(row)) for row in normalized_rows]
    header = padded[0]
    separator = ["---"] * width
    body = padded[1:]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return lines
