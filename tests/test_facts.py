"""Fact store, bill audit and views (M8, ADR-0018); no Ollama, synthetic chunks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from audit_agent.config import Settings
from audit_agent.corpus import DocType, DocumentCatalog, DocumentMeta, TariffKind, UtilityType
from audit_agent.facts import CheckStatus, FactKind, FactStore, Role, check_bill
from audit_agent.facts.chart import render_chart
from audit_agent.facts.extract import extract_document, row_pairs
from audit_agent.facts.views import Topic, rows_for
from audit_agent.ingestion import ChunkMetadata, ChunkType, DocumentChunk, ParsedDocument

CONTRACT = DocumentMeta(
    file="01_e/31_Heizstrom_Vertrag.pdf",
    utility_type=UtilityType.ELECTRICITY,
    tariff_kind=TariffKind.HEATING,
    doc_type=DocType.CONTRACT,
    provider="SüdVolt",
    contract_id="H-1",
    document_date=date(2023, 12, 12),
    valid_from=date(2024, 1, 1),
)
LETTER = CONTRACT.model_copy(
    update={
        "file": "01_e/33_Heizstrom_Preis.pdf",
        "doc_type": DocType.PRICE_ADJUSTMENT,
        "valid_from": date(2025, 1, 1),
        "document_date": date(2024, 11, 15),
    }
)
BILL = CONTRACT.model_copy(
    update={
        "file": "01_e/34_Heizstrom_Rechnung_2025.pdf",
        "doc_type": DocType.BILL,
        "valid_from": None,
        "document_date": date(2026, 1, 20),
        "billing_period_start": date(2025, 1, 1),
        "billing_period_end": date(2025, 12, 31),
    }
)

CONTRACT_ROWS = [
    "Preisbestandteil: Grundpreis (inkl. Messstellenbetrieb Zweitarifzähler) | Einheit: EUR / Monat | "
    "Netto: 7,48 EUR | Brutto (inkl. 19 % USt.): 8,90 EUR",
    "Preisbestandteil: Arbeitspreis Hochtarif HT (06:00–22:00 Uhr) | Einheit: ct / kWh | Netto: 26,81 ct | "
    "Brutto (inkl. 19 % USt.): 31,90 ct",
    "Preisbestandteil: Arbeitspreis Niedertarif NT (22:00–06:00 Uhr) | Einheit: ct / kWh | Netto: 18,82 ct | "
    "Brutto (inkl. 19 % USt.): 22,40 ct",
    "Preisbestandteil: Monatlicher Abschlag (11 Teilbeträge Feb–Dez, jeweils 15.) | Einheit: EUR / Monat | "
    "Netto: 71,43 EUR | Brutto (inkl. 19 % USt.): 85,00 EUR",
]
LETTER_ROWS = [
    "Preisbestandteil: Grundpreis (EUR / Monat) | Bisher Netto: 7,48 EUR | Bisher Brutto: 8,90 EUR | "
    "Neu Netto (ab 01.01.2025): 8,32 EUR | Neu Brutto (inkl. 19 % USt.): 9,90 EUR",
    "Preisbestandteil: Arbeitspreis Hochtarif HT (ct / kWh) | Bisher Netto: 26,81 ct | Bisher Brutto: 31,90 ct | "
    "Neu Netto (ab 01.01.2025): 28,15 ct | Neu Brutto (inkl. 19 % USt.): 33,50 ct",
    "Preisbestandteil: Arbeitspreis Niedertarif NT (ct / kWh) | Bisher Netto: 18,82 ct | Bisher Brutto: 22,40 ct | "
    "Neu Netto (ab 01.01.2025): 20,25 ct | Neu Brutto (inkl. 19 % USt.): 24,10 ct",
]
BILL_ROWS = [
    "Rechnungsbetrag Heizstromlieferung 2025 (inkl. 19 % USt.): 1.257,82 EUR",
    "Abzüglich geleistete Abschlagszahlungen (11 × 95,00 EUR, Feb–Dez 2025): -1.045,00 EUR",
    "Zählernummer: 1EMH | Zählwerk: HT | Datum: 01.01.2025 | Ableseart: Anfangsstand (K) | "
    "Zählerstand: 2.620 kWh | Verbrauch: -",
    "Zählernummer: 1EMH | Zählwerk: HT | Datum: 31.12.2025 | Ableseart: Kundenablesung (K) | "
    "Zählerstand: 3.200 kWh | Verbrauch: 580 kWh",
    "Zählernummer: 1EMH | Zählwerk: NT | Datum: 01.01.2025 | Ableseart: Anfangsstand (K) | "
    "Zählerstand: 12.680 kWh | Verbrauch: -",
    "Zählernummer: 1EMH | Zählwerk: NT | Datum: 31.12.2025 | Ableseart: Kundenablesung (K) | "
    "Zählerstand: 16.100 kWh | Verbrauch: 3.920 kWh",
    "Abrechnungsposition: Arbeitspreis Hochtarif (HT) | Zeitraum / Menge: 580 kWh | Preis Netto: 28,15 ct/kWh | "
    "Preis Brutto: 33,50 ct/kWh | Betrag Netto: 163,28 EUR | Betrag Brutto: 194,30 EUR",
    "Abrechnungsposition: Arbeitspreis Niedertarif (NT) | Zeitraum / Menge: 3.920 kWh | Preis Netto: 20,25 ct/kWh | "
    "Preis Brutto: 24,10 ct/kWh | Betrag Netto: 793,88 EUR | Betrag Brutto: 944,72 EUR",
    "Abrechnungsposition: Grundpreis (12 Monate) | Zeitraum / Menge: 01.01. – 31.12.2025 | Preis Netto: 8,32 EUR/ Mon. | "
    "Preis Brutto: 9,90 EUR/ Mon. | Betrag Netto: 99,83 EUR | Betrag Brutto: 118,80 EUR",
    "Abrechnungsposition: Rechnungsbetrag inkl. 19 % Umsatzsteuer (200,83 EUR USt.) | Betrag Netto: 1.056,99 EUR | "
    "Betrag Brutto: 1.257,82 EUR",
]
BILL_2024_TEXT = (
    "Den Nachzahlungsbetrag von 81,90 EUR ziehen wir am 05.02.2025 ein. Ihr neuer monatlicher "
    "Heizstrom-Abschlag beträgt ab 15.02.2025 jeweils 95,00 EUR brutto (11 Abschläge Feb–Dez 2025)."
)


def _document(meta: DocumentMeta, rows: list[str], texts: tuple[str, ...] = ()) -> ParsedDocument:
    chunks = []
    stem = Path(meta.file).stem
    for i, row in enumerate(rows, start=1):
        metadata = ChunkMetadata.from_document(meta).model_copy(update={"table_id": "tab01"})
        chunks.append(
            DocumentChunk(
                chunk_id=f"{stem}_r{i:02d}",
                chunk_type=ChunkType.TABLE_ROW,
                content=row,
                page_number=1,
                metadata=metadata,
            )
        )
    for i, text in enumerate(texts, start=1):
        chunks.append(
            DocumentChunk(
                chunk_id=f"{stem}_t{i:02d}",
                chunk_type=ChunkType.TEXT,
                content=text,
                page_number=1,
                metadata=ChunkMetadata.from_document(meta),
            )
        )
    return ParsedDocument(file=meta.file, page_count=1, chunks=tuple(chunks))


def _store(bill_rows: list[str] = BILL_ROWS) -> FactStore:
    old_bill = BILL.model_copy(
        update={
            "file": "01_e/32_Heizstrom_Rechnung_2024.pdf",
            "billing_period_start": date(2024, 1, 1),
            "billing_period_end": date(2024, 12, 31),
        }
    )
    facts = extract_document(_document(CONTRACT, CONTRACT_ROWS), CONTRACT)
    facts += extract_document(_document(LETTER, LETTER_ROWS), LETTER)
    facts += extract_document(_document(old_bill, [], (BILL_2024_TEXT,)), old_bill)
    facts += extract_document(_document(BILL, bill_rows), BILL)
    return FactStore(facts=tuple(facts))


def test_row_pairs_split_columns_at_the_first_colon():
    assert row_pairs("A: 1 | B: 2: x | C") == [("A", "1"), ("B", "2: x"), ("C", "")]


def test_contract_and_letter_prices_get_zone_unit_and_validity():
    # Arrange / Act
    store = _store()
    nt = store.select([FactKind.ENERGY_PRICE], role=Role.AGREED, zone="NT")

    # Assert
    assert [(f.value, f.valid_from) for f in nt] == [
        (Decimal("22.40"), date(2024, 1, 1)),
        (Decimal("24.10"), date(2025, 1, 1)),
    ]
    assert all(f.unit == "ct/kWh" and f.tariff_kind is TariffKind.HEATING for f in nt)


def test_agreed_value_is_the_latest_that_applies_on_the_day():
    store = _store()
    kwargs = {"contract_id": "H-1", "utility_type": UtilityType.ELECTRICITY, "zone": "HT"}
    assert store.agreed(FactKind.ENERGY_PRICE, date(2024, 6, 1), **kwargs).value == Decimal("31.90")
    assert store.agreed(FactKind.ENERGY_PRICE, date(2025, 1, 1), **kwargs).value == Decimal("33.50")


def test_advance_from_a_sentence_ignores_the_balance_before_it():
    advances = _store().select([FactKind.ADVANCE], role=Role.AGREED)
    assert {(f.value, f.valid_from) for f in advances} == {
        (Decimal("85.00"), date(2024, 1, 1)),
        (Decimal("95.00"), date(2025, 2, 15)),
    }


def test_check_bill_finds_the_planted_nt_consumption_error_with_its_effect():
    # Arrange / Act
    report = check_bill(_store(), BILL)
    by_name = {c.name: c for c in report.checks}

    # Assert
    assert [c.name for c in report.deviations] == ["Verbrauch NT aus Zählerständen"]
    nt = by_name["Verbrauch NT aus Zählerständen"]
    assert nt.impact_eur == Decimal("120.50")
    assert "3.420 kWh" in nt.expected and "3.920 kWh" in nt.actual
    assert by_name["Arbeitspreis NT"].status is CheckStatus.OK
    assert by_name["angerechnete Abschläge"].status is CheckStatus.OK
    assert by_name["Summe der Positionen"].status is CheckStatus.OK


def test_check_bill_reports_a_wrong_price_against_the_letter():
    rows = [
        r.replace("Preis Brutto: 24,10 ct/kWh", "Preis Brutto: 25,10 ct/kWh") for r in BILL_ROWS
    ]
    report = check_bill(_store(rows), BILL)
    price = next(c for c in report.checks if c.name == "Arbeitspreis NT")
    assert price.status is CheckStatus.DEVIATION
    assert price.impact_eur == Decimal("39.20")  # 1,00 ct x 3.920 kWh


def test_a_bill_without_agreed_prices_is_unverifiable_not_wrong():
    store = FactStore(facts=tuple(extract_document(_document(BILL, BILL_ROWS), BILL)))
    report = check_bill(store, BILL)
    prices = [c for c in report.checks if c.name.startswith("Arbeitspreis")]
    assert prices and all(c.status is CheckStatus.UNVERIFIABLE for c in prices)


def test_consumption_rows_come_from_the_meter_readings(tmp_path: Path):
    # Arrange
    catalog = DocumentCatalog(documents=(CONTRACT, LETTER, BILL))

    # Act
    rows = rows_for(Topic.CONSUMPTION, _store(), catalog)
    png, data = render_chart(rows, Topic.CONSUMPTION, "Heizstrom 2025", tmp_path)

    # Assert
    assert [(r.series, r.value) for r in rows] == [
        ("Heizstrom HT", Decimal("580")),
        ("Heizstrom NT", Decimal("3420")),
    ]
    assert png.is_file() and png.stat().st_size > 1000
    assert '"value": "3420"' in data.read_text(encoding="utf-8")


REAL = Settings()


@pytest.mark.skipif(
    not (REAL.processed_dir / "35_Wasser_Jahresbescheid_2026_SWM_chunks.json").is_file(),
    reason="needs data/processed (run the ingestion first)",
)
def test_all_five_planted_errors_and_no_false_alarm_on_the_real_corpus():
    from audit_agent.corpus import load_document_catalog, load_ground_truth
    from audit_agent.facts import build_fact_store

    store = build_fact_store(REAL)
    catalog = load_document_catalog(REAL.documents_file)
    truth = load_ground_truth(REAL.ground_truth_file)
    for audit in truth.audit_checks:
        report = check_bill(store, catalog.by_file(audit.file))
        assert bool(report.deviations) is not audit.is_correct, audit.file


def test_balance_is_negative_for_a_credit_and_positive_for_a_back_payment():
    rows = [*BILL_ROWS, "Nachzahlungsbetrag (fällig am 05.02.2026): 212,82 EUR"]
    store = FactStore(facts=tuple(extract_document(_document(BILL, rows), BILL)))
    (balance,) = store.of_file(BILL.file, FactKind.BALANCE)
    assert balance.value == Decimal("212.82")
