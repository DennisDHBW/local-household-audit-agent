"""Index build: ``data/processed`` chunks -> embeddings -> ChromaDB (concept.md, section 10.9).

Every chunk except headings is embedded as ``search_document: [Folder | File | H1 > H2] content``.
Headings are not indexed: they are already part of the path of the chunks below them.
The collection is rebuilt from scratch on every run, so the index is idempotent.
"""

from __future__ import annotations

import json
import logging
import time
from collections import Counter
from collections.abc import Sequence
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from pydantic import BaseModel

from audit_agent.config import Settings
from audit_agent.ingestion import CHUNKS_SUFFIX, ChunkType, DocumentChunk, load_parsed_document
from audit_agent.retrieval.models import RetrievalError

logger = logging.getLogger(__name__)

HEADING_SEPARATOR = " > "
"""Joins the headings inside the hierarchy prefix (display only; metadata keeps JSON)."""


class EmbeddingClient(Protocol):
    """Subset of ``ollama.Client`` used for embeddings (tests inject a fake)."""

    def embed(self, **kwargs: Any) -> Any: ...


class IndexReport(BaseModel):
    """What one index build did."""

    embedding_model: str
    document_count: int
    chunk_count: int
    chunks_by_type: dict[str, int]
    skipped_headings: int
    vector_dimension: int
    seconds: float


def open_vector_client(settings: Settings) -> ClientAPI:
    """Persistent ChromaDB client in ``data/vectors/``."""
    settings.vectors_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.vectors_dir))


def get_collection(settings: Settings, vector_client: ClientAPI) -> Collection:
    """The existing chunk collection; fails with the command to build it."""
    try:
        return vector_client.get_collection(
            settings.retrieval.collection_name, embedding_function=None
        )
    except Exception as error:  # chromadb raises different types per version
        raise RetrievalError(
            "no index found; run `uv run python -m audit_agent.retrieval index` first"
        ) from error


def load_chunks(processed_dir: Path) -> tuple[list[DocumentChunk], int]:
    """All chunks of ``data/processed`` in a stable order and the number of documents."""
    paths = sorted(processed_dir.glob(f"*{CHUNKS_SUFFIX}"))
    if not paths:
        raise RetrievalError(
            f"no *{CHUNKS_SUFFIX} files in {processed_dir}; run "
            "`uv run python -m audit_agent.ingestion` and the enrichment first"
        )
    chunks = [chunk for path in paths for chunk in load_parsed_document(path).chunks]
    ids = Counter(chunk.chunk_id for chunk in chunks)
    duplicates = sorted(chunk_id for chunk_id, count in ids.items() if count > 1)
    if duplicates:
        raise RetrievalError(f"duplicate chunk ids across documents: {duplicates[:5]}")
    return chunks, len(paths)


def is_indexed(chunk: DocumentChunk) -> bool:
    """Headings only carry the path of other chunks and are not embedded (ADR-0009)."""
    return chunk.chunk_type is not ChunkType.HEADING


def hierarchy_prefix(chunk: DocumentChunk) -> str:
    """``[Folder | File | H1 > H2]`` in front of the content (without file extension)."""
    path = PurePosixPath(chunk.metadata.filename)
    parts = [path.parent.name, path.stem]
    if chunk.heading_stack:
        parts.append(HEADING_SEPARATOR.join(chunk.heading_stack))
    return "[" + " | ".join(part for part in parts if part) + "]"


def embedding_text(chunk: DocumentChunk, document_task_prefix: str) -> str:
    """Exact text that is embedded for a chunk."""
    return f"{document_task_prefix}{hierarchy_prefix(chunk)} {chunk.content}"


def date_number(value: date) -> int:
    """``2025-12-31`` -> ``20251231``; ChromaDB can only compare numbers, not dates."""
    return value.year * 10000 + value.month * 100 + value.day


def chunk_record(chunk: DocumentChunk) -> dict[str, str | int | bool]:
    """Flat ChromaDB metadata of a chunk (``None`` values are left out)."""
    meta = chunk.metadata
    record: dict[str, str | int | bool | None] = {
        "filename": meta.filename,
        "chunk_type": chunk.chunk_type.value,
        "page_number": chunk.page_number,
        "heading_stack": json.dumps(chunk.heading_stack, ensure_ascii=False),
        "has_heading": bool(chunk.heading_stack),
        "utility_type": meta.utility_type.value,
        "doc_type": meta.doc_type.value,
        "provider": meta.provider,
        "contract_id": meta.contract_id,
        "document_date": date_number(meta.document_date),
        "period_start": date_number(meta.billing_period_start)
        if meta.billing_period_start
        else None,
        "period_end": date_number(meta.billing_period_end) if meta.billing_period_end else None,
        "valid_from": date_number(meta.valid_from) if meta.valid_from else None,
        "table_id": meta.table_id,
        "image_path": meta.image_path,
    }
    return {key: value for key, value in record.items() if value is not None}


def embed_texts(
    client: EmbeddingClient, model: str, texts: Sequence[str], keep_alive: str
) -> list[list[float]]:
    """One embedding call; fails fast if the answer does not match the input."""
    try:
        response = client.embed(model=model, input=list(texts), keep_alive=keep_alive)
    except Exception as error:  # ollama raises ResponseError, httpx errors, ...
        raise RetrievalError(f"embedding with {model} failed: {error}") from error
    vectors = [list(vector) for vector in response.embeddings]
    if len(vectors) != len(texts) or any(not vector for vector in vectors):
        raise RetrievalError(f"{model} returned {len(vectors)} embeddings for {len(texts)} texts")
    return vectors


def build_index(
    settings: Settings, client: EmbeddingClient, vector_client: ClientAPI
) -> IndexReport:
    """Rebuild the collection from ``data/processed`` (call after ingestion + enrichment)."""
    started = time.perf_counter()
    settings_r = settings.retrieval
    chunks, document_count = load_chunks(settings.processed_dir)
    indexed = [chunk for chunk in chunks if is_indexed(chunk)]
    if not any(chunk.chunk_type is ChunkType.TABLE_SUMMARY for chunk in indexed):
        logger.warning("no table summaries found: run the enrichment first (ISS-021)")

    existing = {collection.name for collection in vector_client.list_collections()}
    if settings_r.collection_name in existing:
        vector_client.delete_collection(settings_r.collection_name)
    collection = vector_client.create_collection(
        settings_r.collection_name,
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
    )

    dimension = 0
    batch_size = settings_r.embed_batch_size
    for start in range(0, len(indexed), batch_size):
        batch = indexed[start : start + batch_size]
        texts = [embedding_text(chunk, settings_r.document_task_prefix) for chunk in batch]
        vectors = embed_texts(client, settings.models.embedding, texts, settings_r.keep_alive)
        dimension = len(vectors[0])
        collection.add(
            ids=[chunk.chunk_id for chunk in batch],
            embeddings=vectors,
            documents=[chunk.content for chunk in batch],
            metadatas=[chunk_record(chunk) for chunk in batch],
        )
        logger.info("indexed %d/%d chunks", start + len(batch), len(indexed))

    return IndexReport(
        embedding_model=settings.models.embedding,
        document_count=document_count,
        chunk_count=len(indexed),
        chunks_by_type=dict(Counter(chunk.chunk_type.value for chunk in indexed)),
        skipped_headings=len(chunks) - len(indexed),
        vector_dimension=dimension,
        seconds=round(time.perf_counter() - started, 1),
    )
