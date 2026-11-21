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

### 2026-11-21 – M8 Auswertung Endlauf run-028 (zurückgehaltene Fragen)
**Ziel der Sitzung:** Den Endlauf B0/P1/P2 auf T1–T8 von Hand prüfen und mit den Entwicklungsfragen vergleichen; keine Nachbesserung an diesen Fragen (ISS-108).
**Was wurde gemacht:**
- Rohdaten von run-028 committet; `holdout_questions.yaml` erst jetzt gelesen
- Alle 24 Antworten gegen Sollwerte geprüft, alle P2-Schrittprotokolle und die P1-Kontexte gelesen; Ollama-Journal auf 17:23–18:17 gefiltert
- Ursachen im Code nachvollzogen und ohne Ollama nachgestellt: `route_tools`/`is_audit_question` für T1–T8, `is_pure_gap_answer` für T1, Pfad der leeren Antwort in `AgentLoop.run`
**Ergebnis:** P2 laut Metrik 5/8, nach Handprüfung 4 + 2 Grenzfälle (Entwicklungsfragen: 16 + 1 von 21); P1 3/8 (2 + 1), B0 1/8. Reihenfolge B0 < P1 < P2 hält. Die P2-Ausfälle T3, T5, T6 kommen aus der Wortliste für Prüffragen, der Zeitraum-Reparatur und dem Antwortzwang nach leerer Antwort; T6 erfindet eine Prüfung mit erfundenen Belegen, zählt aber formal als richtiges Urteil ohne Fehlalarm.
**Gelieferte Dateien / Funktionen:** `data/eval/run-028*`, RUN-028 in `evaluation-log.md`, ISS-126, ISS-127, Nachträge zu ISS-108 (jetzt akzeptiert), ISS-119, ISS-120, ISS-125, ADR-0020, ADR-0021, Glossar (Endlauf, Zufallstreffer, Prüffrage); kein Code geändert
**Entscheidungen:** Keine neue ADR; Statusnachträge in ADR-0020 und ADR-0021. Nach ISS-108 keine Nachbesserung an T1–T8.
**Probleme / Überraschungen:** ISS-126 (zwei von zwei Prüffragen nicht erkannt; leere Antworten erstmals, vermutlich Aufrufe nicht angebotener Werkzeuge, nicht geprüft; Antwortzwang ohne Ergebnisse, teils eigener Entwurfsfehler in ADR-0021), ISS-127. Die Lücken-Rückfrage half zum ersten Mal (T3). Das Home der VM-Shell war voll; `uv` installiert Python jetzt nach `/tmp/uv-python-*`.
**Offen / unklar:** Ursache der leeren Antworten (Einzelaufruf mit Ollama nötig); RAGAS für M8
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `test(evaluation): add final run-028 data (M8, held-out questions, B0/P1/P2, qwen2.5:7b)`, `docs: record final run-028 evaluation, ISS-126 and ISS-127`

### 2026-11-21 – M8 Auswertung Kontrolllauf run-027
**Ziel der Sitzung:** Prüfen, ob das Fix-Paket (ISS-121 bis ISS-123) im Kontrolllauf etwas schlechter gemacht hat als in run-026; keine Nachbesserung an den Entwicklungsfragen.
**Was wurde gemacht:**
- Rohdaten von run-027 committet; Kennzahlen aus `report.md`, `scores.json`, `evidence.json` und `agentics.json` mit run-026 verglichen
- Antworten inhaltlich verglichen: 16 von 21 wortgleich (Temperatur 0), anders nur S1, S4, N1, Z2, Z3; diese fünf mit Schrittprotokoll, Sollwerten aus `ground_truth.yaml` und Code der Rückfragen (`loop.py`) geprüft
- Ollama-Journal auf das Laufzeitfenster gefiltert (Datei enthält auch Einträge vom Vortag): höchstens 2.944 Token je Anfrage, keine Kontextverschiebung
**Ergebnis:** laut Metrik 17/21 (run-026: 15), nach Handprüfung 16 + Grenzfall S1 (15); N1 und S1 besser, keine Frage im Ergebnis schlechter; kein `context_limit`, Lücken-Rückfrage 5 → 2, 172 statt 207 s je Frage; Präzision je Beleg 83 % (in Z2 nur formal); 5/5 Fehler, 0 Fehlalarme
**Gelieferte Dateien / Funktionen:** `data/eval/run-027*`, Eintrag RUN-027 in `evaluation-log.md`, ISS-125, Nachträge zu ISS-121 und ISS-122; kein Code geändert
**Entscheidungen:** Nutzer: unverändert in den Endlauf (run-028, `--holdout`); ISS-125 bleibt Befund. Keine ADR.
**Probleme / Überraschungen:** ISS-125 (Mischantwort S1 ohne Beleg, weil die Zitat-Rückfrage Antworten mit Lückensatz überspringt; S4 nach `repeat_limit` mit erfundener Belegnummer). Die Rückfrage-Texte führen in N1 und S4 zuerst zu einem wiederholten `list_documents`. Der alte uv-Cache in `/tmp` gehört einem früheren Sitzungsnutzer; Prüfumgebung deshalb unter `/tmp/*-$(id -u)`.
**Offen / unklar:** RAGAS für M8; wie stark der Gewinn auf den zurückgehaltenen Fragen hält (ISS-108)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `test(evaluation): add control run-027 data (M8, P2 only, qwen2.5:7b)`, `docs: record run-027 evaluation and ISS-125`

### 2026-11-21 – M8 Fix-Paket vor dem Endlauf (ISS-121 bis ISS-123)
**Ziel der Sitzung:** Die drei offenen Befunde aus run-026 beheben, bevor der Kontrolllauf run-027 und der Endlauf laufen.
**Was wurde gemacht:**
- ISS-123: `score_answer` zählt `cited_expected` je zitiertem Beleg; Test mit mehreren Belegen derselben Seite; run-020, 021, 025, 026 mit `evaluation score` offline neu bewertet und mit der Nachrechnung in ISS-123 abgeglichen
- ISS-121: Kontextschätzung je Frage aus den angebotenen Schemas (`_is_context_full`); Test mit einem Fenster, in das nur die geroutete Teilmenge passt; mit dem alten Code schlägt er fehl
- ISS-122: `is_pure_gap_answer` (Lückensatz, keine Zahl, keine Belegnummer); in v2 löst nur sie die Lückenrückfrage aus; Text `RETRY_BEFORE_GAP_MESSAGE_V2` ohne Hinweise auf das Korpus; v1 unverändert (Vergleichbarkeit mit M6)
- Prüfumgebung in der VM-Shell aufgebaut (`/tmp`, weil das Home der VM fast voll ist); `m8_night.sh` auf run-027/run-028 gesetzt
**Gelieferte Dateien / Funktionen:** `evaluation/metrics.py` (`score_answer`), `agent/loop.py` (`_is_context_full`, Bedingung der Lückenrückfrage), `agent/prompts.py` (`is_pure_gap_answer`, `RETRY_BEFORE_GAP_MESSAGE_V2`), 6 neue Tests, neu bewertete `data/eval/run-02{0,1,5,6}`, `scripts/m8_night.sh`, Doku (Glossar, ADR-0021-Nachtrag, concept, evaluation-log)
**Entscheidungen:** Nachtrag zu ADR-0021 (Punkt 5); `min_searches_before_gap` und der Faktor 2,4 Zeichen je Token bleiben unverändert (B0, ISS-120)
**Probleme / Überraschungen:** ISS-124 (Skript hätte run-026 fortgesetzt, eigener Fehler, vor dem Start gefunden). Restrisiko ISS-122: N1 ist eine reine Lückenantwort und wird weiter einmal hinterfragt; S4 bleibt vermutlich falsch.
**Offen / unklar:** Wirkung der drei Fixes erst mit run-027; RAGAS für M8 ja oder nein
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `fix(evaluation): count source precision per cited source`, `test(evaluation): rescore runs 020, 021, 025, 026 with per-source precision`, `fix(agent): estimate context from the schemas of the offered tools`, `fix(agent): question only pure gap answers with a neutral message`, `docs: close fix package for ISS-121 to ISS-123`

### 2026-11-21 – M8 Auswertung Nachtlauf run-026
**Ziel der Sitzung:** run-026 (P2 nach den Fixes aus ADR-0021) auswerten und entscheiden, ob vor dem Endlauf noch etwas behoben wird.
**Was wurde gemacht:**
- Rohdaten von run-026 committet; alle 21 Antworten und Schrittprotokolle von Hand geprüft, Frage für Frage mit run-025 verglichen
- Ursachen der 6 Fehlschläge eingeordnet (Steuerung, Lesefehler des Modells, Werkzeugwahl, Formulierung); Kennzahlen aus `agentics.json` gegenübergestellt
- Kontextabbrüche mit dem Ollama-Journal abgeglichen und die Schätzung im Code nachgemessen (alle 8 Schemas statt der angebotenen)
- Zitat-Präzision für run-020, run-021, run-025 und run-026 nachgerechnet; Messfehler gefunden
**Gelieferte Dateien / Funktionen:** `data/eval/run-026*`, Eintrag RUN-026 in `evaluation-log.md`, ISS-121 bis ISS-123 und Nachträge zu ISS-108, ISS-119, ISS-120, Glossar (`repeat_limit`, Hinweis Quellen-Präzision); kein Code geändert
**Entscheidungen:** Nutzer: Fix-Paket (ISS-121 bis ISS-123) mit Kontrolllauf vor dem Endlauf; B0-Budget im Endlauf unverändert. Endlauf heißt damit run-028. Keine ADR (noch keine Architekturänderung).
**Probleme / Überraschungen:** ISS-122 (Lücken-Rückfrage verschlechtert N1 und S1), ISS-121 (`context_limit` bei ca. 3.700 statt 6.400 Token, eigener Fehler), ISS-123 (Zitat-Präzision seit M6 falsch gemessen, eigener Fehler; betrifft die Zahlen der Ausarbeitung)
**Offen / unklar:** RAGAS für M8; ob die Lücken-Rückfrage nach dem Fix überhaupt noch nützt
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `test(evaluation): add night run-026 data (M8, P2 only, qwen2.5:7b)`, `docs: record run-026 evaluation and ISS-121 to ISS-123`

### 2026-11-21 – M8 Auswertung run-024-smoke und Nachtlauf run-025, Nachbesserung
**Ziel der Sitzung:** Smoke-Test und Nachtlauf auswerten (Handprüfung, Kennzahlen Agentik) und die Fehler an den Entwicklungsfragen beheben.
**Was wurde gemacht:**
- Handprüfung aller 21 P2-Verläufe (Schrittprotokolle) und Durchsicht von B0 und P1: P2 9 von 21 (+2 Grenzfälle), P1 6, B0 4; P2 5 von 5 eingebauten Fehlern, 0 Fehlalarme; 41 von 49 Sollfakten im Kontext, aber nur 27 in der Antwort
- Ursachen: 8 von 12 Fehlschlägen in der Steuerung (Plan als Text, leere Antworten, Verschlechterung durch Rückfragen, Schleife), 3 in Argumenten, 1 Synthese
- Fixes (ADR-0021): Plan-Hinweis entfernt, Schritt-Text bereinigt, Rückfrage bei reiner Ankündigung und leerer Antwort, Rückfall auf die frühere Antwort, Wiederholungsgrenze, Lücke erst nach Volltextsuche, Sprach-Rückfrage, Reparatur von Jahr, Fernwärme und Umfang von Übersicht/Grafik
- Messfehler gefunden und behoben: Tool-Wahl prüfte v2 gegen v1-Werkzeuge (11/21 → 19/21, ISS-118); run-024/025 neu bewertet
- 22 Regressionstests mit echten Ausgaben aus run-025 (21 schlagen auf dem alten Code fehl); 437 Tests grün; Trockenlauf ohne Absturz, Orakel-Obergrenze unverändert 17/21
**Gelieferte Dateien / Funktionen:** `strip_step_talk`, `is_english`, `needs_citation`, `REPEAT_LIMIT`, `AgentRun.is_fallback_answer` (`loop.py`, `prompts.py`, `models.py`, `scope.py`), `expected_tools_v2`/`uses_tool_set_v2` (Bewertung), `scripts/analyze_agentics.py`, `m8_night.sh` (run-026 nur P2, Endlauf run-027), `tests/test_agent_run025.py`
**Entscheidungen:** ADR-0021, Nachtrag ADR-0020
**Probleme / Überraschungen:** ISS-117, ISS-118, ISS-119, ISS-120; eigene Fehler: Fußnoten-Fehler in `drop_trailing_gap` und zu breite Fernwärme-Umdeutung aus der letzten Sitzung, Tool-Wahl-Kennzahl nicht an v2 angepasst, Journal-Kürzung zuerst falsch zugeordnet (UTC/MEZ)
**Offen / unklar:** Wirkung erst in run-026; Fixes sind aus den Entwicklungsfragen abgeleitet (ISS-108); Mischantworten und „stimmt“ ohne Zahlen offen (ISS-119)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,5 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `test(evaluation)` ×2, `fix(agent)` ×2, `test(agent)`, `fix(evaluation)`, `feat(evaluation)`, `docs` ×2

