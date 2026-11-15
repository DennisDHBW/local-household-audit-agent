# ADR-0011: Aufbau des Testmoduls (B0, P1, P2 und eigene Metriken)

- **Status:** akzeptiert (Technik mit Fakes getestet; erster Lauf RUN-007)
- **Datum:** 2026-11-14
- **Meilenstein:** M6a

## Kontext
`concept.md` 11 verlangt einen Vergleich von drei Varianten (B0 Volltext, P1 Pipeline, P2 Agent) über den 12-Fragen-Katalog mit eigenen Metriken und RAGAS. Bis M5 gab es nur das Retrieval von P1 und den Agenten P2; Synthese für P1 und B0 fehlten (ISS-037). Rahmen: nur CPU, Prefill ca. 18 Token/s, `num_ctx` 8192, eine Antwort kostet 1–7 Minuten. Der Korpus hat ca. 60.000 Zeichen Seitentext (geschätzt 17.000–20.000 Token) und passt damit nicht in den Kontext.

## Entscheidung
Paket `audit_agent.evaluation` mit getrennten Schritten `generate` (braucht Ollama, schreibt Antworten) und `score` (ohne Ollama, beliebig wiederholbar).

1. **Testset:** Die Fragen kommen direkt aus `dataset/ground_truth.yaml` (`select_questions`); ein eigenes `testset.yaml` entfällt (DRY).
2. **Gleiche Bedingungen:** Alle Varianten nutzen dasselbe Modell, denselben `ChatClient`, dieselben Chat-Optionen (`chat_arguments`: `num_ctx`, `num_predict`, Temperatur 0) und dasselbe Belegformat `[n] Datei, S. x`. P1 und B0 bekommen einen eigenen kurzen Systemprompt mit den Regeln des Agenten (Belegnummern, brutto, ehrliche Lücke), aber ohne Tools.
3. **P1:** ein `Retriever.search` mit der Frage als Anfrage, ohne Filter, mit Hierarchie-Boost, Top-5 über Text, Tabellenzeilen und Bildbeschreibungen (wie die drei Suchtools des Agenten zusammen), Treffer auf 600 Zeichen gekürzt; danach genau ein Modellaufruf.
4. **B0 (Variante A):** Seitentext (Text, Überschriften, Tabellenzeilen, keine KI-Texte) je Seite als Block, Dateien in Katalogreihenfolge, bis das Budget `num_ctx − num_predict − Reserve − Prompt` voll ist. Gezählt wird mit der Schätzung des Agenten (2,4 Zeichen/Token, gemessen in RUN-007), denn ein zu langer Prompt wird von Ollama still auf die Hälfte gekürzt (ISS-041). Der Kontext ist für alle Fragen gleich und steht im Systemprompt vor der Frage, damit Ollama ihn als Präfix wiederverwenden kann. Welche Dateien hineinpassen, steht in `manifest.json` (Stand M6a: 6 von 30, Dateien 01–06).
5. **P2:** der Agent aus M5 unverändert; sein `AgentRun` wird in das gemeinsame Format `VariantAnswer` übersetzt, jeder Schritt landet zusätzlich in `p2-<Frage>.jsonl`.
6. **Speicher:** Vor jeder Variante werden die Modelle entladen (Modell und Prompt-Cache beginnen neu; ISS-043).
7. **Speicherung:** `data/eval/<run>/answers-<variante>.jsonl`, eine Zeile je Antwort, sofort geschrieben. Ein abgebrochener Lauf wird mit demselben Befehl fortgesetzt; ein Lauf darf nur ein Modell enthalten (Fail fast).
8. **Eigene Metriken (deterministisch):** Fakten (Zahl in der Antwort, Belegnummern vorher entfernt; Text als ganzes Wort), Quellen-Präzision und -Recall auf Datei + Seite über die zitierten `[n]`, erfundene Belegnummern, Ablenker in Zitaten und im Kontext (`is_noise_document`), Tool-Wahl (gültige Aufrufe), Filterwahl (eigener Filter schließt eine erwartete Quelle aus, nach den Regeln der Tools), Negativerkennung (`is_gap_answer`), Prüfurteil ja/nein aus dem ersten Satz → Fehlererkennung und Fehlalarm, Latenz und Prompt-Token. Ergebnis: `scores.json` und `report.md` (Tabelle Variante × Metrik, Matrix Frage × Variante, alle Antworten).
9. **RAGAS** folgt in M6b auf denselben gespeicherten Antworten (umgesetzt in ADR-0012).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| B0 mit `num_ctx` ca. 24.000 (Variante B) | Ganzer Korpus im Prompt, aber ca. 8 GB RAM nur für dieses Modell und rund 18 Minuten erster Prefill; B0 soll zeigen, was ohne RAG auf dieser Hardware geht |
| B0 mit gleich großem Anteil je Dokument | Schneidet Tabellen mitten durch; die Reihenfolge-Variante ist einfacher zu erklären |
| P1 mit Filtern aus der Frage | Wäre eine zweite, handgebaute Agentik; P1 soll die einfache Pipeline ohne Entscheidungen sein |
| LLM-Bewerter für alle Metriken | Langsam und selbst fehleranfällig; die eigenen Metriken sind nachvollziehbar und wiederholbar, RAGAS ergänzt sie |
| Antworten und Bewertung in einem Schritt | Jede Änderung an einer Metrik würde stundenlange Neuläufe erzwingen |

## Konsequenzen
- Positiv: Bewertung ohne Ollama in Sekunden; Varianten unterscheiden sich nur in der Belegauswahl; Nachtläufe sind fortsetzbar; 26 neue Tests mit Fakes.
- Negativ / Preis: Fakten- und Urteilsprüfung sind Heuristiken (ISS-038); B0 kann Fragen zu Dateien 09–30 nicht beantworten (ISS-039); Fehlererkennung deckt nur E1 ab (ISS-040).
- Zu testen: RUN-007 (3 Fragen × 3 Varianten); in M6b alle 12 Fragen mit `llama3.1:8b` und `qwen2.5:7b`, ob die Präfix-Wiederverwendung bei B0 greift (ISS-005).

## Belege
ISS-037 bis ISS-043; RUN-007 (abgebrochen, B0 gekürzt), RUN-008; `concept.md` 7.1, 11.
