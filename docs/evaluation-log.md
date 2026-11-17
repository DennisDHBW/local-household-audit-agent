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

### RUN-002 – Enrichment M3, erster Lauf (5 Captions, 65 Tabellen-Summaries)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m3-enrichment`, Stand `docs: document enrichment design …`
- **Varianten:** keine (kein Retrieval, nur Anreicherung)
- **Konfiguration:** `gemma3:4b` (Captions, `num_predict=400`) und `llama3.2` (Summaries, `num_predict=160`), `num_ctx=8192`, `temperature=0`, Ollama 0.35.1, reine CPU, Cache leer; Befehl `uv run python -m audit_agent.enrichment --run-id run-002`
- **Dauer:** 26,4 Minuten Modellzeit für 70 Jobs; Captions 63–93 s (Ø 74 s), Summaries Ø 18,7 s (max. 37 s)
- **Rohdaten:** `data/eval/run-002/` (`enrichment.json`, `console.log`)

| Messung | Wert |
|---|---|
| Captions mit richtigen Beschriftungswerten (gegen PNG geprüft) | 4 von 5 |
| Summaries gesamt | 65 |
| davon am Token-Limit abgeschnitten (Satz endet mitten im Wort oder in der Aufzählung) | 21 |
| davon mit Zahl, die nicht im Tabellentext steht (alte Prüfung) | 11 |
| davon nach Korrektur der Prüfung (Datumsteile erlaubt, nachgerechnet an RUN-002) | 4 |

- **Captions (Sichtprüfung gegen die PNGs):**
  - Dok. 04, 06, 10 (Balkendiagramm), 15: alle Beschriftungswerte richtig (z. B. 06: alle zwölf Monate von 320 bis 340 kWh; 15: 81, 78, 74, 91 m³).
  - Dok. 10, zweites Diagramm (Heizgasbedarf mit Temperaturlinie): **erfundene Werte**. Die Säulen haben keine Zahlenbeschriftung, das Modell hat trotzdem Zahlen genannt (Juli 2.300 kWh, im Bild ca. 130 kWh; Sommer und Winter vertauscht), das Doppelachsen-Diagramm als zwei Diagramme beschrieben und beim Token-Limit mitten im Wort („Ok“) abgebrochen (ISS-023).
- **Summaries (Auffälligkeiten):**
  - Inhaltliche Fehler, von der Zahlenprüfung gefunden: Dok. 05 nennt einen Verbrauch von „1.234.567,89 kWh“ (Zahl erfunden, die Tabelle ist der Briefkopf); Dok. 14 schreibt, der Trinkwasserpreis werde „um 0,04 EUR/m³ geringer“, tatsächlich steigt er von 2,30 auf 2,42 EUR brutto (das Modell verglich Netto neu mit Brutto alt); Dok. 03 nennt selbst berechnete Differenzen (2,86 ct), obwohl der Prompt das verbietet.
  - Das Modell hielt sich oft nicht an „zwei bis drei Sätze“, sondern schrieb Aufzählungen und begann mit „Die Tabelle aus einer Abrechnung oder einem Vertrag zeigt …“ (Wortlaut aus dem Prompt).
  - Zusammenfassungen von Briefkopf-Tabellen (Dok. 02, 05) sind inhaltlich Rauschen (ISS-015).
- **Auffällige Einzelfälle:** 7 von 11 gemeldeten Summaries waren Fehlalarme der Prüfung (Datum „16. Oktober 2024“ im Text, „16.10.2024“ in der Tabelle). Die Prüfung wurde danach so geändert, dass Tag, Monat und Jahr aus Datumsangaben als vorhanden gelten.
- **Grenzen der Messung:** Nur die 5 Captions und die 11 gemeldeten Summaries wurden von Hand geprüft; die übrigen 54 Summaries sind nur gegen die Zahlenprüfung getestet (ISS-022). Eine Messung pro Konfiguration.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Prompts und Limits anpassen (Caption: keine Zahlen schätzen, 600 Tokens; Summary: höchstens drei Sätze, keine Differenzen, 256 Tokens), Abschneiden im Report markieren, zweiter Lauf als RUN-003. Die abgeschnittenen und fehlerhaften Summaries aus RUN-002 sind der Grund, den Lauf zu wiederholen.

### RUN-003 – Enrichment M3, zweiter Lauf mit angepassten Prompts
- **Datum / Commit:** 2026-11-14 · Branch `feat/m3-enrichment`, Stand `fix(enrichment): flag truncated answers, tighten prompts …`
- **Varianten:** keine (kein Retrieval)
- **Konfiguration:** wie RUN-002, aber Caption-Prompt „keine Zahlen schätzen“ mit `num_predict=600`, Summary-Prompt „höchstens drei Sätze, keine Differenzen“ mit `num_predict=256`; Cache der Prompts neu, alle 70 Jobs berechnet; Befehl `uv run python -m audit_agent.enrichment --run-id run-003`
- **Dauer:** 26,6 Minuten Modellzeit; Captions 65–79 s (Ø 73 s), Summaries Ø 18,9 s (max. 38 s)
- **Rohdaten:** `data/eval/run-003/` (`enrichment.json`, `console.log`)

| Messung | RUN-002 | RUN-003 |
|---|---|---|
| Captions mit richtigen Beschriftungswerten (gegen PNG) | 4 von 5 | 4 von 5 |
| Caption mit erfundenen Zahlen | 1 | 0 |
| am Token-Limit abgeschnitten (Captions / Summaries) | 1 / 21 | 0 / 0 |
| Summaries mit Zahl, die nicht in der Tabelle steht | 11 (alte Prüfung), 4 (neue Prüfung) | 6 |
| Summaries mit Aufzählung / Einleitung „Die Tabelle aus …“ | viele | 5 / 8 |
| Summary-Länge Ø / max (Zeichen) | 370 / 542 | 363 / 697 |

- **Captions:** Die vier Diagramme mit beschrifteten Werten sind weiterhin vollständig richtig (04, 06, 10 Balken, 15). Das Heizgas-Diagramm ohne Zahlenbeschriftung (Dok. 10, zweites Bild) enthält keine erfundenen Zahlen mehr, aber der beschriebene Verlauf stimmt nicht: Das Modell schreibt „im Juli und August ist der Erdgasbedarf am höchsten“, tatsächlich ist er im Sommer am niedrigsten, und die Beschreibung ist für die Suche nahezu wertlos (ISS-023).
- **Summaries, 6 Meldungen der Zahlenprüfung:**
  - Briefkopf-Tabellen (Dok. 08, 10, 29, jeweils `tab01`): erfundene Verbrauchsangaben („7.500 Kubikmeter“, „7.000 MWh“) und falsche Rechnungsnummer, weil die Tabelle nur Anschrift und Kundendaten enthält (ISS-015).
  - Dok. 03: selbst gerechnete Differenzen (2,86 ct; 15,08 EUR), teils falsch.
  - Dok. 27: Summe „320,22 Euro“ aus zwei Tabellenwerten gebildet.
  - Dok. 28: „31“ aus dem Datum, Prüfung zu streng.
- **Fehler, die die Prüfung nicht findet:** Dok. 14 (Wassergebühren): „Trinkwasser-Verbrauchspreis von 2,30 auf 2,26 EUR/m³ gesenkt“. Beide Zahlen stehen in der Tabelle, aber 2,30 ist der alte Brutto-, 2,26 der neue Nettopreis; der neue Bruttopreis ist 2,42 EUR. Außerdem „Vorauszahlung wird eingeführt“ statt „von 120 auf 125 EUR erhöht“. Die Zahlenprüfung kann solche Fehler grundsätzlich nicht erkennen (ISS-022).
- **Auffällige Einzelfälle:** Einfache Tabellen (Dok. 04 tab01–03, 05 tab02) sind sauber und vollständig zusammengefasst. Probleme treten bei Tabellen mit mehreren Preisspalten (netto/brutto, bisher/neu) und bei Briefkopf-Tabellen auf.
- **Grenzen der Messung:** Von Hand geprüft wurden die 5 Captions, die 6 gemeldeten und 4 weitere Summaries; die übrigen 55 sind nur automatisch auf Zahlen und Abschneiden geprüft. Eine Messung pro Konfiguration, kein Vergleich mehrerer Modelle.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Die Anpassung der Prompts hat Abschneiden (21 → 0) und erfundene Caption-Zahlen beseitigt, aber nicht die inhaltlichen Fehler bei Preistabellen. Summaries gelten deshalb nur als Suchhilfe (thematisches Finden), nie als Beleg: Der Agent zitiert und rechnet mit `table_row`-Chunks. In M4 zeigt die Evidence-UI den Typ „KI-Zusammenfassung“, und es wird gemessen, ob die Summaries das Retrieval verbessern oder Distraktoren erzeugen. Kein dritter Lauf: Ein 3B-Modell wird durch weitere Prompt-Arbeit nicht zuverlässig.

### RUN-004 – Retrieval M4: Filter, Boost und Chunk-Auswahl (12 Fragen, 6 Konfigurationen)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m4-retrieval`, Stand `docs: document retrieval commands, prefix format and glossary terms for M4`
- **Varianten:** P1-Retrieval allein (ohne Agent und ohne Synthese); sechs Konfigurationen derselben Suche
- **Konfiguration:** `nomic-embed-text` (768 Dimensionen), Cosinus, 547 Chunks (178 Text, 299 Tabellenzeilen, 65 Summaries, 5 Bilder; 82 Überschriften nicht eingebettet), 20 Kandidaten, Top-5, Boost 1.5; Fragen S1 bis Z3 aus `ground_truth.yaml` (10 beantwortbar, 2 negativ); Filter je Frage von Hand gesetzt (`QUESTION_FILTERS`, ISS-028); Befehl `uv run python -m audit_agent.retrieval index` und `… compare --run-id run-004`
- **Dauer:** Index 86,1 s; der gesamte Befehl (Index, Vergleich, drei Beispielsuchen) lief nach den Dateizeitstempeln unter 2 Minuten
- **Rohdaten:** `data/eval/run-004/` (`retrieval.json`, `retrieval.md`, `index.log`, `compare.log`, `search-s2-*.txt`)

| Konfiguration | Datei gefunden | Seite gefunden | MRR (Datei) | Ablenker-Treffer | leere Ergebnisse |
|---|---|---|---|---|---|
| plain (kein Filter, kein Boost) | 9/10 | 9/10 | 0,683 | 4/60 | 0 |
| nur Boost | 9/10 | 9/10 | 0,683 | 3/60 | 0 |
| nur Filter | 9/10 | 9/10 | 0,733 | 0/55 | 1 |
| Filter + Boost | 9/10 | 9/10 | 0,733 | 0/55 | 1 |
| Filter + Boost, ohne Summaries | 8/10 | 8/10 | 0,633 | 0/55 | 1 |
| Filter + Boost, ohne Text ohne Kapitel | 9/10 | 9/10 | 0,733 | 0/55 | 1 |

