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
