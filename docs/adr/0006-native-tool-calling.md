# ADR-0006: Natives Ollama-Tool-Calling statt Text-ReAct

- **Status:** akzeptiert (vorläufig, Bestätigung in M5)
- **Datum:** 2026-11-14
- **Meilenstein:** M0

## Kontext
Der Agent (P2) muss Werkzeuge wie `search_tables` oder `calculate` aufrufen. Zwei Wege sind möglich: das native Tool-Calling der Ollama-Chat-API (Tool-Schemas als JSON, strukturierte Antwort) oder ReAct als Text-Prompt mit eigenem Parser für „Thought/Action/Observation“. Kleine lokale Modelle sind bei freiem Text oft unzuverlässig; zusätzlich ist jeder Token auf der CPU teuer (ISS-001).

## Entscheidung
Der Agent nutzt das native Tool-Calling der Ollama-API (`tools=[...]` im Chat-Aufruf). Die Argumente werden zusätzlich selbst gegen das Schema validiert; bei ungültigem Aufruf gibt es einen Korrekturversuch (siehe `concept.md`, 7.4). Die ReAct-Schleife (Thought → Action → Observation) bleibt der Kontrollfluss, nur das Aufrufformat ist strukturiert.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| ReAct als Freitext mit eigenem Parser | Mehr Fehlerquellen beim Parsen, längere Ausgaben (langsam bei 5–6 Tokens/s); in RUN-000 war das native Format nicht nötig zu ersetzen |
| Beides parallel anbieten | YAGNI; nur als Rückfall, falls M5 das native Format widerlegt |

## Konsequenzen
- Positiv: In RUN-000 lieferten alle 10 Aufrufe (2 Modelle × 5 Aufgaben) einen formal gültigen Tool-Aufruf mit parsebaren Argumenten; 8 von 10 wählten das erwartete Werkzeug.
- Negativ: Die Tool-Wahl ist nicht perfekt (ISS-006), und die Modelle setzen ungefragt Filter (ISS-007). Beides muss durch Tool-Beschreibungen und Fallbacks aufgefangen werden.
- Zu testen (M5): Mehrschritt-Läufe, bei denen Tool-Ergebnisse zurück an das Modell gehen (im Smoke-Test nur der erste Schritt). Zeigt sich dort Instabilität, wird ein Text-ReAct-Fallback ergänzt und dieses ADR angepasst.

## Belege
RUN-000, ISS-005, ISS-006, ISS-007.
