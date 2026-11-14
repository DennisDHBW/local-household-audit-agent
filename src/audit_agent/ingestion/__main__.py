"""CLI: ``uv run python -m audit_agent.ingestion`` parses all PDFs into ``data/processed/``."""

from __future__ import annotations

import logging
import sys

from audit_agent.config import Settings
from audit_agent.corpus import CorpusError
from audit_agent.ingestion.parser import ParseError
from audit_agent.ingestion.pipeline import run_ingestion


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    settings = Settings.from_env()
    try:
        report = run_ingestion(settings)
    except (CorpusError, ParseError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{report.documents} documents, {report.total_chunks} chunks: {report.chunks_by_type}")
    print(f"written to {settings.processed_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
