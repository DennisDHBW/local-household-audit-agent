# ADR-0008: Enrichment als eigener Schritt mit SHA-256-Cache

- **Status:** akzeptiert
- **Datum:** 2026-11-14
- **Meilenstein:** M3

## Kontext
Die Ingestion (M2) liefert 564 Chunks, darunter 5 Diagramme mit Platzhaltertext und 65 Tabellen mit 299 Zeilen. Für die Suche fehlen die Beschreibung der Diagramme (`search_images`) und eine thematische Zusammenfassung je Tabelle. Beides braucht ein Modell, und die CPU ist langsam: Prefill ca. 46 Tokens/s bei `llama3.2` und ca. 78 s pro Diagramm bei `gemma3:4b` (RUN-000). Das Enrichment darf deshalb nur einmal laufen, nicht bei jedem Parserlauf.

## Entscheidung
Das Enrichment ist ein eigener Schritt `python -m audit_agent.enrichment` (Paket `audit_agent.enrichment`) nach der Ingestion. Es liest `data/processed/*_chunks.json` und schreibt dorthin zurück.

1. **Bild-Captions:** `ImageCaptioner` schickt das PNG mit einem deutschen Prompt an `gemma3:4b` (Modell aus `Settings.models.vision`). Der Prompt enthält den `heading_stack` als Kontext, verlangt jede Beschriftung mit Zahlenwert und Einheit und verbietet Rechnen. Die Caption ersetzt den Platzhaltertext des `image`-Chunks.
2. **Tabellen-Summaries:** `TableSummarizer` fasst alle Zeilen einer `table_id` zusammen (`llama3.2`, 2–3 Sätze, Zahlen unverändert übernehmen). Das Ergebnis ist ein eigener Chunk vom Typ `table_summary` mit der ID `<…>_tabNN_sum`. Er steht vor der ersten Zeile der Tabelle und trägt `heading_stack`, Seite und Metadaten der ersten Zeile.
3. **Cache:** `diskcache` unter `.cache/enrichment/`. Der Schlüssel ist ein SHA-256 über Aufgabe, Modell-Tag, den vollständigen Prompt, die Generierungsoptionen (`num_ctx`, `num_predict`, `temperature`) und bei Bildern den SHA-256 der Bildbytes. Weil der fertige Prompt im Schlüssel steckt, macht jede Prompt-Änderung die alten Antworten ungültig, ohne dass eine Versionsnummer gepflegt werden muss. Fehlgeschlagene Aufrufe werden nicht gespeichert.
4. **Speicherbudget:** Die Phasen laufen nacheinander (erst alle Bilder, dann alle Tabellen). Vor dem Start werden alle geladenen Modelle entladen, nach jeder Phase das Modell der Phase. Es ist nie mehr als ein Modell geladen (ADR-0004).
5. **Fail fast, aber fortsetzbar:** Fehlende Modelle, fehlende Dateien und leere Modellantworten brechen den Lauf ab. Die JSON-Dateien werden nach jeder Phase geschrieben; bereits berechnete Antworten stehen im Cache, ein erneuter Start macht dort weiter.
6. **Idempotenz:** Mit gefülltem Cache macht ein Lauf keinen Modellaufruf und schreibt dasselbe Ergebnis. Läuft die Ingestion neu und überschreibt die JSONs, stellt ein Enrichment-Lauf den angereicherten Stand in Sekunden aus dem Cache wieder her.
7. **Prüfungen im Report:** Jede Summary wird gegen den Tabellentext geprüft: Zahlen, die dort nicht vorkommen, stehen im Report (`unsupported_numbers`); Tag, Monat und Jahr aus Datumsangaben der Tabelle gelten als vorhanden. Antworten, die am Token-Limit endeten (`done_reason == "length"`), sind mit `is_truncated` markiert. Beide Prüfungen markieren nur, sie verwerfen nichts. Die Prompts verbieten Rechnen, Vergleichen von Spalten und geschätzte Zahlen (RUN-002, ISS-023, ISS-024).
8. **Bedienung:** `--only images|tables`, `--limit N` für einen Probelauf, `--dry-run` zählt offene Jobs ohne Ollama, `--run-id` bestimmt den Ordner unter `data/eval/` für den Report.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Enrichment direkt im Parser | Jeder Parserlauf würde 20–25 Minuten dauern; Parser und Modellaufrufe wären nicht getrennt testbar (SoC, CQRS) |
| Cache-Schlüssel aus Chunk-ID | Ändert sich der Inhalt (Parser, Prompt, Modell), würde der Cache veraltete Antworten liefern |
| Prompt-Versionsnummer im Schlüssel | Muss von Hand gepflegt werden und wird vergessen; der Prompt-Text im Schlüssel ist fehlerfrei |
| Summary als Zusatzfeld der Zeilen | Die Summary soll einzeln gefunden werden (thematische Tabellensuche), also braucht sie einen eigenen Chunk |
| Größeres Modell für die Summaries | Zwei Modelle nacheinander sind im Budget, aber `llama3.1:8b` hätte ca. 20 statt 46 Tokens/s Prefill; die Tabellen sind klein und die Aufgabe einfach |
| Bild und Tabelle parallel verarbeiten | `OLLAMA_NUM_PARALLEL=1` und 9 GB: bringt auf der CPU nichts und riskiert das Speicherlimit |

## Konsequenzen
- Positiv: Das langsame Enrichment läuft einmal; Parser, Cache und Modellaufruf sind einzeln mit einem Fake-Client getestet (20 Tests ohne Ollama).
- Negativ: Die Ingestion überschreibt angereicherte Dateien; die Reihenfolge Ingestion → Enrichment muss eingehalten werden (ISS-021). Die Zahlenprüfung deckt nur Zahlen ab, keine inhaltlichen Fehler (ISS-022). Ein 3B-Modell kann Tabellen falsch zusammenfassen, deshalb stehen bei Tabellen immer auch die Einzelzeilen im Index.
- Zu testen: Ob die Summaries das Retrieval in M4 verbessern oder Distraktor-Treffer erzeugen; ob die Captions beim Abgleich mit der Tabelle in M5 abweichen (Vision-Fehler).

## Belege
RUN-002 in `evaluation-log.md`, `tests/test_enrichment.py`, ISS-021 bis ISS-024.
