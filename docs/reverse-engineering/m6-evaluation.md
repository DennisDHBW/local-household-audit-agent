# Reverse Engineering – M6 (Runde 1): Testmodul & Metriken

> Runde 1 von 3 zu M6. Runde 2: `m6-quantity-retrieval.md` (Größen-Anfrage, Sparten-Filter). Runde 3: `m6-agent.md` (Zitier-Rückfrage, Prüfablauf, RAGAS).
> **Regel:** Abschnitte 1–4 bereitet Claude vor. Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-17 · **Commit / Tag:** `f3e14f4` (vor v1.0.0) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `evaluation/models.py` | Datensätze des Testmoduls: eine gespeicherte Antwort, ihre Bewertung und die Summe je Variante. | `VariantAnswer`, `ShownSource`, `ToolUse`, `AnswerScore` (mit `is_correct`), `VariantSummary`, `EvaluationError` | `agent.models.ModelCallStep`, `corpus.QuestionCategory`, `ingestion.ChunkType` |
| `evaluation/testset.py` | Wählt Fragen aus `dataset/ground_truth.yaml` aus; ein eigenes Testset gibt es nicht (DRY). | `select_questions` | `corpus` |
| `evaluation/store.py` | Speichert Antworten als JSON-Zeilen, damit ein abgebrochener Lauf weiterlaufen kann. | `answers_path`, `append_answer`, `load_answers`, `load_run`, `check_same_model` | `models` |
| `evaluation/prompts.py` | System-Prompt für B0 und P1 mit denselben Regeln wie der Agent-Prompt. | `EVIDENCE_PROMPT`, `evidence_prompt` | `agent.prompts.GAP_ANSWER` |
| `evaluation/variants.py` | Die drei Vergleichsvarianten B0 (Volltext), P1 (Pipeline) und P2 (Agent) hinter einer gemeinsamen Schnittstelle. | `Variant` (Protocol), `FullTextVariant`, `build_full_text_context`, `PipelineVariant`, `AgentVariant`, `answer_from_run`, `unloads_after_each_question` | `agent.loop` (`chat_arguments`, `estimate_tokens`, `model_call_step`), `retrieval` (`quantity_query`, `new_quantity_hits`, `with_query_utility`), `ingestion` |
| `evaluation/metrics.py` | Deterministische Bewertung einer Antwort gegen die Ground Truth, ohne LLM als Richter. | `score_answer`, `summarize`, `is_fact_in_answer`, `answer_verdict`, `expected_verdict`, `cited_numbers`, `filter_excludes` | `numbers.extract_numbers`, `retrieval.search.fold`, `agent.tools.FilterArguments`, `agent.prompts.is_gap_answer` |
| `evaluation/report.py` | Schreibt `report.md`: Tabelle Variante × Metrik, Matrix Frage × Variante, alle Antworten im Wortlaut. | `render_report`, `ratio`, `_metric_rows` | `metrics`, `ragas_eval` |
| `evaluation/__main__.py` | Kommandozeile `generate`, `score`, `ragas`; steuert Modell-Entladen und Fortsetzen. | `_generate`, `_score`, `_ragas`, `_unload`, `_build_variant`, `main` | alles oben, `ollama.Client`, `preflight` |
| `scripts/check_evidence.py` | Trennt „Beleg kam nie beim Modell an“ von „Beleg war da, Antwort trotzdem falsch“. | schreibt `evidence.json` | `metrics.is_fact_in_answer` |
| `scripts/analyze_timing.py` | Teilt die P2-Zeit in Prefill und Decode auf (ISS-057). | liest `p2-*.jsonl` | – |

## 2. Datenfluss

Beispiel: Frage **G1** („Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?“), Variante **P1**, Lauf **RUN-020** (`qwen2.5:7b`).

```
uv run python -m audit_agent.evaluation generate --run-id run-020 --variants p1 --all
  → main() → Settings.from_env(), ollama.Client
  → _generate()
      ensure_models_available()             Antwort- und Embedding-Modell installiert?
      select_questions(truth, None)         alle 14 Fragen in Katalog-Reihenfolge
      load_answers(answers-p1.jsonl)        schon beantwortete IDs → werden übersprungen
      check_same_model(done, model)         Lauf darf keine Modelle mischen
      _unload(client, used_models)          RAM freigeben (keep_alive=0, ISS-043)
      _build_variant("p1") → PipelineVariant(settings, client, Retriever)
      _write_manifest()                     Konfiguration steht schon vor der ersten Antwort fest
  → PipelineVariant.answer(G1, model)
      backend.search(question, SearchOptions(chunk_types={text, table_row, image}))
                                            → 5 Treffer (Top 5, ohne Filter)
      quantity_query(question)              erkennt „Arbeitspreis“ als Größe
      with_query_utility(options, question) „Stromabrechnung“ → utility_type = electricity
      new_quantity_hits(..., limit=2)       → 2 zusätzliche Tabellenzeilen, ans Ende gehängt
      render_numbered_hit(n, hit, 600)      → Blöcke [1] … [7]
      evidence_prompt(context)              System-Prompt + Auszüge
      _ask_once() → client.chat()           EIN Modellaufruf
      _single_call_answer()                 → VariantAnswer(stop_reason="answer", seconds=103.1, 7 sources)
  → append_answer()                         eine JSON-Zeile in answers-p1.jsonl
  → _unload()                               P1/P2 entladen nach jeder Frage, B0 nicht
  → _score(settings, "run-020")
      score_answer(G1, answer, catalog)
        cited_numbers("… [7] … [6].")       → {6, 7}; beide gehören zu gezeigten Quellen
        cited_pairs                         {(06_…Jahresabrechnung…, 1), (03_…Preisanpassung…, 1)}
                                            → cited_expected 2, expected_cited 2
        is_fact_in_answer(38.20 ct/kWh)     nicht gefunden
        is_fact_in_answer(39.50 ct/kWh)     gefunden („39,50“)
        is_fact_in_answer(40.30 EUR)        nicht gefunden
        expected_verdict(G1)                „Nein. …“ → "nein"
        answer_verdict(answer)              beginnt mit „Ja,“ → "ja"
        → AnswerScore.is_correct == False
      summarize(scores)                     → VariantSummary je Variante
      → scores.json, report.md
```

