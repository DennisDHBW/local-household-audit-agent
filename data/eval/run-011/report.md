# Evaluation run-011 (2026-11-15)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

B0-Kontext: 6 Dateien vollständig, teilweise: -, fehlend: 24; ca. 6727 von 6961 Token.

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 4/14 (29 %) | 6/14 (43 %) | 4/14 (29 %) |
| Zahlen/Fakten gefunden | 6/27 (22 %) | 10/27 (37 %) | 8/27 (30 %) |
| Zitate auf erwartete Quelle (Präzision) | 3/8 (38 %) | 8/16 (50 %) | 6/19 (32 %) |
| Erwartete Quellen zitiert (Recall) | 3/18 (17 %) | 8/18 (44 %) | 6/18 (33 %) |
| Erfundene Belegnummern | 0 | 0 | 0 |
| Ablenker in Zitaten | 0/8 (0 %) | 0/16 (0 %) | 0/19 (0 %) |
| Ablenker im Kontext | 0/112 (0 %) | 4/70 (6 %) | 0/80 (0 %) |
| Tool-Wahl korrekt | - | - | 5/14 (36 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 19 / 9 |
| Negativfragen erkannt | 2/2 (100 %) | 2/2 (100 %) | 1/2 (50 %) |
| Fehler erkannt | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) |
| Fehlalarme | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) |
| Sekunden je Frage (Mittel / Median) | 89.8 / 34.5 | 77.7 / 71.4 | 297.6 / 290.9 |
| Prompt-Token je Frage (Mittel) | 7699 | 975 | 10515 |

RAGAS (ADR-0012), Bewerter `audit-judge`; Mittel über die bewerteten Antworten, Stichproben von Hand prüfen.

