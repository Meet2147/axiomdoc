from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from axiomdoc.models import CanonicalDocument


class ParserBackend(ABC):
    name = "base"
    supported_suffixes: tuple[str, ...] = ()

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_suffixes

    @abstractmethod
    def parse(self, path: Path) -> CanonicalDocument:
        raise NotImplementedError
