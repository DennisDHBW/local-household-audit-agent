# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-18 (Kapitel 6 entworfen)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft: alle sechs Kapitel entworfen (1,3 / 1,3 / 1,6 / 1,25 / 1,45 / 0,7 S.; PDF endet auf Seite 8 nach gut 80 %, Puffer ca. 0,18 S.), Überarbeitung als Nächstes | – |

## Zuletzt erledigt (Sitzung: Kapitel 6)
- Kapitel 6 entworfen, 0,70 Seiten (Budget 0,75): Annahme aus Kapitel 1 nicht bestätigt (P1 auch bei Grenzfällen vorn), Verlauf P2 3 → 9 → 6 mit gemeinsam gemessenen Änderungen, G4 einmal erkannt und verloren, gültiger Aufruf gegen richtige Rechnung (G2), Rückfragen gegen Self-RAG, Prüfablauf sichert Herkunft statt Zuordnung, Chinesisch bei S5; Ausblick: Soll/Ist nach Dokumentart, Vorjahresrechnung (G3), Hinweis Rechtsberatung, größerer Fragenkatalog
- Fünf Fragen in `paper-questions.md`; PDF aller Kapitel unter `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` (nicht versioniert)

## Nächstes Arbeitspaket
Überarbeitung aller Kapitel. **Vorher (Nutzer):** PDF `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` lesen, Stellen markieren (Seite und Satz, als Liste im Chat oder in `paper-questions.md`) und die Fragen in `docs/paper-questions.md` unter „Antworten (von mir)“ kurz beantworten, dazu die Punkte „Beim Lesen besonders prüfen“ und die offenen Entscheidungen unten. **Claude:** Antworten und Markierungen einarbeiten (Formulierungen des Nutzers sinngemäß übernehmen), Querverweise und Wiederholungen zwischen den Kapiteln prüfen, Seitenzahl halten (max. 8), Branch `docs/paper-revision`. Liegen keine Antworten vor: nur Kapitel gegeneinander prüfen und die offenen Entscheidungen abfragen.

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Überarbeitung (siehe oben)
2. Endkontrolle einmalig mit Opus 5.5 / Max (Checkliste `writing-guide.md` Abschnitt 4, `requirements.md` Abschnitt 11)
3. Nur bei Zeit: ISS-080/081/086/088

## Offene Entscheidungen / Fragen
- Bearbeitungszeitraum auf dem Titelblatt: „November 2026“ ok oder gibt die DHBW einen Zeitraum vor?
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen, Platz in Kapitel 6 ca. 0,05 S. (ISS-087)
- KI-Hinweis: Soll die Ausarbeitung nennen, dass Claude die Handprüfung der Antworten gemacht hat? Vorher Stichproben selbst lesen (ISS-094)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton; ISS-084/085: Verständnisfragen M0–M6 nicht selbst beantwortet. Kapitel 6 enthält keine persönlichen Eindrücke, Verständnis ist bewertungsrelevant
- ISS-094: Hauptergebnis von Kapitel 5 beruht auf der Handprüfung durch Claude, vom Nutzer nicht gegengelesen
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (Kapitel 1 und 6)
- ISS-090/092/093: Seitenbudget; Summe der Kapitel ca. 7,6 S., im PDF wegen Gleitobjekten ca. 7,8 S.; Ergänzungen in der Überarbeitung müssen anderswo gekürzt werden
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<…>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer (Schritt 5 Überarbeitung), Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Begriff „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen. Inhaltliche Aufteilung: Kapitel 3 Prüfablauf und Rückfragen, Kapitel 4 GraphRAG/Hausverwaltung, Kapitel 5 Qualitätsaussage und Messgrenzen, Kapitel 6 nur Bewertung und Ausblick (nichts davon doppeln)
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Ca. 380–400 Wörter je Seite; Wortzahl vor dem ersten Build zählen (Erstentwürfe 20–30 % zu lang); kurze Absatzenden kosten eine ganze Zeile; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen (Satzspiegel ca. 74–774 pt), Einträge im Inhaltsverzeichnis überspringen; Listings mit Umlauten brauchen `literate`. Neues PDF für den Nutzer nach `Claude outputs/` (über `device_commit_files`)
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`)