- **Filter:** Ablenker-Treffer (Internet-Dokumente 22/23) sinken von 4 auf 0, die MRR steigt von 0,683 auf 0,733 (G1: Rang 2 → 1). N2 (Fernwärme) liefert mit Filter kein Ergebnis, was richtig ist, denn es gibt keine Fernwärme-Dokumente; ohne Filter kommen dort zwei Internet-Dokumente zurück.
- **Boost:** Ränge unverändert, Ablenker nur 4 → 3. Der Boost wirkte bei 55 von 60 Treffern (ohne Filter) und bei allen 55 (mit Filter), also fast gleichmäßig: Begriffe wie „Kündigungsfrist“ oder „Arbeitspreis“ stehen in den Überschriften vieler Dokumente (S2: „arbeits“ trifft die Gas-Preisanpassung, S1: „Kündigungsfrist“ trifft die Internet-Zusammenfassung). Ein gleichmäßiger Faktor ändert die Reihenfolge nicht (ISS-027).
- **Summaries:** Ohne sie sinkt die Trefferquote auf 8/10 und die MRR auf 0,633 (S2: erwartetes Dokument fällt aus den Top-5, G1: Rang 1 → 2). Sie helfen dem Retrieval, sind aber kein Beleg (ADR-0008).
- **Chunks ohne Kapitel (Briefkopf, Anschrift):** Ausschalten ändert kein Ergebnis dieser 12 Fragen; sie stören nicht messbar und bleiben im Index.
- **Auffällige Einzelfälle:**
  - S4 (Verbrauch 2022/2023 nur im Diagramm): in keiner Konfiguration in den Top-5, der Bild-Chunk der Abrechnung 2024 verliert gegen Chunks zu Verbrauch 2025 (ISS-029).
  - S2: Rang 2. Platz 1 ist die Summary der Preisanpassung 2025 (0,712 × 1,5 = 1,068), danach der Vertrag; für die Frage „laut Stromvertrag“ ist der Filter `doc_type=contract` die Aufgabe des Agenten.
  - N1 (Stromrechnung 2023): die Suche liefert Rechnungen 2024 und 2025; dass es 2023 keine gibt, muss der Agent über `list_documents` erkennen.
  - „Seite gefunden“ ist gleich „Datei gefunden“, weil bis auf S4 alle erwarteten Quellen auf Seite 1 stehen; die Seitenmetrik trennt hier nichts.
- **Grenzen der Messung:** 10 beantwortbare Fragen, nach dem Pipeline-Bau bekannt; Filter von Hand statt vom Agenten gewählt (ISS-028); eine Messung je Konfiguration; von jeder Suche nur die Top-5 gespeichert, daher ist der Rang außerhalb der Top-5 unbekannt; keine Messung der Antwortqualität.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Der Filter trägt den Nutzen (ADR-0002 akzeptiert), der Boost bleibt als Vorlesungsbaustein, sein Nutzen ist nicht belegt (ISS-027). Summaries und Chunks ohne Kapitel bleiben im Index. M5: Tool `search_images` mit `chunk_types={image}` für S4; Tool-Beschreibungen sagen, wann welcher Filter zu setzen ist (ISS-025).

### RUN-005 – Agent M5, erster Lauf (4 Fragen, `llama3.1:8b`)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m5-agent`, Stand `docs: document agent commands, glossary terms, concept notes and M5 issues`
- **Varianten:** P2 (Agent)
- **Konfiguration:** `llama3.1:8b`, `num_ctx` 8192, `temperature` 0, `num_predict` 600, höchstens 6 Werkzeugaufrufe, Treffer auf 600 Zeichen gekürzt, `table_summary`-Treffer für das Modell sichtbar (damaliger Stand), Index aus M4; Fragen S2, G1, N1, S4; Befehl `uv run python -m audit_agent.agent run-set --run-id run-005`
- **Dauer:** S2 183 s, G1 66 s, N1 33 s, S4 301 s, zusammen knapp 10 Minuten
- **Rohdaten:** `data/eval/run-005/` (`agent.md`, `agent.json`, `agent-<Frage>.jsonl`), `data/eval/run-005.log`

| Frage | erwartete Tools | gerufene Tools | Antwort richtig | Ende |
|---|---|---|---|---|
| S2 Arbeits-/Grundpreis | search_tables | search_tables | nein (netto statt brutto) | answer |
| G1 neuer Arbeitspreis angewendet? | search_tables, calculate | search_documents | nein („keine Angaben“) | answer |
| N1 Stromrechnung 2023 | list_documents | search_tables, list_documents | ja („keine Angaben“) | answer |
| S4 Verbrauch 2022/2023 | search_images | search_tables, list_documents, search_tables, calculate ×3 | nein | tool_limit |

- **Technik:** Alle 4 Läufe liefen durch; Schleife, Argumentprüfung, Log und Belegnummern funktionieren; keine Abstürze, kein Kontextüberlauf.
- **S2:** Die Suche fand die richtigen Tabellenzeilen (Treffer [2] Grundpreis, [4] Arbeitspreis, je mit netto und brutto). Das Modell nahm aber Treffer [1], die KI-Zusammenfassung, und nannte 29,24 ct/kWh und 9,66 EUR/Monat (netto). Erwartet waren die Bruttowerte 34,80 ct/kWh und 11,50 EUR/Monat. Die Warnung „kein Beleg“ im Treffer hat das Modell nicht gehindert (ISS-035).
- **G1:** Das Modell wählte `search_documents` mit den selbst gesetzten Filtern `bill` und Jahr 2025 (ISS-007). Die Preisanpassung ist keine Rechnung, also fehlte sie; nach einem Aufruf antwortete es „keine Angaben“. Weder Rechnungszeile noch `calculate` kamen vor (ISS-036).
- **N1:** Richtig. Die Suche mit Jahr 2023 fand nichts, `list_documents` bestätigte, dass es nur Rechnungen 2024 und 2025 gibt, die Antwort räumt die Lücke ein.
- **S4:** `search_tables` mit Jahr 2022 und `bill` fand nichts; `search_images` wurde nie gerufen. Dann dreimal derselbe ungültige Aufruf `calculate({'a': ..., 'b': ...})`, obwohl die Fehlermeldung den fehlenden Parameter nannte. Die erzwungene Schlussantwort nennt Rechnungsbeträge in EUR „Stromverbrauch“ (ISS-036).
- **Zeiten und Prompt (ISS-030, ISS-005):** Der erste Aufruf hatte 1.997 bis 2.008 Prompt-Token (Tool-Schemas plus System-Prompt). Prefill S2: 108,7 s (18 Token/s, wie ISS-001); G1 und N1: 4,8 s und 2,8 s für dieselbe Prompt-Länge, also Wiederverwendung des Anfangs im Cache; S4: wieder 88,9 s, ohne erkennbaren Grund. Der letzte Aufruf ohne Tools (S4, 1.621 Token) kostete 69,6 s, wie in ADR-0010 vorhergesagt. Die gemeldeten Token-Zahlen sind widersprüchlich (N1, zweiter Aufruf: 563 Token, weniger als die Schemas allein); `prompt_eval_count` ist nicht die Kontextgröße. Der Kontextwächter schätzt deshalb jetzt selbst.
- **Grenzen der Messung:** 4 von 12 Fragen, ein Lauf, ein Modell; grobe Prüfung (Tool, Quelle, Zahl), die Antworten wurden von Hand gelesen; die Zeitmessung stammt aus Ollama-Zahlen, die nicht immer zueinander passen.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Vier Änderungen mit Test: (1) Summaries für das Modell ausgeblendet (`include_table_summaries=False`), (2) System-Prompt: Preise brutto, Verbräuche früherer Jahre stehen im Diagramm, (3) eine Antwort „keine Angaben“ nach weniger als 2 Werkzeugaufrufen wird einmal hinterfragt, (4) Fehlermeldung bei ungültigen Argumenten nennt den richtigen Aufruf. RUN-006 prüft dieselben Fragen. Das Modell (`llama3.1:8b` gegen `qwen2.5:7b`) bleibt Aufgabe von M6.

### RUN-006 – Agent M5, zweiter Lauf nach Korrekturen (4 Fragen, `llama3.1:8b`)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m5-agent`, Stand `docs: record RUN-005, ISS-035 and ISS-036 and update ADR-0010`
- **Varianten:** P2 (Agent)
- **Konfiguration:** wie RUN-005, aber `table_summary` für das Modell ausgeblendet, Prompt mit „Preise brutto“ und Hinweis auf Vorjahreswerte im Diagramm, Rückfrage bei „keine Angaben“ nach weniger als 2 Werkzeugaufrufen, Fehlermeldung mit richtigem Aufruf; Befehl `uv run python -m audit_agent.agent run-set --run-id run-006`
- **Dauer:** S2 192 s, G1 266 s, N1 36 s, S4 421 s, zusammen gut 15 Minuten
- **Rohdaten:** `data/eval/run-006/`, `data/eval/run-006.log`

| Frage | gerufene Tools | Antwort richtig | Ende | RUN-005 |
|---|---|---|---|---|
| S2 | search_tables | ja (34,80 ct/kWh brutto, 11,50 EUR/Monat brutto) | answer | falsch (netto) |
| G1 | search_documents ×2 (mit Rückfrage) | nein (nennt den Abschlag 120 EUR, nicht den Arbeitspreis) | answer | falsch („keine Angaben“) |
| N1 | search_tables, list_documents | ja („keine Angaben“) | answer | ja |
| S4 | search_tables ×4, list_documents, calculate (ungültig) | nein, aber ehrlich („keine Informationen gefunden“) | tool_limit | falsch (Euro als Verbrauch) |

