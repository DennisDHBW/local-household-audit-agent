# M9 – Plan: Agent v3 „Verstehen – Ausführen – Prüfen“

**Stand:** 2026-11-21 · **Status:** Vorschlag, wartet auf Freigabe durch den Nutzer · **Bezug:** RUN-028, ISS-108, ISS-110 bis ISS-112, ISS-125 bis ISS-128, ADR-0022 (vorgeschlagen)

> Ziel von M9 ist eine deutlich bessere Qualität durch eine andere Architektur, nicht durch weitere Regeln. Gemessen wird auf Fragen, an denen nicht entwickelt wurde.

---

## 1. Ausgangslage

P2 (Agent v2) erreicht auf den zurückgehaltenen Fragen T1–T8 nach Handprüfung 50 % (mit Grenzfällen 75 %), auf den Entwicklungsfragen 76 %. Alle drei Ausfälle (T3, T5, T6) kommen aus Regeln, die an den Entwicklungsfragen gebaut wurden. Wo das passende Werkzeug lief (T2, T4, T8), stimmte die Antwort; kein Ausfall geht auf Retrieval oder Faktenspeicher zurück. Das Problem liegt in der **Steuerung**.

### Strukturelle Ursachen

| # | Ursache | Sichtbar in |
|---|---|---|
| U1 | Ein Modellaufruf soll gleichzeitig verstehen, Werkzeug wählen, Argumente bilden und formulieren; der Verlauf wächst mit jedem Schritt | 4,2 Modellaufrufe je Frage, 10 Rückfragen in 8 Fragen (run-028) |
| U2 | Steuerentscheidungen hängen an Wortlisten im Code (`AUDIT_PHRASES`, `CHART_PHRASES`, `OVERVIEW_PHRASES`, `route_tools`) | T3, T6: „berechnet“, „in Ordnung“ nicht erkannt, `check_bill` 0-mal |
| U3 | Die Ausgabe des Modells ist frei: Text, Werkzeugaufruf oder nichts; Belegnummern und Zahlen schreibt das Modell selbst | leere Antworten T3/T5/T6, „[2024]“ in T8, erfundene [1]/[2] in T6 |
| U4 | Selbstkorrektur über Rückfragen ohne konkrete Rückmeldung von außen | Lücken-Rückfrage 1 von 4-mal hilfreich |
| U5 | Jede neue Fehlerform braucht eine neue Regel, und die Regeln greifen ineinander | ISS-125 (engere Prüfung bricht eine andere), ISS-127 (Reparatur kennt nur `year`) |
| U6 | Das Prefill dominiert (73 % der Zeit); der erste Aufruf jeder Frage braucht 79–97 s für ca. 1.670 Token, der Präfix-Cache greift zwischen den Fragen nicht | Schrittprotokolle run-028, ISS-128 |
| U7 | Die Messung trägt wenig: 8 Fragen (eine Frage = 12,5 Prozentpunkte), Fragen und Regeln vom selben Autor | ISS-108, ISS-112 |

---

## 2. Was die Literatur dazu sagt

