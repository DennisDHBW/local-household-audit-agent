# Verständnisfragen zur Ausarbeitung

> Je Kapitel 3–5 Fragen, die ein Prüfer zum Text stellen könnte. Keine Musterantworten.
> Der Nutzer liest die Kapitel und beantwortet die Fragen gesammelt, wenn alle sechs Kapitel entworfen sind (Entscheidung 2026-11-18). Die Antworten fließen danach in die Überarbeitung ein.

## Kapitel 1 – Problemstellung und Use Case

1. Warum reicht es nicht, alle Unterlagen direkt in den Prompt zu geben, und was hat B0 dazu konkret gezeigt?
2. Warum ist der Fehler in der Stromrechnung 2025 an der Rechnung allein nicht zu erkennen? Welche Schritte braucht der Agent, um ihn zu finden?
3. Warum ist ein monatlicher Verbrauchsverlauf aus Datenschutzsicht heikler als der Jahresverbrauch?
4. RAGAS sendet laut Quelltext nur Metadaten wie Anbieter und Modellname. Warum schaltet der Prototyp das trotzdem ab?
5. Was gewinnt das Projekt durch den synthetischen Korpus, und was verliert es gegenüber echter Post?

**Antworten (von mir):**

**Beim Lesen besonders prüfen:**
- Titelblatt: Bearbeitungszeitraum „November 2026“ ist aus Git abgeleitet (erster Commit 14.11.2026), nicht vorgegeben.
- Letzter Absatz: Der Hinweis „keine Rechtsberatung“ fehlt im Prototyp (ISS-088). Passt die Formulierung im Text?

## Kapitel 2 – Datenbasis und Vorverarbeitung

1. Warum nutzt der Parser von `find_tables()` nur Fläche und Zeilenbänder der Tabelle und nicht den Zelltext, den PyMuPDF selbst liefert?
2. Was ginge verloren, wenn eine Tabellenzeile ohne Spaltennamen serialisiert würde, etwa nur „Arbeitspreis ÖkoStrom | 3.100 kWh | 33,19 ct/kWh | 39,50 ct/kWh“? Welche Prüffrage wäre davon betroffen?
3. Warum steckt im Cache-Schlüssel des Enrichments der vollständige Prompt und nicht einfach die Chunk-ID?
4. Die Tabellen-Summaries enthalten nachweislich Fehler. Warum bleiben sie trotzdem im Index, und welche Chunks nutzt der Agent stattdessen als Beleg?
5. Was müsste an der Vorverarbeitung geändert werden, damit der Prototyp echte, teils gescannte Post eines anderen Anbieters verarbeiten kann?

**Antworten (von mir):**

**Beim Lesen besonders prüfen:**
- Aus Platzgründen fehlt das Problem der aneinanderstoßenden Tabellen (ISS-014, Kostenzeilen mit Spalten der Zählertabelle). Bei Bedarf in Kapitel 6 aufgreifen.
- „Eine fette erste Zeile gilt als Spaltenkopf“ ist vereinfacht: Die Regel verlangt außerdem mindestens zwei Zellen (ADR-0007, Punkt 3).
- Der Satz „8 statt 9 von 10 Testfragen“ ist ein Retrieval-Ergebnis (RUN-004). Kapitel 4 soll ihn nicht wiederholen.

## Kapitel 3 – Architektur des Agenten

1. Warum laufen Einlesen und Abfrage in getrennten Phasen, und was kann der Agent deshalb zur Abfragezeit nicht?
2. Im Protokoll steht bei keinem Werkzeugaufruf ein Thought. Ist P2 trotzdem ein ReAct-Agent, und wo steckt die Überlegung des Modells?
3. Warum hat das Zusammenlegen der beiden Suchwerkzeuge die Fragen zu Kündigungsfristen gelöst, und was hat der Agent dabei an Steuerung verloren?
4. Die Rückfragen übernehmen die Selbstprüfung im Code. Wie unterscheidet sich das von Self-RAG, und warum hat eine Rechennachfrage allein keinen eingebauten Fehler gefunden?
5. Warum kostet schon der erste Modellaufruf jeder Frage 82 bis 105 s, und wie ließe sich das verkürzen, ohne den Schutz vor Speichermangel aufzugeben?

