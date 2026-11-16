"""Deterministic metrics of one answer (concept.md, 11.3); no LLM judge is involved.

The checks are simple on purpose and therefore have known limits (ISS-038): a number is
found anywhere in the answer, a verdict is read from the first or last sentence. The report shows
every answer next to its score, so a wrong check can be spotted by hand.
"""

from __future__ import annotations

import re
import statistics
from collections.abc import Iterable, Mapping
from decimal import Decimal

from pydantic import ValidationError

from audit_agent.agent.prompts import is_gap_answer
from audit_agent.agent.tools import YEAR_FILTER_DOC_TYPES, FilterArguments, clean_arguments
from audit_agent.corpus import DocumentCatalog, DocumentMeta, ExpectedFact, Question
from audit_agent.evaluation.models import (
    VARIANT_NAMES,
    AnswerScore,
    VariantAnswer,
    VariantSummary,
    Verdict,
)
from audit_agent.numbers import extract_numbers
from audit_agent.retrieval.search import fold

CITATION = re.compile(r"\[(\d+(?:\s*[,;]\s*\d+)*)\]")
"""``[3]`` or ``[1, 4]``; the numbers refer to the shown sources of the answer."""
UNIT_FACTORS = (Decimal(1), Decimal(100), Decimal("0.01"))
"""A fact may be written as EUR or ct, 0.348 or 34,8."""
SEARCH_TOOLS = frozenset({"search", "search_documents", "search_tables", "search_images"})
"""``search_documents`` and ``search_tables`` only appear in runs before ADR-0014."""
_LEADING_VERDICT = re.compile(r"\W*(ja|nein)\b")
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)|\n")
NEUTRAL_PHRASES = ("keine abweichung", "kein fehler", "keine fehler", "nicht zu beanstanden")
"""Removed before the markers are checked: they contain a negative word but mean "correct"."""
NEGATIVE_MARKERS = ("nicht", "abweich", "zu viel", "zu hoch", "falsch", "fehler")
POSITIVE_MARKERS = ("stimmt", "korrekt", "richtig", "ueberein", "passt", "konsistent")


def cited_numbers(answer: str) -> set[int]:
    """All citation numbers in an answer."""
    numbers: set[int] = set()
    for group in CITATION.findall(answer):
        numbers.update(int(part) for part in re.split(r"[,;]", group))
    return numbers


def strip_citations(answer: str) -> str:
    """The answer without ``[n]`` markers (a citation must not count as a found number)."""
    return CITATION.sub(" ", answer)


def is_fact_in_answer(fact: ExpectedFact, answer: str) -> bool:
    """Numbers match any number of the answer (also in ct); text facts match as whole words."""
    text = strip_citations(answer)
    if isinstance(fact.value, str):
        return re.search(rf"\b{re.escape(fold(fact.value))}\b", fold(text)) is not None
    return any(
        abs(Decimal(str(number)) - fact.value * factor) <= fact.tolerance * max(factor, 1)
        for number in extract_numbers(text)
        for factor in UNIT_FACTORS
    )


def expected_verdict(question: Question) -> Verdict | None:
    """``ja``/``nein`` if the expected answer starts with it (audit questions), else ``None``."""
    match = _LEADING_VERDICT.match(fold(question.expected_answer))
    return None if match is None else match.group(1)  # type: ignore[return-value]


def answer_verdict(answer: str) -> Verdict | None:
    """Verdict: a leading ja/nein, else markers in the first, then the last sentence (heuristic).

    Small models often state the conclusion at the end ("… wurde nicht angewendet.").
    """
    text = fold(strip_citations(answer)).strip()
    match = _LEADING_VERDICT.match(text)
    if match is not None:
        return match.group(1)  # type: ignore[return-value]
    sentences = [part for part in _SENTENCE_END.split(text) if part.strip()]
    if not sentences:
        return None
    for sentence in dict.fromkeys((sentences[0], sentences[-1])):
        verdict = _marker_verdict(sentence)
        if verdict is not None:
            return verdict
    return None


def _marker_verdict(sentence: str) -> Verdict | None:
    for phrase in NEUTRAL_PHRASES:
        sentence = sentence.replace(phrase, " stimmt ")
    if any(marker in sentence for marker in NEGATIVE_MARKERS):
        return "nein"
    if any(marker in sentence for marker in POSITIVE_MARKERS):
        return "ja"
    return None


def _filter_arguments(arguments: Mapping[str, object]) -> FilterArguments | None:
    try:
        return FilterArguments.model_validate(clean_arguments(arguments))
    except ValidationError:
        return None


def has_filter(arguments: Mapping[str, object]) -> bool:
    """True if a search call set any metadata filter."""
    parsed = _filter_arguments(arguments)
    return parsed is not None and parsed != FilterArguments()


