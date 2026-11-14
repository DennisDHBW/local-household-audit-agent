"""Enrichment pipeline: adds image captions and table summaries to ``data/processed``.

Runs after the ingestion (``python -m audit_agent.ingestion``). Idempotent: with a filled
cache a rerun makes no model call and writes the same result. A failure stops the run, but
all finished answers stay in the cache, so the next run resumes where this one ended.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from audit_agent.config import Settings
from audit_agent.enrichment.cache import EnrichmentCache
from audit_agent.enrichment.captioner import ImageCaptioner
from audit_agent.enrichment.checks import unsupported_numbers
from audit_agent.enrichment.llm import (
    ChatClient,
    EnrichmentError,
    installed_models,
    unload_all_running,
    unload_model,
)
from audit_agent.enrichment.prompts import describe_context
from audit_agent.enrichment.summarizer import TableSummarizer
from audit_agent.ingestion import (
    CHUNKS_SUFFIX,
    ChunkType,
    DocumentChunk,
    ParsedDocument,
    load_parsed_document,
)
from audit_agent.preflight import ensure_models_available

logger = logging.getLogger(__name__)

CACHE_SUBDIRECTORY = "enrichment"
SUMMARY_SUFFIX = "_sum"


class EnrichmentKind(StrEnum):
    IMAGES = "images"
    TABLES = "tables"


class EnrichedItem(BaseModel):
    """One image caption or table summary of a run (``text`` stays empty in a dry run)."""

    kind: EnrichmentKind
    item_id: str
    model: str
    is_cache_hit: bool
    seconds: float | None = None
    text: str | None = None
    unsupported_numbers: list[float] = []


class EnrichmentReport(BaseModel):
    """What one enrichment run did (written to ``data/eval/<run-id>/enrichment.json``)."""

    is_dry_run: bool
    items: list[EnrichedItem]

    @property
    def cache_hits(self) -> int:
        return sum(item.is_cache_hit for item in self.items)

    @property
    def cache_misses(self) -> int:
        return len(self.items) - self.cache_hits

    @property
    def flagged_summaries(self) -> list[EnrichedItem]:
        return [item for item in self.items if item.unsupported_numbers]


@dataclass(frozen=True)
class _TableJob:
    path: Path
    table_id: str
    rows: tuple[DocumentChunk, ...]


Documents = dict[Path, ParsedDocument]


def load_processed_documents(processed_dir: Path) -> Documents:
    paths = sorted(processed_dir.glob(f"*{CHUNKS_SUFFIX}"))
    if not paths:
        raise EnrichmentError(
            f"no *{CHUNKS_SUFFIX} files in {processed_dir}; run "
            "`uv run python -m audit_agent.ingestion` first"
        )
    return {path: load_parsed_document(path) for path in paths}


def _write_documents(documents: Documents) -> None:
    for path, document in documents.items():
        path.write_text(document.model_dump_json(indent=2) + "\n", encoding="utf-8")


def run_enrichment(
    settings: Settings,
    client: ChatClient,
    *,
    kinds: frozenset[EnrichmentKind] = frozenset(EnrichmentKind),
    limit: int | None = None,
    is_dry_run: bool = False,
) -> EnrichmentReport:
    """Enrich the processed documents. ``limit`` caps the jobs per kind (quick trial run)."""
    documents = load_processed_documents(settings.processed_dir)
    if not is_dry_run:
        required = []
        if EnrichmentKind.IMAGES in kinds:
            required.append(settings.models.vision)
        if EnrichmentKind.TABLES in kinds:
            required.append(settings.models.summary)
        ensure_models_available(installed_models(client), required)
        unload_all_running(client)

    cache = EnrichmentCache(settings.cache_dir / CACHE_SUBDIRECTORY)
    items: list[EnrichedItem] = []
    try:
        if EnrichmentKind.IMAGES in kinds:
            items += _enrich_images(settings, client, cache, documents, limit, is_dry_run)
        if EnrichmentKind.TABLES in kinds:
            items += _enrich_tables(settings, client, cache, documents, limit, is_dry_run)
    finally:
        cache.close()
    return EnrichmentReport(is_dry_run=is_dry_run, items=items)


# ---- images --------------------------------------------------------------------------------


def _enrich_images(
    settings: Settings,
    client: ChatClient,
    cache: EnrichmentCache,
    documents: Documents,
    limit: int | None,
    is_dry_run: bool,
) -> list[EnrichedItem]:
    captioner = ImageCaptioner(client, settings, cache)
    jobs = [
        (path, chunk)
        for path, document in documents.items()
        for chunk in document.chunks
        if chunk.chunk_type is ChunkType.IMAGE
    ][:limit]
    items: list[EnrichedItem] = []
    captions: dict[tuple[Path, str], str] = {}
    for number, (path, chunk) in enumerate(jobs, start=1):
        image = _read_image(settings, chunk)
        if is_dry_run:
            is_hit = captioner.is_cached(image, chunk.heading_stack)
            items.append(_dry_item(EnrichmentKind.IMAGES, chunk.chunk_id, captioner.model, is_hit))
            continue
        answer, is_hit = captioner.caption(image, chunk.heading_stack)
        captions[(path, chunk.chunk_id)] = answer.text
        items.append(
            EnrichedItem(
                kind=EnrichmentKind.IMAGES,
                item_id=chunk.chunk_id,
                model=answer.model,
                is_cache_hit=is_hit,
                seconds=answer.seconds,
                text=answer.text,
            )
        )
        _log_progress("image", number, len(jobs), chunk.chunk_id, is_hit, answer.seconds)
    if captions:
        _apply_to_documents(documents, lambda chunks, path: _with_captions(chunks, path, captions))
        _write_documents(documents)
    if not is_dry_run and jobs:
        unload_model(client, captioner.model)
    return items


def _read_image(settings: Settings, chunk: DocumentChunk) -> bytes:
    relative = chunk.metadata.image_path
    if relative is None:  # excluded by the DocumentChunk validator, kept for the type checker
        raise EnrichmentError(f"{chunk.chunk_id}: image chunk without image_path")
    path = settings.processed_dir / relative
    if not path.is_file():
        raise EnrichmentError(f"{chunk.chunk_id}: image file {path} is missing; rerun ingestion")
    return path.read_bytes()


def _with_captions(
    chunks: tuple[DocumentChunk, ...], path: Path, captions: dict[tuple[Path, str], str]
) -> tuple[DocumentChunk, ...]:
    return tuple(
        chunk.model_copy(update={"content": captions[(path, chunk.chunk_id)]})
        if (path, chunk.chunk_id) in captions
        else chunk
        for chunk in chunks
    )


# ---- tables --------------------------------------------------------------------------------


def _enrich_tables(
    settings: Settings,
    client: ChatClient,
    cache: EnrichmentCache,
    documents: Documents,
    limit: int | None,
    is_dry_run: bool,
) -> list[EnrichedItem]:
    summarizer = TableSummarizer(client, settings, cache)
    jobs = _table_jobs(documents)[:limit]
    items: list[EnrichedItem] = []
    summaries: dict[tuple[Path, str], DocumentChunk] = {}
    for number, job in enumerate(jobs, start=1):
        first = job.rows[0]
        row_texts = [row.content for row in job.rows]
        columns = first.metadata.columns
        summary_id = _summary_id(first)
        if is_dry_run:
            is_hit = summarizer.is_cached(first.heading_stack, columns, row_texts)
            items.append(_dry_item(EnrichmentKind.TABLES, summary_id, summarizer.model, is_hit))
            continue
        answer, is_hit = summarizer.summarize(first.heading_stack, columns, row_texts)
        source = "\n".join([describe_context(first.heading_stack), *columns, *row_texts])
        unsupported = unsupported_numbers(answer.text, source)
        summaries[(job.path, job.table_id)] = first.model_copy(
            update={
                "chunk_id": summary_id,
                "chunk_type": ChunkType.TABLE_SUMMARY,
                "content": answer.text,
            }
        )
        items.append(
            EnrichedItem(
                kind=EnrichmentKind.TABLES,
                item_id=summary_id,
                model=answer.model,
                is_cache_hit=is_hit,
                seconds=answer.seconds,
                text=answer.text,
                unsupported_numbers=unsupported,
            )
        )
        _log_progress("table", number, len(jobs), summary_id, is_hit, answer.seconds)
        if unsupported:
            logger.warning("  numbers not found in the table: %s", unsupported)
    if summaries:
        _apply_to_documents(
            documents, lambda chunks, path: _with_summaries(chunks, path, summaries)
        )
        _write_documents(documents)
    if not is_dry_run and jobs:
        unload_model(client, summarizer.model)
    return items


def _table_jobs(documents: Documents) -> list[_TableJob]:
    jobs: list[_TableJob] = []
    for path, document in documents.items():
        rows_by_table: dict[str, list[DocumentChunk]] = {}
        for chunk in document.chunks:
            if chunk.chunk_type is ChunkType.TABLE_ROW and chunk.metadata.table_id is not None:
                rows_by_table.setdefault(chunk.metadata.table_id, []).append(chunk)
        jobs += [_TableJob(path, table_id, tuple(rows)) for table_id, rows in rows_by_table.items()]
    return jobs


def _summary_id(first_row: DocumentChunk) -> str:
    """``<stem>_p1_tab01_r01`` -> ``<stem>_p1_tab01_sum``."""
    return first_row.chunk_id.rsplit("_r", 1)[0] + SUMMARY_SUFFIX


def _with_summaries(
    chunks: tuple[DocumentChunk, ...],
    path: Path,
    summaries: dict[tuple[Path, str], DocumentChunk],
) -> tuple[DocumentChunk, ...]:
    """Replace old summaries of the given tables and put the new one before the first row."""
    result: list[DocumentChunk] = []
    inserted: set[str] = set()
    for chunk in chunks:
        table_id = chunk.metadata.table_id
        summary = None if table_id is None else summaries.get((path, table_id))
        if summary is None:
            result.append(chunk)
        elif chunk.chunk_type is ChunkType.TABLE_SUMMARY:
            continue  # replaced by the new summary
        else:
            if table_id not in inserted:
                result.append(summary)
                inserted.add(table_id)  # type: ignore[arg-type]
            result.append(chunk)
    return tuple(result)


# ---- shared helpers ------------------------------------------------------------------------


def _apply_to_documents(
    documents: Documents,
    transform: Callable[[tuple[DocumentChunk, ...], Path], tuple[DocumentChunk, ...]],
) -> None:
    """Rebuild every document (re-validates ids) with the transformed chunk tuple."""
    for path, document in list(documents.items()):
        documents[path] = ParsedDocument(
            file=document.file,
            page_count=document.page_count,
            chunks=transform(document.chunks, path),
        )


def _dry_item(kind: EnrichmentKind, item_id: str, model: str, is_hit: bool) -> EnrichedItem:
    return EnrichedItem(kind=kind, item_id=item_id, model=model, is_cache_hit=is_hit)


def _log_progress(
    label: str, number: int, total: int, item_id: str, is_hit: bool, seconds: float
) -> None:
    source = "cache" if is_hit else f"{seconds:.0f} s"
    logger.info("[%s %d/%d] %s (%s)", label, number, total, item_id, source)
