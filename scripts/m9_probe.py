"""Feasibility probe for agent v3 (M9-0, ADR-0022).

Per candidate model the probe checks whether Ollama keeps a JSON schema (``format``) with
thinking switched off, how fast prefill and decoding are, how well a draft ``QueryFrame``
matches eight neutral questions, and whether the prompt cache carries a shared prefix from
one call to the next (ISS-128). For ``qwen2.5:7b`` two extra calls show what the model
emits when the fitting tool is not offered (ISS-126).

The ``QueryFrame`` here is a draft for the probe only; M9a defines the real one in
``src/``. The probe questions and prompt examples come from none of the test sets.

Writes ``data/eval/<run-id>/m9-probe.json`` (all calls) and ``m9-probe.md`` (summary).
Unloads every loaded model first and each candidate after its calls. Needs Ollama and the
pulled models; missing models are skipped. About 30-45 minutes on the CPU.

    uv run python scripts/m9_probe.py --run-id run-029-probe
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

import httpx
from ollama import Client, ResponseError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from audit_agent.agent.fact_tools import FactName
from audit_agent.config import Settings
from audit_agent.corpus.models import DocType, TariffKind, UtilityType

CANDIDATES = ("qwen2.5:7b", "qwen3:8b", "qwen3.5:4b", "granite4:tiny-h")
ISS126_MODEL = "qwen2.5:7b"
FRAME_NUM_PREDICT = 400
"""A frame with three tasks needs about 250 tokens; more means the model ran away."""
CACHE_NUM_PREDICT = 8
"""The cache calls only measure prefill; their output is not used."""
CGROUP_MEMORY = Path("/sys/fs/cgroup/system.slice/ollama.service/memory.current")


# --- Draft schema (M9a defines the real one) ------------------------------------------


class Intent(StrEnum):
    FACT = "fact"
    CHECK = "check"
    OVERVIEW = "overview"
    CHART = "chart"
    CLAUSE = "clause"
    OTHER = "other"


class Period(StrEnum):
    YEARS = "years"
    SINCE = "since"
    LATEST = "latest"
    ALL = "all"
    NONE = "none"


class SubTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    utility: UtilityType | None
    tariff_kind: TariffKind | None
    period: Period
    years: list[int] = Field(max_length=6)
    metric: FactName | None
    doc_type: DocType | None


class QueryFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[SubTask] = Field(min_length=1, max_length=3)
    search_query: str
    is_follow_up: bool


def _task(intent: Intent, utility: UtilityType | None, period: Period, **rest: Any) -> SubTask:
    values: dict[str, Any] = {"tariff_kind": None, "years": [], "metric": None, "doc_type": None}
    values.update(rest)
    return SubTask(intent=intent, utility=utility, period=period, **values)


# --- Prompts ---------------------------------------------------------------------------

FRAME_INSTRUCTIONS = """\
Du ordnest Fragen zu Haushaltsunterlagen (Strom, Heizstrom, Gas, Wasser, Nebenkosten, \
Miete, Internet, Mobilfunk, Versicherungen) einem festen Auftragsrahmen zu. Du beantwortest \
die Frage nicht und rechnest nichts. Gib nur JSON nach dem Schema aus.

Felder je Teilaufgabe (tasks, 1 bis 3 Einträge, einer je Teilfrage):
- intent: fact = einzelne Werte nachschlagen (Preis, Abschlag, Verbrauch, Zählerstand, \
Betrag); check = prüfen, ob eine Rechnung, Abrechnung oder ein Bescheid stimmt; \
overview = Tabelle oder Aufstellung; chart = Grafik oder Diagramm; clause = Vertragstext \
(Frist, Laufzeit, Kündigung, Bedingungen, Leistungen); other = alles andere.
- utility: Sparte. electricity = Strom (Licht- und Heizstrom); gas; district_heating = \
Fernwärme; water = Wasser und Abwasser; service_charges = Nebenkosten und Betriebskosten; \
rent = Miete und Mietvertrag; telecom = Internet, Telefon, Mobilfunk; insurance = \
Versicherungen; other = eine Sparte, die keine dieser ist; null = keine Sparte genannt.
- tariff_kind: nur bei Strom. heating = Heizstrom, Nachtstrom, Speicherheizung; \
household = Haushaltsstrom, Lichtstrom; null = nicht gesagt.
- period: years = bestimmte Jahre (in years eintragen); since = ab einem Jahr bis heute \
(Startjahr in years); latest = aktueller oder neuester Stand; all = alle Jahre oder Verlauf \
ohne Jahresangabe; none = die Zeit spielt keine Rolle.
- years: Jahreszahlen, sonst leere Liste. Relative Angaben rechnest du mit dem heutigen \
Datum aus der Nachricht um.
- metric: gesuchte Größe, falls genannt: preise, arbeitspreis, grundpreis, wasserpreis, \
schmutzwassergebuehr, abschlag, verbrauch, zaehlerstand, rechnungsbetrag, z_zahl, \
wohnflaeche; sonst null.
- doc_type: nur wenn eine Dokumentart gemeint ist: contract, payment_plan, \
price_adjustment, bill, notice, handover_protocol, policy; sonst null.

