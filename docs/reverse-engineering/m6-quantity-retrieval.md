# Reverse Engineering – M6 (Runde 2): Größen-Anfrage, Sparten-Filter, Werkzeuge

> Runde 2 von 3 zu M6. Runde 1: `m6-evaluation.md`, Runde 3: `m6-agent.md`.
> **Regel:** Abschnitte 1–4 bereitet Claude vor. Abschnitte 5–7 schreibe ich selbst.

**Datum:** 2026-11-17 · **Commit / Tag:** `f3e14f4` (vor v1.0.0) · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| `retrieval/quantity.py` | Kürzt eine Frage auf die gefragte Abrechnungsgröße („Arbeitspreis“) und erkennt die genannte Sparte; damit läuft eine zweite Suche (ADR-0017, ISS-077). | `quantity_query`, `utility_in_query`, `with_query_utility`, `new_quantity_hits`, `FILLER`, `UTILITY_WORDS`, `DOCUMENT_WORDS` | `retrieval.search` (`fold`, `STOPWORDS`), `retrieval.models`, `corpus.UtilityType` |
| `retrieval/evidence.py` | Neues gemeinsames Trefferformat für P1 und P2, damit beide gleich zitieren. | `render_numbered_hit`, `shorten` (vorher privat) | `retrieval.models.SearchHit` |
| `numbers.py` | Zahlen aus Text lesen; Tausendergruppen dürfen jetzt nicht mit 0 beginnen. | `parse_number`, `extract_numbers` | – |
| `agent/tools.py` | Die fünf Agent-Werkzeuge nach ADR-0014: eine `search` über Text und Tabellen, Filter nur nach Sparte, optional Gegenstück-Suche, Größen-Suche, nachsichtige Argumente. | `ToolBox.tools`, `_search`, `_counterpart_hits`, `_inventory`, `SearchArguments`, `FilterArguments`, `CalculateArguments._accept_operands`, `clean_arguments`, `tool_parameters`, `matches_year` | `retrieval`, `agent.calculator`, `agent.models.EvidenceBook`, `corpus` |

Nach ADR-0014 bietet `ToolBox.tools` fünf Werkzeuge an: `list_documents`, `search`, `search_images`, `get_document_outline` und `calculate`. `search_documents` und `search_tables` gibt es nur noch in alten Läufen.

## 2. Datenfluss

Beispiel: Frage **G1**, Variante **P2**, Lauf **RUN-021** (`qwen2.5:7b`), erster Tool-Aufruf aus `data/eval/run-021/p2-G1.jsonl`.

```
Modell ruft: search({"query": "neuer Arbeitspreis 2025", "utility_type": "electricity",
                     "year": 2025, "include_counterpart": true})
  → clean_arguments()                       leere Werte raus, "filter": {...} flach machen
  → SearchArguments.model_validate()        extra="ignore": "year" wird still verworfen
  → ToolBox._search(args, book, {text, table_row})
      MetadataFilter(utility_type=electricity)
      backend.search("neuer Arbeitspreis 2025", options)
          → 5 Treffer, alle aus 05_Strom_Zwischenablesung_Info_2025.pdf (doc_type notice)
      with_query_utility(options, query)    Filter schon gesetzt → bleibt electricity
      quantity_query("neuer Arbeitspreis 2025")
          Wörter: neuer (FILLER), Arbeitspreis (bleibt), 2025 (Ziffern) → "Arbeitspreis"
      new_quantity_hits(search, "Arbeitspreis", options, hits, wanted=2)
          search("Arbeitspreis", top_k = 2 + 5)
          bekannte chunk_ids raus, die ersten 2 neuen behalten
          → 03_Strom_Preisanpassung…, Tabellenzeile (34,80 bisher / 38,20 neu)
          → 06_Strom_Jahresabrechnung_2025…, Tabellenzeile (39,50 ct/kWh, 3.100 kWh)
          Hinweis: 'Weitere Treffer stammen aus einer Suche nur nach "Arbeitspreis".'
      _counterpart_hits("Arbeitspreis", electricity, hits, types)
          found = Dokumentarten aller 7 Treffer = {notice, price_adjustment, bill}
          → bill und eine Basis-Art sind schon da, wanted = [] → keine einzige Suche, extra = []
          Hinweis: 'Im Gegenstück (Vertrag bzw. Rechnung) gibt es keine Treffer.'   (irreführend, ISS-081)
      book.register(hit) je Treffer          → Belegnummern 1 … 7
      render_numbered_hit(n, hit, 600)       → "[6] 03_Strom_Preisanpassung_SuedVolt_2025.pdf, S. 1, Tabellenzeile"
                                               "Kapitel: … > Preisgegenüberstellung im Detail (ab 01.01.2025)"
                                               "Preisbestandteil: Arbeitspreis … Neu Brutto …: 38,20 ct"
  → ToolResult(text, hit_numbers=(1, …, 7))  geht als Beobachtung zurück an das Modell
Modell antwortet: „… der neue Arbeitspreis von 38,20 ct/kWh … angewendet … [6] … [7]“ (falsch: [7] zeigt 39,50)
```

Ohne die Größen-Suche hätte der Agent nur die fünf Treffer aus dem Zwischenablesungsschreiben gesehen (RUN-014, ISS-072). Mit ihr hat er beide Zahlen im Kontext und vergleicht trotzdem falsch. Der Engpass liegt danach nicht mehr beim Retrieval, sondern beim Lesen und Vergleichen.

## 3. Datenstrukturen

