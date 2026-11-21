# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (M9-0 Machbarkeitsprobe fertig, RUN-029)
**Phase:** Phase 1; die Ausarbeitung wird erst nach M9 neu überarbeitet
**Aktueller Meilenstein:** M9 Agent v3 (Plan `docs/m9-plan.md` freigegeben, ADR-0022 angenommen)
**Version:** v2.0.0 (M9 wird v3.0.0)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ISS-107); Überarbeitung nach M9 | – |
| M8 | Agent v2 | fertig (run-028: P2 auf T1–T8 4 + 2 Grenzfälle von 8) | v2.0.0 |
| M9 | Agent v3 „Verstehen – Ausführen – Prüfen“ | M9-0 fertig; als Nächstes M9a | – |

## Zuletzt erledigt
- Entscheidungen: Plan und ADR-0022 freigegeben; H2 schreibt Claude (ISS-130); alle drei Modelle geladen; P2 v2 läuft im Endlauf auf H2 mit
- `scripts/m9_probe.py` + RUN-029: alle 4 Modelle halten das JSON-Schema (36/36), Rahmen 7/8 bei den drei Qwen-Modellen, 5/8 bei granite; gemeinsamer Fehler F3 (Sparte „alle“ fehlt im Entwurf)
- Cache: Transformer-Modelle bei geladenem Modell 1,8 s statt 67 s Prefill (qwen2.5:7b); getrennte Prompts je Stufe kosten nichts (Prompt-Cache des llama-servers); Hybridmodelle nutzen den Präfix nicht
- ISS-126 geklärt: Ollama entfernt Aufrufe nicht angebotener Werkzeuge stillschweigend; ISS-128 geklärt (Entladen nach jeder Frage, stand schon in ISS-057)
- H2 (24 Fragen U1–U24) in `dataset/holdout_h2.yaml`, SHA-256-Siegel, Test; Quality Gates grün (454 bestanden, 1 übersprungen)

## Nächstes Arbeitspaket
M9a Verstehen & Ausführen: `src/audit_agent/orchestrator/` mit `frame.py` (`QueryFrame` endgültig, inkl. „mehrere/alle Sparten“, Prompt mit festem Präfix, Zeitraum-Auflösung), `skills.py`, Belege E1…En, `evidence.py` (vollständig/lückenhaft/leer), Neuplanung; Unit-Tests mit aufgezeichneten Modellantworten aus RUN-029.

**Empfohlenes Modell:** Opus 5.5, Effort High (`ai-workflow.md` Abschnitt 4: Architektur; `m9-plan.md` Abschnitt 7)

## Nächste Schritte
1. M9a → M9b (Formulieren & Verifizieren) → M9c (Testmodul) → M9d (Entwicklungslauf) → M9e (optional) → M9f (Endlauf H2) → M9g (Abschluss, Reverse Engineering M8 + M9, v3.0.0)
2. Danach Ausarbeitung neu (ISS-107)

## Offene Entscheidungen / Fragen
- Modelle für M9d (höchstens zwei): Empfehlung `qwen2.5:7b` + `qwen3.5:4b` (RUN-029), Entscheidung spätestens zu Beginn von M9d
- ISS-131: Limit des Prompt-Caches (bis 8 GiB unter `MemoryMax=9G`) vor M9c klären, erst dann Modell zwischen Fragen geladen lassen
- RAGAS für M9 ja oder nein (3 h je Lauf)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-130/112/108: H2 vom selben Autor wie Code; Fehlerfälle der Prüffragen aus der Entwicklung bekannt; Siegel erkennt nur Änderungen
- ISS-131/043: Speicher bei geladenem Modell und Prompt-Cache
- ISS-110/111: Gewinn aus Code und Faktenspeicher
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- **`dataset/holdout_h2.yaml` nicht öffnen, nicht ausgeben, nicht zum Entwickeln nutzen (bis M9f).** An T1–T8 ebenfalls nicht entwickeln
- Ergebnisse der Probe: `data/eval/run-029-probe/m9-probe.json` (Rohantworten aller Modelle für Tests nutzbar), Entwurf von Schema und Prompt in `scripts/m9_probe.py`
- Datum und Frage gehören ans Ende des Prompts, der feste Teil nach vorn; Token mit Zeichen/4 geschätzt sind ca. 25 % zu niedrig
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests in der VM-Shell: `/tmp` ist voll; vorhandenes venv nutzen: `V=/tmp/venv-test-1043/bin; $V/ruff check --no-cache .; $V/ruff format --check --no-cache .; PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 $V/python -m pytest -m "not slow" -p no:cacheprovider`. Das `.venv` im Repo nicht anfassen
- `ruff format --check` prüft auch Python-Blöcke in Markdown
- Zahlen für Kapitel 5 bis M9: Entwicklungsfragen B0/P1 aus run-025, P2 aus run-027; T1–T8 aus run-028
