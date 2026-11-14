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
- **Lösung / Workaround:** Heuristik auf die Prefill-Dauer umgestellt (`is_prefix_reused` vergleicht Sekunden, Test angepasst). Nachmessen ist offen und passiert beim ersten Mehrschritt-Agentenlauf in M5; bis dahin gilt die Wiederverwendung als „sehr wahrscheinlich“ (Zeitindiz), nicht als belegt.
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
