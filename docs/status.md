# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-18 (RAGAS-Auswertung v1.0.0, Phase 2 freigegeben)
**Phase:** 2 – Ausarbeitung (vom Nutzer am 2026-11-18 freigegeben); Phase 1 abgeschlossen
**Aktueller Meilenstein:** M7 Ausarbeitung
**Version:** v1.0.0

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde offen) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | fertig (Reverse-Engineering Runde 1 vorbereitet) | v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8 von 14, P2 6 von 14 nach Handprüfung, eingebaute Fehler 0 von 3; RAGAS v1.0.0 ausgewertet; M6-Fragen nur von Claude erklärt, ISS-085) | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft (Kapitel 1 als Nächstes) | – |

## Zuletzt erledigt (Sitzung: RAGAS-Auswertung)
- RAGAS-Nachtlauf (3,1 h, ohne Fehlschlag) ausgewertet: Faithfulness / Context Recall P1 0,72 / 0,38, P2 0,69 / 0,46; Nachtrag in `evaluation-log.md`, ISS-082 gelöst
- Die 8 Widersprüche zum Sollfakten-Abgleich sind Scheinwidersprüche (ISS-086); Faithfulness trennt bei P2 richtige nicht von falschen Antworten
- Nutzer gibt Phase 2 frei und liefert keinen O-Ton mehr (ISS-087)

## Nächstes Arbeitspaket
Phase 2, Kapitel 1 „Problem & Use Case“ (`paper/content/chapter/01-problem-use-case/main.tex`) mit dem Skill audit-paper-writer. Vorher einmal das Seitenbudget je Kapitel aus `concept.md` Abschnitt 14 festlegen und die Titelblatt-Angaben erfragen; dann Material mit Fundstellen sammeln, Gliederung zur Freigabe vorlegen, Entwurf schreiben (Branch `docs/paper-01-problem-use-case`).

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Kapitel 1 bis 6 nacheinander, ein Kapitel je Chat; zusammen 5–8 Seiten Fließtext
2. Endkontrolle einmalig mit Opus 5.5 / Max (Checkliste `writing-guide.md` Abschnitt 4, `requirements.md` Abschnitt 11)
3. Nur bei Zeit: ISS-080/081/086

## Offene Entscheidungen / Fragen
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen (ISS-087)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton (1 von 20 Journal-Einträgen); ISS-084/085: Verständnisfragen M0–M6 nicht selbst beantwortet. Reflexion droht generisch, Verständnis ist bewertungsrelevant
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-080/081/083: im Katalog nicht wirksame Schwächen aus dem Reverse Engineering
- ISS-078/075: Claudes Shell ohne `uv`, Quality Gate läuft auf dem Laptop
- ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<kapitel>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht mehr nach dem O-Ton fragen (Wunsch des Nutzers, ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer, Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md` (RUN-020/021 und RAGAS-Nachtrag); fehlende Angaben als `\todo{...}`
- LaTeX: `latexmk`, `pdflatex`, `lualatex` sind in Claudes Shell vorhanden (`cd paper && latexmk -pdf main.tex`); Seitenzahl damit selbst prüfen
- Claudes Shell (ISS-078): kein `uv`, kein `ruff`/`pytest`; Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer geben. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`); `Write`/`Edit` wirken nur im Container
