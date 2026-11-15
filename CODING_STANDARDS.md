Verbindliche Software-Design- & Engineering-Prinzipien

Dieses Dokument definiert die verbindlichen IT- und Software-Engineering-Standards für das Projekt `local-household-audit-agent`. Jede Architekturentscheidung, jede neue Datei und jedes Refactoring muss diesen Regeln entsprechen.

---

## 1. Code- & Software-Design-Prinzipien

- **Separation of Concerns (SoC):** Strikte Trennung zwischen Dokumenten-Ingestion/Parsing, Chunking/Enrichment, Retrieval-Logik, deterministischen Audit-/Rechen-Tools, Agenten-Orchestrierung und Benutzeroberfläche (CLI/UI). Änderungen an einer Schicht dürfen keine Seiteneffekte in anderen Schichten auslösen.
- **SOLID-Prinzipien (pragmatisch für Python umgesetzt):**
  - *Single Responsibility (SRP):* Jedes Modul, jede Klasse und jedes Agent-Tool hat genau eine klar abgegrenzte Aufgabe (z. B. getrennte Extraktoren für Fließtext, Tabellen und eingebettete Bilder).
  - *Open/Closed (OCP):* Neue Dokumenttypen, Parser-Strategien oder Agent-Tools lassen sich als neue Komponenten ergänzen, ohne die bestehende Agenten-Schleife umzuschreiben.
  - *Liskov Substitution (LSP):* Alle Implementierungen einer Schnittstelle (z. B. verschiedene Retriever oder LLM-Client-Wrapper) sind austauschbar, ohne das Verhalten der Aufrufer zu brechen.
  - *Interface Segregation (ISP):* Kleine, fokussierte Schnittstellen (`typing.Protocol` / abstrakte Basisklassen) und präzise Tool-Signaturen statt überladener Allzweck-Schnittstellen.
  - *Dependency Inversion (DIP):* Die Fachlogik hängt von Abstraktionen (z. B. `EmbeddingProvider`, `VectorStore`, `ChatModel`) ab, nicht direkt von konkreten Bibliotheks- oder HTTP-Aufrufen.
