#!/usr/bin/env bash
# P2 evaluation runs (M6f): one "run-id:model" pair per argument, run one after the other.
# Per run: system load, generate (P2, all questions), score, evidence check, timing and the
# Ollama journal (only there are model loads and cache hits visible, ISS-057).
# Example: scripts/eval_run.sh run-014:qwen2.5:7b run-015:llama3.1:8b
set -uo pipefail
cd "$(dirname "$0")/.."

HOST="${AUDIT_OLLAMA_HOST:-http://localhost:11434}"

wait_for_ollama() {
    for _ in $(seq 1 60); do
        curl -sf "$HOST/api/version" >/dev/null && return 0
        sleep 10
    done
    echo "Ollama ist seit 10 Minuten nicht erreichbar" >&2
    return 1
}

[ "$#" -gt 0 ] || { echo "Aufruf: $0 run-id:model [run-id:model ...]" >&2; exit 2; }
uv sync || exit 1
mkdir -p data/eval

for pair in "$@"; do
    run_id="${pair%%:*}"
    model="${pair#*:}"
    log="data/eval/$run_id.log"
    started=$(date +%s)
    echo "== $run_id ($model) gestartet: $(date '+%F %T')"
    { date; uptime; free -h; } > "data/eval/$run_id-env.txt"
    wait_for_ollama || exit 1
    if ! uv run python -m audit_agent.evaluation generate --run-id "$run_id" \
            --variants p2 --all --model "$model" 2>&1 | tee "$log"; then
        echo "generate fehlgeschlagen: $run_id" >&2
        continue
    fi
    {
        uv run python -m audit_agent.evaluation score --run-id "$run_id"
        uv run python scripts/check_evidence.py --run-id "$run_id"
        uv run python scripts/analyze_timing.py --run-id "$run_id"
    } 2>&1 | tee -a "$log"
    minutes=$(( ($(date +%s) - started) / 60 + 5 ))
    journalctl -u ollama --since "-${minutes}min" --no-pager > "data/eval/$run_id-journal.txt"
    echo "== $run_id beendet: $(date '+%F %T')"
done
echo FERTIG
