# Evaluation run-024-smoke (2026-11-21)

Modell: `qwen2.5:7b`. Metriken deterministisch (concept.md 11.3, ADR-0011); Urteil ja/nein und Fakten sind Heuristiken (ISS-038).

| Metrik | P2 Agent |
|---|---|
| Richtig (gesamt) | 3/5 (60 %) |
| Zahlen/Fakten gefunden | 11/14 (79 %) |
| Zitate auf erwartete Quelle (Präzision) | 6/10 (60 %) |
| Erwartete Quellen zitiert (Recall) | 6/10 (60 %) |
| Erfundene Belegnummern | 0 |
| Ablenker in Zitaten | 0/10 (0 %) |
| Ablenker im Kontext | 0/36 (0 %) |
| Tool-Wahl korrekt | 4/5 (80 %) |
| Suchen mit eigenem Filter / davon schließen Quelle aus | 0 / 0 |
| Negativfragen erkannt | - |
| Fehler erkannt | 2/2 (100 %) |
| Fehlalarme | 0/1 (0 %) |
| Sekunden je Frage (Mittel / Median) | 218.2 / 215.7 |
| Prompt-Token je Frage (Mittel) | 7461 |

## Fragen × Varianten (✓/✗, gefundene Fakten)

| Frage | P2 Agent |
|---|---|
| G2 | ✓ 3/3 |
| Z2 | ✗ 0/1 |
| H2 | ✓ 3/3 |
| W1 | ✓ 3/3 |
| V1 | ✗ 2/4 |

## G2: Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?

Erwartet: Ja. 78 m² von 312 m² sind 25 %, 25 % von 7.320,00 EUR sind 1.830,00 EUR; abzüglich 1.920,00 EUR Vorauszahlungen ergibt sich ein Guthaben von 90,00 EUR.

**P2 Agent** (217.4 s, answer): Ja, die Betriebskosten-Rechnung 2025 stimmt mit Vertrag, Preisschreiben und Zählerständen überein. Ihr Anteil beträgt 25,00 % der Wohnfläche, was 78,00 m² entspricht [2]. Der berechnete Betrag lautet 1.830,00 EUR [3], und es besteht ein Guthaben von 90,00 EUR [6].

- Fakten fehlen: -; Urteil: ja (erwartet ja); Lücke benannt: nein; Tools: plan, check_bill
- Zitiert: [2] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [3] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1, [6] 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S. 1

## Z2: Wie hoch ist mein aktueller monatlicher Stromabschlag?

Erwartet: 120,00 EUR ab 15.02.2026, nicht die früheren 105,00 oder 115,00 EUR.

**P2 Agent** (137.9 s, answer): Dazu liegen in den Unterlagen keine Angaben vor. Es scheint, dass der Stromabschlag für das Jahr 2023 nicht in den verfügbaren Unterlagen aufgeführt ist. 

Wir könnten versuchen, dies im Vertrag oder in den Rechnungen zu suchen, aber bisher haben wir keine entsprechenden Unterlagen gefunden.

- Fakten fehlen: Aktueller Abschlag; Urteil: - (erwartet -); Lücke benannt: ja; Tools: list_documents

## H2: Ist die Heizstromabrechnung 2025 korrekt?

Erwartet: Nein. Laut Zählerständen (12.680 auf 16.100 kWh) wurden im NT 3.420 kWh verbraucht, abgerechnet sind 3.920 kWh; das sind 500 kWh und 120,50 EUR zu viel.

**P2 Agent** (215.0 s, answer): Nein, die Heizstrom-Rechnung 2025 stimmt nicht. Es gibt eine Abweichung im Verbrauch NT aus Zählerständen: Soll 3.420 kWh, Ist abgerechnet 3.920 kWh [10], was zu einem zusätzlichen Betrag von 120,50 EUR [10] führt.

Kurzfassung: Der Verbrauch NT wurde zu hoch abgerechnet [10], was zu einem zusätzlichen Betrag von 120,50 EUR [10] führt.

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [10] 34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf S. 1

## W1: Ist der Wasserbescheid 2026 korrekt?

Erwartet: Nein. Seit Q1/2026 beträgt die Vorauszahlung 125,00 EUR je Quartal, gezahlt wurden also 500,00 EUR; angerechnet sind nur 4 × 120,00 = 480,00 EUR. Das Guthaben ist um 20,00 EUR zu niedrig.

**P2 Agent** (215.7 s, answer): Nein, die Wasserbescheid-Rechnung 2026 stimmt nicht. Es wurden weniger Abschläge angerechnet als vereinbart, was 20,00 EUR zu Ihren Lasten auswirkt.

Zur Kurzfassung:
- Soll: 4 × 125,00 EUR = 500,00 EUR [11]
- Ist: 4 × 120,00 EUR = 480,00 EUR [11]
- Auswirkung: 20,00 EUR zu Ihren Lasten [10]

- Fakten fehlen: -; Urteil: nein (erwartet nein); Lücke benannt: nein; Tools: check_bill
- Zitiert: [10] 14_Wasser_Gebuehrenanpassung_2026_SWM.pdf S. 1, [11] 35_Wasser_Jahresbescheid_2026_SWM.pdf S. 1

## V1: Erstelle eine Grafik zum Stromverbrauch 2024 und 2025, getrennt nach Licht- und Heizstrom.

Erwartet: Lichtstrom 3.250 kWh (2024) und 3.100 kWh (2025); Heizstrom HT 620 und 580 kWh, NT 3.180 und 3.420 kWh laut Zählerständen.

**P2 Agent** (305.0 s, answer): Grafik erstellt: Verbrauch Lichtstrom 2024–2025 (verbrauch-lichtstrom-2024-2025.png, wird angehängt).

Plan:
1. make_chart Verbrauch Lichtstrom 2024-2025 [bereits erstellt]
2. check_bill Heizstrom 2024-2025
3. get_facts Heizstrom 2024-2025
4. make_overview Strom 2024-2025
5. list_documents Strom 2024-2025

Nächster Schritt: 
2. check_bill Heizstrom 2024-2025, um den Heizstromverbrauch zu überprüfen.

Ergebnis: 
- Lichtstrom 2024: 3.250 kWh [1] [2]
- Lichtstrom 2025: 3.100 kWh [3] [4]

Grafik zeigt den Verbrauch des Lichtstroms für 2024 und 2025 getrennt nach Zählerständen [1] [2] [3] [4]. Sie zeigt einen geringfügigen Rückgang des Lichtstromverbrauchs von 3.250 kWh im Jahr 2024 auf 3.100 kWh im Jahr 2025.

- Fakten fehlen: Heizstrom NT 2024, Heizstrom NT 2025; Urteil: - (erwartet -); Lücke benannt: nein; Tools: make_chart
- Zitiert: [1] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [2] 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S. 1, [3] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1, [4] 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S. 1
