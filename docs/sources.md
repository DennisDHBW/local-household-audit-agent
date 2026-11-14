# Literatur & Quellen

> Pflicht laut Vorlesung: mindestens 3 Grundlagen- und 3 aktuelle Paper sichten. Literaturbezug zählt 10 %.
> Nicht das ganze Paper lesen müssen: Abstract, Einleitung, Abbildungen, Fazit reichen meist. Die Spalte „Kernaussage“ kann Claude (z. B. mit dem Skill deep-research) vorbereiten; die Spalte „Bezug zu meinem Projekt“ ist das, was in der Ausarbeitung zählt.
> arXiv-Nummern vor dem Zitieren auf arxiv.org prüfen. BibTeX direkt in `references.bib` übernehmen (für LaTeX).

## Status
`offen` · `überflogen` · `gelesen` · `zitiert`

## Grundlagen (aus der Vorlesung)

| Kürzel | Titel | Autoren, Jahr | arXiv | Status | Kernaussage | Bezug zu meinem Projekt |
|---|---|---|---|---|---|---|
| yao2022react | ReAct: Synergizing Reasoning and Acting in Language Models | Yao et al., 2022 | 2210.03629 | offen | | Agenten-Schleife (P2) |
| schick2023toolformer | Toolformer: Language Models Can Teach Themselves to Use Tools | Schick et al., 2023 | 2302.04761 | offen | | Tool-Nutzung, `calculate` |
| lewis2020rag | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al., 2020 | 2005.11401 | offen | | RAG-Grundidee |
| gao2023ragsurvey | Retrieval-Augmented Generation for Large Language Models: A Survey | Gao et al., 2023 | 2312.10997 | offen | | Naive vs. Advanced vs. Modular RAG |
| asai2023selfrag | Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection | Asai et al., 2023 | 2310.11511 | offen | | Selbstprüfung vor der Antwort |

## Evaluation

| Kürzel | Titel | Autoren, Jahr | arXiv | Status | Kernaussage | Bezug |
|---|---|---|---|---|---|---|
| es2023ragas | RAGAS: Automated Evaluation of Retrieval Augmented Generation | Es et al., 2023 | 2309.15217 | offen | | Testmodul, Metriken |

## Aktuelle Paper (selbst recherchieren, mind. 3)

Suchideen: Tabellen in RAG / Table QA, Multimodal RAG mit Diagrammen, Small Language Models für Tool-Calling, LLM-as-a-Judge (Zuverlässigkeit), Document Layout Parsing.

| Kürzel | Titel | Autoren, Jahr | Quelle | Status | Kernaussage | Bezug |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## Technische Dokumentation (nicht wissenschaftlich, aber zitierbar)

| Quelle | Wofür |
|---|---|
| Ollama-Dokumentation (Tool-Calling, `num_ctx`, `keep_alive`) | Modellbetrieb |
| ChromaDB-Dokumentation (Metadatenfilter `where`) | Retrieval |
| PyMuPDF-Dokumentation (`find_tables`) | Parser |
| nomic-embed-text Model Card (Präfixe `search_document:` / `search_query:`) | Embeddings |
| RAGAS-Dokumentation | Testmodul |
