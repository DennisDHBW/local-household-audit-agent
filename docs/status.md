# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14 (M3)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M4 – Embedding & Retrieval (M0 bis M3 abgeschlossen)
**Version:** v0.1.0 (nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidence-UI | offen | – |
| M5 | Agent (P2) mit Tools | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M3)
- `audit_agent.enrichment`: `ImageCaptioner` (`gemma3:4b`), `TableSummarizer` (`llama3.2`), SHA-256-Cache (`diskcache`, `.cache/enrichment/`), Zahlenprüfung, Report, CLI (`--only`, `--limit`, `--dry-run`, `--run-id`); neuer Chunk-Typ `table_summary`; `numbers.py` aus dem Smoke-Test herausgelöst
- RUN-002/003: je 70 Jobs, ca. 26 Minuten; Captions 4 von 5 richtig (ein Diagramm ohne Zahlenbeschriftung bleibt unzuverlässig), Summaries nach Prompt-Fix nicht mehr abgeschnitten (21 → 0), 65 Summary-Chunks; bei Preistabellen mit mehreren Spalten und Briefkopf-Tabellen teils falsch
- ADR-0008, ISS-021 bis ISS-024, 24 neue Tests (107 schnelle Tests), Quality Gates grün; Reverse-Engineering-Notiz `m3-enrichment.md` (Abschnitte 1–4)

## Nächstes Arbeitspaket
M4 – Embedding & Retrieval (P1) + Evidence-UI (braucht Ollama für `nomic-embed-text`, du startest den Befehl): ChromaDB-Index aus `data/processed/` mit Hierarchie-Prefix und Aufgaben-Präfixen, Retrieval mit Metadatenfilter und Hierarchie-Boost (ADR-0002), Score von Hand nachrechenbar, Evidence-Ausgabe (Typ „KI-Zusammenfassung“ für `table_summary` kennzeichnen). Zuerst Plan vorlegen; `chromadb` ist noch nicht in `pyproject.toml`.

**Empfohlenes Modell:** Sonnet 5.5, Effort High

## Nächste Schritte
1. Reverse-Engineering zu M2 und M3 beantworten (`m2-parser.md`, `m3-enrichment.md`, Abschnitte 5–7), O-Ton für M0 bis M3 nachtragen; offen bleiben M0 und M1
2. M4: Embedding und Retrieval
3. M5: Agent mit Tools

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): Testmodul M6
- Referenzprototyp als Basis oder eigener Aufbau? UI: Streamlit + CLI (Empfehlung)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)
- Briefkopf-Chunks und KI-Summaries (ISS-015/016/022): stören oder helfen sie dem Retrieval? Bewertung in M4

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-005: Präfix-Wiederverwendung noch nicht belegt (Nachmessen in M5)
- ISS-006/007: Verwechslung `search_documents`/`search_tables`, ungefragte Metadatenfilter
- ISS-010: Zusatzdokumente 29/30 anders im Layout, nur 3 eingebaute Fehler (Evaluation grob)
- ISS-015/016/019: Parser-Grenzen (Layout-Tabellen im Briefkopf, Firmennamen als Überschrift, nur ein-seitige Tabellen)
- ISS-022/023: Summaries und Captions sind Suchhilfe, kein Beleg (Zahlenprüfung findet nur einen Teil der Fehler; Diagramm ohne Beschriftung unzuverlässig)
- ISS-001/002/003: langsames Prefill, kein Ollama aus Claudes Shell, Nutzer pusht selbst

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Modellaufrufe nur über `Settings` (`AUDIT_*`-Variablen), nie hartkodiert
- `data/processed/` und `.cache/` sind nicht versioniert: Reihenfolge Ingestion (ca. 30 s) → Enrichment (aus dem Cache in Sekunden, nur nach Cache-Verlust ca. 26 min mit Ollama); nach jeder neuen Ingestion das Enrichment erneut starten (ISS-021)
- Summaries (`table_summary`) und Captions nie als Beleg zitieren; Agent rechnet mit `table_row`-Chunks (ADR-0008)
