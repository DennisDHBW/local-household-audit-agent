# M1 – Verständnisfragen mit Antworten (Referenz zum späteren Lernen)

> Auf Wunsch von mir von Claude mit Antworten hinterlegt, weil heute keine Zeit war. Ersetzt **nicht** den Erklär-Test: Vor dem Lesen der Antworten die Fragen selbst beantworten und in `m1-metadata-ground-truth.md`, Abschnitt 6, eintragen. Fragen zu M0 stehen in `m0-setup.md`.

## Fragen und Antworten

**1. Was gibt `load_document_catalog` zurück, und was passiert bei kaputtem YAML?**
Ein `DocumentCatalog` (unveränderliche Liste von `DocumentMeta`). `_read_yaml` fängt `yaml.YAMLError` und wirft `CorpusError("… invalid YAML …")`. Fehlt die Datei, kommt `CorpusError("… not found …")`. Verletzt der Inhalt das Schema, wird die Pydantic-`ValidationError` ebenfalls in `CorpusError` umgewandelt. Aufrufer müssen also nur einen Fehlertyp behandeln.

**2. Warum steht `is_noise_document` in `documents.yaml`, die Fehlerinfos (`PlantedError`) aber nur in `ground_truth.yaml`?**
`documents.yaml` liefert Metadaten, die später in die Chunks und damit in den Agenten-Kontext fließen. Fehlerinfos dürfen dort nicht stehen, sonst könnte der Agent sie lesen und die Fehlererkennung wäre wertlos. Das Rauschen-Flag dient nur der Auswertung (Distractor Rate). Ehrlicher Hinweis: Im Konzept ist es als „für den Agenten nicht sichtbar“ vorgesehen, erzwungen wird das erst bei Ingest/Tools (M2/M4), nicht im Datenmodell.

**3. Was passiert bei `billing_period_start` ohne `billing_period_end`?**
Der `@model_validator(mode="after")` `DocumentMeta._check_consistency` wirft einen `ValueError` („billing period needs both start and end“). Pydantic macht daraus eine `ValidationError`, `load_document_catalog` daraus ein `CorpusError`. Dasselbe passiert, wenn der Start nach dem Ende liegt.

**4. Warum `frozen` und `extra="forbid"`?**
`frozen=True` macht die Modelle nach dem Laden unveränderlich (keine versehentlichen Änderungen am Referenzdatensatz, zudem hashbar). `extra="forbid"` lehnt unbekannte Felder ab: Ein Tippfehler wie `colour` oder `utilty_type` fällt sofort auf, statt still ignoriert zu werden (Fail Fast).

**5. Verfolge „40,30 EUR zu viel“ (E1) von `ground_truth.yaml` bis zur Auswertung.**
Der Wert steht als `ExpectedFact` in Frage G1 und in `PlantedError` E1. `load_ground_truth` macht daraus `Decimal("40.30")` mit Toleranz 0,01. In der Evaluation (M6) vergleicht die Metrik **numerische Korrektheit** die Zahl der Agentenantwort mit diesem Wert; die **Fehlererkennungsrate** prüft, ob der Agent E1 bei der Rechnung 06 meldet.

**6. Wie berechnet sich der Fehlbetrag 51,74 EUR in Dokument 29?**
Abgerechnet: 11.819 kWh (1.060 m³ × z-Zahl 1,0000 × 11,150) × 9,95 ct = 1.175,99 EUR plus Grundpreis 12 × 16,00 = 192,00 EUR, zusammen **1.367,99 EUR**. Richtig: 1.060 m³ × 0,9560 × 11,150 = 11.299 kWh × 9,95 ct = 1.124,25 EUR plus 192,00 EUR = **1.316,25 EUR**. Differenz 51,74 EUR. Die richtige z-Zahl steht in den Gasrechnungen 2024 und 2025 (Dokumente 08 und 10).

**7. Warum 10 `audit_checks`, welche Kennzahlen?**
Es sind alle Abrechnungen mit Zeitraum aus Strom, Gas, Wasser und Betriebskosten (je 2024, 2025 und für Strom/Gas/Betriebskosten teils 2026), davon 7 korrekt und 3 fehlerhaft (E1–E3). Damit messbar: **Fehlererkennungsrate** (gemeldete von den 3 Fehlern) und **Fehlalarmrate** (Meldungen bei den 7 korrekten Abrechnungen). Telekom- und Versicherungsrechnungen sind Ablenker und nicht Teil der Prüfurteile.

**8. Schwäche bei nur drei eingebauten Fehlern?**
Jeder Treffer ändert die Fehlererkennungsrate um 33 Prozentpunkte, statistisch aussagekräftig ist das kaum. Dazu sind nur drei Fehlerarten abgedeckt (Preis, Umrechnungsfaktor, Umlageschlüssel), und die Dokumente 29/30 sind später datiert und im Layout anders als die Originale (ISS-010). Die Evaluation muss das als Einschränkung ausweisen.

## Zusatz: Test, den ich selbst schreiben könnte
Mindestens einen Fehlerpfad aus `tests/test_corpus.py` ergänzen, z. B. `AuditCheck` mit `is_correct: false` ohne `planted_error_id` (erwartet: `ValueError`), oder ein ungültiger `utility_type`.
