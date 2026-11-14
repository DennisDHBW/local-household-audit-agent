# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-14
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M1 – Metadaten & Ground Truth (M0 abgeschlossen)
**Version:** – (erstes Tag: `v0.1.0` nach M2)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0 | Setup (Tooling, Struktur, Config, Smoke-Test) | fertig (Reverse-Engineering-Fragen offen) | – |
| M1 | Metadaten & Ground Truth (Korpus liegt vor) | offen | – |
| M2 | Parser & JSON-Zwischenformat | offen | v0.1.0 |
| M3 | Enrichment & Cache | offen | – |
| M4 | Embedding & Retrieval (P1) + Evidence-UI | offen | – |
| M5 | Agent (P2) mit Tools | offen | v0.2.0 |
| M6 | Testmodul & Evaluation | offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M0)
- Tooling: `uv` mit Python 3.13, `ruff`, `pytest`, `scripts/check.sh`; zentrale `Settings`; Preflight für Ollama-Modelle
- Smoke-Test (`uv run python -m audit_agent.smoke`) gelaufen: RUN-000 in `evaluation-log.md`, Rohdaten in `data/eval/run-000/`
- Entschieden: Agent-Modell vorläufig `llama3.1:8b` (ADR-0004), natives Tool-Calling (ADR-0006)
- 40 Tests ohne LLM, Quality Gates grün

## Nächstes Arbeitspaket
M1 – Metadaten & Ground Truth: `documents.yaml` (Metadaten je PDF) und `ground_truth.yaml` (12-Fragen-Katalog) mit Pydantic-Modellen und Validierungstests; zwei weitere fehlerhafte Dokumente im Stil des Korpus erzeugen (Skill `pdf`), `docs/concept.md` Abschnitt 4 anpassen.

**Empfohlenes Modell:** Sonnet 5.5, Effort Medium

## Nächste Schritte
1. M1 umsetzen
2. Reverse-Engineering-Fragen zu M0 beantworten (`docs/reverse-engineering/m0-setup.md`, Abschnitte 5–7) und O-Ton für M0 nachtragen
3. M2: Parser und JSON-Zwischenformat

## Offene Entscheidungen / Fragen
- Endgültiges Agent-Modell (`llama3.1:8b` vs. `qwen2.5:7b`): Testmodul M6
- Referenzprototyp als Basis oder eigener Aufbau? UI: Streamlit + CLI (Empfehlung)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-005: Präfix-Wiederverwendung noch nicht belegt (Nachmessen in M5)
- ISS-006: Verwechslung `search_documents` / `search_tables`
- ISS-007: Modelle setzen ungefragt Metadatenfilter
- ISS-004: nur ein eingebauter Fehler im Korpus (Abhilfe in M1)
- ISS-001/002/003: langsames Prefill, kein Ollama aus Claudes Shell, Nutzer pusht selbst

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen (ISS-009), Quality Gate: `./scripts/check.sh`
- Modellaufrufe nur über `Settings` (`AUDIT_*`-Variablen), nie hartkodiert
