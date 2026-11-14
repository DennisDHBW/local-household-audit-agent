"""CLI: ``uv run python -m audit_agent.agent ask "<Frage>" | run-set``."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from ollama import Client, ResponseError

from audit_agent.agent.factory import create_agent
from audit_agent.agent.log import RunLog
from audit_agent.agent.models import AgentRun, AgentStep, EvidenceBook, NudgeStep, ToolCallStep
from audit_agent.agent.report import render_markdown
from audit_agent.config import Settings
from audit_agent.corpus import CorpusError, Question, load_ground_truth
from audit_agent.enrichment.llm import installed_models
from audit_agent.evaluation.testset import select_questions
from audit_agent.preflight import MissingModelError, ensure_models_available
from audit_agent.retrieval import RetrievalError

DEFAULT_QUESTION_IDS = ("S2", "G1", "N1", "S4")
"""Table lookup, audit with calculation, negative question, chart (RUN-005)."""
logger = logging.getLogger(__name__)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask the audit agent (needs Ollama)")
    commands = parser.add_subparsers(dest="command", required=True)

    ask = commands.add_parser("ask", help="answer one question")
    ask.add_argument("question")
    ask.add_argument("--model", help="agent model (default: AUDIT_MODEL_AGENT)")
    ask.add_argument("--run-id", default="agent-adhoc", help="folder name under data/eval/")

    run_set = commands.add_parser("run-set", help="answer questions of the ground truth")
    run_set.add_argument("--ids", nargs="+", default=list(DEFAULT_QUESTION_IDS))
    run_set.add_argument("--all", action="store_true", help="all 12 questions")
    run_set.add_argument("--model", help="agent model (default: AUDIT_MODEL_AGENT)")
    run_set.add_argument("--run-id", default="agent", help="folder name under data/eval/")
    return parser


def _print_step(step: AgentStep, book: EvidenceBook) -> None:
    """Live progress on stderr: one line per step (a question takes minutes)."""
    if isinstance(step, ToolCallStep):
        state = "ok" if step.is_valid else "FEHLER"
        print(f"  Tool {step.tool} {step.arguments} -> {state} ({step.seconds} s)", file=sys.stderr)
    elif isinstance(step, NudgeStep):
        print("  Rückfrage: Antwort „keine Angaben“ nach zu wenigen Suchen", file=sys.stderr)
    else:
        calls = ", ".join(call.name for call in step.tool_calls) or "Antwort"
        print(
            f"  Modell: {step.seconds} s, Prompt {step.prompt_tokens} Token -> {calls}",
            file=sys.stderr,
        )


def _answer(agent, question: str, model: str, log_path: Path) -> AgentRun:
    log = RunLog(log_path)

    def on_step(step: AgentStep, book: EvidenceBook) -> None:
        log(step, book)
        _print_step(step, book)

    run = agent.run(question, model=model, on_step=on_step)
    log.finish(run)
    return run


def _print_run(run: AgentRun) -> None:
    print(f"\n{run.answer}\n")
    print(f"[{run.stop_reason}, {run.tool_call_count} Werkzeugaufrufe, {run.seconds} s]")
    for source in run.sources:
        hit = source.hit
        print(f"  [{source.number}] {Path(hit.filename).name}, S. {hit.page_number}")


def _run(args: argparse.Namespace, settings: Settings, client: Client) -> int:
    model = args.model or settings.models.agent
    ensure_models_available(installed_models(client), [model, settings.models.embedding])
    agent = create_agent(settings, client)
    out_dir = settings.eval_dir / args.run_id

    if args.command == "ask":
        log_path = out_dir / f"ask-{time.strftime('%H%M%S')}.jsonl"
        _print_run(_answer(agent, args.question, model, log_path))
        print(f"log: {log_path}")
        return 0

    results: list[tuple[Question, AgentRun]] = []
    truth = load_ground_truth(settings.ground_truth_file)
    for question in select_questions(truth, None if args.all else args.ids):
        print(f"\n== {question.id}: {question.question}", file=sys.stderr)
        run = _answer(agent, question.question, model, out_dir / f"agent-{question.id}.jsonl")
        _print_run(run)
        results.append((question, run))
    report = render_markdown(model, results)
    (out_dir / "agent.md").write_text(report, encoding="utf-8")
    runs_json = "[" + ",\n".join(run.model_dump_json() for _, run in results) + "]\n"
    (out_dir / "agent.json").write_text(runs_json, encoding="utf-8")
    print(f"\nreport: {out_dir / 'agent.md'}")
    return 0


def _unload(client: Client, models: list[str]) -> None:
    for model in models:
        try:
            client.generate(model=model, prompt="", keep_alive=0)
        except ResponseError as error:
            logger.warning("could not unload %s: %s", model, error)


def main() -> int:
    args = _parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = Settings.from_env()
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)
    try:
        return _run(args, settings, client)
    except (RetrievalError, MissingModelError, CorpusError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    finally:
        _unload(client, [args.model or settings.models.agent, settings.models.embedding])


if __name__ == "__main__":
    sys.exit(main())
