# ADR-0003: Kein vollständiges GraphRAG, Beziehungen über Metadaten

- **Status:** vorgeschlagen
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
