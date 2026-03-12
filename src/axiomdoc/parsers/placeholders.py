from __future__ import annotations

from pathlib import Path

from axiomdoc.models import CanonicalDocument
from axiomdoc.parsers.base import ParserBackend


class PlaceholderParser(ParserBackend):
    def __init__(self, name: str, supported_suffixes: tuple[str, ...], install_hint: str) -> None:
        self.name = name
        self.supported_suffixes = supported_suffixes
        self.install_hint = install_hint

    def parse(self, path: Path) -> CanonicalDocument:
        raise RuntimeError(
            f"No production parser is configured for '{path.suffix}'. "
            f"Install or implement the backend noted in the roadmap: {self.install_hint}"
        )
