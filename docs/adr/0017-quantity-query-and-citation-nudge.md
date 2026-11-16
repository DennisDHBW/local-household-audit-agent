# ADR-0017: Größen-Anfrage für P1 und P2, Zitier-Rückfrage, Einheitenfaktor nur für Geldfakten

- **Status:** vorgeschlagen (umgesetzt in M6h, Messung RUN-018 und RUN-019 offen)
- **Datum:** 2026-11-16
- **Meilenstein:** M6 (M6h)
- **Ersetzt:** –; ergänzt ADR-0009 (Suche), ADR-0014 (Werkzeug `search`), ADR-0015 (Rückfragen)

## Kontext
Nach RUN-014 scheitern G1 und G3 daran, dass die Sollzahl nie im Kontext steht; P1 hat 12 Retrieval-Fehlschläge (`evaluation-log.md`, ISS-051/052). Der Verlauf von G1 zeigt die Ursache: Die Suche „neuer Arbeitspreis 2025“ liefert fünf Treffer aus dem Schreiben zur Zwischenablesung (Kapitel „1. Halbjahr 2025“), die Zeile mit 38,20 ct fehlt (ISS-072). Außerdem nennen 8 von 14 Antworten in RUN-014 keine Treffernummer, obwohl der Prompt es verlangt. Der Nutzer entschied am 2026-11-16: gezielte Größen-Anfrage statt mehr Treffer, Hierarchie-Boost behalten, Tabellen-Zusammenfassungen für den Agenten aus, Einheitenfaktor nur für ct und EUR.

## Entscheidung
1. **Größen-Anfrage (`retrieval/quantity.py`):** `quantity_query` entfernt aus einer Anfrage Jahreszahlen, Stoppwörter, Frage- und Urteilswörter, Dokumentwörter (auch Zusammensetzungen auf „-abrechnung“, „-rechnung“, „-vertrag“) und Sparten. Bleibt kein Wort übrig oder ändert sich nichts, gibt es keine zweite Suche. Sonst sucht `new_quantity_hits` mit ihr (gleicher Filter, gleiche Chunk-Typen) und hängt bis zu `AgentSettings.quantity_hits` (2) Treffer an, die noch nicht dabei sind. P1 (Frage als Anfrage) und P2 (`search`) nutzen dieselbe Funktion; die Gegenstück-Suche von `include_counterpart` sucht mit der Größen-Anfrage statt mit der langen Anfrage.
2. **Zitier-Rückfrage (`loop.py`):** Enthält die Antwort Zahlen, aber keine Treffernummer `[n]`, nach mindestens einem Werkzeugaufruf und ohne Lückenantwort, fragt der Loop einmal nach (`NudgeStep.reason="cite"`, `AgentSettings.require_citation`).
3. **Einheitenfaktor (`evaluation/metrics.py`):** Die Faktoren 100 und 0,01 gelten nur für Fakten, deren Einheit „ct“ oder „EUR“ enthält. Die Metrik ändert sich damit nur dort, wo bisher „34,80 ct“ den Sollwert 3.480 kWh traf; die Nachbewertung von RUN-010 bis RUN-017 ändert keine Bewertung.
4. **Unverändert:** Hierarchie-Boost 1,5 (ISS-027), `top_k` 5, `candidate_count` 20, Tabellen-Zusammenfassungen für den Agenten aus (ISS-035).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| `top_k` auf 8 bis 10 | Mehr Kontext je Suche kostet bei 18 Token/s Prefill Minuten und erhöht das Kontextlimit-Risiko (G1 in RUN-013); die Zeile wäre nicht sicher dabei. |
| Größe als Parameter von `search` (das Modell nennt sie) | Kleine Modelle füllen zusätzliche Parameter unzuverlässig (ISS-007, ISS-063); der Code kann die Größe aus der Anfrage ableiten. |
| Wortliste der Größen aus den Testfragen | Auf die 14 Fragen zugeschnitten; stattdessen werden nur Füllwörter entfernt, die Größe bleibt, was die Anfrage nennt. |
| Hierarchie-Boost abschalten | Erst in der Messung entscheiden (`retrieval compare` kennt beide Varianten); jetzt wäre es eine zweite Änderung im selben Lauf. |
| Zitierpflicht nur im Prompt | Steht schon darin; trotzdem fehlen Nummern in 8 von 14 Antworten (RUN-014). |

## Konsequenzen
- Positiv: Eine Zeile mit dem Fachbegriff erreicht den Kontext, auch wenn die Frage Jahr und Dokumentart nennt; die Logik ist ein reiner Textfilter ohne Modellaufruf, abschaltbar (`quantity_hits=0`, `require_citation=False`) und mit Tests belegt.
- Negativ / Preis: Bis zu 2 Treffer mehr je Suche (rund 300 Token, bei 18 Token/s etwa 15 bis 20 s Prefill), eine Einbettung mehr je Suche; die Zitier-Rückfrage kostet höchstens einen Modellaufruf je Frage und kann eine richtige Antwort umformulieren. Fragen ohne Größe in der Anfrage („Ist die Gasabrechnung 2026 korrekt?“, G3) profitieren nicht (ISS-074). Die Füllwortliste ist deutsch und von Hand gepflegt; ein unbekanntes Füllwort bleibt in der Anfrage stehen.
- Was muss getestet werden? RUN-018 (P2, `qwen2.5:7b`, 14 Fragen) gegen RUN-014 und RUN-019 (P1) gegen RUN-011: Fakten gefunden (von 27), erwartete Quellen im Kontext (`check_evidence.py`), richtig nach Handprüfung, Antworten mit Treffernummer, Zeit und Prompt-Token je Frage, Kontextlimit-Abbrüche. Die Wirkung von Größen-Anfrage und Zitier-Rückfrage lässt sich nur getrennt zuordnen, wenn die Nachfragen in den Logs (`nudge`, Grund `cite`) gezählt werden.

## Belege
RUN-014, `data/eval/run-014/p2-G1.jsonl` und `p2-G3.jsonl`, ISS-027, ISS-035, ISS-050, ISS-051, ISS-052, ISS-072, ISS-074; Tests in `tests/test_retrieval.py` (`test_quantity_query_keeps_the_billing_quantity`), `tests/test_agent_tools.py`, `tests/test_agent_loop.py`, `tests/test_evaluation.py`.
