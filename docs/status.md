# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (run-024-smoke und Nachtlauf run-025 ausgewertet; Fixes an der Schleife und den Argumenten, ADR-0021, ISS-117 bis ISS-120)
**Phase:** Phase 1 (Umsetzung M8); die Ausarbeitung wird erst nach besseren Ergebnissen neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2
**Version:** v1.0.0 (M8 wird v2.0.0 nach dem Endlauf)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14, eingebaute Fehler 0 von 3) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen zu lang, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2 | run-025: P2 9/21 (P1 6, B0 4), 5/5 eingebaute Fehler, 0 Fehlalarme, Tool-Wahl 19/21; Fixes nach run-025 offline getestet (437 Tests); run-026 und Endlauf run-027 offen | – |

## Zuletzt erledigt
- Handprüfung run-025: 8 von 12 P2-Fehlschlägen lagen in der Steuerung der Schleife, nicht im Retrieval (41/49 Sollfakten im Kontext, 27 in der Antwort)
- ADR-0021: Schritt-Text bereinigt, Rückfall auf die frühere Antwort, Rückfragen `steps`/`empty`/`language`, `REPEAT_LIMIT`, Lücke erst nach Suche, Argumente (Jahr, Fernwärme, Umfang Übersicht/Grafik)
- Tool-Wahl-Kennzahl für v2 korrigiert (ISS-118); `scripts/analyze_agentics.py` (Kennzahlen Agentik, `agentics.json`)

## Nächstes Arbeitspaket
Nutzer startet `./scripts/m8_night.sh` (run-026: P2 auf den 21 Entwicklungsfragen, ca. 80 min). Danach run-026 auswerten (Handprüfung, `agentics.json`, Vergleich mit run-025) und entscheiden, ob ISS-119 noch angegangen wird; dann Endlauf run-027 mit `--holdout`.

**Empfohlenes Modell:** Opus 5.5, Effort High (Auswertung der Evaluation, `ai-workflow.md` Abschnitt 4)

## Nächste Schritte
1. run-026 auswerten; Nachbesserungen nur an Entwicklungsfragen
2. Endlauf `./scripts/m8_night.sh --holdout` (run-027: B0, P1, P2 auf T1–T8), danach keine Nachbesserung mehr an diesen Fragen (ISS-108)
3. Tag v2.0.0, Reverse-Engineering-Runde M8, Grafiken für die Ausarbeitung, dann Ausarbeitung neu (ISS-107)

## Offene Entscheidungen / Fragen
- B0 im Endlauf: Budget unverändert lassen (vergleichbar mit run-025) oder für `qwen2.5` kürzen (ISS-120); Empfehlung: unverändert
- RAGAS für M8 ja oder nein (3 h je Lauf); bisher nicht im Nachtlauf
- Heizstrom als Zusatzheizung neben Gas-Etagenheizung (ISS-109), so vom Nutzer gewählt

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-108: Fixes aus den Entwicklungsfragen abgeleitet, run-026 wird zu günstig; aussagekräftig erst run-027
- ISS-119: Mischantworten, „stimmt“ ohne Zahlen, `plan` selten, `AgentLoop.run` lang
- ISS-110/112/111: Gewinn kommt aus dem Code, Regeln und Fehler vom selben Autor, Regeln aufs Korpuslayout zugeschnitten
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten, Token-Schätzung für `qwen2.5` zu niedrig
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests: Repo als Archiv nach `.cache/` packen, mit `device_stage_files` in die Cloud-Umgebung holen, dort `uv sync --group dev` und `uv run pytest -m "not slow"`; Änderungen als Archiv mit Prüfsummen zurückspielen (ISS-078)
- Dateizeiten der VM stehen in UTC, das Ollama-Journal in MEZ (ISS-120)
- Auswertung: `uv run python scripts/analyze_agentics.py --run-id run-026` (schreibt der Nachtlauf schon mit)
- Zurückgehaltene Fragen (`dataset/holdout_questions.yaml`) nicht lesen, um daran zu entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