### 2026-11-20 – M8 letzte Runde vor dem Nachtlauf
**Ziel der Sitzung:** Ein letztes Mal so viel wie möglich verbessern, ohne Ollama.
**Was wurde gemacht:**
- Trockenlauf `scripts/dry_run.py` (ganzer Nachtlauf mit Hash-Embeddings und Orakel im Temp-Ordner): kein Absturz; Orakel-Obergrenze P2 von 14 auf 17 von 21 Entwicklungsfragen gehoben (ISS-116)
- Urteilsprüfung gegen `check_bill`, `get_facts(fact=preise)`, Verbrauch/Umrechnung in der Kurzfassung, „Strom“ = Lichtstrom, „seit JJJJ“; `check_evidence.py` kennt die zurückgehaltenen Fragen
- 414 Tests grün
**Gelieferte Dateien / Funktionen:** `scripts/dry_run.py`, Änderungen in `loop.py`, `prompts.py`, `scope.py`, `fact_tools.py`, `models.py`, `scripts/check_evidence.py`, Tests
**Entscheidungen:** ADR-0020 (Nachtrag)
**Probleme / Überraschungen:** ISS-116
**Offen / unklar:** Modellverhalten erst im Nachtlauf
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / Medium · **Commit(s):** `feat(agent)`, `test(evaluation)`, `docs`

### 2026-11-20 – M8 Nachbesserung nach Smoke-Test run-023
**Ziel der Sitzung:** Fehler des Smoke-Tests beheben und vor dem Nachtlauf so viel wie möglich verbessern.
**Was wurde gemacht:**
- run-023-smoke ausgewertet (H2 falsch wegen Sparte Fernwärme, W1 richtig nach drei gesperrten Wiederholungen, V1 richtig mit angehängtem Lückensatz, kein `plan`)
- Bewertungsabbruch behoben (ISS-115); Argument-Reparatur (`agent/scope.py`), `check_bill` mit Kurzfassung, Saldo und beiden Stromrechnungen, Lückensatz entfernen, Plan-Hinweis, kürzere Schemas (ISS-114)
- Werkzeugauswahl nach Fragetyp, Planprüfung, neue Prüfregeln (Preisänderung im Zeitraum, Verbrauchssprung), neuester Stand bei `get_facts` (ADR-0020)
- 411 Tests grün; Werkzeugabdeckung offline: bei 15 von 16 Entwicklungsfragen stehen alle Sollfakten im Ergebnis des passenden Werkzeugs
**Gelieferte Dateien / Funktionen:** `agent/scope.py`, Änderungen in `loop.py`, `fact_tools.py`, `tools.py`, `prompts.py`, `facts/audit.py`, `facts/extract.py`, Tests
**Entscheidungen:** ADR-0020
**Probleme / Überraschungen:** ISS-114, ISS-115
**Offen / unklar:** Wirkung erst im Nachtlauf sichtbar; neue Prüfregeln greifen im Korpus nicht
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,5 h · **Modell/Effort:** Opus 5.5 / Medium · **Commit(s):** `fix(evaluation)`, `fix(agent)`, `feat(agent)`, `docs`

### 2026-11-20 – Text-Befunde und M8 Agent v2 (Heizstrom, Faktenspeicher, Plan, Grafiken)
**Ziel der Sitzung:** Befunde zur Ausarbeitung einarbeiten; danach Architektur so umbauen, dass der Agent mehr als Agent handelt, die Qualität deutlich steigt und auf Anfrage Übersichten und Grafiken entstehen; Dokumentenfokus Strom (Licht- und Heizstrom), Gas, Wasser mit Verträgen.
**Was wurde gemacht:**
- Fragen des Nutzers beantwortet (schwache Ergebnisse, Herkunft `final_score`, 55/60), Text in Kapitel 1–5 angepasst, PDF gebaut (ca. 12 Zeilen über 8 Seiten, ISS-107)
- Plan M8 mit vier Rückfragen vorgelegt (Heizstrom als Nachtspeicher HT/NT, Nebenkosten bleiben, Claude schreibt zurückgehaltene Fragen, Plan freigegeben)
- Dok. 31–35 mit WeasyPrint erzeugt, `tariff_kind` in Metadaten, Index und Filter
- Faktenspeicher und Prüfregeln; Offline-Prüfung RUN-022: 5 von 5 eingebauten Fehlern mit richtiger Auswirkung, 0 Fehlalarme (nach zwei korrigierten Scheinabweichungen)
- Werkzeugsatz v2, Planungsschritt, Selbstprüfung, Artefakte, Chat-UI mit Verlauf; Testmodul mit 21 Entwicklungs- und 8 zurückgehaltenen Fragen, Kennzahlen für Artefakte und Agentik; 402 Tests grün (Cloud-Umgebung)
**Gelieferte Dateien / Funktionen:** `src/audit_agent/facts/` (`extract`, `audit.check_bill`, `views`, `chart`), `agent/fact_tools.py`, `agent/errors.py`, Änderungen in `agent/loop.py`, `tools.py`, `prompts.py`, `models.py`, `app.py`, `evaluation/*`, `corpus/*`; `dataset/holdout_questions.yaml`; `scripts/generate_m8_documents.py`, `m8_prepare.sh`, `m8_night.sh`; Tests `test_facts.py`, `test_agent_v2.py`
**Entscheidungen:** ADR-0018 (Faktenspeicher, regelbasierte Prüfung), ADR-0019 (Agent v2)
**Probleme / Überraschungen:** ISS-107 (Text, Seitenbudget), ISS-108 (Test = Entwicklung), ISS-109 (Heizstrom neben Gasheizung), ISS-110 (Gewinn aus Code), ISS-111 (Regeln layoutgebunden), ISS-112 (zirkuläre Erkennungsrate), ISS-113 (noch kein Ollama-Lauf)
**Offen / unklar:** Verhalten von `qwen2.5:7b` mit acht Werkzeugen; Laufzeit je Frage; RAGAS für M8
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 3 h · **Modell/Effort:** Opus 5.5 / Medium · **Commit(s):** `docs(paper)`, `feat(dataset)`, `feat(facts)`, `feat(agent)`, `feat(evaluation)`, `docs`

