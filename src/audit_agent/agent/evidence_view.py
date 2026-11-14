"""Evidence-first view (concept.md, section 6): hits as document -> chapter -> hit with number.

Pure functions without Streamlit, so the structure can be tested. The numbers are the citation
numbers the model saw (``[3]``), so the answer can be checked against the shown evidence.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath

from audit_agent.agent.models import NumberedHit
from audit_agent.retrieval.evidence import MODEL_GENERATED, TYPE_LABELS, build_evidence


def evidence_sections(hits: Iterable[NumberedHit]) -> list[tuple[str, str]]:
    """``(title, markdown body)`` per document, best-scoring document first."""
    numbers = {item.hit.chunk_id: item.number for item in hits}
    by_id = {item.hit.chunk_id: item.hit for item in hits}
    sections = []
    for document in build_evidence(by_id.values()):
        title = f"{PurePosixPath(document.filename).name} (Score {document.best_score:.3f})"
        lines: list[str] = []
        for chapter in document.chapters:
            lines.append(f"**{chapter.title}**")
            for hit in chapter.hits:
                marker = " (KI, kein Beleg)" if hit.chunk_type in MODEL_GENERATED else ""
                lines.append(
                    f"- **[{numbers[hit.chunk_id]}]** S. {hit.page_number} · "
                    f"{TYPE_LABELS[hit.chunk_type]}{marker} · "
                    f"{hit.base_score:.3f} × {hit.boost:.1f} = {hit.final_score:.3f}"
                )
                lines.append(f"\n```text\n{hit.content}\n```\n")
        sections.append((title, "\n".join(lines)))
    return sections
