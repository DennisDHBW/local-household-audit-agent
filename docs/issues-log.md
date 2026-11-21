# Probleme & Schwachstellen

> Jedes Problem sofort notieren, auch kleine. Gerade Umwege, Fehlannahmen und Fehler der KI sind für die Reflexion wertvoll („Was lief schief und was habe ich daraus gelernt?“).
> Neueste oben. Status: `offen` · `gelöst` · `akzeptiert` (bewusst nicht gelöst, als Grenze dokumentiert)

## Kategorien
`parser` · `chunking` · `enrichment` · `retrieval` · `agent` · `tools` · `llm` · `hardware` · `evaluation` · `daten` · `ki-assistent` (falscher/unpassender Code oder Rat von Claude) · `konzept`

## Vorlage

```markdown
### ISS-000 – <kurzer Titel>
- **Datum / Meilenstein:**
- **Kategorie:**
- **Status:** offen
- **Symptom:** Was ist passiert? (konkret, ggf. Fehlermeldung oder Beispiel)
- **Ursache:** Warum? (erst eintragen, wenn verstanden)
- **Lösung / Workaround:**
- **Gelernt:** (1 Satz in eigenen Worten)
- **Relevant für Ausarbeitung?** ja/nein → Kapitel …
```

---

## Einträge

### ISS-124 – `m8_night.sh` hätte run-026 fortgesetzt statt einen neuen Lauf zu starten (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Das Skript trug für den Standardlauf fest `run-026` ein; status.md nennt den Kontrolllauf run-027. `generate` setzt einen vorhandenen Lauf mit derselben `--run-id` fort und hätte nichts neu erzeugt; die Daten von run-026 wären mit den alten Antworten neu bewertet worden.
- **Ursache:** Beim Auswerten von run-026 wurde die Lauf-Nummer im Skript nicht mit der Planung in status.md abgeglichen. Gefunden beim Sitzungsabschluss, bevor der Lauf gestartet wurde.
- **Lösung / Workaround:** Standardlauf `run-027`, `--holdout` `run-028` (Skript, README).
- **Gelernt:** Vor dem Start eines langen Laufs die Lauf-Nummer im Skript gegen die Planung prüfen.
- **Relevant für Ausarbeitung?** nein

### ISS-123 – Kennzahl Zitat-Präzision mischt zwei Zählweisen (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** evaluation
- **Status:** gelöst
- **Symptom:** Die gemeldete Präzision von P2 fiel von 50 % (run-025) auf 33 % (run-026), obwohl die Handprüfung kaum falsche Zitate zeigt. H3 zitiert 14 Belege, alle auf die beiden erwarteten Seiten (Vertrag 4, Rechnung 10); gezählt werden 2 von 14.
- **Ursache:** `score_answer` zählt im Zähler (`cited_expected`) die verschiedenen erwarteten Paare aus Datei und Seite, im Nenner (`cited_count`) die zitierten Belegnummern. Mehrere Belege derselben Seite zählen im Nenner mehrfach, im Zähler einmal. Das Glossar beschreibt die Kennzahl richtig („Anteil der zitierten Belege“), der Code nicht. So seit M6; kein Test mit mehreren Belegen derselben Seite.
- **Nachgerechnet** (mit der heutigen `ground_truth.yaml`; für run-020/021 vorläufig, weil sich Quellenangaben seit M6 geändert haben können):

| Lauf | Variante | bisher | je Beleg | je Seite |
|---|---|---|---|---|
| run-020 | P1 | 9/20 (45 %) | 16/20 (80 %) | 9/12 (75 %) |
| run-021 | P2 | 8/17 (47 %) | 10/17 (59 %) | 8/14 (57 %) |
| run-025 | B0 | 3/8 (38 %) | 3/8 (38 %) | 3/8 (38 %) |
| run-025 | P1 | 14/39 (36 %) | 25/39 (64 %) | 14/26 (54 %) |
| run-025 | P2 | 18/36 (50 %) | 34/36 (94 %) | 18/20 (90 %) |
| run-026 | P2 | 24/72 (33 %) | 55/72 (76 %) | 24/37 (65 %) |

- **Lösung / Workaround:** Im nächsten Paket: Zähler je Beleg zählen, Test mit mehreren Belegen derselben Seite, alle Läufe offline neu bewerten, Zahlen in `evaluation-log.md` und in der Ausarbeitung nachziehen. Umgesetzt (2026-11-21): `score_answer` zählt `cited_expected` je zitiertem Beleg, neuer Test mit mehreren Belegen derselben Seite; run-020, 021, 025 und 026 offline neu bewertet (Werte wie in der Spalte „je Beleg“). Zahlen in der Ausarbeitung folgen in Phase 2.
- **Gelernt:** Bei einer Quote müssen Zähler und Nenner dieselben Dinge zählen.
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (alle Präzisionswerte betroffen)

### ISS-122 – Lücken-Rückfrage schadet in run-026 mehr, als sie nützt
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** agent
- **Status:** gelöst
- **Symptom:** Die Lücken-Rückfrage kam in 5 von 21 Fragen (N1, S1, S4, Z2, Z3). Geholfen hat sie in keiner, verschlechtert in zwei: N1 (die erste Antwort „keine Angaben“ war richtig, danach eine Vermutung, die Rechnung 2023 liege „in der Nähe“ von 2024 und 2025) und S1 (die erste Antwort war inhaltlich richtig, danach Heizstromvertrag und Jahr 2024). In S4, Z2 und Z3 blieb das Ergebnis gleich, kostete aber 120 bis 270 s je Frage (Schritte nach der Rückfrage).
- **Ursache:** (1) `is_gap_answer` findet den Lückensatz irgendwo in der Antwort, Mischantworten (S1, Z2, Z3) zählen als Lücke; `drop_trailing_gap` entfernt nur den exakten Satz und nur, wenn der Rest zitiert. (2) `min_searches_before_gap` zählt Werkzeugaufrufe, nicht Suchen; nach einem einzigen Aufruf wird immer nachgefragt. (3) Der Text der v2-Rückfrage nennt Heizstrom, Lichtstrom und Vergleichsdiagramme; er stammt aus S4 und N1 (ISS-111) und lenkt bei der Gasfrage S1 auf Strom.
- **Lösung / Workaround:** Im nächsten Paket: Rückfrage nur bei einer reinen Lückenantwort, Text ohne Hinweise auf das Korpus. S4 (Werte nur im Diagramm) bleibt dann vermutlich falsch; das wird hingenommen. Umgesetzt (2026-11-21, Tests): Die v2-Rückfrage kommt nur noch bei einer reinen Lückenantwort (`is_pure_gap_answer`: Lückensatz, keine Zahl, kein Beleg); Text ohne Hinweise auf das Korpus. Restrisiko: N1 (reine Lückenantwort nach einer Suche) wird weiter einmal hinterfragt. Wirkung erst mit run-027 gemessen. **Offline-Probe vor run-027 (2026-11-21):** Die neue Regel auf alle Lückenantworten aus run-026 angewendet: S1, Z2, Z3 (Mischantworten) werden nicht mehr zurückgeschickt; N1 und S4 (reine Lückenantworten) weiter einmal. Entscheidung des Nutzers: unverändert lassen, weil jede weitere Regel auf die Entwicklungsfragen zugeschnitten wäre (ISS-108); in run-027 prüfen, ob N1 weiter schlechter wird (dann Rückfrage in v2 abschalten, nach dem Endlauf als Befund).
- **Gelernt:** Eine Regel, die Antworten verbessern soll, muss man auch daran messen, wie oft sie eine richtige Antwort verschlechtert.
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Rückfragen der Schleife)

### ISS-121 – Kontextschätzung zählt alle Werkzeugschemas, `context_limit` greift zu früh (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** agent
- **Status:** gelöst
- **Symptom:** In run-026 enden S1 und Z2 nach 4 Werkzeugaufrufen mit `context_limit`. Laut Ollama-Journal waren die Anfragen höchstens 3.737 bzw. 3.654 Token lang; frei wären 6.392 (8.192 − 600 Antwort − 1.200 Reserve).
- **Ursache:** `AgentLoop._spec_tokens` wird einmal im Konstruktor aus den Schemas aller 8 Werkzeuge geschätzt (ca. 3.000 Token). Seit ADR-0020 werden je Frage nur 4 bis 5 Werkzeuge angeboten (ca. 1.800 Token geschätzt); die Schätzung wurde dabei nicht angepasst. Auch mit den angebotenen Schemas liegt die Schätzung beim ersten Aufruf rund 45 % über dem Wert von Ollama (ca. 2.500 gegen 1.720 Token), weil 2,4 Zeichen je Token für JSON-Schemas zu wenig sind.
- **Lösung / Workaround:** Im nächsten Paket: Schätzung je Frage aus den angebotenen Schemas (`_active_specs`). In run-026 hat der frühe Abbruch kein Ergebnis gekippt (beide Antworten waren vorher schon falsch), er nimmt aber längeren Ketten den Spielraum. Umgesetzt (2026-11-21, Test): `_is_context_full` schätzt die Schemas der angebotenen Werkzeuge (`_active_specs`) statt aller 8. Die Schätzung liegt weiter etwa 45 % über Ollama (2,4 Zeichen je Token), bewusst nicht geändert wegen B0 (ISS-120). Wirkung erst mit run-027 gemessen.
- **Gelernt:** Wer eine Größe an einer Stelle verkleinert, muss jede Stelle nachziehen, an der sie gerechnet wird.
- **Relevant für Ausarbeitung?** ja → Kapitel 4 (Grenzen der Schleife), knapp

### ISS-120 – B0: Kontext für `qwen2.5:7b` zu knapp geschätzt, Kontextverschiebung bei V2
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** evaluation
- **Status:** akzeptiert (Entscheidung des Nutzers 2026-11-21: B0-Budget im Endlauf unverändert, Grenze im Bericht nennen)
- **Symptom:** Im Ollama-Journal von run-025 steht um 23:27:10 „truncated = 1, n_tokens = 4149“. Zur selben Zeit lief B0/V2: 7.695 Prompt-Token plus 548 erzeugte Token, zusammen mehr als `num_ctx` 8.192. Ollama hat den Kontext verschoben und dabei die Hälfte verworfen; das Ende der B0-Antwort entstand mit gekürztem Kontext.
- **Ursache:** Das B0-Budget schätzt mit 2,4 Zeichen je Token (gemessen an `llama3.1:8b`, ISS-041) 6.727 Token; der Tokenizer von `qwen2.5:7b` braucht für denselben Text 7.695 (+14 %). Reserviert sind 600 Token für die Antwort, real bleiben knapp 500. Betroffen ist nur V2, die einzige B0-Antwort über 497 Token; sie war ohnehin falsch.
- **Lösung / Workaround:** Für run-025 hingenommen. B0 läuft erst wieder im Endlauf run-027; ändert man das Budget, ist B0 nicht mehr mit run-025 vergleichbar. Empfehlung: unverändert lassen und im Bericht nennen. Eigener Fehler bei der ersten Auswertung: Die Dateizeiten der VM stehen in UTC, das Journal in MEZ; deshalb wurde die Kürzung zuerst P2/S4 zugeordnet.
- **Gelernt:** Token-Schätzungen hängen am Tokenizer; nach einem Modellwechsel muss man sie neu messen.
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Grenze von B0)

### ISS-119 – Offene Antwortschwächen nach run-025 (bewusst nicht behoben)
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** (1) Mischantworten: „Dazu liegen … keine Angaben vor.“ und danach doch ein Inhalt (Z3, N2, N1). (2) Prüfantworten „stimmt“ ohne Zahlen (H3), obwohl die Kurzfassung von `check_bill` die Werte nennt. (3) S2 „laut Stromvertrag“: `get_facts` ohne Jahr markiert den neuesten Stand (Preisanpassung 2025), der Vertrag ist von 2024. (4) `plan` nur in 4 von 21 Fragen. (5) Die Wortlisten für Schritt-Text und Englisch (ADR-0021) stammen aus den Antworten auf die Entwicklungsfragen. (6) `AgentLoop.run` ist mit allen Rückfragen rund 190 Zeilen lang und schwer zu lesen.
- **Ursache:** (1) ist nicht automatisch lösbar: Bei N2 ist die Lücke richtig und der Inhalt falsch, bei Z3 umgekehrt. (2)–(4) liegen am Modell; Code-Regeln dafür wären auf diese Fragen zugeschnitten.
- **Lösung / Workaround:** Nicht in diesem Paket, um nicht weiter auf die Entwicklungsfragen hin zu optimieren (ISS-108, ISS-111). Nach run-026 entscheiden, ob (2) und (6) noch angegangen werden.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 5 und 6 (Grenzen)
- **Nachtrag 2026-11-21 (run-026):** (1) Mischantworten weiter in S1, Z2, Z3 und S3 („keine weiteren Grafiken“); sie lösen jetzt die Lücken-Rückfrage aus (ISS-122). (2) H3 nennt jetzt alle Soll- und Ist-Werte; Z1 lässt die z-Zahl aus der Kurzfassung weg. (3) S2 nennt jetzt den abgerechneten, falschen Arbeitspreis 39,50 ct/kWh. Neu: Z2 nennt 115,00 EUR, obwohl `get_facts` 120,00 EUR als „neuester Stand“ markiert; das Modell liest die Werkzeugausgabe falsch. (4) `plan` in 3 von 21 Fragen. (7) Neu: Zitate passen nicht immer genau zur Aussage (G4 ohne Belegnummern; V3 belegt die Preise ab 2026 mit den Belegen für 2024; G3 belegt den Ist-Wert 1,0000 nur mit der Rechnung 2024). (8) Neu: Füllsätze aus der Kurzfassung von `check_bill` („stimmt mit Vertrag, Preisschreiben und Zählerständen überein“ auch bei den Betriebskosten G2). Entscheidung: (1) bis (8) werden nicht mehr angegangen; vor dem Endlauf nur ISS-121 bis ISS-123.

### ISS-118 – Kennzahl Tool-Wahl prüfte v2-Läufe gegen die v1-Werkzeuge (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** evaluation
- **Status:** gelöst
- **Symptom:** run-025 meldete für P2 „Tool-Wahl korrekt 11/21“. Bei G1–G4, S5 und Z1 nutzte der Agent richtig `check_bill`, erwartet waren aber `search` und `calculate`; bei S2, S3 und Z2 `get_facts` statt `search`.
- **Ursache:** Die erwarteten Werkzeuge der 14 alten Fragen stammen aus M6 (Werkzeugsatz v1). Beim Umbau auf v2 (ADR-0019) wurden sie nicht angepasst.
- **Lösung / Workaround:** Neues Feld `expected_tools_v2` in `ground_truth.yaml` für S2–S5, G1–G4, Z1, Z2. Die Bewertung erkennt einen v2-Lauf daran, dass irgendeine P2-Antwort ein reines v2-Werkzeug aufrief (`uses_tool_set_v2`); alte v1-Läufe werden unverändert bewertet. run-024-smoke und run-025 neu bewertet: Tool-Wahl 4/5 statt 3/5 und 19/21 statt 11/21, alle anderen Zahlen gleich. Die zwei verbleibenden Fehlgriffe sind echt (S4 ohne Suche, Z2 ohne gültiges `get_facts`).
- **Gelernt:** Wenn sich die Werkzeuge ändern, muss die Messung mit umziehen.
- **Relevant für Ausarbeitung?** ja → Kapitel 5

### ISS-117 – Nachtlauf run-025: Die Schleife verschenkt richtige Antworten
- **Datum / Meilenstein:** 2026-11-21 / M8
- **Kategorie:** agent
- **Status:** gelöst (Wirkung in run-026 zu prüfen)
- **Symptom:** P2 9 von 21 richtig, aber 41 von 49 Sollfakten im Kontext. 10 Endantworten enthielten angekündigte Schritte („Plan: 1. check_bill …“), 3 nur diese (S2, H1, N1); 3 richtige oder fast richtige Antworten wurden durch eine Rückfrage schlechter (G4: Lücke statt Urteil, H1: richtige Preise auf Englisch, nach der Zahlen-Rückfrage nur noch Plan-Text, S2); 2 leere Antworten (S1, Z3); N1 wiederholte zwei Aufrufe bis zum Limit; Z2 suchte im erfundenen Jahr 2023; N2 wurde von „Fernwärme“ zu Heizstrom umgedeutet; V1 und V2 zeigten nur einen Teil.
- **Ursache:** (1) Der Plan-Hinweis nach dem ersten Werkzeugergebnis (ISS-114) brachte das Modell dazu, Pläne als Text zu schreiben; die Schleife nahm jeden Text ohne Werkzeugaufruf als Antwort. (2) Die Antwort nach einer Rückfrage ersetzte die vorige ohne Vergleich. (3) Keine Rückfallebene für leere Antworten; bei S1 lief die Selbstprüfung sogar auf eine leere Antwort. (4) Wiederholungen wurden erkannt, aber nicht begrenzt. (5) Eigener Fehler in `drop_trailing_gap`: Die Fußnote „[1] Hinweis: Argumente angepasst …“ galt als Beleg, deshalb fiel bei N1 der richtige Lücken-Satz weg. (6) Eigener Fehler aus ISS-114: Die Umdeutung Fernwärme → Heizstrom griff auch, wenn die Frage „Fernwärme“ sagt. (7) Die Zahlen-Prüfung las „24.10“ als 24.
- **Lösung / Workaround:** ADR-0021: Plan-Hinweis entfernt; `strip_step_talk` entfernt Schritt-Text, reine Ankündigung wird einmal nachgefragt (`steps`); leere Antwort bekommt einen Antwortaufruf ohne Werkzeuge (`empty`); Rückfall auf die letzte echte Antwort nach Rückfragen außer `verdict` und `check`; `REPEAT_LIMIT` 2; Lücke erst nach Volltextsuche; Sprach-Rückfrage; Dezimalpunkt; Argumente: Jahr nur aus der Frage, Fernwärme bleibt, Umfang von Übersicht und Grafik aus der Frage. Außerdem setzt `run()` die aktuelle Frage jetzt auch nach einer Ausnahme zurück (vorher blieb sie im Kontext stehen). 22 neue Tests mit den echten Ausgaben aus run-025, 21 davon schlagen auf dem alten Code fehl. Offline liefern V1, V2, Z2 und N2 mit den reparierten Argumenten die erwarteten Werte.
- **Gelernt:** Jede Rückfrage ist ein Risiko; sie darf eine schon belegte Antwort höchstens verbessern, nie ersetzen.
- **Relevant für Ausarbeitung?** ja → Kapitel 3 (Steuerung der Schleife) und 5 (Fehleranalyse)

### ISS-116 – Trockenlauf mit Orakel: Obergrenze der Werkzeuge, Ausgaben der zurückgehaltenen Fragen kurz sichtbar
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** `scripts/dry_run.py` lief ohne Absturz durch (B0, P1, P2 auf 21 Entwicklungsfragen, P2 auf den zurückgehaltenen Fragen, `score`, `check_evidence`). Mit dem regelbasierten Orakel statt des Modells kam P2 zunächst auf 14, nach drei Ergänzungen (`fact=preise`, Verbrauch in der Kurzfassung, „seit JJJJ“) auf 17 von 21 Entwicklungsfragen; offen S1 (Orakel liest Suchtreffer nicht), S4 (Diagrammwerte nur über die Suche), N1/N2 (Orakel kennt keine Lücke). Beim ersten Lauf erschienen im Fehlerkanal Bruchstücke der Orakel-Antworten auf zurückgehaltene Fragen.
- **Ursache:** Der Trockenlauf prüft bewusst auch den `--holdout`-Weg; die Ausgabe der Antworten war nicht abgeschaltet.
- **Lösung / Workaround:** Für die zurückgehaltenen Fragen druckt das Skript nur noch „ohne Fehler“; der Bericht wird nicht gelesen. An den gesehenen Bruchstücken wurde nichts angepasst. Die 17 von 21 sind eine Obergrenze bei perfekter Werkzeugwahl, kein Ergebnis des Agenten, und dürfen nicht so berichtet werden.
- **Gelernt:** Ein Trockenlauf mit Orakel trennt „Werkzeuge liefern es nicht“ von „Modell wählt falsch“.
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Obergrenze der Werkzeuge gegen tatsächliches Modellergebnis)

### ISS-115 – Bewertung des Smoke-Tests brach ab (`_all_questions` nicht definiert)
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** `m8_prepare.sh` lief bis zum Ende, `score` brach mit `NameError: _all_questions` ab; die Antworten von run-023-smoke waren gespeichert.
- **Ursache:** Claude hängte die Funktion ans Dateiende hinter `if __name__ == "__main__": sys.exit(main())`; sie wurde beim Start nie definiert. Unit-Tests rufen `main()` nicht über `python -m` auf, ruff erkennt das nicht.
- **Lösung / Workaround:** Funktion vor den Startblock verschoben.
- **Gelernt:** Code nach dem Startblock wird bei `python -m` nie erreicht; neue Funktionen nie ans Dateiende einer `__main__.py` hängen.
- **Relevant für Ausarbeitung?** nein

### ISS-114 – Smoke-Test: Modell füllt Sparte und Stromart falsch, ruft `plan` nicht auf
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** agent
- **Status:** gelöst (Wirkung im nächsten Lauf zu prüfen)
- **Symptom:** run-023-smoke: H2 `check_bill(utility_type=district_heating)` für „Heizstrom“ → keine Rechnung → „keine Angaben“; W1 `tariff_kind=household` bei Wasser → keine Rechnung, danach dreimal derselbe gesperrte Aufruf (447 s); V1 `tariff_kind="household,heating"` ungültig und am Ende der richtigen Antwort der Satz „Dazu liegen … keine Angaben vor“. `plan` wurde in keiner Frage aufgerufen. Erster Modellaufruf ca. 175 s Prefill bei 2.600 Token.
- **Ursache:** 7B-Modell verwechselt Heizstrom mit Fernwärme und überträgt `tariff_kind` auf andere Sparten; der Plan-Schritt stand nur im Prompt.
- **Lösung / Workaround:** `agent/scope.py`: Argumente werden vor der Prüfung repariert (Heizstrom → electricity/heating, `tariff_kind` nur bei Strom, beide Stromarten → keiner, fehlende Sparte/Jahr aus der Frage) und die Reparatur steht im Ergebnis; `check_bill` prüft bei Strom ohne Stromart beide Rechnungen; Hinweis auf `plan` nach dem ersten Werkzeugergebnis (kein zusätzlicher Modellaufruf); angehängter Lückensatz wird entfernt; `check_bill` liefert eine „Kurzfassung für die Antwort“ mit Saldo; Werkzeugbeschreibungen gekürzt.
- **Gelernt:** Was der Code aus der Frage sicher ableiten kann, sollte er nicht dem Modell überlassen.
- **Relevant für Ausarbeitung?** ja → Kapitel 3
- **Nachtrag 2026-11-21 (run-025):** Der Plan-Hinweis hat geschadet (Pläne als Text statt Aufrufe) und ist entfernt; die Umdeutung Fernwärme → Heizstrom gilt nicht mehr, wenn die Frage „Fernwärme“ nennt (ISS-117, ADR-0021).

