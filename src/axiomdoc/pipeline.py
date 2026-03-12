from __future__ import annotations

from pathlib import Path

from axiomdoc.exporters.markdown import document_to_markdown
from axiomdoc.exporters.xml import document_to_xml
from axiomdoc.indexing import build_index_manifest
from axiomdoc.models import CanonicalDocument
from axiomdoc.parsers.registry import ParserRegistry


def parse_document(path: str | Path, registry: ParserRegistry | None = None) -> CanonicalDocument:
    source = Path(path)
    parser_registry = registry or ParserRegistry()
    backend = parser_registry.resolve(source)
    return backend.parse(source)


def parse_to_artifacts(path: str | Path, registry: ParserRegistry | None = None) -> tuple[CanonicalDocument, str, str, dict]:
    document = parse_document(path=path, registry=registry)
    xml_output = document_to_xml(document)
    markdown_output = document_to_markdown(document)
    index_manifest = build_index_manifest(document)
    return document, xml_output, markdown_output, index_manifest
