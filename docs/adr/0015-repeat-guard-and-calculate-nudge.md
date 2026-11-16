# ADR-0015: Wiederholungssperre und Rechennachfrage im Agent-Loop

- **Status:** vorgeschlagen (RUN-013: Sperre wirkt wie vorgesehen, Rechennachfrage bei `llama3.1:8b` ohne Wirkung; Entscheidung 2 bleibt bis zur Gegenprobe mit `qwen2.5:7b` offen)
- **Datum:** 2026-11-16
- **Meilenstein:** M6 (M6e)

## Kontext
RUN-012 (ADR-0014) fand keinen der drei eingebauten Abrechnungsfehler (0 von 3) und meldete eine richtige Abrechnung als Abweichung (S5). In 24 Werkzeugaufrufen kam `calculate` kein einziges Mal vor (ISS-058). Bei G1 und G2 wiederholte `llama3.1:8b` dieselbe Suche mit denselben Argumenten; die Wiederholung lieferte denselben Text und kostete bei G1 rund 3.000 Zeichen Kontext (gut 1.200 Token, bei 18 Token/s Prefill über eine Minute). Bei G1, G3 und G4 stand keine Sollzahl im Kontext, weil die Suchanfrage die Frage selbst wiederholte („Gasabrechnung 2026“) statt die Größe zu benennen.

## Entscheidung
1. **Wiederholungssperre:** Der Loop merkt sich je Frage die gültigen Aufrufe (Werkzeug plus validierte Argumente). Ein identischer Aufruf wird nicht ausgeführt; das Modell bekommt `REPEAT_OBSERVATION` („Ergebnis steht weiter oben, suche anders, rechne oder antworte“). Der Aufruf zählt zum Limit von 6 und erscheint im Log als `is_repeat` (Status „Wiederholung“); er zählt nicht als ungültig und liefert keinen Beleg für die Auswertung.
2. **Rechennachfrage:** Kommt das Modell bei einer Prüffrage mit einer Antwort, ohne `calculate` gültig aufgerufen zu haben, fragt der Loop **einmal** nach („rechne mit `calculate` nach, fehlt ein Wert, suche ihn“). Bedingungen: mindestens ein Werkzeugaufruf, Antwort nicht leer und keine Lückenantwort, Werkzeuglimit nicht erreicht. Ob eine Frage eine Prüffrage ist, entscheidet `is_audit_question` am Wortlaut der Frage.
3. **Suchbegriffe:** Der Systemprompt verlangt je Prüfgröße getrennte Suchen für Sollwert (Vertrag, Preisschreiben) und Istwert (Rechnung) mit den Begriffen der Unterlagen und nennt die Frage als schlechte Suchanfrage. Das sind 263 Zeichen mehr (geschätzt rund 110 Token, bei 18 Token/s ohne Cache etwa 6 s mehr Prefill beim ersten Aufruf), bewusst ohne Beispiele aus dem Testkatalog, damit der Prompt nicht auf die Testfragen zugeschnitten ist.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Fester Prüfablauf im Code (Sollwerte suchen, Istwerte suchen, `calculate`) | Der Code übernimmt die Entscheidungen, die den Agenten ausmachen; das Ergebnis wäre eine Pipeline mit einem Sprachmodell am Ende. Als Ausblick für die Ausarbeitung notiert, falls die Nachfrage nicht reicht. |
| Nachfrage bei jedem Aufruf mit `include_counterpart=true` | Das Modell setzt das Flag in 12 von 17 Suchen, auch bei Einzelfragen (RUN-012); Fragen wie die Kündigungsfrist bekämen eine sinnlose Rechenaufforderung. |
| Wiederholungen ausführen und nur einen Hinweis anhängen | Der Kontext wächst um dieselben 3.000 Zeichen, die Prefill-Zeit fällt trotzdem an. |
| Nachfrage mehrfach wiederholen | Jede Nachfrage ist ein weiterer Modellaufruf (ISS-057); ein zweiter Versuch ändert bei Temperatur 0 selten etwas. |
| Beispielanfragen aus dem Testkatalog in den Prompt schreiben | Würde die Messung verfälschen: Die Fragen G1 bis G4 sind die Prüfmenge. |

## Konsequenzen
- Positiv: Schleifen kosten keinen Prefill mehr. Jede Prüffrage mit Antwort bekommt mindestens einen Anstoß zum Rechnen; die Entscheidung, was gerechnet wird, bleibt beim Modell. Alles ist als Schritt im Log sichtbar (`NudgeStep.reason`, `ToolCallStep.is_repeat`).
- Negativ / Preis der Entscheidung: Die Nachfrage garantiert nichts. Das Modell kann sie ignorieren oder falsch rechnen (ISS-054), und die Stichwort-Erkennung ist grob (ISS-060). Jede nachgefragte Prüffrage kostet einen zusätzlichen Modellaufruf. Der Systemprompt wird länger.
- Was muss getestet werden, um die Entscheidung zu bestätigen? RUN-013 (P2, 14 Fragen, `llama3.1:8b`) gegen RUN-012: Anzahl `calculate`-Aufrufe, Fehler erkannt (von 3), Fehlalarme (von 3), richtig nach Handprüfung (von 14), Laufzeit. Streuung zwischen zwei Läufen ist weiter nicht gemessen; ein Unterschied von ein oder zwei Fragen gilt nicht als Beleg.

## Ergebnis (RUN-013, einzelner Lauf)
- Entscheidung 1 (Sperre): 4 Wiederholungen abgefangen (G1, G2, N1, Z1), Observation je 191 Zeichen statt 1.500 bis 3.000. Wirkt wie beabsichtigt, hat aber keine der Antworten verbessert.
- Entscheidung 2 (Rechennachfrage): 4 Nachfragen (G3, G4, S5, Z1), 0 gültige `calculate`-Aufrufe, 59 statt 44 Modellaufrufe und 73 statt 61 Minuten (ein Teil davon kommt aus dem größeren Kontext, nicht nur aus den Nachfragen). Fehler erkannt: von Hand 0 von 3.
- Entscheidung 3 (Prompt): Nach Handprüfung 6 statt 9 richtige Antworten; ob das an der Änderung liegt oder an der Streuung, ist offen (ISS-062).
- Folge für die Entscheidung: Die Nachfrage bleibt vorläufig im Code, bis `qwen2.5:7b` mit demselben Loop gemessen ist; zeigt auch dieses Modell keinen Effekt, wird sie entfernt. Der feste Prüfablauf im Code, hier als verworfene Alternative geführt, wird als offene Entscheidung in `status.md` geführt.

## Belege
RUN-012, RUN-013 (`docs/evaluation-log.md`), ISS-054, ISS-057, ISS-058, ISS-060 bis ISS-063; ADR-0010 (Werkzeuge), ADR-0014 (Suchwerkzeug), `scripts/analyze_timing.py`.
