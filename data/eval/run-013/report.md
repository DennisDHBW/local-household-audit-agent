# Evaluation run-013 (2026-11-16)

Modell: `llama3.1:8b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 5/14 (36 %) |
| Zahlen/Fakten gefunden | 7/27 (26 %) |
| Zitate auf erwartete Quelle (Präzision) | 1/4 (25 %) |
| Erwartete Quellen zitiert (Recall) | 1/18 (6 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/4 (0 %) |
| Ablenker im Kontext | 1/110 (1 %) |
| Tool-Wahl korrekt | 7/14 (50 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 23 / 5 |
| Negativfragen erkannt | 1/2 (50 %) |
| Fehler erkannt | 2/3 (67 %) |
| Fehlalarme | 0/3 (0 %) |
| Sekunden je Frage (Mittel / Median) | 314.3 / 297.9 |
| Prompt-Token je Frage (Mittel) | 8536 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| S1 | ✓ 3/3 |
| S2 | ✗ 0/2 |
| S3 | ✓ 1/1 |
| S4 | ✗ 0/2 |
| S5 | ✗ 0/2 |
| G1 | ✗ 0/3 |
| G2 | ✗ 0/3 |
| G3 | ✗ 0/3 |
| G4 | ✗ 0/3 |
| N1 | ✓ |
| N2 | ✗ |
| Z1 | ✗ 1/3 |
| Z2 | ✓ 1/1 |
| Z3 | ✓ 1/1 |

## S1: Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?

Erwartet: 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat Frist (unbefristet).

**P2 Agent** (185.5 s, answer): Die Kündigungsfrist für den Gasvertrag beträgt 6 Wochen zum Ablauf der Erstvertragslaufzeit in Textform, anschließend unbefristet mit 1 Monat Kündigungsfrist. Die Erstvertragslaufzeit beträgt 24 Monate, also bis zum 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

**P2 Agent** (202.2 s, answer): Laut Stromvertrag gelten folgende Preise:

* Arbeitspreis: 29,24 ct/kWh (Netto)
* Grundpreis: 115,97 EUR/Jahr (Netto) oder 130,08 EUR/Jahr (Netto) ab 01.01.2025

- Fakten fehlen: Arbeitspreis brutto, Grundpreis brutto; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S3: Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?

Erwartet: 74 m³ (Zählerstand 386 m³ am Jahresende minus 312 m³ am Jahresanfang).

**P2 Agent** (165.7 s, answer): Der Wasserverbrauch 2025 laut Zählerständen beträgt 74 m³.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

**P2 Agent** (330.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Stromverbrauch 2022, Stromverbrauch 2023; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search_images, list_documents, list_documents, search

## S5: Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?

Erwartet: Ja, der Rechnungsbetrag von 1.189,00 EUR ist mit den Vertragspreisen und dem Neukundenbonus konsistent.

**P2 Agent** (408.5 s, answer): Ich benötige den Wert für die geleisteten Abschlagszahlungen. Ich werde nach diesem Wert suchen.

{"name": "search", "parameters": {"query":"geleistete Abschlagszahlungen 2024","utility_type":"electricity"}}

- Fakten fehlen: Rechnungsbetrag 2024, Abrechnung korrekt; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: search, search

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.

**P2 Agent** (394.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet; Urteil: - (erwartet nein); Lücke benannt: ja; Tools: search, search, search_images

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (371.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wohnflächenanteil, Anteil Betriebskosten 2025, Guthaben; Urteil: - (erwartet ja); Lücke benannt: ja; Tools: search, search, search_images, list_documents

## G3: Ist die Gasabrechnung 2026 korrekt?

Erwartet: Nein. Abgerechnet wurde mit z-Zahl 1,0000 statt 0,9560 (wie 2024 und 2025); richtig wären 1.060 m³ × 0,9560 × 11,150 kWh/m³ = 11.299 kWh statt 11.819 kWh, das sind 51,74 EUR zu viel.

**P2 Agent** (442.3 s, answer): Die Abrechnung 2026 stimmt nicht mit dem Vertrag überein.

Der Rechnungsbetrag für die Erdgaslieferung 2026 beträgt 1.367,99 EUR brutto (Tabelle [2]).

Der monatliche Abschlag ab 15.02.2027 beträgt 125,00 EUR brutto (Tabelle [1]).

Die Abzüglich geleisteter Abschlagszahlungen (11 × 125,00 EUR, Feb–Dez 2026) beträgt -1.375,00 EUR (Tabelle [10]).

Der Rechnungsbetrag ist um 1,00 EUR (1.367,99 - 1.367,99) niedriger als der Betrag Brutto (192,00 EUR) in der Tabelle [11].

Die Abrechnung 2026 ist um 1,00 EUR niedriger als der Betrag Brutto (192,00 EUR) in der Tabelle [11].

- Fakten fehlen: Korrekte z-Zahl, Korrekte Energiemenge, Zu viel berechnet; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: search, search
- Zitiert: [1] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [2] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [10] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1, [11] 29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf S. 1

## G4: Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet?

Erwartet: Nein. Abgerechnet wurden 82 m² (26,28 %) statt der im Mietvertrag vereinbarten 78 m² (25 %); richtig wären 25 % von 7.470,00 EUR = 1.867,50 EUR statt 1.963,28 EUR.

**P2 Agent** (695.9 s, tool_limit): Es tut mir leid, aber ich konnte die Abweichung nicht berechnen, da ich keine gültigen Argumente für den calculate-Aufruf hatte.

Der Sollwert für Ihren Anteil an den Betriebskosten 2026 beträgt 1.963,28 EUR (26,28 %). Der Abzug der geleisteten Betriebskostenvorauszahlungen ergibt einen negativen Betrag von -1.920,00 EUR.

Ich konnte keine Abweichung zwischen Soll- und Istwert berechnen, da die notwendigen Werte nicht in den Unterlagen enthalten sind.

- Fakten fehlen: Wohnfläche laut Mietvertrag, Abgerechnete Wohnfläche, Korrekter Anteil; Urteil: nein (erwartet nein); Lücke benannt: ja; Tools: search, list_documents, search, search

## N1: Wie hoch war meine Stromrechnung 2023?

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

**P2 Agent** (284.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents, search, search_images

## N2: Welchen Grundpreis zahle ich für Fernwärme?

Erwartet: Es gibt keinen Fernwärmevertrag; die Wohnung wird mit einer Gasetagenheizung beheizt.

**P2 Agent** (267.9 s, answer): Der Grundpreis für Fernwärme beträgt 10,84 EUR brutto (inkl. 19 % USt.) pro Monat ab 01.01.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search, list_documents, search

## Z1: Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?

Erwartet: Ja. 9.320 − 8.120 = 1.200 m³; 1.200 m³ × 0,9560 × 11,150 kWh/m³ ergeben 12.791 kWh.

**P2 Agent** (311.5 s, answer): Da wir bereits wissen, dass der abgerechnete Gasverbrauch 2025 1.200 m³ beträgt, müssen wir den Sollwert ermitteln. Wir wissen, dass der Zählerstand am 01.01.2025 8.120 m³ betrug und am 31.12.2025 9.320 m³. Der Gesamtverbrauch ist also 9.320 - 8.120 = 1.200 m³.

Der Sollwert ist also 1.200 m³, was mit dem abgerechneten Verbrauch übereinstimmt. Es gibt also keine Abweichung.

- Fakten fehlen: z-Zahl, Energiemenge; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: search, search

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (172.0 s, answer): Dein aktueller monatlicher Stromabschlag beträgt 120,00 EUR brutto (11 Abschläge von Februar bis Dezember 2026, jeweils zum 15. des Monats).

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search

## Z3: Mit welcher Frist kann ich meinen Stromvertrag kündigen?

Erwartet: Nach der Erstlaufzeit (bis 31.12.2024) jederzeit mit 1 Monat Frist; die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu.

**P2 Agent** (168.6 s, answer): Die Kündigungsfrist für den Stromvertrag beträgt 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform, danach unbefristet mit 1 Monat Frist kündbar.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: search