- **S2 gelöst:** Ohne Summaries steht die Tabellenzeile oben, das Modell nennt die Bruttowerte. Es zitiert keine Belegnummer, obwohl der Prompt es verlangt.
- **G1 nicht gelöst:** Die Rückfrage wurde ausgelöst („Antwort nach einem Aufruf: keine Angaben“), das Modell wiederholte aber denselben Aufruf mit `bill` und Jahr 2025 unverändert. Danach antwortete es mit einer unpassenden Zahl, nicht mit „keine Angaben“. Die Rückfrage hat also die falsche Antwort nur ausgetauscht.
- **S4 nicht gelöst:** `search_images` wird wieder nie gerufen; viermal `search_tables` mit erfundenem Argument `doc_id`; ein ungültiger `calculate`-Aufruf (`a` bis `e`), obwohl die Meldung `calculate(expression*)` nannte. Die Schlussantwort ist diesmal ehrlich statt falsch.
- **Zeiten:** Erste Aufrufe 2.041 bis 2.055 Prompt-Token; Prefill S2 118 s und S4 100 s (kein Cache), G1 5 s und N1 3 s (Cache). Der Aufruf ohne Tools am Ende von S4 (2.594 Token) brauchte 140 s. Die gemeldeten Token-Zahlen bleiben uneinheitlich (je Frage meldet der zweite Aufruf nur 1.254, 1.300 oder 610 Token, weniger als die Tool-Schemas allein); `prompt_eval_count` ist weiter kein Maß für die Kontextgröße.
- **Grenzen der Messung:** wie RUN-005 (4 Fragen, ein Lauf, ein Modell, Antworten von Hand gelesen).
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Die Technik (Schleife, Argumentprüfung, Log, Oberfläche) steht; die Antwortqualität von `llama3.1:8b` bei Tool-Wahl und Filtern nicht (2 von 4). Weitere Prompt-Arbeit an vier Fragen wäre Anpassen an den Test. M6 misst alle 12 Fragen mit `llama3.1:8b` und `qwen2.5:7b` und prüft Gegenmaßnahmen: gemeinsames Suchwerkzeug (ISS-006), Filter nur durch Code statt durch das Modell (ISS-007), Beispiele im Prompt.

### RUN-007 – Testmodul M6a, erster Probelauf B0/P1/P2 (3 Fragen, `llama3.1:8b`, abgebrochen)
- **Datum / Commit:** 2026-11-14 · Branch `feat/m6a-eval-harness`, Stand `docs: record evaluation harness (ADR-0011) …`
- **Varianten:** B0 (Volltext), P1 (Pipeline), P2 (Agent)
- **Konfiguration:** `llama3.1:8b`, `num_ctx` 8192, Temperatur 0; B0 mit Dateien 01–08 (ca. 6.900 geschätzte Token); P1 Top-5 ohne Filter mit Boost; P2 wie RUN-006; Fragen S2, G1, N1; Befehl `uv run python -m audit_agent.evaluation generate --run-id run-007 --ids S2 G1 N1`
- **Dauer:** ca. 16 Minuten bis zum Abbruch; B0 je Frage rund 300 s, P1 31–60 s, P2/S2 207 s
- **Abbruch:** Bei P2/G1 war Ollama nicht mehr erreichbar (`ConnectionError`); 7 von 9 Antworten gespeichert. Ursache: OOM-Kill (ISS-043). Der CLI fing den Fehler nicht ab und schrieb `manifest.json` erst am Ende (ISS-042, behoben).
- **Rohdaten:** `data/eval/run-007/` (`answers-*.jsonl`, `p2-S2.jsonl`, `report.md`, `scores.json`), `data/eval/run-007.log`

| Frage | B0 Volltext | P1 Pipeline | P2 Agent |
|---|---|---|---|
| S2 | falsch: 33,19 ct/kWh und 10,84 EUR netto (Werte der Rechnung 2025, als „Vertrag [1]“ zitiert) | „keine Angaben“; Vertrag nicht unter den Top-5 | richtig (34,80 ct/kWh, 11,50 EUR brutto), ohne Belegnummer |
| G1 | Urteil „nicht angewendet“, aber Begründung falsch (vergleicht mit dem Gaspreis) | „keine Angaben“, obwohl 03 und 06 unter den Top-5 waren | nicht gelaufen |
| N1 | ehrlich („keine Informationen“) | ehrlich („keine Angaben“) | nicht gelaufen |

- **Wichtigster Befund (ISS-041):** Alle drei B0-Aufrufe melden genau 4.098 Prompt-Token. Das Journal bestätigt: Der B0-Prompt hatte real 8.424 Token (geschätzt ca. 7.200), Ollama kürzte ihn auf die letzten ca. 4.096 Token. Die B0-Antworten kannten deshalb nur Datei 06/07. Der B0-Teil dieses Laufs ist nicht verwertbar. Messung mit `scripts/probe_context.py` (`context-probe.json`): 1.912 / 3.787 / 7.537 Token kamen ungekürzt an, Zeile 0 jedes Mal richtig, `context_length` 8192; Prefill 19,7 / 17,8 / 15,0 Token/s (bei langem Prompt langsamer). Ursache war also die Schätzung Zeichen/3, nicht `num_ctx`; neu 2,4 Zeichen/Token.
- **Abbruch-Ursache (ISS-043):** Kernel-OOM-Kill von `ollama.service` um 23:37 (`ollama-journal.txt`). Gegenmaßnahme: Modelle vor jeder Variante entladen.
- **P1:** Die Suche mit der ganzen Frage findet für S2 den Vertrag nicht (Top-5: Preisanpassungen 03/09 und Rechnung 04); für G1 waren die richtigen Dokumente dabei, das Modell antwortete trotzdem „keine Angaben“. P1 rät nie, beantwortet aber auch nichts: 2 von 3 Antworten „keine Angaben“.
- **Metrik-Korrekturen nach dem Lesen:** B0/N1 („Ich habe keine Informationen …“) wurde zuerst nicht als ehrliche Lücke erkannt, B0/G1 nicht als „nein“ (Schluss im letzten Satz). Beides angepasst (ISS-038); B0/G1 zählt jetzt als „Fehler erkannt“, obwohl die Begründung falsch ist: Das Urteil allein ist kein Beleg für eine richtige Prüfung.
- **Grenzen der Messung:** 3 Fragen, ein Lauf, P2 nur 1 Frage, B0 vermutlich abgeschnitten.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** RUN-007 bleibt als dokumentierter Fehlschlag stehen; Wiederholung mit korrigierter Schätzung und Entladen zwischen den Varianten als RUN-008.

### RUN-008 – Testmodul M6a, Probelauf B0/P1/P2 nach Korrekturen (3 Fragen, `llama3.1:8b`)
- **Datum / Commit:** 2026-11-15 · Branch `feat/m6a-eval-harness`, Stand `docs: record context truncation and OOM findings (ISS-041, ISS-043)`
- **Varianten:** B0 (Volltext), P1 (Pipeline), P2 (Agent)
- **Konfiguration:** wie RUN-007, aber Token-Schätzung 2,4 Zeichen/Token (B0 mit Dateien 01–06, ca. 6.730 geschätzte, 6.604 gemeldete Token) und Entladen der Modelle vor jeder Variante; Befehl `uv run python -m audit_agent.evaluation generate --run-id run-008 --ids S2 G1 N1`
- **Dauer:** ca. 20 Minuten (09:14–09:34); B0 547 / 60 / 14 s, P1 27–73 s, P2 35–245 s
- **Rohdaten:** `data/eval/run-008/` (`report.md`, `scores.json`, `answers-*.jsonl`, `p2-*.jsonl`, `manifest.json`, `ollama-journal.txt`), `data/eval/run-008.log`

| Metrik | B0 | P1 | P2 |
|---|---|---|---|
| Richtig | 2/3 | 1/3 | 2/3 |
| Fakten gefunden | 3/5 | 0/5 | 2/5 |
| Erwartete Quellen zitiert | 3/3 | 0/3 | 0/3 |
| Negativfrage erkannt (N1) | ja | ja | ja |
| Fehler erkannt (G1, nur Urteil) | ja | nein | nein |
| Tool-Wahl korrekt | – | – | 2/3 |
| Suchen mit eigenem Filter / schließen Quelle aus | – | – | 4 / 2 |

- **Technik:** Keine Kürzung (`truncated = 0` in allen Aufrufen), kein OOM-Kill (ISS-041, ISS-043). B0 nutzt den Prompt-Cache: erste Frage 430 s Prefill, die beiden folgenden 12 s und 7 s bei gleich gemeldeten ca. 6.600 Token (ISS-005: Wiederverwendung für B0 belegt; `prompt_eval_count` zählt gecachte Token mit).
- **S2:** B0 und P2 richtig (34,80 ct/kWh, 11,50 EUR brutto). B0 zitiert [1] und nennt zusätzlich die Preise ab 2025 aus der Preisanpassung [3]. P2 zitiert wieder keine Belegnummer (wie RUN-006), deshalb Recall 0. P1 findet den Vertrag mit der ganzen Frage als Suchanfrage nicht unter den Top-5 und antwortet „keine Angaben“.
- **G1:** Keine Variante vollständig richtig. B0 urteilt „nicht angewendet“ und nennt 39,50 ct/kWh richtig, aber den angekündigten Preis falsch (32,10 statt 38,20) und keine Differenz. P1 antwortet „keine Angaben“, obwohl Preisanpassung 03 und Rechnung 06 unter den Top-5 waren. P2 wiederholt das Muster aus RUN-006: zweimal `search_documents` mit `bill`/2025 (schließt die Preisanpassung 03 aus) und eine Antwort über den Abschlag statt über den Arbeitspreis (ISS-036).
- **N1:** alle drei ehrlich.
- **Grenzen der Messung:** 3 Fragen, ein Lauf, ein Modell; B0 sieht nur Stromdokumente (begünstigt bei S2, G1, ISS-039); „Fehler erkannt“ misst nur das Urteil (ISS-038, ISS-040).
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Das Testmodul läuft stabil. M6b: alle 12 Fragen mit `llama3.1:8b` und `qwen2.5:7b` (über Nacht), dann Gegenmaßnahmen messen (Filter durch Code, gemeinsames Suchwerkzeug, Zitierpflicht für P2) und RAGAS. Auffällig für die Auswertung: P1 antwortet bei vorhandenen Belegen „keine Angaben“ (2 von 3), B0 ist bei Stromfragen konkurrenzfähig, solange alles in den Kontext passt.

### RUN-009 – M6b, Probelauf neue Prüffragen G3/G4 und erster RAGAS-Lauf (`llama3.1:8b`, Bewerter `audit-judge`)
- **Datum / Commit:** 2026-11-15 · Branch `feat/m6b-ragas-catalog`, Stand `docs: record RAGAS judge (ADR-0012), questions G3/G4 and ISS-044 to ISS-046`
- **Varianten:** B0 (Volltext), P1 (Pipeline), P2 (Agent); danach RAGAS Faithfulness und Context Recall
- **Konfiguration:** Antwortmodell `llama3.1:8b`, `num_ctx` 8192, B0 mit Dateien 01–06 (ca. 6.730 Token); Bewerter `audit-judge` (= `qwen2.5:7b`, `num_ctx` 8192, Temperatur 0), `max_tokens` 1024; Befehle `generate --run-id run-009 --ids G3 G4` und `ragas --run-id run-009`
- **Dauer:** ca. 47 Minuten (10:00–10:47): Antworten ca. 25 min (B0 452 / 271 s, P1 173 / 71 s, P2 263 / 72 s), RAGAS ca. 23 min für 4 bewertbare Antworten (70–190 s je Metrik, ein Abbruch nach 499 s)
- **Rohdaten:** `data/eval/run-009/` (`report.md`, `scores.json`, `ragas.jsonl`, `answers-*.jsonl`, `p2-*.jsonl`, `manifest.json`, `ollama-journal.txt`), `data/eval/run-009.log`