### ISS-113 – Agent v2 noch nicht mit Ollama gelaufen
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** agent
- **Status:** gelöst (run-024-smoke und run-025 mit Ollama, 2026-11-20/21; Befunde in ISS-117)
- **Symptom:** Werkzeuge, Plan-Schritt, Selbstprüfung und Chat sind nur mit gescripteten Antworten getestet (Unit-Tests). Ob `qwen2.5:7b` `plan` zuerst aufruft, `check_bill` mit `tariff_kind` richtig füllt und die Befunde korrekt wiedergibt, ist unbekannt.
- **Ursache:** Claudes Shell erreicht Ollama nicht.
- **Lösung / Workaround:** `scripts/m8_prepare.sh` endet mit einem Smoke-Test (H2, V1, W1); erst danach der Nachtlauf.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 3 und 5

### ISS-112 – Prüfregeln und eingebaute Fehler stammen beide von Claude
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** RUN-022 erkennt 5 von 5 eingebauten Fehlern ohne Fehlalarm. Die Fehler E4/E5 und die Regeln wurden in derselben Sitzung geschrieben; die Regeln decken genau die Fehlerarten ab, die es im Korpus gibt (Preis, Zählerstand, z-Zahl, Abschläge, Wohnfläche).
- **Ursache:** Testdaten und Prüflogik vom selben Autor, kein unabhängiger Fehlerkatalog.
- **Lösung / Workaround:** In der Ausarbeitung als Grenze nennen: Die Regeln prüfen bekannte Fehlerarten, unbekannte (z. B. falscher Steuersatz, doppelte Position) erkennen sie nicht. Die zurückgehaltenen Fragen enthalten bewusst keinen neuen Fehlertyp, prüfen also nur die Agentik.
- **Gelernt:** Eine Erkennungsrate von 100 % auf selbst gebauten Fehlern sagt wenig über echte Rechnungen.
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Grenzen)

### ISS-111 – Faktenregeln auf die Layouts des Korpus zugeschnitten
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** daten
- **Status:** akzeptiert
- **Symptom:** `facts/extract.py` erkennt Zeilen an Spaltennamen wie „Preis Brutto“, „Neu Brutto (ab …)“, „Zählwerk“ und an festen Sätzen („Ihr neuer monatlicher Abschlag beträgt ab …“). Ein anderer Anbieter bräuchte neue Regeln. Erster Probelauf: zwei Scheinabweichungen (Zwischensumme als Position, Vorauszahlungen in einer „Position“-Zeile), beide behoben.
- **Ursache:** Regelbasiert ohne Layoutmodell, wie der Parser (ADR-0007).
- **Lösung / Workaround:** Regeln mit Unit-Tests auf Beispielzeilen und einem Test über den echten Korpus (`test_facts.py`); nicht erkannte Zeilen führen zu „nicht prüfbar“, nicht zu „stimmt“.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 2 und 4

### ISS-110 – Qualitätsgewinn von M8 kommt aus Code, nicht aus dem Modell
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** konzept
- **Status:** akzeptiert
- **Symptom:** Mit `check_bill` vergleicht der Code, nicht das Modell. Ein Vergleich P1 (unverändert) gegen P2 v2 misst deshalb Agent plus Faktenspeicher, nicht Agentik allein.
- **Ursache:** Bewusste Architekturentscheidung (ADR-0018).
- **Lösung / Workaround:** In der Ausarbeitung offen trennen: Werkzeugsatz v1 bleibt einstellbar; was der Agent beiträgt (Werkzeugwahl, Plan, Nachprüfung, Grafik auf Anfrage), wird mit eigenen Kennzahlen gemessen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 3 und 5

### ISS-109 – Heizstrom (Nachtspeicher) neben Gas-Etagenheizung
- **Datum / Meilenstein:** 2026-11-20 / M8
- **Kategorie:** daten
- **Status:** akzeptiert
- **Symptom:** Der Mietvertrag (Dok. 16) nennt eine Gas-Etagenheizung; der Nutzer wünscht Heizstrom mit HT/NT (Nachtspeicher). Die neuen Dokumente 31–34 beschreiben zwei Nachtspeicheröfen mit eigenem Zweitarifzähler und eigenem Vertrag. Beides zusammen ist ungewöhnlich, aber nicht unmöglich.
- **Ursache:** Nachträgliche Erweiterung des erfundenen Haushalts (Entscheidung des Nutzers, 2026-11-20).
- **Lösung / Workaround:** Keine Änderung an Dok. 16; in der Ausarbeitung den Heizstrom als Zusatzheizung beschreiben.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1 und 2

### ISS-108 – Testfragen waren zugleich Entwicklungsfragen
- **Datum / Meilenstein:** 2026-11-20 / M7 (Befund), M8 (Lösung)
- **Kategorie:** evaluation
- **Status:** offen
- **Symptom:** Alle 14 Fragen dienten seit RUN-010 der Entwicklung. Größen-Anfrage, Spartenfilter, Lücken-, Rechen- und Zitier-Rückfrage gehen auf einzelne dieser Fragen zurück. Die Ergebnisse (P1 8, P2 6 von 14) sind deshalb eher zu günstig.
- **Ursache:** Kein zurückgehaltener Fragensatz von Anfang an (Fehler im Vorgehen, von Claude nicht angesprochen).
- **Lösung / Workaround:** In Kapitel 5 als Grenze genannt. Ab M8 gibt es einen zurückgehaltenen Fragensatz (`dataset/holdout_questions.yaml`), der erst im Endlauf läuft.
- **Gelernt:** Wer am Testset entwickelt, misst am Ende auch die eigene Anpassung.
- **Relevant für Ausarbeitung?** ja → Kapitel 5
- **Nachtrag 2026-11-21 (run-026):** P2 steigt auf den Entwicklungsfragen von 9 auf 15 von 21. Die Fixes (ADR-0021) stammen aus genau diesen Fragen, der Anstieg ist deshalb zu günstig; aussagekräftig ist erst der Endlauf auf `holdout_questions.yaml`.

### ISS-107 – Text-Befunde eingearbeitet, Ausarbeitung ca. 12 Zeilen über 8 Seiten
- **Datum / Meilenstein:** 2026-11-20 / M7
- **Kategorie:** ki-assistent
- **Status:** offen
- **Symptom:** Nutzer fragte nach schlechten Ergebnissen, Herkunft von `final_score` und der missverständlichen Angabe „0 von 55 statt 4 von 60“. Befunde: Herkunft der Formel fehlte, 55/60 doppelt mit verschiedener Bedeutung und mit 10 statt 12 Fragen, Schluss „Grenze eines 7B-Modells“ nicht gemessen, Prüffragen nur bei korrekten Abrechnungen richtig, interne Begriffe (Nachtlauf, Dokument 29, Rechennachfrage), Pointen und Inversionen.
- **Ursache:** Claudes Text (ISS-105) prüfte die Zahlen, aber nicht, wie ein Leser sie versteht; die 7B-Einordnung war eine ungemessene Behauptung (ISS-106).
- **Lösung / Workaround:** Branch `docs/paper-findings`: alle Punkte umformuliert, Schluss neu (Architektur überlässt den schwersten Schritt dem Modell, Faktentabelle). Trotz Kürzungen endet Kapitel 5 ca. 12 Zeilen auf Seite 9. Keine weitere Kürzung, weil der Text nach M8 ohnehin neu überarbeitet wird; Architekturabbildung und Ausblick folgen dann.
- **Gelernt:** Eine Zahl kann stimmen und trotzdem falsch gelesen werden.
- **Relevant für Ausarbeitung?** ja → Kapitel 4 und 5; Seitenbudget bei der Überarbeitung nach M8

### ISS-106 – Reflexion nach Entfernen von Kapitel 6 nur noch knapp
- **Datum / Meilenstein:** 2026-11-20 / M7
- **Kategorie:** konzept
- **Status:** akzeptiert
- **Symptom:** Kapitel 6 (Reflexion und Ausblick) ist auf Wunsch des Nutzers ganz entfallen, ohne Ersatzkapitel. Das Kriterium „Literaturbezug & Reflexion“ (10 %) verlangt aber kritische Reflexion, Grenzen und Ausblick. Weggefallen sind die Lehre zum Vorgehen (mehrere Änderungen in einem Lauf gemessen, P2 fiel von 9 auf 6), die Grenzen der Prüfungen im Code (ein gültiger `calculate`-Aufruf belegt keine richtige Rechnung, G2) und der nächste Versuch (Soll und Ist getrennt nach Dokumentart suchen).
- **Ursache:** Entscheidung des Nutzers.
- **Lösung / Workaround:** Mit Freigabe des Nutzers ein Absatz in Kapitel 5: Annahme aus Kapitel 1 nicht bestätigt, Ferrazzi et al. (die fünfte Quelle bleibt so im Literaturverzeichnis), Einordnung „spricht nicht gegen agentisches RAG an sich, Grenze eines 7B-Modells auf der CPU“. Grenzen der Messung bleiben in Kapitel 5, Grenzen von Parser und Suche in Kapitel 2 und 4, Ausblick nur noch Faktentabelle und Hausverwaltung in Kapitel 4.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 5; mögliche Prüferfrage nach Reflexion und Ausblick

### ISS-105 – Text klang nach KI, Fragen-Kürzel schwer lesbar; erste Überarbeitung drei Seiten zu lang
- **Datum / Meilenstein:** 2026-11-20 / M7
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Der Nutzer fand Stellen, die nach KI klingen, und wollte „synthetischer Korpus“ nicht mehr lesen. Sätze wie „Bei den Prüffragen G1, G3 und G4 steckt je ein eingebauter Fehler …, bei S5, G2 und Z1 zählt eine gemeldete Abweichung als Fehlalarm“ setzen voraus, dass man sich die Kürzel merkt. Eigener Fehler: Der erste Entwurf der Überarbeitung war rund 470 Wörter länger und die neue Fragentabelle stand mit vielen Umbrüchen auf einer eigenen Gleitseite; das PDF hatte 11 statt 8 Seiten Inhalt.
- **Ursache:** Text stark verdichtet (eine Zahl je Satz, viele Kurzsätze, Inversionen wie „Messbar half …“, Pointen am Absatzende); die Kürzel S/G/N/Z wurden nach Kapitel 1 vorausgesetzt (Hinweis in `status.md`). Beim Umschreiben die Wortzahl nicht vorab gegen das Seitenbudget gerechnet, obwohl der Hinweis dazu in `status.md` steht.
- **Lösung / Workaround:** Kürzel aus dem Fließtext entfernt, Fragen über ihren Inhalt benannt; Tabelle 5.1 zeigt alle 14 Fragen (gekürzt) mit Abrechnung (korrekt / mit Fehler) und Ergebnis je Variante, darunter die Kennzahlen; RAGAS-Werte stehen jetzt im Text. „Synthetisch“ ersetzt durch „selbst erstellte PDFs eines erfundenen Haushalts“ bzw. „Testdokumente“. Sätze mit ausgeschriebenen Begründungen und Übergängen neu formuliert. Zum Ausgleich gestrichen: Gas-„Preissenkung“ (Kapitel 1), Laufzeiten von P1/P2 am Ende von Kapitel 3 (stehen in Tabelle 5.1), einzelne Nebensätze; Tabelle in `\footnotesize` und `[!t]`. Inhalt endet auf Seite 8 mit gut einer Zeile frei.
- **Gelernt:** Bei Umformulierungen die Wortzahl je Kapitel vor dem ersten Build gegen das alte PDF rechnen.
- **Relevant für Ausarbeitung?** ja → Kapitel 1–5

### ISS-104 – Text klang, als sei agentisches RAG generell schlecht; Rechtsberatung entfernt
- **Datum / Meilenstein:** 2026-11-20 / M7 (Endprüfung)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Der Nutzer las Kapitel 5 und 6 so, als sei agentisches RAG schlecht. Die Sätze „Die Annahme … hat sich nicht bestätigt“, „Der Agent ist nicht besser als die Pipeline“ und „lohnt sich nur, wenn …“ galten ohne Einschränkung, obwohl nur ein 7B-Modell auf der CPU mit 14 Fragen gemessen wurde. Außerdem soll der Text nichts zum Hinweis „keine Rechtsberatung“ enthalten und das Wort „Inferenz“ vermeiden (Wunsch des Nutzers).
- **Ursache:** Befund beim Schreiben verallgemeinert, die Einordnung (mehr Sollfakten im Kontext, Engpass beim Lesen und Vergleichen) stand nur in Kapitel 5.
- **Lösung / Workaround:** Kapitel 5 „In diesem Aufbau“, Kapitel 6 „in diesem Prototyp“ und neue Einordnung: spricht nicht gegen agentisches RAG an sich, P2 hatte mehr Sollfakten im Kontext (18 gegen 16), scheiterte am Lesen und Vergleichen, also vor allem an den Grenzen eines 7B-Modells auf der CPU. Rechtsberatung aus Kapitel 1 und 6 gestrichen (ISS-088 bleibt als Lücke im Code, steht aber nicht mehr im Text). „Telekommunikations-“ ersetzt (Überlauf). Inhalt 8 Seiten.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1, 5, 6

### ISS-103 – Endprüfung: Quellenlücken, widersprüchlich wirkende Stellen und KI-Klang
- **Datum / Meilenstein:** 2026-11-20 / M7 (Endprüfung)
- **Kategorie:** ki-assistent (auch konzept)
- **Status:** gelöst
- **Symptom:** Der Nutzer wollte vor der Abgabe Quellen, KI-Klang und Stellen prüfen lassen, die nach Nicht-Verstehen aussehen. Gefunden: (1) Lewis 2020 und Gao 2023 aus der Literaturliste der Vorlesung fehlten, obwohl Kapitel 1 „einfaches RAG“ und „modulare Pipeline“ nennt; (2) Kapitel 4 zitierte Xiang et al. gegen einen Graphen, ohne zu sagen, warum Prüffragen trotz zweier verknüpfter Fakten als Faktensuche gelten; (3) Kapitel 1 und 3 nannten P2 „ReAct-Muster“ und räumten danach die Variante Act ein; (4) Kapitel 1 stellte 8.192 Token wie eine Grenze des Modells dar, es ist eine eigene Einstellung (ADR-0004, ADR-0011); (5) Kapitel 6 „P1 lag vorn“ bei 1 gegen 0 Grenzfällen widersprach Kapitel 5 (ein bis zwei Fragen unsicher); (6) Kapitel 3 „brachte keine richtige Antwort mehr (6 von 14)“ las sich wie null richtige; (7) Kapitel 4 vermischte im Filter-Satz Retrieval-Test und Agentenlauf; (8) „Das Jahr prägte den Vektor“ stand als Tatsache da, ist laut ISS-072 eine Deutung; (9) Kapitel 6 „Jede neue Nachricht verändert den Prompt“ war banal formuliert. Zum KI-Klang: Begriffe zum Abhaken („Die Qualitätsaussage lautet damit“, „Evidence-First-Prinzip“, Satz mit Query-Rewriting, Hybrid-Suche und BM25), elf mit Komma verbundene Hauptsätze, gleichförmige Vorbehalte am Absatzende, Reflexion ohne Bewertung des eigenen Vorgehens. Die Orchestrierung (Bewertungskriterium Architektur) war beschrieben, aber nicht benannt.
- **Ursache:** (3) entstand durch die eigene Präzisierung in ISS-102; (5), (6) und (9) wurden in den Endkontrollen ISS-098 und ISS-102 übersehen; „Modular RAG“ wurde am 2026-11-19 ohne Quelle gestrichen, statt Gao zu zitieren (ISS-099); die übrigen Sätze wurden beim Kürzen auf das Seitenbudget zu stark verdichtet.
- **Lösung / Workaround:** Entscheidung des Nutzers: höchstens fünf Quellen insgesamt. Literatur jetzt ReAct, Gao et al., RAGAS, Xiang et al., Ferrazzi et al.; Self-RAG und die RAGAS-Dokumentation entfernt (Vergleich mit Self-RAG gestrichen, Context Recall in eigenen Worten als Metrik der RAGAS-Bibliothek). Gao vorher gegen arXiv v5 gelesen: Naive RAG als „Retrieve-Read“ mit Top-K, Query-Rewriting als Vorverarbeitung im Advanced RAG, Modular RAG mit austauschbaren oder umkonfigurierbaren Modulen; zitiert bei „einfaches RAG“ (Kapitel 1) und bei den einzeln abschaltbaren Bausteinen der Suche (Kapitel 4). Alle neun Stellen korrigiert, Orchestrierung in Kapitel 3 benannt (Modell wählt zur Laufzeit, eigene Schleife führt aus und begrenzt), Kapitel 6 neu gegliedert (Ergebnis, Lehre zum Vorgehen, Grenzen der Prüfungen im Code, nächster Schritt). Zum Ausgleich gekürzt: Rechnung zu S2, „zu lang“-Satz, Self-RAG-Halbsätze, einzelne Wörter an Absatzenden. Inhalt weiter 8 Seiten (endet unten auf Seite 8), Literatur Seite 9. PDF `Claude outputs/Ausarbeitung-Endpruefung.pdf`. Restrisiko: Gao ordnet Metadaten im Index und Query-Rewriting dem Advanced RAG zu, der Text nennt P1 nach der Vorlesung „modulare Pipeline“; mögliche Prüferfrage.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1 bis 6, Literaturverzeichnis

### ISS-102 – Quellenprüfung: sieben Stellen ungenau zitiert oder formatiert
- **Datum / Meilenstein:** 2026-11-20 / M7 (Quellenprüfung)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Auf Wunsch des Nutzers alle fünf Quellen erneut auf arxiv.org, aclanthology.org und iclr.cc geprüft und jede Textstelle mit dem Paper verglichen. Bibliografische Angaben stimmten, ICLR 2026 bei Xiang et al. ist jetzt bestätigt. Ungenau waren: (1) Literatur [Ferrazzi] mit „Adresse: https://…“ (deutscher Bibstring des IEEE-Stils), ohne DOI, Tagungsband nicht offiziell benannt; (2) Kapitel 6 „nicht ob der Inhalt stimmt“, obwohl Self-RAG Relevanz und Belegtreue bewertet, nicht Richtigkeit (Widerspruch zur eigenen Trennung in Kapitel 5); (3) Kapitel 3 „übernehmen … die Selbstprüfung“, obwohl nur ein Teil abgedeckt ist; (4) Kapitel 5 nennt Context Recall im Satz mit dem RAGAS-Zitat, das Paper enthält die Metrik nicht, und ragas 0.4.4 urteilt laut Code je Aussage, nicht je Satz; (5) Kapitel 3 „schreibt keinen Thought aus“, obwohl der System-Prompt gar keinen verlangt, die Läufe entsprechen der Variante „Act“ des ReAct-Papers; (6) Kapitel 4 „verlängert den Prompt deutlich“ gilt nicht für alle Graph-Varianten (HippoRAG2); (7) Kapitel 6 „3,3-mal“ ist ein Mittelwert, das Fazit nennt „bis zu 3,6-mal“.
- **Ursache:** Beim Einbau am 2026-11-19 nur Abstract, Einleitung und Ergebnisse gesichtet und die Aussagen knapp verdichtet; Prompt und RAGAS-Code nicht gegen die Formulierung geprüft; Literaturverzeichnis nur auf fehlende Verweise, nicht auf Formatierung geprüft.
- **Lösung / Workaround:** Alle sieben Stellen präzisiert, RAGAS-Dokumentation als Quelle [5] ergänzt (Ferrazzi jetzt [6]), DOI statt URL, Bibstring „Verfügbar unter“, kein Umbruch nach „https:“. Seitenumbrüche unverändert, Inhalt endet auf Seite 8, Literatur auf Seite 9; zum Ausgleich in Kapitel 6 „fanden ihn“ gestrichen. PDF `Claude outputs/Ausarbeitung-Quellenpruefung.pdf`.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 3 bis 6, Literaturverzeichnis

### ISS-101 – Context Recall steht nicht im RAGAS-Paper
- **Datum / Meilenstein:** 2026-11-19 / M7 (Quellen)
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** Kapitel 5 nutzt die RAGAS-Metriken Faithfulness und Context Recall. Das zitierte Paper (Es et al., EACL 2024) beschreibt Faithfulness, Answer Relevance und Context Relevance, aber kein Context Recall.
- **Ursache:** Context Recall kam später in die RAGAS-Bibliothek; die Definition steht nur in der Dokumentation.
- **Lösung / Workaround:** Zitat nur bei der ersten Nennung von RAGAS; Context Recall bleibt ohne Paper-Beleg. Falls ein Prüfer fragt: Definition aus der RAGAS-Dokumentation (Abschnitt „Technische Dokumentation“ in `sources.md`). Nachtrag 2026-11-20: Dokumentation jetzt als eigene Quelle direkt bei Context Recall zitiert (ISS-102).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Hintergrund für Nachfragen)

### ISS-100 – Aussage „Docling wäre auf der CPU langsam“ ungemessen
- **Datum / Meilenstein:** 2026-11-19 / M7 (Quellen)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Kapitel 2 begründete den Verzicht auf ein Layoutmodell unter anderem damit, dass Docling auf der CPU langsam wäre. Der Docling Technical Report (arXiv 2408.09869) beschreibt das Gegenteil: effizient auf Standardhardware mit kleinem Ressourcenbudget.
- **Ursache:** Begründung aus ADR-0007 (M2) übernommen; sie war eine Annahme von Claude und wurde nie gemessen.
- **Lösung / Workaround:** Satz in Kapitel 2 geändert („stützt sich auf eigene KI-Modelle und wäre nicht Regel für Regel erklärbar“), Nachtrag in ADR-0007.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 2 (umgesetzt)

### ISS-099 – Literaturbezug nachgeholt, Entscheidung „keine Literatur“ aufgehoben
- **Datum / Meilenstein:** 2026-11-19 / M7 (Quellen)
- **Kategorie:** konzept
- **Status:** offen (Paper vom Nutzer noch nicht selbst gelesen)
- **Symptom:** Kriterium 6 „Literaturbezug & Reflexion“ (10 %) war seit 2026-11-14 bewusst ohne Quellen (Risiko in status.md).
- **Ursache:** Entscheidung vom 2026-11-14, um Aufwand zu sparen.
- **Lösung / Workaround:** Auf Wunsch des Nutzers 21 Quellen gesichtet (`sources.md`), fünf zitiert: ReAct, Self-RAG, RAGAS (Begriffe standen schon im Text), Xiang et al. 2026 zur GraphRAG-Entscheidung (Kapitel 4), Ferrazzi et al. 2026 zum Vergleich Agent und Pipeline (Kapitel 6). „Modular RAG“ ohne Quelle aus dem Text genommen. Für die zwei neuen Sätze an sechs Stellen gekürzt; Inhalt weiter 8 Seiten, Literaturverzeichnis auf Seite 9 (zählt laut requirements nicht mit). Risiken: Die Paper sind von Claude über Abstract, Einleitung und Ergebnisse gesichtet, nicht vom Nutzer gelesen; Xiang et al. sprechen von „Faktensuche“, die Prüffragen vergleichen aber zwei Werte (Aussage gilt für die einzelnen Nachschlage-Schritte); die Tagung ICLR 2026 bei Xiang et al. steht nur im PDF-Kopf von v3. Nachtrag 2026-11-20: ICLR 2026 auf iclr.cc bestätigt; Quellenprüfung mit sieben Präzisierungen (ISS-102).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1 bis 6, Literaturverzeichnis

