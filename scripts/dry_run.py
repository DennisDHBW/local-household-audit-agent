"""Dry run of the night run without Ollama (ISS-115, ADR-0020).

Builds a throw-away copy of the project (dataset and parsed chunks) in a temporary folder,
indexes it with hashed bag-of-words vectors instead of ``nomic-embed-text`` and runs
``generate``, ``score`` and ``check_evidence`` for B0, P1 and P2 over all development questions.
The chat model is replaced by a rule-based "oracle": it plans, picks the tool the question
type suggests and answers with the tool's short summary.

Purpose: find crashes and wrong wiring before a night run (ISS-115 cost one run), and show
what the tools deliver if the model chooses perfectly. The numbers are NOT model results and
must never be reported as such. Nothing in ``data/`` of the project is touched.

    uv run python scripts/dry_run.py
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from ollama import ChatResponse, Message

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = 256
GAP = "Dazu liegen in den Unterlagen keine Angaben vor."


def _vector(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"\w{3,}", text.lower()):
        vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIMENSIONS] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def _reply(
    content: str = "", calls: list[tuple[str, dict[str, Any]]] | None = None
) -> ChatResponse:
    tool_calls = [
        Message.ToolCall(function=Message.ToolCall.Function(name=name, arguments=arguments))
        for name, arguments in calls or []
    ]
    return ChatResponse(
        model="dry-run",
        message=Message(role="assistant", content=content, tool_calls=tool_calls or None),
        prompt_eval_count=100,
        prompt_eval_duration=1_000_000,
        eval_count=10,
        eval_duration=1_000_000,
        total_duration=2_000_000,
    )


def _oracle_call(question: str) -> tuple[str, dict[str, Any]]:
    from audit_agent.agent.prompts import is_audit_question, wants_chart, wants_overview
    from audit_agent.agent.scope import question_scope

    utilities, tariffs, years = question_scope(question)
    args: dict[str, Any] = {}
    plain = utilities - {"district_heating"}
    if len(plain) == 1:
        args["utility_type"] = next(iter(plain))
    if len(tariffs) == 1:
        args["tariff_kind"] = next(iter(tariffs))
    folded = question.lower()
    topic = "preise" if "preis" in folded else "kosten" if "kosten" in folded else "verbrauch"
    if wants_chart(question) or wants_overview(question):
        if years:
            args.update(from_year=min(years), to_year=max(years))
        return ("make_chart" if wants_chart(question) else "make_overview"), {
            "topic": topic,
            **args,
        }
    if is_audit_question(question):
        return "check_bill", {**args, **({"year": max(years)} if years else {})}
    if "grundpreis" in folded and "arbeits" in folded:
        return "get_facts", {"fact": "preise", **args}
    for word, fact in (
        ("arbeitspreis", "arbeitspreis"),
        ("grundpreis", "grundpreis"),
        ("abschlag", "abschlag"),
        ("verbrauch", "verbrauch"),
        ("zählerst", "zaehlerstand"),
    ):
        if word in folded:
            return "get_facts", {"fact": fact, **args, **({"year": max(years)} if years else {})}
    return "search", {"query": question}


class FakeOllama:
    """Enough of ``ollama.Client`` for index, B0, P1 and the agent loop."""

    def __init__(self, models: list[str]):
        self._models = models

    def list(self) -> SimpleNamespace:
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self._models])

    def generate(self, **_: Any) -> None:
        return None

    def embed(self, model: str, input: list[str], **_: Any) -> SimpleNamespace:  # noqa: A002
        return SimpleNamespace(embeddings=[_vector(text) for text in input])

    def chat(self, **kwargs: Any) -> ChatResponse:
        messages = kwargs["messages"]
        if not kwargs.get("tools"):
            return _reply(GAP)
        question = next(m["content"] for m in messages if m["role"] == "user")
        tool_messages = [m for m in messages if isinstance(m, dict) and m.get("role") == "tool"]
        last = messages[-1]
        if not tool_messages:
            return _reply(
                calls=[
                    ("plan", {"steps": ["Werkzeug wählen", "antworten"]}),
                    _oracle_call(question),
                ]
            )
        if isinstance(last, dict) and last.get("role") == "user":  # a self-check nudge
            for tool in ("check_bill", "make_chart", "make_overview"):
                if tool in last["content"]:
                    name, args = _oracle_call(question)
                    return _reply(calls=[(tool, args)])
        output = tool_messages[-1]["content"]
        if output.startswith("FEHLER"):
            return _reply(GAP)
        citations = " ".join(dict.fromkeys(re.findall(r"\[\d+\]", output)))
        summary = next(
            (line for line in output.splitlines() if line.startswith("Kurzfassung")), None
        )
        if summary:
            return _reply(summary.split(":", 1)[1].strip() + f" {citations}")
        body = "\n".join(output.splitlines()[:12])
        return _reply(f"{body}\n{citations}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="audit-dry-run-") as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / "dataset", root / "dataset")
        shutil.copytree(ROOT / "data" / "processed", root / "data" / "processed")
        (root / "data" / "processed" / "facts.json").unlink(missing_ok=True)
        os.environ["AUDIT_PROJECT_ROOT"] = str(root)

        from audit_agent.config import Settings

        settings = Settings.from_env()
        fake = FakeOllama([settings.models.agent, settings.models.embedding])
        import audit_agent.evaluation.__main__ as evaluation
        import audit_agent.retrieval.__main__ as retrieval

        retrieval.Client = lambda **_: fake  # type: ignore[assignment]
        evaluation.Client = lambda **_: fake  # type: ignore[assignment]
        sys.path.insert(0, str(ROOT / "scripts"))
        import check_evidence

        steps = [
            (retrieval, ["index"]),
            (
                evaluation,
                ["generate", "--run-id", "dry-run", "--variants", "b0", "p1", "p2", "--all"],
            ),
            (
                evaluation,
                ["generate", "--run-id", "dry-run-holdout", "--variants", "p2", "--holdout"],
            ),
        ]
        for module, argv in steps:
            sys.argv = ["dry-run", *argv]
            code = module.main()
            if code:
                print(f"Schritt {argv[0]} endete mit {code}", file=sys.stderr)
                return code
        for run_id in ("dry-run", "dry-run-holdout"):
            check_evidence.main(["--run-id", run_id])
        # Held-out questions: only "does it run"; their scores stay unseen (ISS-108).
        print("\nZurückgehaltene Fragen: Lauf, Bewertung und Belegabgleich ohne Fehler.")
        report = settings.eval_dir / "dry-run" / "report.md"
        print("\n=== dry-run (Orakel, KEIN Modellergebnis) ===")
        print(report.read_text(encoding="utf-8")[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
