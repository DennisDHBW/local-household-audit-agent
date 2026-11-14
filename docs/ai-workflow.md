# Arbeitsweise mit Claude (Claude Desktop, Chat)

> Ziel: Das Projekt mit möglichst wenig Handarbeit für mich umsetzen, dabei jeden Teil verstehen (Reverse Engineering) und alles so dokumentieren, dass Claude daraus später die Ausarbeitung schreiben kann.
> **Claude arbeitet selbstständig:** liest und schreibt Dateien direkt im Projektordner, führt Befehle aus, committet und mergt. **Ich:** gebe Pläne frei, starte Befehle, die Ollama brauchen, liefere den O-Ton und beantworte Verständnisfragen.

---

## 1. Einrichtung (einmalig)

### 1.1 Projektanweisungen
Den Block unten in die **Anweisungen des Claude-Projekts** `local-household-audit-agent` kopieren (ersetzt die alte Fassung).

```text
# Projekt: local-household-audit-agent – Energie- & Nebenkosten-Auditor
Hochschulprojekt (DHBW, Kurs „Agentensysteme: Local Agentic AI“): lokaler, agentischer RAG-Prototyp (Python 3.13, Ollama, ChromaDB) und danach eine Ausarbeitung (5–8 Seiten ohne Anhang, LaTeX-Vorlage unter paper/).

## Phasen
- Phase 1 = Umsetzung (aktuell). Phase 2 = Ausarbeitung, erst wenn ich es ausdrücklich sage.

## Umgebung
- Projektordner: /home/usr0/PycharmProjects/local-household-audit-agent (in Claude Desktop verbunden). GitHub: DennisDHBW/local-household-audit-agent, Branch main.
- Du arbeitest selbst im verbundenen Ordner: Dateien direkt lesen und schreiben, Befehle selbst ausführen (git, uv, ruff, pytest). Keine Downloads oder Befehlslisten für Dinge, die du selbst erledigen kannst.
- Deine Shell erreicht Ollama nicht. Alles, was Ollama braucht (Smoke-Test, Enrichment, Agent-Läufe, Evaluation), gibst du mir als EINEN kopierbaren Befehl für mein Terminal im Projektordner. Ergebnisse schreibt der Befehl in Dateien im Repo; die liest du danach selbst aus.
- Fehlt dir eine Berechtigung (Ordnerzugriff, Löschen für git), frag sie über die Tools an.

## Git
- Pro Arbeitspaket ein kurzer Branch (feat/…, fix/…, docs/…, test/…), kleine Commits, danach lokal mit `git merge --no-ff` in main mergen und den Branch löschen.
- Conventional Commits auf Englisch (feat(ingestion): …). Autor ist immer meine Git-Identität aus der Repo-Konfiguration.
- NIE Co-Authored-By, „Generated with Claude“ oder andere Hinweise auf Claude in Commits, Branches, Tags oder Code.
- Pushen: siehe docs/ai-workflow.md, Abschnitt 3 (aktueller Stand dort).
- Vor jedem Commit: `ruff check`, `ruff format --check`, `pytest -m "not slow"` müssen grün sein.

## Ablauf
- Sitzungsbeginn: docs/status.md lesen. Weitere Dateien nur, wenn die Aufgabe sie braucht.
- Vor jedem Arbeitspaket: Plan in 3–6 Stichpunkten (Dateien, Funktionen, Datenfluss), auf mein OK warten. Danach ohne weitere Rückfragen umsetzen, testen, committen, mergen.
- Bei echten Unsicherheiten (fachlich, Architektur, Daten, irreversible Aktionen) fragen, statt zu raten.
- Code nach CODING_STANDARDS.md. Hardware: nur CPU, Ollama MemoryMax=9G, max. 2 geladene Modelle, Prefill ca. 18 Tokens/s, keine Modelle > 8B.
- Keine erfundenen APIs. Bei Unsicherheit über Bibliotheken nachsehen oder es offen sagen.
- Nach jedem Paket: kurze Erklärung auf Studierenden-Niveau (Zweck je Datei, Datenfluss, wichtige Funktionen, Bibliotheken) und 1–2 Verständnisfragen.
- Ehrlich sein: Schwächen, Abkürzungen, Risiken und eigene Fehler offen benennen und im issues-log festhalten.

## Dokumentation (immer mitpflegen, ohne dass ich es sagen muss)
- docs/status.md: am Ende jeder Sitzung aktualisieren (max. 1 Seite).
- docs/dev-journal.md: Eintrag pro Sitzung; das Feld „O-Ton“ kommt von mir, frag am Sitzungsende danach.
- docs/issues-log.md: jedes Problem, jede Schwachstelle, jeden eigenen Fehler sofort eintragen.
- docs/adr/: bei jeder Architektur- oder Technologieentscheidung (neu oder Statusänderung).
- docs/evaluation-log.md: nach jedem Smoke-/Testlauf mit Konfiguration und Ergebnis.
- docs/reverse-engineering/: nach jedem Meilenstein (Vorlage template.md), mit Verständnisfragen an mich ohne Musterantworten.
- docs/glossary.md: neue Fachbegriffe und Code-Bezeichner.
- docs/concept.md und docs/requirements.md: anpassen, wenn sich Konzept oder Anforderungen ändern; vor Meilenstein-Abschluss gegen requirements.md prüfen.
- README.md: Installation und Befehle aktuell halten.
- Doku-Änderungen gehören in denselben Branch wie der Code.

## Sprache
- Chat und docs/: Deutsch. Code, Bezeichner, Commits: Englisch (Begriffe laut docs/glossary.md).
- Antworten knapp, keine langen Zusammenfassungen.
```

