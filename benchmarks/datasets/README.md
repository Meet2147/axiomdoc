# Benchmark Datasets

This directory is for small public benchmark corpora used to compare AXIOMDoc with other document-intelligence libraries.

Current benchmark runner expects a folder of PDF files:

```bash
python benchmarks/run_benchmarks.py --dataset-dir benchmarks/datasets/pdfs
```

The benchmark reports:

- median seconds per page
- XML well-formed rate
- median markdown character count
- median detected heading count
- median chunk count

These are operational metrics, not full scientific quality metrics. If we later add labeled datasets for section reconstruction, tables, or key-value extraction, those should be reported separately.
