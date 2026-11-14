# Glossar (Ubiquitous Language)

> Ein Begriff = ein Name, überall gleich: im Chat, im Code, in Tests und in der Ausarbeitung.
> Die Spalte **„In meinen Worten“** fülle ich selbst aus, sobald ich den Begriff wirklich verstanden habe. Das ist Übung für die Ausarbeitung und ein Verständnis-Check.
> Code-Bezeichner sind Vorschläge und werden beim ersten Gebrauch im Code bestätigt.

## Fachdomäne (Energie & Nebenkosten)

| Deutsch | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Liefervertrag | `Contract` | Vertrag über Lieferung von Strom/Gas/Wärme mit Preisen und Laufzeit | |
| Jahresabrechnung | `UtilityBill` | Abrechnung eines Versorgers über einen Abrechnungszeitraum | |
| Preisänderung | `PriceAdjustment` | Mitteilung über neuen Preis ab Stichtag | |
| Zählerstand | `MeterReading` | Ablesewert eines Zählers zu einem Datum | |
| Rechnungsposition | `CostLineItem` | Einzelne Zeile einer Kostenaufstellung | |
| Prüfbefund | `AuditFinding` | Vom Agenten gemeldete Auffälligkeit mit Belegen | |
| Arbeitspreis | `energy_price` (ct/kWh) | Preis je verbrauchter Einheit | |
| Grundpreis | `base_price` | verbrauchsunabhängiger Preis je Zeitraum | |
| Abschlag | `advance_payment` | regelmäßige Vorauszahlung | |
| Abrechnungszeitraum | `billing_period` | Zeitraum, den eine Abrechnung abdeckt | |
| Nebenkostenabrechnung | `ServiceChargeStatement` | Abrechnung der Betriebskosten durch Vermieter | |
| Umlageschlüssel | `allocation_key` | Regel, wie Kosten auf Mietparteien verteilt werden (z. B. nach Wohnfläche) | |
| Wohnfläche | `living_area_sqm` | Fläche der Wohnung in m² | |
| Sparte | `utility_type` | electricity, gas, district_heating, water, service_charges, rent, other | |
| Dokumentart | `doc_type` | contract, terms, price_adjustment, bill, notice, policy | |
| Ablenkungsdokument | `is_noise_document` | Dokument ohne Bezug zur Prüfung (Handy-, DSL-Vertrag, …) | |

## RAG & Agenten

| Begriff | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Chunk | `DocumentChunk` | Kleinste suchbare Einheit (Absatz, Tabellenzeile, Bild-Caption) | |
| Chunk-Typ | `chunk_type` | text, heading, table_row, table_summary, image | |
| Überschriften-Stapel | `heading_stack` | Liste der aktiven Überschriften über einem Chunk | |
| Hierarchie-Prefix | – | `[Sparte \| Dokumenttyp \| Datei \| Kapitel]` vor dem Embedding | |
| Enrichment | `enrichment` | Anreicherung durch Modelle (Tabellen-Summary, Bild-Caption) | |
| Embedding | `EmbeddingProvider` | Vektor-Darstellung eines Textes | |
| Vektor-Store | `VectorStore` | Datenbank für Vektoren + Metadaten (ChromaDB) | |
| base_score | `base_score` | 1 − Kosinus-Distanz | |
| Hierarchie-Boost | `hierarchy_boost` | Faktor 1.5 bei Treffer in Dateiname/Ordner/heading_stack | |
| Metadatenfilter | `metadata_filter` | Einschränkung der Suche auf Sparte/Typ/Zeitraum | |
| Evidence-First | – | Belege anzeigen, bevor das LLM antwortet | |
| ReAct | `AuditAgent` | Schleife aus Thought → Action → Observation | |
| Tool | `AuditTool` | Funktion, die der Agent aufrufen kann | |
| Tool-Ergebnis | `AuditToolResult` | Normalisiertes Ergebnis eines Tools mit Quellen | |
| Ground Truth | `ground_truth` | Bekannte richtige Antwort für eine Testfrage | |
| Halluzination | – | Plausible, aber nicht belegte Aussage | |

## Betrieb & Messung

| Begriff | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Smoke-Test | `audit_agent.smoke` | Kurzer Funktionstest der Umgebung (Geschwindigkeit, Tool-Calling, Embedding, Vision) | |
| Prefill | `prompt_eval_*` | Verarbeitung des Eingabe-Prompts vor der ersten Ausgabe (hier ca. 18–20 Tokens/s) | |
| Generierung | `eval_*` | Erzeugung der Antwort-Tokens (hier ca. 5–6 Tokens/s bei 7–8B) | |
| Kontextfenster | `num_ctx` | Anzahl Tokens, die das Modell gleichzeitig sieht; bestimmt den KV-Cache und damit den RAM-Bedarf | |
| Modell entladen | `keep_alive=0` | Gibt den RAM eines Modells sofort frei | |
| Preflight | `ensure_models_available` | Fail-fast-Prüfung, ob alle benötigten Ollama-Modelle installiert sind | |
| Tool-Calling (nativ) | `tools=[...]` | Das Modell antwortet mit einem strukturierten Werkzeugaufruf statt Freitext | |
| Einstellungen | `Settings` | Zentrale Konfiguration (Pfade, Modelle, Limits), überschreibbar per `AUDIT_*`-Variablen | |
| Präfix-Wiederverwendung | `is_prefix_reused` | Ollama behält den gleichen Prompt-Anfang im Cache und spart Prefill-Zeit | |
