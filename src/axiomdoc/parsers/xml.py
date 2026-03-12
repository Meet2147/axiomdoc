from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from axiomdoc.models import Block, CanonicalDocument
from axiomdoc.parsers.base import ParserBackend


class XmlParser(ParserBackend):
    name = "xml"
    supported_suffixes = (".xml", ".html", ".htm")

    def parse(self, path: Path) -> CanonicalDocument:
        tree = ET.parse(path)
        root = tree.getroot()

        document = CanonicalDocument.empty(path, source_format=path.suffix.lower().lstrip("."), parser_name=self.name)
        document.metadata["root_tag"] = root.tag

        for index, element in enumerate(root.iter(), start=1):
            text = self._extract_text(element)
            if not text:
                continue

            kind = "heading" if self._looks_like_heading(element.tag, text) else "paragraph"
            level = 1 if kind == "heading" else None
            document.blocks.append(
                Block(
                    block_id=f"x{index}",
                    kind=kind,
                    text=text,
                    level=level,
                    metadata={
                        "tag": element.tag,
                        "attributes": dict(element.attrib),
                    },
                )
            )

        return document

    @staticmethod
    def _looks_like_heading(tag: str, text: str) -> bool:
        tag_lower = tag.lower()
        if tag_lower in {"title", "h1", "h2", "h3", "h4", "h5", "h6", "heading", "head"}:
            return True
        return len(text.split()) <= 12 and text == text.title()

    @staticmethod
    def _extract_text(element: ET.Element) -> str:
        if list(element):
            return ""
        return " ".join(part.strip() for part in element.itertext() if part.strip())
