# ADR-0005: Vollständig synthetischer Dokumentenkorpus

- **Status:** akzeptiert
- **Datum:** 2026-11-14
- **Meilenstein:** M1

## Kontext
Der Agent braucht Testdokumente mit Tabellen, Überschriften-Hierarchien und Diagrammen sowie Fragen mit gesicherter richtiger Antwort. Echte Unterlagen enthalten personenbezogene Daten und keine bekannten Fehler. Selbst erzeugte Dokumente sind für die Prüfungsleistung erlaubt.

## Entscheidung
Der Korpus unter `dataset/` ist vollständig synthetisch: 28 PDFs eines fiktiven Haushalts (Strom, Gas, Wasser, Miete/Betriebskosten, Handwerker sowie Telekommunikation und Versicherungen als Ablenker). Metadaten und erwartete Antworten werden in `documents.yaml` und `ground_truth.yaml` gepflegt.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Echte eigene Unterlagen (anonymisiert) | Datenschutz, keine gesicherte Ground Truth, Anonymisierung aufwendig |
| Mischung echt/synthetisch | Mehraufwand ohne klaren Nutzen, da die synthetischen Layouts bereits realistisch sind |

## Konsequenzen
- Positiv: Ground Truth bekannt, unbedenklich im öffentlichen Repo, gezielte Fallen möglich
- Negativ: Layouts einheitlicher als echte Post; bisher nur ein eingebauter Fehler (ISS-004)
- Zu testen: Parser-Robustheit bei mehrspaltigen Tabellen und Diagrammen (M2/M3)

## Belege
Korpus-Prüfung in `concept.md`, Abschnitt 4.2.