### ISS-098 – Endkontrolle: zwei ungenaue Aussagen, ein abweichender Begriff, eine zu sichere Aussage
- **Datum / Meilenstein:** 2026-11-19 / M7 (Endkontrolle)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Beim Abgleich jeder Zahl und Absolutaussage mit `evaluation-log.md`, ADRs, `ground_truth.yaml`, den Chunk-Dateien, PDFs und Laufprotokollen fielen auf: (1) Kapitel 2 „jede Seite endet mit Bank- und Registerangaben“: 5 von 34 Seiten (Dok. 16–19 und 30 der Hausverwaltung) enden nur mit Register- und Kontaktangaben. (2) Kapitel 4 begründete die 9 ausschließenden Filter aus RUN-010 damit, dass „ein Jahr Verträge ohne Abrechnungszeitraum ausschließt“. Im Code-Stand von RUN-010 (`f46e50e`) galt der Jahresfilter aber nur zusammen mit Rechnung, Hinweis oder Abschlagsplan (ADR-0010, ISS-025); ausgeschlossen hat die Kombination Rechnung plus Jahr (8 von 9: S4, S5, G1 ×2, G2, G3 ×2, G4; dazu S1 mit `contract`). (3) Kapitel 1 schrieb „Ablenker“, Kapitel 4 und das Glossar „Ablenkungsdokument“. (4) Kapitel 4 „Ein Graph lohnt sich erst bei vielen Wohnungen“ ist ungemessen, stand aber als sichere Aussage da (writing-guide 3.3). Nebenbefund: `evaluation-log.md` (RUN-014 bis RUN-016) nannte „G2 und G4 (RUN-015)“, der Fehlalarm G2 mit falschem Operanden stammt aber aus RUN-014.
- **Ursache:** (1) und (4) beim Verdichten zugespitzt; (2) ISS-025 (M4, von Hand gesetzte Filter) mit dem Verhalten des Agenten in RUN-010 vermischt und nicht gegen den Code-Stand geprüft.
- **Lösung / Workaround:** Alle vier Sätze angepasst („fast jede Seite“, „und so meist nur in der Rechnung des gefragten Jahres suchte“, „Ablenkungsdokumente“, „vermutlich“), Nebenbefund im evaluation-log korrigiert. Jede Änderung bleibt in den bestehenden Zeilen; Zeilenvergleich alter/neuer Build zeigt sonst kein verschobenes Wort, das PDF bleibt bei 8 Seiten.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1, 2, 4 (umgesetzt)

### ISS-097 – GraphRAG-Begründung im Entwurf einseitig und unbelegt
- **Datum / Meilenstein:** 2026-11-19 / M7 (Prüfung gegen die Anforderungen)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Auf Nachfrage des Nutzers („Bist du dir sicher?“) zeigte sich: Der GraphRAG-Absatz in Kapitel 4 behandelte die Prüffragen aus `requirements.md` 5.5 nur teilweise (keine Entitäten, keine Fragen, die profitieren würden) und ließ das stärkste Gegenargument aus den eigenen Ergebnissen weg: G1 und G3 scheitern an Beziehungen (geltender Preis, Vorjahresrechnung). „LLM-Extraktion wäre langsam“ und „ein falsch extrahierter Preis schadet“ standen ohne Beleg da, obwohl Belege vorlagen (Enrichment-Zeiten, Wasser-Summary). „Ein Graph lohnt sich erst bei einer Hausverwaltung“ war zu pauschal.
- **Ursache:** Beim Schreiben von Kapitel 4 wurde die Begründung aus ADR-0003 (vor der Evaluation geschrieben) übernommen und nicht gegen die Ergebnisse aus Kapitel 5 geprüft.
- **Lösung / Workaround:** Absatz neu geschrieben: Entitäten, Beziehungen, betroffene Fragen G1/G3, Gründe gegen LLM-Extraktion mit Belegen (Schätzung ca. 3 h, Wasser-Summary), Faktentabelle als naheliegendere Alternative, Hinweis, dass nichts davon gemessen ist. ADR-0003 und concept §10 nachgetragen. Kapitel 4 wächst von ca. 490 auf ca. 570 Wörter; dafür an fünf Stellen in Kapitel 1–3, 5 und 6 gekürzt. Das PDF endet jetzt ganz unten auf Seite 8 (kein Puffer mehr).
- **Gelernt:** Entscheidungen, die vor der Evaluation fielen, im Text gegen die Ergebnisse prüfen.
- **Relevant für Ausarbeitung?** ja → Kapitel 4 (umgesetzt)

### ISS-096 – Fragen zur Ausarbeitung unbeantwortet, Überarbeitung Teil 2 entfallen
- **Datum / Meilenstein:** 2026-11-19 / M7 (Ausarbeitung)
- **Kategorie:** konzept
- **Status:** akzeptiert
- **Symptom:** Die 30 Fragen in `paper-questions.md` (Kapitel 1–6) sind unbeantwortet, zum PDF liegen keine Markierungen und für Kapitel 6 keine eigenen Eindrücke vor. Damit fehlte die Grundlage für Überarbeitung Teil 2 (Formulierungen des Nutzers einarbeiten). Entscheidung des Nutzers: direkt zur Endkontrolle.
- **Ursache:** Zeitmangel des Nutzers (vgl. ISS-085/087).
- **Lösung / Workaround:** Überarbeitung Teil 2 gestrichen; die Endkontrolle prüft Zahlen, Begriffe, Zusammenhang und Seitenzahl. Die Fragen bleiben in `paper-questions.md` als Vorbereitung auf Nachfragen. Risiko: Der Text enthält keine Formulierungen des Nutzers (Checkliste `writing-guide.md` Abschnitt 4, „eigene Formulierungen ergänzt“, „jeden Absatz mündlich erklären“), Verständnis ist laut `requirements.md` bewertungsrelevant.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein (betrifft Abgabe und mögliche Nachfragen)

### ISS-095 – Kapitel passten an mehreren Stellen nicht zueinander
- **Datum / Meilenstein:** 2026-11-18 / M7 (Überarbeitung Teil 1)
- **Kategorie:** ki-assistent
- **Status:** gelöst (Restpunkte am 2026-11-19 umgesetzt)
- **Symptom:** Die sechs Kapitel entstanden in getrennten Sitzungen; jede prüfte ihre Zahlen, aber nicht den Zusammenhang. Beim Querlesen fielen auf: Kapitel 1 beschrieb als Ist-Zustand, dass der Prototyp Soll- und Istwert getrennt sucht, obwohl der feste Prüfablauf abgeschaltet ist (Kapitel 3); die Fragekürzel (S2, G1, Z1) und P2 standen in Kapitel 3 und 4 vor ihrer Erklärung in Kapitel 5; Kapitel 3 nannte Z1 noch „Grenzfall“ statt „knapp als richtig gewertet“; die Kennung E1 kam nur in Kapitel 2 vor; die 629 Chunks in Kapitel 4 ließen sich aus den 564 in Kapitel 2 nicht herleiten; „18 von 23“ (Kapitel 3) und „19-mal“ (Kapitel 5) standen unverbunden nebeneinander; Kapitel 3 nahm die Begründung aus Kapitel 6 vorweg; in Kapitel 6 fehlte zu „Welche“ das Bezugswort. Alle Zahlen stimmten mit `evaluation-log.md` überein (auch die Zeiten im Listing, nachgeprüft in `run-021/p2-Z1.jsonl`).
- **Ursache:** Kapitelweises Schreiben mit Prüfung nur gegen die Quellen, nicht gegen die anderen Kapitel.
- **Lösung / Workaround:** Abkürzungen S/G/N/Z und P2 in Kapitel 1 eingeführt, G1 dort markiert, Kapitel 1 als Ziel („soll“) formuliert, übrige Stellen angeglichen. Eine erste Fassung der Korrekturen (Erklärung der z-Zahl in Kapitel 3, Summaries in Kapitel 4) verschob Gleitobjekte und kostete 0,12 S.; sie wurde gekürzt bzw. nach Kapitel 2 in einen Absatz mit freier Zeile verlegt, das PDF endet wieder bei gut 80 % von Seite 8. Restpunkte aus Platzgründen offen: z-Zahl wird nirgends erklärt (Kapitel 3, 5), die 10 Retrieval-Testfragen (Kapitel 2, 4) sind nicht ausdrücklich als Teilmenge eines früheren Katalogs gekennzeichnet, Lauf-Kennungen (RUN-011, RUN-021) in den Bildunterschriften werden nicht erklärt. Nachtrag 2026-11-19: alle drei umgesetzt (z-Zahl in Kapitel 3 erklärt, „10 beantwortbare Fragen eines ersten Katalogs“ in Kapitel 2/4, Lauf-Kennung in Kapitel 5 eingeführt).
- **Gelernt:** Ergänzungen kosten im fertigen Satz ganze Zeilen; vorher prüfen, wo ein Absatz auf seiner letzten Zeile noch Platz hat.
- **Relevant für Ausarbeitung?** ja → alle Kapitel (Endkontrolle)

### ISS-094 – Qualitätsaussage in Kapitel 5 stützt sich auf eine Handprüfung durch Claude
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 5)
- **Kategorie:** ki-assistent
- **Status:** offen
- **Symptom:** Kapitel 5 nennt „richtig nach Handprüfung“ (B0 3, P1 8, P2 6 von 14) als Hauptergebnis und die von Hand vergebenen Hauptursachen der Fehlschläge. Beides hat Claude beim Auswerten der Läufe gemacht (`evaluation-log.md`, RUN-010 bis RUN-021); der Text sagt nur „nicht unabhängig gegengelesen“, nicht wer geprüft hat. Bei ISS-086 und ISS-091 musste Claude eigene Deutungen schon einmal korrigieren.
- **Ursache:** Zeitmangel (ISS-084/085/087); die Handprüfung wurde nie vom Nutzer gegengelesen.
- **Lösung / Workaround:** Entscheidung des Nutzers am 2026-11-18: kein Hinweis auf die Rolle von Claude, weder in Kapitel 5 noch in einer KI-Erklärung; der KI-Hinweis der Vorlage ist entfernt (Kennzeichnung laut `requirements.md` nicht vorgesehen). Offen bleibt das Gegenlesen: Der Nutzer sollte mindestens RUN-020 G1, G2, Z1, RUN-021 G2, Z1 und RUN-011 B0/S5 selbst lesen, damit er die Handprüfung im Gespräch erklären kann.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 5 (Grenzen), Kapitel 6, ggf. KI-Hinweis

### ISS-093 – Erstentwurf Kapitel 4 zu lang und mit drei ungenauen Aussagen
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 4)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Der erste Entwurf hatte gut 500 Wörter statt der geplanten ca. 370; eine spätere Fassung kam gemessen auf 1,39 statt 1,25 Seiten. Beim Gegenlesen gegen die Quellen fielen drei Aussagen auf, die so nicht stimmten: „Überschriften sind keine eigenen Chunks“ (es gibt 82 Überschriften-Chunks, sie werden nur nicht eingebettet), „die Zeile mit 38,20 ct enthält weder Jahr noch Dokumentwort“ (ihr Präfix enthält „01.01.2025“; ISS-072 sagt „kaum“), „bekam nur Treffer aus dem Schreiben zur Zwischenablesung“ (die Gegenstück-Suche lieferte zusätzlich Grundpreiszeilen). Außerdem bezeichnet „Sollzahlen“ (ADR-0017, evaluation-log) die 27 Sollfakten nicht genau, 5 davon sind Fristen, Datum oder Urteil.
- **Ursache:** Beim Verdichten wurden Aussagen aus den Quellen zugespitzt; die Länge wurde wie bei Kapitel 2 und 3 unterschätzt.
- **Lösung / Workaround:** Alle drei Sätze an die Quellen angepasst, im Text „Sollfakten“ statt „Sollzahlen“, Glossar ergänzt. Gekürzt in sieben Build-Runden auf 1,25 Seiten, gemessen von Überschrift bis Überschrift. Nachtrag Kapitel 5: erster Entwurf 542 Wörter (Ziel ca. 420), gemessen 1,75 Seiten; nach drei Kürzungsrunden 1,43 Seiten bei gut 480 Wörtern und einer Tabelle mit zehn Zeilen. Weggelassen, aber für Kapitel 6 vorgemerkt: Verlauf von P2 (3 → 9 → 6) und der einmal erkannte Fehler in G4 (RUN-014). Nachtrag Kapitel 6: erster Entwurf 334 Wörter (Ziel ca. 270), vor dem ersten Build in zwei Runden auf ca. 280 Wörter gekürzt; gemessen 0,70 Seiten (Budget 0,75). Diesmal vor dem Build gezählt: zwei Builds (0,73 S., nach Kürzung einer Restzeile 0,70 S.).
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein (Arbeitsweise; bei der Endkontrolle jede Zahl und jede Absolutaussage gegen die Quelle prüfen)

### ISS-092 – Kapitel 3 kommt auf ca. 1,6 statt 1,5 Seiten
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 3)
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** Der erste Entwurf von Kapitel 3 hatte 616 Wörter und kam mit Tabelle und Listing auf ca. 2,1 Seiten. Nach drei Kürzungsrunden liegt das Kapitel bei ca. 1,6 Seiten (gemessen Überschrift bis Überschrift).
- **Ursache:** Wieder zu viel Text im ersten Entwurf, obwohl die Gliederung ca. 430 Wörter vorsah; Tabelle (Gleitobjekt) und Listing brauchen zusammen ca. 0,4 Seiten, und Gleitobjekte lassen am Seitenende Lücken.
- **Lösung / Workaround:** Gekürzt wurden Belegnummer und Trefferkürzung (kommen in Kapitel 4), Text-Aufrufe, Speicherwerte der Modelle und die Begründung zur Werkzeugzahl. Hochrechnung jetzt ca. 7,7 von 8 Seiten (1,3 + 1,3 + 1,6 + 1,25 + 1,5 + 0,75). Kapitel 4 bis 6 dürfen ihr Budget nicht überschreiten.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein (Planung)

### ISS-091 – ADR-0014 schreibt den Rückgang ungültiger Werkzeugaufrufe dem Suchwerkzeug zu
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 3)
- **Kategorie:** ki-assistent
- **Status:** gelöst (Doku korrigiert)
- **Symptom:** ADR-0014 nennt als positive Folge „kein ungültiger Werkzeugaufruf in 24 Aufrufen (RUN-010: 13 von 37)“. Beim Auszählen der Protokolle für Kapitel 3 zeigte sich: 11 der 13 ungültigen Aufrufe in RUN-010 waren `calculate`, nur 2 `search_tables`. In RUN-012 kam `calculate` gar nicht vor (ISS-058).
- **Ursache:** Eigene Fehldeutung beim Schreiben von ADR-0014: Der Vergleich wurde nicht nach Werkzeug aufgeschlüsselt.
- **Lösung / Workaround:** Nachtrag in ADR-0014 und in `evaluation-log.md` (RUN-021, Nachtrag Werkzeugnutzung). Kapitel 3 nennt die Zahl nicht als Wirkung des Suchwerkzeugs, sondern die Fehleranalyse (18 von 23 Fehlschlägen bei Werkzeugwahl und Filtern).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 3 (Zahl bewusst nicht verwendet)

### ISS-090 – Seitenbudget knapp: Kapitel 1 und 2 zusammen ca. 0,35 Seiten über Plan
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 2)
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** Der erste Entwurf von Kapitel 2 kam auf ca. 1,7 Seiten bei 1,0 Seiten Budget (plus 0,25 für das Listing). Erst nach Kürzen auf ca. 400 Wörter lag er bei ca. 1,3 Seiten. Mit derselben Messung (Kapitelüberschrift bis Kapitelüberschrift) kommt Kapitel 1 auf ca. 1,3 statt der notierten 1,2 Seiten.
- **Ursache:** Die Faustregel „ca. 400 Wörter je Seite“ trifft zu, der erste Entwurf hatte aber über 500 Wörter. Wie Kapitel 1 gemessen wurde, war nicht notiert; die Abweichung von 0,1 Seiten stammt vermutlich aus der Messmethode.
- **Lösung / Workaround:** Messmethode in `concept.md` §14 festgehalten. Kapitel 2 gekürzt; dabei fiel das Problem der aneinanderstoßenden Tabellen (ISS-014) heraus (in `paper-questions.md` vermerkt). Hochrechnung: ca. 7,6 von 8 Seiten. Kapitel 3 bis 6 vor dem Schreiben auf Wortzahl planen (ca. 400 Wörter je Seite abzüglich Tabellen).
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein (Planung)

### ISS-089 – LaTeX in Claudes Shell unvollständig: deutsches babel und biblatex fehlen
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 1)
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** `latexmk -pdf main.tex` bricht in Claudes Shell ab (`Unknown option 'ngerman'`, `File 'biblatex.sty' not found`). Der Hinweis in `status.md` („latexmk, pdflatex, lualatex sind in Claudes Shell vorhanden; Seitenzahl damit selbst prüfen“) stimmte nur halb: Die Programme sind da, die Pakete `texlive-lang-german` und `texlive-bibtex-extra` nicht.
- **Ursache:** Die VM enthält nur einen Teil von TeX Live. Warum der Hinweis ohne erfolgreichen Probelauf in `status.md` stand, ist nicht mehr nachvollziehbar.
- **Lösung / Workaround:** `paper/` als Archiv in den Projektordner packen, mit `device_stage_files` in Claudes Cloud-Umgebung kopieren und dort nach `apt-get install texlive-lang-german texlive-bibtex-extra texlive-plain-generic biber` kompilieren. Danach das Archiv löschen. Seitenzahl und Layout werden dort geprüft. Auf dem Laptop des Nutzers ändert sich nichts.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-088 – Hinweis „keine Rechtsberatung“ fehlt in Prompt und Oberfläche
- **Datum / Meilenstein:** 2026-11-18 / M7 (Kapitel 1)
- **Kategorie:** konzept
- **Status:** akzeptiert
- **Symptom:** `concept.md` §12 sieht gegen das Risiko „Antworten wirken wie Rechtsberatung“ einen Hinweis im System-Prompt und in der UI vor. Beim Materialsammeln für Kapitel 1 zeigte sich: Weder `agent/prompts.py` noch `agent/app.py` enthalten einen solchen Hinweis. Die Abgrenzung wirkt nur indirekt über die Prompt-Regeln (Abweichung mit beiden Werten und Unterschied nennen, bei fehlenden Belegen „Dazu liegen in den Unterlagen keine Angaben vor.“ statt raten).
- **Ursache:** In M5 beim Bau von Prompt und Streamlit-UI übersehen; der Risikoplan wurde vor dem Meilenstein-Abschluss nicht gegen den Code geprüft.
- **Lösung / Workaround:** Phase 1 ist abgeschlossen, der Code bleibt unverändert. Kapitel 1 nennt die Lücke offen. Für ein Folgeprojekt: ein Satz im System-Prompt und ein `st.caption` unter der Antwort.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel 1 (Abgrenzung), ggf. Reflexion

### ISS-087 – Kein O-Ton mehr für das Entwicklungstagebuch
- **Datum / Meilenstein:** 2026-11-18 / Übergang Phase 1 → Phase 2
- **Kategorie:** konzept
- **Status:** akzeptiert
- **Symptom:** Der Nutzer kann ab 2026-11-18 grundsätzlich keinen O-Ton mehr liefern. Von 20 Einträgen im `dev-journal.md` hat nur einer einen O-Ton (2026-11-17); die übrigen standen auf „ausstehend“ oder „nicht geliefert“.
- **Ursache:** Zeitmangel des Nutzers (vgl. ISS-085).
- **Lösung / Workaround:** Claude fragt nicht mehr nach dem O-Ton; das Feld steht auf „(nicht geliefert, ISS-087)“. Die Reflexion in Phase 2 stützt sich nur auf belegte Einträge (issues-log, evaluation-log, ADRs, der eine vorhandene O-Ton) und erfindet keine persönlichen Eindrücke. Der Nutzer muss den persönlichen Teil vor der Abgabe selbst lesen und bei Bedarf ergänzen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Reflexion (Risiko: generischer Text)

### ISS-086 – Abgleich „Context Recall gegen Sollfakten“ zählt Scheinwidersprüche
- **Datum / Meilenstein:** 2026-11-18 / M6 (RAGAS-Auswertung v1.0.0)
- **Kategorie:** evaluation (auch ki-assistent: Fehldeutung in RUN-010/011)
- **Status:** akzeptiert
- **Symptom:** `scripts/check_evidence.py` meldet für RUN-020/021 8 von 24 Context-Recall-Werten als Widerspruch („alle Sollfakten im Kontext“ gegen Wert ≥ 0,5). Von Hand gegen Referenzsatz und Belege gelesen, ist keiner davon ein Fehlurteil des Bewerters. Das echte Fehlurteil P2/S2 (0,50, obwohl beide Preise im Kontext stehen) zählt der Abgleich dagegen nicht. Claude hat dieselbe Zählung in RUN-010/011 (13 von 48) und in ISS-053, Punkt 3, als Unzuverlässigkeit des Bewerters gedeutet; das war vermutlich zum Teil eine Fehldeutung.
- **Ursache:** Zwei verschiedene Bezugsgrößen. RAGAS urteilt je Aussage der Referenzantwort (`expected_answer`; zuerst als „je Satz“ notiert, laut Code von ragas 0.4.4 je Aussage, ISS-102), der Abgleich prüft die Sollfakten (`facts`). Die Referenzsätze enthalten zusätzlich berechnete Werte, Flächen, ältere Ablenker-Werte und Hinweise, die in keinem Beleg stehen (G1–G4, Z2, Z3); umgekehrt enthalten die Sollfakten Urteile wie „Abrechnung korrekt: ja“ (S5), die nie in einem Beleg stehen. Dazu kommt die Ja/Nein-Schwelle 0,5 gegen einen anteiligen Wert (S2).
- **Lösung / Workaround:** Widersprüche von Hand auflösen (`evaluation-log.md`, RAGAS-Nachtrag RUN-020/021). Nur bei Zeit: Urteilsfakten im Abgleich auslassen und den Anteil der Sollfakten im Kontext mit Context Recall vergleichen. Die Referenzantworten bleiben unverändert, damit die Läufe vergleichbar bleiben.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen), Reflexion

### ISS-085 – Verständnisfragen M6 nicht selbst beantwortet, Erklärungen von Claude eingetragen
- **Datum / Meilenstein:** 2026-11-17 / M6 (Reverse Engineering)
- **Kategorie:** konzept
- **Status:** offen
- **Symptom:** Der Nutzer kann die 24 Fragen R1-1 bis R3-8 nach eigener Aussage mangels Vorwissen und Zeit nicht beantworten. Auf seinen Wunsch hat Claude die Fragen in einfacher Sprache beantwortet; die Erklärungen stehen in einer eigenen Spalte „Erklärung (Claude)“ in Abschnitt 6 der drei M6-Notizen, „Meine Antwort“ ist leer. Abschnitte 5–7 der Notizen M0–M6 sind ebenfalls noch leer.
- **Ursache:** Zeitmangel und fehlendes Vorwissen (Aussage des Nutzers).
- **Lösung / Workaround:** Erklärungen vor Phase 2 lesen; Ausarbeitung in eigener Sprache schreiben; in der Reflexion offen nennen, dass das Reverse Engineering mit KI-Erklärungen erfolgte. Risiko: Verständnis ist laut `requirements.md` (Abschnitt 7) bewertungsrelevant.
- **Gelernt:** Reverse Engineering gesammelt am Ende ist zu viel auf einmal; besser direkt nach jedem Meilenstein.
- **Relevant für Ausarbeitung?** ja → Reflexion, Vorgehen

