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
- **Lösung / Workaround:** RAGAS bleibt als zweite Sicht im Report, trägt aber keine Aussage allein. Die Tabelle nennt Faithfulness zusätzlich ohne reine Lückenantworten. Für „Beleg im Kontext?“ zählt der deterministische Abgleich aus `scripts/check_evidence.py`. Ergänzt ISS-047.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Evaluation (Grenzen von LLM-Bewertern auf kleiner Hardware)

### ISS-052 – `search_documents` findet keine Tabellenzeilen, ist bei S1 und Z3 aber das erwartete Werkzeug
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** tools
- **Status:** offen
- **Symptom:** Bei S1 und Z3 (Kündigungsfristen) rufen beide Modelle `search_documents`, wie in `ground_truth.yaml` erwartet. Zurück kommen nur Fließtext-Chunks: Grußformel, Briefkopf, Hinweis auf das Sonderkündigungsrecht. Die Frist steht in einer Tabellenzeile („Kündigungsfrist: 1 Monat …“), die nur `search_tables` liefert. Alle vier P2-Antworten sind falsch, zwei davon erfunden („2 Monate zum Kalendervierteljahr“, „14 Tage“). Die Metrik „Tool-Wahl korrekt“ zählt diese Aufrufe als richtig.
- **Ursache:** Die Werkzeuge trennen nach Chunk-Typ, nicht nach Inhalt. Ob ein Fakt im Fließtext oder in einer Tabelle steht, kann weder das Modell noch der Fragenkatalog vorher wissen; der Katalog hat hier selbst falsch geraten. Die Kapitelüberschrift im Chunk-Text hebt zudem inhaltsleere Zeilen nach oben (ISS-027).
- **Lösung / Workaround:** Noch keine. Für M6d: ein Suchwerkzeug über Text und Tabellen (ISS-006), danach `expected_tools` im Katalog anpassen. Bis dahin ist „Tool-Wahl korrekt“ (7/14 bzw. 5/14) nur eingeschränkt aussagekräftig.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Agent (Werkzeugentwurf), Evaluation (Grenzen der Tool-Wahl-Metrik)

### ISS-051 – Leere gefilterte Suche wird ohne Filter wiederholt und liefert Ablenker
- **Datum / Meilenstein:** 2026-11-15 / M6c (RUN-010, RUN-011)
- **Kategorie:** tools
- **Status:** offen
- **Symptom:** Bei N2 („Grundpreis für Fernwärme“) filtern beide Modelle richtig auf `district_heating`. Die Suche findet nichts, meldet „Keine Treffer mit Filter …; Wiederholung ohne Filter“ und liefert Grundpreise aus Strom- und Gasdokumenten (bei `llama3.1:8b` auch eine Internetrechnung). `llama3.1:8b` nennt daraufhin 12,90 EUR/Monat, `qwen2.5:7b` 13,45 EUR/Monat als Fernwärme-Grundpreis. B0 und P1 beantworten N2 richtig.
- **Ursache:** Die Wiederholung ohne Filter war als Schutz gegen zu enge Filter des Modells gedacht (ISS-007). Bei einer Sparte, die es im Bestand nicht gibt, ist „keine Treffer“ aber genau die richtige Auskunft; die Wiederholung macht daraus scheinbar passende Belege.
- **Lösung / Workaround:** Noch keine. Für M6d: bei leerem Ergebnis nicht ungefiltert wiederholen, sondern melden, welche Sparten und Jahre es gibt, oder nur den Filter lockern, der nicht die Sparte betrifft.
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
- **Status:** offen
- **Symptom:** In RUN-000 setzten beide Modelle bei allen 6 Suchaufrufen selbst einen `doc_type`-Filter (z. B. `contract`, `bill`), obwohl die Frage ihn nicht nannte.
- **Ursache:** vermutlich die Beschreibung der optionalen Parameter im Tool-Schema; nicht geklärt.
- **Lösung / Workaround:** In M4/M5: Parameterbeschreibung schärfen („nur setzen, wenn die Frage ihn eindeutig nennt“) und bei null Treffern automatisch ohne Filter wiederholen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Retrieval (Filter-Risiko), Agent (Tool-Beschreibungen)

### ISS-006 – Verwechslung von `search_documents` und `search_tables`
- **Datum / Meilenstein:** 2026-11-14 / M0
- **Kategorie:** tools
- **Status:** offen
- **Symptom:** Bei „Wie hoch ist der Arbeitspreis laut Stromvertrag?“ wählten beide Modelle `search_documents` (Vertrag, Fließtext) statt `search_tables`. Alle anderen Aufgaben (außer dieser) waren richtig.
- **Ursache:** Die Frage nennt „Stromvertrag“, das Tool-Schema trennt Fließtext und Tabellen. Preise stehen aber im Vertrag oft in Tabellen. Die Aufgabe war also teilweise mehrdeutig; Stichprobe mit 5 Aufgaben ist zu klein für Aussagen über die Modelle.
- **Lösung / Workaround:** In M4/M5 prüfen: Tool-Beschreibungen schärfen oder ein gemeinsames Suchwerkzeug mit `chunk_type`-Filter statt zwei getrennter Tools. Im Testmodul die Tool-Wahl-Korrektheit mitmessen.
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
