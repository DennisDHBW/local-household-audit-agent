# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-17 (M6i)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6i fertig; Abschluss mit Reverse-Engineering M6 und Tag v1.0.0 steht aus)
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
| M6 | Testmodul & Evaluation | M6a–M6i fertig (RUN-020: P1 nach Handprüfung 8 von 14, RUN-021: P2 6 von 14); Reverse-Engineering M6 offen | v1.0.0 (offen) |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6i)
- Sparte in der Größen-Anfrage (ISS-077 gelöst): `utility_in_query` erkennt genau eine Sparte („Stromabrechnung“, „Gas“, „Fernwärme“), `with_query_utility` filtert Größen- und Gegenstück-Suche danach, sofern kein Filter gesetzt ist; 20 neue Tests (381 insgesamt)
- RUN-020 (P1): Sollzahlen im Kontext 13 auf 16 von 27, Fakten in der Antwort 9 auf 12, Fehlalarm S5 weg; G1 hat jetzt 38,20 und 39,50 ct im Kontext, Antwort trotzdem falsch
- RUN-021 (P2): unverändert gegen RUN-018 (13 von 14 Antworten wortgleich), der Agent setzt die Sparte selbst; Lauf brach nach N2 ab und wurde fortgesetzt (ISS-079)

## Nächstes Arbeitspaket
Reverse-Engineering M6 (Skill `audit-reverse-engineering`, Datei `docs/reverse-engineering/m6.md`): Testmodul, Metriken, Größen-Anfrage, Sparten-Filter, Zitier-Rückfrage; danach M6 gegen `requirements.md` prüfen und Tag v1.0.0 setzen. G3 (ISS-074) und leere Antwort (ISS-076) bleiben als dokumentierte Grenzen.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Reverse-Engineering-Runde; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Reverse-Engineering M6, Abgleich mit `requirements.md`, Tag v1.0.0
2. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6h nachtragen
3. Phase 2 (Ausarbeitung) erst auf dein Wort; Engpass Lesen und Vergleichen (G1 bei P1 und P2), Negativergebnisse ADR-0016/0017 und Autonomie gegen Zuverlässigkeit gehören ins Kapitel Reflexion

## Offene Entscheidungen / Fragen
- Hierarchie-Boost und Tabellen-Summaries: unverändert (ISS-027, ISS-035), nicht mehr vor v1.0.0
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt, `eval_run.sh` überschreibt Log beim Fortsetzen
- ISS-078/075: Claudes Shell ohne bleibende Umgebung, Quality Gate läuft im Messbefehl auf dem Laptop
- ISS-070/071/068: Prüfablauf (abgeschaltet) ordnet Soll und Ist falsch zu; ISS-066/067: Fehlalarme durch falsche Operanden, eingebaute Fehler werden kaum erkannt (0 von 3)
- ISS-062, ISS-057 (Laufzeit nur bei gleicher Ladepolitik vergleichbar), ISS-054 (`qwen2.5:7b` sagt oft „ja“), ISS-050/038 (Metrik nur mit Handprüfung), ISS-053/047/046/045 (RAGAS nur zweite Sicht), ISS-039, ISS-029
- ISS-036, ISS-030/031/032/033, ISS-025/027/028, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell (ISS-078): `/dev/shm` ist je Aufruf leer, `uv sync` schafft 180 s nicht. Erst einmal probieren (`export UV_CACHE_DIR=/dev/shm/uvc UV_PROJECT_ENVIRONMENT=/dev/shm/venv UV_LINK_MODE=hardlink`, Sync und Prüfung in einem Aufruf); scheitert es, `./scripts/check.sh > <log> 2>&1 &&` an den Anfang des Befehls für das Terminal des Nutzers stellen
- Dateien im Projektordner: über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`); `Write`/`Edit` wirken nur im Container
- Evaluation: `generate` → `score` → `check_evidence.py`, `analyze_timing.py`; abgebrochene Läufe mit demselben `generate`-Befehl fortsetzen (überspringt Beantwortetes), Log mit `tee -a`, nicht über `eval_run.sh` (ISS-079); nach einem Neustart Systemjournal mit `journalctl -b -1` sichern
- Nach jedem Lauf alle Antworten von Hand lesen; Ollama-Journal ohne Filter sichern
- Die Zeichenkette `toolbench_rapidapi_key` in `run-011` ist vom Modell erfunden (ISS-054); meldet GitHub sie beim Push, ist das ein Fehlalarm
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`