Weitere Felder:
- search_query: 2 bis 6 deutsche Stichwörter für eine Volltextsuche.
- is_follow_up: true, wenn die Frage ohne die Vorfrage unvollständig ist. Fehlende Angaben \
übernimmst du dann aus dem Rahmen der Vorfrage.

Ordne auch Fragen nach Sparten genau zu, zu denen es vielleicht keine Unterlagen gibt. Ob es \
Unterlagen gibt, prüft das Programm.

Beispiele:"""


@dataclass(frozen=True)
class Example:
    question: str
    frame: QueryFrame
    previous: tuple[str, QueryFrame] | None = None


EXAMPLES = (
    Example(
        "Welcher Grundpreis gilt derzeit für Gas?",
        QueryFrame(
            tasks=[_task(Intent.FACT, UtilityType.GAS, Period.LATEST, metric=FactName.GRUNDPREIS)],
            search_query="Grundpreis Gas",
            is_follow_up=False,
        ),
    ),
    Example(
        "Kontrollier bitte die Mobilfunkrechnung vom Dezember 2025.",
        QueryFrame(
            tasks=[
                _task(
                    Intent.CHECK,
                    UtilityType.TELECOM,
                    Period.YEARS,
                    years=[2025],
                    doc_type=DocType.BILL,
                )
            ],
            search_query="Mobilfunk Rechnung Dezember 2025",
            is_follow_up=False,
        ),
    ),
    Example(
        "Stell mir die Versicherungsbeiträge in einer Tabelle zusammen.",
        QueryFrame(
            tasks=[_task(Intent.OVERVIEW, UtilityType.INSURANCE, Period.ALL)],
            search_query="Versicherung Beitrag",
            is_follow_up=False,
        ),
    ),
    Example(
        "Bis wann muss ich den Mietvertrag kündigen, wenn ich Ende Juni ausziehen will?",
        QueryFrame(
            tasks=[_task(Intent.CLAUSE, UtilityType.RENT, Period.NONE, doc_type=DocType.CONTRACT)],
            search_query="Mietvertrag Kündigungsfrist",
            is_follow_up=False,
        ),
    ),
    Example(
        "Wie viel kostet mich Heizöl im Jahr?",
        QueryFrame(
            tasks=[
                _task(
                    Intent.FACT, UtilityType.OTHER, Period.LATEST, metric=FactName.RECHNUNGSBETRAG
                )
            ],
            search_query="Heizöl Kosten",
            is_follow_up=False,
        ),
    ),
    Example(
        "Zeig mir den Stromverbrauch seit 2024 als Diagramm und nenne den aktuellen Abschlag.",
        QueryFrame(
            tasks=[
                _task(
                    Intent.CHART,
                    UtilityType.ELECTRICITY,
                    Period.SINCE,
                    years=[2024],
                    metric=FactName.VERBRAUCH,
                ),
                _task(
                    Intent.FACT, UtilityType.ELECTRICITY, Period.LATEST, metric=FactName.ABSCHLAG
                ),
            ],
            search_query="Stromverbrauch Abschlag",
            is_follow_up=False,
        ),
    ),
    Example(
        "Und der Abschlag?",
        QueryFrame(
            tasks=[
                _task(
                    Intent.FACT,
                    UtilityType.GAS,
                    Period.YEARS,
                    years=[2024],
                    metric=FactName.ABSCHLAG,
                )
            ],
            search_query="Gas Abschlag 2024",
            is_follow_up=True,
        ),
        previous=(
            "Wie hoch war der Gasverbrauch 2024?",
            QueryFrame(
                tasks=[
                    _task(
                        Intent.FACT,
                        UtilityType.GAS,
                        Period.YEARS,
                        years=[2024],
                        metric=FactName.VERBRAUCH,
                    )
                ],
                search_query="Gasverbrauch 2024",
                is_follow_up=False,
            ),
        ),
    ),
)

EXAMPLE_TODAY = "2026-11-21"
"""The examples use a fixed date so that the prompt prefix stays the same every day."""


def user_message(question: str, today: str, previous: tuple[str, QueryFrame] | None) -> str:
    """The per-question part of the prompt; everything before it is the shared prefix."""
    lines = [f"Heute: {today}"]
    if previous is not None:
        lines.append(f"Vorfrage: {previous[0]}")
        lines.append(f"Rahmen der Vorfrage: {previous[1].model_dump_json()}")
    lines.append(f"Frage: {question}")
    return "\n".join(lines)


def frame_system_prompt() -> str:
    """Instructions plus examples; the same text for every question (cache prefix)."""
    parts = [FRAME_INSTRUCTIONS]
    for example in EXAMPLES:
        parts.append(user_message(example.question, EXAMPLE_TODAY, example.previous))
        parts.append(f"JSON: {example.frame.model_dump_json()}")
    return "\n\n".join(parts)


WRITER_INSTRUCTIONS = """\
Du formulierst die Antwort auf eine Frage zu Haushaltsunterlagen. Du bekommst die Frage und \
nummerierte Belege E1, E2, ... mit Wert, Quelle und Zeitraum. Schreibe kurze deutsche Sätze. \
Jeder Satz mit einer Zahl nennt die Belege, aus denen die Zahl stammt. Erfinde keine Zahl \
und keinen Beleg. Reichen die Belege nicht, sage, was fehlt. Rechne nicht; Ergebnisse von \
Prüfungen stehen in den Belegen. Gib nur JSON nach dem Schema aus."""

CACHE_EVIDENCE = """\
E1: Grundpreis Gas 2025: 12,90 EUR/Monat brutto (Gas_Jahresabrechnung_2025, S. 1)
E2: Arbeitspreis Gas 2025: 10,40 ct/kWh brutto (Gas_Jahresabrechnung_2025, S. 1)
E3: Verbrauch Gas 2025: 9.870 kWh (Gas_Jahresabrechnung_2025, S. 1)
E4: Abschlag Gas ab Februar 2026: 98,00 EUR/Monat (Gas_Abschlagsplan_2026, S. 1)"""

CACHE_QUESTIONS = (
    "Was hat das Gas 2025 pro Kilowattstunde gekostet?",
    "Wie hoch ist der Beitrag für die Hausratversicherung 2026?",
)
"""Two questions for the stage-alternation test; they are not scored."""


def shared_system_prompt() -> str:
    """One system prompt for both stages: the stage instruction follows in the user part."""
    return (
        "Je nach Aufgabe in der Nachricht arbeitest du als Zuordner (Aufgabe: Rahmen) oder "
        "als Schreiber (Aufgabe: Antwort).\n\n## Rahmen\n"
        + frame_system_prompt()
        + "\n\n## Antwort\n"
        + WRITER_INSTRUCTIONS
    )


# --- Probe questions with gold frames ---------------------------------------------------

Gold = Mapping[str, tuple[Any, ...]]
"""Field name -> accepted values; fields that are missing are not scored."""


@dataclass(frozen=True)
class ProbeQuestion:
    id: str
    question: str
    gold_tasks: tuple[Gold, ...]
    gold_follow_up: bool = False
    previous: tuple[str, QueryFrame] | None = None


PROBE_QUESTIONS = (
    ProbeQuestion(
        "F1",
        "Was hat der Kubikmeter Trinkwasser 2025 gekostet?",
        ({"intent": ("fact",), "utility": ("water",), "period": ("years",), "years": ((2025,),)},),
    ),
    ProbeQuestion(
        "F2",
        "Hat SüdVolt bei der Stromrechnung 2024 richtig abgerechnet?",
        (
            {
                "intent": ("check",),
                "utility": ("electricity",),
                "period": ("years",),
                "years": ((2024,),),
            },
        ),
    ),
    ProbeQuestion(
        "F3",
        "Welche Abschläge zahle ich im Moment? Bitte als Tabelle.",
        ({"intent": ("overview",), "utility": (None,), "period": ("latest",)},),
    ),
    ProbeQuestion(
        "F4",
        "Mach ein Säulendiagramm vom Gasverbrauch seit 2024.",
        ({"intent": ("chart",), "utility": ("gas",), "period": ("since",), "years": ((2024,),)},),
    ),
    ProbeQuestion(
        "F5",
        "Wie lange bin ich an den Glasfaservertrag mindestens gebunden?",
        ({"intent": ("clause",), "utility": ("telecom",), "period": ("none", "latest")},),
    ),
    ProbeQuestion(
        "F6",
        "Wie viel Nachtstrom hat die Speicherheizung 2024 verbraucht?",
        (
            {
                "intent": ("fact",),
                "utility": ("electricity",),
                "tariff_kind": ("heating",),
                "period": ("years",),
                "years": ((2024,),),
            },
        ),
    ),
    ProbeQuestion(
        "F7",
        "Was war 2025 teurer: Strom oder Gas?",
        (
            {
                "intent": ("fact", "overview"),
                "utility": ("electricity",),
                "period": ("years",),
                "years": ((2025,),),
            },
            {
                "intent": ("fact", "overview"),
                "utility": ("gas",),
                "period": ("years",),
                "years": ((2025,),),
            },
        ),
    ),
    ProbeQuestion(
        "F8",
        "Und ein Jahr später?",
        (
            {
                "intent": ("fact",),
                "utility": ("water",),
                "period": ("years",),
                "years": ((2025,),),
            },
        ),
        gold_follow_up=True,
        previous=(
            "Wie hoch war der Wasserverbrauch 2024?",
            QueryFrame(
                tasks=[
                    _task(
                        Intent.FACT,
                        UtilityType.WATER,
                        Period.YEARS,
                        years=[2024],
                        metric=FactName.VERBRAUCH,
                    )
                ],
                search_query="Wasserverbrauch 2024",
                is_follow_up=False,
            ),
        ),
    ),
)


# --- Pure helpers (unit-tested) -----------------------------------------------------------


@dataclass
class FrameScore:
    matched: int = 0
    total: int = 0
    mismatches: list[str] = field(default_factory=list)

    @property
    def exact(self) -> bool:
        return self.total > 0 and self.matched == self.total


def _task_value(task: SubTask, name: str) -> Any:
    value = getattr(task, name)
    if name == "years":
        return tuple(sorted(value))
    return value.value if isinstance(value, StrEnum) else value


def _score_pair(task: SubTask | None, gold: Gold) -> tuple[int, list[str]]:
    matched = 0
    mismatches: list[str] = []
    for name, accepted in gold.items():
        value = None if task is None else _task_value(task, name)
        if value in accepted:
            matched += 1
        else:
            mismatches.append(f"{name}={value!r}")
    return matched, mismatches


def score_frame(frame: QueryFrame | None, question: ProbeQuestion) -> FrameScore:
    """Fields that match the gold frame; tasks are paired in the order that matches best.

    A missing task counts every gold field as wrong; an extra task costs one point.
    """
    score = FrameScore(total=sum(len(gold) for gold in question.gold_tasks) + 1)
    predicted: list[SubTask | None] = list(frame.tasks) if frame is not None else []
    predicted += [None] * max(0, len(question.gold_tasks) - len(predicted))
    best: tuple[int, list[str]] = (-1, [])
    for order in itertools.permutations(predicted, len(question.gold_tasks)):
        results = [
            _score_pair(task, gold) for task, gold in zip(order, question.gold_tasks, strict=True)
        ]
        matched = sum(result[0] for result in results)
        if matched > best[0]:
            best = (matched, [miss for result in results for miss in result[1]])
    score.matched, score.mismatches = best
    extra = len(frame.tasks) - len(question.gold_tasks) if frame is not None else 0
    if extra > 0:
        score.total += 1
        score.mismatches.append(f"tasks+{extra}")
    if frame is not None and frame.is_follow_up == question.gold_follow_up:
        score.matched += 1
    else:
        score.mismatches.append(f"is_follow_up={None if frame is None else frame.is_follow_up}")
    return score


def parse_frame(content: str) -> tuple[bool, QueryFrame | None, str | None]:
    """(valid JSON, frame if the schema holds, error)."""
    try:
        json.loads(content)
    except json.JSONDecodeError as error:
        return False, None, f"json: {error}"
    try:
        return True, QueryFrame.model_validate_json(content), None
    except ValidationError as error:
        return True, None, f"schema: {error.error_count()} errors, {error.errors()[0]['msg']}"


def _seconds(nanoseconds: Any) -> float | None:
    return round(nanoseconds / 1e9, 2) if isinstance(nanoseconds, int | float) else None


def call_metrics(response: Any, wall_seconds: float) -> dict[str, Any]:
    """Token counts and durations as Ollama reports them (chat and generate responses).

    ``prompt_tokens`` is the whole prompt even on a cache hit (run-028); a hit shows only in
    ``prefill_seconds``.
    """
    message = getattr(response, "message", None)
    content = getattr(message, "content", None) if message else getattr(response, "response", "")
    thinking = getattr(message, "thinking", None) if message else getattr(response, "thinking", "")
    tool_calls = getattr(message, "tool_calls", None) if message else None
    return {
        "wall_seconds": round(wall_seconds, 2),
        "load_seconds": _seconds(getattr(response, "load_duration", None)),
        "prompt_tokens": getattr(response, "prompt_eval_count", None),
        "prefill_seconds": _seconds(getattr(response, "prompt_eval_duration", None)),
        "generated_tokens": getattr(response, "eval_count", None),
        "decode_seconds": _seconds(getattr(response, "eval_duration", None)),
        "done_reason": getattr(response, "done_reason", None),
        "content": content or "",
        "thinking": thinking or "",
        "tool_calls": [
            {"name": call.function.name, "arguments": dict(call.function.arguments)}
            for call in tool_calls or []
        ],
    }


def _rate(tokens: Any, seconds: Any) -> float | None:
    if isinstance(tokens, int) and isinstance(seconds, int | float) and seconds > 0:
        return round(tokens / seconds, 1)
    return None


def _median(values: Sequence[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return round(statistics.median(present), 2) if present else None


def summarize_model(calls: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """One row of the summary table for one model."""
    frames = [call for call in calls if call["part"] in ("frame", "repeat")]
    scored = [call for call in calls if call["part"] == "frame"]
    first = frames[0] if frames else {}
    warm = [call["prefill_seconds"] for call in scored[1:]]
    repeat = next((call for call in calls if call["part"] == "repeat"), {})
    by_part = {
        part: [call for call in calls if call["part"] == part]
        for part in ("alt-separate", "alt-shared")
    }
    return {
        "calls": len(frames),
        "errors": sum(1 for call in frames if call.get("error")),
        "json_valid": sum(1 for call in frames if call.get("json_ok")),
        "schema_valid": sum(1 for call in frames if call.get("schema_ok")),
        "thinking_leaks": sum(
            1 for call in frames if call.get("thinking") or "<think>" in call.get("content", "")
        ),
        "exact_frames": sum(1 for call in scored if call.get("exact")),
        "questions": len(scored),
        "field_matches": sum(call.get("matched", 0) for call in scored),
        "field_total": sum(call.get("total", 0) for call in scored),
        "load_seconds": first.get("load_seconds"),
        "cold_prompt_tokens": first.get("prompt_tokens"),
        "cold_prefill_seconds": first.get("prefill_seconds"),
        "cold_prefill_tps": _rate(first.get("prompt_tokens"), first.get("prefill_seconds")),
        "warm_prefill_median_seconds": _median(warm),
        "repeat_prefill_seconds": repeat.get("prefill_seconds"),
        "decode_tps_median": _median(
            [_rate(call.get("generated_tokens"), call.get("decode_seconds")) for call in frames]
        ),
        "frame_wall_median_seconds": _median([call.get("wall_seconds") for call in scored]),
        "alt_separate_third_prefill_seconds": _third_prefill(by_part["alt-separate"]),
        "alt_shared_third_prefill_seconds": _third_prefill(by_part["alt-shared"]),
    }


def _third_prefill(calls: Sequence[Mapping[str, Any]]) -> float | None:
    return calls[2].get("prefill_seconds") if len(calls) >= 3 else None


def render_markdown(result: Mapping[str, Any]) -> str:
    """Short report for evaluation-log.md; the JSON keeps every call."""
    lines = [
        f"# M9-0 Machbarkeitsprobe ({result['run_id']})",
        "",
        f"Ollama {result.get('ollama_version')} · {result['started']} · "
        f"num_ctx {result['num_ctx']} · temperature 0",
        "",
        "| Modell | gültiges JSON | Schema | Thinking | Rahmen exakt | Felder | Laden s | "
        "Prefill kalt s (Tok/s) | Prefill warm s | Wiederholung s | Decode Tok/s | "
        "Rahmen s | Wechsel getrennt s | Wechsel gemeinsam s | RAM MB |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for model, entry in result["models"].items():
        if entry.get("missing"):
            lines.append(f"| {model} | nicht geladen |" + " |" * 13)
            continue
        row = entry["summary"]
        lines.append(
            f"| {model} | {row['json_valid']}/{row['calls']} | {row['schema_valid']}/{row['calls']}"
            f" | {row['thinking_leaks']} | {row['exact_frames']}/{row['questions']}"
            f" | {row['field_matches']}/{row['field_total']} | {row['load_seconds']}"
            f" | {row['cold_prefill_seconds']} ({row['cold_prefill_tps']})"
            f" | {row['warm_prefill_median_seconds']} | {row['repeat_prefill_seconds']}"
            f" | {row['decode_tps_median']} | {row['frame_wall_median_seconds']}"
            f" | {row['alt_separate_third_prefill_seconds']}"
            f" | {row['alt_shared_third_prefill_seconds']} | {entry.get('memory_mb')} |"
        )
    lines += [
        "",
        "Prefill warm: Median der Fragen F2–F8 (gleicher Präfix). Wiederholung: F1 ein zweites "
        "Mal, identischer Prompt. Wechsel: dritter Aufruf der Folge Rahmen → Antwort → Rahmen, "
        "mit getrennten oder einem gemeinsamen Systemprompt.",
    ]
    mismatches = [
        f"- {model} {call['question_id']}: {', '.join(call['mismatches']) or call.get('error')}"
        for model, entry in result["models"].items()
        for call in entry.get("calls", [])
        if call["part"] == "frame" and not call.get("exact")
    ]
    if mismatches:
        lines += ["", "## Abweichungen vom Gold-Rahmen", "", *mismatches]
    iss126 = result.get("iss126")
    if iss126:
        lines += [
            "",
            "## ISS-126",
            "",
            f"Angeboten: {', '.join(iss126.get('offered_tools', []))}",
            "",
        ]
        for name, case in iss126.get("cases", {}).items():
            for kind, call in case.items():
                lines.append(
                    f"- {name} / {kind}: {call.get('prompt_tokens')} Prompt-Token, "
                    f"{call.get('generated_tokens')} Token, done_reason {call.get('done_reason')}, "
                    f"Werkzeugaufrufe {call.get('tool_calls')}, "
                    f"Text {call.get('content', '')[:300]!r}, Fehler {call.get('error')}"
                )
    return "\n".join(lines) + "\n"


QWEN25_TOOLS_INTRO = """

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>"""
QWEN25_TOOLS_OUTRO = """
</tools>

