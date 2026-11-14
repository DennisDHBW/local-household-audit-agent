"""Pure helpers and result models of the smoke test (no network access, fully unit-testable)."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel

NANOSECONDS_PER_SECOND = 1_000_000_000


class SpeedResult(BaseModel):
    """Throughput of one model, derived from Ollama's own timing fields."""

    model: str
    prompt_tokens: int | None
    prefill_tokens_per_s: float | None
    generated_tokens: int | None
    generation_tokens_per_s: float | None
    load_seconds: float | None
    resident_gb: float | None = None


class PrefixReuseResult(BaseModel):
    """Does Ollama re-use the prompt prefix between two calls with the same system prompt?"""

    model: str
    first_prompt_tokens: int | None
    second_prompt_tokens: int | None
    first_prefill_seconds: float | None = None
    second_prefill_seconds: float | None = None
    is_prefix_reused: bool


class ToolCallResult(BaseModel):
    """Outcome of one tool-calling task."""

    task_id: str
    called_tool: str | None
    arguments: dict[str, Any]
    is_tool_correct: bool
    are_arguments_valid: bool
    seconds: float


class ToolCallingSummary(BaseModel):
    model: str
    results: list[ToolCallResult]

    @property
    def tool_accuracy(self) -> float:
        return _ratio(sum(r.is_tool_correct for r in self.results), len(self.results))

    @property
    def argument_accuracy(self) -> float:
        return _ratio(sum(r.are_arguments_valid for r in self.results), len(self.results))


class EmbeddingResult(BaseModel):
    model: str
    dimensions: int
    relevant_similarity: float
    irrelevant_similarity: float
    is_ranking_correct: bool


class VisionResult(BaseModel):
    model: str
    page_image: str
    caption: str
    expected_values: list[float]
    found_values: list[float]
    seconds: float

    @property
    def are_all_values_found(self) -> bool:
        return set(self.expected_values) <= set(self.found_values)


class SmokeReport(BaseModel):
    """Everything one smoke-test run produces (serialised to ``smoke.json``)."""

    run_id: str
    started_at: str
    num_ctx: int
    speed: list[SpeedResult] = []
    prefix_reuse: list[PrefixReuseResult] = []
    tool_calling: list[ToolCallingSummary] = []
    embedding: EmbeddingResult | None = None
    vision: VisionResult | None = None
    errors: list[str] = []


def _ratio(part: int, total: int) -> float:
    return part / total if total else 0.0


def tokens_per_second(token_count: int | None, duration_ns: int | None) -> float | None:
    """Tokens per second from Ollama's count and nanosecond duration (None if unknown)."""
    if not token_count or not duration_ns:
        return None
    return token_count / (duration_ns / NANOSECONDS_PER_SECOND)


def speed_from_response(model: str, response: Any, resident_gb: float | None = None) -> SpeedResult:
    """Extract throughput numbers from an Ollama chat/generate response object."""
    load_ns = getattr(response, "load_duration", None)
    return SpeedResult(
        model=model,
        prompt_tokens=getattr(response, "prompt_eval_count", None),
        prefill_tokens_per_s=tokens_per_second(
            getattr(response, "prompt_eval_count", None),
            getattr(response, "prompt_eval_duration", None),
        ),
        generated_tokens=getattr(response, "eval_count", None),
        generation_tokens_per_s=tokens_per_second(
            getattr(response, "eval_count", None), getattr(response, "eval_duration", None)
        ),
        load_seconds=None if load_ns is None else load_ns / NANOSECONDS_PER_SECOND,
        resident_gb=resident_gb,
    )


def is_prefix_reused(first_seconds: float | None, second_seconds: float | None) -> bool:
    """Heuristic: the second call needs clearly less prefill time than the first.

    The token counts are not usable: Ollama 0.35.1 reports the full prompt length even when
    a cached prefix is reused (RUN-000, ISS-004). The prefill duration is what really drops.
    """
    if not first_seconds or second_seconds is None:
        return False
    return second_seconds < 0.5 * first_seconds


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    if norm == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")
    return sum(x * y for x, y in zip(a, b, strict=True)) / norm


def tool_call_is_correct(
    called_tool: str | None,
    expected_tool: str,
    arguments: Mapping[str, Any],
    expected: Mapping[str, str],
) -> tuple[bool, bool]:
    """Return ``(is_tool_correct, are_arguments_valid)`` for one tool-calling task.

    Arguments are valid when every expected key is present and matches case-insensitively
    (a key mapped to ``"*"`` only has to be present and non-empty).
    """
    is_tool_correct = called_tool == expected_tool
    if not is_tool_correct:
        return False, False
    for key, wanted in expected.items():
        value = arguments.get(key)
        if value is None or str(value).strip() == "":
            return True, False
        if wanted != "*" and wanted.lower() not in str(value).lower():
            return True, False
    return True, True
