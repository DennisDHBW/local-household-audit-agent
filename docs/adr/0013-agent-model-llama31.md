# ADR-0013: Agent-Modell `llama3.1:8b`

- **Status:** akzeptiert (vom Nutzer am 2026-11-15 bestätigt; Gegenprobe mit `qwen2.5:7b` nach den Gegenmaßnahmen)
- **Nachtrag 2026-11-16 (RUN-014 bis RUN-016):** Gegenprobe gemacht. Handrichtig 6 von 14 bei beiden Modellen; `qwen2.5:7b` zitiert besser, befolgt die Rechennachfrage und erkennt G4, meldet aber zwei richtige Abrechnungen als Abweichung. Der Zeitgrund (136 gegen 298 s) gilt nicht mehr: 320 bis 325 gegen 301 s. Der Status bleibt, bis der Nutzer über die Modellwahl entschieden hat (ISS-066, ADR-0015).
- **Datum:** 2026-11-15
- **Meilenstein:** M6 (M6c)

## Kontext
ADR-0004 ließ offen, ob `llama3.1:8b` oder `qwen2.5:7b` die Antworten schreibt und im Agenten die Werkzeuge wählt. Beide passen in das Speicherbudget (6,25 bzw. 5,46 GB, RUN-000). Die Nachtläufe RUN-010 und RUN-011 haben beide Modelle mit denselben 14 Fragen in den Varianten B0, P1 und P2 gemessen. Weitere Messungen (Gegenmaßnahmen in M6d) kosten auf der CPU je Lauf ein bis zwei Stunden, jede Wiederholung mit zwei Modellen verdoppelt das.

## Entscheidung
`llama3.1:8b` bleibt das Agent-Modell für P1 und P2 und für alle Messungen der Gegenmaßnahmen. `qwen2.5:7b` bleibt Bewerter für RAGAS (ADR-0012). Nach den Gegenmaßnahmen wird P2 einmal mit `qwen2.5:7b` gegengeprüft.

Gründe:
- **Richtigkeit trennt die Modelle nicht.** Nach Handprüfung 5 / 5 / 3 richtige Antworten (llama, B0 / P1 / P2) gegen 3 / 5 / 2 (qwen) bei 14 Fragen und einem Lauf. Die meisten Fehlschläge in P2 entstehen bei beiden gleich, durch den Werkzeugentwurf (ISS-051, ISS-052, ISS-007).
- **Zeit.** P2 braucht mit `llama3.1:8b` 136 s je Frage, mit `qwen2.5:7b` 298 s (32 gegen 69 Minuten für 14 Fragen).
- **Zustimmungsneigung.** `qwen2.5:7b` fällte 14 Urteile, alle „ja“, auch bei den fehlerhaften Abrechnungen. Für ein Werkzeug, das Fehler finden soll, ist das die ungünstigere Schwäche (ISS-054).
- **Unabhängiger Bewerter.** Mit `llama3.1:8b` als Antwortmodell bewertet `qwen2.5:7b` nicht seine eigenen Antworten (ISS-045).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| `qwen2.5:7b` als Agent-Modell | Macht weniger ungültige Werkzeugaufrufe (2 gegen 13) und zitiert Belege (19 Zitate gegen 2), ist aber gut doppelt so langsam, stimmt jeder Abrechnung zu, ruft `calculate` nie und würde vom selben Modell bewertet. |
| Entscheidung bis nach M6d offenlassen und alles mit beiden Modellen messen | Verdoppelt die Laufzeit jeder Messung; die bisherigen Unterschiede sind kleiner als die Wirkung des Werkzeugentwurfs. |
| Ein drittes Modell testen | Bis 8B gibt es auf dieser Hardware kein deutlich stärkeres Modell mit Tool-Calling (ADR-0004); weitere Modelltests lösen die Werkzeugprobleme nicht. |

## Konsequenzen
- Positiv: Messungen der Gegenmaßnahmen dauern etwa halb so lang; RAGAS-Werte stammen von einem anderen Modell als die Antworten.
- Negativ / Preis der Entscheidung: `llama3.1:8b` zitiert in P2 fast nie Belegnummern (2 von 18 erwarteten Quellen) und ruft `calculate` meist mit falschen Argumenten (11 von 13). Beides muss der Harness auffangen (Zitierpflicht, Argumentprüfung). Es braucht ca. 0,8 GB mehr RAM; beide OOM-Kills (RUN-007, RUN-010) fielen in llama-Läufe, seit dem Entladen nach jeder Antwort trat keiner mehr auf (ISS-043).
- Was muss getestet werden, um die Entscheidung zu bestätigen? Nach den Gegenmaßnahmen P2 mit beiden Modellen auf allen 14 Fragen (qwen ca. 70 Minuten). Liegt `qwen2.5:7b` dann um mehr als zwei Fragen vorn, wird die Entscheidung neu gefasst.

## Belege
RUN-010, RUN-011 (`docs/evaluation-log.md`, `data/eval/run-010/`, `data/eval/run-011/`); RUN-000 (RAM, Geschwindigkeit); ISS-036, ISS-043, ISS-045, ISS-050, ISS-054. Grenze: 14 Fragen, ein Lauf je Modell, Temperatur 0; die Handprüfung wurde nicht gegengelesen.