| Befund im Projekt | Literatur | Folgerung für M9 |
|---|---|---|
| U1: alles in einem wachsenden Gespräch | ReWOO (Xu et al. 2023) trennt Planer, Ausführer und Löser; Beobachtungen fließen nicht in jeden Denkschritt zurück, das spart Token und ist robuster bei Werkzeugfehlern. α-UMi (Shen et al., EMNLP 2024): kleine Modelle sind schwache Werkzeugnutzer, eine Aufteilung in Planer, Aufrufer und Zusammenfasser hilft. StateFlow (Wu et al., COLM 2024): Ablauf als Zustandsautomat, Übergänge durch Regeln oder Modellentscheidungen; höhere Erfolgsquote als ReAct bei weniger Kosten | Getrennte Rollen mit je eigenem, kurzem Aufruf; expliziter Zustandsautomat statt offener Schleife |
| U2: Wortlisten | Rabinovich und Anaby-Tavor (TrustNLP 2025): bei umformulierten Anfragen sinkt die gemessene Genauigkeit um 8–19 %, laut den Autoren aber zu 70–90 % wegen starrer Bewertung der Parameterwerte, nicht wegen der Modelle; zusätzliche ähnliche Werkzeuge kosten 1–8 %. Paramanayakam et al. (DATE 2025): weniger angebotene Werkzeuge verbessern kleine Modelle auf Edge-Hardware | Starrer Wortabgleich ist die Schwachstelle, nicht das Sprachverständnis des Modells: das Modell ordnet die Frage einem festen Schema zu (wenige Optionen je Entscheidung), der Code sucht keine Wörter mehr; Umformulierungen werden eigens gemessen und auf der Ebene der Schema-Werte verglichen, nicht als Text |
| U3: freie Ausgaben | JSONSchemaBench (Geng et al. 2025): eingeschränkte Dekodierung (constrained decoding) mit JSON-Schema ist Standard. Chavan (arXiv 2609.23742, 2026): bei Modellen von 0,6B bis 4B beseitigt sie Strukturfehler vollständig, Inhaltsfehler aber nicht. Ollama unterstützt JSON-Schemas über `format` | Jede Modellausgabe hat ein JSON-Schema; Belegnummern sind ein `enum` der vorhandenen Belege, erfundene Nummern sind damit unmöglich |
| U3: Format kostet Denkleistung | Tam et al. (EMNLP Industry 2024): Formatvorgaben verschlechtern Schlussfolgern, je strenger, desto mehr | Kein Rechnen und Prüfen im JSON; das macht der Code. Schemas flach halten |
| U4: Rückfragen ohne Rückmeldung | Huang et al. (ICLR 2024, schon in `sources.md`): ohne externe Rückmeldung kaum Selbstkorrektur. CRITIC (Gou et al., ICLR 2024): Korrektur mit Rückmeldung aus Werkzeugen wirkt. CRAG (Yan et al. 2024): ein Prüfschritt bewertet die abgerufenen Belege als richtig, unklar oder falsch und löst je nachdem eine andere Aktion aus | Der Code prüft Evidenz und Antwort deterministisch und gibt dem Modell nur bei einem konkreten Befund eine zweite Chance |
| U3/U4: erfundene Belege | ALCE (Gao et al., EMNLP 2023): Zitierqualität als eigene Messgröße; selbst gute Modelle belegen ihre Aussagen oft nicht vollständig | Belege per Konstruktion: Satz → Beleg-IDs, Zahlen gegen die zitierten Belege geprüft, Verweise setzt der Code |
| Gewinn kommt aus dem Code (ISS-110) | Binder (Cheng et al., ICLR 2023): Frage → ausführbares Programm, das Modell parst, die Ausführung ist symbolisch. Yang et al. (arXiv 2610.19474, 2026): vom Modell erzeugte Spezifikationen plus deterministische Ausführung verbessern Aggregationsfragen deutlich | Faktenspeicher und `check_bill` bleiben; das Modell liefert nur noch die Spezifikation (Auftragsrahmen) |
| Workflow oder Agent | Anthropic, „Building effective agents“ (2024): Workflows mit festen Code-Pfaden sind für klar umrissene Aufgaben berechenbarer; Muster Routing und Evaluator-Optimizer. Ferrazzi et al. (ACL 2026, zitiert): Agentic RAG ist nicht generell besser und deutlich teurer | Agentisch bleibt, wo das Modell wirklich entscheidet (Auftrag, Plan, Neuplanung, Formulierung); fest ist, was berechenbar ist |
| Dokumente sind fremde Eingaben | Beurer-Kellner et al. (2025): Plan-then-Execute verhindert, dass Werkzeugausgaben die Wahl der Aktionen beeinflussen (Schutz gegen Prompt Injection) | Zusatznutzen für Kapitel 3: Inhalte einer Rechnung können den Ablauf nicht umsteuern |
| Beispiele im Prompt | Liu et al. (DeeLIO 2022, KATE): Beispiele nach semantischer Ähnlichkeit auswählen schlägt Zufallsauswahl | Optional: Beispiele für den Auftragsrahmen per Embedding wählen (nomic ist ohnehin geladen); gegen feste Beispiele messen (Cache!) |
| U7: kleine, eigene Testmenge | Miller (2024): Konfidenzintervalle und gepaarte Vergleiche je Frage. Kapoor et al. (2024, schon in `sources.md`): zurückgehaltene Daten, Kosten mitberichten. Metamorphes Testen (z. B. arXiv 2603.13173, 2026): gleiche Bedeutung, gleiche Antwort | Neuer zurückgehaltener Satz von einem anderen Autor, Umformulierungen je Frage, Intervalle und gepaarter Vergleich, Ziele vor dem Lauf festlegen |

