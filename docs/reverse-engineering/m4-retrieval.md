# Reverse Engineering – M4: Embedding & Retrieval

> Pro Meilenstein eine Kopie der Vorlage. Abschnitte 1–4 hat Claude vorbereitet, Abschnitte 5–7 schreibe ich selbst.
> Ziel (Professor): Konzept (logisch) und Prototyp (technisch) „in all seinen Körperteilen“ verstehen: Code-Dateien, Funktionen, Datenstrukturen, Datenflüsse, Bibliotheken.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m4-retrieval` (kein Tag, `v0.2.0` kommt nach M5) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `config.py` (Erweiterung) | Zentrale Parameter für Index und Suche (Top-20, Top-5, Boost 1.5, Task-Präfixe, Collection-Name) | `RetrievalSettings`, `Settings.retrieval` | pydantic |
| `retrieval/models.py` | Typisierte Optionen und Ergebnisse der Suche | `MetadataFilter`, `SearchOptions`, `SearchHit`, `RetrievalError` | `corpus` (Enums), `ingestion` (`ChunkType`) |
| `retrieval/index.py` | Baut aus `data/processed/` die ChromaDB-Collection (Text mit Hierarchie-Präfix → Embedding → Speicher) | `load_chunks`, `hierarchy_prefix`, `embedding_text`, `chunk_record`, `embed_texts`, `build_index`, `get_collection` | `ingestion`, `config`, chromadb, Ollama |
| `retrieval/search.py` | Einbetten der Anfrage, ChromaDB-Abfrage mit Filter, Hierarchie-Boost, Neusortierung | `Retriever.search`, `tokenize_query`, `path_matches`, `build_where`, `fold` | `index` (Hilfsfunktionen), `models`, chromadb |
| `retrieval/evidence.py` | Ordnet Treffer als Dokument → Kapitel → Treffer und kennzeichnet KI-Texte | `build_evidence`, `render_evidence_text` | `models`, `index` |
| `retrieval/compare.py` | Vergleichslauf: 12 Fragen × 6 Konfigurationen gegen die erwarteten Quellen (nur Evaluation) | `QUESTION_FILTERS`, `CONFIGS`, `evaluate_question`, `summarize`, `run_comparison`, `render_markdown` | `search`, `corpus` (Ground Truth) |
| `retrieval/__main__.py` | CLI mit drei Unterbefehlen `index`, `search`, `compare` | `main`, `_run` | alle oben, `ollama.Client` |
| `tests/test_retrieval.py` | 39 schnelle Tests ohne Ollama (Fake-Embedder, ChromaDB in `tmp_path`) | `FakeEmbedder`, `TestBuildIndex`, `TestSearch`, `TestComparison` … | pytest, chromadb |

## 2. Datenfluss
Beispiel: Frage **S2** „Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?“ (Filter `utility_type=electricity`), erster Treffer aus RUN-004.

**A) Index (einmalig, `python -m audit_agent.retrieval index`)**
```
data/processed/03_Strom_Preisanpassung_SuedVolt_2025_chunks.json
  → load_chunks()        alle 30 Dateien, 629 Chunks, prüft doppelte chunk_ids
  → is_indexed()         82 Überschriften fallen weg → 547 Chunks
  → embedding_text()     "search_document: [01_electricity_suedvolt | 03_Strom_Preisanpassung_SuedVolt_2025 |
                          Anpassung Ihrer Strompreise zum 01.01.2025 > Preisgegenüberstellung im Detail (ab 01.01.2025)]
                          Die Tabelle zeigt die Anpassung der Strompreise …"      (Chunk …_p1_tab02_sum)
  → embed_texts()        16 Texte je Aufruf an Ollama (nomic-embed-text) → 768 Zahlen je Text
  → chunk_record()       {filename, chunk_type: "table_summary", utility_type: "electricity", doc_type: "price_adjustment",
                          period_start: 20250101, …, heading_stack: '["Anpassung …", "Preisgegenüberstellung …"]', has_heading: True}
  → collection.add()     ids, Vektoren, Originaltext (ohne Präfix), Metadaten → data/vectors/
