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
| Bild-Caption | `ImageCaptioner` | Vom Vision-Modell erzeugte Beschreibung eines Diagramms mit Zahlenwerten; ersetzt den Platzhalter im `image`-Chunk | |
| Tabellen-Summary | `TableSummarizer`, `table_summary` | Kurze Zusammenfassung einer ganzen Tabelle als eigener Chunk, zusätzlich zu den Zeilen | |
| Enrichment-Cache | `EnrichmentCache` | Festplatten-Cache (`.cache/enrichment/`) für Modellantworten, Schlüssel ist ein SHA-256 | |
| Cache-Schlüssel | `make_cache_key` | Hash über Aufgabe, Modell, Prompt, Optionen und Bild; ändert sich einer davon, wird neu berechnet | |
| Unbelegte Zahl | `unsupported_numbers` | Zahl in einer Summary, die nicht im Tabellentext steht (Hinweis auf Fehler) | |
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
| Dokument-Metadaten | `DocumentMeta` | Von Hand gepflegte Angaben je PDF (Sparte, Dokumentart, Anbieter, Zeitraum, Rauschen) | |
| Eingebauter Fehler | `PlantedError` | Absichtlich falsche Angabe in einer Abrechnung, Grundlage der Fehlererkennungsrate | |
| Prüfurteil | `AuditCheck` | Erwartetes Ergebnis der Prüfung einer Abrechnung (korrekt oder fehlerhaft) | |
| Erwartete Tatsache | `ExpectedFact` | Prüfbarer Wert einer erwarteten Antwort mit Einheit und Toleranz | |
| Ablenkungsdokument | `is_noise_document` | PDF mit ähnlichem Vokabular, aber ohne Bezug zur Frage (Internet, Mobilfunk, Versicherung) | |
| Korpus-Fehler | `CorpusError` | Fehler beim Laden oder Validieren von `documents.yaml` bzw. `ground_truth.yaml` | |
| Parser | `DocumentParser` | Liest ein PDF und erzeugt typisierte Chunks (Tabellen, Überschriften, Text, Bilder) | |
| Zwischenformat | `ParsedDocument` | Alle Chunks eines PDFs als JSON unter `data/processed/<datei>_chunks.json` | |
| Chunk-Metadaten | `ChunkMetadata` | Dokument-Metadaten plus `table_id`, `columns`, `image_path` je Chunk | |
| Span | `_Span` | Zusammenhängendes Textstück mit gleicher Schrift (kleinste Einheit aus PyMuPDF) | |
| Tabellenregion | `_TableRegion` | Fläche und Zeilenbänder einer erkannten Tabelle | |
| Abschnittszeile | – | Fette, größere Einzelzelle innerhalb einer Tabelle; trennt zwei Tabellen und wird zur Überschrift | |
| Lesereihenfolge | `_reading_order` | Von oben nach unten, bei vertikaler Überlappung spaltenweise | |
| Kopf-/Fußzone | `header_zone_ratio`, `footer_zone_ratio` | Seitenränder, deren Text verworfen wird (Seitenzahl, Bank, Register) | |
| Parser-Einstellungen | `ParserSettings` | Schwellwerte des Parsers (`min_chars`, `max_block_chars`, `cell_gap_pt` …) | |
| Ingestion | `run_ingestion` | Pipeline von `documents.yaml` und PDFs zu den JSON-Dateien; idempotent | |
| Parse-Fehler | `ParseError` | PDF fehlt, ist nicht lesbar oder enthält keinen Inhalt | |
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

## Retrieval (M4)

