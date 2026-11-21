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
| Hierarchie-Prefix | – | Begriff aus dem Konzept (`[Sparte \| Dokumenttyp \| Datei \| Kapitel]`); umgesetzt und in der Ausarbeitung verwendet als „Hierarchie-Präfix“ (ADR-0009) | |
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
| Act (ReAct-Variante) | – | Variante aus dem ReAct-Paper ohne Thought, nur Action → Observation; so laufen P2 und `qwen2.5:7b`, weil der Prompt keinen Thought verlangt (ISS-102) | |
| Orchestrierung | `AgentLoop` (`agent/loop.py`) | Wer den Ablauf steuert: in P2 wählt das Modell zur Laufzeit Werkzeug und Argumente, die eigene Schleife führt die Aufrufe aus und setzt Grenzen (6 Aufrufe, Kontext, Rückfragen); in P1 legt der Code den Ablauf fest | |
| Naive RAG / Modular RAG | – | Begriffe aus Gao et al. 2023: Naive RAG sucht einmal mit der Frage (Top-K) und antwortet; Modular RAG besteht aus Bausteinen, die sich austauschen oder umkonfigurieren lassen; Metadaten im Index und Query-Rewriting zählen dort zum Advanced RAG | |
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
| Werkzeugkasten | `ToolBox` | Baut die fünf Tools aus Einstellungen, Suche und Dokumentkatalog | |
| Beobachtung | `observation` | Text, den ein Tool an das Modell zurückgibt (Treffer, Liste, Rechenergebnis oder `FEHLER:`) | |
| Belegnummer | `EvidenceBook` | Laufende Nummer `[n]` je gefundenem Chunk in einem Lauf; das Modell zitiert sie, die Oberfläche zeigt sie | |
| Schritt | `ModelCallStep`, `ToolCallStep` | Ein Modellaufruf (mit Token und Zeiten) oder ein Tool-Aufruf (mit Argumenten und Beobachtung) im Log | |
| Lauf | `AgentRun` | Frage, Antwort, Endgrund, alle Schritte und die nummerierten Quellen einer Frage | |
| Endgrund | `stop_reason` | `answer`, `tool_limit`, `context_limit`, `repeat_limit` oder `empty_answer` | |
| Werkzeuglimit | `max_tool_calls` | Höchstens 6 Tool-Aufrufe je Frage, gültige und ungültige | |
| Kontextwächter | `context_reserve_tokens` | Beendet die Suche, wenn Prompt und Beobachtungen den Platz für die Antwort aufbrauchen würden | |
| Rechner | `calculate` | Rechnet Ausdrücke über den Syntaxbaum (`ast`) mit `Decimal`, ohne `eval` | |
| Jahresfilter-Regel | `YEAR_FILTER_DOC_TYPES` | Der Jahresfilter gilt nur für Dokumente mit Abrechnungszeitraum (Rechnung, Hinweis, Abschlagsplan) | |
| Laufprotokoll | `RunLog` | Schreibt jeden Schritt sofort als JSON-Zeile nach `data/eval/<run>/` | |

## Evaluation (M6)

