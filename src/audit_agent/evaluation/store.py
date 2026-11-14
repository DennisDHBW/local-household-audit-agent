"""Answers of a run as JSON lines: ``data/eval/<run>/answers-<variant>.jsonl``.

One line is written as soon as an answer is finished, so an interrupted night run keeps
everything done so far and can be resumed with the same command.
"""

from __future__ import annotations

from pathlib import Path

from audit_agent.evaluation.models import (
    VARIANT_NAMES,
    EvaluationError,
    VariantAnswer,
    VariantName,
)


def answers_path(run_dir: Path, variant: VariantName) -> Path:
    return run_dir / f"answers-{variant}.jsonl"


def load_answers(path: Path) -> list[VariantAnswer]:
    """All answers of one file (empty list if the file does not exist yet)."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [VariantAnswer.model_validate_json(line) for line in lines if line.strip()]


def append_answer(path: Path, answer: VariantAnswer) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(answer.model_dump_json() + "\n")


def load_run(run_dir: Path) -> list[VariantAnswer]:
    """Answers of all variants of a run, B0 first; fails if there are none."""
    answers = [a for name in VARIANT_NAMES for a in load_answers(answers_path(run_dir, name))]
    if not answers:
        raise EvaluationError(f"no answers in {run_dir}; run `generate` first")
    return answers


def check_same_model(answers: list[VariantAnswer], model: str) -> None:
    """Fail fast if a run would mix models (resume only with the model it started with)."""
    others = sorted({answer.model for answer in answers} - {model})
    if others:
        raise EvaluationError(
            f"this run already holds answers of {others}; use a new --run-id for {model}"
        )
