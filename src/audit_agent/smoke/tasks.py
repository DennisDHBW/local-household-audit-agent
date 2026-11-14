"""Fixed inputs of the smoke test: tool schemas, tool-calling tasks and prompts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

UTILITY_TYPES = ["electricity", "gas", "district_heating", "water", "service_charges", "rent"]
DOC_TYPES = ["contract", "terms", "price_adjustment", "bill", "notice", "policy"]

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Search the text of household documents (contracts, terms, letters). "
                "Use it for clauses, notice periods and price announcements."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query in German."},
                    "utility_type": {"type": "string", "enum": UTILITY_TYPES},
                    "doc_type": {"type": "string", "enum": DOC_TYPES},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tables",
            "description": (
                "Search table rows of bills and meter readings. "
                "Use it for prices, consumption values and cost items."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query in German."},
                    "utility_type": {"type": "string", "enum": UTILITY_TYPES},
                    "doc_type": {"type": "string", "enum": DOC_TYPES},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate an arithmetic expression, e.g. '3100 * (0.395 - 0.382)'.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]

TOOL_SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Haushaltsdokumente (Strom, Gas, Wasser, Nebenkosten) prüft. "
    "Wähle für jede Frage genau ein passendes Werkzeug und rufe es auf. "
    "Antworte nicht direkt, sondern nutze immer ein Werkzeug."
)


@dataclass(frozen=True)
class ToolTask:
    """One tool-calling task with the tool and (partial) arguments a good model should choose."""

    task_id: str
    prompt: str
    expected_tool: str
    expected_arguments: dict[str, str] = field(default_factory=dict)


TOOL_TASKS: tuple[ToolTask, ...] = (
    ToolTask(
        "T1-clause",
        "Welche Kündigungsfrist gilt laut Gasliefervertrag?",
        "search_documents",
        {"query": "*", "utility_type": "gas"},
    ),
    ToolTask(
        "T2-table",
        "Wie hoch ist der Arbeitspreis laut Stromvertrag?",
        "search_tables",
        {"query": "*", "utility_type": "electricity"},
    ),
    ToolTask(
        "T3-calc",
        "Berechne mir bitte 3100 * (0.395 - 0.382).",
        "calculate",
        {"expression": "3100"},
    ),
    ToolTask(
        "T4-table-water",
        "Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?",
        "search_tables",
        {"query": "*", "utility_type": "water"},
    ),
    ToolTask(
        "T5-calc-percent",
        "Wie viel Prozent sind 1339 EUR von 1379,30 EUR? Rechne es aus.",
        "calculate",
        {"expression": "1339"},
    ),
)

SPEED_PARAGRAPH = (
    "Die Jahresrechnung Strom enthält den Zeitraum der Abrechnung, die Zählerstände zu Beginn "
    "und Ende, den Verbrauch in Kilowattstunden, den Arbeitspreis in Cent je Kilowattstunde, "
    "den monatlichen Grundpreis, die bereits gezahlten Abschläge und am Ende den Betrag, der "
    "nachzuzahlen ist oder als Guthaben erstattet wird. "
)
SPEED_INSTRUCTION = "Fasse den Text in genau einem Satz zusammen."


def build_speed_prompt(repetitions: int = 6) -> str:
    """A prompt of a few hundred tokens so that prefill speed is measurable."""
    return SPEED_PARAGRAPH * repetitions + SPEED_INSTRUCTION


PREFIX_SYSTEM_PROMPT = (
    "Du bist ein sorgfältiger Prüfer für Haushaltsdokumente. " + SPEED_PARAGRAPH * 5
)
PREFIX_QUESTIONS = ("Nenne einen Punkt, den du prüfst.", "Nenne einen anderen Punkt.")

EMBEDDING_QUERY = "Wie hoch ist der Arbeitspreis für Strom?"
EMBEDDING_RELEVANT = "[Strom | Vertrag | Vertragsbestätigung] Arbeitspreis 34,80 ct/kWh brutto"
EMBEDDING_IRRELEVANT = "[Versicherung | Vertrag | Hausrat] Die Hausratversicherung deckt Feuer ab."

VISION_PROMPT = (
    "Beschreibe das Diagramm. Nenne jedes Jahr mit seinem Zahlenwert und der Einheit, "
    "zum Beispiel '2022: 1.000 kWh'."
)
VISION_DOCUMENT = "01_electricity_suedvolt/04_Strom_Jahresabrechnung_2024_SuedVolt.pdf"
VISION_PAGE_INDEX = 1  # page 2, zero-based
VISION_EXPECTED_VALUES = [3480.0, 3390.0]  # electricity consumption 2022 and 2023 (question S4)
