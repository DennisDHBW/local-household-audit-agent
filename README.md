# local-household-audit-agent

Lokaler, agentischer RAG-Prototyp: **Energie- & Nebenkosten-Auditor**.
Der Agent durchsucht Strom-, Gas-/Fernwärme-, Wasser- und Nebenkostenunterlagen, gleicht Verträge mit Abrechnungen ab, rechnet Beträge nach und meldet Auffälligkeiten mit Quellenangabe. Alles läuft lokal (Ollama, ChromaDB), ohne Cloud-API.

Hochschulprojekt im Kurs „Agentensysteme: Local Agentic AI“ (DHBW). Phase 1: Umsetzung des Prototyps. Phase 2: Ausarbeitung (5–8 Seiten, LaTeX).

---

## Projektstruktur (M0 bis M6 umgesetzt, Stand v1.0.0)

```
local-household-audit-agent/
├── README.md
├── CODING_STANDARDS.md        # verbindliche Engineering-Regeln
├── pyproject.toml, uv.lock    # Abhängigkeiten (uv), ruff- und pytest-Konfiguration
├── scripts/check.sh           # Quality Gate (ruff check, ruff format --check, pytest)
├── dataset/                   # synthetischer Testkorpus (30 PDFs), documents.yaml, ground_truth.yaml
├── data/                      # erzeugt: processed/ (JSON-Chunks), vectors/ (ChromaDB), eval/ (versioniert)
├── .cache/                    # erzeugt: Enrichment-Cache (nicht versioniert)
├── src/audit_agent/
│   ├── config.py              # zentrale Konfiguration (Pfade, Modelle, Limits, AUDIT_*-Variablen)
│   ├── preflight.py           # Fail-fast-Prüfung der Ollama-Modelle
│   ├── smoke/                 # Smoke-Test (Geschwindigkeit, Tool-Calling, Embedding, Vision)
│   ├── corpus/                # Modelle und Loader für documents.yaml und ground_truth.yaml
│   ├── ingestion/             # PDF-Parser, Chunk-Modelle, Pipeline
│   ├── enrichment/            # Bild-Captions, Tabellen-Summaries, Cache (braucht Ollama)
│   ├── retrieval/             # Index (ChromaDB), Suche mit Filter und Hierarchie-Boost, Evidenz, Vergleichslauf (braucht Ollama)
│   ├── agent/                 # ReAct-Schleife mit 5 Tools (ADR-0014), Rechner, Protokoll, Report, CLI, Streamlit-Oberfläche (braucht Ollama)
│   ├── evaluation/            # Testmodul: Varianten B0/P1/P2, eigene Metriken, RAGAS mit lokalem Bewerter, Report
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
| `docs/sources.md` | Hintergrund-Literatur (nicht Teil der Ausarbeitung) | optional | – |
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

## Schnellstart

```bash
# Voraussetzungen: uv, Ollama als Dienst
ollama pull qwen2.5:7b && ollama pull llama3.1:8b && ollama pull gemma3:4b && ollama pull llama3.2 && ollama pull nomic-embed-text

