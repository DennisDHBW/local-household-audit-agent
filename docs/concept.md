# Projektidee: Energie- & Nebenkosten-Auditor

**Arbeitstitel:** local-household-audit-agent – Energie- & Nebenkosten-Auditor
**Kurzbeschreibung:** Ein lokal laufender KI-Agent, der Strom-, Gas-/Fernwärme-, Wasser- und Nebenkostenunterlagen eines Haushalts durchsucht, Verträge mit Abrechnungen abgleicht, Beträge nachrechnet und Auffälligkeiten mit genauer Quellenangabe (Dokument, Kapitel, Seite) meldet.

> Bezug: Alle Pflichtanforderungen stehen in `Anforderungen_Projekt_und_Ausarbeitung.md` (im Repo: `docs/requirements.md`). Engineering-Regeln: `CODING_STANDARDS.md`. Dieses Dokument zeigt, wie die Projektidee sie erfüllt. Querverweise in der Form „→ Anf. 5.5“ beziehen sich auf die Abschnitte dort.

---

## Inhaltsverzeichnis

1. [Problem & Use Case](#1-problem--use-case)
2. [Warum die Idee zur Vorlesung passt](#2-warum-die-idee-zur-vorlesung-passt)
3. [Abgleich mit den Pflichtanforderungen](#3-abgleich-mit-den-pflichtanforderungen)
4. [Dokumentenkorpus](#4-dokumentenkorpus)
5. [Vorverarbeitung & Datenstrukturen](#5-vorverarbeitung--datenstrukturen)
6. [Retrieval-Konzept](#6-retrieval-konzept)
7. [Agenten-Architektur & Tools](#7-agenten-architektur--tools)
8. [ReAct-Zyklen (Beispiele für die Ausarbeitung)](#8-react-zyklen-beispiele-für-die-ausarbeitung)
9. [Modellauswahl für die eigene Hardware](#9-modellauswahl-für-die-eigene-hardware)
10. [GraphRAG-Entscheidung](#10-graphrag-entscheidung)
11. [Test- & Evaluationskonzept (Testmodul)](#11-test--evaluationskonzept-testmodul)
12. [Risiken & Gegenmaßnahmen](#12-risiken--gegenmaßnahmen)
13. [Meilensteine mit Reverse-Engineering-Checkpoints](#13-meilensteine-mit-reverse-engineering-checkpoints)
14. [Vorschlag für die Gliederung der Ausarbeitung](#14-vorschlag-für-die-gliederung-der-ausarbeitung-58-seiten)
15. [Offene Entscheidungen](#15-offene-entscheidungen)

---

## 1. Problem & Use Case

**Problem:** Private Haushalte bekommen jedes Jahr mehrere Abrechnungen (Strom, Gas/Fernwärme, Wasser, Nebenkosten vom Vermieter). Ob diese Abrechnungen stimmen, prüft kaum jemand. Für eine Prüfung muss man Informationen aus **mehreren Dokumenten zusammenführen**:
- **Vertrag/Preisblatt:** vereinbarter Arbeitspreis (ct/kWh), Grundpreis (€/Jahr bzw. €/Monat), Preisgarantie, Laufzeit
- **Preisänderungsschreiben:** neuer Preis ab einem Stichtag
- **Jahresabrechnung:** Zählerstände, Verbrauch, abgerechnete Preise, Abschläge, Nachzahlung/Guthaben
- **Mietvertrag/Nebenkostenabrechnung:** Umlageschlüssel, Wohnfläche, Vorauszahlungen, Kostenarten

**Zielgruppe:** Mieter:innen und Eigentümer:innen, die ihre Unterlagen prüfen wollen, ohne sie bei einem Cloud-Dienst hochzuladen.

**Was der Agent leistet:**
1. Fragen zu den eigenen Unterlagen beantworten (z. B. „Welcher Arbeitspreis gilt laut Stromvertrag?“), immer mit Quellenangabe
2. Vertrag und Abrechnung abgleichen (vereinbarter vs. abgerechneter Preis)
3. Beträge nachrechnen (Verbrauch × Arbeitspreis + anteiliger Grundpreis, Differenz zu Abschlägen)
4. Jahre vergleichen (Verbrauchsentwicklung, auch aus Grafiken)
5. Auffälligkeiten melden, statt Urteile zu fällen (siehe Abgrenzung)

**Abgrenzung:** Der Agent liefert **keine Rechtsberatung**. Er meldet nachvollziehbare Abweichungen mit Belegen („Im Vertrag steht X, auf der Rechnung Y, die Differenz beträgt Z“). Die Bewertung bleibt beim Menschen. Das passt zum Evidence-First-Gedanken der Vorlesung.

**Warum lokal (→ Anf. 4.1):** Die Unterlagen enthalten sensible personenbezogene Daten: Name, Adresse, Zählernummern, Bankverbindung, Verbrauchsprofile (aus denen sich Anwesenheitsmuster ableiten lassen). Das ist ein starkes, konkretes DSGVO-Argument für eine vollständig lokale Lösung ohne Cloud-API.

---

## 2. Warum die Idee zur Vorlesung passt

| Vorlesungskonzept | Entsprechung im Use Case |
|---|---|
| Tiefe Überschriften-Hierarchien → `heading_stack`, Hierarchie-Prefix | Verträge und AGB (z. B. „§ 5 Preise > 5.2 Preisanpassung“) |
| Tabellen → `table_row` + Tabellen-Summary | Tarif-, Zählerstands-, Verbrauchs- und Kostentabellen in Jahresabrechnungen und Nebenkostenabrechnungen |
| Bilder → Vision-Captioning (`gemma3:4b`) + `search_images` | Vorjahres-Vergleichsgrafiken (Balkendiagramme), Verbrauchsverläufe, ggf. eingescannte Seiten |
| Agentisches Multi-Hop + `calculate` | Preis aus dem Vertrag → Verbrauch aus der Rechnung → Nachrechnen → Vergleich |
| Metadatenfilter & Hierarchie-Boost | Viele ähnliche Dokumente (mehrere Jahre, mehrere Sparten, Ablenkungsdokumente mit ähnlichem Vokabular) |
| Negativfragen | Fragen zu Daten, die nicht im Korpus liegen (z. B. Abrechnung eines fehlenden Jahres) |
| Evidence-First / Zitation | Prüfergebnis nur glaubwürdig, wenn Vertrags- und Rechnungsstelle angezeigt werden |

**Zwingende Agenten-Logik:** Eine typische Prüffrage braucht mindestens drei abhängige Schritte:
1. Den vereinbarten Arbeitspreis im **Vertragsdokument** suchen
2. Den abgerechneten Verbrauch und Preis in der **Rechnungstabelle** suchen
3. Mit `calculate` den Sollbetrag und die Differenz berechnen

Ein Standard-RAG holt in einem Durchgang die Top-k Chunks zur Frage. Er kann nicht gezielt nachsuchen, wenn ein Wert fehlt, und er kann nicht rechnen. Dass er an solchen Fragen scheitert, ist zunächst eine **Hypothese**. Sie soll im Testmodul durch einen Vergleich belegt werden (siehe Abschnitt 11), nicht einfach behauptet.

---

## 3. Abgleich mit den Pflichtanforderungen

| Anforderung | Umsetzung im Projekt |
|---|---|
| Lokal / offline | Ollama (LLM, Vision, Embeddings), ChromaDB auf der Festplatte, PyMuPDF; keine Cloud-API. Ein Cloud-Vergleich wird höchstens als abschaltbare Option eingebaut. |
| Modulare RAG-Pipeline | Parser → Strukturerkennung → Enrichment → typisiertes Chunking → Hierarchie-Prefix-Embedding → Retrieval mit Metadatenfilter + Hierarchie-Boost → Evidence-First → Antwort |
| Agentisch | ReAct-Loop mit Tool-Calling (Abschnitt 7), Multi-Hop-Nachsuche, Rechen-Tool, Selbstprüfung vor der finalen Antwort |
| Systematisch getestet | Testmodul mit eigenem Testset (Ground Truth inkl. eingebauter Fehler), RAGAS-Metriken, Vergleich mit Baselines (Abschnitt 11) |
| GraphRAG-Entscheidung | Begründet: kein vollständiges GraphRAG, stattdessen Verknüpfung über Metadaten (Abschnitt 10) |
| Testfragen 5/2/2 | Konkret formuliert in Abschnitt 11.2 |
| Reverse Engineering | Checkpoints je Meilenstein (Abschnitt 13) |

---

## 4. Dokumentenkorpus

### 4.1 Überblick
Der Korpus liegt vollständig synthetisch unter `dataset/` (30 PDFs, erzeugt mit WeasyPrint, mit Textebene; 28 Ausgangsdokumente plus die Fehlervarianten 29 und 30). Fiktiver Haushalt: Lukas Weber, Hauptstraße 42, 74821 Mosbach, 3-Zimmer-Wohnung mit 78 m² (Anteil 25 % an 312 m²), Gasetagenheizung, Zeitraum 2023–2027 (die Jahresabrechnungen 2026 tragen Daten im Januar bis März 2027).

| Ordner | Dokumente | Anbieter (fiktiv) | Rolle im Test |
|---|---|---|---|
| `01_electricity_suedvolt` | 01 Vertragsbestätigung, 02 Abschlagsplan 2024, 03 Preisanpassung 2025, 04 Jahresrechnung 2024, 05 Zwischenablesung 2025, 06 Jahresrechnung 2025 | SüdVolt Energie GmbH | Kern: Preise, Zähler, Abschläge, Diagramme |
| `02_gas_neckarenergie` | 07 Liefervertrag, 08 Jahresrechnung 2024, 09 Preisanpassung 2026, 10 Jahresrechnung 2025, 11 Abschlagsplan 2026, **29 Jahresrechnung 2026 (fehlerhaft)** | NeckarEnergie Versorgung AG | Kern: m³→kWh-Umrechnung, Diagramme |
| `03_water_stadtwerke_mosbach` | 12 Anmeldebestätigung, 13 Jahresbescheid 2024, 14 Gebührenanpassung 2026, 15 Jahresbescheid 2025 | Stadtwerke Mosbach | Zusatz: Gebührentabellen, Diagramm |
| `04_housing_utilities_contractors` | 16 Mietvertrag, 17 Übergabeprotokoll, 18/19 Betriebskostenabrechnung 2024/2025, **30 Betriebskostenabrechnung 2026 (fehlerhaft)**, 20/21 Handwerkerrechnung Heizungswartung 2024/2025 | Hausverwaltung Kraichgau & Neckar, SHK Kraichgau | Kern: Umlageschlüssel; teils relevant (Anfangszählerstände, § 35a) |
| `05_telecom_insurance` | 22/23 Internet, 24/25 Mobilfunk, 26/27 Hausrat, 28 Kfz | GlasfaserPlus, MobilPlus, AlpenSchutz | Ablenker (ähnliches Vokabular: Grundpreis, Laufzeit, Kündigungsfrist) |

### 4.2 Prüfung des Korpus (2026-11-14)
- **Qualität:** realistisches Layout (Briefkopf, Infoboxen, mehrspaltige Tabellen, Fußzeilen mit Bankdaten, Rechtshinweise), 1–2 Seiten je Dokument, insgesamt ca. 7.000 Wörter (grob 10.000 Tokens). Das passt nicht sinnvoll in ein 8k-Kontextfenster und rechtfertigt RAG.
- **Rechnerisch konsistent** (alle Summen, Umrechnungen und Abschläge nachgerechnet), mit **einer Ausnahme**, die sich als eingebauter Fehler eignet: Die Stromrechnung 2025 (06) setzt 39,50 ct/kWh brutto an, angekündigt waren laut Preisanpassung (03) 38,20 ct/kWh. Bei 3.100 kWh sind das 40,30 EUR brutto zu viel (korrekter Rechnungsbetrag 1.339,00 statt 1.379,30 EUR; Nachzahlung 74,00 statt 114,30 EUR).
- **Diagramme mit Zusatzinformation:** Die Seiten 2 von 04, 06, 10 und 15 enthalten Rasterdiagramme (Vorjahresvergleich, Monatsverlauf, Vergleichsgruppen). Teilweise stehen Werte nur im Bild (z. B. Stromverbrauch 2022: 3.480 kWh, 2023: 3.390 kWh). Damit ist `search_images` nicht nur Dekoration.
- **Querbezüge:** Anfangszählerstände im Übergabeprotokoll (17) = Startwerte der ersten Abrechnungen; Wohnfläche und Vorauszahlung im Mietvertrag (16) ↔ Betriebskostenabrechnungen (18/19); Abschläge aus Preisanpassungen ↔ Jahresrechnungen.
- **Fallen für den Agenten:** Gas-„Preissenkung“ 2026 senkt den Arbeitspreis, erhöht aber den Grundpreis (14,50 → 16,00 EUR/Monat); mehrere Abschlagshöhen über die Jahre (Strom 105 → 115 → 120 EUR); „Grundpreis“ und „Kündigungsfrist“ auch in Internet- und Mobilfunkverträgen.
- **Bewertung:** Der Korpus ist gut geeignet und wird beibehalten. Ursprünglich gab es nur einen eingebauten Fehler; deshalb wurden in M1 zwei weitere ergänzt (siehe 4.3).

### 4.3 Eingebaute Fehler und Ground Truth (M1)
| ID | Dokument | Fehler | Richtig wäre | Erkennbar durch |
|---|---|---|---|---|
| E1 | 06 Stromrechnung 2025 | Arbeitspreis 39,50 statt 38,20 ct/kWh | Rechnungsbetrag 1.339,00 statt 1.379,30 EUR (40,30 EUR zu viel) | Vergleich mit 03 (Preisanpassung) |
| E2 | 29 Gasrechnung 2026 | z-Zahl 1,0000 statt 0,9560, dadurch 11.819 statt 11.299 kWh | Rechnungsbetrag 1.316,25 statt 1.367,99 EUR (51,74 EUR zu viel) | Vergleich mit 08/10 (z-Zahl) und eigene Rechnung 1.060 m³ × 0,9560 × 11,150 |
| E3 | 30 Betriebskostenabrechnung 2026 | Wohnfläche 82 m² (26,28 %) statt 78 m² (25 %) | Anteil 1.867,50 statt 1.963,28 EUR (Guthaben 52,50 EUR statt Nachzahlung 43,28 EUR) | Vergleich mit 16 (Mietvertrag) |

Die Dokumente 29 und 30 stammen aus `scripts/generate_error_documents.py`. Alle Beträge dort werden berechnet, sodass nur der eingebaute Fehler stimmt, nicht aber Summen oder Rundung. Der Generator läuft mit WeasyPrint in einer eigenen Umgebung (keine Projektabhängigkeit). Layout und Datenmodell: einseitig ohne Diagramm, im Stil von 10 bzw. 19 nachgebaut.

`dataset/documents.yaml` enthält die Metadaten aller 30 PDFs, `dataset/ground_truth.yaml` den Fragenkatalog (14 Fragen, seit M6b), die drei eingebauten Fehler sowie `audit_checks`, die erwarteten Urteile zu den zehn Abrechnungen (7 korrekt, 3 fehlerhaft) für Fehlererkennungs- und Fehlalarmrate. Beide Dateien werden von `audit_agent.corpus` validiert.

## 5. Vorverarbeitung & Datenstrukturen

### 5.1 Pipeline (angelehnt an den Referenzprototyp)
1. **Parsing (PyMuPDF):** zuerst Tabellen erkennen (`find_tables()`) und ihre Flächen aus dem Fließtext ausschließen; Überschriften per Font-Heuristik (`font_size`, `is_bold`) in den `heading_stack`; Absätze aggregieren (`min_chars = 20`, `max_block_chars = 1500`); Bilder extrahieren.
2. **Enrichment:**
   - Tabellen: zeilenweise Serialisierung mit Spaltenköpfen in jeder Zeile + Tabellen-Summary (lokales LLM, `llama3.2`; eigener Chunk vor der ersten Zeile, Zahlen werden gegen den Tabellentext geprüft)
   - Bilder: Caption durch `gemma3:4b` (z. B. „Balkendiagramm Stromverbrauch 2023: 2.950 kWh, 2024: 2.710 kWh“)
   - Ergebnisse im DiskCache (`.cache/enrichment/`, SHA-256 über Aufgabe, Modell, Prompt, Optionen und Bild), damit die langsame Anreicherung auf dem Laptop nur einmal läuft (ADR-0008)
3. **Typisiertes Chunking:** `text`, `heading`, `table_row`, `table_summary`, `image`
4. **Hierarchie-Prefix vor dem Embedding:** `[Ordner | Datei | Kapitel > Unterkapitel]` (Umsetzung M4, ADR-0009; Sparte und Dokumenttyp stehen als Metadaten und werden gefiltert). `nomic-embed-text` erwartet zusätzlich Aufgaben-Präfixe: `search_document: [01_electricity_suedvolt | 04_Strom_Jahresabrechnung_2024 | …] <Text>` beim Indexieren und `search_query: <Anfrage>` bei der Suche. Sein Kontext ist auf 2.048 Tokens begrenzt; Chunks mit max. 1.500 Zeichen passen gut hinein.
5. **Speicherung:** JSON-Zwischenformat (`data/processed/`), ChromaDB (`data/vectors/`)

### 5.2 Domänenspezifische Ergänzung: Dokument-Metadaten
Bezeichner und Werte sind englisch (CODING_STANDARDS.md, Glossar).

Damit der Agent gezielt filtern kann, bekommt jedes Dokument (und damit jeder Chunk) zusätzliche Metadaten. Sie werden beim Ingest aus einer kleinen, manuell gepflegten Datei `documents.yaml` übernommen. Das ist bewusst einfach und dadurch nachvollziehbar.

| Feld | Beispielwerte | Zweck |
|---|---|---|
| `utility_type` | electricity, gas, district_heating, water, service_charges, rent, telecom, insurance, other | Filter nach Sparte |
| `doc_type` | contract, payment_plan, price_adjustment, bill, notice, handover_protocol, policy | Filter nach Dokumentart |
| `provider` | z. B. „Stadtwerke Musterstadt“ (fiktiv) | Zuordnung Vertrag ↔ Rechnung |
| `contract_id` | z. B. „ELEC-001“ | verknüpft Vertrag, Preisänderung und Rechnungen |
| `billing_period_start` / `billing_period_end` | 2024-01-01 / 2024-12-31 | richtigen Abrechnungszeitraum finden |
| `valid_from` | 2024-07-01 | Gültigkeit von Preisen |
| `document_date` | 2025-01-18 | Schreibdatum, um das neueste Dokument zu wählen |
| `is_noise_document` | true / false | Ablenkungsdokumente kennzeichnen (nur für die Auswertung, **nicht** für den Agenten sichtbar) |

### 5.3 JSON-Zwischenformat (Beispiel)

```json
{
  "chunk_id": "str_abr_2024_p2_tbl_01_r03",
  "chunk_type": "table_row",
  "content": "Zeitraum: 01.07.2024–31.12.2024 | Verbrauch: 1.380 kWh | Arbeitspreis: 32,10 ct/kWh | Betrag: 442,98 €",
  "heading_stack": ["Ihre Stromabrechnung 2024", "Kostenaufstellung"],
  "page_number": 2,
  "metadata": {
    "filename": "strom_abrechnung_2024.pdf",
    "utility_type": "electricity",
    "doc_type": "bill",
    "contract_id": "ELEC-001",
    "billing_period_start": "2024-01-01",
    "billing_period_end": "2024-12-31",
    "table_id": "tab_01",
    "columns": ["Zeitraum", "Verbrauch", "Arbeitspreis", "Betrag"]
  }
}
```

*(Zahlen sind Platzhalter.)*

**Umsetzung in M2 (Stand 2026-11-14):** Die Datei `data/processed/<datei>_chunks.json` enthält ein `ParsedDocument` mit `file`, `page_count` und `chunks`. Jeder Chunk hat genau die oben gezeigten Felder; `table_id` lautet `p<Seite>_tab<NN>` (z. B. `p1_tab03`), `chunk_id` bei Tabellenzeilen `<dateiname>_p1_tab03_r02`. Bild-Chunks tragen in `metadata.image_path` den Pfad unter `data/processed/images/`; ihr Text ist bis M3 ein Platzhalter. Die Parser-Regeln stehen in ADR-0007, bekannte Grenzen in ISS-015 bis ISS-019.

---

## 6. Retrieval-Konzept

Grundlage ist das Verfahren aus der Vorlesung:
1. **Query-Rewriting:** Im Agenten (P2) formuliert das Agent-Modell die Suchanfragen selbst in den Tool-Argumenten, ein eigenes Rewriting-Modell ist dort überflüssig. In P1 übernimmt das Synthese-Modell das Rewriting. Ein drittes Modell würde das Speicherlimit sprengen (siehe Abschnitt 9).
2. **Kandidatensuche** in ChromaDB (Top-20): `base_score = 1 − cosine_distance`
3. **Hierarchie-Boost:** Suchbegriffe in Dateiname, Ordner oder `heading_stack` → Faktor × 1.5
4. **Finaler Score:** `final_score = base_score × hierarchy_boost`

**Projektspezifische Erweiterung: Metadatenfilter vor der Vektorsuche.**
Die Tools können `utility_type`, `doc_type` und Zeitraum als ChromaDB-`where`-Filter übergeben. Damit wird zum Beispiel bei „Arbeitspreis laut Stromvertrag“ nur in `utility_type=electricity, doc_type=contract|price_adjustment` gesucht, und der „Grundpreis“ aus dem Handyvertrag kann gar nicht erst auftauchen.

**Messbare Frage für die Ausarbeitung:** Wie oft landen Ablenkungsdokumente in den Top-k, (a) ohne Filter und Boost, (b) nur mit Boost, (c) mit Filter und Boost? Daraus lässt sich der Nutzen der Erweiterung direkt belegen (→ Testmodul, Metrik „Distractor Rate“).

**Evidence-First-UI (Streamlit):** Vor der finalen Antwort werden die gefundenen Belege hierarchisch angezeigt (Dokument → Kapitel → Text/Tabellenzeile/Grafik-Caption mit Seite und Score).

**Umsetzung in M4 (Stand 2026-11-14):** Paket `audit_agent.retrieval` (ADR-0009). Der Index enthält alle Chunks außer Überschriften; die Suche holt 20 Kandidaten, multipliziert bei einem Pfadtreffer mit 1.5 und liefert die 5 besten mit `base_score`, `boost` und `final_score`. Der Metadatenfilter (Sparte, Dokumenttyp, Vertragsnummer, Zeitraum) wirkt als `where`-Bedingung; der Zeitraumfilter schließt Dokumente ohne Abrechnungszeitraum aus (ISS-025). Ein Rewriting-Modell gibt es in P1 nicht. Die Evidenz erscheint in M4 als Text in der CLI (`python -m audit_agent.retrieval search`), die Streamlit-Oberfläche folgt in M5.

---

## 7. Agenten-Architektur & Tools

### 7.1 Zwei Varianten zum Vergleich (wie im Referenzprototyp)
- **P1 – Modulare Pipeline:** deterministisch, ein Retrieval-Durchgang, Evidence-First, danach LLM-Synthese
- **P2 – Agentic RAG:** ReAct-Loop, das LLM wählt Tools, sucht bei Bedarf nach und rechnet

### 7.2 Werkzeuge
Die 5 Werkzeuge des Referenzprototyps bleiben erhalten und werden um Metadatenfilter und ein Inventar-Tool ergänzt. Bewusst wenige Tools, weil kleine lokale Modelle bei vielen Tools häufiger das falsche wählen.

| Tool | Zweck | Warum nötig |
|---|---|---|
| `list_documents(utility_type?, doc_type?, year?)` | Liefert das Dokumentinventar aus den Metadaten | Agent weiß zuerst, *welche* Unterlagen es gibt (wichtig für Negativfragen: „Für 2022 liegt keine Abrechnung vor“) |
| `search_documents(query, top_k, filter?)` | Suche in Fließtext und Überschriften | Vertragsklauseln, AGB, Preisänderungsschreiben |
| `search_tables(query, top_k, filter?)` | Suche in Tabellenzeilen und Tabellen-Summaries | Preise, Zählerstände, Verbräuche, Kostenarten |
| `search_images(query, top_k, filter?)` | Suche in Grafik-Captions | Vorjahresvergleiche, Verbrauchsverläufe |
| `get_document_outline(filename_filter)` | Gliederung eines Dokuments | Navigation in Verträgen/AGB (z. B. „Wo steht die Preisanpassung?“) |
| `calculate(expression)` | Sichere Arithmetik (kein `eval`, z. B. AST-basiert) | Sollbetrag, Differenzen, zeitanteilige Grundpreise, Prozentveränderungen |

### 7.3 Selbstprüfung vor der finalen Antwort
Vor der Final Answer prüft der Agent per Prompt-Regel:
- Ist jede Zahl in der Antwort durch eine Quelle oder ein `calculate`-Ergebnis belegt?
- Stammen Vertrag und Rechnung zur selben `contract_id` und passenden Zeitraum?
- Wenn Belege fehlen: ehrlich „nicht in den Unterlagen gefunden“ statt raten.

### 7.4 Sicherheitsgrenzen der Agenten-Schleife
- Maximal z. B. 6 Tool-Aufrufe pro Frage (Schutz vor Endlosschleifen auf langsamer Hardware)
- Ungültiges Tool-JSON wird abgefangen und dem Modell als Fehlermeldung zurückgegeben (einmaliger Korrekturversuch)
- Vollständiges Logging von Thought/Action/Observation, als Grundlage für Tests und Reverse Engineering

**Umsetzung in M5 (Stand 2026-11-14):** Paket `audit_agent.agent` (ADR-0010). Die sechs Tools stehen wie oben, aber ohne `top_k` und mit flachen Filterargumenten (`utility_type`, `doc_type`, `year`) statt `filter?`. `search_documents` durchsucht nur `text` (Überschriften sind nicht indiziert, ihr Pfad steckt in den Chunks; die Gliederung liefert `get_document_outline`). Der Jahresfilter gilt nur mit `bill`, `notice` oder `payment_plan` (ISS-025); eine Suche ohne Jahr und ohne Treffer wird ohne Filter wiederholt (ISS-007). Jeder Treffer trägt eine Belegnummer `[n]`, die Antwort zitiert sie. Jeder Aufruf, auch ein ungültiger, zählt gegen das Limit von 6; der Korrekturversuch ist der nächste Modellaufruf nach der Fehlermeldung. Das Log ist eine JSON-Zeile je Schritt unter `data/eval/<run>/`. Die Streamlit-Oberfläche (`agent/app.py`) zeigt die Belege schon während der Suche.

---

## 8. ReAct-Zyklen (Beispiele für die Ausarbeitung)

Die Zahlen stammen aus dem echten Testkorpus.

### 8.1 Standard-Prüfung: Wurde der vereinbarte Arbeitspreis berechnet?
**Frage:** „Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?“

```
Thought 1:  Ich brauche die vereinbarten Preise aus dem Stromvertrag.
Action 1:   search_tables(query="Arbeitspreis Grundpreis Tarif", filter={utility_type: electricity, doc_type: contract})
Observation: "Arbeitspreis: 34,80 ct/kWh brutto | Grundpreis: 11,50 EUR/Monat | Neukundenbonus 80,00 EUR" (01, S. 1)

Thought 2:  Jetzt Verbrauch und abgerechnete Preise aus der Jahresrechnung 2024.
Action 2:   search_tables(query="Arbeitspreis Verbrauch kWh Betrag", filter={utility_type: electricity, doc_type: bill, year: 2024})
Observation: "Arbeitspreis ÖkoStrom | 3.250 kWh | 34,80 ct/kWh | 1.131,00 EUR"; "Grundpreis 12 Monate | 138,00 EUR"; "Bonus -80,00 EUR" (04, S. 1)

Thought 3:  Preise stimmen überein. Ich rechne den Rechnungsbetrag nach.
Action 3:   calculate("3250 * 0.348 + 12 * 11.50 - 80")
Observation: {"result": 1189.0}

Final Answer: Ja. Abgerechnet wurden die vertraglichen 34,80 ct/kWh und 11,50 EUR/Monat [1][2].
              3.250 kWh × 34,80 ct + 138,00 EUR − 80,00 EUR Bonus = 1.189,00 EUR, wie auf der Rechnung.
```

### 8.2 Grenzfall: Preisanpassung und Rechnung passen nicht zusammen
**Frage:** „Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?“

Schritte: `search_documents`/`search_tables` im Preisanpassungsschreiben 03 (neu: 38,20 ct/kWh brutto ab 01.01.2025) → Rechnungstabelle 06 (abgerechnet: 39,50 ct/kWh, 3.100 kWh) → `calculate("3100 * (0.395 - 0.382)")` = 40,30 EUR. Der Agent meldet eine Abweichung mit Belegen aus beiden Dokumenten und nennt den korrekten Betrag (1.339,00 statt 1.379,30 EUR).

### 8.3 Grafik-Fall: Verbrauchsentwicklung
**Frage:** „Wie hat sich der Stromverbrauch von 2022 bis 2024 entwickelt?“
`search_images` (Caption des Vergleichsdiagramms in 04: 2022 3.480 kWh, 2023 3.390 kWh, 2024 3.250 kWh) → zur Gegenprüfung `search_tables` (Zählerstände 2024: 3.250 kWh) → `calculate` der prozentualen Veränderung. Weichen Caption und Tabelle ab, wird das gemeldet (Hinweis auf Vision-Fehler).

---

## 9. Modellauswahl für die eigene Hardware

### 9.1 Rahmenbedingungen

| Parameter | Wert | Folge |
|---|---|---|
| CPU | Ryzen 5 7520U, 4 Kerne/8 Threads, AVX2, kein AVX-512 | reine CPU-Inferenz (iGPU wird von Ollama ignoriert) |
| RAM | 14,4 GiB nutzbar | |
| Ollama | `MemoryMax=9G`, `OLLAMA_MAX_LOADED_MODELS=2`, `OLLAMA_NUM_PARALLEL=1` | höchstens 2 Modelle, zusammen inkl. KV-Cache unter 9 GB |
| Prefill | ca. 18 Tokens/s | 1.000 Tokens Prompt ≈ 55 s, bevor die Antwort beginnt |
| Generierung | ca. 5–6 Tokens/s (7–8B), ca. 10,5 Tokens/s (3B) | 100 Tokens Antwort ≈ 18 s (8B) |

Modelle aus den Folien wie `phi3:medium` (14B) oder `qwen2.5:32b` scheiden aus.

### 9.2 Modellwahl je Aufgabe

| Aufgabe | Modell | RAM ca. | Begründung |
|---|---|---|---|
| Embeddings | `nomic-embed-text` | < 0,5 GB | 768 Dimensionen, Standard der Vorlesung; Präfixe `search_document:` / `search_query:` |
| Bild-Captions (Ingest) | `gemma3:4b` | 4,0 GB | multimodal, ca. 8–9 Tokens/s |
| Tabellen-Summaries (Ingest) | `llama3.2` (3B) | 3,1 GB | schnell, einfache Zusammenfassungsaufgabe |
| Agent, Tool-Calling, Antwort (Query) | `qwen2.5:7b` **oder** `llama3.1:8b` | 5,5 bzw. 6,3 GB | beide gut bei strukturierter Ausgabe/Tool-Calling; in RUN-000 gleichauf; vorläufig `llama3.1:8b`, Endentscheidung im Testmodul (ADR-0004) |

`qwen3` (bis 8B) höchstens mit abgeschaltetem Thinking-Modus testen: Denk-Tokens kosten bei 5 Tokens/s zu viel Zeit.

### 9.3 Speicherbudget nach Phasen (CQRS, siehe ADR-0004)

| Phase | Gleichzeitig geladen | Summe | Unter 9 GB? |
|---|---|---|---|
| Ingest: Enrichment | `gemma3:4b` + `llama3.2` | ca. 7,1 GB | ja |
| Ingest: Embedding | `nomic-embed-text` | < 0,5 GB | ja |
| Query | Agent-Modell (7–8B) + `nomic-embed-text` | ca. 6–7 GB + KV-Cache | ja |
| nicht möglich | Agent-Modell + `gemma3:4b` oder + 3B-Rewriter | > 9 GB | nein |

Daraus folgt: keine Bildanalyse zur Abfragezeit (nur gecachte Captions) und kein separates Rewriting-Modell (siehe Abschnitt 6).

### 9.4 Betriebsregeln
- Ingest und Abfrage strikt getrennt ausführen (`ingest` vs. `query`/UI)
- `num_ctx` explizit setzen (z. B. 8192 für den Agenten), nicht dem Standardwert überlassen; der KV-Cache wächst mit dem Kontext
- **Prompts kurz halten:** knapper System-Prompt, kurze Tool-Beschreibungen, `top_k` klein (3–5), Tool-Ergebnisse kompakt (nur Inhalt + Quelle). Jeder Token im Prompt kostet ca. 55 ms.
- Grobe Abschätzung für eine Agentenfrage mit 3 Tool-Schritten: 1–4 Minuten. In M0 gemessen (RUN-000): Prefill 18,9–20,1 Tokens/s, Generierung 5,0–5,9 Tokens/s. Ob Ollama den Prompt-Präfix wiederverwendet, ist wahrscheinlich, aber noch nicht belegt (ISS-005); Prüfung beim ersten Mehrschritt-Lauf in M5.
- Antwortzeiten im Testmodul mitmessen. Latenz auf Standard-Hardware ist eine ehrliche Kennzahl für die Reflexion.

---

## 10. GraphRAG-Entscheidung

**Entscheidung: kein vollständiges GraphRAG. Beziehungen werden stattdessen über Metadaten abgebildet.**

| Prüffrage (→ Anf. 5.5) | Antwort für diesen Use Case |
|---|---|
| Welche Entitäten? | Vertrag, Anbieter, Zähler, Tarif/Preis, Abrechnungszeitraum, Kostenart, Wohnung |
| Welche Beziehungen? | Rechnung *bezieht sich auf* Vertrag; Preisänderung *ändert* Tarif *ab* Datum; Zähler *gehört zu* Vertrag; Kostenart *wird umgelegt nach* Schlüssel |
| Welche Fragen wären mit GraphRAG besser? | „Welche Preisstände galten in welchem Zeitraum für welchen Zähler?“; Überblicksfragen über alle Verträge und Kostenarten |
| Warum reicht klassisches RAG plus Agent? | Wenige Entitäten (ein Haushalt, ca. 4 Verträge); die wichtigen Beziehungen sind wenige, stabile Schlüssel (`contract_id`, `billing_period`, `valid_from`), die sich als Metadaten exakt filtern lassen. Multi-Hop übernimmt der ReAct-Loop. |
| Zusätzliche Kosten/Komplexität | LLM-basierte Entity- und Relationsextraktion ist auf der CPU langsam und fehleranfällig (falsch extrahierte Preise wären schlimmer als keine); zusätzliche Graph-Datenbank; aufwendigeres Testen |

**Ausblick:** Bei einem Hausverwaltungs-Szenario mit vielen Wohnungen, Mietparteien und Verträgen würde sich GraphRAG lohnen.

---

## 11. Test- & Evaluationskonzept (Testmodul)

### 11.1 Aufbau des Testmoduls
- Testset: die Fragen aus `dataset/ground_truth.yaml` (erwartete Antwort, Fakten, Quellen mit Datei + Seite, erwartete Tools, Kategorie); ein eigenes `testset.yaml` entfällt (M6a, ADR-0011)
- `python -m audit_agent.evaluation generate` führt die Fragen gegen **drei Varianten** aus und schreibt je Variante eine JSON-Zeile pro Antwort; `score` bewertet die gespeicherten Antworten ohne Ollama (`scores.json`, `report.md`):
  - **B0 – Volltext-Baseline:** Seitentext in Katalogreihenfolge, bis das Kontextfenster voll ist (bei `num_ctx` 8192 die Dateien 01–06, ISS-039), direkt im Prompt
  - **P1 – Modulare Pipeline:** eine Suche (Top-5, ohne Filter, mit Boost), danach ein Modellaufruf mit nummerierten Treffern
  - **P2 – Agentic RAG:** der Agent aus M5
  - Alle drei mit demselben Modell, denselben Chat-Optionen und demselben Belegformat `[n]`
- Whitebox-Unit-Tests (`pytest`) für Parser, Chunker, Serialisierung, Score-Berechnung und `calculate`

Der Vergleich mit B0 und P1 belegt messbar, ob RAG und Agentik hier nötig sind. Damit wird der Einwand „ein einfacher Volltext-Prompt reicht“ mit Daten beantwortet.

### 11.2 Verbindlicher Fragenkatalog (14 Fragen)

Mindestens 5 Standardfragen, 2 komplexe Grenzfälle und 2 Negativfragen (Vorlesung) plus 3 Zusatzfragen (CODING_STANDARDS.md: 12-Fragen-Katalog). In M6b kamen die Grenzfälle G3 und G4 dazu, damit jeder eingebaute Fehler (E1–E3) genau eine Prüffrage hat (ISS-040); Prüffragen mit „Ja“ (S5, G2, Z1) messen Fehlalarme. Die erwarteten Antworten stammen aus dem Korpus und stehen in `dataset/ground_truth.yaml`.

| ID | Kategorie | Testfrage | Erwartete Antwort (Quelle) | Prüft vor allem |
|---|---|---|---|---|
| S1 | Standard (Text) | Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit? | 6 Wochen zum Ende der Erstlaufzeit am 31.12.2025, danach 1 Monat (07, 09) | Text-Retrieval, Hierarchie |
| S2 | Standard (Tabelle) | Welcher Arbeits- und Grundpreis gelten laut Stromvertrag? | 34,80 ct/kWh und 11,50 EUR/Monat brutto (01) | `search_tables`, Filter |
| S3 | Standard (Tabelle) | Wie hoch war der Wasserverbrauch 2025 laut Zählerständen? | 386 − 312 = 74 m³ (15) | Tabellenzeilen, Jahr |
| S4 | Standard (Bild) | Wie hoch war der Stromverbrauch 2022 und 2023? | 3.480 bzw. 3.390 kWh, nur im Diagramm (04, S. 2) | `search_images`, Vision-Caption |
| S5 | Standard (Multi-Hop + Rechnen) | Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein? | Ja, 1.189,00 EUR (01, 04) | ReAct, `calculate`, keine Fehlalarme |
| G1 | Grenzfall (Fehler) | Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet? | Nein: 39,50 statt 38,20 ct/kWh, 40,30 EUR zu viel (03, 06) | Multi-Hop über 2 Dokumente, Fehlererkennung |
| G2 | Grenzfall (Querbezug) | Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet? | Ja: 78/312 m² = 25 %, 7.320 × 25 % = 1.830 EUR, Guthaben 90 EUR (16, 19) | Mietvertrag ↔ Abrechnung, keine Fehlalarme |
| G3 | Grenzfall (Fehler E2) | Ist die Gasabrechnung 2026 korrekt? | Nein: z-Zahl 1,0000 statt 0,9560; 1.060 × 0,9560 × 11,150 = 11.299 statt 11.819 kWh, 51,74 EUR zu viel (29, 10) | Vergleich mit dem Vorjahr, Umrechnung |
| G4 | Grenzfall (Fehler E3) | Ist mein Anteil an den Betriebskosten 2026 korrekt berechnet? | Nein: 82 statt 78 m²; 25 % von 7.470 EUR = 1.867,50 statt 1.963,28 EUR (16, 30) | Mietvertrag ↔ Abrechnung, Fehlererkennung |
| N1 | Negativ | Wie hoch war meine Stromrechnung 2023? | Liegt nicht vor (Belieferung ab 01.01.2024); nur der Verbrauch 2023 ist aus dem Diagramm bekannt | keine erfundene Zahl |
| N2 | Negativ | Welchen Grundpreis zahle ich für Fernwärme? | Kein Fernwärmevertrag vorhanden (Gasetagenheizung, 07/16) | Ablenker nicht verwechseln |
| Z1 | Zusatz (Umrechnung) | Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen? | Ja: 1.200 m³ × 0,9560 × 11,150 = 12.791 kWh (10) | Rechnen mit Umrechnungsfaktoren |
| Z2 | Zusatz (Zeitraum) | Wie hoch ist mein aktueller monatlicher Stromabschlag? | 120,00 EUR ab 15.02.2026, nicht 105 oder 115 EUR (06) | neuestes Dokument wählen |
| Z3 | Zusatz (Ablenkung) | Mit welcher Frist kann ich meinen Stromvertrag kündigen? | Nach der Erstlaufzeit jederzeit mit 1 Monat Frist (01); nicht Internet-/Mobilfunkvertrag | Distractor Rate |

Weitere mögliche Fragen (Reserve): Gas-„Preissenkung“ 2026 (Arbeitspreis sinkt, Grundpreis steigt), Wasser-Gebühren 2026, steuerlich absetzbarer Lohnanteil der Heizungswartung 2025 (285,60 EUR brutto).

### 11.3 Metriken

**Etabliertes Framework (RAGAS)**, mit einem lokalen Ollama-Modell als Bewerter:
- Faithfulness (Antwort durch Kontext gedeckt?)
- Answer Relevancy
- Context Precision / Context Recall
- Optional: synthetischer Testdatensatz aus dem Korpus (RAGAS-Testset-Generierung)
- Kritisch reflektieren: Ein kleines lokales Bewertermodell ist selbst fehleranfällig, daher werden Stichproben manuell geprüft.

**Eigene, kontextspezifische Metriken** (deterministisch, ohne LLM-Bewerter):

| Metrik | Messung |
|---|---|
| Numerische Korrektheit | Zahl in der Antwort = Ground Truth (Toleranz z. B. ±0,01 €) |
| Fehlererkennungsrate | Anteil der eingebauten Fehler, die der Agent meldet |
| Fehlalarmrate | Meldungen bei korrekten Abrechnungen |
| Quellen-Korrektheit | Zitierte Datei + Seite ∈ erwartete Quellen |
| Distractor Rate | Anteil der Ablenkungsdokumente in den Top-k bzw. in den Zitaten |
| Tool-Wahl-Korrektheit | erwartete Tools aufgerufen (aus dem ReAct-Log) |
| Negativ-Erkennung | N-Fragen korrekt als „nicht vorhanden“ beantwortet |
| Latenz | Sekunden pro Frage je Variante (B0/P1/P2) |

Umsetzung (M6a): Zahlen gelten als gefunden, wenn sie irgendwo in der Antwort stehen (Belegnummern ausgenommen); Quellen werden über die zitierten `[n]` auf Datei + Seite geprüft; Tool- und Filterwahl nur für P2; Fehlererkennung und Fehlalarm über das Ja/Nein-Urteil der Prüffragen S5, G1, G2, Z1. Das sind bewusst einfache Heuristiken (ISS-038); der Bericht zeigt jede Antwort zur Kontrolle. Seit M6b deckt die Fehlererkennung E1–E3 ab (G1, G3, G4).

Umsetzung RAGAS (M6b, ADR-0012): Faithfulness und Context Recall mit dem lokalen Bewerter `audit-judge` (`qwen2.5:7b`, `num_ctx` 8192) auf den gespeicherten Antworten und deren Belegtexten; Answer Relevancy, Context Precision und die Testset-Generierung entfallen aus Zeitgründen. Prompts, die nicht in den Kontext passen, werden nicht bewertet statt still gekürzt (betrifft vor allem B0, ISS-046); beim `qwen2.5:7b`-Lauf bewertet das Modell sich selbst (ISS-045).

**Laufzeit der Evaluation realistisch planen:** 14 Fragen × 3 Varianten bei 1–7 Minuten pro Antwort (B0 mit langem Volltext-Prompt am langsamsten) ergeben grob 1–3 Stunden. RAGAS braucht pro Frage mehrere zusätzliche LLM-Aufrufe für die Bewertung. Deshalb:
- Antworten erzeugen und bewerten in **getrennten Schritten**; Antworten als JSON speichern, damit die Bewertung wiederholt werden kann, ohne neu zu generieren
- Komplettläufe über Nacht, als `slow` markiert (`pytest -m slow`)
- Für schnelle Iterationen eine Teilmenge (z. B. 3 Fragen) nutzen

### 11.4 Qualitätsaussage
Ergebnis ist eine Tabelle „Variante × Metrik“, aus der eine begründete Qualitätszuschreibung folgt, zum Beispiel: „P2 erkennt x von y eingebauten Fehlern bei z Fehlalarmen; P1 und B0 erkennen keine Fehler, die eine Rechnung erfordern.“ Dazu kommt eine Fehleranalyse einzelner Fehlschläge (Parser? Retrieval? Tool-Wahl? Synthese?).

---

## 12. Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Tabellenerkennung zerlegt mehrspaltige Rechnungstabellen falsch | Parser-Unit-Tests mit bekannten Tabellen; JSON-Zwischenformat manuell prüfen; bei Bedarf Spaltenzuordnung nachbessern |
| `gemma3:4b` liest Werte aus Balkendiagrammen ungenau ab | Grafik nur ergänzend nutzen; Gegenprüfung mit Tabellenwerten; Abweichungen melden statt verwenden |
| Kleines Modell erzeugt ungültiges Tool-JSON oder wählt falsche Tools | Wenige, klar beschriebene Tools; Fehler abfangen und zurückmelden; Modellvergleich im Testmodul |
| Langsame CPU-Inferenz (Prefill ca. 18 Tokens/s), RAM-Grenze 9 GB | Modelle ≤ 8B, max. 2 gleichzeitig nach Phasenplan (Abschnitt 9.3), kurze Prompts, kleines `top_k`, Caching, Begrenzung der Tool-Aufrufe, Evaluation über Nacht |
| Testlauf dauert so lange, dass zu selten getestet wird | Teilmengen-Testset für schnelle Iterationen; Unit-Tests ohne LLM (Mocks) als breite Basis der Testpyramide |
| Fachliche Komplexität (Brennwert/Zustandszahl beim Gas, Heizkostenverteilung) | Scope begrenzen: Kernprüfungen auf Strom-Arbeitspreis/Grundpreis und Nebenkosten-Umlage; Gas-Umrechnung als Erweiterung |
| Zahlenformate (Komma, Tausenderpunkt, ct vs. €) | Normalisierung vor `calculate`; Unit-Tests dafür |
| Datenschutz bei echten Unterlagen in der Abgabe | synthetische oder anonymisierte Dokumente abgeben |
| Antworten wirken wie Rechtsberatung | Formulierung als „Auffälligkeit mit Beleg“, Hinweis im System-Prompt und in der UI |

---

## 13. Meilensteine mit Reverse-Engineering-Checkpoints

Nach jedem Meilenstein: Code-Dateien, Funktionen, Datenstrukturen, Datenflüsse und Bibliotheken nachvollziehen, mit Whitebox-Tests absichern und kurze eigene Notizen schreiben (→ Anf. 7). Die Notizen sind später Rohmaterial für die Ausarbeitung in eigener Sprache.

| # | Meilenstein | Ergebnis | Reverse-Engineering-Checkpoint |
|---|---|---|---|
| M0 | Setup | Repo, ruff/pytest, Ollama-Modelle, Smoke-Test (Geschwindigkeit, Tool-Calling) | Wie spricht Python mit Ollama (HTTP-API)? Was messe ich im Smoke-Test und warum? |
| M1 | Metadaten & Ground Truth | Korpus geprüft (30 PDFs vorhanden), `documents.yaml`, `ground_truth.yaml` | Warum ist welches Dokument im Korpus? Welche Frage testet welches Dokument? |
| M2 | Parser & JSON-Zwischenformat | `data/processed/*_chunks.json` | Wie erkennt `find_tables` Tabellen? Wie entsteht der `heading_stack`? Ein Dokument von Hand mit dem JSON vergleichen |
| M3 | Enrichment & Cache | Captions, Tabellen-Summaries, `.cache/` | Welcher Prompt geht an `gemma3:4b`? Wie funktioniert der SHA-256-Cache-Schlüssel? |
| M4 | Embedding & Retrieval (P1) | ChromaDB-Index, Score mit Boost + Filter, Evidence-UI | Score für einen Treffer von Hand nachrechnen; Wirkung von Filter und Boost an einem Beispiel zeigen |
| M5 | Agent (P2) | ReAct-Loop, 6 Tools, Logging | Ein Log Schritt für Schritt erklären: Was ging ans Modell, was kam zurück, wie wird der Tool-Aufruf geparst? |
| M6 | Testmodul | `testset.yaml`, `run_eval.py`, pytest, RAGAS | Wie berechnet RAGAS Faithfulness? Wie werden die eigenen Metriken berechnet? |
| M7 | Ausarbeitung | 5–8 Seiten | Jede Aussage über das System ist durch eigenes Verständnis und Testergebnisse gedeckt |

---

## 14. Vorschlag für die Gliederung der Ausarbeitung (5–8 Seiten)

| Kapitel | Inhalt | Bewertungskriterium |
|---|---|---|
| 1. Problem & Use Case | Prüfproblem, Zielgruppe, Datenschutzargument, Abgrenzung | 15 % |
| 2. Datenbasis & Vorverarbeitung | Korpus, Strukturelemente, Parsing, Chunk-Typen, Metadaten, JSON-Format | 15 % |
| 3. Architektur | Gesamtbild, P1 vs. P2, Tools, ReAct-Beispiel, Modellwahl & Hardware | 25 % |
| 4. RAG- & Retrieval-Konzept | Hierarchie-Prefix, Score-Formel, Metadatenfilter, Evidence-First, GraphRAG-Entscheidung | 20 % |
| 5. Testmodul & Evaluation | 14-Fragen-Katalog (5/4/2 + 3), RAGAS + eigene Metriken, Baselines, Ergebnisse, Fehleranalyse | 15 % |
| 6. Reflexion und Ausblick | Grenzen, Erkenntnisse aus Tests und Issues, Ausblick (ohne Literatur) | 10 % |

---

## 15. Offene Entscheidungen

- [x] Herkunft der Dokumente: vollständig synthetisch, Korpus mit 30 PDFs liegt vor und wurde geprüft (Abschnitt 4)
- [x] Sparten-Scope: alle vier Sparten im Korpus; Kern der Prüffragen Strom, Gas und Betriebskosten
- [x] Python-Umgebung: `uv`, Python 3.13 (laut `pyproject.toml`)
- [x] Zwei weitere eingebaute Fehler in M1 ergänzt (Abschnitt 4.3)
- [x] Keine Literatur in der Ausarbeitung
- [x] Agent-Modell: vorläufig `llama3.1:8b` (RUN-000: gleiche Trefferquote wie `qwen2.5:7b`, ca. 18 % schnellere Generierung); Endentscheidung im Testmodul M6 (ADR-0004)
- [x] Tool-Calling: natives Ollama-Tool-Calling (ADR-0006), Bestätigung in M5
- [ ] Referenzprototyp als Basis oder eigener Aufbau? (Code liegt nicht im Repo)
- [ ] UI: Streamlit (Evidence-First wie Referenz) + CLI für Tests (Empfehlung)
