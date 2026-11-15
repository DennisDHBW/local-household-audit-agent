"""CLI: ``uv run python -m audit_agent.retrieval index | search | compare``."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from ollama import Client, ResponseError

from audit_agent.config import Settings
from audit_agent.corpus import (
    CorpusError,
    DocType,
    UtilityType,
    load_document_catalog,
    load_ground_truth,
)
from audit_agent.enrichment.llm import installed_models
from audit_agent.ingestion import ChunkType
from audit_agent.preflight import MissingModelError, ensure_models_available
from audit_agent.retrieval.compare import render_markdown, run_comparison
from audit_agent.retrieval.evidence import build_evidence, render_evidence_text
from audit_agent.retrieval.index import build_index, get_collection, open_vector_client
from audit_agent.retrieval.models import MetadataFilter, RetrievalError, SearchOptions
from audit_agent.retrieval.search import Retriever


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Index and search the household documents")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("index", help="rebuild the vector index from data/processed")

    search = commands.add_parser("search", help="search and print the evidence")
    search.add_argument("query")
    search.add_argument("--utility-type", choices=[u.value for u in UtilityType])
    search.add_argument("--doc-type", choices=[d.value for d in DocType])
    search.add_argument("--contract-id")
    search.add_argument("--year", type=int, help="billing period overlaps this calendar year")
    search.add_argument("--no-boost", action="store_true", help="switch the hierarchy boost off")
    search.add_argument("--types", nargs="+", choices=[t.value for t in ChunkType])
    search.add_argument("--require-heading", action="store_true")
    search.add_argument("--top-k", type=int)

    compare = commands.add_parser("compare", help="compare filter/boost on the question catalog")
    compare.add_argument("--run-id", default="retrieval", help="folder name under data/eval/")
    return parser


def _filter_from(args: argparse.Namespace) -> MetadataFilter:
    fields = {
        "utility_type": UtilityType(args.utility_type) if args.utility_type else None,
        "doc_type": DocType(args.doc_type) if args.doc_type else None,
        "contract_id": args.contract_id,
    }
    if args.year:
        return MetadataFilter.for_year(args.year, **fields)
    return MetadataFilter(**fields)


def _unload(client: Client, model: str) -> None:
    try:
        client.generate(model=model, prompt="", keep_alive=0)
    except ResponseError as error:
        logging.getLogger(__name__).warning("could not unload %s: %s", model, error)


def _run(args: argparse.Namespace, settings: Settings, client: Client) -> int:
    model = settings.models.embedding
    ensure_models_available(installed_models(client), [model])
    vector_client = open_vector_client(settings)

    if args.command == "index":
        report = build_index(settings, client, vector_client)
        print(f"{report.chunk_count} chunks from {report.document_count} documents indexed")
        print(f"by type: {report.chunks_by_type}, headings skipped: {report.skipped_headings}")
        print(f"{report.embedding_model}, {report.vector_dimension} dimensions, {report.seconds} s")
        return 0

    retriever = Retriever(settings, client, get_collection(settings, vector_client))
    if args.command == "search":
        options = SearchOptions(
            metadata_filter=_filter_from(args),
            use_hierarchy_boost=not args.no_boost,
            chunk_types=frozenset(ChunkType(t) for t in args.types) if args.types else None,
            require_heading=args.require_heading,
            top_k=args.top_k,
        )
        hits = retriever.search(args.query, options)
        print(render_evidence_text(build_evidence(hits)) or "(keine Treffer)")
        return 0

    truth = load_ground_truth(settings.ground_truth_file)
    catalog = load_document_catalog(settings.documents_file)
    report = run_comparison(retriever, truth, catalog, settings.retrieval.top_k)
    out_dir = settings.eval_dir / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "retrieval.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    markdown = render_markdown(report)
    (out_dir / "retrieval.md").write_text(markdown + "\n", encoding="utf-8")
    print(markdown.split("## Rang")[0])
    print(f"report: {out_dir / 'retrieval.md'} (generated {date.today().isoformat()})")
    return 0


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
        _unload(client, settings.models.embedding)


if __name__ == "__main__":
    sys.exit(main())
