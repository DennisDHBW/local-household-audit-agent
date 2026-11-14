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


class NudgeStep(_Frozen):
    """The loop questioned a "not in the documents" answer that rested on too few searches."""

    kind: Literal["nudge"] = "nudge"
    index: int
    message: str


AgentStep = ModelCallStep | ToolCallStep | NudgeStep


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
