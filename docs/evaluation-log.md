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
