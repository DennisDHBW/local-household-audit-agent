# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-20 (Quellenprüfung, ISS-102)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | Endkontrolle fertig (ISS-098); fünf Quellen eingebaut (ISS-099) und geprüft, sieben Stellen präzisiert (ISS-102); Inhalt 8 Seiten, Literatur S. 9; offen nur noch Punkte des Nutzers (siehe Nächste Schritte) | – |

## Zuletzt erledigt (Sitzung: Quellenprüfung)
- Alle fünf Paper auf arxiv.org, aclanthology.org, iclr.cc bestätigt (ICLR 2026 bei Xiang jetzt belegt); jede Zitatstelle gegen das Paper gelesen
- Sieben Stellen präzisiert (ISS-102): Self-RAG (Kap. 3, 6), ReAct/Act (Kap. 3), Xiang „meist“ (Kap. 4), Context Recall mit RAGAS-Doku als Quelle [5] und „je Aussage“ (Kap. 5), Ferrazzi „im Mittel“ (Kap. 6, jetzt [6]); Literaturverzeichnis ohne „Adresse:“, mit DOI
- Neues PDF `Claude outputs/Ausarbeitung-Quellenpruefung.pdf` (Seitenumbrüche wie vorher, Inhalt bis Seite 8, Literatur Seite 9)

## Nächstes Arbeitspaket
Kein Claude-Paket geplant. Erst wenn der Nutzer Ergänzungen liefert (persönlicher Teil Kapitel 6, eigene Formulierungen, Antworten aus `paper-questions.md`): diese einarbeiten, Branch `docs/paper-user-edits`, dafür anderswo kürzen (kein Seitenpuffer), Zahlen erneut gegen `evaluation-log.md` prüfen, neues PDF nach `Claude outputs/`.

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Nutzer vor der Abgabe: von den fünf Papern Abstract und Ergebnisse selbst lesen (ISS-099, Kernaussagen und Ausnahmen in `sources.md`), neue Fragen 4–6 zu den Quellen in `paper-questions.md` beantworten; PDF laut lesen; jeden Absatz mündlich erklären können (Fragen in `paper-questions.md`, ISS-096); Stichproben der Handprüfung selbst lesen (ISS-094); in jedem Kapitel 2–3 Sätze selbst umformulieren; persönlichen Teil in Kapitel 6 ergänzen (ISS-087); Abgabe über Moodle, optional mit Link zum Repository
2. Danach ggf. das Paket oben
3. Nur bei Zeit: ISS-080/081/086/088

## Offene Entscheidungen / Fragen
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen; dafür muss anderswo gekürzt werden (ISS-087)
- Literaturbezug: fünf Paper plus RAGAS-Dokumentation für Context Recall (Entscheidung 2026-11-19, ergänzt 2026-11-20); Reserve in `sources.md` nur bei freiem Platz

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton; ISS-084/085/096: Verständnisfragen M0–M6 und Fragen zur Ausarbeitung nicht selbst beantwortet. Kapitel 6 enthält keine persönlichen Eindrücke, Verständnis ist bewertungsrelevant
- ISS-094: Hauptergebnis von Kapitel 5 beruht auf der Handprüfung durch Claude, vom Nutzer nicht gegengelesen; kein KI-Hinweis (Entscheidung 2026-11-18), Stichproben selbst lesen
- ISS-099: Paper nur von Claude gesichtet; ISS-101/102: Context Recall nur in der RAGAS-Dokumentation belegt; P2 läuft ohne Thought (Variante Act des ReAct-Papers), Kapitel 3 sagt das jetzt
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (Kapitel 1 und 6)
- ISS-090/092/093/097: Seitenbudget; PDF endet ganz unten auf Seite 8, jede Ergänzung muss anderswo gekürzt werden. ISS-098: Endkontrolle mit vier Korrekturen, gelöst
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<…>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer (Endkontrolle: Checkliste vollständig als Liste ausgeben; seine Regel „Kein Literaturverzeichnis“ ist seit 2026-11-19 überholt, Literaturverzeichnis nicht wieder auskommentieren; jede Zitatstelle sagt nur, was das Paper selbst sagt, Mittelwerte als „im Mittel“, Ausnahmen in `sources.md`), Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Begriff „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen. Inhaltliche Aufteilung: Kapitel 3 Prüfablauf und Rückfragen, Kapitel 4 GraphRAG/Hausverwaltung, Kapitel 5 Qualitätsaussage und Messgrenzen, Kapitel 6 nur Bewertung und Ausblick (nichts davon doppeln). Kürzel S/G/N/Z, B0/P1/P2 und G1 als Beispiel stehen in Kapitel 1 und werden danach vorausgesetzt. Vor jeder Ergänzung prüfen, ob der Absatz auf seiner letzten Zeile Platz hat (ISS-095)
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Ca. 380–400 Wörter je Seite; Wortzahl vor dem ersten Build zählen (Erstentwürfe 20–30 % zu lang); kurze Absatzenden kosten eine ganze Zeile; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen (Satzspiegel ca. 74–774 pt), Einträge im Inhaltsverzeichnis überspringen; Listings mit Umlauten brauchen `literate`. Neues PDF für den Nutzer nach `Claude outputs/` (über `device_commit_files`) Zum Vergleich der Seitenwirkung den alten Stand mit `git archive --format=tar.gz -o .paper-old.tgz main paper` mitbauen und die Zeilen je Absatz vergleichen (ISS-095).
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`). Rohdaten für Faktenprüfung: `data/processed/*_chunks.json`, `data/eval/run-*/p2-*.jsonl`, `scores.json` mit System-`python3` lesbar; PDFs mit `pdfplumber` (PyMuPDF fehlt im System-Python, `.venv/bin/python` fehlt). Layoutvergleich alt/neu: `diff` über `pdftotext -layout`