| Metrik | B0 | P1 | P2 |
|---|---|---|---|
| Richtig | 0/2 | 0/2 | 0/2 |
| Fakten gefunden | 0/6 | 0/6 | 0/6 |
| Fehler erkannt (E2, E3) | 0/2 | 0/2 | 0/2 |
| Suchen mit eigenem Filter / schließen Quelle aus | – | – | 3 / 3 |
| RAGAS Faithfulness | zu lang (2) | 0,57 (1 von 2, 1 Fehler) | 1,00 (2 von 2) |
| RAGAS Context Recall | zu lang (2) | 0,00 (2 von 2) | 0,00 (2 von 2) |

- **Technik:** Journal ohne Kürzung (`truncated = 0` in allen 54 Zeilen) und ohne OOM. `audit-judge` lieferte in 7 von 8 Aufrufen gültiges JSON; P1/G3 Faithfulness brach mit `IncompleteOutputException` ab (`max_tokens` 1024 zu klein für die lange Antwort, danach auf 2048 erhöht; ISS-047). B0 wurde wie erwartet nicht bewertet (geschätzt 9.100–10.300 Token, ISS-046).
- **G3 (Gas 2026, Fehler E2):** B0 „keine Angaben“ (Rechnung 29 nicht im Kontext, ISS-039). P1 liest den Rechnungsbetrag 1.367,99 EUR richtig, fällt aber kein Urteil. P2 urteilt „korrekt“ (Fehlurteil): Alle Suchen sind auf Gas/Rechnung/2026 gefiltert, die Abrechnung 2025 mit z-Zahl 0,9560 kommt nie in den Kontext.
- **G4 (Nebenkosten 2026, Fehler E3):** B0 rechnet mit einer Stromrechnung (falsches Dokument). P1 findet 7.470,00 und 1.963,28 EUR, verrechnet sie mit den Vorauszahlungen und antwortet „keine Angaben“. P2 sucht nur in Nebenkosten/2026 (Mietvertrag mit 78 m² ausgeschlossen) und addiert unpassende Beträge zu 859,26 EUR.
- **RAGAS-Deutung:** Faithfulness 1,00 bei P2 trotz falscher Antworten: Die Aussagen stehen in den Belegen bzw. in der Rechner-Beobachtung, richtig sind sie deshalb nicht. Context Recall 0,00 überall passt dazu, dass keine Variante das zweite Dokument (Vorjahr, Mietvertrag) im Kontext hatte; die Einzelurteile gibt RAGAS nicht aus (ISS-047).
- **Grenzen der Messung:** 2 Fragen, ein Lauf, ein Modell; RAGAS-Werte auf 1–2 Antworten je Zelle.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Der Ablauf funktioniert von der Antwort bis zum RAGAS-Report. Die neuen Prüffragen bestätigen ISS-007/036: Der selbst gesetzte Filter des Agenten schließt das Vergleichsdokument aus. Nachtläufe mit 14 Fragen: Antworten ca. 1,5–2 h je Modell, RAGAS ca. 2 h je Modell (28 Antworten P1/P2 à ca. 4,5 min, B0 wird übersprungen).

### RUN-010 / RUN-011 – M6b/M6c, Nachtläufe mit 14 Fragen (`llama3.1:8b` und `qwen2.5:7b`), RAGAS, Fehleranalyse
- **Datum / Commit:** 2026-11-15 · Code-Stand `f46e50e` (Merge `fix/ollama-oom-night-run`); von RUN-010 entstanden B0, P1 und P2 bis Z2 schon am Vormittag vor diesem Fix (Abbruch bei P2/Z3, ISS-043), der Rest im Nachtlauf
- **Varianten:** B0 (Volltext), P1 (Pipeline), P2 (Agent); danach RAGAS Faithfulness und Context Recall
- **Konfiguration:** Antwortmodell RUN-010 `llama3.1:8b`, RUN-011 `qwen2.5:7b`; `num_ctx` 8192, Temperatur 0; B0 mit Dateien 01–06 (ca. 6.730 von 6.961 Token); P1 Top-5 ohne Filter mit Boost; P2 höchstens 6 Werkzeugaufrufe; Entladen nach jeder P1/P2-Antwort; Bewerter `audit-judge` (= `qwen2.5:7b`), `max_tokens` 2048; alle 14 Fragen; Befehl `scripts/night_eval.sh`
- **Dauer:** Nachtlauf 13:32–22:06. Antworten RUN-010 71 min (B0 26, P1 13, P2 32), RUN-011 109 min (B0 21, P1 18, P2 69); RAGAS 2,7 h (RUN-010) und 4,0 h (RUN-011) für je 28 bewertbare Antworten
- **Rohdaten:** `data/eval/run-010/`, `data/eval/run-011/` (`report.md`, `scores.json`, `ragas.jsonl`, `answers-*.jsonl`, `p2-*.jsonl`, `manifest.json`, `evidence.json`), `data/eval/night-m6b.log`, `data/eval/night-m6b-journal.txt`

| Metrik | llama B0 | llama P1 | llama P2 | qwen B0 | qwen P1 | qwen P2 |
|---|---|---|---|---|---|---|
| Richtig laut Metrik (von 14) | 5 | 5 | 3 | 4 | 6 | 4 |
| Richtig nach Handprüfung (von 14) | 5 | 5 | 3 | 3 | 5 | 2 |
| Fakten gefunden (von 27) | 5 | 9 | 6 | 6 | 10 | 8 |
| Erwartete Quellen zitiert (von 18) | 7 | 7 | 2 | 3 | 8 | 6 |
| Negativfragen erkannt (von 2) | 2 | 2 | 1 | 2 | 2 | 1 |
| Fehler erkannt, nur Urteil (von 3) | 1 | 0 | 0 | 0 | 0 | 0 |
| Fehlalarme (von 3 richtigen Abrechnungen) | 0 | 0 | 1 | 0 | 0 | 0 |
| Tool-Wahl korrekt (von 14) | – | – | 7 | – | – | 5 |
| Suchen mit eigenem Filter / schließen Quelle aus | – | – | 19 / 9 | – | – | 19 / 9 |
| Ungültige Werkzeugaufrufe | – | – | 13 von 37 | – | – | 2 von 31 |
| Abbruch am Werkzeug-Limit | – | – | 3 | – | – | 0 |
| Sekunden je Frage (Mittel) | 113 | 56 | 136 | 90 | 78 | 298 |
| Prompt-Token je Frage (Mittel) | 6.608 | 891 | 5.624 | 7.699 | 975 | 10.515 |
| RAGAS Faithfulness (14 von 14 bewertet) | zu lang | 0,71 | 0,68 | zu lang | 0,74 | 0,69 |
| RAGAS Faithfulness ohne reine Lückenantworten | – | 0,86 (n = 8) | 0,66 (n = 13) | – | 0,82 (n = 9) | 0,64 (n = 12) |
| RAGAS Context Recall (12 von 14 bewertet) | zu lang | 0,33 | 0,50 | zu lang | 0,33 | 0,58 |

- **Technik:** Im Nachtlauf kein OOM-Kill und keine Kürzung (`truncated = 0` in allen 440 Journalzeilen). Der einzige `oom-kill` im Journal (12:28) liegt vor dem Fix „Entladen nach jeder Antwort“ und vor dem Start des Nachtlaufs (ISS-043). Kein RAGAS-Fehlschlag, B0 wie erwartet „zu lang“ (ISS-046).
- **Handprüfung der Metrik (alle 84 Antworten gelesen):** Vier Antworten zählen laut Metrik als richtig, ihre Begründung trägt aber nicht; alle stammen von `qwen2.5:7b` und enden auf „Ja“ (ISS-050):
  - B0/S5: rechnet mit dem Prognoseverbrauch 3.300 kWh statt 3.250 kWh, und die eigene Summe stimmt nicht (138,00 + 1.148,40 − 80,00 ergibt 1.206,40, nicht 1.189,00).
  - P1/S5: zieht nur die Abschläge vom Rechnungsbetrag ab; der Vertrag mit den Preisen war nicht unter den Treffern.
  - P2/S5: vergleicht nur den Grundpreis (11,50 × 12 = 138,00) mit der Rechnung selbst; der Vertrag wurde nie gesucht.
  - P2/G2: nennt alle drei Sollzahlen, rechnet aber „1.830,00 − 1.920,00 − 90,00 = −100,00“ und begründet das Ja mit einem Guthaben von 100 EUR.
  - Grenzfälle, nicht umgewertet: qwen B0/S2 nennt den Grundpreis als 138,00 EUR für 12 Monate statt 11,50 EUR/Monat (inhaltlich gleich, zählt als falsch); llama P1/Z1 nennt Volumen und Energiemenge richtig, aber nicht die z-Zahl (zählt als falsch).
  - `qwen2.5:7b` fällte in den drei Varianten 14 Urteile, alle „ja“; `llama3.1:8b` fällte nur 5 Urteile bei 18 Prüffragen-Antworten.
- **Fehleranalyse (61 falsche von 84 Antworten, je eine Hauptursache, von Hand zugeordnet):**

