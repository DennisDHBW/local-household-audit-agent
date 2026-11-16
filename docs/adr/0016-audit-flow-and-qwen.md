# ADR-0016: Fester Prüfablauf im Code und Modellwechsel auf `qwen2.5:7b`

- **Status:** akzeptiert (Entscheidung des Nutzers am 2026-11-16; Wirkung mit RUN-017 zu bestätigen)
- **Datum:** 2026-11-16
- **Meilenstein:** M6 (M6g)
- **Ersetzt:** ADR-0013 (Modell) und die verworfene Alternative „fester Prüfablauf“ aus ADR-0015; ADR-0015 bleibt für Wiederholungssperre und Rechennachfrage gültig.

## Kontext
RUN-012 bis RUN-016 zeigen, dass die kleinen Modelle Prüffragen nicht verlässlich lösen: Der Sollwert steht oft nie im Kontext (G1, G3, ISS-051/052), und wenn `calculate` aufgerufen wird, stammen die Operanden häufig aus verschiedenen Größen (G2, S5, G4; ISS-067). Beide Modelle liegen nach Handprüfung bei 6 von 14 (ISS-066). Die Rechennachfrage erzwingt einen Rechenaufruf, aber nicht die richtigen Zahlen. Der Nutzer hat entschieden, den Prüfablauf fest im Code zu verdrahten und `qwen2.5:7b` als Agent-Modell zu nehmen.

## Entscheidung
1. **Prüfablauf (`agent/audit_flow.py`)** für Fragen, die `is_audit_question` erkennt (abschaltbar mit `AgentSettings.audit_flow_enabled`):
   - *Plan:* Ein Modellaufruf mit strukturierter Ausgabe (JSON-Schema im `format`-Parameter von Ollama) nennt bis zu `audit_max_checks` (3) Prüfgrößen und je eine Suchanfrage für Sollwert und Istwert.
   - *Suchen:* Der Code führt sie mit dem normalen `search`-Werkzeug aus (Beleg-Nummern, Log und Wiederholungssperre bleiben gleich). Gleiche Anfragen werden nur einmal ausgeführt.
   - *Lesen:* Je Prüfgröße ein Modellaufruf mit strukturierter Ausgabe: Sollzahl, Istzahl, Einheit und die Nummer des Treffers, aus dem jede Zahl stammt.
   - *Prüfen und Rechnen:* Der Code verlangt, dass jede Zahl in dem genannten Treffer **der eigenen Seite** (Soll- oder Ist-Suche) in einer Zeile steht, und bildet die Differenz Ist minus Soll mit dem Werkzeug `calculate`. Zahlen, die nicht belegt sind, werden nicht verwendet (`not_verified`).
   - *Übergabe:* Das Ergebnis geht als eine Nachricht an das Modell (Zahl, Treffernummer, Belegzeile, Differenz, „gleich“ oder „ABWEICHUNG“); danach läuft der Agent-Loop wie bisher, das Modell darf weiter suchen und rechnen (Folgebeträge wie Differenz mal Menge) und schreibt die Antwort. Die Aufrufe des Ablaufs zählen nicht zum Limit von 6 Werkzeugaufrufen (`ToolCallStep.is_flow_call`); die Rechennachfrage entfällt, wenn der Ablauf eine Differenz gerechnet hat.
2. **Modell:** `ModelNames.agent` = `qwen2.5:7b` (Gründe: 6 von 18 erwarteten Quellen zitiert gegen 1, befolgt Anweisungen zum Rechnen, Laufzeit gleich). `llama3.1:8b` bleibt Kandidat (`agent_candidates`); `qwen2.5:7b` bleibt auch Bewerter für RAGAS (ADR-0012), damit bewertet dasselbe Modell nun seine eigenen Antworten (ISS-045 beachten, RAGAS nur als zweite Sicht).

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Agent behält die Wahl, nur Plausibilitätsprüfung der Operanden | Verhindert Fehlalarme nicht, wenn die Sollzahl nie gesucht wird (G1, G3). |
| Vollständig fester Ablauf ohne Modell für den Plan (Regeln je Fragetyp) | Wäre auf die 14 Testfragen zugeschnitten und würde die Messung verfälschen; der Plan bleibt Sache des Modells. |
| Freier Text statt strukturierter Ausgabe | Das Modell schrieb Aufrufe und Zahlen in uneinheitlichen Formaten (ISS-061, ISS-063); das `format`-Schema erzwingt gültiges JSON. |
| Ablauf für alle Fragen | Einzelfragen (Kündigungsfrist, Preis) brauchen weder Plan noch Differenz; zusätzliche Modellaufrufe kosten auf der CPU Minuten (ISS-057). |
| Weiter `llama3.1:8b` | Zitiert kaum, befolgt Rechenanweisung nicht, kein Zeitvorteil mehr (ISS-066). |

## Konsequenzen
- Positiv: Operanden stammen nachweislich aus Treffern der richtigen Seite, die Rechnung ist exakt (`Decimal`), Sollwerte werden gezielt gesucht (Anfrage nennt die Größe, nicht die Frage). Alles steht im Log (`AuditFlowStep`, `is_flow_call`).
- Negativ / Preis der Entscheidung:
  - Der Code garantiert nicht, dass Soll und Ist **dieselbe Größe** sind; das entscheidet das Modell beim Lesen (ISS-068). Vorzeichen gehen verloren (`extract_numbers` liest Beträge ohne Vorzeichen).
  - Der Plan hängt am Wortschatz des Modells; Größen wie die z-Zahl stehen deshalb als Beispiele im Prompt (Gebietswissen, keine Testantworten). Mit höchstens 3 Prüfgrößen kann eine Frage Fehler in einer vierten Größe nicht finden.
  - Mehr Modellaufrufe: 1 Plan plus je Prüfgröße 1 Lesen (Prefill von 2 Suchen mit bis zu 5 Treffern je 600 Zeichen, geschätzt 2 bis 3 Minuten bei 18 Token/s) vor der Antwort; je Prüffrage deutlich mehr Zeit als bisher.
  - Der Ablauf ist eine Pipeline für Prüffragen; die Werkzeugwahl des Agenten bleibt nur für den Rest. In der Ausarbeitung als Abwägung zwischen Autonomie und Zuverlässigkeit darzustellen.
- Was muss getestet werden? RUN-017 (P2, 14 Fragen, `qwen2.5:7b`) gegen RUN-014: Fehler erkannt (von 3, mit tragfähiger Begründung), Fehlalarme bei G2, S5, Z1 (von 3 richtigen Abrechnungen), richtig nach Handprüfung (von 14), Zeit je Prüffrage, Anzahl `not_found` und `not_verified` je Prüfgröße.

## Belege
RUN-012 bis RUN-016 (`docs/evaluation-log.md`), ISS-051, ISS-052, ISS-054, ISS-058, ISS-060, ISS-063, ISS-066, ISS-067, ISS-068; ADR-0013, ADR-0014, ADR-0015; Tests in `tests/test_audit_flow.py`.
