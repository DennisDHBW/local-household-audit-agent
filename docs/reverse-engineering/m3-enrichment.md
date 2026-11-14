# Reverse Engineering – M3: Enrichment & Cache

> Abschnitte 1–4 von Claude vorbereitet, Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m3-enrichment` (Tag folgt mit M5) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `src/audit_agent/enrichment/cache.py` | Festplatten-Cache für Modellantworten mit SHA-256-Schlüssel | `make_cache_key`, `digest_bytes`, `CachedAnswer`, `EnrichmentCache.get_or_compute` | `diskcache`, `pydantic` |
| `src/audit_agent/enrichment/llm.py` | Die kleine Schnittstelle zu Ollama (ein Chat-Aufruf, Entladen, Modellliste) | `ChatClient` (Protocol), `ask_model`, `model_options`, `unload_model`, `unload_all_running`, `EnrichmentError` | `ollama`, `cache.py`, `config.py` |
| `src/audit_agent/enrichment/prompts.py` | Prompt-Vorlagen (deutsch) und das Einsetzen von Kontext und Zeilen | `CAPTION_PROMPT`, `SUMMARY_PROMPT`, `build_caption_prompt`, `build_summary_prompt`, `describe_context` | – |
| `src/audit_agent/enrichment/captioner.py` | Beschreibt ein Diagramm mit dem Vision-Modell, mit Cache | `ImageCaptioner.caption`, `.cache_key`, `.is_cached` | `cache.py`, `llm.py`, `prompts.py` |
| `src/audit_agent/enrichment/summarizer.py` | Fasst eine Tabelle mit dem Textmodell zusammen, mit Cache | `TableSummarizer.summarize`, `.cache_key`, `.is_cached` | wie Captioner |
| `src/audit_agent/enrichment/checks.py` | Meldet Zahlen in einer Summary, die nicht im Tabellentext stehen | `unsupported_numbers`, `_date_parts` | `numbers.py` |
| `src/audit_agent/enrichment/pipeline.py` | Steuert den Lauf: Jobs bilden, Phasen nacheinander, Chunks ersetzen/einfügen, JSON schreiben, Report | `run_enrichment`, `_enrich_images`, `_enrich_tables`, `_with_captions`, `_with_summaries`, `EnrichmentReport` | alle oben, `ingestion` |
| `src/audit_agent/enrichment/__main__.py` | Kommandozeile mit `--only`, `--limit`, `--dry-run`, `--run-id` | `main` | `pipeline.py` |
| `src/audit_agent/numbers.py` | Zahlen im deutschen und englischen Format erkennen (aus dem Smoke-Test herausgelöst) | `parse_number`, `extract_numbers` | `re` |
| `src/audit_agent/ingestion/models.py` | Neu: Chunk-Typ `table_summary` und Prüfung der `table_id` | `ChunkType.TABLE_SUMMARY`, `DocumentChunk._check_type_details` | `pydantic` |
| `src/audit_agent/config.py` | Neu: Token-Limits und `keep_alive` des Enrichments | `EnrichmentSettings`, `Settings.enrichment`, `Settings.cache_dir` | `pydantic` |
| `tests/test_enrichment.py` | Tests mit einem skriptbaren Ollama-Fake, ohne laufendes Ollama | 24 Testfälle | `pytest` |

## 2. Datenfluss
Beispiel: die Tabelle „Zählerstände“ der Stromabrechnung 2024 (`04_Strom_Jahresabrechnung_2024_SuedVolt.pdf`, Seite 1, `table_id` `p1_tab02`) und das Diagramm auf Seite 2.

```
data/processed/04_Strom_..._chunks.json (von der Ingestion)
  → load_processed_documents: alle *_chunks.json laden, je Datei ein ParsedDocument
  → run_enrichment: ensure_models_available (Fail Fast), unload_all_running (RAM leeren)

Phase 1: Bild  (…_p2_img01, content = Platzhalter)
  → _enrich_images: Job = (Datei, image-Chunk); _read_image liest images/…png
  → ImageCaptioner.caption: Prompt = CAPTION_PROMPT + "Titel > Kapitel"
  → make_cache_key(task, model, prompt, options, SHA-256 der Bildbytes) → Schlüssel
  → EnrichmentCache.get_or_compute: Treffer? sonst ask_model → gemma3:4b (ca. 74 s) → CachedAnswer
  → _with_captions: image-Chunk bekommt die Caption als content (model_copy)
  → _write_documents; unload_model(gemma3:4b)

