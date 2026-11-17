"""Retrieval: prefix, filter clause, boost arithmetic, evidence and comparison without Ollama."""

import hashlib
import math
import re
from datetime import date
from types import SimpleNamespace

import chromadb
import pytest
from pydantic import ValidationError

from audit_agent.config import RetrievalSettings, Settings
from audit_agent.corpus import (
    DocType,
    DocumentCatalog,
    DocumentMeta,
    GroundTruth,
    UtilityType,
)
from audit_agent.ingestion import (
    ChunkMetadata,
    ChunkType,
    DocumentChunk,
    ParsedDocument,
    chunks_path,
)
from audit_agent.retrieval import (
    MetadataFilter,
    RetrievalError,
    Retriever,
    SearchOptions,
    build_evidence,
    build_index,
    build_where,
    embedding_text,
    get_collection,
    hierarchy_prefix,
    path_matches,
    quantity_query,
    render_evidence_text,
    tokenize_query,
    utility_in_query,
    with_query_utility,
)
from audit_agent.retrieval.compare import (
    CompareConfig,
    evaluate_question,
    render_markdown,
    run_comparison,
    summarize,
)
from audit_agent.retrieval.index import chunk_record, date_number, load_chunks

POWER_PDF = "01_electricity_x/04_Strom_Jahresabrechnung_2024.pdf"
GAS_PDF = "02_gas_y/10_Gas_Jahresabrechnung_2025.pdf"
NOISE_PDF = "05_telecom/22_Internet_Vertrag.pdf"
DIM = 64


class FakeEmbedder:
    """Bag-of-words embeddings: texts with shared words are similar (deterministic)."""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.calls: list[list[str]] = []

    def embed(self, **kwargs):
        if self.fail:
            raise RuntimeError("service down")
        texts = list(kwargs["input"])
        self.calls.append(texts)
        return SimpleNamespace(embeddings=[self._vector(text) for text in texts])

    @staticmethod
    def _vector(text: str) -> list[float]:
        text = re.sub(r"search_(document|query): ", "", text.lower())
        vector = [0.0] * DIM
        for word in re.findall(r"\w+", text):
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def _chunk(
    chunk_id: str,
    content: str,
    pdf: str = POWER_PDF,
    chunk_type: ChunkType = ChunkType.TEXT,
    heading_stack: tuple[str, ...] = ("Rechnung",),
    page: int = 1,
    utility: UtilityType = UtilityType.ELECTRICITY,
    period: tuple[date, date] | None = (date(2024, 1, 1), date(2024, 12, 31)),
) -> DocumentChunk:
    is_table = chunk_type in (ChunkType.TABLE_ROW, ChunkType.TABLE_SUMMARY)
    return DocumentChunk(
        chunk_id=chunk_id,
        chunk_type=chunk_type,
        content=content,
        heading_stack=heading_stack,
        page_number=page,
        metadata=ChunkMetadata(
            filename=pdf,
            utility_type=utility,
            doc_type=DocType.BILL,
            provider="Anbieter",
            document_date=date(2025, 1, 18),
            billing_period_start=period[0] if period else None,
            billing_period_end=period[1] if period else None,
            table_id="tab_01" if is_table else None,
            image_path="images/x.png" if chunk_type is ChunkType.IMAGE else None,
        ),
    )


def _corpus() -> list[ParsedDocument]:
    return [
        ParsedDocument(
            file=POWER_PDF,
            page_count=1,
            chunks=(
                _chunk("p_h", "Rechnung", chunk_type=ChunkType.HEADING),
                _chunk("p_t1", "Arbeitspreis 34,80 ct/kWh netto Strom"),
                _chunk("p_t2", "Kontakt Servicetelefon Kundenservice", heading_stack=()),
                _chunk(
                    "p_r1",
                    "Position: Arbeitspreis | Betrag: 34,80",
                    chunk_type=ChunkType.TABLE_ROW,
                ),
                _chunk(
                    "p_s1",
                    "Die Tabelle nennt den Arbeitspreis.",
                    chunk_type=ChunkType.TABLE_SUMMARY,
                ),
            ),
        ),
        ParsedDocument(
            file=GAS_PDF,
            page_count=1,
            chunks=(
                _chunk(
                    "g_t1",
                    "Arbeitspreis Gas 9,80 ct/kWh",
                    pdf=GAS_PDF,
                    utility=UtilityType.GAS,
                    period=(date(2025, 1, 1), date(2025, 12, 31)),
                    heading_stack=("Gasabrechnung",),
                ),
            ),
        ),
        ParsedDocument(
            file=NOISE_PDF,
            page_count=1,
            chunks=(
                _chunk(
                    "n_t1",
                    "Arbeitspreis Internet Flatrate 39,99",
                    pdf=NOISE_PDF,
                    utility=UtilityType.TELECOM,
                    period=None,
                    heading_stack=("Vertrag",),
                ),
            ),
        ),
    ]


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(project_root=tmp_path)


