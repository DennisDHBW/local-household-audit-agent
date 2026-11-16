# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-16 (M6e)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6e fertig; Prüfablauf für P2 weiter ungelöst)
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
| M6 | Testmodul & Evaluation | M6a–M6e fertig (RUN-012: P2 9 von 14 richtig, RUN-013: 6 von 14); Prüfablauf (ISS-058) offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6e)
- Wiederholungssperre (identischer Aufruf wird nicht ausgeführt) und einmalige Rechennachfrage bei Prüffragen im Agent-Loop (ADR-0015, vorgeschlagen); Prompt um Hinweis zu getrennten Soll-/Ist-Suchen ergänzt; `scripts/analyze_timing.py`; 288 Tests grün
- RUN-013 (P2, `llama3.1:8b`, 14 Fragen, 73 min): nach Handprüfung 6 von 14 richtig (RUN-012: 9); Sperre griff 4-mal, Nachfrage 4-mal, aber 0 gültige `calculate`-Aufrufe, Fehler erkannt 0 von 3 mit tragfähiger Begründung
- Laufzeit: erste Anfrage je Frage in RUN-012 und RUN-013 ohne Cache (28 Modellladungen im Journal); Zeitvergleich mit RUN-010 nicht belastbar (ISS-057)

## Nächstes Arbeitspaket
M6f – Prüfablauf stabilisieren und Gegenprobe. Plan zuerst vorlegen. Ansatzpunkte: (1) Werkzeugaufruf als Text in der Antwort erkennen (ISS-061, S5); (2) `calculate` verzeihender machen und identische ungültige Aufrufe sperren (ISS-063); (3) Gegenprobe P2 mit `qwen2.5:7b` und demselben Loop (ca. 75 min, vom Nutzer), danach Entscheidung zu ADR-0015 Teil 2 und ADR-0013; (4) Streuung: gleicher Code zweimal mit `llama3.1:8b` (ISS-062). Die Entscheidung „fester Prüfablauf im Code“ (siehe unten) vor dem Plan klären.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (anspruchsvoller Code: ReAct-Schleife, Werkzeuge; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. M6f (siehe oben), danach P1: mehr Treffer oder gezieltere Suchanfrage (12 Retrieval-Fehlschläge), Zitierpflicht P2, Hierarchie-Boost entscheiden
2. Reverse-Engineering M6, Tag v1.0.0 erst, wenn der P2-Prüfablauf entschieden ist
3. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6e nachtragen

## Offene Entscheidungen / Fragen
- Fester Prüfablauf im Code (Sollwerte suchen, Istwerte suchen, rechnen) in den Prototyp oder nur als Ausblick? RUN-013 spricht dafür, ADR-0015 hat ihn bisher verworfen, damit der Agent die Werkzeugwahl behält
- Rechennachfrage behalten oder entfernen (nach `qwen2.5:7b`-Gegenprobe)? Welche Gegenmaßnahmen kommen in den Prototyp, welche nur als Ausblick (Zeit)?
- Hierarchie-Boost behalten? (ISS-027); Summaries für den Agenten wieder an? (ISS-035); Einheitenfaktor der Zahlensuche einschränken? (ISS-050)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-058/060/063: P2 rechnet nicht (`calculate` 0 von 14 gültig), Fehler bleiben unerkannt; ISS-061: Werkzeugaufruf als Antworttext (S5); ISS-062: Rückschritte S2/S4/N2, Streuung nicht gemessen
- ISS-057: Laufzeit nur zwischen Läufen mit gleicher Ladepolitik vergleichbar; ISS-054: `qwen2.5:7b` sagt immer „ja“, `llama3.1:8b` scheitert an `calculate` und zitiert kaum
- ISS-050/038: „richtig laut Metrik“ nur mit Handprüfung verwenden; ISS-053/047/046/045: RAGAS nur als zweite Sicht; ISS-039: B0 sieht nur Stromdokumente; ISS-029: S4 (Diagramm)
- ISS-036, ISS-030/031/032/033, ISS-025/027/028, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen, in neuer Sitzung zuerst `uv sync` (ISS-009); Quality Gate `./scripts/check.sh` vor jedem Commit, auch bei Daten und Skripten (ISS-056), nie hinter eine Pipe vor `&&` (ISS-048)
- Dateien im Projektordner: `Write`/`Edit` wirken nur im Container. Bearbeiten über `device_bash` (kleine Python-Ersetzung mit `assert`) oder Stage-Kopie bearbeiten und mit `device_commit_files` zurückschreiben
- Evaluation: `generate` → `score` (ohne Ollama) → `check_evidence.py`, `analyze_timing.py` → `ragas` (`uv run --group ragas …`); ein Lauf = ein Antwortmodell; für Vergleichsläufe nur P2: `generate --variants p2 --all`
- Nach jedem Lauf `uv run python scripts/check_evidence.py --run-id <id>` und die Antworten von Hand lesen; Journal sichern (`truncat|oom`)
- Die Zeichenkette `toolbench_rapidapi_key` in `run-011` ist vom Modell erfunden und bleibt in den Rohdaten (ISS-054); meldet GitHub sie beim Push, ist das ein Fehlalarm
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
- Nach jedem Lauf das Ollama-Journal ohne Filter sichern (`journalctl -u ollama --since "-130min"`): nur dort stehen Modellladungen und Cache-Treffer
