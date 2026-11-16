"""Quantity query: the question reduced to the billing quantity it asks for (M6h, ISS-051/052).

A long question embeds as "a question about a 2025 bill", so the year and the document words
pull in every chunk of that document and the table row with the actual number stays behind
(RUN-014, G1: five hits from the meter-reading letter, no row with the new price). The quantity
query keeps only the content words ("Arbeitspreis"); a second search with it finds the rows.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from audit_agent.retrieval.models import SearchHit, SearchOptions
from audit_agent.retrieval.search import STOPWORDS, fold

_WORD = re.compile(r"[^\W_]+(?:-[^\W_]+)*")
"""Words with inner hyphens stay whole (``z-Zahl``)."""
MIN_CHARS = 3

_FILLER_TEXT = (
    "angewendet angewandt abgerechnet berechnet angesetzt korrekt richtig falsch stimmt stimmen "
    "passt passen ueberein uebereinstimmung pruefe pruefen nachgerechnet wieviel viel hoch "
    "hoeher niedriger zahle zahlen musste muss soll sollte sollten haette hat hatte "
    "neu neue neuer neuen neues alt alte alter alten aktuell aktuelle aktueller aktuellen "
    "bisher bisherige bisheriger bisherigen angekuendigt angekuendigte angekuendigter "
    "angekuendigten vereinbart vereinbarte vereinbarter vereinbarten "
    "rechnung rechnungen abrechnung abrechnungen jahresrechnung jahresabrechnung "
    "vertrag vertraege liefervertrag mietvertrag vertragsbestaetigung preisanpassung "
    "preisschreiben schreiben dokument dokumente unterlagen unterlage "
    "strom gas erdgas wasser fernwaerme"
)
FILLER = frozenset(_FILLER_TEXT.split())
"""Folded words that name no quantity: question and verdict words, dates, document and utility."""
_DOCUMENT_SUFFIXES = ("abrechnung", "rechnung", "vertrag")
"""Compounds such as ``Gasabrechnung`` or ``Stromvertrag`` name a document, not a quantity."""


def _is_filler(folded: str) -> bool:
    return (
        len(folded) < MIN_CHARS
        or folded.isdigit()
        or folded in STOPWORDS
        or folded in FILLER
        or folded.endswith(_DOCUMENT_SUFFIXES)
    )


def quantity_query(query: str) -> str | None:
    """The content words of a query, or ``None`` if there are none or nothing was removed.

    ``"neuer Arbeitspreis 2025"`` gives ``"Arbeitspreis"``; ``"Gasabrechnung 2026"`` gives
    ``None`` (no quantity named); ``"Arbeitspreis"`` gives ``None`` (the query is already
    that short, a second search would repeat the first).
    """
    words = _WORD.findall(query)
    kept = [word for word in words if not _is_filler(fold(word))]
    if not kept or len(kept) == len(words):
        return None
    return " ".join(dict.fromkeys(kept))


def new_quantity_hits(
    search: Callable[[str, SearchOptions], list[SearchHit]],
    quantity: str,
    options: SearchOptions,
    hits: list[SearchHit],
    wanted: int,
) -> list[SearchHit]:
    """Up to ``wanted`` hits of the quantity search that ``hits`` does not contain yet.

    ``options`` are those of the first search (filter, chunk types); its ``top_k`` is replaced
    so that the new hits are not crowded out by the ones that are already there.
    """
    seen = {hit.chunk_id for hit in hits}
    found = search(quantity, options.model_copy(update={"top_k": wanted + len(hits)}))
    return [hit for hit in found if hit.chunk_id not in seen][:wanted]
