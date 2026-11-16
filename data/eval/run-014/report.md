# Evaluation run-014 (2026-11-16)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 4/14 (29 %) |
| Zahlen/Fakten gefunden | 9/27 (33 %) |
| Zitate auf erwartete Quelle (Präzision) | 6/12 (50 %) |
| Erwartete Quellen zitiert (Recall) | 6/18 (33 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/12 (0 %) |
| Ablenker im Kontext | 0/92 (0 %) |
| Tool-Wahl korrekt | 9/14 (64 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 11 / 0 |
| Negativfragen erkannt | 2/2 (100 %) |
| Fehler erkannt | 2/3 (67 %) |
| Fehlalarme | 1/3 (33 %) |
| Sekunden je Frage (Mittel / Median) | 301.2 / 226.8 |
| Prompt-Token je Frage (Mittel) | 9371 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 1/2 |
| S3 | ✗ 0/1 |
| S4 | ✗ 0/2 |
| S5 | ✗ 1/2 |
| G1 | ✗ 0/3 |
| G2 | ✗ 1/3 |
| G3 | ✗ 0/3 |
| G4 | ✗ 1/3 |
| N1 | ✓ |
| N2 | ✓ |
| Z1 | ✗ 1/3 |
| Z2 | ✗ 0/1 |
| Z3 | ✓ 1/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**P2 Agent** (201.7 s, answer): Für den Gasvertrag gilt eine Kündigungsfrist von 6 Wochen zum Ablauf der Erstvertragslaufzeit. Anschließend ist der Vertrag unbefristet und kann mit einer Kündigungsfrist von 1 Monat beendet werden.

Die Erstlaufzeit des Vertrags beträgt 24 Monate, also von 01.01.2024 bis 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search, search

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P2 Agent** (170.0 s, answer): Laut dem Stromvertrag gelten der Grundpreis von 115,97 EUR pro Jahr und 138,00 EUR pro Jahr inklusive USt. (ab 01.01.2025). Der Arbeitspreis beträgt 29,24 ct pro kWh netto und 34,80 ct pro kWh brutto inklusive USt.

- Fakten fehlen: Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P2 Agent** (159.6 s, answer): Der Zählerstand für das Wohnungs-Wasserzähler 8WAS445566 am 31.12.2025 lautete 386 m³ [2].

- Fakten fehlen: Wasserverbrauch 2025; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [2] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P2 Agent** (225.2 s, answer): Dazu liegen in den Unterlagen keine Angaben für den Stromverbrauch im Jahr 2023 vor. Für 2022 und 2025 liegen nur ungenaue Angaben vor, die den Verbrauch nicht präzise bestimmen lassen.

Für 2025 liegen folgende Angaben vor:
- Im 1. Halbjahr 2025 betrugen der Stromverbrauch 1.470 kWh [1].
- Der Rechnungsbetrag für den Stromverbrauch 2025 beträgt 1.379,30 EUR brutto [4].

Für 2022 finden wir keine spezifischen Angaben.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents
- Zitiert: [1] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1, [4] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P2 Agent** (1030.7 s, context_limit): Die Stromabrechnung 2024 beträgt 1.189,00 EUR [1], während der Sollwert für den monatlichen Abschlag ab Februar 2025 115,00 EUR brutto beträgt [10]. Die Abweichung beträgt 1.074,00 EUR [1189 - 115 = 1074].

Da der Sollwert für 2024 nicht explizit in den Unterlagen angegeben ist, kann nicht direkt mit dem Vertrag verglichen werden. Die Preisanpassung für 2025 wurde angepasst, aber die genauen Preise für 2024 sind nicht im Vertrag aufgeführt.

Es wird empfohlen, den Vertrag genauer zu prüfen oder den Anbieter direkt zu kontaktieren, um mögliche Preisanpassungen oder andere relevanten Informationen zu erhalten.

- Fakten fehlen: Abrechnung korrekt; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: search, list_documents, search, calculate
- Zitiert: [1] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [10] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P2 Agent** (254.1 s, answer): Es scheint, dass die notwendigen Unterlagen für das Jahr 2025 und die Sparte Strom nicht vorliegen. Bitte überprüfen Sie die Verfügbarkeit der Unterlagen erneut.

Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: nein (erwartet nein); Lücke benannt: ja; Tools: search

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (306.3 s, answer): Die Abweichung zwischen dem berechneten Anteil an den Betriebskosten [1] (1.830,00 EUR) und dem Wert in der Nebenkostenabrechnung [5] (1.870,00 EUR) beträgt -40,00 EUR.

Sollwert: 1.830,00 EUR
Istwert: 1.870,00 EUR
Abweichung: -40,00 EUR

- Fakten fehlen: Wohnflächenanteil, Guthaben; Urteil: nein (erwartet ja); Lücke benannt: nein; Tools: search, calculate
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [5] 18_Nebenkostenabrechnung_2024_Hausverwaltung.pdf S. 1

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P2 Agent** (348.9 s, answer): Okay, ich werde die Berechnungen mit `calculate` durchführen.

### Berechnungen:

1. **Sollwert (Vertrag):**
   - Monatlicher Abschlag ab 01.01.2026: 105,04 EUR netto
   - USt. (19%): 105,04 * 0,19 = 20,00 EUR
   - Brutto: 105,04 + 20,00 = 125,04 EUR

2. **Istwert (Rechnung):**
   - Monatlicher Abschlag ab 15.02.2027: 125,00 EUR

### Abweichung:
- Sollwert: 125,04 EUR
- Istwert: 125,00 EUR
- Abweichung: 125,04 - 125,00 = 0,04 EUR

### Ergebnis:
Der Sollwert beträgt 125,04 EUR, während der Istwert 125,00 EUR beträgt. Die Abweichung beträgt 0,04 EUR.

Das Rechnungsbetrag von 125,00 EUR stimmt also mit dem Sollwert von 125,04 EUR sehr gut überein.

```json
{
  "Sollwert": 125,04,
  "Istwert": 125,00,
  "Abweichung": 0,04
}
```

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P2 Agent** (407.2 s, answer): Der Sollwert für Ihren Anteil an den Betriebskosten 2026 lautet 1.867,50 EUR (7.470,00 EUR * 25,00 %).

Der berechnete Istwert lautet 1.963,28 EUR (siehe Treffer [1]).

Die Abweichung beträgt 95,78 EUR (1.963,28 EUR - 1.867,50 EUR).

Zusammenfassend ist der berechnete Anteil von 1.963,28 EUR mit einem Abstand zum Sollwert von 95,78 EUR abweichend.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: search, calculate
- Zitiert: [1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P2 Agent** (206.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor, dass es eine Stromrechnung für das Jahr 2023 gibt.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P2 Agent** (228.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P2 Agent** (342.7 s, answer): Der abgerechnete Gasverbrauch von 1.200 m³ im Jahr 2025 entspricht den Zählerständen, wie sie in der Rechnung [1] angegeben sind. Der Zählerstand am 31.12.2025 beträgt 9.320 m³ (K), was mit dem Zählerstand in der Rechnung übereinstimmt.

Dazu liegen in den Unterlagen keine Angaben vor: 
- Zählerstand am 01.01.2025
- Zählerstand am 31.12.2025 in Vertrag [1]

Abweichungen: 
- Zählerstand am 01.01.2025 in Rechnung [1] ist 8.120 m³ (K), in Vertrag [1] ist er nicht angegeben.
- Zählerstand am 31.12.2025 in Vertrag [1] ist 9.320 m³ (K), in Rechnung [1] ist er ebenfalls 9.320 m³ (K).

Differenz: 8.120 m³ (K) - 9.320 m³ (K) = -1.200 m³ (K) für den Zählerstand am 01.01.2025.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: - (erwartet ja); Lücke benannt: ja; Tools: search, search
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (167.8 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR brutto [1,2,3].

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
- Zitiert: [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [2] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [3] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P2 Agent** (167.7 s, answer): Gemäß Ihrem Vertrag lautet die Kündigungsfrist:

- **1 Monat zum Ablauf der Erstvertragslaufzeit in Textform; danach unbefristet mit 1 Monat Frist kündbar.**

Zusätzlich haben Sie das **gesetzliches Sonderkündigungsrecht** (§ 41 Abs. 5 EnWG), das Sie das Recht gibt, den Vertrag ohne Einhaltung einer Kündigungsfrist zum Zeitpunkt des Wirksamwerdens der Änderung (31.12.2024) in Textform zu kündigen, wenn Ihre Preise ändern.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
