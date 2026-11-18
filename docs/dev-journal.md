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
