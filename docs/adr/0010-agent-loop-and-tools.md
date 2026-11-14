# ADR-0010: Agentenschleife und Werkzeuge (P2)

- **Status:** akzeptiert (Technik in RUN-005/006 bestätigt; Antwortqualität offen bis M6)
- **Datum:** 2026-11-14
- **Meilenstein:** M5

## Kontext
M4 liefert einen `Retriever` mit Metadatenfilter. M5 setzt darauf den Agenten P2 (ReAct) nach `concept.md` 7. Rahmen: nur CPU, Prefill ca. 18 Token/s (ISS-001), `num_ctx` 8192, Agent-Modell `llama3.1:8b`, natives Tool-Calling (ADR-0006). Offen waren: Wie sehen die Tools aus, wo werden die Regeln aus ISS-006, ISS-007 und ISS-025 durchgesetzt, wie wird die Schleife begrenzt, und wie wird sie protokolliert?

## Entscheidung
Das Paket `audit_agent.agent` trennt Rechner (`calculator.py`), Tools (`tools.py`), Schleife (`loop.py`), Prompts (`prompts.py`), Protokoll (`models.py`, `log.py`), Auswertung (`report.py`), Verdrahtung (`factory.py`), CLI (`__main__.py`) und Oberfläche (`evidence_view.py`, `app.py`).

1. **Sechs Tools** wie im Konzept: `list_documents`, `search_documents` (nur `text`), `search_tables` (`table_row` und `table_summary`), `search_images` (nur `image`), `get_document_outline`, `calculate`. Die Suchtools sind dünne Hüllen um `Retriever.search` mit festem `chunk_types`; die Trennung der Texttypen geschieht also im Code und nicht durch das Modell (ISS-006: Verwechslung wird gemessen, nicht umgangen).
2. **Argumente:** je Tool ein pydantic-Modell. Daraus entsteht das JSON-Schema für Ollama (`tool_parameters` löst `$ref` auf und entfernt `title` und `default`), und mit demselben Modell werden die Aufrufe geprüft. Flache Filterargumente `utility_type`, `doc_type`, `year` statt eines verschachtelten `filter`-Objekts; `top_k` ist fest (YAGNI, weniger Argumente für kleine Modelle). Liberal beim Lesen (Postel): leere Werte und `"null"` werden verworfen, ein verschachteltes `filter` wird abgeflacht, unbekannte Argumente werden ignoriert, `"2024"` wird zu `2024`.
3. **Regeln im Code statt nur im Prompt:**
   - ISS-025: Der Jahresfilter gilt nur zusammen mit `bill`, `notice` oder `payment_plan` (Dokumente mit Abrechnungszeitraum); sonst wird er verworfen und die Beobachtung sagt es.
   - ISS-007: Liefert eine Suche mit Sparte oder Dokumenttyp (ohne Jahr) null Treffer, wird sie ohne Filter wiederholt und die Beobachtung nennt das. Mit Jahresfilter gibt es keine Wiederholung: Dann ist „keine Treffer“ ein echtes Negativ (N1: Stromrechnung 2023), und die Beobachtung verweist auf `list_documents`.
