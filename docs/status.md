# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-15 (M6a)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a fertig, M6b offen)
**Version:** v0.2.0 (nach M5)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | fertig (Reverse-Engineering Runde 1 vorbereitet) | v0.2.0 |
| M6 | Testmodul & Evaluation | M6a fertig (Testmodul, B0, P1-Synthese); M6b offen (12 Fragen, 2 Modelle, RAGAS) | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6a)
- `audit_agent.evaluation`: Varianten B0 (Seitentext in Katalogreihenfolge bis zum Token-Budget, Dateien 01–06), P1 (Top-5 ohne Filter + ein Modellaufruf), P2 (Agent); gemeinsames Antwortformat, JSON-Zeilen je Antwort (fortsetzbar), eigene Metriken ohne LLM, `report.md`; CLI `generate` / `score`; ADR-0011; 254 schnelle Tests
- RUN-007 abgebrochen: B0-Prompt real 8.424 Token, Ollama kürzte still auf 4.096 (Schätzung Zeichen/3 zu niedrig, jetzt 2,4; ISS-041), danach OOM-Kill (Modelle jetzt vor jeder Variante entladen; ISS-043). `scripts/probe_context.py` misst die echte Prompt-Länge
- RUN-008 (S2, G1, N1, `llama3.1:8b`): stabil, keine Kürzung; richtig B0 2/3, P1 1/3, P2 2/3; G1 von keiner Variante vollständig gelöst; P1 antwortet bei vorhandenen Belegen „keine Angaben“; P2 zitiert keine Belegnummern; B0-Präfix-Cache belegt (430 s → 12 s)

## Nächstes Arbeitspaket
M6b – Evaluation vervollständigen: Prüffragen zu E2/E3 ergänzen (ISS-040), RAGAS mit lokalem Bewerter auf den gespeicherten Antworten anbinden, dann Nachtläufe 12 Fragen × B0/P1/P2 mit `llama3.1:8b` und `qwen2.5:7b` (je ca. 60–90 min) und Auswertung. Zuerst Plan vorlegen.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Auswertung der Läufe danach: Opus 5.5, Effort High)

## Nächste Schritte
1. Reverse-Engineering zu M2 bis M5 beantworten (`m2-parser.md` … `m5-agent.md`), O-Ton für M0 bis M5 nachtragen
2. M6b: Katalog erweitern, RAGAS, Läufe mit beiden Modellen
3. Danach Gegenmaßnahmen messen (Filter durch Code ISS-007, gemeinsames Suchtool ISS-006, Zitierpflicht P2, P1-Suchanfrage) und Hierarchie-Boost entscheiden; Reverse-Engineering M6, Tag v1.0.0

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): nach M6b
- Gegenmaßnahmen für ISS-006/007/036 erst nach dem 12-Fragen-Lauf wählen (nicht an 3 Fragen anpassen)
- Hierarchie-Boost behalten? (ISS-027); Summaries für den Agenten wieder an? (ISS-035)
- RAGAS-Bewerter: welches lokale Modell, und passt RAGAS zu Ollama ohne Cloud-Zugriff? In M6b prüfen, nicht raten
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-036/006/007: Agent wählt Tools und Filter unzuverlässig (G1 in RUN-006 und RUN-008 gleich falsch)
- ISS-038/040: eigene Metriken sind Heuristiken; Fehlererkennung misst nur E1
- ISS-039: B0 sieht nur Stromdokumente (01–06)
- ISS-041: früher gekürzte Agentenläufe (M5) nicht ausgeschlossen, aber unwahrscheinlich
- ISS-030/031/032/033, ISS-025/027/028/029, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Evaluation: `uv run python -m audit_agent.evaluation generate --run-id <id> [--ids … | --all] [--variants b0 p1 p2] [--model …]`, danach `score --run-id <id>` ohne Ollama; ein Lauf = ein Modell; Abbruch → derselbe Befehl setzt fort
- Nach jedem Lauf Journal sichern: `journalctl -u ollama --since "-3h" --no-pager | grep -iE "truncat|oom"` (Kürzung und OOM sieht man nur dort)
- Token-Schätzung 2,4 Zeichen/Token (`CHARS_PER_TOKEN`); Ollama kürzt zu lange Prompts ohne Fehler auf die Hälfte
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
