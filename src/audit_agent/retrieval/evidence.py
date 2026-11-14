"""Evidence view: hits regrouped as document -> chapter -> hit (concept.md, section 10.10).

``table_summary`` and ``image`` hits come from a model, not from the PDF text; they are
labelled as AI output and are never evidence for a figure (ADR-0008).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict

from audit_agent.ingestion import ChunkType
from audit_agent.retrieval.index import HEADING_SEPARATOR
from audit_agent.retrieval.models import SearchHit

NO_CHAPTER = "(ohne Kapitel)"
TYPE_LABELS: dict[ChunkType, str] = {
    ChunkType.TEXT: "Text",
    ChunkType.HEADING: "Überschrift",
    ChunkType.TABLE_ROW: "Tabellenzeile",
    ChunkType.TABLE_SUMMARY: "KI-Zusammenfassung, kein Beleg",
    ChunkType.IMAGE: "KI-Bildbeschreibung, kein Beleg",
}
MODEL_GENERATED = frozenset({ChunkType.TABLE_SUMMARY, ChunkType.IMAGE})


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class EvidenceChapter(_Frozen):
    heading_stack: tuple[str, ...]
    hits: tuple[SearchHit, ...]

    @property
    def title(self) -> str:
        return HEADING_SEPARATOR.join(self.heading_stack) or NO_CHAPTER

    @property
    def best_score(self) -> float:
        return max(hit.final_score for hit in self.hits)


class EvidenceDocument(_Frozen):
    filename: str
    chapters: tuple[EvidenceChapter, ...]

    @property
    def best_score(self) -> float:
        return max(chapter.best_score for chapter in self.chapters)


def build_evidence(hits: Iterable[SearchHit]) -> list[EvidenceDocument]:
    """Group hits by document and chapter; best-scoring groups first."""
    by_document: dict[str, dict[tuple[str, ...], list[SearchHit]]] = {}
    for hit in hits:
        by_document.setdefault(hit.filename, {}).setdefault(hit.heading_stack, []).append(hit)
    documents = []
    for filename, chapters in by_document.items():
        built = [
            EvidenceChapter(
                heading_stack=stack,
                hits=tuple(sorted(group, key=lambda h: (-h.final_score, h.chunk_id))),
            )
            for stack, group in chapters.items()
        ]
        built.sort(key=lambda chapter: (-chapter.best_score, chapter.title))
        documents.append(EvidenceDocument(filename=filename, chapters=tuple(built)))
    documents.sort(key=lambda document: (-document.best_score, document.filename))
    return documents


def _shorten(text: str, limit: int) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def render_evidence_text(documents: Iterable[EvidenceDocument], content_chars: int = 160) -> str:
    """Plain-text evidence panel for the CLI (score = base × boost = final)."""
    lines: list[str] = []
    for document in documents:
        lines.append(f"{PurePosixPath(document.filename).name}  (Score {document.best_score:.3f})")
        for chapter in document.chapters:
            lines.append(f"  {chapter.title}")
            for hit in chapter.hits:
                marker = " [KI]" if hit.chunk_type in MODEL_GENERATED else ""
                lines.append(
                    f"    S.{hit.page_number} {TYPE_LABELS[hit.chunk_type]}{marker}  "
                    f"{hit.base_score:.3f} × {hit.boost:.1f} = {hit.final_score:.3f}"
                    + (
                        f"  Pfadtreffer: {', '.join(hit.matched_terms)}"
                        if hit.matched_terms
                        else ""
                    )
                )
                lines.append(f"      {_shorten(hit.content, content_chars)}")
    return "\n".join(lines)
