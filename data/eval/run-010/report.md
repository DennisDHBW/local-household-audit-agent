# Evaluation run-010 (2026-11-15)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

B0-Kontext: 6 Dateien vollständig, teilweise: -, fehlend: 24; ca. 6727 von 6961 Token.

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 5/14 (36 %) | 5/14 (36 %) | 3/14 (21 %) |
| Zahlen/Fakten gefunden | 5/27 (19 %) | 9/27 (33 %) | 6/27 (22 %) |
| Zitate auf erwartete Quelle (Präzision) | 7/11 (64 %) | 7/18 (39 %) | 2/2 (100 %) |
| Erwartete Quellen zitiert (Recall) | 7/18 (39 %) | 7/18 (39 %) | 2/18 (11 %) |
| Erfundene Belegnummern | 0 | 0 | 0 |
| Ablenker in Zitaten | 0/11 (0 %) | 0/18 (0 %) | 0/2 (0 %) |
| Ablenker im Kontext | 0/112 (0 %) | 4/70 (6 %) | 1/69 (1 %) |
| Tool-Wahl korrekt | - | - | 7/14 (50 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 19 / 9 |
| Negativfragen erkannt | 2/2 (100 %) | 2/2 (100 %) | 1/2 (50 %) |
| Fehler erkannt | 1/3 (33 %) | 0/3 (0 %) | 0/3 (0 %) |
| Fehlalarme | 0/3 (0 %) | 0/3 (0 %) | 1/3 (33 %) |
| Sekunden je Frage (Mittel / Median) | 112.8 / 42.6 | 55.6 / 43.3 | 136.2 / 150.8 |
| Prompt-Token je Frage (Mittel) | 6608 | 891 | 5624 |

RAGAS (ADR-0012), Bewerter `audit-judge`; Mittel über die bewerteten Antworten, Stichproben von Hand prüfen.

| RAGAS | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Faithfulness | - (0/14 bewertet, 14 zu lang) | 0.71 (14/14 bewertet) | 0.68 (14/14 bewertet) |
| Context Recall | - (0/14 bewertet, 12 zu lang) | 0.33 (12/14 bewertet) | 0.50 (12/14 bewertet) |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| S1 | ✗ 0/3 | ✓ 3/3 | ✗ 1/3 |
| S2 | ✓ 2/2 | ✗ 0/2 | ✓ 2/2 |
| S3 | ✗ 0/1 | ✓ 1/1 | ✓ 1/1 |
| S4 | ✗ 0/2 | ✗ 0/2 | ✗ 0/2 |
| S5 | ✗ 0/2 | ✗ 0/2 | ✗ 1/2 |
| G1 | ✗ 1/3 | ✗ 0/3 | ✗ 0/3 |
| G2 | ✗ 0/3 | ✗ 2/3 | ✗ 0/3 |
| G3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| G4 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| N1 | ✓ | ✓ | ✓ |
| N2 | ✓ | ✓ | ✗ |
| Z1 | ✗ 0/3 | ✗ 2/3 | ✗ 1/3 |
| Z2 | ✓ 1/1 | ✗ 0/1 | ✗ 0/1 |
| Z3 | ✓ 1/1 | ✓ 1/1 | ✗ 0/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**B0 Volltext** (455.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Kündigungsfrist in der Erstlaufzeit, Ende der Erstlaufzeit, Kündigungsfrist danach; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (79.9 s, answer): Laut Auszug [1] gilt für den Gasvertrag eine Kündigungsfrist von 6 Wochen zum Ablauf der Erstvertragslaufzeit in Textform, anschließend unbefristet mit 1 Monat Kündigungsfrist.

Die Erstvertragslaufzeit beträgt laut Auszug [3] 24 Monate, also vom 01.01.2024 bis 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

**P2 Agent** (173.3 s, answer): Die Kündigungsfrist für den Gasvertrag beträgt 2 Monate zum Ablauf eines Kalendervierteljahres. Die Erstlaufzeit läuft bis 31.12.2025.

- Fakten fehlen: Kündigungsfrist in der Erstlaufzeit, Kündigungsfrist danach; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_documents
- RAGAS: Context Recall 0.00, Faithfulness 0.00

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**B0 Volltext** (111.3 s, answer): Laut Auszug [1] gelten folgende Preise:

* Arbeitspreis (verbrauchsabhängig): 34,80 ct/kWh (Brutto, inkl. 19 % USt.)
* Grundpreis (verbrauchsabhängig): 11,50 EUR/Monat (Brutto, inkl. 19 % USt.)

Laut Auszug [3] gelten folgende Preise ab 01.01.2025:

* Arbeitspreis (verbrauchsabhängig): 38,20 ct/kWh (Brutto, inkl. 19 % USt.)
* Grundpreis (verbrauchsabhängig): 12,90 EUR/Monat (Brutto, inkl. 19 % USt.)

Es ist also zu beachten, dass die Preise ab 01.01.2025 geändert wurden.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (38.1 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 0.00

**P2 Agent** (63.1 s, answer): Der Arbeitspreis beträgt 34,80 ct/kWh (Brutto) und der Grundpreis 11,50 EUR/Monat (Brutto).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**B0 Volltext** (15.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasserverbrauch 2025; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (46.2 s, answer): Laut [1] beträgt der Anfangsstand am 01.01.2025 312 m³. Laut [3] beträgt der Zählerstand am 31.12.2025 386 m³. Der Verbrauch 2025 beträgt also 386 m³ - 312 m³ = 74 m³.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1, [3] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

**P2 Agent** (57.6 s, answer): Der Wasserverbrauch 2025 laut Zählerständen beträgt 74 m³.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**B0 Volltext** (13.6 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (31.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 0.00

**P2 Agent** (298.4 s, tool_limit): Es tut mir leid, aber ich konnte keine Informationen über den Stromverbrauch 2022 und 2023 finden. Die Belege, die ich hatte, beziehen sich auf die Jahre 2024 und 2025. Es scheint, dass die Unterlagen für die Jahre 2022 und 2023 nicht vorhanden sind.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: nein (erwartet -); Lücke benannt: ja; Tools: search_tables, list_documents, search_tables, search_tables, search_tables
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**B0 Volltext** (182.6 s, answer): Die Stromabrechnung 2024 (Auszug [4]) und die Vertragsbedingungen (Auszug [1]) zeigen folgende Preise:

Vertragspreise (Auszug [1]):
- Arbeitspreis (verbrauchsabhängig): 29,24 ct/kWh (Netto)
- Grundpreis (verbrauchsabhängig): 9,66 EUR/Monat (Netto)
- Einmaliger Neukundenbonus: 67,23 EUR (Netto)

Abrechnung 2024 (Auszug [4]):
- Arbeitspreis (verbrauchsabhängig): 29,24 ct/kWh (Netto)
- Grundpreis (verbrauchsabhängig): 9,66 EUR/Monat (Netto)
- Einmaliger Neukundenbonus: -67,23 EUR (Netto)

Die Abrechnung 2024 stimmt mit den Vertragspreisen überein, außer für den Einmaligen Neukundenbonus. Der Einmalige Neukundenbonus ist in der Abrechnung 2024 mit -67,23 EUR (Netto) angegeben, was bedeutet, dass der Bonus bereits im Jahr 2024 abgerechnet wurde. In den Vertragsbedingungen ist jedoch angegeben, dass der Bonus nach 12 Monaten Belieferung gezahlt wird.

- Fakten fehlen: Rechnungsbetrag 2024, Abrechnung korrekt; Urteil: - (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (27.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Rechnungsbetrag 2024, Abrechnung korrekt; Urteil: - (erwartet ja); Lücke benannt: ja
- RAGAS: Context Recall 1.00, Faithfulness 0.00

**P2 Agent** (83.3 s, answer): Die Stromabrechnung 2024 stimmt nicht mit den Vertragspreisen überein.

Der Rechnungsbetrag für die Stromlieferung 2024 beträgt 1.189,00 EUR (inkl. 19 % USt. & Neukundenbonus), während der Preis Netto für die Energielieferung 2024 1.066,39 EUR beträgt. Der Preis Brutto für die Energielieferung 2024 beträgt 1.269,00 EUR.

Der Unterschied zwischen dem Rechnungsbetrag und dem Preis Netto beträgt 122,61 EUR.

- Fakten fehlen: Abrechnung korrekt; Urteil: nein (erwartet ja); Lücke benannt: nein; Tools: search_tables
- RAGAS: Context Recall 1.00, Faithfulness 0.80

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**B0 Volltext** (56.4 s, answer): [3] besagt, dass der Arbeitspreis ab 01.01.2025 32,10 ct/kWh brutto (neu) ist, aber in der Abrechnung 2025 [7] wird ein Arbeitspreis von 39,50 ct/kWh brutto (alt) angegeben. Der neue Arbeitspreis wurde also nicht angewendet.

- Fakten fehlen: Angekündigter Arbeitspreis, Zu viel berechnet; Urteil: nein (erwartet nein); Lücke benannt: nein
- Zitiert: [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (32.6 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (243.1 s, answer): Es gibt eine Stromabrechnung für 2025. Der neue monatliche Abschlag beträgt ab 15.02.2026 jeweils 120,00 EUR brutto.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search_documents, search_documents
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**B0 Volltext** (254.9 s, answer): Um die Frage zu beantworten, müssen wir die Betriebskosten 2025 ermitteln und dann den Anteil des Kunden ermitteln.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 1 können wir die folgenden Betriebskosten ermitteln:

Rechnungsbetrag Stromlieferung 2025 (inkl. 19 % USt.): 1.379,30 EUR
Abzüglich geleistete Abschlagszahlungen (11 × 115,00 EUR, Feb–Dez 2025): -1.265,00 EUR
Nachzahlungsbetrag (fällig am 05.02.2026): 114,30 EUR

Der Netto-Rechnungsbetrag beträgt also 1.379,30 - 1.265,00 = 114,30 EUR.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 2 können wir die folgenden regulierten Bestandteile ermitteln:

Netzentgelte Stadtwerke Mosbach Netz GmbH: 289,40 EUR
Messstellenbetrieb: 16,81 EUR
Stromsteuer: 63,55 EUR
Konzessionsabgabe: 40,92 EUR
KWKG-Umlage: 8,59 EUR
§ 19 StromNEV-Umlage: 48,30 EUR
Offshore-Netzumlage: 25,39 EUR

Die Summe dieser regulierten Bestandteile beträgt 492,96 EUR.

Der Anteil des Kunden an den Betriebskosten kann also wie folgt berechnet werden:

(492,96 EUR / 1.159,07 EUR) * 100 % = 42,6 %

Der Anteil des Kunden an den Betriebskosten 2025 beträgt also 42,6 %.

- Fakten fehlen: Wohnflächenanteil, Anteil Betriebskosten 2025, Guthaben; Urteil: - (erwartet ja); Lücke benannt: nein
- Zitiert: [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (58.9 s, answer): Laut [1] beträgt mein Anteil an den Betriebskosten 2025 1.830,00 EUR (25,00 % von 7.320,00 EUR).

Laut [2] beträgt mein Anteil an den Betriebskosten 2025 -1.920,00 EUR (25,00 % von 12 × 160,00 EUR).

Der Unterschied zwischen den beiden Werten beträgt 3.750,00 EUR (1.830,00 EUR - 1.920,00 EUR).

Dazu liegen in den Unterlagen keine Angaben vor, warum der Anteil in [2] negativ ist.

- Fakten fehlen: Guthaben; Urteil: - (erwartet ja); Lücke benannt: ja
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [2] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.50

**P2 Agent** (71.2 s, answer): Ihr Anteil an den Betriebskosten 2025 beträgt 540,00 EUR.

- Fakten fehlen: Wohnflächenanteil, Anteil Betriebskosten 2025, Guthaben; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: search_tables, calculate
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**B0 Volltext** (14.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (130.5 s, answer): Um die Korrektheit der Gasabrechnung 2026 zu überprüfen, müssen wir die in den Auszügen bereitgestellten Informationen analysieren.

Zunächst ist der Rechnungsbetrag Erdgaslieferung 2026 (inkl. 19 % USt.) laut Auszug [1] 1.367,99 EUR.

In Auszug [2] wird erwähnt, dass der Arbeitspreis zum 01.01.2026 gesenkt wird. Der genaue Wert des Arbeitspreises wird jedoch nicht angegeben.

In Auszug [3] wird erwähnt, dass der monatliche Abschlag ab 15.02.2027 unverändert 125,00 EUR brutto beträgt. Dies deutet darauf hin, dass der Arbeitspreis vor dem 15.02.2027 höher war als 125,00 EUR brutto.

In Auszug [5] wird die thermische Gasabrechnung nach DVGW-Arbeitsblatt G 685 bereitgestellt. Hier ist die Energiemenge 11.819 kWh angegeben.

Um die Korrektheit der Gasabrechnung 2026 zu überprüfen, müssen wir nun den Rechnungsbetrag mit der Energiemenge in Beziehung setzen.

Die Energiemenge beträgt 11.819 kWh. Der Brennwert beträgt 11,150 kWh/m³. Daher beträgt das Volumen 11.819 kWh / 11,150 kWh/m³ = 1.060 m³.

Der Rechnungsbetrag beträgt 1.367,99 EUR. Der Preis pro Kubikmeter beträgt also 1.367,99 EUR / 1.060 m³ = 1,29 EUR/m³.

Dieser Preis ist jedoch nicht korrekt, da der Arbeitspreis zum 01.01.2026 laut Auszug [2] gesenkt wurde. Der genaue Wert des Arbeitspreises ist jedoch nicht angegeben.

Da der genaue Wert des Arbeitspreises zum 01.01.2026 nicht bekannt ist, können wir nicht bestätigen, ob die Gasabrechnung 2026 korrekt ist.

Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: ja
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [2] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1, [3] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [5] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.80

**P2 Agent** (146.0 s, answer): Die Gasabrechnung 2026 ist korrekt. Der Verbrauch beträgt 1.060 m³, der Grundpreis beträgt 16,00 EUR/Monat, der Arbeitspreis beträgt 9,95 ct/kWh und der Rechnungsbetrag inkl. 19 % Umsatzsteuer beträgt 1.367,99 EUR.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein; Tools: list_documents, search_tables, search_tables
- RAGAS: Context Recall 0.00, Faithfulness 0.40

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**B0 Volltext** (344.0 s, answer): Um die Frage zu beantworten, müssen wir die Betriebskosten 2026 ermitteln und dann den Anteil des Kunden ermitteln.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 1 können wir die Rechnungsbeträge für 2025 ersehen:

Rechnungsbetrag Stromlieferung 2025 (inkl. 19 % USt.): 1.379,30 EUR
Abzüglich geleistete Abschlagszahlungen (11 × 115,00 EUR, Feb–Dez 2025): -1.265,00 EUR
Nachzahlungsbetrag (fällig am 05.02.2026): 114,30 EUR

Der Netto-Rechnungsbetrag für 2025 beträgt also 1.379,30 - 1.265,00 = 114,30 EUR.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 2 können wir die regulierten Bestandteile ersehen:

Im Netto-Rechnungsbetrag (1.159,07 EUR) sind folgende regulierte Bestandteile enthalten: Netzentgelte Stadtwerke Mosbach Netz GmbH (289,40 EUR), Messstellenbetrieb (16,81 EUR), Stromsteuer 2,05 ct/kWh (63,55 EUR), Konzessionsabgabe (40,92 EUR), KWKG- Umlage (8,59 EUR), § 19 StromNEV-Umlage (48,30 EUR) sowie Offshore-Netzumlage (25,39 EUR).

Der Anteil der regulierten Bestandteile am Netto-Rechnungsbetrag beträgt also:

(289,40 + 16,81 + 63,55 + 40,92 + 8,59 + 48,30 + 25,39) / 1.159,07 = 0,492 oder 49,2 %

Der Anteil der regulierten Bestandteile am Rechnungsbetrag 2025 beträgt also 49,2 %.

Der Anteil des Kunden an den Betriebskosten 2026 beträgt also:

114,30 EUR (Netto-Rechnungsbetrag 2025) x 49,2 % = 56,29 EUR

Der Anteil des Kunden an den Betriebskosten 2026 beträgt also 56,29 EUR.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: nein
- Zitiert: [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (71.7 s, answer): Um dies zu überprüfen, müssen wir die Gesamtkosten 2026 und den Anteil berechnen.

[1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf: Gesamtkosten Objekt: 7.470,00 EUR, Ihr Anteil: 1.963,28 EUR

[2] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf: Abzüglich geleistete Betriebskostenvorauszahlungen: -1.920,00 EUR

Der korrekte Anteil an den Betriebskosten 2026 beträgt also:

1.963,28 EUR (Anteil nach [1]) - 1.920,00 EUR (Abzüglich geleistete Betriebskostenvorauszahlungen) = 43,28 EUR

Dieser Wert ist jedoch nicht in den Unterlagen enthalten. Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: ja
- Zitiert: [1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1, [2] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.57

**P2 Agent** (72.6 s, answer): Ihr Anteil an den Betriebskosten 2026 beträgt 859,26 EUR.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search_tables, calculate
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**B0 Volltext** (13.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness zu lang

**P1 Pipeline** (26.6 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness 1.00

**P2 Agent** (32.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search_tables, list_documents
- RAGAS: Context Recall entfällt, Faithfulness 1.00

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**B0 Volltext** (14.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness zu lang

**P1 Pipeline** (41.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness 1.00

**P2 Agent** (158.3 s, answer): Der Grundpreis für Fernwärme beträgt 10,84 EUR/Monat (Netto) bzw. 12,90 EUR/Monat (Brutto) ab 01.01.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables
- RAGAS: Context Recall entfällt, Faithfulness 0.00

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**B0 Volltext** (17.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Volumen, z-Zahl, Energiemenge; Urteil: - (erwartet ja); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (106.6 s, answer): Um die Frage zu beantworten, müssen wir die Zählerstände 2025 aus [1] und [2] sowie den abgerechneten Gasverbrauch 2025 aus [4] vergleichen.

Zählerstand 01.01.2025: 8.120 m³ (K) [1]
Zählerstand 31.12.2025: 9.320 m³ (K) [1]
Volumen: 1.200 m³ [1]
Energiemenge: 12.791 kWh [1]

Zählerstand 01.01.2026: 9.320 m³ (K) [2]
Zählerstand 31.12.2026: 10.380 m³ (K) [2]
Volumen: 1.060 m³ [2]
Energiemenge: 11.819 kWh [2]

Der abgerechnete Gasverbrauch 2025 beträgt 1.200 m³ [1], was der Volumenmenge entspricht, die zwischen den Zählerständen 01.01.2025 und 31.12.2025 verbraucht wurde.

Die Energiemenge 2025 beträgt 12.791 kWh [1], was der Energiemenge entspricht, die zwischen den Zählerständen 01.01.2025 und 31.12.2025 verbraucht wurde.

Der abgerechnete Gasverbrauch 2025 passt also zu den Zählerständen 2025.

- Fakten fehlen: z-Zahl; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [2] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [4] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

**P2 Agent** (165.6 s, tool_limit): Der abgerechnete Gasverbrauch 2025 beträgt 1.200 m³ (Treffer [1]). Der Zählerstand am 01.01.2025 beträgt 8.120 m³ (Treffer [1]) und am 31.12.2025 9.320 m³ (Treffer [1]). Der Gesamtverbrauch kann also nicht mit den Zählerständen übereinstimmen, da der Zählerstand am Ende des Jahres höher ist als der abgerechnete Verbrauch. Der Unterschied beträgt 1.200 m³.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: search_tables
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 0.83

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**B0 Volltext** (37.6 s, answer): Laut [2] beträgt der monatliche Abschlag 105,00 EUR brutto. Laut [7] beträgt der neue monatliche Abschlag ab 15.02.2026 120,00 EUR brutto.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 02_Strom_Begruessung_Abschlagsplan_2024.pdf S. 1, [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (44.8 s, answer): Laut Auszug [2] beträgt der aktuelle monatliche Abschlag 115,00 EUR brutto.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (186.6 s, tool_limit): Ich entschuldige mich für die vorherigen Fehler. Basierend auf den vorhandenen Belegen kann ich folgende Antwort geben:

Der aktuelle monatliche Stromabschlag beträgt 115,42 EUR (Treffer [2]).

Bitte beachten Sie, dass die anderen Treffer nur Jahresrechnungen oder Einmalbeträge darstellen und nicht den monatlichen Abschlag.

- Fakten fehlen: Aktueller Abschlag; Urteil: nein (erwartet -); Lücke benannt: nein; Tools: search_tables
- Zitiert: [2] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.50

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**B0 Volltext** (47.6 s, answer): Laut Auszug [1] ist die Kündigungsfrist 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform. Da die Vertragslaufzeit 12 Monate beträgt, kann der Vertrag also zum Ablauf des 31.12.2024 gekündigt werden.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (41.3 s, answer): Laut [2] und [3] kann der Stromvertrag kündbar sein mit einer Frist von 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform, danach unbefristet mit 1 Monat Frist kündbar.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [3] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (155.5 s, answer): Die Kündigungsfrist für Ihren Stromvertrag beträgt 14 Tage zum Ablauf der Vertragslaufzeit.

- Fakten fehlen: Kündigungsfrist Strom; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_documents
- RAGAS: Context Recall 1.00, Faithfulness 0.00
