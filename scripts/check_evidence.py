"""Check per stored answer whether the expected facts were in the model's context (M6c).

Separates "the evidence never reached the model" (context budget, retrieval, tool choice,
filter) from "the evidence was there, the answer is still wrong" (synthesis). Also lists
the RAGAS values next to this check, because Context Recall should follow it, and marks
answers that consist only of the gap sentence. Uses the fact matcher of the metrics, so it
shares its limits (ISS-038, ISS-050). Needs no Ollama.

Writes ``data/eval/<run-id>/evidence.json`` and prints a summary.

    uv run python scripts/check_evidence.py --run-id run-010
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any

from audit_agent.agent.prompts import GAP_ANSWER
from audit_agent.config import Settings
from audit_agent.corpus.loader import load_ground_truth, load_question_set
from audit_agent.corpus.models import Question
from audit_agent.evaluation.metrics import is_fact_in_answer
from audit_agent.evaluation.models import VariantAnswer
from audit_agent.evaluation.ragas_eval import RagasScore, load_ragas_scores, ragas_path
from audit_agent.evaluation.store import load_run

GAP_ONLY_MAX_CHARS = 200
"""A longer answer says more than the gap sentence and counts as a normal answer."""
RECALL_THRESHOLD = 0.5


def is_gap_only(answer: str) -> bool:
    text = answer.strip()
    return text.startswith(GAP_ANSWER) and len(text) < GAP_ONLY_MAX_CHARS


def _ragas_value(
    scores: dict[tuple[str, str, str], RagasScore], key: tuple[str, str, str]
) -> float | None:
    score = scores.get(key)
    return score.value if score is not None and score.status == "ok" else None


def evidence_row(
    question: Question,
    answer: VariantAnswer,
    shown_files: set[str],
    ragas: dict[tuple[str, str, str], RagasScore],
) -> dict[str, Any]:
    context = "\n".join(answer.contexts)
    return {
        "variant": answer.variant,
        "question_id": question.id,
        "facts_in_context": [is_fact_in_answer(fact, context) for fact in question.facts],
        "facts_in_answer": [is_fact_in_answer(fact, answer.answer) for fact in question.facts],
        "sources_shown": [source.file in shown_files for source in question.sources],
        "is_gap_only": is_gap_only(answer.answer),
        "faithfulness": _ragas_value(ragas, (answer.variant, question.id, "faithfulness")),
        "context_recall": _ragas_value(ragas, (answer.variant, question.id, "context_recall")),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts for the evaluation log: recall against the fact check, gap-only answers."""
    recall = Counter(
        (all(row["facts_in_context"]), row["context_recall"] >= RECALL_THRESHOLD)
        for row in rows
        if row["context_recall"] is not None and row["facts_in_context"]
    )
    gap_values = Counter(row["faithfulness"] for row in rows if row["is_gap_only"])
    return {
        "recall_agrees": recall[(True, True)] + recall[(False, False)],
        "recall_high_without_facts": recall[(False, True)],
        "recall_low_with_facts": recall[(True, False)],
        "gap_only_faithfulness": {str(value): count for value, count in gap_values.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True, help="folder name under data/eval/")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    run_dir = settings.eval_dir / args.run_id
    questions = {q.id: q for q in load_ground_truth(settings.ground_truth_file).questions}
    if settings.holdout_file.is_file():  # held-out run (ISS-108)
        questions |= {q.id: q for q in load_question_set(settings.holdout_file).questions}
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    full_text_files = set(manifest.get("b0_context", {}).get("complete_files", []))
    ragas = {score.key: score for score in load_ragas_scores(ragas_path(run_dir))}

    rows = []
    for answer in load_run(run_dir):
        shown = (
            full_text_files
            if answer.variant == "b0"
            else {source.filename for source in answer.sources}
        )
        rows.append(evidence_row(questions[answer.question_id], answer, shown, ragas))

    result = {"run_id": args.run_id, "summary": summarize(rows), "rows": rows}
    out_file = run_dir / "evidence.json"
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"evidence: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
