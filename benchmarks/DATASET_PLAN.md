# 1000-Document Evaluation Plan

This benchmark expansion is the path from a small pilot comparison to a real multi-format evaluation set.

## Target size

- Total documents: 1000
- PDF: 500
- DOCX: 200
- XLSX: 100
- XML: 100
- HTML: 50
- TXT: 50

## Evaluation tracks

1. Operational benchmark
   - success rate
   - median time per page or per document unit
   - XML well-formed rate
   - markdown yield
   - chunk yield

2. Labeled benchmark
   - heading precision and recall
   - table precision and recall
   - field extraction precision and recall

## Manifest workflow

1. Download or curate documents under a dataset root.
2. Build a manifest:

```bash
python benchmarks/build_manifest.py --dataset-dir benchmarks/datasets --output benchmarks/manifests/generated.json
```

3. Run benchmark comparisons:

```bash
python benchmarks/run_benchmarks.py --manifest benchmarks/manifests/generated.json --libraries axiomdoc docling pdfplumber pymupdf_raw --output benchmarks/results/generated.json
```

## Dataset policy

- Do not claim 1000-document results in the README until the manifest actually contains 1000 documents and the run has been completed.
- Keep source provenance in the manifest so comparisons are auditable.
- Keep labeled subsets explicitly separate from unlabeled bulk documents.
