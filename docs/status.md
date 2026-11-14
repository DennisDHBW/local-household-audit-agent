# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14
**Phase:** 0 – Vorbereitung abgeschlossen bis auf die Punkte unten; Phase 1 startet mit M0
**Aktueller Meilenstein:** M0 – Setup
**Version:** – (erstes Tag: `v0.1.0` nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | offen | – |
| M1 | Metadaten & Ground Truth (Korpus liegt vor) | offen | – |
| M2 | Parser & JSON-Zwischenformat | offen | v0.1.0 |
| M3 | Enrichment & Cache | offen | – |
| M4 | Embedding & Retrieval (P1) + Evidence-UI | offen | – |
| M5 | Agent (P2) mit Tools | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt
- Korpus (28 PDFs) geprüft: konsistent, realistisch, Diagramme mit Zusatzinfos; ein eingebauter Fehler (Strom 2025, Arbeitspreis)
- 12-Fragen-Katalog an den echten Korpus angepasst (`concept.md`, 11.2)
- Doku, `.gitignore`, LaTeX-Vorlage (`paper/`) eingespielt; Git-Historie in sinnvolle Commits aufgeteilt

## Nächste Schritte
1. Nutzer: Projektanweisungen ersetzen, pushen, Ollama-Modelle laden (`preparation-checklist.md`)
2. M0 starten

## Offene Entscheidungen / Fragen
- Weitere eingebaute Fehler im Korpus ergänzen?
- Agent-Modell: `qwen2.5:7b` vs. `llama3.1:8b` (Smoke-Test in M0)
- Tool-Calling: natives Ollama-Tool-Calling oder Text-ReAct?
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-001: Prefill nur ca. 18 Tokens/s
- ISS-002: Claudes Shell erreicht Ollama nicht → Ollama-Befehle führt der Nutzer aus
- ISS-003: Claude kann noch nicht pushen → Nutzer pusht am Sitzungsende

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Shell-Python ist 3.10; Projekt braucht 3.13 → `uv python install 3.13` bzw. `uv sync` in M0 prüfen
