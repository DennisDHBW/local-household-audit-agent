# Reverse Engineering – M6 (Runde 3): Agent-Schleife, Rückfragen, Prüfablauf, RAGAS

> Runde 3 von 3 zu M6. Runde 1: `m6-evaluation.md`, Runde 2: `m6-quantity-retrieval.md`.
> **Regel:** Abschnitte 1–4 bereitet Claude vor. Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-17 · **Commit / Tag:** `f3e14f4` (vor v1.0.0) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `agent/loop.py` | ReAct-Schleife mit nativen Tool Calls; neu in M6: drei einmalige Rückfragen vor dem Akzeptieren einer Antwort, Wiederholungssperre, Text-Aufrufe, optionaler Prüfablauf. | `AgentLoop.run`, `_execute`, `_CallMemory`, `_is_context_full`, `_call_model`, `chat_arguments`, `model_call_step`, `estimate_tokens` | `ollama.Message`, `prompts`, `tools`, `text_calls`, `audit_flow` |
| `agent/prompts.py` | Alle Texte, die das Modell vom Agenten bekommt, plus Erkennungsfunktionen für Lücken-Antwort, Zitat und Prüffrage. | `SYSTEM_PROMPT`, `RETRY_BEFORE_GAP_MESSAGE`, `CALCULATE_BEFORE_ANSWER_MESSAGE`, `CITE_BEFORE_ANSWER_MESSAGE`, `REPEAT_*`, `is_gap_answer`, `has_citation`, `is_audit_question` | `retrieval.search.fold` |
| `agent/text_calls.py` | Liest einen Werkzeugaufruf, den das Modell als JSON in den Antworttext geschrieben hat (ISS-061). | `parse_text_call`, `_call_at`, `TextCall` | `json.JSONDecoder.raw_decode` |
| `agent/audit_flow.py` | Fester Prüfablauf Planen → Suchen → Lesen → Rechnen (ADR-0016); **standardmäßig aus** (`audit_flow_enabled=False`) und als Negativergebnis behalten. | `run_audit_flow`, `_plan`, `_check`, `_verified`, `_difference`, `render_findings`, `AuditPlan`, `Reading` | `tools.tool_parameters`, `numbers.extract_numbers` |
| `agent/models.py` | Schritt-Datensätze des Laufs; neu: `NudgeStep` (mit `reason`), `AuditFlowStep`, `AuditCheckResult`, Felder `is_repeat`, `is_text_call`, `is_flow_call` an `ToolCallStep`. | siehe Abschnitt 3 | `retrieval.SearchHit` |
| `evaluation/ragas_eval.py` | RAGAS als zweite Sicht: Faithfulness und Context Recall mit lokalem Richtermodell (ADR-0012). | `RagasJudge`, `score_answer_ragas`, `evaluate_run`, `_precheck`, `estimate_judge_tokens`, `summarize_ragas`, `load_ragas_scores` | `ragas` (optional), `openai.AsyncOpenAI`, `evaluation.models` |

## 2. Datenfluss

Beispiel: Frage **S1** („Welche Kündigungsfrist gilt für den Gasvertrag und bis wann läuft die Erstlaufzeit?“), Variante **P2**, Lauf **RUN-021**, Log `data/eval/run-021/p2-S1.jsonl`.

```
AgentLoop.run(question)
  messages = [system_prompt(6), user: Frage]
  is_audit_question(Frage)              keine Prüf-Phrase („stimmt“, „korrekt“, …) → False
  audit_flow_enabled == False           → kein Prüfablauf
  ── Durchlauf 1
  _call_model(offer_tools=True)         → ModelCallStep: content "", 2 tool_calls
  _execute(search{"query": "Kündigungsfrist Gasvertrag", "utility_type": "gas"})
      clean_arguments → SearchArguments.model_validate → key nicht in memory.valid
      tool.run → ToolResult (Treffer [1] …)          → ToolCallStep(is_valid=True)
  _execute(search{"query": "Erstlaufzeit Gasvertrag", "utility_type": "gas"})
      → weitere Treffer, fortlaufend nummeriert im EvidenceBook (u. a. [3])
  tool_call_count = 2 < 6, _is_context_full() False → weiter
  ── Durchlauf 2
  _call_model(offer_tools=True)         → Antworttext ohne tool_calls
  parse_text_call(content)              kein JSON am Ende → None → ist eine Antwort
  Rückfrage-Prüfungen in fester Reihenfolge, jede höchstens einmal:
      gap:       is_gap_answer? nein                                  → übersprungen
      calculate: is_audit? nein                                       → übersprungen
      cite:      require_citation, Zahlen („6 Wochen“, „24 Monate“) im Text,
                 has_citation? nein                                    → NudgeStep(reason="cite")
                 messages += [Antwort, user: CITE_BEFORE_ANSWER_MESSAGE]
  ── Durchlauf 3
  _call_model(offer_tools=True)         → gleiche Antwort, jetzt mit [1] und [3]
  alle Rückfragen schon gestellt         → stop_reason "answer", break
  AgentRun(answer, steps, sources=book.numbered_hits)
→ answer_from_run() (Runde 1) → VariantAnswer → score_answer()
→ optional: ragas → score_answer_ragas("faithfulness", S1, answer, judge, settings)
      _precheck: Antwort nicht leer, contexts vorhanden → Richter wird gefragt
      prompt_chars → estimate_judge_tokens ≤ judge_num_ctx (8192)? sonst "too_long"
      RagasJudge.score → Faithfulness.ascore(user_input, response, retrieved_contexts)
      → RagasScore(status "ok", value) → eine Zeile in ragas.jsonl
```

