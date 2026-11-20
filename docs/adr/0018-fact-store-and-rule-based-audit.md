# ADR-0018: Faktenspeicher und regelbasierte Rechnungsprüfung

- **Status:** akzeptiert
- **Datum:** 2026-11-20
- **Meilenstein:** M8

## Kontext
Nach M6 erkannte keine Variante einen der drei eingebauten Fehler (ISS-066/067). Die Fehleranalyse (RUN-020/021, ISS-107) zeigte: Die Belege kamen meist im Kontext an (P2 18 von 27 Sollfakten), das 7B-Modell entschied aber falsch, welcher Wert ab wann gilt (Arbeitspreis 2025 gegen den Preis von 2024, Stromabschlag 115 statt 120 EUR), und verglich Soll und Ist nicht zuverlässig. Den schwersten Schritt erledigte also die schwächste Komponente. Der Nutzer verlangt eine deutlich höhere Qualität und zusätzlich Heizstrom (Nachtspeicher, HT/NT) im Korpus.

## Entscheidung
Ein Faktenspeicher (`src/audit_agent/facts/`) liest per Regel aus den Tabellenzeilen und festen Sätzen der Chunks Preise, Grundpreise, Abschläge, Zählerstände, Verbräuche, z-Zahl, Brennwert, Rechnungsbeträge und Wohnflächen, jeweils mit Rolle (vereinbart / abgerechnet), Gültigkeit, HT/NT-Zone und Quell-Chunk (`facts.json`, ohne LLM). `check_bill` vergleicht eine Rechnung im Code mit den geltenden vereinbarten Werten: Preise, Zählerstände gegen abgerechnete Menge, Gas-Umrechnung und z-Zahl, Rechenwege, angerechnete Abschläge, Wohnfläche. Das Modell erklärt die Befunde nur noch.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Faktenextraktion mit LLM (`llama3.2`) | gleiche Fehlerklasse wie die Summaries (Wasser-Summary verwechselt brutto/netto, ISS-034); ca. 3 h für alle Chunks |
| GraphRAG | ADR-0003: Beziehungen sind fest (Vertragsnummer, Zeitraum), ein falsch extrahierter Preis stünde im Graphen wie ein Fakt |
| Nur bessere Prompts / größeres Modell | Prompt-Arbeit in M6 brachte keine Fehlererkennung (ISS-070/071); Modelle > 8B passen nicht in 9 GB (ADR-0004) |

## Konsequenzen
- Positiv: Prüfungen sind deterministisch, testbar ohne Ollama und mit Belegnummern zitierbar. Offline-Prüfung (RUN-022): 5 von 5 eingebauten Fehlern erkannt, 0 Fehlalarme bei 8 korrekten Rechnungen, Auswirkungen in EUR wie in der Ground Truth.
- Negativ: Die Regeln sind auf die Layouts dieses Korpus zugeschnitten (ISS-111). Regeln und eingebaute Fehler stammen beide von Claude, das Ergebnis von RUN-022 ist deshalb zirkulär (ISS-112). Der Qualitätsgewinn kommt aus Code, nicht aus dem Modell (ISS-110).
- Zu testen: Ob das Modell `check_bill` im richtigen Moment aufruft und die Befunde richtig wiedergibt (Nachtlauf M8).

## Belege
RUN-020/021, RUN-022, ISS-066/067, ISS-107, ISS-108, ISS-110 bis ISS-112; Kapitel 4 der Ausarbeitung (Faktentabelle als Alternative zu GraphRAG).
