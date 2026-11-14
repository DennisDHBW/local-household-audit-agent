"""Chunk models and the ingestion pipeline (idempotence, stale files, fail fast)."""

import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from audit_agent.config import Settings
from audit_agent.corpus import CorpusError, DocType, UtilityType, load_document_catalog
from audit_agent.ingestion import (
    Chunk,
    ChunkMetadata,
    ChunkType,
    ParsedDocument,
    chunks_path,
    load_parsed_document,
    run_ingestion,
)

REAL = Settings()
PDF = "01_electricity_suedvolt/05_Strom_Zwischenablesung_Info_2025.pdf"


def _metadata(**overrides) -> ChunkMetadata:
    values = {
        "filename": "x.pdf",
        "utility_type": UtilityType.GAS,
        "doc_type": DocType.BILL,
        "provider": "P",
        "document_date": date(2025, 1, 1),
    }
    return ChunkMetadata(**(values | overrides))


def _chunk(chunk_id="c1", chunk_type=ChunkType.TEXT, **overrides) -> Chunk:
    values = {
        "chunk_id": chunk_id,
        "chunk_type": chunk_type,
        "content": "Inhalt",
        "page_number": 1,
        "metadata": _metadata(),
    }
    return Chunk(**(values | overrides))


def test_table_row_without_table_id_is_rejected():
    with pytest.raises(ValidationError, match="table_id"):
        _chunk(chunk_type=ChunkType.TABLE_ROW)


def test_image_without_path_is_rejected():
    with pytest.raises(ValidationError, match="image_path"):
        _chunk(chunk_type=ChunkType.IMAGE)


def test_duplicate_chunk_ids_are_rejected():
    with pytest.raises(ValidationError, match="duplicate"):
        ParsedDocument(file="x.pdf", page_count=1, chunks=(_chunk("a"), _chunk("a")))


def test_chunk_metadata_hides_the_noise_flag():
    assert "is_noise_document" not in ChunkMetadata.model_fields


@pytest.fixture
def mini_settings(tmp_path: Path) -> Settings:
    """A project root with a one-document dataset copied from the real corpus."""
    root = tmp_path / "project"
    (root / "dataset" / Path(PDF).parent).mkdir(parents=True)
    shutil.copy(REAL.dataset_dir / PDF, root / "dataset" / PDF)
    entry = load_document_catalog(REAL.documents_file).by_file(PDF).model_dump(mode="json")
    entry = {key: value for key, value in entry.items() if value is not None}
    (root / "dataset" / "documents.yaml").write_text(
        yaml.safe_dump({"documents": [entry]}, allow_unicode=True), encoding="utf-8"
    )
    return Settings(project_root=root)


def test_pipeline_writes_one_json_per_pdf_and_reads_it_back(mini_settings):
    report = run_ingestion(mini_settings)

    target = chunks_path(mini_settings.processed_dir, PDF)
    parsed = load_parsed_document(target)
    assert target.name == "05_Strom_Zwischenablesung_Info_2025_chunks.json"
    assert report.documents == 1
    assert report.total_chunks == len(parsed.chunks) > 0
    assert parsed.file == PDF


def test_pipeline_is_idempotent(mini_settings):
    run_ingestion(mini_settings)
    target = chunks_path(mini_settings.processed_dir, PDF)
    first = target.read_bytes()

    run_ingestion(mini_settings)

    assert target.read_bytes() == first


def test_pipeline_removes_results_of_pdfs_that_left_the_catalog(mini_settings):
    stale = mini_settings.processed_dir / "99_old_chunks.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}", encoding="utf-8")

    run_ingestion(mini_settings)

    assert not stale.exists()


def test_pipeline_fails_fast_when_catalog_and_folder_disagree(mini_settings):
    (mini_settings.dataset_dir / PDF).unlink()

    with pytest.raises(CorpusError, match="disagree"):
        run_ingestion(mini_settings)