### ISS-084 – Verständnisfragen zum Reverse Engineering nur im Chat, nicht im Repo
- **Datum / Meilenstein:** 2026-11-17 / M6 (Reverse Engineering)
- **Kategorie:** ki-assistent
- **Status:** teilweise gelöst
- **Symptom:** Die Fragen aus den Reverse-Engineering-Runden zu M0 und M2–M6 standen nur im jeweiligen Chat. Abschnitt 6 der Notizen war leer. In einem neuen Chat lassen sich Antworten damit nicht gegen die Fragen prüfen.
- **Ursache:** Claude hat die Fragen nur im Chat gestellt und nicht in die Notizen geschrieben; die Vorlage verlangt das nicht ausdrücklich.
- **Lösung / Workaround:** Für M6 neu formulierte Fragen (R1-1 bis R3-8) in Abschnitt 6 von `m6-evaluation.md`, `m6-quantity-retrieval.md` und `m6-agent.md` eingetragen. Für M0 und M2–M5 fehlen sie noch; beim Auswerten dieser Runden zuerst die Fragen ins Repo schreiben. Künftig stehen die Fragen immer in Abschnitt 6.
- **Gelernt:** Was nur im Chat steht, ist für die nächste Sitzung verloren.
- **Relevant für Ausarbeitung?** ja → Reflexion (Arbeiten mit dem KI-Assistenten)

### ISS-083 – `is_audit_question` hält reine Nachschlagefragen mit „abgerechnet“ für Prüffragen
- **Datum / Meilenstein:** 2026-11-17 / M6 (Reverse Engineering)
- **Kategorie:** agent
- **Status:** akzeptiert
- **Symptom:** „Wie viel wurde 2024 abgerechnet?“ enthält „abgerechnet“ und gilt damit als Prüffrage; der Loop würde die Rechennachfrage stellen, obwohl nichts zu rechnen ist.
- **Ursache:** Erkennung über Wortliste auf dem Fragetext (`AUDIT_PHRASES`), bewusst einfach.
- **Lösung / Workaround:** Keine Frage im Katalog ist betroffen; die Rechennachfrage kommt höchstens einmal. Als Grenze dokumentiert.
- **Gelernt:** Eine Wortliste trennt Absicht nicht von Wortlaut.
- **Relevant für Ausarbeitung?** nein

### ISS-082 – RAGAS-Werte fehlen für den Stand v1.0.0
- **Datum / Meilenstein:** 2026-11-17 / M6 (Abgleich mit `requirements.md`)
- **Kategorie:** evaluation
- **Status:** gelöst
- **Symptom:** `ragas.jsonl` gibt es nur für RUN-009 bis RUN-011. Seitdem haben sich Werkzeuge, Größen-Anfrage und Rückfragen geändert; RUN-020/021 haben keine RAGAS-Werte.
- **Ursache:** Ab M6d lag der Fokus auf den deterministischen Metriken und der Handprüfung; ein RAGAS-Lauf kostet mehrere Stunden CPU-Zeit.
- **Lösung / Workaround:** Optional über Nacht `uv run --group ragas python -m audit_agent.evaluation ragas --run-id run-020` und danach dasselbe mit `run-021`. Ohne Lauf nennt die Ausarbeitung die RAGAS-Werte mit ihrem Code-Stand. Nachtlauf 2026-11-17/18 ohne Fehlschlag (3,1 h); Auswertung im `evaluation-log.md` (RAGAS-Nachtrag RUN-020/021), Befund zum Abgleich in ISS-086.
- **Gelernt:** Eine zweite Sicht hilft nur, wenn sie zum gleichen Stand gehört.
- **Relevant für Ausarbeitung?** ja → Testmodul, Reflexion

### ISS-081 – Hinweis „Im Gegenstück gibt es keine Treffer“, obwohl das Gegenstück schon in der Liste steht
- **Datum / Meilenstein:** 2026-11-17 / M6 (Reverse Engineering, RUN-021 G1)
- **Kategorie:** tools
- **Status:** offen
- **Symptom:** Bei G1 lieferte die Größen-Suche bereits Preisschreiben [6] und Rechnung [7]. `_counterpart_hits` fand daher nichts zu suchen und meldete dem Modell „Im Gegenstück (Vertrag bzw. Rechnung) gibt es keine Treffer.“
- **Ursache:** `_counterpart_hits` bestimmt die gefundenen Dokumentarten nach dem Anhängen der Größen-Treffer und unterscheidet nicht zwischen „nichts gefunden“ und „nichts mehr zu suchen“.
- **Lösung / Workaround:** Kandidat: bei leerer `wanted`-Liste „Rechnung und Vertrag bzw. Preisschreiben sind schon unter den Treffern“ melden. Nicht vor v1.0.0 geändert; Wirkung auf die Antworten unklar.
- **Gelernt:** Eine Rückmeldung an das Modell muss auch den Fall „nichts zu tun“ richtig benennen.
- **Relevant für Ausarbeitung?** nein

### ISS-080 – Sparten-Erkennung übersieht Komposita wie „Gaspreis“
- **Datum / Meilenstein:** 2026-11-17 / M6 (Reverse Engineering)
- **Kategorie:** retrieval
- **Status:** offen
- **Symptom:** „Stimmt der Strom- und Gaspreis?“ ergibt `utility_in_query` = `electricity`, weil „Strom“ allein zählt, „Gaspreis“ aber nicht (nur Dokument-Komposita wie „Gasabrechnung“). Die Größen-Suche nach „Gaspreis“ läuft dann mit Strom-Filter.
- **Ursache:** `_utility_of_word` akzeptiert hinter dem Spartenwort nur Dokumentwörter, damit „Wasserverbrauch“ in der Nebenkostenabrechnung nicht als Sparte zählt.
- **Lösung / Workaround:** Keine Frage im Katalog ist betroffen. Kandidat: Komposita mit Spartenanfang mitzählen, aber nur für das Ergebnis „mehrere Sparten → kein Filter“.
- **Gelernt:** Eine Ausnahme für einen Fall („Wasserverbrauch“) erzeugt leicht einen Fehler in einem anderen.
- **Relevant für Ausarbeitung?** nein

### ISS-079 – RUN-021 bricht nach N2 ohne Meldung ab; Fortsetzung überschreibt Protokoll und Umgebungsdatei
- **Datum / Meilenstein:** 2026-11-17 / M6i (RUN-021)
- **Kategorie:** evaluation
- **Status:** offen
- **Symptom:** `eval_run.sh run-021:qwen2.5:7b` endete nach 11 von 14 Fragen direkt beim Start von Z1 (13:59 Uhr, `p2-Z1.jsonl` leer), ohne Traceback, ohne `FERTIG`. Beim Fortsetzen (17:25 Uhr, Laptop 6 min vorher neu gestartet) über `eval_run.sh` wurden `run-021.log` und `run-021-env.txt` neu geschrieben; die Ausgaben der ersten 11 Fragen und der Speicherstand beim Start fehlen im Protokoll.
- **Ursache:** Abbruch nicht geklärt (harter Prozessabbruch; Ruhezustand, Neustart oder OOM-Killer möglich). Das Systemjournal um 13:59 wurde nicht gesichert (`journalctl -b -1` wäre nach dem Neustart nötig gewesen). `eval_run.sh` schreibt Log und Umgebung mit `tee` und `>`, nicht anhängend.
- **Lösung / Workaround:** Die Antworten sind vollständig: `generate` überspringt beantwortete Fragen, Z1 bis Z3 wurden nachgeholt, Bewertung über alle 14. Kandidat: `eval_run.sh` mit `tee -a` und Umgebung je Start anhängen.
- **Gelernt:** Ein fortsetzbarer Lauf braucht auch ein fortsetzbares Protokoll.
- **Relevant für Ausarbeitung?** nein

### ISS-078 – Claudes Shell: `/dev/shm` je Aufruf leer, `uv sync` zu langsam; Quality Gate läuft auf dem Laptop
- **Datum / Meilenstein:** 2026-11-17 / M6i
- **Kategorie:** ki-assistent
- **Status:** gelöst (Workaround)
- **Symptom:** Nach einem Verbindungsabbruch war `/dev/shm` in jedem `device_bash`-Aufruf leer (jeder Aufruf hat ein eigenes `/dev`); `uv sync` lädt rund 300 MB mit ca. 0,3–0,8 MB/s und schafft das nicht in 180 s. Auch ein Cache auf der Projektplatte (`.vm-uv/`) kam nicht über `pymupdf` (66 MB) hinaus, abgebrochene Downloads setzt `uv` nicht fort.
- **Ursache:** Sandbox der VM (eigenes `/dev` je Aufruf, `/sessions` zu 100 % voll, langsamer Proxy); Workaround aus ISS-075 hing an einem `/dev/shm`, das zwischen Aufrufen bestehen blieb.
- **Lösung / Workaround:** Quality Gate (`./scripts/check.sh`) im Befehl für das Terminal des Nutzers vor der Messung, Ausgabe nach `.vm-uv/check-m6i.log`, Messung nur bei grünem Gate (`&&`). Der Ordner `.vm-uv/` steht in `.git/info/exclude` und wurde danach gelöscht. Folge: Claude sieht Testfehler erst mit dem Messbefehl; kleine Codeprüfungen gehen weiter mit `python3` ohne Abhängigkeiten.
- **Gelernt:** Wenn die Werkzeugumgebung wackelt, gehört die Prüfung dorthin, wo die Umgebung stabil ist, und muss die teure Messung absichern.
- **Relevant für Ausarbeitung?** ja → Reflexion (Arbeit mit dem KI-Assistenten)

### ISS-077 – Größen-Anfrage ohne Sparte trifft das falsche Dokument (P1)
- **Datum / Meilenstein:** 2026-11-17 / M6h (RUN-019), gelöst in M6i (RUN-020)
- **Kategorie:** retrieval
- **Status:** gelöst
- **Symptom:** P1/G1: Die Größen-Anfrage „Arbeitspreis“ liefert zwei Treffer aus dem Gas-Preisschreiben (Kapitel „Senkung Ihres Gas-Arbeitspreises“), nicht die Strom-Zeile mit 38,20 ct. Die Sollzahlen im Kontext bleiben bei P1 13 von 27 (RUN-011: 13). P1/S5 kippt von „Ja, stimmt“ zu einem Fehlalarm mit sinnloser Rechnung (68,00 EUR).
- **Ursache:** `quantity_query` entfernt Sparten und Zusammensetzungen wie „Stromabrechnung“ ganz; P1 hat keinen Sparten-Filter (P2 übergibt `utility_type` an beide Suchen). Das Wort steht dann im Kapitel eines anderen Dokuments und bekommt den Hierarchie-Boost 1,5. Fehler im Entwurf von Claude: Der Fall P1 ohne Filter wurde nicht bedacht, und ohne Ollama ließ sich die Wirkung vorab nicht prüfen.
- **Lösung / Workaround:** M6i: `utility_in_query` erkennt genau eine Sparte („Strom“, „Gas“, „Erdgas“, „Wasser“, „Fernwärme“ allein oder vor einem Dokumentwort wie „Stromabrechnung“); `with_query_utility` setzt sie als Sparten-Filter der Größen- und der Gegenstück-Suche, nur wenn noch kein Filter gesetzt ist. Als Filter statt Suchwort, weil „Strom“ als Suchwort über den Dateinamen jedem Stromdokument den Hierarchie-Boost gäbe. Zusammensetzungen wie „Wasserverbrauch“ und Betriebskosten zählen nicht (G2/G4 brauchen Mietvertrag und Abrechnung zusammen). RUN-020 (P1): G1 0 auf 2 von 3 Sollzahlen im Kontext (Strom-Preisanpassung und Strom-Abrechnung statt Gas-Schreiben), S5 wieder „Ja, stimmt“, Sollzahlen im Kontext 13 auf 16 von 27. RUN-021 (P2): keine Änderung, der Agent setzt die Sparte selbst oder seine Anfragen nennen keine.
- **Gelernt:** Eine Anfrage, die nur noch den Fachbegriff enthält, verliert den Kontext, der das richtige Dokument bestimmt; Entfernen von Wörtern braucht eine Messung mit dem echten Embedding-Modell.
- **Relevant für Ausarbeitung?** ja → Retrieval (Grenzen), Reflexion (Fehler im Entwurf)

### ISS-076 – Leere Antwort nach der Rechennachfrage (G1, RUN-018)
- **Datum / Meilenstein:** 2026-11-17 / M6h (RUN-018)
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** P2/G1: Die erste Antwort („neuer Arbeitspreis 38,20 ct angewendet“, falsch, aber nicht leer) löst die Rechennachfrage aus; die nächste Modellantwort hat 25 erzeugte Token, aber leeren Inhalt und keinen Werkzeugaufruf. Der Loop endet mit `stop_reason=empty_answer` und liefert nichts.
- **Ursache:** Nicht geklärt (Einzelfall, ein Lauf). Die Nachfrage ersetzt keine Antwort, sondern hängt eine Nutzernachricht an; das Modell antwortet hier nur mit Steuerzeichen oder einem verworfenen Aufruf.
- **Lösung / Workaround:** Offen. Kandidat: bei leerer Antwort nach einer Rückfrage die vorherige Antwort zurückgeben oder einmal neu fragen. Erst bei Wiederholung in einem weiteren Lauf umsetzen. RUN-021 zeigt dieselbe leere Antwort, aber mit identischem Kontext und Temperatur 0 (13 von 14 Antworten wortgleich mit RUN-018); das ist eine Wiederholung derselben Eingabe, kein unabhängiger zweiter Fall.
- **Gelernt:** Jede Rückfrage des Loops braucht einen Plan für die leere Antwort danach.
- **Relevant für Ausarbeitung?** nein

### ISS-075 – VM ohne Speicherplatz: `uv sync` scheitert, alte Umgebungen anderer Sitzungen nicht löschbar
- **Datum / Meilenstein:** 2026-11-16 / M6h
- **Kategorie:** ki-assistent
- **Status:** gelöst (Workaround)
- **Symptom:** `uv sync` in Claudes Shell brach mit „No space left on device“ ab (Wurzel-Dateisystem der VM 99 % voll, 189 MB frei). Die Ordner `/tmp/uv-cache`, `/tmp/uvc-m6g`, `/tmp/venv-m6g`, `/tmp/venvs` (zusammen 3,4 GB) gehören einer früheren Sitzung (Benutzer `nobody`), sind nicht lesbar, nicht ausführbar und nicht löschbar.
- **Ursache:** Jede Sitzung legt eine eigene Umgebung (870 MB) und einen eigenen Cache (850 MB) an, wie in `status.md` verlangt (neuer Ordnername je Sitzung, ISS-065/069); frühere Ordner bleiben liegen.
- **Lösung / Workaround:** Cache und Umgebung dieser Sitzung liegen in `/dev/shm` (RAM-Speicher, 2 GB) mit `UV_LINK_MODE=hardlink` (nur eine Kopie): `export UV_CACHE_DIR=/dev/shm/uvc UV_PROJECT_ENVIRONMENT=/dev/shm/venv UV_LINK_MODE=hardlink`. Nichts davon liegt im Projektordner. Das RAM-Verzeichnis ist nach Sitzungsende weg; `uv run` baut das Projektpaket bei jedem Aufruf neu (einige Sekunden).
- **Gelernt:** Das Anlegen einer neuen Umgebung je Sitzung läuft auf einer VM mit festem Speicher irgendwann voll; ein RAM-Verzeichnis ist der Ausweg, wenn man fremde Ordner nicht löschen darf.
- **Relevant für Ausarbeitung?** nein

### ISS-074 – G3: Das Gegenstück „gleiche Stelle im Vorjahr“ fehlt weiter
- **Datum / Meilenstein:** 2026-11-16 / M6h
- **Kategorie:** retrieval
- **Status:** offen
- **Symptom:** G3 („Ist die Gasabrechnung 2026 korrekt?“) braucht die z-Zahl 0,9560 aus der Abrechnung 2025. Die Frage nennt keine Größe, die Größen-Anfrage (ISS-072) findet nichts („Gasabrechnung 2026“ besteht nur aus Dokument- und Jahreswörtern, `quantity_query` gibt `None`), und `include_counterpart` kennt nur die Familien Vertrag, Preisschreiben und Rechnung, nicht „Rechnung des Vorjahres“.
- **Ursache:** Der Code kennt Dokumentfamilien, aber keine zeitliche Beziehung zwischen zwei Rechnungen derselben Sparte und Vertragsnummer. Welche Zeile der Vorjahresrechnung gemeint ist, hängt von der geprüften Größe ab, die in der Frage fehlt.
- **Lösung / Workaround:** Offen. Kandidat: für Rechnungstreffer die Zeile mit gleicher Überschrift in der Rechnung eines anderen Zeitraums holen (Text des Treffers als Suchanfrage, Filter Sparte und Dokumentart Rechnung); kostet je Treffer eine Einbettung und mehr Kontext. RUN-018: G3 hat weiter 0 von 3 Sollzahlen im Kontext (die Antwort „stimmt sehr gut überein“ vergleicht nur den Abschlag), das Retrieval ist also weiter der Engpass.
- **Gelernt:** Eine Größen-Anfrage kann nur finden, was die Frage nennt; Fragen mit „ist alles korrekt?“ brauchen einen Plan, welche Größen zu prüfen sind (siehe Negativergebnis ADR-0016).
- **Relevant für Ausarbeitung?** ja → Retrieval (Grenzen), Agent

### ISS-073 – `parse_number` las „0,348“ als 348
- **Datum / Meilenstein:** 2026-11-16 / M6h
- **Kategorie:** evaluation
- **Status:** gelöst
- **Symptom:** Der neue Test „0,348 EUR/kWh gilt als 34,80 ct/kWh“ schlug fehl. `extract_numbers("0,348")` lieferte 348.0.
- **Ursache:** Die Erkennung englischer Tausendergruppen (`\d{1,3}(,\d{3})+`) passte auf „0,348“. Eine Tausendergruppe beginnt aber nie mit 0. Betroffen war auch die deutsche Variante mit Punkt („0.956“). Die Zahlensuche der Metrik und die Smoke-Prüfung der Anreicherung teilen sich die Funktion.
- **Lösung / Workaround:** Beide Muster verlangen jetzt eine erste Ziffer von 1 bis 9 (`numbers.py`, Test mit „0,348“, „0.956“, „0,956“). „3,480“ bleibt mehrdeutig (englisch: 3480, deutsch: 3,48) und wird wie bisher als 3480 gelesen.
- **Gelernt:** Ein Test für den neuen Einheitenfaktor deckte einen alten Fehler in einer Hilfsfunktion auf; Prüffunktionen brauchen Randfälle (führende Null).
- **Relevant für Ausarbeitung?** nein

### ISS-072 – Jahr und Dokumentwort in der Suchanfrage ziehen das Dokument, nicht die Zeile
- **Datum / Meilenstein:** 2026-11-16 / M6h (RUN-014, G1)
- **Kategorie:** retrieval
- **Status:** akzeptiert (umgesetzt in M6h; RUN-018/019: Wirkung nur bei P2/G1, bei P1 keine; Nachbesserung ISS-077)
- **Symptom:** G1: Die Suche „neuer Arbeitspreis 2025“ liefert fünf Treffer aus dem Schreiben zur Zwischenablesung (Kapitel „… 1. Halbjahr 2025“); die Zeile „Arbeitspreis … Neu Brutto 38,20 ct“ im Preisschreiben fehlt. Auch die Gegenstück-Treffer sind Grundpreiszeilen, nicht der Arbeitspreis. Das Modell antwortet „keine Angaben“. P1 (die ganze Frage als Anfrage) hat dasselbe Problem.
- **Ursache:** Das Jahr und Wörter wie „Abrechnung“ prägen die Einbettung der Anfrage stärker als der Fachbegriff, und der Hierarchie-Boost belohnt Kapitel mit „2025“ im Titel (ISS-027). Die Zeile mit der Zahl trägt kaum Jahr oder Dokumentwörter.
- **Lösung / Workaround:** `retrieval/quantity.py`: `quantity_query` entfernt Jahreszahlen, Frage- und Urteilswörter, Dokumentwörter (auch Zusammensetzungen wie „Gasabrechnung“) und Sparten, übrig bleibt die Größe („Arbeitspreis“). Eine zweite Suche mit ihr fügt bis zu `AgentSettings.quantity_hits` (2) neue Treffer an (P1 und P2); die Gegenstück-Suche nutzt dieselbe kurze Anfrage. Bleibt kein Wort übrig oder ändert sich die Anfrage nicht, entfällt die zweite Suche. Schalter: `quantity_hits=0`.
- **Gelernt:** Eine Frage und die gesuchte Zeile ähneln sich in der Einbettung wenig; die Anfrage muss wie die Zeile klingen, nicht wie die Frage.
- **Relevant für Ausarbeitung?** ja → Retrieval (Suchanfrage und Tabellenzeilen), Agent (Werkzeugentwurf)

### ISS-071 – Prüfablauf: Nachricht des Ablaufs führt zu Lückenantworten und chinesischem Text
- **Datum / Meilenstein:** 2026-11-16 / M6g (RUN-017)
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** Sind alle Prüfgrößen „nicht gefunden“ oder „nicht belegt“ (G3, G4, Z1), antwortet das Modell sofort „Dazu liegen in den Unterlagen keine Angaben vor“, bekommt die Lücken-Rückfrage und sucht erst dann frei weiter (zwei bis drei Modellaufrufe und rund 2 Minuten verloren). In S5 antwortet `qwen2.5:7b` auf die Nachricht des Ablaufs auf Chinesisch („基线值和实际值一致“) und rechnet einen erfundenen Stückpreis 1 EUR/kWh. In RUN-014 trat das nie auf.
- **Ursache:** Die Nachricht ist ein langer, formelhafter Block mit „Soll/Ist/ABWEICHUNG“ und endet ohne Sprachvorgabe; bei einem wertlosen Befund („Soll- oder Istwert nicht gefunden“) liest das Modell das als Ergebnis der Suche. Nicht einzeln getestet, was den Sprachwechsel auslöst.
- **Lösung / Workaround:** Offen. Kandidaten: negative Befunde nicht an das Modell geben (nur Treffer mit Differenz), „Antworte auf Deutsch“ in die Nachricht, Befund als Werkzeug-Antwort statt als Nutzernachricht.
- **Gelernt:** Eine Zwischennachricht des Loops ist Teil des Prompts und kann Sprache und Verhalten kippen; jede neue Nachrichtenart braucht einen eigenen Test mit dem echten Modell.
- **Relevant für Ausarbeitung?** ja → Agent (Grenzen kleiner Modelle), Reflexion