---

## 3. Zielarchitektur P3

**Grundidee:** Das Modell trifft die Entscheidungen, jeweils in einem kurzen Aufruf mit festem JSON-Schema. Der Code führt aus, rechnet, prüft und setzt die Antwort zusammen.

```
Frage (+ Auftragsrahmen der Vorfrage bei Folgefragen)
  │
  ▼
[1] VERSTEHEN & PLANEN      Modell, Schema QueryFrame
  │                         Teilaufgaben (1–3): Absicht, Sparte, Tarif, Zeitraum, Größe, Darstellung; Suchanfrage
  │                         Code: Schema-Prüfung, Zeitraum auflösen („aktuell“, „letzte Jahre“, „seit 2024“)
  ▼
[2] AUSFÜHREN               Code, Skills: lookup_facts, check_bill, overview, chart, search_text, list_documents
  │                         → Belege E1…En (Wert, Quelle, Zeitraum)
  ▼
[3] EVIDENZ PRÜFEN          Code: vollständig | lückenhaft | leer, mit konkretem Grund
  │   lückenhaft/leer, Runde < 2 → [3a] NEU PLANEN: Modell, Schema ReplanDecision
  │                                 {andere Suche | anderer Zeitraum | andere Sparte | aufgeben} → zurück zu [2]
  ▼
[4] FORMULIEREN             Modell, Schema AnswerDraft
  │                         Antworttyp, Urteil, Sätze mit Beleg-IDs ∈ {E1…En} (enum, je Frage erzeugt)
  ▼
[5] VERIFIZIEREN            Code: Zahlen ⊂ zitierte Belege, Urteil = Ergebnis von check_bill,
  │                         jede Aussage belegt oder als Lücke markiert
  │   Verstoß → einmal zurück zu [4] mit dem Befund, sonst Rückfall
  ▼
[6] AUSGEBEN                Code: Text mit [n]-Verweisen, Tabelle/Grafik aus [2]
                            Rückfall: Vorlagenantwort aus den Belegen oder Standard-Lückensatz
```

### Wer entscheidet was

| Entscheidung | Modell | Code |
|---|---|---|
| Was ist gefragt (Absicht, Sparte, Tarif, Zeitraum, Größe, Darstellung) | ✓ (Schema mit `enum`) | prüft das Schema, löst relative Zeitangaben auf |
| Welche Schritte in welcher Reihenfolge | ✓ (Teilaufgaben) | ordnet jeder Absicht genau einen Skill zu |
| Werte nachschlagen, Rechnung prüfen, Tabelle/Grafik bauen, Volltextsuche | – | ✓ (bestehender Faktenspeicher, `check_bill`, `views`, `chart`, Suche) |
| Reicht die Evidenz? | – | ✓ (vollständig/lückenhaft/leer) |
| Was tun, wenn nicht | ✓ (Neuplanung, höchstens 2 Runden) | gibt den Grund vor, begrenzt die Runden |
| Formulierung der Antwort | ✓ (Sätze + Beleg-IDs) | – |
| Stimmen Zahlen, Urteil und Belege | – | ✓ (Verifikation), eine Korrekturrunde mit konkretem Befund |
| Belegnummern, Formatierung, Anhänge | – | ✓ (Renderer) |

### Schemas (Entwurf, wird in M9a festgelegt)

