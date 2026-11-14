# Evaluations-Logbuch

> Jeder Testlauf wird hier festgehalten, auch Fehlschläge. Ohne festgehaltene Konfiguration sind Ergebnisse später nicht vergleichbar.
> Rohdaten (CSV/JSON) liegen unter `data/eval/<run-id>/`, hier stehen nur Zusammenfassung und Deutung.

## Vorlage

```markdown
### RUN-000 – <Zweck, z. B. "Baseline P1 vs. P2, erster Lauf">
- **Datum / Commit:**
- **Varianten:** B0 (Volltext) / P1 (Pipeline) / P2 (Agent)
- **Konfiguration:** Modell(e), num_ctx, top_k, Boost-Faktor, Filter an/aus, Testset-Version
- **Dauer:** gesamt … min, pro Frage Ø … s
- **Ergebnisse (Kurz):**

| Metrik | B0 | P1 | P2 |
|---|---|---|---|
| Numerische Korrektheit | | | |
| Fehlererkennungsrate | | | |
| Fehlalarmrate | | | |
| Quellen-Korrektheit | | | |
| Distractor Rate | | | |
| Tool-Wahl-Korrektheit | – | – | |
| Negativ-Erkennung | | | |
| RAGAS Faithfulness | | | |
| RAGAS Context Precision | | | |
| Latenz Ø (s) | | | |

- **Auffällige Einzelfälle:** (Frage-ID, was ging schief, an welcher Stelle: Parser / Retrieval / Tool-Wahl / Synthese)
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:**
```

---

## Läufe

*(noch keine)*

### RUN-000 – Smoke-Test M0 (Geschwindigkeit, Tool-Calling, Embedding, Vision)
- **Datum / Commit:** 2026-11-14 · Code-Stand `feat(smoke)` auf Branch `feat/m0-setup`
- **Varianten:** keine (Setup-Messung, noch keine Pipeline)
- **Konfiguration:** `num_ctx=8192`, `temperature=0`, Ollama 0.35.1, reine CPU, `MemoryMax=9G`; Modelle `qwen2.5:7b`, `llama3.1:8b`, `llama3.2`, `gemma3:4b`, `nomic-embed-text`; Modelle einzeln geladen und danach entladen
- **Dauer:** ca. 6,5 Minuten gesamt (15:17–15:23)
- **Rohdaten:** `data/eval/run-000/` (`smoke.json`, `smoke.md`, `console.log`, `chart.png`)

| Messung | qwen2.5:7b | llama3.1:8b | llama3.2 |
|---|---|---|---|
| Prefill (Tokens/s) | 18,9 | 20,1 | 45,9 |
| Generierung (Tokens/s) | 5,0 | 5,9 | 12,5 |
| Ladezeit (s) | 12,9 | 10,5 | 5,5 |
| RAM (GB) | 5,46 | 6,25 | 3,12 |
| Tool-Wahl richtig (5 Aufgaben) | 4/5 | 4/5 | – |
| Argumente gültig | 4/5 | 4/5 | – |

- **Embedding:** `nomic-embed-text`, 768 Dimensionen; Kosinus-Ähnlichkeit relevant 0,747 vs. irrelevant 0,550 → Ranking korrekt.
- **Vision:** `gemma3:4b` brauchte 78 s für das Diagramm (Seite 2 der Stromabrechnung 2024) und gab alle sechs Balkenwerte richtig wieder (3.480 / 3.390 / 3.250 sowie 1.900 / 3.000 / 3.900 kWh), nachgeprüft am Bild. Die Zuordnung zu den Beschriftungen war richtig, die Beschreibung der Gruppen etwas frei.
- **Auffällige Einzelfälle:**
  - Aufgabe T2 („Arbeitspreis laut Stromvertrag“): beide Modelle wählten `search_documents` statt `search_tables` (Tool-Wahl, ISS-006).
  - Beide Modelle setzten bei fast jedem Suchaufruf selbst einen `doc_type`-Filter (ISS-007).
  - Prefix-Test: „wiederverwendet: nein“ in `smoke.md` ist ein Messfehler. Die Tokenzahl (507 vs. 502) sagt bei Ollama 0.35.1 nichts über den Cache aus (ISS-005). Indirekter Hinweis auf Wiederverwendung: Die erste Tool-Aufgabe dauerte 38–42 s (inkl. Laden und Prefill von ca. 370 Tokens), die folgenden mit gleichem System-Prompt und gleichen Tool-Schemas nur 6–8 s.
