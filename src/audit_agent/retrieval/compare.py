"""Retrieval comparison for ADR-0002: metadata filter and hierarchy boost on or off.

Runs the questions of the ground truth against several search configurations and checks
the top hits against the expected sources. The ground truth is used only here, never by
index or search. The filters stand for what a correct agent would pass for each question.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from audit_agent.corpus import DocumentCatalog, GroundTruth, Question, UtilityType
from audit_agent.ingestion import ChunkType
from audit_agent.retrieval.models import MetadataFilter, SearchHit, SearchOptions
from audit_agent.retrieval.search import Retriever

QUESTION_FILTERS: dict[str, MetadataFilter] = {
    "S1": MetadataFilter(utility_type=UtilityType.GAS),
    "S2": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "S3": MetadataFilter.for_year(2025, utility_type=UtilityType.WATER),
    "S4": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "S5": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "G1": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "G2": MetadataFilter.for_year(2025, utility_type=UtilityType.SERVICE_CHARGES),
    "G3": MetadataFilter(utility_type=UtilityType.GAS),
    "G4": MetadataFilter.for_year(2026, utility_type=UtilityType.SERVICE_CHARGES),
    "N1": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "N2": MetadataFilter(utility_type=UtilityType.DISTRICT_HEATING),
    "Z1": MetadataFilter.for_year(2025, utility_type=UtilityType.GAS),
    "Z2": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
    "Z3": MetadataFilter(utility_type=UtilityType.ELECTRICITY),
}


class CompareConfig(BaseModel):
    """One search configuration of the comparison."""

    model_config = ConfigDict(frozen=True)

    name: str
    use_filter: bool = False
    use_boost: bool = False
    chunk_types: frozenset[ChunkType] | None = None
    require_heading: bool = False


WITHOUT_SUMMARIES = frozenset(set(ChunkType) - {ChunkType.TABLE_SUMMARY, ChunkType.HEADING})
CONFIGS: tuple[CompareConfig, ...] = (
    CompareConfig(name="plain"),
    CompareConfig(name="boost", use_boost=True),
    CompareConfig(name="filter", use_filter=True),
    CompareConfig(name="filter+boost", use_filter=True, use_boost=True),
    CompareConfig(
        name="filter+boost, no summaries",
        use_filter=True,
        use_boost=True,
        chunk_types=WITHOUT_SUMMARIES,
    ),
    CompareConfig(
        name="filter+boost, no headless text",
        use_filter=True,
        use_boost=True,
        require_heading=True,
    ),
)


class QuestionResult(BaseModel):
    question_id: str
    category: str
    is_answerable: bool
    config: str
    file_rank: int | None
    """Rank of the first hit from an expected source file (``None`` = not found)."""
    page_rank: int | None
    """Rank of the first hit from an expected source file and page."""
    noise_hits: int
    """Hits from distractor documents (telecom, insurance)."""
    hits: tuple[SearchHit, ...]


class ConfigSummary(BaseModel):
    config: str
    file_found: int
    page_found: int
    answerable: int
    mean_reciprocal_rank: float
    noise_hits: int
    total_hits: int
    empty_results: int


class ComparisonReport(BaseModel):
    top_k: int
    results: tuple[QuestionResult, ...]
    summaries: tuple[ConfigSummary, ...]


def options_for(config: CompareConfig, question_id: str) -> SearchOptions:
    return SearchOptions(
        metadata_filter=QUESTION_FILTERS[question_id] if config.use_filter else MetadataFilter(),
        use_hierarchy_boost=config.use_boost,
        chunk_types=config.chunk_types,
        require_heading=config.require_heading,
    )


def evaluate_question(
    question: Question,
    config: str,
    hits: list[SearchHit],
    catalog: DocumentCatalog,
) -> QuestionResult:
    """Rank of the expected source and number of distractor hits for one search."""
    expected_files = {source.file for source in question.sources}
    expected_pages = {(source.file, source.page) for source in question.sources}
    file_rank = next(
        (rank for rank, hit in enumerate(hits, 1) if hit.filename in expected_files), None
    )
    page_rank = next(
        (
            rank
            for rank, hit in enumerate(hits, 1)
            if (hit.filename, hit.page_number) in expected_pages
        ),
        None,
    )
    noise_hits = sum(1 for hit in hits if catalog.by_file(hit.filename).is_noise_document)
    return QuestionResult(
        question_id=question.id,
        category=question.category.value,
        is_answerable=question.is_answerable,
        config=config,
        file_rank=file_rank,
        page_rank=page_rank,
        noise_hits=noise_hits,
        hits=tuple(hits),
    )


def summarize(config: str, results: list[QuestionResult]) -> ConfigSummary:
    answerable = [r for r in results if r.is_answerable]
    ranks = [1 / r.file_rank for r in answerable if r.file_rank is not None]
    return ConfigSummary(
        config=config,
        file_found=sum(1 for r in answerable if r.file_rank is not None),
        page_found=sum(1 for r in answerable if r.page_rank is not None),
        answerable=len(answerable),
        mean_reciprocal_rank=round(sum(ranks) / len(answerable), 3) if answerable else 0.0,
        noise_hits=sum(r.noise_hits for r in results),
        total_hits=sum(len(r.hits) for r in results),
        empty_results=sum(1 for r in results if not r.hits),
    )


def run_comparison(
    retriever: Retriever,
    truth: GroundTruth,
    catalog: DocumentCatalog,
    top_k: int,
    configs: tuple[CompareConfig, ...] = CONFIGS,
) -> ComparisonReport:
    """Every question under every configuration (each query is embedded only once)."""
    vectors = {q.id: retriever.embed_query(q.question) for q in truth.questions}
    results: list[QuestionResult] = []
    summaries: list[ConfigSummary] = []
    for config in configs:
        config_results = []
        for question in truth.questions:
            options = options_for(config, question.id).model_copy(update={"top_k": top_k})
            hits = retriever.search(question.question, options, query_vector=vectors[question.id])
            config_results.append(evaluate_question(question, config.name, hits, catalog))
        results.extend(config_results)
        summaries.append(summarize(config.name, config_results))
    return ComparisonReport(top_k=top_k, results=tuple(results), summaries=tuple(summaries))


def render_markdown(report: ComparisonReport) -> str:
    """Report for ``evaluation-log.md``: summary table, rank per question, hits of one config."""
    lines = [
        f"# Retrieval-Vergleich (Top-{report.top_k})",
        "",
        "| Konfiguration | Datei gefunden | Seite gefunden | MRR (Datei) "
        "| Ablenker-Treffer | leere Ergebnisse |",
        "|---|---|---|---|---|---|",
    ]
    for s in report.summaries:
        lines.append(
            f"| {s.config} | {s.file_found}/{s.answerable} | {s.page_found}/{s.answerable} "
            f"| {s.mean_reciprocal_rank:.3f} | {s.noise_hits}/{s.total_hits} | {s.empty_results} |"
        )
    configs = [s.config for s in report.summaries]
    lines += ["", "## Rang der erwarteten Quelle (Datei / Seite)", ""]
    lines.append("| Frage | " + " | ".join(configs) + " |")
    lines.append("|---|" + "---|" * len(configs))
    for question_id in dict.fromkeys(r.question_id for r in report.results):
        cells = []
        for config in configs:
            r = next(
                x for x in report.results if x.question_id == question_id and x.config == config
            )
            cells.append(
                "–" if not r.is_answerable else f"{r.file_rank or '✗'} / {r.page_rank or '✗'}"
            )
        lines.append(f"| {question_id} | " + " | ".join(cells) + " |")
    best = "filter+boost"
    lines += ["", f"## Treffer der Konfiguration „{best}“", ""]
    for r in (x for x in report.results if x.config == best):
        lines.append(f"**{r.question_id}** ({r.category})")
        for hit in r.hits:
            lines.append(
                f"- {hit.filename.rsplit('/', 1)[-1]} S.{hit.page_number} {hit.chunk_type.value} "
                f"{hit.base_score:.3f} × {hit.boost:.1f} = {hit.final_score:.3f}"
            )
        if not r.hits:
            lines.append("- (keine Treffer)")
        lines.append("")
    return "\n".join(lines)