### 2026-11-20 – Kapitel 6 entfernt, Kapitel 1–5 sprachlich überarbeitet
**Ziel der Sitzung:** Auf Wunsch des Nutzers Kapitel 6 ohne Ersatz entfernen und den übrigen Text so überarbeiten, dass er weniger nach KI klingt; kein „synthetischer Korpus“, keine Ketten von Fragen-Kürzeln.
**Was wurde gemacht:**
- Anforderungen (`requirements.md`, Projektdoku „Anforderungen“), `writing-guide.md` und alle Kapitel gelesen; Plan mit zwei Rückfragen vorgelegt (Ferrazzi-Absatz in Kapitel 5, Testfragen-Tabelle), beide freigegeben
- Kapitel 6 und sein `\input` gelöscht, Verweis in Kapitel 3 entfernt
- Kapitel 1–5 umformuliert: Fragen über ihren Inhalt benannt, Begründungen ausgeschrieben, Inversionen und Pointen umgestellt, „synthetisch“ ersetzt; neue Tabelle 5.1 mit allen 14 Fragen, Abrechnung (korrekt / mit Fehler) und Ergebnis je Variante plus Kennzahlen; Absatz zu Annahme, Ferrazzi et al. und 7B-Grenze in Kapitel 5
- Erster Entwurf drei Seiten zu lang (ISS-105), danach in vier Builds auf 8 Seiten gekürzt; Zahlen unverändert aus dem alten Text bzw. `evaluation-log.md` (Einzelergebnisse aus dem Nachtrag für Kapitel 5)
**Gelieferte Dateien / Funktionen:** `paper/main.tex`, `paper/content/chapter/0{1..5}*/main.tex`, Kapitel 6 gelöscht; `docs/status.md`, `docs/issues-log.md`, `docs/concept.md`, `docs/requirements.md`, `docs/writing-guide.md`, `docs/sources.md`, `docs/paper-questions.md`; `Claude outputs/Ausarbeitung-ohne-Kapitel6.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** Kapitel 6 entfällt (Nutzer); Ferrazzi-Absatz in Kapitel 5 und Testfragen-Tabelle (vom Nutzer freigegeben); keine ADR
**Probleme / Überraschungen:** ISS-105 (KI-Klang, Kürzel, eigener Fehler beim Seitenbudget), ISS-106 (Reflexion nur noch knapp)
**Offen / unklar:** Reflexion und Ausblick sind dünn (ISS-106); Nutzer liest das neue PDF laut und beantwortet die neuen Fragen 11–14 in `paper-questions.md`
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / Medium · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-20 – Endprüfung der Ausarbeitung (Quellen, KI-Klang, Verständnis)
**Ziel der Sitzung:** Auf Wunsch des Nutzers die Qualität final prüfen: Passen die Quellen zu den Aussagen, sind es die besten, was klingt nach KI, wo wirkt der Text, als sei das Thema nicht verstanden?
**Was wurde gemacht:**
- Lese-Prüfung aller Kapitel gegen `sources.md`, `writing-guide.md`, `requirements.md` und `evaluation-log.md`; Befunde und Plan vorgelegt, Umsetzung erst nach Freigabe
- Quellen auf Wunsch des Nutzers auf höchstens fünf begrenzt: Gao et al. 2023 (Literaturliste der Vorlesung) neu, Self-RAG und RAGAS-Dokumentation entfernt; Gao vorher auf arxiv.org (v5) gelesen; Reserve (Lewis, Panickssery, Zhang et al.) geprüft, nicht aufgenommen
- Neun Stellen korrigiert, die widersprüchlich oder unverstanden wirkten (ISS-103), Orchestrierung in Kapitel 3 benannt
- KI-Klang: Begriffe zum Abhaken umformuliert, Komma-Ketten getrennt, Kapitel 6 neu geschrieben
- Mehrzeilen durch Kürzungen ausgeglichen, alt und neu gebaut und Zeilen je Kapitel verglichen; Inhalt 8 Seiten, Literatur Seite 9
- Fragen des Nutzers beantwortet: Deckblatt bleibt „Konzeptentwurf“ (Name der Prüfungsleistung); Orchestrierung in P2 liegt beim Modell (Werkzeugwahl zur Laufzeit) und bei `AgentLoop` (Ausführung, Grenzen)
**Gelieferte Dateien / Funktionen:** `paper/bibliographie.bib`, `paper/content/chapter/0{1..6}*/main.tex`, `docs/sources.md`, `docs/issues-log.md`, `docs/glossary.md`, `docs/paper-questions.md`, `docs/requirements.md`, `docs/writing-guide.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Endpruefung.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** höchstens fünf Quellen (Nutzer); Deckblatt bleibt „Konzeptentwurf“; Reflexion ohne O-Ton, mit Lehren aus dem dokumentierten Vorgehen; keine ADR
**Probleme / Überraschungen:** ISS-103 (darunter eigene Fehler: Widerspruch ReAct/Act aus ISS-102, drei in den Endkontrollen übersehene Formulierungen, „Modular RAG“ ohne Quelle gestrichen statt Gao zu zitieren)
**Offen / unklar:** Persönlicher Teil in Kapitel 6 (ISS-087); Nutzer beantwortet Fragen 7–10 in `paper-questions.md`; Einordnung von P1 nach Gao (Advanced oder Modular RAG) als mögliche Prüferfrage
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,5 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-20 – Quellenprüfung der Ausarbeitung
**Ziel der Sitzung:** Auf Wunsch des Nutzers die fünf Quellen prüfen und kontrollieren, ob sie im Text korrekt verwendet sind.
**Was wurde gemacht:**
- Angaben aller fünf Paper auf arxiv.org, aclanthology.org und iclr.cc geprüft (Autoren, Titel, Tagung, Seiten, DOI); ICLR 2026 bei Xiang et al. bestätigt
- Jede Zitatstelle gegen das Paper gelesen (Ferrazzi: Abschnitte zu Kosten und Fazit; Xiang: Obs. 1, 2, 8 und Token-Tabelle), dazu System-Prompt (`prompts.py`) und Context-Recall-Code von ragas 0.4.4
- Sieben Stellen präzisiert (ISS-102): Self-RAG in Kapitel 3 und 6, ReAct/Act in Kapitel 3, „meist deutlich“ in Kapitel 4, Context Recall mit eigener Quelle und „je Aussage“ in Kapitel 5, „im Mittel“ in Kapitel 6; Literatur [6] mit DOI, Bibstring „Verfügbar unter“, kein URL-Umbruch nach „https:“
- Alt und neu in der Cloud-Umgebung gebaut und Seite für Seite verglichen: Seitenumbrüche gleich, Inhalt endet auf Seite 8, Literatur auf Seite 9 mit sechs Einträgen
**Gelieferte Dateien / Funktionen:** `paper/bibliographie.bib`, `paper/ads/header.tex`, `paper/content/chapter/0{3,4,5,6}*/main.tex`, `docs/sources.md`, `docs/issues-log.md`, `docs/glossary.md`, `docs/paper-questions.md`, `docs/writing-guide.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Quellenpruefung.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** RAGAS-Dokumentation als sechste Quelle (nur für Context Recall); keine ADR
**Probleme / Überraschungen:** ISS-102 (eigene Ungenauigkeiten vom 2026-11-19); ISS-086 nachgetragen (je Aussage statt je Satz); der Prompt verlangt keinen Thought, P2 ist streng genommen die Variante Act
**Offen / unklar:** Nutzer liest die Paper selbst (ISS-099) und beantwortet die neuen Fragen 4–6 in `paper-questions.md`
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-19 – Quellen für die Ausarbeitung gesucht und eingebaut
**Ziel der Sitzung:** Auf Wunsch des Nutzers passende, möglichst aktuelle Quellen (auch Whitepaper von arXiv) für die Ausarbeitung suchen, die fünf besten auswählen und einbauen.
**Was wurde gemacht:**
- Alle sechs Kapitel nach Begriffen ohne Beleg durchsucht (ReAct, Self-RAG, Modular RAG, RAGAS, GraphRAG, Docling)
- Erste Runde: sechs Quellen aus der Vorlesungsliste und zu GraphRAG/LLM-as-a-Judge geprüft; zweite Runde: 15 weitere aus 2024 bis 2026 (u. a. ACL 2026, ICLR 2026, NeurIPS-2026-Workshop), Tagung und Kennung jeweils auf arxiv.org bzw. aclanthology.org geprüft, Ergebnisse in `sources.md`
- Auswahl mit dem Nutzer abgestimmt: ReAct, Self-RAG, RAGAS, Xiang et al. 2026, Ferrazzi et al. 2026; BibTeX in `paper/bibliographie.bib`, Beispiel-Einträge der Vorlage entfernt, `\printbibliography` aktiv
- ReAct, Self-RAG, RAGAS nur als `\cite`; je ein neuer Satz zu Xiang (Kapitel 4) und Ferrazzi (Kapitel 6); „Modular RAG“ umformuliert; Docling-Satz korrigiert (ISS-100)
- Drei Builds in der Cloud-Umgebung: erste Fassung 4 Zeilen, zweite 2 Zeilen über Seite 8; danach an sechs Stellen gekürzt (Kapitel 1, 2, 3, 4, 5 je kurze Absatzenden); Inhalt endet auf Seite 8, Literatur auf Seite 9, keine undefinierten Verweise
**Gelieferte Dateien / Funktionen:** `paper/bibliographie.bib`, `paper/main.tex`, `paper/content/chapter/0{1..6}*/main.tex`, `docs/sources.md`, `docs/issues-log.md`, `docs/requirements.md`, `docs/writing-guide.md`, `docs/adr/0007-parser-heuristics.md`, `docs/paper-questions.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Quellen.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** Literatur in der Ausarbeitung (ersetzt Entscheidung 2026-11-14); ADR-0007 Nachtrag (Begründung korrigiert, Entscheidung bleibt)
**Probleme / Überraschungen:** ISS-099 (Paper nicht vom Nutzer gelesen), ISS-100 (ungemessene Docling-Aussage), ISS-101 (Context Recall nicht im RAGAS-Paper); der Skill audit-paper-writer verbietet noch ein Literaturverzeichnis
**Offen / unklar:** Nutzer liest Abstract und Ergebnisse der fünf Paper; Reserve-Quellen (Zhang et al. 2026, Wataoka et al. 2024, Huang et al. 2024) nur bei freiem Platz
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-19 – Endkontrolle der Ausarbeitung
**Ziel der Sitzung:** Einmalige Endkontrolle laut status.md: Checklisten `writing-guide.md` §4 und `requirements.md` §11 vollständig prüfen, jede Zahl und jede Absolutaussage gegen die Quelle prüfen (ISS-093), Seitenzahl ≤ 8 halten, neues PDF.
**Was wurde gemacht:**
- Alle sechs Kapitel gelesen und Satz für Satz gegen `evaluation-log.md`, ADR-0004/0006/0007/0008/0009/0010/0012/0014/0016/0017, `ground_truth.yaml`, die Chunk-Dateien, die PDFs (Fußzeilen mit pdfplumber), `data/eval/run-004/search-s2-*.txt`, `run-010/scores.json`, `run-011/answers-p2.jsonl` und `run-021/p2-*.jsonl` geprüft (u. a. Listing-Zeiten 99/112/16/38 s, Pfadtreffer „stromvertrag“ bei S2, 382 Tests, `calculate("1830 - 1920")` bei G2)
- Vier Stellen korrigiert (ISS-098): Fußzeilen Kapitel 2, Ursache der ausschließenden Filter in Kapitel 4 (Code-Stand `f46e50e`), „Ablenkungsdokumente“ in Kapitel 1, „vermutlich“ bei der Graph-Aussage in Kapitel 4; Nebenbefund im evaluation-log korrigiert
- Stil: Suchlauf über die Liste aus writing-guide §3.3, Ich-/Wir-Form, Gedankenstriche, Fettdruck, `\todo`: keine Treffer
- Alter und neuer Stand in der Cloud-Umgebung gebaut und mit `pdftotext -layout` verglichen: nur die vier Sätze ändern sich, gleiche Zeilenzahl, 8 Inhaltsseiten, keine undefinierten Verweise
- Checklisten abgehakt, soweit prüfbar; Punkte des Nutzers offen gelassen
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/01*/02*/04*/main.tex`, `docs/issues-log.md`, `docs/evaluation-log.md`, `docs/writing-guide.md`, `docs/requirements.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Endkontrolle.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** keine neue ADR
**Probleme / Überraschungen:** ISS-098 (zwei ungenaue Aussagen, ein Begriff, eine zu sichere Aussage trotz früherer Prüfungen)
**Offen / unklar:** alle Punkte, die nur der Nutzer erfüllen kann (laut lesen, erklären, eigene Formulierungen, persönlicher Teil Kapitel 6, Abgabe); Literaturbezug bleibt Risiko
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,75 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-19 – GraphRAG kritisch geprüft, Kapitel gegen Anforderungen geprüft
**Ziel der Sitzung:** Auf Nachfrage des Nutzers die GraphRAG-Entscheidung kritisch hinterfragen und den Text anpassen, danach die Ausarbeitung gegen `requirements.md` prüfen und Verbesserungen umsetzen.
**Was wurde gemacht:**
- GraphRAG-Absatz gegen requirements 5.5, ADR-0003 und die Ergebnisse aus Kapitel 5 geprüft: Entscheidung haltbar, Begründung einseitig (ISS-097); Absatz neu geschrieben, Nutzer gab den Vorschlag frei („so anpassen, dass du mit der Qualität zufrieden bist“)
- Alle sechs Kapitel gegen requirements Abschnitte 3, 5 und 6 gelesen: Modellwahl im Enrichment und Hybrid-Suche ergänzt, Restpunkte ISS-095 (z-Zahl, 10 Retrieval-Testfragen, Lauf-Kennungen) umgesetzt; Literaturbezug wegen Entscheidung 2026-11-14 nicht angefasst
- Drei Builds in der Cloud-Umgebung; erste Fassung ragte 0,13 S. auf Seite 9, nach Kürzungen an sieben Stellen endet das PDF ganz unten auf Seite 8; Wortliste writing-guide §3.3 und Ich-/Wir-Form geprüft (keine Treffer)
- Verbindung zum Rechner zwischendurch weg; Kapitel in der Cloud-Kopie fertig bearbeitet und danach übertragen
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/0{1..6}*/main.tex`, `docs/adr/0003-no-full-graphrag.md`, `docs/concept.md`, `docs/issues-log.md`, `docs/paper-questions.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` (überschrieben, nicht versioniert); kein Python-Code geändert
**Entscheidungen:** ADR-0003 Nachtrag (Entscheidung bleibt, Faktentabelle als nicht umgesetzte Alternative)
**Probleme / Überraschungen:** ISS-097 (Begründung vor der Evaluation geschrieben und nicht nachgeprüft); Seitenpuffer aufgebraucht
**Offen / unklar:** persönlicher Teil Kapitel 6 (ISS-087) ohne Platz; Literaturbezug
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-19 – Entscheidung: Überarbeitung Teil 2 entfällt
**Ziel der Sitzung:** Laut status.md Überarbeitung Teil 2 mit den Antworten und Markierungen des Nutzers.
**Was wurde gemacht:**
- `paper-questions.md` geprüft: alle Felder „Antworten (von mir)“ leer, keine Markierungen, keine Eindrücke für Kapitel 6
- Nutzer gefragt (wie in status.md vorgesehen); Entscheidung: direkt Endkontrolle
- status.md auf Endkontrolle umgestellt, Hinweis in `paper-questions.md`, ISS-096 angelegt
**Gelieferte Dateien / Funktionen:** `docs/status.md`, `docs/issues-log.md`, `docs/paper-questions.md`, `docs/dev-journal.md`; kein Code und kein LaTeX geändert
**Entscheidungen:** keine ADR; Überarbeitung Teil 2 gestrichen (Nutzer)
**Probleme / Überraschungen:** ISS-096
**Offen / unklar:** Restpunkte ISS-095 (Endkontrolle); persönlicher Teil Kapitel 6 (ISS-087)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,1 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs`