**Prüffrage (G1), falls der Prüfablauf eingeschaltet wäre:** `_plan` lässt das Modell mit JSON-Schema (`format=PLAN_SCHEMA`) Prüfgrößen samt Suchanfragen für Soll und Ist nennen. Der Code führt die Suchen aus. `_check` lässt das Modell je Seite eine Zahl mit Belegnummer lesen (`READING_SCHEMA`). `_verified` prüft, ob diese Zahl wirklich in einer Zeile des genannten Treffers steht. `_difference` rechnet Ist minus Soll mit `calculate`. `render_findings` schreibt das Ergebnis als Nachricht an das Modell. In RUN-017 brachte das keine Verbesserung (ISS-070/071), daher aus.

## 3. Datenstrukturen

- **`ModelCallStep`**: `index`, `offered_tools`, `message_count`, `prompt_tokens`, `prefill_seconds`, `generated_tokens`, `decode_seconds` (Werte aus der Ollama-Antwort, Nanosekunden umgerechnet), `seconds`, `content`, `tool_calls`.
- **`ToolCallStep`**: `tool`, `arguments` (roh, wie vom Modell), `is_valid`, `observation`, `hit_numbers`, `is_repeat` (Wiederholung gesperrt), `is_text_call` (aus dem Text gelesen), `is_flow_call` (vom Prüfablauf ausgelöst).
- **`NudgeStep`**: `message`, `reason` ∈ {`gap`, `calculate`, `cite`}.
- **`AuditCheckResult`** / **`AuditFlowStep`**: je Prüfgröße `status` (`not_found`, `not_verified`, `equal`, `deviation`), Soll/Ist mit Treffernummer und Zeile, `difference` als Text aus `calculate`.
- **`AgentRun`**: `answer`, `stop_reason` ∈ {`answer`, `tool_limit`, `context_limit`, `empty_answer`}, `tool_call_count`, `seconds`, `steps`, `sources` (`NumberedHit` mit Nummer und `SearchHit`).
- **`_CallMemory`**: zwei Mengen. `valid` hält (Werkzeug, validierte Argumente als JSON), `failed` hält (Werkzeug, bereinigte Rohargumente). Beide sperren eine Wiederholung innerhalb einer Frage.
- **`TextCall`**: `name`, `arguments`. Er entsteht nur, wenn ein JSON-Objekt die Nachricht beendet, ein bekanntes Werkzeug nennt und `parameters` oder `arguments` als Objekt hat.
- **`RagasScore`**: `variant`, `question_id`, `metric`, `judge`, `status` (`ok`, `too_long`, `no_context`, `not_applicable`, `no_statements`, `error`), `value`, `estimated_tokens`, `seconds`, `detail`. Bei doppeltem Schlüssel gewinnt beim Laden die letzte Zeile (wiederholte Fehler).
- **Schalter in `AgentSettings`**: `max_tool_calls` (6), `min_searches_before_gap` (2), `require_citation` (True), `audit_flow_enabled` (False), `audit_max_checks` (3), `context_reserve_tokens` (1200), `temperature` (0.0).

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| ollama 0.6.3 | Chat mit Tool Calling, strukturierte Ausgabe im Prüfablauf, Token- und Zeitwerte | `Client.chat(model, messages, tools=…, format=<JSON-Schema>, options={num_ctx, num_predict, temperature}, keep_alive)`, `Message.ToolCall`, `Message.ToolCall.Function` | LangChain `ChatOllama` mit `bind_tools` (mehr Abstraktion, weniger Kontrolle über den Prompt) |
| pydantic 2.14.3 | Schritt-Datensätze, Argumentprüfung, JSON-Schema für `format=` | `model_validate`, `model_validate_json`, `ValidationError.errors()`, `model_dump_json` | `jsonschema` + dicts |
| json (Standardbibliothek) | JSON-Objekt mitten im Text finden, ohne den Rest zu parsen | `JSONDecoder.raw_decode(text, start)` gibt Wert und Endposition zurück | Regex auf `{…}` (scheitert an verschachtelten Klammern) |
| ragas 0.4.4 (optionale Gruppe) | Faithfulness und Context Recall als zweite Sicht | `llm_factory(model, provider="openai", client=…)`, `Faithfulness(llm=…).ascore(...)`, `ContextRecall(llm=…).ascore(...)`, Prompt-Klassen für die Längenschätzung | eigenes LLM-as-a-Judge-Prompt; DeepEval |
| openai 3.3.0 | Client für den OpenAI-kompatiblen Endpunkt `/v1` von Ollama, den RAGAS erwartet | `AsyncOpenAI(base_url=…/v1, api_key="ollama", max_retries=0)`, `APIConnectionError`, `APITimeoutError` | LiteLLM als Adapter |
| asyncio (Standardbibliothek) | RAGAS-Metriken sind `async` | `asyncio.run(evaluate_run(...))` | – |

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
