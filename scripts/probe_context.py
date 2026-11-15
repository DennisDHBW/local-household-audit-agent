"""Measure how many prompt tokens Ollama really processes (ISS-041).

Sends three prompts of about 1.500, 3.000 and 6.000 tokens with ``num_ctx`` from the
settings and asks for the number in line 0. Writes ``prompt_eval_count``, the answer and the
loaded model's details from ``ollama ps`` to ``data/eval/<run-id>/context-probe.json``.

If the long prompt reports about 4.096 tokens or loses line 0, Ollama cuts the prompt and
the configured ``num_ctx`` is not in effect. Needs Ollama; takes about 10 minutes on the CPU.

    uv run python scripts/probe_context.py --run-id run-007
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from ollama import Client

from audit_agent.agent.loop import chat_arguments
from audit_agent.config import Settings

LINE = "Zeile {n}: Der Zählerstand am Monatsende betrug {value} Kilowattstunden.\n"
QUESTION = "Welche Zahl steht in Zeile 0? Antworte nur mit der Zahl."
LINE_COUNTS = (75, 150, 300)
"""About 20 tokens per line: roughly 1.500, 3.000 and 6.000 prompt tokens."""


def _prompt(line_count: int) -> str:
    # Each prompt starts differently, so Ollama cannot reuse a cached prefix.
    header = f"Messreihe mit {line_count} Zeilen.\n"
    lines = "".join(LINE.format(n=i, value=7000 + i * 3) for i in range(line_count))
    return header + lines + QUESTION


def _loaded_models(client: Client) -> list[dict[str, Any]]:
    return [model.model_dump(mode="json") for model in client.ps().models]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", help="default: AUDIT_MODEL_AGENT")
    args = parser.parse_args()
    settings = Settings.from_env()
    model = args.model or settings.models.agent
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)

    results: list[dict[str, Any]] = []
    loaded: list[dict[str, Any]] = []
    for line_count in LINE_COUNTS:
        prompt = _prompt(line_count)
        arguments = chat_arguments(settings, model, [{"role": "user", "content": prompt}])
        arguments["options"]["num_predict"] = 16
        response = client.chat(**arguments)
        loaded = _loaded_models(client)
        result = {
            "lines": line_count,
            "prompt_chars": len(prompt),
            "num_ctx_requested": settings.num_ctx,
            "prompt_eval_count": response.prompt_eval_count,
            "prefill_seconds": (response.prompt_eval_duration or 0) / 1e9,
            "answer": (response.message.content or "").strip(),
            "expected_answer": "7000",
        }
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
    client.generate(model=model, prompt="", keep_alive=0)

    out = settings.eval_dir / args.run_id / "context-probe.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "results": results, "ollama_ps": loaded}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"probe: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
