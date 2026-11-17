# Evaluation run-021 (2026-11-17)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 4/14 (29 %) |
| Zahlen/Fakten gefunden | 8/27 (30 %) |
| Zitate auf erwartete Quelle (Präzision) | 8/17 (47 %) |
| Erwartete Quellen zitiert (Recall) | 8/18 (44 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/17 (0 %) |
| Ablenker im Kontext | 0/105 (0 %) |
| Tool-Wahl korrekt | 9/14 (64 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 11 / 0 |
| Negativfragen erkannt | 2/2 (100 %) |
| Fehler erkannt | 1/3 (33 %) |
| Fehlalarme | 1/3 (33 %) |
| Sekunden je Frage (Mittel / Median) | 307.9 / 270.9 |
| Prompt-Token je Frage (Mittel) | 9647 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 1/2 |
| S3 | ✗ 0/1 |
| S4 | ✗ 0/2 |
| S5 | ✗ 0/2 |
| G1 | ✗ 0/3 |
| G2 | ✗ 2/3 |
| G3 | ✗ 0/3 |
| G4 | ✗ 0/3 |
| N1 | ✓ |
| N2 | ✓ |
| Z1 | ✗ 1/3 |
| Z2 | ✗ 0/1 |
| Z3 | ✓ 1/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**P2 Agent** (344.3 s, answer): Für den Gasvertrag gilt eine Kündigungsfrist von 6 Wochen zum Ablauf der Erstvertragslaufzeit [1]. Anschließend ist der Vertrag unbefristet und kann mit einer Kündigungsfrist von 1 Monat beendet werden [1].

Die Erstlaufzeit des Vertrags beträgt 24 Monate, also von 01.01.2024 bis 31.12.2025 [3].

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search, search
- Zitiert: [1] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P2 Agent** (288.6 s, answer): Laut dem Stromvertrag gelten derzeit folgende Arbeits- und Grundpreise:

- **Grundpreis (Netto):** 115,97 EUR pro Jahr
- **Grundpreis (Brutto):** 138,00 EUR pro Jahr (inkl. 19 % USt.)

Diese Werte gelten bis zum 31.12.2024. Ab dem 01.01.2025 werden sie angepasst:

- **Grundpreis (Netto):** 130,08 EUR pro Jahr
- **Grundpreis (Brutto):** 154,80 EUR pro Jahr (inkl. 19 % USt.)

Der Arbeitspreis beträgt:

- **Arbeitspreis (Netto):** 29,24 ct pro kWh
- **Arbeitspreis (Brutto):** 34,80 ct pro kWh (inkl. 19 % USt.)

Ab dem 01.01.2025 ändern sich die Arbeits- und Grundpreise:

- **Arbeitspreis (Netto):** 32,10 ct pro kWh
- **Arbeitspreis (Brutto):** 38,20 ct pro kWh (inkl. 19 % USt.)

Diese Informationen stammen aus den Dokumenten [1] und [2].

- Fakten fehlen: Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [2] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P2 Agent** (233.0 s, answer): Der Zählerstand des Wohnungswasserzählers 8WAS445566 am 31.12.2025 lautete [2] 386 m³.

- Fakten fehlen: Wasserverbrauch 2025; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [2] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P2 Agent** (234.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor, welche Stromverbrauchsdaten für 2022 verfügbar sind. Für 2023 ist der Stromverbrauch im 1. Halbjahr 1.470 kWh [1].

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents
- Zitiert: [1] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P2 Agent** (359.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor, die die Übereinstimmung der Stromabrechnung 2024 mit den Vertragspreisen belegen. Es gibt keine expliziten Vergleiche oder Preise in der Abrechnung 2024, die mit den Vertragspreisen verglichen werden könnten.

- Fakten fehlen: Rechnungsbetrag 2024, Abrechnung korrekt; Urteil: ja (erwartet ja); Lücke benannt: ja; Tools: search, list_documents, search

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P2 Agent** (249.7 s, empty_answer): 

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (389.1 s, answer): Die Abweichung zwischen dem berechneten Anteil von 1.830,00 EUR [1] und dem Wert von -1.920,00 EUR [2] beträgt -90,00 EUR. 

Der Sollwert lautet 1.830,00 EUR, während der Istwert -1.920,00 EUR ist. Die Abweichung beträgt -90,00 EUR.

- Fakten fehlen: Wohnflächenanteil; Urteil: nein (erwartet ja); Lücke benannt: nein; Tools: search, calculate
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [2] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P2 Agent** (555.0 s, answer): ### Berechnungen:

1. **Sollwert (Vertrag):**
   - Monatlicher Abschlag ab 01.01.2026: 105,04 EUR netto [8]
   - USt. (19%): 105,04 * 0,19 = 20,00 EUR [8]
   - Brutto: 105,04 + 20,00 = 125,04 EUR [8]

2. **Istwert (Rechnung):**
   - Monatlicher Abschlag ab 15.02.2027: 125,00 EUR [2]

### Abweichung:
- Sollwert: 125,04 EUR [8]
- Istwert: 125,00 EUR [2]
- Abweichung: 125,04 - 125,00 = 0,04 EUR

### Ergebnis:
Der Sollwert beträgt 125,04 EUR [8], während der Istwert 125,00 EUR [2] beträgt. Die Abweichung beträgt 0,04 EUR.

Das Rechnungsbetrag von 125,00 EUR [2] stimmt also mit dem Sollwert von 125,04 EUR [8] sehr gut überein.

```json
{
  "Sollwert": 125,04 [8],
  "Istwert": 125,00 [2],
  "Abweichung": 0,04
}
```

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search
- Zitiert: [2] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [8] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P2 Agent** (455.5 s, answer): Ihr Anteil an den Betriebskosten 2026 lautet 1.963,28 EUR in der Abrechnung [1], während der Sollwert laut Vertrag [9] 1.830,00 EUR beträgt. Die Abweichung beträgt 133,28 EUR.

Rechne: \( 1963.28 - 1830 = 133.28 \)

Zusammengefasst: Ihr Anteil an den Betriebskosten 2026 in der Abrechnung ist 1.963,28 EUR, im Vertrag ist er 1.830,00 EUR. Die Abweichung beträgt 133,28 EUR.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: search, calculate
- Zitiert: [1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1, [9] 16_Mietvertrag_Hauptstrasse42_2023.pdf S. 1

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P2 Agent** (236.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor, dass es eine Stromrechnung für das Jahr 2023 gibt.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P2 Agent** (275.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P2 Agent** (266.1 s, answer): Der Zählerstandunterschied beträgt 1.200 m³ [1]. Der abgerechnete Verbrauch für 2025 lautet ebenfalls 1.200 m³. Es gibt also keine Abweichung zwischen Sollwert und Istwert.

Zusammengefasst:
- Sollwert: 1.200 m³
- Istwert: 1.200 m³

Es passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: search, calculate
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (189.9 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR brutto (96,64 EUR netto zzgl. 18,36 EUR USt.), wie es in der [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf, S. 1, und in der [3] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf, S. 1, festgelegt ist.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [3] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P2 Agent** (233.1 s, answer): Der Vertrag kann kündigt werden:

- **1 Monat vor Ablauf der Erstvertragslaufzeit (01.01.2024 – 31.12.2024)**: Danach ist die Kündigungsfrist unbefristet, mit einer Frist von 1 Monat. [1]
- **Sonderkündigungsrecht**: Sie haben das Recht, den Vertrag zum Zeitpunkt der Wirksamwerden der Preisanpassung (31.12.2024) in Textform zu kündigen, ohne Frist einzuhalten. In diesem Fall wird die Preisänderung Ihnen gegenüber nicht wirksam. [2]

- Fakten fehlen: -; Urteil: nein (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [2] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1
