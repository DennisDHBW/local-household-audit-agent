# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (M8 abgeschlossen, Plan M9 vorgelegt)
**Phase:** Phase 1; die Ausarbeitung wird erst nach M9 neu überarbeitet
**Aktueller Meilenstein:** M9 Agent v3 (Plan `docs/m9-plan.md`, wartet auf Freigabe)
**Version:** v2.0.0 (M9 wird v3.0.0)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ISS-107); Überarbeitung nach M9 | – |
| M8 | Agent v2 | fertig: run-028 auf T1–T8 P2 4 + 2 Grenzfälle von 8 (Entwicklung 76 %), P1 2 + 1, B0 1; Abgleich `reverse-engineering/m8-abgleich-requirements.md` | v2.0.0 |
| M9 | Agent v3 „Verstehen – Ausführen – Prüfen“ | geplant (ADR-0022 vorgeschlagen) | – |

## Zuletzt erledigt
- Recherche (ca. 20 Paper/Preprints) und Plan M9: P3 als Zustandsautomat mit JSON-Schemas (Ollama `format`), deterministischen Skills, Evidenzprüfung, Neuplanung, Belegen per `enum`, Verifikation und Renderer; P2 v2 bleibt als Vergleich
- Neue Evaluation geplant: H2 (20–24 Fragen von Dennis, versiegelt), Umformulierungen, Wilson-Intervalle, gepaarter Vergleich, Ziele und Stoppregel vorab
- ISS-128 (Präfix-Cache greift zwischen P2-Fragen nicht, ca. 80 s je Frage), ISS-129; Quality Gates grün (443 bestanden, 1 übersprungen)

## Nächstes Arbeitspaket
Zuerst Freigabe des Plans `docs/m9-plan.md` und die drei Entscheidungen aus Abschnitt 10 einholen (falls noch nicht im Chat gegeben). Dann M9-0 Machbarkeitsprobe: Skript `scripts/m9_probe.py` (je Kandidat Schema-Treue mit `format` ohne Thinking, Geschwindigkeit, Cache-Probe, 8 neutrale Fragen für den Auftragsrahmen, ein Aufruf zu ISS-126) und ein Befehl für Dennis.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (`ai-workflow.md` Abschnitt 4: anspruchsvoller Code / Testmodul)

## Nächste Schritte
1. M9-0 → M9a (Verstehen & Ausführen) → M9b (Formulieren & Verifizieren) → M9c (Testmodul) → M9d (Entwicklungslauf) → M9e (optional) → M9f (Endlauf H2) → M9g (Abschluss, Reverse Engineering M8 + M9, v3.0.0)
2. Danach Ausarbeitung neu (ISS-107)

## Offene Entscheidungen / Fragen
- Freigabe von `docs/m9-plan.md` / ADR-0022
- H2-Fragen: Dennis schreibt (empfohlen) oder Claude versiegelt
- Modelle für M9-0 laden: `qwen3:8b`, `qwen3.5:4b`, `granite4:tiny-h` (ca. 12–14 GB)
- P2 v2 im Endlauf mitlaufen lassen (empfohlen)
- RAGAS für M9 ja oder nein (3 h je Lauf)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-126/127/125: Wortlisten, Antwortzwang, Zeitraum-Reparatur, Mischantworten in v2 → Anlass für M9
- ISS-128: Prefill dominiert, Cache zwischen Fragen ungenutzt
- ISS-108/110/111/112: Entwicklungszahlen zu günstig, Gewinn aus Code, Regeln auf Korpus zugeschnitten, Fragen und Regeln vom selben Autor
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests in der VM-Shell: `export UV_PROJECT_ENVIRONMENT=/tmp/venv-test-$(id -u) UV_CACHE_DIR=/tmp/uv-cache-$(id -u) UV_PYTHON_INSTALL_DIR=/tmp/uv-python-$(id -u)`, dann `uv sync --group dev --frozen` und `uv run --frozen pytest -m "not slow" -p no:cacheprovider`. Ist `/tmp` voll (2026-11-21): vorhandenes venv einer früheren Sitzung nutzen, z. B. `V=/tmp/venv-test-1043/bin; $V/ruff check --no-cache .; PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 $V/python -m pytest -m "not slow" -p no:cacheprovider`. Das `.venv` im Repo nicht anfassen
- `ruff format --check` prüft auch Python-Blöcke in Markdown
- An T1–T8 nicht mehr entwickeln; H2 erst nach dem Code-Freeze öffnen
- Zahlen für Kapitel 5 bis M9: Entwicklungsfragen B0/P1 aus run-025, P2 aus run-027; T1–T8 aus run-028
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
