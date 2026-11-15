# Evaluation run-009 (2026-11-15)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

B0-Kontext: 6 Dateien vollständig, teilweise: -, fehlend: 24; ca. 6727 von 6961 Token.

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 0/2 (0 %) | 0/2 (0 %) | 0/2 (0 %) |
| Zahlen/Fakten gefunden | 0/6 (0 %) | 0/6 (0 %) | 0/6 (0 %) |
| Zitate auf erwartete Quelle (Präzision) | 0/1 (0 %) | 2/6 (33 %) | - |
| Erwartete Quellen zitiert (Recall) | 0/4 (0 %) | 2/4 (50 %) | 0/4 (0 %) |
| Erfundene Belegnummern | 0 | 0 | 0 |
| Ablenker in Zitaten | 0/1 (0 %) | 0/6 (0 %) | - |
| Ablenker im Kontext | 0/16 (0 %) | 0/10 (0 %) | 0/14 (0 %) |
| Tool-Wahl korrekt | - | - | 1/2 (50 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 3 / 3 |
| Negativfragen erkannt | - | - | - |
| Fehler erkannt | 0/2 (0 %) | 0/2 (0 %) | 0/2 (0 %) |
| Fehlalarme | - | - | - |
| Sekunden je Frage (Mittel / Median) | 361.2 / 361.2 | 122.0 / 122.0 | 167.6 / 167.6 |
| Prompt-Token je Frage (Mittel) | 6608 | 902 | 6308 |

RAGAS (ADR-0012), Bewerter `audit-judge`; Mittel über die bewerteten Antworten, Stichproben von Hand prüfen.

| RAGAS | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Faithfulness | - (0/2 bewertet, 2 zu lang) | 0.57 (1/2 bewertet, 1 Fehler) | 1.00 (2/2 bewertet) |
| Context Recall | - (0/2 bewertet, 2 zu lang) | 0.00 (2/2 bewertet) | 0.00 (2/2 bewertet) |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| G3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| G4 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**B0 Volltext** (451.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (172.7 s, answer): Um die Korrektheit der Gasabrechnung 2026 zu überprüfen, müssen wir die in den Auszügen bereitgestellten Informationen analysieren.

Zunächst ist der Rechnungsbetrag Erdgaslieferung 2026 (inkl. 19 % USt.) laut Auszug [1] 1.367,99 EUR.

In Auszug [2] wird erwähnt, dass der Arbeitspreis zum 01.01.2026 gesenkt wird. Der genaue Wert des Arbeitspreises wird jedoch nicht angegeben.

In Auszug [3] wird erwähnt, dass der monatliche Abschlag ab 15.02.2027 unverändert 125,00 EUR brutto beträgt. Dies deutet darauf hin, dass der Arbeitspreis vor dem 15.02.2027 höher war als 125,00 EUR brutto.

In Auszug [5] wird die thermische Gasabrechnung nach DVGW-Arbeitsblatt G 685 bereitgestellt. Hier ist die Energiemenge 11.819 kWh angegeben.

Um die Korrektheit der Gasabrechnung 2026 zu überprüfen, müssen wir den Rechnungsbetrag mit der Energiemenge in Beziehung setzen. Der Brennwert ist 11,150 kWh/m³.

Rechnungsbetrag = Energiemenge x Brennwert
= 11.819 kWh x 11,150 kWh/m³
= 131.511,45 kWh

Da der Rechnungsbetrag 1.367,99 EUR und die Energiemenge 11.819 kWh beträgt, können wir den Preis pro kWh ermitteln:

Preis pro kWh = Rechnungsbetrag / Energiemenge
= 1.367,99 EUR / 11.819 kWh
= 0,116 EUR/kWh

Da der Brennwert 11,150 kWh/m³ beträgt, können wir den Preis pro m³ ermitteln:

Preis pro m³ = Preis pro kWh / Brennwert
= 0,116 EUR/kWh / 11,150 kWh/m³
= 0,0104 EUR/m³

Der Rechnungsbetrag 1.367,99 EUR entspricht also einem Preis von 0,0104 EUR/m³ x 1.060 m³ = 11,044 EUR. Dieser Wert ist jedoch nicht gleich dem Rechnungsbetrag 1.367,99 EUR.

Da der Rechnungsbetrag 1.367,99 EUR und der berechnete Wert 11,044 EUR sind, beträgt der Unterschied 1.367,99 EUR -

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [2] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1, [3] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [5] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness Fehler

**P2 Agent** (262.9 s, answer): Die Gasabrechnung 2026 ist korrekt. Der Verbrauch beträgt 1.060 m³, der Grundpreis beträgt 16,00 EUR/Monat, der Arbeitspreis beträgt 9,95 ct/kWh und der Rechnungsbetrag inkl. 19 % Umsatzsteuer beträgt 1.367,99 EUR.

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein; Tools: list_documents, search_tables, search_tables
- RAGAS: Context Recall 0.00, Faithfulness 1.00

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**B0 Volltext** (271.0 s, answer): Um die Frage zu beantworten, müssen wir die Betriebskosten 2026 ermitteln und dann den Anteil des Kunden ermitteln.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 1 können wir die Rechnungsbeträge für 2025 ersehen:

Rechnungsbetrag Stromlieferung 2025 (inkl. 19 % USt.): 1.379,30 EUR
Abzüglich geleistete Abschlagszahlungen (11 × 115,00 EUR, Feb–Dez 2025): -1.265,00 EUR
Nachzahlungsbetrag (fällig am 05.02.2026): 114,30 EUR

Der Netto-Rechnungsbetrag für 2025 beträgt also 1.379,30 - 1.265,00 = 114,30 EUR.

Aus [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf, S. 2 können wir die regulierten Bestandteile ersehen:

Im Netto-Rechnungsbetrag (1.159,07 EUR) sind folgende regulierte Bestandteile enthalten: Netzentgelte Stadtwerke Mosbach Netz GmbH (289,40 EUR), Messstellenbetrieb (16,81 EUR), Stromsteuer 2,05 ct/kWh (63,55 EUR), Konzessionsabgabe (40,92 EUR), KWKG- Umlage (8,59 EUR), § 19 StromNEV-Umlage (48,30 EUR) sowie Offshore-Netzumlage (25,39 EUR).

Der Anteil der regulierten Bestandteile beträgt also 1.159,07 - 114,30 = 1.044,77 EUR.

Der Anteil des Kunden an den Betriebskosten 2026 beträgt also 114,30 EUR.

Die Antwort lautet also: Ja, der Anteil des Kunden an den Betriebskosten 2026 ist korrekt berechnet.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: ja (erwartet nein); Lücke benannt: nein
- Zitiert: [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
- RAGAS: Context Recall zu lang, Faithfulness zu lang

**P1 Pipeline** (71.4 s, answer): Um dies zu überprüfen, müssen wir die Gesamtkosten 2026 und den Anteil berechnen.

[1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf: Gesamtkosten Objekt: 7.470,00 EUR, Ihr Anteil: 1.963,28 EUR

[2] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf: Abzüglich geleistete Betriebskostenvorauszahlungen: -1.920,00 EUR

Der korrekte Anteil an den Betriebskosten 2026 beträgt also:

1.963,28 EUR (Anteil nach [1]) - 1.920,00 EUR (Abzüglich geleistete Betriebskostenvorauszahlungen) = 43,28 EUR

Dieser Wert ist jedoch nicht in den Unterlagen enthalten. Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: ja
- Zitiert: [1] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1, [2] 30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf S. 1
- RAGAS: Context Recall 0.00, Faithfulness 0.57

**P2 Agent** (72.4 s, answer): Ihr Anteil an den Betriebskosten 2026 beträgt 859,26 EUR.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search_tables, calculate
- RAGAS: Context Recall 0.00, Faithfulness 1.00