```python
class Intent(StrEnum):  # Was soll getan werden?
    FACT = "fact"  # Wert nachschlagen (Preis, Abschlag, Verbrauch, …)
    CHECK = "check"  # Rechnung/Bescheid prüfen
    OVERVIEW = "overview"  # Tabelle
    CHART = "chart"  # Grafik
    CLAUSE = "clause"  # Vertragstext (Frist, Laufzeit, Bedingungen)
    OTHER = "other"  # sonst: Volltextsuche


class Period(StrEnum):
    YEARS = "years"
    LATEST = "latest"
    ALL = "all"
    SINCE = "since"
    NONE = "none"


class SubTask(BaseModel):
    intent: Intent
    utility: UtilityType | None  # alle Sparten des Korpus inkl. Fernwärme, Telekom, Versicherung
    tariff_kind: TariffKind | None
    period: Period
    years: list[int]  # nur bei YEARS/SINCE
    metric: FactName | None
    doc_type: DocType | None


class QueryFrame(BaseModel):
    tasks: list[SubTask]  # 1–3
    search_query: str  # Stichworte für die Volltextsuche
    is_follow_up: bool  # „und jetzt als Grafik?“ übernimmt fehlende Felder der Vorfrage


class Sentence(BaseModel):
    text: str
    evidence: list[EvidenceId]  # enum, je Frage aus E1…En erzeugt; leer nur bei Lückensätzen


class AnswerDraft(BaseModel):
    kind: Literal["answer", "partial", "no_data"]
    verdict: Literal["ok", "deviation", "not_checkable", "none"]
    sentences: list[Sentence]
```

Das Negativ-Verhalten folgt aus den Daten, nicht aus Wörtern: Fragt jemand nach Fernwärme, ist `utility = district_heating` ein gültiger Wert; der Skill findet keine Dokumente, die Evidenz ist leer, die Antwort ist der Lückensatz.

### Was wegfällt (P2 v2 bleibt eingefroren als Vergleichsvariante)

- Wortlisten und Routing: `AUDIT_PHRASES`, `CHART_PHRASES`, `OVERVIEW_PHRASES`, `route_tools`, `question_scope`, `repair_utility_arguments`
- Rückfrage-Maschinerie: Lücken-, Leer-, Schritt-, Zitat-, Rechen- und Plan-Rückfragen, `answer_now`, `parse_text_call`
- Text-Nachbearbeitung: `strip_step_talk`, `drop_trailing_gap`, `is_gap_answer`, `needs_citation`
- Abhängigkeit vom nativen Tool-Calling-Template des Modells (Ollama-Fehler bei neueren Modellen, siehe Abschnitt 4)

### Was bleibt

Parser, Enrichment, Index und Suche (M2–M4), Faktenspeicher und `check_bill` (ADR-0018), `views` und `chart`, Testmodul, Varianten B0 und P1, P2 v2 als Vergleich, Streamlit-Oberfläche (bekommt P3).

### Code-Struktur (Vorschlag)

`src/audit_agent/orchestrator/` mit `frame.py` (Schema, Prompt, Zeitraum-Auflösung), `skills.py`, `evidence.py`, `writer.py`, `verify.py`, `render.py`, `run.py` (Zustandsautomat, Protokoll je Zustand). Variante `P3` im Testmodul.

---

## 4. Modellwahl

Regel bleibt: höchstens 8B, Q4, Ollama-Limit 9 GB, zwei geladene Modelle (LLM + nomic-embed-text). Da P3 nur `format` (JSON-Schema) und kein natives Tool-Calling braucht, lässt sich das Modell leicht tauschen.

