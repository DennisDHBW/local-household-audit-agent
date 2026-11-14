"""PDF parser: tables first, then headings and paragraphs, then images.

Pipeline per page (concept.md, section 5.1):

1. Detect tables (``find_tables``) and cut their area out of the running text.
2. Group the remaining spans into text blocks; blocks that are entirely bold and larger than
   the body font are headings and maintain the ``heading_stack``.
3. Bring tables, text blocks and images into reading order.
4. Merge very short fragments, cap long paragraphs, serialise table rows as ``Column: value``.

The parser only reads a PDF; it never calls an LLM (captions and summaries follow in M3).
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from audit_agent.config import ParserSettings
from audit_agent.corpus import DocumentMeta
from audit_agent.ingestion.models import Chunk, ChunkMetadata, ChunkType, ParsedDocument

BBox = tuple[float, float, float, float]

_BOLD_FLAG = 16
_TABLE_STRATEGIES = ("lines", "lines_strict")
_TABLE_OVERLAP_SHARE = 0.3
_BAND_TOLERANCE_PT = 1.0
_HEADING_SIZE_TOLERANCE_PT = 0.4
_MAX_HEADING_CHARS = 150
_MIN_HEADING_CHARS = 8
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class ParseError(Exception):
    """A PDF cannot be parsed into chunks."""


@dataclass(frozen=True)
class _Span:
    bbox: BBox
    text: str
    size: float
    is_bold: bool

    @property
    def center(self) -> tuple[float, float]:
        return (self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2


@dataclass(frozen=True)
class _TextBlock:
    bbox: BBox
    lines: tuple[tuple[_Span, ...], ...]
    has_left_peer: bool = False
    """Other text sits left of this block on the same row (label/value pair, not a heading)."""

    @property
    def text(self) -> str:
        return _normalise(" ".join(span.text for line in self.lines for span in line))

    @property
    def max_size(self) -> float:
        return max(span.size for line in self.lines for span in line)

    @property
    def is_all_bold(self) -> bool:
        return all(span.is_bold for line in self.lines for span in line)


@dataclass(frozen=True)
class _TableRegion:
    bbox: BBox
    row_bboxes: tuple[BBox, ...]


@dataclass(frozen=True)
class _ImageRegion:
    bbox: BBox
    xref: int


@dataclass(frozen=True)
class _Element:
    """Anything with a place on the page; ``payload`` is a block, table or image."""

    bbox: BBox
    payload: _TextBlock | _TableRegion | _ImageRegion


@dataclass
class _PageContent:
    number: int
    elements: list[_Element]
    spans: list[_Span]


@dataclass
class _Cursor:
    """Running state while chunks are emitted in reading order."""

    stem: str
    meta: ChunkMetadata
    levels: dict[float, int]
    body_size: float
    stack: list[tuple[int, str]] = field(default_factory=list)
    counters: Counter[str] = field(default_factory=Counter)
    chunks: list[Chunk] = field(default_factory=list)
    pending_text: str = ""
    pending_page: int = 0
    pending_stack: tuple[str, ...] = ()

    @property
    def heading_stack(self) -> tuple[str, ...]:
        return tuple(text for _, text in self.stack)


def _has_digit(text: str) -> bool:
    return any(char.isdigit() for char in text)


def _join_cells(texts: list[str]) -> str:
    """Headerless row: ``Label: value`` for two cells, otherwise cells joined by `` | ``.

    A cell that already ends with a colon is a label and is glued to the next cell.
    """
    if len(texts) == 2 and not texts[0].endswith(":"):
        return f"{texts[0]}: {texts[1]}"
    result = ""
    for text in texts:
        if not result:
            result = text
        elif result.endswith(":"):
            result = f"{result} {text}"
        else:
            result = f"{result} | {text}"
    return result


def _normalise(text: str) -> str:
    return " ".join(text.split())


def _union(a: BBox, b: BBox) -> BBox:
    return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


def _area(box: BBox) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def _intersection_area(a: BBox, b: BBox) -> float:
    return _area((max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))


def _contains_center(box: BBox, span: _Span, margin: float = 1.0) -> bool:
    cx, cy = span.center
    return box[0] - margin <= cx <= box[2] + margin and box[1] - margin <= cy <= box[3] + margin


class DocumentParser:
    """Turns one PDF into typed chunks (see ``ParsedDocument``)."""

    def __init__(self, settings: ParserSettings, images_dir: Path) -> None:
        self._cfg = settings
        self._images_dir = images_dir

    def parse(self, pdf_path: Path, meta: DocumentMeta) -> ParsedDocument:
        if not pdf_path.is_file():
            raise ParseError(f"PDF not found: {pdf_path}")
        try:
            document = pymupdf.open(pdf_path)
        except Exception as error:  # pymupdf raises plain RuntimeError/FileDataError
            raise ParseError(f"{pdf_path.name}: cannot open PDF: {error}") from error
        with document:
            pages = [self._read_page(page) for page in document]
            body_size = self._body_size(pages)
            levels = self._heading_levels(pages, body_size)
            cursor = _Cursor(
                stem=pdf_path.stem,
                meta=ChunkMetadata.from_document(meta),
                levels=levels,
                body_size=body_size,
            )
            for content in pages:
                self._emit_page(document, content, cursor)
                self._flush_text(cursor)
        if not cursor.chunks:
            raise ParseError(f"{pdf_path.name}: no content found")
        return ParsedDocument(file=meta.file, page_count=len(pages), chunks=tuple(cursor.chunks))

    # ---- phase 1: read geometry -------------------------------------------------------

    def _read_page(self, page: pymupdf.Page) -> _PageContent:
        spans, blocks = self._read_spans(page)
        tables = self._split_at_section_rows(self._detect_tables(page), spans)
        header_limit = page.rect.height * self._cfg.header_zone_ratio
        footer_limit = page.rect.height * (1 - self._cfg.footer_zone_ratio)

        elements: list[_Element] = [_Element(t.bbox, t) for t in tables]
        for block in blocks:
            lines = tuple(
                line
                for line in block
                if not any(_contains_center(t.bbox, span) for t in tables for span in line)
            )
            if not lines:
                continue
            bbox = lines[0][0].bbox
            for span in (s for line in lines for s in line):
                bbox = _union(bbox, span.bbox)
            if bbox[1] < header_limit or bbox[3] > footer_limit:
                continue
            has_peer = any(
                other.bbox[2] <= bbox[0] + 2
                and bbox[1] <= other.center[1] <= bbox[3]
                and not _contains_center(bbox, other)
                for other in spans
            )
            elements.append(_Element(bbox, _TextBlock(bbox, lines, has_left_peer=has_peer)))
        elements.extend(self._image_elements(page))
        ordered = self._reading_order(elements, page.rect.width)
        return _PageContent(number=page.number + 1, elements=ordered, spans=spans)

    @staticmethod
    def _read_spans(page: pymupdf.Page) -> tuple[list[_Span], list[list[tuple[_Span, ...]]]]:
        all_spans: list[_Span] = []
        blocks: list[list[tuple[_Span, ...]]] = []
        for raw_block in page.get_text("dict")["blocks"]:
            if raw_block["type"] != 0:
                continue
            lines: list[tuple[_Span, ...]] = []
            for raw_line in raw_block["lines"]:
                line = tuple(
                    _Span(
                        bbox=tuple(raw["bbox"]),
                        text=raw["text"],
                        size=raw["size"],
                        is_bold=bool(raw["flags"] & _BOLD_FLAG),
                    )
                    for raw in raw_line["spans"]
                    if raw["text"].strip()
                )
                if line:
                    lines.append(line)
                    all_spans.extend(line)
            if lines:
                blocks.append(lines)
        return all_spans, blocks

    @staticmethod
    def _detect_tables(page: pymupdf.Page) -> list[_TableRegion]:
        """Run both line strategies; on overlap the table with more rows (then larger area) wins.

        ``lines`` loses header rows whose cells have a fill but no border, ``lines_strict``
        loses rows in other layouts, so neither is sufficient alone (ADR-0007).
        """
        candidates: list[_TableRegion] = []
        for strategy in _TABLE_STRATEGIES:
            for table in page.find_tables(strategy=strategy).tables:
                rows = tuple(tuple(row.bbox) for row in table.rows)
                candidates.append(_TableRegion(tuple(table.bbox), rows))
        candidates.sort(key=lambda t: (len(t.row_bboxes), _area(t.bbox)), reverse=True)
        kept: list[_TableRegion] = []
        for candidate in candidates:
            overlaps = any(
                _intersection_area(candidate.bbox, other.bbox)
                > _TABLE_OVERLAP_SHARE * min(_area(candidate.bbox), _area(other.bbox))
                for other in kept
            )
            if not overlaps:
                kept.append(candidate)
        return kept

    def _split_at_section_rows(
        self, tables: list[_TableRegion], spans: Sequence[_Span]
    ) -> list[_TableRegion]:
        """Cut a table where a section title row sits inside it.

        ``find_tables`` joins touching tables; the title between them ("2. Entgeltberechnung")
        then becomes a table row. Such a row (one bold cell, larger than the table text) is
        left to the heading logic and the rows above and below become separate tables.
        """
        result: list[_TableRegion] = []
        for table in tables:
            inside = [s for s in spans if _contains_center(table.bbox, s)]
            if not inside:
                result.append(table)
                continue
            table_size = Counter(round(s.size, 1) for s in inside).most_common(1)[0][0]
            segments: list[list[BBox]] = [[]]
            for row_box in table.row_bboxes:
                cells = self._row_cells(row_box, table.bbox, spans)
                row_spans = [s for s in spans if row_box[1] <= s.center[1] <= row_box[3]]
                is_section = (
                    len(cells) == 1
                    and bool(row_spans)
                    and all(s.is_bold for s in row_spans)
                    and max(s.size for s in row_spans) >= table_size * self._cfg.heading_size_factor
                    and len(cells[0][2]) >= _MIN_HEADING_CHARS
                )
                if is_section:
                    segments.append([])
                else:
                    segments[-1].append(row_box)
            if len(segments) == 1:
                result.append(table)
                continue
            for rows in segments:
                if rows:
                    box = rows[0]
                    for row_box in rows[1:]:
                        box = _union(box, row_box)
                    result.append(
                        _TableRegion((table.bbox[0], box[1], table.bbox[2], box[3]), tuple(rows))
                    )
        return result

    def _image_elements(self, page: pymupdf.Page) -> list[_Element]:
        found: list[_Element] = []
        for info in page.get_image_info(xrefs=True):
            bbox = tuple(info["bbox"])
            if info["xref"] and bbox[2] - bbox[0] >= self._cfg.min_image_width_pt:
                found.append(_Element(bbox, _ImageRegion(bbox, info["xref"])))
        return found

    @staticmethod
    def _reading_order(elements: Sequence[_Element], page_width: float) -> list[_Element]:
        """Top to bottom; elements that share vertical space are read column by column."""
        remaining = sorted(elements, key=lambda e: (e.bbox[1], e.bbox[0]))
        ordered: list[_Element] = []
        while remaining:
            band = [remaining.pop(0)]
            band_end = band[0].bbox[3]
            index = 0
            while index < len(remaining):
                if remaining[index].bbox[1] < band_end - _BAND_TOLERANCE_PT:
                    element = remaining.pop(index)
                    band.append(element)
                    band_end = max(band_end, element.bbox[3])
                else:
                    index += 1
            band.sort(key=lambda e: ((e.bbox[0] + e.bbox[2]) / 2 >= page_width / 2, e.bbox[1]))
            ordered.extend(band)
        return ordered

    # ---- phase 2: fonts and heading levels ----------------------------------------------

    @staticmethod
    def _body_size(pages: Sequence[_PageContent]) -> float:
        weights: Counter[float] = Counter()
        for page in pages:
            for element in page.elements:
                if isinstance(element.payload, _TextBlock):
                    for line in element.payload.lines:
                        for span in line:
                            weights[round(span.size, 1)] += len(span.text)
        if not weights:
            raise ParseError("document has no running text")
        return weights.most_common(1)[0][0]

    def _is_heading(self, block: _TextBlock, body_size: float) -> bool:
        return (
            block.is_all_bold
            and not block.has_left_peer
            and block.max_size >= body_size * self._cfg.heading_size_factor
            and _MIN_HEADING_CHARS <= len(block.text) <= _MAX_HEADING_CHARS
        )

    def _heading_levels(self, pages: Sequence[_PageContent], body_size: float) -> dict[float, int]:
        """Larger heading font = higher level (0 = top); similar sizes share a level."""
        sizes = sorted(
            {
                round(e.payload.max_size, 1)
                for page in pages
                for e in page.elements
                if isinstance(e.payload, _TextBlock) and self._is_heading(e.payload, body_size)
            },
            reverse=True,
        )
        levels: dict[float, int] = {}
        level = -1
        previous: float | None = None
        for size in sizes:
            if previous is None or previous - size > _HEADING_SIZE_TOLERANCE_PT:
                level += 1
            levels[size] = level
            previous = size
        return levels

    # ---- phase 3: emit chunks -----------------------------------------------------------

    def _emit_page(self, document: pymupdf.Document, content: _PageContent, cur: _Cursor) -> None:
        for element in content.elements:
            payload = element.payload
            if isinstance(payload, _TextBlock):
                if self._is_heading(payload, cur.body_size):
                    self._emit_heading(payload, content.number, cur)
                else:
                    self._add_text(payload.text, content.number, cur)
            elif isinstance(payload, _TableRegion):
                self._flush_text(cur)
                self._emit_table(payload, content, cur)
            else:
                self._flush_text(cur)
                self._emit_image(document, payload, content.number, cur)

    def _next_id(self, cur: _Cursor, page: int, kind: str) -> str:
        key = f"p{page}_{kind}"
        cur.counters[key] += 1
        return f"{cur.stem}_{key}{cur.counters[key]:02d}"

    def _emit_heading(self, block: _TextBlock, page: int, cur: _Cursor) -> None:
        self._flush_text(cur)
        level = cur.levels[round(block.max_size, 1)]
        while cur.stack and cur.stack[-1][0] >= level:
            cur.stack.pop()
        cur.stack.append((level, block.text))
        cur.chunks.append(
            Chunk(
                chunk_id=self._next_id(cur, page, "h"),
                chunk_type=ChunkType.HEADING,
                content=block.text,
                heading_stack=cur.heading_stack,
                page_number=page,
                metadata=cur.meta,
            )
        )

    def _add_text(self, text: str, page: int, cur: _Cursor) -> None:
        """Short fragments are glued to the next block until they reach ``min_chars``."""
        if cur.pending_text and len(cur.pending_text) >= self._cfg.min_chars:
            self._flush_text(cur)
        if not cur.pending_text:
            cur.pending_page = page
            cur.pending_stack = cur.heading_stack
        cur.pending_text = f"{cur.pending_text} {text}".strip()

    def _flush_text(self, cur: _Cursor) -> None:
        text, cur.pending_text = cur.pending_text, ""
        if not text or (len(text) < self._cfg.min_chars and not _has_digit(text)):
            return  # leftover noise such as a lone place name; short facts with digits stay
        for part in self._split_long(text):
            cur.chunks.append(
                Chunk(
                    chunk_id=self._next_id(cur, cur.pending_page, "t"),
                    chunk_type=ChunkType.TEXT,
                    content=part,
                    heading_stack=cur.pending_stack,
                    page_number=cur.pending_page,
                    metadata=cur.meta,
                )
            )

    def _split_long(self, text: str) -> list[str]:
        """Cut at sentence ends, then at spaces, never beyond ``max_block_chars``."""
        limit = self._cfg.max_block_chars
        if len(text) <= limit:
            return [text]
        parts: list[str] = []
        current = ""
        for sentence in _SENTENCE_END.split(text):
            while len(sentence) > limit:
                cut = sentence.rfind(" ", 0, limit) or limit
                cut = cut if cut > 0 else limit
                if current:
                    parts.append(current)
                    current = ""
                parts.append(sentence[:cut].strip())
                sentence = sentence[cut:].strip()
            if current and len(current) + 1 + len(sentence) > limit:
                parts.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            parts.append(current)
        return parts

    # ---- tables ---------------------------------------------------------------------------

    def _emit_table(self, table: _TableRegion, content: _PageContent, cur: _Cursor) -> None:
        filled = [
            (box, self._row_cells(box, table.bbox, content.spans)) for box in table.row_bboxes
        ]
        filled = [(box, cells) for box, cells in filled if cells]
        if not filled:
            return
        rows = [cells for _, cells in filled]
        header = self._header_columns(filled[0][0], content.spans, rows[0])
        data_rows = rows[1:] if header else rows
        counter_key = f"p{content.number}_tab"
        cur.counters[counter_key] += 1
        table_id = f"{counter_key}{cur.counters[counter_key]:02d}"
        columns = tuple(name for _, _, name in header)
        meta = cur.meta.model_copy(update={"table_id": table_id, "columns": columns})
        for row_number, row in enumerate(data_rows, start=1):
            text = self._serialise_row(row, header)
            if not text:
                continue
            cur.chunks.append(
                Chunk(
                    chunk_id=f"{cur.stem}_{table_id}_r{row_number:02d}",
                    chunk_type=ChunkType.TABLE_ROW,
                    content=text,
                    heading_stack=cur.heading_stack,
                    page_number=content.number,
                    metadata=meta,
                )
            )

    def _row_cells(
        self, row_box: BBox, table_box: BBox, spans: Sequence[_Span]
    ) -> list[tuple[float, float, str]]:
        """Cluster the spans of one row into cells: x-overlapping or close spans belong together."""
        inside = [
            s
            for s in spans
            if row_box[1] - 1 <= s.center[1] <= row_box[3] + 1
            and table_box[0] - 1 <= s.center[0] <= table_box[2] + 1
        ]
        clusters: list[list[_Span]] = []
        for span in sorted(inside, key=lambda s: s.bbox[0]):
            if (
                clusters
                and span.bbox[0] <= max(s.bbox[2] for s in clusters[-1]) + self._cfg.cell_gap_pt
            ):
                clusters[-1].append(span)
            else:
                clusters.append([span])
        cells = []
        for cluster in clusters:
            ordered = sorted(cluster, key=lambda s: (round(s.bbox[1]), s.bbox[0]))
            text = _normalise(" ".join(s.text for s in ordered))
            if text:
                cells.append(
                    (min(s.bbox[0] for s in cluster), max(s.bbox[2] for s in cluster), text)
                )
        return cells

    @staticmethod
    def _header_columns(
        first_row_box: BBox, spans: Sequence[_Span], first_row: list[tuple[float, float, str]]
    ) -> list[tuple[float, float, str]]:
        """The first row is the header if all its text is bold and it has several cells."""
        row_spans = [
            s for s in spans if first_row_box[1] - 1 <= s.center[1] <= first_row_box[3] + 1
        ]
        is_bold_row = bool(row_spans) and all(s.is_bold for s in row_spans)
        return first_row if is_bold_row and len(first_row) >= 2 else []

    @staticmethod
    def _serialise_row(
        row: list[tuple[float, float, str]], header: list[tuple[float, float, str]]
    ) -> str:
        if not header:
            return _join_cells([text for _, _, text in row])
        values: dict[int, list[str]] = {}
        for x0, x1, text in row:
            overlapping = [i for i, (h0, h1, _) in enumerate(header) if min(x1, h1) > max(x0, h0)]
            if overlapping:
                column = overlapping[0]  # a wide merged label belongs to its leftmost column
            else:
                column = min(
                    range(len(header)),
                    key=lambda i: abs((x0 + x1) / 2 - (header[i][0] + header[i][1]) / 2),
                )
            values.setdefault(column, []).append(text)
        return " | ".join(f"{header[i][2]}: {' '.join(values[i])}" for i in sorted(values))

    # ---- images ---------------------------------------------------------------------------

    def _emit_image(
        self, document: pymupdf.Document, image: _ImageRegion, page: int, cur: _Cursor
    ) -> None:
        extracted = document.extract_image(image.xref)
        if not extracted:
            return
        chunk_id = self._next_id(cur, page, "img")
        file_name = f"{chunk_id}.{extracted['ext']}"
        self._images_dir.mkdir(parents=True, exist_ok=True)
        (self._images_dir / file_name).write_bytes(extracted["image"])
        meta = cur.meta.model_copy(update={"image_path": f"{self._images_dir.name}/{file_name}"})
        cur.chunks.append(
            Chunk(
                chunk_id=chunk_id,
                chunk_type=ChunkType.IMAGE,
                content=f"Abbildung auf Seite {page} (Beschreibung folgt im Enrichment)",
                heading_stack=cur.heading_stack,
                page_number=page,
                metadata=meta,
            )
        )


__all__ = ["DocumentParser", "ParseError"]
