# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (Fix-Paket ISS-121 bis ISS-123 umgesetzt und getestet; Kontrolllauf run-027 offen)
**Phase:** Phase 1 (Umsetzung M8); die Ausarbeitung wird erst nach dem Endlauf neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2
**Version:** v1.0.0 (M8 wird v2.0.0 nach dem Endlauf)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14, eingebaute Fehler 0 von 3); Zitat-Präzision falsch gemessen, jetzt je Beleg korrigiert (ISS-123) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen zu lang, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2 | run-026: P2 15/21, 5/5 eingebaute Fehler, 0 Fehlalarme; zu günstig (ISS-108); Fix-Paket fertig (ISS-121 bis ISS-123), Kontrolllauf run-027 und Endlauf run-028 offen | – |

## Zuletzt erledigt
- ISS-123: Quellen-Präzision je Beleg (`score_answer`, Test); run-020, 021, 025, 026 offline neu bewertet (z. B. run-026 P2 55/72 = 76 %, run-025 P2 34/36 = 94 %)
- ISS-121: `_is_context_full` schätzt die Schemas der angebotenen Werkzeuge, nicht aller 8 (Test schlägt auf altem Code fehl)
- ISS-122: v2-Lückenrückfrage nur bei reiner Lückenantwort (`is_pure_gap_answer`), neuer Text ohne Korpus-Hinweise; Nachtrag in ADR-0021
- `m8_night.sh`: Standardlauf run-027, `--holdout` run-028 (ISS-124; vorher hätte es run-026 fortgesetzt)
- Quality Gates: `ruff check`, `ruff format --check` grün, `pytest -m "not slow"` 443 bestanden, 1 übersprungen

## Nächstes Arbeitspaket
Auswertung des Kontrolllaufs run-027 (P2, 21 Entwicklungsfragen, ca. 75 min; Nutzer startet `./scripts/m8_night.sh` im Projektordner). Nur prüfen, ob etwas schlechter wurde als in run-026 (Handprüfung der Fragen mit anderem Ergebnis, Lückenrückfragen, `context_limit`, Zitat-Präzision je Beleg); keine weitere Nachbesserung an den Entwicklungsfragen.

**Empfohlenes Modell:** Opus 5.5, Effort High (Auswertung der Evaluation, `ai-workflow.md` Abschnitt 4)

## Nächste Schritte
1. Kontrolllauf run-027 auswerten (siehe oben)
2. Endlauf `./scripts/m8_night.sh --holdout` (run-028: B0, P1, P2 auf T1–T8; das Skript nimmt die Nummer selbst), danach keine Nachbesserung mehr an diesen Fragen (ISS-108)
3. Tag v2.0.0, Reverse-Engineering-Runde M8, Grafiken, dann Ausarbeitung neu (ISS-107, Präzisionswerte aus ISS-123 nachziehen)

## Offene Entscheidungen / Fragen
- RAGAS für M8 ja oder nein (3 h je Lauf); bisher nicht im Nachtlauf
- Heizstrom als Zusatzheizung neben Gas-Etagenheizung (ISS-109), so vom Nutzer gewählt

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-108: Fixes aus den Entwicklungsfragen abgeleitet; aussagekräftig erst der Endlauf
- ISS-119: Mischantworten, Lesefehler des Modells (Z2 115 statt 120 EUR, S2), ungenaue Zitate, Füllsätze, `AgentLoop.run` lang; werden nicht mehr behoben
- ISS-110/112/111: Gewinn kommt aus dem Code, Regeln und Fehler vom selben Autor, Regeln aufs Korpuslayout zugeschnitten
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten, Token-Schätzung für `qwen2.5` zu niedrig
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests laufen direkt in der VM-Shell: `export UV_PROJECT_ENVIRONMENT=/tmp/venv-test UV_CACHE_DIR=/tmp/uv-cache`, dann `uv sync --group dev --frozen` und `uv run --frozen pytest -m "not slow"` (Home der VM hat nur ca. 100 MB frei, deshalb `/tmp`; das `.venv` im Repo nicht anfassen). Das Archivverfahren (ISS-078) nur als Rückfall
- Präzisions-Fix abgeglichen: Neubewertung stimmt mit der Spalte „je Beleg“ in ISS-123 überein; Werte in `evaluation-log.md` (RUN-026, Neubewertung)
- Lücken-Rückfrage: `is_pure_gap_answer`, `drop_trailing_gap`, `RETRY_BEFORE_GAP_MESSAGE_V2` (`prompts.py`), Bedingung in `AgentLoop.run` (`loop.py`); Kontext: `_is_context_full` (rechnet mit `_active_specs`)
- Dateizeiten der VM stehen in UTC, das Ollama-Journal in MEZ (ISS-120)
- Zurückgehaltene Fragen (`dataset/holdout_questions.yaml`) nicht lesen, um daran zu entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