| Begriff | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Variante | `Variant`, `VariantName` | Eine der drei verglichenen Lösungen: `b0`, `p1`, `p2` | |
| B0 – Volltext-Baseline | `FullTextVariant`, `build_full_text_context` | Seitentext aller Dokumente in Katalogreihenfolge, bis das Kontextfenster voll ist; ein Modellaufruf ohne Suche | |
| P1 – Pipeline | `PipelineVariant` | Eine Suche (Top-5, ohne Filter, mit Boost), danach ein Modellaufruf mit den nummerierten Treffern | |
| P2 – Agent | `AgentVariant`, `answer_from_run` | Der ReAct-Agent aus M5, übersetzt ins gemeinsame Antwortformat | |
| Antwortdatensatz | `VariantAnswer` | Antwort einer Variante auf eine Frage mit gezeigten Quellen, Tool-Aufrufen und Modellaufrufen | |
| Gezeigte Quelle | `ShownSource` | Nummerierter Beleg, den das Modell sah und als `[n]` zitieren kann | |
| Token-Budget (B0) | `full_text_budget` | `num_ctx − num_predict − Reserve − Prompt`; so viel Seitentext darf in den B0-Prompt | |
| Generieren / Bewerten | `generate`, `score` | Getrennte Schritte: Antworten erzeugen (Ollama, langsam) und deterministisch bewerten (ohne Ollama) | |
| Bewertung einer Antwort | `AnswerScore`, `score_answer` | Alle eigenen Metriken einer Antwort gegen die Ground Truth | |
| Zusammenfassung je Variante | `VariantSummary`, `summarize` | Summen und Quoten einer Variante über alle Fragen (Tabelle Variante × Metrik) | |
| Quellen-Präzision | `cited_expected / cited_count` | Anteil der zitierten Belege, deren Datei und Seite erwartet sind (der Code zählt bis zur Korrektur im Zähler Seiten statt Belege, ISS-123) | |
| Quellen-Recall | `expected_cited / expected_count` | Anteil der erwarteten Quellen, die die Antwort zitiert | |
| Erfundene Belegnummer | `invalid_citations` | Zitierte `[n]`, die das Modell nie gesehen hat | |
| Ablenkerquote | `cited_distractors`, `shown_distractors` | Anteil von Ablenkungsdokumenten (`is_noise_document`) in den Zitaten bzw. im Kontext | |
| Filterfehler | `filter_misses`, `filter_excludes` | Suche des Agenten, deren selbst gesetzter Filter ein erwartetes Quelldokument ausschließt | |
| Prüfurteil | `answer_verdict`, `expected_verdict` | Ja/Nein einer Prüffrage (stimmt die Abrechnung?); daraus Fehlererkennung und Fehlalarm | |
| Fehlererkennung / Fehlalarm | `errors_detected`, `false_alarms` | Erwartet „nein“ und geantwortet „nein“ / erwartet „ja“ und geantwortet „nein“ | |
| Laufmanifest | `manifest.json` | Modell, `num_ctx`, B0-Kontext (welche Dateien passten) und RAGAS-Einstellungen eines Evaluationslaufs | |
| Belegtexte | `VariantAnswer.contexts` | Text der Belege, wie das Modell sie sah (B0 Seitenblöcke, P1 Treffer, P2 Tool-Beobachtungen); Eingabe für RAGAS | |
| Eingebauter Fehler einer Frage | `Question.planted_error` | Id des eingebauten Fehlers (E1–E3), den eine Prüffrage aufdecken soll (G1, G3, G4) | |
| RAGAS | `ragas_eval`, Befehl `ragas` | Framework, das Antworten mit einem LLM als Bewerter benotet; hier lokal mit `audit-judge` | |
| Bewertermodell | `audit-judge`, `RagasJudge` | Alias von `qwen2.5:7b` mit festem `num_ctx` 8192, bewertet für RAGAS | |
| Faithfulness | `faithfulness` | Anteil der Aussagen einer Antwort, die durch die gezeigten Belege gedeckt sind (0–1) | |
| Context Recall | `context_recall` | Anteil der Aussagen der erwarteten Antwort (`expected_answer`), die in den gezeigten Belegen stehen (0–1); der Bewerter zerlegt die Referenz in Aussagen und urteilt je Aussage (Code ragas 0.4.4, ISS-102), eine Aussage mit einem unbelegten Teil zählt ganz als nicht belegt (ISS-086) | |
| RAGAS-Status | `RagasStatus` | `ok`, `too_long` (Prompt passt nicht, nicht gekürzt), `no_context`, `not_applicable`, `no_statements`, `error` | |
| Belegabgleich | `scripts/check_evidence.py`, `evidence.json` | Prüft je gespeicherter Antwort, ob die Sollfakten im Kontext des Modells standen und ob die erwarteten Quellen gezeigt wurden; trennt „Beleg kam nie an“ von „Beleg da, Antwort falsch“ | |
| Reine Lückenantwort | `is_gap_only`, `GAP_ANSWER` | Antwort, die nur aus dem Satz „Dazu liegen in den Unterlagen keine Angaben vor.“ besteht | |
| Hauptursache eines Fehlschlags | – | Von Hand vergebene Klasse je falscher Antwort: Kontextbudget, Retrieval, Tool-Wahl, Filter, Argumente, Synthese, Parser (evaluation-log, RUN-010/011) | |
| Handprüfung | – | Lesen jeder Antwort gegen Ground Truth und Belege; korrigiert „richtig laut Metrik“ zu „richtig nach Handprüfung“ (ISS-050) | |
| Knapp als richtig gewertet | – | Antwort, der ein Teil fehlt (etwa Z1 ohne z-Zahl), die nach Handprüfung trotzdem als richtig zählt; im evaluation-log „Grenzfall“ genannt, in der Ausarbeitung umbenannt, damit es nicht mit der Fragekategorie Grenzfälle (G1–G4) verwechselt wird | |
| Frage ohne Prüfung | – | Die 8 Testfragen, die keine Prüffrage sind (S1–S4, N1, N2, Z2, Z3); Grundlage der Qualitätsaussage in Kapitel 5 | |
| Suchwerkzeug | `search` | Einziges Textsuchwerkzeug des Agenten; durchsucht Fließtext und Tabellenzeilen, Filter nur `utility_type` (ADR-0014) | |
| Gegenstück | `include_counterpart` | Parameter von `search` für Prüffragen: ergänzt je bis zu 2 Treffer aus Vertrag/Preisschreiben bzw. Rechnung, falls die erste Suche nur eine Familie trifft | |
| Bestandsmeldung | `ToolBox._inventory` | Text bei leerer Suche: nennt Sparten und Dokumentarten, zu denen Unterlagen vorliegen (ISS-051) | |
| Wiederholungssperre | `_CallMemory`, `REPEAT_OBSERVATION`, `REPEAT_FAILED_OBSERVATION`, `ToolCallStep.is_repeat` | Ein Aufruf mit gleichem Werkzeug und gleichen (bereinigten) Argumenten wird in derselben Frage nicht erneut ausgeführt, ebenso ein schon fehlgeschlagener; das Modell bekommt einen Hinweis, der Aufruf zählt zum Limit (ADR-0015) | |
| Prüffrage | `is_audit_question` | Frage, die eine Rechnung gegen Vertrag, Preisschreiben oder Zählerstände prüfen lässt; erkannt am Wortlaut (korrekt, stimmt, passt, …) | |
| Rechennachfrage | `CALCULATE_BEFORE_ANSWER_MESSAGE`, `NudgeStep.reason` | Einmalige Rückfrage des Loops, wenn eine Prüffrage ohne `calculate` beantwortet werden soll (ISS-058, ADR-0015) | |
| Lückenrückfrage | `RETRY_BEFORE_GAP_MESSAGE`, `NudgeStep.reason="gap"`, `AgentSettings.min_searches_before_gap` | Einmalige Rückfrage des Loops, wenn das Modell nach weniger als 2 Werkzeugaufrufen „keine Angaben“ antwortet: noch einmal anders suchen und mit `list_documents` prüfen (ADR-0010, ISS-036) | |
| Prüfablauf | `agent/audit_flow.py`, `run_audit_flow`, `AuditFlowStep` | Fester Ablauf für Prüffragen: Modell plant Prüfgrößen und Suchanfragen, Code sucht, Modell liest Soll- und Istzahl, Code prüft die Herkunft und rechnet die Differenz (ADR-0016) | |
| Prüfgröße | `PlannedCheck`, `AuditCheckResult.quantity` | Eine Größe, die der Prüfablauf vergleicht (Arbeitspreis, Wohnfläche, z-Zahl, …) mit Sollwert (Vertrag, Preisschreiben) und Istwert (Rechnung) | |
| Strukturierte Ausgabe | `format` (JSON-Schema) im Ollama-Chat-Aufruf | Das Modell darf nur JSON nach einem Schema erzeugen; der Prüfablauf nutzt sie für Plan und Lesen | |
| Laufzeitauswertung | `scripts/analyze_timing.py` | Zerlegt die P2-Zeit eines Laufs in Prefill und Dekodieren, erste und spätere Modellaufrufe (ISS-057) | |
| Entladen je Frage | `unloads_after_each_question`, `_unload` | Die Auswertung gibt Chat- und Embedding-Modell nach jeder P1/P2-Frage frei (Schutz vor OOM, ISS-043); führt in RUN-012 und RUN-013 zu rund 90 s Prefill für die erste Anfrage je Frage (ISS-057) | |
| Größen-Anfrage | `quantity_query`, `new_quantity_hits`, `AgentSettings.quantity_hits` | Die Frage oder Suchanfrage ohne Jahr, Dokument- und Fragewörter („neuer Arbeitspreis 2025“ → „Arbeitspreis“); eine zweite Suche damit ergänzt P1 und P2 um bis zu 2 neue Treffer (ISS-072, ADR-0017) | |
| Sparte der Anfrage | `utility_in_query`, `with_query_utility`, `UTILITY_WORDS` | Die eine Sparte, die eine Frage nennt („Stromabrechnung“ → `electricity`); Größen- und Gegenstück-Suche filtern danach, wenn noch kein Sparten-Filter gesetzt ist (ISS-077, ADR-0017 Nachtrag M6i) | |
| Query-Rewriting | – (P2: Suchanfrage des Agenten; `quantity_query`) | Umformulieren der Suchanfrage vor der Suche; im Prototyp ohne eigenes Modell: Der Agent formuliert seine Anfragen selbst, die Größen-Anfrage streicht Füllwörter im Code (ADR-0009 Punkt 8, ADR-0017) | |
| Sollfakt | `facts` in `dataset/ground_truth.yaml` | Angabe, die eine richtige Antwort enthalten muss, meist eine Zahl mit Einheit, vereinzelt Frist oder Urteil (27 über alle 14 Fragen); „Sollfakten im Kontext“ zählt, wie viele davon in den Belegen des Modells standen (`check_evidence.py`); in ADR-0017 und im evaluation-log auch „Sollzahlen“ | |
| Zitier-Rückfrage | `CITE_BEFORE_ANSWER_MESSAGE`, `has_citation`, `NudgeStep.reason="cite"`, `AgentSettings.require_citation` | Einmalige Rückfrage des Loops, wenn eine Antwort Zahlen, aber keine Treffernummer `[n]` enthält (ADR-0017) | |
| Text-Aufruf | `parse_text_call`, `TextCall`, `ToolCallStep.is_text_call` | Werkzeugaufruf, den das Modell als JSON ans Ende seines Antworttexts schreibt statt als nativen Tool Call; der Loop führt ihn wie einen nativen aus (ISS-061) | |
| Geldfakt | `MONEY_UNITS`, `_is_money` | Erwarteter Fakt mit Einheit ct oder EUR; nur bei ihm gilt der Umrechnungsfaktor 100 bzw. 0,01 der Metrik (ISS-050) | |

