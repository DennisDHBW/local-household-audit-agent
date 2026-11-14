# Reverse Engineering – M5: Agent (P2) mit Tools

> Pro Meilenstein eine Kopie der Vorlage. Abschnitte 1–4 hat Claude vorbereitet, Abschnitte 5–7 schreibe ich selbst.
> Ziel (Professor): Konzept (logisch) und Prototyp (technisch) „in all seinen Körperteilen“ verstehen: Code-Dateien, Funktionen, Datenstrukturen, Datenflüsse, Bibliotheken.
> **Runde 1 (Kern):** `calculator`, `tools`, `loop`, `models`, `prompts`, `log`. **Runde 2 (Rand):** `report`, `factory`, `__main__`, `evidence_view`, `app`. Die Randdateien stehen unten nur mit einem Satz.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m5-agent`, Tag `v0.2.0` nach dem Merge · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `config.py` (Erweiterung) | Parameter der Schleife: Werkzeuglimit 6, Trefferlänge 600, Antwortlänge 600 Token, Kontextreserve, Summaries aus, Lückenrückfrage | `AgentSettings`, `Settings.agent` | pydantic |
| `agent/calculator.py` | Rechnet Ausdrücke sicher über den Syntaxbaum, ohne `eval` | `calculate`, `normalize_expression`, `format_result`, `CalculationError` | `ast`, `decimal` |
| `agent/models.py` | Typisierte Protokollsätze eines Laufs und das Nummernbuch der Treffer | `ModelCallStep`, `ToolCallStep`, `NudgeStep`, `AgentRun`, `EvidenceBook`, `NumberedHit` | `retrieval` (`SearchHit`) |
| `agent/tools.py` | Die sechs Tools mit Argumentmodell, Beschreibung und Funktion; erzeugt das JSON-Schema für Ollama | `ToolBox`, `AgentTool`, `tool_parameters`, `clean_arguments`, `ToolBox._search`, `_effective_filter` | `retrieval`, `corpus`, `ingestion`, `calculator`, `models` |
| `agent/prompts.py` | System-Prompt, Rückfrage und Abschlussaufforderung, Erkennung einer „keine Angaben“-Antwort | `system_prompt`, `is_gap_answer`, `RETRY_BEFORE_GAP_MESSAGE` | `retrieval.search.fold` |
| `agent/loop.py` | Die Agentenschleife: Modell fragen, Tools ausführen, Beobachtungen zurückgeben, Limits prüfen | `AgentLoop.run`, `_call_model`, `_execute`, `_is_context_full`, `estimate_tokens` | `tools`, `models`, `prompts`, `ollama` (über Protocol) |
| `agent/log.py` | Schreibt jeden Schritt sofort als JSON-Zeile | `RunLog` | `models` |
| *Runde 2:* `agent/report.py` | Grobe Prüfung eines Laufs gegen die Ground Truth und Markdown-Report | `evaluate_run`, `is_fact_in_answer`, `render_markdown` | `corpus`, `numbers` |
| *Runde 2:* `agent/factory.py` | Verdrahtet Einstellungen, Ollama-Client, Retriever, Tools und Schleife | `create_agent` | `retrieval`, `corpus` |
| *Runde 2:* `agent/__main__.py` | CLI `ask` und `run-set` mit Live-Ausgabe, Log und Report | `main`, `_answer`, `_questions` | alle oben |
| *Runde 2:* `agent/evidence_view.py`, `agent/app.py` | Belege nach Dokument und Kapitel mit Belegnummer; Streamlit-Seite, die sie schon während des Laufs zeigt | `evidence_sections`, `main` | `streamlit`, `retrieval.evidence` |
| `tests/test_agent_tools.py`, `tests/test_agent_loop.py`, `tests/agent_fakes.py` | 79 schnelle Tests ohne Ollama (Skript-Client, Fake-Suche) | `ScriptedChat`, `FakeBackend`, `tool_reply`, `answer_reply` | pytest, ollama (Datentypen) |

## 2. Datenfluss
**A) Eine Frage durch die Schleife.** Beispiel: S2 „Welcher Arbeits- und Grundpreis gelten laut Stromvertrag?“ aus RUN-006 (`data/eval/run-006/agent-S2.jsonl`).

```
AgentLoop.run(question)
  → messages = [system (system_prompt(6)), user (Frage)]                      EvidenceBook leer
  → _call_model()      chat(model, messages, tools=6 Schemas, options, keep_alive)
                       Antwort: tool_calls = [search_tables {doc_type: contract, utility_type: electricity,
                                                              query: "Arbeitspreis und Grundpreis Stromvertrag"}]
                       Schritt 1: 2.044 Prompt-Token, Prefill 118 s (kein Cache), 42 Token erzeugt   → ModelCallStep
  → messages += [Antwort des Modells]
  → _execute(call)     Tool "search_tables" nachschlagen
                       clean_arguments(): leere Werte raus, "filter" abflachen
                       SearchArguments.model_validate(): doc_type "contract" → DocType.CONTRACT, Pflichtfeld query ok
                       ToolBox._search(): _effective_filter() → kein Jahr, also keine Notiz
                                          SearchOptions(MetadataFilter(electricity, contract), chunk_types={table_row})
                       Retriever.search() → build_where() → ChromaDB → 5 SearchHit
                       EvidenceBook.register() → Nummern 1 bis 5
                       Text: "Treffer für … (Filter: Sparte=electricity, Art=contract):\n[1] 01_Strom_Vertragsbestaetigung…pdf, S. 1,
                              Tabellenzeile\nKapitel: …\nPreisbestandteil: Grundpreis … Netto: 9,66 EUR | Brutto …: 11,50 EUR\n[2] …"   → ToolCallStep
  → messages += {"role": "tool", "tool_name": "search_tables", "content": Text}
  → tool_call_count 1 < 6, Kontext nicht voll → nächste Runde
  → _call_model()      Antwort ohne tool_calls: "Der Arbeitspreis beträgt 34,80 ct/kWh (Brutto) und der Grundpreis 11,50 EUR/Monat (Brutto)."
                       Schritt 3: 1.254 Token gemeldet, Prefill 45 s
  → stop_reason "answer" → AgentRun(answer, steps, sources=[Nr. 1 bis 5])