For each function call, return a json object with function name and arguments within \
<tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>"""


def _compact(value: Any, sort_keys: bool = False) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=sort_keys)


def render_qwen25_prompt(
    system: str, specs: Sequence[Mapping[str, Any]], messages: Sequence[Mapping[str, Any]]
) -> str:
    """The chat prompt as Qwen2.5's Ollama template renders it (reconstructed, ISS-126).

    Go writes the tool schemas as compact JSON with sorted property names; this rendering
    keeps Python's key order, so the token count differs slightly. The real template is
    saved next to the result.
    """
    tools = "".join(
        f'\n{{"type": "function", "function": {_compact(spec["function"])}}}' for spec in specs
    )
    parts = [
        f"<|im_start|>system\n{system}{QWEN25_TOOLS_INTRO}{tools}{QWEN25_TOOLS_OUTRO}<|im_end|>\n"
    ]
    for message in messages:
        if message["role"] == "user":
            parts.append(f"<|im_start|>user\n{message['content']}<|im_end|>\n")
        elif message["role"] == "assistant":
            calls = "".join(
                f'{{"name": "{call["function"]["name"]}", "arguments": '
                f"{_compact(call['function']['arguments'], sort_keys=True)}}}\n"
                for call in message.get("tool_calls", [])
            )
            parts.append(f"<|im_start|>assistant\n<tool_call>\n{calls}</tool_call><|im_end|>\n")
        elif message["role"] == "tool":
            parts.append(
                f"<|im_start|>user\n<tool_response>\n{message['content']}\n</tool_response><|im_end|>\n"
            )
    parts.append("<|im_start|>assistant\n")
    return "".join(parts)


# --- Calls against Ollama -------------------------------------------------------------


class ProbeClient(Protocol):
    def chat(self, **kwargs: Any) -> Any: ...

    def generate(self, **kwargs: Any) -> Any: ...


CALL_ERRORS = (ResponseError, httpx.TransportError, ConnectionError)


def _timed(call: Any, **kwargs: Any) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = call(**kwargs)
    except CALL_ERRORS as error:
        return {"error": f"{type(error).__name__}: {error}", "content": "", "thinking": ""}
    return call_metrics(response, time.perf_counter() - started)


def _log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def probe_model(
    client: ProbeClient,
    model: str,
    options: Mapping[str, Any],
    keep_alive: str,
    supports_thinking: bool,
    today: str,
) -> list[dict[str, Any]]:
    """Frame calls (F1, F1 again, F2-F8), then the two stage-alternation sequences."""
    extra: dict[str, Any] = {"think": False} if supports_thinking else {}
    schema = QueryFrame.model_json_schema()
    frame_system = frame_system_prompt()
    calls: list[dict[str, Any]] = []
    order = [(PROBE_QUESTIONS[0], "frame"), (PROBE_QUESTIONS[0], "repeat")]
    order += [(question, "frame") for question in PROBE_QUESTIONS[1:]]
    for question, part in order:
        messages = [
            {"role": "system", "content": frame_system},
            {"role": "user", "content": user_message(question.question, today, question.previous)},
        ]
        call = _timed(
            client.chat,
            model=model,
            messages=messages,
            format=schema,
            options={**options, "num_predict": FRAME_NUM_PREDICT},
            keep_alive=keep_alive,
            **extra,
        )
        call.update({"part": part, "question_id": question.id})
        if not call.get("error"):
            json_ok, frame, error = parse_frame(call["content"])
            score = score_frame(frame, question)
            call.update(
                {
                    "json_ok": json_ok,
                    "schema_ok": frame is not None,
                    "parse_error": error,
                    "matched": score.matched,
                    "total": score.total,
                    "exact": score.exact,
                    "mismatches": score.mismatches,
                }
            )
        _log(
            f"  {model} {question.id} {part}: {call.get('wall_seconds')} s, "
            f"prefill {call.get('prefill_seconds')} s, exact {call.get('exact')}, "
            f"{call.get('error') or call.get('parse_error') or ''}"
        )
        calls.append(call)
    calls += _alternation(client, model, options, keep_alive, extra, today)
    return calls


def _alternation(
    client: ProbeClient,
    model: str,
    options: Mapping[str, Any],
    keep_alive: str,
    extra: Mapping[str, Any],
    today: str,
) -> list[dict[str, Any]]:
    """Frame -> answer -> frame with separate system prompts, then with one shared prompt."""
    first, second = CACHE_QUESTIONS
    writer_user = f"Frage: {first}\nBelege:\n{CACHE_EVIDENCE}"
    shared = shared_system_prompt()
    sequences = {
        "alt-separate": [
            (frame_system_prompt(), user_message(first, today, None)),
            (WRITER_INSTRUCTIONS, writer_user),
            (frame_system_prompt(), user_message(second, today, None)),
        ],
        "alt-shared": [
            (shared, "Aufgabe: Rahmen\n" + user_message(first, today, None)),
            (shared, "Aufgabe: Antwort\n" + writer_user),
            (shared, "Aufgabe: Rahmen\n" + user_message(second, today, None)),
        ],
    }
    calls: list[dict[str, Any]] = []
    for part, steps in sequences.items():
        for index, (system, user) in enumerate(steps):
            call = _timed(
                client.chat,
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                options={**options, "num_predict": CACHE_NUM_PREDICT},
                keep_alive=keep_alive,
                **extra,
            )
            call.update({"part": part, "question_id": f"C{index + 1}"})
            _log(f"  {model} {part} {index + 1}: prefill {call.get('prefill_seconds')} s")
            calls.append(call)
    return calls


ISS126_QUESTION = "Wurde die Heizstromrechnung 2024 richtig berechnet?"
"""Same bill as the development question H3; not a held-out question."""


FALLBACK_PLAN = ["check_bill Heizstrom 2024", "get_facts verbrauch Heizstrom 2024"]


def plan_observation(steps: Sequence[str]) -> str:
    """The text of P2's plan tool (``FactTools.plan``), so the replay matches run-028."""
    numbered = "; ".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    return f"Plan notiert: {numbered}. Führe jetzt Schritt 1 aus."


