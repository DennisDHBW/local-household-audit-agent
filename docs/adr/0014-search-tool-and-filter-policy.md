# ADR-0014: Ein Suchwerkzeug, Filter nur nach Sparte, keine Wiederholung ohne Filter

- **Status:** akzeptiert (Messung RUN-012: P2 nach Handprüfung 9 von 14 statt 3 von 14; einzelner Lauf, Streuung nicht gemessen)
- **Datum:** 2026-11-16
- **Meilenstein:** M6 (M6d)

## Kontext
Die Fehleranalyse zu RUN-010/011 zeigte, dass P2 seine Belege meist schon durch den Werkzeugentwurf verliert: 18 von 23 P2-Fehlschlägen entstanden bei Werkzeugwahl und Filtern. Die Kündigungsfristen (S1, Z3) stehen in Tabellenzeilen, die nur `search_tables` findet, der Katalog erwartete aber `search_documents` (ISS-052, ISS-006). Das Modell setzte unaufgefordert `doc_type` und Jahr und schloss damit Quellen aus (ISS-007, ISS-025). Eine leere gefilterte Suche wurde ohne Filter wiederholt und lieferte Ablenker, etwa Strompreise auf die Frage nach Fernwärme (ISS-051).

## Entscheidung
1. **Ein Werkzeug `search`** durchsucht Text und Tabellenzeilen (`text`, `table_row`, mit `table_summary` nur bei eingeschalteter Einstellung). `search_images` bleibt getrennt, weil Bildbeschreibungen kein Beleg sind (ADR-0010).
2. **Das Modell filtert nur nach Sparte** (`utility_type`). `doc_type` und Jahr bietet `search` nicht mehr an; Jahr und Dokumentart gehören in die Suchanfrage (der Hierarchie-Boost nutzt den Dateinamen). `list_documents` behält alle drei Filter, weil es nur Metadaten auflistet.
3. **`include_counterpart=true`** (Parameter für Prüffragen) ergänzt je fehlender Dokumentfamilie bis zu 2 Treffer: fehlt unter den Treffern eine Rechnung, wird mit `doc_type=bill` nachgesucht; fehlt Vertrag oder Preisschreiben, mit `contract` und `price_adjustment`. Ob ein Treffer zu einer Rechnung oder einem Vertrag gehört, bestimmt der Code über den Dokumentkatalog.
4. **Keine Wiederholung ohne Filter mehr.** Eine leere Suche meldet „Keine Treffer“ und nennt, zu welchen Sparten und Dokumentarten es Unterlagen gibt. Die Meldung ist die Auskunft „liegt nicht vor“ und kein Anlass zu raten.
5. Der Fragenkatalog erwartet `search` statt `search_documents`/`search_tables`; die Metrik „Tool-Wahl korrekt“ bleibt für ältere Läufe lesbar (`SEARCH_TOOLS` kennt beide alten Namen).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Zwei Suchwerkzeuge mit besserer Beschreibung behalten | Ob ein Fakt in Fließtext oder Tabelle steht, weiß weder Modell noch Katalog vorher (ISS-052). Beschreibungen ändern nichts daran. |
| Modell setzt gar keine Filter mehr (Variante A) | Die Sparte war in RUN-010 bei allen Fragen richtig gesetzt und schließt Ablenker aus fremden Sparten sicher aus (N2). Der Verzicht würde das Retrieval für diese Fälle verschlechtern. |
| `year` und `doc_type` als Filter behalten, Beschreibung weiter schärfen | Seit RUN-000 ohne Wirkung: in RUN-010 schlossen 9 von 19 Filtern die Sollquelle aus (ISS-007). |
| Gegenstück immer automatisch mitsuchen | Der Code kennt den Fragetyp nicht; bei Einzelfragen verlängerten die Zusatztreffer den Kontext (Prefill 18 Token/s, ISS-001). Das Modell wählt, der Code führt aus. |
| Bei leerer Suche den Filter lockern | Bei einer Sparte, die es nicht gibt, ist „keine Treffer“ die richtige Antwort (ISS-051). |

## Konsequenzen
- Positiv: Kein ungültiger Werkzeugaufruf in 24 Aufrufen (RUN-010: 13 von 37). S1, Z3 (Kündigungsfristen) und N2 (Negativfrage) werden richtig beantwortet. Weniger Code im Modellvertrag (ein Suchwerkzeug, drei Parameter).
- Negativ / Preis der Entscheidung: Das Modell setzt `include_counterpart` in 12 von 17 Suchen, auch bei Einzelfragen; der Kontext wird größer. Jahr und Dokumentart laufen nur noch über die Suchanfrage und damit über die Ähnlichkeit statt über eine harte Auswahl. Die Laufzeit je Frage stieg von 136 s auf 263 s (Ursache offen, ISS-057). Fehler in Abrechnungen findet P2 weiterhin nicht (0 von 3), weil `llama3.1:8b` `calculate` nie aufruft (ISS-058).
- Was muss getestet werden, um die Entscheidung zu bestätigen? Zweiter Lauf zur Streuung; Gegenprobe mit `qwen2.5:7b` (ADR-0013); prüfen, ob das Jahr in der Suchanfrage ohne Jahresfilter bei Fragen wie N1 („Stromrechnung 2023“) ausreicht.

## Belege
RUN-012 gegen RUN-010 (`docs/evaluation-log.md`), ISS-006, ISS-007, ISS-025, ISS-051, ISS-052, ISS-057, ISS-058; ADR-0010 (Werkzeuge), ADR-0013 (Agent-Modell).
