from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import fitz

from axiomdoc.models import Block, BoundingBox, CanonicalDocument
from axiomdoc.parsers.base import ParserBackend


class PdfParser(ParserBackend):
    name = "pymupdf"
    supported_suffixes = (".pdf",)

    def parse(self, path: Path) -> CanonicalDocument:
        document = CanonicalDocument.empty(path, source_format="pdf", parser_name=self.name)

        with fitz.open(path) as pdf:
            self._load_metadata(pdf, document)
            outline_levels = self._build_outline_map(pdf)
            base_font_size = self._infer_base_font_size(pdf)
            block_counter = 1

            for page_index, page in enumerate(pdf, start=1):
                page_dict = page.get_text("dict")
                for block in page_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue

                    text, font_size, flags = self._extract_block_text(block)
                    if not text:
                        continue

                    heading_level = self._detect_heading_level(text, font_size, flags, base_font_size, outline_levels)
                    kind = "heading" if heading_level is not None else "paragraph"
                    bbox = self._bbox_for_block(block, page_index)

                    document.blocks.append(
                        Block(
                            block_id=f"p{page_index}-b{block_counter}",
                            kind=kind,
                            text=text,
                            level=heading_level,
                            page_number=page_index,
                            bbox=bbox,
                            metadata={
                                "font_size": font_size,
                                "font_flags": flags,
                            },
                        )
                    )
                    block_counter += 1

        return document

    @staticmethod
    def _load_metadata(pdf: fitz.Document, document: CanonicalDocument) -> None:
        metadata = {key: value for key, value in (pdf.metadata or {}).items() if value}
        document.metadata.update(metadata)
        document.metadata["page_count"] = pdf.page_count
        if metadata.get("title"):
            document.metadata["title"] = metadata["title"]

    @staticmethod
    def _build_outline_map(pdf: fitz.Document) -> dict[str, int]:
        outline_map: dict[str, int] = {}
        for level, title, page_number, *_ in pdf.get_toc(simple=False):
            if not title:
                continue
            normalized = PdfParser._normalize_text(title)
            if normalized:
                outline_map[normalized] = level
        return outline_map

    @staticmethod
    def _infer_base_font_size(pdf: fitz.Document) -> float:
        sizes: Counter[float] = Counter()
        for page in pdf:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue
                        size = round(float(span.get("size", 0.0)), 1)
                        sizes[size] += len(text)
        if not sizes:
            return 12.0
        return sizes.most_common(1)[0][0]

    @staticmethod
    def _extract_block_text(block: dict) -> tuple[str, float, int]:
        lines: list[str] = []
        font_sizes: list[float] = []
        flags = 0

        for line in block.get("lines", []):
            line_parts: list[str] = []
            for span in line.get("spans", []):
                span_text = span.get("text", "").strip()
                if not span_text:
                    continue
                line_parts.append(span_text)
                font_sizes.append(float(span.get("size", 0.0)))
                flags |= int(span.get("flags", 0))
            if line_parts:
                lines.append(" ".join(line_parts))

        text = "\n".join(line.strip() for line in lines if line.strip()).strip()
        if not text:
            return "", 0.0, flags

        avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0.0
        return text, avg_size, flags

    @staticmethod
    def _detect_heading_level(
        text: str,
        font_size: float,
        flags: int,
        base_font_size: float,
        outline_levels: dict[str, int],
    ) -> int | None:
        normalized = PdfParser._normalize_text(text)
        if normalized in outline_levels:
            return min(outline_levels[normalized], 6)

        line_count = len(text.splitlines())
        word_count = len(text.split())
        if line_count > 3 or word_count == 0 or word_count > 18:
            return None

        bold = bool(flags & 16)
        is_numbered = bool(re.match(r"^\d+(\.\d+)*\s+\S+", text))
        title_like = text == text.title() or text.isupper() or text.endswith(":")
        larger_than_body = font_size >= base_font_size * 1.18 if base_font_size else False

        if not (larger_than_body or bold or is_numbered):
            return None
        if not title_like and not is_numbered and word_count > 10:
            return None

        if font_size >= base_font_size * 1.8:
            return 1
        if font_size >= base_font_size * 1.45:
            return 2
        if is_numbered:
            return min(text.count(".") + 1, 6)
        if bold or font_size >= base_font_size * 1.18:
            return 3
        return None

    @staticmethod
    def _bbox_for_block(block: dict, page_number: int) -> BoundingBox | None:
        coords = block.get("bbox")
        if not coords or len(coords) != 4:
            return None
        x0, y0, x1, y1 = coords
        return BoundingBox(page_number=page_number, x0=x0, y0=y0, x1=x1, y1=y1)

    @staticmethod
    def _normalize_text(text: str) -> str:
        collapsed = " ".join(text.split()).strip().casefold()
        return re.sub(r"\s+", " ", collapsed)
