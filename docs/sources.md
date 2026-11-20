# Literatur & Quellen

> Die fünf Quellen mit Status `zitiert` stehen in der Ausarbeitung. Seit 2026-11-20 gilt: höchstens fünf Quellen insgesamt (Entscheidung des Nutzers, ISS-103). Gao et al. ersetzt Self-RAG und die RAGAS-Dokumentation. BibTeX in `paper/bibliographie.bib`.
> Quellenprüfung 2026-11-20 (ISS-102): Angaben aller fünf Paper auf arxiv.org, aclanthology.org und iclr.cc bestätigt; jede Textstelle gegen das Paper geprüft, sieben Stellen präzisiert.
> Gesichtet von Claude am 2026-11-19 über Abstract, Einleitung, Ergebnisse und Fazit; Kennung und Tagung auf arxiv.org bzw. aclanthology.org geprüft. Selbst lesen: Abstract, Abbildungen, Fazit reichen meist (ISS-099).
> Neue Quellen nur mit geprüfter Kennung eintragen; ein Zitat stützt nur, was das Paper selbst sagt.

## Status
`offen` · `überflogen` · `gelesen` · `zitiert` · `verworfen`

## Zitiert in der Ausarbeitung

| Kürzel | Titel | Autoren, Jahr, Ort | Kennung | Status | Kernaussage | Bezug zu meinem Projekt |
|---|---|---|---|---|---|---|
| yao2023react | ReAct: Synergizing Reasoning and Acting in Language Models | Yao et al., ICLR 2023 | arXiv 2210.03629 | zitiert | Das Modell erzeugt abwechselnd Denkschritte und Aktionen und nutzt die Beobachtungen für den nächsten Schritt | Agentenschleife P2, Kapitel 1 und 3. Der Prompt verlangt keinen Thought, die Läufe entsprechen deshalb der Variante „Act“ des Papers (Kapitel 3, ISS-102) |
| gao2023survey | Retrieval-Augmented Generation for Large Language Models: A Survey | Gao et al., 2023 (arXiv, v5 vom 27.03.2024, „Ongoing Work“, keine Tagung) | arXiv 2312.10997 | zitiert | Drei Paradigmen: Naive RAG („Retrieve-Read“, Top-K), Advanced RAG (Vorverarbeitung wie Metadaten im Index und Query-Rewriting, Nachbearbeitung wie Reranking), Modular RAG (Module lassen sich austauschen oder umkonfigurieren, flexible Abläufe) | Steht auf der Literaturliste der Vorlesung. „Einfaches RAG“ in Kapitel 1, einzeln abschaltbare Bausteine der Suche in Kapitel 4 (ISS-103). Achtung: Filter und Query-Rewriting sind bei Gao Advanced RAG |
| es2024ragas | RAGAs: Automated Evaluation of Retrieval Augmented Generation | Es et al., EACL 2024 (System Demonstrations), S. 150–158 | arXiv 2309.15217, DOI 10.18653/v1/2024.eacl-demo.16 | zitiert | Referenzfreie Metriken Faithfulness (Antwort im abgerufenen Kontext begründet), Answer Relevance, Context Relevance | Zweite Sicht im Testmodul (Kapitel 5); Context Recall steht nicht im Paper; im Text als Metrik der RAGAS-Bibliothek ohne eigene Quelle beschrieben (ISS-101, ISS-103) |
| xiang2026graphs | When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation | Xiang et al., ICLR 2026 (Poster, bestätigt auf iclr.cc und mlanthology.org) | arXiv 2506.05690 | zitiert | GraphRAG-Bench: Graph im Vorteil bei komplexem Schließen und Zusammenfassen; bei einfacher Faktensuche ist einfaches RAG gleich gut oder besser; GraphRAG verlängert den Prompt stark (Obs. 1, 2, 8). Ausnahmen: HippoRAG2 kaum länger (ca. 1.000 statt 879 Token), im Medizin-Datensatz bei Faktensuche besser; Text und Tabelle des Papers nennen verschiedene Tokenzahlen, deshalb keine Zahl übernehmen | GraphRAG-Entscheidung (Kapitel 4). Prüffragen vergleichen zwei Werte; die Aussage gilt für die einzelnen Nachschlage-Schritte, die Beziehungen hängen an Metadaten (ISS-099) |
| ferrazzi2026agentic | Is Agentic RAG worth it? An experimental comparison of RAG approaches | Ferrazzi et al., ACL 2026 (Volume 6: Industry Track), S. 56–75 | arXiv 2601.07711, DOI 10.18653/v1/2026.acl-industry.5 | zitiert | Weder Enhanced (feste Pipeline mit Router, Query-Rewriting, Reranker) noch Agentic RAG ist generell überlegen; Agentic braucht im Mittel 3,3-mal so viele Eingabe-Token, 1,9-mal so viele Ausgabe-Token und 1,5-mal so lange (Fazit: „bis zu 3,6-mal“ so teuer). Generatoren Qwen3 0.6B bis 32B, Aufgaben Retrieval und QA (FIQA, NQ, FEVER, CQADupStack) | Agent P2 nicht besser als Pipeline P1, fast dreimal so langsam (Kapitel 5, seit Kapitel 6 entfallen ist) |

## Geprüft, nicht zitiert (Reserve und verworfen)

