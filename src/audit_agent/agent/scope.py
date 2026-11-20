"""Scope of the current question and repair of tool arguments (ADR-0019, ISS-114).

The smoke test run-023 showed that ``qwen2.5:7b`` fills the utility arguments badly: "Heizstrom"
became ``district_heating`` (Fernwärme), ``tariff_kind=household`` was set for water, and
``"household,heating"`` for "Licht- und Heizstrom". The model chooses the tool; the code repairs
arguments that contradict the question or the schema before validation. Every repair is noted in
the observation, so the log shows it.
"""

from __future__ import annotations

import re
from contextvars import ContextVar
from typing import Any

from audit_agent.retrieval.search import fold

CURRENT_QUESTION: ContextVar[str] = ContextVar("current_question", default="")
"""Question (with the history of the chat) of the running agent; set by ``AgentLoop.run``."""
REPAIR_NOTES: ContextVar[list[str] | None] = ContextVar("repair_notes", default=None)
"""Repairs of the current tool call; the loop reads and resets them around every call."""

_UTILITY_WORDS = (
    ("heizstrom", "electricity", "heating"),
    ("nachtspeicher", "electricity", "heating"),
    ("lichtstrom", "electricity", "household"),
    ("haushaltsstrom", "electricity", "household"),
    ("strom", "electricity", None),
    ("erdgas", "gas", None),
    ("gas", "gas", None),
    ("wasser", "water", None),
    ("betriebskosten", "service_charges", None),
    ("nebenkosten", "service_charges", None),
)
_UTILITY_VALUES = {
    "strom": "electricity",
    "electricity": "electricity",
    "gas": "gas",
    "wasser": "water",
    "water": "water",
    "nebenkosten": "service_charges",
    "betriebskosten": "service_charges",
    "service_charges": "service_charges",
    "district_heating": "district_heating",
    "fernwaerme": "district_heating",
}


def question_scope(question: str) -> tuple[set[str], set[str], set[int]]:
    """Utilities, tariff kinds and years the question names (folded keyword match)."""
    folded = fold(question)
    utilities: set[str] = set()
    tariffs: set[str] = set()
    for word, utility, tariff in _UTILITY_WORDS:
        if word in folded:
            utilities.add(utility)
            if tariff:
                tariffs.add(tariff)
    if "licht- und heiz" in folded or "heiz- und licht" in folded:
        tariffs |= {"household", "heating"}
    if "fernwaerme" in folded:
        utilities.add("district_heating")
    is_view = any(w in folded for w in ("grafik", "diagramm", "uebersicht", "tabelle", "vergleich"))
    if "electricity" in utilities and not tariffs and not is_view and "alle" not in folded:
        tariffs.add("household")  # plain "Strom" means the household supply (ADR-0020)
    years = {int(y) for y in re.findall(r"\b(20\d{2})\b", question)}
    return utilities, tariffs, years


def _tariff(value: Any) -> str | None:
    """``heating``/``household`` or ``None`` for anything else (lists, "both", "")."""
    if isinstance(value, list):
        value = ",".join(str(v) for v in value)
    text = fold(str(value or ""))
    heating = any(w in text for w in ("heat", "heiz", "nacht"))
    household = any(w in text for w in ("house", "haush", "licht"))
    if heating and not household:
        return "heating"
    if household and not heating:
        return "household"
    return None


def repair_utility_arguments(
    data: Any, *, needs_utility: bool = False, needs_year: bool = False
) -> Any:
    """Make ``utility_type``/``tariff_kind`` (and ``year``) consistent with each other and the
    question. Returns the data unchanged if it is not a mapping."""
    if not isinstance(data, dict):
        return data
    data = dict(data)
    notes: list[str] = []
    utilities, tariffs, years = question_scope(CURRENT_QUESTION.get())
    raw_utility = data.get("utility_type")
    utility = _UTILITY_VALUES.get(fold(str(raw_utility))) if raw_utility else None
    tariff = _tariff(data.get("tariff_kind")) if data.get("tariff_kind") else None
    if data.get("tariff_kind") and tariff is None:
        notes.append("tariff_kind entfernt (beide Stromarten)")
    if utility == "district_heating" and ("heating" in tariffs or tariff == "heating"):
        utility, tariff = "electricity", "heating"
        notes.append("Heizstrom ist Sparte electricity mit tariff_kind heating, nicht Fernwärme")
    if tariff is not None and utility not in (None, "electricity"):
        notes.append(f"tariff_kind gilt nur für Strom, bei {utility} entfernt")
        tariff = None
    if tariff is not None and utility is None:
        utility = "electricity"
    if utility is None and needs_utility and len(utilities - {"district_heating"}) == 1:
        utility = next(iter(utilities - {"district_heating"}))
        notes.append(f"utility_type aus der Frage ergänzt: {utility}")
    if (
        utility == "electricity"
        and tariff is None
        and len(tariffs) == 1
        and not data.get("tariff_kind")
    ):
        tariff = next(iter(tariffs))
        notes.append(f"tariff_kind aus der Frage ergänzt: {tariff}")
    since = re.search(r"\bseit (20\d{2})\b", CURRENT_QUESTION.get())
    if since and data.get("to_year") and int(str(data["to_year"])) <= int(since.group(1)):
        data["to_year"] = None
        notes.append(f"„seit {since.group(1)}“: Endjahr entfernt")
    if needs_year and not data.get("year") and len(years) == 1:
        data["year"] = next(iter(years))
        notes.append(f"Jahr aus der Frage ergänzt: {data['year']}")
    data["utility_type"] = utility
    data["tariff_kind"] = tariff
    collected = REPAIR_NOTES.get()
    if notes and collected is not None:
        collected.extend(notes)
    return data


ALWAYS_OFFERED = frozenset({"plan", "list_documents", "calculate"})


def route_tools(question: str, context: str) -> frozenset[str]:
    """Tools offered for this question (ADR-0020): fewer schemas mean less prefill and fewer
    wrong picks. The model still chooses among them and may call any tool it knows."""
    from audit_agent.agent.prompts import is_audit_question, wants_chart, wants_overview

    if wants_chart(context):
        return ALWAYS_OFFERED | {"make_chart", "get_facts"}
    if wants_overview(question):
        return ALWAYS_OFFERED | {"make_overview", "make_chart", "get_facts"}
    if is_audit_question(question):
        return ALWAYS_OFFERED | {"check_bill", "get_facts", "search"}
    return ALWAYS_OFFERED | {"get_facts", "search"}
