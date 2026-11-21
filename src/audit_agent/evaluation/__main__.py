"""CLI: ``uv run python -m audit_agent.evaluation generate | score | ragas`` (concept.md, 11).

``generate`` needs Ollama and writes the answers; ``score`` needs nothing but the files and
writes ``scores.json`` and ``report.md``; ``ragas`` judges the stored answers with a local
model (ADR-0012). ``generate`` and ``ragas`` score at the end as well.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

import httpx
from ollama import Client, ResponseError

from audit_agent.agent.factory import create_agent
from audit_agent.config import Settings
from audit_agent.corpus import (
    CorpusError,
    GroundTruth,
    Question,
    load_document_catalog,
    load_ground_truth,
    load_question_set,
)
from audit_agent.enrichment.llm import installed_models
from audit_agent.evaluation.metrics import score_answer, summarize, uses_tool_set_v2
from audit_agent.evaluation.models import (
    VARIANT_LABELS,
    VARIANT_NAMES,
    EvaluationError,
    VariantName,
)
from audit_agent.evaluation.ragas_eval import (
    RAGAS_LABELS,
    RAGAS_METRICS,
    RagasJudge,
    RagasScore,
    evaluate_run,
    load_ragas_scores,
    ragas_path,
    summarize_ragas,
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
    unloads_after_each_question,
)
from audit_agent.preflight import MissingModelError, ensure_models_available, find_missing_models
from audit_agent.retrieval import RetrievalError, Retriever, get_collection, open_vector_client

JUDGE_MODELFILE = "scripts/audit-judge.Modelfile"
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
    generate.add_argument("--all", action="store_true", help="all questions of the catalog")
    generate.add_argument(
        "--holdout",
        action="store_true",
        help="the held-out questions of holdout_questions.yaml (final run only, ISS-108)",
    )
    generate.add_argument("--model", help="answer model (default: AUDIT_MODEL_AGENT)")

    score = commands.add_parser("score", help="score stored answers (no Ollama needed)")
    score.add_argument("--run-id", required=True)

    ragas = commands.add_parser("ragas", help="judge stored answers with RAGAS (needs Ollama)")
    ragas.add_argument("--run-id", required=True)
    ragas.add_argument("--variants", nargs="+", choices=VARIANT_NAMES, default=list(VARIANT_NAMES))
    ragas.add_argument("--metrics", nargs="+", choices=RAGAS_METRICS, default=list(RAGAS_METRICS))
    ragas.add_argument("--judge", help="judge model (default: AUDIT_MODEL_JUDGE)")
    ragas.add_argument("--retry-errors", action="store_true", help="judge failed answers again")
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
        manifest["b0_context"] = context.model_dump(exclude={"text", "blocks", "sources"})
        return FullTextVariant(settings, client, context)
    if name == "p1":
        collection = get_collection(settings, open_vector_client(settings))
        return PipelineVariant(settings, client, Retriever(settings, client, collection))
    return AgentVariant(create_agent(settings, client), log_dir=run_dir)


def _generate(args: argparse.Namespace, settings: Settings, client: Client) -> int:
    model = args.model or settings.models.agent
    variants: list[VariantName] = list(dict.fromkeys(args.variants))
    used_models = [model, settings.models.embedding] if needs_index(variants) else [model]
    ensure_models_available(installed_models(client), used_models)
    truth = load_ground_truth(settings.ground_truth_file)
    if args.holdout:
        questions = list(load_question_set(settings.holdout_file).questions)
    else:
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
        # Free the RAM (model and Ollama's prompt cache) before each variant (ISS-043).
        _unload(client, used_models)
        variant = _build_variant(name, settings, client, run_dir, manifest)
        _write_manifest(run_dir, manifest)
        for question in todo:
            print(
                f"\n== {VARIANT_LABELS[name]} {question.id}: {question.question}", file=sys.stderr
            )
            answer = variant.answer(question, model)
            append_answer(path, answer)
            print(f"   {answer.seconds} s: {answer.answer[:200]}", file=sys.stderr)
            if unloads_after_each_question(name):
                _unload(client, used_models)
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
    by_id = {question.id: question for question in _all_questions(settings, truth)}
    unknown = sorted({a.question_id for a in answers} - by_id.keys())
    if unknown:
        raise EvaluationError(f"answers for unknown questions: {unknown}")
    is_v2 = uses_tool_set_v2(answers)
    scores = [score_answer(by_id[a.question_id], a, catalog, is_v2) for a in answers]
    summaries = summarize(scores)
    ragas = load_ragas_scores(ragas_path(run_dir))
    payload = {
        "summaries": [s.model_dump(mode="json") for s in summaries],
        "ragas": [s.model_dump(mode="json") for s in summarize_ragas(ragas)],
        "scores": [s.model_dump(mode="json") for s in scores],
    }
    (run_dir / "scores.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = render_report(
        run_id,
        _all_questions(settings, truth),
        answers,
        scores,
        summaries,
        _read_manifest(run_dir),
        ragas,
    )
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"report: {run_dir / 'report.md'}")
    return 0


def _ragas(args: argparse.Namespace, settings: Settings, client: Client) -> int:
    judge_model = args.judge or settings.models.judge
    if find_missing_models(installed_models(client), [judge_model]):
        raise EvaluationError(
            f"judge model {judge_model} is missing; run once: "
            f"ollama create {judge_model} -f {JUDGE_MODELFILE}"
        )
    run_dir = settings.eval_dir / args.run_id
    variants = set(args.variants)
    answers = [answer for answer in load_run(run_dir) if answer.variant in variants]
    answer_models = sorted({answer.model for answer in answers})
    _unload(client, [*answer_models, settings.models.embedding])  # RAM for the judge (ISS-043)
    truth = load_ground_truth(settings.ground_truth_file)
    judge = RagasJudge(settings, judge_model)
    manifest = _read_manifest(run_dir)
    manifest["ragas"] = {
        "judge": judge_model,
        "judge_num_ctx": settings.evaluation.judge_num_ctx,
        "judge_max_tokens": settings.evaluation.judge_max_tokens,
        "metrics": list(args.metrics),
    }
    _write_manifest(run_dir, manifest)

    def report(score: RagasScore) -> None:
        value = "" if score.value is None else f" {score.value:.2f}"
        print(
            f"   {VARIANT_LABELS[score.variant]} {score.question_id} "
            f"{RAGAS_LABELS[score.metric]}: {score.status}{value} ({score.seconds} s) "
            f"{score.detail}",
            file=sys.stderr,
        )

    try:
        asyncio.run(
            evaluate_run(
                answers,
                {question.id: question for question in _all_questions(settings, truth)},
                judge,
                settings,
                ragas_path(run_dir),
                metrics=args.metrics,
                retry_errors=args.retry_errors,
                on_score=report,
                after_judged=lambda _answer: _unload(client, [judge_model]),
            )
        )
    finally:
        _unload(client, [judge_model])
    return _score(settings, args.run_id)


def _unload(client: Client, models: list[str]) -> None:
    for model in models:
        try:
            client.generate(model=model, prompt="", keep_alive=0)
        except (ResponseError, ConnectionError, httpx.TransportError) as error:
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
        if args.command == "ragas":
            return _ragas(args, settings, client)
        try:
            return _generate(args, settings, client)
        finally:
            _unload(client, [args.model or settings.models.agent, settings.models.embedding])
    except (EvaluationError, RetrievalError, MissingModelError, CorpusError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except (ConnectionError, httpx.TransportError) as error:
        # httpx.TransportError: Ollama died in the middle of a request (RUN-010, ISS-049)
        print(
            f"ERROR: {error}\nFertige Antworten sind gespeichert; nach dem Neustart von "
            "Ollama setzt derselbe Befehl den Lauf fort.",
            file=sys.stderr,
        )
        return 1


def _all_questions(settings: Settings, truth: GroundTruth) -> list[Question]:
    """Development questions plus the held-out ones (if the file exists)."""
    questions = list(truth.questions)
    if settings.holdout_file.is_file():
        questions += list(load_question_set(settings.holdout_file).questions)
    return questions


if __name__ == "__main__":
    sys.exit(main())
