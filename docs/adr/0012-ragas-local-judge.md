# ADR-0012: RAGAS mit lokalem Bewertermodell

- **Status:** vorgeschlagen (Technik mit Fakes getestet; erster echter Lauf im Probelauf RUN-009)
- **Datum:** 2026-11-15
- **Meilenstein:** M6b

## Kontext
`concept.md` 11.3 und die Anforderungen der Vorlesung verlangen neben eigenen Metriken ein etabliertes Framework mit KPIs, genannt ist RAGAS. RAGAS bewertet mit einem LLM als Bewerter und ist auf Cloud-Modelle ausgelegt. Rahmen: nur lokal (ADR-0001), nur CPU, höchstens 8B-Modelle, `MemoryMax=9G`, Prefill ca. 18 Token/s. Die Antworten der drei Varianten liegen bereits als JSON-Zeilen vor (ADR-0011), enthielten bis M6a aber nur Dateiname und Seite der Belege, nicht deren Text.

## Entscheidung
Ein eigener Schritt `ragas` bewertet die gespeicherten Antworten nachträglich, getrennt von `generate` und `score`.

1. **Version und Anbindung:** `ragas==0.4.4` als eigene Abhängigkeitsgruppe (`uv sync --group ragas`), nur in `evaluation/ragas_eval.py` und erst bei Bedarf importiert. Bewerter über `llm_factory` (Instructor, JSON-Modus) an Ollamas OpenAI-kompatibler Schnittstelle `/v1`.
2. **Metriken:** Faithfulness (Anteil der Aussagen der Antwort, die durch die gezeigten Belege gedeckt sind; 2 Bewerteraufrufe) und Context Recall (Anteil der Aussagen der erwarteten Antwort, die in den Belegen stehen; 1 Aufruf). Context Recall entfällt für Negativfragen, weil deren Referenz nur eine Lücke beschreibt.
3. **Belege:** `VariantAnswer.contexts` speichert den Text, den das Modell wirklich sah: B0 je Seite ein Block, P1 je Treffer ein Block, P2 die Beobachtung jedes gültigen Tool-Aufrufs (Treffer, Dokumentlisten, Rechenergebnisse).
4. **Bewertermodell:** festes Alias `audit-judge` aus `qwen2.5:7b` mit `num_ctx 8192` und Temperatur 0 (`scripts/audit-judge.Modelfile`). Die OpenAI-Schnittstelle nimmt kein `num_ctx` je Anfrage an; ohne Alias würde Ollama mit seinem Standardkontext still kürzen (ISS-041). Ein Unit-Test prüft, dass Modelfile und `EvaluationSettings.judge_num_ctx` übereinstimmen.
5. **Keine stille Kürzung:** Vor jedem Aufruf wird der längste Bewerter-Prompt mit den RAGAS-Prompt-Klassen gebaut und mit 2,4 Zeichen/Token plus Antwortbudget geschätzt. Passt er nicht, wird die Antwort als „zu lang“ markiert und nicht bewertet.
6. **Robust über Nacht:** Fehler des Bewerters (ungültiges JSON, Zeitüberschreitung) werden je Antwort gespeichert, ein Verbindungsabbruch beendet den Lauf. Ergebnis: `ragas.jsonl`, eine Zeile je Antwort und Metrik, fortsetzbar; `--retry-errors` wiederholt nur Fehlschläge. `score` übernimmt die Mittelwerte in `scores.json` und `report.md`.
7. **Telemetrie aus:** RAGAS schickt sonst Nutzungsereignisse an den Hersteller; `RagasJudge` setzt `RAGAS_DO_NOT_TRACK=true` vor dem ersten Import (ISS-044).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Bewerter = jeweiliges Antwortmodell | Jedes Modell bewertet sich selbst; die Werte der beiden Läufe wären nicht vergleichbar |
| Gegenseitige Bewertung (`llama3.1:8b` ↔ `qwen2.5:7b`) | Kein Selbstbewertungsfehler, aber zwei verschiedene Maßstäbe; die Werte der Läufe wären wieder nicht vergleichbar |
| `llama3.1:8b` als fester Bewerter | Ebenfalls Selbstbewertung (Standard-Agentenmodell); `qwen2.5:7b` wurde wegen seines Rufs bei strukturierten JSON-Ausgaben gewählt, das ist im Projekt aber noch nicht gemessen (RUN-009) |
| Answer Relevancy, Context Precision zusätzlich | Etwa doppelte Laufzeit (Context Precision ein Aufruf je Beleg, Answer Relevancy mehrere Generierungen plus Embeddings) |
| LangChain-Wrapper (`LangchainLLMWrapper`, `ChatOllama`) | In RAGAS 0.4 veraltet; `llm_factory` ist der dokumentierte Weg |
| RAGAS-Testset-Generierung (synthetische Fragen) | Viele zusätzliche LLM-Aufrufe; der eigene Katalog mit Ground Truth ist für die eingebauten Fehler aussagekräftiger |

## Konsequenzen
- Positiv: RAGAS-Werte ohne Neugenerieren der Antworten; nichts verlässt den Rechner; keine stillen Kürzungen; Kern und Quality Gate bleiben ohne LangChain.
- Negativ / Preis: Ein 7B-Bewerter ist selbst fehleranfällig, die RAGAS-Prompts sind englisch, die Texte deutsch; beim `qwen2.5:7b`-Lauf bewertet das Modell seine eigenen Antworten (ISS-045). B0 ist mit ca. 6.700 Token Belegen fast immer „zu lang“ und bekommt keine RAGAS-Werte (ISS-046). Laufzeit grob 3 Bewerteraufrufe à 1–3 Minuten je Antwort.
- Zu testen: RUN-009 (Probelauf G3/G4): liefert `audit-judge` gültiges JSON, wie lange dauert ein Aufruf, meldet das Journal Kürzungen? Danach Stichproben von Hand gegen die Urteile prüfen.

## Belege
ISS-040, ISS-041, ISS-044 bis ISS-046; RAGAS-Quelltext 0.4.4 (`ragas/metrics/collections/faithfulness`, `context_recall`, `_analytics.py`); RAGAS-Doku „LLM adapters“ (Abschnitt Ollama).
