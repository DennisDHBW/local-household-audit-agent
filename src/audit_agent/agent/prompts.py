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


# --- Agent v2 (ADR-0019) --------------------------------------------------------------------

SYSTEM_PROMPT_V2 = """\
Du bist ein Prüf-Agent für die Haushaltsunterlagen eines Nutzers: Strom (Lichtstrom und \
Heizstrom mit HT/NT), Gas, Wasser und Betriebskosten. Du arbeitest in Schritten mit \
Werkzeugen und antwortest nur anhand ihrer Ergebnisse.

Ablauf:
1. Rufe zuerst plan auf: 2 bis 5 kurze Schritte mit Werkzeug und Ziel.
2. Arbeite den Plan ab und lies jedes Ergebnis. Zeigt es Neues (eine Abweichung, eine \
fehlende Unterlage), passe das weitere Vorgehen an.
3. Antworte erst, wenn jeder Teil der Frage belegt ist. Höchstens {max_tool_calls} \
Werkzeugaufrufe.

Werkzeugwahl:
- Stimmt eine Rechnung, wurde ein Preis angewendet, passt der Verbrauch? check_bill \
(Sparte, Jahr). Übernimm Urteil, Soll, Ist und Auswirkung aus dem Ergebnis.
- Preise, Abschläge, Verbräuche, Zählerstände, Beträge, z-Zahl, Wohnfläche: get_facts mit \
Jahr; der markierte Wert gilt in diesem Jahr (fact=preise: alle Preise auf einmal).
- Klauseln, Kündigungsfristen, Laufzeiten und alles Übrige: search.
- Übersicht oder Tabelle gewünscht: make_overview. Grafik, Diagramm oder Verlauf gewünscht: \
make_chart.
- Ob es eine Unterlage gibt: list_documents. Jede Rechnung: calculate.
- Strom: Lichtstrom oder Haushaltsstrom = tariff_kind household, Heizstrom (Nachtspeicher, \
HT/NT) = tariff_kind heating.

Antwort: Deutsch, kurz, Preise brutto. Belege jede Zahl mit der Nummer aus den Ergebnissen, \
z. B. [2]. Prüffragen: zuerst das Urteil (stimmt / stimmt nicht), dann Soll, Ist, \
Unterschied und Auswirkung in EUR. Übersicht oder Grafik: sage in zwei Sätzen, was sie \
zeigt; sie wird automatisch angehängt. Findest du nichts, schreibe "{gap_answer}" und rate \
nicht.\
"""

CHECK_BEFORE_ANSWER_MESSAGE = (
    "Selbstprüfung: Das ist eine Prüffrage. Prüfe die Rechnung zuerst mit check_bill (Sparte, "
    "Jahr, bei Strom tariff_kind) und übernimm Urteil, Soll, Ist und Auswirkung aus dem Ergebnis."
)
CHART_BEFORE_ANSWER_MESSAGE = (
    "Selbstprüfung: Die Frage verlangt eine Grafik. Erstelle sie mit make_chart (topic, Sparte, "
    "Jahre) und beschreibe sie dann kurz."
)
OVERVIEW_BEFORE_ANSWER_MESSAGE = (
    "Selbstprüfung: Die Frage verlangt eine Übersicht. Erstelle sie mit make_overview (topic, "
    "Sparte, Jahre) und fasse sie dann kurz zusammen."
)
NUMBERS_BEFORE_ANSWER_MESSAGE = (
    "Selbstprüfung: Diese Zahlen deiner Antwort stehen in keinem Werkzeugergebnis: {numbers}. "
    "Belege sie mit einem Werkzeug, rechne sie mit calculate oder lass sie weg. Antworte "
    "sonst unverändert."
)

CHART_PHRASES = ("grafik", "diagramm", "chart", "visualis", "schaubild", "plot")
OVERVIEW_PHRASES = ("uebersicht", "tabelle", "aufstellung", "auflistung", "gegenueberstell")
_NUMBER = re.compile(r"(?<![\d.,])-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|(?<![\d.,])-?\d+(?:,\d+)?")
_DATE = re.compile(r"\d{1,2}\.\d{1,2}\.\d{2,4}")
_DOT_DECIMAL = re.compile(r"(?<![\d.,])(\d+)\.(\d{1,2})(?![\d.,])")
"""``24.10`` (English decimal point, run-025 H1); German thousands always have three digits."""


