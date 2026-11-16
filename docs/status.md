# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-16 (M6f)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6f fertig; Prüfablauf für P2 weiter ungelöst)
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
| M6 | Testmodul & Evaluation | M6a–M6f fertig (RUN-012: P2 9 von 14 richtig; RUN-013/015: 6; RUN-014 `qwen2.5:7b`: 6); Prüfablauf (ISS-058) offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6f)
- Aufruf als Text wird erkannt und ausgeführt (`agent/text_calls.py`), `calculate` nimmt Operanden und deutsche Zahlen; `scripts/eval_run.sh` fährt Läufe samt Auswertung (ISS-061 gelöst, ISS-063 teilweise)
- RUN-014 (`qwen2.5:7b`), RUN-015 und RUN-016 (`llama3.1:8b`, gleicher Code): je 6 von 14 richtig nach Handprüfung; 015 und 016 sind bis auf die Zeit identisch, Streuung also 0 (ISS-062 gelöst)
- Rechennachfrage wirkt bei `qwen2.5:7b` (3 von 4 gültige `calculate`-Aufrufe, G4 erkannt), bei `llama3.1:8b` nicht (1 von 4); falsche Operanden erzeugen Fehlalarme (ISS-066, ISS-067)
- Zeit je Frage nun gleich (301 gegen 320 bis 325 s); der Zeitgrund aus ADR-0013 entfällt

## Nächstes Arbeitspaket
M6g – Entscheidung zu Prüfablauf und Modell, danach Umsetzung und ein Messlauf. Plan zuerst vorlegen, vorher mit dir klären: (1) fester Prüfablauf im Code (Soll suchen, Ist suchen, Code rechnet) ja oder nein (ISS-067); (2) Modell für P2: `llama3.1:8b` oder `qwen2.5:7b` (ISS-066, ADR-0013). Danach: G1 und G3 scheitern am Retrieval der Sollzahl (Suchanfrage, mehr Treffer); Reverse-Engineering M6 erst danach, Tag v1.0.0 erst bei entschiedenem Prüfablauf.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Änderung an Agent-Loop und Prompt; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. M6g (siehe oben), danach P1: mehr Treffer oder gezieltere Suchanfrage (12 Retrieval-Fehlschläge), Zitierpflicht P2, Hierarchie-Boost entscheiden
2. Reverse-Engineering M6, Tag v1.0.0 erst, wenn der P2-Prüfablauf entschieden ist
3. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6f nachtragen

## Offene Entscheidungen / Fragen
- Fester Prüfablauf im Code oder nur als Ausblick? RUN-014 bis RUN-016 sprechen dafür (richtige Operanden nur so sicher), ADR-0015 hat ihn bisher verworfen, damit der Agent die Werkzeugwahl behält
- Modell für P2: `llama3.1:8b` (ADR-0013) oder `qwen2.5:7b` (zitiert besser, befolgt die Nachfrage, mehr Fehlalarme)? Rechennachfrage bleibt vorerst im Code
- Hierarchie-Boost behalten? (ISS-027); Summaries für den Agenten wieder an? (ISS-035); Einheitenfaktor der Zahlensuche einschränken? (ISS-050)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-058/060/063/066/067: P2 rechnet nur mit `qwen2.5:7b`, dort teils mit falschen Operanden; Fehler bleiben meist unerkannt; ISS-062: Rückschritte S2/S4/N2 aus dem Code von M6e, Ursache nicht getrennt
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
