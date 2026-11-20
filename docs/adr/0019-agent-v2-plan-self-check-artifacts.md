# ADR-0019: Agent v2 mit Planungsschritt, Selbstprüfung, Übersichten und Grafiken

- **Status:** akzeptiert (Wirkung noch nicht mit Ollama gemessen)
- **Datum:** 2026-11-20
- **Meilenstein:** M8

## Kontext
Im letzten Lauf (RUN-021) machte P2 ein bis drei Werkzeugaufrufe je Frage, `calculate` dreimal, zwei Werkzeuge nie; ein ausgeschriebener Denkschritt fehlte (Variante Act). Der Nutzer verlangt, dass der Agent „mehr als Agent handelt“ und auf Anfrage Übersichten oder Grafiken erstellt.

## Entscheidung
Werkzeugsatz v2 (`AgentSettings.tool_set = "v2"`, v1 bleibt für Vergleiche): `plan`, `list_documents`, `check_bill`, `get_facts`, `search` (jetzt auch Diagrammbeschreibungen), `make_overview`, `make_chart`, `calculate`. Der Prompt verlangt zuerst einen Plan. Vor jeder Antwort prüft die Schleife einmal je Grund: Prüffrage ohne `check_bill`, verlangte Grafik oder Übersicht fehlt, Zahlen der Antwort stehen in keinem Werkzeugergebnis. Tabellen und Grafiken hängt der Code an die Antwort an (`Artifact`). Höchstens 10 statt 6 Werkzeugaufrufe. Die Streamlit-Oberfläche ist ein Chat; die letzten zwei Fragen und Antworten gehen als Verlauf mit.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Plan als eigener Modellaufruf ohne Werkzeuge | anderer Prompt-Präfix, kein Prompt-Cache, ca. 90 s mehr je Frage |
| Freitext-ReAct mit Thought | eigener Parser nötig (ADR-0006), `qwen2.5:7b` schreibt bei nativem Tool-Calling keinen Text |
| Grafik als Code, den das Modell schreibt | unsicher und fehleranfällig; die Daten kommen ohnehin aus dem Faktenspeicher |

## Konsequenzen
- Positiv: Planung, Werkzeugwahl, Nachprüfung und Darstellung sind im Protokoll sichtbar und messbar (Kennzahlen: Werkzeugaufrufe, verschiedene Werkzeuge, Plan vorhanden, Artefakt vorhanden).
- Negativ: Mehr Werkzeuge verlängern die Werkzeugschemas (mehr Prefill), jede Rückfrage kostet einen Modellaufruf. Ob `qwen2.5:7b` `plan` zuverlässig zuerst aufruft, ist offen (ISS-113).
- Zu testen: Smoke-Test mit drei Fragen, dann Nachtlauf über 21 Entwicklungsfragen, am Ende die 8 zurückgehaltenen Fragen (ISS-108).

## Belege
RUN-021 (Werkzeugnutzung), ADR-0006, ADR-0014, ADR-0018, ISS-108, ISS-113.
