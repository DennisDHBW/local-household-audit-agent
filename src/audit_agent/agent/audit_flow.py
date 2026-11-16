"""Fixed audit flow for check questions (ADR-0016): plan, search, read, compute.

For a question like "Is the bill correct?" the small models did not search for target and
actual value of one quantity, and when they called ``calculate`` they often took operands that
do not belong together (ISS-067). The flow takes these steps out of the model's hands:

1. The model names the quantities to check and one search query per side (structured output).
2. The code runs the searches (the normal ``search`` tool, so evidence and log stay the same).
3. The model reads one target and one actual value per quantity from the hits (structured
   output). The code checks that each number stands in the hit the model cited.
4. The code subtracts with ``calculate`` and writes the findings for the model.

What stays with the model: which quantities matter, what the queries say, which number in a
hit is the right one, and the final answer. What the code guarantees: the operands come from
cited hits and the arithmetic is exact. It does not guarantee that target and actual are the
same quantity (the model decides that, see ISS-067).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from audit_agent.agent.models import AuditCheckResult, ToolCallStep
from audit_agent.agent.prompts import (
    AUDIT_FLOW_CLOSING,
    READ_SYSTEM_PROMPT,
    plan_prompt,
)
from audit_agent.agent.tools import tool_parameters
from audit_agent.numbers import extract_numbers
from audit_agent.retrieval.search import fold

MAX_LINE_CHARS = 160
RELATIVE_TOLERANCE = 1e-9

AskModel = Callable[[list[dict[str, str]], dict[str, Any]], str]
"""Messages and JSON schema -> raw JSON text of the answer (the loop logs the call)."""
RunTool = Callable[[str, dict[str, object]], ToolCallStep]
"""Tool name and arguments -> the executed (and logged) step."""
HitContent = Callable[[int], str]
"""Citation number -> full text of that hit (empty if the number is unknown)."""


class PlannedCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    quantity: str
    target_query: str
    actual_query: str


class AuditPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    checks: list[PlannedCheck]


class Reading(BaseModel):
    """Two numbers as the model read them; ``""`` and ``0`` mean "not found"."""

    model_config = ConfigDict(extra="ignore")

    target_value: str
    target_hit: int
    actual_value: str
    actual_hit: int
    unit: str = ""


PLAN_SCHEMA = tool_parameters(AuditPlan)
READING_SCHEMA = tool_parameters(Reading)


def run_audit_flow(
    question: str,
    ask_model: AskModel,
    run_tool: RunTool,
    hit_content: HitContent,
    max_checks: int,
) -> tuple[tuple[AuditCheckResult, ...], str]:
    """The result per quantity and the message for the model (empty if nothing to check)."""
    planned = _plan(question, ask_model, max_checks)
    searched: dict[str, ToolCallStep] = {}

    def search(query: str) -> ToolCallStep:
        """One search per distinct query: the loop blocks an identical second call."""
        if query not in searched:
            searched[query] = run_tool("search", {"query": query})
        return searched[query]

    results = tuple(_check(item, ask_model, search, run_tool, hit_content) for item in planned)
    return results, render_findings(results)


def _plan(question: str, ask_model: AskModel, max_checks: int) -> list[PlannedCheck]:
    messages = [
        {"role": "system", "content": plan_prompt(max_checks)},
        {"role": "user", "content": question},
    ]
    try:
        plan = AuditPlan.model_validate_json(ask_model(messages, PLAN_SCHEMA))
    except ValidationError:
        return []
    unique: dict[str, PlannedCheck] = {}
    for item in plan.checks:
        key = fold(item.quantity).strip()
        if key and len(item.target_query) >= 2 and len(item.actual_query) >= 2:
            unique.setdefault(key, item)
    return list(unique.values())[:max_checks]


def _check(
    item: PlannedCheck,
    ask_model: AskModel,
    search: Callable[[str], ToolCallStep],
    run_tool: RunTool,
    hit_content: HitContent,
) -> AuditCheckResult:
    target_step = search(item.target_query)
    actual_step = search(item.actual_query)
    if not (target_step.hit_numbers and actual_step.hit_numbers):
        return AuditCheckResult(quantity=item.quantity, status="not_found")
    messages = [
        {"role": "system", "content": READ_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Prüfgröße: {item.quantity}\n\n"
                f"Treffer für den Sollwert:\n{target_step.observation}\n\n"
                f"Treffer für den Istwert:\n{actual_step.observation}"
            ),
        },
    ]
    try:
        reading = Reading.model_validate_json(ask_model(messages, READING_SCHEMA))
    except ValidationError:
        return AuditCheckResult(quantity=item.quantity, status="not_found")
    if not reading.target_value.strip() or not reading.actual_value.strip():
        return AuditCheckResult(quantity=item.quantity, status="not_found", unit=reading.unit)
    target = _verified(reading.target_value, reading.target_hit, target_step, hit_content)
    actual = _verified(reading.actual_value, reading.actual_hit, actual_step, hit_content)
    if target is None or actual is None:
        return AuditCheckResult(quantity=item.quantity, status="not_verified", unit=reading.unit)
    difference = _difference(actual[0], target[0], run_tool)
    is_equal = math.isclose(actual[0], target[0], rel_tol=RELATIVE_TOLERANCE, abs_tol=1e-9)
    return AuditCheckResult(
        quantity=item.quantity,
        status="equal" if is_equal else "deviation",
        unit=reading.unit,
        target_value=target[0],
        target_hit=reading.target_hit,
        target_line=target[1],
        actual_value=actual[0],
        actual_hit=reading.actual_hit,
        actual_line=actual[1],
        difference=difference,
    )


def _verified(
    value: str, hit_number: int, step: ToolCallStep, hit_content: HitContent
) -> tuple[float, str] | None:
    """The number and the line of the hit it stands in; ``None`` if the hit does not show it.

    The hit must be one of this side's search hits: a number from an unrelated hit is the
    typical wrong operand (ISS-067).
    """
    numbers = extract_numbers(value)
    if hit_number not in step.hit_numbers or not numbers:
        return None
    wanted = numbers[0]
    for line in hit_content(hit_number).splitlines():
        found = extract_numbers(line)
        if any(math.isclose(n, wanted, rel_tol=RELATIVE_TOLERANCE) for n in found):
            return wanted, " ".join(line.split())[:MAX_LINE_CHARS]
    return None


def _difference(actual: float, target: float, run_tool: RunTool) -> str | None:
    """Actual minus target by the ``calculate`` tool (exact decimal arithmetic)."""
    step = run_tool("calculate", {"expression": f"{actual!r} - {target!r}"})
    if not step.is_valid:
        return None
    return step.observation.rsplit("=", 1)[-1].strip()


def render_findings(results: tuple[AuditCheckResult, ...]) -> str:
    """The text the model reads instead of doing the search and subtraction itself."""
    if not results:
        return ""
    lines = ["Prüfablauf (vom Code ausgeführt, Zahlen stehen in den genannten Treffern):"]
    for number, check in enumerate(results, start=1):
        unit = f" ({check.unit})" if check.unit else ""
        head = f"{number}. {check.quantity}{unit}: "
        if check.status == "not_found":
            lines.append(head + "Soll- oder Istwert nicht gefunden. Suche selbst weiter.")
        elif check.status == "not_verified":
            lines.append(head + "genannte Zahl steht nicht im Treffer. Suche selbst weiter.")
        else:
            verdict = "gleich" if check.status == "equal" else "ABWEICHUNG"
            lines.append(
                f"{head}Soll {_number(check.target_value)} [{check.target_hit}] "
                f"„{check.target_line}“; Ist {_number(check.actual_value)} "
                f"[{check.actual_hit}] „{check.actual_line}“; Ist minus Soll = "
                f"{check.difference} → {verdict}"
            )
    lines.append(AUDIT_FLOW_CLOSING)
    return "\n".join(lines)


def _number(value: float | None) -> str:
    return "?" if value is None else f"{value:.6f}".rstrip("0").rstrip(".")
