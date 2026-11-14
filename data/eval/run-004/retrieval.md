# Retrieval-Vergleich (Top-5)

| Konfiguration | Datei gefunden | Seite gefunden | MRR (Datei) | Ablenker-Treffer | leere Ergebnisse |
|---|---|---|---|---|---|
| plain | 9/10 | 9/10 | 0.683 | 4/60 | 0 |
| boost | 9/10 | 9/10 | 0.683 | 3/60 | 0 |
| filter | 9/10 | 9/10 | 0.733 | 0/55 | 1 |
| filter+boost | 9/10 | 9/10 | 0.733 | 0/55 | 1 |
| filter+boost, no summaries | 8/10 | 8/10 | 0.633 | 0/55 | 1 |
| filter+boost, no headless text | 9/10 | 9/10 | 0.733 | 0/55 | 1 |

## Rang der erwarteten Quelle (Datei / Seite)

| Frage | plain | boost | filter | filter+boost | filter+boost, no summaries | filter+boost, no headless text |
|---|---|---|---|---|---|---|
| S1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| S2 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | ✗ / ✗ | 2 / 2 |
| S3 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| S4 | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ |
| S5 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| G1 | 2 / 2 | 2 / 2 | 1 / 1 | 1 / 1 | 2 / 2 | 1 / 1 |
| G2 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| N1 | – | – | – | – | – | – |
| N2 | – | – | – | – | – | – |
| Z1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| Z2 | 3 / 3 | 3 / 3 | 3 / 3 | 3 / 3 | 3 / 3 | 3 / 3 |
| Z3 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 |

## Treffer der Konfiguration „filter+boost“

**S1** (standard)
- 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S.1 table_row 0.749 × 1.5 = 1.123
- 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S.1 table_summary 0.727 × 1.5 = 1.090
- 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S.1 table_row 0.694 × 1.5 = 1.042
- 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S.1 table_row 0.682 × 1.5 = 1.023
- 07_Gas_Liefervertrag_NeckarEnergie_2024.pdf S.1 text 0.680 × 1.5 = 1.020

**S2** (standard)
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 table_summary 0.712 × 1.5 = 1.068
- 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S.1 table_summary 0.690 × 1.5 = 1.035
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 text 0.673 × 1.5 = 1.009
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.668 × 1.5 = 1.002
- 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S.1 table_row 0.660 × 1.5 = 0.990

**S3** (standard)
- 15_Wasser_Jahresbescheid_2025_SWM.pdf S.1 table_summary 0.768 × 1.5 = 1.151
- 15_Wasser_Jahresbescheid_2025_SWM.pdf S.1 table_row 0.731 × 1.5 = 1.097
- 15_Wasser_Jahresbescheid_2025_SWM.pdf S.1 table_row 0.719 × 1.5 = 1.078
- 15_Wasser_Jahresbescheid_2025_SWM.pdf S.1 table_summary 0.707 × 1.5 = 1.061
- 15_Wasser_Jahresbescheid_2025_SWM.pdf S.1 table_summary 0.696 × 1.5 = 1.044

**S4** (standard)
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 table_summary 0.726 × 1.5 = 1.089
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 table_row 0.725 × 1.5 = 1.088
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 text 0.723 × 1.5 = 1.085
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 table_row 0.723 × 1.5 = 1.084
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.721 × 1.5 = 1.081

**S5** (standard)
- 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S.1 table_summary 0.762 × 1.5 = 1.143
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.756 × 1.5 = 1.134
- 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S.1 table_row 0.752 × 1.5 = 1.128
- 02_Strom_Begruessung_Abschlagsplan_2024.pdf S.1 table_summary 0.741 × 1.5 = 1.111
- 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S.1 table_row 0.734 × 1.5 = 1.100

**G1** (edge_case)
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 table_summary 0.710 × 1.5 = 1.065
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 text 0.694 × 1.5 = 1.040
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.692 × 1.5 = 1.038
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 table_summary 0.691 × 1.5 = 1.037
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 text 0.683 × 1.5 = 1.025

**G2** (edge_case)
- 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S.1 table_row 0.758 × 1.5 = 1.136
- 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S.1 table_summary 0.756 × 1.5 = 1.134
- 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S.1 table_row 0.734 × 1.5 = 1.100
- 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S.1 table_row 0.727 × 1.5 = 1.091
- 19_Nebenkostenabrechnung_2025_Hausverwaltung.pdf S.1 table_summary 0.714 × 1.5 = 1.071

**N1** (negative)
- 04_Strom_Jahresabrechnung_2024_SuedVolt.pdf S.1 table_summary 0.708 × 1.5 = 1.062
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_row 0.706 × 1.5 = 1.059
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.704 × 1.5 = 1.056
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 table_row 0.703 × 1.5 = 1.055
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 text 0.702 × 1.5 = 1.054

**N2** (negative)
- (keine Treffer)

**Z1** (additional)
- 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S.1 table_row 0.758 × 1.5 = 1.136
- 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S.1 table_summary 0.736 × 1.5 = 1.104
- 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S.1 table_row 0.730 × 1.5 = 1.094
- 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S.1 table_row 0.727 × 1.5 = 1.090
- 10_Gas_Jahresabrechnung_2025_NeckarEnergie.pdf S.1 table_summary 0.720 × 1.5 = 1.080

**Z2** (additional)
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 text 0.721 × 1.5 = 1.081
- 05_Strom_Zwischenablesung_Info_2025.pdf S.1 text 0.684 × 1.5 = 1.026
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 text 0.683 × 1.5 = 1.025
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 table_summary 0.682 × 1.5 = 1.022
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 text 0.681 × 1.5 = 1.021

**Z3** (additional)
- 03_Strom_Preisanpassung_SuedVolt_2025.pdf S.1 text 0.718 × 1.5 = 1.077
- 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S.1 table_row 0.712 × 1.5 = 1.068
- 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S.1 table_summary 0.699 × 1.5 = 1.049
- 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S.1 table_row 0.686 × 1.5 = 1.028
- 06_Strom_Jahresabrechnung_2025_SuedVolt.pdf S.1 table_summary 0.677 × 1.5 = 1.015