- **`SearchOptions`** (aus M4): `metadata_filter`, `chunk_types`, `top_k`. Wird mit `model_copy(update=…)` kopiert, nie verändert (frozen).
- **`MetadataFilter`** (aus M4): `utility_type`, `doc_type`, `period_start`/`period_end`; `for_year()` baut den Zeitraum eines Jahres.
- **`SearchArguments`**: `query` (min. 2 Zeichen), `utility_type`, `include_counterpart` (Standard `false`). `extra="ignore"` verwirft erfundene Argumente.
- **`FilterArguments`** (`list_documents`): `utility_type`, `doc_type`, `year` (1990–2100). In der Metrik `filter_excludes` (Runde 1) wird dieselbe Klasse genutzt, damit Werkzeug und Metrik gleich filtern.
- **`CalculateArguments`**: `expression`. Der `model_validator(mode="before")` baut den Ausdruck aus `a`/`b` und `operator` zusammen, wenn das Modell die Operanden getrennt schickt (ISS-063). Fehlt der Operator, gibt es eine Fehlermeldung mit den Zahlen des Modells.
- **`ToolResult`**: `text` (für das Modell), `hit_numbers` (welche Belegnummern darin stehen).
- **`AgentTool`** (dataclass): `name`, `description`, `arguments` (pydantic-Klasse), `run`. `spec()` erzeugt den Eintrag für `tools=[…]` von Ollama, `usage()` die Kurzform `search(query*, utility_type, include_counterpart)`.
- **Wortlisten in `quantity.py`**: `FILLER` = Frage- und Urteilswörter + `DOCUMENT_WORDS` + Spartenwörter. `UTILITY_WORDS` bildet gefaltete Spartenwörter auf `UtilityType` ab. Nebenkosten fehlen dort absichtlich (Frage braucht Mietvertrag und Abrechnung zusammen).
- **Konfiguration**: `agent.quantity_hits` (Standard 2, 0 schaltet die Größen-Suche ab), `agent.max_hit_chars` (600), `agent.include_table_summaries`.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| pydantic 2.14.3 | Argumente des Modells prüfen, JSON-Schema für Ollama erzeugen, unveränderliche Optionen kopieren | `Field(description=…, min_length, ge, le)`, `ConfigDict(extra="ignore")`, `model_validator(mode="before")`, `model_json_schema()`, `model_copy(update=…)` | JSON-Schema von Hand + `jsonschema` zur Prüfung |
| re (Standardbibliothek) | Wörter mit Umlauten und Bindestrich finden, Zahlen-Token, Tausendergruppen | `[^\W_]+(?:-[^\W_]+)*` (Unicode-Buchstaben ohne Unterstrich), `fullmatch`, `findall` | Tokenizer aus spaCy (schwer, für CPU-Projekt überdimensioniert) |
| enum.StrEnum (Standardbibliothek) | `UtilityType`, `DocType` als Text vergleichbar und in f-Strings als Wert lesbar („electricity“) | `StrEnum` | `Literal[...]` von typing |
| ChromaDB 1.5.9 (über `Retriever` aus M4) | Metadatenfilter der Größen- und Gegenstück-Suche | `where`-Filter, gebaut von `build_where` | Filter erst nach der Suche in Python (verliert Treffer bei kleinem `top_k`) |
| Ollama Tool Calling (ADR-0006) | Das Modell sieht `spec()` als `tools=[…]` und antwortet mit `tool_calls` | Schema `{"type": "function", "function": {name, description, parameters}}` | Werkzeugaufruf als Text im Antworttext parsen (siehe Runde 3, `text_calls.py`) |

## 5. Whitebox-Tests (selbst nachvollzogen)
- Welche Tests gibt es? Was prüfen sie genau?
- Welchen Test habe ich selbst geschrieben oder verändert?
- Was ist **nicht** getestet?

## 6. Erklär-Test (ohne in den Code zu schauen)

> Fragen am 2026-11-17 im Repo gesichert (ISS-084). Sie sind neu formuliert und nicht wörtlich die aus dem Chat. Antworten ohne Blick in den Code eintragen; „Stimmt?“ füllt Claude beim Abgleich mit dem Code.

| Frage | Meine Antwort | Stimmt? |
|---|---|---|
| R2-1: Was macht `quantity_query` aus „neuer Arbeitspreis 2025“, und warum gibt es diese zweite Suche überhaupt? | | |
| R2-2: Warum hängt `new_quantity_hits` die neuen Treffer ans Ende und behält nur Treffer mit noch unbekannter `chunk_id`? | | |
| R2-3: Woher kommt die Sparte, wenn das Modell keinen `utility_type` mitgibt? Und warum fehlen Nebenkosten in `UTILITY_WORDS`? | | |
| R2-4: `SearchArguments` hat `extra="ignore"`. Was passiert mit `"year": 2025` im G1-Beispiel, und was folgt daraus für die Suche? | | |
| R2-5: Warum filtert ChromaDB mit `where` schon in der Suche statt Python danach? Was ginge bei kleinem `top_k` verloren? | | |
| R2-6: Bei G1 meldet `_counterpart_hits` „keine Treffer im Gegenstück“. Warum ist der Hinweis irreführend (ISS-081)? | | |
| R2-7: Was macht `CalculateArguments._accept_operands`, und welches Modellverhalten fängt es ab? | | |
| R2-8: Warum nutzt die Metrik `filter_excludes` dieselbe Klasse `FilterArguments` wie das Werkzeug `list_documents`? | | |

## 7. Was ich geändert hätte / Schwächen / offene Fragen
-