Phase 2: Tabelle (…_p1_tab02_r01 und _r02)
  → _table_jobs: Zeilen mit gleicher table_id zu einem _TableJob gruppieren
  → TableSummarizer.summarize: Prompt = Kontext + Spalten + "- Zählernummer: … | Zählerstand: 14.200 kWh | …"
  → Cache (Schlüssel aus dem fertigen Prompt) → llama3.2 (ca. 19 s) → Summary-Text
  → unsupported_numbers(Summary, Zeilen + Überschriften + Spalten) → Liste unbelegter Zahlen
  → Summary-Chunk: Kopie der ersten Zeile mit neuer ID …_p1_tab02_sum, Typ table_summary
  → _with_summaries: alte Summary derselben Tabelle entfernen, neue vor die erste Zeile setzen
  → ParsedDocument neu aufbauen (Validierung: eindeutige IDs), JSON schreiben, Modell entladen

→ EnrichmentReport (Treffer, Fehlgriffe, abgeschnitten, unbelegte Zahlen) → data/eval/<run-id>/enrichment.json
```

## 3. Datenstrukturen
- **`CachedAnswer`:** `text` (Antwort), `model` (Tag), `seconds` (Dauer des Originalaufrufs, nicht des Cache-Treffers), `is_truncated` (Token-Limit erreicht, aus `done_reason == "length"`).
- **`EnrichmentCache`:** Wrapper um `diskcache.Cache` in `.cache/enrichment/`; speichert `CachedAnswer.model_dump()` unter dem Hash-Schlüssel.
- **Cache-Schlüssel:** SHA-256 über JSON aus `task`, `model`, `prompt`, `options`, `image` (Hash der Bildbytes oder `null`).
- **`DocumentChunk` (Typ `table_summary`):** wie eine Tabellenzeile (`heading_stack`, Seite, `metadata.table_id`, `metadata.columns`), aber mit der Modellantwort als `content` und der ID `<…>_tabNN_sum`.
- **`_TableJob`:** Datei, `table_id`, die Zeilen-Chunks der Tabelle in Lesereihenfolge.
- **`EnrichedItem`:** ein Ergebnis im Report: Art, ID, Modell, `is_cache_hit`, Dauer, Text, `is_truncated`, `unsupported_numbers`.
- **`EnrichmentReport`:** Liste der Items, `is_dry_run`; berechnet `cache_hits`, `cache_misses`, `truncated`, `flagged_summaries`.
- **`EnrichmentSettings`:** `caption_max_tokens` (600), `summary_max_tokens` (256), `keep_alive` (10 min).

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| `diskcache` 5.6.3 | Persistenter Schlüssel-Wert-Speicher für Modellantworten | `diskcache.Cache(pfad)`, `.get`, `.set`, `.close` | `shelve` (Standardbibliothek), SQLite direkt, `joblib.Memory` |
| `ollama` 0.6.3 (Python-Client) | Chat mit Bildern, Entladen, Modellliste | `Client.chat(model, messages, options, keep_alive)`, `Image(value=bytes)`, `Client.generate(keep_alive=0)`, `.list()`, `.ps()` | direkt `httpx` gegen die REST-API, `openai`-Client gegen die kompatible Schnittstelle |
| `hashlib` (Standardbibliothek) | SHA-256 für Schlüssel und Bildinhalt | `hashlib.sha256(...).hexdigest()` | `blake2b` (schneller; hier nicht nötig) |
| `json` (Standardbibliothek) | Stabile Textform der Schlüsselbestandteile | `json.dumps(sort_keys=True, ensure_ascii=False)` | `pickle` (nicht stabil über Versionen) |
| `re` (Standardbibliothek) | Zahlen und Datumsangaben im Text finden | `re.compile`, `findall`, `split` | `dateparser`, `babel` für Zahlenformate |
| `pydantic` 2.14.3 | Validierung der Chunks nach dem Umbau, Report als JSON | `BaseModel`, `model_copy(update=…)`, `model_dump_json`, `model_validate_json` | `dataclasses` + `json` (ohne Validierung) |
| `typing.Protocol` | Austauschbarer Ollama-Client, Fake in den Tests | `ChatClient` | abstrakte Basisklasse (`abc`) |
