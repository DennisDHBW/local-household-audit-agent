# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (Nachtlauf run-026 ausgewertet; ISS-121 bis ISS-123, Entscheidung: Fix-Paket vor dem Endlauf)
**Phase:** Phase 1 (Umsetzung M8); die Ausarbeitung wird erst nach dem Endlauf neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2
**Version:** v1.0.0 (M8 wird v2.0.0 nach dem Endlauf)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14, eingebaute Fehler 0 von 3); Zitat-Präzision falsch gemessen (ISS-123) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen zu lang, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2 | run-026: P2 15/21 (run-025: 9/21), 42/49 Fakten, 5/5 eingebaute Fehler, 0 Fehlalarme; zu günstig (ISS-108); Fix-Paket, Kontrolllauf und Endlauf offen | – |

## Zuletzt erledigt
- run-026 von Hand geprüft (alle 21 Antworten und Schrittprotokolle): 6 Fragen besser, keine schlechter; Hand 15/21 (Z1 richtig, Z3 Mischantwort); 47/49 Sollfakten im Kontext
- Befunde: Lücken-Rückfrage 5-mal, 0-mal geholfen, 2-mal verschlechtert (ISS-122); `context_limit` zu früh, weil alle Werkzeugschemas gezählt werden (ISS-121); Zitat-Präzision mischt Seiten und Belege, seit M6 zu niedrig (ISS-123)
- Entscheidungen des Nutzers: Fix-Paket vor dem Endlauf; B0-Budget im Endlauf unverändert (ISS-120)

## Nächstes Arbeitspaket
Fix-Paket vor dem Endlauf: (1) Zitat-Präzision je Beleg zählen, Test dazu, alle Läufe offline neu bewerten (ISS-123); (2) Kontextschätzung aus den angebotenen Werkzeugschemas (ISS-121); (3) Lücken-Rückfrage nur bei reiner Lückenantwort und ohne Korpus-Hinweise (ISS-122). Danach startet der Nutzer den Kontrolllauf `./scripts/m8_night.sh` (run-027, nur P2, ca. 75 min).

**Empfohlenes Modell:** Sonnet 5.5, Effort High (ReAct-Schleife und Testmodul, `ai-workflow.md` Abschnitt 4)

## Nächste Schritte
1. Fix-Paket, Kontrolllauf run-027 auswerten (nur prüfen, ob etwas schlechter wurde; keine weitere Nachbesserung an den Entwicklungsfragen)
2. Endlauf `./scripts/m8_night.sh --holdout` (run-028: B0, P1, P2 auf T1–T8), danach keine Nachbesserung mehr an diesen Fragen (ISS-108)
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
- Tests: Repo als Archiv nach `.cache/` packen, mit `device_stage_files` in die Cloud-Umgebung holen, dort `uv sync --group dev` und `uv run pytest -m "not slow"`; Änderungen als Archiv mit Prüfsummen zurückspielen (ISS-078)
- Sollwerte nach dem Präzisions-Fix: Spalte „je Beleg“ der Tabelle in ISS-123 (zum Abgleich nach dem Neubewerten)
- Lücken-Rückfrage: `is_gap_answer`, `drop_trailing_gap`, `RETRY_BEFORE_GAP_MESSAGE_V2` (`prompts.py`), Bedingung in `AgentLoop.run` (`loop.py`); Kontext: `_spec_tokens`, `_is_context_full`
- Dateizeiten der VM stehen in UTC, das Ollama-Journal in MEZ (ISS-120)
- Zurückgehaltene Fragen (`dataset/holdout_questions.yaml`) nicht lesen, um daran zu entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
