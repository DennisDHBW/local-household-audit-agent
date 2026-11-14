# Reverse Engineering – M0: Setup

> Abschnitte 1–4 von Claude vorbereitet. Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-14 · **Commit / Tag:** Branch `feat/m0-setup` (kein Tag) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `pyproject.toml` | Projekt, Abhängigkeiten, ruff- und pytest-Einstellungen | – | `uv`, `hatchling` |
| `scripts/check.sh` | Quality Gate vor jedem Commit | – | `ruff`, `pytest` |
| `src/audit_agent/config.py` | Einzige Quelle für Pfade, Modellnamen, Limits; liest `AUDIT_*`-Variablen | `Settings`, `Settings.from_env`, `ModelNames` | `pydantic` |
| `src/audit_agent/preflight.py` | Bricht früh ab, wenn Ollama-Modelle fehlen, und nennt den `ollama pull`-Befehl | `normalize_model_tag`, `find_missing_models`, `ensure_models_available` | – |
| `src/audit_agent/smoke/tasks.py` | Feste Testeingaben: Tool-Schemas, 5 Tool-Aufgaben, Prompts, Diagramm-Quelle | `TOOLS`, `TOOL_TASKS`, `build_speed_prompt` | – |
| `src/audit_agent/smoke/metrics.py` | Reine Rechen- und Bewertungsfunktionen plus Ergebnismodelle (kein Netzwerk) | `tokens_per_second`, `speed_from_response`, `is_prefix_reused`, `cosine_similarity`, `parse_number`, `tool_call_is_correct`, `SmokeReport` | `pydantic` |
| `src/audit_agent/smoke/runner.py` | Führt die Messschritte gegen Ollama aus, immer ein Modell nach dem anderen | `run_all`, `measure_speed`, `measure_prefix_reuse`, `run_tool_calling`, `run_embedding`, `run_vision`, `unload_model` | `ollama`, `pymupdf`, `config`, `preflight`, `metrics`, `tasks` |
| `src/audit_agent/smoke/report.py` | Macht aus dem `SmokeReport` eine lesbare Markdown-Datei | `render_markdown` | `metrics` |
| `src/audit_agent/smoke/__main__.py` | Kommandozeilen-Einstieg `python -m audit_agent.smoke` | `main` | alle `smoke`-Module |
| `tests/` | 40 Tests ohne LLM (gefakter Client) | `FakeOllama` in `conftest.py` | `pytest`, `ollama`-Typen |

## 2. Datenfluss

Beispiel: Tool-Aufgabe T2 „Wie hoch ist der Arbeitspreis laut Stromvertrag?“ für `llama3.1:8b`.

```
Befehl: uv run python -m audit_agent.smoke
  → main(): Settings.from_env() liest Standardwerte (+ AUDIT_*), Client(host, timeout) wird erzeugt
  → run_all(): installed_models() fragt client.list(); ensure_models_available() prüft alle 5 Modelle
  → unload_all_running(): entlädt alles, was Ollama gerade im RAM hält
  → run_tool_calling(client, "llama3.1:8b", settings), Aufgabe T2:
       messages = [system: TOOL_SYSTEM_PROMPT, user: "Wie hoch ist der Arbeitspreis …?"], tools = TOOLS
       client.chat(...) → ChatResponse mit message.tool_calls[0].function
            name = "search_documents", arguments = {"utility_type": "electricity", "doc_type": "contract", "query": "Arbeitspreis"}
       tool_call_is_correct("search_documents", "search_tables", arguments, {"query": "*", "utility_type": "electricity"})
            → (False, False)   # falsches Werkzeug, daher sind die Argumente nicht „gültig“
       → ToolCallResult(task_id="T2-table", is_tool_correct=False, …, seconds=7)
  → ToolCallingSummary(model, results) → tool_accuracy = 4/5 = 0.8
  → unload_model(): client.generate(prompt="", keep_alive=0) gibt den RAM frei
  → SmokeReport → smoke.json (model_dump_json) und smoke.md (render_markdown)
```

Das gleiche Muster gilt für Geschwindigkeit (Ollama liefert `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, `eval_duration` in Nanosekunden → `tokens_per_second`), Embedding (zwei Dokumente und eine Anfrage → `cosine_similarity`) und Vision (Bild aus dem PDF → Caption → `extract_numbers` → Sollwert-Vergleich).

## 3. Datenstrukturen

- **`Settings`** (frozen): `ollama_host`, `ollama_timeout_s`, `num_ctx`, `memory_limit_gb`, `max_loaded_models`, `models: ModelNames`, `project_root` plus abgeleitete Ordner (`dataset_dir`, `data_dir`, `eval_dir`, …). Ändern ist verboten (frozen), neue Werte kommen nur über Umgebungsvariablen.
- **`ModelNames`**: Modell-Tags je Aufgabe (`embedding`, `vision`, `summary`, `agent`) und `agent_candidates` für den Vergleich.
- **`ToolTask`** (frozen dataclass): `task_id`, `prompt`, `expected_tool`, `expected_arguments` (Teilstring-Erwartung; `"*"` heißt „vorhanden und nicht leer“).
- **`SpeedResult`**: Tokens und Tokens/s für Prefill und Generierung, Ladezeit, belegter RAM.
- **`PrefixReuseResult`**: Tokenzahlen und Prefill-Sekunden zweier Aufrufe mit gleichem Anfang, daraus `is_prefix_reused`.
- **`ToolCallResult` / `ToolCallingSummary`**: Ergebnis je Aufgabe und Trefferquoten (`tool_accuracy`, `argument_accuracy` als Properties).
- **`EmbeddingResult`, `VisionResult`**: Dimensionen und Ähnlichkeiten bzw. Caption, erwartete und gefundene Zahlen.
- **`SmokeReport`**: Sammelobjekt eines Laufs inkl. `errors`; wird als JSON gespeichert.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| `ollama` 0.6.3 | Python-Client für die lokale Ollama-HTTP-API | `Client.chat(tools=…, options=…, keep_alive=…)`, `Client.embed`, `Client.generate(keep_alive=0)`, `Client.list`, `Client.ps`, `Image` | direkte HTTP-Aufrufe mit `httpx` an `/api/chat` |
| `pydantic` 2.14.3 | Typisierte, validierte Datenmodelle (Settings, Ergebnisse) | `BaseModel`, `ConfigDict(frozen=True)`, `Field(gt=…)`, `model_dump_json` | `dataclasses` (ohne Validierung) |
| `pymupdf` 2.1 | Eingebettetes Diagramm aus dem PDF holen | `pymupdf.open`, `page.get_images`, `document.extract_image` | `pypdf`, `pdfplumber` |
| `uv` 0.13.4 | Python 3.13, virtuelle Umgebung, Lockfile | `uv sync`, `uv run` | `pip` + `venv`, `poetry` |
| `hatchling` | Build-Backend für das `src/`-Layout | `[tool.hatch.build.targets.wheel]` | `setuptools` |
| `ruff` 0.17.5 | Linter und Formatter | `ruff check`, `ruff format --check` | `flake8` + `black` |
| `pytest` 9.2.0 | Tests, Marker `slow` für Ollama-abhängige Tests | `-m "not slow"`, `tmp_path`, `parametrize` | `unittest` |