### ISS-070 – Prüfablauf: Plan und Lesen ordnen Soll und Ist falsch zu
- **Datum / Meilenstein:** 2026-11-16 / M6g (RUN-017)
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** Von 14 Prüfgrößen sind nur 4 inhaltlich brauchbar. Beide Suchseiten liefern oft dieselben Treffer (G1: 3, 2; G3: 1, 2, 3, 5), in 4 Prüfgrößen steht Soll und Ist im selben Treffer (S5, G3, G4). G1 vergleicht Rechnungsbetrag Gas mit Rechnungsbetrag Strom; G4 bekommt einen Dateinamen als Wert und 1367 als Trefferzahl; G2 sucht Zustandszahl bei einer Betriebskostenfrage.
- **Ursache:** (1) Die Suchanfragen des Plans nennen nur „Vertrag oder Preisschreiben“ und „Rechnung“ als Wörter, kein Filter trennt Vertrag und Rechnung (ADR-0014 hält `doc_type` bewusst vom Modell fern). (2) Das Lesen prüft nur die Herkunft der Zahl. (3) Die Beispielliste im Plan-Prompt (z-Zahl, Brennwert, …) wird auch dort gewählt, wo sie nicht passt. (4) Das Schema lässt freie Strings als Wert zu.
- **Lösung / Workaround:** Offen (Kandidaten in `status.md`): Soll- und Ist-Suche im Code nach Dokumentart trennen (Soll: Vertrag/Preisschreiben, Ist: Rechnung), verlangen, dass beide Zahlen aus verschiedenen Treffern stammen, Größe und Einheit im Treffer abgleichen, Zahlenfelder als Zahl im Schema, Plan-Prompt ohne Beispielliste; oder Ablauf abschalten.
- **Gelernt:** Ein fester Ablauf ersetzt nicht die Qualität der einzelnen Schritte: Er macht aus einem falschen Suchtreffer eine exakte, belegt wirkende falsche Rechnung.
- **Relevant für Ausarbeitung?** ja → Agent (Autonomie gegen Zuverlässigkeit), Evaluation (Negativergebnis)

### ISS-069 – `/tmp/uv-cache` in der VM nicht beschreibbar, Sitzungsplatte wieder fast voll (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-16 / M6g
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** `uv sync` scheiterte erst mit „No space left on device“ (Sitzungsplatte `/sessions` 98 % voll), dann mit „Permission denied“ in `/tmp/uv-cache` (der Ordner stammt aus einer früheren Sitzung). Mein Versuch, die alten Cache-Ordner unter `$HOME` zu löschen, wurde vom Berechtigungsprüfer abgelehnt.
- **Ursache:** Der feste Name aus ISS-065 kollidiert mit Ordnern anderer Sitzungen; die Regel „am besten `/tmp/uv-cache`“ war zu ungenau.
- **Lösung / Workaround:** Eigener, frischer Ordnername je Sitzung (`UV_CACHE_DIR=/tmp/uvc-m6g UV_PROJECT_ENVIRONMENT=/tmp/venv-m6g UV_LINK_MODE=copy`), nichts gelöscht. `status.md` angepasst. `/` hat danach nur noch ca. 570 MB frei; schwere Gruppen (`--group ragas`) passen in der VM nicht mehr, RAGAS läuft auf dem Laptop.
- **Gelernt:** Namen für temporäre Ordner enthalten die Sitzung oder das Paket; vor einem Löschbefehl prüfen, ob er nötig ist, statt ihn zu versuchen.
- **Relevant für Ausarbeitung?** nein

### ISS-068 – Der Prüfablauf sichert die Herkunft der Zahlen, nicht ihre Vergleichbarkeit
- **Datum / Meilenstein:** 2026-11-16 / M6g
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** (vor RUN-017 erwartet, in RUN-017 eingetreten: G1 Rechnungsbetrag Gas gegen Strom) Der Code prüft, dass Soll- und Istzahl im genannten Treffer der richtigen Suchseite stehen, nicht, dass beide dieselbe Größe meinen: Ein Modell kann aus einer Tabelle den falschen Wert (z. B. Nettopreis statt Bruttopreis, Monats- statt Jahresbetrag) lesen und der Code rechnet damit exakt. Vorzeichen gehen verloren (`extract_numbers`: Beträge ohne Vorzeichen, ISS-067 G4). Z1 (Zählerstände: zwei Werte, eine Differenz) passt nicht in das Schema „ein Soll, ein Ist“.
- **Ursache:** Die Zuordnung der Größe ist Leseverständnis des Modells; der Code kennt keine Einheiten und keine Bedeutung der Zeilen.
- **Lösung / Workaround:** Die Belegzeile steht in der Nachricht an das Modell („Soll 38,2 [1] „Arbeitspreis | 38,20 ct/kWh“…“), das Modell sieht und die Auswertung zeigt, woher die Zahl kommt. RUN-017 von Hand prüfen (Fehlalarme, `not_verified`). Möglich später: Einheit im Treffer mit der angegebenen Einheit abgleichen.
- **Gelernt:** Die Herkunftsprüfung schützt vor erfundenen Zahlen, nicht vor falsch zugeordneten; die Zuordnung gehört mit dem Modell geprüft (Größe und Einheit im Treffer) oder aus der Suche selbst gesichert (Dokumentart je Seite).
- **Relevant für Ausarbeitung?** ja → Agent (Grenzen der Zuverlässigkeit trotz festem Ablauf), Reflexion

### ISS-067 – `calculate` wird gültig, aber mit falschen Operanden aufgerufen (Fehlalarme)
- **Datum / Meilenstein:** 2026-11-16 / M6f (RUN-014, RUN-015)
- **Kategorie:** agent
- **Status:** akzeptiert (Grenze; fester Prüfablauf in RUN-017 ohne Gewinn und abgeschaltet, ADR-0016, ISS-070)
- **Symptom:** `qwen2.5:7b` rechnet in G2 `1830 - 1870` (Sollwert minus falscher Istwert) und meldet „−40,00 EUR“ bei einer richtigen Abrechnung; in S5 rechnet es `1189 - 115` (Rechnungsbetrag minus Monatsabschlag) und meldet 1.074 EUR Abweichung. `llama3.1:8b` rechnet in G4 `1.963,28 - -1.920,00` = 3.883,28 EUR (Istwert minus negative Vorauszahlung).
- **Ursache:** Die Nachfrage erzwingt einen Rechenaufruf, aber nicht die richtigen Operanden; die Modelle wählen Zahlen aus dem Kontext, die nicht zusammengehören (ISS-054). `calculate` prüft nur die Form, nicht den Sinn.
- **Lösung / Workaround:** Keine. Kandidaten: fester Prüfablauf im Code (Soll- und Istwert als benannte Felder, Code bildet die Differenz); sonst nur als Grenze dokumentieren.
- **Gelernt:** Ein gültiger Werkzeugaufruf ist kein Beleg für eine richtige Rechnung; „calculate-Aufrufe“ allein sind als Metrik ungeeignet, die Operanden müssen von Hand gelesen werden.
- **Relevant für Ausarbeitung?** ja → Evaluation (Gültigkeit gegen Richtigkeit), Reflexion (Grenzen kleiner Modelle)

### ISS-066 – Rechennachfrage wirkt bei `qwen2.5:7b`, nicht bei `llama3.1:8b`
- **Datum / Meilenstein:** 2026-11-16 / M6f (RUN-014 bis RUN-016)
- **Kategorie:** agent
- **Status:** gelöst (Modell `qwen2.5:7b` seit M6g, ADR-0016; Fehlalarme bleiben als Grenze, ISS-067)
- **Symptom:** Nach der Nachfrage ruft `qwen2.5:7b` in 3 von 4 Fällen `calculate` gültig auf (G2, G4, S5), `llama3.1:8b` in 1 von 4 (G4, sinnlos). Dafür zitiert `llama3.1:8b` 1 von 18 erwarteten Quellen, `qwen2.5:7b` 6 von 18. Handrichtig liegen beide bei 6 von 14.
- **Ursache:** Modellunterschied bei Werkzeug-Format und Befolgung von Anweisungen; nicht weiter untersucht. Der Zeitvorteil von `llama3.1:8b` aus ADR-0013 (136 gegen 298 s je Frage) besteht nicht mehr: 320 bis 325 gegen 301 s.
- **Lösung / Workaround:** Entscheidung offen (ADR-0013, ADR-0015): `llama3.1:8b` behalten, auf `qwen2.5:7b` wechseln oder den Prüfablauf fest im Code verdrahten, damit die Modellwahl weniger zählt.
- **Gelernt:** Modellvergleiche nach Handprüfung sagen wenig, wenn die Profile verschieden sind; erst die Einzelmetriken (Zitate, Rechnen, Format) zeigen den Unterschied.
- **Relevant für Ausarbeitung?** ja → Evaluation, Reflexion (Modellwahl auf CPU-Hardware)

### ISS-065 – `.venv` des Laptops zerstört und Platte der VM voll (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-16 / M6f
- **Kategorie:** ki-assistent
- **Status:** gelöst (nach `uv sync` auf dem Laptop; der Wrapper `scripts/eval_run.sh` ruft es zu Beginn auf)
- **Symptom:** (1) In Claudes Shell lief ein `uv run` ohne `UV_PROJECT_ENVIRONMENT`; `uv` entfernte das `.venv` im Projektordner („linked to non-existent Python interpreter“) und legte ein leeres, auf VM-Pfade zeigendes an. Das `.venv` des Laptops (PyCharm-Interpreter) war damit weg. (2) `uv sync` in der VM scheiterte mit „No space left on device“: die Sitzungsplatte (`/sessions`) war zu 99 % voll.
- **Ursache:** (1) Der Hinweis aus ISS-009 stand in `status.md`, aber der Export stand in diesem einen Befehl nicht, weil die Umgebungsvariablen nicht von einem Aufruf zum nächsten gelten. (2) Cache und Umgebung unter `$HOME` liegen auf der kleinen Sitzungsplatte.
- **Lösung / Workaround:** Den Rest des leeren `.venv` gelöscht; `uv sync` auf dem Laptop baut das echte neu. Für Claudes Shell gilt jetzt `UV_CACHE_DIR=/tmp/uv-cache UV_PROJECT_ENVIRONMENT=/tmp/venvs/audit UV_LINK_MODE=copy` in **jedem** Befehl mit `uv`, am besten als erste Zeile. `status.md` ist angepasst.
- **Gelernt:** Eine Regel, die nur in der Doku steht, schützt nicht; jeder `uv`-Befehl der VM beginnt mit dem Export, und `uv` nie ohne ihn aufrufen, auch nicht für `--help`.
- **Relevant für Ausarbeitung?** nein

### ISS-064 – Zwei kleine eigene Fehler vor dem Commit (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-16 / M6e
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** (1) Die Prüfphrase „überein“ stand als `uberein` in `AUDIT_PHRASES`, `fold` macht aber `ue` daraus; die Frage S5 wäre nicht erkannt worden. (2) Der Zuwachs des Systemprompts war im ADR mit „rund 70 Token“ angegeben, gemessen sind 263 Zeichen, also rund 110 Token. Außerdem scheiterte `test_agent_variant_translates_the_run_and_logs_every_step`, weil seine Frage jetzt eine Prüffrage war.
- **Ursache:** (1) Faltungsregel nicht nachgesehen. (2) Schätzung statt Messung. (3) Test setzte eine Prüffrage voraus, ohne dass es für ihn wichtig war.
- **Lösung / Workaround:** (1) beim Durchlesen vor den Tests bemerkt und korrigiert, `test_is_audit_question` deckt S5 ab. (2) ADR korrigiert, nachdem der Unterschied gemessen war. (3) Frage im Test durch eine Einzelfrage ersetzt.
- **Gelernt:** Größen messen statt schätzen, und Faltung und Normalisierung im Code nachlesen, bevor man Vergleichswörter schreibt.
- **Relevant für Ausarbeitung?** nein

### ISS-063 – G4 ruft `calculate` zweimal mit erfundenen Argumenten auf und verbraucht damit das Limit
- **Datum / Meilenstein:** 2026-11-16 / M6e (RUN-013)
- **Kategorie:** agent
- **Status:** offen (teilweise behoben in M6f)
- **Symptom:** G4 ruft nach der Rechennachfrage zweimal `calculate {"a": "1.963,28", "b": "-1.920,00"}` auf (Pflichtargument `expression` fehlt). Beide Aufrufe sind ungültig und zählen zum Limit von 6; die Antwort entschuldigt sich, dass nicht gerechnet werden konnte. Die Wiederholungssperre greift nur bei gültigen Aufrufen, der zweite identische ungültige Aufruf wird noch einmal als Fehler beantwortet.
- **Ursache:** `llama3.1:8b` folgt dem Format von `calculate` nicht (siehe ISS-054); die Fehlermeldung mit dem richtigen Aufruf ändert bei Temperatur 0 nichts. Ob eine Sperre auch für identische ungültige Aufrufe sinnvoll ist, ist nicht geprüft.
- **Lösung / Workaround:** Keine. Kandidaten: identische ungültige Aufrufe ebenfalls sperren; die Argumente von `calculate` verzeihender machen (z. B. zwei Zahlen und Operator akzeptieren); Gegenprobe mit `qwen2.5:7b`. Stand M6f: `calculate` akzeptiert Operanden und deutsche Tausendertrennzeichen; in RUN-015 ist der zweite G4-Aufruf gültig, das Limit von 6 Aufrufen wird trotzdem erreicht und die Rechnung ist sinnlos (ISS-067). Gegenprobe `qwen2.5:7b`: 3 von 3 `calculate`-Aufrufen gültig (ISS-066).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Format-Treue kleiner Modelle bei Werkzeugargumenten)

### ISS-062 – RUN-013 schlechter als RUN-012 bei S2, S4 und N2, Ursache unklar
- **Datum / Meilenstein:** 2026-11-16 / M6e (RUN-013)
- **Kategorie:** evaluation
- **Status:** gelöst (Streuung gemessen; Ursache im Code noch nicht getrennt)
- **Symptom:** Nach Handprüfung 6 richtig statt 9. S2 nennt Nettopreise statt der geforderten Bruttopreise, S4 antwortet mit der Lückenantwort, N2 nennt einen Grundpreis aus einem Ablenker, weil das Modell im zweiten Versuch den Sparten-Filter wegließ. Dieselben Fragen waren in RUN-012 richtig.
- **Ursache:** Nicht geklärt. Mögliche Gründe: der längere Systemprompt (263 Zeichen mehr), die geänderte Aufruffolge durch Nachfrage und Sperre, oder Streuung zwischen Läufen (Temperatur 0 schließt sie nicht aus, weil Ollama bei Prompt-Änderungen und Cache-Zuständen anders rechnen kann). Ein Lauf mit unverändertem Code wurde nicht gemacht.
- **Lösung / Workaround:** RUN-015 und RUN-016 (gleicher Code, `llama3.1:8b`) sind bis auf die Zeiten identisch (gleiche Antworten, Token, Metrik; Zeit je Frage 325 gegen 320 s). Bei Temperatur 0 und gleichem Rechner gibt es hier keine Streuung der Antworten. Die Rückschritte S2/S4/N2 gegenüber RUN-012 bleiben auch in RUN-015 und stammen damit aus dem Code oder Prompt von M6e. Welche der drei Änderungen (Prompt, Sperre, Nachfrage) die Ursache ist, wurde nicht einzeln gemessen. Einschränkung: eine Wiederholung, ein Rechner.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen von Einzelläufen)

### ISS-061 – Antwort besteht aus einem Werkzeugaufruf als Text (S5)
- **Datum / Meilenstein:** 2026-11-16 / M6e (RUN-013)
- **Kategorie:** agent
- **Status:** gelöst (Erkennung); die Antwort von S5 bleibt falsch (ISS-058, ISS-067)
- **Symptom:** Auf die Rechennachfrage hin schreibt `llama3.1:8b` bei S5 „Ich benötige den Wert für die geleisteten Abschlagszahlungen. Ich werde nach diesem Wert suchen.“ und danach `{"name": "search", "parameters": {...}}` als Text statt als Werkzeugaufruf. Der Loop sieht keinen Aufruf, hält den Text für die Antwort und beendet die Frage mit `stop_reason=answer`.
- **Ursache:** Das Modell gibt den Aufruf im Fließtext aus; Ollamas natives Tool-Calling erkennt ihn nicht. Der Loop prüft Antworten nur auf die Lückenformel (ADR-0010).
- **Lösung / Workaround:** Umgesetzt in M6f (`agent/text_calls.py`): Antworttext, der als JSON mit `name` und `parameters` lesbar ist, wird als Werkzeugaufruf ausgeführt (`ToolCallStep.is_text_call`). RUN-015: S5 führt die dritte Suche daraus aus (1 Erkennung in 36 Aufrufen). Ursprünglicher Kandidat: Antworttext, der als JSON mit `name` und `parameters` lesbar ist, als Werkzeugaufruf behandeln oder einmal nachfragen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Tool-Calling kleiner Modelle)

### ISS-060 – Prüffragen-Erkennung nach Stichwörtern und einmalige Rechennachfrage sind grobe Mittel
- **Datum / Meilenstein:** 2026-11-16 / M6e
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** Ob eine Frage eine Prüffrage ist, entscheidet `is_audit_question` am Wortlaut (korrekt, stimmt, passt, angewendet, abgerechnet, …). Eine Frage wie „Stimmt es, dass die Frist 6 Wochen beträgt?“ würde ebenfalls erkannt, eine Prüffrage ohne diese Wörter nicht. Die Nachfrage „rechne mit `calculate` nach“ kommt höchstens einmal je Frage; das Modell kann sie ignorieren oder falsch rechnen (`llama3.1:8b` scheiterte in RUN-010 an den Argumenten von `calculate`, ISS-054).
- **Ursache:** Der Loop kennt den Fragetyp nicht. Der Plan sah bewusst keinen festen Prüfablauf im Code vor (ADR-0015), damit der Agent die Werkzeugwahl behält.
- **Lösung / Workaround:** Keine. Ergebnis RUN-013: Die Nachfrage kam bei G3, G4, S5 und Z1; in keinem Fall folgte ein gültiger `calculate`-Aufruf (ISS-058, ISS-063). Ursprünglich geplante Messung: Wirkung wird in RUN-013 gemessen (Anzahl `calculate`-Aufrufe, erkannte Fehler, Fehlalarme). Die Erkennung nutzt bewusst nicht `include_counterpart`, weil das Modell dieses Flag in 12 von 17 Suchen auch bei Einzelfragen setzt (RUN-012).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Grenzen von Nachfragen als Steuerung eines kleinen Modells)

### ISS-059 – `check_evidence.py` bricht bei Läufen ohne B0 ab (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-16 / M6d (RUN-012)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** `KeyError: 'b0_context'` beim ersten Aufruf auf RUN-012, das nur P2 enthält.
- **Ursache:** Das Skript aus M6c setzte voraus, dass jedes Manifest eine B0-Angabe hat; getestet wurde nur an den Läufen mit allen drei Varianten.
- **Lösung / Workaround:** `manifest.get("b0_context", {})`; das Skript läuft jetzt auch für Läufe mit nur P1 oder P2. Kein eigener Test (Skript, keine Bibliothek).
- **Gelernt:** Auswerteskripte gegen die kleinste Konfiguration testen, nicht nur gegen den Vollbestand.
- **Relevant für Ausarbeitung?** nein

### ISS-058 – P2 ruft `calculate` nie auf und findet daher keinen Abrechnungsfehler
- **Datum / Meilenstein:** 2026-11-16 / M6d (RUN-012)
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** In 24 Werkzeugaufrufen über 14 Fragen kein einziger `calculate`-Aufruf. G3 antwortet „Die Gasabrechnung 2026 ist korrekt“ (E2 übersehen), G4 nennt 1.963,28 EUR statt 1.867,50 EUR (E3 übersehen), G1 endet am Kontextlimit, G2 liefert eine Antwort ohne Zahlen. S5 (richtige Abrechnung) wird fälschlich als Abweichung gemeldet. Fehler erkannt: 0 von 3, Fehlalarm 1 von 3. In G1, G3 und G4 stand keine der Sollzahlen im Kontext; bei G2 standen alle drei im Kontext, die Antwort nennt keine.
- **Ursache:** Mehrere Gründe zugleich: `llama3.1:8b` beendet nach einer Suche (G3, G4), wiederholt bei G1 und G2 dieselbe Suche mit gleichen Argumenten (2 identische Wiederholungen), und die Suchanfrage („Gasabrechnung 2026“) trifft die Preistabellen nicht. Der Prompt verlangt `calculate` für jede Rechnung, das Modell folgt dem nicht (siehe ISS-054).
- **Lösung / Workaround:** In M6e umgesetzt und mit RUN-013 gemessen (ADR-0015): Die Wiederholungssperre funktioniert (4 Sperren), die Rechennachfrage bewirkt bei `llama3.1:8b` nichts (4 Nachfragen, 0 gültige `calculate`-Aufrufe; ISS-060, ISS-063), erkannte Fehler 0 von 3 mit tragfähiger Begründung. Offen bleibt die Wahl zwischen einem festen Prüfablauf im Code (bisher verworfen) und einem anderen Modell (`qwen2.5:7b`, ADR-0013). Status bleibt `offen`. Ergebnis M6f (RUN-014 bis RUN-016): Mit `qwen2.5:7b` folgt auf 3 von 4 Nachfragen ein gültiger `calculate`-Aufruf und G4 wird erkannt (ISS-066); die Operanden stimmen nicht immer (ISS-067).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Grenzen kleiner Modelle bei mehrstufigen Prüfungen), Evaluation

### ISS-057 – P2 braucht in RUN-012 fast doppelt so lange, obwohl die Prompt-Token gleich sind
- **Datum / Meilenstein:** 2026-11-16 / M6d (RUN-012)
- **Kategorie:** hardware
- **Status:** offen (teilweise geklärt)
- **Symptom:** 263 s je Frage im Mittel (Median 229 s) gegenüber 136 s in RUN-010, bei gleicher mittlerer Prompt-Token-Zahl (5.582 gegen 5.624). Der Lauf dauerte rund 61 Minuten statt 32.
- **Ursache:** Teilweise geklärt (`scripts/analyze_timing.py`, Ollama-Journal von RUN-013). Von +1.760 s Gesamtzeit (RUN-012 gegen RUN-010) entfallen +937 s auf die erste Modellanfrage je Frage (Systemprompt und Werkzeugbeschreibungen, rund 1.700 Token): RUN-010 hatte bei 11 von 14 Fragen 3 bis 5 s Prefill (Prompt-Cache), RUN-012 und RUN-013 bei 0 von 14 rund 93 s (18 Token/s). Belegt für RUN-013: Das Journal zeigt 28 Modellladungen für 14 Fragen (je 14 für Chat- und Embedding-Modell), jede Frage beginnt also mit kaltem Cache, weil die Auswertung beide Modelle nach jeder P1/P2-Frage entlädt (`unloads_after_each_question`, Commit `92fed4d`, Schutz vor OOM, ISS-043). Für RUN-012 ist das aus dem gleichen Zeitmuster geschlossen. Nicht erklärt: RUN-010 lief laut `night-m6b.log` ab 13:32 und damit nach dem Fix-Commit (12:14), hatte aber trotzdem meist eine schnelle erste Anfrage; ein Journal mit den Ladevorgängen von RUN-010 liegt nicht vor (das gefilterte Journal enthält nur `truncat|oom`). Weitere +570 s kommen aus späteren Aufrufen (mehr Prompt-Token je Aufruf), +114 s aus dem Dekodieren.
- **Lösung / Workaround:** Kein Eingriff: Das Entladen schützt vor OOM (ISS-043) und bleibt. Laufzeiten nur zwischen Läufen mit gleichem Verhalten vergleichen: RUN-012 gegen RUN-013 ist zulässig (beide kalt), der Vergleich mit RUN-010 nicht. Offen: die Frage, warum RUN-010 meist aus dem Cache startete; zu klären nur, wenn die Laufzeit für die Ausarbeitung gebraucht wird (dann Journal ohne Filter mitschreiben).
- **Gelernt:**
- **Relevant für Ausarbeitung?** eher ja, kurz → Evaluation/Hardware (Prompt-Cache gegen Speichergrenze; Laufzeiten nur bei gleicher Ladepolitik vergleichbar)

