from __future__ import annotations

from pathlib import Path

from axiomdoc.models import Block, CanonicalDocument
from axiomdoc.parsers.base import ParserBackend


class PlainTextFallbackParser(ParserBackend):
    name = "plain-text-fallback"
    supported_suffixes = (".txt", ".md", ".csv", ".json")

    def parse(self, path: Path) -> CanonicalDocument:
        document = CanonicalDocument.empty(path, source_format=path.suffix.lower().lstrip("."), parser_name=self.name)

        raw = path.read_text(encoding="utf-8", errors="ignore")
        for index, line in enumerate(raw.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue

            kind = "heading" if self._looks_like_heading(stripped) else "paragraph"
            level = self._infer_level(stripped) if kind == "heading" else None
            document.blocks.append(
                Block(
                    block_id=f"b{index}",
                    kind=kind,
                    text=stripped,
                    level=level,
                    metadata={"source_line": index},
                )
            )
        return document

    @staticmethod
    def _looks_like_heading(text: str) -> bool:
        if len(text) > 120:
            return False
        if text.endswith(":"):
            return True
        words = text.split()
        return 0 < len(words) <= 12 and text == text.title()

    @staticmethod
    def _infer_level(text: str) -> int:
        if text.isupper():
            return 1
        if text.endswith(":"):
            return 2
        return 3