4. **Schleife:** Natives Tool-Calling, Kontrollfluss ReAct. Jeder Aufruf zählt gegen `max_tool_calls` (6), auch ein ungültiger; der Fehler geht als Beobachtung zurück („Korrekturversuch“ ist damit der nächste Aufruf des Modells). Beim Limit, oder wenn der Kontext bis auf `num_predict` + Reserve voll ist (geschätzt aus dem Text der Nachrichten und der Tool-Schemas, Zeichen/3; `prompt_eval_count` taugt nicht, RUN-005), folgt ein letzter Modellaufruf ohne Tools mit der Aufforderung zu antworten. Ruft das Modell im selben Zug mehr Tools als erlaubt, werden die überzähligen mit einer Fehlermeldung beantwortet.
5. **Belegnummern:** Jeder Treffer bekommt je Lauf eine Nummer (`EvidenceBook`), der Chunk behält sie bei erneutem Fund. Das Modell zitiert `[3]`; die Oberfläche zeigt dieselben Nummern. So lässt sich jede Zahl der Antwort auf einen Treffer zurückführen.
6. **Kürzung:** Treffertexte erreichen das Modell mit höchstens 600 Zeichen (Prefill-Kosten), die Evidenz zeigt den vollen Text (ISS-031).
7. **Protokoll:** Jeder Schritt (Modellaufruf mit Prompt-Token, Prefill- und Decode-Zeit; Tool-Aufruf mit Argumenten und Beobachtung) wird sofort als JSON-Zeile in `data/eval/<run>/agent-<Frage>.jsonl` geschrieben, am Ende folgt eine Zusammenfassungszeile. `agent.md` und `agent.json` fassen einen `run-set` zusammen, mit grober Prüfung gegen die Ground Truth (Tools, Quellen, Zahlen, ehrliche Lücke).
8. **Anpassungen nach RUN-005:** (a) `search_tables` liefert dem Modell nur `table_row`; die KI-Zusammenfassungen bleiben im Index, sind aber im Agenten abgeschaltet (`include_table_summaries`), weil das Modell eine als „kein Beleg“ gekennzeichnete Summary mit Nettowerten zitierte (ISS-035). (b) Eine Antwort „keine Angaben“ nach weniger als 2 Werkzeugaufrufen wird einmal hinterfragt („suche ohne Filter, prüfe mit `list_documents`“, Schritt `nudge` im Log; ISS-036). (c) Die Fehlermeldung bei ungültigen Argumenten nennt den richtigen Aufruf, z. B. `calculate(expression*)`. (d) System-Prompt: Preise brutto, Vorjahreswerte stehen im Diagramm.
9. **Oberfläche:** Streamlit zeigt die Belege schon während des Laufs (nach jedem Tool-Schritt), danach Antwort und Schrittverlauf (`evidence_first` aus `concept.md` 6).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Ein gemeinsames Suchtool mit `chunk_type`-Argument (ISS-006) | Ein Argument mehr, das das Modell raten muss; die getrennten Tools entsprechen dem Konzept. Falls RUN-005/M6 häufige Fehlwahl zeigen, wird umgestellt |
| Filter nur per Prompt steuern | In RUN-000 setzten beide Modelle ungefragt Filter (ISS-007); eine Regel im Code ist zuverlässiger als eine Bitte |
| Automatische Wiederholung ohne Jahresfilter | Würde für Negativfragen (Rechnung 2023) Treffer aus 2024/2025 liefern, die das Modell fälschlich verwenden könnte |
| Tools immer ohne Treffer-Kürzung | 5 Treffer à 1.500 Zeichen sind ca. 2.000 Token, bei 18 Token/s rund 110 s Prefill je Suche |
| Log erst am Ende schreiben | Ein Lauf dauert Minuten; bei Abbruch wäre alles verloren |
| LangChain/LlamaIndex-Agent | Mehr Abstraktion als nötig; die Schleife hat unter 200 Zeilen und ist für das Reverse Engineering lesbar |

## Konsequenzen
- Positiv: Die Schleife ist ohne Ollama testbar (Fake-Client mit Skript), jede Regel hat einen Test. Das Log erlaubt, jeden Schritt zu erklären (Reverse-Engineering-Checkpoint M5).
- Negativ / Preis: Der Prompt ist groß (Tool-Schemas ca. 6.000 Zeichen plus System-Prompt, ISS-030); das erzwungene Schlussantwort-Ende ohne Tools ändert den Prompt-Anfang und kostet einen vollen Prefill; Kürzung kann die gesuchte Stelle abschneiden (ISS-031); der Wiederholungsfilter bleibt eine Heuristik (ISS-032).
- Zu testen: Tool-Wahl und Filter in RUN-005 (4 Fragen) und M6 (12 Fragen, beide Modelle); ob die Präfix-Wiederverwendung greift (ISS-005); ob die Beobachtungen in `num_ctx` passen.

## Belege
`tests/test_agent_tools.py`, `tests/test_agent_loop.py`, RUN-005 in `evaluation-log.md`, ISS-005 bis ISS-007, ISS-025, ISS-030 bis ISS-034.