@pytest.fixture
def retriever(settings) -> Retriever:
    settings.processed_dir.mkdir(parents=True)
    for document in _corpus():
        path = chunks_path(settings.processed_dir, document.file)
        path.write_text(document.model_dump_json(), encoding="utf-8")
    embedder = FakeEmbedder()
    vector_client = chromadb.PersistentClient(path=str(settings.vectors_dir))
    build_index(settings, embedder, vector_client)
    return Retriever(settings, embedder, get_collection(settings, vector_client))


class TestIndexText:
    def test_prefix_has_folder_file_and_headings(self):
        chunk = _chunk("c", "x", heading_stack=("Rechnung", "Preise"))

        assert hierarchy_prefix(chunk) == (
            "[01_electricity_x | 04_Strom_Jahresabrechnung_2024 | Rechnung > Preise]"
        )

    def test_prefix_without_headings_has_no_empty_part(self):
        assert hierarchy_prefix(_chunk("c", "x", heading_stack=())) == (
            "[01_electricity_x | 04_Strom_Jahresabrechnung_2024]"
        )

    def test_embedding_text_starts_with_document_task_prefix(self):
        text = embedding_text(_chunk("c", "Inhalt"), "search_document: ")

        assert text.startswith("search_document: [01_electricity_x |")
        assert text.endswith("] Inhalt")

    def test_record_is_flat_and_leaves_out_none(self):
        record = chunk_record(_chunk("c", "x", period=None))

        assert "period_start" not in record and "contract_id" not in record
        assert record["has_heading"] is True
        assert record["utility_type"] == "electricity"
        assert record["heading_stack"] == '["Rechnung"]'

    def test_date_number_is_comparable(self):
        assert date_number(date(2025, 12, 31)) == 20251231
        assert date_number(date(2025, 2, 1)) < date_number(date(2025, 11, 1))


class TestBuildIndex:
    def test_headings_are_not_indexed(self, retriever, settings):
        collection = get_collection(settings, chromadb.PersistentClient(str(settings.vectors_dir)))

        assert collection.count() == 6
        assert "p_h" not in collection.get()["ids"]

    def test_rebuild_is_idempotent(self, retriever, settings):
        vector_client = chromadb.PersistentClient(path=str(settings.vectors_dir))

        report = build_index(settings, FakeEmbedder(), vector_client)

        assert report.chunk_count == 6
        assert report.skipped_headings == 1
        assert report.document_count == 3
        assert report.chunks_by_type["table_summary"] == 1
        assert get_collection(settings, vector_client).count() == 6

    def test_embeds_in_batches_with_document_prefix(self, settings):
        settings.processed_dir.mkdir(parents=True)
        for document in _corpus():
            path = chunks_path(settings.processed_dir, document.file)
            path.write_text(document.model_dump_json(), encoding="utf-8")
        small = settings.model_copy(update={"retrieval": RetrievalSettings(embed_batch_size=4)})
        embedder = FakeEmbedder()

        build_index(small, embedder, chromadb.PersistentClient(path=str(settings.vectors_dir)))

        assert [len(batch) for batch in embedder.calls] == [4, 2]
        assert all(text.startswith("search_document: [") for text in embedder.calls[0])

    def test_missing_processed_files_fail_fast(self, settings):
        settings.processed_dir.mkdir(parents=True)

        with pytest.raises(RetrievalError, match="ingestion"):
            load_chunks(settings.processed_dir)

    def test_embedding_failure_becomes_retrieval_error(self, settings):
        settings.processed_dir.mkdir(parents=True)
        document = _corpus()[0]
        chunks_path(settings.processed_dir, document.file).write_text(
            document.model_dump_json(), encoding="utf-8"
        )

        with pytest.raises(RetrievalError, match="embedding with nomic-embed-text failed"):
            build_index(
                settings,
                FakeEmbedder(fail=True),
                chromadb.PersistentClient(path=str(settings.vectors_dir)),
            )

    def test_search_without_index_names_the_command(self, settings):
        client = chromadb.PersistentClient(path=str(settings.vectors_dir))

        with pytest.raises(RetrievalError, match="retrieval index"):
            get_collection(settings, client)


