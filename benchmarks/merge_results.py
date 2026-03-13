from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_benchmarks import summarize_by_doc_type, summarize_results, DocumentResult


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge shard benchmark results into a single result payload.")
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    merged_documents = []
    library_name = None
    manifest_name = []

    for path in args.inputs:
        payload = json.loads(path.read_text(encoding="utf-8"))
        library_name = library_name or payload["libraries"][0]["library"]
        manifest_name.append(payload["manifest"])
        merged_documents.extend(payload["libraries"][0]["documents"])

    results = [DocumentResult(**item) for item in merged_documents]
    payload = {
        "manifest": manifest_name,
        "document_count": len(merged_documents),
        "libraries": [
            {
                "library": library_name,
                "documents": merged_documents,
                "summary": summarize_results(results),
                "by_doc_type": summarize_by_doc_type(results),
            }
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