### 2026-11-18 – Überarbeitung Teil 1 (Kapitel gegeneinander geprüft)
**Ziel der Sitzung:** Laut status.md die Überarbeitung; da noch keine Antworten in `paper-questions.md` vorlagen, nur die Kapitel gegeneinander prüfen und die offenen Entscheidungen klären.
**Was wurde gemacht:**
- Offene Entscheidungen mit dem Nutzer geklärt: Titelblatt „November 2026“ bleibt; kein Hinweis auf die Rolle von Claude bei der Handprüfung, KI-Hinweis der Vorlage entfernt (`aiNote.tex`, Schalter in `main.tex`, `commandDefs.tex`, `settings/document.tex`); PDF noch nicht gelesen
- Alle sechs Kapitel gegeneinander gelesen und neun Stellen angeglichen (ISS-095): Kürzel S/G/N/Z und P2 in Kapitel 1 eingeführt, G1 dort markiert, Prüfablauf in Kapitel 1 als Ziel formuliert, „Grenzfall“ in Kapitel 3 ersetzt, E1 durch Verweis auf Kapitel 1 ersetzt, 629 Chunks in Kapitel 2 hergeleitet, 18/19 Werkzeug-Fehlschläge verbunden, Doppelung der Begründung Kapitel 3/6 entfernt, Bezugswort in Kapitel 6 ergänzt
- Alle Zahlen gegen `evaluation-log.md` geprüft (keine Abweichung; Listing-Zeiten in `run-021/p2-Z1.jsonl` nachgeprüft); Wortliste aus `writing-guide.md` §3.3, Gedankenstriche und rhetorische Fragen geprüft (keine Treffer)
- Zwei Builds: Die erste Fassung kostete 0,12 S. (zusätzliche Zeilen und verschobene Gleitobjekte), nach Kürzung und Verlagerung in einen Absatz mit freier letzter Zeile endet das PDF wie vorher bei gut 80 % von Seite 8; Vergleich gegen einen Build von `main`
- Geänderte Stellen oben in `paper-questions.md` aufgelistet, damit der Nutzer sie beim Lesen findet
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/0{1..6}*/main.tex`, `paper/main.tex`, `paper/ads/commandDefs.tex`, `paper/settings/document.tex`, `paper/ads/aiNote.tex` (gelöscht), `docs/requirements.md`, `docs/paper-questions.md`, `docs/issues-log.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` (überschrieben, nicht versioniert); kein Python-Code geändert
**Entscheidungen:** keine ADR; kein KI-Hinweis (ISS-094, `requirements.md` Abschnitt 2.2)
**Probleme / Überraschungen:** ISS-095 (Kapitel passten nicht zueinander, obwohl jede Zahl stimmte; erste Korrektur zu teuer im Seitenbudget)
**Offen / unklar:** z-Zahl unerklärt, Restpunkte ISS-095; Antworten und Markierungen des Nutzers; persönlicher Teil Kapitel 6 (ISS-087)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,5 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `chore(paper)`, `docs(paper)`, `docs`

### 2026-11-18 – Kapitel 6 „Reflexion und Ausblick“
**Ziel der Sitzung:** Kapitel 6 entwerfen (laut status.md), damit alle sechs Kapitel für die Überarbeitung vorliegen.
**Was wurde gemacht:**
- Material gesammelt (concept §14, requirements §3/§5.7, ADR-0013/0015/0016, RUN-010 bis RUN-021, ISS-058/062/066/067/070/071/074/076/087/088/094, Kandidaten aus `paper-questions.md`); Kapitel 1, 3, 4 und 5 auf Überschneidungen geprüft (Prüfablauf, Self-RAG, GraphRAG und Messgrenzen stehen schon dort); Plan mit drei Absätzen und Wortzahl vorgelegt, Nutzer gab frei
- Kapitel geschrieben: Annahme aus Kapitel 1 nicht bestätigt, Verlauf P2 3 → 9 → 6 und warum die Ursache offen ist, G4 einmal erkannt und verloren, gültiger Aufruf gegen richtige Rechnung (G2), Rückfragen gegen Self-RAG, Prüfablauf sichert Herkunft statt Zuordnung (4 von 14 Prüfgrößen aus demselben Treffer, Chinesisch bei S5); Ausblick mit ISS-070/074/088 und größerem Fragenkatalog
- Vor dem Build von 334 auf ca. 280 Wörter gekürzt, zwei Builds (0,73 und 0,70 S.); Wortliste aus writing-guide §3.3 und Ich-/Wir-Form geprüft (keine Treffer); jede Zahl gegen evaluation-log und ADRs geprüft
- Fünf Fragen in `paper-questions.md`; concept §14 (Seiten); PDF aller Kapitel nach `Claude outputs/` gelegt
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/06-reflection/main.tex`, `docs/paper-questions.md`, `docs/concept.md`, `docs/issues-log.md`, `docs/status.md`, `Claude outputs/Ausarbeitung-Entwurf-Kapitel1-6.pdf` (nicht versioniert); kein Python-Code geändert
**Entscheidungen:** keine ADR; Kapitel 6 ohne persönliche Eindrücke (ISS-087) und ohne Hinweis auf die Rolle von Claude bei der Handprüfung (ISS-094, Entscheidung beim Nutzer)
**Probleme / Überraschungen:** ISS-093 ergänzt (Erstentwurf wieder ca. 24 % zu lang); Gesamtumfang im PDF ca. 7,8 statt 7,6 S. (Lücken durch Gleitobjekte)
**Offen / unklar:** persönlicher Teil der Reflexion, KI-Hinweis, Titelblatt-Zeitraum (status.md)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,5 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-18 – Kapitel 5 „Testmodul und Evaluation“
**Ziel der Sitzung:** Kapitel 5 entwerfen (laut status.md).
**Was wurde gemacht:**
- Material gesammelt (concept §4.3, §11, §14; ADR-0011/0012; RUN-010 bis RUN-021 mit RAGAS-Nachtrag; ISS-028/038/039/045/046/047/050/053/062/066/067/074/076/086/091; `run-011/report.md`, `evidence.json` von RUN-020/021); per git geprüft, dass der B0-Code seit RUN-011 unverändert ist; Plan mit acht Teilen und Wortzahl vorgelegt, Nutzer gab frei
- Kapitel geschrieben: Testmodul (`generate`/`score`/`ragas`, 382 Unit-Tests), Testdaten (Sollfakten 27, Quellen 18, Prüffragen mit und ohne eingebauten Fehler), eigene Metriken und warum von Hand geprüft wird (S5), Belegabgleich, RAGAS mit Grenzen (Faithfulness 0,69 bei richtigen und falschen Antworten, Context Recall gegen Referenzsätze), Tabelle 5.1 B0/P1/P2, Qualitätsaussage, Fehleranalyse (61 Fehlschläge, Engpass Lesen und Vergleichen), Grenzen
- Länge in drei Build-Runden von 1,75 auf 1,43 S. gebracht; Wortliste aus writing-guide §3.3 und Ich-/Wir-Form geprüft (keine Treffer); jede Zahl gegen evaluation-log und `report.md` geprüft
- evaluation-log: Nachtrag Ergebnisse je Fragekategorie; Glossar: „Knapp als richtig gewertet“, „Frage ohne Prüfung“; concept §14 und writing-guide (14 statt 12 Testfragen) aktualisiert; fünf Fragen in `paper-questions.md`
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/05-evaluation/main.tex`, `docs/evaluation-log.md`, `docs/glossary.md`, `docs/concept.md`, `docs/writing-guide.md`, `docs/paper-questions.md`, `docs/issues-log.md`, `docs/status.md`; kein Python-Code geändert
**Entscheidungen:** keine ADR; „knapp als richtig gewertet“ statt „Grenzfall“ für Bewertungen (Glossar); Verlauf von P2 (3 → 9 → 6) aus Platzgründen nach Kapitel 6 verschoben
**Probleme / Überraschungen:** ISS-094 (Qualitätsaussage beruht auf Handprüfung durch Claude); ISS-093 ergänzt (Erstentwurf wieder ca. 25 % zu lang)
**Offen / unklar:** KI-Hinweis zur Rolle von Claude bei der Auswertung (Nutzer entscheidet)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-18 – Kapitel 4 „RAG- und Retrieval-Konzept“
**Ziel der Sitzung:** Kapitel 4 entwerfen (laut status.md).
**Was wurde gemacht:**
- Material gesammelt (concept §6, §10, §14; ADR-0002/0003/0009/0010/0014/0017; RUN-004 mit `search-s2-*.txt`, RUN-018 bis RUN-021; ISS-007/025/027/028/031/051/072/074/077); Plan mit sechs Absätzen und Wortzahl vorgelegt, Nutzer gab frei (RUN-004 im Fließtext statt Tabelle, ADR-0003 auf akzeptiert)
- Kapitel geschrieben: Index und Hierarchie-Präfix, Score-Formel mit S2-Beispiel (0,712 × 1,5 = 1,068) und Boost ohne belegten Nutzen, Metadatenfilter (0/55 statt 4/60 Ablenker, MRR 0,683 → 0,733) und seine Grenzen beim Agenten, Gegenstück und Größen-Anfrage (ISS-072/077, P1 16 statt 13 von 27 Sollfakten im Kontext), Evidence-First mit Belegnummern und 600-Zeichen-Kürzung, GraphRAG-Entscheidung mit G3 als Grenzfall
- Satz zum Gegenstück über den Plan hinaus ergänzt (Begriff stand unerklärt in Tabelle 3.1)
- Länge in sieben Build-Runden von ca. 1,39 auf 1,25 S. gebracht; drei ungenaue Aussagen beim Gegenlesen korrigiert (ISS-093); Wortliste aus writing-guide §3.3 geprüft (keine Treffer)
- ADR-0003 auf „akzeptiert“ mit Nachtrag; Glossar um Query-Rewriting und Sollfakt ergänzt, alter Eintrag „Hierarchie-Prefix“ auf „Hierarchie-Präfix“ verwiesen; concept §14 aktualisiert; fünf Fragen in `paper-questions.md`
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/04-retrieval/main.tex`, `docs/adr/0003-no-full-graphrag.md`, `docs/glossary.md`, `docs/concept.md`, `docs/paper-questions.md`, `docs/issues-log.md`, `docs/status.md`; kein Python-Code geändert
**Entscheidungen:** ADR-0003 akzeptiert (Nutzer); RUN-004-Zahlen im Fließtext ohne Tabelle (Nutzer)
**Probleme / Überraschungen:** ISS-093 (Entwurf zu lang, drei zugespitzte Aussagen)
**Offen / unklar:** Abgrenzung zu Kapitel 5 bei RUN-020 (in `paper-questions.md` markiert)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)` ×2, `docs`

### 2026-11-18 – Kapitel 3 „Architektur des Agenten“
**Ziel der Sitzung:** Kapitel 3 entwerfen (laut status.md).
**Was wurde gemacht:**
- Material gesammelt (concept §7–9, ADR-0001/0004/0006/0010/0013 bis 0017, RUN-000, RUN-005/006, RUN-010 bis RUN-021, ISS-001/005/030/043/057/061/076); Plan mit Wortzahl je Absatz vorgelegt
- Nutzer ließ ohne Rückmeldung fortfahren; Vorschläge übernommen: ReAct-Beispiel Z1 (Prüffrage mit Rechennachfrage, Grenzfall), Prüfablauf in Kapitel 3
- RUN-021-Protokolle ausgezählt: 23 Werkzeugaufrufe (16 `search`, 4 `list_documents`, 3 `calculate`), 13 Rückfragen, 22 von 22 Antworten mit Werkzeugaufruf ohne Text (kein sichtbarer Thought), erster Aufruf 1.761–1.775 Token und 82–105 s Prefill; als Nachtrag in `evaluation-log.md`
- Beim Auszählen ADR-0014 korrigiert: Der Rückgang ungültiger Aufrufe kam vom fehlenden `calculate`, nicht vom Suchwerkzeug (ISS-091)
- Kapitel geschrieben: zwei Phasen, Werkzeugtabelle, natives Tool-Calling, Umbau auf `search`, eigene Schleife mit Rückfragen (Bezug Self-RAG), Prüfablauf als Negativergebnis, Listing Z1, Modellwahl llama → qwen, Antwortzeit; Erstentwurf 616 Wörter / ca. 2,1 S., gekürzt auf ca. 1,6 S. (ISS-092); Wortliste aus writing-guide §3.3 geprüft (keine Treffer)
- Kapitel 2: Zeilenüberlauf bei \enquote{Datum: 18.01.2025} behoben; Glossar um „Lückenrückfrage“ ergänzt; fünf Fragen in `paper-questions.md`
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/03-architecture/main.tex`, `paper/content/chapter/02-data-preprocessing/main.tex`, `docs/evaluation-log.md`, `docs/glossary.md`, `docs/adr/0014-search-tool-and-filter-policy.md`, `docs/issues-log.md`, `docs/paper-questions.md`, `docs/status.md`; kein Python-Code geändert
**Entscheidungen:** keine ADR; Z1 als ReAct-Beispiel und Prüfablauf in Kapitel 3 (Vorschlag von Claude, Nutzer ließ fortfahren)
**Probleme / Überraschungen:** ISS-091 (eigene Fehldeutung in ADR-0014), ISS-092 (Kapitel 3 ca. 0,1 S. über Budget)
**Offen / unklar:** Ob der Self-RAG-Vergleich im Gespräch trägt (in `paper-questions.md` markiert)
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(eval)`, `docs(paper)`, `fix(paper)`, `docs(status)`

### 2026-11-18 – Kapitel 2 „Datenbasis und Vorverarbeitung“
**Ziel der Sitzung:** Kapitel 2 entwerfen (laut status.md).
**Was wurde gemacht:**
- Material gesammelt (concept §4–5, ADR-0005/0007/0008, ISS-012 bis ISS-024, RUN-001 bis RUN-004, Fehleranalyse RUN-010/011, echter Chunk aus `data/processed/06_…_chunks.json`)
- Nutzer wählte Variante (a): JSON-Listing im Text, Budget 1,25 statt 1,0 Seiten
- Kapitel geschrieben: Layoutmerkmale des Korpus, Parser-Regeln mit ISS-012/013 und verworfenen Alternativen, Chunk-Zahlen aus RUN-001, ISS-017, Listing der E1-Zeile, Enrichment mit Cache, Fehler aus RUN-002/003, Summaries nur als Suchhilfe (RUN-004), Grenzen
- Erster Entwurf ca. 1,7 Seiten, auf ca. 1,3 Seiten gekürzt; ISS-014 dabei gestrichen; Wortliste aus writing-guide §3.3 geprüft (keine Treffer)
- Fünf Verständnisfragen in `paper-questions.md`; Seitenbudget und Messmethode in `concept.md` §14
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/02-data-preprocessing/main.tex`, `docs/paper-questions.md`, `docs/concept.md`, `docs/issues-log.md`, `docs/status.md`; kein Python-Code geändert
**Entscheidungen:** JSON-Listing im Text statt im Anhang (Nutzer); keine ADR
**Probleme / Überraschungen:** ISS-090 (Seitenbudget knapp, Messmethode für Kapitel 1 nicht notiert)
**Offen / unklar:** –
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 / High · **Commit(s):** `docs(paper)`, `docs`

