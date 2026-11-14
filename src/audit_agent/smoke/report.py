"""Human-readable summary of a smoke-test run."""

from __future__ import annotations

from audit_agent.smoke.metrics import SmokeReport


def _fmt(value: float | None, digits: int = 1) -> str:
    return "–" if value is None else f"{value:.{digits}f}"


def _yes_no(flag: bool) -> str:
    return "ja" if flag else "nein"


def _speed_section(report: SmokeReport) -> list[str]:
    lines = [
        "## Geschwindigkeit",
        "",
        "| Modell | Prompt-Tokens | Prefill (Tok/s) | Generierung (Tok/s) | Laden (s) | RAM (GB) |",
        "|---|---|---|---|---|---|",
    ]
    for s in report.speed:
        cells = [
            s.model,
            str(s.prompt_tokens or "–"),
            _fmt(s.prefill_tokens_per_s),
            _fmt(s.generation_tokens_per_s),
            _fmt(s.load_seconds),
            _fmt(s.resident_gb, 2),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Prompt-Präfix-Wiederverwendung", ""]
    for p in report.prefix_reuse:
        lines.append(
            f"- {p.model}: 1. Aufruf {p.first_prompt_tokens} Tokens, "
            f"2. Aufruf {p.second_prompt_tokens} Tokens → wiederverwendet: "
            f"{_yes_no(p.is_prefix_reused)}"
        )
    return lines


def _tool_section(report: SmokeReport) -> list[str]:
    lines = ["", "## Tool-Calling", ""]
    for summary in report.tool_calling:
        lines += [
            f"### {summary.model}: Werkzeug {summary.tool_accuracy:.0%}, "
            f"Argumente {summary.argument_accuracy:.0%}",
            "",
            "| Aufgabe | Werkzeug | Argumente | Werkzeug ok | Argumente ok | Sekunden |",
            "|---|---|---|---|---|---|",
        ]
        for r in summary.results:
            cells = [
                r.task_id,
                r.called_tool or "–",
                f"`{r.arguments}`",
                _yes_no(r.is_tool_correct),
                _yes_no(r.are_arguments_valid),
                f"{r.seconds:.0f}",
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return lines


def _embedding_and_vision_section(report: SmokeReport) -> list[str]:
    lines: list[str] = []
    if report.embedding:
        e = report.embedding
        lines += [
            "## Embedding",
            "",
            f"- {e.model}: {e.dimensions} Dimensionen; Ähnlichkeit relevant "
            f"{e.relevant_similarity:.3f} vs. irrelevant {e.irrelevant_similarity:.3f} → "
            f"Ranking korrekt: {_yes_no(e.is_ranking_correct)}",
            "",
        ]
    if report.vision:
        v = report.vision
        lines += [
            "## Vision",
            "",
            f"- {v.model}, Bild `{v.page_image}`, {v.seconds:.0f} s; erwartet "
            f"{v.expected_values}, gefunden {v.found_values} → alle Sollwerte gefunden: "
            f"{_yes_no(v.are_all_values_found)}",
            "",
            "```text",
            v.caption.strip(),
            "```",
            "",
        ]
    return lines


def render_markdown(report: SmokeReport) -> str:
    lines = [
        f"# Smoke-Test {report.run_id}",
        "",
        f"Start: {report.started_at} · num_ctx: {report.num_ctx}",
        "",
        *_speed_section(report),
        *_tool_section(report),
        *_embedding_and_vision_section(report),
    ]
    if report.errors:
        lines += ["## Fehler", "", *[f"- {error}" for error in report.errors], ""]
    return "\n".join(lines)
