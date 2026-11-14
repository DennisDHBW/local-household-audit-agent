# Reverse Engineering – M<x>: <Meilenstein>

> Pro Meilenstein eine Kopie dieser Vorlage anlegen: `m2-parser.md`, `m5-agent.md`, …
> Ziel (Professor): Konzept (logisch) und Prototyp (technisch) „in all seinen Körperteilen“ verstehen: Code-Dateien, Funktionen, Datenstrukturen, Datenflüsse, Bibliotheken.
> **Regel:** Abschnitte 1–4 darf Claude vorbereiten. Abschnitte 5–7 schreibe ich selbst.

**Datum:** · **Commit / Tag:** · **Zeitaufwand:**

## 1. Dateien dieses Meilensteins

| Datei | Zweck (1 Satz) | Wichtigste Funktionen/Klassen | Abhängig von |
|---|---|---|---|
| | | | |

## 2. Datenfluss
Eingabe → Verarbeitungsschritte → Ausgabe (als Liste oder kleines Diagramm). An einem **konkreten Beispiel** aus dem Korpus durchspielen (z. B. eine Tabellenzeile der Stromabrechnung von der PDF bis zum Chunk).

```
<Beispiel-Eingabe>
  → <Funktion> → <Zwischenergebnis>
  → …
```

## 3. Datenstrukturen
Welche Modelle/Dataclasses entstehen oder werden genutzt? Felder und Bedeutung.

## 4. Bibliotheken & Technologie-Bausteine

| Bibliothek | Wofür genau hier? | Welche Funktion nutze ich? | Alternative |
|---|---|---|---|
| | | | |

## 5. Whitebox-Tests (selbst nachvollzogen)
- Welche Tests gibt es? Was prüfen sie genau?
- Welchen Test habe ich selbst geschrieben oder verändert?
- Was ist **nicht** getestet?

## 6. Erklär-Test (ohne in den Code zu schauen)
Beantworte die Verständnisfragen, die Claude gestellt hat, in eigenen Worten. Danach mit dem Code vergleichen und Fehler markieren.

| Frage | Meine Antwort | Stimmt? |
|---|---|---|
| | | |

## 7. Was ich geändert hätte / Schwächen / offene Fragen
-
