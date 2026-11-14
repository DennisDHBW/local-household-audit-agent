"""Prompt templates of the enrichment (German, because the documents are German)."""

from __future__ import annotations

from collections.abc import Sequence

CAPTION_PROMPT = (
    "Du siehst ein Diagramm aus einer Energie- oder Wasserabrechnung. "
    "Abschnitt des Dokuments: {context}\n"
    "Beschreibe das Diagramm sachlich auf Deutsch: Art des Diagramms, Achsen mit Einheit und "
    "jede Beschriftung (Jahr oder Monat) mit ihrem Zahlenwert und der Einheit, zum Beispiel "
    "'2022: 1.000 kWh'. Nenne nur Werte, die im Bild stehen. Rechne nichts aus."
)

SUMMARY_PROMPT = (
    "Fasse die folgende Tabelle aus einer Abrechnung oder einem Vertrag in zwei bis drei "
    "Sätzen auf Deutsch zusammen.\n"
    "Abschnitt des Dokuments: {context}\n"
    "Spalten: {columns}\n"
    "Zeilen:\n{rows}\n"
    "Regeln: Nenne, worum es in der Tabelle geht, und die wichtigsten Werte mit Einheit. "
    "Übernimm Zahlen exakt so, wie sie in den Zeilen stehen. Rechne nichts aus und erfinde "
    "nichts dazu."
)


def describe_context(heading_stack: Sequence[str]) -> str:
    """Heading path as one line (``Dokumenttitel > Kapitel``)."""
    return " > ".join(heading_stack) if heading_stack else "unbekannt"


def build_caption_prompt(heading_stack: Sequence[str]) -> str:
    return CAPTION_PROMPT.format(context=describe_context(heading_stack))


def build_summary_prompt(
    heading_stack: Sequence[str], columns: Sequence[str], row_texts: Sequence[str]
) -> str:
    return SUMMARY_PROMPT.format(
        context=describe_context(heading_stack),
        columns=", ".join(columns) if columns else "(keine Kopfzeile)",
        rows="\n".join(f"- {text}" for text in row_texts),
    )
