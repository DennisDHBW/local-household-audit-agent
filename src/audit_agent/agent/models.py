"""Typed records of an agent run: what went to the model, which tool ran, what came back.

The records are the log (concept.md, 7.4): they are written line by line while the agent
works and are the base for the evaluation and the reverse engineering of one run.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from audit_agent.retrieval import SearchHit

StopReason = Literal["answer", "tool_limit", "context_limit", "empty_answer"]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class ToolInvocation(_Frozen):
    """One tool call as the model wrote it (before validation)."""

    name: str
    arguments: dict[str, object]


class ModelCallStep(_Frozen):
    """One chat call: size of the prompt, prefill and decode times, what the model said."""

    kind: Literal["model_call"] = "model_call"
    index: int
    offered_tools: bool
    message_count: int
    prompt_tokens: int | None
    prefill_seconds: float | None
    generated_tokens: int | None
    decode_seconds: float | None
    seconds: float
    content: str
    tool_calls: tuple[ToolInvocation, ...]


class Artifact(_Frozen):
    """A table or chart that a tool made; the answer shows it below the text (ADR-0019)."""

    kind: Literal["table", "chart"]
    title: str
    markdown: str
    """The data as a Markdown table with citation numbers."""
    image_path: str | None = None
    data_path: str | None = None


class ToolCallStep(_Frozen):
    """One executed (or rejected) tool call and the observation given back to the model."""

    kind: Literal["tool_call"] = "tool_call"
    index: int
    tool: str
    arguments: dict[str, object]
    is_valid: bool
    observation: str
    seconds: float
    hit_numbers: tuple[int, ...] = ()
    is_repeat: bool = False
    """The same call (valid or failed) was made before; it was not run again (ISS-058, ISS-063)."""
    is_text_call: bool = False
    """The model wrote the call as text in its message, not as a native tool call (ISS-061)."""
    is_flow_call: bool = False
    """The call was made by the audit flow (code), not chosen by the model (ADR-0016)."""
    artifacts: tuple[Artifact, ...] = ()

    @property
    def state(self) -> str:
        """Short status for the progress lines: ``ok``, ``FEHLER`` or ``Wiederholung``."""
        if not self.is_valid:
            return "FEHLER (Wiederholung)" if self.is_repeat else "FEHLER"
        return "Wiederholung" if self.is_repeat else "ok"


NudgeReason = Literal[
    "gap", "calculate", "cite", "check", "chart", "overview", "numbers", "plan", "verdict"
]

NUDGE_LABELS: dict[NudgeReason, str] = {
    "gap": "Rückfrage: Antwort „keine Angaben“ nach zu wenigen Suchen",
    "calculate": "Rückfrage: Prüffrage ohne calculate beantwortet",
    "cite": "Rückfrage: Antwort mit Zahlen ohne Treffernummer",
    "check": "Selbstprüfung: Prüffrage ohne check_bill beantwortet",
    "chart": "Selbstprüfung: Grafik verlangt, aber nicht erstellt",
    "overview": "Selbstprüfung: Übersicht verlangt, aber nicht erstellt",
    "numbers": "Selbstprüfung: Zahlen ohne Werkzeugergebnis",
    "plan": "Selbstprüfung: geplanter Schritt nicht ausgeführt",
    "verdict": "Selbstprüfung: Urteil widerspricht check_bill",
}


class NudgeStep(_Frozen):
    """The loop questioned an answer before accepting it (see ``NudgeReason``).

    ``gap``: a "not in the documents" answer that rested on too few searches.
    ``calculate``: an audit question answered without a single ``calculate`` call (ISS-058).
    ``cite``: an answer with numbers and no hit number (M6h).
    """

    kind: Literal["nudge"] = "nudge"
    index: int
    message: str
    reason: NudgeReason = "gap"
    """Old logs have no reason; they only knew the first kind of question."""

    @property
    def label(self) -> str:
        return NUDGE_LABELS[self.reason]


CheckStatus = Literal["equal", "deviation", "not_found", "not_verified"]


class AuditCheckResult(_Frozen):
    """One checked quantity of the audit flow: target and actual value with their sources.

    ``not_found``: a value is missing in the hits; ``not_verified``: the model named a value
    that does not stand in the hit it cited (the flow does not use it).
    """

    quantity: str
    status: CheckStatus
    unit: str = ""
    target_value: float | None = None
    target_hit: int | None = None
    target_line: str = ""
    actual_value: float | None = None
    actual_hit: int | None = None
    actual_line: str = ""
    difference: str | None = None
    """Actual minus target as ``calculate`` printed it."""


class AuditFlowStep(_Frozen):
    """The fixed audit flow of one check question: result per quantity and the message."""

    kind: Literal["audit_flow"] = "audit_flow"
    index: int
    checks: tuple[AuditCheckResult, ...]
    message: str
    """What the model gets to read (empty if the flow found no quantity to check)."""
    seconds: float

    @property
    def label(self) -> str:
        deviations = sum(1 for check in self.checks if check.status == "deviation")
        return (
            f"Prüfablauf: {len(self.checks)} Prüfgrößen, {deviations} mit Abweichung "
            f"({self.seconds} s)"
        )


AgentStep = ModelCallStep | ToolCallStep | NudgeStep | AuditFlowStep


class NumberedHit(_Frozen):
    """A hit with the citation number the model saw in the observations (``[3]``)."""

    number: int = Field(ge=1)
    hit: SearchHit


class AgentRun(_Frozen):
    """Result of one question."""

    question: str
    model: str
    answer: str
    stop_reason: StopReason
    tool_call_count: int
    seconds: float
    steps: tuple[AgentStep, ...]
    sources: tuple[NumberedHit, ...]
    artifacts: tuple[Artifact, ...] = ()
    """Tables and charts of the run, in the order they were made (ADR-0019)."""

    @property
    def plan(self) -> tuple[str, ...]:
        """Steps of the first valid ``plan`` call (empty if the model did not plan)."""
        for step in self.steps:
            if isinstance(step, ToolCallStep) and step.tool == "plan" and step.is_valid:
                return tuple(str(s) for s in step.arguments.get("steps", []) or [])
        return ()

    @property
    def called_tools(self) -> tuple[str, ...]:
        """Names of all tool calls in order (valid and invalid)."""
        return tuple(step.tool for step in self.steps if isinstance(step, ToolCallStep))


class EvidenceBook:
    """Numbers every distinct chunk found during one run (the same chunk keeps its number)."""

    def __init__(self) -> None:
        self._numbers: dict[str, int] = {}
        self._hits: list[SearchHit] = []

    def register(self, hit: SearchHit) -> int:
        number = self._numbers.get(hit.chunk_id)
        if number is None:
            self._hits.append(hit)
            number = self._numbers[hit.chunk_id] = len(self._hits)
        return number

    def number_of(self, chunk_id: str) -> int | None:
        return self._numbers.get(chunk_id)

    @property
    def numbered_hits(self) -> tuple[NumberedHit, ...]:
        return tuple(NumberedHit(number=i, hit=hit) for i, hit in enumerate(self._hits, start=1))


StepCallback = Callable[[AgentStep, EvidenceBook], None]
"""Called after every step; the log file and the Streamlit view use it."""
