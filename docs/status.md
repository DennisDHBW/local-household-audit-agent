# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-17 (M6h)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6h fertig; Größen-Anfrage ohne messbaren Gewinn, Nachbesserung ISS-077 offen)
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
| M6 | Testmodul & Evaluation | M6a–M6h fertig (RUN-018: P2 6 von 14 wie RUN-014, Zitier-Rückfrage wirkt, Größen-Anfrage ohne Gewinn); Sparte in der Größen-Anfrage (M6i) offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6h)
- Größen-Anfrage (`retrieval/quantity.py`, ADR-0017): zweite Suche mit der Größe allein (ohne Jahr, Dokument- und Fragewörter), bis zu 2 neue Treffer für P1 und P2, Gegenstück-Suche nutzt sie ebenfalls; Zitier-Rückfrage (einmal, wenn Zahlen ohne `[n]`); Einheitenfaktor der Metrik nur für ct und EUR; Fehler `parse_number("0,348")` behoben (ISS-073)
- RUN-018 (P2) und RUN-019 (P1), `qwen2.5:7b`: P2 nach Handprüfung 6 von 14 wie RUN-014, Fehler erkannt 0 von 3; Antworten mit Treffernummer 5 von 9 auf 9 von 9; Sollzahlen im Kontext P2 17 auf 18, P1 13 unverändert; P1/S5 jetzt Fehlalarm. Nachbewertung RUN-010 bis RUN-017 ändert nichts
- Entscheidung des Nutzers: mergen, Größen-Anfrage bleibt an (`quantity_hits=2`); Hierarchie-Boost und Tabellen-Summaries für den Agenten unverändert

## Nächstes Arbeitspaket
M6i – Sparte in der Größen-Anfrage (ISS-077): „Arbeitspreis“ trifft ohne Sparte das Gas-Schreiben; Sparte aus „Stromabrechnung“ behalten (als Suchwort oder Filter, nur wenn die Frage sie nennt), P1 und P2 neu messen. Optional G3 (Vorjahres-Gegenstück, ISS-074) und leere Antwort nach Rückfrage (ISS-076). Plan zuerst vorlegen. Offen für dich: Soll M6 danach abgeschlossen werden (Reverse-Engineering M6, Tag v1.0.0) oder schon jetzt mit M6h?

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Retrieval-Scoring und Testmodul; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. M6i (siehe oben), danach Reverse-Engineering M6 und Tag v1.0.0
2. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6h nachtragen
3. Phase 2 (Ausarbeitung) erst auf dein Wort; Negativergebnisse Prüfablauf (ADR-0016) und Größen-Anfrage (ADR-0017), Autonomie gegen Zuverlässigkeit gehören ins Kapitel Reflexion

## Offene Entscheidungen / Fragen
- M6 mit M6h oder erst nach M6i abschließen (Reverse-Engineering M6, Tag v1.0.0)?
- Hierarchie-Boost und Tabellen-Summaries: unverändert gelassen (ISS-027, ISS-035), erst nach M6i neu bewerten
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-077/074/076: Größen-Anfrage ohne Sparte trifft bei P1 das falsche Dokument, G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-075: VM-Speicher, Umgebung in `/dev/shm`
- ISS-070/071/068: Prüfablauf (abgeschaltet) ordnet Soll und Ist falsch zu, Nachricht löst Lückenantworten und Sprachwechsel aus; ISS-066/067: Fehlalarme durch falsche Operanden bleiben Grenze, P2 findet die eingebauten Fehler kaum
- ISS-062: Rückschritte S2/S4/N2 aus dem Code von M6e, Ursache nicht getrennt; ISS-057: Laufzeit nur zwischen Läufen mit gleicher Ladepolitik vergleichbar; ISS-054: `qwen2.5:7b` sagt oft „ja“
- ISS-050/038: „richtig laut Metrik“ nur mit Handprüfung verwenden; ISS-053/047/046/045: RAGAS nur als zweite Sicht (Antwortmodell und Bewerter sind jetzt beide `qwen2.5:7b`); ISS-039: B0 sieht nur Stromdokumente; ISS-029: S4 (Diagramm)
- ISS-036, ISS-030/031/032/033, ISS-025/027/028, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: jeder `uv`-Befehl beginnt mit `export UV_CACHE_DIR=/dev/shm/uvc UV_PROJECT_ENVIRONMENT=/dev/shm/venv UV_LINK_MODE=hardlink` (VM-Platte voll, alte `/tmp`-Ordner nicht löschbar, ISS-075/065/069; `/dev/shm` ist nach Sitzungsende leer), in neuer Sitzung zuerst `uv sync`; Quality Gate `./scripts/check.sh` vor jedem Commit, auch bei Daten und Skripten (ISS-056), nie hinter eine Pipe vor `&&` (ISS-048)
- Dateien im Projektordner: `Write`/`Edit` wirken nur im Container. Bearbeiten über `device_bash` (kleine Python-Ersetzung mit `assert`) oder Stage-Kopie bearbeiten und mit `device_commit_files` zurückschreiben
- Evaluation: `generate` → `score` (ohne Ollama) → `check_evidence.py`, `analyze_timing.py` → `ragas` (`uv run --group ragas …`); ein Lauf = ein Antwortmodell; für Vergleichsläufe nur P2: `generate --variants p2 --all`
- Nach jedem Lauf `uv run python scripts/check_evidence.py --run-id <id>` und die Antworten von Hand lesen; Journal sichern (`truncat|oom`)
- Die Zeichenkette `toolbench_rapidapi_key` in `run-011` ist vom Modell erfunden und bleibt in den Rohdaten (ISS-054); meldet GitHub sie beim Push, ist das ein Fehlalarm
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
- Nach jedem Lauf das Ollama-Journal ohne Filter sichern (`journalctl -u ollama --since "-130min"`): nur dort stehen Modellladungen und Cache-Treffer
