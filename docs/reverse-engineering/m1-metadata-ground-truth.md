# Reverse Engineering – M1: Metadaten & Ground Truth

> Abschnitte 1–4 von Claude vorbereitet, Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m1-metadata-ground-truth` (noch kein Tag) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `src/audit_agent/corpus/models.py` | Typisierte Modelle für Dokument-Metadaten und Ground Truth samt Konsistenzprüfungen | `DocumentMeta`, `DocumentCatalog`, `Question`, `PlantedError`, `AuditCheck`, `GroundTruth` | `pydantic` |
| `src/audit_agent/corpus/loader.py` | Liest die YAML-Dateien und validiert sie (Fail Fast) | `load_document_catalog`, `load_ground_truth`, `missing_files`, `CorpusError` | `yaml`, `models.py` |
| `src/audit_agent/corpus/__init__.py` | Öffentliche Schnittstelle des Pakets | Re-Exports | `models.py`, `loader.py` |
| `src/audit_agent/config.py` | Neu: Pfade `documents_file`, `ground_truth_file` | `Settings.documents_file` | – |
| `dataset/documents.yaml` | Metadaten je PDF (Sparte, Dokumentart, Anbieter, Zeitraum, Rauschen) | – | `DocumentMeta` |
| `dataset/ground_truth.yaml` | 12 Testfragen, 3 eingebaute Fehler, 10 erwartete Prüfurteile | – | `GroundTruth` |
| `scripts/generate_error_documents.py` | Erzeugt die PDFs 29 und 30 mit eingebautem Fehler | `gas_bill`, `service_charges`, `money` | `weasyprint` |
| `tests/test_corpus.py` | Whitebox-Tests ohne LLM für Loader, Modelle und Korpus-Konsistenz | 17 Testfälle | `pytest`, `pymupdf` |

## 2. Datenfluss
Beispiel: Frage G1 („Wurde der neue Arbeitspreis angewendet?“) und der eingebaute Fehler E1.

```
dataset/ground_truth.yaml  (Eintrag id: G1, sources: 03_… und 06_…)
  → load_ground_truth(Settings().ground_truth_file)
      → _read_yaml: Pfad prüfen, yaml.safe_load → dict (sonst CorpusError)
      → GroundTruth.model_validate(dict): Pydantic baut Question, ExpectedFact, SourceRef
          (extra="forbid" lehnt unbekannte Felder ab, Decimal-Werte wie 38.20 bleiben exakt)
      → @model_validator _check_catalog: 5/2/2/3 Fragen, eindeutige IDs,
          audit_checks und planted_errors verweisen auf dieselben Fehler-IDs
  → GroundTruth (unveränderlich) → später: Evaluation vergleicht Agentenantwort mit facts
  → tests/test_corpus.py: referenced_files() ⊆ Dateien aus documents.yaml
```

Zweiter Pfad: `load_document_catalog` → `DocumentCatalog` → `missing_files(catalog, dataset_dir)` vergleicht Katalog und `rglob("*.pdf")` in beide Richtungen.

## 3. Datenstrukturen
- **`DocumentMeta`:** `file` (relativ zu `dataset/`), `utility_type`, `doc_type` (Enums), `provider`, `contract_id`, `document_date`, optional `billing_period_start/end` (nur zusammen), `valid_from`, `is_noise_document`.
- **`ExpectedFact`:** `label`, `value` (Zahl oder Text), `unit`, `tolerance` (Standard 0,01) für die numerische Korrektheit.
- **`Question`:** `id` (S1…Z3), `category`, `question`, `expected_answer`, `facts`, `sources` (Datei + Seite), `expected_tools`, `is_answerable` (nur bei Negativfragen `false`), `tests`.
- **`PlantedError`:** `id` (E1…E3), fehlerhafte Datei, `related_files`, Beschreibung, `facts` (richtig vs. abgerechnet).
- **`AuditCheck`:** erwartetes Urteil je Rechnung (`is_correct`, `planted_error_id`).
- **`GroundTruth`:** bündelt die drei Listen und prüft sie gegeneinander.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| `pydantic` 2.14.3 | Modelle, Typ- und Konsistenzprüfung | `BaseModel`, `ConfigDict(frozen, extra="forbid")`, `model_validator`, `model_validate` | `dataclasses` mit Handarbeit, `attrs` |
| `pyyaml` 6.0.3 | YAML einlesen | `yaml.safe_load` | `ruamel.yaml`, JSON/TOML |
| `weasyprint` 70.0 (nur Generator, keine Projektabhängigkeit) | HTML/CSS zu PDF | `HTML(string=…).write_pdf` | `reportlab`, Headless-Browser |
| `pymupdf` 2.1 | Test: Text aus PDFs lesen | `pymupdf.open`, `page.get_text` | `pypdf`, `pdftotext` |
| `pytest` | Tests, Parametrisierung | `fixture`, `parametrize`, `raises(match=…)` | `unittest` |

## 5. Whitebox-Tests (selbst nachvollzogen)
-

## 6. Erklär-Test (ohne in den Code zu schauen)

| Frage | Meine Antwort | Stimmt? |
|---|---|---|
| | | |

## 7. Was ich geändert hätte / Schwächen / offene Fragen
-
