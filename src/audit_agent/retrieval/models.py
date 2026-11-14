"""Typed options and results of the retrieval (concept.md, section 10.9)."""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from audit_agent.corpus import DocType, UtilityType
from audit_agent.ingestion import ChunkType


class RetrievalError(RuntimeError):
    """Raised when the index is missing or empty or the embedding service fails."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MetadataFilter(_Frozen):
    """Hard filter on document metadata (ADR-0002); unset fields do not filter.

    A billing period filter keeps documents whose billing period overlaps the given range.
    Documents without a billing period (contracts, notices) are dropped by it (ISS-025).
    """

    utility_type: UtilityType | None = None
    doc_type: DocType | None = None
    contract_id: str | None = None
    period_start: date | None = None
    period_end: date | None = None

    @model_validator(mode="after")
    def _check_period(self) -> Self:
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("a period filter needs both period_start and period_end")
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValueError("period_start is after period_end")
        return self

    @classmethod
    def for_year(
        cls,
        year: int,
        utility_type: UtilityType | None = None,
        doc_type: DocType | None = None,
        contract_id: str | None = None,
    ) -> MetadataFilter:
        """Filter on the billing period of a whole calendar year plus optional fields."""
        return cls(
            utility_type=utility_type,
            doc_type=doc_type,
            contract_id=contract_id,
            period_start=date(year, 1, 1),
            period_end=date(year, 12, 31),
        )


class SearchOptions(_Frozen):
    """How one search runs; the defaults are the full strategy (filter off, boost on)."""

    metadata_filter: MetadataFilter = Field(default_factory=MetadataFilter)
    use_hierarchy_boost: bool = True
    chunk_types: frozenset[ChunkType] | None = None
    """Restrict the search to these chunk types (``None`` = everything that is indexed)."""
    require_heading: bool = False
    """Skip chunks without a heading path (letterhead and address blocks, ISS-015)."""
    top_k: int | None = Field(default=None, ge=1)
    """Number of returned hits (``None`` = ``RetrievalSettings.top_k``)."""


class SearchHit(_Frozen):
    """One re-ranked search result; ``final_score = base_score * boost`` can be recomputed."""

    chunk_id: str
    chunk_type: ChunkType
    content: str
    heading_stack: tuple[str, ...]
    page_number: int = Field(ge=1)
    filename: str
    base_score: float
    """``1 - cosine distance`` between query and chunk embedding."""
    boost: float
    """``RetrievalSettings.hierarchy_boost`` for a path match, otherwise ``1.0``."""
    final_score: float
    matched_terms: tuple[str, ...] = ()
    """Query terms found in file name, folder or headings (the reason for the boost)."""
