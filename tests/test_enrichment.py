"""Enrichment: cache keys, summary check and the pipeline with a scripted Ollama fake."""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from audit_agent.config import Settings
from audit_agent.corpus import DocType, UtilityType
from audit_agent.enrichment import (
    EnrichmentCache,
    EnrichmentError,
    EnrichmentKind,
    ImageCaptioner,
    make_cache_key,
    run_enrichment,
    unsupported_numbers,
)
from audit_agent.enrichment.cache import CachedAnswer
from audit_agent.enrichment.prompts import build_caption_prompt, build_summary_prompt
from audit_agent.ingestion import (
    ChunkMetadata,
    ChunkType,
    DocumentChunk,
    ParsedDocument,
    chunks_path,
    load_parsed_document,
)
from audit_agent.preflight import MissingModelError

PDF = "01_x/04_bill.pdf"
IMAGE_RELATIVE = "images/04_bill_p2_img01.png"
CAPTION = "Balkendiagramm Stromverbrauch: 2022: 3.480 kWh, 2023: 3.390 kWh."
SUMMARY = "Die Tabelle nennt 14.200 kWh und 3.250 kWh Verbrauch."


class FakeEnrichmentOllama:
    """Answers captions for image calls and summaries for text calls; counts every call."""

    def __init__(
        self,
        installed: tuple[str, ...] = ("gemma3:4b", "llama3.2:latest"),
        summary: str = SUMMARY,
        caption: str = CAPTION,
        done_reason: str = "stop",
    ):
        self.installed = installed
        self.summary = summary
        self.caption = caption
        self.done_reason = done_reason
        self.chat_calls: list[dict] = []
        self.unloaded: list[str] = []

    def list(self):
        return SimpleNamespace(models=[SimpleNamespace(model=tag) for tag in self.installed])

    def ps(self):
        return SimpleNamespace(models=[SimpleNamespace(model="old-model:latest")])

    def generate(self, **kwargs):
        if kwargs.get("keep_alive") == 0:
            self.unloaded.append(kwargs["model"])

    def chat(self, **kwargs):
        self.chat_calls.append(kwargs)
        message = kwargs["messages"][-1]
        text = self.caption if "images" in message else self.summary
        return SimpleNamespace(message=SimpleNamespace(content=text), done_reason=self.done_reason)


def _metadata(table_id: str | None = None, image_path: str | None = None) -> ChunkMetadata:
    return ChunkMetadata(
        filename=PDF,
        utility_type=UtilityType.ELECTRICITY,
        doc_type=DocType.BILL,
        provider="SüdVolt",
        document_date=date(2025, 1, 18),
        table_id=table_id,
        columns=("Datum", "Zählerstand") if table_id else (),
        image_path=image_path,
    )


def _chunk(chunk_id, chunk_type, content, page=1, **meta) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        chunk_type=chunk_type,
        content=content,
        heading_stack=("Jahresrechnung 2024", "1. Verbrauch"),
        page_number=page,
        metadata=_metadata(**meta),
    )


