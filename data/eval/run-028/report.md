# Evaluation run-028 (2026-11-21)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

B0-Kontext: 6 Dateien vollständig, teilweise: -, fehlend: 29; ca. 6727 von 6961 Token.

| Metrik | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| Richtig (gesamt) | 1/8 (12 %) | 3/8 (38 %) | 5/8 (62 %) |
| Zahlen/Fakten gefunden | 0/11 (0 %) | 3/11 (27 %) | 6/11 (55 %) |
| Zitate auf erwartete Quelle (Präzision) | 0/1 (0 %) | 3/6 (50 %) | 6/6 (100 %) |
| Erwartete Quellen zitiert (Recall) | 0/11 (0 %) | 3/11 (27 %) | 5/11 (45 %) |
| Erfundene Belegnummern | 0 | 0 | 3 |
| Ablenker in Zitaten | 0/1 (0 %) | 0/6 (0 %) | 0/6 (0 %) |
| Ablenker im Kontext | 0/64 (0 %) | 0/54 (0 %) | 0/20 (0 %) |
| Tool-Wahl korrekt | - | - | 5/8 (62 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | - | - | 4 / 0 |
| Negativfragen erkannt | 1/1 (100 %) | 0/1 (0 %) | 1/1 (100 %) |
| Fehler erkannt | - | - | - |
| Fehlalarme | 0/2 (0 %) | 0/2 (0 %) | 0/2 (0 %) |
| Sekunden je Frage (Mittel / Median) | 110.7 / 15.1 | 92.8 / 84.5 | 194.6 / 178.9 |
| Prompt-Token je Frage (Mittel) | 7698 | 1340 | 8312 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| T1 | ✗ 0/1 | ✓ 1/1 | ✓ 1/1 |
| T2 | ✗ 0/1 | ✗ 0/1 | ✓ 1/1 |
| T3 | ✗ 0/1 | ✓ 1/1 | ✗ 1/1 |
| T4 | ✗ 0/1 | ✓ 1/1 | ✓ 1/1 |
| T5 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| T6 | ✗ 0/2 | ✗ 0/2 | ✗ 0/2 |
| T7 | ✓ | ✗ | ✓ |
| T8 | ✗ 0/2 | ✗ 0/2 | ✓ 2/2 |

## T1: Welche Kündigungsfrist gilt für den Heizstromvertrag?

Erwartet: 1 Monat zum Ende der Erstlaufzeit (31.12.2024), danach jederzeit mit 1 Monat Frist.

**B0 Volltext** (476.8 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Kündigungsfrist Heizstrom; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (85.6 s, answer): Die Kündigungsfrist für den Heizstromvertrag beträgt 1 Monat zum Ablauf der Erstvertragslaufzeit in Textform; danach unbefristet mit 1 Monat Frist kündbar. Dies ist aus dem Auszug [1] ersichtlich.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1

**P2 Agent** (240.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor. Es gibt Hinweise darauf, dass die Kündigungsfrist 1 Monat beträgt, wenn zum Ablauf der Erstvertragslaufzeit gekündigt wird, danach ist der Vertrag unbefristet mit einer Kündigungsfrist von 1 Monat.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: search, list_documents, search

## T2: Wie viel Wasser wurde 2026 verbraucht?

Erwartet: 72 m³ (Zählerstand 386 auf 458 m³).

**B0 Volltext** (12.5 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasserverbrauch 2026; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (67.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasserverbrauch 2026; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (117.0 s, answer): Der Wasserverbrauch im Jahr 2026 betrug 72 m³ [1]. Dies wird in der Jahresbescheidung der Wasserabrechnung 2026 auf Seite 1 vermerkt.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: get_facts
- Zitiert: [1] 35_Wasser_Jahresbescheid_2026_SWM.pdf S. 1

## T3: Wurde in der Gasabrechnung 2026 der neue Arbeitspreis berechnet?

Erwartet: Ja, 9,95 ct/kWh laut Preisanpassung ab 01.01.2026. Die Rechnung hat aber einen anderen Fehler (z-Zahl 1,0000 statt 0,9560).

**B0 Volltext** (16.0 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Arbeitspreis 2026; Urteil: - (erwartet ja); Lücke benannt: ja

**P1 Pipeline** (83.5 s, answer): Ja, in der Gasabrechnung 2026 wird der neue Arbeitspreis berechnet. Dies ist belegt durch den Abschlagsplan für das Lieferjahr 2026 in [4], der den neuen Arbeitspreis von 9,95 ct/kWh brutto verwendet.

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein
- Zitiert: [4] 11_Gas_Abschlagsplan_2026_NeckarEnergie.pdf S. 1

**P2 Agent** (270.4 s, answer): Durch die Preisanpassung wurde der neue Arbeitspreis für 2026 berechnet. [3] Der neue netto Arbeitspreis beträgt 8,36 ct/kWh [3], inklusive USt. 9,95 ct/kWh [3]. Dieser Wert wurde in der Gasabrechnung 2026 angewendet. [2]

- Fakten fehlen: -; Urteil: - (erwartet ja); Lücke benannt: nein; Tools: list_documents, search
- Zitiert: [2] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1, [3] 09_Gas_Preisanpassung_NeckarEnergie_2026.pdf S. 1

## T4: Wie hoch ist der monatliche Heizstromabschlag ab Februar 2026?

Erwartet: 105,00 EUR brutto (11 Abschläge Feb–Dez 2026).

**B0 Volltext** (29.7 s, answer): Der monatliche Heizstromabschlag ab Februar 2026 beträgt 120,00 EUR brutto, wie in Auszug [7] angegeben.

- Fakten fehlen: Heizstromabschlag 2026; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [7] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

**P1 Pipeline** (91.5 s, answer): Der monatliche Heizstromabschlag ab Februar 2026 beträgt 105,00 EUR brutto (inkl. 19 % USt.), wie aus [1] ersichtlich ist.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [1] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

**P2 Agent** (179.7 s, answer): Der monatliche Heizstromabschlag ab Februar 2026 beträgt 105,00 EUR [3].

Soll: 105,00 EUR/Monat
Ist: 105,00 EUR/Monat
Unterschied: 0,00 EUR
Auswirkung: 0,00 EUR

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: plan, get_facts
- Zitiert: [3] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## T5: Zeig mir den Wasserverbrauch der letzten Jahre als Diagramm.

Erwartet: 78 m³ (2024), 74 m³ (2025), 72 m³ (2026).

**B0 Volltext** (12.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasser 2024, Wasser 2025, Wasser 2026; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (98.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Wasser 2024, Wasser 2025, Wasser 2026; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (178.2 s, answer): Dazu liegen in den Unterlagen keine Angaben vor. [1-5]

- Fakten fehlen: Wasser 2024, Wasser 2025, Wasser 2026; Urteil: - (erwartet -); Lücke benannt: ja; Tools: list_documents

## T6: Ist die Wasserabrechnung 2025 in Ordnung?

Erwartet: Ja, Preise, Verbrauch (74 m³) und Vorauszahlungen passen; Gesamtkosten 459,10 EUR.

**B0 Volltext** (14.1 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Abrechnung korrekt, Gesamtkosten 2025; Urteil: - (erwartet ja); Lücke benannt: ja

**P1 Pipeline** (156.1 s, answer): Zur Wasserabrechnung 2025 finden wir zwei relevante Auszüge:

[2] 15_Wasser_Jahresbescheid_2025_SWM.pdf, S. 1, Tabellenzeile
Abzüglich geleistete Quartals-Vorauszahlungen (4 × 120,00 EUR in 2025): -480,00 EUR

[6] 12_Wasser_Anmeldebestaetigung_SWM_2024.pdf, S. 1, Tabellenzeile
Ihre vierteljährliche Vorauszahlung beträgt 120,00 EUR (fallsig jeweils zum 15.02., 15.05., 15.08. und 15.11. eines Jahres, Einzug per SEPA-Lastschrift von IBAN DE89 6745 0048 0012 3456 78).

Basierend auf diesen Informationen können wir die Abrechnung 2025 prüfen:

1. Die Vorauszahlungen von 120,00 EUR pro Quartal wurden in 2025 geleistet. Das ergibt insgesamt 480,00 EUR (4 × 120,00 EUR).

2. Der Abzug der Vorauszahlungen von 480,00 EUR in [2] stimmt mit den Vorauszahlungen von 120,00 EUR pro Quartal überein.

3. Es gibt keine weiteren Einzelheiten zur Wasserabrechnung 2025 in den anderen Auszügen.

Da wir keine weiteren Einzelheiten zur Wasserabrechnung 2025 haben, können wir nur bestätigen, dass die Vorauszahlungen korrekt abgezogen wurden. Es liegt in den Unterlagen keine spezifische Abrechnung für 2025 vor, die wir zur Prüfung verwenden könnten.

Zusammenfassend lässt sich sagen, dass die Vorauszahlungen in Ordnung sind, aber die spezifische Wasserabrechnung 2025 fehlt, um eine vollständige Prüfung durchzuführen.

- Fakten fehlen: Abrechnung korrekt, Gesamtkosten 2025; Urteil: - (erwartet ja); Lücke benannt: nein
- Zitiert: [2] 15_Wasser_Jahresbescheid_2025_SWM.pdf S. 1, [6] 12_Wasser_Anmeldebestaetigung_SWM_2024.pdf S. 1

**P2 Agent** (263.7 s, answer): Die Wasserabrechnung 2025 stimmt [1]. Der Soll-Verbrauch beträgt 1200 Liter, der Ist-Verbrauch 1150 Liter. Der Unterschied von 100 Liter hat keine finanziellen Auswirkungen, da der Preis von 0,02 EUR pro Liter [2] nicht in die Berechnung einfließt.

- Fakten fehlen: Abrechnung korrekt, Gesamtkosten 2025; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: plan
- Zitiert: [1] (unbekannt), [2] (unbekannt)

## T7: Was kostet bei mir die Kilowattstunde Fernwärme?

Erwartet: Dazu liegen keine Unterlagen vor; der Haushalt hat keinen Fernwärmevertrag.

**B0 Volltext** (13.4 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja

**P1 Pipeline** (76.4 s, answer): Der Preis für die Kilowattstunde Fernwärme lautet 24,10 ct/kWh [2]. Dies basiert auf der Abrechnung für den Zeitraum 01.01.2025 bis 31.12.2025.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein
- Zitiert: [2] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

**P2 Agent** (158.7 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: ja; Tools: plan, list_documents, search

## T8: Stelle die Stromkosten 2024 für Licht- und Heizstrom in einer Tabelle gegenüber.

Erwartet: Lichtstrom 1.189,00 EUR, Heizstrom 1.016,90 EUR.

**B0 Volltext** (309.9 s, answer): | Monat | Abrechnungsmonat | Nettobetrag | USt. (19%) | Bruttobetrag |
|-------|------------------|-------------|------------|--------------|
| 02    | Abschlag 01 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 03    | Abschlag 02 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 04    | Abschlag 03 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 05    | Abschlag 04 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 06    | Abschlag 05 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 07    | Abschlag 06 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 08    | Abschlag 07 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 09    | Abschlag 08 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 10    | Abschlag 09 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 11    | Abschlag 10 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |
| 12    | Abschlag 11 / 2024 | 88,24 EUR    | 16,76 EUR  | 105,00 EUR   |

**Gesamtsumme für 2024:**
- Nettobetrag: 1,066,39 EUR
- Umsatzsteuer:

- Fakten fehlen: Lichtstrom 2024, Heizstrom 2024; Urteil: - (erwartet -); Lücke benannt: nein

**P1 Pipeline** (83.3 s, answer): Dazu liegen in den Unterlagen keine Angaben vor.

- Fakten fehlen: Lichtstrom 2024, Heizstrom 2024; Urteil: - (erwartet -); Lücke benannt: ja

**P2 Agent** (148.2 s, answer): Die Stromkosten für 2024 sind in der folgenden Tabelle dargestellt:

| Stromart | 2024 | Wert |
|---|---|---|
| Heizstrom | [2024] | 1.016,90 EUR [1] |
| Lichtstrom | [2024] | 1.189,00 EUR [2] |

Die Tabelle zeigt die Kosten für Heiz- und Lichtstrom im Jahr 2024.

- Fakten fehlen: -; Urteil: - (erwartet -); Lücke benannt: nein; Tools: make_overview
- Zitiert: [1] 32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [2024] (unbekannt)
