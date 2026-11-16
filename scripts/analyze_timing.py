"""Split the P2 time of stored runs into prefill and decode, first call and later calls (ISS-057).

Reads the step logs ``data/eval/<run-id>/p2-*.jsonl`` (written by the agent loop). The first
model call of a question carries the system prompt and the tool descriptions; if Ollama
re-uses them from its prompt cache, its prefill takes seconds instead of about 90 s.
Needs no Ollama.

    uv run python scripts/analyze_timing.py --run-id run-010 --run-id run-012
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from audit_agent.config import Settings

CACHE_HIT_MAX_SECONDS = 20.0
"""A first call with less prefill than this was served (mostly) from the prompt cache."""


def model_calls(path: Path) -> list[dict[str, Any]]:
    """The ``model_call`` records of one step log, in order."""
    records = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line)
    return [record for record in records if record.get("kind") == "model_call"]


def summarize(logs: list[list[dict[str, Any]]]) -> dict[str, float]:
    """Seconds and counts over all questions of a run (calls without timing count as 0)."""
    first = [calls[0] for calls in logs if calls]
    later = [call for calls in logs for call in calls[1:]]
    prefill = lambda calls: sum(call["prefill_seconds"] or 0 for call in calls)  # noqa: E731
    return {
        "questions": len(first),
        "model_calls": len(first) + len(later),
        "wall_seconds": round(sum(c["seconds"] for c in first + later), 1),
        "prefill_first_calls": round(prefill(first), 1),
        "first_calls_from_cache": sum(
            1 for call in first if (call["prefill_seconds"] or 0) < CACHE_HIT_MAX_SECONDS
        ),
        "prefill_later_calls": round(prefill(later), 1),
        "prompt_tokens_later_calls": sum(call["prompt_tokens"] or 0 for call in later),
        "decode_seconds": round(sum(c["decode_seconds"] or 0 for c in first + later), 1),
        "generated_tokens": sum(c["generated_tokens"] or 0 for c in first + later),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", action="append", required=True, help="folder under data/eval/")
    args = parser.parse_args(argv)
    eval_dir = Settings.from_env().eval_dir
    result = {
        run_id: summarize([model_calls(p) for p in sorted((eval_dir / run_id).glob("p2-*.jsonl"))])
        for run_id in args.run_id
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
