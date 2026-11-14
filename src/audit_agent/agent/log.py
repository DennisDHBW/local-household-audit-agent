"""Step log of one question as JSON lines (written while the agent works, not at the end).

A crash or a timeout in a run of many minutes therefore still leaves every finished step on disk.
"""

from __future__ import annotations

from pathlib import Path

from audit_agent.agent.models import AgentRun, AgentStep, EvidenceBook


class RunLog:
    """Appends each step as one line; ``finish`` adds the summary line of the run."""

    def __init__(self, path: Path):
        self._path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    def __call__(self, step: AgentStep, book: EvidenceBook) -> None:
        self._append(step.model_dump_json())

    def finish(self, run: AgentRun) -> None:
        """Summary line: everything of the run except the steps already written."""
        summary = run.model_dump_json(exclude={"steps"})
        self._append(f'{{"kind": "run", "run": {summary}}}')

    def _append(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")
