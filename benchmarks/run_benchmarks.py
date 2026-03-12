from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import median
from typing import Callable
from xml.etree import ElementTree as ET

import fitz

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axiomdoc.pipeline import parse_to_artifacts


@dataclass
class DocumentResult:
    document: str
    pages: int
    runtime_seconds: float
    seconds_per_page: float
    xml_well_formed: bool
    markdown_chars: int
    heading_count: int
    chunk_count: int
    success: bool
    error: str | None = None


def run_axiomdoc(path: Path) -> tuple[str, str, dict]:
    _, xml_output, markdown_output, index_manifest = parse_to_artifacts(path)
    return xml_output, markdown_output, index_manifest


def run_pymupdf_raw(path: Path) -> tuple[str, str, dict]:
    with fitz.open(path) as pdf:
        pages: list[str] = []
        for page in pdf:
            pages.append(page.get_text("text"))
        markdown = "\n\n".join(text.strip() for text in pages if text.strip()) + "\n"
    xml_output = f"<document source_name=\"{path.name}\"><text>{_xml_escape(markdown)}</text></document>"
    return xml_output, markdown, {"chunks": []}


def run_docling(path: Path) -> tuple[str, str, dict]:
    converter_module = importlib.import_module("docling.document_converter")
    converter = converter_module.DocumentConverter()
    result = converter.convert(str(path))
    document = result.document
    markdown = document.export_to_markdown()
    xml_output = f"<document source_name=\"{path.name}\"><text>{_xml_escape(markdown)}</text></document>"
    return xml_output, markdown, {"chunks": []}


def run_pdfplumber(path: Path) -> tuple[str, str, dict]:
    pdfplumber = importlib.import_module("pdfplumber")
    with pdfplumber.open(str(path)) as pdf:
        texts = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                texts.append(text.strip())
    markdown = "\n\n".join(texts) + "\n"
    xml_output = f"<document source_name=\"{path.name}\"><text>{_xml_escape(markdown)}</text></document>"
    return xml_output, markdown, {"chunks": []}


def run_unstructured(path: Path) -> tuple[str, str, dict]:
    partition_pdf = importlib.import_module("unstructured.partition.pdf").partition_pdf
    elements = partition_pdf(filename=str(path))
    texts = [str(element).strip() for element in elements if str(element).strip()]
    markdown = "\n\n".join(texts) + "\n"
    xml_output = f"<document source_name=\"{path.name}\"><text>{_xml_escape(markdown)}</text></document>"
    return xml_output, markdown, {"chunks": []}


RUNNERS: dict[str, Callable[[Path], tuple[str, str, dict]]] = {
    "axiomdoc": run_axiomdoc,
    "pymupdf_raw": run_pymupdf_raw,
    "docling": run_docling,
    "pdfplumber": run_pdfplumber,
    "unstructured": run_unstructured,
}


def evaluate_runner(name: str, files: list[Path]) -> dict:
    runner = RUNNERS[name]
    results: list[DocumentResult] = []

    for path in files:
        with fitz.open(path) as pdf:
            pages = pdf.page_count

        started = time.perf_counter()
        try:
            xml_output, markdown_output, index_manifest = runner(path)
            runtime = time.perf_counter() - started
            results.append(
                DocumentResult(
                    document=path.name,
                    pages=pages,
                    runtime_seconds=runtime,
                    seconds_per_page=runtime / max(pages, 1),
                    xml_well_formed=_is_well_formed_xml(xml_output),
                    markdown_chars=len(markdown_output),
                    heading_count=_count_markdown_headings(markdown_output),
                    chunk_count=len(index_manifest.get("chunks", [])),
                    success=True,
                )
            )
        except Exception as exc:
            runtime = time.perf_counter() - started
            results.append(
                DocumentResult(
                    document=path.name,
                    pages=pages,
                    runtime_seconds=runtime,
                    seconds_per_page=runtime / max(pages, 1),
                    xml_well_formed=False,
                    markdown_chars=0,
                    heading_count=0,
                    chunk_count=0,
                    success=False,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    successful = [result for result in results if result.success]

    return {
        "library": name,
        "documents": [asdict(result) for result in results],
        "summary": {
            "success_rate": sum(1 for result in results if result.success) / len(results),
            "median_seconds_per_page": median(result.seconds_per_page for result in successful) if successful else None,
            "xml_well_formed_rate": (
                sum(1 for result in successful if result.xml_well_formed) / len(successful) if successful else 0.0
            ),
            "median_markdown_chars": median(result.markdown_chars for result in successful) if successful else None,
            "median_heading_count": median(result.heading_count for result in successful) if successful else None,
            "median_chunk_count": median(result.chunk_count for result in successful) if successful else None,
        },
    }


def _is_well_formed_xml(xml_output: str) -> bool:
    try:
        ET.fromstring(xml_output)
        return True
    except ET.ParseError:
        return False


def _count_markdown_headings(markdown_output: str) -> int:
    return sum(1 for line in markdown_output.splitlines() if line.lstrip().startswith("#"))


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run benchmark comparisons for AXIOMDoc against baseline libraries.")
    parser.add_argument("--dataset-dir", type=Path, required=True, help="Directory containing benchmark PDF files")
    parser.add_argument("--libraries", nargs="+", default=["axiomdoc", "pymupdf_raw", "pdfplumber", "docling"])
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results/latest.json"))
    args = parser.parse_args()

    files = sorted(args.dataset_dir.glob("*.pdf"))
    if not files:
        raise SystemExit(f"No PDF files found in {args.dataset_dir}")

    payload = {
        "dataset_dir": str(args.dataset_dir),
        "libraries": [],
    }
    for library in args.libraries:
        payload["libraries"].append(evaluate_runner(library, files))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