| Hauptursache | Bedeutung | B0 | P1 | P2 | Summe |
|---|---|---|---|---|---|
| Kontextbudget | Dokument oder Diagrammwert nicht im Volltext-Kontext (ISS-039) | 14 | – | – | 14 |
| Retrieval | erwarteter Beleg nicht unter den Top-5 | – | 12 | – | 12 |
| Tool-Wahl | Werkzeug durchsucht den Chunk-Typ mit dem Fakt nicht (ISS-006, ISS-052) | – | – | 8 | 8 |
| Filter | eigener Filter schließt das nötige Dokument aus (ISS-007) oder Suche ohne Filter liefert Ablenker (ISS-051) | – | – | 10 | 10 |
| Argumente | ungültige `calculate`-Aufrufe bis zum Limit (ISS-036) | – | – | 1 | 1 |
| Synthese | Beleg war im Kontext, Antwort trotzdem falsch | 6 | 6 | 4 | 16 |
| Parser | Fakt fehlt oder ist entstellt in den Chunks | 0 | 0 | 0 | 0 |

  - **B0:** 7 von 14 Fragen je Modell sind nicht beantwortbar: bei 6 fehlt das Dokument, weil nur die Stromdokumente 01–06 in den Kontext passen, bei S4 steht der Wert nur im Diagramm. B0 antwortet dort meist ehrlich „keine Angaben“. Bei G2 und G4 rechnet es stattdessen mit der Stromrechnung.
  - **P1:** Alle 7 reinen Lückenantworten auf beantwortbare Fragen (llama: S2, S4, S5, G1; qwen: S2, S4, G1) sind berechtigt: Die gesuchten Werte (bei S5 die Vertragspreise) standen nicht in den fünf Treffern (`evidence.json`). Bei G1 waren zwar beide Dokumente dabei, aber nicht die Zeilen mit 38,20 und 39,50 ct/kWh. Das korrigiert die Deutung aus RUN-007/008 (ISS-055). Für G3 und G4 fehlt das Vergleichsdokument (Abrechnung 2025, Mietvertrag); eine einzelne Suche mit der Frage holt es nicht. Synthesefehler: Z2 (beide nennen 115,00 EUR aus dem älteren Dokument, obwohl 120,00 EUR ab 15.02.2026 unter den Treffern stand), G2, Z1.
  - **P2:** 18 von 23 Fehlschlägen entstehen, bevor das Modell die Antwort schreibt. `search_documents` liefert nur Fließtext; Kündigungsfristen stehen aber in Tabellenzeilen (S1, Z3). Dort ist `search_documents` sogar das „erwartete“ Werkzeug (ISS-052). In beiden Läufen schließen 9 von 19 gefilterten Suchen eine erwartete Quelle aus: Bei S5, G1, G3 und G4 sucht der Agent nur in der Rechnung des gefragten Jahres und nie im Vertrag, in der Preisanpassung, in der Vorjahresabrechnung oder im Mietvertrag. `search_images` wird bei S4 nie gerufen, obwohl die Bildbeschreibung mit 3.480 und 3.390 kWh im Index steht.
  - **N2 (Fernwärme):** Beide Modelle filtern richtig auf `district_heating`, die Suche findet nichts und wiederholt sich ohne Filter. Zurück kommen Strom- und Gaspreise, und beide Modelle geben einen davon als Fernwärme-Grundpreis aus (ISS-051). B0 und P1 antworten hier richtig.
  - **Eingebaute Fehler:** E2 (G3) und E3 (G4) erkennt keine Variante; fünf Antworten nennen die fehlerhafte Abrechnung ausdrücklich „korrekt“ (llama P2/G3, qwen P1 und P2 je G3 und G4). Bei llama P1/G3 liest die Metrik fälschlich ein „ja“, die Antwort sagt „können wir nicht bestätigen“ (ISS-050). Die Abrechnungen sind in sich stimmig (1.060 m³ × 11,150 = 11.819 kWh), der Fehler zeigt sich erst im Vergleich mit einem zweiten Dokument. E1 (G1) erkennt nur llama B0 im Urteil, mit falschem Preis (32,10 statt 38,20 ct/kWh).
  - **Parser:** Kein Fehlschlag geht auf fehlende oder entstellte Chunks zurück. Auffällig ist aber, dass bei S1 und Z3 Grußformeln und Briefkopfzeilen als Treffer oben stehen, weil sie die Kapitelüberschrift „… Kündigungsfrist …“ tragen (ISS-027).
- **Modellvergleich P2:** `llama3.1:8b` ist gut doppelt so schnell (136 s gegen 298 s je Frage) und braucht halb so viele Prompt-Token. `qwen2.5:7b` ruft 10-mal `list_documents` (bei 9 von 14 Fragen, 7-mal ohne Filter und damit mit der ganzen Dokumentliste), macht kaum ungültige Aufrufe (2 gegen 13) und zitiert Belege (19 Zitate gegen 2). `llama3.1:8b` ruft `calculate` 13-mal, davon 11-mal mit ungültigen Argumenten (`input` oder `a` bis `e` statt `expression`, trotz Fehlermeldung mit dem richtigen Aufruf) und zweimal mit sinnlosen Summen; `qwen2.5:7b` ruft `calculate` nie und rechnet im Kopf, zum Teil falsch. Einmal erfand `qwen2.5:7b` ein Argument `toolbench_rapidapi_key` mit einer schlüsselähnlichen Zeichenkette (ISS-054).
- **RAGAS-Stichprobe (12 Antworten von Hand gegen die Belegtexte geprüft, 6 je Lauf):**
  - Nachvollziehbar: 9 von 12 Faithfulness-Werten. Erfundene Angaben bekommen 0,00 (llama P2/S1 „2 Monate zum Kalendervierteljahr“, llama P2/Z3 „14 Tage“, qwen P2/N2 Fernwärme). Belegte, aber falsche Antworten bekommen 1,00 (llama P2/G4 mit 859,26 EUR aus der eigenen Rechnung, qwen P2/G3 „korrekt“, qwen P2/Z2 mit dem alten Abschlag).
  - Nicht nachvollziehbar: llama P1/S4 (berechtigte Lückenantwort, 0,00), qwen P1/Z3 (Antwort fast wörtlich aus der Tabellenzeile, 0,50), qwen P2/Z3 (zitiert das Sonderkündigungsrecht wörtlich aus dem Beleg, 0,00).
  - Der Satz „Dazu liegen in den Unterlagen keine Angaben vor.“ allein erhält in 5 von 14 Fällen 0,00 und in 9 Fällen 1,00, ohne erkennbare Regel (ISS-053). Ohne diese Antworten liegt P1 bei 0,86 / 0,82 und P2 bei 0,66 / 0,64.
  - Context Recall: Bei Z3 ist der Wert genau verkehrt. P1 hat die Zeile „Kündigungsfrist: 1 Monat …“ im Kontext und bekommt 0,00 (beide Läufe); llama P2 hat sie nicht und bekommt 1,00. Insgesamt widersprechen 13 von 48 Werten dem Abgleich „alle Sollfakten im Kontext“ (`scripts/check_evidence.py`).
  - Ein Bonus für die eigenen Antworten des Bewerters ist nicht zu sehen (qwen-Lauf 0,74 / 0,69 gegen 0,71 / 0,68; ISS-045).
- **Grenzen der Messung:** 14 Fragen, ein Lauf je Modell, Temperatur 0 (keine Streuung gemessen); Unterschiede von ein bis zwei Fragen zwischen den Modellen sind nicht belastbar. Handprüfung und Ursachenzuordnung stammen von einer Person (Claude) und wurden nicht gegengelesen; je Antwort ist nur die Hauptursache gezählt, viele haben eine zweite. Der Abgleich „Fakt im Kontext“ nutzt dieselbe Zahlensuche wie die Metrik (ISS-050). B0 sieht nur Stromdokumente.
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:** Der Agent (P2) ist in beiden Läufen schlechter als die einfache Pipeline (P1), und die Ursache liegt überwiegend im Werkzeugentwurf, nicht im Modell. Gegenmaßnahmen für M6d, nach Zahl der betroffenen Fehlschläge: (1) Filter nicht mehr dem Modell überlassen bzw. bei Prüffragen Vergleichsdokumente mitsuchen (ISS-007, 10 Fälle); (2) ein Suchwerkzeug über Text und Tabellen (ISS-006/052, 8 Fälle); (3) bei leerer gefilterter Suche „keine Treffer“ melden statt ungefiltert zu wiederholen, wenn es die Sparte nicht gibt (ISS-051); (4) P1: mehr Treffer oder gezieltere Suchanfrage (12 Fälle). Agent-Modell: ADR-0013.

### RUN-012 – M6d, P2 mit den Gegenmaßnahmen (`llama3.1:8b`, 14 Fragen)
- **Datum / Commit:** 2026-11-16 · Branch `feat/p2-search-countermeasures`, Commit `feat(agent): merge text and table search, filter by utility type only, report empty searches`
- **Variante:** nur P2 (`generate --variants p2 --all`); B0 und P1 unverändert aus RUN-010
- **Konfiguration:** Antwortmodell `llama3.1:8b`, `num_ctx` 8192, Temperatur 0, höchstens 6 Werkzeugaufrufe; Werkzeuge nach ADR-0014 (`search` über Text und Tabellen, Filter nur Sparte, `include_counterpart`, keine Wiederholung ohne Filter); Katalog erwartet `search`; Befehl `uv run python -m audit_agent.evaluation generate --run-id run-012 --variants p2 --all --model llama3.1:8b`; danach `score` und `scripts/check_evidence.py`. Kein RAGAS-Lauf.
- **Dauer:** ca. 61 Minuten (RUN-010: 32)
- **Rohdaten:** `data/eval/run-012/` (`report.md`, `scores.json`, `answers-p2.jsonl`, `p2-*.jsonl`, `manifest.json`, `evidence.json`), `data/eval/run-012.log`

| Metrik (P2, llama3.1:8b) | RUN-010 | RUN-012 |
|---|---|---|
| Richtig laut Metrik (von 14) | 3 | 7 |
| Richtig nach Handprüfung (von 14) | 3 | 9 |
| Fakten gefunden (von 27) | 6 | 11 |
| Erwartete Quellen zitiert (von 18) | 2 | 3 |
| Negativfragen erkannt (von 2) | 1 | 2 |
| Fehler erkannt, nur Urteil (von 3) | 0 | 0 |
| Fehlalarme (von 3 richtigen Abrechnungen) | 1 | 1 |
| Tool-Wahl korrekt (von 14) | 7 | 7 |
| Ungültige Werkzeugaufrufe | 13 von 37 | 0 von 24 |
| Suchen mit eigenem Filter / schließen Quelle aus | 19 / 9 | 17 / 3 (nur Sparte) |
| Abbruch (Werkzeug- oder Kontextlimit) | 3 | 1 (Kontext, G1) |
| Sekunden je Frage (Mittel) | 136 | 263 |
| Prompt-Token je Frage (Mittel) | 5.624 | 5.582 |

- **Handprüfung (alle 14 Antworten gelesen):** Richtig sind S1, S2, S3, S4, N1, N2, Z1, Z2, Z3. Zwei davon zählt die Metrik als falsch: S2 nennt den Grundpreis als 138,00 EUR brutto pro Jahr statt 11,50 EUR/Monat (gleichwertig), Z1 nennt Volumen 1.200 m³ und das Ergebnis „passt“ richtig, aber nicht die z-Zahl (Grenzfall, hier als richtig gezählt). Falsch sind S5 (richtige Abrechnung als Abweichung gemeldet), G1 (Kontextlimit, keine Antwort), G2 (Antwort ohne Zahlen), G3 („korrekt“, Fehler E2 übersehen), G4 (falscher Betrag, E3 übersehen).
- **Ursachen der fünf Fehlschläge:** G1, G3, G4: Sollzahlen nie im Kontext (Retrieval/Suchanfrage; G1 wiederholt dieselbe Suche). G2: alle Sollzahlen im Kontext, Antwort ohne Zahlen (Synthese). S5: beide Quellen standen im Kontext, das Urteil ist falsch (Synthese, ohne `calculate`). In keiner Frage wurde `calculate` aufgerufen (ISS-058).
- **Deutung:** Die vier Gegenmaßnahmen beheben genau die Ursachen, die für sie beschrieben waren (ISS-051, ISS-052, ISS-006, ISS-007): S1, Z3, N2 kippen von falsch auf richtig, ungültige Aufrufe verschwinden. Die Prüffragen mit eingebauten Fehlern (G1, G3, G4) bleiben falsch; dafür braucht es Rechnen und einen festen Prüfablauf (ISS-058). Es ist ein einzelner Lauf bei Temperatur 0, die Streuung ist nicht gemessen; der Anstieg von 3 auf 9 stammt aus allen vier Maßnahmen zusammen und lässt sich nicht einzeln zuordnen. Die Laufzeit stieg stark ohne erklärende Veränderung der Token-Zahl (ISS-057).

