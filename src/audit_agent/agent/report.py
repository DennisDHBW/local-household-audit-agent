"""Quick checks and a Markdown report for a set of agent runs (RUN-005, evaluation-log).

These checks are deliberately simple (tool choice, found sources, numbers in the answer).
The full metrics and RAGAS belong to the test module of M6.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from audit_agent.agent.models import AgentRun, ModelCallStep, ToolCallStep
from audit_agent.corpus import ExpectedFact, Question
from audit_agent.numbers import extract_numbers
from audit_agent.retrieval.search import fold

GAP_PHRASES = (
    "keine angaben",
    "liegt nicht vor",
    "liegen nicht vor",
    "nicht in den unterlagen",
    "nicht gefunden",
)
"""Phrases of an honest "not in the documents" answer (checked on the folded answer)."""
UNIT_FACTORS = (Decimal(1), Decimal(100), Decimal("0.01"))
"""A fact may be written as EUR or ct, 0.348 or 34,8."""


class RunCheck(BaseModel):
    """Result of the quick checks of one run."""

    model_config = ConfigDict(frozen=True)

    question_id: str
    expected_tools: tuple[str, ...]
    called_tools: tuple[str, ...]
    are_tools_ok: bool
    missing_files: tuple[str, ...]
    missing_facts: tuple[str, ...]
    admits_gap: bool | None
    """For unanswerable questions: does the answer say that the information is missing?"""


def is_fact_in_answer(fact: ExpectedFact, answer: str) -> bool:
    """Numbers match any number of the answer (also in ct); text facts match as substring."""
    if isinstance(fact.value, str):
        return fold(fact.value) in fold(answer)
    numbers = extract_numbers(answer)
    return any(
        abs(Decimal(str(number)) - fact.value * factor) <= fact.tolerance * max(factor, 1)
        for number in numbers
        for factor in UNIT_FACTORS
    )


def evaluate_run(question: Question, run: AgentRun) -> RunCheck:
    """Compare one run with the ground truth of its question."""
    called = run.called_tools
    found_files = {source.hit.filename for source in run.sources}
    return RunCheck(
        question_id=question.id,
        expected_tools=question.expected_tools,
        called_tools=called,
        are_tools_ok=all(tool in called for tool in question.expected_tools),
        missing_files=tuple(
            sorted({s.file for s in question.sources if s.file not in found_files})
        ),
        missing_facts=tuple(
            fact.label for fact in question.facts if not is_fact_in_answer(fact, run.answer)
        ),
        admits_gap=None
        if question.is_answerable
        else any(phrase in fold(run.answer) for phrase in GAP_PHRASES),
    )


def _yes_no(value: bool) -> str:
    return "ja" if value else "nein"


def _call_rows(run: AgentRun) -> list[str]:
    rows = []
    for step in run.steps:
        if not isinstance(step, ModelCallStep):
            continue
        rate = (
            f"{step.prompt_tokens / step.prefill_seconds:.0f}"
            if step.prompt_tokens and step.prefill_seconds
            else "-"
        )
        rows.append(
            f"| {step.index} | {step.prompt_tokens} | "
            f"{step.prefill_seconds if step.prefill_seconds is not None else '-'} | {rate} | "
            f"{step.generated_tokens} | {step.seconds} |"
        )
    return rows


def render_markdown(model: str, results: list[tuple[Question, AgentRun]]) -> str:
    """Summary table, then answer, tool steps and model calls per question."""
    lines = [
        f"# Agentenlauf ({date.today().isoformat()})",
        "",
        f"Modell: `{model}`. Prüfungen sind grob (siehe M6 für die Metriken).",
        "",
        "| Frage | Tools erwartet | Tools gerufen | Tools ok | Quellen fehlen | Zahlen fehlen "
        "| Lücke benannt | Ende | Aufrufe | Sekunden |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    checks = [(question, run, evaluate_run(question, run)) for question, run in results]
    for question, run, check in checks:
        gap = "-" if check.admits_gap is None else _yes_no(check.admits_gap)
        lines.append(
            f"| {question.id} | {', '.join(check.expected_tools)} | "
            f"{', '.join(check.called_tools) or '-'} | {_yes_no(check.are_tools_ok)} | "
            f"{len(check.missing_files)} | {', '.join(check.missing_facts) or '-'} | {gap} | "
            f"{run.stop_reason} | {run.tool_call_count} | {run.seconds} |"
        )
    for question, run, check in checks:
        lines += [
            "",
            f"## {question.id}: {question.question}",
            "",
            f"**Antwort:** {run.answer}",
            "",
        ]
        lines.append(f"Erwartet: {question.expected_answer.strip()}")
        if check.missing_files:
            lines.append(f"Nicht gefundene Quellen: {', '.join(check.missing_files)}")
        lines += ["", "Werkzeugaufrufe:"]
        for step in run.steps:
            if isinstance(step, ToolCallStep):
                state = "ok" if step.is_valid else "FEHLER"
                lines.append(
                    f"- {step.tool}({step.arguments}) → {state}, "
                    f"Treffer {list(step.hit_numbers)}, {step.seconds} s"
                )
        lines += [
            "",
            "| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |",
            "|---|---|---|---|---|---|",
            *_call_rows(run),
        ]
    return "\n".join(lines) + "\n"
