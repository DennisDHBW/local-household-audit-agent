"""Records of the test module: one answer of one variant and its deterministic score.

Answers and scores are kept apart on purpose (concept.md, 11.3): an answer costs minutes of
CPU time and is stored as one JSON line; scoring reads the lines again and can be repeated
without Ollama whenever a metric changes.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from audit_agent.agent.models import ModelCallStep
from audit_agent.corpus import QuestionCategory
from audit_agent.ingestion import ChunkType

VariantName = Literal["b0", "p1", "p2"]
VARIANT_NAMES: tuple[VariantName, ...] = ("b0", "p1", "p2")
VARIANT_LABELS: dict[VariantName, str] = {
    "b0": "B0 Volltext",
    "p1": "P1 Pipeline",
    "p2": "P2 Agent",
}
Verdict = Literal["ja", "nein"]


class EvaluationError(RuntimeError):
    """The evaluation cannot run (missing data, mixed models in one run, unknown ids)."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class ShownSource(_Frozen):
    """A numbered piece of evidence the model saw and may cite as ``[number]``."""

    number: int
    filename: str
    page_number: int
    chunk_type: ChunkType | None = None
    """``None`` for a B0 page block (text, headings and table rows of one page)."""


class ToolUse(_Frozen):
    """One tool call of the agent, reduced to what the metrics need."""

    name: str
    arguments: dict[str, object]
    is_valid: bool


class VariantAnswer(_Frozen):
    """The answer of one variant (B0, P1 or P2) to one question of the ground truth."""

    variant: VariantName
    question_id: str
    model: str
    answer: str
    stop_reason: str
    seconds: float
    sources: tuple[ShownSource, ...]
    tool_uses: tuple[ToolUse, ...] = ()
    model_calls: tuple[ModelCallStep, ...]
    contexts: tuple[str, ...] = ()
    """Evidence text exactly as the model saw it, the input of RAGAS (ADR-0012).

    B0: one block per page; P1: one block per hit; P2: the observation of each valid tool
    call (search hits, document lists, calculations). Empty in runs before M6b.
    """

    @property
    def prompt_tokens(self) -> int:
        """Prompt tokens Ollama evaluated (cached prefix tokens are not counted, ISS-005)."""
        return sum(call.prompt_tokens or 0 for call in self.model_calls)


class AnswerScore(_Frozen):
    """Deterministic checks of one answer against the ground truth (concept.md, 11.3)."""

    variant: VariantName
    question_id: str
    category: QuestionCategory
    is_answerable: bool
    facts_total: int
    missing_facts: tuple[str, ...]
    cited_count: int
    """Cited numbers that belong to a shown source."""
    invalid_citations: int
    """Cited numbers the model never saw (invented citations)."""
    cited_expected: int
    """Cited sources whose file and page are expected sources."""
    expected_count: int
    expected_cited: int
    """Expected sources (file and page) that the answer cites."""
    cited_distractors: int
    shown_count: int
    shown_distractors: int
    expected_tools: tuple[str, ...]
    called_tools: tuple[str, ...] | None
    """Valid tool calls in order; ``None`` for variants without tools (B0, P1)."""
    filtered_searches: int
    filter_misses: int
    """Searches whose self-set filter excludes an expected source document."""
    admits_gap: bool
    expected_verdict: Verdict | None
    answer_verdict: Verdict | None
    stop_reason: str
    seconds: float
    prompt_tokens: int

    @property
    def facts_found(self) -> int:
        return self.facts_total - len(self.missing_facts)

    @property
    def are_tools_ok(self) -> bool | None:
        if self.called_tools is None:
            return None
        return all(tool in self.called_tools for tool in self.expected_tools)

    @property
    def is_verdict_ok(self) -> bool | None:
        if self.expected_verdict is None:
            return None
        return self.answer_verdict == self.expected_verdict

    @property
    def is_correct(self) -> bool:
        """Negative question: gap admitted. Otherwise: all facts found and the verdict fits."""
        if not self.is_answerable:
            return self.admits_gap
        return not self.missing_facts and self.is_verdict_ok is not False


class VariantSummary(_Frozen):
    """Counts of one variant over all scored questions (the "variant x metric" table)."""

    variant: VariantName
    question_count: int
    correct_count: int
    facts_found: int
    facts_total: int
    cited_count: int
    invalid_citations: int
    cited_expected: int
    expected_count: int
    expected_cited: int
    cited_distractors: int
    shown_count: int
    shown_distractors: int
    tools_ok_count: int | None
    filtered_searches: int
    filter_misses: int
    negatives_detected: int
    negative_count: int
    errors_detected: int
    error_count: int
    false_alarms: int
    correct_bill_count: int
    seconds_mean: float
    seconds_median: float
    prompt_tokens_mean: float
