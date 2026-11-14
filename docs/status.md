# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14 (M5)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M0 bis M5 abgeschlossen)
**Version:** v0.2.0 (nach M5)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | fertig, Antwortqualität offen bis M6 (Reverse-Engineering Runde 1 vorbereitet) | v0.2.0 |
| M6 | Testmodul & Evaluation (inkl. P1-Synthese und B0, ISS-037) | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M5)
- `audit_agent.agent`: ReAct-Schleife mit nativem Tool-Calling, 6 Tools (`list_documents`, `search_documents`, `search_tables`, `search_images`, `get_document_outline`, `calculate`), AST-Rechner mit `Decimal`, Belegnummern `[n]`, Limits (6 Aufrufe, Kontextwächter), JSON-Zeilen-Log je Schritt, Streamlit-Oberfläche mit Live-Belegen, CLI `ask` und `run-set`; 79 neue Tests (226 schnelle Tests), Quality Gates grün
- RUN-005 und RUN-006 (4 Fragen, `llama3.1:8b`): Technik stabil, 2 von 4 Antworten richtig (S2 nach Ausblenden der Summaries, N1); G1 und S4 scheitern an Tool-Wahl und selbst gesetzten Filtern (ISS-036). Präfix-Wiederverwendung teilweise belegt (ISS-005), Prompt rund 2.050 Token (ISS-030)
- ADR-0010 (Agentenschleife und Tools), ADR-0006 bestätigt (Format bleibt), ISS-030 bis ISS-037; Reverse-Engineering-Notiz `m5-agent.md` (Abschnitte 1–4, Runde 1)

## Nächstes Arbeitspaket
M6a – Testmodul-Grundlage (braucht danach Ollama): `testset` aus `ground_truth.yaml`, P1-Synthese (Top-5 aus dem Retriever, ein Modellaufruf, Belegnummern) und B0 (Volltext bis 8.192 Token) neben dem Agenten (ISS-037), eigene Metriken (Zahl, Quelle, Tool-Wahl, Filterwahl, Ablenker, Negativerkennung, Latenz) und ein Lauf, der Antworten und Bewertung getrennt speichert. Danach M6b: Läufe mit `llama3.1:8b` und `qwen2.5:7b` über 12 Fragen, RAGAS, Gegenmaßnahmen für ISS-006/007/036 messen. Zuerst Plan vorlegen.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Auswertung der Läufe später: Opus 5.5, Effort High)

## Nächste Schritte
1. Reverse-Engineering zu M2 bis M5 beantworten (`m2-parser.md`, `m3-enrichment.md`, `m4-retrieval.md`, `m5-agent.md`, Abschnitte 5–7), O-Ton für M0 bis M5 nachtragen; Runde 2 von M5 (Report, CLI, Oberfläche) auf Wunsch
2. M6a: Testmodul, P1-Synthese, B0
3. M6b: Evaluation beider Agent-Modelle, Gegenmaßnahmen messen, Hierarchie-Boost entscheiden

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): M6; bisher nur `llama3.1:8b` getestet (2 von 4)
- Gemeinsames Suchtool statt `search_documents`/`search_tables`/`search_images` (ISS-006), Filter durch Code statt durch das Modell (ISS-007): in M6 messen
- Hierarchie-Boost behalten oder streichen? Nutzen in RUN-004 nicht belegt (ISS-027); nach M6 entscheiden
- Summaries für den Agenten wieder einschalten? Aus seit RUN-006 (ISS-035); `include_table_summaries` erlaubt den Vergleich in M6
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-036/006/007: Tool-Wahl, selbst gesetzte Filter, erfundene Argumente (Agent bei 2 von 4)
- ISS-037: P1 ohne Synthese, B0 fehlt
- ISS-030/005: Prompt rund 2.050 Token, erster Aufruf ohne Cache ca. 100 s; `prompt_eval_count` nicht verlässlich
- ISS-031/032/033: Kürzung der Treffer auf 600 Zeichen, Filterregeln im Code sind Heuristiken, `list_documents` kennt keine Vertragslaufzeit
- ISS-025/027/028/029: Zeitraumfilter schließt Dokumente ohne Abrechnungszeitraum aus; Boost ohne Nutzen; Vergleich mit handgesetzten Filtern; S4 (Diagramm) nicht gefunden
- ISS-010: Zusatzdokumente 29/30 anders im Layout, nur 3 eingebaute Fehler (Evaluation grob)
- ISS-015/016/019: Parser-Grenzen (Layout-Tabellen im Briefkopf, Firmennamen als Überschrift, nur ein-seitige Tabellen)
- ISS-022/023: Summaries und Captions sind Suchhilfe, kein Beleg
- ISS-001/002/003: langsames Prefill, kein Ollama aus Claudes Shell, Nutzer pusht selbst

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Modellaufrufe nur über `Settings` (`AUDIT_*`-Variablen), nie hartkodiert
- `data/processed/` und `.cache/` sind nicht versioniert: Reihenfolge Ingestion (ca. 30 s) → Enrichment (aus dem Cache in Sekunden) → `uv run python -m audit_agent.retrieval index` (ca. 90 s mit Ollama); `data/vectors/` ist nicht versioniert
- Agent: `uv run python -m audit_agent.agent run-set --run-id <id> [--ids … | --all] [--model …]`; eine Frage dauert 0,5 bis 7 Minuten; Logs je Frage unter `data/eval/<id>/agent-<Frage>.jsonl`
- Summaries und Captions nie als Beleg zitieren; der Agent sieht Summaries nicht (ADR-0008, ISS-035)
