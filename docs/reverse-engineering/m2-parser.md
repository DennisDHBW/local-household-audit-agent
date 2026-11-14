# Reverse Engineering – M2: Parser & JSON-Zwischenformat

> Abschnitte 1–4 von Claude vorbereitet, Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m2-parser`, Tag `v0.1.0` nach dem Merge · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `src/audit_agent/ingestion/models.py` | Typisierte Modelle des JSON-Zwischenformats | `ChunkType`, `ChunkMetadata`, `DocumentChunk`, `ParsedDocument` | `pydantic`, `corpus` |
| `src/audit_agent/ingestion/parser.py` | Wandelt ein PDF in typisierte Chunks (Tabellen, Überschriften, Text, Bilder) | `DocumentParser.parse`, `_read_page`, `_detect_tables`, `_split_at_section_rows`, `_reading_order`, `_emit_table`, `_row_cells`, `_serialise_row`, `_add_text`, `_flush_text` | `pymupdf`, `config.ParserSettings`, `models.py` |
| `src/audit_agent/ingestion/pipeline.py` | Verarbeitet alle PDFs aus `documents.yaml` und schreibt je PDF eine JSON-Datei | `run_ingestion`, `chunks_path`, `load_parsed_document`, `IngestionReport` | `parser.py`, `corpus` |
| `src/audit_agent/ingestion/__main__.py` | Kommandozeile `python -m audit_agent.ingestion` | `main` | `pipeline.py` |
| `src/audit_agent/ingestion/__init__.py` | Öffentliche Schnittstelle des Pakets | Re-Exports | – |
| `src/audit_agent/config.py` | Neu: Parser-Schwellwerte und `images_dir` | `ParserSettings`, `Settings.parser`, `Settings.images_dir` | `pydantic` |
| `tests/test_ingestion_parser.py` | Tests mit synthetischen PDFs und Golden-Checks auf dem echten Korpus | 19 Testfälle (1 `slow`) | `pytest`, `pymupdf` |
| `tests/test_ingestion_models_pipeline.py` | Tests für Modelle und Pipeline (idempotent, veraltete Dateien, Fail Fast) | 8 Testfälle | `pytest`, `yaml` |

## 2. Datenfluss
Beispiel: die Zeile „Arbeitspreis ÖkoStrom“ in der Stromabrechnung 2024 (`04_Strom_Jahresabrechnung_2024_SuedVolt.pdf`, Seite 1).

```
documents.yaml-Eintrag (Sparte electricity, Typ bill, Vertrag SV-2024-99104, …)
  → run_ingestion: Katalog laden, missing_files prüfen, DocumentParser(settings.parser, images_dir)
  → DocumentParser.parse(pdf, meta)
      → _read_page(Seite 1)
          → _read_spans: page.get_text("dict") → Spans mit bbox, Text, Größe, fett?
              z. B. Span "Arbeitspreis ÖkoStrom" (x 67–157, y 602–612, 8,0 pt, nicht fett)
          → _detect_tables: find_tables("lines") + find_tables("lines_strict")
              "lines": Tabelle ab y=622 (4 Zeilen, Kopf fehlt), "lines_strict": y=569–737 (6 Zeilen)
              → Sortierung nach (Zeilenzahl, Fläche): die 6-Zeilen-Tabelle gewinnt, die andere überlappt
          → _split_at_section_rows: keine Abschnittszeile in dieser Tabelle → bleibt unverändert
          → Textblöcke ohne Spans innerhalb der Tabellenfläche, Kopf-/Fußzone raus
          → _reading_order: Elemente nach y sortieren, bei Überlappung links vor rechts
      → _body_size: häufigste Schriftgröße im Fließtext (je Dokument verschieden); _heading_levels: Größe → Ebene
      → _emit_page: Elemente der Reihe nach
          → Überschrift „2. Detailberechnung der Energiekosten (Tarif: …)“ (9,2 pt, fett) → heading_stack
          → _emit_table:
              _row_cells(Zeile 2): Spans nach x sortieren, Lücke < 5 pt oder Überlappung = eine Zelle
                 → [(67,157,"Arbeitspreis ÖkoStrom"), (187,230,"3.250 kWh"), (315,350,"29,24 ct/ kWh"),
                    (362,415,"34,80 ct/kWh"), (433,480,"950,42 EUR"), (494,548,"1.131,00 EUR")]
              _header_columns: Zeile 1 komplett fett, ≥ 2 Zellen → Kopf: Abrechnungsposition, Zeitraum / Menge,
                 Preis Netto, Preis Brutto, Betrag Netto, Betrag Brutto
              _serialise_row: jede Zelle zur am weitesten links überlappenden Kopfspalte
      → DocumentChunk(chunk_id "04_Strom_…_p1_tab03_r01", chunk_type table_row,
            content "Abrechnungsposition: Arbeitspreis ÖkoStrom | Zeitraum / Menge: 3.250 kWh | Preis Netto: 29,24 ct/ kWh | … | Betrag Brutto: 1.131,00 EUR",
            heading_stack ("Ihre Jahresrechnung Strom für den Zeitraum …", "2. Detailberechnung …"),
            page_number 1, metadata (… table_id "p1_tab03", columns (6 Namen)))
  → ParsedDocument(...).model_dump_json → data/processed/04_Strom_Jahresabrechnung_2024_SuedVolt_chunks.json