| Kandidat | Warum | Bekannte Risiken |
|---|---|---|
| `qwen2.5:7b` | heutiges Modell, Vergleichbarkeit | – |
| `qwen3:8b` (ohne Thinking) | Nachfolger, gleiche Größenklasse | Thinking muss sicher aus sein |
| `qwen3.5:4b` (ohne Thinking) | neue Generation, Hybrid-Architektur, halbe Größe → schneller | Ollama hatte bei Qwen3.5 Fehler im Tool-Calling-Template (Issue #14493) und ignorierte `format` bei abgeschaltetem Thinking (Issue #14645); auf der installierten Version prüfen |
| `granite4:tiny-h` | 7B gesamt, 1B aktiv (MoE + Mamba-2), für schnelle Agenten-Schritte gebaut | neue Architektur, Geschwindigkeit auf dieser CPU unbekannt |

`qwen3.5:9b` scheidet wegen der 8B-Regel aus. Entscheidung: Machbarkeitsprobe M9-0 (Schema-Treue, Geschwindigkeit, Cache), danach höchstens zwei Modelle im Entwicklungslauf.

---

## 5. Laufzeit (Schätzung, wird gemessen)

| Schritt | Annahme | qwen2.5:7b, Cache greift | ohne Cache |
|---|---|---|---|
| [1] Verstehen | fester Präfix ca. 1.200 Token, Frage ca. 60 Token, Ausgabe ca. 80 Token | ca. 20 s | ca. 80 s |
| [2]–[3] Ausführen, Prüfen | Code, Suche mit Embedding | ca. 2 s | ca. 2 s |
| [4] Formulieren | Belege 400–1.200 Token, Ausgabe 80–200 Token | 40–100 s | 50–110 s |
| [3a]/[5] Zusatzrunden | nur bei Befund | 0–60 s | 0–60 s |
| **Summe je Frage** | | **ca. 60–180 s** | **ca. 130–250 s** |

Zum Vergleich P2 v2: 195 s (run-028). Ein 4B-Modell wäre schneller; das misst M9-0. ISS-128 (Cache greift zwischen Fragen nicht) wird in M9-0 untersucht, weil es pro Frage rund 80 s kostet.

---

## 6. Evaluation neu

**Fragesätze**

| Satz | Zweck | Regel |
|---|---|---|
| Entwicklung (21 Fragen) | entwickeln, Fehler suchen | wie bisher |
| Umformulierungen der Entwicklungsfragen (2 je Frage, von Claude) | Robustheit gegen Wortlaut | nur zur Entwicklung |
| T1–T8 | Vergleich mit run-028 | an T1–T8 wird nicht entwickelt |
| **H2 (neu, 20–24 Fragen)** | Endmessung | **schreibt Dennis** in eigenen Worten nach Vorgabe der Mischung; Datei wird mit Hash versiegelt; Claude ergänzt die erwarteten Antworten erst nach dem Code-Freeze |

Mischung für H2 (Vorschlag): 6 Wertfragen, 5 Prüffragen (davon 2 mit eingebautem Fehler), 3 Übersichten/Grafiken, 3 Vertragsfragen, 3 Negativfragen, 2–4 Folgefragen oder Mehrfachfragen. Erfüllt die Vorgabe 5 Standard / 2 Grenzfall / 2 Negativ.

**Neue Kennzahlen:** Genauigkeit des Auftragsrahmens (Absicht, Sparte, Zeitraum gegen Gold), Konsistenz über Umformulierungen, erfundene Belegnummern (Ziel 0), Urteil ohne Prüfergebnis (Ziel 0), richtige und falsche Enthaltungen, Sekunden und Modellaufrufe je Frage. Alle Quoten mit 95-%-Wilson-Intervall, P3 gegen P2 gepaart je Frage (exakter McNemar-Test).

**Ziele, vor dem Lauf festgelegt (keine Versprechen):**

1. P3 auf H2 nach Handprüfung besser als P2 v2 auf H2 (gepaart, mit Intervall berichtet)
2. Abstand Entwicklung → H2 bei P3 höchstens 15 Prozentpunkte (P2 v2: 26)
3. Konsistenz über Umformulierungen mindestens 85 %
4. 0 erfundene Belegnummern, 0 Urteile ohne Prüfergebnis
5. Mittlere Zeit je Frage höchstens 195 s

**Grenze der Aussagekraft:** Bei 24 Fragen und einer Quote um 50 % ist das 95-%-Intervall etwa ±20 Prozentpunkte breit. Nur große Unterschiede sind belegbar; das steht so in der Ausarbeitung.

**Stoppregel:** genau eine Umbau-Runde, höchstens eine Nachbesserung für **Fehlerklassen** (keine Sonderregel für eine einzelne Frage, jede Änderung mit Begründung im issues-log), dann Code-Freeze, Endlauf auf H2. Das Ergebnis geht unverändert in die Ausarbeitung.

---

## 7. Arbeitspakete

| Paket | Inhalt | Modell / Effort | Dein Anteil | Ollama-Zeit |
|---|---|---|---|---|
| M9-0 Machbarkeitsprobe | Skript: je Kandidat Schema-Treue mit `format` und ohne Thinking, Geschwindigkeit, Cache-Probe (zwei Fragen mit gleichem Präfix), 8 neutrale Testfragen für den Auftragsrahmen; dazu ein Aufruf zur Klärung der leeren Antworten (ISS-126) | Sonnet 5.5 / High | Modelle laden (je 2–5 GB), einen Befehl starten | ca. 30–45 min |
| M9a Verstehen & Ausführen | `QueryFrame`, Zeitraum-Auflösung, Skills, Belege, Evidenzprüfung, Neuplanung; Unit-Tests mit aufgezeichneten Modellantworten | Opus 5.5 / High | – | – |
| M9b Formulieren & Verifizieren | `AnswerDraft` mit Beleg-`enum`, Verifikation, Renderer, Rückfall, Zustandsautomat, Protokoll; Streamlit auf P3 | Opus 5.5 / High | – | Smoke-Test ca. 15 min |
| M9c Testmodul | Variante P3, Umformulierungen, neue Kennzahlen, Wilson und McNemar, Nachtlauf-Skript; H2-Vorlage | Sonnet 5.5 / High | H2-Fragen schreiben (ca. 30 min, kann parallel) | – |
| M9d Entwicklungslauf | P3 mit 2 Modellen auf 21 + 42 Fragen, Auswertung, Modellentscheidung | Opus 5.5 / High | Nachtlauf starten | ca. 3–4 h (Nacht) |
| M9e Nachbesserung (optional) | nur Fehlerklassen aus M9d, Kontrolllauf | Opus 5.5 / High | Befehl starten | ca. 2 h |
| M9f Endlauf H2 | Code-Freeze, erwartete Antworten für H2, Lauf B0/P1/P2 v2/P3 auf H2 und T1–T8, Handprüfung | Opus 5.5 / High | Nachtlauf starten | ca. 3–4 h (Nacht; B0/P1/P2 v2 nur auf H2, weil sich ihr Code nicht ändert) |
| M9g Abschluss | Abgleich `requirements.md`, ADRs, Reverse Engineering M8 + M9, Tag v3.0.0 | Sonnet 5.5 / High | Verständnisfragen | – |

**Summe:** 7–8 Sitzungen, 9–11 h Ollama-Laufzeit (überwiegend nachts), beim bisherigen Tempo 3–4 Tage. Danach Ausarbeitung.

---

## 8. Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Das kleine Modell ordnet Fragen falsch zu (Absicht, Zeitraum) | eigene Kennzahl „Rahmen-Genauigkeit“; Beispiele im Prompt, die nicht aus den Testsätzen stammen; Absicht `other` führt zur Volltextsuche statt zu nichts |
| Formatvorgaben schwächen das Modell (Tam et al.) | flache Schemas, kein Rechnen im JSON, Rechnen und Prüfen im Code |
| Ollama-Fehler mit `format` oder Thinking bei neuen Modellen | M9-0 prüft das vor jeder Zeile Code; `qwen2.5:7b` bleibt als sichere Wahl |
| Kritik „das ist kein Agent mehr“ | Das Modell plant, plant neu und formuliert; Muster aus der Literatur (ReWOO, StateFlow, Plan-then-Execute) werden in Kapitel 3 benannt; P2 v2 (ReAct-Variante) bleibt als Vergleich |
| Gewinn wieder nur aus Code und Faktenspeicher (ISS-110) | bleibt so und wird offen berichtet; neu ist, dass die **Steuerung** nicht mehr an Wortlisten hängt |
| H2 wird doch an die Regeln angepasst (ISS-108) | Fragen von Dennis, versiegelt per Hash, Gold-Antworten erst nach Code-Freeze |
| Aufwand höher als geschätzt | Stoppregel; M9e entfällt, wenn M9d reicht |

---

## 9. Verworfene Alternativen

| Alternative | Warum nicht |
|---|---|
| Weitere Regeln an v2 (Wortlisten erweitern, Reparaturen ergänzen) | genau das hat die Lücke Entwicklung → zurückgehalten verursacht (U5) |
| Größeres Modell (z. B. `qwen3.5:9b`) | verletzt die 8B-Regel; Prefill auf der CPU noch langsamer |
| Feinabstimmung (LoRA) eines kleinen Modells für Planung | auf der CPU nicht machbar; Trainingsdaten wären wieder vom selben Autor |
| Self-Consistency (mehrere Pläne ziehen und abstimmen) | Kosten × N bei 18 Token/s Prefill |
| Zweites LLM als Richter für die Antwort | ohne externe Rückmeldung wenig wirksam (Huang et al.); deterministische Prüfungen sind billiger und genauer |
| LLM-gestützte Faktenextraktion beim Einlesen (gegen ISS-111) | sinnvoll für neue Layouts, im festen Korpus aber nicht messbar; Ausblick in der Ausarbeitung |
| Reranker, GraphRAG | kein Ausfall in run-028 geht auf das Retrieval zurück; GraphRAG siehe ADR-0003 |

---

## 10. Entscheidungen, die Dennis treffen muss

1. **H2-Fragen:** selbst schreiben (empfohlen, ca. 30 min, verringert ISS-112) oder Claude schreibt sie jetzt versiegelt
2. **Modelle laden:** `qwen3:8b`, `qwen3.5:4b`, `granite4:tiny-h` für M9-0 (zusammen ca. 12–14 GB Download und Plattenplatz)
3. **P2 v2 im Endlauf:** mitlaufen lassen (empfohlen, ca. 80 min mehr in der Nacht) für den gepaarten Vergleich

---

## 11. Quellen (für den Plan; die Ausarbeitung bleibt bei höchstens fünf)

- Xu et al. 2023, ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models, arXiv 2305.18323
- Shen et al. 2024, Small LLMs Are Weak Tool Learners: A Multi-LLM Agent, EMNLP 2024, arXiv 2401.07324
- Wu et al. 2024, StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows, COLM 2024, arXiv 2403.11322
- Rabinovich und Anaby-Tavor 2025, On the Robustness of Agentic Function Calling, TrustNLP@NAACL 2025, arXiv 2504.00914
- Paramanayakam et al. 2024, Less is More: Optimizing Function Calling for LLM Execution on Edge Devices, DATE 2025, arXiv 2411.15399
- Geng et al. 2025, JSONSchemaBench, arXiv 2501.10868
- Chavan 2026, Constrained Decoding Eliminates Structural Failures in Small LLMs but Reveals a Scale-Dependent Semantic Gap, arXiv 2609.23742 (Preprint, Einzelautor)
- Tam et al. 2024, Let Me Speak Freely?, EMNLP 2024 Industry, arXiv 2408.02442
- Gou et al. 2024, CRITIC, ICLR 2024, arXiv 2305.11738
- Yan et al. 2024, Corrective Retrieval Augmented Generation, arXiv 2401.15884
- Gao, Yen, Yu, Chen 2023, Enabling Large Language Models to Generate Text with Citations (ALCE), EMNLP 2023, arXiv 2305.14627
- Cheng et al. 2023, Binding Language Models in Symbolic Languages (Binder), ICLR 2023, arXiv 2210.02875
- Yang et al. 2026, When Agent Memory Needs to Compute, arXiv 2610.19474 (Preprint)
- Anthropic 2024, Building effective agents (Blog)
- Beurer-Kellner et al. 2025, Design Patterns for Securing LLM Agents against Prompt Injections, arXiv 2506.08837
- Liu et al. 2022, What Makes Good In-Context Examples for GPT-3?, DeeLIO 2022, arXiv 2101.06804
- Miller 2024, Adding Error Bars to Evals, arXiv 2411.00640
- Semantic Invariance in Agentic AI (metamorphes Testen), arXiv 2603.13173 (Preprint)
- Jeong et al. 2024, Adaptive-RAG, NAACL 2024, arXiv 2403.14403 (Routing nach Fragetyp, Hintergrund)
- Ollama-Dokumentation „Structured Outputs“; Ollama-Issues #14493 und #14645 (Qwen3.5)
- Bereits in `sources.md`: Huang et al. 2024, Kapoor et al. 2024, Ferrazzi et al. 2026, Yao et al. 2023 (ReAct)
