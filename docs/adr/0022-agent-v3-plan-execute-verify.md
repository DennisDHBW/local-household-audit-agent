# ADR-0022: Agent v3 – Verstehen, Ausführen, Prüfen mit festen JSON-Schemas

- **Status:** vorgeschlagen (wartet auf Freigabe; Plan in `docs/m9-plan.md`)
- **Datum:** 2026-11-21
- **Meilenstein:** M9

## Kontext
Der Endlauf run-028 zeigt für P2 (v2) nach Handprüfung 50 % auf den zurückgehaltenen Fragen gegenüber 76 % auf den Entwicklungsfragen. Alle drei Ausfälle stammen aus Regeln, die an den Entwicklungsfragen gebaut wurden: Wortliste für Prüffragen (ADR-0020), Reparatur der Jahresangabe, Antwortzwang nach leerer Antwort (ADR-0021). Das Modell entscheidet in einer offenen Schleife gleichzeitig über Verständnis, Werkzeug, Argumente und Text; seine Ausgaben sind frei (Text, Werkzeugaufruf oder nichts). Der Nutzer verlangt eine deutlich bessere Qualität durch eine bessere Architektur statt weiterer Regeln. Rahmen: nur CPU, höchstens 8B, Prefill ca. 18 Token/s.

## Entscheidung
P3 ersetzt die offene ReAct-Schleife durch einen Zustandsautomaten mit getrennten Rollen: (1) das Modell füllt einen Auftragsrahmen (`QueryFrame`) per eingeschränkter Dekodierung (Ollama `format`), (2) der Code führt deterministische Skills auf Faktenspeicher und Suche aus, (3) der Code prüft die Evidenz und lässt das Modell höchstens zweimal neu planen, (4) das Modell formuliert Sätze mit Beleg-IDs aus einem `enum`, (5) der Code verifiziert Zahlen, Urteil und Belege, (6) der Code setzt die Antwort zusammen. P2 v2 bleibt eingefroren als Vergleich.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| v2 mit weiteren Wortlisten und Reparaturen | Ursache des Einbruchs auf den zurückgehaltenen Fragen (ISS-108, ISS-126, ISS-127) |
| Natives Tool-Calling mit allen Werkzeugen, ohne Routing | kleine Modelle wählen schlechter, je mehr Werkzeuge angeboten werden; mehr Prefill; offene Ausgabe bleibt |
| Rein feste Pipeline ohne Modellentscheidung | verfehlt die Anforderung „agentisch“ (requirements.md 4.3) |
| Größeres Modell oder Feinabstimmung | 8B-Regel, CPU |

## Konsequenzen
- Positiv: Keine Wortlisten in der Steuerung; Strukturfehler der Modellausgabe ausgeschlossen; erfundene Belegnummern per Konstruktion unmöglich; weniger Modellaufrufe; Modell leicht austauschbar (kein Tool-Calling-Template nötig); Dokumentinhalte können den Ablauf nicht umsteuern.
- Negativ / Preis: neuer Code (Orchestrator, Schemas, Renderer); Formatvorgaben können das Schlussfolgern schwächen; Inhaltsfehler beim Verstehen bleiben möglich; mehr Festlegung im Code, weniger freie Werkzeugwahl.
- Zu testen: M9-0 (Schema-Treue, Geschwindigkeit, Cache je Modell), Entwicklungslauf mit Umformulierungen, Endlauf auf dem neuen zurückgehaltenen Satz H2 mit den in `m9-plan.md` vorab festgelegten Zielen.

## Belege
RUN-028, ISS-108, ISS-110, ISS-112, ISS-125 bis ISS-128, ADR-0019 bis ADR-0021. Literatur: ReWOO (arXiv 2305.18323), StateFlow (arXiv 2403.11322), α-UMi (arXiv 2401.07324), Rabinovich und Anaby-Tavor 2025 (arXiv 2504.00914), JSONSchemaBench (arXiv 2501.10868), Chavan 2026 (arXiv 2609.23742), CRITIC (arXiv 2305.11738), CRAG (arXiv 2401.15884), ALCE (arXiv 2305.14627), Tam et al. 2024 (arXiv 2408.02442), Beurer-Kellner et al. 2025 (arXiv 2506.08837).