## M8: Heizstrom, Faktenspeicher und Agent v2

| Begriff | Code (EN) | Kurzdefinition | In meinen Worten |
|---|---|---|---|
| Lichtstrom / Heizstrom | `TariffKind.HOUSEHOLD` / `TariffKind.HEATING`, `tariff_kind` | Haushaltsstrom (Eintarifzähler) und Strom für die Nachtspeicherheizung mit Zweitarifzähler; nur bei Sparte Strom gesetzt (ADR-0018) | |
| HT / NT | `zone` | Hochtarif (06–22 Uhr) und Niedertarif (22–06 Uhr) des Heizstroms; je Zone eigener Preis und eigener Zählerstand | |
| Faktenspeicher | `FactStore`, `facts.json` | Alle per Regel gelesenen Zahlen des Korpus mit Rolle, Gültigkeit, Zone und Quell-Chunk (ADR-0018) | |
| Fakt | `Fact`, `FactKind` | Eine Zahl mit Bedeutung, z. B. Arbeitspreis NT 24,10 ct/kWh gültig ab 01.01.2025 aus Dok. 33 | |
| Vereinbart / abgerechnet | `Role.AGREED` / `Role.STATED` | Sollwert aus Vertrag, Preisschreiben, Abschlagsplan, Mietvertrag gegen Istwert aus Rechnung oder Mitteilung | |
| Geltender Wert | `FactStore.agreed()` | Der vereinbarte Wert mit dem spätesten „gültig ab“ vor dem Stichtag | |
| Prüfregel | `check_bill`, `Check`, `CheckStatus` | Vergleich im Code: Preis, Zählerstände, Umrechnung und z-Zahl, Rechenweg, Abschläge, Wohnfläche; Ergebnis stimmt / ABWEICHUNG / nicht prüfbar mit Auswirkung in EUR | |
| Werkzeugsatz v1 / v2 | `AgentSettings.tool_set` | v1: Suchwerkzeuge aus M5/M6; v2: plan, list_documents, check_bill, get_facts, search, make_overview, make_chart, calculate (ADR-0019) | |
| Plan-Schritt | `plan`, `AgentRun.plan` | Erster Werkzeugaufruf des Agenten v2: 2–5 Schritte mit Werkzeug und Ziel | |
| Selbstprüfung | `_self_check`, `NudgeReason` (`check`, `chart`, `overview`, `verdict`, `plan`, `language`, `numbers`) | Prüfung vor der Antwort: Prüffrage ohne `check_bill`, fehlende Grafik oder Übersicht, Urteil gegen `check_bill`, geplanter Schritt fehlt, Antwort nicht deutsch, Zahlen ohne Werkzeugergebnis; je Grund eine Rückfrage | |
| Artefakt | `Artifact` | Tabelle oder Grafik eines Werkzeugs, die an die Antwort angehängt wird (Markdown, PNG, JSON) | |
| Zurückgehaltene Fragen | `holdout_questions.yaml`, `--holdout` | 8 Testfragen (T1–T8), vor M8 geschrieben, nur für den Endlauf (ISS-108) | |
| Werkzeugauswahl nach Fragetyp | `route_tools`, `AgentSettings.route_tools` | Code bietet je Fragetyp (Prüffrage, Grafik, Übersicht, sonst) nur passende Werkzeuge an (ADR-0020) | |
| Argument-Reparatur | `scope.repair_utility_arguments` | Korrigiert Sparte, Stromart und Jahr der Werkzeugargumente anhand der Frage; steht als „Hinweis: Argumente angepasst“ im Ergebnis (ISS-114) | |
| Hinweis (Prüfung) | `CheckStatus.NOTICE` | Plausibilitätshinweis, z. B. Verbrauch über 25 % anders als im Vorjahr; kein Fehler | |
| Trockenlauf / Orakel | `scripts/dry_run.py`, `FakeOllama` | Nachtlauf ohne Ollama in einem Temp-Ordner; ein regelbasiertes Orakel wählt Werkzeuge statt des Modells; zeigt Abstürze und die Obergrenze der Werkzeuge (ISS-116) | |
| Schritt-Text | `strip_step_talk`, `NudgeReason` `steps` | Angekündigte Schritte und Pläne in einer Antwort („Plan: 1. check_bill …“, „Lassen Sie uns …“); werden entfernt, eine reine Ankündigung wird einmal nachgefragt (ADR-0021) | |
| Leere Antwort | `EMPTY_ANSWER_MESSAGE`, `NudgeReason` `empty` | Einmaliger Antwortaufruf ohne Werkzeuge, wenn das Modell nichts geschrieben hat (ADR-0021) | |
| Rückfall-Antwort | `AgentRun.is_fallback_answer`, `FALLBACK_REASONS` | Die letzte echte Antwort vor einer Rückfrage gilt, wenn die Antwort danach leer, eine Lücke oder nur Schritt-Text ist (ADR-0021) | |
| Wiederholungsgrenze | `REPEAT_LIMIT`, `StopReason` `repeat_limit` | Nach 2 wiederholten Werkzeugaufrufen erzwingt die Schleife eine Antwort (ADR-0021) | |
| Erwartete Werkzeuge v2 | `expected_tools_v2`, `uses_tool_set_v2` | Erwartete Werkzeuge einer Frage im Werkzeugsatz v2, wo sie von v1 abweichen; ob ein Lauf v2 ist, erkennt die Bewertung an v2-Werkzeugen im Lauf (ISS-118) | |
| Kennzahlen Agentik | `scripts/analyze_agentics.py`, `agentics.json` | Wie der Agent arbeitete: Stoppgründe, Werkzeuge, Plan, Rückfragen, Wiederholungen, Schritt-Text, durch Rückfrage verschlechterte Antworten (ISS-117) | |