### 2026-11-18 – Kapitel 1 „Problemstellung und Use Case“
**Ziel der Sitzung:** Seitenbudget je Kapitel und Titelblatt festlegen, Kapitel 1 entwerfen (laut status.md).
**Was wurde gemacht:**
- Seitenbudget festgelegt (concept.md §14): 1,25 / 1,0 / 1,5 / 1,25 / 1,5 / 0,75 Seiten, Summe 7,25 von 8
- Kapitel beginnen ohne Seitenumbruch (`\scr@startchapter` gepatcht), sonst bis zu 3 Seiten Weißraum bei 6 kurzen Kapiteln
- Titelblatt vollständig (Name, Matrikelnummer, Studiengang, Kurs INF24A, Dozent, November 2026); fehlendes Leerzeichen in der Vorlage („Baden-WürttembergMosbach“) behoben; rotes `\todo`-Makro für offene Angaben
- Material gesammelt (concept §1–4, ADR-0001/0005, ISS-019/039/044, RUN-010-Manifest, Chunks mit IBAN und Zählernummer); Kapitel 1 geschrieben, gemessen ca. 1,2 Seiten (ca. 500 Wörter), Wortliste aus writing-guide §3.3 geprüft
- Lücke gefunden: Hinweis „keine Rechtsberatung“ fehlt in Prompt und UI (ISS-088), im Text offen benannt
- Nutzer liest und beantwortet die Verständnisfragen erst nach allen Kapiteln; Fragen in `docs/paper-questions.md`
**Gelieferte Dateien / Funktionen:** `paper/content/chapter/01-problem-use-case/main.tex`, `paper/settings/document.tex`, `paper/ads/header.tex`, `paper/ads/commandDefs.tex`, `paper/ads/cover.tex`, `docs/paper-questions.md` (neu), `docs/concept.md`, `docs/writing-guide.md`, `docs/issues-log.md`, `docs/status.md`; kein Python-Code geändert
**Entscheidungen:** Seitenbudget und Kapitel ohne Seitenumbruch (Layout, keine ADR); Schritte 4–7 des Leitfadens gesammelt nach Kapitel 6 (Wunsch des Nutzers)
**Probleme / Überraschungen:** ISS-088 (Rechtsberatungs-Hinweis fehlt), ISS-089 (LaTeX-Pakete fehlen in Claudes Shell, Build in der Cloud-Umgebung)
**Offen / unklar:** Bearbeitungszeitraum „November 2026“ aus Git abgeleitet, nicht vorgegeben
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(paper)` ×2, `docs(status)`

### 2026-11-18 – RAGAS-Auswertung v1.0.0, Freigabe Phase 2
**Ziel der Sitzung:** RAGAS-Ergebnisse von RUN-020 (P1) und RUN-021 (P2) auswerten und ISS-082 schließen (laut status.md).
**Was wurde gemacht:**
- RAGAS-Nachtlauf geprüft: 3,1 h, kein Fehlschlag; Rohdaten und die RAGAS-Abschnitte in `report.md` committet
- Quality Gate und `check_evidence.py` auf dem Laptop (382 Tests grün); RAGAS-Werte mit Sollfakten im Kontext, Lückenantworten und Handprüfung abgeglichen
- Alle 24 Context-Recall-Werte und 6 auffällige Faithfulness-Werte von Hand gegen Referenzsatz und Belege gelesen
- Befund: Die 8 gemeldeten Widersprüche zum Sollfakten-Abgleich sind Scheinwidersprüche (ISS-086); die Deutung aus RUN-010/011 ist damit zum Teil korrigiert (ISS-053). Faithfulness trennt bei P2 richtige nicht von falschen Antworten (beide 0,69)
- Nutzer gibt Phase 2 frei und liefert keinen O-Ton mehr (ISS-087); offene O-Ton-Felder auf „nicht geliefert“ gesetzt
**Gelieferte Dateien / Funktionen:** `data/eval/run-020/`, `data/eval/run-021/` (`ragas.jsonl`, `evidence.json`, `report.md`, `scores.json`, `manifest.json`), `data/eval/ragas-v1.0.0.log`, `data/eval/ragas-v1.0.0-check.log`; `docs/evaluation-log.md` (RAGAS-Nachtrag RUN-020/021), `docs/issues-log.md`, `docs/glossary.md` (Context Recall), `docs/status.md`; kein Code geändert
**Entscheidungen:** Referenzantworten bleiben unverändert (Vergleichbarkeit der Läufe); Phase 2 startet auf Wunsch des Nutzers; keine ADR
**Probleme / Überraschungen:** ISS-086 (Scheinwidersprüche im Abgleich, eigene Fehldeutung in RUN-010/011), ISS-087 (kein O-Ton); ISS-082 gelöst
**Offen / unklar:** Titelblatt-Angaben; ISS-080/081/086 nur bei Zeit
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,5 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `test(evaluation)`, `docs(evaluation)`, `docs(status)`

### 2026-11-17 – Erklärungen zu den M6-Fragen, RAGAS-Nachtlauf gestartet
**Ziel der Sitzung:** Nächstes Paket laut status.md: Antworten des Nutzers zu R1-1 bis R3-8 abgleichen.
**Was wurde gemacht:**
- Nutzer kann die Fragen mangels Zeit und Vorwissen nicht beantworten; auf seinen Wunsch alle 24 Fragen in einfacher Sprache beantwortet, vorher gegen den Code geprüft (`loop.py`, `prompts.py`, `variants.py`, `store.py`, `quantity.py`, `metrics.py`, `audit_flow.py`, `ragas_eval.py`, `check_evidence.py`)
- Erklärungen als eigene Spalte „Erklärung (Claude)“ in Abschnitt 6 der drei M6-Notizen; „Meine Antwort“ bleibt leer
- Befehl für den RAGAS-Nachtlauf auf RUN-020 und RUN-021 übergeben (ISS-082); Log `data/eval/ragas-v1.0.0.log`
**Gelieferte Dateien / Funktionen:** `docs/reverse-engineering/m6-evaluation.md`, `m6-quantity-retrieval.md`, `m6-agent.md` (Abschnitt 6); kein Code geändert
**Entscheidungen:** RAGAS-Nachtlauf statt alter RAGAS-Werte (offene Frage aus ISS-082); keine ADR
**Probleme / Überraschungen:** ISS-085 (Fragen nicht selbst beantwortet)
**Offen / unklar:** Ergebnis des RAGAS-Nachtlaufs; Abschnitte 5–7 der Notizen M0–M6
**O-Ton (von mir):** „Ich habe zu wenig wissen um die Fragen beantworten zu können und zu wenig Zeit um mich damit zu beschäftigen.“
**Zeitaufwand:** ca. 0,4 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(reverse-engineering)`

