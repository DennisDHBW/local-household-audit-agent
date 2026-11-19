# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-19 (GraphRAG-Absatz überarbeitet, Kapitel gegen Anforderungen geprüft)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft: alle sechs Kapitel entworfen und gegeneinander geprüft und gegen die Anforderungen geprüft (PDF endet ganz unten auf Seite 8, kein Puffer); Überarbeitung Teil 2 entfallen, Endkontrolle als Nächstes | – |

## Zuletzt erledigt (Sitzung: Überarbeitung Teil 2 entfällt, GraphRAG und Anforderungen)
- Überarbeitung Teil 2 entfällt, weil keine Antworten oder Markierungen vorlagen (Entscheidung Nutzer, ISS-096)
- GraphRAG-Absatz in Kapitel 4 auf Nachfrage kritisch geprüft und neu geschrieben (ISS-097, Nachtrag ADR-0003, concept §10): Entscheidung bleibt, aber mit Entitäten, betroffenen Fragen G1/G3, Belegen und Faktentabelle als Alternative
- Kapitel gegen `requirements.md` geprüft: Modellwahl im Enrichment (Kapitel 3), Abgrenzung zur Hybrid-Suche (Kapitel 4), Restpunkte ISS-095 umgesetzt; für die Seitenzahl an sieben Stellen gekürzt (Liste in `paper-questions.md`)
- Neues PDF `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` (8 Seiten, letzte Seite voll)

## Nächstes Arbeitspaket
Endkontrolle der Ausarbeitung (einmalig), Branch `docs/paper-final-check`: Checkliste `writing-guide.md` Abschnitt 4 und `requirements.md` Abschnitt 11 vollständig durchgehen und als Liste ausgeben (Skill audit-paper-writer), jede Zahl und jede Absolutaussage gegen `evaluation-log.md` bzw. die Quelle prüfen (ISS-093), Seitenzahl max. 8 halten (kein Puffer mehr, jede Ergänzung kürzt anderswo), neues PDF nach `Claude outputs/`. Punkte, die nur der Nutzer erfüllen kann (jeden Absatz mündlich erklären, eigene Formulierungen, laut lesen, Abgabe über Moodle), nicht abhaken, sondern als offene Liste übergeben.

**Empfohlenes Modell:** Opus 5.5, Effort Max (Endkontrolle; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Endkontrolle (siehe oben)
2. Nutzer vor der Abgabe: PDF lesen, Stichproben der Handprüfung selbst lesen (ISS-094), Fragen in `paper-questions.md` als Vorbereitung auf Nachfragen durchgehen (ISS-096), persönlichen Teil in Kapitel 6 ergänzen (ISS-087), Abgabe über Moodle
3. Nur bei Zeit: ISS-080/081/086/088

## Offene Entscheidungen / Fragen
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen; dafür muss anderswo gekürzt werden (ISS-087)
- Literaturbezug (Kriterium 6, 10 %) bewusst ohne Quellen (Entscheidung 2026-11-14); bleibt Risiko

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton; ISS-084/085/096: Verständnisfragen M0–M6 und Fragen zur Ausarbeitung nicht selbst beantwortet. Kapitel 6 enthält keine persönlichen Eindrücke, Verständnis ist bewertungsrelevant
- ISS-094: Hauptergebnis von Kapitel 5 beruht auf der Handprüfung durch Claude, vom Nutzer nicht gegengelesen; kein KI-Hinweis (Entscheidung 2026-11-18), Stichproben selbst lesen
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (Kapitel 1 und 6)
- ISS-090/092/093/097: Seitenbudget; PDF endet ganz unten auf Seite 8 (Kapitel 4 ca. 570 Wörter nach GraphRAG-Überarbeitung); Ergänzungen müssen anderswo gekürzt werden
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<…>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer (Endkontrolle: Checkliste vollständig als Liste ausgeben), Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Begriff „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen. Inhaltliche Aufteilung: Kapitel 3 Prüfablauf und Rückfragen, Kapitel 4 GraphRAG/Hausverwaltung, Kapitel 5 Qualitätsaussage und Messgrenzen, Kapitel 6 nur Bewertung und Ausblick (nichts davon doppeln). Kürzel S/G/N/Z, B0/P1/P2 und G1 als Beispiel stehen in Kapitel 1 und werden danach vorausgesetzt. Vor jeder Ergänzung prüfen, ob der Absatz auf seiner letzten Zeile Platz hat (ISS-095)
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Ca. 380–400 Wörter je Seite; Wortzahl vor dem ersten Build zählen (Erstentwürfe 20–30 % zu lang); kurze Absatzenden kosten eine ganze Zeile; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen (Satzspiegel ca. 74–774 pt), Einträge im Inhaltsverzeichnis überspringen; Listings mit Umlauten brauchen `literate`. Neues PDF für den Nutzer nach `Claude outputs/` (über `device_commit_files`) Zum Vergleich der Seitenwirkung den alten Stand mit `git archive --format=tar.gz -o .paper-old.tgz main paper` mitbauen und die Zeilen je Absatz vergleichen (ISS-095).
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`)
