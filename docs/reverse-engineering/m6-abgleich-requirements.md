# M6 – Abgleich mit `requirements.md` (vor Tag v1.0.0)

**Datum:** 2026-11-17 · **Stand:** `f3e14f4` + Reverse-Engineering-Notizen M6

| Anforderung (Abschnitt in `requirements.md`) | Stand | Beleg / Lücke |
|---|---|---|
| 4.1 Lokal / offline (MUSS) | erfüllt | Alle Modelle über Ollama auf dem Laptop; RAGAS-Richter lokal über `/v1`, Telemetrie mit `RAGAS_DO_NOT_TRACK` aus (ADR-0001, ADR-0012) |
| 4.2 Modulare RAG-Pipeline (MUSS) | erfüllt | Parser, typisierte Chunks, Enrichment, Hierarchie-Prefix, Filter und Boost (M2–M4); in M6 Größen-Anfrage mit Sparten-Filter (ADR-0017) |
| 4.3 Agentisch (MUSS) | erfüllt | ReAct-Schleife mit fünf Werkzeugen, Rückfragen, Wiederholungssperre (M5, ADR-0014/0015) |
| 4.4 Systematisch getestet / validiert (MUSS) | erfüllt | 381 Unit-Tests, Testmodul mit 21 dokumentierten Läufen (RUN-000 bis RUN-021) |
| 5.6 Testset 5 Standard / 2 Grenzfall / 2 Negativ (MUSS) | erfüllt | `ground_truth.yaml`: 5 Standard, 4 Grenzfälle, 2 Negativ, 3 Zusatz |
| 6 Testmodul umgesetzt und genutzt (MUSS) | erfüllt | `audit_agent.evaluation` (`generate`, `score`, `ragas`), Varianten B0/P1/P2, Tabelle Variante × Metrik in `report.md` |
| 6 Etabliertes Framework mit KPIs (RAGAS) | teilweise | Nur Faithfulness und Context Recall; Werte nur für RUN-009 bis RUN-011 (alter Code), nicht für den Stand v1.0.0 (ISS-082) |
| 6 Eigene kontextspezifische Szenarien | erfüllt | Eingebaute Fehler E1–E3, Fehlalarm-Fragen, Ablenkdokumente; deterministische Metriken plus Handprüfung (ISS-050) |
| 6 Ergebnisse → Qualitätsaussage | erfüllt mit Grenzen | RUN-020: P1 nach Handprüfung 8 von 14; RUN-021: P2 6 von 14; eingebaute Fehler 0 von 3. B0 zuletzt in RUN-010/011 gemessen (anderer Code-Stand) |
| 7 Reverse Engineering je Meilenstein (SOLL, bewertungsrelevant) | teilweise | Notizen M0–M6 vorbereitet (M6 in drei Runden); Antworten und Abschnitte 5–7 des Nutzers für M0, M2–M6 offen |
| 5.5 GraphRAG-Entscheidung (MUSS) | erfüllt (Konzept) | ADR-0003 |
| 5.7 Literaturbezug | bewusst nicht bedient | Entscheidung 2026-11-14 (requirements.md 2.2) |
| Ausarbeitung (Phase 2) | offen | M7 |

**Fazit:** Die MUSS-Anforderungen an Prototyp und Testmodul sind erfüllt. Zwei Lücken bleiben dokumentiert: RAGAS für den aktuellen Stand (ISS-082) und die eigenen Antworten im Reverse Engineering. Die zweite kann nur der Nutzer schließen. Die schwachen Ergebnisse (G1, G3, 0 von 3 eingebauten Fehlern) sind ein Messergebnis und kein Verstoß gegen eine Anforderung. Sie gehören in die Reflexion.
