"""Tests of the RAGAS step (M6b, ADR-0012): pre-checks, resume, summary, report, judge setup."""

from __future__ import annotations

import asyncio
import math
import os
import re
from collections.abc import Sequence

import pytest

from audit_agent.agent.models import ModelCallStep
from audit_agent.config import PROJECT_ROOT, EvaluationSettings, ModelNames, Settings
from audit_agent.corpus import Question, QuestionCategory, SourceRef, load_document_catalog
from audit_agent.evaluation import ShownSource, VariantAnswer, score_answer, summarize
from audit_agent.evaluation.ragas_eval import (
    TRACKING_ENV,
    RagasMetric,
    RagasScore,
    evaluate_run,
    load_ragas_scores,
    ragas_path,
    score_answer_ragas,
    summarize_ragas,
)
from audit_agent.evaluation.report import render_report

BILL = "01_electricity_suedvolt/06_Strom_Jahresabrechnung_2025_SuedVolt.pdf"


class FakeJudge:
    """Returns scripted values per metric and records every call."""

    model = "fake-judge"

    def __init__(self, values: dict[RagasMetric, object] | None = None):
        self.values: dict[RagasMetric, object] = values or {
            "faithfulness": 0.75,
            "context_recall": 0.5,
        }
        self.calls: list[tuple[RagasMetric, str]] = []

    def prompt_chars(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> int:
        return len(question) + len(response) + sum(map(len, contexts)) + len(reference)

    async def score(
        self,
        metric: RagasMetric,
        question: str,
        response: str,
        contexts: Sequence[str],
        reference: str,
    ) -> float:
        self.calls.append((metric, question))
        value = self.values[metric]
        if isinstance(value, BaseException):
            raise value
        assert isinstance(value, float)
        return value


def _question(**overrides) -> Question:
    values = {
        "id": "G1",
        "category": QuestionCategory.EDGE_CASE,
        "question": "Wurde der neue Arbeitspreis angewendet?",
        "expected_answer": "Nein. Angekündigt 38,20, abgerechnet 39,50 ct/kWh.",
        "sources": (SourceRef(file=BILL, page=1),),
        "tests": "Fehlererkennung",
    }
    return Question(**{**values, **overrides})


def _negative() -> Question:
    return Question(
        id="N1",
        category=QuestionCategory.NEGATIVE,
        question="Stromrechnung 2023?",
        expected_answer="Liegt nicht vor.",
        is_answerable=False,
        tests="keine erfundene Zahl",
    )


def _answer(question_id="G1", variant="p1", text="Nein, 39,50 statt 38,20 [1].", **overrides):
    values = {
        "variant": variant,
        "question_id": question_id,
        "model": "m",
        "answer": text,
        "stop_reason": "answer",
        "seconds": 10.0,
        "sources": (ShownSource(number=1, filename=BILL, page_number=1),),
        "model_calls": (
            ModelCallStep(
                index=0,
                offered_tools=False,
                message_count=2,
                prompt_tokens=100,
                prefill_seconds=1.0,
                generated_tokens=10,
                decode_seconds=1.0,
                seconds=2.0,
                content=text,
                tool_calls=(),
            ),
        ),
        "contexts": ("[1] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 1\nArbeitspreis 39,50",),
    }
    return VariantAnswer(**{**values, **overrides})


def _run(coroutine):
    return asyncio.run(coroutine)


def test_both_metrics_are_scored_with_the_stored_contexts(tmp_path):
    judge = FakeJudge()
    score = _run(score_answer_ragas("faithfulness", _question(), _answer(), judge, Settings()))
    recall = _run(score_answer_ragas("context_recall", _question(), _answer(), judge, Settings()))
    assert (score.status, score.value, score.judge) == ("ok", 0.75, "fake-judge")
    assert (recall.status, recall.value) == ("ok", 0.5)
    assert score.estimated_tokens > Settings().evaluation.judge_max_tokens


@pytest.mark.parametrize(
    ("metric", "question", "answer", "status"),
    [
        ("context_recall", _negative(), _answer("N1"), "not_applicable"),
        ("faithfulness", _question(), _answer(text="  "), "not_applicable"),
        ("faithfulness", _question(), _answer(contexts=()), "no_context"),
    ],
)
def test_prechecks_skip_the_judge(metric, question, answer, status):
    judge = FakeJudge()
    score = _run(score_answer_ragas(metric, question, answer, judge, Settings()))
    assert score.status == status and score.value is None
    assert judge.calls == []


def test_faithfulness_of_a_negative_answer_is_still_judged():
    judge = FakeJudge()
    score = _run(score_answer_ragas("faithfulness", _negative(), _answer("N1"), judge, Settings()))
    assert score.status == "ok"


def test_a_prompt_beyond_the_judge_context_is_skipped_not_cut():
    # Arrange: a context of 2,000 tokens leaves no room in a 2,048-token judge window
    settings = Settings(evaluation=EvaluationSettings(judge_num_ctx=2048, judge_max_tokens=512))
    answer = _answer(contexts=("x" * 4800,))
    judge = FakeJudge()

    # Act
    score = _run(score_answer_ragas("faithfulness", _question(), answer, judge, settings))

    # Assert
    assert score.status == "too_long" and judge.calls == []
    assert score.estimated_tokens > 2048 and "2048" in score.detail


def test_judge_failures_are_recorded_but_a_lost_connection_stops_the_run():
    failing = FakeJudge({"faithfulness": ValueError("invalid JSON"), "context_recall": 0.5})
    score = _run(score_answer_ragas("faithfulness", _question(), _answer(), failing, Settings()))
    assert score.status == "error" and "invalid JSON" in score.detail

    offline = FakeJudge({"faithfulness": ConnectionError("down"), "context_recall": 0.5})
    with pytest.raises(ConnectionError):
        _run(score_answer_ragas("faithfulness", _question(), _answer(), offline, Settings()))


def test_nan_means_the_judge_found_no_statements():
    judge = FakeJudge({"faithfulness": math.nan, "context_recall": 0.5})
    score = _run(score_answer_ragas("faithfulness", _question(), _answer(), judge, Settings()))
    assert score.status == "no_statements" and score.value is None


def test_a_run_resumes_and_retries_only_errors_on_request(tmp_path):
    # Arrange
    path = ragas_path(tmp_path)
    questions = {"G1": _question(), "N1": _negative()}
    answers = [_answer(), _answer("N1", text="Liegt nicht vor.")]
    flaky = FakeJudge({"faithfulness": ValueError("bad"), "context_recall": 0.5})

    # Act: first run with a failing faithfulness, then resume, then retry the errors
    _run(evaluate_run(answers, questions, flaky, Settings(), path))
    resumed = FakeJudge()
    _run(evaluate_run(answers, questions, resumed, Settings(), path))
    fixed = FakeJudge()
    scores = _run(evaluate_run(answers, questions, fixed, Settings(), path, retry_errors=True))

    # Assert
    assert len(flaky.calls) == 3  # G1 both metrics, N1 faithfulness only
    assert resumed.calls == []
    assert [metric for metric, _ in fixed.calls] == ["faithfulness", "faithfulness"]
    assert {s.key: s.status for s in scores} == {
        ("p1", "G1", "faithfulness"): "ok",
        ("p1", "G1", "context_recall"): "ok",
        ("p1", "N1", "faithfulness"): "ok",
        ("p1", "N1", "context_recall"): "not_applicable",
    }
    assert len(path.read_text(encoding="utf-8").splitlines()) == 6
    assert len(load_ragas_scores(path)) == 4


def test_summary_averages_only_scored_answers():
    def score(question_id, status, value=None):
        return RagasScore(
            variant="p2",
            question_id=question_id,
            metric="faithfulness",
            judge="j",
            status=status,
            value=value,
        )

    rows = [score("S1", "ok", 1.0), score("S2", "ok", 0.5), score("G1", "too_long")]
    rows.append(score("G2", "error"))
    (summary,) = summarize_ragas(rows)
    assert (summary.mean, summary.scored, summary.total) == (0.75, 2, 4)
    assert (summary.too_long, summary.errors) == (1, 1)


def test_report_shows_the_ragas_table_and_a_line_per_answer():
    # Arrange
    question = _question()
    answer = _answer()
    catalog = load_document_catalog(PROJECT_ROOT / "dataset" / "documents.yaml")
    scores = [score_answer(question, answer, catalog)]
    ragas = [
        RagasScore(
            variant="p1",
            question_id="G1",
            metric="faithfulness",
            judge="audit-judge",
            status="ok",
            value=0.8,
        ),
        RagasScore(
            variant="p1",
            question_id="G1",
            metric="context_recall",
            judge="audit-judge",
            status="too_long",
        ),
    ]

    # Act
    report = render_report("r", [question], [answer], scores, summarize(scores), None, ragas)

    # Assert
    assert "| Faithfulness | 0.80 (1/1 bewertet) |" in report
    assert "| Context Recall | - (0/1 bewertet, 1 zu lang) |" in report
    assert "- RAGAS: Context Recall zu lang, Faithfulness 0.80" in report
    assert "`audit-judge`" in report


def test_judge_modelfile_matches_the_settings():
    text = (PROJECT_ROOT / "scripts" / "audit-judge.Modelfile").read_text(encoding="utf-8")
    num_ctx = re.search(r"^PARAMETER num_ctx (\d+)$", text, re.MULTILINE)
    base = re.search(r"^FROM (\S+)$", text, re.MULTILINE)
    assert num_ctx and int(num_ctx.group(1)) == EvaluationSettings().judge_num_ctx
    assert base and base.group(1) in ModelNames().agent_candidates
    assert ModelNames().judge == "audit-judge"


def test_judge_env_override():
    settings = Settings.from_env({"AUDIT_MODEL_JUDGE": "llama3.1:8b"})
    assert settings.models.judge == "llama3.1:8b"


def test_ragas_judge_disables_tracking_and_measures_its_prompts(monkeypatch):
    pytest.importorskip("ragas")
    from audit_agent.evaluation.ragas_eval import RagasJudge

    monkeypatch.setenv(TRACKING_ENV, "false")
    judge = RagasJudge(Settings())  # builds the client only, no request is sent
    assert judge.model == "audit-judge"
    assert os.environ[TRACKING_ENV] == "true"
    short = judge.prompt_chars("faithfulness", "Frage?", "Antwort.", ["kurz"], "Ref.")
    long = judge.prompt_chars("faithfulness", "Frage?", "Antwort.", ["lang " * 500], "Ref.")
    recall = judge.prompt_chars("context_recall", "Frage?", "", ["lang " * 500], "Ref.")
    assert long - short >= 2400 and recall > 2500


def test_the_judge_is_unloaded_only_after_answers_it_judged(tmp_path):
    # Arrange: G1 is judged twice, the N1 answer without evidence is skipped by the pre-checks
    questions = {"G1": _question(), "N1": _negative()}
    answers = [_answer(), _answer("N1", text="Liegt nicht vor.", contexts=())]
    unloaded: list[str] = []

    # Act
    _run(
        evaluate_run(
            answers,
            questions,
            FakeJudge(),
            Settings(),
            ragas_path(tmp_path),
            after_judged=lambda answer: unloaded.append(answer.question_id),
        )
    )

    # Assert
    assert unloaded == ["G1"]
