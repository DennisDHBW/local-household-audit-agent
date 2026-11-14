from __future__ import annotations

from pathlib import Path

import pytest

from audit_agent.config import Settings
from audit_agent.corpus import (
    CorpusError,
    DocumentCatalog,
    GroundTruth,
    QuestionCategory,
    load_document_catalog,
    load_ground_truth,
    missing_files,
)


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="module")
def catalog(settings: Settings) -> DocumentCatalog:
    return load_document_catalog(settings.documents_file)


@pytest.fixture(scope="module")
def ground_truth(settings: Settings) -> GroundTruth:
    return load_ground_truth(settings.ground_truth_file)


def test_every_pdf_has_exactly_one_metadata_entry(settings: Settings, catalog: DocumentCatalog):
    # Arrange / Act
    problems = missing_files(catalog, settings.dataset_dir)

    # Assert
    assert problems == []
    assert len(catalog.documents) == 30


def test_noise_documents_are_telecom_and_insurance(catalog: DocumentCatalog):
    # Arrange / Act
    noise = {d.file.split("/")[0] for d in catalog.documents if d.is_noise_document}

    # Assert
    assert noise == {"05_telecom_insurance"}


def test_bills_have_billing_period(catalog: DocumentCatalog):
    # Arrange
    handyman = {"20_", "21_"}

    # Act
    bills = [
        d
        for d in catalog.documents
        if d.doc_type == "bill" and not Path(d.file).name.startswith(tuple(handyman))
    ]

    # Assert
    assert bills
    assert all(d.billing_period_start and d.billing_period_end for d in bills)


def test_ground_truth_has_required_question_mix(ground_truth: GroundTruth):
    # Arrange / Act
    counts = {c: sum(q.category == c for q in ground_truth.questions) for c in QuestionCategory}

    # Assert
    assert counts == {
        QuestionCategory.STANDARD: 5,
        QuestionCategory.EDGE_CASE: 2,
        QuestionCategory.NEGATIVE: 2,
        QuestionCategory.ADDITIONAL: 3,
    }


def test_ground_truth_references_only_cataloged_files(
    catalog: DocumentCatalog, ground_truth: GroundTruth
):
    # Arrange
    cataloged = {d.file for d in catalog.documents}

    # Act
    unknown = ground_truth.referenced_files() - cataloged

    # Assert
    assert unknown == set()


def test_every_bill_is_covered_by_an_audit_check(
    catalog: DocumentCatalog, ground_truth: GroundTruth
):
    # Arrange
    checked = {c.file for c in ground_truth.audit_checks}
    expected = {
        d.file
        for d in catalog.documents
        if d.doc_type == "bill"
        and d.utility_type in {"electricity", "gas", "water", "service_charges"}
        and d.billing_period_start is not None
    }

    # Act / Assert
    assert checked == expected


def test_three_planted_errors_among_ten_checked_bills(ground_truth: GroundTruth):
    # Arrange / Act
    faulty = [c for c in ground_truth.audit_checks if not c.is_correct]

    # Assert
    assert len(ground_truth.audit_checks) == 10
    assert {c.planted_error_id for c in faulty} == {"E1", "E2", "E3"}


def test_negative_questions_have_no_sources(ground_truth: GroundTruth):
    # Arrange / Act
    negatives = [q for q in ground_truth.questions if q.category is QuestionCategory.NEGATIVE]

    # Assert
    assert all(not q.is_answerable and not q.sources for q in negatives)


def test_invalid_yaml_is_rejected(tmp_path: Path):
    # Arrange
    broken = tmp_path / "documents.yaml"
    broken.write_text("documents: [unclosed", encoding="utf-8")

    # Act / Assert
    with pytest.raises(CorpusError, match="invalid YAML"):
        load_document_catalog(broken)


def test_missing_file_is_rejected(tmp_path: Path):
    with pytest.raises(CorpusError, match="not found"):
        load_ground_truth(tmp_path / "nope.yaml")


def test_unknown_field_is_rejected(tmp_path: Path):
    # Arrange
    path = tmp_path / "documents.yaml"
    path.write_text(
        "documents:\n  - file: a.pdf\n    utility_type: gas\n    doc_type: bill\n"
        '    provider: "X"\n    document_date: 2025-01-01\n    colour: red\n',
        encoding="utf-8",
    )

    # Act / Assert
    with pytest.raises(CorpusError, match="colour"):
        load_document_catalog(path)


def test_half_open_billing_period_is_rejected(tmp_path: Path):
    # Arrange
    path = tmp_path / "documents.yaml"
    path.write_text(
        "documents:\n  - file: a.pdf\n    utility_type: gas\n    doc_type: bill\n"
        '    provider: "X"\n    document_date: 2025-01-01\n    billing_period_start: 2025-01-01\n',
        encoding="utf-8",
    )

    # Act / Assert
    with pytest.raises(CorpusError, match="needs both start and end"):
        load_document_catalog(path)


def test_duplicate_file_is_rejected(tmp_path: Path):
    # Arrange
    entry = (
        "  - file: a.pdf\n    utility_type: gas\n    doc_type: bill\n"
        '    provider: "X"\n    document_date: 2025-01-01\n'
    )
    path = tmp_path / "documents.yaml"
    path.write_text("documents:\n" + entry + entry, encoding="utf-8")

    # Act / Assert
    with pytest.raises(CorpusError, match="duplicate files"):
        load_document_catalog(path)


def test_wrong_question_mix_is_rejected(tmp_path: Path, ground_truth: GroundTruth):
    # Arrange: drop one standard question
    data = ground_truth.model_dump(mode="json")
    data["questions"] = [q for q in data["questions"] if q["id"] != "S1"]

    # Act / Assert
    with pytest.raises(ValueError, match="expected 5 questions"):
        GroundTruth.model_validate(data)


@pytest.mark.parametrize(
    ("file", "expected_texts"),
    [
        (
            "02_gas_neckarenergie/29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf",
            ["11.819 kWh", "1,0000", "1.367,99 EUR"],
        ),
        (
            "04_housing_utilities_contractors/30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf",
            ["82,00 m²", "26,28", "1.963,28 EUR", "43,28 EUR"],
        ),
        (
            "01_electricity_suedvolt/06_Strom_Jahresabrechnung_2025_SuedVolt.pdf",
            ["39,50 ct/kWh", "1.379,30 EUR"],
        ),
    ],
)
def test_planted_error_values_appear_in_pdf_text(
    settings: Settings, file: str, expected_texts: list[str]
):
    # Arrange
    import pymupdf

    with pymupdf.open(settings.dataset_dir / file) as pdf:
        text = " ".join(page.get_text() for page in pdf).replace("\xa0", " ")

    # Act / Assert
    for expected in expected_texts:
        assert expected in text