```

**B) Das Limit und die Rückfrage (G1, RUN-006).** Nach einem Aufruf antwortet das Modell „Dazu liegen … keine Angaben vor.“ → `is_gap_answer` ist wahr und `tool_call_count` (1) < `min_searches_before_gap` (2) → die Antwort kommt als Assistentennachricht in den Verlauf, dazu die Aufforderung `RETRY_BEFORE_GAP_MESSAGE` → `NudgeStep` → neuer Modellaufruf. Nur einmal je Frage (`is_gap_questioned`). Bei `tool_call_count == 6` oder vollem Kontext wird `forced` gesetzt: dann folgt ein letzter Aufruf **ohne** `tools` und mit `FORCED_ANSWER_MESSAGE`.

**C) Der Rechner.** `calculate("3100 * (0.395 - 0.382)")` → `normalize_expression` (Komma zwischen Ziffern wird Punkt, `€`/`EUR` fallen weg) → `ast.parse(mode="eval")` → `_evaluate` läuft den Baum ab: `Constant` → `Decimal("3100")`, `BinOp(Sub)` → `Decimal("0.395") - Decimal("0.382")` = `0.013`, `BinOp(Mult)` → `40.300` → `quantize` auf 6 Stellen → `format_result` → `"40.3"`. Alles andere (`Name`, `Call`, `Attribute`, `%`, Exponent über 10) wirft `CalculationError`.

## 3. Datenstrukturen
- **`AgentSettings`** (frozen): `max_tool_calls` (6), `max_hit_chars` (600), `max_list_rows` (40), `num_predict` (600), `context_reserve_tokens` (1.200), `temperature` (0), `keep_alive`, `include_table_summaries` (aus), `min_searches_before_gap` (2).
- **`AgentTool`**: `name`, `description`, `arguments` (pydantic-Klasse), `run` (Funktion `(Argumente, EvidenceBook) → ToolResult`); `spec()` liefert den Ollama-Eintrag, `usage()` die Aufrufform `calculate(expression*)`.
- **Argumentmodelle:** `FilterArguments` (`utility_type`, `doc_type`, `year`), `SearchArguments` (+ `query`), `OutlineArguments` (`filename`), `CalculateArguments` (`expression`). Unbekannte Felder werden ignoriert (`extra="ignore"`).
- **`ToolResult`**: `text` für das Modell, `hit_numbers` für das Log.
- **`EvidenceBook`**: Zuordnung `chunk_id → Nummer`, Liste der Treffer; `register()` vergibt die nächste Nummer oder gibt die alte zurück.
- **`ModelCallStep`**: Index, ob Tools angeboten wurden, Nachrichtenzahl, Prompt-Token, Prefill-, Decode- und Gesamtsekunden, Inhalt, Tool-Aufrufe wie geschrieben. **`ToolCallStep`**: Tool, Argumente (roh), `is_valid`, Beobachtung, Sekunden, Trefferzahlen. **`NudgeStep`**: Rückfrage.
- **`AgentRun`**: Frage, Modell, Antwort, `stop_reason` (`answer`, `tool_limit`, `context_limit`, `empty_answer`), Aufrufzahl, Sekunden, Schritte, nummerierte Quellen; `called_tools` ist abgeleitet.
- **Nachrichten an Ollama:** Wörterbücher `{"role": ..., "content": ...}` (`system`, `user`, `tool` mit `tool_name`) und die `Message`-Objekte der Modellantworten.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| `ollama` 0.6.3 | Chat mit nativem Tool-Calling | `Client.chat(model, messages, tools, options, keep_alive)`; Antwort `ChatResponse` mit `message.tool_calls`, `prompt_eval_count`, `prompt_eval_duration` | Ollama erlaubt auch Python-Funktionen direkt als `tools`; LangChain, smolagents |
| `pydantic` 2.14.3 | Argumente prüfen, JSON-Schema erzeugen, unveränderliche Protokollsätze | `model_validate`, `model_json_schema`, `model_dump_json(exclude=…)`, `ConfigDict(frozen=True, extra="ignore")` | `dataclasses` mit eigener Prüfung; `jsonschema` |
| `ast`, `decimal` (Standardbibliothek) | Sicherer, exakter Rechner | `ast.parse(mode="eval")`, `ast.walk`, `Decimal.quantize` | `simpleeval`, `numexpr`; `fractions.Fraction` |
| `chromadb` 1.5.9 (über `Retriever`) | Vektorsuche mit Filter; die Tools rufen nur `Retriever.search` | – (siehe M4) | – |
| `streamlit` 1.67.0 | Oberfläche mit Live-Belegen | `st.text_area`, `st.button`, `st.empty`, `st.container`, `st.expander`, `st.markdown`; Test: `streamlit.testing.v1.AppTest` | Gradio, NiceGUI, Flask mit HTMX |
| `pytest` 9.2.0 | Tests ohne Ollama | eigene Fakes `ScriptedChat` und `FakeBackend` statt `unittest.mock` | `unittest.mock`, `pytest-mock` |

## 5. Whitebox-Tests (selbst nachvollzogen)
- Welche Tests gibt es? Was prüfen sie genau?
- Welchen Test habe ich selbst geschrieben oder verändert?
- Was ist **nicht** getestet?

## 6. Erklär-Test (ohne in den Code zu schauen)
Beantworte die Verständnisfragen, die Claude gestellt hat, in eigenen Worten. Danach mit dem Code vergleichen und Fehler markieren.

| Frage | Meine Antwort | Stimmt? |
|---|---|---|
| | | |

## 7. Was ich geändert hätte / Schwächen / offene Fragen
-