def after_plan_messages(question: str, steps: Sequence[str]) -> list[dict[str, Any]]:
    """P2's second call: the plan was called and noted, now step 1 (``check_bill``) is due.

    In run-028 (T3, T5, T6) exactly this call came back empty (ISS-126).
    """
    return [
        {"role": "user", "content": question},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "plan", "arguments": {"steps": list(steps)}}}],
        },
        {"role": "tool", "content": plan_observation(steps)},
    ]


def probe_iss126(client: Client, settings: Settings, options: Mapping[str, Any]) -> dict[str, Any]:
    """P2's first and second call with the default tool set, each also sent raw (ISS-126).

    The raw calls show the text the model writes before Ollama parses tool calls out of it.
    Order: both chat calls, then both raw calls, so each second call reuses the cache.
    """
    from audit_agent.agent.prompts import system_prompt_v2
    from audit_agent.agent.scope import route_tools
    from audit_agent.agent.tools import ToolBox
    from audit_agent.corpus import load_document_catalog
    from audit_agent.retrieval import Retriever, get_collection, open_vector_client

    catalog = load_document_catalog(settings.documents_file)
    retriever = Retriever(settings, client, get_collection(settings, open_vector_client(settings)))
    tools = ToolBox(settings, retriever, catalog).tools()
    offered = route_tools(ISS126_QUESTION, ISS126_QUESTION)
    specs = [tool.spec() for name, tool in tools.items() if name in offered]
    system = system_prompt_v2(settings.agent.max_tool_calls)
    common = {
        "model": ISS126_MODEL,
        "options": {**options, "num_predict": settings.agent.num_predict},
        "keep_alive": settings.agent.keep_alive,
    }
    system_message = {"role": "system", "content": system}
    first = [{"role": "user", "content": ISS126_QUESTION}]
    cases: dict[str, dict[str, Any]] = {"first": {}, "after_plan": {}}
    cases["first"]["chat"] = _timed(
        client.chat, messages=[system_message, *first], tools=specs, **common
    )
    planned = [
        call for call in cases["first"]["chat"].get("tool_calls", []) if call["name"] == "plan"
    ]
    steps = (
        [str(step) for step in planned[0]["arguments"].get("steps", [])]
        if planned
        else FALLBACK_PLAN
    )
    second = after_plan_messages(ISS126_QUESTION, steps)
    cases["after_plan"]["chat"] = _timed(
        client.chat, messages=[system_message, *second], tools=specs, **common
    )
    for name, messages in (("first", first), ("after_plan", second)):
        cases[name]["raw"] = _timed(
            client.generate,
            prompt=render_qwen25_prompt(system, specs, messages),
            raw=True,
            **common,
        )
    for name, case in cases.items():
        for kind, call in case.items():
            _log(
                f"  ISS-126 {name} {kind}: {call.get('generated_tokens')} Token, "
                f"{call.get('tool_calls')}, {call.get('content', '')[:160]!r}"
            )
    try:
        template = client.show(ISS126_MODEL).template
    except CALL_ERRORS as error:
        template = f"error: {error}"
    return {
        "question": ISS126_QUESTION,
        "offered_tools": sorted(offered),
        "plan_steps": steps,
        "cases": cases,
        "template": template,
    }


