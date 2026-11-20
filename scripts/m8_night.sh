#!/usr/bin/env bash
# M8 night run (ADR-0019): all 21 development questions with B0, P1 and P2 v2 (run-024).
# The held-out questions run separately at the very end: scripts/m8_night.sh --holdout (run-025).
set -uo pipefail
cd "$(dirname "$0")/.."
HOST="${AUDIT_OLLAMA_HOST:-http://localhost:11434}"
RUN=run-024
SELECT=(--all)
if [ "${1:-}" = "--holdout" ]; then RUN=run-025; SELECT=(--holdout); fi
LOG="data/eval/$RUN.log"

wait_for_ollama() {
    for _ in $(seq 1 60); do
        curl -sf "$HOST/api/version" >/dev/null && return 0
        sleep 10
    done
    echo "Ollama ist seit 10 Minuten nicht erreichbar" >&2
    return 1
}

step() {
    for attempt in 1 2; do
        wait_for_ollama || return 1
        uv run python -m audit_agent.evaluation "$@" && return 0
        echo "Schritt fehlgeschlagen (Versuch $attempt): $*" >&2
        sleep 30
    done
    return 1
}

mkdir -p data/eval
{
    echo "== $RUN gestartet: $(date '+%F %T')"
    { date; uptime; free -h; } > "data/eval/$RUN-env.txt"
    step generate --run-id "$RUN" --variants b0 p1 p2 "${SELECT[@]}"
    uv run python -m audit_agent.evaluation score --run-id "$RUN"
    uv run python scripts/check_evidence.py --run-id "$RUN"
    echo "== $RUN beendet: $(date '+%F %T')"
} 2>&1 | tee -a "$LOG"
journalctl -u ollama --since "-14h" --no-pager | grep -iE "truncat|oom" > "data/eval/$RUN-journal.txt"
echo FERTIG