```
**B) Suche (`Retriever.search`)**
```
"Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?"
  → embed_query()        "search_query: " + Frage → 768 Zahlen
  → build_where()        {"utility_type": {"$eq": "electricity"}}
  → collection.query()   20 nächste Chunks, Abstand d (Cosinus) je Chunk
  → tokenize_query()     ("arbeits", "grundpreis", "stromvertrag")      (Stoppwörter und Wörter < 3 Zeichen entfallen)
  → path_matches()       Chunk-Pfad enthält Ordner "01_electricity_suedvolt", Datei "03_Strom_…": Wort "strom" ist der Anfang
                          von "stromvertrag" → matched_terms = ("stromvertrag",) → boost = 1.5
  → base_score 1 − d = 0.712  ·  final_score = 0.712 × 1.5 = 1.068
  → sortieren nach final_score, die besten 5 → list[SearchHit]
```
**C) Evidenz (`build_evidence`)**: Treffer nach `filename` und `heading_stack` gruppieren, Gruppen nach bestem Score sortieren, `table_summary` als „KI-Zusammenfassung, kein Beleg“ markieren.

## 3. Datenstrukturen
- **`RetrievalSettings`** (frozen): `collection_name`, `document_task_prefix`, `query_task_prefix`, `embed_batch_size` (16), `candidate_count` (20), `top_k` (5, höchstens `candidate_count`), `hierarchy_boost` (1.5), `min_term_chars` (3), `keep_alive`.
- **`MetadataFilter`**: optionale Felder `utility_type`, `doc_type`, `contract_id`, `period_start`/`period_end` (nur beide oder keins; Start ≤ Ende). `for_year(2025)` setzt den Zeitraum auf das Kalenderjahr.
- **`SearchOptions`**: `metadata_filter`, `use_hierarchy_boost`, `chunk_types` (Menge oder `None`), `require_heading`, `top_k`.
- **`SearchHit`**: `chunk_id`, `chunk_type`, `content`, `heading_stack`, `page_number`, `filename`, `base_score`, `boost` (1.0 oder 1.5), `final_score`, `matched_terms`.
- **Chroma-Metadaten** (flach, ohne `None`): Text, Zahl oder Wahrheitswert; Datum als Zahl `YYYYMMDD`, `heading_stack` als JSON-Text.
- **`IndexReport`**: Modell, Dokumentzahl, Chunkzahl je Typ, übersprungene Überschriften, Vektorlänge, Sekunden.
- **`EvidenceDocument` → `EvidenceChapter` → `SearchHit`**: Gruppierung für die Anzeige.
- **`CompareConfig`, `QuestionResult`, `ConfigSummary`, `ComparisonReport`**: Konfiguration und Messwerte des Vergleichslaufs (Rang der erwarteten Datei und Seite, Ablenker-Treffer, MRR).

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| `chromadb` 1.5.9 | Lokale Vektordatenbank in `data/vectors/` | `PersistentClient`, `create_collection(configuration={"hnsw": {"space": "cosine"}}, embedding_function=None)`, `add`, `query(query_embeddings, n_results, where, include)`, `delete_collection`, `count` | FAISS, sqlite-vec, Qdrant (lokal) |
| `ollama` 0.6.3 | Embeddings von `nomic-embed-text` | `Client.embed(model, input=[…], keep_alive)`; `generate(keep_alive=0)` zum Entladen | `sentence-transformers` im Python-Prozess |
| `pydantic` 2.14.3 | Frozen-Modelle und Validierung (Zeitraum, `top_k`) | `BaseModel`, `ConfigDict(frozen=True)`, `model_validator`, `model_copy(update=…)` | `dataclasses` + eigene Prüfungen |
| `re`, `json` (Standardbibliothek) | Wörter aus Anfrage und Pfad, `heading_stack` als Text speichern | `re.compile(r"[^\W_]+").findall`, `json.dumps/loads` | `nltk`-Tokenizer (für diesen Zweck zu schwer) |
| `argparse` | CLI mit Unterbefehlen | `add_subparsers` | `typer`, `click` |
| `pytest` | Whitebox-Tests mit Fake-Embedder | `fixture`, `raises`, `approx` | `unittest` |
