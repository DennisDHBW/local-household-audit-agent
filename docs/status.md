# Projektstand

> Diese Datei liest Claude zu Beginn jeder Sitzung. Kurz halten (max. 1 Seite). Alte Einträge überschreiben; die Historie steht in `dev-journal.md` und in Git.

**Letzte Aktualisierung:** 2026-11-21 (Endlauf run-028 ausgewertet)
**Phase:** Phase 1 (Abschluss M8); die Ausarbeitung wird danach neu überarbeitet
**Aktueller Meilenstein:** M8 Agent v2 (Auswertung fertig, Abschluss offen)
**Version:** v1.0.0 (M8 wird v2.0.0)

## Meilensteine

| # | Meilenstein | Status | Tag |
|---|---|---|---|
| M0–M5 | Setup bis Agent mit Streamlit | fertig (Reverse-Engineering-Fragen offen) | v0.1.0, v0.2.0 |
| M6 | Testmodul & Evaluation | fertig (P1 8, P2 6 von 14); Zitat-Präzision je Beleg korrigiert (ISS-123) | v1.0.0 |
| M7 | Ausarbeitung | Zwischenstand (`Claude outputs/Ausarbeitung-Befunde.pdf`, ca. 12 Zeilen zu lang, ISS-107); wird nach M8 neu überarbeitet | – |
| M8 | Agent v2 | Endlauf run-028 auf T1–T8: P2 5/8 laut Metrik, 4 + 2 Grenzfälle nach Handprüfung (Entwicklungsfragen run-027: 16 + 1 von 21); P1 3/8, B0 1/8 | – |

## Zuletzt erledigt
- Endlauf run-028 ausgewertet (alle 24 Antworten, alle P2-Schrittprotokolle, Kontexte von P1, Journal): RUN-028 in `evaluation-log.md`
- Reihenfolge B0 < P1 < P2 hält; P2 nach Handprüfung 50 % statt 76 % auf den Entwicklungsfragen; alle drei P2-Ausfälle (T3, T5, T6) aus Regeln, die an den Entwicklungsfragen gebaut wurden
- Neu: ISS-126 (Wortliste erkennt Prüffragen T3/T6 nicht, `check_bill` 0-mal; leere Antwort → Antwortzwang ohne Werkzeuge, T6 erfindet eine Prüfung), ISS-127 (`make_chart` mit erfundenem Zeitraum); Nachträge ISS-108 (jetzt akzeptiert), ISS-119, ISS-120, ISS-125, ADR-0020, ADR-0021
- Kein Code geändert. Quality Gates: `ruff check`, `ruff format --check` grün, `pytest -m "not slow"` 443 bestanden, 1 übersprungen

## Nächstes Arbeitspaket
M8 abschließen: Abgleich mit `requirements.md`, Grafiken für Kapitel 5 (B0/P1/P2, Entwicklungs- gegen zurückgehaltene Fragen aus `scores.json`), Tag v2.0.0; danach die Reverse-Engineering-Runde M8 (Skill audit-reverse-engineering).

**Empfohlenes Modell:** Sonnet 5.5, Effort High (Reverse-Engineering-Runde, `ai-workflow.md` Abschnitt 4)

## Nächste Schritte
1. M8 abschließen (siehe oben), Reverse Engineering M8
2. Ausarbeitung neu (ISS-107): Endlauf neben die Entwicklungsfragen stellen (ISS-108), Befunde ISS-123, ISS-125, ISS-126, ISS-127 einarbeiten

## Offene Entscheidungen / Fragen
- RAGAS für M8 ja oder nein (3 h je Lauf); bisher nicht im Nachtlauf
- Heizstrom als Zusatzheizung neben Gas-Etagenheizung (ISS-109), so vom Nutzer gewählt

## Bekannte Probleme / Risiken (Details in `issues-log.md`)
- ISS-126/127: Werkzeugauswahl per Wortliste, Antwortzwang nach leerer Antwort, Zeitraum-Reparatur nur für `year`; nicht behoben (ISS-108)
- ISS-108: Entwicklungszahlen zu günstig; Endlauf hat nur 8 Fragen (eine Frage = 12,5 Prozentpunkte)
- ISS-125/119: Mischantworten ohne Beleg, Formfehler (T4 Soll/Ist-Block, T8 „[2024]“), Lesefehler des Modells
- ISS-110/112/111: Gewinn kommt aus dem Code, Regeln und Fehler vom selben Autor, Regeln auf Korpus und Fragen zugeschnitten
- ISS-039/120: B0 sieht nur 6 von 35 Dokumenten, Kontextverschiebung bei langen B0-Antworten (run-028 T8)
- ISS-094/087/084/085/096: Handprüfung nur von Claude, kein O-Ton, Verständnisfragen offen

## Hinweise für die nächste Sitzung
- Git: Branch pro Arbeitspaket, `merge --no-ff`, keine Claude-Hinweise; Löschrecht zu Beginn anfragen
- Nicht nach dem O-Ton fragen (ISS-087); im Journal „(nicht geliefert, ISS-087)“
- Tests in der VM-Shell: `export UV_PROJECT_ENVIRONMENT=/tmp/venv-test-$(id -u) UV_CACHE_DIR=/tmp/uv-cache-$(id -u) UV_PYTHON_INSTALL_DIR=/tmp/uv-python-$(id -u)`, dann `uv sync --group dev --frozen` und `uv run --frozen pytest -m "not slow" -p no:cacheprovider` (Home der VM voll, deshalb auch Python nach `/tmp`; das `.venv` im Repo nicht anfassen). Archivverfahren (ISS-078) nur als Rückfall
- Läufe inhaltlich vergleichen (`answers-*.jsonl`: `answer`, `tool_uses`), nicht byteweise; die `p2-*.jsonl` enthalten Zeiten
- Ollama-Journal auf das Laufzeitfenster filtern; Dateizeiten der VM in UTC, Journal in MEZ (ISS-120)
- Zahlen für Kapitel 5: Entwicklungsfragen B0/P1 aus run-025, P2 aus run-027; zurückgehaltene Fragen aus run-028; an T1–T8 nicht mehr entwickeln
- Ausarbeitung: Regeln aus `writing-guide.md`, Bauanleitung LaTeX wie bisher (ISS-089)
