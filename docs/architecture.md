# AXIOMDoc Architecture

## Name

Primary recommendation: `AXIOM`

- Expansion: `Any-document eXtraction, Indexing, and Ontology Mapping`
- Why it works: short, memorable, sounds infrastructure-grade, and covers parsing plus retrieval.

Alternatives:

- `ATLAS`: `Adaptive Transformation, Layout Analysis, and Search`
- `CORTEX`: `Contextual OCR, Retrieval, Transformation, and Extraction`
- `ORBIT`: `Omni-format Retrieval and Binary Intelligence Toolkit`

## Product goal

Build an open-source Python library that:

1. Accepts arbitrary document formats.
2. Preserves structural fidelity during normalization.
3. Produces a canonical XML representation.
4. Produces a high-fidelity Markdown representation for LLM and RAG workflows.
5. Extracts fields, tables, entities, and layout-aware chunks for RAG indexing.
6. Ships as a PyPI package with optional heavyweight dependencies.

## Non-negotiable design decisions

### 1. Canonical document model first

Every source format should map into one internal schema containing:

- Document metadata
- Layout blocks
- Heading hierarchy
- Tables
- Key-value fields
- Inline spans
- Bounding boxes and page anchors
- Provenance for every extracted element

Without this, each file type grows its own ad hoc extraction logic and the library becomes impossible to maintain.

### 2. Parser backend abstraction

Use format-specific adapters under a common interface:

- PDF: text layer, metadata, outlines, page geometry, OCR fallback
- DOCX/DOC: styles, numbered headings, tables, comments, tracked structure where possible
- XLSX: workbook, sheet names, merged cells, table regions, formulas, data validation
- XML/HTML: native tree preservation, namespaces, attribute retention
- Images/scans: OCR plus layout detection

### 3. Hybrid heading detection

Heading detection must not rely on font size alone. It should combine:

- Native structural signals
- Typography and spacing features
- Outline/bookmark metadata
- Relative page position
- Lexical cues
- Sequence-model or classifier support for ambiguous cases

This is the only way to avoid promoting body text into headings while also preserving unstyled headings in real-world PDFs.

### 4. Retrieval artifacts are first-class outputs

RAG quality depends on preserving provenance and hierarchy. For every chunk or field, keep:

- Section path
- Page number
- Block ids
- Table anchors
- Source offsets where available
- Confidence scores

## Research direction used here

The architecture is informed by recent work and strong open-source systems:

- Docling formalizes a multi-format document conversion pipeline and reinforces the value of a common document model across PDF, DOCX, HTML, and spreadsheets.
- Marker shows that practical PDF extraction quality comes from combining text, layout, tables, and OCR-aware fallbacks rather than raw text scraping.
- ColPali and the ViDoRe line of work show that retrieval over document representations benefits from preserving visual and structural cues, not only plain text chunks.
- RAPTOR argues for hierarchical retrieval over long documents, which directly supports section-aware chunking and XML-derived index trees.
- Recent VLM-based parsing work such as MinerU 2.5 and PaddleOCR-VL points toward using multi-stage model pipelines only for the hard cases, not as the entire parser stack.

## Recommended architecture

```text
ingest
  -> parser backend
  -> canonical document model
  -> enrichment passes
  -> exporters (xml/json/markdown)
  -> index builders
  -> retriever adapters
```

### Ingest layer

Responsibilities:

- MIME and extension detection
- Password/encryption checks
- Source hashing
- Basic document metadata capture

### Parser layer

Recommended order of implementation:

1. Native XML/HTML parser
2. DOCX parser
3. XLSX parser
4. PDF parser with text-layer support
5. OCR-enhanced PDF/image parser
6. Legacy DOC via external conversion bridge

### Enrichment layer

Passes to implement after baseline parsing:

- Heading classifier
- Table normalization
- Key-value extraction
- Entity extraction
- Citation and reference linking
- Chunk synthesis for RAG

### Export layer

Canonical XML should preserve:

- Stable ids
- Structural nesting
- Layout metadata
- Native metadata when present
- Confidence and provenance tags

Markdown export should preserve:

- Heading levels
- Table structure where possible
- Lists and callouts
- Clean reading order for RAG chunking and LLM ingestion
- Stable anchors via sidecar metadata or block ids

PDF-to-XML should use both explicit PDF metadata and inferred structure. The exporter must not trust one source blindly because bookmarks are often incomplete and layout-only heuristics are often wrong.

PDF-to-Markdown should be derived from the same canonical document model as XML and the index artifacts. That keeps heading levels, reading order, and table boundaries consistent across all outputs.

## RAG-specific indexing strategy

Generate three complementary indexes:

1. Section index
2. Chunk index
3. Field/table index

### Section index

One node per heading or semantic section. Used for hierarchical retrieval and context expansion.

### Chunk index

Paragraph-sized chunks with section path, page anchors, and neighboring context references.

### Field/table index

For forms, invoices, policies, and spreadsheets, retrieval must address exact fields and rows rather than only prose chunks.

## Recommended implementation roadmap

### Phase 1

- Publish `axiomdoc` package skeleton
- Define canonical schema
- Implement XML exporter
- Implement Markdown exporter
- Implement basic chunk manifest
- Add CLI

### Phase 2

- Add DOCX parser using paragraph styles and table extraction
- Add XLSX parser with sheet-level and cell-range semantics
- Add native XML parser with namespace preservation

### Phase 3

- Add PDF parser based on PyMuPDF for text spans, outlines, metadata, and page geometry
- Add optional OCR backend for scanned PDFs
- Add heading classifier using supervised features plus VLM fallback

### Phase 4

- Add layout-aware chunking
- Add table and form extraction
- Add PageIndex-compatible exporter
- Add vector store adapters and reranking hooks

### Phase 5

- Benchmark against public datasets
- Publish reproducible evaluation harness
- Push package to PyPI

## Packaging recommendations

- Use optional extras per file family and model backend.
- Keep the core install small.
- Expose both Python API and CLI.
- Publish JSON schema for the canonical document model.
- Version the XML format separately from the Python package if downstream indexing systems depend on it.

## Immediate next files to implement

- `src/axiomdoc/parsers/pdf.py`
- `src/axiomdoc/parsers/docx.py`
- `src/axiomdoc/parsers/xlsx.py`
- `src/axiomdoc/parsers/xml.py`
- `tests/`

## Source links

- [Docling](https://docling-project.github.io/docling/)
- [Unstructured partitioning docs](https://docs.unstructured.io/open-source/core-functionality/partitioning)
- [Marker](https://github.com/VikParuchuri/marker)
- [RAPTOR paper](https://arxiv.org/abs/2401.18059)
- [ColPali paper](https://arxiv.org/abs/2407.01449)
- [MinerU 2.5 paper](https://arxiv.org/abs/2509.22186)
- [PaddleOCR-VL paper](https://arxiv.org/abs/2510.14528)
