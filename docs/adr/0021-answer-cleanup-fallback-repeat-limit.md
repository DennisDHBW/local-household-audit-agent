# ADR-0021: Antwortbereinigung, Rückfall auf die belegte Antwort und Wiederholungsgrenze

- **Status:** akzeptiert; Punkt 5 geändert am 2026-11-21 (Nachtrag unten); Wirkung des Nachtrags erst mit run-027 gemessen; Antwortzwang nach leerer Antwort im Endlauf run-028 als Schwachstelle bestätigt (ISS-126)
- **Datum:** 2026-11-21
- **Meilenstein:** M8

## Kontext
Im Nachtlauf run-025 (RUN-025, ISS-117) beantwortete P2 9 von 21 Fragen richtig. Von den 12 Fehlschlägen lagen die meisten nicht am Wissen, sondern an der Steuerung der Schleife:
- 10 Endantworten enthielten angekündigte Schritte („Plan: 1. check_bill …“, „Nächster Schritt:“), 3 bestanden nur daraus. Ausgelöst wurde das vor allem durch den Plan-Hinweis nach dem ersten Werkzeugergebnis (ISS-114): `plan` wurde trotzdem nur in 4 von 21 Fragen aufgerufen.
- In 3 Fragen (G4, H1, S2) stand eine richtige oder fast richtige Antwort schon da; eine Rückfrage der Selbstprüfung machte daraus Plan-Text oder eine Lückenantwort, und diese wurde gewertet.
- 2 leere Antworten (S1, Z3), 1 Schleife aus denselben zwei Aufrufen bis zum Werkzeuglimit (N1).
- Argumente: erfundenes Jahr 2023 bei „aktuell“ (Z2), „Fernwärme“ wurde zu Heizstrom umgedeutet (N2), Grafik und Übersicht nur für einen Teil der Frage (V1, V2).

## Entscheidung
1. **Plan-Hinweis entfällt.** `plan` bleibt im Systemprompt; die Plan-Nachfrage aus ADR-0020 bleibt.
2. **Schritt-Text wird aus der Antwort entfernt** (`strip_step_talk`): Absätze, die mit „Plan“, „Nächster Schritt“, „Lass uns“, „Now, I will“ u. Ä. beginnen, Listen mit Werkzeugnamen und Sätze wie „Lassen Sie uns …“ nach einem echten ersten Satz. Besteht eine Antwort nur aus Schritt-Text, fragt die Schleife einmal nach (`steps`: „Führe den nächsten Schritt mit einem Werkzeugaufruf aus“). Ist die Antwort leer, folgt einmal ein Antwortaufruf ohne Werkzeuge (`empty`).
3. **Rückfall:** Endet die Schleife nach einer Rückfrage mit einer leeren Antwort, einer Lückenantwort oder reinem Schritt-Text, gilt die letzte echte Antwort davor (`AgentRun.is_fallback_answer`). Das gilt nur für Rückfragen, die etwas ergänzen oder bestätigen lassen (`plan`, `numbers`, `cite`, `language`, `chart`, `overview`), nicht nach `verdict` und `check`; dort war die frühere Antwort falsch oder ungeprüft.
4. **Wiederholungsgrenze:** Nach 2 wiederholten Aufrufen erzwingt die Schleife eine Antwort ohne Werkzeuge (`StopReason` `repeat_limit`, `REPEAT_LIMIT`).
5. **Lücke erst nach Volltextsuche:** Eine Lückenantwort wird einmal hinterfragt, solange `search` angeboten, aber nicht benutzt wurde. Vorjahreswerte stehen oft nur im Verbrauchsdiagramm einer Rechnung, das der Faktenspeicher nicht kennt (S4).
6. **Sprache:** Englische Antworten werden einmal hinterfragt (`language`); die Zahlenprüfung liest auch „24.10“ als Dezimalzahl.
7. **Argumente** (`scope.py`): Ein Jahr, das die Frage (mit Verlauf) nicht nennt, wird entfernt, außer bei `check_bill`; `get_facts` markiert dann den neuesten Stand. „Fernwärme“ in der Frage bleibt Fernwärme. Übersicht und Grafik nehmen den Umfang aus der Frage: keine Sparte genannt → alle Sparten, Licht- und Heizstrom genannt → beide Stromarten.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Plan-Hinweis behalten und Plan-Text als `plan`-Aufruf deuten | Das Modell soll nach dem Plan handeln; ein gedeuteter Text führt trotzdem keinen Schritt aus |
| Antwort im festen JSON-Format erzwingen (`format`) | im selben Aufruf könnte das Modell kein Werkzeug mehr wählen; der Agent würde zur Pipeline |
| Zusätzlicher Modellaufruf, der die Antwort bereinigt | ca. 30–60 s je Frage, und das Modell könnte dabei Zahlen ändern |
| Selbstprüfung ganz abschalten | `verdict` und `check` korrigieren falsche Urteile; nur der Schaden durch Rückfragen soll weg |