| Titel | Autoren, Jahr, Ort | Kennung | Status | Urteil |
|---|---|---|---|---|
| Quantifying the Latency-Accuracy Trade-off in Local Agentic RAG Workflows | Zhang et al., NeurIPS 2026 Workshop SLM-Agents | OpenReview tZTKDMOazF | überflogen | Gegenbefund: agentische Pipelines mit lokalen kleinen Modellen (u. a. Llama 3.1 8B, HotpotQA) in 10 von 12 Vergleichen besser. Reserve, bräuchte einen Satz in Kapitel 5 (Kapitel 6 entfallen) |
| Dissecting Agentic RAG: A Component Ablation for Multi-Hop QA with a Local 7B Model | Shaikh, 2026 | arXiv 2606.21553 | überflogen | `qwen2.5:7b` über Ollama; einfache feste Varianten so gut wie adaptive. Einzelautor, Preprint, nur HotpotQA, Modell zwischen den Suchschritten nicht gefragt (kein ReAct). Reserve |
| Self-Preference Bias in LLM-as-a-Judge | Wataoka et al., 2024 (NeurIPS 2024 Workshop) | arXiv 2410.21819 | überflogen | Bewertermodelle bevorzugen Texte, die ihnen vertraut sind. Reserve für Kapitel 5 (`audit-judge` = Antwortmodell) |
| Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng et al., 2023 | arXiv 2306.05685 | überflogen | Self-enhancement bias; älter als Wataoka |
| Large Language Models Cannot Self-Correct Reasoning Yet | Huang et al., ICLR 2024 | arXiv 2310.01798 | überflogen | Ohne externe Rückmeldung kaum Selbstkorrektur; passt zu den Rückfragen (Kapitel 3), bräuchte einen Satz |
| Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection | Asai et al., ICLR 2024 | arXiv 2310.11511 | überflogen | Bis 2026-11-20 zitiert (Rückfragen gegen antrainierte Selbstprüfung, Kapitel 3 und 6); wegen der Grenze von fünf Quellen entfernt, der Vergleich ist aus dem Text genommen (ISS-103) |
| From Local to Global: A Graph RAG Approach to Query-Focused Summarization | Edge et al., 2024 | arXiv 2404.16130 | überflogen | GraphRAG für Überblicksfragen über den ganzen Korpus; durch Xiang et al. ersetzt |
| RAG vs. GraphRAG: A Systematic Evaluation and Key Insights | Han et al., 2025 (v3 März 2026) | arXiv 2502.11371 | überflogen | Deckt dasselbe ab wie Xiang et al. |
| Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG | Singh et al., 2025 (v4 April 2026) | arXiv 2501.09136 | überflogen | Überblick ohne eigene Messung; für ReAct ist die Primärquelle besser |
| AI Agents That Matter | Kapoor et al., 2024 | arXiv 2407.01502 | überflogen | Kostenkontrollierte Evaluation, einfache Baselines; durch Ferrazzi et al. abgedeckt |
| Small Language Models are the Future of Agentic AI | Belcak et al. (NVIDIA), 2025 | arXiv 2506.02153 | überflogen | Positionspapier ohne eigene Messung; eigene Ergebnisse sprechen eher dagegen |
| The Berkeley Function Calling Leaderboard (BFCL) | Patil et al., ICML 2025 | PMLR 267 | überflogen | Natives Tool-Calling gegen Umweg über Textausgabe; Randaspekt |
| A Survey on LLM-as-a-Judge | Gu et al., 2024 | arXiv 2411.15594 | überflogen | Zu allgemein |
| OCR Hinders RAG | Zhang et al., 2024 | arXiv 2412.02592 | überflogen | Selbst die beste OCR mindestens 14 % hinter strukturierten Daten; Grenze ohne OCR, Randaspekt |
| Docling Technical Report | Auer et al., 2024 | arXiv 2408.09869 | überflogen | Läuft laut Report effizient auf Standardhardware; Aussage „auf der CPU langsam“ deshalb aus Kapitel 2 entfernt (ISS-100) |
| Correctness is not Faithfulness in RAG Attributions | Wallat et al., 2025 | arXiv 2412.18004 | verworfen | „Faithfulness“ heißt dort, dass das Modell sich wirklich auf die zitierten Dokumente stützt; anderer Begriff als bei RAGAS |
| Toolformer: Language Models Can Teach Themselves to Use Tools | Schick et al., 2023 | arXiv 2302.04761 | offen | Training für Tool-Nutzung; Prototyp nutzt natives Tool-Calling |
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al., 2020 | arXiv 2005.11401 | offen | RAG-Grundidee; im Text nicht nötig |

## Technische Dokumentation (nicht wissenschaftlich, aber zitierbar)

| Quelle | Wofür |
|---|---|
| Ollama-Dokumentation (Tool-Calling, `num_ctx`, `keep_alive`) | Modellbetrieb |
| ChromaDB-Dokumentation (Metadatenfilter `where`) | Retrieval |
| PyMuPDF-Dokumentation (`find_tables`) | Parser |
| nomic-embed-text Model Card (Präfixe `search_document:` / `search_query:`) | Embeddings |
| RAGAS-Dokumentation, Seite „Context Recall“ (docs.ragas.io, besucht 2026-11-19) | Testmodul; vom 2026-11-20 (ISS-102) bis zur Endprüfung zitiert, seit ISS-103 nicht mehr (höchstens fünf Quellen). Laut Code von ragas 0.4.4 urteilt der Bewerter je Aussage der Referenz |
