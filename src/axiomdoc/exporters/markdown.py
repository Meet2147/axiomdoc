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
        else:
            lines.append(text)

        lines.append("")

    return "\n".join(lines).strip() + "\n"
