# Entwicklungstagebuch

> Ein Eintrag pro Arbeitssitzung, neueste oben. Claude schreibt den Eintrag beim Sitzungsabschluss.
> **Das Feld „O-Ton“ kommt von mir:** 2–3 ungeschliffene Sätze, wie es lief, was genervt oder überrascht hat. Daraus wird in Phase 2 der persönliche Teil der Ausarbeitung (Reflexion, Vorgehen). Ohne O-Ton klingt der Text später generisch.

## Vorlage

```markdown
### YYYY-MM-DD – <Meilenstein / Arbeitspaket>
**Ziel der Sitzung:**
**Was wurde gemacht:**
-
**Gelieferte Dateien / Funktionen:**
-
**Entscheidungen:** (→ ADR-Nr.)
**Probleme / Überraschungen:** (→ ISS-Nr.)
**Offen / unklar:**
**O-Ton (von mir):**
**Zeitaufwand:** ca. … h · **Modell/Effort:** … · **Commit(s):**
```

---

## Einträge

### 2026-11-14 – M4: Embedding & Retrieval
**Ziel der Sitzung:** Aus den 629 Chunks einen ChromaDB-Index bauen und eine Suche mit Metadatenfilter und Hierarchie-Boost liefern, deren Score sich von Hand nachrechnen lässt; Wirkung von Filter, Boost und Chunk-Auswahl messen.
**Was wurde gemacht:**
- Plan mit sechs Punkten vorgelegt und bestätigt (kein Query-Rewriting in M4, Streamlit erst in M5)
- Paket `audit_agent.retrieval`: Index (Hierarchie-Präfix, Task-Präfixe, flache Metadaten, Neuaufbau je Lauf), Suche (Kandidaten, `where`-Filter, Pfadregel, Boost), Evidenz, Vergleichslauf, CLI; `RetrievalSettings` in der Config; `chromadb` als Abhängigkeit
- 39 Tests mit Fake-Embedder; dabei einen eigenen Fehler gefunden (Unterstrich als Wortzeichen, ISS-026)
- Index mit Ollama gebaut (86 s) und RUN-004 gefahren: Filter bringt 0 statt 4 Ablenker-Treffer und MRR 0,733 statt 0,683, der Boost ändert keinen Rang, Summaries helfen, Chunks ohne Kapitel stören nicht, S4 wird nicht gefunden
**Gelieferte Dateien / Funktionen:** `src/audit_agent/retrieval/{models,index,search,evidence,compare,__main__,__init__}.py`, `config.py` (`RetrievalSettings`), `tests/test_retrieval.py`, `docs/adr/0009-index-and-search-design.md`, `docs/reverse-engineering/m4-retrieval.md`, `data/eval/run-004/`
**Entscheidungen:** ADR-0009 (Aufbau von Index und Suche), ADR-0002 akzeptiert (Filter belegt, Boost ohne belegten Nutzen)
**Probleme / Überraschungen:** ISS-025 (Zeitraumfilter schließt Dokumente ohne Zeitraum aus), ISS-026 (eigener Fehler: Regex-Wortzeichen), ISS-027 (Boost greift fast überall), ISS-028 (Vergleich mit handgesetzten Filtern), ISS-029 (S4 nicht gefunden); im Plan stand 542 statt 547 Chunks, ein Rechenfehler von mir; überrascht hat, dass der Boost keinen Rang ändert, obwohl er fast jeden Treffer erreicht
**Offen / unklar:** Ob der Boost bleibt (ISS-027); wie oft der Agent falsche Filter setzt (ISS-028); Rang des S4-Bild-Chunks außerhalb der Top-5 unbekannt; Reverse-Engineering zu M2, M3 und M4 unbeantwortet
**O-Ton (von mir):** (ausstehend, wird nachgetragen; heute keine Zeit)
**Zeitaufwand:** ca. 1,2 h (Ollama-Lauf unter 2 min) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `build`, `feat(config)`, `feat(retrieval)`, `test(retrieval)`, `docs(adr)`, `docs` ×3, `docs: close M4 session`

