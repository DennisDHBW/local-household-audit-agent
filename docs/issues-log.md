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

### ISS-004 – Nur ein eingebauter Fehler im Testkorpus
- **Datum / Meilenstein:** 2026-11-14 / M1 (Vorbereitung)
- **Kategorie:** daten
- **Status:** offen
- **Symptom:** Beim Nachrechnen aller 28 Dokumente fiel nur eine Unstimmigkeit auf (Stromrechnung 2025: 39,50 statt 38,20 ct/kWh).
- **Ursache:** Korpus wurde ohne Fehlerliste erzeugt.
- **Lösung / Workaround:** offen: 1–2 weitere fehlerhafte Varianten ergänzen oder die Fehlererkennungsrate in der Ausarbeitung als eingeschränkt aussagekräftig benennen.
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
- **Lösung / Workaround:** Kurze System-Prompts und Tool-Beschreibungen, kleines `top_k`, kompakte Tool-Ergebnisse, Ergebnisse cachen, Evaluation über Nacht laufen lassen. Wirkung in M0 messen.
- **Gelernt:**
- **Relevant für Ausarbeitung?** ja → Architektur (Modellwahl), Reflexion (Grenzen lokaler Hardware)
