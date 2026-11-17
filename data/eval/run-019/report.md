# Evaluation run-019 (2026-11-17)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P1 Pipeline |
|---|---|
| Richtig (gesamt) | 5/14 (36 %) |
| Zahlen/Fakten gefunden | 9/27 (33 %) |
| Zitate auf erwartete Quelle (Präzision) | 7/15 (47 %) |
| Erwartete Quellen zitiert (Recall) | 7/18 (39 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/15 (0 %) |
| Ablenker im Kontext | 7/94 (7 %) |
| Tool-Wahl korrekt | - |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - |
| Negativfragen erkannt | 2/2 (100 %) |
| Fehler erkannt | 0/3 (0 %) |
| Fehlalarme | 1/3 (33 %) |
| Sekunden je Frage (Mittel / Median) | 91.6 / 86.0 |
| Prompt-Token je Frage (Mittel) | 1233 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P1 Pipeline |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 0/2 |
| S3 | ✓ 1/1 |
| S4 | ✗ 0/2 |
| S5 | ✗ 1/2 |
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

**P1 Pipeline** (94.0 s, answer): Für den Gasvertrag gilt eine Kündigungsfrist von 6 Wochen zum Ablauf der Erstvertragslaufzeit. Anschließend ist der Vertrag unbefristet, mit einer Kündigungsfrist von 1 Monat. Die Erstvertragslaufzeit beträgt 24 Monate und endet am 31.12.2025 [3, 5].

Zusammengefasst:
- Kündigungsfrist zum Ende der Erstlaufzeit: 6 Wochen
- Kündigungsfrist anschließend: 1 Monat
- Erstvertragslaufzeit: 24 Monate bis 31.12.2025

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [5] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P1 Pipeline** (76.1 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P1 Pipeline** (87.8 s, answer): Der Wasserverbrauch 2025 laut den Zählerständen beträgt 74 m³. Dies kann aus dem Auszug [3] entnommen werden, der den Zählerstand am 31.12.2025 mit 386 m³ anzeigt und den Verbrauch von 74 m³ im Jahr 2025 angibt.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [3] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P1 Pipeline** (68.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P1 Pipeline** (137.0 s, answer): Zunächst berechnen wir den erwarteten Stromabrechnungsbetrag für 2024 basierend auf den Vertragspreisen.

1. **Abschlagszahlungen:**
   - 11 × 105,00 EUR = 1.155,00 EUR [4]

2. **Rechnungsbetrag Stromlieferung 2024 (inkl. 19 % USt. & Neukundenbonus):**
   - 1.189,00 EUR [1]

3. **Nachzahlungsbetrag:**
   - 34,00 EUR [2]

**Rechnung:**
- Rechnungsbetrag Stromlieferung 2024: 1.189,00 EUR
- Minus Abschlagszahlungen: 1.155,00 EUR
- Plus Nachzahlungsbetrag: 34,00 EUR

**Ergebnis:**
1.189,00 EUR - 1.155,00 EUR + 34,00 EUR = 68,00 EUR

**Vergleich:**
- Rechnungsbetrag Stromlieferung 2024: 1.189,00 EUR [1]
- Berechneter Betrag: 68,00 EUR

**Abweichung:**
- 1.189,00 EUR - 68,00 EUR = 1.121,00 EUR

**Fazit:**
Die Stromabrechnung 2024 (1.189,00 EUR) stimmt nicht mit den berechneten Vertragspreisen (68,00 EUR) überein. Es gibt einen Abweichung von 1.121,00 EUR.

- Fakten fehlen: Abrechnung korrekt; Urteil: nein (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P1 Pipeline** (73.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P1 Pipeline** (84.4 s, answer): Ja, der Anteil an den Betriebskosten für 2025 ist korrekt berechnet. 

Rechnung:
1. Gesamtkosten Objekt: 7.320,00 EUR
2. Ihr Anteil (25,00 %): 7.320,00 EUR × 25,00 % = 1.830,00 EUR

Die Berechnung stimmt mit der Angabe in [1] überein.

- Fakten fehlen: Guthaben; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P1 Pipeline** (161.0 s, answer): Um die Korrektheit der Gasabrechnung 2026 zu prüfen, betrachten wir die relevanten Informationen aus den Auszügen:

1. **Rechnungsbetrag Erdgaslieferung 2026 (inkl. 19 % USt.): 1.367,99 EUR** [1]

2. **Guthaben zu Ihren Gunsten (Gutschrift am 12.02.2027): -7,01 EUR** [4]

3. **Gutschrift: Das Guthaben von 7,01 EUR überweisen wir am 12.02.2027 auf Ihr Konto** [3]

4. **Volumen: 1.060 m³** [5]

5. **Brennwert: 11,150 kWh/ m³** [5]

6. **Energiemenge: 11.819 kWh** [5]

### Berechnung der Energiemenge:
- **Volumen: 1.060 m³**
- **Brennwert: 11,150 kWh/ m³**

\[ 1.060 \, \text{m}^3 \times 11,150 \, \text{kWh/m}^3 = 11.819 \, \text{kWh} \]

Die berechnete Energiemenge von 11.819 kWh entspricht der angegebenen Energiemenge in der Abrechnung [5]. Somit ist die Berechnung des Energievolumens korrekt.

### Berechnung des Rechnungsbetrags:
- **Volumen: 1.060 m³**
- **Brennwert: 11,150 kWh/ m³**
- **Preis pro kWh: \(\frac{1.367,99 \, \text{EUR}}{11.819 \, \text{kWh}} \approx 0,1157 \, \text{EUR/kWh}\)**

\[ 11.819 \, \text{kWh} \times 0,1157 \, \text{EUR/kWh} = 1.367,99 \, \text{EUR} \]

Der berechnete Rechnungsbetrag von 1.367,99 EUR entspricht dem angegebenen Rechnungsbetrag in der Abrechnung [1]. Somit ist der Rechnungsbetrag korrekt.

### Guthaben:
- **Guthaben zu Ihren

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [3] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [4] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [5] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P1 Pipeline** (87.6 s, answer): Ja, der Anteil an den Betriebskosten 2026 ist korrekt berechnet.

Rechnung:
1. Gesamtkosten Objekt: 7.470,00 EUR
2. Ihr Anteil (26,28 %): 7.470,00 EUR × 26,28 % = 1.963,28 EUR

Die Berechnung stimmt mit der angegebenen Summe von 1.963,28 EUR überein.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: ja (erwartet nein); Lücke benannt: nein

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P1 Pipeline** (47.6 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P1 Pipeline** (78.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P1 Pipeline** (115.0 s, answer): Ja, der abgerechnete Gasverbrauch 2025 passt zu den Zählerständen. 

Rechnung:
1. Zählerstand am 01.01.2025: 8.120 m³
2. Zählerstand am 31.12.2025: 9.320 m³
3. Verbrauch 2025: 9.320 m³ - 8.120 m³ = 1.200 m³

Dies entspricht dem Wert in [1], wo der Verbrauch 1.200 m³ angegeben ist.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P1 Pipeline** (92.2 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR brutto (96,64 EUR netto zzgl. 18,36 EUR USt.), wie aus dem Auszug [1] ersichtlich ist.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P1 Pipeline** (78.9 s, answer): Der Stromvertrag kann bis 31.12.2024 ohne Kündigungsfrist kündigt, ab diesem Datum ist die Kündigungsfrist 1 Monat [2, 3].

Dazu liegen in den Unterlagen keine Angaben vor: Frist für Kündigung nach 31.12.2024.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- Zitiert: [2] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [3] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1
