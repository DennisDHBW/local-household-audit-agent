# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-15 (M6c)
**Phase:** 1 – Umsetzung
**Aktueller Meilenstein:** M6 – Testmodul & Evaluation (M6a, M6b, M6c fertig; Gegenmaßnahmen M6d offen)
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
| M6 | Testmodul & Evaluation | M6a–M6c fertig (Nachtläufe ausgewertet); M6d Gegenmaßnahmen offen | v1.0.0 |
| M7 | Ausarbeitung (Phase 2, Vorlage unter `paper/`) | offen | – |

## Zuletzt erledigt (M6c)
- RUN-010 (`llama3.1:8b`) und RUN-011 (`qwen2.5:7b`) vollständig, 8,5 h ohne OOM und ohne Kürzung (ISS-043 gelöst)
- Alle 84 Antworten gelesen. Richtig nach Handprüfung (B0 / P1 / P2): llama 5 / 5 / 3, qwen 3 / 5 / 2 von 14; kein eingebauter Fehler erkannt
- Fehleranalyse je Fehlschlag (61): Kontextbudget 14, Retrieval 12, Filter 10, Tool-Wahl 8, Argumente 1, Synthese 16, Parser 0. P2 ist schlechter als P1, 18 von 23 P2-Fehlschlägen kommen aus Werkzeugentwurf und Filtern
- `scripts/check_evidence.py` (`evidence.json`): standen die Sollfakten im Kontext?
- RAGAS-Stichprobe (12 Antworten): im Einzelfall unzuverlässig (ISS-053); Metrik bei „ja“-Urteilen zu großzügig (ISS-050)
- ADR-0013: Agent-Modell `llama3.1:8b` (akzeptiert), `qwen2.5:7b` bleibt Bewerter

## Nächstes Arbeitspaket
M6d – Gegenmaßnahmen für P2 bauen und messen. Reihenfolge nach Wirkung: (1) Filter nicht mehr dem Modell überlassen bzw. bei Prüffragen Vergleichsdokumente mitsuchen (ISS-007), (2) ein Suchwerkzeug über Text und Tabellen, danach `expected_tools` im Katalog anpassen (ISS-006/052), (3) leere gefilterte Suche meldet „keine Treffer“ statt ungefiltert zu wiederholen (ISS-051). Danach ein P2-Lauf mit `llama3.1:8b` auf 14 Fragen (ca. 35 min, vom Nutzer) und Vergleich mit RUN-010. Zuerst Plan vorlegen, auch zur Frage, ob (1) bis (3) in ein Paket passen.

**Empfohlenes Modell:** Sonnet 5.5, Effort High (anspruchsvoller Code: Werkzeuge, ReAct-Schleife)

## Nächste Schritte
1. M6d (Gegenmaßnahmen P2), danach Gegenprobe P2 mit `qwen2.5:7b` (ca. 70 min, ADR-0013)
2. P1: mehr Treffer oder gezieltere Suchanfrage (12 Retrieval-Fehlschläge), Zitierpflicht P2, Hierarchie-Boost entscheiden; Reverse-Engineering M6, Tag v1.0.0
3. Reverse-Engineering zu M2 bis M5 beantworten, O-Ton für M0 bis M6c nachtragen

## Offene Entscheidungen / Fragen
- Welche Gegenmaßnahmen kommen in den Prototyp, welche nur als Ausblick in die Ausarbeitung (Zeit)?
- Hierarchie-Boost behalten? (ISS-027: hebt Grußformeln mit Kapitelüberschrift nach oben); Summaries für den Agenten wieder an? (ISS-035)
- Einheitenfaktor der Zahlensuche einschränken? (ISS-050, erst nach den Vergleichsläufen)
- Titelblatt-Angaben für `paper/` (Name, Matrikelnummer, Kurs, Dozent)

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-051/052/006/007/036: Agent verliert Belege durch Werkzeugtrennung, eigene Filter und Wiederholung ohne Filter
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
