"""Quantity query: the question reduced to the billing quantity it asks for (M6h, ISS-051/052).

A long question embeds as "a question about a 2025 bill", so the year and the document words
pull in every chunk of that document and the table row with the actual number stays behind
(RUN-014, G1: five hits from the meter-reading letter, no row with the new price). The quantity
query keeps only the content words ("Arbeitspreis"); a second search with it finds the rows.

The removed words name the utility ("Stromabrechnung"). Without them "Arbeitspreis" also fits
the gas price letter (RUN-019, ISS-077), so the utility the query names becomes a metadata
filter of the second search (M6i).
"""

from __future__ import annotations

import re
from collections.abc import Callable

from audit_agent.corpus import UtilityType
from audit_agent.retrieval.models import SearchHit, SearchOptions
from audit_agent.retrieval.search import STOPWORDS, fold

_WORD = re.compile(r"[^\W_]+(?:-[^\W_]+)*")
"""Words with inner hyphens stay whole (``z-Zahl``)."""
MIN_CHARS = 3

_QUESTION_TEXT = (
    "angewendet angewandt abgerechnet berechnet angesetzt korrekt richtig falsch stimmt stimmen "
    "passt passen ueberein uebereinstimmung pruefe pruefen nachgerechnet wieviel viel hoch "
    "hoeher niedriger zahle zahlen musste muss soll sollte sollten haette hat hatte "
    "neu neue neuer neuen neues alt alte alter alten aktuell aktuelle aktueller aktuellen "
    "bisher bisherige bisheriger bisherigen angekuendigt angekuendigte angekuendigter "
    "angekuendigten vereinbart vereinbarte vereinbarter vereinbarten"
)
_DOCUMENT_TEXT = (
    "rechnung rechnungen abrechnung abrechnungen jahresrechnung jahresabrechnung "
    "vertrag vertraege liefervertrag mietvertrag vertragsbestaetigung preisanpassung "
    "preisschreiben schreiben dokument dokumente unterlagen unterlage"
)
DOCUMENT_WORDS = frozenset(_DOCUMENT_TEXT.split())
"""Folded words that name a document; ``Strom`` + one of them names the utility of a document."""
UTILITY_WORDS: dict[str, UtilityType] = {
    "strom": UtilityType.ELECTRICITY,
    "gas": UtilityType.GAS,
    "erdgas": UtilityType.GAS,
    "wasser": UtilityType.WATER,
    "fernwaerme": UtilityType.DISTRICT_HEATING,
}
"""Folded utility words of a query. Operating costs are left out on purpose: such a question
needs the tenancy agreement (``rent``) and the statement (``service_charges``) together."""
FILLER = frozenset(_QUESTION_TEXT.split()) | DOCUMENT_WORDS | frozenset(UTILITY_WORDS)
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


def _utility_of_word(folded: str) -> UtilityType | None:
    """Utility of ``strom`` or ``stromabrechnung``; ``None`` for ``stromverbrauch``."""
    for name, utility in UTILITY_WORDS.items():
        rest = folded.removeprefix(name)
        if folded.startswith(name) and (
            not rest or rest in DOCUMENT_WORDS or rest.endswith(_DOCUMENT_SUFFIXES)
        ):
            return utility
    return None


def utility_in_query(query: str) -> UtilityType | None:
    """The one utility a query names, or ``None`` if it names none or more than one.

    Counted are the utility word alone (``Strom``, also as part of ``Gas-Arbeitspreis``) and
    as the start of a document word (``Stromabrechnung``, ``Gasvertrag``). Compounds that name
    a quantity (``Wasserverbrauch``) are not counted: they stay in the quantity query, and in
    an operating cost statement they are a cost item, not the utility of the document.
    """
    parts = (part for word in _WORD.findall(query) for part in fold(word).split("-"))
    found = {utility for part in parts if (utility := _utility_of_word(part)) is not None}
    return found.pop() if len(found) == 1 else None


def with_query_utility(options: SearchOptions, query: str) -> SearchOptions:
    """``options`` narrowed to the utility that ``query`` names (for the quantity search).

    A utility filter that is already set wins (the agent chose it); without a utility in the
    query the options come back unchanged.
    """
    if options.metadata_filter.utility_type is not None:
        return options
    utility = utility_in_query(query)
    if utility is None:
        return options
    narrowed = options.metadata_filter.model_copy(update={"utility_type": utility})
    return options.model_copy(update={"metadata_filter": narrowed})


def new_quantity_hits(
    search: Callable[[str, SearchOptions], list[SearchHit]],
    quantity: str,
    options: SearchOptions,
    hits: list[SearchHit],
    wanted: int,
) -> list[SearchHit]:
    """Up to ``wanted`` hits of the quantity search that ``hits`` does not contain yet.

    ``options`` are those of the first search (filter, chunk types), narrowed by
    ``with_query_utility``; its ``top_k`` is replaced so that the new hits are not crowded out
    by the ones that are already there.
    """
    seen = {hit.chunk_id for hit in hits}
    found = search(quantity, options.model_copy(update={"top_k": wanted + len(hits)}))
    return [hit for hit in found if hit.chunk_id not in seen][:wanted]
