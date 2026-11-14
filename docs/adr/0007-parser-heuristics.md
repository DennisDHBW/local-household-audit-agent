# ADR-0007: Parser-Heuristiken für Tabellen, Überschriften und Lesereihenfolge

- **Status:** akzeptiert
- **Datum:** 2026-11-14
- **Meilenstein:** M2

## Kontext
Die 30 PDFs enthalten Rechnungstabellen mit Zebra-Füllung statt durchgehender Rahmen, zweizeilige Spaltenköpfe, Überschriften ohne eigene Auszeichnung außer Fettdruck, einen zweispaltigen Briefkopf und auf jeder Seite Kopf- und Fußzeilen (Kundennummer, Bank, Handelsregister). PyMuPDF liefert dafür `find_tables()` und Textspans mit Schriftgröße und Flags. Auf den echten Dokumenten zeigte sich: keine einzelne Einstellung liefert saubere Tabellen (ISS-012, ISS-013, ISS-014).

## Entscheidung
Der `DocumentParser` (`src/audit_agent/ingestion/parser.py`) arbeitet mit folgenden Regeln. Alle Schwellwerte stehen in `ParserSettings` (`config.py`).

1. **Tabellenregionen:** `find_tables()` läuft mit den Strategien `lines` und `lines_strict`. Bei überlappenden Treffern gewinnt die Tabelle mit mehr Zeilen, danach die größere Fläche. Von `find_tables` werden nur Fläche und Zeilenbänder genutzt, nicht der extrahierte Text.
2. **Zellen:** Die Spans einer Zeile werden zu Zellen zusammengefasst: Spans, die sich in x-Richtung überlappen oder weniger als `cell_gap_pt` (5 pt) Abstand haben, bilden eine Zelle. Dadurch bleiben mehrzeilige Zellen („29,24 ct/“ über „kWh“) zusammen.
3. **Spaltenkopf:** Die erste nicht leere Zeile ist der Kopf, wenn alle ihre Spans fett sind und sie mindestens zwei Zellen hat. Jede Zelle einer Datenzeile gehört zur am weitesten links liegenden Kopfspalte, die sie überlappt (breite verbundene Beschriftungen landen so in der ersten Spalte). Ohne Kopf entsteht `Label: Wert` (zwei Zellen) bzw. `A | B | C`.
4. **Abschnittszeilen:** Eine Tabellenzeile mit nur einer fetten Zelle, deren Schrift größer ist als der Tabellentext, ist eine Überschrift. Die Tabelle wird dort getrennt (ISS-014).
5. **Überschriften im Fließtext:** Ein Textblock ist eine Überschrift, wenn alle Spans fett sind, die Länge zwischen 8 und 150 Zeichen liegt, die Schrift mindestens Fließtextgröße hat (`heading_size_factor = 1.0`) und links auf derselben Zeile kein anderer Text steht (sonst ist es der Wert eines Label-Wert-Paars). Die Ebene ergibt sich aus der Schriftgröße (größer = höher; Größen innerhalb von 0,4 pt teilen eine Ebene) und bestimmt den `heading_stack`.
6. **Kopf- und Fußzone:** Textblöcke in den oberen 4 % und unteren 6 % der Seite werden verworfen. Die Fußzeilen enthalten nur Bank-, Register- und Absenderangaben, die Retrieval verschmutzen würden.
7. **Lesereihenfolge:** Elemente (Textblöcke, Tabellen, Bilder) werden von oben nach unten gelesen; Elemente, die sich vertikal überlappen, werden spaltenweise gelesen (links vor rechts).
8. **Absätze:** Ein Textblock ist ein Absatz. Fragmente unter `min_chars` (20) werden mit dem folgenden Block zusammengefügt. Ein verbleibender Rest unter 20 Zeichen bleibt nur, wenn er eine Ziffer enthält (z. B. „Datum: 18.01.2025“). Absätze über `max_block_chars` (1.500) werden an Satzenden, notfalls an Leerzeichen geteilt.
9. **Bilder:** Eingebettete Bilder ab 50 pt Breite werden unter `data/processed/images/` gespeichert und als `image`-Chunk mit Platzhaltertext angelegt. Die Beschreibung folgt in M3.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| `Table.extract()` bzw. `to_markdown()` für den Zelltext | zerreißt Zahlen und Einheiten („1 189 00 EUR“), vermischt verbundene Zellen (ISS-013) |
| Nur die Standardstrategie von `find_tables()` | verliert Kopfzeile und erste Zeile bei gefüllten, rahmenlosen Zellen (ISS-012) |
| Naiver Text-Split (`get_text()` + feste Länge) | genau der Standard-RAG-Fehler, den das Projekt zeigen will: zerrissene Tabellen, kein Kontext |
| Layoutmodell (z. B. Docling, unstructured) | schwere Abhängigkeiten, auf der CPU langsam, im Seminar kaum nachvollziehbar; die Regeln hier lassen sich im Reverse Engineering Zeile für Zeile erklären |
| OCR / Vision für alle Seiten | die PDFs haben eine Textebene; Vision auf der CPU wäre um Größenordnungen langsamer (RUN-000: 78 s pro Bild) |

## Konsequenzen
- Positiv: Auf allen 30 PDFs entstehen Tabellenzeilen mit Spaltennamen in jeder Zeile (RUN-001), auch für die Fehlerdokumente 29 und 30. Alle Regeln sind per Unit-Test mit synthetischen PDFs abgesichert.
- Negativ: Die Regeln sind auf dieses Layout abgestimmt (fette Köpfe, gleichmäßige Schriftgrößen). Echte Post mit anderen Layouts würde Nachbesserung brauchen (ISS-019). Layout-Tabellen im Briefkopf werden fälschlich als Tabelle erkannt (ISS-015); Firmennamen im Briefkopf werden zu Überschriften (ISS-016).
- Zu testen: Auswirkung der Briefkopf-Chunks auf das Retrieval in M4; Parser-Fehler als eigene Fehlerklasse in der Fehleranalyse von M6.

## Belege
RUN-001 in `evaluation-log.md`, ISS-012 bis ISS-019, `tests/test_ingestion_parser.py`.
