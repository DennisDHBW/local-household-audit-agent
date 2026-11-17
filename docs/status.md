# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-17 (M6-Fragen im Repo gesichert)
**Phase:** 1 – Umsetzung (abgeschlossen bis auf offene Antworten; Phase 2 erst auf dein Wort)
**Aktueller Meilenstein:** M6 fertig, Tag v1.0.0 gesetzt
**Version:** v1.0.0

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | fertig (Reverse-Engineering Runde 1 vorbereitet) | v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (RUN-020: P1 8 von 14 nach Handprüfung, RUN-021: P2 6 von 14, eingebaute Fehler 0 von 3); Reverse-Engineering-Notizen in drei Runden vorbereitet, Antworten offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (Sitzung: Fragen sichern)
- Auswertung der Reverse-Engineering-Antworten verschoben: Nutzer hat aktuell keine Zeit zum Antworten
- Die M6-Fragen standen nur im alten Chat (ISS-084); neu formuliert als R1-1 bis R3-8 in Abschnitt 6 der drei M6-Notizen eingetragen
- Davor (Abschluss M6): Notizen in drei Runden, Abgleich mit `requirements.md`, ISS-080 bis ISS-083, Tag v1.0.0

## Nächstes Arbeitspaket
Wartet auf den Nutzer: Er meldet sich, sobald er die Fragen R1-1 bis R3-8 (Abschnitt 6 der M6-Notizen) beantwortet hat; dann Antworten mit dem Code abgleichen und „Stimmt?“ füllen. Optional vorher über Nacht RAGAS für RUN-020/021 (Befehl in ISS-082). Phase 2 nur auf sein Wort.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Reverse-Engineering-Runde; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Reverse-Engineering-Fragen M6 (drei Runden) und M2–M5 beantworten, Abschnitte 5–7 der Notizen selbst füllen, mindestens einen fehlenden Whitebox-Test selbst schreiben
2. O-Ton für M0 bis M6 nachtragen (Rohmaterial für die Reflexion)
3. Phase 2 (Ausarbeitung) erst auf dein Wort; Engpass Lesen und Vergleichen (G1 bei P1 und P2), Negativergebnisse ADR-0016/0017 und Autonomie gegen Zuverlässigkeit gehören ins Kapitel Reflexion

## Offene Entscheidungen / Fragen
- RAGAS-Nachtlauf für RUN-020/021 machen oder RAGAS-Werte mit altem Code-Stand berichten (ISS-082)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)
- ISS-080/081 erst nach v1.0.0, nur wenn Zeit bleibt

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-084: Fragen zu M0, M2–M5 nur in alten Chats
- ISS-080/081/083: neue, im Katalog nicht wirksame Schwächen aus dem Reverse Engineering; ISS-082: RAGAS nicht für v1.0.0
- ISS-078/075: Claudes Shell ohne bleibende Umgebung, Quality Gate läuft auf dem Laptop
- ISS-070/071/068 (Prüfablauf abgeschaltet), ISS-066/067 (Fehlalarme, 0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-053/047/046/045, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Claudes Shell (ISS-078): kein `uv`-Umfeld, kein `ruff`/`pytest`; Quality Gate als `./scripts/check.sh > <log> 2>&1 &&` vor den Befehl für das Terminal des Nutzers stellen. Python 3.10 der Shell reicht für Skripte ohne Projekt-Imports (z. B. JSON-Logs lesen)
- Dateien im Projektordner: über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`); `Write`/`Edit` wirken nur im Container
- Reverse-Engineering-Auswertung: Antworten nicht umformulieren, Abschnitt 6 füllt der Nutzer selbst; M6-Fragen stehen in Abschnitt 6 der Notizen (R1-1 … R3-8); für M0 und M2–M5 erst die Fragen ins Repo schreiben (ISS-084). Neue Fragen immer direkt in Abschnitt 6
- Evaluation: `generate` → `score` → `check_evidence.py`, `analyze_timing.py`; abgebrochene Läufe mit demselben `generate`-Befehl fortsetzen, Log mit `tee -a` (ISS-079)