### RUN-013 – M6e, P2 mit Wiederholungssperre und Rechennachfrage (`llama3.1:8b`, 14 Fragen)
- **Datum / Commit:** 2026-11-16 · Branch `feat/p2-audit-flow`, Commit `feat(agent): block repeated tool calls and ask for calculate on audit questions`
- **Variante:** nur P2 (`generate --variants p2 --all`); gleiche Fragen, gleiches Modell wie RUN-012
- **Konfiguration:** wie RUN-012, dazu ADR-0015 (vorgeschlagen): identische Aufrufe werden nicht ausgeführt, Prüffrage ohne `calculate` wird einmal nachgefragt, Prompt um 263 Zeichen länger (je Prüfgröße getrennt nach Soll- und Istwert suchen); Befehl `uv run python -m audit_agent.evaluation generate --run-id run-013 --variants p2 --all --model llama3.1:8b`, danach `score`, `scripts/check_evidence.py`, `scripts/analyze_timing.py`. Kein RAGAS-Lauf.
- **Dauer:** ca. 73 Minuten (RUN-012: 61)
- **Rohdaten:** `data/eval/run-013/` (`report.md`, `scores.json`, `answers-p2.jsonl`, `p2-*.jsonl`, `manifest.json`, `evidence.json`), `data/eval/run-013.log`, `run-013-env.txt` (Systemlast vor dem Lauf), `run-013-journal.txt` (Ollama-Journal)

| Metrik (P2, llama3.1:8b) | RUN-012 | RUN-013 |
|---|---|---|
| Richtig laut Metrik (von 14) | 7 | 5 |
| Richtig nach Handprüfung (von 14) | 9 | 6 |
| Fakten gefunden (von 27) | 11 | 7 |
| Erwartete Quellen zitiert (von 18) | 3 | 1 |
| Negativfragen erkannt (von 2) | 2 | 1 |
| Fehler erkannt, nur Urteil (von 3) | 0 | 2 laut Metrik, von Hand 0 (siehe unten) |
| Fehlalarme (von 3 richtigen Abrechnungen) | 1 | 0 (S5 ohne Urteil) |
| Gültige `calculate`-Aufrufe | 0 | 0 (2 Versuche, beide ungültig) |
| Rechennachfragen / danach `calculate` | – | 4 (G3, G4, S5, Z1) / 0 gültig |
| Wiederholungen blockiert | – | 4 (G1, G2, N1, Z1) |
| Ungültige Werkzeugaufrufe | 0 von 24 | 2 von 35 (beide `calculate`, G4) |
| Suchen mit eigenem Filter / schließen Quelle aus | 17 / 3 | 23 / 5 |
| Abbruch (Werkzeug- oder Kontextlimit) | 1 (Kontext, G1) | 1 (Werkzeuglimit, G4) |
| Modellaufrufe / Werkzeugaufrufe | 44 / 24 | 59 / 35 |
| Sekunden je Frage (Mittel) | 263 | 314 |
| Prompt-Token je Frage (Mittel) | 5.582 | 8.536 |

- **Handprüfung (alle 14 Antworten gelesen):** Richtig sind S1, S3, N1, Z1 (Grenzfall wie in RUN-012: Ergebnis „passt“ richtig, z-Zahl fehlt), Z2, Z3. Falsch: S2 (Preise netto statt brutto angegeben; die Nettowerte 29,24 ct/kWh und 115,97 EUR/Jahr sind rechnerisch richtig, ein zweiter Grundpreis „ab 2025“ steht dazu), S4 (Lückenantwort, in RUN-012 richtig), S5 (die Antwort besteht aus einem Werkzeugaufruf als Text, ISS-061), G1 und G2 (Lückenantwort), G3 (Urteil „stimmt nicht“, aber die Begründung ist Unsinn: „1.367,99 − 1.367,99 = 1,00 EUR niedriger als 192,00 EUR“; keine der Sollzahlen), G4 (Werkzeuglimit nach zwei ungültigen `calculate`-Aufrufen, genannter Sollwert falsch), N2 (Fernwärme-Grundpreis aus einem Ablenker genannt: das Modell ließ im zweiten Versuch den Sparten-Filter selbst weg, ISS-051 durch das Modell statt durch den Code).
- **Was die neuen Maßnahmen taten:** Die Wiederholungssperre griff viermal wie vorgesehen (Observation 191 Zeichen statt je 1.500 bis 3.000). Die Rechennachfrage kam viermal, G4 rechnete danach zweimal mit erfundenen Argumenten (`a`, `b` statt `expression`), G3, S5 und Z1 suchten weiter oder erzählten. Kein gültiger `calculate`-Aufruf, keine erkannten Fehler mit tragfähiger Begründung.
- **Laufzeit (`scripts/analyze_timing.py`):** Erste Modellanfrage je Frage 1.286 s (RUN-012) gegen 1.379 s (RUN-013), in beiden Läufen 0 von 14 aus dem Prompt-Cache; spätere Aufrufe 1.602 s gegen 2.147 s bei 54.071 gegen 94.313 Prompt-Token; Dekodieren 610 s gegen 722 s. Das Ollama-Journal zeigt 28 Ladevorgänge (je 14 für Chat- und Embedding-Modell): Die Auswertung entlädt beide Modelle nach jeder Frage (`unloads_after_each_question`, Commit `92fed4d`, ISS-043) und mit ihnen den Prompt-Cache. Damit beginnt jede Frage mit kaltem Cache; das erklärt die langsame erste Anfrage in RUN-012 und RUN-013. Warum RUN-010 trotz demselben Code meist aus dem Cache startete, ist nicht geklärt, der Zeitvergleich mit RUN-010 ist deshalb nicht belastbar (ISS-057).
- **Deutung:** Die Maßnahmen von M6e haben das Ziel (Rechnen und Fehler erkennen) bei `llama3.1:8b` nicht erreicht, und der Lauf ist nach Handprüfung schlechter als RUN-012 (6 gegen 9). Ob die Rückschritte bei S2, S4 und N2 von den Änderungen kommen oder Streuung sind, ist nicht bekannt: Temperatur 0, aber der Prompt ist ein anderer, ein Wiederholungslauf mit unverändertem Code wurde nicht gemacht (ISS-062). Gesichert ist nur: Die Wiederholungssperre funktioniert mechanisch, die Rechennachfrage bewirkt bei diesem Modell nichts, und Prüffragen ohne festen Ablauf bleiben ungelöst (ISS-058, ADR-0015).

### RUN-014 – M6f, P2 mit `qwen2.5:7b` (Gegenprobe, 14 Fragen)
- **Datum / Commit:** 2026-11-16 · Branch `feat/p2-format-tolerance`, Commit `feat(scripts): add wrapper for P2 evaluation runs` (davor `feat(agent): run tool calls written as text and block repeated failed calls`, `feat(agent): accept operands and German thousands separators in calculate`)
- **Variante:** nur P2; Antwortmodell `qwen2.5:7b` (ADR-0013: Gegenprobe nach den Gegenmaßnahmen), sonst Code und Prompt wie RUN-015
- **Konfiguration:** `num_ctx` 8192, Temperatur 0; Aufruf über `scripts/eval_run.sh` (generate, score, `check_evidence.py`, `analyze_timing.py`, Ollama-Journal); Systemlast vor dem Lauf in `run-014-env.txt`
- **Dauer:** 70 min (4.208 s)
- **Rohdaten:** `data/eval/run-014/`, `data/eval/run-014.log`, `run-014-env.txt`, `run-014-journal.txt`

### RUN-015 / RUN-016 – M6f, P2 mit `llama3.1:8b`, gleicher Code zweimal (Streuungsmessung, 14 Fragen)
- **Datum / Commit:** 2026-11-16 · gleicher Stand wie RUN-014
- **Variante:** nur P2; `llama3.1:8b`; RUN-016 ist die unveränderte Wiederholung von RUN-015 (ISS-062)
- **Dauer:** 76 min (4.543 s) und 75 min (4.476 s)
- **Rohdaten:** `data/eval/run-015/`, `data/eval/run-016/` und je `.log`, `-env.txt`, `-journal.txt`

| Metrik (P2) | RUN-013 llama (M6e-Code) | RUN-014 qwen | RUN-015 = RUN-016 llama |
|---|---|---|---|
| Richtig laut Metrik (von 14) | 5 | 4 | 5 |
| Richtig nach Handprüfung (von 14) | 6 | 6 | 6 |
| Fakten gefunden (von 27) | 7 | 9 | 8 |
| Erwartete Quellen zitiert (von 18) | 1 | 6 | 1 |
| Negativfragen erkannt (von 2) | 1 | 2 | 1 |
| Fehler erkannt laut Metrik (von 3) | 2 | 2 | 2 |
| Fehler erkannt von Hand, tragfähige Begründung (von 3) | 0 | 1 (G4) | 0 (G3: Urteil richtig, Begründung Unsinn) |
| Fehlalarme bei richtigen Abrechnungen (von 3) von Hand | 0 | 2 (S5, G2) | 1 (S5) |
| Rechennachfragen | 4 | 4 (G2, G3, G4, S5) | 4 (G3, G4, S5, Z1) |
| Gültige `calculate`-Aufrufe | 0 (2 Versuche) | 3 von 3, alle nach Nachfrage | 1 von 2 (G4, sinnlose Rechnung) |
| Wiederholungen blockiert / Aufrufe als Text erkannt | 4 / – | 0 / 0 | 4 / 1 (S5) |
| Ungültige Werkzeugaufrufe | 2 von 35 | 1 von 25 | 1 von 36 |
| Suchen mit eigenem Filter / schließen Quelle aus | 23 / 5 | 11 / 0 | 24 / 5 |
| Abbruch | 1 (Werkzeuglimit, G4) | 1 (Kontext, S5) | 1 (Werkzeuglimit, G4) |
| Modellaufrufe | 59 | 47 | 60 |
| Sekunden je Frage (Mittel) | 314 | 301 | 325 / 320 |
| Prompt-Token je Frage (Mittel) | 8.536 | 9.371 | 8.819 |

