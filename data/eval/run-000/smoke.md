# Smoke-Test run-000

Start: 2026-11-14T15:17:01+01:00 · num_ctx: 8192

## Geschwindigkeit

| Modell | Prompt-Tokens | Prefill (Tok/s) | Generierung (Tok/s) | Laden (s) | RAM (GB) |
|---|---|---|---|---|---|
| qwen2.5:7b | 592 | 18.9 | 5.0 | 12.9 | 5.46 |
| llama3.1:8b | 579 | 20.1 | 5.9 | 10.5 | 6.25 |
| llama3.2 | 594 | 45.9 | 12.5 | 5.5 | 3.12 |

## Prompt-Präfix-Wiederverwendung

- qwen2.5:7b: 1. Aufruf 507 Tokens, 2. Aufruf 502 Tokens → wiederverwendet: nein
- llama3.1:8b: 1. Aufruf 514 Tokens, 2. Aufruf 509 Tokens → wiederverwendet: nein

## Tool-Calling

### qwen2.5:7b: Werkzeug 80%, Argumente 80%

| Aufgabe | Werkzeug | Argumente | Werkzeug ok | Argumente ok | Sekunden |
|---|---|---|---|---|---|
| T1-clause | search_documents | `{'query': 'Kündigungsfrist', 'utility_type': 'gas', 'doc_type': 'contract'}` | ja | ja | 38 |
| T2-table | search_documents | `{'query': 'Arbeitspreis', 'doc_type': 'contract', 'utility_type': 'electricity'}` | nein | nein | 7 |
| T3-calc | calculate | `{'expression': '3100 * (0.395 - 0.382)'}` | ja | ja | 7 |
| T4-table-water | search_tables | `{'doc_type': 'bill', 'query': 'Wasserverbrauch 2025', 'utility_type': 'water'}` | ja | ja | 8 |
| T5-calc-percent | calculate | `{'expression': '100 * (1339 / 1379.30)'}` | ja | ja | 7 |

### llama3.1:8b: Werkzeug 80%, Argumente 80%

| Aufgabe | Werkzeug | Argumente | Werkzeug ok | Argumente ok | Sekunden |
|---|---|---|---|---|---|
| T1-clause | search_documents | `{'doc_type': 'contract', 'query': 'Kündigungsfrist Gasliefervertrag', 'utility_type': 'gas'}` | ja | ja | 42 |
| T2-table | search_documents | `{'utility_type': 'electricity', 'doc_type': 'contract', 'query': 'Arbeitspreis'}` | nein | nein | 7 |
| T3-calc | calculate | `{'expression': '3100 * (0.395 - 0.382)'}` | ja | ja | 6 |
| T4-table-water | search_tables | `{'utility_type': 'water', 'doc_type': 'bill', 'query': 'Wasserverbrauch 2025'}` | ja | ja | 8 |
| T5-calc-percent | calculate | `{'expression': '(1339 / 1379.30) * 100'}` | ja | ja | 6 |

## Embedding

- nomic-embed-text: 768 Dimensionen; Ähnlichkeit relevant 0.747 vs. irrelevant 0.550 → Ranking korrekt: ja

## Vision

- gemma3:4b, Bild `chart.png`, 78 s; erwartet [3480.0, 3390.0], gefunden [2022.0, 2023.0, 2024.0, 2.0, 2022.0, 3480.0, 1.0, 2023.0, 3390.0, 2024.0, 3250.0, 1900.0, 2.0, 3000.0, 3.0, 3900.0, 40.0, 2.0, 40.0, 2.0] → alle Sollwerte gefunden: ja

```text
Okay, hier ist eine Beschreibung des Diagramms, mit den jeweiligen Jahreswerten und Einheiten:

**Diagrammübersicht:**

Das Diagramm zeigt den Energieverbrauch (in kWh/Jahr) verschiedener Haushaltstypen über die Jahre 2022, 2023 und 2024. Zusätzlich werden Vergleichsgruppen für Single-, Zwei- und Dreiköpfige Haushalte dargestellt.

**Jahreswerte und Einheiten:**

*   **Vorjahr 2 (2022):** 3.480 kWh/Jahr
*   **Vorjahr 1 (2023):** 3.390 kWh/Jahr
*   **Abrechnungsjahr 2024:** 3.250 kWh/Jahr
*   **Single-Haushalt:** 1.900 kWh/Jahr
*   **2-Personen-Haushalt:** 3.000 kWh/Jahr
*   **3-Personen-Haushalt:** 3.900 kWh/Jahr

**Zusätzliche Anmerkungen:**

*   Das Diagramm ist nach dem deutschen Titel "Verbrauchsentwicklung & Vergleichsgruppen gemäß § 40 Abs. 2 EnWG" (Entwicklung des Energieverbrauchs und Vergleichsgruppen gemäß § 40 Absatz 2 der Energieeinsparver
```
