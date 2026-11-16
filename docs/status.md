# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-16 (M6d)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a bis M6d fertig; Rechnen und Prüfablauf M6e offen)
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
| M6 | Testmodul & Evaluation | M6a–M6d fertig (RUN-012: P2 9 von 14 richtig); M6e Rechnen/Prüfablauf offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6d)
- Ein Suchwerkzeug `search` über Text und Tabellen, Filter nur nach Sparte, `include_counterpart` für Prüffragen, leere Suche nennt den Bestand statt ungefiltert zu wiederholen (ADR-0014; ISS-006/007/051/052 gelöst)
- RUN-012 (P2, `llama3.1:8b`, 14 Fragen, 61 min): richtig nach Handprüfung 9 von 14 (RUN-010: 3), 0 von 24 Werkzeugaufrufen ungültig (13 von 37), Negativfragen 2 von 2; einzelner Lauf, Streuung nicht gemessen
- Offen geblieben: Fehler erkannt 0 von 3, Fehlalarm 1 von 3 (S5); `calculate` wurde nie aufgerufen (ISS-058); Laufzeit 263 s statt 136 s je Frage (ISS-057)
- `scripts/check_evidence.py` läuft jetzt auch für reine P2-Läufe (ISS-059)

## Nächstes Arbeitspaket
M6e – P2 rechnen und prüfen lassen (ISS-058). Plan zuerst vorlegen. Ansatzpunkte: (1) gleiche Suche mit gleichen Argumenten abfangen und dem Modell melden, (2) für Prüffragen einen festen Ablauf im Code (Sollwerte suchen, Istwerte suchen, `calculate`) oder eine Nachfrage nach `calculate` vor der Antwort, (3) bessere Suchanfragen für G1/G3/G4 (Sollzahlen standen nie im Kontext), (4) Laufzeit klären (ISS-057: Prefill gegen Generierung je Aufruf). Danach P2-Lauf auf 14 Fragen (ca. 60 min, vom Nutzer) und Vergleich mit RUN-012.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (anspruchsvoller Code: Werkzeuge, ReAct-Schleife)

## Nächste Schritte
1. M6e (Rechnen und Prüfablauf P2), danach Gegenprobe P2 mit `qwen2.5:7b` (ca. 70 min, ADR-0013)
2. P1: mehr Treffer oder gezieltere Suchanfrage (12 Retrieval-Fehlschläge), Zitierpflicht P2, Hierarchie-Boost entscheiden; Reverse-Engineering M6, Tag v1.0.0
3. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6c nachtragen

## Offene Entscheidungen / Fragen
- Welche Gegenmaßnahmen kommen in den Prototyp, welche nur als Ausblick in die Ausarbeitung (Zeit)?
- Hierarchie-Boost behalten? (ISS-027: hebt Grußformeln mit Kapitelüberschrift nach oben); Summaries für den Agenten wieder an? (ISS-035)
- Einheitenfaktor der Zahlensuche einschränken? (ISS-050, erst nach den Vergleichsläufen)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-058: P2 ruft `calculate` nie auf, Abrechnungsfehler bleiben unerkannt; ISS-057: P2-Laufzeit fast verdoppelt, Ursache offen; ISS-036 wie bisher (ISS-006/007/051/052 gelöst in M6d)
- ISS-054: `qwen2.5:7b` sagt immer „ja“, `llama3.1:8b` scheitert an `calculate` und zitiert kaum
- ISS-050/038: „richtig laut Metrik“ nur mit Handprüfung verwenden; ISS-053/047/046/045: RAGAS nur als zweite Sicht
- ISS-039: B0 sieht nur Stromdokumente (01–06); ISS-029: S4 (Diagramm) findet keine Variante
- ISS-030/031/032/033, ISS-025/027/028, ISS-010, ISS-015/016/019, ISS-022/023, ISS-001/002/003: wie bisher

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff` in main, keine Claude-Hinweise in Commits; Löschrecht für den Projektordner zu Beginn anfragen (sonst bleiben `.git/*.lock` liegen)
- Claudes Shell: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` vor `uv`-Befehlen, in neuer Sitzung zuerst `uv sync` (ISS-009); Quality Gate `./scripts/check.sh` vor jedem Commit, auch bei Daten und Skripten (ISS-056), nie hinter eine Pipe vor `&&` (ISS-048)
- Evaluation: `generate` → `score` (ohne Ollama) → `ragas` (`uv run --group ragas …`); ein Lauf = ein Antwortmodell; für Vergleichsläufe nur P2: `generate --variants p2 --all`
- Nach jedem Lauf `uv run python scripts/check_evidence.py --run-id <id>` und die Antworten von Hand lesen; Journal sichern (`truncat|oom`)
- Die Zeichenkette `toolbench_rapidapi_key` in `run-011` ist vom Modell erfunden und bleibt in den Rohdaten (ISS-054); meldet GitHub sie beim Push, ist das ein Fehlalarm
- Reihenfolge nach neuer Ingestion: Ingestion → Enrichment (Cache) → `retrieval index`; `data/processed/`, `.cache/`, `data/vectors/` sind nicht versioniert
