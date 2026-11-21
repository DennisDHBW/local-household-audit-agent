# ADR-0020: Werkzeugauswahl nach Fragetyp, Planprüfung und Plausibilitätsregeln

- **Status:** akzeptiert, gemessen in run-024/run-025 (Nachtrag 2026-11-21, ADR-0021); im Endlauf run-028 als Schwachstelle bestätigt (Nachtrag unten, ISS-126)
- **Datum:** 2026-11-20
- **Meilenstein:** M8

## Kontext
Smoke-Test run-023 (ISS-114): Das Modell wählte falsche Argumente, rief `plan` nie auf, und der erste Modellaufruf kostete wegen acht Werkzeugschemas rund 175 s Prefill. Prüfregeln, die nur bekannte Fehlerarten abdecken, sind zirkulär (ISS-112).

## Entscheidung
1. Der Code erkennt den Fragetyp (Prüffrage, Grafik, Übersicht, sonst Einzelwert/Klausel; Grafik auch aus dem Chatverlauf) und bietet nur die passenden Werkzeuge an; `plan`, `list_documents` und `calculate` immer (`AgentSettings.route_tools`). Das Modell wählt weiter selbst.
2. Nennt der Plan `check_bill`, `get_facts`, `make_chart` oder `make_overview` und lief das Werkzeug nicht, fragt die Selbstprüfung einmal nach (`NudgeReason` `plan`).
3. Neue Prüfregeln: Preisänderung innerhalb des Abrechnungszeitraums führt zu „nicht prüfbar“ statt zu einem falschen Urteil; Verbrauchsänderung über 25 % gegenüber dem Vorjahr ergibt einen Hinweis (`CheckStatus.NOTICE`), keinen Fehler.
4. `get_facts` ohne Jahr markiert den neuesten Stand; die Kurzfassung von `check_bill` nennt auch die Notizen mit Zahlen (z. B. richtige Energiemenge).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Feste Abläufe je Fragetyp ohne Modellwahl | wäre eine Pipeline, kein Agent mehr; der feste Prüfablauf brachte in RUN-017 nichts |
| Werkzeugwahl durch einen eigenen Modellaufruf | ca. 90–170 s zusätzlich je Frage |
| Anteilige Preisprüfung nach Tagen | kommt im Korpus nicht vor, wäre ungetestet |

## Konsequenzen
- Positiv: kürzere Schemas (weniger Prefill), weniger Fehlgriffe, Plan wirkt steuernd; keine falschen Urteile bei Preisänderungen im Jahr.
- Negativ: Die Fragetyp-Erkennung ist eine Wortliste und kann irren; ein falscher Typ blendet Werkzeuge aus (das Modell kann sie trotzdem aufrufen, sie stehen im Prompt). Die neuen Regeln greifen im Korpus nicht (keine Preisänderung im Jahr, kein Verbrauchssprung über 25 %), sie sind nur mit Unit-Tests belegt.
- Zu testen: run-024-smoke und Nachtlauf run-025.

## Belege
run-023-smoke, ISS-112, ISS-114, ADR-0019.

## Nachtrag 2026-11-20 (letzte Runde vor dem Nachtlauf)
- Selbstprüfung „Urteil“: Widerspricht das Urteil im ersten Satz dem Ergebnis von `check_bill`, fragt die Schleife einmal nach (`NudgeReason` `verdict`).
- `get_facts(fact=preise)` liefert alle Preise eines Vertrags in einem Aufruf; die Kurzfassung korrekter Rechnungen nennt Verbrauch aus Zählerständen und Gas-Umrechnung.
- Reine Erwähnung von „Strom“ (ohne Heiz-/Licht, ohne Übersicht/Grafik/„alle“) gilt als Lichtstrom; „seit JJJJ“ lässt das Endjahr einer Übersicht offen.
- `scripts/dry_run.py`: Trockenlauf des ganzen Nachtlaufs ohne Ollama in einem Temp-Ordner (Hash-Embeddings, regelbasiertes Orakel statt Modell). Findet Abstürze wie ISS-115 vorab; seine Trefferquote ist kein Modellergebnis.

## Nachtrag 2026-11-21 (gemessen in run-025)
- Werkzeugauswahl: laut Metrik 11 von 21 Fragen mit passendem Werkzeug; kein Fall, in dem ein ausgeblendetes Werkzeug gefehlt hätte.
- Plan-Nachfrage: 3-mal ausgelöst (S1, G2, G4); zweimal danach eine schlechtere Antwort (S1 leer, G4 Lückenantwort statt des richtigen Urteils). Bleibt, aber mit Rückfall auf die frühere Antwort (ADR-0021).
- `plan` selbst wurde nur in 4 von 21 Fragen aufgerufen. Der Plan-Hinweis aus ISS-114 führte eher dazu, dass das Modell den Plan als Text schrieb; er entfällt (ADR-0021).
- Plausibilitätsregeln: griffen im Korpus wie erwartet nicht.

## Nachtrag 2026-11-21 (Endlauf run-028, zurückgehaltene Fragen)
- Die Wortliste der Prüffragen erkennt 0 von 2 Prüffragen der zurückgehaltenen Fragen („berechnet“ in T3, „in Ordnung“ in T6). `check_bill` wird nicht angeboten und läuft im ganzen Endlauf 0-mal.
- Die Annahme „das Modell kann ausgeblendete Werkzeuge trotzdem aufrufen“ hat sich nicht bestätigt: In T3 und T6 (`check_bill`) und T5 (`search` bei einer Grafikfrage) folgt auf die Aufforderung eine leere Antwort, danach keine Prüfung (ISS-126). Die Ursache der leeren Antworten ist nicht geprüft.
- Die Entscheidung bleibt für M8 unverändert (keine Nachbesserung an den zurückgehaltenen Fragen, ISS-108). Die negative Konsequenz oben ist damit gemessen: Ein falsch erkannter Fragetyp kostet hier zwei von acht Antworten.
