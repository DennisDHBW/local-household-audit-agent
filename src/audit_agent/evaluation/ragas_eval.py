"""RAGAS as a second view on stored answers (concept.md 11.3, ADR-0012).

- **Faithfulness:** share of the answer's statements that the judge finds in the evidence the
  answering model saw (``VariantAnswer.contexts``).
- **Context recall:** share of the reference answer's statements found in that evidence.

The judge is a local Ollama model behind Ollama's OpenAI-compatible endpoint. RAGAS is an
optional dependency group (``uv sync --group ragas``) and imported lazily by :class:`RagasJudge`
only, so the quality gate runs without it. Each result is one JSON line in ``ragas.jsonl``;
an interrupted run resumes with the same command.
"""

from __future__ import annotations

import math
import os
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from statistics import mean
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from audit_agent.agent.loop import CHARS_PER_TOKEN
from audit_agent.config import Settings
from audit_agent.corpus import Question
from audit_agent.evaluation.models import VARIANT_NAMES, EvaluationError, VariantAnswer, VariantName

RAGAS_FILE = "ragas.jsonl"
RagasMetric = Literal["faithfulness", "context_recall"]
RAGAS_METRICS: tuple[RagasMetric, ...] = ("faithfulness", "context_recall")
RAGAS_LABELS: dict[RagasMetric, str] = {
    "faithfulness": "Faithfulness",
    "context_recall": "Context Recall",
}
RagasStatus = Literal["ok", "too_long", "no_context", "not_applicable", "no_statements", "error"]
"""``too_long``: the judge prompt would not fit into ``judge_num_ctx`` (no silent cut, ISS-041);
``no_context``: the model saw no evidence; ``not_applicable``: empty answer, or context recall
of a negative question (its reference states a gap, not facts); ``no_statements``: the judge
extracted nothing to check (RAGAS returns NaN)."""
OPENAI_PATH = "/v1"
TRACKING_ENV = "RAGAS_DO_NOT_TRACK"


class RagasScore(BaseModel):
    """One RAGAS metric of one stored answer."""

    model_config = ConfigDict(frozen=True)

    variant: VariantName
    question_id: str
    metric: RagasMetric
    judge: str
    status: RagasStatus
    value: float | None = None
    estimated_tokens: int = 0
    seconds: float = 0.0
    detail: str = ""

    @property
    def key(self) -> tuple[VariantName, str, RagasMetric]:
        return (self.variant, self.question_id, self.metric)


class RagasSummary(BaseModel):
    """Mean of one metric of one variant over the answers the judge could score."""

    model_config = ConfigDict(frozen=True)

    variant: VariantName
    metric: RagasMetric
    mean: float | None
    scored: int
    total: int
    too_long: int
    errors: int


