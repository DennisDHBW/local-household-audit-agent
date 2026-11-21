#!/usr/bin/env bash
# M8 night run (ADR-0019, ADR-0021).
#   scripts/m8_night.sh            run-027: P2 on the 21 development questions (control run after
#                                  ISS-121 to ISS-123; B0 and P1 did not change, their numbers stay
#                                  those of run-025). run-026 was the run before these fixes.
#   scripts/m8_night.sh --holdout  run-028: B0, P1 and P2 on the held-out questions, at the very end
set -uo pipefail
cd "$(dirname "$0")/.."
HOST="${AUDIT_OLLAMA_HOST:-http://localhost:11434}"
RUN=run-027
VARIANTS=(p2)
SELECT=(--all)
if [ "${1:-}" = "--holdout" ]; then RUN=run-028; VARIANTS=(b0 p1 p2); SELECT=(--holdout); fi
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
    uv run python -m audit_agent.facts build || exit 1  # facts.json must match the code
    { date; uptime; free -h; } > "data/eval/$RUN-env.txt"
    step generate --run-id "$RUN" --variants "${VARIANTS[@]}" "${SELECT[@]}"
    uv run python -m audit_agent.evaluation score --run-id "$RUN"
    uv run python scripts/check_evidence.py --run-id "$RUN"
    uv run python scripts/analyze_agentics.py --run-id "$RUN" --write
    echo "== $RUN beendet: $(date '+%F %T')"
} 2>&1 | tee -a "$LOG"
journalctl -u ollama --since "-14h" --no-pager | grep -iE "truncat|oom" > "data/eval/$RUN-journal.txt"
echo FERTIG
