# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-16 (M6g)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6g fertig; Prüfablauf entschieden: abgeschaltet)
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
| M6 | Testmodul & Evaluation | M6a–M6g fertig (RUN-017: P2 mit Prüfablauf 6 von 14, kein Gewinn, Ablauf aus); Retrieval-Verbesserungen (M6h) offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6g)
- Fester Prüfablauf umgesetzt (`agent/audit_flow.py`: Plan, Suche, Lesen mit JSON-Schema, Herkunftsprüfung, Differenz mit `calculate`; ADR-0016), Standardmodell P2 jetzt `qwen2.5:7b`
- RUN-017 (89 min): nach Handprüfung 6 von 14 wie RUN-014, G4 verloren, 27 % mehr Zeit, neue Fehlerarten (falsche Zuordnung von Soll und Ist, Lückenantworten, chinesische Antwort in S5; ISS-070, ISS-071)
- Entscheidung des Nutzers: Ablauf bleibt als Negativergebnis im Code, Standard `audit_flow_enabled=False`; P2 läuft wie RUN-014 (`qwen2.5:7b`, Sperre, Rechennachfrage)

## Nächstes Arbeitspaket
M6h – Retrieval verbessern: G1 und G3 scheitern daran, dass die Sollzahl nie im Kontext steht (ISS-051/052), P1 hat 12 Retrieval-Fehlschläge. Plan zuerst vorlegen, vorher mit dir klären: mehr Treffer oder gezieltere Suchanfrage (Größe statt Frage), Hierarchie-Boost behalten (ISS-027), Summaries wieder an (ISS-035), Einheitenfaktor der Zahlensuche (ISS-050), Zitierpflicht P2. Danach ein Messlauf P1 und P2; Reverse-Engineering M6 und Tag v1.0.0 erst danach.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Retrieval-Scoring und Testmodul; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. M6h (siehe oben), danach Reverse-Engineering M6 und Tag v1.0.0
2. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6g nachtragen
3. Phase 2 (Ausarbeitung) erst auf dein Wort; Negativergebnis Prüfablauf (ADR-0016, ISS-070) und Autonomie gegen Zuverlässigkeit gehören ins Kapitel Reflexion

## Offene Entscheidungen / Fragen
- Hierarchie-Boost behalten? (ISS-027); Summaries für den Agenten wieder an? (ISS-035); Einheitenfaktor der Zahlensuche einschränken? (ISS-050)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-070/071/068: Prüfablauf (abgeschaltet) ordnet Soll und Ist falsch zu, Nachricht löst Lückenantworten und Sprachwechsel aus; ISS-066/067: Fehlalarme durch falsche Operanden bleiben Grenze, P2 findet die eingebauten Fehler kaum
- ISS-062: Rückschritte S2/S4/N2 aus dem Code von M6e, Ursache nicht getrennt; ISS-057: Laufzeit nur zwischen Läufen mit gleicher Ladepolitik vergleichbar; ISS-054: `qwen2.5:7b` sagt oft „ja“
- ISS-050/038: „richtig laut Metrik“ nur mit Handprüfung verwenden; ISS-053/047/046/045: RAGAS nur als zweite Sicht (Antwortmodell und Bewerter sind jetzt beide `qwen2.5:7b`); ISS-039: B0 sieht nur Stromdokumente; ISS-029: S4 (Diagramm)
- ISS-036, ISS-030/031/032/033, ISS-025/027/028, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: jeder `uv`-Befehl beginnt mit `export UV_CACHE_DIR=/tmp/uvc-<sitzung> UV_PROJECT_ENVIRONMENT=/tmp/venv-<sitzung> UV_LINK_MODE=copy` (neuer Ordnername je Sitzung, `/tmp/uv-cache` gehört einer alten Sitzung, ISS-065/069), in neuer Sitzung zuerst `uv sync`; Quality Gate `./scripts/check.sh` vor jedem Commit, auch bei Daten und Skripten (ISS-056), nie hinter eine Pipe vor `&&` (ISS-048)
- Dateien im Projektordner: `Write`/`Edit` wirken nur im Container. Bearbeiten über `device_bash` (kleine Python-Ersetzung mit `assert`) oder Stage-Kopie bearbeiten und mit `device_commit_files` zurückschreiben
- Evaluation: `generate` → `score` (ohne Ollama) → `check_evidence.py`, `analyze_timing.py` → `ragas` (`uv run --group ragas …`); ein Lauf = ein Antwortmodell; für Vergleichsläufe nur P2: `generate --variants p2 --all`
- Nach jedem Lauf `uv run python scripts/check_evidence.py --run-id <id>` und die Antworten von Hand lesen; Journal sichern (`truncat|oom`)
- Die Zeichenkette `toolbench_rapidapi_key` in `run-011` ist vom Modell erfunden und bleibt in den Rohdaten (ISS-054); meldet GitHub sie beim Push, ist das ein Fehlalarm
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
- Nach jedem Lauf das Ollama-Journal ohne Filter sichern (`journalctl -u ollama --since "-130min"`): nur dort stehen Modellladungen und Cache-Treffer
