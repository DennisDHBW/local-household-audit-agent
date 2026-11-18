# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-18 (Kapitel 5 entworfen)
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
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | läuft: Kapitel 1–5 entworfen (ca. 1,3 / 1,3 / 1,6 / 1,25 / 1,45 S.), Kapitel 6 als Nächstes | – |

## Zuletzt erledigt (Sitzung: Kapitel 5)
- Kapitel 5 entworfen, ca. 1,45 Seiten (im Budget): Testmodul (`generate`/`score`/`ragas`, 382 Unit-Tests), Testdaten, eigene Metriken mit Handprüfung und Belegabgleich, RAGAS als zweite Sicht mit Grenzen, Ergebnistabelle B0/P1/P2 (Endfassung `qwen2.5:7b`), Qualitätsaussage, Fehleranalyse, Grenzen
- Qualitätsaussage: P1 8, P2 6, B0 3 von 14; Fragen ohne Prüfung P1/P2 je 5 von 8; eingebaute Fehler 0 von 3, Fehlalarm P2/G2
- evaluation-log: Nachtrag Ergebnisse je Fragekategorie; Glossar: „knapp als richtig gewertet“, „Frage ohne Prüfung“; ISS-094 (Handprüfung durch Claude), ISS-093 ergänzt

## Nächstes Arbeitspaket
Kapitel 6 „Reflexion und Ausblick“ (`paper/content/chapter/06-reflection/main.tex`, Budget 0,75 Seiten, ca. 280 Wörter) mit dem Skill audit-paper-writer. Material mit Fundstellen (Kandidaten in `paper-questions.md`, Kapitel 5 „Weggelassen“: Verlauf P2 3 → 9 → 6, G4 in RUN-014; ADR-0013/0015/0016, ISS-058/066/067/070/071/074/076/088/094; Begriffe ReAct, Modular RAG, Self-RAG für den Literaturbezug ohne Literaturverzeichnis; nur belegte Erkenntnisse, ISS-087) und Gliederung mit Wortzahl zusammen mit dem Plan vorlegen, nach dem OK schreiben, messen, 3–5 Fragen in `paper-questions.md`, mergen (Branch `docs/paper-06-reflection`).

**Empfohlenes Modell:** Opus 5.5, Effort High (Ausarbeitung schreiben; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. Kapitel 6 (Budget 0,75 S. laut `concept.md` §14; Hochrechnung ca. 7,7 von 8 Seiten, Puffer ca. 0,35)
2. Danach ein Chat Überarbeitung: Nutzer liest alle Kapitel, beantwortet `paper-questions.md`, Claude arbeitet Markierungen und Antworten ein
3. Endkontrolle einmalig mit Opus 5.5 / Max (Checkliste `writing-guide.md` Abschnitt 4, `requirements.md` Abschnitt 11)
4. Nur bei Zeit: ISS-080/081/086/088

## Offene Entscheidungen / Fragen
- Bearbeitungszeitraum auf dem Titelblatt: „November 2026“ ok oder gibt die DHBW einen Zeitraum vor?
- Reflexion ohne O-Ton: persönlichen Teil vor der Abgabe selbst lesen und ergänzen (ISS-087)
- KI-Hinweis: Soll die Ausarbeitung nennen, dass Claude die Handprüfung der Antworten gemacht hat? Vorher Stichproben selbst lesen (ISS-094)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-087: kein O-Ton; ISS-084/085: Verständnisfragen M0–M6 nicht selbst beantwortet. Reflexion droht generisch, Verständnis ist bewertungsrelevant
- ISS-094: Hauptergebnis von Kapitel 5 beruht auf der Handprüfung durch Claude, vom Nutzer nicht gegengelesen
- ISS-086/053/047/045: RAGAS nur als zweite Sicht; Context Recall misst gegen Referenzsätze, Faithfulness misst Belegtreue, nicht Richtigkeit
- ISS-074/076: G3 ohne Vorjahres-Gegenstück, leere Antwort nach Rückfrage (G1); ISS-079: Abbruch von RUN-021 ungeklärt
- ISS-088: Rechtsberatungs-Hinweis aus dem Konzept nicht umgesetzt (in Kapitel 1 genannt)
- ISS-090/092/093: Seitenbudget knapp (Kapitel 1–5: 1,3 / 1,3 / 1,6 / 1,25 / 1,45 S.); Kapitel 6 darf 0,75 S. nicht überschreiten; Erstentwürfe waren bisher immer 20–30 % zu lang (Kapitel 5: 1,75 S. im ersten Build)
- ISS-080/081/083, ISS-078/075, ISS-070/071/068, ISS-066/067 (0 von 3 eingebauten Fehlern erkannt), ISS-062, ISS-057, ISS-054, ISS-050/038, ISS-039, ISS-029 und ältere: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket (`docs/paper-<kapitel>`), `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen und nach jedem Verbindungsabbruch neu
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“ eintragen
- Ausarbeitung: Skill audit-paper-writer, Regeln aus `writing-guide.md`; Zahlen exakt wie in `evaluation-log.md`; `\todo{...}` (rot) nur für Angaben, die sich aus dem Material nicht belegen lassen; Kapitel ohne Unterabschnitte, solange das Budget unter 1,5 Seiten liegt; Kapitel 5 enthält schon Qualitätsaussage, RAGAS-Grenzen, Fehleranalyse und Grenzen der Messung (14 Fragen, Einzelläufe, Handprüfung nicht gegengelesen); Kapitel 6 verweist darauf, statt zu wiederholen, und reflektiert: Annahme aus Kapitel 1 (Prüffragen brauchen einen Agenten) nicht bestätigt, beste gemessene P2-Fassung (RUN-012) ist nicht die Endfassung, Rückfragen und Prüfablauf ohne Gewinn, Engpass Lesen/Vergleichen bei kleinen Modellen; Begriff „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen
- LaTeX (ISS-089): In Claudes Shell fehlen `babel-german` und `biblatex`. Bauen: `tar czf .paper-build.tgz paper` im Projektordner, `device_stage_files`, in der Cloud-Umgebung `apt-get update && apt-get install -y texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber`, dann `latexmk -pdf main.tex` in einem neuen Ordner; Archiv danach löschen. Neuen Build-Ordner je Lauf anlegen (Löschen des Arbeitsordners wird blockiert). Ca. 380–400 Wörter je Seite, Tabelle plus Listing ca. 0,4 S.; Wortzahl vor dem ersten Build zählen, die ersten Entwürfe waren immer 20–30 % zu lang (Kapitel 4: ca. 1,25 S. bei gut 450 Wörtern plus Formel); kurze Absatzenden kosten eine ganze Zeile, gezielt dort kürzen; Seitenzahl mit `pdftotext -bbox-layout` von Überschrift bis Überschrift messen; Listings mit Umlauten brauchen `literate`; Tabelle mit zehn Zeilen und Caption ca. 0,3 S. (Kapitel 5); beim Messen die Einträge im Inhaltsverzeichnis überspringen
- Claudes Shell: `.venv/bin/ruff` läuft, `pytest` nicht (ISS-078); bei reinen Doku-/LaTeX-Änderungen reicht ruff, sonst Quality Gate als `./scripts/check.sh > <log> 2>&1` an den Nutzer. Dateien im Projektordner über `device_bash` bearbeiten (kleine Python-Ersetzung mit `assert`)
