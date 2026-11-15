#!/usr/bin/env bash
# Night run M6b/M6c (docs/status.md): answers of both models, then RAGAS on both runs.
# Every step waits until Ollama answers and is retried once; finished answers and RAGAS
# lines are kept, so a retry resumes where the step stopped (ISS-043, ISS-049).
set -uo pipefail
cd "$(dirname "$0")/.."

HOST="${AUDIT_OLLAMA_HOST:-http://localhost:11434}"
LOG=data/eval/night-m6b.log

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
        uv run --group ragas python -m audit_agent.evaluation "$@" && return 0
        echo "Schritt fehlgeschlagen (Versuch $attempt): $*" >&2
        sleep 30
    done
    return 1
}

uv sync --group ragas
{
    echo "== Nachtlauf gestartet: $(date '+%F %T')"
    step generate --run-id run-010 --all --model llama3.1:8b
    step generate --run-id run-011 --all --model qwen2.5:7b
    step ragas --run-id run-010
    step ragas --run-id run-011
    echo "== Nachtlauf beendet: $(date '+%F %T')"
} 2>&1 | tee -a "$LOG"
journalctl -u ollama --since "-16h" --no-pager | grep -iE "truncat|oom" > data/eval/night-m6b-journal.txt
echo FERTIG