uv sync                                   # installiert Python 3.13 und alle Abhängigkeiten
./scripts/check.sh                        # Quality Gate (ruff, pytest ohne LLM)
uv run python -m audit_agent.smoke        # Smoke-Test, braucht laufendes Ollama (ca. 15-30 Min.)
uv run python -m audit_agent.ingestion    # parst alle PDFs nach data/processed/ (ca. 30 s, ohne Ollama)
uv run python -m audit_agent.enrichment   # Captions + Summaries, braucht Ollama (erster Lauf ca. 20-25 Min., danach Cache)
uv run python -m audit_agent.retrieval index    # baut den ChromaDB-Index in data/vectors/, braucht Ollama (nomic-embed-text)
uv run python -m audit_agent.retrieval search "Arbeitspreis Stromvertrag" --utility-type electricity   # Evidenz in der CLI
uv run python -m audit_agent.retrieval compare --run-id run-004   # alle Fragen x 6 Konfigurationen, Report unter data/eval/run-004/
uv run python -m audit_agent.agent ask "Welchen Arbeitspreis nennt der Stromvertrag?"   # eine Frage, braucht Ollama (mehrere Minuten)
uv run python -m audit_agent.agent run-set --run-id run-005   # Fragen S2, G1, N1, S4 (--ids ... oder --all), Report unter data/eval/run-005/agent.md
uv run streamlit run src/audit_agent/agent/app.py   # Chat mit Plan, Belegen, Tabellen und Grafiken; Rückfragen wie „und als Grafik?“, braucht Ollama
uv run python -m audit_agent.evaluation generate --run-id run-007 --ids S2 G1 N1   # B0, P1, P2 (--variants, --all, --model), braucht Ollama
uv run python -m audit_agent.evaluation score --run-id run-007   # bewertet gespeicherte Antworten ohne Ollama
ollama create audit-judge -f scripts/audit-judge.Modelfile   # einmalig: RAGAS-Bewerter (qwen2.5:7b, num_ctx 8192)
uv run --group ragas python -m audit_agent.evaluation ragas --run-id run-009   # RAGAS auf gespeicherten Antworten, braucht Ollama
./scripts/night_eval.sh                   # Nachtlauf: 14 Fragen mit beiden Modellen, danach RAGAS (wartet auf Ollama, wiederholt Abbrüche)
uv run python scripts/check_evidence.py --run-id run-010   # Belegabgleich ohne Ollama: standen die Sollfakten im Kontext? schreibt evidence.json
uv run python scripts/analyze_timing.py --run-id run-010 --run-id run-012   # P2-Zeit je Lauf: Prefill gegen Dekodieren, erste gegen spätere Aufrufe, ohne Ollama
uv run python -m audit_agent.facts build    # Faktenspeicher data/processed/facts.json aus den Chunks (ohne Ollama, M8)
uv run python -m audit_agent.facts audit    # prüft alle Rechnungen mit den Prüfregeln (ohne Ollama), zeigt Abweichungen
uv run python scripts/dry_run.py              # Trockenlauf des Nachtlaufs ohne Ollama (Temp-Ordner, Orakel statt Modell), findet Abstürze vorab
./scripts/m8_prepare.sh                     # M8: Ingestion, Enrichment, Fakten, Index, Quality Gate, Smoke-Test (braucht Ollama)
./scripts/m8_night.sh                       # M8: Kontrolllauf P2 über alle Entwicklungsfragen (run-027, nach ISS-121 bis ISS-123)
./scripts/m8_night.sh --holdout             # M8: Endlauf B0/P1/P2 mit den zurückgehaltenen Fragen (run-028), erst ganz am Schluss
uv run python scripts/analyze_agentics.py --run-id run-025   # Kennzahlen zur Agentik eines Laufs (ohne Ollama)
```

Der Smoke-Test schreibt `data/eval/<run-id>/smoke.json` und `smoke.md`. Einstellungen lassen sich per Umgebungsvariable ändern, z. B. `AUDIT_OLLAMA_HOST`, `AUDIT_NUM_CTX`, `AUDIT_MODEL_AGENT`. Die Ingestion schreibt je PDF eine Datei `data/processed/<datei>_chunks.json` und die Diagramme nach `data/processed/images/`. Das Enrichment ergänzt diese Dateien um Bild-Captions und `table_summary`-Chunks; es muss nach jeder neuen Ingestion erneut laufen (aus dem Cache in Sekunden). Mit `--dry-run` zählt es die offenen Jobs ohne Ollama, mit `--limit 1` macht es einen Probelauf, mit `--run-id <id>` landet der Report unter `data/eval/<id>/enrichment.json`. Der Index (`retrieval index`) muss nach jeder neuen Ingestion und jedem Enrichment neu gebaut werden. `retrieval search` akzeptiert `--utility-type`, `--doc-type`, `--contract-id`, `--year`, `--no-boost`, `--types`, `--require-heading` und `--top-k`. Bei Prüffragen (Wörter wie „korrekt“, „stimmt“, „passt“) kann vor der Antwort ein fester Prüfablauf laufen (Plan, Suche, Lesen, Differenz mit `calculate`, ADR-0016); er ist nach RUN-017 standardmäßig aus (`AgentSettings.audit_flow_enabled`). Der Agent schreibt je Frage `data/eval/<run-id>/agent-<id>.jsonl` (jeder Schritt eine Zeile) und bei `run-set` zusätzlich `agent.md` und `agent.json`; die Modellwahl geht mit `--model` oder `AUDIT_MODEL_AGENT`. Der Index muss vorher gebaut sein. Die Evaluation schreibt nach `data/eval/<run-id>/` je Variante `answers-<b0|p1|p2>.jsonl` (eine Zeile je Antwort; ein abgebrochener Lauf wird mit demselben Befehl fortgesetzt), beim Agenten zusätzlich `p2-<Frage>.jsonl`, dazu `manifest.json` (Modell, B0-Kontext), `scores.json` und `report.md`. Der Katalog hat 14 Fragen (5 Standard, 4 Grenzfälle, 2 Negativ, 3 Zusatz); G1, G3 und G4 prüfen die eingebauten Fehler E1–E3. `ragas` (Abhängigkeitsgruppe `ragas`, ADR-0012) bewertet Faithfulness und Context Recall mit dem Bewerter `audit-judge` (`AUDIT_MODEL_JUDGE`, `--judge`), schreibt `ragas.jsonl` (fortsetzbar, `--retry-errors` für Fehlschläge) und aktualisiert danach `scores.json` und `report.md`; Antworten, deren Bewerter-Prompt nicht in 8.192 Token passt, werden als „zu lang“ gezählt statt gekürzt. RAGAS-Telemetrie ist abgeschaltet. Ein Lauf enthält nur ein Modell; für ein anderes Modell eine neue `--run-id` wählen. B0 braucht die Ingestion, P1 und P2 zusätzlich den Index.

## Ausarbeitung bauen

```bash
cd paper && latexmk -pdf main.tex
```