- **DRY (Don't Repeat Yourself):** Keine doppelte Logik und keine verstreuten Magic Values. Pfade, Modellnamen, Chunk-Parameter, RAM-Limits und Metadaten-Schemas werden an genau einer zentralen Stelle definiert („Single Source of Truth“).
- **KISS (Keep It Simple, Stupid):** Bevorzuge klare, lineare und direkt nachvollziehbare Python-Lösungen gegenüber unnötig komplexen Meta-Frameworks oder verschachtelten Abstraktionen.
- **YAGNI (You Aren't Gonna Need It):** Implementiere nur Funktionen, Tools und Abstraktionen, die konkret für den Haushalts-Audit-Use-Case, die Hardware-Grenzen und die Prüfungsanforderungen benötigt werden – keine spekulativen Erweiterungen auf Vorrat.
- **Composition over Inheritance:** Baue Pipelines (z. B. Ingestion-Schritte, Hybrid-Retriever, Tool-Registries) durch Komposition kleiner, wiederverwendbarer Komponenten statt über tiefe Vererbungshierarchien.
- **Law of Demeter (Principle of Least Knowledge):** Module kommunizieren ausschließlich über definierte Datenmodelle und direkte Schnittstellen (`DocumentChunk`, `AuditToolResult`) statt tief durch fremde Objektstrukturen zu navigieren (`a.get_b().get_c().run()`).
- **Fail Fast:** Validiere Eingaben, Konfigurationen, Datei-Integrität und Laufzeitvoraussetzungen (z. B. erreichbarer Ollama-Dienst, vorhandene Modelle, Speicherbudget) so früh und eindeutig wie möglich mit aussagekräftigen Fehlermeldungen.
- **Boy Scout Rule:** Hinterlasse jedes angefasste Modul, jeden Test und jede Dokumentation bei jeder Bearbeitung sauberer, klarer und besser typisiert als zuvor.

---

## 2. Git, Versionierung & Entwicklungsfluss

- **Conventional Commits (auf Englisch):** Jede Commit-Nachricht folgt dem standardisierten Präfix-Format (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`), z. B. `feat(ingestion): add structured table extraction for utility bills`.
- **Semantic Versioning (SemVer):** Projekt-Meilensteine werden sauber nach `MAJOR.MINOR.PATCH` getaggt (z. B. `v0.1.0` Ingestion-Pipeline, `v0.2.0` Agent & Tools, `v1.0.0` evaluierte Gesamtlösung).
- **Trunk-Based Development (TBD):** Kurze, fokussierte Arbeitspakete mit kleinen, atomaren Commits direkt auf `main` (oder extrem kurzlebigen Feature-Branches) statt langlaufender Parallel-Branches.

---

## 3. Architektur- & Systemprinzipien

- **Clean / Hexagonal Architecture (Ports & Adapters):** Die fachliche Kernlogik (Haushaltsdokumenten-Analyse, Retrieval-Scoring, Plausibilitäts- und Kostenberechnungen) bleibt vollständig unabhängig von technischen Außendetails wie PDF-Bibliotheken, Vektordatenbank, Ollama-API oder UI-Framework.
- **The Twelve-Factor App (relevante Faktoren):**
  - *Config:* Alle Pfade, Ollama-URLs, Modellnamen und Schwellenwerte sind über zentrale Konfigurationsdateien / Umgebungsvariablen steuerbar (keine hartkodierten Pfade im Fachcode).
  - *Backing Services:* Ollama und der lokale Vektorspeicher werden als austauschbare lokale Dienste angebunden.
  - *Build, Release, Run:* Strikte Trennung zwischen Offline-Indexierung (`ingest`) und interaktiver Abfrage-/Audit-Ausführung (`query` / UI).
  - *Logs:* Strukturierte, nachvollziehbare Protokollierung von Retrieval-Scores, Tool-Aufrufen, Latenzen und Speichernutzung.
- **Domain-Driven Design (Ubiquitous Language & Domain Models):** Einheitliche englische Fachbegriffe im gesamten Codebase (`UtilityBill`, `Contract`, `PriceAdjustment`, `MeterReading`, `CostLineItem`, `AuditFinding`) als stark typisierte Datenmodelle (Pydantic / Dataclasses).
- **Modular Monolith:** Eine einzige, lokal ausführbare Python-Anwendung (`src/`), intern streng in isolierte fachliche Module gegliedert (`ingestion`, `retrieval`, `tools`, `agent`, `evaluation`, `ui`).
- **Statelessness & Idempotenz:**
  - Die Ingestion-Pipeline muss **idempotent** sein: Mehrfaches Ausführen auf `dataset/` erzeugt denselben konsistenten Index ohne Duplikate.
  - Agent-Tools (Suche, Tabellenabfrage, Python-Rechner) arbeiten zustandslos und deterministisch.
- **CQRS (Command Query Responsibility Segregation):** Klare Trennung zwischen der schreibenden Indexierungs-Pipeline (Parsing, Vision-Enrichment, Embedding-Erzeugung) und der lesenden Abfrage-Pipeline (Hybrid Retrieval, Tool-Calling, Synthese) – auch zur strikten RAM-Trennung unter `MemoryMax=9G`.

---

## 4. Schnittstellen- & Datenrobustheit

- **Postel's Law (Robustness Principle):** „Sei konservativ in dem, was du sendest, und liberal in dem, was du akzeptierst.“
  - *Liberal beim Einlesen:* PDF-Parser und Agent-Tools tolerieren realistische Formatvarianten (z. B. deutsche Dezimalzahlen `1.234,56 €` vs. `1234.56`, unterschiedliche Datumsformate, leichte Abweichungen bei LLM-Tool-Parametern).
  - *Konservativ bei der Ausgabe:* Alle internen Komponenten und Tools liefern ausschließlich streng validierte, normalisierte Datenstrukturen mit expliziten Quellen- und Seitenangaben.

---

## 5. Testing- & Qualitätssicherungs-Konventionen

- **Testpyramide / Testing Trophy:**
  - *Breite Basis (Unit-Tests):* Schnelle, CPU-schonende Tests ohne laufendes LLM für Parser, Zahlennormalisierung, Chunking, deterministische Rechner-Tools und Hybrid-Retrieval.
  - *Mitte (Integrationstests):* Zusammenspiel von Ingestion -> Vektorspeicher -> Tool-Ausführung auf Beispieldokumenten.
  - *Spitze (End-to-End & RAGAS):* Vollständige Agenten-Evaluation über den verbindlichen Fragenkatalog (12 Fragen, seit M6b 14).
- **AAA-Pattern:** Jeder Test ist klar in **Arrange** (Testdaten/Mocks vorbereiten), **Act** (Funktion ausführen) und **Assert** (Ergebnis prüfen) gegliedert.
- **FIRST-Prinzipien:** Unit-Tests sind **F**ast (Millisekunden statt LLM-Wartezeit), **I**ndependent (isolierte `tmp_path`-Verzeichnisse), **R**epeatable (deterministische Mocks/Fixtures), **S**elf-Validating (eindeutige Assertions) und **T**imely (direkt mit jedem Modul geschrieben).
- **Shift-Left-Testing & Quality Gates:** Linter (`ruff check`), Formatter (`ruff format --check`) und schnelle Unit-Tests (`pytest -m "not slow"`) werden vor jedem Commit lokal ausgeführt, um Fehler sofort abzufangen.

---

## 6. Naming, Dokumentation & Code-Hygiene

- **Verbindliche Namenskonventionen (durchgängig Englisch):**
  - Verzeichnisse & Python-Dateien: `snake_case` (z. B. `src/ingestion/table_parser.py`)
  - Klassen, Typen & Pydantic-Modelle: `PascalCase` (z. B. `DocumentChunk`, `AuditAgent`)
  - Funktionen, Methoden & Variablen: `snake_case` (z. B. `extract_line_items()`)
  - Wahrheitswerte (Booleans): klare Präfixe wie `is_valid`, `has_table`, `is_noise_document`
  - Konstanten: `SCREAMING_SNAKE_CASE` (z. B. `MAX_OLLAMA_MEMORY_GB`)
  - Markdown- & Konfigurationsdateien im Projekt: `kebab-case.md` oder etablierte Standardnamen (`README.md`, `CLAUDE.md`, `CODING_STANDARDS.md`)
- **Architecture Decision Records (ADRs):** Kurze, nummerierte Markdown-Dateien unter `docs/adr/` (z. B. `0001-hybrid-retrieval-and-tools.md`), die Kontext, Entscheidung, verworfene Alternativen und Konsequenzen festhalten – als direkt verwertbare Faktenbasis für Phase 2.
- **Opinionated Code Formatting:** `ruff` dient als verbindlicher Formatter und Linter für den gesamten Python-Codebase.