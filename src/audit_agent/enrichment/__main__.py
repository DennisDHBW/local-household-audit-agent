"""CLI: ``uv run python -m audit_agent.enrichment`` adds captions and table summaries."""

from __future__ import annotations

import argparse
import logging
import sys

from ollama import Client

from audit_agent.config import Settings
from audit_agent.enrichment.llm import EnrichmentError
from audit_agent.enrichment.pipeline import EnrichmentKind, run_enrichment
from audit_agent.preflight import MissingModelError


def main() -> int:
    parser = argparse.ArgumentParser(description="Add image captions and table summaries")
    parser.add_argument("--only", choices=[kind.value for kind in EnrichmentKind])
    parser.add_argument("--limit", type=int, help="at most N jobs per kind (trial run)")
    parser.add_argument("--dry-run", action="store_true", help="only count open jobs")
    parser.add_argument("--run-id", default="enrichment", help="folder name under data/eval/")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = Settings.from_env()
    kinds = frozenset([EnrichmentKind(args.only)] if args.only else EnrichmentKind)
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)

    try:
        report = run_enrichment(
            settings, client, kinds=kinds, limit=args.limit, is_dry_run=args.dry_run
        )
    except (EnrichmentError, MissingModelError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"{len(report.items)} jobs: {report.cache_hits} from cache, "
        f"{report.cache_misses} {'still open' if report.is_dry_run else 'computed'}"
    )
    if report.is_dry_run:
        return 0
    seconds = sum(item.seconds or 0 for item in report.items if not item.is_cache_hit)
    print(f"model time of this run: {seconds / 60:.1f} min")
    print(f"summaries with numbers not found in the table: {len(report.flagged_summaries)}")
    out_dir = settings.eval_dir / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "enrichment.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(f"report: {out_dir / 'enrichment.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
