# Entwicklungstagebuch

> Ein Eintrag pro Arbeitssitzung, neueste oben. Claude schreibt den Eintrag beim Sitzungsabschluss.
> **Das Feld „O-Ton“ kommt von mir:** 2–3 ungeschliffene Sätze, wie es lief, was genervt oder überrascht hat. Daraus wird in Phase 2 der persönliche Teil der Ausarbeitung (Reflexion, Vorgehen). Ohne O-Ton klingt der Text später generisch.

## Vorlage

```markdown
### YYYY-MM-DD – <Meilenstein / Arbeitspaket>
**Ziel der Sitzung:**
**Was wurde gemacht:**
-
**Gelieferte Dateien / Funktionen:**
-
**Entscheidungen:** (→ ADR-Nr.)
**Probleme / Überraschungen:** (→ ISS-Nr.)
**Offen / unklar:**
**O-Ton (von mir):**
**Zeitaufwand:** ca. … h · **Modell/Effort:** … · **Commit(s):**
```

---

## Einträge

### 2026-11-14 – M0: Setup, Config, Smoke-Test
**Ziel der Sitzung:** Tooling aufsetzen, zentrale Konfiguration bauen und per Smoke-Test Geschwindigkeit, Tool-Calling, Embedding und Vision der lokalen Modelle messen.
**Was wurde gemacht:**
- `uv`-Projekt mit Python 3.13, `ruff`, `pytest` und Quality-Gate-Skript
- `Settings` und Modell-Preflight; Smoke-Test-Paket mit gefaktem Ollama-Client für Tests ohne LLM
- Smoke-Test vom Nutzer auf dem Laptop ausgeführt (RUN-000, ca. 6,5 Minuten), Ergebnisse ausgewertet
- Messfehler bei der Präfix-Wiederverwendung erkannt und die Messung auf Prefill-Zeit umgestellt
- Doku: ADR-0004 angenommen, ADR-0006 neu, Evaluationslog, Issues, Glossar, README, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `pyproject.toml`, `scripts/check.sh`, `src/audit_agent/{config,preflight}.py`, `src/audit_agent/smoke/*`, `tests/*`, `data/eval/run-000/*`
**Entscheidungen:** ADR-0004 (Agent-Modell vorläufig `llama3.1:8b`), ADR-0006 (natives Tool-Calling)
**Probleme / Überraschungen:** ISS-005 (ungültige Prefix-Messung), ISS-006 (Tool-Verwechslung), ISS-007 (ungefragte Filter), ISS-008 (Bilddaten falsch übergeben), ISS-009 (gemeinsames `.venv`)
**Offen / unklar:** Präfix-Cache belegen (M5); Reverse-Engineering-Fragen zu M0 unbeantwortet; Titelblatt-Angaben
**O-Ton (von mir):** (nicht geliefert, Nutzer hatte keine Zeit)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `chore(tooling)`, `feat(config)`, `feat(smoke)`, `fix(smoke)`, `docs(eval)`, `docs: …M0`

### 2026-11-14 – Vorbereitung II: Korpus-Prüfung, Vorlage, Git
**Ziel der Sitzung:** Vorhandene Testdokumente prüfen, LaTeX-Vorlage einbinden, Doku ins Repo bringen, Arbeitsweise auf „Claude führt selbst aus“ umstellen.
**Was wurde gemacht:**
- 28 synthetische PDFs ausgelesen, alle Beträge nachgerechnet, Diagramme angesehen
- Testkatalog (12 Fragen) mit erwarteten Antworten an den echten Korpus angepasst
- DHBW-LaTeX-Vorlage unter `paper/` eingebunden (nur Titelblatt, Inhaltsverzeichnis, Kapitel aktiv), Kapitelgerüst angelegt
- Git-Historie neu aufgeteilt (Initialisierung, Doku, Korpus, Vorlage); `.idea/` aus der Versionsverwaltung genommen
- Projektanweisungen für Claude neu gefasst (selbstständiges Arbeiten, Git ohne Claude-Hinweise)
**Gelieferte Dateien / Funktionen:** `docs/*` aktualisiert, `paper/`, `.gitignore`, ADR-0005
**Entscheidungen:** ADR-0005 (synthetischer Korpus) akzeptiert
**Probleme / Überraschungen:** ISS-002 (Ollama aus Claudes Shell nicht erreichbar), ISS-003 (kein Push durch Claude), ISS-004 (nur ein eingebauter Fehler)
**Offen / unklar:** weitere Fehler im Korpus? Titelblatt-Angaben; Agent-Modell
**O-Ton (von mir):**
**Zeitaufwand:** ca. … h · **Modell/Effort:** Opus 5.5 · **Commit(s):** siehe `git log`

### 2026-11-14 – Projektstart / Vorbereitung
**Ziel der Sitzung:** Anforderungen sammeln, Projektidee festlegen, Vorbereitung planen.
**Was wurde gemacht:**
- Anforderungen aus Folien und Professor-Hinweisen zusammengefasst (`requirements.md`)
- Projektidee „Energie- & Nebenkosten-Auditor“ ausgearbeitet (`concept.md`)
- Coding Standards, Doku-Struktur, Arbeitsweise mit Claude festgelegt
- Klärungen: selbst erzeugte Dokumente erlaubt, Ich-Form vermeiden
**Gelieferte Dateien / Funktionen:** Doku-Gerüst unter `docs/`, ADR-0001 bis 0004 (Entwürfe)
**Entscheidungen:** ADR-0001 (nur lokal) akzeptiert
**Probleme / Überraschungen:** ISS-001 (langsames Prefill)
**Offen / unklar:** Agent-Modell, Tool-Calling-Variante, Referenzprototyp als Basis?
**O-Ton (von mir):**

**Ausgangslage (für die Reflexion, kurz von mir ergänzen):**
- Was ich schon kann:
- Was ich noch nicht kann / wovor ich Respekt habe:
- Was ich erwarte (z. B. „Agent wird deutlich besser als Standard-RAG“):

**Zeitaufwand:** ca. … h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs: add project documentation scaffold`