### 2026-11-14 – M3: Enrichment & Cache
**Ziel der Sitzung:** Die fünf Diagramme beschreiben (Caption) und jede der 65 Tabellen zusammenfassen (`table_summary`), mit einem Cache, damit die langsame Anreicherung nur einmal läuft.
**Was wurde gemacht:**
- Plan mit Prompts, Cache-Schlüssel und Phasenreihenfolge vorgelegt und bestätigt
- Paket `audit_agent.enrichment`: Cache, Captioner, Summarizer, Zahlenprüfung, Pipeline, CLI; `numbers.py` aus dem Smoke-Test herausgelöst; Chunk-Typ `table_summary` und `EnrichmentSettings`
- RUN-002 (erster Lauf, 26 min) gegen die PNGs und Tabellen geprüft: ein Diagramm mit erfundenen Zahlen, 21 abgeschnittene und mehrere inhaltlich falsche Summaries
- Prompts und Limits angepasst, Abschneiden im Report markiert, Zahlenprüfung um Datumsteile erweitert; RUN-003 (26 min): nichts mehr abgeschnitten, keine erfundenen Caption-Zahlen, aber weiter Fehler bei Preistabellen und Briefkopf-Tabellen
- 24 Tests mit Ollama-Fake, Reverse-Engineering-Notiz M3 (Abschnitte 1–4)
**Gelieferte Dateien / Funktionen:** `src/audit_agent/enrichment/{cache,llm,prompts,captioner,summarizer,checks,pipeline,__main__,__init__}.py`, `src/audit_agent/numbers.py`, `config.py` (`EnrichmentSettings`), `ingestion/models.py` (`TABLE_SUMMARY`), `tests/test_enrichment.py`, `docs/adr/0008-enrichment-and-cache.md`, `docs/reverse-engineering/m3-enrichment.md`, `data/eval/run-002/`, `data/eval/run-003/`
**Entscheidungen:** ADR-0008 (Enrichment als eigener Schritt, Prompt-Text im Cache-Schlüssel, Summaries nur als Suchhilfe)
**Probleme / Überraschungen:** ISS-021 (Ingestion überschreibt Enrichment), ISS-022 (Zahlenprüfung nur Teilcheck), ISS-023 (Caption erfindet Werte ohne Beschriftung), ISS-024 (abgeschnittene Summaries, eigener Fehler: `done_reason` nicht ausgewertet); der erste Lauf hat erst durch die Sichtprüfung gezeigt, dass die Ergebnisse schlechter waren, als der Report vermuten ließ
**Offen / unklar:** Wirkung der Summaries und Briefkopf-Chunks aufs Retrieval (M4); Reverse-Engineering zu M0 bis M3 unbeantwortet
**O-Ton (von mir):** (ausstehend, wird nachgetragen; heute keine Zeit)
**Zeitaufwand:** ca. 1,3 h (davon 2 × 26 min Ollama-Lauf, parallel zur Doku) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `refactor(numbers)`, `feat(ingestion)`, `feat(enrichment)`, `fix(enrichment)`, `docs: …` ×3, `docs(reverse-engineering)`