### 2026-11-17 – Reverse-Engineering-Fragen M6 im Repo gesichert
**Ziel der Sitzung:** Antworten des Nutzers zu den M6-Fragen auswerten (laut status.md).
**Was wurde gemacht:**
- Festgestellt: Die Fragen standen nur im alten Chat, Abschnitt 6 der Notizen war leer (ISS-084)
- Nutzer hat aktuell keine Zeit zum Antworten; Auswertung verschoben
- Je 8 Fragen pro Runde neu formuliert und in Abschnitt 6 der drei M6-Notizen eingetragen (ohne Musterantworten)
**Gelieferte Dateien / Funktionen:** `docs/reverse-engineering/m6-evaluation.md`, `m6-quantity-retrieval.md`, `m6-agent.md` (Abschnitt 6); kein Code geändert
**Entscheidungen:** keine
**Probleme / Überraschungen:** ISS-084 (Fragen nur im Chat; betrifft auch M0, M2–M5)
**Offen / unklar:** Antworten des Nutzers; RAGAS-Nachtlauf ja oder nein
**O-Ton (von mir):** (nicht geliefert, Nutzer hatte keine Zeit)
**Zeitaufwand:** ca. 0,3 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(reverse-engineering)`

### 2026-11-17 – Abschluss M6: Reverse Engineering, Abgleich mit den Anforderungen, v1.0.0
**Ziel der Sitzung:** M6 rückwärts aufarbeiten (Testmodul, Größen-Anfrage, Sparten-Filter, Rückfragen), gegen `requirements.md` prüfen und v1.0.0 taggen.
**Was wurde gemacht:**
- 44 seit v0.2.0 geänderte Dateien in drei Runden aufgeteilt (Nutzer einverstanden, Tag auch ohne seine Antworten)
- Datenflüsse an echten Läufen nachgezeichnet: G1 in P1 (RUN-020) und P2 (RUN-021), S1 mit Zitier-Rückfrage (RUN-021)
- Je Runde Erklärung, 4 fehlende Whitebox-Tests und 7–8 Verständnisfragen ohne Musterantworten im Chat
- Abgleich mit `requirements.md`; Konzept 11.1 (P1 mit Größen-Suche) und 13 (M6-Dateien), Glossar (Wiederholungssperre, Text-Aufruf), README, ADR-0017-Status nachgezogen; vier Grundanforderungen in der Abgabe-Checkliste abgehakt
**Gelieferte Dateien / Funktionen:** `docs/reverse-engineering/m6-evaluation.md`, `m6-quantity-retrieval.md`, `m6-agent.md`, `m6-abgleich-requirements.md`; kein Code geändert
**Entscheidungen:** ADR-0017 Status ergänzt (ISS-077 gelöst in M6i); keine neue Architekturentscheidung
**Probleme / Überraschungen:** ISS-080 (Sparte bei „Strom- und Gaspreis“), ISS-081 (Gegenstück-Hinweis „keine Treffer“, obwohl Rechnung und Preisschreiben schon da sind), ISS-082 (RAGAS nicht für v1.0.0), ISS-083 (Prüffrage-Erkennung per Wortliste). Zwei eigene Fehldeutungen beim Schreiben der Notizen, vor dem Commit korrigiert: Beleg [6] enthält bei G1 beide Preise (34,80 und 38,20), und bei G1 lief gar keine Gegenstück-Suche
**Offen / unklar:** Antworten des Nutzers zu M6 (und M0, M2–M5); RAGAS-Nachtlauf ja oder nein
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h · **Modell/Effort:** Opus 5.5 · **Commit(s):** `docs(reverse-engineering)`, `docs`, Tag `v1.0.0`

### 2026-11-17 – M6i: Sparte in der Größen-Anfrage
**Ziel der Sitzung:** Den Fehler aus M6h beheben, dass die Größen-Anfrage ohne Sparte bei P1 das Gas-Schreiben statt der Strom-Zeile trifft (ISS-077); P1 und P2 neu messen.
**Was wurde gemacht:**
- Plan mit Entscheidung des Nutzers: Sparte als Metadaten-Filter statt als Suchwort, nur wenn die Frage genau eine Sparte nennt und kein Filter gesetzt ist; G3 (ISS-074) und leere Antwort (ISS-076) nicht in diesem Paket
- `utility_in_query`, `with_query_utility`; P1 (Größen-Suche) und P2 (Größen- und Gegenstück-Suche) angepasst; Hinweistext nennt die Sparte; 20 neue Tests (381 insgesamt)
- Zwei Verbindungsabbrüche zum Laptop; danach war in Claudes Shell keine bleibende Umgebung mehr möglich, Quality Gate lief im Messbefehl auf dem Laptop (ISS-078)
- RUN-020 (P1, 25 min) und RUN-021 (P2, nach Abbruch fortgesetzt, ISS-079) ausgewertet; alle 14 P1-Antworten von Hand gelesen, P2 gegen RUN-018 verglichen
**Gelieferte Dateien / Funktionen:** `retrieval/quantity.py` (`utility_in_query`, `with_query_utility`, `UTILITY_WORDS`, `DOCUMENT_WORDS`), `agent/tools.py` (`_search`, `_counterpart_hits` mit Sparte), `evaluation/variants.py` (P1), Tests in `test_retrieval.py`, `test_agent_tools.py`, `test_evaluation.py`
**Entscheidungen:** ADR-0017, Nachtrag M6i (Sparte als Filter, Suchwort verworfen)
**Probleme / Überraschungen:** ISS-077 gelöst; ISS-078 (Shell ohne bleibende Umgebung, Gate auf dem Laptop); ISS-079 (RUN-021-Abbruch ungeklärt, Log beim Fortsetzen überschrieben); ISS-076 erneut, aber nur als identische Wiederholung (Temperatur 0)
**Offen / unklar:** Warum RUN-021 um 13:59 abbrach; G1 bleibt bei P1 und P2 falsch, obwohl die Zahlen im Kontext stehen (Engpass Lesen und Vergleichen); Streuung der Läufe nicht gemessen
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** Arbeit ca. 2,5 h über den Tag verteilt, Läufe 25 + 72 min Rechenzeit · **Modell/Effort:** Fable 5.2, ab der Fortsetzung Opus 5.5 · **Commit(s):** `feat(retrieval)`, `test(evaluation)`, `docs`

### 2026-11-17 – M6h: Größen-Anfrage, Zitier-Rückfrage und Einheitenfaktor
**Ziel der Sitzung:** Das Retrieval verbessern, damit die Sollzahl (G1, G3) im Kontext steht; Zitierpflicht für P2; Einheitenfaktor der Metrik einschränken (ISS-050, ISS-051/052).
**Was wurde gemacht:**
- Plan mit vier Entscheidungen des Nutzers: gezielte Größen-Anfrage statt mehr Treffer, Hierarchie-Boost behalten, Summaries für den Agenten aus, Einheitenfaktor nur für ct und EUR
- `quantity_query` und `new_quantity_hits`: zweite Suche mit der Größe allein für P1 und P2, Gegenstück-Suche nutzt sie; Zitier-Rückfrage im Loop; Metrik und `parse_number` angepasst (ISS-073); 26 neue Tests (361 insgesamt), Quality Gate grün
- Nachbewertung RUN-010 bis RUN-017 mit der neuen Metrik: keine Änderung
- RUN-018 (P2, 63 min) und RUN-019 (P1, 21 min) ausgewertet, alle 14 Antworten von RUN-018 gelesen, Kontext je Frage gegen RUN-014 und RUN-011 verglichen
- VM-Speicher voll: Umgebung in `/dev/shm` (ISS-075)
**Gelieferte Dateien / Funktionen:** `retrieval/quantity.py` (`quantity_query`, `new_quantity_hits`), `agent/tools.py` (`_search`, `_counterpart_hits`), `agent/loop.py` (Zitier-Rückfrage), `agent/prompts.py` (`has_citation`, `CITE_BEFORE_ANSWER_MESSAGE`), `evaluation/variants.py` (P1), `evaluation/metrics.py` (`_is_money`), `numbers.py`, `config.py` (`quantity_hits`, `require_citation`)
**Entscheidungen:** ADR-0017 (Zitier-Rückfrage und Einheitenfaktor akzeptiert; Größen-Anfrage umgesetzt, ohne messbaren Gewinn, bleibt an)
**Probleme / Überraschungen:** ISS-072 (Jahr und Dokumentwort ziehen das Dokument), ISS-073 (`0,348` als 348 gelesen), ISS-074 (G3 ohne Vorjahres-Gegenstück), ISS-075 (VM-Speicher), ISS-076 (leere Antwort nach Rückfrage), ISS-077 (Größen-Anfrage ohne Sparte, Fehler im Entwurf von Claude)
**Offen / unklar:** Ob die Sparte in der Größen-Anfrage P1 und P2 hilft (M6i); ob M6 vor oder nach M6i abgeschlossen wird; Streuung der Läufe nicht gemessen
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** Sitzung ca. 3 h, Läufe 63 + 21 min Rechenzeit · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `fix(numbers)`, `feat(retrieval)`, `feat(agent)`, `docs` ×2, `test(evaluation)`

### 2026-11-16 – M6g: Fester Prüfablauf und Modellwechsel (Negativergebnis)
**Ziel der Sitzung:** Prüfablauf (Soll suchen, Ist suchen, Code rechnet) und Modell für P2 entscheiden, umsetzen und mit RUN-017 messen (ISS-066, ISS-067).
**Was wurde gemacht:**
- Entscheidungen des Nutzers: fester Prüfablauf ja, `qwen2.5:7b` als P2-Modell; später nach RUN-017: Ablauf abschalten, als Negativergebnis behalten
- `agent/audit_flow.py`: Plan (JSON-Schema), Suchen über das normale `search`-Werkzeug, Lesen je Prüfgröße, Herkunftsprüfung der Zahlen im Treffer der richtigen Seite, Differenz mit `calculate`; Einbindung in `AgentLoop`, neue Schritte `AuditFlowStep` und `is_flow_call` in Log, CLI, UI und Report
- 15 neue Tests (`tests/test_audit_flow.py`), bestehende Loop-Tests auf abgeschalteten Ablauf umgestellt; Quality Gate grün (335 Tests)
- RUN-017 (89 min) ausgewertet: Schrittdateien aller 6 Prüffragen gelesen, alle 14 Antworten von Hand bewertet, Ollama-Journal geprüft (kein Abschneiden)
- Doku: ADR-0016 (mit Ergebnis und Folge), ADR-0013/0015 Status, ISS-066/067 Status, ISS-068 bis ISS-071, evaluation-log, Glossar, README, concept.md
**Gelieferte Dateien / Funktionen:** `agent/audit_flow.py`, `agent/loop.py` (`_run_audit_flow`), `agent/models.py` (`AuditFlowStep`, `AuditCheckResult`), `agent/prompts.py`, `config.py` (`audit_flow_enabled`, `audit_max_checks`, Standardmodell), `tests/test_audit_flow.py`, `data/eval/run-017/`
**Entscheidungen:** ADR-0016 (akzeptiert für das Modell; Ablauf umgesetzt, nicht bestätigt, abgeschaltet)
**Probleme / Überraschungen:** ISS-070 (Soll und Ist falsch zugeordnet, gleiche Treffer auf beiden Seiten), ISS-071 (Nachricht des Ablaufs führt zu Lückenantworten und chinesischem Text), ISS-068 (Herkunft gesichert, Vergleichbarkeit nicht), ISS-069 (VM-Platte voll, Cache-Ordner einer alten Sitzung; mein Löschversuch wurde abgelehnt, ohne Löschen gelöst). Ein fester Ablauf machte aus falschen Suchtreffern exakte, belegt wirkende falsche Rechnungen.
**Offen / unklar:** Warum G4 ohne Ablauf (RUN-014) gefunden wurde und mit Ablauf nicht (nur ein Lauf je Zustand, Streuung bei gleichem Code 0); ob eine Überarbeitung (Dokumentart je Seite trennen) den Ablauf rettet; G1 und G3 scheitern weiter am Retrieval der Sollzahl
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** Sitzung ca. 2 h, Lauf 89 min Rechenzeit · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(agent)`, `test(evaluation)`, `docs` ×3, `feat(agent)` (Ablauf aus)

### 2026-11-16 – M6f: Format-Toleranz, Gegenprobe `qwen2.5:7b`, Streuungsmessung
**Ziel der Sitzung:** Prüfablauf von P2 stabilisieren (Aufruf als Text, `calculate`), Gegenprobe mit `qwen2.5:7b` und Streuung bei gleichem Code messen (ISS-061 bis ISS-063).
**Was wurde gemacht:**
- Code (frühere Sitzung): Aufruf als Text erkennen und ausführen, `calculate` akzeptiert Operanden und deutsche Zahlen, Wrapper `scripts/eval_run.sh`
- Drei Läufe auf dem Laptop: RUN-014 (`qwen2.5:7b`), RUN-015 und RUN-016 (`llama3.1:8b`, derselbe Code)
- Alle 42 Antworten gelesen und von Hand bewertet; Rechennachfrage, Sperre und Textaufrufe je Lauf aus den Schrittdateien gezählt; Ollama-Journale auf Speichermangel und Abschneiden geprüft (keins)
- Doku: evaluation-log, ISS-061/062/063/058 aktualisiert, ISS-066/067 neu, ADR-0015 und ADR-0013 ergänzt
**Gelieferte Dateien / Funktionen:** `agent/text_calls.py`, `agent/calculator.py`, `agent/loop.py`, `scripts/eval_run.sh`, `data/eval/run-014/` bis `run-016/`
**Entscheidungen:** keine neue; ADR-0015 (vorgeschlagen) und ADR-0013 warten auf deine Entscheidung zu Modell und festem Prüfablauf
**Probleme / Überraschungen:** RUN-015 und RUN-016 sind bis auf die Zeiten identisch (Streuung 0, ISS-062); die Nachfrage wirkt bei `qwen2.5:7b`, nicht bei `llama3.1:8b` (ISS-066); gültige `calculate`-Aufrufe mit falschen Operanden erzeugen Fehlalarme (ISS-067); beide Modelle 6 von 14 nach Handprüfung
**Offen / unklar:** fester Prüfablauf ja oder nein; Modell für P2; welche M6e-Änderung S2/S4/N2 verschlechtert hat; G1 und G3 scheitern am Retrieval der Sollzahl
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** Auswertung und Doku ca. 1 h, Läufe 3 h 41 min Rechenzeit (70 + 76 + 75 min) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(agent)`, `feat(scripts)`, `test(evaluation)`, `docs`

### 2026-11-16 – M6e: P2 rechnen und prüfen lassen (Wiederholungssperre, Rechennachfrage)
**Ziel der Sitzung:** Der Agent soll bei Prüffragen rechnen (ISS-058) und nicht mehr dieselbe Suche wiederholen; Laufzeitursache klären (ISS-057); mit RUN-013 messen.
**Was wurde gemacht:**
- Laufzeit zuerst ausgewertet: `scripts/analyze_timing.py` trennt Prefill und Dekodieren je Lauf; die erste Anfrage je Frage hatte in RUN-012 keinen Prompt-Cache
- Loop: identische Aufrufe werden nicht ausgeführt (`REPEAT_OBSERVATION`, `ToolCallStep.is_repeat`); Prüffrage ohne `calculate` wird einmal nachgefragt (`is_audit_question`, `NudgeStep.reason`); Prompt um Soll-/Ist-Suchhinweis ergänzt; CLI, Streamlit und Bericht zeigen den Status
- 16 neue Tests mit gescriptetem Chat-Client, ein vorhandener Test an die neue Prüffragen-Erkennung angepasst (288 grün)
- RUN-013 (P2, 14 Fragen, 73 min) ausgewertet: alle 14 Antworten gelesen, 6 richtig nach Handprüfung (RUN-012: 9); Ollama-Journal ausgewertet (28 Modellladungen)
**Gelieferte Dateien / Funktionen:** `src/audit_agent/agent/loop.py` (`seen_calls`, Nachfrage), `models.py`, `prompts.py` (`is_audit_question`), `scripts/analyze_timing.py`, `docs/adr/0015-repeat-guard-and-calculate-nudge.md`, `data/eval/run-013/`
**Entscheidungen:** ADR-0015 (vorgeschlagen): Sperre wirkt, Rechennachfrage bei `llama3.1:8b` ohne Wirkung; ein fester Prüfablauf im Code bleibt als offene Entscheidung; Prompt ohne Beispiele aus dem Testkatalog
**Probleme / Überraschungen:** ISS-060 (Stichwort-Erkennung grob, Nachfrage wirkungslos), ISS-061 (Antwort besteht aus Werkzeugaufruf als Text), ISS-062 (Rückschritte S2/S4/N2, Streuung unbekannt), ISS-063 (`calculate` mit erfundenen Argumenten), ISS-064 (zwei kleine eigene Fehler vor dem Commit); ISS-057 nur teilweise geklärt: meine erste Erklärung (Entladen je Frage) passte nicht zu RUN-010, ich habe sie vor dem Eintragen korrigiert
**Offen / unklar:** Streuung zwischen Läufen; ob `qwen2.5:7b` die Nachfrage befolgt; fester Prüfablauf ja oder nein; Laufzeit von RUN-010
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 2 h Sitzung, dazu Lauf ca. 1 h 15 min Rechenzeit · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(scripts)`, `feat(agent)`, `test(evaluation)`, `docs`

