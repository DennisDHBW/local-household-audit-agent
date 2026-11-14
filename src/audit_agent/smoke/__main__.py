"""Entry point: ``uv run python -m audit_agent.smoke [--run-id run-000]``."""

from __future__ import annotations

import argparse
from datetime import datetime

from ollama import Client

from audit_agent.config import Settings
from audit_agent.smoke.report import render_markdown
from audit_agent.smoke.runner import run_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test of the local Ollama setup")
    parser.add_argument("--run-id", default="run-000")
    args = parser.parse_args()

    settings = Settings.from_env()
    out_dir = settings.eval_dir / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)

    report = run_all(
        client,
        settings,
        args.run_id,
        datetime.now().astimezone().isoformat(timespec="seconds"),
        out_dir,
    )
    (out_dir / "smoke.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / "smoke.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"Done. Results: {out_dir / 'smoke.json'} and {out_dir / 'smoke.md'}")
    if report.errors:
        print(f"{len(report.errors)} step(s) failed, see smoke.md")


if __name__ == "__main__":
    main()
