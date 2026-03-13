from __future__ import annotations

from axiomdoc.exporters.markdown import document_to_markdown
from axiomdoc.exporters.xml import document_to_xml
from axiomdoc.models import Block, CanonicalDocument, Provenance


def make_document() -> CanonicalDocument:
    document = CanonicalDocument(
        doc_id="demo\x01",
        source_name="sample.pdf",
        source_format="pdf",
        provenance=Provenance(source_path="sample.pdf", parser_name="test"),
        metadata={"title": "Quarterly\x0bReport"},
        blocks=[
            Block(block_id="b1", kind="heading", text="Overview", level=2),
            Block(block_id="b2", kind="paragraph", text="Revenue increased."),
            Block(block_id="b3", kind="list_item", text="North America"),
        ],
    )
    return document


def test_document_to_xml_sanitizes_invalid_characters() -> None:
    xml_output = document_to_xml(make_document())

    assert "\x01" not in xml_output
    assert "\x0b" not in xml_output
    assert 'id="demo"' in xml_output
    assert "<text>Revenue increased.</text>" in xml_output


def test_document_to_markdown_preserves_heading_and_list_blocks() -> None:
    markdown_output = document_to_markdown(make_document())

    assert markdown_output.startswith("# Quarterly")
    assert "## Overview" in markdown_output
    assert "Revenue increased." in markdown_output
    assert "- North America" in markdown_output