- **Streuung (ISS-062):** RUN-015 und RUN-016 sind bis auf die Zeiten identisch: gleiche 60 Modellaufrufe, gleiche 2.908 erzeugte und 98.271 Prompt-Token, gleiche Antworttexte, gleiche Metrik. Die Zeit je Frage streut um 1,5 % (325 gegen 320 s). Bei gleichem Code, Temperatur 0 und demselben Rechner ist `llama3.1:8b` hier deterministisch; Unterschiede zwischen Läufen mit verschiedenem Code kommen also vom Code, nicht vom Zufall. Einschränkung: eine Wiederholung auf einem Rechner; Ollama-Version und Lastzustand blieben gleich.
- **Handprüfung RUN-015/016 (alle 14 Antworten gelesen):** Richtig sind S1, S3, N1, Z1 (Grenzfall: Ergebnis „passt“ und 1.200 m³ stimmen, die z-Zahl fehlt; wie in RUN-012/013 gezählt), Z2, Z3. Falsch: S2 (nur Nettopreise, dazu ein zweiter Grundpreis), S4 und G1, G2 (Lückenantwort), S5 (richtige Abrechnung als Abweichung gemeldet, 34,00 EUR ohne `calculate` gerechnet), G3 (Urteil „stimmt nicht“ richtig, Begründung Unsinn: „1,00 EUR (1.367,99 − 1.367,99)“; z-Zahl nie gefunden), G4 (Werkzeuglimit nach `calculate("1.963,28 - -1.920,00")`, Antwort 3.883,28 EUR), N2 (Fernwärme-Grundpreis aus einem Ablenker).
- **Handprüfung RUN-014 (qwen):** Richtig sind S1, S2 (brutto 34,80 ct/kWh und 138,00 EUR/Jahr = 11,50 EUR/Monat genannt, daneben die Nettowerte), G4 (Soll 1.867,50 EUR mit `calculate(7470 * 0.25)`, Ist 1.963,28 EUR, Abweichung 95,78 EUR; die Ursache 82 statt 78 m² wird nicht genannt), N1, N2, Z3. Falsch: S3 (Zählerstand 386 m³ statt Verbrauch 74 m³), S4 (Lückenantwort mit Teilangaben), S5 (Kontextlimit, Abweichung 1.074 EUR aus 1.189 − 115 gemeldet), G1 (Lücke), G2 (Sollwert 1.830 EUR richtig, Istwert 1.870 EUR falsch, daher „−40,00 EUR“ als Abweichung), G3 (kündigt Rechnung an, rechnet nicht, Ergebnis „stimmt“), Z1 (richtiges Ergebnis, aber widersprüchlich mit „keine Angaben“), Z2 (115 statt 120 EUR).
- **Was die Änderungen von M6f bewirkten (RUN-013 gegen RUN-015, gleiches Modell):** Aufruf als Text wird erkannt und ausgeführt (S5: dritte Suche), `calculate` akzeptiert deutsche Zahlen (G4: zweiter Aufruf gültig). Handrichtig bleibt bei 6, die Rückschritte S2/S4/N2 gegenüber RUN-012 bleiben: Sie stammen also nicht aus Streuung, sondern aus dem Code oder Prompt von M6e (welche der drei Änderungen, ist nicht getrennt gemessen).
- **Rechennachfrage nach Modell:** Bei `qwen2.5:7b` folgt auf 3 von 4 Nachfragen ein gültiger `calculate`-Aufruf, bei `llama3.1:8b` auf 1 von 4 (und der ist sinnlos). Gültig heißt nicht richtig: In G2 und G4 (RUN-015) stimmen die Operanden nicht, G2 wird dadurch zum Fehlalarm. Der einzige sauber erkannte Fehler im ganzen Material ist G4 mit `qwen2.5:7b`.
- **Nicht gefunden:** G1 (neuer Arbeitspreis) und G3 (z-Zahl 1,0000) scheitern bei beiden Modellen daran, dass die Sollzahl nie im Kontext steht (Suchanfrage und Retrieval, ISS-051/052); Rechnen hilft dort nicht.
- **Laufzeit:** Die Zeit je Frage ist bei beiden Modellen nahezu gleich (301 gegen 320 bis 325 s), in beiden Läufen 0 von 14 ersten Anfragen aus dem Prompt-Cache (ISS-057). Das Ollama-Journal zeigt in keinem der drei Läufe Speichermangel; „truncated = 0“ in allen Anfragen, der Kontext von 8.192 Token reichte außer bei S5 (qwen).
- **Deutung:** Nach Handprüfung liegen beide Modelle gleichauf (6 von 14), mit verschiedenen Stärken: `qwen2.5:7b` zitiert besser (6 gegen 1 von 18), befolgt die Rechennachfrage und erkennt G4, meldet aber auch richtige Abrechnungen als Abweichung; `llama3.1:8b` hält Format und Filter schlechter und rechnet nicht. Ein Lauf je Modell und 14 Fragen sind eine dünne Basis; die Handprüfung ist von einer Person (Claude) gemacht und nicht gegengelesen.

### RUN-017 – M6g, P2 mit festem Prüfablauf und `qwen2.5:7b` (14 Fragen)
- **Datum / Commit:** 2026-11-16 · Branch `feat/p2-audit-flow-decision`, Commit `feat(agent): add fixed audit flow for check questions and switch default model to qwen2.5:7b`
- **Variante:** nur P2; Antwortmodell `qwen2.5:7b`; gegenüber RUN-014 neu: Prüfablauf (ADR-0016) für die 6 Prüffragen G1 bis G4, S5, Z1
- **Konfiguration:** `num_ctx` 8192, Temperatur 0, `audit_max_checks` 3; Aufruf über `scripts/eval_run.sh run-017:qwen2.5:7b`; Systemlast in `run-017-env.txt`
- **Dauer:** 89 min (5.338 s); Journal ohne Abschneiden (`truncated = 0`), 70 Modellaufrufe
- **Rohdaten:** `data/eval/run-017/`, `data/eval/run-017.log`, `run-017-env.txt`, `run-017-journal.txt`

| Metrik (P2) | RUN-014 qwen (ohne Ablauf) | RUN-017 qwen (mit Ablauf) |
|---|---|---|
| Richtig laut Metrik (von 14) | 4 | 4 |
| Richtig nach Handprüfung (von 14) | 6 | 6 (S1, S2, N1, N2, Z1, Z3) |
| Fakten gefunden (von 27) | 9 | 7 |
| Erwartete Quellen zitiert (von 18) | 6 | 6 |
| Fehler erkannt von Hand, tragfähige Begründung (von 3) | 1 (G4) | 0 |
| Fehlalarme bei richtigen Abrechnungen (von 3) von Hand | 2 (S5, G2) | 0 (aber S5 in chinesischer Sprache, G2 Unsinn) |
| Sekunden je Frage (Mittel) | 301 | 382 |
| Prompt-Token je Frage (Mittel) | 9.371 | 11.983 |
| Abbruch durch Werkzeuglimit | 0 | 1 (G3, 1.291 s) |

- **Prüfablauf in Zahlen:** 6 Prüffragen, 14 geplante Prüfgrößen: 4 Abweichung, 3 gleich, 4 nicht gefunden, 3 nicht belegt. In 4 Prüfgrößen stammen Soll- und Istzahl aus demselben Treffer. 33 Aufrufe des Ablaufs, 1.494 s (25 min) nur im Ablauf, je Prüffrage 113 bis 336 s zusätzlich.
- **Handprüfung der sechs Prüffragen:** G1: Urteil „Abweichung“ stimmt zufällig, die Begründung ist falsch (Gas-Rechnungsbetrag 1.555,43 EUR gegen Strom-Rechnungsbetrag 1.379,30 EUR, −176,13 EUR; Prüfgröße war „Arbeitspreis“). G2: Unsinn (Verbrauch und „z-Zahl“ einer Stromabrechnung, nichts zu Betriebskosten). G3: Ablauf liest z-Zahl 1,0000 auf beiden Seiten aus demselben Treffer, danach „keine Angaben“, die freie Schleife endet im Werkzeuglimit mit „7,01 EUR Abweichung“ (falsch). G4: sagt „korrekt“, rechnet 11.819 kWh × 13,45 EUR/1.000 kWh; die Wohnflächenabweichung wird nicht gefunden (RUN-014 fand sie). S5: Urteil „stimmt“ richtig, Antwort chinesisch mit erfundenem Stückpreis „1 EUR/kWh“. Z1: Urteil „passt“ und 1.200 m³ richtig, Text widersprüchlich (Soll gleich Ist aus demselben Wert).
- **Deutung:** Der Prüfablauf bringt in dieser Form keinen Gewinn: gleiche Handpunktzahl (6 von 14) bei 27 % mehr Zeit, G4 geht verloren, und es entstehen neue Fehlerarten (ISS-070, ISS-071). Gut ist nur, dass die Zahlen nachweislich aus Treffern stammen und der Code rechnet; die Treffer sind aber meist die falschen. Die Bedingung aus ADR-0016, den Ablauf zu bestätigen, ist nicht erfüllt.

### RUN-018 / RUN-019 – M6h, Größen-Anfrage und Zitier-Rückfrage (P2 und P1, `qwen2.5:7b`, 14 Fragen)
- **Datum / Commit:** 2026-11-17 · Branch `feat/m6h-retrieval`, Commit `docs: add ADR-0017, ISS-072 to ISS-075, glossary and concept note for M6h`
- **Variante:** RUN-018 nur P2 (Vergleich RUN-014), RUN-019 nur P1 (Vergleich RUN-011); gleiche Fragen und gleiches Modell; neu gegenüber RUN-014/011: Größen-Anfrage mit bis zu 2 neuen Treffern (P1 und P2, ADR-0017), Gegenstück-Suche mit der Größen-Anfrage, Zitier-Rückfrage (nur P2), Einheitenfaktor der Metrik nur für ct und EUR
- **Konfiguration:** `num_ctx` 8192, Temperatur 0, `quantity_hits` 2, `require_citation` an; Aufruf `scripts/eval_run.sh run-018:qwen2.5:7b`, danach `generate --run-id run-019 --variants p1 --all`, `score`, `scripts/check_evidence.py`
- **Dauer:** RUN-018 63 min (3.773 s; RUN-014: 70 min), RUN-019 ca. 21 min (92 s je Frage)
- **Rohdaten:** `data/eval/run-018/`, `data/eval/run-019/`, `run-018.log`, `run-018-env.txt`, `run-018-journal.txt`, `run-019-journal.txt`

| Metrik | RUN-014 P2 | RUN-018 P2 | RUN-011 P1 | RUN-019 P1 |
|---|---|---|---|---|
| Richtig laut Metrik (von 14) | 4 | 4 | 6 | 5 |
| Richtig nach Handprüfung (von 14) | 6 | 6 | – | – |
| Fakten in der Antwort (von 27) | 9 | 8 | 10 | 9 |
| Fakten im Kontext (von 27) | 17 | 18 | 13 | 13 |
| Erwartete Quellen zitiert (von 18) | 6 | 8 | 8 | 7 |
| Antworten mit Zahlen und `[n]` | 5 von 9 | 9 von 9 | 9 von 9 | 7 von 8 |
| Fehler erkannt von Hand mit tragfähiger Begründung (von 3) | 1 (G4) | 0 | 0 | 0 |
| Sekunden je Frage (Mittel) | 301 | 270 | – | 92 |
| Prompt-Token je Frage (Mittel) | 9.371 | 9.863 | – | 1.233 |