| RAGAS | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Faithfulness | - (0/14 bewertet, 14 zu lang) | 0.74 (14/14 bewertet) | 0.69 (14/14 bewertet) |
| Context Recall | - (0/14 bewertet, 12 zu lang) | 0.33 (12/14 bewertet) | 0.58 (12/14 bewertet) |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| S1 | ✗ 0/3 | ✓ 3/3 | ✗ 0/3 |
| S2 | ✗ 1/2 | ✗ 0/2 | ✗ 0/2 |
| S3 | ✗ 0/1 | ✓ 1/1 | ✓ 1/1 |
| S4 | ✗ 0/2 | ✗ 0/2 | ✗ 0/2 |
| S5 | ✓ 2/2 | ✓ 2/2 | ✓ 2/2 |
| G1 | ✗ 2/3 | ✗ 0/3 | ✗ 1/3 |
| G2 | ✗ 0/3 | ✗ 2/3 | ✓ 3/3 |
| G3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| G4 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| N1 | ✓ | ✓ | ✓ |
| N2 | ✓ | ✓ | ✗ |
| Z1 | ✗ 0/3 | ✗ 1/3 | ✗ 1/3 |
| Z2 | ✗ 0/1 | ✗ 0/1 | ✗ 0/1 |
| Z3 | ✓ 1/1 | ✓ 1/1 | ✗ 0/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**B0 Volltext** (493.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Kündigungsfrist in der Erstlaufzeit, Ende der Erstlaufzeit, Kündigungsfrist danach; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (82.2 s, answer): Für den Gasvertrag gilt eine Kündigungsfrist von 6 Wochen zum Ablauf der Erstvertragslaufzeit in Textform; anschließend unbefristet mit 1 Monat Kündigungsfrist. Die Erstvertragslaufzeit beträgt 24 Monate, also bis 31.12.2025.

Zu den Angaben:
- Kündigungsfrist: 6 Wochen + anschließend 1 Monat [1]
- Erstvertragslaufzeit: 24 Monate bis 31.12.2025 [3]

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1, [3] 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 0.75

**P2 Agent** (348.5 s, answer): Die Kündigungsfrist für den Gasvertrag lautet nicht explizit in den Dokumenten fest. Allerdings ist die Erstlaufzeit des Vertrags ab dem 01.01.2024 gültig.

Zu Ihrer Frage, bis wann die Erstlaufzeit läuft, lautet die Antwort: Die Erstlaufzeit läuft ab dem 01.01.2024. Die genaue Kündigungsfrist ist nicht in den Dokumenten enthalten.

- Fakten fehlen: Kündigungsfrist in der Erstlaufzeit, Ende der Erstlaufzeit, Kündigungsfrist danach; Urteil: nein (erwartet -); Lücke benannt: nein; Tools: list_documents, search_documents, search_documents
- RAGAS: Context Recall 1.00, Faithfulness 0.50

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**B0 Volltext** (45.0 s, answer): Der Arbeits- und Grundpreis lautet wie folgt:

- Arbeitspreis: 34,80 ct/kWh (brutto, inkl. 19 % USt.) [3]
- Grundpreis (12 Monate): 138,00 EUR (brutto, inkl. 19 % USt.) [1]

- Fakten fehlen: Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (61.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 0.00

**P2 Agent** (282.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

Bitte überprüfen Sie die Suchanfrage oder stellen Sie die Frage erneut, falls Sie spezifischere Informationen benötigen.

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: ja; Tools: list_documents, search_documents
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**B0 Volltext** (14.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasserverbrauch 2025; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (70.1 s, answer): Der Wasserverbrauch 2025 laut den Zählerständen beträgt 74 m³. Dies kann aus dem Auszug [3] entnommen werden, der den Zählerstand am 31.12.2025 mit 386 m³ anzeigt und den Verbrauch von 74 m³ im Jahr 2025 angibt.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [3] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

**P2 Agent** (170.4 s, answer): Der Wasserverbrauch laut den Zählerständen für das Jahr 2025 beträgt 74 m³ [4].

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables
- Zitiert: [4] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**B0 Volltext** (13.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (54.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 0.00

**P2 Agent** (364.8 s, answer): Der Stromverbrauch 2022 und 2023 ist nicht direkt in den Tabellen aufgeführt. Allerdings können wir die Rechnungsbeträge für die jeweiligen Jahre berechnen:

2022: 1.189,00 EUR (ohne Nachzahlungsbetrag)
2023: 1.379,30 EUR

Die Abzüge der Abschlagszahlungen beeinflussen den endgültigen Rechnungsbetrag, aber sie stellen den Verbrauch nicht dar.

Für 2022 betrugen die Abschlagszahlungen 1.155,00 EUR, und für 2023 1.265,00 EUR.

Die Verbrauchsdaten sind in den Rechnungen nicht enthalten.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: nein (erwartet -); Lücke benannt: nein; Tools: search_tables, list_documents, search_tables
- RAGAS: Context Recall 0.00, Faithfulness 0.17

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**B0 Volltext** (214.0 s, answer): Ja, die Stromabrechnung 2024 stimmt mit den Vertragspreisen überein.

Rechnungsbetrag Stromlieferung 2024 (inkl. 19 % USt. & Neukundenbonus): 1.189,00 EUR

Zusammengefasst:
- Grundpreis (12 Monate): 138,00 EUR (abzüglich Neukundenbonus -80,00 EUR = 115,97 EUR)
- Arbeitspreis: 1.269,00 EUR
- Neukundenbonus: -80,00 EUR

Die Berechnung entspricht den Vertragspreisen:
- Grundpreis pro Jahr: 138,00 EUR
- Arbeitspreis pro kWh: 34,80 ct = 0,348 EUR
- Prognostizierter Jahresverbrauch: 3.300 kWh

Rechne Schritt für Schritt:
1. Grundpreis pro Jahr: 138,00 EUR
2. Arbeitspreis für 3.300 kWh: 34,80 ct/kWh * 3.300 kWh = 0,348 EUR/kWh * 3.300 kWh = 1.148,40 EUR
3. Neukundenbonus: -80,00 EUR
4. Gesamtbetrag: 138,00 EUR + 1.148,40 EUR - 80,00 EUR = 1.189,00 EUR

Die Stromabrechnung 2024 ist also korrekt und stimmt mit den Vertragspreisen überein.

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (87.4 s, answer): Ja, die Stromabrechnung 2024 stimmt mit den Vertragspreisen überein.

Rechnungsbetrag Stromlieferung 2024 (inkl. 19 % USt. & Neukundenbonus): 1.189,00 EUR [1]

Abzüglich geleistete Abschlagszahlungen (11 × 105,00 EUR, Feb–Dez 2024): -1.155,00 EUR [4]

Netto-Stromabrechnung 2024: 1.189,00 EUR - 1.155,00 EUR = 34,00 EUR

Diese Netto-Betrag (34,00 EUR) entspricht dem Nachzahlungsbetrag, der am 03.02.2025 fällig ist [2]. Daher stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein.

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 0.40

**P2 Agent** (299.4 s, answer): Lass uns die Grundpreise aus der Abrechnung mit den Vertragspreisen vergleichen. 

[1] Grundpreis: 11,50 EUR/ Mon. (Brutto)

[4] Rechnungsbetrag Stromlieferung 2024 (inkl. 19 % USt. & Neukundenbonus): 1.189,00 EUR

Wir müssen den Grundpreis mit dem Gesamtbetrag vergleichen, um zu sehen, ob er in Übereinstimmung ist. 

Grundpreis: 11,50 EUR/ Mon. * 12 Monate = 138,00 EUR

Rechnungsbetrag: 1.189,00 EUR

Die Rechnungsbeträge stimmen mit den Vertragspreisen überein. 

Zusammengefasst: Ja, die Stromabrechnung 2024 stimmt mit den Vertragspreisen überein.

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: list_documents, search_tables
- Zitiert: [1] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 0.50

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**B0 Volltext** (88.2 s, answer): Ja, in der Stromabrechnung 2025 wurde der angekündigte neue Arbeitspreis angewendet. Dies ist im Auszug [7] unter dem Punkt "Detailberechnung der Energiekosten" zu sehen, wo der Arbeitspreis von 33,19 ct/kWh (netto) und 39,50 ct/kWh (brutto) für den Verbrauch von 3.100 kWh abgerechnet wird. Dies entspricht dem neuen Nettopreis von 32,10 ct/kWh und dem Bruttopreis von 38,20 ct/kWh, wie im Auszug [3] angegeben.

- Fakten fehlen: Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein
- Zitiert: [3] 03_Strom_Preisanpassung_SuedVolt_2025.pdf S. 1, [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (62.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (430.7 s, answer): In der Stromabrechnung 2025 wurde der neue Arbeitspreis von 39,50 ct/kWh angewendet. Dies ist deutlich erkennbar in der Tabellenzeile [6], die den Arbeitspreis für die Energiekosten des Zeitraums 01.01.2025 bis 31.12.2025 auf 39,50 ct/kWh aufzeigt.

- Fakten fehlen: Angekündigter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search_documents, list_documents, search_tables
- Zitiert: [6] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**B0 Volltext** (125.4 s, answer): Ja, der Anteil an den Betriebskosten (Netzentgelte) für 2025 ist korrekt berechnet. 

Gemäß Auszug [7] beträgt der Netzentgelbetragsanteil für 2025 289,40 EUR. Dies entspricht dem 20,51 % der Gesamtrechnungsbetrag von 1.379,30 EUR (289,40 EUR / 1.379,30 EUR * 100 = 20,51 %).

Zur Rechnung:
1. Netzentgelte: 289,40 EUR
2. Gesamtrechnungsbetrag: 1.379,30 EUR
3. Berechnung: 289,40 EUR / 1.379,30 EUR * 100 = 20,51 %

Dies entspricht dem Wert, der in den Unterlagen angegeben ist.

- Fakten fehlen: Wohnflächenanteil, Anteil Betriebskosten 2025, Guthaben; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (75.2 s, answer): Ja, der Anteil an den Betriebskosten 2025 ist korrekt berechnet.

Rechnung:
1. Gesamtkosten Objekt: 7.320,00 EUR
2. Ihr Anteil (25,00 %): 7.320,00 EUR × 25,00 % = 1.830,00 EUR

Die Berechnung entspricht der angegebenen Summe [1] 1.830,00 EUR.

- Fakten fehlen: Guthaben; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (388.0 s, answer): Betrachten wir die relevanten Tabellenzeilen aus der Nebenkostenabrechnung 2025:

1. **Summe umlagefähige Betriebskosten 2025**:
   - Gesamtkosten Objekt: 7.320,00 EUR
   - Ihr Anteil (25,00 %): 1.830,00 EUR [1]

2. **Abzüglich geleistete Betriebskostenvorauszahlungen**:
   - (12 × 160,00 EUR) = 1.920,00 EUR
   - Ihr Anteil (25,00 %): -1.920,00 EUR [2]

3. **Guthaben zu Ihren Gunsten (Überweisung am 27.03.2026)**:
   - Ihr Anteil (25,00 %): -90,00 EUR [3]

4. **Leistungsart (§ 35a Abs. 2 EStG) - Summe steuerlich relevanter Aufwendungen**:
   - Gesamter Lohnanteil: 2.000,00 EUR
   - Anteil Mieter (25 %): 500,00 EUR [4]

5. **Leistungsart (§ 35a Abs. 2 EStG) - Gartenpflege und Winterdienst**:
   - Gesamter Lohnanteil: 720,00 EUR
   - Anteil Mieter (25 %): 180,00 EUR [5]

Die Berechnung des Anteils an den Betriebskosten ergibt sich aus der Summe der positiven und negativen Beträge:

- **1.830,00 EUR** (Summe umlagefähige Betriebskosten) + **-1.920,00 EUR** (Vorauszahlungen) + **-90,00 EUR** (Guthaben) = **-100,00 EUR**

Die Berechnung ergibt einen negativen Betrag von -100,00 EUR. Dies bedeutet, dass Ihr Anteil an den Betriebskosten 2025 tatsächlich korrekt berechnet ist, da es sich um einen Guthabenbetrag handelt, der Ihnen zu Gunsten des Hauses überwiesen wird.

Zusammengefasst: Ihr Anteil an den Betriebskosten 2025 ist korrekt berechnet, da es sich um einen Guthabenbetrag von -100,00 EUR handelt

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: list_documents, search_tables
- Zitiert: [1] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [2] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [3] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [4] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [5] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 0.50

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**B0 Volltext** (13.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (163.2 s, answer): Um die Korrektheit der Gasabrechnung 2026 zu prüfen, betrachten wir die relevanten Informationen aus den Auszügen:

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
- RAGAS: Context Recall 0.00, Faithfulness 0.75

**P2 Agent** (254.5 s, answer): Der monatliche Abschlag für 2026 beträgt 125,00 EUR brutto, wie in der Gasabrechnung 2026 [1, 2, 3, 6] deutlich wird.

Zur Kontrolle: Die Berechnung ergibt:
\[ 125,00 \, \text{EUR} \times 11 \, \text{Monate} = 1.375,00 \, \text{EUR} \]

Dazu wurde ein Guthaben von 7,01 EUR überwiesen [1, 8], sodass der Rechnungsbetrag von 1.367,99 EUR ergibt [7].

Die Abrechnung scheint korrekt, da der berechnete Betrag mit dem angegebenen Rechnungsbetrag übereinstimmt.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein; Tools: search_documents, search_tables
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [2] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [3] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [6] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [7] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [8] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**B0 Volltext** (111.5 s, answer): Ja, der Anteil an den Betriebskosten (Netzentgelte) für 2026 ist korrekt berechnet. 

Gemäß Auszug [8] beträgt der Netzentgelbetragsanteil für 2025 (und damit auch 2026, da sich die Netzentgelte in der Regel nicht jährlich ändern) 289,40 EUR. Dies entspricht dem 21,25 % des Gesamtbetrages von 1.379,30 EUR (siehe [8], S. 2).

Rechnung:
\[ 1.379,30 \, \text{EUR} \times 21,25\% = 289,40 \, \text{EUR} \]

Dazu liegen in den Unterlagen keine Angaben vor, die einen anderen Wert nahelegen.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: ja (erwartet nein); Lücke benannt: ja
- Zitiert: [8] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 2
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (75.5 s, answer): Ja, der Anteil an den Betriebskosten 2026 ist korrekt berechnet. 

Rechnung:
1. Gesamtkosten Objekt: 7.470,00 EUR
2. Ihr Anteil (26,28 %): 7.470,00 EUR × 26,28 % = 1.963,28 EUR

Die Berechnung stimmt mit dem Wert von 1.963,28 EUR in Auszug [1] überein.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: ja (erwartet nein); Lücke benannt: nein
- Zitiert: [1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (257.3 s, answer): Betrachten wir die Berechnung des Anteils an den Betriebskosten für 2026:

1. **Nachzahlung zu Ihren Lasten (Zahlung bis 31.03.2027)**: Ihr Anteil beträgt 43,28 EUR.
2. **Summe umlagefähige Betriebskosten 2026**: Ihr Anteil beträgt 1.963,28 EUR.
3. **Müllabfuhr und Straßenreinigung**: Ihr Anteil beträgt 341,67 EUR.
4. **Abzüglich geleistete Betriebskostenvorauszahlungen**: Ihr Anteil beträgt -1.920,00 EUR.
5. **Allgemeinstrom (Treppenhaus & Kellerbeleuchtung)**: Ihr Anteil beträgt 89,36 EUR.

Um den Gesamtbetrag zu berechnen, addieren wir die positiven Anteile und ziehen den negativen Anteil ab:

\[ 43,28 + 1.963,28 + 341,67 + 89,36 - 1.920,00 = 527,59 \, \text{EUR} \]

Die Berechnung stimmt, wenn wir alle Anteile korrekt addieren und subtrahieren. Somit ist Ihr Anteil an den Betriebskosten 2026 korrekt berechnet.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: ja (erwartet nein); Lücke benannt: nein; Tools: list_documents, search_tables
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**B0 Volltext** (13.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness zu lang

**P1 Pipeline** (49.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness 1.00

**P2 Agent** (373.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search_tables, list_documents, list_documents
- RAGAS: Context Recall entfällt, Faithfulness 1.00

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**B0 Volltext** (13.1 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness zu lang

**P1 Pipeline** (66.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja
- RAGAS: Context Recall entfällt, Faithfulness 1.00

**P2 Agent** (189.0 s, answer): Der Grundpreis für Fernwärme beträgt [5] 13,45 EUR pro Monat brutto (inkl. 19 % USt.), ab dem 01.01.2026. Dieser Wert basiert auf dem Preisanpassungsschreiben von NeckarEnergie [4].

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables
- Zitiert: [4] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1, [5] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall entfällt, Faithfulness 0.00

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**B0 Volltext** (16.1 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Volumen, z-Zahl, Energiemenge; Urteil: - (erwartet ja); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (97.4 s, answer): Ja, der abgerechnete Gasverbrauch 2025 passt zu den Zählerständen.

Rechnungsbetrag:
1. Zählerstand am 01.01.2025: 8.120 m³
2. Zählerstand am 31.12.2025: 9.320 m³
3. Volumen: 9.320 m³ - 8.120 m³ = 1.200 m³

Dies entspricht dem Wert in [4], wo der Rechnungsbetrag für die Gaslieferung 2025 (inkl. 19 % USt.) von 1.555,43 EUR abgerechnet wurde.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [4] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

**P2 Agent** (205.7 s, answer): Der abgerechnete Gasverbrauch für 2025 beträgt 1.200 m³, was sich aus den Zählerständen ergibt:

- Stand 01.01.2025: 8.120 m³
- Stand 31.12.2025: 9.320 m³

Die Differenz ist 9.320 m³ - 8.120 m³ = 1.200 m³, was mit der Angabe in [1] übereinstimmt.

Zudem ist der Rechnungsbetrag für die Gaslieferung 2025 (inkl. 19 % USt.) von 1.555,43 EUR in [2] aufgeführt.

Somit passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: search_tables
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [2] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**B0 Volltext** (23.9 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR brutto (gemäß Auszug [4] und [6]).

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [4] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [6] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (69.1 s, answer): Der aktuelle monatliche Stromabschlag beträgt 115,00 EUR brutto, wie aus [2] hervorgeht.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 1.00

**P2 Agent** (438.0 s, answer): Basierend auf den gefundenen Dokumenten ist der aktuelle monatliche Stromabschlag ab Februar 2025 auf 115,00 EUR brutto (96,64 EUR netto zzgl. 18,36 EUR USt.) angepasst. Dieser Wert gilt für die Zeit vom Februar 2025 bis Dezember 2025.

Zur Bestätigung, hier das Ergebnis ausgerechnet:

- Neuer monatlicher Abschlag: 115,00 EUR brutto

Bitte beachten Sie, dass dieser Wert ab Februar 2025 in Kraft tritt.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_tables, list_documents, search_documents
- RAGAS: Context Recall 1.00, Faithfulness 1.00

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**B0 Volltext** (72.5 s, answer): Die Kündigungsfrist beträgt 1 Monat zum Ablauf der Erstvertragslaufzeit, danach ist der Vertrag unbefristet und kann mit 1 Monat Frist kündbar. Da der Erstvertragslaufzeit vom 01.01.2024 bis 31.12.2024 betrifft, können Sie den Vertrag ab 31.12.2024 kündigen, wenn Sie dies mindestens 1 Monat vor dem Ablauf der Erstlaufzeit schriftlich tun.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (72.7 s, answer): Ihre Kündigungsfrist für den Stromvertrag lautet 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform. Danach ist der Vertrag unbefristet kündigbar mit einer Kündigungsfrist von 1 Monat. Dies ist gemäß [2] und [5] festgelegt.

Zusammengefasst:
- 1 Monat zum Ablauf der Erstvertragslaufzeit
- 1 Monat nach der Erstvertragslaufzeit

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1, [5] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.50

**P2 Agent** (163.7 s, answer): Die Kündigungsfrist für Ihren Stromvertrag lautet 31.12.2024, da Sie das Recht haben, den Vertrag ohne Einhaltung einer Kündigungsfrist zum Zeitpunkt des Wirksamwerdens der Preisänderung in Textform zu kündigen.

- Fakten fehlen: Kündigungsfrist Strom; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_documents
- RAGAS: Context Recall 0.00, Faithfulness 0.00