### 2026-11-16 – M6d: Gegenmaßnahmen für P2 (Suchwerkzeug, Filter, leere Suche)
**Ziel der Sitzung:** Die Werkzeugprobleme aus RUN-010/011 beheben (ISS-006/007/051/052) und mit einem P2-Lauf auf allen 14 Fragen messen.
**Was wurde gemacht:**
- `search_documents` und `search_tables` zu einem Werkzeug `search` zusammengeführt; Katalog und Metrik angepasst
- Modell filtert nur noch nach Sparte; `doc_type` und Jahr entfallen. Neuer Parameter `include_counterpart` holt bei Prüffragen Vertrag bzw. Rechnung nach
- Leere Suche wird nicht mehr ohne Filter wiederholt, sondern nennt den Bestand
- Prompts angepasst, Tests umgeschrieben und ergänzt (272 grün), `check_evidence.py` für reine P2-Läufe repariert
- RUN-012 (P2, 14 Fragen, 61 min) ausgewertet: alle 14 Antworten gelesen, 9 richtig nach Handprüfung (RUN-010: 3); Ursachen der 5 Fehlschläge zugeordnet
**Gelieferte Dateien / Funktionen:** `src/audit_agent/agent/tools.py` (`search`, `_counterpart_hits`, `_inventory`), `prompts.py`, `dataset/ground_truth.yaml`, `scripts/check_evidence.py`, `docs/adr/0014-search-tool-and-filter-policy.md`, `data/eval/run-012/`
**Entscheidungen:** ADR-0014 (ein Suchwerkzeug, Filter nur Sparte, keine Wiederholung ohne Filter); Variante B (Sparte bleibt) statt kein Filter, auf Claudes Vorschlag
**Probleme / Überraschungen:** ISS-058 (`calculate` wird nie aufgerufen, Abrechnungsfehler bleiben unerkannt), ISS-057 (Laufzeit fast verdoppelt bei gleicher Token-Zahl, Ursache offen), ISS-059 (eigener Fehler: Skript brach bei Läufen ohne B0 ab); beim ersten Umbau gingen `_outline` und `_calculate` durch einen zu weiten Schnitt verloren, die Tests meldeten es sofort
**Offen / unklar:** Streuung zwischen Läufen; welche der Maßnahmen wie viel bringt; Gegenprobe mit `qwen2.5:7b`; Laufzeitursache
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1 h Sitzung, dazu Lauf ca. 1 h Rechenzeit · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(agent)`, `docs`

### 2026-11-15 – M6c: Nachtläufe RUN-010/011 auswerten
**Ziel der Sitzung:** Die Nachtläufe mit beiden Modellen auswerten: jede falsche Antwort einer Ursache zuordnen, RAGAS-Stichproben von Hand prüfen, das Agent-Modell entscheiden.
**Was wurde gemacht:**
- Laufprüfung: beide Läufe vollständig (je 42 Antworten, 84 RAGAS-Zeilen), im Nachtlauf kein OOM und keine Kürzung
- Alle 84 Antworten gegen Ground Truth und Belegtexte gelesen; vier als richtig gezählte qwen-Antworten umgewertet, weil die Begründung nicht trägt
- Skript für den Belegabgleich geschrieben: standen die Sollfakten im Kontext des Modells? Damit lässt sich „Beleg kam nie an“ von „Beleg da, Antwort falsch“ trennen
- Fehleranalyse: 61 Fehlschläge mit je einer Hauptursache; P2 verliert die Belege meist schon bei Werkzeugwahl und Filter, P1 beim Retrieval, B0 am Kontextbudget
- RAGAS-Stichprobe mit 12 Antworten und Abgleich aller 48 Context-Recall-Werte gegen den Faktenabgleich
- ADR-0013 als Vorschlag geschrieben, vom Nutzer bestätigt
**Gelieferte Dateien / Funktionen:** `scripts/check_evidence.py`, `data/eval/run-010/`, `data/eval/run-011/` (mit `evidence.json`), `data/eval/night-m6b.log`, `data/eval/night-m6b-journal.txt`, `docs/adr/0013-agent-model-llama31.md`, Eintrag RUN-010/011 in `docs/evaluation-log.md`
**Entscheidungen:** ADR-0013 (Agent-Modell `llama3.1:8b`, Gegenprobe mit `qwen2.5:7b` nach den Gegenmaßnahmen); ADR-0004 verweist darauf. Rohdaten von RUN-011 bleiben unverändert (erfundene schlüsselähnliche Zeichenkette, ISS-054)
**Probleme / Überraschungen:** ISS-050 (Metrik zu großzügig bei „ja“), ISS-051 (Wiederholung ohne Filter liefert Ablenker), ISS-052 (`search_documents` findet keine Tabellenzeilen, ist aber das erwartete Werkzeug), ISS-053 (RAGAS im Einzelfall unzuverlässig), ISS-054 (qwen sagt immer „ja“, llama scheitert an `calculate`), ISS-055 (eigener Fehler: frühere Deutung zu P1 war falsch), ISS-056 (eigener Fehler: Commit vor vollständigem Gate); ISS-043 gelöst. Überrascht hat, dass der Agent schlechter abschneidet als die einfache Pipeline und dass der Parser an keinem Fehlschlag schuld ist
**Offen / unklar:** Wirkung der Gegenmaßnahmen (M6d); ob die Ursachenzuordnung einer zweiten Person standhält (nicht gegengelesen); Streuung zwischen Läufen ist nicht gemessen
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 0,5 h Sitzung, dazu Nachtlauf ca. 8,5 h Rechenzeit · **Modell/Effort:** Fable 5.2 · **Commit(s):** `test(evaluation)`, `feat(scripts)`, `docs` ×2

### 2026-11-15 – M6b-1: Prüffragen G3/G4 und RAGAS mit lokalem Bewerter
**Ziel der Sitzung:** Die Lücke ISS-040 schließen (E2/E3 ohne Prüffrage), RAGAS lokal an die gespeicherten Antworten anbinden und mit einem Probelauf prüfen, bevor die Nachtläufe mit beiden Modellen starten.
**Was wurde gemacht:**
- Plan mit fünf Punkten; M6b in M6b-1 (Code + Probelauf) und M6c (Nachtläufe + Auswertung) geteilt; Entscheidung: fester Bewerter `qwen2.5:7b`, nur Faithfulness und Context Recall
- Katalog um G3/G4 erweitert, Pflichtzuordnung Fehler ↔ Frage validiert; Vergleichsfilter für G3/G4 ergänzt
- Belegtexte je Antwort gespeichert; RAGAS 0.4.4 als eigene Abhängigkeitsgruppe, Modul `ragas_eval` mit Längenprüfung, Fehlerprotokoll, Fortsetzen und Report-Tabelle; Bewerter-Alias über Modelfile, weil die OpenAI-Schnittstelle von Ollama kein `num_ctx` je Anfrage nimmt
- Beim Lesen des RAGAS-Quelltexts Telemetrie entdeckt und abgeschaltet (ISS-044)
- RUN-009: Ablauf funktioniert, alle Varianten scheitern an G3/G4; `max_tokens` des Bewerters auf 2048 erhöht
- Nachtlauf am Mittag gestartet: RUN-010 nach ca. 1 h durch OOM-Kill in P2/Z3 beendet, Folgeschritte scheiterten sofort (ISS-043, ISS-049). Nachgebessert: Entladen nach jeder P1/P2-Frage und jeder bewerteten Antwort, Abbruch mitten in der Anfrage sauber abgefangen, `scripts/night_eval.sh` mit Warten und einer Wiederholung je Schritt
**Gelieferte Dateien / Funktionen:** `dataset/ground_truth.yaml` (G3, G4), `corpus/models.py` (`planted_error`), `evaluation/ragas_eval.py`, `evaluation/{models,variants,report,__main__}.py`, `config.py` (`judge`, `judge_num_ctx`, `judge_max_tokens`), `scripts/audit-judge.Modelfile`, `tests/test_ragas_eval.py`, `docs/adr/0012-ragas-local-judge.md`, `data/eval/run-009/`
**Entscheidungen:** ADR-0012 (RAGAS mit lokalem Bewerter); ADR-0011 Punkt 9 verweist darauf
**Probleme / Überraschungen:** ISS-040 gelöst; ISS-044 (Telemetrie), ISS-045 (Selbstbewertung qwen), ISS-046 (B0 nicht bewertbar), ISS-047 (Abbruch bei `max_tokens`, Context Recall 0, Faithfulness 1,00 trotz falscher Antwort), ISS-048 (eigener Fehler: Commit trotz rotem Gate), ISS-049 (eigener Fehler: Abbruch nicht abgefangen, Nachtbefehl ohne Wiederholung), ISS-043 wieder aufgetreten; überrascht hat, dass RAGAS eine sinnlose Rechnung als „treu“ bewertet, weil das Ergebnis in der Rechner-Beobachtung steht
**Offen / unklar:** Nachtläufe RUN-010/011; ob Context Recall 0 wirklich am fehlenden zweiten Dokument liegt (RAGAS gibt die Einzelurteile nicht aus); Stichproben der Bewerterurteile von Hand
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,5 h (davon Probelauf ca. 47 min) · **Modell/Effort:** Opus 5.5 · **Commit(s):** `feat(corpus)`, `feat(evaluation)` ×2, `fix(evaluation)` ×2, `feat(scripts)`, `docs` ×3

### 2026-11-14/15 – M6a: Testmodul-Grundlage (B0, P1-Synthese, Metriken)
**Ziel der Sitzung:** Das Testmodul bauen: Testset aus der Ground Truth, P1 mit Antwortsynthese und B0 als Volltext-Baseline neben dem Agenten, eigene Metriken und einen Lauf, der Antworten und Bewertung getrennt speichert; erster Probelauf mit 3 Fragen.
**Was wurde gemacht:**
- Plan mit sechs Punkten vorgelegt; B0-Variante A (Katalogreihenfolge bis zum Budget) gewählt
- Refactoring: gemeinsames Trefferformat, Chat-Argumente und Modellaufruf-Protokoll für Agent und Evaluation
- Paket `audit_agent.evaluation` mit Varianten, Metriken, Speicherung, Report und CLI; 28 neue Tests
- RUN-007: abgebrochen. Journal und Messskript zeigten: B0-Prompt real 8.424 statt geschätzt ca. 7.200 Token, Ollama kürzte still auf 4.096 (ISS-041); danach OOM-Kill (ISS-043); CLI fing den Abbruch nicht ab (ISS-042)
- Korrekturen: 2,4 Zeichen/Token, Entladen vor jeder Variante, Manifest zuerst, Lücke „keine Informationen“, Urteil auch aus dem letzten Satz
- RUN-008: stabil; B0 2/3, P1 1/3, P2 2/3 richtig; B0-Präfix-Cache belegt
**Gelieferte Dateien / Funktionen:** `src/audit_agent/evaluation/{models,testset,prompts,metrics,variants,store,report,__main__,__init__}.py`, `config.py` (`EvaluationSettings`), `scripts/probe_context.py`, `tests/test_evaluation.py`, `docs/adr/0011-evaluation-harness.md`, `data/eval/run-007/`, `data/eval/run-008/`
**Entscheidungen:** ADR-0011 (Aufbau des Testmoduls, B0 Variante A)
**Probleme / Überraschungen:** ISS-037 gelöst; ISS-038 (Metriken sind Heuristiken), ISS-039 (B0 sieht nur 6 Dateien), ISS-040 (Fehlererkennung nur E1), ISS-041 (stille Kürzung durch falsche Token-Schätzung), ISS-042 (eigener Fehler: Abbruch nicht abgefangen), ISS-043 (OOM-Kill); überrascht hat, dass Ollama zu lange Prompts ohne Fehlermeldung halbiert und nur das Journal es zeigt, und dass P1 trotz passender Treffer „keine Angaben“ antwortet
**Offen / unklar:** RAGAS mit lokalem Bewerter; E2/E3 als Fragen; ob `qwen2.5:7b` die Tool-Wahl verbessert; warum P1 bei vorhandenen Belegen aufgibt
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 2,5 h (davon Ollama-Läufe ca. 50 min) · **Modell/Effort:** Opus 5.5 · **Commit(s):** `refactor(agent)`, `feat(evaluation)`, `test(evaluation)`, `fix(evaluation)` ×2, `feat(scripts)`, `docs` ×4

### 2026-11-14 – M5: Agent (P2) mit Tools
**Ziel der Sitzung:** Auf dem Retriever aus M4 einen Agenten mit nativem Tool-Calling und den sechs Tools aus dem Konzept bauen, mit Protokoll je Schritt und Streamlit-Oberfläche für die Belege, und prüfen, ob er mit `llama3.1:8b` brauchbar antwortet.
**Was wurde gemacht:**
- Plan mit sieben Punkten vorgelegt und bestätigt (getrennte Such-Tools, kein `top_k`, Jahresfilter-Regel und Wiederholung ohne Filter im Code)
- Paket `audit_agent.agent`: Rechner über `ast` mit `Decimal`, sechs Tools mit pydantic-Argumenten und erzeugtem JSON-Schema, Schleife mit Limit, Kontextwächter und Belegnummern, JSON-Zeilen-Log, Report, CLI, Streamlit-Seite; `AgentSettings` in der Config; `streamlit` als Abhängigkeit
- 79 Tests mit Skript-Client und Fake-Suche; zwei eigene Fehler von den Tests gefunden (ISS-034)
- RUN-005: 1 von 4 richtig; Ursachen gefunden und behoben: Summaries als Beleg zitiert (ISS-035), Aufgeben nach einem Aufruf, Fehlermeldung ohne richtigen Aufruf, Kontextschätzung über `prompt_eval_count` unbrauchbar
- RUN-006: 2 von 4 richtig (S2, N1); G1 und S4 scheitern weiter an Tool-Wahl und Filtern (ISS-036). Danach bewusst keine weitere Prompt-Arbeit an denselben vier Fragen
- Beim Planen von M6 aufgefallen: P1 hat keine Antwortsynthese, B0 fehlt (ISS-037)
**Gelieferte Dateien / Funktionen:** `src/audit_agent/agent/{calculator,models,tools,prompts,loop,log,factory,report,evidence_view,app,__main__,__init__}.py`, `config.py` (`AgentSettings`), `tests/{agent_fakes,test_agent_tools,test_agent_loop}.py`, `docs/adr/0010-agent-loop-and-tools.md`, `docs/reverse-engineering/m5-agent.md`, `data/eval/run-005/`, `data/eval/run-006/`
**Entscheidungen:** ADR-0010 (Agentenschleife und Tools), ADR-0006 bestätigt (Aufrufformat bleibt)
**Probleme / Überraschungen:** ISS-030 (großer Prompt), ISS-031 (Kürzung), ISS-032 (Filterregeln als Heuristik), ISS-033 (keine Vertragslaufzeit), ISS-034 (eigene Fehler), ISS-035 (Summary als Beleg zitiert), ISS-036 (Modell gibt auf, wählt falsch), ISS-037 (P1-Synthese und B0 fehlen); überrascht hat, dass die Rückfrage bei „keine Angaben“ nur dieselbe Suche wiederholen ließ und dass `prompt_eval_count` nicht die Kontextgröße ist
**Offen / unklar:** Ob `qwen2.5:7b` oder ein gemeinsames Suchtool die Tool-Wahl verbessert (M6); ob die Summaries für den Agenten wieder eingeschaltet werden; Reverse-Engineering zu M2 bis M5 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,5 h (zwei Ollama-Läufe mit zusammen gut 25 min) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `build`, `feat(config)`, `feat(agent)`, `feat(ui)`, `test(agent)`, `fix(agent)`, `docs(adr)`, `docs` ×3, `docs: close M5 session`

### 2026-11-14 – M4: Embedding & Retrieval
**Ziel der Sitzung:** Aus den 629 Chunks einen ChromaDB-Index bauen und eine Suche mit Metadatenfilter und Hierarchie-Boost liefern, deren Score sich von Hand nachrechnen lässt; Wirkung von Filter, Boost und Chunk-Auswahl messen.
**Was wurde gemacht:**
- Plan mit sechs Punkten vorgelegt und bestätigt (kein Query-Rewriting in M4, Streamlit erst in M5)
- Paket `audit_agent.retrieval`: Index (Hierarchie-Präfix, Task-Präfixe, flache Metadaten, Neuaufbau je Lauf), Suche (Kandidaten, `where`-Filter, Pfadregel, Boost), Evidenz, Vergleichslauf, CLI; `RetrievalSettings` in der Config; `chromadb` als Abhängigkeit
- 39 Tests mit Fake-Embedder; dabei einen eigenen Fehler gefunden (Unterstrich als Wortzeichen, ISS-026)
- Index mit Ollama gebaut (86 s) und RUN-004 gefahren: Filter bringt 0 statt 4 Ablenker-Treffer und MRR 0,733 statt 0,683, der Boost ändert keinen Rang, Summaries helfen, Chunks ohne Kapitel stören nicht, S4 wird nicht gefunden
**Gelieferte Dateien / Funktionen:** `src/audit_agent/retrieval/{models,index,search,evidence,compare,__main__,__init__}.py`, `config.py` (`RetrievalSettings`), `tests/test_retrieval.py`, `docs/adr/0009-index-and-search-design.md`, `docs/reverse-engineering/m4-retrieval.md`, `data/eval/run-004/`
**Entscheidungen:** ADR-0009 (Aufbau von Index und Suche), ADR-0002 akzeptiert (Filter belegt, Boost ohne belegten Nutzen)
**Probleme / Überraschungen:** ISS-025 (Zeitraumfilter schließt Dokumente ohne Zeitraum aus), ISS-026 (eigener Fehler: Regex-Wortzeichen), ISS-027 (Boost greift fast überall), ISS-028 (Vergleich mit handgesetzten Filtern), ISS-029 (S4 nicht gefunden); im Plan stand 542 statt 547 Chunks, ein Rechenfehler von mir; überrascht hat, dass der Boost keinen Rang ändert, obwohl er fast jeden Treffer erreicht
**Offen / unklar:** Ob der Boost bleibt (ISS-027); wie oft der Agent falsche Filter setzt (ISS-028); Rang des S4-Bild-Chunks außerhalb der Top-5 unbekannt; Reverse-Engineering zu M2, M3 und M4 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,2 h (Ollama-Lauf unter 2 min) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `build`, `feat(config)`, `feat(retrieval)`, `test(retrieval)`, `docs(adr)`, `docs` ×3, `docs: close M4 session`

### 2026-11-14 – M3: Enrichment & Cache
**Ziel der Sitzung:** Die fünf Diagramme beschreiben (Caption) und jede der 65 Tabellen zusammenfassen (`table_summary`), mit einem Cache, damit die langsame Anreicherung nur einmal läuft.
**Was wurde gemacht:**
- Plan mit Prompts, Cache-Schlüssel und Phasenreihenfolge vorgelegt und bestätigt
- Paket `audit_agent.enrichment`: Cache, Captioner, Summarizer, Zahlenprüfung, Pipeline, CLI; `numbers.py` aus dem Smoke-Test herausgelöst; Chunk-Typ `table_summary` und `EnrichmentSettings`
- RUN-002 (erster Lauf, 26 min) gegen die PNGs und Tabellen geprüft: ein Diagramm mit erfundenen Zahlen, 21 abgeschnittene und mehrere inhaltlich falsche Summaries
- Prompts und Limits angepasst, Abschneiden im Report markiert, Zahlenprüfung um Datumsteile erweitert; RUN-003 (26 min): nichts mehr abgeschnitten, keine erfundenen Caption-Zahlen, aber weiter Fehler bei Preistabellen und Briefkopf-Tabellen
- 24 Tests mit Ollama-Fake, Reverse-Engineering-Notiz M3 (Abschnitte 1–4)
**Gelieferte Dateien / Funktionen:** `src/audit_agent/enrichment/{cache,llm,prompts,captioner,summarizer,checks,pipeline,__main__,__init__}.py`, `src/audit_agent/numbers.py`, `config.py` (`EnrichmentSettings`), `ingestion/models.py` (`TABLE_SUMMARY`), `tests/test_enrichment.py`, `docs/adr/0008-enrichment-and-cache.md`, `docs/reverse-engineering/m3-enrichment.md`, `data/eval/run-002/`, `data/eval/run-003/`
**Entscheidungen:** ADR-0008 (Enrichment als eigener Schritt, Prompt-Text im Cache-Schlüssel, Summaries nur als Suchhilfe)
**Probleme / Überraschungen:** ISS-021 (Ingestion überschreibt Enrichment), ISS-022 (Zahlenprüfung nur Teilcheck), ISS-023 (Caption erfindet Werte ohne Beschriftung), ISS-024 (abgeschnittene Summaries, eigener Fehler: `done_reason` nicht ausgewertet); der erste Lauf hat erst durch die Sichtprüfung gezeigt, dass die Ergebnisse schlechter waren, als der Report vermuten ließ
**Offen / unklar:** Wirkung der Summaries und Briefkopf-Chunks aufs Retrieval (M4); Reverse-Engineering zu M0 bis M3 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. 1,3 h (davon 2 × 26 min Ollama-Lauf, parallel zur Doku) · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `refactor(numbers)`, `feat(ingestion)`, `feat(enrichment)`, `fix(enrichment)`, `docs: …` ×3, `docs(reverse-engineering)`

### 2026-11-14 – M2: Parser & JSON-Zwischenformat
**Ziel der Sitzung:** Alle 30 PDFs in typisierte Chunks mit Metadaten umwandeln und als JSON-Zwischenformat unter `data/processed/` speichern.
**Was wurde gemacht:**
- Zuerst alle PDFs mit PyMuPDF untersucht (Tabellen je Strategie, Schriftgrößen, Bilder, Fußzeilen) und den Plan darauf abgestimmt
- Paket `audit_agent.ingestion`: Modelle, `DocumentParser`, Pipeline, CLI; `ParserSettings` in der zentralen Config
- Auf den echten PDFs drei Parser-Fehler gefunden und behoben: unvollständige Tabellen je Strategie (ISS-012), zerrissener Zelltext (ISS-013), verschmolzene Tabellen (ISS-014)
- 19 Parser-Tests (synthetische PDFs plus Golden-Checks auf Dok. 04, 10, 16, 29, 30) und 8 Tests für Modelle und Pipeline
- Doku: ADR-0007, ISS-012 bis ISS-020, RUN-001, Glossar, README, concept.md, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `src/audit_agent/ingestion/{models,parser,pipeline,__main__,__init__}.py`, `config.py` (`ParserSettings`), `tests/test_ingestion_*.py`, `docs/adr/0007-parser-heuristics.md`, `docs/reverse-engineering/m2-parser.md`
**Entscheidungen:** ADR-0007 (Parser-Heuristiken); Abweichung von der Vorlage: kurze Reste mit Ziffer bleiben erhalten (ISS-017)
**Probleme / Überraschungen:** ISS-012 bis ISS-020; die Unit-Tests allein hätten die Tabellenfehler nicht gefunden, erst der Blick in die echten JSON-Zeilen
**Offen / unklar:** Wirkung der Briefkopf-Chunks aufs Retrieval (M4); Reverse-Engineering zu M0, M1, M2 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, ISS-087)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / High · **Commit(s):** `feat(ingestion)` ×3, `refactor(ingestion)`, `docs: …M2`

### 2026-11-14 – M1: Metadaten & Ground Truth
**Ziel der Sitzung:** Metadaten und Ground Truth des Korpus als validierte Dateien bereitstellen und zwei weitere fehlerhafte Dokumente ergänzen.
**Was wurde gemacht:**
- Paket `audit_agent.corpus` mit Pydantic-Modellen und Loader (Fail Fast, `extra="forbid"`, Konsistenzprüfungen)
- `dataset/documents.yaml` für alle 30 PDFs, `dataset/ground_truth.yaml` mit 12 Fragen, 3 eingebauten Fehlern und 10 Prüfurteilen
- Zwei fehlerhafte Dokumente (29 Gas 2026: falsche z-Zahl, 30 Betriebskosten 2026: falsche Wohnfläche) per `scripts/generate_error_documents.py` mit WeasyPrint erzeugt und visuell geprüft
- 17 Tests ohne LLM (inklusive Prüfung, dass die Fehlerwerte im PDF-Text stehen); Quality Gate grün (57 Tests)
- Doku: Konzept 4.3 und 5.2, ADR-0005, Issues, Glossar, README, Reverse-Engineering-Notiz
**Gelieferte Dateien / Funktionen:** `src/audit_agent/corpus/{models,loader}.py`, `dataset/{documents,ground_truth}.yaml`, PDFs 29 und 30, `tests/test_corpus.py`
**Entscheidungen:** Neue Sparten `telecom`, `insurance` und Dokumentarten `payment_plan`, `handover_protocol` im Metadatenschema; Fehlerdokumente für 2026 statt Duplikate (ISS-010)
**Probleme / Überraschungen:** ISS-010 (Zusatzdokumente anders als Originale, nur 3 Fehler), ISS-011 (Löschrecht für git zu spät angefragt)
**Offen / unklar:** Reverse-Engineering-Fragen zu M1 mit Antworten in `m1-fragen-und-antworten.md` hinterlegt (Nutzer hatte keine Zeit), Erklär-Test steht aus. Die erwarteten Urteile „korrekt“ für 08, 13, 15, 18, 19 stützen sich auf die Korpus-Prüfung vom Projektstart; Reverse-Engineering-Fragen zu M0 und M1 unbeantwortet
**O-Ton (von mir):** (nicht geliefert, Nutzer hatte keine Zeit)
**Zeitaufwand:** ca. … h · **Modell/Effort:** Sonnet 5.5 / Medium · **Commit(s):** `feat(dataset)`, `feat(corpus)`, `docs: …M1`

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
