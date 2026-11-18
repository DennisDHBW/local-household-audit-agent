# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-18 (Kapitel 4 entworfen)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft: Kapitel 1–4 entworfen (ca. 1,3 / 1,3 / 1,6 / 1,25 S.), Kapitel 5 als Nächstes | – |

## Zuletzt erledigt (Sitzung: Kapitel 4)
- Kapitel 4 entworfen, ca. 1,25 Seiten (im Budget): Index und Hierarchie-Präfix, Score-Formel mit S2-Beispiel, Boost ohne belegten Nutzen, Metadatenfilter (RUN-004) und Filterpolitik des Agenten, Gegenstück, Größen-Anfrage (ISS-072/077, RUN-020), Evidence-First, GraphRAG-Entscheidung
- ADR-0003 auf „akzeptiert“ (Nutzer); Glossar: Query-Rewriting, Sollfakt; concept §14 aktualisiert
- ISS-093: Entwurf zu lang, drei zugespitzte Aussagen beim Gegenlesen korrigiert

## Nächstes Arbeitspaket
Kapitel 5 „Testmodul und Evaluation“ (`paper/content/chapter/05-evaluation/main.tex`, Budget 1,5 Seiten inkl. Ergebnistabelle) mit dem Skill audit-paper-writer. Material mit Fundstellen (concept §11, ADR-0011/0012, Fragenkatalog 14 Fragen, RUN-010 bis RUN-021 mit Handprüfung, RAGAS-Nachtrag v1.0.0, Fehleranalyse, ISS-028/038/045/047/050/053/086) und Gliederung mit Wortzahl je Absatz zusammen mit dem Plan vorlegen, nach dem OK schreiben, messen, 3–5 Fragen in `paper-questions.md`, mergen (Branch `docs/paper-05-evaluation`).

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Kapitel 5 und 6, ein Kapitel je Chat (Budget laut `concept.md` §14; Hochrechnung ca. 7,7 von 8 Seiten, Puffer ca. 0,3)
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
- ISS-090/092/093: Seitenbudget knapp (Kapitel 1–4: 1,3 / 1,3 / 1,6 / 1,25 S.); Kapitel 5 und 6 dürfen ihr Budget nicht überschreiten; Erstentwürfe waren bisher immer zu lang
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<kapitel>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer, Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Kapitel ohne Unterabschnitte, solange das Budget unter 1,5 Seiten liegt; Kapitel 4 enthält schon RUN-004 (Filter, Boost), 9 von 19 Agentenfiltern (RUN-010) und P1 16 statt 13 von 27 Sollfakten im Kontext (RUN-020); Kapitel 5 verweist darauf und ordnet G1 als Lese- und Vergleichsfehler ein. Begriff „Sollfakten“ statt „Sollzahlen“ (Glossar); Kandidat für Kapitel 5: Zitier-Rückfrage 9 von 9 Antworten mit `[n]` (RUN-018)
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Neuen Build-Ordner je Lauf anlegen (Löschen des Arbeitsordners wird blockiert). Ca. 380–400 Wörter je Seite, Tabelle plus Listing ca. 0,4 S.; Wortzahl vor dem ersten Build zählen, die ersten Entwürfe waren immer 20–30 % zu lang (Kapitel 4: ca. 1,25 S. bei gut 450 Wörtern plus Formel); kurze Absatzenden kosten eine ganze Zeile, gezielt dort kürzen; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen; Listings mit Umlauten brauchen `literate`
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`)
