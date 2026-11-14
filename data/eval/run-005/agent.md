# Agentenlauf (2026-11-14)

Modell: `llama3.1:8b`. Prüfungen sind grob (siehe M6 für die Metriken).

| Frage | Tools erwartet | Tools gerufen | Tools ok | Quellen fehlen | Zahlen fehlen | Lücke benannt | Ende | Aufrufe | Sekunden |
|---|---|---|---|---|---|---|---|---|---|
| S2 | search_tables | search_tables | ja | 0 | Arbeitspreis brutto, Grundpreis brutto | - | answer | 1 | 183.3 |
| G1 | search_tables, calculate | search_documents | nein | 1 | Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet | - | answer | 1 | 66.2 |
| N1 | list_documents | search_tables, list_documents | ja | 0 | - | ja | answer | 2 | 32.9 |
| S4 | search_images | search_tables, list_documents, search_tables, calculate, calculate, calculate | nein | 0 | Stromverbrauch 2022, Stromverbrauch 2023 | - | tool_limit | 6 | 301.4 |

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

**Antwort:** Der Arbeitspreis beträgt 29,24 Cent pro Kilowattstunde (kWh) und der Grundpreis 9,66 Euro pro Monat.

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

Werkzeugaufrufe:
- search_tables({'doc_type': 'contract', 'query': 'Arbeitspreis und Grundpreis Stromvertrag', 'utility_type': 'electricity'}) → ok, Treffer [1, 2, 3, 4, 5], 1.44 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 1997 | 108.658256 | 18 | 42 | 129.54 |
| 2 | 1257 | 44.862656 | 28 | 37 | 52.33 |

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

**Antwort:** Dazu liegen in den Unterlagen keine Angaben vor.

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.
Nicht gefundene Quellen: 01_electricity_suedvolt/03_Strom_Preisanpassung_SuedVolt_2025.pdf

Werkzeugaufrufe:
- search_documents({'utility_type': 'electricity', 'year': '2025', 'doc_type': 'bill', 'query': 'neuer Arbeitspreis in Stromabrechnung 2025'}) → ok, Treffer [1, 2, 3, 4, 5], 0.1 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 2008 | 4.842686 | 415 | 52 | 18.37 |
| 2 | 1253 | 45.072089 | 28 | 14 | 47.7 |

## N1: Wie hoch war meine Stromrechnung 2023?

**Antwort:** Dazu liegen in den Unterlagen keine Angaben vor.

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

Werkzeugaufrufe:
- search_tables({'utility_type': 'electricity', 'year': '2023', 'doc_type': 'bill', 'query': 'Stromrechnung 2023'}) → ok, Treffer [], 0.04 s
- list_documents({'doc_type': 'bill', 'query': 'Stromrechnung 2023', 'utility_type': 'electricity', 'year': '2023'}) → ok, Treffer [], 0.0 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 1994 | 2.760438 | 722 | 46 | 14.67 |
| 2 | 563 | 6.375633 | 88 | 39 | 13.04 |
| 4 | 643 | 2.87847 | 223 | 14 | 5.13 |

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

**Antwort:** Der Stromverbrauch für 2022 und 2023 ist nicht in den Unterlagen vermerkt. Es gibt jedoch Informationen über den Stromverbrauch für 2024 und 2025.

Für 2024 beträgt der Stromverbrauch 1.189,00 EUR (Treffer [3]) und für 2025 beträgt der Stromverbrauch 1.379,30 EUR (Treffer [1]). Der Nachzahlungsbetrag für 2024 beträgt 34,00 EUR (Treffer [4]).

Es ist nicht möglich, den Stromverbrauch für 2022 und 2023 genau zu bestimmen, da diese Informationen nicht in den Unterlagen enthalten sind.

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

Werkzeugaufrufe:
- search_tables({'utility_type': 'electricity', 'year': '2022', 'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023'}) → ok, Treffer [], 0.04 s
- list_documents({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity'}) → ok, Treffer [], 0.0 s
- search_tables({'doc_id': 'SV-2024-99104', 'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity'}) → ok, Treffer [1, 2, 3, 4, 5], 0.07 s
- calculate({'a': '1.379,30', 'b': '1.265,00'}) → FEHLER, Treffer [], 0.0 s
- calculate({'a': '1.379,30', 'b': '1.265,00'}) → FEHLER, Treffer [], 0.0 s
- calculate({'a': '1.379,30', 'b': '1.265,00'}) → FEHLER, Treffer [], 0.0 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 1998 | 88.939379 | 22 | 50 | 101.7 |
| 2 | 575 | 7.087299 | 81 | 38 | 13.62 |
| 4 | 735 | 7.047654 | 104 | 49 | 15.63 |
| 6 | 1402 | 38.035424 | 37 | 30 | 43.68 |
| 8 | 1472 | 7.17566 | 205 | 27 | 12.26 |
| 10 | 1542 | 5.537641 | 278 | 27 | 11.01 |
| 12 | 1621 | 69.598879 | 23 | 156 | 103.42 |
