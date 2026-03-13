# AXIOMDoc

![AXIOMDoc logo](https://raw.githubusercontent.com/Meet2147/axiomdoc/main/assets/axiomdoc-logo.svg)

`AXIOM` stands for `Any-document eXtraction, Indexing, and Ontology Mapping`.

AXIOMDoc is an open-source Python library for document intelligence in RAG pipelines. It is being built to ingest heterogeneous documents, preserve structure, export canonical XML and Markdown, and generate retrieval-ready indexing artifacts with provenance.

## What AXIOMDoc is for

- Converting PDFs, XML, DOCX, DOC, XLSX, HTML, and related formats into one canonical document model.
- Preserving headings, reading order, page anchors, metadata, and layout evidence.
- Falling back to OCR for image-only PDFs when text extraction is unavailable.
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

## Install

```bash
python3 -m pip install -e .
```

Full parser and test dependencies:

```bash
python3 -m pip install -e ".[full,dev]"
```

## Example

```bash
axiomdoc parse ./sample.pdf --xml-out ./sample.xml --markdown-out ./sample.md --index-out ./sample.index.json
```

## Evaluation

![AXIOMDoc evaluation plan](https://raw.githubusercontent.com/Meet2147/axiomdoc/main/assets/evaluation-grid.svg)

We are moving the evaluation stack to a manifest-driven, multi-format benchmark so we can compare AXIOMDoc on at least 1000 documents across PDF, DOCX, XLSX, XML, HTML, and text. The core pieces for that pipeline now live in:

- [benchmarks/run_benchmarks.py](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/run_benchmarks.py)
- [benchmarks/build_manifest.py](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/build_manifest.py)
- [benchmarks/DATASET_PLAN.md](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/DATASET_PLAN.md)
- [benchmarks/manifests/target-1000-plan.json](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/manifests/target-1000-plan.json)

Target evaluation size:

- 1000 total documents
- 500 PDF
- 200 DOCX
- 100 XLSX
- 100 XML
- 50 HTML
- 50 TXT

Target comparison set:

- AXIOMDoc
- Docling
- PyMuPDF raw extraction baseline
- pdfplumber
- raw text baseline for simple structured files

We now have a completed large-corpus PDF benchmark on `1076` real PDFs for `AXIOMDoc`, `PyMuPDF raw`, and `pdfplumber`. `docling` remains in-progress on this corpus because its runtime on the same dataset is hours-scale.

### 1076-PDF corpus benchmark

This is still an operational benchmark, not a full scientific benchmark with human labels, so the metrics are limited to things we can measure honestly and reproduce today.

Local PDF corpus used in this run:

- `1076` PDFs from the local document store
- `13,594` total pages
- median PDF length: `2` pages
- max PDF length: `1178` pages

Measured results from the current run:

| Library | Success Rate | Median Sec/Page | XML Well-Formed Rate | Median Heading Count | Median Markdown Chars | Median Chunk Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AXIOMDoc | 0.9991 | 0.01514 | 1.0000 | 5 | 5009 | 17 |
| PyMuPDF raw | 0.9991 | 0.00275 | 0.9600 | 0 | 4369 | 0 |
| pdfplumber | 0.9926 | 0.07410 | 0.9972 | 0 | 4316.5 | 0 |
| Docling | pending | pending | pending | pending | pending | pending |

Interpretation:

- AXIOMDoc is slower than raw PyMuPDF, which is expected because it performs structure recovery and builds XML, Markdown, and chunk manifests.
- AXIOMDoc is faster than pdfplumber on this corpus while also emitting RAG-ready chunks.
- AXIOMDoc is the only completed large-corpus run here currently producing a non-zero chunk manifest.
- PyMuPDF raw had the fastest median page time, but a lower XML well-formed rate because the wrapper path surfaced malformed outputs on some documents.
- pdfplumber had the lowest success rate among the completed large-corpus runs.

Benchmark files:

- [benchmarks/results/pdf-only-1076-axiomdoc.json](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/results/pdf-only-1076-axiomdoc.json)
- [benchmarks/results/pdf-only-1076-pymupdf.json](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/results/pdf-only-1076-pymupdf.json)
- [benchmarks/results/pdf-only-1076-pdfplumber.json](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/results/pdf-only-1076-pdfplumber.json)
- [benchmarks/manifests/pdf-only-1076.json](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/manifests/pdf-only-1076.json)

Large-corpus benchmark commands:

```bash
.venv/bin/python benchmarks/run_benchmarks.py --manifest benchmarks/manifests/pdf-only-1076.json --libraries axiomdoc --output benchmarks/results/pdf-only-1076-axiomdoc.json
.venv/bin/python benchmarks/run_benchmarks.py --manifest benchmarks/manifests/pdf-only-1076.json --libraries pymupdf_raw --output benchmarks/results/pdf-only-1076-pymupdf.json
.venv/bin/python benchmarks/run_benchmarks.py --manifest benchmarks/manifests/pdf-only-1076.json --libraries pdfplumber --output benchmarks/results/pdf-only-1076-pdfplumber.json
```

Limits of this benchmark:

- This run is PDF-only. The 1000-document multi-format plan exists, but only the PDF track is complete so far.
- Heading recovery here is markdown heading count, not labeled precision/recall.
- Markdown character count is a yield proxy, not a semantic quality score.
- The docling large-corpus baseline is still pending because of runtime cost on this machine.

Labeled fixture evaluation is now available in [benchmarks/labeled_eval.py](https://github.com/Meet2147/axiomdoc/blob/main/benchmarks/labeled_eval.py) and exercised in [tests/test_hardening.py](https://github.com/Meet2147/axiomdoc/blob/main/tests/test_hardening.py). That scorer currently measures expected heading recovery and table recovery against explicit JSON labels.

## XML safety

XML does not allow certain control and surrogate characters. AXIOMDoc now sanitizes invalid XML 1.0 characters before serialization in [src/axiomdoc/exporters/xml.py](https://github.com/Meet2147/axiomdoc/blob/main/src/axiomdoc/exporters/xml.py), so malformed text content does not break XML generation.

## Release readiness

The repo now includes:

- production PDF, DOCX, XML, and XLSX parsers
- OCR fallback for image-only PDFs through the local `tesseract` binary
- structured table preservation in XML, Markdown, and chunk manifests
- pytest coverage for exporters, parser resolution, and PDF smoke behavior
- labeled evaluation fixtures for heading and table recovery
- a GitHub Actions test workflow at [.github/workflows/tests.yml](https://github.com/Meet2147/axiomdoc/blob/main/.github/workflows/tests.yml)
- an MIT [LICENSE](https://github.com/Meet2147/axiomdoc/blob/main/LICENSE)

## Status

The project is in late release-prep. PDF, DOCX, XLSX, and XML baseline parsing are implemented, OCR fallback exists for image-only PDFs, and labeled evaluation now covers heading/table recovery on fixtures. The remaining gaps before a strict `1.0.0` are broader labeled datasets, richer scanned-document accuracy validation, and more advanced form/table semantics. The roadmap remains in [docs/architecture.md](https://github.com/Meet2147/axiomdoc/blob/main/docs/architecture.md).
