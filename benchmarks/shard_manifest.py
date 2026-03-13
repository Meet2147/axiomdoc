from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Split a benchmark manifest into page-balanced shards.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--shards", type=int, default=4)
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    documents = sorted(data["documents"], key=lambda item: item.get("pages") or 1, reverse=True)

    buckets = [{"documents": [], "pages": 0} for _ in range(args.shards)]
    for document in documents:
        bucket = min(buckets, key=lambda item: item["pages"])
        bucket["documents"].append(document)
        bucket["pages"] += document.get("pages") or 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index, bucket in enumerate(buckets, start=1):
        path = args.output_dir / f"shard-{index:02d}.json"
        path.write_text(json.dumps({"documents": bucket["documents"]}, indent=2), encoding="utf-8")
        print(path, len(bucket["documents"]), bucket["pages"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