# --- Orchestration --------------------------------------------------------------------


def _memory_mb() -> int | None:
    try:
        return int(CGROUP_MEMORY.read_text().strip()) // 2**20
    except (OSError, ValueError):
        return None


def _unload(client: Client, models: Sequence[str]) -> None:
    for model in models:
        try:
            client.generate(model=model, prompt="", keep_alive=0)
        except CALL_ERRORS as error:
            _log(f"could not unload {model}: {error}")


def _loaded(client: Client) -> list[dict[str, Any]]:
    return [model.model_dump(mode="json") for model in client.ps().models]


def _ollama_version(host: str) -> str | None:
    try:
        return httpx.get(f"{host}/api/version", timeout=10).json().get("version")
    except (httpx.HTTPError, ValueError):
        return None


def _write(out_dir: Path, result: Mapping[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "m9-probe.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    (out_dir / "m9-probe.md").write_text(render_markdown(result), encoding="utf-8")


def _rerun_iss126(
    client: Client, settings: Settings, options: Mapping[str, Any], out_dir: Path
) -> int:
    """Replace the ISS-126 part of an existing result (the model calls stay as they were)."""
    path = out_dir / "m9-probe.json"
    if not path.exists():
        _log(f"{path} fehlt: erst den ganzen Lauf mit dieser --run-id starten")
        return 1
    result = json.loads(path.read_text(encoding="utf-8"))
    result["iss126"] = probe_iss126(client, settings, options)
    result["iss126"]["started"] = time.strftime("%Y-%m-%d %H:%M")
    _unload(client, [ISS126_MODEL])
    _write(out_dir, result)
    _log(f"probe: {out_dir / 'm9-probe.md'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--models", nargs="+", default=list(CANDIDATES))
    parser.add_argument("--skip-iss126", action="store_true")
    parser.add_argument(
        "--only-iss126",
        action="store_true",
        help="only the ISS-126 calls; updates the existing result of --run-id",
    )
    args = parser.parse_args()
    settings = Settings.from_env()
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)
    options = {"num_ctx": settings.num_ctx, "temperature": 0.0}
    out_dir = settings.eval_dir / args.run_id
    today = date.today().isoformat()

    try:
        available = {model.model for model in client.list().models}
    except CALL_ERRORS as error:
        _log(f"Ollama nicht erreichbar ({settings.ollama_host}): {error}")
        return 1
    _unload(client, [model["model"] for model in _loaded(client)])
    if args.only_iss126:
        return _rerun_iss126(client, settings, options, out_dir)
    result: dict[str, Any] = {
        "run_id": args.run_id,
        "started": time.strftime("%Y-%m-%d %H:%M"),
        "ollama_version": _ollama_version(settings.ollama_host),
        "num_ctx": settings.num_ctx,
        "frame_prompt_chars": len(frame_system_prompt()),
        "frame_schema": QueryFrame.model_json_schema(),
        "models": {},
    }
    for model in args.models:
        if model not in available:
            _log(f"== {model}: nicht geladen, übersprungen (ollama pull {model})")
            result["models"][model] = {"missing": True}
            continue
        capabilities = client.show(model).capabilities or []
        _log(f"== {model} ({', '.join(capabilities)})")
        calls = probe_model(
            client,
            model,
            options,
            settings.agent.keep_alive,
            "thinking" in capabilities,
            today,
        )
        result["models"][model] = {
            "capabilities": capabilities,
            "calls": calls,
            "summary": summarize_model(calls),
            "loaded": _loaded(client),
            "memory_mb": _memory_mb(),
        }
        if model == ISS126_MODEL and not args.skip_iss126:
            result["iss126"] = probe_iss126(client, settings, options)
        _unload(client, [model])
        _write(out_dir, result)
    _write(out_dir, result)
    _log(f"probe: {out_dir / 'm9-probe.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
