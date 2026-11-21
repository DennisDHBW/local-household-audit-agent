# Evaluation run-027 (2026-11-21)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 17/21 (81 %) |
| Zahlen/Fakten gefunden | 43/49 (88 %) |
| Zitate auf erwartete Quelle (Präzision) | 57/69 (83 %) |
| Erwartete Quellen zitiert (Recall) | 25/35 (71 %) |
| Erfundene Belegnummern | 1 |
| Ablenker in Zitaten | 0/69 (0 %) |
| Ablenker im Kontext | 0/153 (0 %) |
| Tool-Wahl korrekt | 19/21 (90 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 4 / 0 |
| Negativfragen erkannt | 2/2 (100 %) |
| Fehler erkannt | 5/5 (100 %) |
| Fehlalarme | 0/4 (0 %) |
| Sekunden je Frage (Mittel / Median) | 171.7 / 166.7 |
| Prompt-Token je Frage (Mittel) | 5838 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 0/2 |
| S3 | ✓ 1/1 |
| S4 | ✗ 0/2 |
| S5 | ✓ 2/2 |
| G1 | ✓ 3/3 |
| G2 | ✓ 3/3 |
| G3 | ✓ 3/3 |
| G4 | ✓ 3/3 |
| N1 | ✓ |
| N2 | ✓ |
| Z1 | ✗ 2/3 |
| Z2 | ✗ 0/1 |
| Z3 | ✓ 1/1 |
| H1 | ✓ 2/2 |
| H2 | ✓ 3/3 |
| H3 | ✓ 2/2 |
| W1 | ✓ 3/3 |
| V1 | ✓ 4/4 |
| V2 | ✓ 5/5 |
| V3 | ✓ 3/3 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**P2 Agent** (166.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

Die Kündigungsfrist für den Gasvertrag beträgt 6 Wochen zum Ablauf der Erstvertragslaufzeit, anschließend ist der Vertrag unbefristet mit einer Kündigungsfrist von 1 Monat. Die Erstvertragslaufzeit beträgt 24 Monate, also bis 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P2 Agent** (167.3 s, answer): Der Arbeitspreis für den Strom (Lichtstrom) lautet 39,50 ct/kWh für das Jahr 2025 [6], basierend auf der Stromabrechnung. Der Grundpreis beträgt 12,90 EUR pro Monat für 2025 [8], ebenfalls aus der Stromabrechnung.

Zusammenfassend zeigt das:
- Arbeitspreis: 39,50 ct/kWh [6]
- Grundpreis: 12,90 EUR/Monat [8]

Diese Werte sind ab 01.01.2025 gültig, wie die neuesten Rechnungen und Preisanpassungsanträge belegen [2] und [4].

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein; Tools: get_facts
- Zitiert: [2] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [4] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [6] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [8] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P2 Agent** (122.8 s, answer): Der Wasserverbrauch 2025 lautet auf 74 m³ [1].

Zusammenfassend zeigt dies, dass der Soll-Wert von 74 m³ mit dem Ist-Wert von 74 m³ übereinstimmt. Es gibt keinen Unterschied, und somit hat das Urteil keine Auswirkung.

Dazu liegen in den Unterlagen keine weiteren Grafiken vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: get_facts
- Zitiert: [1] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P2 Agent** (204.5 s, repeat_limit): Dazu liegen in den Unterlagen keine Angaben vor. [1]

[1] Hinweis: Es gibt keine Unterlagen oder Informationen über den Stromverbrauch 2022 in den verfügbaren Unterlagen.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja; Tools: plan, list_documents, list_documents, list_documents
- Zitiert: [1] (unbekannt)

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P2 Agent** (160.6 s, answer): Ja, die Stromabrechnung 2024 stimmt mit den Vertragspreisen überein. [1] Der Arbeitspreis beträgt 34,80 ct/kWh, [2] der Grundpreis 11,50 EUR/Monat, [3] der Verbrauch 3.250 kWh, [4] der Rechnungsbetrag 1.189,00 EUR und [5] die Nachzahlung beträgt 34,00 EUR.

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: check_bill
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [3] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [5] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P2 Agent** (156.4 s, answer): Nein, die Stromabrechnung 2025 stimmt nicht. Der Arbeitspreis wurde nicht auf den angekündigten 38,20 ct/kWh angepasst, sondern auf 39,50 ct/kWh. Dies führt zu einem zusätzlichen Betrag von 40,30 EUR zu Ihren Lasten [1].

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [1] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (184.1 s, answer): Ja, die Betriebskosten-Rechnung 2025 stimmt mit Vertrag, Preisschreiben und Zählerständen überein. Ihr Anteil beträgt 25,00 % der Wohnfläche, was 78,00 m² entspricht [2]. Der berechnete Betrag lautet 1.830,00 EUR [3], und es besteht ein Guthaben von 90,00 EUR [6].

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: plan, check_bill
- Zitiert: [2] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [3] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [6] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P2 Agent** (224.7 s, answer): Nein, die Gasabrechnung 2026 stimmt nicht. Es gibt eine Abweichung in der z-Zahl. Sollte die z-Zahl 0,9560 betragen (wie in den anderen Gasrechnungen), ist sie jedoch auf 1,0000 festgelegt [6]. Dies führt zu einem zusätzlichen Betrag von 51,74 EUR zu Ihren Lasten [6], da die z-Zahl von der Höhe und Druck der Verbrauchsstelle abhängt und die richtige Energiemenge 11.299 kWh betragen sollte, anstatt 11.819 kWh [5].

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [5] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [6] 08_Gas_Jahresabrechnung_2024_NeckarEnergie.pdf S. 1

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P2 Agent** (214.6 s, answer): Nein, die Betriebskosten-Rechnung 2026 stimmt nicht. Wohnfläche: Soll 78,00 m² laut Mietvertrag (25,00 % Anteil), Ist 82,00 m², 95,78 EUR (richtiger Anteil 78,00 m² / 312,00 m² = 25,00 %, also 1.867,50 EUR statt 1.963,28 EUR). Die Rechnung zeigt eine Abweichung, zusammen 95,78 EUR zu Ihren Lasten.

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: plan, check_bill

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P2 Agent** (198.8 s, answer): Die Stromrechnung für 2023 ist nicht direkt in den Unterlagen enthalten. Allerdings finden wir Hinweise auf die Rechnungen für 2024 und 2025:

- Die Stromrechnung für 2024 betrugen [2] 1.189,00 EUR (inkl. 19 % USt. & Neukundenbonus).
- Die Stromrechnung für 2025 ist [1] 1.379,30 EUR (inkl. 19 % USt.).

Da keine direkte Angabe für 2023 vorliegt, können wir davon ausgehen, dass die Rechnung für 2023 nicht in den Unterlagen abgedeckt ist.

- Fakten fehlen: -; Urteil: nein (erwartet -); Lücke benannt: ja; Tools: list_documents, list_documents, search
- Zitiert: [1] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P2 Agent** (132.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P2 Agent** (165.8 s, answer): Ja, die abgerechnete Gasverbrauch 2025 stimmt mit den Zählerständen [5]. Der Verbrauch von 1.200 m³ wurde korrekt in 12.791 kWh umgerechnet [5], und der Rechnungsbetrag von 1.555,43 EUR [7] entspricht den Vertrag und Preisschreiben [1][2][3][4].

- Fakten fehlen: z-Zahl; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: check_bill
- Zitiert: [1] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [2] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [4] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [5] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [7] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (155.6 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR [4]. Dieser Wert gilt ab 15.02.2025 und basiert auf den neuesten vertraglichen Angaben [3] und [4].

Zur Übersicht:
- Der Abschlag wurde in den Rechnungen für 2025 mit 115,00 EUR pro Monat angerechnet [6].

Dazu liegen in den Unterlagen keine Angaben vor, was der aktuelle Abschlag für die vergangenen Monate war.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: ja; Tools: get_facts
- Zitiert: [3] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [4] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [6] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P2 Agent** (166.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor, die eine genaue Kündigungsfrist für Ihren Stromvertrag nennen. Allerdings finden wir in der Vertragsbestätigung von 2024 [3] die Angabe, dass die Kündigungsfrist 1 Monat beträgt, wenn sie zum Ablauf der Erstvertragslaufzeit erfolgt. Danach ist der Vertrag unbefristet und kann mit 1 Monat Frist kündbar sein.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search
- Zitiert: [3] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1

## H1: Welche HT- und NT-Arbeitspreise gelten 2025 für den Heizstrom?

Erwartet: Ab 01.01.2025 gelten 33,50 ct/kWh im Hochtarif (HT) und 24,10 ct/kWh im Niedertarif (NT), jeweils brutto.

**P2 Agent** (144.6 s, answer): Die HT- und NT-Arbeitspreise für 2025 gelten wie folgt:

- **Heizstrom Arbeitspreis HT**: 33,50 ct/kWh [2]
- **Heizstrom Arbeitspreis NT**: 24,10 ct/kWh [4]

Diese Preise werden in den Rechnungen für 2025 verwendet [5] [6].

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: get_facts
- Zitiert: [2] 33_Heizstrom_Preisanpassung_SuedVolt_2025.pdf S. 1, [4] 33_Heizstrom_Preisanpassung_SuedVolt_2025.pdf S. 1, [5] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [6] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## H2: Ist die Heizstromabrechnung 2025 korrekt?

Erwartet: Nein. Laut Zählerständen (12.680 auf 16.100 kWh) wurden im NT 3.420 kWh verbraucht, abgerechnet sind 3.920 kWh; das sind 500 kWh und 120,50 EUR zu viel.

**P2 Agent** (189.9 s, answer): Nein, die Heizstrom-Rechnung 2025 stimmt nicht. Es gibt eine Abweichung im Verbrauch NT aus Zählerständen: Soll 3.420 kWh, Ist abgerechnet 3.920 kWh [10], was zu einem zusätzlichen Betrag von 120,50 EUR [10] führt.

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [10] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## H3: Stimmt die Heizstromabrechnung 2024?

Erwartet: Ja. Preise, Zählerstände (HT 620 kWh, NT 3.180 kWh) und Abschläge passen, der Rechnungsbetrag von 1.016,90 EUR stimmt.

**P2 Agent** (205.0 s, answer): Ja, die Heizstrom-Rechnung 2024 stimmt. Hier sind die Details:

- Arbeitspreis HT: Soll 31,90 ct/kWh, Ist 31,90 ct/kWh [1] [2]
- Arbeitspreis NT: Soll 22,40 ct/kWh, Ist 22,40 ct/kWh [3] [4]
- Grundpreis: Soll 8,90 EUR/Monat, Ist 8,90 EUR/Monat [5] [6]
- Verbrauch HT: Soll 620 kWh, Ist 620 kWh [7] [8]
- Verbrauch NT: Soll 3.180 kWh, Ist 3.180 kWh [9] [10]
- Rechnungsbetrag: Soll 1.016,90 EUR, Ist 1.016,90 EUR [11]
- Abschläge: Soll 935,00 EUR, Ist 935,00 EUR [12] [13]
- Nachzahlung: 81,90 EUR [14]

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: check_bill
- Zitiert: [1] 31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [2] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [3] 31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [4] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [5] 31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [6] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [7] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [8] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [9] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [10] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [11] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [12] 31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [13] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [14] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1

## W1: Ist der Wasserbescheid 2026 korrekt?

Erwartet: Nein. Seit Q1/2026 beträgt die Vorauszahlung 125,00 EUR je Quartal, gezahlt wurden also 500,00 EUR; angerechnet sind nur 4 × 120,00 = 480,00 EUR. Das Guthaben ist um 20,00 EUR zu niedrig.

**P2 Agent** (185.8 s, answer): Nein, die Wasserbescheid-Rechnung 2026 stimmt nicht. Die angerechneten Abschläge sind niedriger als vereinbart: Soll 4 × 125,00 EUR = 500,00 EUR [11], Ist 4 × 120,00 EUR = 480,00 EUR [11], was 20,00 EUR zu Ihren Lasten [11] beträgt.

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [11] 35_Wasser_Jahresbescheid_2026_SWM.pdf S. 1

## V1: Erstelle eine Grafik zum Stromverbrauch 2024 und 2025, getrennt nach Licht- und Heizstrom.

Erwartet: Lichtstrom 3.250 kWh (2024) und 3.100 kWh (2025); Heizstrom HT 620 und 580 kWh, NT 3.180 und 3.420 kWh laut Zählerständen.

**P2 Agent** (157.5 s, answer): Die Grafik zeigt den Stromverbrauch für Licht- und Heizstrom im Jahr 2024 und 2025.

- Heizstrom HT: 2024: 620 kWh [1], 2025: 580 kWh [5]
- Heizstrom NT: 2024: 3.180 kWh [3], 2025: 3.420 kWh [7]
- Lichtstrom: 2024: 3.250 kWh [9], 2025: 3.100 kWh [11]

Grafik: verbrauch-strom-2024-2025.png, zeigt den Verbrauch je Jahr getrennt nach Licht- und Heizstrom.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: make_chart
- Zitiert: [1] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [3] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [5] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [7] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [9] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [11] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## V2: Gib mir eine Übersicht über alle Kosten 2025.

Erwartet: Lichtstrom 1.379,30 EUR, Heizstrom 1.257,82 EUR, Gas 1.555,43 EUR, Wasser 459,10 EUR, Betriebskosten (Anteil) 1.830,00 EUR.

**P2 Agent** (151.2 s, answer): Hier ist eine Übersicht über alle Kosten für das Jahr 2025:

- Betriebskosten: 1.830,00 EUR (Ihr Anteil vor Abzug der Vorauszahlungen) [1]
- Gas: 1.555,43 EUR [2]
- Heizstrom: 1.257,82 EUR [3]
- Lichtstrom: 1.379,30 EUR [4]
- Wasser: 459,10 EUR [5]

Diese Übersicht zeigt die Kosten für alle Sparten im Jahr 2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: make_overview
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [2] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [3] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [4] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [5] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1

## V3: Wie haben sich die Gaspreise seit 2024 entwickelt? Zeig das als Grafik.

Erwartet: Arbeitspreis 10,80 ct/kWh (2024–2025), ab 01.01.2026 9,95 ct/kWh; Grundpreis 14,50 EUR/Monat, ab 01.01.2026 16,00 EUR/Monat.

**P2 Agent** (151.1 s, answer): Die Grafik zeigt die Entwicklung der Gaspreise seit 2024. Es gibt zwei Grundpreise und zwei Arbeitspreise, die sich ab 2026 ändern:

1. Der Grundpreis steigt von 14,50 EUR/Monat ab 1. Januar 2024 auf 16,00 EUR/Monat ab 1. Januar 2026 [1].
2. Der Arbeitspreis sinkt von 10,80 ct/kWh ab 1. Januar 2024 auf 9,95 ct/kWh ab 1. Januar 2026 [3].

![Grafik der Gaspreise 2024–](preise-gas-2024.png)

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: make_chart
- Zitiert: [1] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1
