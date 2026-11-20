# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-20 (Kapitel 6 entfernt, Klang überarbeitet, ISS-105/106)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | Kapitel 6 entfernt (Nutzer), Kapitel 1–5 ohne Fragen-Kürzel und „synthetisch“ überarbeitet, Tabelle 5.1 mit allen 14 Fragen; fünf Quellen (ReAct, Gao, RAGAS, Xiang, Ferrazzi); Inhalt 8 Seiten, Literatur S. 9; offen nur noch Punkte des Nutzers (siehe Nächste Schritte) | – |

## Zuletzt erledigt (Sitzung: Kapitel 6 entfernt, Klang überarbeitet)
- Kapitel 6 ohne Ersatz gelöscht (Wunsch Nutzer); in Kapitel 5 ein Absatz zu Annahme, Ferrazzi et al. und 7B-Grenze (vom Nutzer freigegeben, ISS-106)
- Kapitel 1–5 sprachlich überarbeitet (ISS-105): keine Fragen-Kürzel im Fließtext, kein „synthetischer Korpus“, Begründungen ausgeschrieben, Inversionen und Pointen umgestellt
- Tabelle 5.1 neu: alle 14 Fragen (gekürzt), Abrechnung korrekt / mit Fehler, Ergebnis je Variante, darunter Kennzahlen; RAGAS-Werte im Text
- Erster Entwurf 3 Seiten zu lang, auf 8 Seiten gekürzt (Kapitel 1–5: 1,15 / 1,3 / 1,67 / 1,64 / 2,15 S.); neues PDF `Claude outputs/Ausarbeitung-ohne-Kapitel6.pdf`

## Nächstes Arbeitspaket
Kein Claude-Paket geplant. Erst wenn der Nutzer Ergänzungen liefert (eigene Formulierungen, ggf. ein Satz Ausblick): einarbeiten, Branch `docs/paper-user-edits`, dafür anderswo kürzen (ca. 1 Zeile frei auf Seite 8), Zahlen erneut gegen `evaluation-log.md` prüfen, neues PDF nach `Claude outputs/`.

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Nutzer vor der Abgabe: `Ausarbeitung-ohne-Kapitel6.pdf` laut lesen; Abstract und Ergebnisse der fünf Paper selbst lesen (Kernaussagen in `sources.md`); Fragen 4, 6–9 und 11–14 in `paper-questions.md` beantworten; Stichproben der Handprüfung lesen (ISS-094); 2–3 Sätze je Kapitel selbst umformulieren; Abgabe über Moodle, optional mit Link zum Repository
2. Danach ggf. das Paket oben
3. Nur bei Zeit: ISS-080/081/086

## Offene Entscheidungen / Fragen
- Reflexion und Ausblick: Kapitel 6 entfallen (Nutzer), nur noch ein Absatz in Kapitel 5 und der GraphRAG-Ausblick in Kapitel 4 (ISS-106); ein Satz Ausblick wäre nur gegen Kürzung möglich
- Literatur: höchstens fünf Quellen (Entscheidung 2026-11-20); eine neue Quelle nur im Tausch gegen eine bestehende

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-106: Reflexion nach Entfernen von Kapitel 6 nur noch knapp (10-%-Kriterium); ISS-105: KI-Klang und Fragen-Kürzel überarbeitet, gelöst
- ISS-087: kein O-Ton; ISS-084/085/096: Verständnisfragen M0–M6 und Fragen zur Ausarbeitung nicht selbst beantwortet. Der Text enthält keine persönlichen Eindrücke, Verständnis ist bewertungsrelevant
- ISS-094: Hauptergebnis von Kapitel 5 beruht auf der Handprüfung durch Claude, vom Nutzer nicht gegengelesen; kein KI-Hinweis (Entscheidung 2026-11-18), Stichproben selbst lesen
- ISS-099/103: Paper nur von Claude gesichtet; Gao ordnet Filter und Query-Rewriting dem Advanced RAG zu, der Text nennt P1 nach der Vorlesung „modulare Pipeline“ (Prüferfrage 7). P2 läuft ohne Thought (Variante Act), Kapitel 3 sagt das. Context Recall steht nicht im RAGAS-Paper, der Text beschreibt es als Metrik der Bibliothek
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (steht nicht im Text)
- ISS-090/092/093/097/105: Seitenbudget; PDF endet ganz unten auf Seite 8 (gut eine Zeile frei), jede Ergänzung muss anderswo gekürzt werden. ISS-098: Endkontrolle mit vier Korrekturen, gelöst
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<…>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer (Endkontrolle: Checkliste vollständig als Liste ausgeben; seine Regel „Kein Literaturverzeichnis“ ist seit 2026-11-19 überholt, Literaturverzeichnis nicht wieder auskommentieren; höchstens fünf Quellen (ISS-103); jede Zitatstelle sagt nur, was das Paper selbst sagt, Mittelwerte als „im Mittel“, Ausnahmen in `sources.md`), Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Begriff „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen. Inhaltliche Aufteilung: Kapitel 3 Prüfablauf und Rückfragen, Kapitel 4 GraphRAG/Hausverwaltung, Kapitel 5 Qualitätsaussage, Einordnung (Ferrazzi) und Messgrenzen; Kapitel 6 gibt es nicht mehr (nichts davon doppeln). B0/P1/P2 stehen in Kapitel 1; Fragen-Kürzel (S1, G1 …) und „synthetisch“ nicht im Fließtext, Fragen über ihren Inhalt benennen (ISS-105). Vor jeder Ergänzung prüfen, ob der Absatz auf seiner letzten Zeile Platz hat (ISS-095)
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Ca. 380–400 Wörter je Seite; Wortzahl vor dem ersten Build zählen (Erstentwürfe 20–30 % zu lang); kurze Absatzenden kosten eine ganze Zeile; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen (Satzspiegel ca. 74–774 pt), Einträge im Inhaltsverzeichnis überspringen; Listings mit Umlauten brauchen `literate`. Neues PDF für den Nutzer nach `Claude outputs/` (über `device_commit_files`) Zum Vergleich der Seitenwirkung den alten Stand mit `git archive --format=tar.gz -o .paper-old.tgz main paper` mitbauen und die Zeilen je Absatz vergleichen (ISS-095).
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`). Rohdaten für Faktenprüfung: `data/processed/*_chunks.json`, `data/eval/run-*/p2-*.jsonl`, `scores.json` mit System-`python3` lesbar; PDFs mit `pdfplumber` (PyMuPDF fehlt im System-Python, `.venv/bin/python` fehlt). Layoutvergleich alt/neu: `diff` über `pdftotext -layout`