## Konsequenzen
- Positiv: Antworten ohne interne Schritte; eine Rückfrage kann eine belegte Antwort nicht mehr verschlechtern; keine Schleife bis zum Limit; Grafik und Übersicht decken die Frage ab. Offline (Faktenspeicher) liefern V1, V2, Z2 und N2 mit den reparierten Argumenten die erwarteten Werte.
- Negativ: Die Wortlisten für Schritt-Text und Englisch sind Heuristiken, abgeleitet aus den Ausgaben von `qwen2.5:7b` in run-025, also aus den Entwicklungsfragen (ISS-108, ISS-111). Der Rückfall kann nach einer `numbers`-Rückfrage eine Antwort mit unbelegter Zahl zurückbringen. Die Lückenregel kostet bei echten Negativfragen einen Werkzeugaufruf mehr (ca. 20–60 s). `AgentLoop.run` ist dadurch noch länger geworden.
- Zu testen: run-026 (P2, 21 Entwicklungsfragen), danach Endlauf run-027 mit den zurückgehaltenen Fragen.

## Belege
RUN-025, `data/eval/run-025/agentics.json`, ISS-114, ISS-117, ADR-0019, ADR-0020; Tests `tests/test_agent_run025.py` (21 von 22 schlagen auf dem alten Code fehl).

## Nachtrag 2026-11-21 (nach run-026, ISS-121 bis ISS-123)
- **Punkt 5 geändert:** Die Lückenrückfrage in v2 kommt nur noch bei einer reinen Lückenantwort (`is_pure_gap_answer`: Lückensatz, keine Zahl, keine Belegnummer). Mischantworten werden nicht mehr zurückgeschickt. Der Text (`RETRY_BEFORE_GAP_MESSAGE_V2`) nennt keine Dokumente des Korpus mehr, sondern nur `list_documents` und `search` und die Anweisung, nicht zu raten. Grund: In run-026 half die Rückfrage in 0 von 5 Fällen und verschlechterte 2 (N1, S1); der alte Text stammte aus S4 und N1 (ISS-111). Erwartet: S4 bleibt falsch (Werte nur im Diagramm); N1 wird weiter einmal hinterfragt.
- **Kontextschätzung:** `_is_context_full` zählt die Schemas der angebotenen Werkzeuge (`_active_specs`), nicht aller 8 (ISS-121).
- **Messung:** Die Quellen-Präzision zählt Zähler und Nenner je Beleg (ISS-123).

## Nachtrag 2026-11-21 (Endlauf run-028, zurückgehaltene Fragen)
- **Leere Antwort (Punkt 2):** In run-026 und run-027 nie ausgelöst, im Endlauf 3-mal (T3, T5, T6). Der Antwortaufruf ohne Werkzeuge kam jedes Mal, bevor ein brauchbares Ergebnis vorlag: T3 und T5 antworten „keine Angaben“, T6 erfindet eine Prüfung mit Zahlen und zwei Belegnummern ohne Treffer. Die einmalige Zahlen-Rückfrage hält das nicht auf.
- **Rückfall und Schritt-Text:** Im Endlauf kein Schritt-Text, kein Englisch, keine Rückfall-Antwort; `repeat_limit` nicht erreicht.
- **Lückenrückfrage:** 4-mal, einmal geholfen (T3), keinmal verschlechtert; in T1 greift sie bei einer Mischantwort, weil „1 Monat“ nicht als belegpflichtige Angabe zählt (ISS-125).
- Keine Änderung für M8 (ISS-108). Für eine spätere Version: den Antwortzwang nur zulassen, wenn schon Werkzeugergebnisse vorliegen.
