# ADR-0004: Modellauswahl und Speicherbudget unter `MemoryMax=9G`

- **Status:** akzeptiert (Agent-Modell vorläufig `llama3.1:8b`, Endentscheidung im Testmodul M6)
- **Datum:** 2026-11-14
- **Meilenstein:** M0

## Kontext
Ollama läuft als systemd-Dienst mit `MemoryMax=9G`, `OLLAMA_MAX_LOADED_MODELS=2`, `OLLAMA_NUM_PARALLEL=1`. Reine CPU-Inferenz: Prefill ca. 18 Tokens/s, Generierung ca. 5–6 Tokens/s (7–8B) bzw. 10,5 Tokens/s (3B). Modelle ab 14B scheiden aus.

## Entscheidung (Vorschlag)
Zwei getrennte Phasen mit je höchstens zwei geladenen Modellen (CQRS):

| Phase | Modelle | RAM ca. | Passt in 9G? |
|---|---|---|---|
| Ingest (schreibend) | `gemma3:4b` (Captions) + `llama3.2` (Tabellen-Summaries) | 4,0 + 3,1 = 7,1 GB | ja |
| Ingest (Embedding, eigener Schritt) | `nomic-embed-text` | < 0,5 GB | ja |
| Query (lesend) | Agent-Modell `qwen2.5:7b` **oder** `llama3.1:8b` + `nomic-embed-text` | 5,5–6,3 + < 0,5 GB | ja (KV-Cache beachten) |
| **nicht** möglich | Agent 7–8B + `gemma3:4b` oder + 3B-Rewriter | > 9 GB | nein |

Folgerungen:
- **Kein separates Query-Rewriting-Modell** in der Abfragephase. Im Agenten (P2) formuliert das Agent-Modell die Suchanfragen ohnehin selbst in den Tool-Argumenten. In P1 übernimmt das Synthese-Modell das Rewriting.
- **Keine Bildanalyse zur Abfragezeit**, nur gecachte Captions aus dem Ingest.
- `num_ctx` explizit setzen (z. B. 8192) statt Standardwert; KV-Cache wächst mit dem Kontext.
- `qwen3` nur mit abgeschaltetem Thinking-Modus testen (Denk-Tokens bei 5 Tokens/s zu langsam).

## Ergebnis des Smoke-Tests (RUN-000, 2026-11-14)
- Speicher passt: `qwen2.5:7b` belegt 5,46 GB, `llama3.1:8b` 6,25 GB, `llama3.2` 3,12 GB (gemessen mit `ollama ps`, `num_ctx=8192`). Agent-Modell plus `nomic-embed-text` bleibt unter 9 GB.
- Geschwindigkeit (CPU): Prefill 18,9 / 20,1 / 45,9 Tokens/s, Generierung 5,0 / 5,9 / 12,5 Tokens/s für `qwen2.5:7b` / `llama3.1:8b` / `llama3.2`. Das bestätigt die Annahmen aus ISS-001.
- Tool-Calling: beide Agent-Kandidaten erreichen 4 von 5 Aufgaben (gleiche Fehlentscheidung, siehe ISS-006). Das Ergebnis trennt die Modelle nicht.
- **Vorläufige Wahl `llama3.1:8b`:** gleichauf bei der Trefferquote, aber rund 18 % schnellere Generierung und etwas schnelleres Prefill; der höhere Speicherbedarf (+0,8 GB) passt noch ins Budget. `qwen2.5:7b` bleibt Kandidat und lässt sich per `AUDIT_MODEL_AGENT` testen. Belastbar wird der Vergleich erst mit dem 12-Fragen-Katalog (M6).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| `phi3:medium` (14B) aus den Folien | sprengt `MemoryMax=9G` |
| Ein Modell für alles | Vision-Modell schwächer beim Tool-Calling; Agent-Modell kann keine Bilder |

## Konsequenzen
- Positiv: stabiler Betrieb ohne Swapping, klare Trennung Ingest/Query
- Negativ: lange Antwortzeiten; Evaluation dauert Stunden
- Noch zu testen (M5/M6): Mehrschritt-Agentenläufe und der Vergleich beider Kandidaten auf dem 12-Fragen-Katalog

## Belege
Hardware-Spezifikation; RUN-000 (`data/eval/run-000/smoke.md`); ISS-001, ISS-005, ISS-006.
