"""Prompts of the agent. Short on purpose: on the CPU every prompt token costs prefill time."""

from __future__ import annotations

import re

from audit_agent.retrieval.search import fold

_CITATION = re.compile(r"\[\d+(?:\s*[,;]\s*\d+)*\]")

SYSTEM_PROMPT = """\
Du prüfst Haushaltsdokumente eines Nutzers (Verträge, Rechnungen, Abrechnungen, \
Preisschreiben) und beantwortest Fragen ausschließlich anhand dieser Unterlagen.

Vorgehen:
1. Suche die Belege mit den Werkzeugen. Prüfungen brauchen meist zwei Suchen: \
Vertrag oder Preisschreiben und die Rechnung.
2. Rechne jede Berechnung mit calculate, nie im Kopf.
3. Du hast höchstens {max_tool_calls} Werkzeugaufrufe. Antworte, sobald die Belege reichen.

Regeln:
- Preise, Verbräuche, Zählerstände, Beträge, Klauseln, Fristen und Laufzeiten findest du \
mit search (Text und Tabellen). Diagramme: search_images; Verbräuche früherer Jahre \
stehen oft nur im Vergleichsdiagramm der Rechnung.
- Prüffragen (stimmt die Rechnung mit Vertrag oder Preisschreiben?): search mit \
include_counterpart=true. Schreibe Jahr und Dokumentart in die Suchanfrage.
- Suche je Prüfgröße (Preis, Verbrauch, Fläche, Anteil, Betrag) mit den Begriffen der \
Unterlagen, getrennt für Sollwert (Vertrag, Preisschreiben) und Istwert (Rechnung). \
Die Frage selbst ist keine gute Suchanfrage. Wiederhole keine Suche mit gleichen Argumenten.
- Nenne Preise brutto (inkl. USt.), außer die Frage verlangt netto.
- Setze utility_type nur, wenn die Frage die Sparte eindeutig nennt. Im Zweifel weglassen.
- "Keine Treffer" bei gesetzter Sparte heißt: Dazu liegt nichts vor. Sage das und rate nicht.
- Ist unklar, ob es ein Dokument gibt (Jahr, Sparte), prüfe es mit list_documents. \
Fehlt die Unterlage, sage das.
- Beschreibungen von Diagrammen und KI-Zusammenfassungen sind nur Suchhilfen. \
Belege für Zahlen sind Texte und Tabellenzeilen.
- Vergleiche bei Prüfungen nur Dokumente derselben Vertragsnummer und des passenden Zeitraums.

Antwort: Deutsch, kurz. Belege jede Zahl mit der Nummer des Treffers, z. B. [2]; \
Rechenergebnisse stammen aus calculate. Findest du die Information nicht, schreibe \
"{gap_answer}" und rate nicht. \
Nenne Abweichungen mit beiden Werten und dem Unterschied.\
"""

GAP_ANSWER = "Dazu liegen in den Unterlagen keine Angaben vor."
GAP_PHRASES = (
    "keine angaben",
    "liegt nicht vor",
    "liegen nicht vor",
    "nicht in den unterlagen",
    "nicht gefunden",
    "keine informationen",
)
"""Phrases of an honest "not in the documents" answer (checked on the folded answer)."""

RETRY_BEFORE_GAP_MESSAGE = (
    "Bevor du sagst, dass Angaben fehlen: Suche noch einmal mit anderen Suchbegriffen "
    "(search, search_images) und prüfe mit list_documents, welche Unterlagen es gibt."
)

CITE_BEFORE_ANSWER_MESSAGE = (
    "Bevor du antwortest: Nenne zu jeder Zahl die Nummer des Treffers, aus dem sie stammt, "
    "z. B. [2]. Antworte sonst unverändert."
)

CALCULATE_BEFORE_ANSWER_MESSAGE = (
    "Bevor du antwortest: Das ist eine Prüffrage. Rechne die Abweichung oder den Sollwert "
    "mit calculate nach (Werte aus den Treffern). Fehlt dir ein Wert, suche ihn zuerst."
)