def _write_processed(settings: Settings, extra: tuple[DocumentChunk, ...] = ()) -> Path:
    chunks = (
        _chunk("d_p1_t01", ChunkType.TEXT, "Fließtext"),
        _chunk(
            "d_p1_tab01_r01",
            ChunkType.TABLE_ROW,
            "Datum: 01.01.2024 | Zählerstand: 14.200 kWh",
            table_id="p1_tab01",
        ),
        _chunk(
            "d_p1_tab01_r02",
            ChunkType.TABLE_ROW,
            "Datum: 31.12.2024 | Zählerstand: 3.250 kWh",
            table_id="p1_tab01",
        ),
        _chunk(
            "d_p2_img01",
            ChunkType.IMAGE,
            "Abbildung auf Seite 2 (Beschreibung folgt im Enrichment)",
            page=2,
            image_path=IMAGE_RELATIVE,
        ),
        *extra,
    )
    document = ParsedDocument(file=PDF, page_count=2, chunks=chunks)
    image = settings.processed_dir / IMAGE_RELATIVE
    image.parent.mkdir(parents=True, exist_ok=True)
    image.write_bytes(b"fake-png-bytes")
    path = chunks_path(settings.processed_dir, PDF)
    path.write_text(document.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(project_root=tmp_path)


# ---- models, keys, cache -------------------------------------------------------------------


def test_table_summary_without_table_id_is_rejected():
    with pytest.raises(ValidationError, match="table_id"):
        _chunk("s", ChunkType.TABLE_SUMMARY, "Zusammenfassung")


def test_cache_key_is_stable_and_reacts_to_every_input():
    options = {"num_ctx": 8192, "temperature": 0}
    base = make_cache_key("table_summary", "llama3.2", "prompt", options)

    assert base == make_cache_key("table_summary", "llama3.2", "prompt", options)
    assert base != make_cache_key("image_caption", "llama3.2", "prompt", options)
    assert base != make_cache_key("table_summary", "llama3.1:8b", "prompt", options)
    assert base != make_cache_key("table_summary", "llama3.2", "other prompt", options)
    assert base != make_cache_key("table_summary", "llama3.2", "prompt", {**options, "num_ctx": 1})
    assert base != make_cache_key("table_summary", "llama3.2", "prompt", options, "abc123")


def test_cache_computes_once_and_survives_reopening(tmp_path: Path):
    calls = []

    def compute() -> CachedAnswer:
        calls.append(1)
        return CachedAnswer(text="Antwort", model="m", seconds=1.5)

    cache = EnrichmentCache(tmp_path / "cache")
    first, first_hit = cache.get_or_compute("key", compute)
    second, second_hit = cache.get_or_compute("key", compute)
    cache.close()
    reopened = EnrichmentCache(tmp_path / "cache")
    third = reopened.get("key")
    reopened.close()

    assert (first_hit, second_hit) == (False, True)
    assert first == second == third
    assert len(calls) == 1


def test_failed_computation_is_not_cached(tmp_path: Path):
    cache = EnrichmentCache(tmp_path / "cache")

    def fail() -> CachedAnswer:
        raise RuntimeError("model crashed")

    with pytest.raises(RuntimeError):
        cache.get_or_compute("key", fail)

    assert cache.get("key") is None
    cache.close()


def test_prompts_contain_context_and_rows():
    caption_prompt = build_caption_prompt(("Titel", "Kapitel"))
    summary_prompt = build_summary_prompt(("Titel",), ("Datum", "Wert"), ("Datum: 1 | Wert: 2",))

    assert "Titel > Kapitel" in caption_prompt
    assert "Spalten: Datum, Wert" in summary_prompt
    assert "- Datum: 1 | Wert: 2" in summary_prompt
    assert "(keine Kopfzeile)" in build_summary_prompt((), (), ("x",))


# ---- number check --------------------------------------------------------------------------


def test_numbers_from_the_table_are_supported():
    source = "Zählerstand: 14.200 kWh | Betrag: 1.189,00 EUR"

    assert unsupported_numbers("Es sind 14.200 kWh und 1.189 EUR.", source) == []


def test_date_written_in_words_is_not_reported():
    source = "Datum: 16.10.2024 | Leistung am 11.10.2024 | Zeitraum 01.2025"

    assert (
        unsupported_numbers("Erstellt am 16. Oktober 2024, Leistung im Januar 2025.", source) == []
    )


def test_invented_numbers_are_reported_and_small_counts_ignored():
    source = "Zählerstand: 14.200 kWh"

    assert unsupported_numbers("Drei von 4 Werten: 14.200 und 99.999 kWh.", source) == [99999.0]


# ---- pipeline ------------------------------------------------------------------------------


def test_pipeline_adds_caption_and_summary_chunk(settings: Settings):
    path = _write_processed(settings)
    client = FakeEnrichmentOllama()

    report = run_enrichment(settings, client)

    document = load_parsed_document(path)
    by_id = {chunk.chunk_id: chunk for chunk in document.chunks}
    assert by_id["d_p2_img01"].content == CAPTION
    summary = by_id["d_p1_tab01_sum"]
    assert summary.chunk_type is ChunkType.TABLE_SUMMARY
    assert summary.content == SUMMARY
    assert summary.metadata.table_id == "p1_tab01"
    assert summary.heading_stack == ("Jahresrechnung 2024", "1. Verbrauch")
    ids = [chunk.chunk_id for chunk in document.chunks]
    assert ids.index("d_p1_tab01_sum") == ids.index("d_p1_tab01_r01") - 1
    assert (report.cache_hits, report.cache_misses) == (0, 2)
    assert report.flagged_summaries == []


def test_second_run_uses_only_the_cache_and_changes_nothing(settings: Settings):
    path = _write_processed(settings)
    client = FakeEnrichmentOllama()
    run_enrichment(settings, client)
    first_output = path.read_text(encoding="utf-8")
    calls_after_first_run = len(client.chat_calls)

    report = run_enrichment(settings, client)

    assert len(client.chat_calls) == calls_after_first_run
    assert (report.cache_hits, report.cache_misses) == (2, 0)
    assert path.read_text(encoding="utf-8") == first_output


def test_rerun_after_ingestion_restores_enrichment_from_cache(settings: Settings):
    path = _write_processed(settings)
    client = FakeEnrichmentOllama()
    run_enrichment(settings, client)
    enriched = path.read_text(encoding="utf-8")
    _write_processed(settings)  # the ingestion overwrote the file with the plain parser output
    calls = len(client.chat_calls)

    run_enrichment(settings, client)

    assert len(client.chat_calls) == calls
    assert path.read_text(encoding="utf-8") == enriched


def test_old_summary_is_replaced_not_duplicated(settings: Settings):
    old = _chunk(
        "d_p1_tab01_sum", ChunkType.TABLE_SUMMARY, "Alte Zusammenfassung", table_id="p1_tab01"
    )
    path = _write_processed(settings, extra=(old,))

    run_enrichment(settings, FakeEnrichmentOllama(), kinds=frozenset({EnrichmentKind.TABLES}))

    summaries = [
        chunk
        for chunk in load_parsed_document(path).chunks
        if chunk.chunk_type is ChunkType.TABLE_SUMMARY
    ]
    assert [chunk.content for chunk in summaries] == [SUMMARY]


def test_dry_run_counts_open_jobs_without_calling_the_model(settings: Settings):
    path = _write_processed(settings)
    before = path.read_text(encoding="utf-8")
    client = FakeEnrichmentOllama(installed=())

    report = run_enrichment(settings, client, is_dry_run=True)

    assert (report.cache_hits, report.cache_misses) == (0, 2)
    assert client.chat_calls == []
    assert path.read_text(encoding="utf-8") == before


def test_only_images_and_limit_restrict_the_jobs(settings: Settings):
    path = _write_processed(settings)
    client = FakeEnrichmentOllama()

    report = run_enrichment(settings, client, kinds=frozenset({EnrichmentKind.IMAGES}), limit=1)

    assert [item.kind for item in report.items] == [EnrichmentKind.IMAGES]
    assert len(client.chat_calls) == 1
    types = {chunk.chunk_type for chunk in load_parsed_document(path).chunks}
    assert ChunkType.TABLE_SUMMARY not in types


def test_each_model_is_unloaded_after_its_phase(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama()

    run_enrichment(settings, client)

    assert client.unloaded == ["old-model:latest", "gemma3:4b", "llama3.2"]


def test_summary_with_invented_number_is_flagged(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama(summary="Der Verbrauch beträgt 99.999 kWh.")

    report = run_enrichment(settings, client)

    assert [item.unsupported_numbers for item in report.flagged_summaries] == [[99999.0]]


def test_missing_processed_files_fail_fast(settings: Settings):
    with pytest.raises(EnrichmentError, match="ingestion"):
        run_enrichment(settings, FakeEnrichmentOllama())


def test_missing_model_fails_before_any_call(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama(installed=("llama3.2:latest",))

    with pytest.raises(MissingModelError, match="gemma3:4b"):
        run_enrichment(settings, client)

    assert client.chat_calls == []


def test_missing_image_file_fails_fast(settings: Settings):
    _write_processed(settings)
    (settings.processed_dir / IMAGE_RELATIVE).unlink()

    with pytest.raises(EnrichmentError, match="missing"):
        run_enrichment(settings, FakeEnrichmentOllama())


def test_empty_model_answer_is_an_error_and_not_cached(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama(caption="   ")

    with pytest.raises(EnrichmentError, match="empty"):
        run_enrichment(settings, client, kinds=frozenset({EnrichmentKind.IMAGES}))

    cache = EnrichmentCache(settings.cache_dir / "enrichment")
    captioner = ImageCaptioner(client, settings, cache)
    assert not captioner.is_cached(b"fake-png-bytes", ("Jahresrechnung 2024", "1. Verbrauch"))
    cache.close()


def test_caption_call_sends_the_image_and_deterministic_options(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama()

    run_enrichment(settings, client, kinds=frozenset({EnrichmentKind.IMAGES}))

    call = client.chat_calls[0]
    assert call["model"] == settings.models.vision
    assert call["options"]["temperature"] == 0
    assert call["options"]["num_ctx"] == settings.num_ctx
    assert len(call["messages"][0]["images"]) == 1


def test_answer_cut_off_by_the_token_limit_is_flagged(settings: Settings):
    _write_processed(settings)
    client = FakeEnrichmentOllama(done_reason="length")

    report = run_enrichment(settings, client)

    assert len(report.truncated) == 2
    assert all(item.is_truncated for item in report.truncated)


def test_complete_answers_are_not_flagged_as_truncated(settings: Settings):
    _write_processed(settings)

    report = run_enrichment(settings, FakeEnrichmentOllama())

    assert report.truncated == []


def test_prompts_forbid_guessing_numbers_and_comparing_columns():
    caption_prompt = build_caption_prompt(())
    summary_prompt = build_summary_prompt((), (), ("x",))

    assert "schätze keine Zahlen" in caption_prompt
    assert "keine Differenzen" in summary_prompt