- **Grenzen der Messung:** nur 5 Aufgaben pro Modell und nur der erste Schritt ohne Rückgabe von Tool-Ergebnissen; eine Einzelmessung pro Modell (keine Streuung); der Vision-Test prüft „Sollwerte kommen vor“ und ist deshalb großzügig.
- **Meine Deutung (eigene Worte):**

### RUN-001 – Parser-Lauf M2 (30 PDFs → JSON-Zwischenformat)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m2-parser`, Stand nach `refactor(ingestion): rename Chunk to DocumentChunk …`
- **Varianten:** keine (kein LLM, nur Parser)
- **Konfiguration:** `ParserSettings` mit Standardwerten (`min_chars=20`, `max_block_chars=1500`, Kopfzone 4 %, Fußzone 6 %, `heading_size_factor=1.0`, `cell_gap_pt=5`, `min_image_width_pt=50`); PyMuPDF 2.1 (Lockfile), Python 3.13; Befehl `uv run python -m audit_agent.ingestion`
- **Dauer:** ca. 31 s für 30 PDFs (Claudes VM, CPU)
- **Rohdaten:** `data/processed/*_chunks.json`, `data/processed/images/` (nicht versioniert, jederzeit neu erzeugbar)

| Messung | Wert |
|---|---|
| Dokumente / Seiten | 30 / 34 |
| Chunks gesamt | 564 |
| davon `text` | 178 |
| davon `heading` | 82 |
| davon `table_row` | 299 (aus 65 Tabellen) |
| davon `image` | 5 (Diagramme in Dok. 04, 06, 10 (2×), 15) |
| Text-Chunks: Länge min / max (Zeichen) | 25 / 1.056 (Grenze 1.500 nie erreicht) |

- **Manuelle Sichtprüfung** (Chunk-Liste gegen PDF) an Dok. 04, 10, 16, 18, 22, 26, 29, 30:
  - Spaltenköpfe stehen in jeder Tabellenzeile; Beträge, Einheiten und Datumsangaben sind unversehrt („Betrag Brutto: 1.131,00 EUR“).
  - Fehlerdokumente: Dok. 29 enthält „z-Zahl: 1,0000“ und „Volumen: 1.060 m³“ als Zeile; „Rechnungsbetrag … 1.367,99 EUR“ und „Abzüglich Abschlagszahlungen … -1.375,00 EUR“ stehen in getrennten Zeilen. Dok. 30 enthält „Wohnfläche 82,00 m²“ im Text.
  - Fußzeilen (Bank, Handelsregister) und Seitenkopf („Seite 2 von 2“) tauchen in keinem Chunk auf.
- **Auffällige Einzelfälle (Parser):** Briefkopf-Tabellen in Dok. 08/10/29 mischen Anschrift und Metadaten (ISS-015); Firmennamen im Briefkopf werden zu Überschriften (ISS-016); die Fehler ISS-012 bis ISS-014 fielen erst bei der Sichtprüfung der echten PDFs auf; die Unit-Tests entstanden danach und sichern sie jetzt ab.
- **Grenzen der Messung:** Die Sichtprüfung deckt acht von 30 Dokumenten ab; es gibt keinen automatischen Vergleich gegen eine Soll-Struktur. Die Golden-Tests prüfen einzelne Zeilen, nicht die Vollständigkeit.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** M3: Bild-Captions (`gemma3:4b`) und Tabellen-Summaries; danach M4 mit Embedding und erstem Retrieval, dort die Wirkung der Briefkopf-Chunks prüfen.

