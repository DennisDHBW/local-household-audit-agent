# local-household-audit-agent

Lokaler, agentischer RAG-Prototyp: **Energie- & Nebenkosten-Auditor**.
Der Agent durchsucht Strom-, Gas-/Fernwärme-, Wasser- und Nebenkostenunterlagen, gleicht Verträge mit Abrechnungen ab, rechnet Beträge nach und meldet Auffälligkeiten mit Quellenangabe. Alles läuft lokal (Ollama, ChromaDB), ohne Cloud-API.

Hochschulprojekt im Kurs „Agentensysteme: Local Agentic AI“ (DHBW). Phase 1: Umsetzung des Prototyps. Phase 2: Ausarbeitung (5–8 Seiten, LaTeX).

---

## Projektstruktur (geplant)

```
local-household-audit-agent/
├── README.md
├── CODING_STANDARDS.md        # verbindliche Engineering-Regeln
├── config/                    # zentrale Konfiguration (Pfade, Modelle, Limits)
├── dataset/                   # synthetischer Testkorpus (28 PDFs) + documents.yaml + ground_truth.yaml
├── data/                      # erzeugt: processed/ (JSON-Chunks), vectors/ (ChromaDB), eval/ (versioniert)
├── src/
│   ├── ingestion/             # Parsing, Chunking, Enrichment (schreibende Seite)
│   ├── retrieval/             # Suche, Scoring, Filter (lesende Seite)
│   ├── tools/                 # deterministische Agent-Tools (Suche, calculate, ...)
│   ├── agent/                 # ReAct-Schleife, Prompts
│   ├── evaluation/            # Testmodul, Metriken, RAGAS
│   └── ui/                    # Streamlit / CLI
├── tests/                     # pytest (unit / integration / slow)
├── paper/                     # Ausarbeitung (LaTeX, DHBW-Vorlage)
└── docs/                      # Projektdokumentation (siehe unten)
```

---

## Dokumentation: Welche Datei wofür?

Die Dateien unter `docs/` werden **während der Umsetzung** laufend gepflegt. Sie sind das Rohmaterial für die Ausarbeitung in Phase 2.

| Datei | Inhalt | Wann pflegen? | Nutzen für die Ausarbeitung |
|---|---|---|---|
| `docs/status.md` | Aktueller Stand, nächste Schritte, offene Fragen (max. 1 Seite) | Ende jeder Arbeitssitzung | Übergabe zwischen Chats, spart Tokens |
| `docs/dev-journal.md` | Entwicklungstagebuch; Claude schreibt, ich liefere den O-Ton | Ende jeder Arbeitssitzung | Reflexion, Vorgehen, persönliche Note |
| `docs/issues-log.md` | Probleme, Bugs, erkannte Schwachstellen mit Ursache und Lösung | sobald ein Problem auftaucht | Reflexion, Grenzen, „Lessons Learned“ |
| `docs/adr/` | Architekturentscheidungen (Kontext, Entscheidung, Alternativen, Folgen) | bei jeder echten Entscheidung | Architekturkapitel, Begründungen |
| `docs/reverse-engineering/` | Verständnisnotizen je Meilenstein | nach jedem Meilenstein | Nachweis des Verständnisses |
| `docs/evaluation-log.md` | Testläufe, Konfiguration, Ergebnisse, Deutung | nach jedem Testlauf | Kapitel Testmodul & Evaluation |
| `docs/glossary.md` | Fachbegriffe DE ↔ Bezeichner EN, Erklärung in eigenen Worten | wenn ein neuer Begriff auftaucht | eigene Sprache, einheitliche Begriffe |
| `docs/sources.md` | Literatur mit Kernaussage in eigenen Worten | beim Lesen | Literaturbezug (10 %) |
| `docs/requirements.md` | Alle Anforderungen (Folien + Professor) | stabil | Abgleich vor der Abgabe |
| `docs/concept.md` | Projektkonzept | bei Konzeptänderungen | Gliederung, Architektur |
| `docs/ai-workflow.md` | Arbeitsweise mit Claude, Projektanweisungen, Modellwahl | bei Bedarf | – |
| `docs/writing-guide.md` | Schreibregeln für Phase 2 (natürlicher studentischer Stil, keine Ich-Form) | stabil | Vorgaben für die Kapitel |
| `docs/preparation-checklist.md` | Was vor dem Start zu tun ist | einmalig | – |

**Faustregel:** Lieber kurze, ehrliche Stichpunkte sofort notieren als später alles aus dem Gedächtnis rekonstruieren.

---

## Arbeitsweise mit Claude

Claude arbeitet direkt im Projektordner (Dateien, `uv`, `ruff`, `pytest`, `git`). Ollama-abhängige Schritte startet der Nutzer mit einem vorbereiteten Befehl. Details: `docs/ai-workflow.md`.

---

## Schnellstart (wird mit dem Code ergänzt)

```bash
# Voraussetzungen: Python 3.13, uv, Ollama als Dienst
ollama pull qwen2.5:7b && ollama pull llama3.1:8b && ollama pull gemma3:4b && ollama pull llama3.2 && ollama pull nomic-embed-text
# Installation, Ingest, Abfrage und Evaluation folgen ab M0
```

## Ausarbeitung bauen

```bash
cd paper && latexmk -pdf main.tex
```