```

## 3. Datenstrukturen

| Modell | Felder (Auswahl) | Bedeutung |
|---|---|---|
| `ChunkType` | `text`, `heading`, `table_row`, `image` | Element-Typ; `table_summary` kommt mit M3 |
| `ChunkMetadata` | `filename`, `utility_type`, `doc_type`, `provider`, `contract_id`, Zeiträume, `table_id`, `columns`, `image_path` | Dokument-Metadaten aus `documents.yaml` plus Tabellen- und Bilddetails; `is_noise_document` fehlt absichtlich |
| `DocumentChunk` | `chunk_id`, `chunk_type`, `content`, `heading_stack`, `page_number`, `metadata` | kleinste suchbare Einheit; Validator: `table_row` braucht `table_id`, `image` braucht `image_path` |
| `ParsedDocument` | `file`, `page_count`, `chunks` | Inhalt einer JSON-Datei; Validator: Chunk-IDs eindeutig |
| `ParserSettings` | `min_chars`, `max_block_chars`, `header_zone_ratio`, `footer_zone_ratio`, `heading_size_factor`, `cell_gap_pt`, `min_image_width_pt` | alle Parser-Schwellwerte an einer Stelle |
| `_Span`, `_TextBlock`, `_TableRegion`, `_ImageRegion`, `_Element`, `_PageContent`, `_Cursor` | intern | Zwischenstrukturen des Parsers; `_Cursor` hält Überschriften-Stapel, Zähler für IDs und den Text-Puffer |

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| PyMuPDF 2.1 (`pymupdf`) | PDF öffnen, Text mit Schrift lesen, Tabellen und Bilder finden | `pymupdf.open`, `page.get_text("dict")`, `page.find_tables(strategy=…)`, `Table.rows`, `page.get_image_info(xrefs=True)`, `Document.extract_image` | `pdfplumber` (Tabellen), `pdfminer.six`, `docling` (Layoutmodell, schwer) |
| Pydantic 2.14 | Typisierte, unveränderliche Modelle, Validierung, JSON-Export | `BaseModel`, `ConfigDict(frozen=True, extra="forbid")`, `model_validator`, `model_dump_json`, `model_validate_json`, `model_copy(update=…)` | `dataclasses` + eigene Validierung |
| PyYAML 6.0 | `documents.yaml` lesen (über `corpus`) | `yaml.safe_load` | `ruamel.yaml` |
| pytest 9.2 | Tests mit `tmp_path`, Fixtures und Marker `slow` | `pytest.fixture`, `pytest.raises`, `pytest.mark.slow` | `unittest` |
