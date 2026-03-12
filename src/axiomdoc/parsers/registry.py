from __future__ import annotations

from pathlib import Path

from axiomdoc.parsers.base import ParserBackend
from axiomdoc.parsers.placeholders import PlaceholderParser
from axiomdoc.parsers.pdf import PdfParser
from axiomdoc.parsers.stub import PlainTextFallbackParser
from axiomdoc.parsers.xml import XmlParser


class ParserRegistry:
    def __init__(self, backends: list[ParserBackend] | None = None) -> None:
        self.backends = backends or [
            PdfParser(),
            XmlParser(),
            PlainTextFallbackParser(),
            PlaceholderParser("docx-placeholder", (".docx", ".doc"), "install the future 'docx' extra powered by python-docx and conversion bridges"),
            PlaceholderParser("xlsx-placeholder", (".xlsx", ".xls"), "install the future 'xlsx' extra powered by openpyxl"),
        ]

    def resolve(self, path: Path) -> ParserBackend:
        for backend in self.backends:
            if backend.can_parse(path):
                return backend
        raise RuntimeError(f"No parser backend registered for suffix '{path.suffix.lower() or '<none>'}'.")
