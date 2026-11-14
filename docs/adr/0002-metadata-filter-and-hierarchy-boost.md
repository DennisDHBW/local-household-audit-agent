# ADR-0002: Metadatenfilter zusätzlich zum Hierarchie-Boost

- **Status:** akzeptiert (Filter belegt, Boost ohne belegten Nutzen)
- **Datum:** 2026-11-14
- **Meilenstein:** M4

## Kontext
Der Korpus enthält ähnliche Begriffe in verschiedenen Dokumenten („Grundpreis“ im Strom-, Gas- und Handyvertrag) und mehrere Jahre derselben Sparte. Reine Vektorsuche mit Hierarchie-Boost (`final_score = base_score × hierarchy_boost`, Boost 1.5) könnte Ablenkungsdokumente oder falsche Jahre liefern.

## Entscheidung
Jeder Chunk erhält Metadaten (`utility_type`, `doc_type`, `contract_id`, `billing_period`, `valid_from`) aus einer manuell gepflegten `documents.yaml`. Die Such-Tools können diese als ChromaDB-`where`-Filter übergeben. Der Hierarchie-Boost aus der Vorlesung bleibt zusätzlich bestehen.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Nur Hierarchie-Boost | wirkt nur auf Begriffe im Pfad, schließt Ablenker nicht aus |
| Metadaten per LLM automatisch extrahieren | langsam auf CPU, fehleranfällig; bei 12–15 Dokumenten nicht nötig (KISS) |
| Separater Index pro Sparte | mehr Komplexität, Querfragen über Sparten schwieriger |

## Konsequenzen
- Positiv: Ablenker gezielt ausschließbar, richtiger Zeitraum auffindbar
- Negativ: Metadaten müssen manuell gepflegt werden; falsche Filter des Agenten können relevante Treffer ausschließen
- Zu testen: Distractor Rate ohne Filter / nur Boost / Filter + Boost (Evaluation)

## Belege
Konzept Abschnitt 6; RUN-004 in `evaluation-log.md` (12 Fragen, Top-5, handgesetzte Filter):
- Ablenker-Treffer: 4/60 ohne Filter, 3/60 nur mit Boost, 0/55 mit Filter (mit und ohne Boost).
- MRR der erwarteten Datei: 0,683 (ohne Filter, mit und ohne Boost), 0,733 mit Filter.
- Der Boost wirkte bei 55 von 60 Treffern und änderte keinen Rang, weil die Anfrageterme in den Überschriften fast aller Dokumente stehen (ISS-027). Er bleibt als Baustein aus der Vorlesung bestehen, weil er nichts verschlechtert hat; ein Nutzen ist nicht belegt.
- Grenzen: ISS-025 (Zeitraumfilter), ISS-028 (Filter von Hand gesetzt). Umsetzung: ADR-0009.
