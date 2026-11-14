"""Ingestion pipeline: ``documents.yaml`` + PDFs -> ``data/processed/<stem>_chunks.json``.

Idempotent: every run rewrites all outputs and removes results of PDFs that left the catalog.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from audit_agent.config import Settings
from audit_agent.corpus import CorpusError, load_document_catalog, missing_files
from audit_agent.ingestion.models import ChunkType, ParsedDocument
from audit_agent.ingestion.parser import DocumentParser

logger = logging.getLogger(__name__)

CHUNKS_SUFFIX = "_chunks.json"


@dataclass(frozen=True)
class IngestionReport:
    """What one pipeline run produced."""

    documents: int
    chunks_by_type: dict[str, int]

    @property
    def total_chunks(self) -> int:
        return sum(self.chunks_by_type.values())


def chunks_path(processed_dir: Path, pdf_file: str) -> Path:
    """Location of the JSON file for a catalog entry such as ``01_x/04_y.pdf``."""
    return processed_dir / f"{Path(pdf_file).stem}{CHUNKS_SUFFIX}"


def load_parsed_document(path: Path) -> ParsedDocument:
    """Read one ``*_chunks.json`` back into the typed model."""
    return ParsedDocument.model_validate_json(path.read_text(encoding="utf-8"))


def run_ingestion(settings: Settings) -> IngestionReport:
    """Parse all catalog PDFs and write the JSON intermediate format."""
    catalog = load_document_catalog(settings.documents_file)
    problems = missing_files(catalog, settings.dataset_dir)
    if problems:
        raise CorpusError(f"catalog and dataset folder disagree: {problems}")

    processed = settings.processed_dir
    processed.mkdir(parents=True, exist_ok=True)
    if settings.images_dir.exists():
        shutil.rmtree(settings.images_dir)
    parser = DocumentParser(settings.parser, settings.images_dir)

    expected: set[Path] = set()
    counts: dict[str, int] = {chunk_type.value: 0 for chunk_type in ChunkType}
    for meta in catalog.documents:
        parsed = parser.parse(settings.dataset_dir / meta.file, meta)
        target = chunks_path(processed, meta.file)
        target.write_text(parsed.model_dump_json(indent=2) + "\n", encoding="utf-8")
        expected.add(target)
        for chunk in parsed.chunks:
            counts[chunk.chunk_type.value] += 1
        logger.info("%s: %d chunks", meta.file, len(parsed.chunks))

    for stale in processed.glob(f"*{CHUNKS_SUFFIX}"):
        if stale not in expected:
            stale.unlink()
    return IngestionReport(documents=len(catalog.documents), chunks_by_type=counts)