def system_prompt_v2(max_tool_calls: int) -> str:
    return SYSTEM_PROMPT_V2.format(max_tool_calls=max_tool_calls, gap_answer=GAP_ANSWER)


def wants_chart(question: str) -> bool:
    return any(phrase in fold(question) for phrase in CHART_PHRASES)


def wants_overview(question: str) -> bool:
    return any(phrase in fold(question) for phrase in OVERVIEW_PHRASES) and not wants_chart(
        question
    )


def _numbers(text: str) -> set[str]:
    """Normalized numbers of a text: ``1.234,50`` -> ``1234.5``; dates and citations dropped."""
    text = _CITATION.sub(" ", _DATE.sub(" ", text))
    text = _DOT_DECIMAL.sub(r"\1,\2", text)
    values = set()
    for token in _NUMBER.findall(text):
        plain = token.replace(".", "").replace(",", ".")
        try:
            value = float(plain)
        except ValueError:
            continue
        values.add(f"{value:.4f}".rstrip("0").rstrip("."))
    return values


def unsupported_numbers(answer: str, sources: list[str]) -> list[str]:
    """Numbers of the answer that appear in no tool result and not in the question.

    Years, counts up to 12 and percentages of the question are ignored. A value also counts
    as supported if it appears with a factor of 100 (ct and EUR).
    """
    known: set[str] = set()
    for text in sources:
        known |= _numbers(text)
    extended = set(known)
    for value in known:
        number = float(value)
        for scaled in (number * 100, number / 100, -number):
            extended.add(f"{scaled:.4f}".rstrip("0").rstrip("."))
    missing = []
    for value in sorted(_numbers(answer), key=float):
        number = float(value)
        if value in extended or (
            number.is_integer() and (abs(number) <= 12 or 1990 <= number <= 2100)
        ):
            continue
        missing.append(value.replace(".", ","))
    return missing


RETRY_BEFORE_GAP_MESSAGE_V2 = (
    "Bevor du sagst, dass Angaben fehlen: Prüfe mit list_documents, welche Unterlagen es gibt "
    "(Heizstrom und Lichtstrom sind Sparte electricity), und suche mit search im Volltext. "
    "Verbräuche früherer Jahre stehen oft nur im Vergleichsdiagramm einer Rechnung."
)
STEP_TALK_MESSAGE = (
    "Du hast nur Schritte angekündigt. Führe den nächsten Schritt jetzt mit einem "
    "Werkzeugaufruf aus oder beantworte die Frage, wenn die Ergebnisse reichen."
)
EMPTY_ANSWER_MESSAGE = (
    "Deine Antwort war leer. Beantworte jetzt die Frage mit den Ergebnissen oben: Deutsch, "
    "kurz, jede Zahl mit Treffernummer. Fehlt ein Beleg, sage das."
)
LANGUAGE_MESSAGE = (
    "Selbstprüfung: Antworte auf Deutsch, Zahlen im deutschen Format (z. B. 24,10 ct/kWh), "
    "und sonst unverändert."
)

_STEP_START = re.compile(
    r"^(?:plan\b|schritt\b|naechste[rnms]? schritt|zum naechsten schritt|zur weiteren pruefung|"
    r"weitere schritte|zurueck zum plan|zur ueberpruefung gehe ich|zur verbesserung|"
    r"lass uns|lassen sie uns|ich werde|ich fuehre|wir koennten|wir werden|"
    r"now,? i will|let'?s|to continue|next step)"
)
_TOOL_NAME = re.compile(
    r"\b(?:check_bill|get_facts|make_overview|make_chart|list_documents|calculate|search|plan)\b"
)
_LIST_ITEM = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_LEADING_CITATION = re.compile(r"^\s*\[\d+(?:\s*[,;]\s*\d+)*\]")


def _is_step_paragraph(paragraph: str) -> bool:
    """A paragraph that announces work instead of answering (run-025: 9 of 21 answers).

    Either it starts like "Plan:", "Nächster Schritt:", "Lass uns …", "Now, I will …", its
    first line ends with ":" and names a "Schritt", or it is a list whose items name tools.
    """
    lines = [line for line in paragraph.splitlines() if line.strip()]
    if not lines:
        return False
    if "argumente angepasst" in fold(paragraph):
        return True  # the model repeated a repair note of a tool result (run-025 N1)
    first = fold(lines[0]).strip().lstrip("*#>-• ").replace("*", "").strip()
    if _STEP_START.match(first) or (first.endswith(":") and "schritt" in first):
        return True
    items = [line for line in lines if _LIST_ITEM.match(line)]
    return (
        len(items) == len(lines)
        and any(_TOOL_NAME.search(line) for line in items)
        and not any(has_citation(line) and not _TOOL_NAME.search(line) for line in items)
    )


