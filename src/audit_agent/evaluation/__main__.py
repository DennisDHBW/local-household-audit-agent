"""CLI: ``uv run python -m audit_agent.evaluation generate | score`` (concept.md, 11.1).

``generate`` needs Ollama and writes the answers; ``score`` needs nothing but the files and
writes ``scores.json`` and ``report.md``. ``generate`` scores at the end as well.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from ollama import Client, ResponseError

from audit_agent.agent.factory import create_agent
from audit_agent.config import Settings
from audit_agent.corpus import CorpusError, load_document_catalog, load_ground_truth
from audit_agent.enrichment.llm import installed_models
from audit_agent.evaluation.metrics import score_answer, summarize
from audit_agent.evaluation.models import (
    VARIANT_LABELS,
    VARIANT_NAMES,
    EvaluationError,
    VariantName,
)
from audit_agent.evaluation.report import render_report
from audit_agent.evaluation.store import (
    answers_path,
    append_answer,
    check_same_model,
    load_answers,
    load_run,
)
from audit_agent.evaluation.testset import select_questions
from audit_agent.evaluation.variants import (
    AgentVariant,
    FullTextVariant,
    PipelineVariant,
    Variant,
    build_full_text_context,
    needs_index,
)
from audit_agent.preflight import MissingModelError, ensure_models_available
from audit_agent.retrieval import RetrievalError, Retriever, get_collection, open_vector_client

DEFAULT_QUESTION_IDS = ("S2", "G1", "N1")
"""Quick subset: table lookup, audit with a planted error, negative question."""
MANIFEST_FILE = "manifest.json"
logger = logging.getLogger(__name__)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate B0, P1 and P2 on the ground truth")
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="answer questions (needs Ollama)")
    generate.add_argument("--run-id", required=True, help="folder name under data/eval/")
    generate.add_argument(
        "--variants", nargs="+", choices=VARIANT_NAMES, default=list(VARIANT_NAMES)
    )
    generate.add_argument("--ids", nargs="+", default=list(DEFAULT_QUESTION_IDS))
    generate.add_argument("--all", action="store_true", help="all 12 questions")
    generate.add_argument("--model", help="answer model (default: AUDIT_MODEL_AGENT)")

    score = commands.add_parser("score", help="score stored answers (no Ollama needed)")
    score.add_argument("--run-id", required=True)
    return parser


def _read_manifest(run_dir: Path) -> dict[str, object]:
    path = run_dir / MANIFEST_FILE
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _build_variant(
    name: VariantName,
    settings: Settings,
    client: Client,
    run_dir: Path,
    manifest: dict[str, object],
) -> Variant:
    if name == "b0":
        context = build_full_text_context(settings, load_document_catalog(settings.documents_file))
        manifest["b0_context"] = context.model_dump(exclude={"text", "sources"})
        return FullTextVariant(settings, client, context)
    if name == "p1":
        collection = get_collection(settings, open_vector_client(settings))
        return PipelineVariant(settings, client, Retriever(settings, client, collection))
    return AgentVariant(create_agent(settings, client), log_dir=run_dir)


def _generate(args: argparse.Namespace, settings: Settings, client: Client) -> int:
    model = args.model or settings.models.agent
    variants: list[VariantName] = list(dict.fromkeys(args.variants))
    required = [model, settings.models.embedding] if needs_index(variants) else [model]
    ensure_models_available(installed_models(client), required)
    truth = load_ground_truth(settings.ground_truth_file)
    questions = select_questions(truth, None if args.all else args.ids)
    run_dir = settings.eval_dir / args.run_id
    manifest = _read_manifest(run_dir)
    manifest.update({"model": model, "num_ctx": settings.num_ctx})

    for name in variants:
        path = answers_path(run_dir, name)
        done = load_answers(path)
        check_same_model(done, model)
        done_ids = {answer.question_id for answer in done}
        todo = [question for question in questions if question.id not in done_ids]
        if not todo:
            print(f"{VARIANT_LABELS[name]}: alle Fragen schon beantwortet", file=sys.stderr)
            continue
        variant = _build_variant(name, settings, client, run_dir, manifest)
        _write_manifest(run_dir, manifest)
        for question in todo:
            print(
                f"\n== {VARIANT_LABELS[name]} {question.id}: {question.question}", file=sys.stderr
            )
            answer = variant.answer(question, model)
            append_answer(path, answer)
            print(f"   {answer.seconds} s: {answer.answer[:200]}", file=sys.stderr)
    _write_manifest(run_dir, manifest)
    return _score(settings, args.run_id)


def _write_manifest(run_dir: Path, manifest: dict[str, object]) -> None:
    """Written before the first answer, so an interrupted run still documents its setup."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / MANIFEST_FILE).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _score(settings: Settings, run_id: str) -> int:
    run_dir = settings.eval_dir / run_id
    answers = load_run(run_dir)
    truth = load_ground_truth(settings.ground_truth_file)
    catalog = load_document_catalog(settings.documents_file)
    by_id = {question.id: question for question in truth.questions}
    unknown = sorted({a.question_id for a in answers} - by_id.keys())
    if unknown:
        raise EvaluationError(f"answers for unknown questions: {unknown}")
    scores = [score_answer(by_id[a.question_id], a, catalog) for a in answers]
    summaries = summarize(scores)
    payload = {
        "summaries": [s.model_dump(mode="json") for s in summaries],
        "scores": [s.model_dump(mode="json") for s in scores],
    }
    (run_dir / "scores.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = render_report(
        run_id, truth.questions, answers, scores, summaries, _read_manifest(run_dir)
    )
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"report: {run_dir / 'report.md'}")
    return 0


def _unload(client: Client, models: list[str]) -> None:
    for model in models:
        try:
            client.generate(model=model, prompt="", keep_alive=0)
        except (ResponseError, ConnectionError) as error:
            logger.warning("could not unload %s: %s", model, error)


def main() -> int:
    args = _parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = Settings.from_env()
    try:
        if args.command == "score":
            return _score(settings, args.run_id)
        client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)
        try:
            return _generate(args, settings, client)
        finally:
            _unload(client, [args.model or settings.models.agent, settings.models.embedding])
    except (EvaluationError, RetrievalError, MissingModelError, CorpusError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except ConnectionError as error:
        print(
            f"ERROR: {error}\nFertige Antworten sind gespeichert; nach dem Neustart von "
            "Ollama setzt derselbe Befehl den Lauf fort.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
