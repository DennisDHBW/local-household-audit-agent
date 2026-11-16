# Evaluation run-012 (2026-11-16)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 7/14 (50 %) |
| Zahlen/Fakten gefunden | 11/27 (41 %) |
| Zitate auf erwartete Quelle (Präzision) | 3/8 (38 %) |
| Erwartete Quellen zitiert (Recall) | 3/18 (17 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/8 (0 %) |
| Ablenker im Kontext | 0/102 (0 %) |
| Tool-Wahl korrekt | 7/14 (50 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 17 / 3 |
| Negativfragen erkannt | 2/2 (100 %) |
| Fehler erkannt | 0/3 (0 %) |
| Fehlalarme | 1/3 (33 %) |
| Sekunden je Frage (Mittel / Median) | 262.6 / 228.9 |
| Prompt-Token je Frage (Mittel) | 5582 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 1/2 |
| S3 | ✓ 1/1 |
| S4 | ✓ 2/2 |
| S5 | ✗ 1/2 |
| G1 | ✗ 0/3 |
| G2 | ✗ 0/3 |
| G3 | ✗ 0/3 |
| G4 | ✗ 0/3 |
| N1 | ✓ |
| N2 | ✓ |
| Z1 | ✗ 1/3 |
| Z2 | ✓ 1/1 |
| Z3 | ✓ 1/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**P2 Agent** (184.8 s, answer): Die Kündigungsfrist für den Gasvertrag beträgt 6 Wochen zum Ablauf der Erstvertragslaufzeit in Textform, anschließend unbefristet mit 1 Monat Kündigungsfrist. Die Erstvertragslaufzeit beträgt 24 Monate, also bis zum 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P2 Agent** (193.1 s, answer): Der Arbeitspreis beträgt 29,24 ct/kWh (netto) bzw. 34,80 ct/kWh (brutto) und der Grundpreis beträgt 115,97 EUR (netto) bzw. 138,00 EUR (brutto) pro Jahr.

- Fakten fehlen: Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P2 Agent** (305.3 s, answer): Der Wasserverbrauch 2025 betrug 74 m³.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_images, list_documents, search

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P2 Agent** (313.2 s, answer): Der Stromverbrauch 2022 betrug 3.480 kWh/Jahr (Balkendiagramm in [2]). Der Stromverbrauch 2023 betrug 3.390 kWh/Jahr (Balkendiagramm in [2]). Der Stromverbrauch im 1. Halbjahr 2025 betrug 1.470 kWh (Tabellenzeile in [3]). Der prognostizierte Jahresverbrauch 2025 betrug ca. 3.100 kWh (Tabellenzeile in [7]).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search_images, search
- Zitiert: [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 2, [3] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1, [7] 05_Strom_Zwischenablesung_Info_2025.pdf S. 1

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P2 Agent** (224.9 s, answer): Die Stromabrechnung 2024 stimmt nicht mit den Vertragspreisen überein. Der Rechnungsbetrag für die Stromlieferung 2024 beträgt 1.189,00 EUR, während der Vertrag eine eingeschränkte Preisgarantie bis 31.12.2024 vorsieht. Der Vertrag enthält auch eine Anpassung der Strompreise zum 01.01.2025, bei der der monatliche Abschlag auf 115,00 EUR brutto (96,64 EUR netto zzgl. 18,36 EUR USt.) angepasst wird.

- Fakten fehlen: Abrechnung korrekt; Urteil: nein (erwartet ja); Lücke benannt: nein; Tools: search

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P2 Agent** (633.6 s, context_limit): Es tut mir leid, aber ich kann keine Antwort geben, da ich keine Werkzeugaufrufe mehr habe. Ich bin jedoch bereit, eine Antwort zu geben, wenn du mir erlaubst, die Unterlagen noch einmal zu überprüfen.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search, search, search_images

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (295.9 s, answer): Es gibt Unterlagen für die Jahre 2024, 2025 und 2026. Ich habe bereits alle relevanten Treffer gefunden.

- Fakten fehlen: Wohnflächenanteil, Anteil Betriebskosten 2025, Guthaben; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: search, search

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P2 Agent** (213.7 s, answer): Die Gasabrechnung 2026 ist korrekt.

Der Rechnungsbetrag für die Erdgaslieferung 2026 beträgt 1.367,99 EUR brutto (Tabelle [2]). Der monatliche Abschlag ab 15.02.2027 beträgt 125,00 EUR brutto (Tabelle [1]). Der Preis wurde zum 01.01.2026 gesenkt, da die Erstvertragslaufzeit endete (Text [8]).

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: ja (erwartet nein); Lücke benannt: nein; Tools: search
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [2] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [8] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P2 Agent** (165.8 s, answer): Dein Anteil an den Betriebskosten 2026 beträgt 1.963,28 EUR brutto (26,28 %).

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: - (erwartet nein); Lücke benannt: nein; Tools: search

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P2 Agent** (269.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents, search

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P2 Agent** (297.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents, search_images

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P2 Agent** (233.0 s, answer): Der abgerechnete Gasverbrauch 2025 ist 1.200 m³, wie in [1] angegeben. Der Zählerstand am 01.01.2025 war 8.120 m³ und am 31.12.2025 war er 9.320 m³, was einem Gesamtverbrauch von 1.200 m³ entspricht. Der Rechnungsbetrag für die Erdgaslieferung 2025 beträgt 1.555,43 EUR, wie in [2] angegeben.

Die Frage, ob der abgerechnete Gasverbrauch 2025 zu den Zählerständen passt, kann also mit Ja beantwortet werden.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: search
- Zitiert: [1] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1, [2] 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (174.0 s, answer): Dein aktueller monatlicher Stromabschlag beträgt 120,00 EUR brutto (11 Abschläge von Februar bis Dezember 2026, jeweils zum 15. des Monats).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P2 Agent** (170.7 s, answer): Die Kündigungsfrist für den Stromvertrag beträgt 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform, danach unbefristet mit 1 Monat Frist kündbar.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
