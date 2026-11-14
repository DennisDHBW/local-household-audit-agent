# ADR-0004: Modellauswahl und Speicherbudget unter `MemoryMax=9G`

- **Status:** vorgeschlagen (Agent-Modell wird nach Smoke-Test in M0 festgelegt)
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

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| `phi3:medium` (14B) aus den Folien | sprengt `MemoryMax=9G` |
| Ein Modell für alles | Vision-Modell schwächer beim Tool-Calling; Agent-Modell kann keine Bilder |

## Konsequenzen
- Positiv: stabiler Betrieb ohne Swapping, klare Trennung Ingest/Query
- Negativ: lange Antwortzeiten; Evaluation dauert Stunden
- Zu testen (M0): Tool-Calling-Zuverlässigkeit und Geschwindigkeit von `qwen2.5:7b` vs. `llama3.1:8b` mit 5 einfachen Tool-Aufgaben

## Belege
Hardware-Spezifikation; Smoke-Test-Ergebnis folgt (RUN-000).
