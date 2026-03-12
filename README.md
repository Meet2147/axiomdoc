# AXIOMDoc

![AXIOMDoc logo](assets/axiomdoc-logo.svg)

`AXIOM` stands for `Any-document eXtraction, Indexing, and Ontology Mapping`.

AXIOMDoc is an open-source Python library for document intelligence in RAG pipelines. It is being built to ingest heterogeneous documents, preserve structure, export canonical XML and Markdown, and generate retrieval-ready indexing artifacts with provenance.

## What AXIOMDoc is for

- Converting PDFs, XML, DOCX, DOC, XLSX, HTML, and related formats into one canonical document model.
- Preserving headings, reading order, page anchors, metadata, and layout evidence.
- Exporting clean XML and Markdown representations for downstream processing.
- Building chunk, section, and field-level artifacts for retrieval and context mapping.

## Core requirements

1. Any-document ingestion across common enterprise and knowledge-document formats.
2. Structure fidelity so headings are not missed and body text is not promoted into headings.
3. Canonical export into XML, Markdown, JSON, and retrieval artifacts from one internal schema.
4. RAG-first indexing with chunk provenance, section paths, and page references.
5. XML-safe serialization that strips characters invalid under XML 1.0.

## Architecture

AXIOMDoc follows a canonical-document-model approach:

- Parser backends normalize source files into one schema.
- Exporters transform that schema into XML, Markdown, and other artifacts.
- Index builders create retrieval-ready records with explicit provenance.
- Enrichment passes can later add headings, entities, forms, tables, and citation anchors.

This keeps parsing separate from retrieval and avoids binding the project to one vendor model or one OCR stack.

## Current package layout

```text
src/axiomdoc/
  cli.py
  pipeline.py
  models.py
  indexing.py
  exporters/
    xml.py
    markdown.py
  parsers/
    base.py
    registry.py
    pdf.py
    xml.py
docs/
  architecture.md
assets/
  axiomdoc-logo.svg
```

## Install

```bash
python3 -m pip install -e .
```

## Example

```bash
axiomdoc parse ./sample.pdf --xml-out ./sample.xml --markdown-out ./sample.md --index-out ./sample.index.json
```

## XML safety

XML does not allow certain control and surrogate characters. AXIOMDoc now sanitizes invalid XML 1.0 characters before serialization in [src/axiomdoc/exporters/xml.py](/Users/meetjethwa/Development/RagPrep/DocIntelligence/src/axiomdoc/exporters/xml.py), so malformed text content does not break XML generation.

## Status

The project is in the initial library phase. The baseline PDF and XML paths exist, and the roadmap for richer DOCX, XLSX, OCR, table extraction, and PageIndex-style indexing is documented in [docs/architecture.md](/Users/meetjethwa/Development/RagPrep/DocIntelligence/docs/architecture.md).
