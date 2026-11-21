"""Agentic behaviour of stored P2 runs: plans, self-checks, repeats, stop reasons (ISS-117).

Reads the step logs ``data/eval/<run-id>/p2-*.jsonl`` and the answers ``answers-p2.jsonl``.
The counts describe how the agent worked, not whether it was right (that is ``report.md``).
"Worse after a question" uses today's ``strip_step_talk``: a real answer existed before a
self-check or follow-up question, the final answer is empty, a gap or only announced steps.
Needs no Ollama.

    uv run python scripts/analyze_agentics.py --run-id run-025 [--write]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from audit_agent.agent.prompts import is_english, is_gap_answer, strip_step_talk
from audit_agent.config import Settings

_CITATION = re.compile(r"\[(\d+)\]")


def _records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _is_real(answer: str) -> bool:
    cleaned = strip_step_talk(answer)
    return bool(cleaned) and not is_gap_answer(cleaned)


def question_metrics(steps: list[dict[str, Any]], answer: dict[str, Any]) -> dict[str, Any]:
    """Counts of one question from its step log and its answer record."""
    calls = [s for s in steps if s["kind"] == "tool_call"]
    models = [s for s in steps if s["kind"] == "model_call"]
    nudges = [s for s in steps if s["kind"] == "nudge"]
    final = answer["answer"]
    real_before_nudge = False
    for index, step in enumerate(steps):
        if step["kind"] != "nudge":
            continue
        previous = [s for s in steps[:index] if s["kind"] == "model_call" and not s["tool_calls"]]
        if previous and _is_real(previous[-1]["content"]):
            real_before_nudge = True
    numbers = {int(n) for n in _CITATION.findall(final)}
    return {
        "stop_reason": answer["stop_reason"],
        "model_calls": len(models),
        "tool_calls": len(calls),
        "invalid_calls": sum(1 for c in calls if not c["is_valid"] and not c["is_repeat"]),
        "repeats": sum(1 for c in calls if c["is_repeat"]),
        "text_calls": sum(1 for c in calls if c.get("is_text_call")),
        "repaired_calls": sum(
            1 for c in calls if c["observation"].startswith("Hinweis: Argumente")
        ),
        "tools": [c["tool"] for c in calls],
        "plan_called": any(c["tool"] == "plan" and c["is_valid"] for c in calls),
        "plan_first": bool(calls) and calls[0]["tool"] == "plan",
        "nudges": [n.get("reason", "gap") for n in nudges],
        "final_has_step_talk": strip_step_talk(final) != final.strip(),
        "final_only_steps": bool(final.strip()) and not strip_step_talk(final),
        "final_english": is_english(final),
        "worse_after_question": real_before_nudge and not _is_real(final),
        "invented_citations": sorted(n for n in numbers if n > len(answer.get("sources", []))),
        "artifacts": answer.get("artifact_kinds") or [],
        "seconds": answer["seconds"],
        "prefill_seconds": sum(m.get("prefill_seconds") or 0 for m in models),
        "decode_seconds": sum(m.get("decode_seconds") or 0 for m in models),
    }


def summarize(per_question: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Totals over all questions of a run."""
    rows = list(per_question.values())
    count = len(rows) or 1
    which = lambda key: sorted(q for q, m in per_question.items() if m[key])  # noqa: E731
    seconds = sum(m["seconds"] for m in rows)
    return {
        "questions": len(rows),
        "stop_reasons": dict(Counter(m["stop_reason"] for m in rows)),
        "model_calls_mean": round(sum(m["model_calls"] for m in rows) / count, 1),
        "tool_calls_mean": round(sum(m["tool_calls"] for m in rows) / count, 1),
        "tool_use": dict(Counter(t for m in rows for t in m["tools"]).most_common()),
        "invalid_calls": sum(m["invalid_calls"] for m in rows),
        "repeats": sum(m["repeats"] for m in rows),
        "text_calls": sum(m["text_calls"] for m in rows),
        "repaired_calls": sum(m["repaired_calls"] for m in rows),
        "plan_called": which("plan_called"),
        "plan_first": which("plan_first"),
        "nudges": dict(Counter(r for m in rows for r in m["nudges"]).most_common()),
        "questions_with_nudge": sorted(q for q, m in per_question.items() if m["nudges"]),
        "final_has_step_talk": which("final_has_step_talk"),
        "final_only_steps": which("final_only_steps"),
        "final_english": which("final_english"),
        "worse_after_question": which("worse_after_question"),
        "invented_citations": {
            q: m["invented_citations"] for q, m in per_question.items() if m["invented_citations"]
        },
        "artifacts": dict(Counter(a for m in rows for a in m["artifacts"])),
        "seconds_mean": round(seconds / count, 1),
        "prefill_share": round(sum(m["prefill_seconds"] for m in rows) / seconds, 2)
        if seconds
        else 0,
        "decode_share": round(sum(m["decode_seconds"] for m in rows) / seconds, 2)
        if seconds
        else 0,
    }


def analyze(run_dir: Path) -> dict[str, Any]:
    answers = {a["question_id"]: a for a in _records(run_dir / "answers-p2.jsonl")}
    per_question = {
        qid: question_metrics(_records(run_dir / f"p2-{qid}.jsonl"), answer)
        for qid, answer in answers.items()
        if (run_dir / f"p2-{qid}.jsonl").exists()
    }
    return {"summary": summarize(per_question), "questions": per_question}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", action="append", required=True, help="folder under data/eval/")
    parser.add_argument("--write", action="store_true", help="write <run>/agentics.json")
    args = parser.parse_args(argv)
    eval_dir = Settings.from_env().eval_dir
    for run_id in args.run_id:
        result = analyze(eval_dir / run_id)
        print(f"== {run_id}")
        print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
        if args.write:
            target = eval_dir / run_id / "agentics.json"
            target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"geschrieben: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
