from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]


def infer_doc_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in {"htm"}:
        return "html"
    if suffix in {"xlsm"}:
        return "xlsx"
    return suffix or "unknown"


def infer_pages(path: Path, doc_type: str) -> int | None:
    if doc_type == "pdf":
        try:
            with fitz.open(path) as pdf:
                return pdf.page_count
        except Exception:
            return None
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a benchmark manifest from a dataset directory.")
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".pdf", ".docx", ".xlsx", ".xml", ".html", ".txt"],
        help="File extensions to include",
    )
    args = parser.parse_args()

    extensions = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args.extensions}
    documents = []

    for path in sorted(args.dataset_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        resolved = path.resolve()
        doc_type = infer_doc_type(path)
        documents.append(
            {
                "document_id": resolved.stem,
                "path": str(resolved.relative_to(ROOT)),
                "doc_type": doc_type,
                "pages": infer_pages(resolved, doc_type),
                "labels": {},
                "source": "local-scan",
            }
        )

    payload = {"documents": documents}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.output)
    print(len(documents))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