- **Nachbewertung:** Die geänderte Metrik (Einheitenfaktor) ändert in RUN-010 bis RUN-017 keine einzige Bewertung; die Läufe bleiben vergleichbar.
- **Handprüfung RUN-018 (alle 14 Antworten gelesen):** Richtig sind S1, S2 (brutto 34,80 ct/kWh und 138,00 EUR/Jahr genannt, daneben Netto- und 2025-Werte; wie RUN-014), N1, N2, Z1 (Grenzfall: „passt“ und 1.200 m³ stimmen, z-Zahl fehlt), Z3 (Satz fehlerhaft, Frist 1 Monat stimmt). Falsch: S3 (Zählerstand 386 m³ statt Verbrauch 74 m³), S4 und S5 (Lückenantwort), G1 (leere Antwort nach der Rechennachfrage, `stop_reason=empty_answer`; vor der Rückfrage stand „angewendet“ mit 38,20 ct), G2 (Istwert −1.920 EUR als Abweichung −90 EUR gemeldet), G3 („stimmt sehr gut überein“, nur der Abschlag verglichen, danach JSON-Reste), G4 (Sollwert 1.830 EUR statt 1.867,50 EUR, Abweichung 133,28 EUR; RUN-014 war richtig), Z2 (115,00 statt 120,00 EUR).
- **Wirkung der Größen-Anfrage:** Sie greift in 13 von 16 Suchen (11 von 14 Fragen) und ist bei P2/G1 der einzige Grund, dass die Preisanpassung mit 38,20 ct im Kontext steht (Treffer [6]); der Gewinn von 0 auf 2 Fakten in G1 wird durch die falsche Antwort nicht genutzt. Bei P1 bleiben 13 von 27 Sollzahlen im Kontext: In 7 von 14 Fragen kamen 2 Treffer dazu, die Antwort änderte sich in S1, S5, G2, G4, Z1, Z2, Z3 (Wortlaut), inhaltlich nur in S5 (RUN-011 „Ja, stimmt“, jetzt Fehlalarm mit 68,00 EUR). Ursache für P1/G1: Die Größen-Anfrage „Arbeitspreis“ hat keine Sparte; die Kapitelüberschrift des Gas-Preisschreibens („Gas-Arbeitspreises“) trifft sie und den Hierarchie-Boost, die Strom-Zeile mit 38,20 ct kommt nicht (ISS-077). Der Rückgang bei G4 im Kontext (2 auf 1 von 3) stammt nicht aus der Suche, sondern aus der fehlenden Rechnung 7470 × 0,25 (der Wert steht nur in einer `calculate`-Antwort).
- **Wirkung der Zitier-Rückfrage:** 4 Rückfragen (S1, S3, G3, Z3), alle führten zu einer Antwort mit Treffernummer; 9 von 9 Antworten mit Zahlen tragen jetzt `[n]` (RUN-014: 5 von 9), erwartete Quellen zitiert 8 statt 6 von 18. Keine Antwort wurde dadurch inhaltlich schlechter oder besser (S3 und Z3 bleiben wie sie waren).
- **Weitere Rückfragen und Abbrüche:** 4 Lückenrückfragen (S4, S5, N1, N2), 5 Rechennachfragen (G1, G2, G3, G4, Z1), dazu die 4 Zitier-Rückfragen; 0 Abbrüche durch Werkzeug- oder Kontextlimit, 1 leere Antwort (G1, ISS-076).
- **Laufzeit:** 3.773 s gegen 4.207 s; das Ollama-Journal zeigt keine Kürzung. Die Zeit hängt weiter an der Ladepolitik (ISS-057), der Vergleich ist nur ein Hinweis, kein Beleg für Schnelligkeit.
- **Deutung:** Die Zitier-Rückfrage wirkt wie beabsichtigt (Belegbarkeit), ohne die Genauigkeit zu ändern. Die Größen-Anfrage bringt im Mittel keinen messbaren Gewinn: Sie holt bei P2/G1 die fehlende Zeile, aber das Modell nutzt sie nicht (keine Rechnung, leere Antwort), und bei P1 verfehlt sie die Strom-Zeile, weil die Sparte fehlt. Nach Handprüfung bleibt P2 bei 6 von 14, die eingebauten Fehler (G1, G3, G4) erkennt keine Variante. Einzelne Läufe bei Temperatur 0, Streuung nicht gemessen.


### RUN-020 / RUN-021 – M6i, Sparte in der Größen-Anfrage (P1 und P2, `qwen2.5:7b`, 14 Fragen)
- **Datum / Commit:** 2026-11-17 · Branch `feat/m6i-quantity-utility`, Commit `feat(retrieval): filter the quantity search by the utility the query names`
- **Variante:** RUN-020 nur P1 (Vergleich RUN-019), RUN-021 nur P2 (Vergleich RUN-018); gleiche Fragen, gleiches Modell, gleiche Einstellungen; neu: Größen- und Gegenstück-Suche filtern nach der Sparte, die die Anfrage nennt (ISS-077, ADR-0017 Nachtrag M6i)
- **Konfiguration:** `num_ctx` 8192, Temperatur 0, `quantity_hits` 2, `require_citation` an; Quality Gate auf dem Laptop vor dem Lauf (ISS-078); RUN-020 mit `generate --run-id run-020 --variants p1 --all`, `score`, `check_evidence.py`; RUN-021 mit `scripts/eval_run.sh run-021:qwen2.5:7b`
- **Dauer:** RUN-020 ca. 25 min (107 s je Frage); RUN-021 nach 11 Fragen um 13:59 ohne Meldung abgebrochen, Z1 bis Z3 nach Neustart des Laptops um 17:25 nachgeholt (ISS-079), zusammen ca. 72 min Rechenzeit
- **Rohdaten:** `data/eval/run-020/`, `data/eval/run-021/`, `run-020.log`, `run-020-env.txt`, `run-020-journal.txt`, `run-021.log` (nur Fortsetzung), `run-021-env.txt` (nur Fortsetzung), `run-021-journal.txt`

| Metrik | RUN-019 P1 | RUN-020 P1 | RUN-018 P2 | RUN-021 P2 |
|---|---|---|---|---|
| Richtig laut Metrik (von 14) | 5 | 6 | 4 | 4 |
| Richtig nach Handprüfung (von 14) | – | 8 (davon 2 Grenzfälle) | 6 | 6 |
| Fakten in der Antwort (von 27) | 9 | 12 | 8 | 8 |
| Fakten im Kontext (von 27) | 13 | 16 | 18 | 18 |
| Erwartete Quellen zitiert (von 18) | 7 | 9 | 8 | 8 |
| Ablenker im Kontext | 7 von 94 | 4 von 92 | 0 von 105 | 0 von 105 |
| Fehlalarme laut Metrik (von 3) | 1 (S5) | 0 | 1 | 1 |
| Fehler erkannt von Hand mit tragfähiger Begründung (von 3) | 0 | 0 | 0 | 0 |
| Sekunden je Frage (Mittel) | 92 | 107 | 270 | 308 |
| Prompt-Token je Frage (Mittel) | 1.233 | 1.207 | 9.863 | 9.647 |

- **Wo der Filter greift:** Nach `utility_in_query` nennen 8 der 14 Fragen genau eine Sparte (S1, S2, S5, G1, G3, N1, N2, Z3); eine Größen-Anfrage haben davon 6 (S1, S2, S5, G1, N2, Z3). Bei P1 wirkt er genau dort; bei P2 nur in einer Suche (S5, „Preis Vergleich“), weil der Agent die Sparte meist selbst setzt oder seine Anfragen keine nennen.
- **P1 je Frage:** G1 0 auf 2 von 3 Sollzahlen im Kontext (Treffer [6] Strom-Preisanpassung, [7] Strom-Abrechnung statt zweier Gas-Treffer); S2 0 auf 1 von 2 (Grundpreis-Zeilen der Strom-Preisanpassung statt Gas-Schreiben); S5 Internet- und Hausrat-Treffer ersetzt durch den Stromvertrag, Antwort wieder „Ja, stimmt“; N2 keine Fernwärme-Dokumente, die Zusatzsuche bringt nichts (5 statt 7 Treffer, alle Fremddokumente weniger); Z3 Strom-Abrechnungen statt Internet- und Gas-Vertrag, Antwort inhaltlich gleich.
- **Handprüfung RUN-020 (alle 14 Antworten gelesen):** Richtig sind S1, S3 (74 m³), S5, N1, N2, Z3; Grenzfälle G2 („korrekt“, 25 % von 7.320 EUR = 1.830 EUR, Guthaben 90 EUR fehlt) und Z1 („passt“, 1.200 m³, z-Zahl und kWh fehlen), gezählt wie Z1 in RUN-018. Falsch: S2 (nur Grundpreis), S4 (Lückenantwort), G1 („ja, angewendet“, vergleicht 39,50 ct mit dem alten Preis 34,80 ct statt mit 38,20 ct), G3 (rechnet nur die Energiemenge nach, kein Urteil), G4 („korrekt“, eingebauter Fehler nicht erkannt), Z2 (115,00 statt 120,00 EUR). Für RUN-019 gibt es keine Handprüfung; der Vergleich der Handzahl ist daher nur gegen die Metrik möglich.
- **Handprüfung RUN-021:** 13 von 14 Antworten wortgleich mit RUN-018 (Temperatur 0, gleicher Kontext); S5 hat einen anderen Kontext, bleibt aber eine Lückenantwort. Ergebnis wie RUN-018: 6 von 14, G1 wieder leer (ISS-076, keine unabhängige Wiederholung).
- **Laufzeit:** P1 +15 s je Frage gegen RUN-019 bei weniger Prompt-Token; P2-Zeiten sind wegen Abbruch und Neustart nicht vergleichbar (ISS-057, ISS-079).
- **Deutung:** Der Sparten-Filter behebt den Fehler aus M6h für P1: mehr Sollzahlen im Kontext, weniger Fremdtreffer, kein Fehlalarm bei S5. Für P2 ändert er nichts, weil der Agent die Sparte schon übergibt. Bei beiden Varianten liegt der Engpass jetzt beim Lesen und Vergleichen: G1 hat bei P1 und P2 die richtigen Zahlen im Kontext, beide Antworten sind falsch. G3 bleibt ein Retrieval-Problem (ISS-074). Einzelne Läufe, Streuung nicht gemessen.
