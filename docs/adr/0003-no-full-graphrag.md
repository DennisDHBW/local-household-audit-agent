# ADR-0003: Kein vollständiges GraphRAG, Beziehungen über Metadaten

- **Status:** akzeptiert (2026-11-18; Prototyp ohne Graph gebaut, Begründung in Kapitel 4 der Ausarbeitung). Vorheriger Stand: vorgeschlagen
- **Datum:** 2026-11-14
- **Meilenstein:** M4

## Kontext
Die Vorlesung verlangt eine begründete Entscheidung, ob GraphRAG sinnvoll ist. Mögliche Entitäten: Vertrag, Anbieter, Zähler, Tarif/Preis, Abrechnungszeitraum, Kostenart, Wohnung. Beziehungen: Rechnung *bezieht sich auf* Vertrag, Preisänderung *ändert* Tarif *ab* Datum, Zähler *gehört zu* Vertrag, Kostenart *wird umgelegt nach* Schlüssel.

## Entscheidung
Kein Knowledge Graph. Die wenigen, stabilen Beziehungen werden über Metadaten-Schlüssel (`contract_id`, `billing_period`, `valid_from`) abgebildet. Multi-Hop übernimmt der ReAct-Agent.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Vollständiges GraphRAG mit LLM-Entity-Extraktion | langsam auf CPU, falsch extrahierte Preise wären schädlicher als keine; zusätzliche Datenbank |
| Kleiner, manuell gepflegter Graph | Informationsgehalt deckt sich fast vollständig mit den Metadaten |

## Konsequenzen
- Positiv: einfacher, schneller, leichter zu testen
- Negativ: Überblicksfragen über viele Verträge/Wohnungen wären mit Graph eleganter
- Ausblick: bei Hausverwaltung mit vielen Wohnungen und Mietparteien wäre GraphRAG sinnvoll

## Belege
Anforderungen 5.5; Konzept Abschnitt 10.

## Nachtrag 2026-11-18 (Kapitel 4)
- Status auf „akzeptiert“ gesetzt: Der Prototyp (v1.0.0) arbeitet ohne Graph; die Beziehungen laufen über `contract_id`, `billing_period` und den Dokumentkatalog (`include_counterpart`, ADR-0014).
- In der Evaluation fiel eine Beziehung auf, die die Suche nicht abbildet: die Vorjahresrechnung bei G3 (ISS-074). Die Daten dafür liegen in den Metadaten (gleiche Vertragsnummer `GV-2024-7731`, früherer Abrechnungszeitraum), genutzt werden sie nicht. Ein Graph wäre dafür nicht nötig.