class TestQueryTerms:
    def test_stop_words_and_short_words_are_dropped(self):
        terms = tokenize_query("Welche Kündigungsfrist gilt für den Gasvertrag?", 3)

        assert terms == ("kuendigungsfrist", "gasvertrag")

    def test_compound_matches_path_word_as_prefix(self):
        matched = path_matches(
            ("stromrechnung", "2024", "wasser"), POWER_PDF, ("Rechnung",), min_chars=3
        )

        assert matched == ("stromrechnung", "2024")

    def test_umlaut_query_matches_ascii_file_name(self):
        terms = tokenize_query("Gebühren", 3)

        matched = path_matches(terms, "03_water/14_Wasser_Gebuehrenanpassung.pdf", (), 3)

        assert matched == ("gebuehren",)

    def test_digits_in_path_do_not_match_by_prefix(self):
        assert path_matches(("2024er",), POWER_PDF, (), 3) == ()


class TestWhereClause:
    def test_no_options_means_no_clause(self):
        assert build_where(SearchOptions()) is None

    def test_single_condition_is_not_wrapped(self):
        options = SearchOptions(metadata_filter=MetadataFilter(utility_type=UtilityType.GAS))

        assert build_where(options) == {"utility_type": {"$eq": "gas"}}

    def test_year_filter_uses_period_overlap(self):
        options = SearchOptions(metadata_filter=MetadataFilter.for_year(2025))

        assert build_where(options) == {
            "$and": [
                {"period_start": {"$lte": 20251231}},
                {"period_end": {"$gte": 20250101}},
            ]
        }

    def test_all_options_are_combined(self):
        options = SearchOptions(
            metadata_filter=MetadataFilter(doc_type=DocType.BILL, contract_id="X-1"),
            chunk_types=frozenset({ChunkType.TEXT, ChunkType.TABLE_ROW}),
            require_heading=True,
        )

        conditions = build_where(options)["$and"]

        assert {"doc_type": {"$eq": "bill"}} in conditions
        assert {"contract_id": {"$eq": "X-1"}} in conditions
        assert {"chunk_type": {"$in": ["table_row", "text"]}} in conditions
        assert {"has_heading": {"$eq": True}} in conditions

    def test_half_period_is_rejected(self):
        with pytest.raises(ValidationError, match="both"):
            MetadataFilter(period_start=date(2025, 1, 1))


class TestSearch:
    def test_score_can_be_recomputed_by_hand(self, retriever):
        hits = retriever.search("Arbeitspreis Strom")

        assert hits
        for hit in hits:
            assert hit.final_score == pytest.approx(hit.base_score * hit.boost)
            assert hit.boost in (1.0, 1.5)

    def test_boost_applies_for_path_match_only(self, retriever):
        hits = {h.chunk_id: h for h in retriever.search("Strom Arbeitspreis", SearchOptions())}

        assert hits["p_t1"].boost == 1.5
        assert "strom" in hits["p_t1"].matched_terms
        assert hits["n_t1"].boost == 1.0
        assert hits["n_t1"].matched_terms == ()

    def test_boost_off_gives_plain_cosine(self, retriever):
        options = SearchOptions(use_hierarchy_boost=False)

        hits = retriever.search("Strom Arbeitspreis", options)

        assert all(hit.boost == 1.0 and hit.final_score == hit.base_score for hit in hits)

    def test_boost_changes_the_order(self, retriever):
        plain = retriever.search("Strom Arbeitspreis", SearchOptions(use_hierarchy_boost=False))
        boosted = retriever.search("Strom Arbeitspreis", SearchOptions())

        assert plain[0].chunk_id != "n_t1" or boosted[0].chunk_id != "n_t1"
        assert boosted[0].filename == POWER_PDF

    def test_filter_excludes_other_utilities(self, retriever):
        options = SearchOptions(metadata_filter=MetadataFilter(utility_type=UtilityType.GAS))

        hits = retriever.search("Arbeitspreis", options)

        assert {hit.filename for hit in hits} == {GAS_PDF}

    def test_year_filter_drops_documents_without_period(self, retriever):
        options = SearchOptions(metadata_filter=MetadataFilter.for_year(2025))

        hits = retriever.search("Arbeitspreis", options)

        assert {hit.filename for hit in hits} == {GAS_PDF}

    def test_filter_without_match_gives_no_hits(self, retriever):
        options = SearchOptions(
            metadata_filter=MetadataFilter(utility_type=UtilityType.DISTRICT_HEATING)
        )

        assert retriever.search("Grundpreis Fernwärme", options) == []

    def test_chunk_type_restriction(self, retriever):
        options = SearchOptions(chunk_types=frozenset({ChunkType.TABLE_ROW}))

        hits = retriever.search("Arbeitspreis", options)

        assert [hit.chunk_type for hit in hits] == [ChunkType.TABLE_ROW]

    def test_require_heading_skips_headless_chunks(self, retriever):
        hits = retriever.search("Kontakt Servicetelefon", SearchOptions(require_heading=True))

        assert "p_t2" not in {hit.chunk_id for hit in hits}

    def test_top_k_limits_and_candidates_are_reranked(self, retriever):
        assert len(retriever.search("Arbeitspreis")) == 5
        assert len(retriever.search("Arbeitspreis", SearchOptions(top_k=2))) == 2

    def test_empty_query_is_rejected(self, retriever):
        with pytest.raises(RetrievalError, match="empty query"):
            retriever.search("   ")

    def test_hit_keeps_heading_stack_and_page(self, retriever):
        hit = next(
            h for h in retriever.search("Gasabrechnung Arbeitspreis") if h.chunk_id == "g_t1"
        )

        assert hit.heading_stack == ("Gasabrechnung",)
        assert hit.page_number == 1
        assert hit.chunk_type is ChunkType.TEXT


