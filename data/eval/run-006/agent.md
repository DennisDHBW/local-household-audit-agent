# Agentenlauf (2026-11-14)

Modell: `llama3.1:8b`. Prüfungen sind grob (siehe M6 für die Metriken).

| Frage | Tools erwartet | Tools gerufen | Tools ok | Quellen fehlen | Zahlen fehlen | Lücke benannt | Ende | Aufrufe | Sekunden |
|---|---|---|---|---|---|---|---|---|---|
| S2 | search_tables | search_tables | ja | 0 | - | - | answer | 1 | 191.9 |
| G1 | search_tables, calculate | search_documents, search_documents | nein | 1 | Angekündigter Arbeitspreis, Abgerechneter Arbeitspreis, Zu viel berechnet | - | answer | 2 | 266.1 |
| N1 | list_documents | search_tables, list_documents | ja | 0 | - | ja | answer | 2 | 35.6 |
| S4 | search_images | search_tables, list_documents, search_tables, search_tables, calculate, search_tables | nein | 0 | Stromverbrauch 2022, Stromverbrauch 2023 | - | tool_limit | 6 | 421.3 |

## S2: Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?

**Antwort:** Der Arbeitspreis beträgt 34,80 ct/kWh (Brutto) und der Grundpreis 11,50 EUR/Monat (Brutto).

Erwartet: Arbeitspreis 34,80 ct/kWh und Grundpreis 11,50 EUR/Monat (jeweils brutto).

Werkzeugaufrufe:
- search_tables({'doc_type': 'contract', 'query': 'Arbeitspreis und Grundpreis Stromvertrag', 'utility_type': 'electricity'}) → ok, Treffer [1, 2, 3, 4, 5], 0.63 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 2044 | 118.328699 | 17 | 42 | 139.04 |
| 2 | 1254 | 45.48581 | 28 | 36 | 52.21 |

## G1: Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?

**Antwort:** Es gibt eine Stromabrechnung für 2025. Der neue monatliche Abschlag beträgt ab 15.02.2026 jeweils 120,00 EUR brutto.

Erwartet: Nein. Angekündigt waren 38,20 ct/kWh, abgerechnet wurden 39,50 ct/kWh; bei 3.100 kWh sind das 40,30 EUR zu viel.
Nicht gefundene Quellen: 01_electricity_suedvolt/03_Strom_Preisanpassung_SuedVolt_2025.pdf

Werkzeugaufrufe:
- search_documents({'doc_type': 'bill', 'query': 'neuer Arbeitspreis in Stromabrechnung 2025', 'utility_type': 'electricity', 'year': '2025'}) → ok, Treffer [1, 2, 3, 4, 5], 0.07 s
- Rückfrage: Antwort „keine Angaben“ nach zu wenigen Suchen
- search_documents({'doc_type': 'bill', 'query': 'neuer Arbeitspreis in Stromabrechnung 2025', 'utility_type': 'electricity', 'year': '2025'}) → ok, Treffer [1, 2, 3, 4, 5], 0.07 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 2055 | 4.967887 | 414 | 52 | 19.12 |
| 2 | 1300 | 50.127563 | 26 | 14 | 52.79 |
| 4 | 2901 | 110.197095 | 26 | 52 | 128.19 |
| 6 | 2146 | 53.757464 | 40 | 44 | 65.81 |

## N1: Wie hoch war meine Stromrechnung 2023?

**Antwort:** Dazu liegen in den Unterlagen keine Angaben vor.

Erwartet: Liegt nicht vor, da die Belieferung erst am 01.01.2024 begann; nur der Verbrauch 2023 (3.390 kWh) ist aus dem Diagramm bekannt.

Werkzeugaufrufe:
- search_tables({'doc_type': 'bill', 'query': 'Stromrechnung 2023', 'utility_type': 'electricity', 'year': '2023'}) → ok, Treffer [], 0.07 s
- list_documents({'doc_type': 'bill', 'query': 'Stromrechnung 2023', 'utility_type': 'electricity', 'year': '2023'}) → ok, Treffer [], 0.0 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 2041 | 2.946875 | 693 | 46 | 16.59 |
| 2 | 610 | 6.943275 | 88 | 39 | 13.64 |
| 4 | 690 | 3.084651 | 224 | 14 | 5.34 |

## S4: Wie hoch war der Stromverbrauch 2022 und 2023?

**Antwort:** Es tut mir leid, aber ich konnte keine Informationen über den Stromverbrauch 2022 und 2023 finden. Die Belege, die ich hatte, beziehen sich auf die Jahre 2024 und 2025. Es scheint, dass die Unterlagen für die Jahre 2022 und 2023 nicht vorhanden sind.

Erwartet: 3.480 kWh (2022) und 3.390 kWh (2023); die Werte stehen nur im Diagramm.

Werkzeugaufrufe:
- search_tables({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity', 'year': '2022'}) → ok, Treffer [], 0.08 s
- list_documents({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity'}) → ok, Treffer [], 0.0 s
- search_tables({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity', 'doc_id': 'SV-2024-99104'}) → ok, Treffer [1, 2, 3, 4, 5], 0.06 s
- search_tables({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity', 'doc_id': 'SV-2024-99104'}) → ok, Treffer [1, 2, 3, 4, 5], 0.1 s
- calculate({'e': '1.155,00', 'a': '1.379,30', 'b': '1.189,00', 'c': '34,00', 'd': '1.265,00'}) → FEHLER, Treffer [], 0.0 s
- search_tables({'doc_type': 'bill', 'query': 'Stromverbrauch 2022 und 2023', 'utility_type': 'electricity', 'doc_id': 'SV-2024-99104'}) → ok, Treffer [1, 2, 3, 4, 5], 0.07 s

| Modellaufruf | Prompt-Token | Prefill s | Token/s | Erzeugt | Gesamt s |
|---|---|---|---|---|---|
| 0 | 2045 | 100.521126 | 20 | 50 | 114.06 |
| 2 | 622 | 7.536062 | 83 | 38 | 14.36 |
| 4 | 782 | 7.594497 | 103 | 49 | 16.15 |
| 6 | 1353 | 36.005673 | 38 | 49 | 46.1 |
| 8 | 1924 | 33.911279 | 57 | 58 | 49.16 |
| 10 | 2014 | 6.01004 | 335 | 49 | 18.95 |
| 12 | 2594 | 139.831598 | 19 | 73 | 162.19 |