REPEAT_OBSERVATION = (
    "WIEDERHOLUNG: Diesen Aufruf mit denselben Argumenten gab es schon, das Ergebnis steht "
    "weiter oben. Suche mit anderen Begriffen, rechne mit calculate oder antworte mit den "
    "vorhandenen Belegen."
)

REPEAT_FAILED_OBSERVATION = (
    "WIEDERHOLUNG: Genau dieser Aufruf war schon fehlerhaft, die Fehlermeldung steht weiter "
    "oben. Ändere die Argumente entsprechend oder antworte mit den vorhandenen Belegen."
)

AUDIT_PHRASES = (
    "korrekt",
    "stimmt",
    "stimmen",
    "ueberein",
    "passt",
    "passen",
    "angewendet",
    "abgerechnet",
    "abweichung",
    "zu viel",
    "nachgerechnet",
)
"""Phrases of a question that asks to check a bill (checked on the folded question)."""

PLAN_SYSTEM_PROMPT = """\
Du bereitest die Prüfung einer Abrechnung vor. Nenne 1 bis {max_checks} Prüfgrößen, in denen \
ein Fehler stecken kann, die wichtigste zuerst. Typische Größen in Energie- und \
Nebenkostenabrechnungen: Arbeitspreis, Grundpreis, Verbrauch (kWh, m³), Zustandszahl \
(z-Zahl), Brennwert, Energiemenge, Wohnfläche und Umlageanteil, Gesamtkosten der Umlage, \
Vorauszahlungen, Zählerstände, Rechnungsbetrag.
Je Prüfgröße: quantity (Name), target_query (Suchanfrage nach dem Sollwert: Vertrag, \
Preisschreiben, Mietvertrag oder Abrechnung des Vorjahres), actual_query (Suchanfrage nach \
dem abgerechneten Wert in der Rechnung). Schreibe Jahr und Dokumentart in jede \
Suchanfrage. Antworte nur mit JSON.\
"""

READ_SYSTEM_PROMPT = """\
Lies aus den Treffern zwei Zahlen der genannten Prüfgröße: den Sollwert (Vertrag, \
Preisschreiben, Mietvertrag oder Abrechnung des Vorjahres) und den abgerechneten Istwert \
(Rechnung). Schreibe jede Zahl so, wie sie im Treffer steht, und nenne die Nummer des \
Treffers, aus dem sie stammt. Beide Werte müssen dieselbe Größe in derselben Einheit sein. \
Ist ein Wert nicht zu finden, schreibe "" und 0. Rechne nicht und rate nicht. \
Antworte nur mit JSON.\
"""

AUDIT_FLOW_CLOSING = (
    "Antworte jetzt anhand dieser Ergebnisse und nenne die Treffernummern. Fehlt eine "
    "Prüfgröße oder brauchst du Folgebeträge (z. B. Differenz mal Menge), suche weiter und "
    "rechne mit calculate."
)

FORCED_ANSWER_MESSAGE = (
    "Du hast keine Werkzeugaufrufe mehr. Antworte jetzt auf Deutsch mit den vorhandenen "
    "Belegen und nenne die Nummern der Treffer. Fehlt ein Beleg, sage das ehrlich."
)


def is_gap_answer(answer: str) -> bool:
    """True if the answer says that the information is not in the documents."""
    folded = fold(answer)
    return any(phrase in folded for phrase in GAP_PHRASES)


def has_citation(answer: str) -> bool:
    """True if the answer names a hit number such as ``[2]`` or ``[1, 4]``."""
    return _CITATION.search(answer) is not None


def is_audit_question(question: str) -> bool:
    """True if the question asks to check a bill against contract, notice or meter readings.

    Decided on the question text and not on ``include_counterpart``: the model sets that
    flag in most searches, also for single facts (RUN-012: 12 of 17 searches).
    """
    folded = fold(question)
    return any(phrase in folded for phrase in AUDIT_PHRASES)


def system_prompt(max_tool_calls: int) -> str:
    """The system prompt with the tool limit of the settings."""
    return SYSTEM_PROMPT.format(max_tool_calls=max_tool_calls, gap_answer=GAP_ANSWER)


def plan_prompt(max_checks: int) -> str:
    """System prompt of the planning call of the audit flow."""
    return PLAN_SYSTEM_PROMPT.format(max_checks=max_checks)
