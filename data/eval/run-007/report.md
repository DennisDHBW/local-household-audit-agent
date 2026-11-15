# Evaluation run-007 (2026-11-15)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 1/3 (33 %) | 1/3 (33 %) | 1/1 (100 %) |
| Zahlen/Fakten gefunden | 0/5 (0 %) | 0/5 (0 %) | 2/2 (100 %) |
| Zitate auf erwartete Quelle (Präzision) | 1/1 (100 %) | - | - |
| Erwartete Quellen zitiert (Recall) | 1/3 (33 %) | 0/3 (0 %) | 0/1 (0 %) |
| Erfundene Belegnummern | 0 | 0 | 0 |
| Ablenker in Zitaten | 0/1 (0 %) | - | - |
| Ablenker im Kontext | 0/30 (0 %) | 0/15 (0 %) | 0/5 (0 %) |
| Tool-Wahl korrekt | - | - | 1/1 (100 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 1 / 0 |
| Negativfragen erkannt | 1/1 (100 %) | 1/1 (100 %) | - |
| Fehler erkannt | 1/1 (100 %) | 0/1 (0 %) | - |
| Fehlalarme | - | - | - |
| Sekunden je Frage (Mittel / Median) | 303.5 / 303.8 | 43.1 / 38.4 | 206.7 / 206.7 |
| Prompt-Token je Frage (Mittel) | 4098 | 852 | 3298 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| S2 | ✗ 0/2 | ✗ 0/2 | ✓ 2/2 |
| G1 | ✗ 0/3 | ✗ 0/3 | - |
| N1 | ✓ | ✓ | - |

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**B0 Volltext** (300.1 s, answer): Laut dem Liefervertrag von SüdVolt Energie GmbH (Dokument [1] 01_Strom_Liefervertrag_SuedVolt.pdf, S. 1) gelten folgende Preise:

* Arbeitspreis: 33,19 ct/kWh (Netto)
* Grundpreis: 10,84 EUR/Monat (Netto)

Diese Preise gelten laut Vertrag für den Zeitraum vom 01.01.2025 bis 31.12.2025.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1

**P1 Pipeline** (59.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (206.7 s, answer): Der Arbeitspreis beträgt 34,80 ct/kWh (Brutto) und der Grundpreis 11,50 EUR/Monat (Brutto).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**B0 Volltext** (303.8 s, answer): In der Stromabrechnung 2025 von SüdVolt Energie GmbH ist der Arbeitspreis ÖkoStrom mit 33,19 ct/kWh angegeben. Im Liefervertrag von 2024 ist jedoch ein Arbeitspreis Erdgas (inkl. Energiesteuer & CO₂-Preis) von 9,08 ct/kWh angegeben. Der Arbeitspreis für Strom ist also nicht gleich dem für Gas. Der angekündigte neue Arbeitspreis für Strom wurde nicht angewendet.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: nein (erwartet nein); Lücke benannt: nein

**P1 Pipeline** (38.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**B0 Volltext** (306.7 s, answer): Ich habe keine Informationen über deine Stromrechnung 2023. Die bereitgestellten Dokumente enthalten Informationen über deine Stromrechnung 2025 und deine Gasrechnung 2024, aber keine Informationen über deine Stromrechnung 2023. Wenn du die Rechnung für 2023 benötigst, solltest du dich an deinen Energieversorger wenden.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (31.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
