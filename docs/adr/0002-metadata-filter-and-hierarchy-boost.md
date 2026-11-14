# ADR-0002: Metadatenfilter zusätzlich zum Hierarchie-Boost

- **Status:** vorgeschlagen
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
Konzept Abschnitt 6; folgt nach RUN-xxx.
