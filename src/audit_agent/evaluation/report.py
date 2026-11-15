"""Markdown report of a run: variant x metric table, question matrix, answers (concept.md 11.4)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import PurePosixPath

from audit_agent.corpus import Question
from audit_agent.evaluation.metrics import cited_numbers
from audit_agent.evaluation.models import (
    VARIANT_LABELS,
    AnswerScore,
    VariantAnswer,
    VariantName,
    VariantSummary,
)
from audit_agent.evaluation.ragas_eval import (
    RAGAS_LABELS,
    RAGAS_METRICS,
    RagasScore,
    RagasStatus,
    RagasSummary,
    summarize_ragas,
)

RAGAS_STATUS_LABELS: dict[RagasStatus, str] = {
    "ok": "",
    "too_long": "zu lang",
    "no_context": "ohne Belege",
    "not_applicable": "entfällt",
    "no_statements": "keine Aussagen",
    "error": "Fehler",
}


def ratio(part: int, total: int) -> str:
    """``3/4 (75 %)``; ``-`` if there is nothing to count."""
    if total == 0:
        return "-"
    return f"{part}/{total} ({round(100 * part / total)} %)"


def _metric_rows(summaries: Sequence[VariantSummary]) -> list[tuple[str, list[str]]]:
    def tools(summary: VariantSummary) -> str:
        if summary.tools_ok_count is None:
            return "-"
        return ratio(summary.tools_ok_count, summary.question_count)

    def agent_only(summary: VariantSummary, value: str) -> str:
        return value if summary.variant == "p2" else "-"

    return [
        ("Richtig (gesamt)", [ratio(s.correct_count, s.question_count) for s in summaries]),
        ("Zahlen/Fakten gefunden", [ratio(s.facts_found, s.facts_total) for s in summaries]),
        (
            "Zitate auf erwartete Quelle (Präzision)",
            [ratio(s.cited_expected, s.cited_count) for s in summaries],
        ),
        (
            "Erwartete Quellen zitiert (Recall)",
            [ratio(s.expected_cited, s.expected_count) for s in summaries],
        ),
        ("Erfundene Belegnummern", [str(s.invalid_citations) for s in summaries]),
        ("Ablenker in Zitaten", [ratio(s.cited_distractors, s.cited_count) for s in summaries]),
        ("Ablenker im Kontext", [ratio(s.shown_distractors, s.shown_count) for s in summaries]),
        ("Tool-Wahl korrekt", [tools(s) for s in summaries]),
        (
            "Suchen mit eigenem Filter / davon schließen Quelle aus",
            [agent_only(s, f"{s.filtered_searches} / {s.filter_misses}") for s in summaries],
        ),
        (
            "Negativfragen erkannt",
            [ratio(s.negatives_detected, s.negative_count) for s in summaries],
        ),
        ("Fehler erkannt", [ratio(s.errors_detected, s.error_count) for s in summaries]),
        ("Fehlalarme", [ratio(s.false_alarms, s.correct_bill_count) for s in summaries]),
        (
            "Sekunden je Frage (Mittel / Median)",
            [f"{s.seconds_mean} / {s.seconds_median}" for s in summaries],
        ),
        ("Prompt-Token je Frage (Mittel)", [f"{s.prompt_tokens_mean:.0f}" for s in summaries]),
    ]


def _mark(score: AnswerScore | None) -> str:
    if score is None:
        return "-"
    state = "✓" if score.is_correct else "✗"
    facts = f" {score.facts_found}/{score.facts_total}" if score.facts_total else ""
    return state + facts


def render_report(
    run_id: str,
    questions: Sequence[Question],
    answers: Sequence[VariantAnswer],
    scores: Sequence[AnswerScore],
    summaries: Sequence[VariantSummary],
    manifest: Mapping[str, object] | None = None,
    ragas: Sequence[RagasScore] = (),
) -> str:
    """The whole report; every answer is printed so wrong checks can be found by hand."""
    variants = [s.variant for s in summaries]
    models = sorted({answer.model for answer in answers})
    lines = [
        f"# Evaluation {run_id} ({date.today().isoformat()})",
        "",
        f"Modell: {', '.join(f'`{m}`' for m in models)}. Metriken deterministisch "
        "(concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).",
    ]
    b0 = (manifest or {}).get("b0_context")
    if isinstance(b0, Mapping):
        lines += [
            "",
            f"B0-Kontext: {len(b0.get('complete_files', []))} Dateien vollständig, "
            f"teilweise: {b0.get('partial_file') or '-'}, "
            f"fehlend: {len(b0.get('missing_files', []))}; "
            f"ca. {b0.get('estimated_tokens')} von {b0.get('budget_tokens')} Token.",
        ]
    lines += [
        "",
        "| Metrik | " + " | ".join(VARIANT_LABELS[v] for v in variants) + " |",
        "|---|" + "---|" * len(variants),
    ]
    lines += [f"| {name} | {' | '.join(values)} |" for name, values in _metric_rows(summaries)]
    if ragas:
        lines += _ragas_table(variants, ragas)

    by_key = {(s.question_id, s.variant): s for s in scores}
    lines += [
        "",
        "## Fragen × Varianten (✓/✗, gefundene Fakten)",
        "",
        "| Frage | " + " | ".join(VARIANT_LABELS[v] for v in variants) + " |",
        "|---|" + "---|" * len(variants),
    ]
    asked = [q for q in questions if any((q.id, v) in by_key for v in variants)]
    for question in asked:
        marks = [_mark(by_key.get((question.id, v))) for v in variants]
        lines.append(f"| {question.id} | {' | '.join(marks)} |")

    answer_by_key = {(a.question_id, a.variant): a for a in answers}
    for question in asked:
        lines += [
            "",
            f"## {question.id}: {question.question}",
            "",
            f"Erwartet: {question.expected_answer.strip()}",
        ]
        for variant in variants:
            answer = answer_by_key.get((question.id, variant))
            score = by_key.get((question.id, variant))
            if answer is None or score is None:
                continue
            lines += [
                "",
                f"**{VARIANT_LABELS[variant]}** ({answer.seconds} s, {answer.stop_reason}): "
                + answer.answer,
                "",
            ]
            details = [
                f"Fakten fehlen: {', '.join(score.missing_facts) or '-'}",
                f"Urteil: {score.answer_verdict or '-'} (erwartet {score.expected_verdict or '-'})",
                f"Lücke benannt: {'ja' if score.admits_gap else 'nein'}",
            ]
            if score.called_tools is not None:
                details.append(f"Tools: {', '.join(score.called_tools) or '-'}")
            lines.append("- " + "; ".join(details))
            cited = _cited_files(answer)
            if cited:
                lines.append(f"- Zitiert: {cited}")
            judged = _ragas_line(ragas, variant, question.id)
            if judged:
                lines.append(f"- RAGAS: {judged}")
    return "\n".join(lines) + "\n"


def _ragas_cell(summary: RagasSummary | None) -> str:
    if summary is None:
        return "-"
    value = "-" if summary.mean is None else f"{summary.mean:.2f}"
    notes = [f"{summary.scored}/{summary.total} bewertet"]
    if summary.too_long:
        notes.append(f"{summary.too_long} zu lang")
    if summary.errors:
        notes.append(f"{summary.errors} Fehler")
    return f"{value} ({', '.join(notes)})"


def _ragas_table(variants: Sequence[VariantName], scores: Sequence[RagasScore]) -> list[str]:
    """Means over the answers the judge could score; skipped ones are counted, not zeroed."""
    by_key = {(s.variant, s.metric): s for s in summarize_ragas(scores)}
    judges = sorted({score.judge for score in scores})
    lines = [
        "",
        f"RAGAS (ADR-0012), Bewerter {', '.join(f'`{j}`' for j in judges)}; Mittel über die "
        "bewerteten Antworten, Stichproben von Hand prüfen.",
        "",
        "| RAGAS | " + " | ".join(VARIANT_LABELS[v] for v in variants) + " |",
        "|---|" + "---|" * len(variants),
    ]
    for metric in RAGAS_METRICS:
        cells = [_ragas_cell(by_key.get((v, metric))) for v in variants]
        if any(cell != "-" for cell in cells):
            lines.append(f"| {RAGAS_LABELS[metric]} | {' | '.join(cells)} |")
    return lines


def _ragas_line(scores: Sequence[RagasScore], variant: VariantName, question_id: str) -> str:
    parts = []
    for score in scores:
        if score.variant != variant or score.question_id != question_id:
            continue
        if score.status == "ok" and score.value is not None:
            shown = f"{score.value:.2f}"
        else:
            shown = RAGAS_STATUS_LABELS[score.status]
        parts.append(f"{RAGAS_LABELS[score.metric]} {shown}")
    return ", ".join(sorted(parts))


def _cited_files(answer: VariantAnswer) -> str:
    by_number = {source.number: source for source in answer.sources}
    parts = []
    for number in sorted(cited_numbers(answer.answer)):
        source = by_number.get(number)
        if source is None:
            parts.append(f"[{number}] (unbekannt)")
        else:
            parts.append(
                f"[{number}] {PurePosixPath(source.filename).name} S. {source.page_number}"
            )
    return ", ".join(parts)