class Judge(Protocol):
    """Scores one metric of one answer (tests use a fake, production :class:`RagasJudge`)."""

    model: str

    def prompt_chars(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> int:
        """Characters of the longest judge prompt this metric will send."""
        ...

    async def score(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> float: ...


def estimate_judge_tokens(prompt_chars: int, settings: Settings) -> int:
    """Prompt plus answer budget; the high German ratio keeps the estimate on the safe side."""
    return int(prompt_chars / CHARS_PER_TOKEN) + 1 + settings.evaluation.judge_max_tokens


def ragas_path(run_dir: Path) -> Path:
    return run_dir / RAGAS_FILE


def load_ragas_scores(path: Path) -> list[RagasScore]:
    """Scores of a run; for a key written twice (retried error) the last line wins."""
    if not path.exists():
        return []
    latest: dict[tuple[VariantName, str, RagasMetric], RagasScore] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            score = RagasScore.model_validate_json(line)
            latest[score.key] = score
    return list(latest.values())


def _append(path: Path, score: RagasScore) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(score.model_dump_json() + "\n")


def _precheck(
    metric: RagasMetric, question: Question, answer: VariantAnswer
) -> tuple[RagasStatus, str] | None:
    """Reason why the judge is not asked at all, or ``None``."""
    if metric == "context_recall" and not question.is_answerable:
        return "not_applicable", "Negativfrage: Referenz enthält keine Fakten"
    if metric == "faithfulness" and not answer.answer.strip():
        return "not_applicable", "leere Antwort"
    if not answer.contexts:
        return "no_context", "keine Belegtexte gespeichert"
    return None


async def score_answer_ragas(
    metric: RagasMetric,
    question: Question,
    answer: VariantAnswer,
    judge: Judge,
    settings: Settings,
) -> RagasScore:
    """One metric of one answer; judge errors are recorded, a lost connection is raised."""

    def result(
        status: RagasStatus,
        value: float | None = None,
        estimated_tokens: int = 0,
        seconds: float = 0.0,
        detail: str = "",
    ) -> RagasScore:
        return RagasScore(
            variant=answer.variant,
            question_id=answer.question_id,
            metric=metric,
            judge=judge.model,
            status=status,
            value=value,
            estimated_tokens=estimated_tokens,
            seconds=seconds,
            detail=detail,
        )

    skip = _precheck(metric, question, answer)
    if skip is not None:
        return result(skip[0], detail=skip[1])
    reference = question.expected_answer.strip()
    chars = judge.prompt_chars(metric, question.question, answer.answer, answer.contexts, reference)
    tokens = estimate_judge_tokens(chars, settings)
    limit = settings.evaluation.judge_num_ctx
    if tokens > limit:
        return result("too_long", estimated_tokens=tokens, detail=f"ca. {tokens} > {limit} Token")
    started = time.perf_counter()
    try:
        value = await judge.score(
            metric, question.question, answer.answer, answer.contexts, reference
        )
    except ConnectionError:
        raise
    except (
        Exception
    ) as error:  # any judge failure (invalid JSON, timeout) must not stop a night run
        return result(
            "error",
            estimated_tokens=tokens,
            seconds=round(time.perf_counter() - started, 1),
            detail=f"{type(error).__name__}: {str(error)[:300]}",
        )
    seconds = round(time.perf_counter() - started, 1)
    if math.isnan(value):
        return result("no_statements", estimated_tokens=tokens, seconds=seconds)
    return result("ok", value=round(value, 4), estimated_tokens=tokens, seconds=seconds)


async def evaluate_run(
    answers: Sequence[VariantAnswer],
    questions: Mapping[str, Question],
    judge: Judge,
    settings: Settings,
    path: Path,
    metrics: Sequence[RagasMetric] = RAGAS_METRICS,
    retry_errors: bool = False,
    on_score: Callable[[RagasScore], None] | None = None,
) -> list[RagasScore]:
    """Score every answer with every metric, skipping keys already in ``path``."""
    done = {score.key: score for score in load_ragas_scores(path)}
    for answer in answers:
        question = questions.get(answer.question_id)
        if question is None:
            raise EvaluationError(f"answer for unknown question {answer.question_id}")
        for metric in metrics:
            previous = done.get((answer.variant, answer.question_id, metric))
            if previous is not None and not (retry_errors and previous.status == "error"):
                continue
            score = await score_answer_ragas(metric, question, answer, judge, settings)
            _append(path, score)
            done[score.key] = score
            if on_score is not None:
                on_score(score)
    return load_ragas_scores(path)


def summarize_ragas(scores: Sequence[RagasScore]) -> list[RagasSummary]:
    """One row per variant and metric that has scores, in fixed order."""
    summaries: list[RagasSummary] = []
    for variant in VARIANT_NAMES:
        for metric in RAGAS_METRICS:
            rows = [s for s in scores if s.variant == variant and s.metric == metric]
            if not rows:
                continue
            values = [s.value for s in rows if s.status == "ok" and s.value is not None]
            summaries.append(
                RagasSummary(
                    variant=variant,
                    metric=metric,
                    mean=round(mean(values), 2) if values else None,
                    scored=len(values),
                    total=len(rows),
                    too_long=sum(s.status == "too_long" for s in rows),
                    errors=sum(s.status == "error" for s in rows),
                )
            )
    return summaries


def _connection_lost(error: BaseException) -> bool:
    """True if the cause chain holds an OpenAI connection error that is not a timeout."""
    from openai import APIConnectionError, APITimeoutError

    current: BaseException | None = error
    while current is not None:
        if isinstance(current, APIConnectionError) and not isinstance(current, APITimeoutError):
            return True
        current = current.__cause__ or current.__context__
    return False


class RagasJudge:
    """RAGAS 0.4 metrics with a local Ollama model as judge (structured output via JSON mode)."""

    def __init__(self, settings: Settings, model: str | None = None):
        # Local-only (ADR-0001): RAGAS sends usage events to its vendor unless told not to.
        # The flag is read once and cached, so it must be set before the first import.
        os.environ[TRACKING_ENV] = "true"
        try:
            from openai import AsyncOpenAI
            from ragas.llms import llm_factory
            from ragas.metrics.collections import ContextRecall, Faithfulness
        except ImportError as error:
            raise EvaluationError(
                "RAGAS is not installed; run `uv sync --group ragas` (ADR-0012)"
            ) from error
        self.model = model or settings.models.judge
        client = AsyncOpenAI(
            api_key="ollama",  # Ollama ignores the key, the client requires one
            base_url=settings.ollama_host.rstrip("/") + OPENAI_PATH,
            timeout=settings.ollama_timeout_s,
            max_retries=0,
        )
        llm = llm_factory(
            self.model,
            provider="openai",
            client=client,
            temperature=0.0,
            max_tokens=settings.evaluation.judge_max_tokens,
        )
        self._faithfulness = Faithfulness(llm=llm)
        self._context_recall = ContextRecall(llm=llm)

    def prompt_chars(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> int:
        from ragas.metrics.collections.context_recall.util import (
            ContextRecallInput,
            ContextRecallPrompt,
        )
        from ragas.metrics.collections.faithfulness.util import (
            NLIStatementInput,
            NLIStatementPrompt,
            StatementGeneratorInput,
            StatementGeneratorPrompt,
        )

        context = "\n".join(contexts)  # RAGAS joins the contexts the same way
        if metric == "context_recall":
            data = ContextRecallInput(question=question, context=context, answer=reference)
            return len(ContextRecallPrompt().to_string(data))
        statements = StatementGeneratorPrompt().to_string(
            StatementGeneratorInput(question=question, answer=response)
        )
        # The statements are not known yet; the answer itself stands in for them.
        verdicts = NLIStatementPrompt().to_string(
            NLIStatementInput(context=context, statements=[response])
        )
        return max(len(statements), len(verdicts))

    async def score(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> float:
        try:
            if metric == "context_recall":
                result = await self._context_recall.ascore(
                    user_input=question, retrieved_contexts=list(contexts), reference=reference
                )
            else:
                result = await self._faithfulness.ascore(
                    user_input=question, response=response, retrieved_contexts=list(contexts)
                )
        except Exception as error:
            if _connection_lost(error):
                raise ConnectionError(f"Ollama is not reachable: {error}") from error
            raise
        return float(result.value)