def filter_excludes(arguments: Mapping[str, object], document: DocumentMeta) -> bool:
    """True if the filter of a search call would drop ``document`` (same rules as the tools)."""
    parsed = _filter_arguments(arguments)
    if parsed is None:
        return False
    if parsed.utility_type is not None and parsed.utility_type != document.utility_type:
        return True
    if parsed.doc_type is not None and parsed.doc_type != document.doc_type:
        return True
    if parsed.year is not None and parsed.doc_type in YEAR_FILTER_DOC_TYPES:
        start, end = document.billing_period_start, document.billing_period_end
        return not (start and end and start.year <= parsed.year <= end.year)
    return False


def score_answer(
    question: Question, answer: VariantAnswer, catalog: DocumentCatalog
) -> AnswerScore:
    """Compare one answer with the ground truth of its question."""
    documents = {document.file: document for document in catalog.documents}
    noise = {file for file, document in documents.items() if document.is_noise_document}
    expected = {(source.file, source.page) for source in question.sources}
    expected_documents = [
        documents[f] for f in {s.file for s in question.sources} if f in documents
    ]

    by_number = {source.number: source for source in answer.sources}
    numbers = cited_numbers(answer.answer)
    cited = [by_number[n] for n in sorted(numbers) if n in by_number]
    cited_pairs = {(source.filename, source.page_number) for source in cited}

    searches = [t for t in answer.tool_uses if t.is_valid and t.name in SEARCH_TOOLS]
    is_agent = answer.variant == "p2"
    return AnswerScore(
        variant=answer.variant,
        question_id=question.id,
        category=question.category,
        is_answerable=question.is_answerable,
        facts_total=len(question.facts),
        missing_facts=tuple(
            fact.label for fact in question.facts if not is_fact_in_answer(fact, answer.answer)
        ),
        cited_count=len(cited),
        invalid_citations=len(numbers - by_number.keys()),
        cited_expected=sum(1 for pair in cited_pairs if pair in expected),
        expected_count=len(expected),
        expected_cited=sum(1 for pair in expected if pair in cited_pairs),
        cited_distractors=sum(1 for source in cited if source.filename in noise),
        shown_count=len(answer.sources),
        shown_distractors=sum(1 for source in answer.sources if source.filename in noise),
        expected_tools=question.expected_tools,
        called_tools=(tuple(t.name for t in answer.tool_uses if t.is_valid) if is_agent else None),
        filtered_searches=sum(1 for t in searches if has_filter(t.arguments)),
        filter_misses=sum(
            1
            for t in searches
            if any(filter_excludes(t.arguments, document) for document in expected_documents)
        ),
        admits_gap=is_gap_answer(answer.answer),
        expected_verdict=expected_verdict(question),
        answer_verdict=answer_verdict(answer.answer),
        stop_reason=answer.stop_reason,
        seconds=answer.seconds,
        prompt_tokens=answer.prompt_tokens,
    )


def summarize(scores: Iterable[AnswerScore]) -> list[VariantSummary]:
    """One summary per variant that has scores, in the order B0, P1, P2."""
    by_variant: dict[str, list[AnswerScore]] = {}
    for score in scores:
        by_variant.setdefault(score.variant, []).append(score)
    summaries = []
    for variant in VARIANT_NAMES:
        rows = by_variant.get(variant)
        if not rows:
            continue
        seconds = [row.seconds for row in rows]
        tools = [row.are_tools_ok for row in rows if row.are_tools_ok is not None]
        summaries.append(
            VariantSummary(
                variant=variant,
                question_count=len(rows),
                correct_count=sum(row.is_correct for row in rows),
                facts_found=sum(row.facts_found for row in rows),
                facts_total=sum(row.facts_total for row in rows),
                cited_count=sum(row.cited_count for row in rows),
                invalid_citations=sum(row.invalid_citations for row in rows),
                cited_expected=sum(row.cited_expected for row in rows),
                expected_count=sum(row.expected_count for row in rows),
                expected_cited=sum(row.expected_cited for row in rows),
                cited_distractors=sum(row.cited_distractors for row in rows),
                shown_count=sum(row.shown_count for row in rows),
                shown_distractors=sum(row.shown_distractors for row in rows),
                tools_ok_count=sum(tools) if variant == "p2" else None,
                filtered_searches=sum(row.filtered_searches for row in rows),
                filter_misses=sum(row.filter_misses for row in rows),
                negatives_detected=sum(row.admits_gap for row in rows if not row.is_answerable),
                negative_count=sum(1 for row in rows if not row.is_answerable),
                errors_detected=sum(
                    row.answer_verdict == "nein" for row in rows if row.expected_verdict == "nein"
                ),
                error_count=sum(1 for row in rows if row.expected_verdict == "nein"),
                false_alarms=sum(
                    row.answer_verdict == "nein" for row in rows if row.expected_verdict == "ja"
                ),
                correct_bill_count=sum(1 for row in rows if row.expected_verdict == "ja"),
                seconds_mean=round(statistics.fmean(seconds), 1),
                seconds_median=round(statistics.median(seconds), 1),
                prompt_tokens_mean=round(statistics.fmean(row.prompt_tokens for row in rows), 0),
            )
        )
    return summaries