### 1.2 Projektwissen
Nur `requirements.md` und `concept.md`. Alles andere liest Claude bei Bedarf direkt aus dem Projektordner.

### 1.3 Ordner und Berechtigungen
In jedem neuen Chat muss Claude den Projektordner und das Löschen im Ordner (für Git-Lock-Dateien) einmal anfragen. Beides einfach bestätigen.

---

## 2. Wer macht was?

| Aufgabe | Claude | Ich |
|---|---|---|
| Plan für ein Arbeitspaket | erstellt | gebe frei |
| Code, Tests, Doku schreiben | ja | – |
| `uv`, `ruff`, `pytest` (ohne LLM), `git` | führt aus | – |
| Befehle mit Ollama (Smoke-Test, Ingest mit Enrichment, Agent, Evaluation) | bereitet einen Befehl vor, wertet Ergebnisdateien aus | starte den Befehl im Terminal, schreibe „fertig“ |
| Push zu GitHub | siehe Abschnitt 3 | siehe Abschnitt 3 |
| O-Ton fürs Journal | fragt danach | 2–3 Sätze |
| Verständnisfragen | stellt sie | beantworte sie |

---

## 3. Push zu GitHub

**Aktueller Stand:** Claude hat noch keine Schreibrechte auf `DennisDHBW/local-household-audit-agent`. Deshalb am Ende jeder Sitzung einmal pushen:

```bash
cd /home/usr0/PycharmProjects/local-household-audit-agent && git push origin main --tags
```

(oder in PyCharm: Git → Push)

Entscheidung: Ich pushe selbst; die Claude-GitHub-App wird nicht installiert.

---

## 4. Modell und Aufwand (Effort)

Im Modellmenü neben dem Senden-Knopf lassen sich Modell, Effort (Low, Medium, High, Extra high, Max) und teilweise Thinking einstellen. Mehr Effort bedeutet gründlichere, aber langsamere Antworten und mehr Verbrauch der Nutzungslimits. Die Einstellung lässt sich mitten im Chat ändern.

| Aufgabe | Modell | Effort |
|---|---|---|
| Routine-Code: Datenmodelle, Config, einfache Tools, Tests, Refactoring | Sonnet 5.5 | Medium |
| Anspruchsvoller Code: Parser, Retrieval-Scoring, ReAct-Schleife, Testmodul | Sonnet 5.5 | High |
| Fehlersuche, wenn Sonnet zweimal danebenliegt | Opus 5.5 | High |
| Architekturentscheidungen, Meilenstein-Planung | Opus 5.5 | High |
| Reverse-Engineering-Runden | Sonnet 5.5 | High |
| Kleine Doku-Pflege | Sonnet 5.5 | Low |
| Auswertung der Evaluation | Opus 5.5 | High |
| Ausarbeitung schreiben | Opus 5.5 | High |
| Endkontrolle der Ausarbeitung (einmalig) | Opus 5.5 | Max |

Fable 5.2 ist nicht nötig. Grundregel: mit Sonnet Medium starten, bei Bedarf eine Stufe hoch.

---

## 5. Ablauf einer Sitzung

**Ein Chat pro Arbeitspaket.** Lange Chats werden teuer; der Zusammenhang steckt in `docs/status.md`.

### Start-Prompt
```text
Neue Sitzung. Lies docs/status.md. Heute: M<x>, „<Arbeitspaket>“. Erst Plan.
```

### Während der Sitzung
- Plan lesen, mit „ok“ oder Änderungswunsch antworten
- Wenn Claude einen Ollama-Befehl gibt: im Terminal ausführen, „fertig“ schreiben
- Verständnisfragen kurz beantworten

### Ende-Prompt
```text
Sitzung abschließen. O-Ton: <2–3 ungeschliffene Sätze, wie es lief>
```
Danach pushen (Abschnitt 3).

---

## 6. Meilenstein-Abschluss

1. Quality Gates grün
2. Reverse-Engineering-Runde (Skill `audit-reverse-engineering`), Verständnisfragen ohne Blick in den Code beantworten
3. ADRs aktualisieren
4. Claude setzt den Tag (SemVer, siehe `status.md`)
5. Pushen inkl. Tags

---

## 7. Skills

| Skill | Wann |
|---|---|
| `audit-session-closeout` | „Sitzung abschließen“ |
| `audit-reverse-engineering` | nach jedem Meilenstein |
| `audit-paper-writer` | Phase 2 |
| **pdf** / **pdf-reading** | Testdokumente ergänzen oder prüfen |
| **dataviz** | Diagramme (Evaluation, Ausarbeitung) |
| **explain-usage** | Verbrauch prüfen |

---

## 8. Phase 2 (Ausarbeitung)

- LaTeX-Vorlage liegt unter `paper/` (DHBW-Vorlage, nur Titelblatt, Inhaltsverzeichnis und Kapitel aktiv)
- Kapitel unter `paper/content/chapter/`, Regeln in `writing-guide.md`
- Modell Opus 5.5, Effort High, Skill `audit-paper-writer`
- Kompilieren: `cd paper && latexmk -pdf main.tex`
