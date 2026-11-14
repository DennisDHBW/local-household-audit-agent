# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14 (M4)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M5 – Agent (P2) mit Tools (M0 bis M4 abgeschlossen)
**Version:** v0.1.0 (nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M4)
- `audit_agent.retrieval`: Index (547 Chunks ohne Überschriften, `search_document: [Ordner | Datei | Kapitel] …`, `nomic-embed-text`, ChromaDB in `data/vectors/`, Bauzeit 86 s), Suche (20 Kandidaten, Metadatenfilter, Hierarchie-Boost ×1.5, Top-5 mit `base_score`, `boost`, `final_score`), Evidenz (Dokument → Kapitel → Treffer, KI-Texte gekennzeichnet), Vergleichslauf, CLI `index | search | compare`
- RUN-004 (12 Fragen, 6 Konfigurationen): Filter senkt Ablenker-Treffer von 4/60 auf 0/55 und hebt die MRR von 0,683 auf 0,733; der Boost ändert keinen Rang (greift bei fast jedem Treffer); ohne Summaries 8/10 statt 9/10; Chunks ohne Kapitel ohne messbare Wirkung; S4 (Diagramm) wird nicht gefunden
- ADR-0009 (Index und Suche), ADR-0002 akzeptiert (Filter belegt, Boost ohne Nutzen), ISS-025 bis ISS-029, 39 neue Tests (146 schnelle Tests), Quality Gates grün; Reverse-Engineering-Notiz `m4-retrieval.md` (Abschnitte 1–4)

## Nächstes Arbeitspaket
M5 – Agent (P2) mit Tools (braucht Ollama, du startest die Befehle): ReAct-Schleife mit nativem Tool-Calling (ADR-0006) und den Tools aus `concept.md` 7.2 (`list_documents`, `search_documents`, `search_tables`, `search_images` nur über Bild-Chunks, `calculate`, …) auf dem `Retriever` aus M4; Tool-Beschreibungen sagen, wann Sparte, Dokumenttyp und Jahr gefiltert werden (ISS-025, ISS-007); Logging jedes Schritts; Streamlit-Evidenz. Zuerst Plan vorlegen; `streamlit` ist noch nicht in `pyproject.toml`.

**Empfohlenes Modell:** Sonnet 5.5, Effort High

## Nächste Schritte
1. Reverse-Engineering zu M2, M3 und M4 beantworten (`m2-parser.md`, `m3-enrichment.md`, `m4-retrieval.md`, Abschnitte 5–7), O-Ton für M0 bis M4 nachtragen; offen bleiben M0 und M1
2. M5: Agent mit Tools
3. M6: Testmodul und Evaluation (Filterwahl des Agenten messen, ISS-028)

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): Testmodul M6
- Referenzprototyp als Basis oder eigener Aufbau? UI: Streamlit (in M5) + CLI
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)
- Hierarchie-Boost behalten oder streichen? Nutzen in RUN-004 nicht belegt (ISS-027); nach M5/M6 entscheiden

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-005: Präfix-Wiederverwendung noch nicht belegt (Nachmessen in M5)
- ISS-006/007: Verwechslung `search_documents`/`search_tables`, ungefragte Metadatenfilter
- ISS-025/027/028/029: Zeitraumfilter schließt Dokumente ohne Abrechnungszeitraum aus; Boost ohne Nutzen; Vergleich mit handgesetzten Filtern; S4 (Diagramm) nicht gefunden
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
- Nach jeder neuen Ingestion und jedem Enrichment den Index neu bauen: `uv run python -m audit_agent.retrieval index` (ca. 90 s mit Ollama); `data/vectors/` ist nicht versioniert