| Begriff | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Index | `build_index` | ChromaDB-Collection `chunks` mit Embeddings und Metadaten aller Chunks außer Überschriften; wird bei jedem Lauf neu gebaut | |
| Aufgaben-Präfix | `document_task_prefix`, `query_task_prefix` | `search_document: ` vor indexierten Texten, `search_query: ` vor Anfragen (verlangt `nomic-embed-text`) | |
| Hierarchie-Präfix | `hierarchy_prefix` | `[Ordner \| Datei \| Kapitel > Unterkapitel]` vor dem Chunk-Inhalt, damit der Pfad Teil des Vektors wird | |
| Metadatenfilter | `MetadataFilter`, `build_where` | Harte Einschränkung auf Sparte, Dokumenttyp, Vertragsnummer oder Zeitraum als ChromaDB-`where` | |
| Kandidaten | `candidate_count` | Die 20 ähnlichsten Chunks der Vektorsuche, bevor der Boost sie neu ordnet | |
| Basis-Score | `base_score` | `1 − Cosinus-Abstand` zwischen Anfrage und Chunk | |
| Hierarchie-Boost | `boost`, `hierarchy_boost` | Faktor 1.5, wenn ein Anfrageterm im Dateinamen, Ordner oder in den Überschriften steht, sonst 1.0 | |
| Finaler Score | `final_score` | `base_score × boost`; danach wird sortiert | |
| Pfadtreffer | `matched_terms`, `path_matches` | Die Anfrageterme, die den Boost ausgelöst haben | |
| Retriever | `Retriever` | Klasse, die Anfrage einbettet, ChromaDB abfragt und die Treffer neu ordnet | |
| Treffer | `SearchHit` | Ein Suchergebnis mit Inhalt, Pfad, Seite und allen drei Score-Zahlen | |
| Evidenz | `build_evidence` | Treffer, gruppiert nach Dokument und Kapitel, mit Typ-Kennzeichnung (KI-Texte sind kein Beleg) | |
| Vergleichslauf | `run_comparison` | Die 12 Fragen unter sechs Konfigurationen (Filter, Boost, Chunk-Auswahl), bewertet gegen die erwarteten Quellen | |
| MRR | `mean_reciprocal_rank` | Mittelwert von 1/Rang der ersten richtigen Quelle; 1.0 heißt immer auf Platz 1 | |
| Agentenschleife | `AgentLoop` | Ruft das Modell, führt dessen Tool-Aufrufe aus, gibt die Beobachtungen zurück und wiederholt das bis zur Antwort oder zum Limit | |
| Werkzeug (Agent) | `AgentTool` | Name, Beschreibung, Argumentmodell und Funktion eines Tools; erzeugt auch das JSON-Schema für Ollama | |
| Werkzeugkasten | `ToolBox` | Baut die sechs Tools aus Einstellungen, Suche und Dokumentkatalog | |
| Beobachtung | `observation` | Text, den ein Tool an das Modell zurückgibt (Treffer, Liste, Rechenergebnis oder `FEHLER:`) | |
| Belegnummer | `EvidenceBook` | Laufende Nummer `[n]` je gefundenem Chunk in einem Lauf; das Modell zitiert sie, die Oberfläche zeigt sie | |
| Schritt | `ModelCallStep`, `ToolCallStep` | Ein Modellaufruf (mit Token und Zeiten) oder ein Tool-Aufruf (mit Argumenten und Beobachtung) im Log | |
| Lauf | `AgentRun` | Frage, Antwort, Endgrund, alle Schritte und die nummerierten Quellen einer Frage | |
| Endgrund | `stop_reason` | `answer`, `tool_limit`, `context_limit` oder `empty_answer` | |
| Werkzeuglimit | `max_tool_calls` | Höchstens 6 Tool-Aufrufe je Frage, gültige und ungültige | |
| Kontextwächter | `context_reserve_tokens` | Beendet die Suche, wenn Prompt und Beobachtungen den Platz für die Antwort aufbrauchen würden | |
| Rechner | `calculate` | Rechnet Ausdrücke über den Syntaxbaum (`ast`) mit `Decimal`, ohne `eval` | |
| Jahresfilter-Regel | `YEAR_FILTER_DOC_TYPES` | Der Jahresfilter gilt nur für Dokumente mit Abrechnungszeitraum (Rechnung, Hinweis, Abschlagsplan) | |
| Laufprotokoll | `RunLog` | Schreibt jeden Schritt sofort als JSON-Zeile nach `data/eval/<run>/` | |
