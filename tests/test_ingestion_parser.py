"""Parser tests on synthetic PDFs (fast, no LLM) and on a few real corpus documents."""

from datetime import date
from pathlib import Path

import pymupdf
import pytest

from audit_agent.config import ParserSettings, Settings
from audit_agent.corpus import DocType, DocumentMeta, UtilityType, load_document_catalog
from audit_agent.ingestion import ChunkType, DocumentParser, ParseError

SETTINGS = Settings()
LONG_SENTENCE = "Dies ist ein längerer Satz über die Abrechnung der Energiekosten im Jahr. "


def _meta(file: str = "sample/sample.pdf") -> DocumentMeta:
    return DocumentMeta(
        file=file,
        utility_type=UtilityType.ELECTRICITY,
        doc_type=DocType.BILL,
        provider="Test GmbH",
        document_date=date(2025, 1, 31),
    )


def _draw_table(page: pymupdf.Page, top: float, rows: list[list[str]]) -> None:
    columns = [50, 200, 330, 460]
    height = 20
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            rect = pymupdf.Rect(
                columns[c], top + r * height, columns[c + 1], top + (r + 1) * height
            )
            page.draw_rect(rect, color=(0, 0, 0), width=0.8)
            font = "hebo" if r == 0 else "helv"
            page.insert_text((rect.x0 + 4, rect.y1 - 6), text, fontname=font, fontsize=9)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 20), "Kunden-Nr. 4711 Seite 1 von 1", fontsize=7)  # running header
    page.insert_text((50, 80), "1. Kosten der Energie", fontname="hebo", fontsize=14)
    page.insert_text(
        (50, 105), "Dies ist ein normaler Absatz mit genug Text zum Testen.", fontsize=9
    )
    page.insert_text((50, 140), "1.1 Strom", fontname="hebo", fontsize=11)
    page.insert_text((50, 160), "Datum:", fontsize=9)
    page.insert_text((50, 175), "18.01.2025", fontsize=9)
    _draw_table(
        page,
        200,
        [
            ["Position", "Menge", "Betrag"],
            ["Arbeitspreis", "1.000 kWh", "300,00 EUR"],
            ["Grundpreis", "12 Monate", "120,00 EUR"],
        ],
    )
    page.insert_text((50, 815), "Amtsgericht Musterstadt HRB 1234 · IBAN DE00 0000", fontsize=6)
    path = tmp_path / "sample.pdf"
    doc.save(path)
    return path


@pytest.fixture
def parser(tmp_path: Path) -> DocumentParser:
    return DocumentParser(ParserSettings(), tmp_path / "images")


def test_headings_build_a_stack_with_levels(parser, sample_pdf):
    # Arrange / Act
    result = parser.parse(sample_pdf, _meta())

    # Assert
    headings = [c for c in result.chunks if c.chunk_type is ChunkType.HEADING]
    assert [h.content for h in headings] == ["1. Kosten der Energie", "1.1 Strom"]
    assert headings[0].heading_stack == ("1. Kosten der Energie",)
    assert headings[1].heading_stack == ("1. Kosten der Energie", "1.1 Strom")


