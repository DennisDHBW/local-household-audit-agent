# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-20 (Smoke-Test run-023 ausgewertet; Argument-Reparatur, Kurzfassung, Werkzeugauswahl nach Fragetyp, Planprüfung, Plausibilitätsregeln, Urteilsprüfung, Trockenlauf; ADR-0020, ISS-116)
**Phase:** zurück in Phase 1 (Umsetzung M8) auf Wunsch des Nutzers; die Ausarbeitung wird erst nach besseren Ergebnissen neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2
**Version:** v1.0.0 (M8 wird v2.0.0 nach dem Nachtlauf)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14, eingebaute Fehler 0 von 3) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand mit eingearbeiteten Befunden (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen über 8 Seiten, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2: Heizstrom HT/NT, Faktenspeicher, `check_bill`, Plan, Selbstprüfung, Übersicht/Grafik, Chat, Testmodul mit zurückgehaltenen Fragen | Code fertig und offline getestet (402 Tests grün, RUN-022: 5 von 5 eingebauten Fehlern, 0 Fehlalarme); Smoke-Test und Nachtlauf mit Ollama offen | – |

## Zuletzt erledigt
- Ausarbeitung: Befunde (55/60, Herkunft `final_score`, Jargon, Pointen, 7B-Schluss, Test = Entwicklung) eingearbeitet, Branch `docs/paper-findings`
- M8 (Branch `feat/m8-agent-v2`): Dok. 31–35 (Heizstrom-Vertrag, -Preisanpassung, -Rechnungen 2024/2025 mit E4, Wasser 2026 mit E5), `tariff_kind`; Faktenspeicher und Prüfregeln (ADR-0018); Werkzeugsatz v2 mit `plan`, `get_facts`, `check_bill`, `make_overview`, `make_chart`, Selbstprüfung, max. 10 Aufrufe, Chat-UI mit Verlauf (ADR-0019); 21 Entwicklungsfragen, 8 zurückgehaltene Fragen T1–T8, Kennzahlen für Artefakte und Agentik; Skripte `m8_prepare.sh`, `m8_night.sh`

## Nächstes Arbeitspaket
Nutzer startet über Nacht: Trockenlauf (`scripts/dry_run.py`, ohne Ollama), Fakten neu bauen, Smoke-Test run-024-smoke (H2, V1, W1, G2, Z2), danach Nachtlauf run-025 (`m8_night.sh`, 21 Fragen, B0/P1/P2). Danach: beide Läufe auswerten (Handprüfung, Kennzahlen Agentik, Grafiken), evaluation-log, Nachbesserungen nur an Entwicklungsfragen; dann Endlauf run-026 mit `--holdout`.

**Empfohlenes Modell:** Opus 5.5, Effort High (Auswertung der Evaluation und Fehlersuche; laut `ai-workflow.md`, Abschnitt 4)

## Nächste Schritte
1. run-024-smoke und Nachtlauf run-025 auswerten (ISS-113/114)
2. Nachbesserungen nur an Entwicklungsfragen, ggf. zweiter Nachtlauf
3. Erst danach Endlauf mit zurückgehaltenen Fragen: `./scripts/m8_night.sh --holdout` (run-026), keine Nachbesserung mehr an Hand dieser Fragen (ISS-108)
4. Tag v2.0.0, Reverse-Engineering-Runde M8, dann Ausarbeitung neu (Architekturabbildung, Ausblick, Seitenbudget, ISS-107)

## Offene Entscheidungen / Fragen
- Heizstrom als Zusatzheizung neben Gas-Etagenheizung (ISS-109), so vom Nutzer gewählt (Nachtspeicher, HT/NT)
- RAGAS für M8 ja oder nein (3 h je Lauf); bisher nicht im Nachtlauf

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-113: v2 nur mit gescripteten Antworten getestet; ISS-110: Gewinn kommt aus Code, nicht aus dem Modell; ISS-112: Regeln und eingebaute Fehler vom selben Autor (zirkulär); ISS-111: Regeln auf Korpuslayout zugeschnitten
- ISS-108: alte Ergebnisse auf Entwicklungsfragen (eher zu günstig); ISS-107: Ausarbeitung ca. 12 Zeilen zu lang
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen
- Ältere Punkte wie bisher (ISS-078: `pytest` läuft nicht in Claudes Shell, Tests laufen in der Cloud-Umgebung)

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests: Repo als Archiv in die Cloud-Umgebung holen (`device_stage_files`), dort `uv sync --group dev` und `uv run pytest -m "not slow"`; Ingestion und `python -m audit_agent.facts audit` laufen dort ohne Ollama. PDFs neu erzeugen: `uv run --with weasyprint python scripts/generate_m8_documents.py` (Pango nötig)
- Zurückgehaltene Fragen (`dataset/holdout_questions.yaml`) nicht lesen, um daran zu entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089): Archiv `paper`, Cloud-Umgebung mit `texlive-lang-german texlive-bibtex-extra texlive-plain-generic texlive-latex-extra biber latexmk`
