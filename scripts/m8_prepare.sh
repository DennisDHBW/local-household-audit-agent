#!/usr/bin/env bash
# M8 preparation (ADR-0018/0019): one command for everything that needs Ollama before the
# night run. New PDFs 31-35 -> ingestion -> enrichment (only new tables, the rest is cached)
# -> fact store -> offline audit -> index -> quality gate -> smoke test of agent v2 on three
# development questions. Output: data/eval/m8-prepare.log and data/eval/run-023-smoke/.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=data/eval/m8-prepare.log
mkdir -p data/eval
{
    echo "== M8-Vorbereitung gestartet: $(date '+%F %T')"
    uv sync || exit 1
    uv run python -m audit_agent.ingestion || exit 1
    uv run python -m audit_agent.enrichment || exit 1
    uv run python -m audit_agent.facts audit || exit 1
    uv run python -m audit_agent.retrieval index || exit 1
    ./scripts/check.sh || exit 1
    uv run python -m audit_agent.evaluation generate --run-id run-023-smoke --variants p2 \
        --ids H2 V1 W1
    uv run python -m audit_agent.evaluation score --run-id run-023-smoke
    echo "== M8-Vorbereitung beendet: $(date '+%F %T')"
} 2>&1 | tee "$LOG"
echo FERTIG
