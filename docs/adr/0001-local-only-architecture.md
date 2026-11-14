# ADR-0001: Vollständig lokale Architektur ohne Cloud-API

- **Status:** akzeptiert
- **Datum:** 2026-11-14
- **Meilenstein:** M0

## Kontext
Die Prüfungsanforderung verlangt, dass der Agent lokal/offline läuft. Zusätzlich enthalten Energie- und Nebenkostenunterlagen personenbezogene Daten (Adresse, Zählernummern, Bankverbindung, Verbrauchsprofile).

## Entscheidung
Alle Modelle laufen über Ollama auf dem eigenen Laptop, Vektoren liegen in einer lokalen ChromaDB. Keine Cloud-API im Standardbetrieb.

## Verworfene Alternativen
| Alternative | Warum nicht? |
|---|---|
| Cloud-LLM für die finale Antwort (Folie: Claude Sonnet / GPT-4o „nur bei Klick“) | widerspricht der Grundanforderung; Datenschutz |
| Cloud-Vergleich als abschaltbare Option | vorerst nicht nötig (YAGNI); höchstens später als klar gekennzeichneter Vergleich |

## Konsequenzen
- Positiv: Datenschutz, keine laufenden Kosten, unbegrenztes Testen
- Negativ: nur CPU-Inferenz, Modelle ≤ 8B, langsame Antworten (siehe ISS-001, ADR-0004)
- Zu testen: Ist die Antwortqualität eines 7–8B-Modells für die Prüffragen ausreichend?

## Belege
Anforderungen 4.1; Hardware-Daten (`preparation-checklist.md`).
