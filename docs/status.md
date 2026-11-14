# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14 (M2)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M3 – Enrichment & Cache (M0, M1, M2 abgeschlossen)
**Version:** v0.1.0 (nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | offen | – |
| M4 | Embedding & Retrieval (P1) + Evidence-UI | offen | – |
| M5 | Agent (P2) mit Tools | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M2)
- `audit_agent.ingestion`: `DocumentParser` (Tabellen zuerst, Überschriften per Font-Heuristik, Lesereihenfolge, Absatz-Aggregation, Bild-Extraktion), Modelle `DocumentChunk`/`ParsedDocument`, Pipeline und CLI `python -m audit_agent.ingestion`
- Ergebnis RUN-001: 30 PDFs → 564 Chunks (178 Text, 82 Überschriften, 299 Tabellenzeilen, 5 Bilder), ca. 31 s; die Fehlerdokumente 29 und 30 sind in den Zeilen korrekt lesbar
- ADR-0007 (Parser-Heuristiken), ISS-012 bis ISS-020, 83 schnelle Tests + 1 `slow`-Test über den ganzen Korpus, Quality Gates grün

## Nächstes Arbeitspaket
M3 – Enrichment & Cache (braucht Ollama, du startest den Befehl): Bild-Captions mit `gemma3:4b` für die 5 Diagramme, Tabellen-Summaries (`table_summary`) mit `llama3.2`, SHA-256-Schlüssel und `diskcache` unter `.cache/`, Ergebnis zurück in die JSON-Dateien. Zuerst Plan vorlegen (Prompts, Cache-Schlüssel, Umgang mit dem langsamen Prefill).

**Empfohlenes Modell:** Sonnet 5.5, Effort High

## Nächste Schritte
1. Reverse-Engineering zu M2 beantworten (`docs/reverse-engineering/m2-parser.md`, Abschnitte 5–7), O-Ton für M0, M1 und M2 nachtragen; offen bleiben M0 und M1
2. M3: Enrichment und Cache (Ollama nötig)
3. M4: Embedding und Retrieval

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): Testmodul M6
- Referenzprototyp als Basis oder eigener Aufbau? UI: Streamlit + CLI (Empfehlung)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)
- Briefkopf-Chunks (ISS-015/016): stören sie das Retrieval? Bewertung in M4

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-005: Präfix-Wiederverwendung noch nicht belegt (Nachmessen in M5)
- ISS-006/007: Verwechslung `search_documents`/`search_tables`, ungefragte Metadatenfilter
- ISS-010: Zusatzdokumente 29/30 anders im Layout, nur 3 eingebaute Fehler (Evaluation grob)
- ISS-015/016/019: Parser-Grenzen (Layout-Tabellen im Briefkopf, Firmennamen als Überschrift, nur ein-seitige Tabellen)
- ISS-001/002/003: langsames Prefill, kein Ollama aus Claudes Shell, Nutzer pusht selbst

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Modellaufrufe nur über `Settings` (`AUDIT_*`-Variablen), nie hartkodiert
- `data/processed/` ist nicht versioniert: bei Bedarf mit `uv run python -m audit_agent.ingestion` neu erzeugen (ca. 30 s)