Auffällig an diesem Beispiel: Beide Zitate zeigen auf erwartete Seiten (Präzision 2/2), die Antwort ist trotzdem falsch. Die Zitat-Metrik vergleicht nur Datei und Seite, nicht ob die zitierte Zahl stimmt. [6] enthält in einer Zeile „Bisher Brutto: 34,80 ct“ und „Neu Brutto: 38,20 ct“. Das Modell nimmt die Spalte „Bisher“ und vergleicht 39,50 mit 34,80 statt mit 38,20 (Engpass Lesen und Vergleichen, siehe status.md).

## 3. Datenstrukturen

- **`ShownSource`** (frozen): `number` (die Belegnummer `[n]`), `filename`, `page_number`, `chunk_type` (bei B0 `None`, weil ein Block eine ganze Seite ist).
- **`ToolUse`**: `name`, `arguments`, `is_valid`; nur das, was die Metriken über einen Tool-Aufruf brauchen.
- **`VariantAnswer`**: `variant` (`b0`/`p1`/`p2`), `question_id`, `model`, `answer`, `stop_reason`, `seconds`, `sources`, `tool_uses` (nur P2), `model_calls` (Token-Zahlen und Zeiten je Aufruf), `contexts` (Belegtext genau so, wie das Modell ihn sah; Eingabe für RAGAS). Property `prompt_tokens` summiert die ausgewerteten Prompt-Tokens (Cache-Treffer zählen nicht, ISS-005).
- **`AnswerScore`**: Zähler einer Antwort: `facts_total`, `missing_facts`; Zitate (`cited_count`, `invalid_citations`, `cited_expected`, `expected_count`, `expected_cited`, `cited_distractors`); Kontext (`shown_count`, `shown_distractors`); Werkzeuge (`expected_tools`, `called_tools`, `filtered_searches`, `filter_misses`); Urteil (`admits_gap`, `expected_verdict`, `answer_verdict`); Aufwand (`seconds`, `prompt_tokens`). Abgeleitet: `facts_found`, `are_tools_ok`, `is_verdict_ok`, `is_correct`.
- **`is_correct`**: Negativfrage → richtig, wenn die Lücke zugegeben wird. Sonst → alle Fakten gefunden **und** Urteil nicht falsch (`is_verdict_ok is not False`, also auch richtig, wenn kein Urteil erwartet wird).
- **`VariantSummary`**: Summen über alle Fragen einer Variante, dazu Mittelwert und Median der Sekunden und der mittlere Prompt-Token-Wert. `tools_ok_count` ist nur bei P2 gesetzt.
- **`FullTextContext`** (B0): `text`, `blocks`, `sources`, `budget_tokens`, `estimated_tokens`, `complete_files`, `partial_file`, `missing_files`. Er zeigt, welche Dateien ins Kontextfenster passten.
- **Dateien eines Laufs** unter `data/eval/<run-id>/`: `answers-<variante>.jsonl`, `manifest.json` (Modell, `num_ctx`, B0-Kontext, RAGAS-Einstellungen), `p2-<frage>.jsonl` (Schritt-Log des Agenten), `scores.json`, `report.md`, optional `ragas-*.jsonl` und `evidence.json`.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| pydantic 2.14.3 | Unveränderliche Datensätze, Serialisierung als JSON-Zeile, Validierung beim Einlesen | `BaseModel`, `ConfigDict(frozen=True)`, `model_dump_json`, `model_validate_json`, `model_dump(mode="json")` | `dataclasses` + `json` (ohne Validierung) |
| ollama 0.6.3 (Python-Client) | Modellaufruf von B0 und P1, Entladen von Modellen | `Client.chat(**chat_arguments(...))`, `Client.generate(model, prompt="", keep_alive=0)` | direkte HTTP-Aufrufe mit `httpx` an `/api/chat` |
| httpx 0.28.1 | Wird vom Ollama-Client benutzt; hier nur, um einen Verbindungsabbruch mitten in einer Anfrage abzufangen | `httpx.TransportError` | `requests` (dann andere Ausnahmen) |
| argparse (Standardbibliothek) | Unterbefehle `generate`, `score`, `ragas` | `add_subparsers`, `choices`, `nargs="+"` | `typer`, `click` |
| re, decimal, statistics (Standardbibliothek) | Zitate und Urteil per Regex finden, Zahlen ohne Rundungsfehler vergleichen, Mittel und Median | `re.compile`, `Decimal`, `statistics.fmean`, `statistics.median` | `float` mit `math.isclose` (Rundungsfehler bei Geldbeträgen möglich) |
| PyYAML 6.0.3 | Liest `ground_truth.yaml` und `documents.yaml` (über `corpus`) | `yaml.safe_load` | JSON-Dateien |

## 5. Whitebox-Tests (selbst nachvollzogen)
- Welche Tests gibt es? Was prüfen sie genau?
- Welchen Test habe ich selbst geschrieben oder verändert?
- Was ist **nicht** getestet?

## 6. Erklär-Test (ohne in den Code zu schauen)

| Frage | Meine Antwort | Stimmt? |
|---|---|---|
| | | |

## 7. Was ich geändert hätte / Schwächen / offene Fragen
-
