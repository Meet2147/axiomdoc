from __future__ import annotations

import json
from pathlib import Path

from benchmarks.build_manifest import infer_doc_type
from benchmarks.run_benchmarks import count_doc_types, load_manifest, summarize_results, DatasetEntry, DocumentResult


def test_infer_doc_type_normalizes_known_suffixes() -> None:
    assert infer_doc_type(Path("sample.htm")) == "html"
    assert infer_doc_type(Path("sheet.xlsm")) == "xlsx"
    assert infer_doc_type(Path("report.pdf")) == "pdf"


def test_load_manifest_and_count_doc_types() -> None:
    entries = load_manifest(Path("benchmarks/manifests/pilot-mixed.json"))

    assert len(entries) == 3
    assert count_doc_types(entries) == {"pdf": 3}
    assert isinstance(entries[0], DatasetEntry)


def test_summarize_results_handles_success_rates() -> None:
    results = [
        DocumentResult(
            document_id="a",
            document="a.pdf",
            doc_type="pdf",
            pages=1,
            runtime_seconds=0.1,
            seconds_per_page=0.1,
            xml_well_formed=True,
            markdown_chars=100,
            heading_count=2,
            chunk_count=5,
            success=True,
        ),
        DocumentResult(
            document_id="b",
            document="b.pdf",
            doc_type="pdf",
            pages=1,
            runtime_seconds=0.2,
            seconds_per_page=0.2,
            xml_well_formed=False,
            markdown_chars=0,
            heading_count=0,
            chunk_count=0,
            success=False,
            error="boom",
        ),
    ]

    summary = summarize_results(results)

    assert summary["document_count"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["median_seconds_per_page"] == 0.1
