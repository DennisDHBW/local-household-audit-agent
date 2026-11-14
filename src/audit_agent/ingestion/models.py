"""Typed chunks of the JSON intermediate format (concept.md, section 5.3).

One ``ParsedDocument`` per PDF is written to ``data/processed/<stem>_chunks.json``.
The chunk metadata contains what the agent may filter on; ``is_noise_document`` is
deliberately left out (it exists only for the evaluation).
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from audit_agent.corpus import DocType, DocumentMeta, UtilityType


class ChunkType(StrEnum):
    """Element type of a chunk. ``table_summary`` is added by the enrichment (M3)."""

    TEXT = "text"
    HEADING = "heading"
    TABLE_ROW = "table_row"
    TABLE_SUMMARY = "table_summary"
    IMAGE = "image"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ChunkMetadata(_Frozen):
    """Document-level metadata copied to every chunk, plus table and image details."""

    filename: str = Field(description="PDF path relative to the dataset folder, POSIX style")
    utility_type: UtilityType
    doc_type: DocType
    provider: str
    contract_id: str | None = None
    document_date: date
    billing_period_start: date | None = None
    billing_period_end: date | None = None
    valid_from: date | None = None
    table_id: str | None = None
    columns: tuple[str, ...] = ()
    image_path: str | None = Field(
        default=None, description="Image file relative to the processed folder"
    )

    @classmethod
    def from_document(cls, meta: DocumentMeta) -> Self:
        return cls(
            filename=meta.file,
            utility_type=meta.utility_type,
            doc_type=meta.doc_type,
            provider=meta.provider,
            contract_id=meta.contract_id,
            document_date=meta.document_date,
            billing_period_start=meta.billing_period_start,
            billing_period_end=meta.billing_period_end,
            valid_from=meta.valid_from,
        )


class DocumentChunk(_Frozen):
    """One typed piece of a document with its place in the heading hierarchy."""

    chunk_id: str
    chunk_type: ChunkType
    content: str = Field(min_length=1)
    heading_stack: tuple[str, ...] = ()
    page_number: int = Field(ge=1)
    metadata: ChunkMetadata

    @model_validator(mode="after")
    def _check_type_details(self) -> Self:
        if (
            self.chunk_type in (ChunkType.TABLE_ROW, ChunkType.TABLE_SUMMARY)
            and self.metadata.table_id is None
        ):
            raise ValueError(f"{self.chunk_id}: {self.chunk_type.value} needs a table_id")
        if self.chunk_type is ChunkType.IMAGE and self.metadata.image_path is None:
            raise ValueError(f"{self.chunk_id}: image needs an image_path")
        return self


class ParsedDocument(_Frozen):
    """All chunks of one PDF in reading order."""

    file: str
    page_count: int = Field(ge=1)
    chunks: tuple[DocumentChunk, ...]

    @model_validator(mode="after")
    def _check_unique_ids(self) -> Self:
        ids = [chunk.chunk_id for chunk in self.chunks]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"{self.file}: duplicate chunk ids {duplicates}")
        return self