### 2026-11-14 – M2: Parser & JSON-Zwischenformat
**Ziel der Sitzung:** Alle 30 PDFs in typisierte Chunks mit Metadaten umwandeln und als JSON-Zwischenformat unter `data/processed/` speichern.
**Was wurde gemacht:**
- Zuerst alle PDFs mit PyMuPDF untersucht (Tabellen je Strategie, Schriftgrößen, Bilder, Fußzeilen) und den Plan darauf abgestimmt
- Paket `audit_agent.ingestion`: Modelle, `DocumentParser`, Pipeline, CLI; `ParserSettings` in der zentralen Config
- Auf den echten PDFs drei Parser-Fehler gefunden und behoben: unvollständige Tabellen je Strategie (ISS-012), zerrissener Zelltext (ISS-013), verschmolzene Tabellen (ISS-014)
- 19 Parser-Tests (synthetische PDFs plus Golden-Checks auf Dok. 04, 10, 16, 29, 30) und 8 Tests für Modelle und Pipeline
- Doku: ADR-0007, ISS-012 bis ISS-020, RUN-001, Glossar, README, concept.md, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `src/audit_agent/ingestion/{models,parser,pipeline,__main__,__init__}.py`, `config.py` (`ParserSettings`), `tests/test_ingestion_*.py`, `docs/adr/0007-parser-heuristics.md`, `docs/reverse-engineering/m2-parser.md`
**Entscheidungen:** ADR-0007 (Parser-Heuristiken); Abweichung von der Vorlage: kurze Reste mit Ziffer bleiben erhalten (ISS-017)
**Probleme / Überraschungen:** ISS-012 bis ISS-020; die Unit-Tests allein hätten die Tabellenfehler nicht gefunden, erst der Blick in die echten JSON-Zeilen
**Offen / unklar:** Wirkung der Briefkopf-Chunks aufs Retrieval (M4); Reverse-Engineering zu M0, M1, M2 unbeantwortet
**O-Ton (von mir):** (ausstehend, wird nachgetragen)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(ingestion)` ×3, `refactor(ingestion)`, `docs: …M2`

### 2026-11-14 – M1: Metadaten & Ground Truth
**Ziel der Sitzung:** Metadaten und Ground Truth des Korpus als validierte Dateien bereitstellen und zwei weitere fehlerhafte Dokumente ergänzen.
**Was wurde gemacht:**
- Paket `audit_agent.corpus` mit Pydantic-Modellen und Loader (Fail Fast, `extra="forbid"`, Konsistenzprüfungen)
- `dataset/documents.yaml` für alle 30 PDFs, `dataset/ground_truth.yaml` mit 12 Fragen, 3 eingebauten Fehlern und 10 Prüfurteilen
- Zwei fehlerhafte Dokumente (29 Gas 2026: falsche z-Zahl, 30 Betriebskosten 2026: falsche Wohnfläche) per `scripts/generate_error_documents.py` mit WeasyPrint erzeugt und visuell geprüft
- 17 Tests ohne LLM (inklusive Prüfung, dass die Fehlerwerte im PDF-Text stehen); Quality Gate grün (57 Tests)
- Doku: Konzept 4.3 und 5.2, ADR-0005, Issues, Glossar, README, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `src/audit_agent/corpus/{models,loader}.py`, `dataset/{documents,ground_truth}.yaml`, PDFs 29 und 30, `tests/test_corpus.py`
**Entscheidungen:** Neue Sparten `telecom`, `insurance` und Dokumentarten `payment_plan`, `handover_protocol` im Metadatenschema; Fehlerdokumente für 2026 statt Duplikate (ISS-010)
**Probleme / Überraschungen:** ISS-010 (Zusatzdokumente anders als Originale, nur 3 Fehler), ISS-011 (Löschrecht für git zu spät angefragt)
**Offen / unklar:** Reverse-Engineering-Fragen zu M1 mit Antworten in `m1-fragen-und-antworten.md` hinterlegt (Nutzer hatte keine Zeit), Erklär-Test steht aus. Die erwarteten Urteile „korrekt“ für 08, 13, 15, 18, 19 stützen sich auf die Korpus-Prüfung vom Projektstart; Reverse-Engineering-Fragen zu M0 und M1 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, Nutzer hatte keine Zeit)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / Medium · **Commit(s):** `feat(dataset)`, `feat(corpus)`, `docs: …M1`

### 2026-11-14 – M0: Setup, Config, Smoke-Test
**Ziel der Sitzung:** Tooling aufsetzen, zentrale Konfiguration bauen und per Smoke-Test Geschwindigkeit, Tool-Calling, Embedding und Vision der lokalen Modelle messen.
**Was wurde gemacht:**
- `uv`-Projekt mit Python 3.13, `ruff`, `pytest` und Quality-Gate-Skript
- `Settings` und Modell-Preflight; Smoke-Test-Paket mit gefaktem Ollama-Client für Tests ohne LLM
- Smoke-Test vom Nutzer auf dem Laptop ausgeführt (RUN-000, ca. 6,5 Minuten), Ergebnisse ausgewertet
- Messfehler bei der Präfix-Wiederverwendung erkannt und die Messung auf Prefill-Zeit umgestellt
- Doku: ADR-0004 angenommen, ADR-0006 neu, Evaluationslog, Issues, Glossar, README, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `pyproject.toml`, `scripts/check.sh`, `src/audit_agent/{config,preflight}.py`, `src/audit_agent/smoke/*`, `tests/*`, `data/eval/run-000/*`
**Entscheidungen:** ADR-0004 (Agent-Modell vorläufig `llama3.1:8b`), ADR-0006 (natives Tool-Calling)
**Probleme / Überraschungen:** ISS-005 (ungültige Prefix-Messung), ISS-006 (Tool-Verwechslung), ISS-007 (ungefragte Filter), ISS-008 (Bilddaten falsch übergeben), ISS-009 (gemeinsames `.venv`)
**Offen / unklar:** Präfix-Cache belegen (M5); Reverse-Engineering-Fragen zu M0 unbeantwortet; Titelblatt-Angaben
**O-Ton (von mir):** (nicht geliefert, Nutzer hatte keine Zeit)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `chore(tooling)`, `feat(config)`, `feat(smoke)`, `fix(smoke)`, `docs(eval)`, `docs: …M0`

### 2026-11-14 – Vorbereitung II: Korpus-Prüfung, Vorlage, Git
**Ziel der Sitzung:** Vorhandene Testdokumente prüfen, LaTeX-Vorlage einbinden, Doku ins Repo bringen, Arbeitsweise auf „Claude führt selbst aus“ umstellen.
**Was wurde gemacht:**
- 28 synthetische PDFs ausgelesen, alle Beträge nachgerechnet, Diagramme angesehen
- Testkatalog (12 Fragen) mit erwarteten Antworten an den echten Korpus angepasst
- DHBW-LaTeX-Vorlage unter `paper/` eingebunden (nur Titelblatt, Inhaltsverzeichnis, Kapitel aktiv), Kapitelgerüst angelegt
- Git-Historie neu aufgeteilt (Initialisierung, Doku, Korpus, Vorlage); `.idea/` aus der Versionsverwaltung genommen
- Projektanweisungen für Claude neu gefasst (selbstständiges Arbeiten, Git ohne Claude-Hinweise)
**Gelieferte Dateien / Funktionen:** `docs/*` aktualisiert, `paper/`, `.gitignore`, ADR-0005
**Entscheidungen:** ADR-0005 (synthetischer Korpus) akzeptiert
**Probleme / Überraschungen:** ISS-002 (Ollama aus Claudes Shell nicht erreichbar), ISS-003 (kein Push durch Claude), ISS-004 (nur ein eingebauter Fehler)
**Offen / unklar:** weitere Fehler im Korpus? Titelblatt-Angaben; Agent-Modell
**O-Ton (von mir):**
**Zeitaufwand:** ca. … h · **Modell/Effort:** Opus 5.5 · **Commit(s):** siehe `git log`

### 2026-11-14 – Projektstart / Vorbereitung
**Ziel der Sitzung:** Anforderungen sammeln, Projektidee festlegen, Vorbereitung planen.
**Was wurde gemacht:**
- Anforderungen aus Folien und Professor-Hinweisen zusammengefasst (`requirements.md`)
- Projektidee „Energie- & Nebenkosten-Auditor“ ausgearbeitet (`concept.md`)
- Coding Standards, Doku-Struktur, Arbeitsweise mit Claude festgelegt
- Klärungen: selbst erzeugte Dokumente erlaubt, Ich-Form vermeiden
**Gelieferte Dateien / Funktionen:** Doku-Gerüst unter `docs/`, ADR-0001 bis 0004 (Entwürfe)
**Entscheidungen:** ADR-0001 (nur lokal) akzeptiert
**Probleme / Überraschungen:** ISS-001 (langsames Prefill)
**Offen / unklar:** Agent-Modell, Tool-Calling-Variante, Referenzprototyp als Basis?
**O-Ton (von mir):**

**Ausgangslage (für die Reflexion, kurz von mir ergänzen):**
- Was ich schon kann:
- Was ich noch nicht kann / wovor ich Respekt habe:
- Was ich erwarte (z. B. „Agent wird deutlich besser als Standard-RAG“):

**Zeitaufwand:** ca. … h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs: add project documentation scaffold`