### ISS-056 – Zwei Commits vor dem vollständigen Quality Gate (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-15 / M6c
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Claude committete die Rohdaten der Nachtläufe und `scripts/check_evidence.py`, nachdem nur `ruff check` und `ruff format --check` auf dem Skript gelaufen waren; `pytest -m "not slow"` lief erst danach.
- **Ursache:** Das Skript wurde als „nur Auswertung“ eingeordnet und die Regel „Gate vor jedem Commit“ verkürzt.
- **Lösung / Workaround:** Gate direkt danach vollständig ausgeführt: grün (272 Tests). Kein Nachbessern nötig. Das Gate läuft wieder vor jedem Commit, auch bei reinen Daten- und Skript-Commits.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-055 – Fehldeutung in RUN-007/008: „P1 antwortet trotz vorhandener Belege mit keine Angaben“
- **Datum / Meilenstein:** 2026-11-15 / M6c
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Im evaluation-log zu RUN-007 und RUN-008 hatte Claude geschrieben, P1 antworte bei G1 „keine Angaben“, obwohl Preisanpassung 03 und Rechnung 06 unter den Top-5 waren, und daraus eine Schwäche der Synthese abgeleitet.
- **Ursache:** Geprüft wurde nur, ob das richtige Dokument unter den Treffern ist, nicht ob der Treffer den gesuchten Wert enthält. Bei G1 sind zwar beide Dokumente dabei, aber Chunks ohne die Preise 38,20 und 39,50 ct/kWh.
- **Lösung / Workaround:** `scripts/check_evidence.py` prüft je Antwort, ob die Sollfakten im Kontext standen (`evidence.json`). Ergebnis für RUN-010/011: Alle 7 reinen Lückenantworten von P1 auf beantwortbare Fragen sind berechtigt; die Ursache ist das Retrieval. Die alten Einträge bleiben stehen, der neue Eintrag RUN-010/011 verweist auf die Korrektur.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Fehleranalyse: Dokument gefunden heißt nicht Beleg gefunden)

### ISS-054 – Modellverhalten in den Nachtläufen: qwen stimmt immer zu, llama scheitert an `calculate`
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** llm
- **Status:** offen
- **Symptom:** (1) `qwen2.5:7b` fällt in B0, P1 und P2 zusammen 14 Urteile, alle „ja“, auch bei den fehlerhaften Abrechnungen G3 und G4; „0 Fehlalarme“ ist deshalb keine Stärke. (2) `llama3.1:8b` ruft `calculate` 13-mal, davon 11-mal mit ungültigen Argumenten (`input`, `unit` oder `a` bis `e` statt `expression`) und wiederholt denselben Aufruf bis zu fünfmal, obwohl die Fehlermeldung den richtigen Aufruf nennt; drei Fragen enden am Werkzeug-Limit. Die zwei gültigen Aufrufe addieren unpassende Beträge. (3) `qwen2.5:7b` ruft `calculate` nie und rechnet im Kopf, zum Teil falsch (B0/S5, P2/G2). (4) `qwen2.5:7b` ruft 10-mal `list_documents`, 7-mal ohne Filter; die lange Liste verdoppelt die Prompt-Länge (10.515 gegen 5.624 Token) und die Zeit je Frage. (5) Bei P2/S5 erfand `qwen2.5:7b` ein Argument `toolbench_rapidapi_key` mit einer schlüsselähnlichen Zeichenkette.
- **Ursache:** (1) bis (4) Modellverhalten bei Temperatur 0; die Abrechnungen sind in sich stimmig, ein „Nachrechnen“ bestätigt sie. (5) Die Zeichenkette steht in keinem Prompt, keiner Konfiguration und keinem Dokument des Projekts, sie kommt also aus dem Modell (vermutlich Trainingsdaten für Tool-Aufrufe; Herkunft nicht nachgeprüft). Überzählige Argumente werden absichtlich ignoriert (`extra="ignore"`), der Aufruf zählt deshalb als gültig.
- **Lösung / Workaround:** Noch keine. Für M6d: Prüffragen brauchen einen festen Ablauf (Vergleichsdokument holen, dann rechnen), nicht nur ein Urteil. Die Zeichenkette steht in den versionierten Rohdaten (`run-011/answers-p2.jsonl`, `run-011/p2-S5.jsonl`); sie ist kein Zugang des Projekts, könnte aber von Schlüssel-Scannern gemeldet werden. Entscheidung des Nutzers: Rohdaten bleiben unverändert. Agent-Modell: ADR-0013.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Modellvergleich), Reflexion (Grenzen kleiner Modelle)

### ISS-053 – RAGAS-Werte des lokalen Bewerters sind im Einzelfall nicht verlässlich
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** (1) Die reine Lückenantwort „Dazu liegen in den Unterlagen keine Angaben vor.“ bekommt Faithfulness 0,00 in 5 und 1,00 in 9 von 14 Fällen; in mindestens 4 der 5 Null-Fälle fehlten die gesuchten Werte tatsächlich im Kontext. (2) Context Recall bei Z3: P1 hat die Zeile „Kündigungsfrist: 1 Monat …“ im Kontext und bekommt 0,00 (beide Läufe), llama P2 hat sie nicht und bekommt 1,00. (3) 13 von 48 Context-Recall-Werten widersprechen dem Abgleich „alle Sollfakten im Kontext“ (7-mal 1,00 ohne die Fakten, 6-mal 0,00 mit den Fakten). (4) Wörtlich belegte Antworten bekommen zum Teil 0,00 oder 0,50 (qwen P2/Z3, qwen P1/Z3).
- **Ursache:** Ein 7B-Bewerter auf der CPU; RAGAS zerlegt die Referenz in Sätze, und die Referenzsätze mischen Fakten mit Hinweisen („die Fristen von Internet- und Mobilfunkvertrag gehören nicht dazu“), die in keinem Beleg stehen. Für Lückenantworten gibt es keine prüfbare Aussage. Die Einzelurteile gibt RAGAS nicht aus, die Ursache je Fall ist deshalb nur vermutet.
- **Lösung / Workaround:** RAGAS bleibt als zweite Sicht im Report, trägt aber keine Aussage allein. Die Tabelle nennt Faithfulness zusätzlich ohne reine Lückenantworten. Für „Beleg im Kontext?“ zählt der deterministische Abgleich aus `scripts/check_evidence.py`. Ergänzt ISS-047. Nachtrag RUN-020/021: Punkt 2 (P1/Z3) und die Zählung in Punkt 3 erklären sich weitgehend aus der Referenzformulierung und dem Abgleich selbst (ISS-086); Punkt 1 und 4 bestätigen sich (P2/N2, P1/S1, P2/Z1).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen von LLM-Bewertern auf kleiner Hardware)

### ISS-052 – `search_documents` findet keine Tabellenzeilen, ist bei S1 und Z3 aber das erwartete Werkzeug
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** tools
- **Status:** gelöst (RUN-012, ADR-0014)
- **Symptom:** Bei S1 und Z3 (Kündigungsfristen) rufen beide Modelle `search_documents`, wie in `ground_truth.yaml` erwartet. Zurück kommen nur Fließtext-Chunks: Grußformel, Briefkopf, Hinweis auf das Sonderkündigungsrecht. Die Frist steht in einer Tabellenzeile („Kündigungsfrist: 1 Monat …“), die nur `search_tables` liefert. Alle vier P2-Antworten sind falsch, zwei davon erfunden („2 Monate zum Kalendervierteljahr“, „14 Tage“). Die Metrik „Tool-Wahl korrekt“ zählt diese Aufrufe als richtig.
- **Ursache:** Die Werkzeuge trennen nach Chunk-Typ, nicht nach Inhalt. Ob ein Fakt im Fließtext oder in einer Tabelle steht, kann weder das Modell noch der Fragenkatalog vorher wissen; der Katalog hat hier selbst falsch geraten. Die Kapitelüberschrift im Chunk-Text hebt zudem inhaltsleere Zeilen nach oben (ISS-027).
- **Lösung / Workaround:** Noch keine. Für M6d: ein Suchwerkzeug über Text und Tabellen (ISS-006), danach `expected_tools` im Katalog anpassen. Bis dahin ist „Tool-Wahl korrekt“ (7/14 bzw. 5/14) nur eingeschränkt aussagekräftig. **M6d:** Ein Werkzeug `search` über Text und Tabellen; Katalog erwartet `search`. S1 und Z3 sind in RUN-012 richtig (RUN-010: beide falsch, zwei Antworten erfunden).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Werkzeugentwurf), Evaluation (Grenzen der Tool-Wahl-Metrik)

### ISS-051 – Leere gefilterte Suche wird ohne Filter wiederholt und liefert Ablenker
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** tools
- **Status:** gelöst (RUN-012, ADR-0014)
- **Symptom:** Bei N2 („Grundpreis für Fernwärme“) filtern beide Modelle richtig auf `district_heating`. Die Suche findet nichts, meldet „Keine Treffer mit Filter …; Wiederholung ohne Filter“ und liefert Grundpreise aus Strom- und Gasdokumenten (bei `llama3.1:8b` auch eine Internetrechnung). `llama3.1:8b` nennt daraufhin 12,90 EUR/Monat, `qwen2.5:7b` 13,45 EUR/Monat als Fernwärme-Grundpreis. B0 und P1 beantworten N2 richtig.
- **Ursache:** Die Wiederholung ohne Filter war als Schutz gegen zu enge Filter des Modells gedacht (ISS-007). Bei einer Sparte, die es im Bestand nicht gibt, ist „keine Treffer“ aber genau die richtige Auskunft; die Wiederholung macht daraus scheinbar passende Belege.
- **Lösung / Workaround:** Noch keine. Für M6d: bei leerem Ergebnis nicht ungefiltert wiederholen, sondern melden, welche Sparten und Jahre es gibt, oder nur den Filter lockern, der nicht die Sparte betrifft. **M6d:** Keine Wiederholung ohne Filter; leere Suche nennt den Bestand. N2 ist in RUN-012 richtig („keine Angaben“; RUN-010: 12,90 EUR/Monat erfunden).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Werkzeugentwurf), Evaluation (Negativfragen)

### ISS-050 – Die Metrik wertet zustimmende Urteile zu großzügig
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** (1) Vier Antworten von `qwen2.5:7b` zählen als richtig, obwohl die Begründung nicht trägt (B0/S5, P1/S5, P2/S5, P2/G2; Einzelheiten im evaluation-log). Nach Handprüfung hat `qwen2.5:7b` 3 / 5 / 2 statt 4 / 6 / 4 richtige Antworten, `llama3.1:8b` unverändert 5 / 5 / 3. (2) Bei llama P1/G3 liest die Metrik ein „ja“, die Antwort sagt „können wir nicht bestätigen“. (3) Die Zahlensuche akzeptiert auch das Hundertfache und ein Hundertstel (für ct und EUR); „34,80 ct“ trifft dadurch den Sollwert 3.480 kWh. In den gelesenen Antworten wurde kein Fakt deshalb falsch gutgeschrieben, im Kontextabgleich (`evidence.json`, B0/S4) aber schon.
- **Ursache:** Bei Fragen mit erwartetem „ja“ stehen die Sollzahlen in der Abrechnung selbst. Wer sie abschreibt und „Ja“ sagt, erfüllt die Prüfung, ohne den Vertrag gelesen zu haben. Ergänzt ISS-038.
- **Lösung / Workaround:** Die Metrik bleibt unverändert, damit die Läufe vergleichbar sind. Der evaluation-log führt „richtig laut Metrik“ und „richtig nach Handprüfung“ getrennt; jede Umwertung ist dort begründet. Später möglich: den Einheitenfaktor nur bei Fakten mit Einheit ct oder EUR anwenden.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Metriken, Grenzen)

### ISS-049 – Abbruch mitten in einer Anfrage endete mit Traceback, Folgeschritte liefen ins Leere
- **Datum / Meilenstein:** 2026-11-15 / M6b (RUN-010)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Als Ollama während P2/Z3 vom OOM-Killer beendet wurde (ISS-043), endete `generate` mit `httpx.RemoteProtocolError: Server disconnected without sending a response.` und Traceback. Die drei folgenden Befehle der Nachtkette (qwen-Lauf, zweimal RAGAS) scheiterten sofort mit „Failed to connect“, weil Ollama noch neu startete; der Nachtlauf war damit nach ca. 1 h vorbei.
- **Ursache:** Die CLI fing nur `ConnectionError` ab (Verbindung kommt nicht zustande), nicht den Abbruch einer laufenden Anfrage, den der Ollama-Client als `httpx`-Fehler weiterreicht. Der von Claude gebaute Nachtbefehl hatte weder Warten noch Wiederholung.
- **Lösung / Workaround:** CLI und Entladen fangen zusätzlich `httpx.TransportError` (Hinweis „derselbe Befehl setzt fort“, Test); `httpx` als direkte Abhängigkeit. Nachtlauf als `scripts/night_eval.sh`: wartet bis zu 10 min auf Ollama und wiederholt jeden Schritt einmal (setzt dabei fort).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Hardware/Betrieb (kurz)

### ISS-048 – Commit trotz rotem Quality Gate (Exit-Code durch Pipe verdeckt)
- **Datum / Meilenstein:** 2026-11-15 / M6b
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Claude rief `./scripts/check.sh | tail -1 && git commit …` auf. `ruff` meldete eine zu lange Zeile, der Commit lief trotzdem durch.
- **Ursache:** Der Exit-Code einer Pipe ist der des letzten Befehls (`tail`), nicht der von `check.sh`.
- **Lösung / Workaround:** Zeile gekürzt, den noch nicht gepushten Commit nachgebessert (`--amend`); Gate seitdem ohne Pipe vor `&&` (Ausgabe in eine Datei, Exit-Code prüfen).
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-047 – RAGAS im Probelauf: Abbruch bei langer Antwort, Context Recall durchweg 0, nachsichtige Faithfulness
- **Datum / Meilenstein:** 2026-11-15 / M6b (RUN-009)
- **Kategorie:** evaluation
- **Status:** teilweise gelöst (Punkt 1), Punkte 2 und 3 akzeptiert
- **Symptom:** (1) P1/G3 Faithfulness: `IncompleteOutputException` nach 499 s, die Aussagenliste der langen Antwort (ca. 1.100 Zeichen) überschritt `max_tokens` 1024. (2) Context Recall ist für alle vier bewerteten Antworten 0,00. (3) P2/G3 behauptet „Die Gasabrechnung 2026 ist korrekt“ und bekommt Faithfulness 1,00; P2/G4 nennt 859,26 EUR aus einer sinnlosen Rechnung (`1963,28 − 1920,00 + 43,28 + 341,67 + 431,03`) und bekommt ebenfalls 1,00.
- **Ursache:** (1) Antwortbudget zu klein bzw. Wiederholungen des Bewerters. (2) Die Referenzantworten von G3/G4 bestehen aus Vergleichen und berechneten Werten (11.299 kWh, 1.867,50 EUR) und brauchen ein zweites Dokument (Vorjahresabrechnung, Mietvertrag), das keine Variante gefunden hat; plausibel, aber nicht von Hand am Bewerter-Output geprüft, weil RAGAS die Einzelurteile nicht zurückgibt. (3) Faithfulness misst nur, ob Aussagen in den Belegen stehen, nicht ob sie richtig sind; die Zahl 859,26 steht in der Beobachtung des Rechners. Das Urteil „korrekt“ hat der Bewerter offenbar als gedeckt gewertet.
- **Lösung / Workaround:** (1) `judge_max_tokens` = 2048; der Fehlschlag lässt sich mit `ragas --retry-errors` wiederholen. (2)/(3) In der Ausarbeitung RAGAS ausdrücklich als Maß für Belegtreue und Belegabdeckung deuten, nicht für Richtigkeit; Richtigkeit und Fehlererkennung kommen aus den eigenen Metriken. Context Recall bei Prüffragen ist systematisch niedrig, weil berechnete Werte nie wörtlich in Belegen stehen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Metriken, Grenzen)

### ISS-046 – RAGAS bewertet B0 praktisch nicht, und die Längenschätzung ist grob
- **Datum / Meilenstein:** 2026-11-15 / M6b
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** (1) Der B0-Kontext hat geschätzt ca. 6.700 Token (RUN-008); zusammen mit dem RAGAS-Prompt und dem Antwortbudget (2.048 Token) passt er nicht in die 8.192 Token des Bewerters. B0 erhält deshalb nur den Status „zu lang“ (RUN-009: geschätzt 9.100–10.300 Token schon mit 1.024 Token Budget). (2) Wie lang der zweite Faithfulness-Prompt wird, hängt von den Aussagen ab, die der Bewerter erst im ersten Aufruf erzeugt; geschätzt wird mit der Antwort als Ersatz. (3) Die Schätzung 2,4 Zeichen/Token ist für deutsche Zahlentabellen gemessen; der englische RAGAS-Prompttext ist günstiger, die Schätzung also eher zu hoch. Dadurch können auch lange P2-Antworten (viele Tool-Aufrufe) übersprungen werden.
- **Ursache:** Kontextgrenze von 8.192 Token bei nur CPU und 9 GB RAM; RAGAS fügt alle Belege in einen Prompt ein.
- **Lösung / Workaround:** Übersprungene Antworten werden gezählt, nicht als 0 gewertet; der Report nennt „x/y bewertet, z zu lang“. B0 wird über die eigenen Metriken verglichen. Ob gekürzt wurde, zeigt nach jedem Lauf das Journal (`truncat`).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen)

### ISS-045 – Bewertermodell bewertet beim qwen-Lauf seine eigenen Antworten
- **Datum / Meilenstein:** 2026-11-15 / M6b
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** RAGAS-Bewerter ist für beide Läufe `audit-judge` (= `qwen2.5:7b`). Im Lauf mit `qwen2.5:7b` als Antwortmodell beurteilt dasselbe Modell seine eigenen Antworten; LLM-Bewerter neigen dazu, eigene Formulierungen milder zu bewerten. Dazu kommen englische RAGAS-Prompts auf deutschen Texten und ein kleines 7B-Modell als Bewerter.
- **Ursache:** Auf der Hardware ist kein größeres oder drittes gleich starkes Modell sinnvoll (≤ 8B, 9 GB RAM); ein fester Bewerter hält die Werte beider Läufe vergleichbar (ADR-0012).
- **Lösung / Workaround:** RAGAS nur als zweite Sicht neben den deterministischen Metriken; Stichproben von Hand prüfen und Fehlurteile hier notieren; die Abweichung zwischen den Läufen nicht allein dem Antwortmodell zuschreiben. RUN-010/011: kein Bonus für die eigenen Antworten erkennbar (Faithfulness P1 / P2 im qwen-Lauf 0,74 / 0,69, im llama-Lauf 0,71 / 0,68); die Werte sind aber ohnehin wenig verlässlich (ISS-053).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen)

### ISS-044 – RAGAS sendet standardmäßig Nutzungsdaten an den Hersteller
- **Datum / Meilenstein:** 2026-11-15 / M6b
- **Kategorie:** llm
- **Status:** gelöst
- **Symptom:** Beim Lesen des Quelltexts von RAGAS 0.4.4 fiel auf, dass jede Bewertung ein Nutzungsereignis an einen Server des Herstellers schickt (`ragas/_analytics.py`, `track(...)` in `InstructorLLM.agenerate`), solange `RAGAS_DO_NOT_TRACK` nicht auf `true` steht. Das widerspricht dem Grundsatz „nichts verlässt den Rechner“ (ADR-0001), auch wenn laut Quelltext nur Metadaten wie Anbieter und Modellname gesendet werden.
- **Ursache:** Opt-out-Telemetrie der Bibliothek; der Wert wird beim ersten Aufruf gelesen und zwischengespeichert.
- **Lösung / Workaround:** `RagasJudge` setzt `RAGAS_DO_NOT_TRACK=true`, bevor RAGAS importiert wird; ein Unit-Test prüft das.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Datenschutz / lokale Architektur (kurz)

### ISS-042 – Evaluations-CLI fing einen Verbindungsabbruch nicht ab
- **Datum / Meilenstein:** 2026-11-14 / M6a (RUN-007)
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Als Ollama während RUN-007 nicht mehr erreichbar war, endete `generate` mit einem Python-Traceback. `manifest.json` (welche Dateien im B0-Kontext waren) fehlte, weil es erst am Ende geschrieben wurde; auch das Entladen der Modelle im `finally` hätte erneut eine Ausnahme geworfen.
- **Ursache:** Von Claude nur für `ResponseError` geplant, nicht für `ConnectionError`; Manifest als „Abschlussdatei“ gedacht statt als Beschreibung des Laufs.
- **Lösung / Workaround:** `ConnectionError` wird abgefangen (Hinweis: derselbe Befehl setzt fort), das Entladen ignoriert ihn, das Manifest wird vor der ersten Antwort geschrieben. Die gespeicherten Antworten blieben dank JSON-Zeilen erhalten.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-043 – Ollama vom Kernel wegen Speichermangel beendet (RUN-007)
- **Datum / Meilenstein:** 2026-11-14 / M6a (RUN-007)
- **Kategorie:** hardware
- **Status:** gelöst (nach „Entladen nach jeder Antwort“ lief der Nachtlauf am 15.11. 8,5 h ohne OOM-Kill; weiter beobachten)
- **Symptom:** Nach B0 (3 lange Prompts), P1 und dem ersten P2-Lauf meldet das Journal um 23:37 `ollama.service: The kernel OOM killer killed some processes` und `Failed with result 'oom-kill'`; systemd startet Ollama neu, der Evaluationslauf bricht mit `ConnectionError` ab.
- **Ursache:** Nicht sicher belegt. Geladen waren `llama3.1:8b` (6,2 GB laut `ollama ps`, mit 8.192 Token KV-Cache) und `nomic-embed-text` unter `MemoryMax=9G`. Der llama-server meldet `idle slots will be saved to prompt cache` und `context checkpoints enabled, max = 32`; Vermutung: Der Prompt-Cache der langen B0-Prompts wuchs im RAM, bis die Grenze erreicht war.
- **Lösung / Workaround:** Vor jeder Variante entlädt `generate` die Modelle (`keep_alive=0`), damit Modell und Prompt-Cache neu beginnen (kostet ca. 10 s Ladezeit je Variante). Tritt der Fehler wieder auf: Speicher während des Laufs mit `systemctl status ollama` beobachten.
- **Nachtrag 2026-11-15 (RUN-010):** Erneut `oom-kill` um 12:28, bei der 14. P2-Frage (Z3) des `llama3.1:8b`-Laufs; B0 und P1 mit je 14 Fragen liefen durch. Auch in RUN-007 starb Ollama in P2. Das Muster passt zur Vermutung, dass der Speicher über viele verschiedene Prompts ohne Entladen wächst; belegt ist es nicht. Erweiterte Gegenmaßnahme: P1 und P2 entladen nach jeder Frage, RAGAS entlädt den Bewerter nach jeder bewerteten Antwort; B0 bleibt geladen, weil alle Fragen denselben Präfix teilen und sonst jede Frage ca. 430 s Prefill kostet. `scripts/night_eval.sh` wartet vor jedem Schritt auf Ollama und wiederholt einen abgebrochenen Schritt einmal.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Hardware/Betrieb

