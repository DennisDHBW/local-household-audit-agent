# ADR-0009: Aufbau von Index und Suche (P1)

- **Status:** akzeptiert
- **Datum:** 2026-11-14
- **Meilenstein:** M4

## Kontext
M2 und M3 liefern 629 Chunks (82 Überschriften, 178 Text, 299 Tabellenzeilen, 65 Summaries, 5 Bilder). M4 baut daraus den Vektorindex und die Suche nach Konzept Abschnitt 6 und ADR-0002. Offen waren: Was wird eingebettet, wie sieht das Präfix aus, wie wird der Boost berechnet, und wie lassen sich Filter, Boost und die Summaries vergleichen?

## Entscheidung
Das Paket `audit_agent.retrieval` trennt Aufbau (`index.py`), Suche (`search.py`), Evidenz (`evidence.py`) und Vergleich (`compare.py`).

1. **Was eingebettet wird:** alle Chunks außer `heading` (547 von 629). Überschriften stehen schon im `heading_stack` der Chunks darunter; ein eigener Chunk würde nur kurze Treffer ohne Inhalt liefern.
2. **Text je Chunk:** `search_document: [Ordner | Datei | Kapitel > Unterkapitel] Inhalt`. Der Ordnername enthält die Sparte (`01_electricity_suedvolt`), Dokumenttyp und Sparte stehen zusätzlich als Metadaten und werden gefiltert, nicht eingebettet. Das ist kürzer als `[Sparte | Dokumenttyp | Datei | Kapitel]` aus dem Konzept. Die Anfrage wird mit `search_query: ` eingebettet (Aufgaben-Präfixe von `nomic-embed-text`).
3. **ChromaDB:** eine Collection `chunks` mit Cosinus-Abstand in `data/vectors/`, ohne eigene Embedding-Funktion (die Vektoren kommen von Ollama). Jeder Indexlauf löscht die Collection und baut sie neu auf, damit er idempotent ist. Der Index liegt unter 600 Chunks; ein Neuaufbau dauert Sekunden bis Minuten.
4. **Metadaten:** flach und ohne `None`. Datumsangaben stehen als Zahl `YYYYMMDD`, weil ChromaDB nur Zahlen vergleicht. Der Zeitraumfilter prüft die Überlappung (`period_start <= Ende` und `period_end >= Anfang`). Der `heading_stack` steht als JSON-Text im Metadatenfeld.
5. **Score:** `base_score = 1 − Abstand`, `boost = 1.5` bei Pfadtreffer sonst `1.0`, `final_score = base_score × boost`. Die Suche holt 20 Kandidaten, sortiert nach `final_score` und gibt die besten 5 zurück. Jeder Treffer enthält alle drei Zahlen und die Begriffe des Pfadtreffers.
6. **Pfadtreffer:** Die Anfrage wird kleingeschrieben, Umlaute werden ausgeschrieben (`ü` → `ue`, wie in den Dateinamen), Stoppwörter und Wörter unter 3 Zeichen entfallen. Ein Begriff trifft, wenn er im Pfadtext (Dateiname, Ordner, Überschriften) vorkommt oder wenn ein Pfadwort (mindestens 3 Buchstaben, keine Zahl) der Anfang des Begriffs ist („Stromrechnung“ trifft den Ordner „Strom“). Der Boost wird höchstens einmal angewendet.
7. **Filter und Optionen:** `MetadataFilter` (Sparte, Dokumenttyp, Vertragsnummer, Zeitraum), `chunk_types` und `require_heading` werden zu einer ChromaDB-`where`-Bedingung. So lassen sich die Summaries oder die Briefkopf-Chunks (Text ohne Kapitel) einzeln ausschalten, ohne den Index zu ändern.
8. **Kein Query-Rewriting in P1-Retrieval:** Das Konzept nennt `phi3:medium`; das Modell hat 14B und passt nicht in das Budget (ADR-0004). Umformuliert wird später vom Agenten in M5.
9. **Evidenz:** `build_evidence()` gruppiert Treffer nach Dokument und Kapitel; Typ `table_summary` heißt „KI-Zusammenfassung, kein Beleg“, Typ `image` „KI-Bildbeschreibung, kein Beleg“ (ADR-0008). Die Darstellung in M4 ist Text in der CLI; Streamlit folgt in M5 zusammen mit dem Agenten.
10. **Vergleich:** `python -m audit_agent.retrieval compare` fährt die 12 Fragen aus `ground_truth.yaml` durch sechs Konfigurationen (kein Filter/Boost, nur Boost, nur Filter, Filter + Boost, ohne Summaries, ohne Chunks ohne Kapitel) und prüft Rang der erwarteten Datei und Seite sowie Treffer aus Ablenkerdokumenten. Die Filter je Frage sind von Hand gesetzt und stehen für einen Agenten, der sie richtig wählt.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Überschriften als eigene Chunks einbetten | Kurze Treffer ohne Inhalt; der Pfad steckt bereits in den Chunks darunter |
| Sparte und Dokumenttyp zusätzlich ins Präfix | Der Ordnername trägt die Sparte, beides wird gefiltert; ein längeres Präfix verwässert den Chunk-Text |
| Inkrementelles Update des Index | Bei unter 600 Chunks unnötig; ein Neuaufbau garantiert Konsistenz mit `data/processed/` (YAGNI) |
| Boost je Treffer-Begriff (mehrfach) | Schwerer von Hand nachzurechnen; das Konzept sieht einen Multiplikator vor |
| Wörtliche Teilstring-Suche im Pfad ohne Präfixregel | „Stromrechnung“ fände den Ordner „Strom“ nicht; deutsche Komposita sind der Normalfall |
| Hybrid mit BM25 | Nicht gefordert; der Pfadboost deckt den Fall „exakter Begriff“ teilweise ab. Bleibt Option, falls RUN-004 es nahelegt |

## Konsequenzen
- Positiv: Der Score lässt sich aus drei Zahlen nachrechnen; Filter, Boost und Chunk-Auswahl sind einzeln schaltbar und damit messbar. 39 schnelle Tests ohne Ollama (Fake-Embedder, ChromaDB in `tmp_path`).
- Negativ: Die Pfadregel ist eine Heuristik (ISS-027); der Zeitraumfilter schließt Dokumente ohne Abrechnungszeitraum aus (ISS-025); der Vergleich mit handgesetzten Filtern ist optimistisch (ISS-028). Ein Neuaufbau braucht Ollama.
- Zu testen: Ob Filter und Boost die Quelle nach vorn bringen und Ablenker ausschließen, und ob Summaries und Briefkopf-Chunks helfen oder stören (RUN-004).

## Belege
`tests/test_retrieval.py`, RUN-004 in `evaluation-log.md`, ISS-025 bis ISS-028.
