from __future__ import annotations

import re
from xml.etree.ElementTree import Element, SubElement, tostring

from axiomdoc.models import Block, CanonicalDocument

_INVALID_XML_CHARS = re.compile(
    "["  # XML 1.0 valid chars are tab, LF, CR, and selected Unicode ranges.
    "\x00-\x08"
    "\x0B-\x0C"
    "\x0E-\x1F"
    "\uD800-\uDFFF"
    "\uFFFE-\uFFFF"
    "]"
)


def document_to_xml(document: CanonicalDocument) -> str:
    root = Element(
        "document",
        attrib={
            "id": _sanitize_xml_text(document.doc_id),
            "source_name": _sanitize_xml_text(document.source_name),
            "source_format": _sanitize_xml_text(document.source_format),
            "parser": _sanitize_xml_text(document.provenance.parser_name or "unknown"),
        },
    )

    metadata_el = SubElement(root, "metadata")
    for key, value in sorted(document.metadata.items()):
        item = SubElement(metadata_el, "field", attrib={"name": _sanitize_xml_text(key)})
        item.text = _sanitize_xml_text(str(value))

    blocks_el = SubElement(root, "blocks")
    for block in document.blocks:
        _append_block(blocks_el, block)

    return tostring(root, encoding="unicode")


def _append_block(parent: Element, block: Block) -> None:
    attrs = {
        "id": _sanitize_xml_text(block.block_id),
        "kind": _sanitize_xml_text(block.kind),
    }
    if block.level is not None:
        attrs["level"] = str(block.level)
    if block.page_number is not None:
        attrs["page"] = str(block.page_number)

    block_el = SubElement(parent, "block", attrib=attrs)
    text_el = SubElement(block_el, "text")
    text_el.text = _sanitize_xml_text(block.text)

    table_rows = block.metadata.get("table_rows")
    if block.kind == "table" and isinstance(table_rows, list):
        table_el = SubElement(block_el, "table")
        for row in table_rows:
            if not isinstance(row, list):
                continue
            row_el = SubElement(table_el, "row")
            for cell in row:
                cell_el = SubElement(row_el, "cell")
                cell_el.text = _sanitize_xml_text(str(cell))

    if block.metadata:
        meta_el = SubElement(block_el, "metadata")
        for key, value in sorted(block.metadata.items()):
            if key == "table_rows":
                continue
            item = SubElement(meta_el, "field", attrib={"name": _sanitize_xml_text(str(key))})
            item.text = _sanitize_xml_text(str(value))


def _sanitize_xml_text(value: str) -> str:
    return _INVALID_XML_CHARS.sub("", value)