### ISS-041 – Ollama kürzt zu lange Prompts still auf die Hälfte (Token-Schätzung zu niedrig)
- **Datum / Meilenstein:** 2026-11-14 / M6a (RUN-007)
- **Kategorie:** llm
- **Status:** gelöst (Schätzung korrigiert), Prüfung früherer Agentenläufe offen
- **Symptom:** Alle drei B0-Aufrufe in RUN-007 melden `prompt_eval_count` = 4.098. Das Journal zeigt `truncating input prompt limit=4098 prompt=8424 keep=4 new=4098`: Der Prompt hatte real 8.424 Token, mehr als `num_ctx` 8192, und Ollama behielt nur die letzten ca. 4.096 Token. Die Antworten kannten deshalb nur die hinteren Dateien (06, 07).
- **Ursache:** Meine Token-Schätzung „Zeichen/3“ (aus M5) war zu optimistisch. Gemessen: B0-Text mit vielen Tabellenzahlen 2,5 Zeichen/Token, Messtext 2,8 Zeichen/Token. `num_ctx` selbst wirkt: `scripts/probe_context.py` schickte 7.537 Token ungekürzt (`ollama ps`: `context_length` 8192), Zeile 0 wurde richtig beantwortet.
- **Lösung / Workaround:** `CHARS_PER_TOKEN` = 2,4 (gilt auch für den Kontextwächter des Agenten, der jetzt früher stoppt). B0 passt damit noch 6 Dateien (01–06, ca. 16.100 Zeichen). Ob in RUN-005/006 Agentenläufe gekürzt wurden, ist nicht geprüft (Journal nur ab 22:00 gesichert); die gemeldeten Prompt-Größen dort lagen unter 2.600 Token.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Hardware/Betrieb, Evaluation (Grenzen)

### ISS-040 – Fehlererkennung misst nur einen der drei eingebauten Fehler
- **Datum / Meilenstein:** 2026-11-14 / M6a
- **Kategorie:** evaluation
- **Status:** gelöst (M6b: Fragen G3 zu E2 und G4 zu E3; `Question.planted_error`, Validierung „jeder eingebaute Fehler hat genau eine Frage“)
- **Symptom:** Die Metriken „Fehler erkannt“ und „Fehlalarm“ zählen Fragen, deren erwartete Antwort mit „Ja“ oder „Nein“ beginnt (S5, G1, G2, Z1). Nur G1 enthält einen eingebauten Fehler (E1). E2 (z-Zahl Gas 2026) und E3 (Wohnfläche Nebenkosten 2026) kommen in keiner Frage vor; `audit_checks` mit 10 Abrechnungen wird nicht genutzt.
- **Ursache:** Der 12-Fragen-Katalog ist aus M1 übernommen; die Prüffragen zu den Abrechnungen 29 und 30 wurden nie formuliert.
- **Lösung / Workaround:** In M6b entweder zwei Reservefragen zu E2/E3 ergänzen oder einen eigenen Prüflauf „Prüfe die Abrechnung X“ über `audit_checks` bauen. Bis dahin die Rate als „1 von 1“ und nicht als Prozentwert berichten.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen)

### ISS-039 – B0 sieht nur 8 von 30 Dokumenten
- **Datum / Meilenstein:** 2026-11-14 / M6a
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** Bei `num_ctx` 8192 passen nach Prompt, Antwort und Reserve ca. 7.000 geschätzte Token Seitentext in B0. Seit der korrigierten Schätzung (ISS-041) sind das die Dateien 01–06 (nur Strom). Fragen zu Gas (S1, Z1), Wasser (S3) und Nebenkosten (G2) kann B0 daher nicht beantworten; die Stromfragen sind durch die Reihenfolge begünstigt.
- **Ursache:** Der Korpus hat ca. 60.000 Zeichen Seitentext; Entscheidung für Variante A (Katalogreihenfolge, gleicher Kontext für alle Fragen), ADR-0011.
- **Lösung / Workaround:** Bewusst so gelassen: Genau das ist die Aussage von B0 („Volltext passt auf dieser Hardware nicht“). Im Bericht steht, welche Dateien im Kontext waren (`manifest.json`). Die Schätzung Zeichen/3 ist vorsichtig; real ist der Prompt kürzer.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Varianten, Grenzen)
- **Nachtrag 2026-11-21 (M8, run-025):** Inzwischen 6 von 35 Dokumenten. B0 antwortet bei den meisten Nicht-Strom-Fragen „keine Angaben“; seine Werte „Negativfragen 2 von 2“ und „Fehlalarme 0“ entstehen dadurch und sind kein Verdienst. Mit `qwen2.5:7b` ist die Schätzung zudem zu niedrig (ISS-120).

### ISS-038 – Fakten- und Urteilsprüfung der eigenen Metriken sind Heuristiken
- **Datum / Meilenstein:** 2026-11-14 / M6a
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** (1) Eine erwartete Zahl gilt als gefunden, wenn sie irgendwo in der Antwort steht, auch in einem falschen Zusammenhang. (2) Textfakten werden als ganzes Wort gesucht; „31. Dezember 2025“ trifft „31.12.2025“ nicht. (3) Das Urteil ja/nein wird aus dem ersten Satz gelesen (führendes Ja/Nein, sonst Signalwörter wie „nicht“, „abweich“, „stimmt“); Sätze wie „weicht nicht ab“ werden falsch eingeordnet. (4) Vorher zählte ein Textfakt „ja“ als gefunden, sobald „Jahresabrechnung“ in der Antwort stand, und eine Belegnummer `[25]` als Zahl 25; beides ist behoben.
- **Ursache:** Deterministische Prüfung ohne LLM-Bewerter (ADR-0011).
- **Lösung / Workaround:** `report.md` zeigt jede Antwort mit erkanntem Urteil und fehlenden Fakten, Fehlurteile werden beim Auswerten von Hand korrigiert und hier notiert. RAGAS (M6b) als zweite Sicht. Nach RUN-007: „keine Informationen“ zählt als ehrliche Lücke; das Urteil wird auch aus dem letzten Satz gelesen. Ein richtiges Ja/Nein kann eine falsche Begründung haben (B0/G1); deshalb zählt eine Antwort nur mit allen Fakten als richtig.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Metriken, Grenzen)

### ISS-037 – P1 hat noch keine Antwortsynthese, B0 fehlt
- **Datum / Meilenstein:** 2026-11-14 / M5 (aufgefallen beim Planen von M6)
- **Kategorie:** konzept
- **Status:** gelöst (M6a, ADR-0011)
- **Symptom:** `concept.md` 7.1 und 11.1 vergleichen drei Varianten (B0 Volltext, P1 Pipeline mit LLM-Synthese, P2 Agent). Gebaut sind bisher nur das Retrieval von P1 (M4) und der Agent P2 (M5). Es gibt weder eine Synthese-Funktion, die aus den Top-5 eine Antwort erzeugt, noch den Volltext-Prompt von B0.
- **Ursache:** Meilensteintabelle und Konzept führten „P1“ unter M4 als Retrieval, die Synthese wurde in keinem Paket eingeplant.
- **Lösung / Workaround:** M6 beginnt mit P1-Synthese (ein Modellaufruf mit Evidenz, Belegnummern wie im Agenten) und B0 (so viel Text wie in 8.192 Token passt), beide über denselben `ChatClient` und dieselben Protokollsätze; erst danach die Evaluation. Das ist mehr Arbeit als im Konzept sichtbar; M6 kann in zwei Pakete geteilt werden.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Varianten)

### ISS-036 – `llama3.1:8b` gibt früh auf und wählt Tools und Argumente unzuverlässig
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** RUN-005: G1 endet nach einer gefilterten Suche mit „keine Angaben“ (Filter `bill`/2025 schloss die Preisanpassung aus); S4 ruft nie `search_images`, wiederholt dreimal denselben ungültigen `calculate`-Aufruf (`a`, `b` statt `expression`) und beschriftet Eurobeträge als Verbrauch; in S2 und N1 erfindet es Argumentnamen (`doc_id`, `query` bei `list_documents`).
- **Ursache:** Ein 8B-Modell mit sechs Tools folgt Beschreibungen nur teilweise (ISS-006, ISS-007 bestätigt). Die Fehlermeldung nannte nur den fehlenden Parameter, nicht den richtigen Aufruf.
- **Lösung / Workaround:** Fehlermeldung nennt `calculate(expression*)`; eine Lückenantwort nach weniger als 2 Werkzeugaufrufen wird einmal hinterfragt; der System-Prompt nennt Vorjahreswerte und Diagramme.
- **Update RUN-006:** Hat nicht gereicht. G1: Die Rückfrage wiederholte denselben Aufruf mit denselben Filtern und tauschte „keine Angaben“ gegen eine unpassende Zahl; S4: weiter kein `search_images`, ungültiges `calculate`, erfundenes Argument `doc_id`; die Schlussantwort ist aber ehrlich. 2 von 4 richtig (S2, N1). Weitere Prompt-Änderungen an diesen vier Fragen unterbleiben (Anpassen an den Test); M6 prüft Gegenmaßnahmen gezielt: `qwen2.5:7b`, ein gemeinsames Suchtool (ISS-006), Filter durch Code statt durch das Modell (ISS-007), Beispiele im Prompt.
- **Status-Hinweis:** bleibt offen bis M6.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation / Grenzen kleiner Modelle

### ISS-035 – Das Modell zitiert eine KI-Zusammenfassung als Beleg
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** agent
- **Status:** gelöst
- **Symptom:** S2: Treffer [1] war die `table_summary` mit Nettowerten (29,24 ct, 9,66 EUR), die Tabellenzeilen mit Brutto folgten als [2] bis [5]. Das Modell antwortete mit [1], obwohl der Treffer „KI-Zusammenfassung, kein Beleg“ trug.
- **Ursache:** Die Summary ist der Frage sprachlich am ähnlichsten und steht daher oben; kleine Modelle folgen dem Ranking, nicht der Kennzeichnung. Die Zahlen der Summary sind zudem mit einem 3B-Modell erzeugt (ISS-022).
- **Lösung / Workaround:** Der Agent sieht Summaries nicht mehr (`AgentSettings.include_table_summaries=False`); sie bleiben im Index für P1. Im System-Prompt: Preise brutto. Preis: Die Hilfe der Summaries beim Finden (RUN-004: 9/10 statt 8/10) entfällt für den Agenten; M6 kann beides vergleichen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval / Agent (KI-Texte nur als Suchhilfe, nie als Beleg)

### ISS-034 – Eigene Fehler beim Bau von M5 (von den Tests gefunden)
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** (1) `list_documents` mit Jahr 2023 listete den Stromvertrag, obwohl er erst ab 2024 gilt. (2) Der Rechner fing nur `DivisionByZero` und `InvalidOperation`, aber nicht `Overflow`.
- **Ursache:** (1) Meine erste Jahreslogik nahm bei Dokumenten ohne Zeitraum auch das Schreibdatum (Dezember 2023) als Treffer; die Ausgabe zeigte aber nur „gültig ab 2024“, der Treffer war nicht erklärbar. (2) Zu enge Ausnahmeliste.
- **Lösung / Workaround:** (1) Reihenfolge Abrechnungszeitraum, dann `valid_from`, dann Schreibdatum; sie entspricht der ausgegebenen Zeile. (2) `ArithmeticError` fangen. Beides hat ein Test aufgedeckt (`test_list_documents_says_so_when_nothing_exists`, Rechner-Angriffsliste).
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-033 – `list_documents` kennt die Laufzeit eines Vertrags nicht
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** tools
- **Status:** akzeptiert
- **Symptom:** Ein Vertrag mit `valid_from` 2024 erscheint bei `year=2025` nicht, obwohl er 2025 noch läuft.
- **Ursache:** Die Metadaten haben kein Vertragsende; nur Abrechnungszeitraum und `valid_from` sind gepflegt.
- **Lösung / Workaround:** Der Jahresfilter von `list_documents` meint „Dokument gehört zu diesem Jahr“, nicht „Vertrag gilt in diesem Jahr“. Für Verträge fragt der Agent ohne Jahr; die Tool-Beschreibung sagt, dass die Liste mit Filtern aufzurufen ist. Ein Feld `valid_until` wäre ein Eingriff in `documents.yaml` und wird nur gemacht, wenn M6 den Fall zeigt.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-032 – Filterregeln im Code sind Heuristiken
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** (a) Ein Jahresfilter ohne `bill`/`notice`/`payment_plan` wird verworfen, auch wenn das Modell ihn für ein Dokument mit `valid_from` meint (Preisanpassung 2025). (b) Die automatische Wiederholung ohne Filter kann Treffer liefern, die zur Frage nicht mehr passen; das Modell muss den Hinweistext lesen.
- **Ursache:** Der Index hat keinen Filter auf `valid_from` (ISS-025, YAGNI); kleine Modelle lesen Hinweise in Beobachtungen nicht zuverlässig.
- **Lösung / Workaround:** Die Hinweise stehen als erste Zeilen der Beobachtung. In RUN-005 und M6 messen: Wie oft wird ein Filter verworfen oder wiederholt, und führt das zu falschen Antworten?
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent / Tools (Regeln im Code statt im Prompt)

### ISS-031 – Kürzung der Treffertexte kann die gesuchte Stelle abschneiden
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** agent
- **Status:** offen
- **Symptom:** Das Modell sieht von jedem Treffer höchstens 600 Zeichen; Text-Chunks sind bis 1.500 Zeichen lang. Eine Kündigungsfrist am Ende eines langen Absatzes könnte fehlen.
- **Ursache:** Abwägung gegen die Prefill-Zeit (ca. 18 Token/s): 5 volle Treffer wären rund 110 s je Suche.
- **Lösung / Workaround:** Die Evidenz in der Oberfläche zeigt den vollen Text. In RUN-005 prüfen, ob eine erwartete Zahl in der gekürzten Beobachtung fehlt; sonst `max_hit_chars` erhöhen oder Treffer am Satzende kürzen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent / Grenzen

### ISS-030 – Der Prompt ist groß, bevor die erste Frage kommt
- **Datum / Meilenstein:** 2026-11-14 / M5
- **Kategorie:** hardware
- **Status:** offen
- **Symptom:** Die sechs Tool-Schemas sind ca. 6.000 Zeichen lang (die Aufzählungen von Sparte und Dokumenttyp stehen in vier Tools), dazu kommt der System-Prompt (ca. 1.300 Zeichen). Geschätzt 1.500 bis 2.500 Token, bei 18 Token/s ein Prefill von 80 bis 140 s vor dem ersten Schritt. `list_documents` ohne Filter liefert 30 Zeilen (ca. 3.300 Zeichen).
- **Ursache:** Kleine Modelle brauchen ausführliche Beschreibungen, die Schemas wiederholen die Filterbeschreibungen.
- **Lösung / Workaround:** Erst messen (RUN-005 protokolliert `prompt_tokens` und `prefill_seconds` je Aufruf), dann kürzen. Wenn die Präfix-Wiederverwendung greift (ISS-005), zahlt sich der Anfang nur einmal aus; ein letzter Aufruf ohne Tools bricht sie und kostet einen vollen Prefill.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Hardware-Grenzen / Agent

### ISS-029 – Frage S4 (Verbrauch 2022/2023 aus dem Diagramm) wird nicht gefunden
- **Datum / Meilenstein:** 2026-11-14 / M4
- **Kategorie:** retrieval
- **Status:** offen
- **Symptom:** Die Frage nach dem Stromverbrauch 2022 und 2023 liefert in keiner der sechs Konfigurationen die erwartete Quelle (Bild-Chunk der Abrechnung 2024, Seite 2) in den Top-5. Vorn stehen Chunks zu Verbrauch 2025 (Zwischenablesung, Abrechnung 2025).
- **Ursache:** Nicht belegt. Vermutung: Die Caption steht gegen viele Text- und Tabellen-Chunks mit dem Wort „Stromverbrauch“. Es wurden nur die Top-5 gespeichert, der tatsächliche Rang ist unbekannt.
- **Lösung / Workaround:** Die Ground Truth erwartet das Tool `search_images`. Mit `chunk_types={image}` gibt es nur 5 Bild-Chunks im Index, die Suche ist dort eindeutig. In M5 als eigenes Tool umsetzen und in M6 prüfen, ob der Agent es wählt (ISS-006).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval-Konzept (typgetrennte Suche statt eines Topfes)

### ISS-028 – Vergleichslauf nutzt handgesetzte Filter und nur 12 Fragen
- **Datum / Meilenstein:** 2026-11-14 / M4
- **Kategorie:** evaluation
- **Status:** akzeptiert
- **Symptom:** Der Vergleich in `retrieval/compare.py` setzt für jede Frage den Metadatenfilter von Hand (`QUESTION_FILTERS`). Die Konfigurationen mit Filter zeigen damit, was ein Agent mit richtigen Filtern erreicht, nicht was er tatsächlich wählt. Dazu sind es nur 10 beantwortbare Fragen, die nach dem Bau der Pipeline bekannt waren.
- **Ursache:** Die Filterwahl gehört zum Agenten (M5); in M4 gibt es ihn noch nicht. Ein größeres Fragenset würde den Aufwand der Ground Truth sprengen.
- **Lösung / Workaround:** Die Zahlen als obere Schranke lesen und in der Ausarbeitung so benennen. In M5/M6 messen, wie oft der Agent falsche Filter setzt (ISS-007).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen der Messung)

### ISS-027 – Hierarchie-Boost greift fast überall und ändert kaum etwas
- **Datum / Meilenstein:** 2026-11-14 / M4
- **Kategorie:** retrieval
- **Status:** offen
- **Symptom:** Der Boost greift, wenn ein Anfrageterm im Pfad steht oder ein Pfadwort der Anfang des Terms ist. Kurze Pfadwörter wie „gas“ treffen jedes Kompositum, das so beginnt („Gasvertrag“, aber auch „Gaststätte“). Der Boost gilt außerdem für alle Chunks eines Dokuments gleich, auch für die unwichtigen (Briefkopf, Summaries). RUN-004 mit echten Embeddings: Der Boost greift bei 55 von 60 Treffern (ohne Filter) und bei allen 55 (mit Filter), weil Begriffe wie „Kündigungsfrist“ oder „Arbeitspreis“ in den Überschriften fast aller Dokumente stehen („arbeits“ trifft sogar die Gas-Preisanpassung bei einer Stromfrage). Die Rangfolge ändert sich dadurch nicht.
- **Ursache:** Konzept sieht „Suchbegriffe im Pfad“ vor, ohne Wortbildung zu regeln; deutsche Komposita brauchen mehr als einen Teilstring-Vergleich.
- **Lösung / Workaround:** Regel in ADR-0009 dokumentiert und mit Tests belegt; Wirkung in RUN-004 gemessen (kein Nutzen). Mögliche Verbesserungen, falls der Boost in M5/M6 gebraucht wird: nur Begriffe boosten, die in wenigen Dokumenten vorkommen (IDF-artig), Sparte und Jahr aus dem Pfad höher gewichten als Fachbegriffe, oder den Boost streichen. Bis dahin bleibt er als Vorlesungsbaustein im Code.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval-Konzept (Grenzen des Boosts)

### ISS-026 – Eigener Fehler: Unterstriche wurden nicht als Worttrenner behandelt
- **Datum / Meilenstein:** 2026-11-14 / M4
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Die Pfadregel fand „Strom“ im Dateinamen `04_Strom_Jahresabrechnung_2024` nicht, weil der reguläre Ausdruck `\w+` den Unterstrich als Wortzeichen zählt und den ganzen Dateinamen als ein Wort las. Der Test `test_compound_matches_path_word_as_prefix` schlug fehl.
- **Ursache:** Von mir (Claude) falsch gewählter Ausdruck; der Fehler wäre bei den echten Dateinamen unbemerkt geblieben, weil der Boost dann nur seltener greift und keine Fehlermeldung kommt.
- **Lösung / Workaround:** Ausdruck `[^\W_]+` (Buchstaben und Ziffern), Test bleibt als Absicherung.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-025 – Zeitraumfilter schließt Dokumente ohne Abrechnungszeitraum aus
- **Datum / Meilenstein:** 2026-11-14 / M4
- **Kategorie:** retrieval
- **Status:** akzeptiert
- **Symptom:** Ein Filter auf das Jahr 2025 liefert nur Rechnungen und Bescheide. Verträge, Preisanpassungen und Hinweise haben keinen `billing_period` und verschwinden aus dem Ergebnis, obwohl sie für 2025 gelten können (z. B. die Preisanpassung 2025 für die Frage G1).
- **Ursache:** Der Zeitraum ist nur bei Abrechnungen gepflegt; `valid_from` gibt es nur bei Preisanpassungen und wird nicht gefiltert.
- **Lösung / Workaround:** Der Agent soll den Zeitraumfilter nur für Abrechnungen setzen und sonst über Sparte und Dokumenttyp filtern (Tool-Beschreibung in M5). Ein Filter auf `valid_from` ist nicht umgesetzt (YAGNI).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval-Konzept (Metadatenfilter und seine Grenzen)


### ISS-024 – Summaries am Token-Limit abgeschnitten, Prompt-Vorgaben missachtet
- **Datum / Meilenstein:** 2026-11-14 / M3
- **Kategorie:** enrichment
- **Status:** gelöst (RUN-003: 0 abgeschnittene Antworten)
- **Symptom:** In RUN-002 endeten 21 von 65 Summaries mitten im Satz („… im Jahr 202“). Statt zwei bis drei Sätzen kamen oft Aufzählungen, einmal mit Wortlaut aus dem Prompt als Einleitung.
- **Ursache:** `num_predict=160` war zu knapp für die Aufzählungen, und die Abschneidung blieb unbemerkt, weil ich `done_reason` nicht ausgewertet habe (eigener Fehler: Ich hatte nur die Zahlenprüfung eingebaut und keinen Test für das Antwortende).
- **Lösung / Workaround:** Limit auf 256, Prompt auf „höchstens drei Sätze, Fließtext, keine Differenzen“, `CachedAnswer.is_truncated` aus `done_reason == "length"`, Report und Log melden abgeschnittene Antworten.
- **Gelernt:** Bei Modellaufrufen immer prüfen, ob die Antwort vollständig ist, nicht nur, ob sie Text enthält.
- **Relevant für Ausarbeitung?** ja → Enrichment, Fehleranalyse

