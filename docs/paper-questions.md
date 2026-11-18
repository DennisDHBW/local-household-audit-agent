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
