"""Test module (M6): variants B0, P1, P2, deterministic metrics and the report."""

from audit_agent.evaluation.metrics import score_answer, summarize
from audit_agent.evaluation.models import (
    VARIANT_NAMES,
    AnswerScore,
    EvaluationError,
    ShownSource,
    ToolUse,
    VariantAnswer,
    VariantName,
    VariantSummary,
)
from audit_agent.evaluation.testset import select_questions

__all__ = [
    "VARIANT_NAMES",
    "AnswerScore",
    "EvaluationError",
    "ShownSource",
    "ToolUse",
    "VariantAnswer",
    "VariantName",
    "VariantSummary",
    "score_answer",
    "select_questions",
    "summarize",
]