### ISS-023 – Caption erfindet Werte bei Diagramm ohne Beschriftung
- **Datum / Meilenstein:** 2026-11-14 / M3
- **Kategorie:** enrichment
- **Status:** akzeptiert (Zahlen nicht mehr erfunden, Verlaufsbeschreibung bleibt unzuverlässig, RUN-003)
- **Symptom:** Das Diagramm „Monatlicher Heizgasbedarf & Witterungsverlauf“ (Dok. 10, zweites Bild) hat keine Zahlen an den Säulen. `gemma3:4b` nannte trotzdem Werte pro Monat, die im Sommer um das Zehnfache zu hoch sind, und beschrieb das Doppelachsen-Diagramm als zwei Diagramme.
- **Ursache:** Das Modell schätzt Säulenhöhen aus Pixeln und füllt Lücken mit plausibel klingenden Werten, wenn der Prompt „jeden Zahlenwert“ verlangt. Dazu kam das Token-Limit (400) mitten in der Aufzählung.
- **Lösung / Workaround:** Prompt: nur beschriftete Werte nennen, sonst den Verlauf in Worten, keine geschätzten Zahlen; Limit 600. Ergebnis RUN-003: keine erfundenen Zahlen mehr, aber der Verlauf in Worten ist falsch (Sommer als Höchstwert). Grundsätzlich bleibt: Captions sind Vision-Modell-Ausgabe und werden vom Agenten gegen die Tabellenzeilen geprüft (concept.md, Abschnitt 7), nie allein als Beleg genutzt.
- **Gelernt:** Eine Anweisung wie „nenne jeden Wert“ erzeugt bei fehlenden Werten Halluzinationen; der Prompt muss den Ausweg („nicht beschriftet“) ausdrücklich erlauben.
- **Relevant für Ausarbeitung?** ja → Enrichment, Grenzen lokaler Vision-Modelle

### ISS-022 – Zahlenprüfung der Summaries ist nur ein Teilcheck
- **Datum / Meilenstein:** 2026-11-14 / M3
- **Kategorie:** enrichment
- **Status:** akzeptiert
- **Symptom:** Ein 3B-Modell (`llama3.2`) kann in Tabellen-Summaries Zahlen verfälschen oder falsch zuordnen. Die automatische Prüfung findet davon nur einen Teil.
- **Ursache:** `unsupported_numbers` prüft nur, ob jede Zahl der Summary irgendwo im Tabellentext vorkommt. Ausgenommen sind Datumsangaben und ganze Zahlen bis 12 (Anzahlen, Monate). Eine echte Zahl am falschen Platz („Arbeitspreis 14.200 kWh“) fällt nicht auf; gerundete Zahlen erzeugen Fehlalarme.
- **Konkretes Beispiel (RUN-003):** Dok. 14 schreibt „Trinkwasserpreis von 2,30 auf 2,26 EUR/m³ gesenkt“; beide Zahlen stehen in der Tabelle (alt brutto, neu netto), die Aussage ist falsch (neu brutto: 2,42 EUR). Die Prüfung meldet das nicht.
- **Lösung / Workaround:** Treffer landen im Report und werden von Hand angesehen. Die Einzelzeilen bleiben im Index, die Summary ersetzt sie nie. Der Agent rechnet in M5 nur mit Zeilen und Captions, nicht mit Summaries.
- **Gelernt:** Eine Prüfung, die nur Vorkommen vergleicht, ist ein Frühwarnsystem und kein Beweis.
- **Relevant für Ausarbeitung?** ja → Enrichment, Grenzen

### ISS-021 – Ingestion überschreibt das Enrichment
- **Datum / Meilenstein:** 2026-11-14 / M3
- **Kategorie:** enrichment
- **Status:** akzeptiert
- **Symptom:** `python -m audit_agent.ingestion` schreibt alle `*_chunks.json` neu. Captions und Summaries sind danach weg.
- **Ursache:** Die Ingestion kennt das Enrichment nicht (Trennung der Schichten, ADR-0008). Die JSON-Dateien sind für beide Schritte dieselbe Datei.
- **Lösung / Workaround:** Reihenfolge Ingestion → Enrichment einhalten. Ist der Cache gefüllt, dauert der zweite Schritt Sekunden (Test `test_rerun_after_ingestion_restores_enrichment_from_cache`). Ändert sich allerdings ein Chunk-Text einer Tabelle, wird nur diese Summary neu berechnet.
- **Gelernt:** Zwei Schritte auf derselben Datei brauchen eine feste Reihenfolge; der Cache macht sie billig.
- **Relevant für Ausarbeitung?** nein

### ISS-020 – Datenmodell zunächst `Chunk` statt `DocumentChunk` (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Das Chunk-Modell hieß im ersten Entwurf `Chunk`, im Glossar und in `CODING_STANDARDS.md` steht `DocumentChunk`.
- **Ursache:** Glossar vor dem Anlegen der Klasse nicht abgeglichen.
- **Lösung / Workaround:** Umbenennung in `DocumentChunk` (eigener Commit), vor dem Merge.
- **Gelernt:** Begriffe vor dem Schreiben im Glossar nachschlagen, nicht danach.
- **Relevant für Ausarbeitung?** nein

### ISS-019 – Grenzen des Parsers (bewusst nicht behandelt)
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** akzeptiert
- **Symptom:** Nicht abgedeckt sind: Tabellen über mehrere Seiten (jede Seite ergibt eine eigene Tabelle), gescannte PDFs ohne Textebene (kein OCR), zweizeilige Spaltenköpfe mit unterschiedlicher Spaltenbreite und Layouts ohne fette Überschriften. Diagramme liefern nur Bild und Seitenzahl; ihre Werte stehen erst nach dem Enrichment (M3) im Text.
- **Ursache:** Regeln sind auf die 30 synthetischen PDFs abgestimmt (ADR-0007); YAGNI.
- **Lösung / Workaround:** Als Grenze in der Ausarbeitung nennen. Kein Korpus-PDF ist betroffen (alle Tabellen passen auf eine Seite).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Reflexion (Grenzen der Vorverarbeitung), Übertragbarkeit auf echte Post

### ISS-018 – Parser braucht ca. 30 Sekunden für 30 PDFs
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** akzeptiert
- **Symptom:** `python -m audit_agent.ingestion` dauert ca. 31 s, der Test über den ganzen Korpus ebenfalls.
- **Ursache:** `find_tables()` läuft pro Seite zweimal (beide Strategien, ADR-0007) und ist der teure Schritt.
- **Lösung / Workaround:** Der Gesamttest ist mit `slow` markiert; die schnellen Tests parsen nur sechs ausgewählte PDFs. Ingestion läuft einmalig, das Ergebnis liegt als JSON vor.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-017 – Kurzer Rest „Datum: 18.01.2025“ ging verloren (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** chunking
- **Status:** gelöst
- **Symptom:** Der Unit-Test für das Zusammenfügen kurzer Fragmente schlug fehl. Ursache im Code: Reste unter `min_chars` (20 Zeichen) wurden verworfen, obwohl „Datum: 18.01.2025“ (das Rechnungsdatum) eine echte Angabe ist. Im Korpus betraf es vier Reste („Datum: …“ in Dok. 04 und 06, zweimal „Mosbach“).
- **Ursache:** `min_chars` aus dem Konzept wörtlich als „verwerfen“ umgesetzt.
- **Lösung / Workaround:** Reste unter der Schwelle bleiben, wenn sie eine Ziffer enthalten; reine Wortreste („Mosbach“) entfallen (ADR-0007, Punkt 8).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel Vorverarbeitung (Abweichung von der Vorlage der Aufgabenstellung, begründet)

### ISS-016 – Überschriften-Heuristik: Briefkopf-Namen und gemischte Blöcke
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** akzeptiert
- **Symptom:** Fett gesetzte Firmennamen im Briefkopf („AlpenSchutz …“, „MobilPlus AG“, „Sanitär & Heizungstechnik …“) werden zu Überschriften und stehen damit am Anfang des `heading_stack` der ganzen Seite. Umgekehrt wird ein fetter Absatzanfang innerhalb eines gemischten Blocks nicht als Überschrift erkannt.
- **Ursache:** Die Heuristik prüft Fettdruck, Größe und Position, aber nicht die Rolle im Dokument.
- **Lösung / Workaround:** Hingenommen; der Prefix hat dadurch bei diesen Dokumenten einen zusätzlichen Eintrag. Wirkung auf das Retrieval in M4 prüfen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Reflexion (Heuristik vs. Dokumentverständnis)

### ISS-015 – Layout-Tabellen im Briefkopf werden als Datentabelle erkannt
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** akzeptiert
- **Symptom:** In den NeckarEnergie-Dokumenten (08, 10, 29) ist der Briefkopf aus Absender, Anschrift und Kundendaten ein rahmenloses Raster, das `find_tables()` als Tabelle liefert. Ergebnis: Zeilen wie „Herrn | Datum: 28.01.2026“ mischen Anschrift und Metadaten.
- **Ursache:** Layouttabelle und Datentabelle sehen für `find_tables()` gleich aus.
- **Folge in M3:** Das Enrichment fasst auch diese Tabellen zusammen und das 3B-Modell erfindet dabei Verbrauchsangaben und Rechnungsnummern (RUN-003, Dok. 08, 10, 29 `tab01`). Die Zahlenprüfung meldet diese Fälle.
- **Lösung / Workaround:** Inhalt ist vollständig und durchsuchbar, nur ungünstig geschnitten. Nicht behoben; Bewertung nach M4.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Reflexion

### ISS-014 – Aneinanderstoßende Tabellen wurden zu einer verschmolzen (und mein erster Fix griff nicht)
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** gelöst
- **Symptom:** In Dok. 08, 10, 13, 15, 29 lagen Zählerstandstabelle und Entgelttabelle direkt untereinander. `find_tables()` lieferte eine Tabelle; die Zwischenüberschrift „2. Entgeltberechnung“ wurde Tabellenzeile, die Kostenzeilen bekamen die Spalten der Zählertabelle („Zählernummer: Arbeitspreis Erdgas“).
- **Ursache:** Zwischen den Tabellen liegt kein Text- oder Leerraum, den die Erkennung als Trennung sieht.
- **Lösung / Workaround:** Zeilen mit nur einer fetten, größeren Zelle trennen die Tabelle (ADR-0007, Punkt 4). Beim ersten Versuch fehlte trotzdem der Spaltenkopf der zweiten Tabelle, weil ich den Kopf aus `row_bboxes[0]` las und dort eine leere Schmalzeile (5 pt hoch) lag. Jetzt wird die erste nicht leere Zeile benutzt; ein Golden-Test deckt Dok. 10 ab.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel Vorverarbeitung

### ISS-013 – Zelltext aus `find_tables()` ist zerrissen
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** gelöst
- **Symptom:** `Table.extract()` lieferte z. B. „1 189 00\n. ,\nEUR“ statt „1.189,00 EUR“ und „Grundpreis(12Monate)“ ohne Leerzeichen.
- **Ursache:** Die Zellextraktion setzt Wörter aus Zeichenpositionen neu zusammen; bei kleiner Schrift und eng gesetzten Satzzeichen geht das schief.
- **Lösung / Workaround:** Nur Fläche und Zeilenbänder von `find_tables()` verwenden; den Text liefern die Spans (`get_text("dict")`), die ich selbst zu Zellen gruppiere (ADR-0007, Punkt 2).
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel Vorverarbeitung, Beleg für „Architektur schlägt naiven Ansatz“

### ISS-012 – `find_tables()` erkennt je nach Strategie unvollständige Tabellen
- **Datum / Meilenstein:** 2026-11-14 / M2
- **Kategorie:** parser
- **Status:** gelöst
- **Symptom:** Bei den Rechnungen mit gefüllten Zellen fehlen Kopfzeile und erste Datenzeile (`lines` in Dok. 04: Tabelle beginnt erst bei „Grundpreis“). `lines_strict` verliert dagegen Kopfzeilen in Dok. 16–19, 26, 28 und fasst in Dok. 29 zwei Zeilen zu einer zusammen („Rechnungsbetrag … Abzüglich Abschlagszahlungen“). Das wäre bei dem Dokument mit dem eingebauten Fehler besonders unglücklich.
- **Ursache:** Die Erkennung braucht sichtbare Kanten. Weiße Zeilen ohne Füllung und ohne Linie haben keine.
- **Lösung / Workaround:** Beide Strategien laufen, bei Überlappung gewinnt die Tabelle mit mehr Zeilen (ADR-0007, Punkt 1). Golden-Tests für Dok. 04, 10, 29.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Kapitel Vorverarbeitung

### ISS-011 – Löschrecht für git zu spät angefragt (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-14 / M1
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Der erste Commit hinterließ `.git/HEAD.lock` und temporäre Objektdateien, weil die Shell nichts löschen durfte.
- **Ursache:** Die Löschberechtigung wurde nicht wie im Projektablauf vorgesehen vor dem ersten Commit angefragt.
- **Lösung / Workaround:** Berechtigung angefragt, die eigenen Lock- und Temp-Dateien entfernt (kein git-Prozess lief), `git fsck` sauber. Künftig zu Sitzungsbeginn anfragen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-010 – Zusatzdokumente 29/30: andere Zeitachse, Layout und wenige Fehler
- **Datum / Meilenstein:** 2026-11-14 / M1
- **Kategorie:** daten
- **Status:** akzeptiert
- **Symptom:** Die Fehlerdokumente sind Rechnungen für 2026 (Datum Januar/März 2027) und damit später als alle Originale. Sie sind einseitig und nachgebaut, nicht aus derselben Vorlage erzeugt wie 01–28. Mit nur drei Fehlern verändert ein einzelner Treffer die Fehlererkennungsrate um 33 Prozentpunkte.
- **Ursache:** Für 2024/2025 existieren bereits Abrechnungen; eine zweite Fassung desselben Jahres hätte den Korpus widersprüchlich gemacht. Die Original-HTML-Vorlagen liegen nicht im Repo.
- **Lösung / Workaround:** Neue Jahre statt Duplikate, Layout per Bildvergleich angenähert. Der Agent muss bei „aktuell“-Fragen das neueste Dokument wählen (Z2 betrifft nur Strom, daher ohne Konflikt). Die Evaluation weist die geringe Fehleranzahl als Einschränkung aus.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Testmodul, Grenzen der Evaluation

### ISS-009 – Gemeinsames `.venv` von Laptop-`uv` und Claudes VM-`uv`
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** Claudes Shell meldete „existing virtual environment linked to non-existent Python interpreter“ und baute `.venv` im Projektordner neu auf. Der Smoke-Test auf dem Laptop baute es danach wieder um (30 Pakete neu installiert).
- **Ursache:** `.venv` verweist auf den Python-Pfad des jeweiligen Rechners; Laptop und Claudes VM sehen denselben Ordner, aber verschiedene Interpreter-Pfade.
- **Lösung / Workaround:** Claudes Shell nutzt `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/audit` außerhalb des Repos. Der Laptop behält das `.venv`. Falls PyCharm den Interpreter nach dem Umbau nicht findet, einmal `uv sync` im Terminal ausführen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-008 – Bilddaten falsch an den Ollama-Client übergeben (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** ki-assistent
- **Status:** gelöst
- **Symptom:** Der Vision-Schritt übergab das Diagramm als rohe `bytes` in `messages[].images`. Die Bibliothek (`ollama` 0.6.3) lehnt das bei der Validierung mit einem `ValidationError` ab. Die Unit-Tests mit gefaktem Client hätten das nie bemerkt.
- **Ursache:** Annahme über die API, die ich nicht gegen die Bibliothek geprüft hatte. Aufgefallen beim Gegenprüfen mit der echten Pydantic-Klasse, bevor der Nutzer den langen Lauf startete.
- **Lösung / Workaround:** Bild als `ollama.Image(value=...)` übergeben; Serialisierung zu Base64 mit `ChatRequest` geprüft.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Reflexion (Grenzen von Mocks, Bibliotheksverhalten selbst prüfen)

### ISS-007 – Modelle setzen ungefragt Metadatenfilter
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** agent
- **Status:** gelöst (RUN-012, ADR-0014)
- **Symptom:** In RUN-000 setzten beide Modelle bei allen 6 Suchaufrufen selbst einen `doc_type`-Filter (z. B. `contract`, `bill`), obwohl die Frage ihn nicht nannte.
- **Ursache:** vermutlich die Beschreibung der optionalen Parameter im Tool-Schema; nicht geklärt.
- **Lösung / Workaround:** In M4/M5: Parameterbeschreibung schärfen („nur setzen, wenn die Frage ihn eindeutig nennt“) und bei null Treffern automatisch ohne Filter wiederholen. **M6d:** Modell filtert nur nach Sparte, `doc_type` und Jahr entfallen; `include_counterpart` holt das Gegenstück. In RUN-012 setzte das Modell in 17 Suchen nie `doc_type` oder Jahr.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval (Filter-Risiko), Agent (Tool-Beschreibungen)

### ISS-006 – Verwechslung von `search_documents` und `search_tables`
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** tools
- **Status:** gelöst (RUN-012, ADR-0014)
- **Symptom:** Bei „Wie hoch ist der Arbeitspreis laut Stromvertrag?“ wählten beide Modelle `search_documents` (Vertrag, Fließtext) statt `search_tables`. Alle anderen Aufgaben (außer dieser) waren richtig.
- **Ursache:** Die Frage nennt „Stromvertrag“, das Tool-Schema trennt Fließtext und Tabellen. Preise stehen aber im Vertrag oft in Tabellen. Die Aufgabe war also teilweise mehrdeutig; Stichprobe mit 5 Aufgaben ist zu klein für Aussagen über die Modelle.
- **Lösung / Workaround:** In M4/M5 prüfen: Tool-Beschreibungen schärfen oder ein gemeinsames Suchwerkzeug mit `chunk_type`-Filter statt zwei getrennter Tools. Im Testmodul die Tool-Wahl-Korrektheit mitmessen. **M6d:** gemeinsames Werkzeug `search` (ADR-0014); Verwechslung nicht mehr möglich.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Werkzeugentwurf), Testmodul (Tool-Wahl-Metrik)

### ISS-005 – Messung der Präfix-Wiederverwendung war ungültig (eigener Fehler)
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** evaluation
- **Status:** offen
- **Symptom:** `smoke.md` meldet „wiederverwendet: nein“ (507 vs. 502 Tokens). Gleichzeitig dauerten Tool-Aufgaben 2–5 mit gleichem System-Prompt und Tool-Schema nur 6–8 s statt der erwarteten 20 s Prefill.
- **Ursache:** Ollama 0.35.1 meldet in `prompt_eval_count` offenbar die volle Prompt-Länge, auch wenn Teile aus dem Cache kommen. Meine Heuristik (weniger Tokens ⇒ Cache) stimmte nicht.
- **Update RUN-005:** Wiederverwendung des Prompt-Anfangs ist zum Teil belegt (G1 und N1: erste Aufrufe mit rund 2.000 Token in 4,8 s und 2,8 s statt 108 s), aber nicht verlässlich (S4: wieder 89 s). `prompt_eval_count` entspricht nicht der Kontextgröße; der Kontextwächter schätzt selbst.
- **Lösung / Workaround:** Heuristik auf die Prefill-Dauer umgestellt (`is_prefix_reused` vergleicht Sekunden, Test angepasst). Nachmessen ist offen und passiert beim ersten Mehrschritt-Agentenlauf in M5; bis dahin gilt die Wiederverwendung als „sehr wahrscheinlich“ (Zeitindiz), nicht als belegt.
- **Update RUN-008:** Für B0 (gleicher Kontext von ca. 6.600 Token, nur die Frage am Ende anders) belegt: Prefill 430 s, danach 12 s und 7 s, bei unverändert gemeldetem `prompt_eval_count`. Die Wiederverwendung wirkt also, `prompt_eval_count` zählt gecachte Token mit; Maß ist die Prefill-Dauer.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Architektur (Latenz im Agentenlauf), Reflexion

### ISS-004 – Nur ein eingebauter Fehler im Testkorpus
- **Datum / Meilenstein:** 2026-11-14 / M1 (Vorbereitung)
- **Kategorie:** daten
- **Status:** gelöst (M1)
- **Symptom:** Beim Nachrechnen aller 28 Dokumente fiel nur eine Unstimmigkeit auf (Stromrechnung 2025: 39,50 statt 38,20 ct/kWh).
- **Ursache:** Korpus wurde ohne Fehlerliste erzeugt.
- **Lösung / Workaround:** In M1 zwei weitere fehlerhafte Dokumente ergänzt (29 Gas 2026: falsche z-Zahl, 30 Betriebskosten 2026: falsche Wohnfläche), Fehlerliste in `ground_truth.yaml`. Mit 3 Fehlern bleibt die Fehlererkennungsrate grob (Schritte von 33 %), siehe ISS-010.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Testmodul, Grenzen der Evaluation

### ISS-003 – Claude kann nicht zu GitHub pushen
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** Claude kann im Projektordner committen und mergen, der Push zu GitHub wird aber abgelehnt (keine Schreibrechte der Claude-GitHub-App).
- **Ursache:** Claude-GitHub-App ist für das Repository nicht installiert; die Shell auf dem Laptop hat keine Git-Zugangsdaten.
- **Lösung / Workaround:** Nutzer pusht am Sitzungsende (`git push origin main --tags`); optional App installieren.
- **Gelernt:**
- **Relevant für Ausarbeitung?** nein

### ISS-002 – Claudes Shell erreicht den lokalen Ollama-Dienst nicht
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** ki-assistent
- **Status:** akzeptiert
- **Symptom:** Aufrufe an `localhost:11434` aus Claudes Shell scheitern.
- **Ursache:** Claudes Shell läuft isoliert in einer VM auf dem Laptop; der Host-`localhost` ist dort nicht erreichbar.
- **Lösung / Workaround:** Alles ohne LLM (ruff, Unit-Tests, Git) führt Claude aus. Ollama-abhängige Schritte startet der Nutzer mit einem vorbereiteten Befehl; Ergebnisse landen als Dateien im Repo und werden von Claude ausgewertet. Unit-Tests nutzen Mocks statt Ollama.
- **Gelernt:**
- **Relevant für Ausarbeitung?** eher nein (höchstens als Randnotiz zur Arbeitsweise)

### ISS-001 – Sehr langsames Prompt-Prefill auf der CPU
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** hardware
- **Status:** akzeptiert
- **Symptom:** Prefill ca. 18 Tokens/s, Generierung ca. 5–6 Tokens/s (7–8B). Ein Prompt mit 4.000 Tokens braucht rechnerisch über 3 Minuten, bevor die Antwort beginnt.
- **Ursache:** Reine CPU-Inferenz (Ryzen 5 7520U, iGPU wird von Ollama nicht genutzt).
- **Lösung / Workaround:** Kurze System-Prompts und Tool-Beschreibungen, kleines `top_k`, kompakte Tool-Ergebnisse, Ergebnisse cachen, Evaluation über Nacht laufen lassen. Gemessen in RUN-000: Prefill 18,9 Tokens/s (`qwen2.5:7b`), 20,1 (`llama3.1:8b`), 45,9 (`llama3.2`); Generierung 5,0 / 5,9 / 12,5 Tokens/s.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Architektur (Modellwahl), Reflexion (Grenzen lokaler Hardware)
