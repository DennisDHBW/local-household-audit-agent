# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (Kontrolllauf run-027 ausgewertet; Endlauf run-028 offen)
**Phase:** Phase 1 (Umsetzung M8); die Ausarbeitung wird erst nach dem Endlauf neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2
**Version:** v1.0.0 (M8 wird v2.0.0 nach dem Endlauf)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14, eingebaute Fehler 0 von 3); Zitat-Präzision falsch gemessen, jetzt je Beleg korrigiert (ISS-123) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen zu lang, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2 | Kontrolllauf run-027 (P2): 17/21 laut Metrik, 16 + 1 Grenzfall nach Handprüfung, 5/5 eingebaute Fehler, 0 Fehlalarme; zu günstig (ISS-108); Endlauf run-028 offen | – |

## Zuletzt erledigt
- Kontrolllauf run-027 ausgewertet: 16 von 21 Antworten wortgleich mit run-026; anders nur S1, S4, N1, Z2, Z3 (von Hand geprüft); N1 und S1 besser, keine Frage im Ergebnis schlechter
- ISS-121 wirkt (kein `context_limit`, längste Anfrage 2.944 Token); ISS-122 wirkt (Lücken-Rückfrage 5 → 2, 172 statt 207 s je Frage)
- ISS-125 (S1 ohne Beleg, S4 erfundene Belegnummer nach `repeat_limit`) als Befund akzeptiert; Entscheidung Nutzer: unverändert in den Endlauf
- Quality Gates: `ruff check`, `ruff format --check` grün, `pytest -m "not slow"` 443 bestanden, 1 übersprungen

## Nächstes Arbeitspaket
Auswertung des Endlaufs run-028 (B0, P1, P2 auf den zurückgehaltenen Fragen T1–T8, ca. 1 h; Nutzer startet vorher `./scripts/m8_night.sh --holdout` im Projektordner). Handprüfung aller Antworten, Vergleich mit run-025 (B0, P1) und run-027 (P2); danach keine Nachbesserung an diesen Fragen (ISS-108).

**Empfohlenes Modell:** Opus 5.5, Effort High (Auswertung der Evaluation, `ai-workflow.md` Abschnitt 4)

## Nächste Schritte
1. Endlauf run-028 auswerten (siehe oben)
2. Tag v2.0.0, Reverse-Engineering-Runde M8, Grafiken
3. Ausarbeitung neu (ISS-107; Präzisionswerte aus ISS-123 und Befunde aus ISS-125 nachziehen)

## Offene Entscheidungen / Fragen
- RAGAS für M8 ja oder nein (3 h je Lauf); bisher nicht im Nachtlauf
- Heizstrom als Zusatzheizung neben Gas-Etagenheizung (ISS-109), so vom Nutzer gewählt

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-108: Fixes aus den Entwicklungsfragen abgeleitet; aussagekräftig erst der Endlauf
- ISS-125: Mischantworten mit Lückensatz ohne Zitat-Rückfrage; Zwangsantwort nach `repeat_limit` ungeprüft (akzeptiert)
- ISS-119: Mischantworten, Lesefehler des Modells (Z2 115 statt 120 EUR, S2), ungenaue Zitate, Füllsätze, `AgentLoop.run` lang; werden nicht mehr behoben
- ISS-110/112/111: Gewinn kommt aus dem Code, Regeln und Fehler vom selben Autor, Regeln aufs Korpuslayout zugeschnitten
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten, Token-Schätzung für `qwen2.5` zu niedrig
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests in der VM-Shell: `export UV_PROJECT_ENVIRONMENT=/tmp/venv-test-$(id -u) UV_CACHE_DIR=/tmp/uv-cache-$(id -u)`, dann `uv sync --group dev --frozen` und `uv run --frozen pytest -m "not slow" -p no:cacheprovider` (Home der VM fast voll; feste `/tmp`-Pfade können einem früheren Sitzungsnutzer gehören; das `.venv` im Repo nicht anfassen). Archivverfahren (ISS-078) nur als Rückfall
- Läufe inhaltlich vergleichen (`answers-*.jsonl`: `answer`, `tool_uses`), nicht byteweise; die `p2-*.jsonl` enthalten Zeiten
- Ollama-Journal auf das Laufzeitfenster filtern (enthält auch den Vortag); Dateizeiten der VM in UTC, Journal in MEZ (ISS-120)
- B0 und P1 sind laut `m8_night.sh` seit run-025 unverändert
- Zurückgehaltene Fragen (`dataset/holdout_questions.yaml`) erst zur Auswertung von run-028 lesen, nie daran entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
