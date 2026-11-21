# M8 – Abgleich mit `requirements.md` (vor Tag v2.0.0)

**Datum:** 2026-11-21 · **Stand:** `7cc1ae7` (nach Auswertung run-028)

| Anforderung (Abschnitt in `requirements.md`) | Stand | Beleg / Lücke |
|---|---|---|
| 4.1 Lokal / offline (MUSS) | erfüllt | Alle Modelle über Ollama auf dem Laptop; Dokumente 31–35 lokal erzeugt (ADR-0001, ADR-0005) |
| 4.2 Modulare RAG-Pipeline (MUSS) | erfüllt | M2–M4 unverändert; neu der Faktenspeicher mit Quellen-Chunk je Fakt (ADR-0018) |
| 4.3 Agentisch (MUSS) | erfüllt mit Einschränkung | Planungswerkzeug, acht Werkzeuge, Selbstprüfung vor der Antwort, Tabellen und Grafiken (ADR-0019); die Werkzeugauswahl hängt aber an Wortlisten (ADR-0020, ISS-126) |
| 4.4 Systematisch getestet (MUSS) | erfüllt | 443 Unit-Tests; RUN-022 bis RUN-028 |
| 5.6 Testset 5 Standard / 2 Grenzfall / 2 Negativ (MUSS) | erfüllt | 21 Entwicklungsfragen in `ground_truth.yaml`, darunter S1–S5 (Standard), G1–G4 (Grenzfälle), N1–N2 (Negativ), dazu Z-, H-, W- und V-Fragen und 8 zurückgehaltene Fragen T1–T8 |
| 6 Testmodul umgesetzt und genutzt (MUSS) | erfüllt | B0/P1/P2 auf Entwicklungs- und zurückgehaltenen Fragen; Kennzahlen zu Artefakten und Agentik (`agentics.json`) |
| 6 Etabliertes Framework (RAGAS) | nicht für M8 gemessen | offene Entscheidung (3 h je Lauf); letzte Werte für v1.0.0 |
| 6 Ergebnisse → Qualitätsaussage | erfüllt mit Grenzen | run-028: P2 nach Handprüfung 4 + 2 Grenzfälle von 8, P1 2 + 1, B0 1; 8 Fragen, eine Frage = 12,5 Prozentpunkte (ISS-108) |
| 7 Reverse Engineering (SOLL) | offen | Runde M8 wird mit M9 zusammengelegt, weil M9 den Agenten umbaut |
| 5.5 GraphRAG-Entscheidung (MUSS) | erfüllt (Konzept) | ADR-0003 |
| 5.7 Literaturbezug | erfüllt für die Ausarbeitung | fünf Quellen (Entscheidung 2026-11-20, ISS-103) |
| Ausarbeitung (Phase 2) | Zwischenstand | wird nach M9 neu überarbeitet (ISS-107) |

**Fazit:** Die MUSS-Anforderungen sind mit dem Stand v2.0.0 erfüllt. Die Einschränkung bei 4.3 ist inhaltlich: Die Steuerung ist zum Teil Wortlisten-Code und bricht bei anderem Wortlaut ein (run-028). Genau dort setzt M9 an (`docs/m9-plan.md`, ADR-0022).
