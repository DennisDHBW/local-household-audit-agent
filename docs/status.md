# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-15 (M6b-1, Nachbesserung OOM)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a, M6b-1 fertig; Nachtläufe und Auswertung offen)
**Version:** v0.2.0 (nach M5)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (30 PDFs, 3 eingebaute Fehler) | fertig (Reverse-Engineering-Fragen offen) | – |
| M2 | Parser & JSON-Zwischenformat | fertig (Reverse-Engineering-Runde läuft) | v0.1.0 |
| M3 | Enrichment & Cache | fertig (Reverse-Engineering-Fragen offen) | – |
| M4 | Embedding & Retrieval (P1) + Evidenz (CLI) | fertig (Reverse-Engineering-Fragen offen) | – |
| M5 | Agent (P2) mit Tools + Streamlit-Evidenz | fertig (Reverse-Engineering Runde 1 vorbereitet) | v0.2.0 |
| M6 | Testmodul & Evaluation | M6a + M6b-1 fertig (14 Fragen, RAGAS); Nachtläufe 2 Modelle + Auswertung offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6b-1)
- Katalog 14 Fragen: G3 (E2, z-Zahl Gas 2026) und G4 (E3, Wohnfläche Nebenkosten 2026); `Question.planted_error`, jeder Fehler hat genau eine Frage (ISS-040 gelöst)
- `VariantAnswer.contexts`: Belegtexte, wie das Modell sie sah (B0 Seiten, P1 Treffer, P2 Tool-Beobachtungen)
- RAGAS 0.4.4 (Gruppe `ragas`): Befehl `ragas`, Faithfulness + Context Recall, Bewerter `audit-judge` (= `qwen2.5:7b`, `num_ctx` 8192, Modelfile), keine stille Kürzung (zu lange Prompts → „zu lang“), fortsetzbar, Telemetrie aus (ISS-044); ADR-0012; 270 Tests
- RUN-009 (G3/G4, `llama3.1:8b`): alle Varianten 0/2; P2 urteilt bei G3 „korrekt“, eigene Filter schließen Vorjahr/Mietvertrag aus (3/3). RAGAS läuft: P2 Faithfulness 1,00 trotz falscher Antworten, Context Recall überall 0; B0 immer „zu lang“; `max_tokens` auf 2048 erhöht (ISS-045 bis ISS-047)

## Nächstes Arbeitspaket
M6c – Nachtläufe auswerten. **Vorher (vom Nutzer, über Nacht, ca. 7–8 h):** den Nachtlauf-Befehl unten ausführen. Dann in der Sitzung: Ergebnisse von RUN-010 (`llama3.1:8b`) und RUN-011 (`qwen2.5:7b`) lesen, RAGAS-Stichproben von Hand prüfen, evaluation-log, Fehleranalyse je Fehlschlag (Parser/Retrieval/Tool-Wahl/Synthese), Agent-Modell entscheiden. Zuerst Plan vorlegen.

**Empfohlenes Modell:** Opus 5.5, Effort High (Auswertung der Evaluation)

Nachtlauf-Befehl:
```bash
/home/usr0/PycharmProjects/local-household-audit-agent/scripts/night_eval.sh
```
Wartet vor jedem Schritt auf Ollama und wiederholt einen abgebrochenen Schritt einmal; erneuter Aufruf setzt fort. Stand 15.11.: RUN-010 hat B0 und P1 mit 14 Fragen, P2 mit 13 (Abbruch durch OOM bei Z3, ISS-043); RUN-011 und RAGAS leer.

## Nächste Schritte
1. Nachtlauf, dann M6c (Auswertung)
2. Gegenmaßnahmen messen (Filter durch Code ISS-007, gemeinsames Suchtool ISS-006, Zitierpflicht P2, P1-Suchanfrage), Hierarchie-Boost entscheiden; Reverse-Engineering M6, Tag v1.0.0
3. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M5 nachtragen

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): nach M6c
- Gegenmaßnahmen für ISS-006/007/036 erst nach dem 14-Fragen-Lauf wählen
- Hierarchie-Boost behalten? (ISS-027); Summaries für den Agenten wieder an? (ISS-035)
- Wie RAGAS in der Ausarbeitung gedeutet wird: Belegtreue/-abdeckung, nicht Richtigkeit (ISS-047)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-036/006/007: Agent wählt Tools und Filter unzuverlässig (G1, G3, G4)
- ISS-043: OOM-Kill in P2 trotz Entladen je Variante (RUN-010); jetzt Entladen je Frage, beobachten
- ISS-045/046/047: RAGAS-Bewerter bewertet beim qwen-Lauf sich selbst, B0 nicht bewertbar, Context Recall bei Prüffragen systematisch niedrig
- ISS-038: eigene Metriken sind Heuristiken; ISS-039: B0 sieht nur Stromdokumente (01–06)
- ISS-030/031/032/033, ISS-025/027/028/029, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009); Quality Gate `./scripts/check.sh` nie hinter eine Pipe vor `&&` (ISS-048)
- Evaluation: `generate` → `score` (ohne Ollama) → `ragas` (`uv run --group ragas …`, Bewerter einmalig mit `ollama create audit-judge -f scripts/audit-judge.Modelfile`); `--retry-errors` wiederholt RAGAS-Fehlschläge; ein Lauf = ein Antwortmodell
- Nach jedem Lauf Journal sichern (`truncat|oom`); Token-Schätzung 2,4 Zeichen/Token (`CHARS_PER_TOKEN`)
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