def strip_step_talk(answer: str) -> str:
    """The answer without announced steps and plans (ISS-117).

    ``qwen2.5:7b`` often wrote its plan as text ("Plan: 1. check_bill …", "Nächster Schritt:")
    instead of calling a tool; the loop took that text as the answer. Whole paragraphs of this
    kind are removed, and so are trailing sentences such as "Lassen Sie uns …" after a real
    first sentence. An answer that consists only of such talk becomes empty.
    """
    kept: list[str] = []
    for paragraph in re.split(r"\n\s*\n", answer.strip()):
        if _is_step_paragraph(paragraph):
            continue
        sentences = _SENTENCE_END.split(paragraph.strip())
        for index, sentence in enumerate(sentences[1:], start=1):
            if _STEP_START.match(fold(sentence).strip()):
                paragraph = " ".join(sentences[:index])
                break
        kept.append(paragraph.strip())
    return "\n\n".join(p for p in kept if p).strip()


_ENGLISH = frozenset(
    ("the", "is", "are", "based", "provided", "following", "these", "this", "with", "of", "to")
    + ("for", "and", "price", "prices", "working", "basic", "valid", "according", "will", "step")
)


def is_english(answer: str) -> bool:
    """True if the answer is mostly English (run-025 S2, H1; the prompt asks for German)."""
    words = re.findall(r"[a-z']+", answer.lower())
    hits = sum(1 for word in words if word in _ENGLISH)
    return hits >= 4 and hits >= 0.15 * len(words)


def needs_citation(answer: str) -> bool:
    """True if the answer has a figure that needs a hit number (years and counts up to 12 do
    not; run-025 H3: a year alone made the model invent the numbers [15] to [18])."""
    for value in _numbers(answer):
        number = float(value)
        if number.is_integer() and (abs(number) <= 12 or 1990 <= number <= 2100):
            continue
        return True
    return False


def drop_trailing_gap(answer: str) -> str:
    """Remove a "not in the documents" sentence that the model appended to a real answer.

    run-023 V1: a correct answer with figures and citations ended with the gap sentence, which
    made it count as a gap answer. Only removed if the rest cites a source.
    """
    if GAP_ANSWER not in answer:
        return answer
    rest = answer.replace(GAP_ANSWER, "").strip()
    return rest if rest and _has_inline_citation(rest) else answer


def _has_inline_citation(text: str) -> bool:
    """A hit number behind text on the same line ("74 m³ [1]"), not a footnote line that only
    starts with one ("[1] Hinweis: …", run-025 N1)."""
    return any(_CITATION.search(_LEADING_CITATION.sub("", line)) for line in text.splitlines())


PLAN_STEP_MISSING_MESSAGE = (
    "Selbstprüfung: Dein Plan sah noch {tools} vor. Führe den Schritt aus oder antworte, "
    "wenn er nicht mehr nötig ist, unverändert."
)

VERDICT_MISMATCH_MESSAGE = (
    "Selbstprüfung: Dein Urteil widerspricht dem Ergebnis von check_bill ({result}). Übernimm "
    "Urteil, Soll, Ist und Auswirkung aus der Kurzfassung von check_bill."
)
_NEGATIVE = (
    "stimmt nicht",
    "nicht korrekt",
    "nicht richtig",
    "passt nicht",
    "nein",
    "abweich",
    "fehler",
    "falsch",
    "zu viel",
    "zu wenig",
)
_POSITIVE = ("stimmt", "korrekt", "richtig", "passt", "ja", "in ordnung")


def answer_says_correct(answer: str) -> bool | None:
    """Verdict of the first sentence: True (correct), False (wrong) or None (no verdict)."""
    first = fold(re.split(r"(?<=[.!?])\s", answer.strip(), maxsplit=1)[0]) if answer else ""
    if any(word in first for word in _NEGATIVE):
        return False
    words = set(re.findall(r"[a-z]+", first))
    if any((w in words) if " " not in w else (w in first) for w in _POSITIVE):
        return True
    return None