class TestEvidence:
    def test_groups_by_document_and_chapter(self, retriever):
        hits = retriever.search("Arbeitspreis Strom", SearchOptions(top_k=6))

        documents = build_evidence(hits)

        assert {d.filename for d in documents} == {h.filename for h in hits}
        assert documents == sorted(documents, key=lambda d: -d.best_score)
        power = next(d for d in documents if d.filename == POWER_PDF)
        assert {c.title for c in power.chapters} <= {"Rechnung", "(ohne Kapitel)"}

    def test_text_view_marks_model_output_and_shows_the_score_formula(self, retriever):
        hits = retriever.search("Arbeitspreis Strom", SearchOptions(top_k=6))

        text = render_evidence_text(build_evidence(hits))

        assert "KI-Zusammenfassung, kein Beleg" in text
        assert "[KI]" in text
        assert " × 1.5 = " in text
        assert "Pfadtreffer: strom" in text


def _catalog() -> DocumentCatalog:
    def meta(file: str, utility: UtilityType, noise: bool) -> DocumentMeta:
        return DocumentMeta(
            file=file,
            utility_type=utility,
            doc_type=DocType.BILL,
            provider="x",
            document_date=date(2025, 1, 1),
            is_noise_document=noise,
        )

    return DocumentCatalog(
        documents=(
            meta(POWER_PDF, UtilityType.ELECTRICITY, False),
            meta(GAS_PDF, UtilityType.GAS, False),
            meta(NOISE_PDF, UtilityType.TELECOM, True),
        )
    )


def _question(question_id: str, text: str, source_file: str | None, category: str = "standard"):
    return {
        "id": question_id,
        "category": category,
        "question": text,
        "expected_answer": "x",
        "facts": [],
        "sources": [{"file": source_file, "page": 1}] if source_file else [],
        "expected_tools": [],
        "is_answerable": category != "negative",
        "tests": "x",
    }


