#!/usr/bin/env bash
# Quality gate: must be green before every commit (CODING_STANDARDS.md, section 5).
set -euo pipefail
cd "$(dirname "$0")/.."
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not slow"
