# Evaluation run-008 (2026-11-15)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

B0-Kontext: 6 Dateien vollständig, teilweise: -, fehlend: 24; ca. 6727 von 6961 Token.

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 2/3 (67 %) | 1/3 (33 %) | 2/3 (67 %) |
| Zahlen/Fakten gefunden | 3/5 (60 %) | 0/5 (0 %) | 2/5 (40 %) |
| Zitate auf erwartete Quelle (Präzision) | 3/4 (75 %) | - | - |
| Erwartete Quellen zitiert (Recall) | 3/3 (100 %) | 0/3 (0 %) | 0/3 (0 %) |
| Erfundene Belegnummern | 0 | 0 | 0 |
| Ablenker in Zitaten | 0/4 (0 %) | - | - |
| Ablenker im Kontext | 0/24 (0 %) | 0/15 (0 %) | 0/10 (0 %) |
| Tool-Wahl korrekt | - | - | 2/3 (67 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 4 / 2 |
| Negativfragen erkannt | 1/1 (100 %) | 1/1 (100 %) | 1/1 (100 %) |
| Fehler erkannt | 1/1 (100 %) | 0/1 (0 %) | 0/1 (0 %) |
| Fehlalarme | - | - | - |
| Sekunden je Frage (Mittel / Median) | 207.2 / 60.4 | 47.8 / 43.2 | 152.8 / 177.9 |
| Prompt-Token je Frage (Mittel) | 6607 | 852 | 5014 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| S2 | ✓ 2/2 | ✗ 0/2 | ✓ 2/2 |
| G1 | ✗ 1/3 | ✗ 0/3 | ✗ 0/3 |
| N1 | ✓ | ✓ | ✓ |

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**B0 Volltext** (546.8 s, answer): Laut Auszug [1] gelten folgende Preise:

* Arbeitspreis (verbrauchsabhängig): 34,80 ct/kWh (Brutto, inkl. 19 % USt.)
* Grundpreis (verbrauchsabhängig): 11,50 EUR/Monat (Brutto, inkl. 19 % USt.)

Laut Auszug [3] gelten folgende Preise ab 01.01.2025:

* Arbeitspreis (verbrauchsabhängig): 38,20 ct/kWh (Brutto, inkl. 19 % USt.)
* Grundpreis (verbrauchsabhängig): 12,90 EUR/Monat (Brutto, inkl. 19 % USt.)

Es ist also zu beachten, dass die Preise ab 01.01.2025 geändert wurden.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1

**P1 Pipeline** (73.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (177.9 s, answer): Der Arbeitspreis beträgt 34,80 ct/kWh (Brutto) und der Grundpreis 11,50 EUR/Monat (Brutto).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**B0 Volltext** (60.4 s, answer): [3] besagt, dass der Arbeitspreis ab 01.01.2025 32,10 ct/kWh brutto (neu) ist, aber in der Abrechnung 2025 [7] wird ein Arbeitspreis von 39,50 ct/kWh brutto (alt) angegeben. Der neue Arbeitspreis wurde also nicht angewendet.

- Fakten fehlen: Angekündigter Arbeitspreis, Zu viel berechnet; Urteil: nein (erwartet nein); Lücke benannt: nein
- Zitiert: [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

**P1 Pipeline** (43.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja

**P2 Agent** (245.2 s, answer): Es gibt eine Stromabrechnung für 2025. Der neue monatliche Abschlag beträgt ab 15.02.2026 jeweils 120,00 EUR brutto.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search_documents, search_documents

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**B0 Volltext** (14.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (26.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (35.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search_tables, list_documents