class TestComparison:
    def test_rank_and_noise_of_one_question(self, retriever):
        parsed = _truth([_question("S1", "Arbeitspreis Strom", POWER_PDF)]).questions[0]
        hits = retriever.search("Arbeitspreis Strom", SearchOptions(top_k=5))

        result = evaluate_question(parsed, "x", hits, _catalog())

        assert result.file_rank == 1
        assert result.page_rank == 1
        assert result.noise_hits == 1

    def test_unfound_source_has_no_rank(self, retriever):
        parsed = _truth([_question("S1", "Arbeitspreis", "02_gas_y/other.pdf")]).questions[0]
        hits = retriever.search("Arbeitspreis")

        result = evaluate_question(parsed, "x", hits, _catalog())

        assert result.file_rank is None and result.page_rank is None

    def test_run_embeds_each_question_once_and_summarizes_each_config(self, retriever):
        truth = _truth(
            [
                _question("S1", "Arbeitspreis Strom", POWER_PDF),
                _question("N2", "Grundpreis Fernwärme", None, category="negative"),
            ]
        )
        configs = (
            CompareConfig(name="plain"),
            CompareConfig(name="filter", use_filter=True, use_boost=True),
        )
        embedder = retriever._client
        calls_before = len(embedder.calls)

        report = run_comparison(retriever, truth, _catalog(), 5, configs)

        assert len(embedder.calls) - calls_before == 2
        assert [s.config for s in report.summaries] == ["plain", "filter"]
        assert len(report.results) == 4
        assert all(s.answerable == 1 for s in report.summaries)
        negative_with_filter = next(
            r for r in report.results if r.question_id == "N2" and r.config == "filter"
        )
        assert negative_with_filter.hits == ()

    def test_summary_counts(self, retriever):
        parsed = _truth([_question("S1", "Arbeitspreis Strom", POWER_PDF)]).questions[0]
        result = evaluate_question(parsed, "c", retriever.search("Arbeitspreis Strom"), _catalog())

        summary = summarize("c", [result])

        assert (summary.file_found, summary.answerable) == (1, 1)
        assert summary.mean_reciprocal_rank == 1.0

    def test_markdown_has_summary_and_rank_table(self, retriever):
        truth = _truth([_question("S2", "Arbeitspreis Strom", POWER_PDF)])
        configs = (CompareConfig(name="filter+boost", use_filter=True, use_boost=True),)

        report = run_comparison(retriever, truth, _catalog(), 5, configs)
        markdown = render_markdown(report)

        assert "| filter+boost | 1/1 | 1/1 | 1.000 |" in markdown
        assert "| S2 | 1 / 1 |" in markdown


def _truth(questions: list[dict]) -> GroundTruth:
    """A ground truth with the given questions only (validation of counts is skipped)."""
    from audit_agent.corpus import Question

    parsed = tuple(Question.model_validate(q) for q in questions)
    return GroundTruth.model_construct(questions=parsed, planted_errors=(), audit_checks=())


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("neuer Arbeitspreis 2025", "Arbeitspreis"),
        ("Arbeitspreis Strom Rechnung 2025", "Arbeitspreis"),
        (
            "Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?",
            "Arbeitspreis",
        ),
        ("z-Zahl Gasabrechnung 2026", "z-Zahl"),
        ("Grundpreis Vertrag 2024", "Grundpreis"),
        ("Kündigungsfrist Gasvertrag", "Kündigungsfrist"),
        ("Brennwert Brennwert 2025", "Brennwert"),
        ("Gasabrechnung 2026", None),
        ("Ist die Gasabrechnung 2026 korrekt?", None),
        ("Arbeitspreis", None),
        ("Wohnfläche Verbrauch", None),
        ("", None),
    ],
)
def test_quantity_query_keeps_the_billing_quantity(query, expected):
    assert quantity_query(query) == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Arbeitspreis Strom Rechnung 2025", UtilityType.ELECTRICITY),
        (
            "Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?",
            UtilityType.ELECTRICITY,
        ),
        ("Kündigungsfrist Gasvertrag", UtilityType.GAS),
        ("Brennwert Erdgas 2025", UtilityType.GAS),
        ("Senkung Gas-Arbeitspreis", UtilityType.GAS),
        ("Grundgebühr Wasserrechnungen", UtilityType.WATER),
        ("Welchen Grundpreis zahle ich für Fernwärme?", UtilityType.DISTRICT_HEATING),
        ("Arbeitspreis Strom und Gas", None),
        ("Stromabrechnung und Gasabrechnung 2025", None),
        ("Wie hoch war der Wasserverbrauch 2025?", None),
        ("Warmwasser Nebenkostenabrechnung 2025", None),
        ("Anteil Betriebskosten 2025", None),
        ("Hauptgasse 4 Abschlag", None),
        ("", None),
    ],
)
def test_utility_in_query_needs_exactly_one_utility_word_or_document_compound(query, expected):
    assert utility_in_query(query) is expected


def test_with_query_utility_adds_the_utility_only_if_no_utility_filter_is_set():
    # Arrange
    plain = SearchOptions(metadata_filter=MetadataFilter(doc_type=DocType.BILL), top_k=3)
    chosen = SearchOptions(metadata_filter=MetadataFilter(utility_type=UtilityType.GAS))

    # Act
    narrowed = with_query_utility(plain, "Arbeitspreis Stromabrechnung 2025")

    # Assert
    assert narrowed.metadata_filter == MetadataFilter(
        utility_type=UtilityType.ELECTRICITY, doc_type=DocType.BILL
    )
    assert narrowed.top_k == 3
    assert plain.metadata_filter.utility_type is None
    assert with_query_utility(chosen, "Arbeitspreis Stromabrechnung 2025") is chosen
    assert with_query_utility(plain, "Anteil Betriebskosten 2025") is plain
