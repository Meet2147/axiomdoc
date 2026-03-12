from __future__ import annotations

import argparse
import json
from pathlib import Path

from axiomdoc.pipeline import parse_to_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axiomdoc", description="Canonical document parsing and RAG artifact generation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="Parse a document into XML and index artifacts.")
    parse_cmd.add_argument("source", help="Path to the source document")
    parse_cmd.add_argument("--xml-out", type=Path, help="Write canonical XML output to this path")
    parse_cmd.add_argument("--markdown-out", type=Path, help="Write Markdown output to this path")
    parse_cmd.add_argument("--index-out", type=Path, help="Write index manifest JSON to this path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "parse":
        _, xml_output, markdown_output, index_manifest = parse_to_artifacts(args.source)
        if args.xml_out:
            args.xml_out.write_text(xml_output, encoding="utf-8")
        else:
            print(xml_output)

        if args.markdown_out:
            args.markdown_out.write_text(markdown_output, encoding="utf-8")

        if args.index_out:
            args.index_out.write_text(json.dumps(index_manifest, indent=2), encoding="utf-8")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
