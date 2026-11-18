# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-18 (Kapitel 3 entworfen)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft: Kapitel 1–3 entworfen (ca. 1,3 / 1,3 / 1,6 S.), Kapitel 4 als Nächstes | – |

## Zuletzt erledigt (Sitzung: Kapitel 3)
- Kapitel 3 entworfen, ca. 1,6 Seiten: zwei Phasen, Werkzeugtabelle, Schleife mit Rückfragen, Prüfablauf als Negativergebnis, ReAct-Listing Z1 aus RUN-021, Modellwahl und Antwortzeit (Nutzer ließ ohne Rückmeldung fortfahren: Z1 als Beispiel, Prüfablauf in Kapitel 3)
- Erster Entwurf 616 Wörter / ca. 2,1 S., in drei Runden gekürzt (ISS-092); Zahlen aus den RUN-021-Protokollen als Nachtrag in `evaluation-log.md`
- ISS-091: ADR-0014 schrieb den Rückgang ungültiger Aufrufe dem Suchwerkzeug zu, tatsächlich fehlte `calculate`; korrigiert. Kapitel 2: Zeilenüberlauf behoben

## Nächstes Arbeitspaket
Kapitel 4 „RAG- und Retrieval-Konzept“ (`paper/content/chapter/04-retrieval/main.tex`, Budget 1,25 Seiten, höchstens ca. 400 Wörter Fließtext, falls Formel oder Tabelle dazukommen weniger) mit dem Skill audit-paper-writer. Material mit Fundstellen (concept §6 und §10, ADR-0002/0003/0009/0014/0017, RUN-004, RUN-018 bis RUN-021, Belegnummern und Trefferkürzung auf 600 Zeichen, die in Kapitel 3 fehlen) und Gliederung mit Wortzahl je Absatz zusammen mit dem Plan vorlegen, nach dem OK schreiben, messen, 3–5 Fragen in `paper-questions.md`, mergen (Branch `docs/paper-04-retrieval`).

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Kapitel 4 bis 6, ein Kapitel je Chat (Budget laut `concept.md` §14; Hochrechnung ca. 7,7 von 8 Seiten, Puffer nur noch ca. 0,3)
2. Danach ein Chat Überarbeitung: Nutzer liest alle Kapitel, beantwortet `paper-questions.md`, Claude arbeitet Markierungen und Antworten ein
3. Endkontrolle einmalig mit Opus 5.5 / Max (Checkliste `writing-guide.md` Abschnitt 4, `requirements.md` Abschnitt 11)
4. Nur bei Zeit: ISS-080/081/086/088

## Offene Entscheidungen / Fragen
- Bearbeitungszeitraum auf dem Titelblatt: „November 2026“ ok oder gibt die DHBW einen Zeitraum vor?
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen (ISS-087)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton; ISS-084/085: Verständnisfragen M0–M6 nicht selbst beantwortet. Reflexion droht generisch, Verständnis ist bewertungsrelevant
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (in Kapitel 1 genannt)
- ISS-090/092: Seitenbudget knapp (Kapitel 1–3: 1,3 / 1,3 / 1,6 S.); Kapitel 4–6 dürfen ihr Budget nicht überschreiten
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<kapitel>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer, Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Kapitel ohne Unterabschnitte, solange das Budget unter 1,5 Seiten liegt; RUN-004-Ergebnis „ohne Summaries 8 statt 9 von 10“ steht schon in Kapitel 2, in Kapitel 4 nur verweisen; Kapitel 3 nennt Werkzeuge, Schleife und Rückfragen, Filter nach Sparte und `search` nur kurz mit Verweis auf Kapitel 4
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Neuen Build-Ordner je Lauf anlegen (Löschen des Arbeitsordners wird blockiert). Ca. 380–400 Wörter je Seite, Tabelle plus Listing ca. 0,4 S.; Wortzahl vor dem ersten Build zählen, die ersten Entwürfe waren immer 20–30 % zu lang; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen; Listings mit Umlauten brauchen `literate`
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`)
