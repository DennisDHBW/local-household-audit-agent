# Anforderungen: KI-Agenten-Prototyp & Konzeptausarbeitung

**Lehrveranstaltung:** Agentensysteme: Local Agentic AI – Leistungsfähige KI-Agenten & Modulares RAG mit rein lokaler Architektur (Ollama)
**Rahmen:** 30 LV à 45 Minuten (1350 Minuten), 3./4. Studienjahr, Informatik-naher Studiengang
**Eigenes Projekt:** local-household-audit-agent (lokaler KI-Agent für Haushaltsdokumente)

**Quellen dieser Zusammenstellung**
- (F) Vorlesungsfolien `01.pdf`
- (P) Ergänzende Hinweise des Professors (Originalwortlaut in [Anhang A](#anhang-a-originalwortlaut-der-professor-hinweise))

> Legende: **MUSS** = explizit gefordert · **SOLL** = ausdrücklich empfohlen bzw. bewertungsrelevant · **OPTIONAL** = freiwillig · **REFERENZ** = Orientierung aus der Vorlesung (Referenzprototyp), kein Pflichtbestandteil

---

## Inhaltsverzeichnis

1. [Auf einen Blick](#1-auf-einen-blick)
2. [Rahmendaten der Prüfungsleistung](#2-rahmendaten-der-prüfungsleistung)
3. [Bewertungskriterien](#3-bewertungskriterien)
4. [Grundanforderungen an den KI-Agenten](#4-grundanforderungen-an-den-ki-agenten)
5. [Inhaltliche Anforderungen an die Ausarbeitung](#5-inhaltliche-anforderungen-an-die-ausarbeitung)
6. [Zusatzanforderung 1: Testmodul](#6-zusatzanforderung-1-testmodul-für-den-rag-ki-agenten)
7. [Zusatzanforderung 2: Reverse Engineering & Eigenverständnis](#7-zusatzanforderung-2-reverse-engineering--eigenverständnis)
8. [Lernziele der Lehrveranstaltung](#8-lernziele-der-lehrveranstaltung-maßstab-für-die-bewertung)
9. [Ablauf, Coachings & Hausaufgaben](#9-ablauf-coachings--hausaufgaben)
10. [Referenzarchitektur aus der Vorlesung](#10-referenzarchitektur-aus-der-vorlesung-orientierung)
11. [Abgabe-Checkliste](#11-abgabe-checkliste)
- [Anhang A: Originalwortlaut der Professor-Hinweise](#anhang-a-originalwortlaut-der-professor-hinweise)

---

## 1. Auf einen Blick

| Bereich | Anforderung | Status |
|---|---|---|
| Abgabe | Konzeptentwurf für einen eigenen KI-Agenten-Prototyp (Moodle) | MUSS |
| Umfang | ca. 5–8 Seiten (oder äquivalente Markdown-/Notebook-Dokumentation) | MUSS |
| Fokus | Architekturentwurf, Datenaufbereitung, Tool-Strategie, Testkonzept | MUSS |
| Agent: Betrieb | lokal / offline | MUSS |
| Agent: Retrieval | modulare RAG-Pipeline | MUSS |
| Agent: Verhalten | agentisch | MUSS |
| Agent: Qualität | systematisch getestet / validiert | MUSS |
| Testmodul | Abschnitt über ein **umgesetztes** Testmodul, mit dem dem Prototyp eine „Qualität“ zugeschrieben wird | MUSS |
| Testfragen | 5 Standardfragen, 2 komplexe Grenzfälle, 2 Negativfragen | MUSS (Leitfrage 6) |
| GraphRAG | begründete Entscheidung, ob GraphRAG sinnvoll ist (nicht implementieren nötig) | MUSS |
| Literatur | Literaturbezug & Reflexion (10 % der Note) | MUSS |
| Verständnis | Konzept (logisch) und Prototyp (technisch) „in all seinen Körperteilen“ verstanden – erkennbar im Dokument | MUSS (bewertungsrelevant) |
| Sprache | Dokument in einer Sprache, die „von Ihnen kommt“ | SOLL (wird beachtet) |
| Code / UI | Lauffähiger Code-Prototyp / UI-Mockup | OPTIONAL laut Folie (siehe Hinweis 2.1) |
| KI-Assistenz | Vibe-Coding / KI-Assistenten ausdrücklich erlaubt | erlaubt |
| Selbststudium | Einheit zu „Reverse Engineering … in der Programmierung“ bzw. „… beim Vibecoden“ | SOLL (Empfehlung) |

---

## 2. Rahmendaten der Prüfungsleistung

**Prüfungsleistung:** Konzeptentwurf für einen eigenen KI-Agenten-Prototyp (Abgabe über Moodle: <https://moodle.dhbw.de/mod/assign/view.php?id=592218>) (F, P)

- **Format:** ca. 5–8 Seiten (oder äquivalente Markdown-/Notebook-Dokumentation)
- **Fokus:** Technisch fundierter Architekturentwurf, Datenaufbereitung, Tool-Strategie, Testkonzept
- **Optional:** Lauffähiger Code-Prototyp / UI-Mockup

### 2.1 Hinweis zur Einordnung „optional“

Laut Folie ist der lauffähige Prototyp optional. Die Zusatzanforderungen des Professors setzen aber faktisch einen umgesetzten Prototyp voraus:
- Das Testmodul soll **umgesetzt** und **genutzt worden sein**, um dem **eigenen Prototyp** eine Qualität zuzuschreiben.
- Der Agent soll **systematisch getestet / validiert** sein.
- Reverse Engineering bezieht sich ausdrücklich auf **jede Code-Datei**, Funktionen, Datenstrukturen, Datenflüsse und Bibliotheken des Prototyps.
- Bewertet wird, ob Konzept (logisch) **und Prototyp (technisch)** verstanden wurden.

→ Praktisch sollte also ein lauffähiger Prototyp mit Testmodul vorliegen und im Dokument beschrieben werden.

### 2.2 Klärungen (Stand 2026-11-14)

| Frage | Antwort |
|---|---|
| Selbst erzeugte (synthetische) Dokumente als Datenbasis? | erlaubt; Korpus liegt vollständig synthetisch unter `dataset/` |
| Ich-Form in der Ausarbeitung? | vermeiden (unpersönlicher Stil) |
| Kennzeichnung des KI-Einsatzes? | nicht vorgesehen; KI-Hinweis der Vorlage entfernt (Entscheidung 2026-11-18) |
| Abgabe des Codes | GitHub-Repository `DennisDHBW/local-household-audit-agent` |
| Seitenumfang | 5–8 Seiten ohne Anhang, Verzeichnisse und Titelblatt |
| LaTeX-Vorlage | DHBW-Projektarbeiten-Template (Evolinox), unter `paper/`; aktiv sind nur Titelblatt, Inhaltsverzeichnis und Kapitel |
| Quellen / Literaturverzeichnis | 5 Quellen mit Literaturverzeichnis (Entscheidung 2026-11-19, ersetzt „keine Literatur“ vom 2026-11-14) |
| Abgabetermin, Coaching-Termine | für die Planung nicht relevant |

> Hinweis: Das Bewertungskriterium „Literaturbezug & Reflexion“ (10 %) bleibt bestehen. Die Ausarbeitung zitiert höchstens fünf Quellen (Entscheidung 2026-11-20, ISS-103): ReAct, Gao et al. 2023, RAGAS, Xiang et al. 2026, Ferrazzi et al. 2026; Auswahl und Reserve in `sources.md`. Der Reflexionsteil stützt sich weiter vor allem auf eigene Ergebnisse.

---

## 3. Bewertungskriterien

| Nr. | Kriterium | Gewicht | Was dazu ins Dokument gehört (abgeleitet aus Folien & Hinweisen) |
|---|---|---|---|
| 1 | Problemverständnis & Use Case | 15 % | Welches konkrete Problem löst der Agent? Welche Daten liegen vor? Warum lokal? |
| 2 | Architekturentwurf des Agenten | 25 % | Komponenten, Kontrollfluss, Agentik (ReAct / Tool-Calling), Orchestrierung, Modellauswahl, lokale Ausführung |
| 3 | RAG- & Retrieval-Konzept | 20 % | Modulare RAG-Pipeline, Embedding, Vektor-Store, Retrieval-Strategie (z. B. Hybrid, Hierarchie-Boost), Quellenkontrolle/Zitation, GraphRAG-Entscheidung |
| 4 | Vorverarbeitung & Datenstrukturen | 15 % | Parsing, Strukturerkennung, Chunking, Enrichment, Zwischenformate (JSON, Metadaten) |
| 5 | Test- & Evaluationsstrategie | 15 % | Testmodul, Metriken/KPIs (z. B. RAGAS), eigene kontextspezifische Testszenarien, 5 Standard-/2 Grenzfall-/2 Negativfragen, Ergebnisse |
| 6 | Literaturbezug & Reflexion | 10 % | Bezug zu Fachliteratur (Paper), kritische Reflexion von Entscheidungen, Grenzen, Ausblick |

**Zusätzlich querschnittlich bewertungsrelevant (P):**
- Erkennbar tiefes Verständnis aller Bestandteile (Reverse Engineering, siehe Abschnitt 7)
- Eigene Sprache des Dokuments

---

## 4. Grundanforderungen an den KI-Agenten

Der Professor hat mitgeteilt, dass der KI-Agent grundsätzlich (P):

### 4.1 Lokal / offline laufen muss (MUSS)
Hintergrund aus der Vorlesung (F):
- 100 % Datensouveränität & DSGVO-Konformität: vertrauliche Daten verlassen niemals das lokale System.
- 0 € laufende API-Kosten, keine Token-Limits oder API-Ausfälle; unbegrenztes Experimentieren und automatisiertes Benchmarking.
- Lokale SLMs/LLMs via **Ollama** (z. B. Llama 3.1 8B, Phi-3/Phi-4, Qwen 2.5, Gemma 3 Vision) beherrschen Tool-Calling und multimodales Verstehen auf Standard-Hardware.
- Lokaler Vektor-Store (z. B. **ChromaDB**).
- „Architektur schlägt Modellgröße“: Strukturiertes Parsing, typisiertes Chunking, Hierarchie-Prefixing und ReAct-Tools machen ein lokales 8B-Modell oft präziser und belegbarer als ein unstrukturiertes 400B-Cloud-Modell.

> ⚠️ Hinweis: Die Folien zeigen als Option für die finale Antwortgenerierung auch Cloud-Modelle (Claude Sonnet / GPT-4o, „nur bei Klick“, „Live-Vergleich per Knopfdruck“). Da „lokal/offline“ eine Grundanforderung ist, sollte der Agent **vollständig lokal funktionieren**; ein Cloud-Modell höchstens als klar gekennzeichnete, abschaltbare Vergleichsoption.

### 4.2 Eine modulare RAG-Pipeline nutzen muss (MUSS)
Abgrenzung (F):
- **Standard-RAG (linear & naiv):** Dokumente → naiver Text-Split → Embeddings → Vektor-DB → Top-k Chunks → Prompt → Antwort. Probleme: Kontextverlust, zerrissene Tabellen, fehlende Bilder, keine Filterung.
- **Modulares RAG (strukturiert & flexibel):** Dokumente → Parser → Strukturerkennung (Heading, Table, Image) → Enrichment (Captions, Summaries) → typisiertes Chunking → hierarchisches Embedding → Hybrid Search & Hierarchie-Boost → Evidence-First Review → Final Answer LLM.

### 4.3 Agentisch sein soll (MUSS)
Aus der Vorlesung (F):
- Agent = Entität, die ihre Umgebung wahrnimmt (Perception) und über Aktuatoren/Tools handelt (Action), um ein Ziel zu erreichen.
- Schlüsselkomponenten eines LLM-Agenten:
  - **Reasoning:** Schlussfolgerung und Handlungsplanung (z. B. ReAct-Muster)
  - **Memory:** Kurzzeit (Kontextfenster) & Langzeit (Vektor-DB, Knowledge Graph)
  - **Tools:** externe Schnittstellen (APIs, Python-Interpreter, Dokumenten-Parser, DB-Suche)
  - **Planning:** Task-Dekomposition, Reflexion, Selbstkorrektur
- Merkmale von Modular/Agentic RAG: dynamische Entscheidungsfindung (Tool-Aufrufe), strukturbewusste Vorverarbeitung, Evidence-First-Verifikation, Selbstreflexion und Fehlerkorrektur.

### 4.4 Systematisch getestet / validiert sein soll (MUSS)
→ Konkretisiert durch das Testmodul (Abschnitt 6) und die Testfragen-Vorgabe (Abschnitt 5.6).

---

## 5. Inhaltliche Anforderungen an die Ausarbeitung

Grundlage: Leitfragen für das Konzept (F, Folie 45), GraphRAG-Projektanforderung (F, Folie 46), Bewertungskriterien.

### 5.1 Problem & Use Case (Leitfrage 1)
- Welches konkrete Problem löst der Agent?

### 5.2 Datenbasis (Leitfrage 2)
- Welche Daten liegen vor? **Formate, Tabellen, Bilder, Qualität**
- Umgang mit semistrukturierten Dokumenten (PDFs sind ein visuelles Darstellungsformat, keine semantische Datenstruktur): mehrspaltige Layouts, umbrochene Absätze, Tabellen ohne Tags, Abbildungen ohne Text-Äquivalent, Überschriftenhierarchien (H1 → H2 → H3).

### 5.3 Chunking- & Ingestion-Pipeline (Leitfrage 3)
- Wie sieht die Chunking- und Ingestion-Pipeline aus?
- Erwartete Inhalte laut Lernzielen/Fokus: Aufbereitung multimodaler, semistrukturierter Dokumente (Text, Tabellen, Bilder); Definition geeigneter **Zwischenformate (JSON, strukturierte Chunks, Metadaten)**.

### 5.4 Tools / Funktionen (Leitfrage 4)
- Welche Tools/Funktionen werden benötigt? (Tool-Strategie ist expliziter Fokus der Prüfungsleistung)

### 5.5 GraphRAG-Entscheidung (Leitfrage 5 + Projektanforderung) – MUSS
GraphRAG muss **nicht vollständig implementiert** werden, aber es muss **begründet entschieden** werden, ob GraphRAG für den eigenen Use Case sinnvoll wäre.

Prüffragen (Leitfrage 5):
- Gibt es relevante Entitäten?
- Gibt es Beziehungen zwischen diesen Entitäten?
- Gibt es Multi-Hop-Fragen oder Querverweise?
- Wäre ein kleiner Knowledge Graph hilfreich?

Kurz zu beschreiben (Folie 46):
- Welche Entitäten könnten im Graph vorkommen?
- Welche Beziehungen wären relevant?
- Welche Fragen wären mit GraphRAG besser beantwortbar?
- Warum reicht ggf. klassisches RAG aus?
- Welche zusätzlichen Kosten und Komplexitäten entstehen?

Entscheidungshilfe aus der Vorlesung – GraphRAG lohnt sich bei:

| Situation | Beispiel |
|---|---|
| Viele Entitäten | Module, Personen, Begriffe, Gesetze, Produkte |
| Viele Beziehungen | Modul A setzt Modul B voraus |
| Querverweise | Paragraphen, Richtlinien, Prozessketten |
| Multi-Hop-Fragen | „Welche Module hängen indirekt mit KI-Agenten zusammen?“ |
| Überblicksfragen | „Welche Themencluster kommen in den Dokumenten vor?“ |

GraphRAG ist weniger notwendig bei einfachen Faktenfragen aus einzelnen Abschnitten. GraphRAG erkennt zusätzlich Entitäten, Beziehungen („gehört zu“, „setzt voraus“, „prüft“, „verweist auf“), Communities/Themencluster und Pfade zwischen Konzepten (Pipeline: Dokumente → Chunks → Entity- & Relationsextraktion → Knowledge Graph → Graph Retrieval + Vector Retrieval → Antwort mit relationalem Kontext).

### 5.6 Test & Evaluation der Antwortgüte (Leitfrage 6) – MUSS
- Wie testen und evaluieren Sie die Antwortgüte?
- Mindest-Testset:
  - **5 Standardfragen**
  - **2 komplexe Grenzfälle**
  - **2 Negativfragen** (Antwort ist nicht in den Dokumenten → Agent muss fehlenden Kontext erkennen)
- Ergänzt durch das Testmodul (Abschnitt 6).

### 5.7 Literaturbezug & Reflexion (10 %)
- Recherche-Hausaufgabe: mindestens **3 Grundlagen-** und **3 aktuelle Paper** sichten.
- Quellen: arXiv.org (Preprints), Papers with Code (Paper + Benchmarks + GitHub), ACL Anthology / NeurIPS / ICLR, Google Scholar.
- Schlüsselpublikationen als Startpunkt:
  - ReAct – Yao et al., 2022: *Synergizing Reasoning and Acting in Language Models*
  - Toolformer – Schick et al., 2023: *Language Models Can Teach Themselves to Use Tools*
  - RAG – Lewis et al., 2020: *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*
  - Modular RAG Survey – Gao et al., 2023: *Retrieval-Augmented Generation for Large Language Models: A Survey*
  - Self-RAG – Asai et al., 2023: *Learning to Retrieve, Generate, and Critique through Self-Reflection*
- Reflexion: kritische Bewertung der eigenen Entscheidungen, Grenzen, Ausblick (Block G: „Konzeptabgabe, Reflexion, Ausblick“).

### 5.8 Kostenbewusstsein & Modellwahl
- Lernziel: kostenbewusste lokale KI-Pipelines (Ollama, ChromaDB) mit API-Modellen **vergleichen und kombinieren**.
- Begründete Modellauswahl je Aufgabe (Embedding, Vision, Query-Rewriting, Reasoning/Tool-Calling) – Kriterien siehe Abschnitt 10.9.

---

## 6. Zusatzanforderung 1: Testmodul für den RAG-KI-Agenten

**Bezug:** Prüfungsleistung (Abgabe Konzeptentwurf / Prototyp) (P)

**MUSS:** Es soll ein **Abschnitt** in die Ausarbeitung aufgenommen werden, in dem ein **umgesetztes Testmodul** beschrieben wird.

- **Zweck:** Das Testmodul soll genutzt worden sein, um dem eigenen Prototyp eine **„Qualität“ zuschreiben** zu können.
- **Zwei sich ergänzende Ansätze** (in der Vorlesung besprochen):
  1. **Etablierte Test-Frameworks mit KPIs**, z. B. **RAGAS** – bauen häufig auf **synthetischen Testdatensätzen** auf.
  2. **Eigene, kontextspezifische Testszenarien** mit sinnvollen Testfragen – ergänzend „zielführend“.
- Verbindung zur Leitfrage 6: 5 Standardfragen, 2 komplexe Grenzfälle, 2 Negativfragen.

Was der Abschnitt demnach sinnvollerweise enthält:
- Aufbau und Funktionsweise des Testmoduls (Code, Datenfluss, Testdaten)
- Verwendete Metriken/KPIs und ihre Bedeutung
- Herkunft der Testdaten (synthetisch vs. eigene Szenarien)
- Durchgeführte Tests und **Ergebnisse** → daraus abgeleitete Qualitätsaussage
- Interpretation, Schwächen, Grenzen der Messung

Referenz aus der Vorlesung: Der Referenzprototyp vergleicht Pipeline (P1) und Agentic RAG (P2) an 5 standardisierten Testfragen (`compare_prototypes.py`) in den Kategorien Tabellen & Noten, Prozess/Text, Bilder/Screenshots, Multi-Hop & Rechnen, Negativ-Test (Details Abschnitt 10.12).

---

## 7. Zusatzanforderung 2: Reverse Engineering & Eigenverständnis

### 7.1 Einsatz von KI-Assistenten
- Die Entwicklung des Prototyps kann **sehr gut mit einem KI-Assistenten** (u. a. Vibe-Coding-Clients) betrieben werden.
- Das ist mit den Lernzielen kompatibel: Anforderungen an ein solches System **verstehen und prompten** (auf Basis der eigenen Idee).
- Gleichzeitiges Ziel: Zwischenergebnisse und Prototyp müssen **verstanden** sein.

### 7.2 Erwartetes Vorgehen
- Bei intensiver KI-Kooperation **immer wieder „Reverse Engineering“** betreiben.
- **Bei jedem Meilenstein** analysieren und testen (**Whitebox-Funktions- und Modultests**): Was hat der Assistent genau geliefert?
- Analysetiefe bis zur **atomaren Struktur**: Datenflüsse, Funktionen, Code-Dateien, Bibliotheken, …
- **Gleich nach Fertigstellung von Prototyp und Testmodul** rückwärts in alle Details einarbeiten (gern mit KI-Assistenz), insbesondere:
  - **jede Code-Datei**
  - **jeden Technologie-Baustein**
  - **Funktionen, Datenstrukturen und Datenflüsse** nachvollziehen
- Konzept (**logisch**) und Prototyp (**technisch**) in all seinen „Körperteilen“ verstanden haben.

### 7.3 Worauf bei der Bewertung geachtet wird
- Beim Lesen des Dokuments soll der Eindruck entstehen, dass die (gern KI-generierten) Ergebnisse zumindest „rückwärts“ **umfassend und tiefgehend verstanden** wurden.
- Ob das Dokument in einer Sprache geschrieben ist, die **„von Ihnen kommt“**.

### 7.4 Empfohlenes Selbststudium
- Separate Selbststudium-Einheit, z. B. zu „Reverse Engineering … in der Programmierung“ oder „… beim Vibecoden“.
- Begründung: Die Reverse-Engineering-Philosophie gewinnt in Zeiten generativer KI (auch außerhalb der Ingenieurwissenschaften) an Bedeutung als Werkzeug zum Verständnis KI-generierter Systeme.

---

## 8. Lernziele der Lehrveranstaltung (Maßstab für die Bewertung)

Am Ende der Lehrveranstaltung können Sie (F):
- Die Grundprinzipien moderner autonomer KI-Agenten erklären und abgrenzen
- Local Agentic AI anwenden: erkennen und umsetzen, dass sich leistungsfähige, datensouveräne KI-Agenten vollständig mit einer rein lokalen Architektur (RAG + lokale LLMs via Ollama) ohne Cloud-Abhängigkeiten realisieren lassen
- Eine modulare RAG-Architektur für wissensintensive Aufgaben entwerfen
- Multimodale, semistrukturierte Dokumente (Text, Tabellen, Bilder) aufbereiten
- Geeignete Zwischenformate (JSON, strukturierte Chunks, Metadaten) definieren
- Kostenbewusste lokale KI-Pipelines (Ollama, ChromaDB) mit API-Modellen vergleichen und kombinieren
- Ein tragfähiges, evidenzbasiertes Agentenkonzept inklusive Teststrategie entwickeln

**Didaktisches Zielbild:** „Gute KI-Agenten entstehen nicht dadurch, dass man einfach ein großes Cloud-Sprachmodell fragt. Gute Agenten entstehen durch Architektur: Datenvorverarbeitung, strukturierte Repräsentation, Retrieval, Tool-Nutzung, Orchestrierung, Quellenkontrolle und Evaluation.“

**Zentrale Erkenntnis:** Leistungsfähige KI-Agenten lassen sich vollständig lokal und digital souverän (z. B. via Ollama mit Llama 3, Phi-3, Gemma Vision und ChromaDB) auf eigener Hardware betreiben – mit 100 % Datenschutz, 0 € laufenden API-Kosten und voller Kontrolle über Daten und Modelle.

**Grenzen reiner LLMs, die die Architektur adressieren soll:**
1. Wissensgrenzen (eingefrorenes Trainingsdatum, kein Zugriff auf private Daten)
2. Halluzinationen
3. Kontextlänge & Kosten
4. Strukturblindheit (Tabellen, Layouts gehen verloren)
5. Mangelnde Nachvollziehbarkeit (keine verlässlichen Quellenangaben/Citations)

---

## 9. Ablauf, Coachings & Hausaufgaben

### 9.1 Grobstruktur der Lehrveranstaltung

| Block | Umfang | Thema |
|---|---|---|
| A: Kick-off & Orientierung | 2 LV | Motivation, Zielbild, Ablauf, Prüfungsleistung |
| B: Theorie kompakt | 4 LV | Agenten, LLMs, RAG, Tool Calling, semistrukturierte Daten |
| C: Literatur & Recherche | 2 LV | Arbeiten mit arXiv, Papers with Code, wissenschaftl. Verzeichnis |
| D: Referenzprototyp | 2 LV | Architektur-Walkthrough, Live-Demo (Streamlit / ChromaDB) |
| E: Brainstorming & Themen | 2 LV | Use Cases, Leitfragen, individuelle Themenfindung |
| F: Projektcoaching | 20 LV | 2 Individualmeetings à 15 min je Student:in (bei 30 Stud.) |
| G: Abschluss & Reflexion | 2 LV | Konzeptabgabe, Reflexion, Ausblick |

### 9.2 Coachings (je Student:in zwei 15-minütige Einzelcoachings)

**Coaching 1: Problemstellung & Architektur**
- Validierung der Datenquelle und des Use Cases
- Festlegung der Komponenten und des Zwischenformats
- Identifikation technischer Risiken

**Coaching 2: Pipeline & Teststrategie**
- Review der Chunking- und Retrieval-Strategie
- Definition der Testfragen und Qualitätskriterien
- Feedback zum Konzeptentwurf

### 9.3 Nächste Schritte / Hausaufgaben
1. Hausaufgabe 1: Formulierung von **3 potenziellen Agenten-Ideen**
2. Recherche: mindestens **3 Grundlagen- und 3 aktuelle Paper** sichten
3. Referenzprototyp erkunden: `streamlit run app.py` starten und Beispieldokument testen

### 9.4 Beispielhafte Themenfelder (aus der Vorlesung)

| Kategorie | Beispiel-Use-Case | Typische Datenbasis |
|---|---|---|
| Studienbegleiter | Prüfungsordnungs- & Modul-Agent | StuPrO-PDFs, Modulhandbücher |
| Technischer Support | Handbuch- & Datenblatt-Agent | Technische Manuals, Datenblätter |
| Prozessassistent | Onboarding- & Richtlinien-Agent | QM-Handbücher, Verfahrensanweisungen |
| Finanz- & Report-Agent | Kennzahlen-Extraktion | Quartalsberichte mit komplexen Tabellen |
| Recherche-Assistent | Wissenschaftlicher Paper-Agent | arXiv-PDFs mit Formeln und Diagrammen |

---

## 10. Referenzarchitektur aus der Vorlesung (Orientierung)

> REFERENZ: Diese Bausteine stammen aus dem Referenzprototyp der Vorlesung. Sie sind keine 1:1-Pflicht, aber der Maßstab, an dem „technisch fundiert“, „modulare RAG-Pipeline“ und „agentisch“ gemessen werden. Eigene Abweichungen sollten begründet werden.

### 10.1 Entwicklung von LLM-Anwendungen
1. Reine Chatbots: statisches Prompting, kein Zugriff auf externe Daten
2. Standard-RAG: naiver Text-Splitter, Vektorsuche, Antwortgenerierung
3. Modulares / Agentic RAG: dynamische Entscheidungsfindung (Tool-Aufrufe), strukturbewusste Vorverarbeitung (Tabellen, Bilder, Hierarchien), Evidence-First-Verifikation, Selbstreflexion und Fehlerkorrektur

### 10.2 Warum naives Text-Splitting scheitert
Eine Rohdatei (PDF/DOCX) ist ein visuelles Layout, kein Textstrom:
- **Fließtext:** liegt in unzusammenhängenden Spans vor; Spaltenlayouts werden vermischt
- **Überschriften:** keine semantischen Tags, nur Layout-Attribute (Schriftgröße, Fettdruck)
- **Tabellen:** Koordinaten und Linien; naive Splitter zerschneiden Zeilen und verlieren Spaltenköpfe
- **Bilder/Diagramme:** Pixelgrafiken ohne durchsuchbaren Text

Ziel der Vorverarbeitung: **Rekonstruktion der logischen Dokumentsemantik vor dem Embedding.**
Lösungsstrategie: (1) layout-bewusstes Parsen (z. B. PyMuPDF / `find_tables()`), (2) objektspezifisches Chunking (Text vs. Tabellenzeilen vs. Bilder), (3) semantisches Zwischenformat (JSON).

### 10.3 Vorverarbeitung im DocumentParser
1. **Tabellenerkennung zuerst** (`page.find_tables()`): Bounding Boxes lokalisieren, Zellen strukturiert extrahieren, Tabellenflächen aus Fließtext ausschließen (verhindert Duplikate).
2. **Hierarchie-Erkennung via Font-Heuristik:** Überschriften anhand `font_size` und `is_bold`; dynamischer `heading_stack` (z. B. `["3. Studienjahr", "Prüfungsordnung"]`).
3. **Absatz-Aggregation & Kontext-Prefixing:** Spans zu Absätzen (`min_chars = 20`, `max_block_chars = 1500`); aktive Überschrift als Prefix („Notenbescheid erstellen: Klicken Sie auf…“).
4. **Bildextraktion:** Bild-Bytes für multimodales Enrichment; Verknüpfung von Bildkoordinaten und Seitenzahl mit dem Kontext.

### 10.4 Typisierte Chunk-Typen

| Element-Typ | Rohinhalt aus Parser | Automatische Transformation |
|---|---|---|
| Text | Fließtext-Absatz | Kontext-Prefixing mit `heading_stack` |
| Heading | Überschriftenzeile | Aktualisierung des Hierarchie-Pfads |
| Table Row | Semantisch serialisierte Zeile (`Spalte: Wert \| …`) | Spaltenkopf-Injektion je Zeile; Generierung einer Tabellen-Zusammenfassung |
| Image | PNG/JPEG-Bytes | Lokales Vision-Modell generiert Bildbeschreibung (Caption) |

### 10.5 Datenpfade der Elemente
- **Pfad A – Fließtext** (`chunk_type == "text"`): Spans aggregieren bis Sinnabsatz vollständig (≥ 20 Zeichen) → `heading_stack` als Prefix → `[Ordner | Datei | Kapitel]` voranstellen, Vektorisierung mit `nomic-embed-text` → Speicherung in ChromaDB mit Metadaten (Dateiname, Seite, Hierarchie).
- **Pfad B – Überschriften** (`chunk_type == "heading"`): große/fette Schrift aktualisiert den hierarchischen Pfad; dient als Metadatenanker für nachfolgende Chunks und steuert den Hierarchie-Boost.
- **Pfad C – Tabellenzeilen** (`chunk_type == "table_row"`): Serialisierung als `"Spalte1: Wert1 | Spalte2: Wert2"`; TableSummarizer erzeugt zusätzlich einen Summary-Chunk (`is_table_summary = True`) → feingranulare Zeilen- und thematische Tabellensuche.
- **Pfad D – Bilder & Diagramme** (`chunk_type == "image"`): Bild-Bytes extrahieren → lokales Vision-Modell (`gemma3:4b`) beschreibt den Inhalt → Bildbeschreibung wird wie Text eingebettet (mit Verweis auf Seitenzahl).

### 10.6 JSON-Zwischenformat (Beispiel)

```json
{
  "chunk_id": "doc_01_p4_tbl_02",
  "chunk_type": "table_row",
  "content": "Modul: KI-Agenten | CP: 5 | Prüfungsleistung: Projektkonzept",
  "heading_stack": ["3. Studienjahr", "Prüfungsübersicht"],
  "page_number": 4,
  "metadata": {
    "filename": "StuPrO_Informatik.pdf",
    "table_id": "tab_02",
    "columns": ["Modul", "CP", "Prüfungsleistung"]
  }
}
```
Vorteil: Jedes Element behält seinen exakten hierarchischen und visuellen Kontext.

### 10.7 Drei Zwischenspeicher-Ebenen

| Ebene | Pfad | Zweck | Vorteil |
|---|---|---|---|
| 1. Strukturiertes JSON-Zwischenformat | `data/processed/<datei>_chunks.json` | alle Chunks inkl. Metadaten | Inspektion, Debugging, Reproduzierbarkeit |
| 2. Enrichment-DiskCache (SHA-256-Hash) | `.cache/` (diskcache) | cached Bild-Captions & Tabellen-Summaries | verhindert teure/langsame LLM-Neuberechnungen |
| 3. Lokaler Vektor-Store | `data/vectors/` (ChromaDB) | 768-dim Embeddings + Metadaten-Filter | schnelle Kosinus-Ähnlichkeitssuche |

### 10.8 Gesamtarchitektur
1. **Ingestion:** DocumentParser (`find_tables`, Font-Heuristik, Spans, Images)
2. **Enrichment:** TableSummarizer & ImageCaptioner (Gemma 3 Vision / Ollama)
3. **Strukturierte Repräsentation:** Chunks + Metadaten + optionale Entities/Relationen
4. Darauf drei Retrieval-Strategien:

| Dimension | Modulare Pipeline | Agentic Tool-Calling | GraphRAG |
|---|---|---|---|
| Kontrollfluss | statisch / deterministisch | dynamisch durch LLM gesteuert | Retrieval über Graphstruktur + Vektoren |
| Wissensstruktur | Chunks + Metadaten | Chunks + Tools | Entitäten + Relationen + Chunks |
| Bausteine | Hybrid Retrieval, Hierarchie-Boost, Evidence-First UI | `search_tables/images`, `get_outline/calculate`, Multi-Hop-Iteration | Entity Extraction, Relation Extraction, Graph Traversal |
| Stärke | schnelle Fakten- und Dokumentensuche | Multi-Step-Aufgaben und Tool-Nutzung | Zusammenhänge, Querverweise, Themencluster |
| Typische Frage | „Was steht in Abschnitt X?“ | „Finde Tabelle und berechne Summe“ | „Wie hängen A, B und C zusammen?“ |
| Kosten/Aufwand | niedrig | mittel bis hoch | mittel bis hoch, v. a. Graphaufbau |
| Einsatz | Standard-Fragen, Fakten | Tabellen, Bilder, Berechnungen | Beziehungswissen, Multi-Hop, Überblicksfragen |

Merke: Vector RAG findet ähnliche Textstellen; GraphRAG nutzt zusätzlich Beziehungen und Pfade zwischen Konzepten.

### 10.9 Embedding, Hierarchie-Prefix & Retrieval
- **Prefix-Prinzip:** Vor der Vektorisierung wird jedem Chunk ein Hierarchie-Header vorangestellt, z. B. `[3. Studienjahr | Informatik | Prüfungsleistungen] Projektarbeit (100%), 5. Semester`. Effekt: Eine Suche nach „Prüfungsleistungen Informatik“ findet den Chunk, obwohl „Informatik“ nicht im Zelleninhalt steht; Pfad- und Kapitelmetadaten werden Teil der Vektorähnlichkeit.
- **Retrieval & Hierarchie-Boosting:**
  Das Retrieval kombiniert Vektor-Distanz mit Pfad-Matching:
  1. Query-Rewriting: lokales Modell (`phi3:medium`) formuliert die Nutzeranfrage in eine präzise Suchphrase um
  2. Kandidatensuche: ChromaDB liefert Top-20 Kandidaten basierend auf Kosinus-Ähnlichkeit: `base_score = 1 − cosine_distance`
  3. Hierarchie-Boost: Kommen Suchbegriffe im Dateinamen, Ordner oder `heading_stack` vor? → Multiplikator **× 1.5** für Pfadtreffer
  4. Finaler Score: `final_score = base_score × hierarchy_boost`

### 10.10 Rekomposition & Zitation
- **Stufe 1 – Hierarchische Evidenz (UI):** `build_evidence()` rekonstruiert aus flachen Chunks die Dokumentstruktur (Dokument → Kapitel → Text / Tabellenzeilen / Abbildungs-Captions, jeweils mit Score und Seite); Farbcodierung nach Relevanz in Streamlit.
- **Stufe 2 – LLM-Kontext & Zitation:** `_build_context()` baut einen Prompt mit durchnummerierten Quellen (Typ, Datei, Hierarchiepfad, Seite) + Frage. System-Prompt: Antwort darf **nur** auf den nummerierten Quellen basieren. Ergebnis: Antwort mit präzisen Quellenangaben (Dokument, Kapitel, Seite).

### 10.11 Lokale, kostenbewusste Architektur & Modellauswahl

| Stufe | Modell / Komponente | Ausführung | Kosten |
|---|---|---|---|
| Parsing & Chunking | PyMuPDF, Python-Algorithmen | CPU lokal | 0 € |
| Embeddings | `nomic-embed-text` | Ollama lokal | 0 € |
| Vector Store | ChromaDB (HNSW Cosine) | Disk lokal | 0 € |
| Bild- & Tabellen-Enrichment | `gemma3:4b` | Ollama lokal | 0 € |
| Query-Rewriting | `phi3:medium` / `llama3.2` | Ollama lokal | 0 € |
| Final Answer Generation | `llama3.1:8b` (lokal) oder Claude Sonnet / GPT-4o | lokal / Cloud-API | 0 € / gering (nur bei Klick) |

Auswahlkriterien („spezialisierte, schlanke Modelle schlagen oft träge Allrounder in Latenz, VRAM-Bedarf und Präzision“):
1. **Embedding** (`nomic-embed-text`): MTEB-Benchmark, Dimension (768 vs. 1536), langes Kontextfenster (8k Tokens), Cosine-Distanz-Stabilität
2. **Multimodal/Vision** (`gemma3:4b`, `llava`, `minicpm-v`): OCR in Diagrammen, Erkennung von Tabellenstrukturen in Bildern, geringer VRAM-Footprint
3. **Query-Rewriting & Klassifikation** (`phi3:medium`, `qwen2.5:7b`): extrem geringe Latenz (< 500 ms), präzises Befolgen von Formatvorgaben (Few-Shot), kein Ausufern
4. **Agentic Reasoning & Tool-Calling** (`llama3.1:8b`, `qwen2.5:32b`, `qwen3-coder`): zuverlässiges JSON-Ausgabeformat, Befolgung von ReAct-Loops, strikte Einhaltung der Evidenz

Kernbotschaft: „Gezieltes Prompting + saubere Evidenz schlägt reines Modell-Gewicht!“
- Kleines lokales Modell (3B–8B) reicht für: faktenbasierte Extraktion aus bereitgestellten Chunks, Formatierung (JSON, Markdown-Tabellen) & Query-Erweiterung, strikte Datensouveränität.
- Cloud-Switch lohnt sich bei: komplexen multilingualen Nuancen bzw. stark verschachteltem Multi-Hop-Reasoning, extrem langen Kontexten mit dutzenden Dokumenten, Live-Vergleich im Prototyp per Knopfdruck. (Siehe Hinweis in 4.1.)

### 10.12 Zwei Agenten-Varianten im Referenzprototyp

**Variante 1 – Evidence-First Workflow (Modulare Pipeline, „IST“):**
Frage → Hybrid Retrieval (Vektor + Hierarchie) → Evidenz-Panel (Dokumente, Kapitel, Tabellen, Bilder) → Nutzer prüft Relevanz → [Button: Finale Antwort generieren] → LLM-Synthese.
Vorteile: Transparenz (Quellen/Seiten vor Modellausführung), Kostenkontrolle (LLM nur bei relevanter Evidenz), Halluzinationsschutz (nur geprüfte Evidenz-Chunks).
Eigenschaften: statischer Kontrollfluss in Python, fixes Hybrid-Retrieval (Top-k), deterministisch, schnell, extrem günstig.

**Variante 2 – Agentic RAG mit ReAct & Tool-Calling („NEU“):**
ReAct (Yao et al., 2022): LLM als zentraler Controller kombiniert Denkschritte (Thought) mit Aktionen (Action) → Observation → Schleife bis Final Answer.
Eigenschaften: dynamische LLM-Orchestrierung, autonomer Werkzeugaufruf nach Bedarf, Multi-Hop-Iteration & Folgerecherche, mächtig für Tabellen, Bilder & Berechnungen.

Die 5 Werkzeuge (`src/agent/tools.py`):
1. `search_documents(query, top_k)` – semantische Suche über Fließtext und Überschriften
2. `search_tables(query, top_k)` – gezielte Suche in serialisierten Tabellenzeilen
3. `search_images(query, top_k)` – Suche in Bild- und Screenshot-Captions
4. `get_document_outline(filename_filter)` – Dokumentgliederung und Kapitelstruktur
5. `calculate(expression)` – sichere Ausführung arithmetischer Berechnungen

Beispiel-ReAct-Zyklus: „Berechne die CP-Summe der Module im 3. Studienjahr“ → `search_tables(...)` → CP-Werte → `calculate("5 + 8 + 5 + …")` → `{"result": 60}` → Final Answer.

Beide Prototypen live testbar über `app.py` oder `python compare_prototypes.py`.

**Testergebnisse Pipeline vs. Agentic RAG (5 standardisierte Testfragen, `compare_prototypes.py`):**

| Test-Kategorie | Modulare Pipeline (P1) | Agentic RAG (P2) |
|---|---|---|
| Tabellen & Noten | liefert Top-8 Chunks; Detailbezug hängt von Distanz ab | wählt gezielt `search_tables`, findet Zeilen präzise |
| Prozess / Text | schnell & treffsicher bei klaren Überschriften | sucht iterativ Text & Gliederung (`get_document_outline`) |
| Bilder / Screenshots | findet Bilder nur, wenn im Vektor-Top-k | wählt gezielt `search_images`, analysiert Captions |
| Multi-Hop & Rechnen | kann nicht rechnen, kombiniert nur Textfragmente | kombiniert `search_tables` mit `calculate` |
| Negativ-Test | erkennt fehlenden Kontext zuverlässig | erkennt nach gezielter Suche fehlende Quellen |

---

## 11. Abgabe-Checkliste

**Formales**
- [x] Konzeptentwurf ca. 5–8 Seiten (oder äquivalente Markdown-/Notebook-Doku) (8 Seiten, Endkontrolle 2026-11-19)
- [ ] Abgabe über Moodle (<https://moodle.dhbw.de/mod/assign/view.php?id=592218>)
- [ ] Optional: lauffähiger Code-Prototyp / UI-Mockup beigefügt (praktisch empfohlen, siehe 2.1)

**Grundanforderungen an den Agenten**
- [x] Läuft lokal / offline (Ollama o. Ä.; Cloud höchstens optionaler, abschaltbarer Vergleich)
- [x] Nutzt eine modulare RAG-Pipeline (nicht nur naiver Splitter + Top-k)
- [x] Ist agentisch (Reasoning, Tools, ggf. Planning/Memory; z. B. ReAct-Loop)
- [x] Ist systematisch getestet / validiert

**Inhalt nach Bewertungskriterien**
- [x] Problemverständnis & Use Case (15 %): konkretes Problem, Zielgruppe, Nutzen, Begründung „lokal“
- [x] Architekturentwurf (25 %): Komponenten, Kontrollfluss, Modellauswahl mit Begründung, Kosten
- [x] RAG- & Retrieval-Konzept (20 %): Embedding, Vektor-Store, Retrieval-Strategie, Quellen/Zitation
- [x] GraphRAG-Entscheidung begründet (Entitäten, Beziehungen, bessere Fragen, warum klassisches RAG ggf. reicht, Kosten/Komplexität)
- [x] Vorverarbeitung & Datenstrukturen (15 %): Datenformate/-qualität, Parsing, Chunking, Enrichment, JSON-Zwischenformat, Metadaten
- [x] Tool-Strategie: benötigte Tools/Funktionen beschrieben
- [x] Test- & Evaluationsstrategie (15 %): 5 Standardfragen, 2 komplexe Grenzfälle, 2 Negativfragen
- [x] **Abschnitt Testmodul:** umgesetzt, beschrieben, genutzt → Qualitätsaussage; Framework-KPIs (z. B. RAGAS, synthetische Testdaten) und/oder eigene kontextspezifische Testszenarien; Ergebnisse
- [ ] Literaturbezug & Reflexion (10 %): Bezug zu Grundlagen- und aktuellen Papern; kritische Reflexion, Grenzen, Ausblick (Kapitel 6 seit 2026-11-20 entfallen, Einordnung, Grenzen und knapper Ausblick in Kapitel 4/5, ISS-106; fünf zitierte Paper, davon zwei aus 2026; Grundlagen-Paper ReAct, Gao et al., RAGAS, aktuelle Paper Xiang et al. und Ferrazzi et al.; Häkchen erst, wenn der Nutzer die Paper selbst gesichtet hat, ISS-099)

**Verständnis & Eigenleistung**
- [ ] Bei jedem Meilenstein Reverse Engineering + Whitebox-Funktions- und Modultests durchgeführt
- [ ] Jede Code-Datei, jeder Technologie-Baustein, alle Funktionen, Datenstrukturen, Datenflüsse und Bibliotheken nachvollzogen
- [ ] Dokument zeigt tiefes Verständnis von Konzept (logisch) und Prototyp (technisch)
- [ ] Dokument in eigener Sprache formuliert
- [ ] Empfohlen: Selbststudium „Reverse Engineering in der Programmierung / beim Vibecoden“

---

## Anhang A: Originalwortlaut der Professor-Hinweise

> **Zusammenfassung aller Anforderungen:**
>
> In den Folien stand geschrieben:
> [Konzeptentwurf](https://moodle.dhbw.de/mod/assign/view.php?id=592218) für einen eigenen KI-Agenten-Prototyp
>
> * Format: ca. 5–8 Seiten (oder äquivalente Markdown-/Notebook-Dokumentation)
> * Fokus: Technisch fundierter Architekturentwurf, Datenaufbereitung, Tool-Strategie, Testkonzept
> * Optional: Lauffähiger Code-Prototyp / UI-Mocku
>
> Außerdem haben wir Ihnen die Anforderungen mitgeteilt, dass Ihr KI-Agent grundsätzlich
>
> * lokal / offline laufen muss,
> * eine modulare RAG-Pipeline nutzen muss,
> * agentisch sein soll,
> * systematisch getestet / validiert sein soll.
>
> Ich möchte dazu noch folgendes ergänzen:
>
> Die Entwicklung eines solchen KI-Agenten-Prototyps kann sehr gut mit einem KI-Assistenten (u.a. Vibe-Coding-Clients) betrieben werden. Das ist auch mit unseren Lernzielen kompatibel, nämlich, die Anforderungen an ein solches System zu verstehen und zu prompten (auf Basis Ihrer eigenen Idee). Gleichzeitig ist es aber auch unser Ziel, dass Sie die Zwischenergebnisse und den Prototyp verstanden haben.
> Ich möchte Ihnen daher raten, dass Sie - im Falle von intensiver Kooperation mit einem KI-Assistenten - immer wieder "Reverse Engineering" betreiben. Sie sollten bei jedem Meilenstein analysieren und testen (Whitebox-Funktions- und Modultests), was hat mir der Assistent da jetzt genau geliefert (bis hin zu der atomaren Struktur, d.h. Datenflüsse, Funktionen, Code-Dateien, Bibliotheken, ...). Das Konzept (logisch) und den Prototyp (technisch) sollten Sie in all seinen "Körperteilen" verstanden haben.
> Darauf werde ich bei der Lektüre Ihres ausformulierten Dokuments achten. Auch, ob es in einer Sprache geschrieben ist, die "von Ihnen kommt" :-)
>
> **1. Testmodul für RAG-KI-Agenten** - Zusätzliche Anforderung bezüglich Prüfungsleistung (Abgabe: [Konzeptentwurf](https://moodle.dhbw.de/mod/assign/view.php?id=592218) / Prototyp):
> Es soll ein Abschnitt inkludiert werden, in dem ein umgesetztes Testmodul beschrieben wird. Das Testmodul soll dazu genutzt worden sein, um dem eigenen Prototyp eine "Qualität" zuschreiben zu können. Wir haben darüber gesprochen, dass es einerseits ganze Test-Frameworks mit etablierten KPIs gibt (z.B. RAGAS), die häufig auf synthetische Testdatensätze aufbauen. Andererseits kann es zielführend sein, ergänzend eigenen Kontext-spezifische Testszenarien mit sinnvollen Testfragen durchzuführen.
>
> **2. Reverse Engineering**
> Wichtig für die Bewertung der Prüfungsleistung ist, dass ich bei der Lektüre der Entwürfe den Eindruck gewinne, dass Sie Ihre (gerne mit KI-generierten Ergebnisse) zumindest "rückwärts" umfassend und tiefsehend verstanden haben.
> Es ist also sehr klug, wenn sie sich (gerne auch mit KI-Assistenz) gleich nach Fertigstellung des Prototyps und des Testmoduls rückwärts (reverse) in alle Details (insbesondere jeden Code-Datei, jeden Technologie-Baustein hinreichend einarbeiten und insbesondere Funktionen, Datenstrukturen und Datenflüsse nachvollziehen).
>
> Die Reverse Engineering Philosophie gewinnt übrigens in Zeiten der generativen KI zunehmend (auch außerhalb der Ingenieurwissenschaften) an Bedeutung als Werkzeug des Verständnis der KI-generierten Systeme. Ich empfehle daher auch einen separate Selbststudium-Einheit, z.B. zu "Reverse Engineering ... in der Programmierung" oder " ... beim Vibecoden).