def test_text_chunk_carries_the_active_heading_stack(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    paragraph = next(c for c in result.chunks if "normaler Absatz" in c.content)
    assert paragraph.chunk_type is ChunkType.TEXT
    assert paragraph.heading_stack == ("1. Kosten der Energie",)


def test_short_fragments_are_merged_into_one_chunk(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    assert any(c.content == "Datum: 18.01.2025" for c in result.chunks)


def test_table_rows_are_serialised_with_column_names(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    rows = [c for c in result.chunks if c.chunk_type is ChunkType.TABLE_ROW]
    assert [r.content for r in rows] == [
        "Position: Arbeitspreis | Menge: 1.000 kWh | Betrag: 300,00 EUR",
        "Position: Grundpreis | Menge: 12 Monate | Betrag: 120,00 EUR",
    ]
    assert rows[0].metadata.table_id == "p1_tab01"
    assert rows[0].metadata.columns == ("Position", "Menge", "Betrag")
    assert rows[0].heading_stack == ("1. Kosten der Energie", "1.1 Strom")
    assert [r.chunk_id for r in rows] == ["sample_p1_tab01_r01", "sample_p1_tab01_r02"]


def test_table_area_does_not_appear_twice_as_text(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    text = " ".join(c.content for c in result.chunks if c.chunk_type is ChunkType.TEXT)
    assert "Arbeitspreis" not in text


def test_running_header_and_letter_footer_are_dropped(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    everything = " ".join(c.content for c in result.chunks)
    assert "Amtsgericht" not in everything
    assert "Seite 1 von 1" not in everything


def test_document_metadata_is_copied_to_every_chunk(parser, sample_pdf):
    result = parser.parse(sample_pdf, _meta())

    assert {c.metadata.filename for c in result.chunks} == {"sample/sample.pdf"}
    assert {c.metadata.provider for c in result.chunks} == {"Test GmbH"}
    assert {c.metadata.utility_type for c in result.chunks} == {UtilityType.ELECTRICITY}


def test_chunk_ids_are_unique_and_deterministic(parser, sample_pdf):
    first = parser.parse(sample_pdf, _meta())
    second = parser.parse(sample_pdf, _meta())

    ids = [c.chunk_id for c in first.chunks]
    assert len(ids) == len(set(ids))
    assert ids == [c.chunk_id for c in second.chunks]


def test_long_paragraph_is_split_below_the_limit(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    long_text = LONG_SENTENCE * 60
    page.insert_textbox(pymupdf.Rect(40, 60, 560, 780), long_text, fontsize=9)
    path = tmp_path / "long.pdf"
    doc.save(path)
    parser = DocumentParser(ParserSettings(max_block_chars=400), tmp_path / "images")

    result = parser.parse(path, _meta("long.pdf"))

    lengths = [len(c.content) for c in result.chunks]
    assert len(lengths) > 1
    assert max(lengths) <= 400


def test_image_is_extracted_and_referenced(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 80), "Eine Abbildung zum Verbrauch im Jahr 2024", fontsize=9)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 100), False)
    pixmap.clear_with(180)
    page.insert_image(pymupdf.Rect(50, 120, 350, 270), pixmap=pixmap)
    path = tmp_path / "chart.pdf"
    doc.save(path)
    images_dir = tmp_path / "images"

    result = DocumentParser(ParserSettings(), images_dir).parse(path, _meta("chart.pdf"))

    image = next(c for c in result.chunks if c.chunk_type is ChunkType.IMAGE)
    assert image.metadata.image_path == f"images/{image.chunk_id}.png"
    assert (images_dir / f"{image.chunk_id}.png").is_file()


def test_missing_pdf_fails_fast(parser, tmp_path):
    with pytest.raises(ParseError, match="not found"):
        parser.parse(tmp_path / "missing.pdf", _meta())


def test_empty_pdf_fails_fast(parser, tmp_path):
    doc = pymupdf.open()
    doc.new_page()
    path = tmp_path / "empty.pdf"
    doc.save(path)

    with pytest.raises(ParseError):
        parser.parse(path, _meta())


# ---- real corpus documents (golden checks) --------------------------------------------------

CATALOG = load_document_catalog(SETTINGS.documents_file)


@pytest.fixture(scope="module")
def corpus_parse(tmp_path_factory):
    parser = DocumentParser(SETTINGS.parser, tmp_path_factory.mktemp("images"))

    def parse(file: str):
        return parser.parse(SETTINGS.dataset_dir / file, CATALOG.by_file(file))

    cache: dict[str, object] = {}

    def cached(file: str):
        if file not in cache:
            cache[file] = parse(file)
        return cache[file]

    return cached


def _contents(parsed, chunk_type: ChunkType) -> list[str]:
    return [c.content for c in parsed.chunks if c.chunk_type is chunk_type]


def test_electricity_bill_table_keeps_column_names_and_amounts(corpus_parse):
    parsed = corpus_parse("01_electricity_suedvolt/04_Strom_Jahresabrechnung_2024_SuedVolt.pdf")

    rows = _contents(parsed, ChunkType.TABLE_ROW)
    assert any(
        "Abrechnungsposition: Arbeitspreis ÖkoStrom" in r
        and "Zeitraum / Menge: 3.250 kWh" in r
        and "Betrag Brutto: 1.131,00 EUR" in r
        for r in rows
    )
    assert any(r.startswith("Rechnungsbetrag Stromlieferung 2024") for r in rows)


def test_planted_gas_error_is_readable_in_the_json_rows(corpus_parse):
    parsed = corpus_parse("02_gas_neckarenergie/29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf")

    rows = _contents(parsed, ChunkType.TABLE_ROW)
    assert any("z-Zahl: 1,0000" in r and "Volumen: 1.060 m³" in r for r in rows)
    assert "Rechnungsbetrag Erdgaslieferung 2026 (inkl. 19 % USt.): 1.367,99 EUR" in rows
    assert (
        "Abzüglich geleistete Abschlagszahlungen (11 × 125,00 EUR, Feb–Dez 2026): -1.375,00 EUR"
        in rows
    )


def test_planted_service_charge_error_is_readable(corpus_parse):
    parsed = corpus_parse(
        "04_housing_utilities_contractors/30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf"
    )

    assert any("Wohnfläche 82,00 m²" in t for t in _contents(parsed, ChunkType.TEXT))


def test_touching_tables_are_split_at_the_section_title(corpus_parse):
    parsed = corpus_parse("02_gas_neckarenergie/10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf")

    meter_rows = [c for c in parsed.chunks if c.metadata.table_id == "p1_tab03"]
    cost_rows = [c for c in parsed.chunks if c.metadata.table_id == "p1_tab04"]
    assert meter_rows[0].metadata.columns[0] == "Zählernummer"
    assert cost_rows[0].metadata.columns[0] == "Abrechnungsposition"
    assert cost_rows[0].heading_stack[-1].startswith("2. Entgeltberechnung")


def test_chart_of_a_bill_becomes_an_image_chunk(corpus_parse):
    parsed = corpus_parse("01_electricity_suedvolt/04_Strom_Jahresabrechnung_2024_SuedVolt.pdf")

    images = [c for c in parsed.chunks if c.chunk_type is ChunkType.IMAGE]
    assert len(images) == 1
    assert images[0].page_number == 2


def test_contract_sections_become_headings(corpus_parse):
    parsed = corpus_parse("04_housing_utilities_contractors/16_Mietvertrag_Hauptstrasse42_2023.pdf")

    headings = _contents(parsed, ChunkType.HEADING)
    assert "§ 2 Mietzeit" in headings
    assert "WOHNRAUMMIETVERTRAG" in headings


@pytest.mark.slow
def test_whole_corpus_parses_with_sane_chunks(tmp_path):
    parser = DocumentParser(SETTINGS.parser, tmp_path / "images")
    for meta in CATALOG.documents:
        parsed = parser.parse(SETTINGS.dataset_dir / meta.file, meta)

        assert parsed.chunks, meta.file
        assert all(len(c.content) <= SETTINGS.parser.max_block_chars for c in parsed.chunks)
        assert not any("Amtsgericht" in c.content for c in parsed.chunks), meta.file