**Antworten (von mir):**

**Beim Lesen besonders prüfen:**
- Self-RAG kommt nur als Begriff vor (keine Literatur, Entscheidung 2026-11-14). Der Satz setzt voraus, dass du erklären kannst, was Self-RAG dem Modell beibringt (Reflexionstoken) und warum hier stattdessen feste Regeln im Code stehen.
- „18 von 23 Fehlschlägen“ stammen aus RUN-010 und RUN-011 zusammen (zwei Modelle, je 14 Fragen). Der Rückgang ungültiger Aufrufe (13 auf 0) steht bewusst nicht im Text, er kam vor allem vom fehlenden `calculate` (ISS-091).
- Das Kapitel ist mit ca. 1,6 Seiten 0,1 Seiten über Budget (ISS-092). Kürzungskandidat, falls nötig: der Satz zur pydantic-Prüfung.
- Weggelassen aus Platzgründen: Text-Aufrufe (ISS-061), Belegnummern und Trefferkürzung auf 600 Zeichen (gehören zu Kapitel 4), Speicherwerte 5,46 und 6,25 GB.
- In Kapitel 2 wurde nebenbei ein Zeilenüberlauf behoben (\enquote{Datum: 18.01.2025}, geschütztes Leerzeichen entfernt).


## Kapitel 4 – RAG- und Retrieval-Konzept

1. Rechne den Score des ersten S2-Treffers nach (0,712 × 1,5). Woher kommen die beiden Zahlen, und warum ändert der Boost an der Reihenfolge der fünf Treffer nichts?
2. Warum entfernt der Metadatenfilter die Ablenker vollständig, der Hierarchie-Boost aber kaum? Und warum sind die Werte mit Filter aus dem Vergleichslauf nur eine obere Schranke für den Agenten?
3. Das Modell darf nur nach Sparte filtern. Wie findet der Agent trotzdem die Rechnung eines bestimmten Jahres, und was passiert, wenn es diese Rechnung gar nicht gibt?
4. Was macht die Größen-Anfrage aus „neuer Arbeitspreis 2025“, und warum fand die erste Fassung bei P1 das Gas-Preisschreiben statt des Strom-Preisschreibens?
5. Welche Testfrage hätte von einem Graphen profitiert, und warum lohnt sich GraphRAG für diesen Haushalt trotzdem nicht?

**Antworten (von mir):**

**Beim Lesen besonders prüfen:**
- Gegenüber dem freigegebenen Plan kam ein Satz zum Argument Gegenstück dazu, weil Tabelle 3.1 den Begriff nennt, ohne ihn zu erklären. Dafür wurden andere Sätze gekürzt (Kapitel bleibt bei ca. 1,25 S.).
- „Im ersten Nachtlauf“ meint RUN-010 mit `llama3.1:8b` (wie in Kapitel 3). Die 9 von 19 ausschließenden Filter stammen aus diesem Lauf.
- „16 statt 13 von 27 Sollfakten“ ist ein Retrieval-Ergebnis von P1 (RUN-011/019 gegen RUN-020). Kapitel 5 soll darauf verweisen und nicht wiederholen, dass G1 trotz der Zahlen im Kontext falsch beantwortet wird, sondern es dort als Lese- und Vergleichsfehler einordnen.
- Hybrid-Suche mit BM25 kommt nicht vor (in ADR-0009 verworfen, nicht gefordert). Ein Prüfer könnte danach fragen; die Antwort steht in ADR-0009.
- Weggelassen aus Platzgründen: Wirkung der Summaries (steht in Kapitel 2), Ablenker im Kontext 7/94 → 4/92 (RUN-020), Bildsuche für S4 (`search_images`), Wirkung der Zitier-Rückfrage (9 von 9 Antworten mit Belegnummer, Kandidat für Kapitel 5).
- Der Satz zur Kürzung auf 600 Zeichen nennt ein Risiko, das nie gezielt gemessen wurde (ISS-031 offen).
