# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14 (M1)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M2 – Parser & JSON-Zwischenformat (M0, M1 abgeschlossen)
**Version:** – (erstes Tag: `v0.1.0` nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | offen | v0.1.0 |
| M3 | Enrichment & Cache | offen | – |
| M4 | Embedding & Retrieval (P1) + Evidence-UI | offen | – |
| M5 | Agent (P2) mit Tools | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M1)
- `audit_agent.corpus`: Pydantic-Modelle und Loader für `documents.yaml` und `ground_truth.yaml` (Fail Fast, Konsistenzprüfungen)
- `dataset/documents.yaml` (30 PDFs), `dataset/ground_truth.yaml` (12 Fragen, 3 eingebaute Fehler E1–E3, 10 Prüfurteile)
- Fehlerdokumente 29 (Gas 2026, falsche z-Zahl) und 30 (Betriebskosten 2026, falsche Wohnfläche), Generator `scripts/generate_error_documents.py`
- 57 Tests ohne LLM, Quality Gates grün

## Nächstes Arbeitspaket
M2 – Parser & JSON-Zwischenformat: PyMuPDF-Parser (Tabellen zuerst per `find_tables()`, Überschriften per Font-Heuristik in den `heading_stack`, Absätze aggregieren, Bilder extrahieren), typisierte Chunks mit Metadaten aus `documents.yaml`, JSON-Ausgabe unter `data/processed/`, Tag `v0.1.0`.

**Empfohlenes Modell:** Sonnet 5.5, Effort High

## Nächste Schritte
1. Reverse-Engineering-Fragen zu M0 und M1 beantworten (`docs/reverse-engineering/`, Abschnitte 5–7) und O-Ton nachtragen
2. M2: Parser und JSON-Zwischenformat
3. M3: Enrichment (Ollama nötig) und Cache

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): Testmodul M6
- Referenzprototyp als Basis oder eigener Aufbau? UI: Streamlit + CLI (Empfehlung)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-005: Präfix-Wiederverwendung noch nicht belegt (Nachmessen in M5)
- ISS-006: Verwechslung `search_documents` / `search_tables`
- ISS-007: Modelle setzen ungefragt Metadatenfilter
- ISS-010: Zusatzdokumente 29/30 anders im Layout, nur 3 eingebaute Fehler (Evaluation grob)
- ISS-001/002/003: langsames Prefill, kein Ollama aus Claudes Shell, Nutzer pusht selbst

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Modellaufrufe nur über `Settings` (`AUDIT_*`-Variablen), nie hartkodiert
