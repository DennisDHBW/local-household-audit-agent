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
- **Status:** offen
- **Symptom:** Beim Nachrechnen aller 28 Dokumente fiel nur eine Unstimmigkeit auf (Stromrechnung 2025: 39,50 statt 38,20 ct/kWh).
- **Ursache:** Korpus wurde ohne Fehlerliste erzeugt.
- **Lösung / Workaround:** In M1 werden zwei weitere fehlerhafte Dokumente im gleichen Stil ergänzt.
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
