# Leitfaden für die Ausarbeitung (Phase 2)

> Claude schreibt die Kapitel. Ich lese jedes Kapitel, korrigiere es und muss jeden Absatz frei erklären können: Der Professor achtet beim Lesen darauf, ob Konzept und Prototyp verstanden wurden, und kann im Gespräch nachfragen.
> Ziel des Stils: ein guter Text eines Informatik-Studierenden im 3./4. Studienjahr. Sachlich, konkret, mit eigenen Messwerten und ehrlichen Problemen. Nicht poliert wie ein Werbetext.

---

## 1. Rahmen

- Umfang: 5–8 Seiten Fließtext ohne Titelblatt, Verzeichnisse und Anhang
- LaTeX-Vorlage unter `paper/` (DHBW-Template). Aktiv: Titelblatt, Inhaltsverzeichnis, Kapitel (`paper/content/chapter/NN-name/main.tex`). Auskommentiert: Sperrvermerk, Erklärung, KI- und Gender-Hinweis, Abstract, Verzeichnisse, Literaturverzeichnis, Glossar. Ein Anhang kann bei Bedarf wieder aktiviert werden.
- Keine Literatur: kein Literaturverzeichnis, keine Zitate, keine Verweise auf Paper (Entscheidung vom 2026-11-14). Fachbegriffe wie ReAct oder RAG dürfen als Begriffe vorkommen. Der Reflexionsteil stützt sich auf eigene Ergebnisse.
- **Keine Ich-Form** (auch kein „wir“). Stattdessen: der Prototyp, der Agent, das System, diese Arbeit, unpersönliche Konstruktionen. Passiv nur dosiert, sonst wird der Text hölzern. Bevorzugt Sätze mit dem System als Subjekt: „Der Parser erkennt Tabellen zuerst …“, „Im ersten Testlauf zeigte sich …“.
- Gliederung und Gewichtung: siehe `concept.md`, Abschnitt 14, und `requirements.md`, Abschnitt 3
- Begriffe genau wie in `glossary.md`

## 2. Arbeitsablauf pro Kapitel

| Schritt | Wer | Was |
|---|---|---|
| 1. Material | Claude | Passende Stellen aus `dev-journal.md` (inkl. O-Ton), `issues-log.md`, ADRs, Reverse-Engineering-Notizen, `evaluation-log.md`, `glossary.md`, `sources.md` heraussuchen und kurz auflisten |
| 2. Gliederung | Claude, ich gebe frei | Stichpunkte pro Absatz, mit Zuordnung zum Bewertungskriterium |
| 3. Entwurf | Claude | Kapitel nach den Regeln unten schreiben, als `.tex`-Datei |
| 4. Lesen | ich | Laut lesen. Stellen markieren, die falsch sind, die ich nicht erklären könnte oder die ich nie so sagen würde |
| 5. Verständnisfragen | Claude | 3–5 Fragen zum Kapitel, die ein Prüfer stellen könnte. Ich beantworte sie kurz |
| 6. Überarbeitung | Claude | Markierungen einarbeiten, meine Formulierungen aus Schritt 4/5 übernehmen |
| 7. Eigene Handschrift | ich | In jedem Kapitel 2–3 Sätze selbst umformulieren oder ergänzen |

> Abweichung (Entscheidung des Nutzers, 2026-11-18): Claude erledigt die Schritte 1–3 je Kapitel in einem eigenen Chat und sammelt die Verständnisfragen (Schritt 5) in `docs/paper-questions.md`. Lesen, Antworten, Überarbeitung und eigene Handschrift (Schritte 4–7) folgen gesammelt, wenn alle sechs Kapitel stehen.

Schritt 7 ist kurz, macht aber viel aus: Eigene Formulierungen und Antworten aus Schritt 5 bringen den Text näher an die eigene Sprache und zeigen beim Lesen, ob alles verstanden ist.

---

## 3. Schreibregeln für Claude

### 3.1 Inhalt
- **Jeder Absatz hat einen konkreten Bezug zum Projekt:** ein Dokument aus dem Korpus, eine Funktion, ein Messwert, ein aufgetretenes Problem, eine Entscheidung. Allgemeinwissen nur, soweit es zum Verständnis nötig ist.
- **Eigene Zahlen statt Adjektive:** „P2 fand 3 von 4 eingebauten Fehlern“ statt „P2 erzielte deutlich bessere Ergebnisse“.
- **Probleme und Umwege zeigen** (aus `issues-log.md`): was zuerst nicht funktionierte, warum, wie es gelöst wurde. Gerade das wirkt glaubwürdig.
- **Entscheidungen begründen** (aus ADRs), inklusive verworfener Alternativen.
- **Grenzen offen benennen**, ohne sich kleinzureden.
- **O-Ton nutzen:** Gedanken und Beobachtungen aus den O-Ton-Feldern des Journals inhaltlich aufgreifen und sinngemäß in die unpersönliche Form übertragen („Überraschend war, dass …“, „Aufwendiger als erwartet war …“).

### 3.2 Sprache
- Sachlicher, klarer Ton auf studentischem Niveau. Fachbegriffe korrekt, aber nicht gestelzt.
- **Satzlänge mischen:** neben normalen Sätzen auch kurze. Keine Kette gleich gebauter Sätze.
- **Absätze unterschiedlich lang.** Nicht jeder Absatz braucht Einleitung, Hauptteil und Schlusssatz.
- **Fließtext statt Aufzählungen.** Listen und Tabellen nur, wo der Inhalt wirklich tabellarisch ist (Testergebnisse, Tools, Chunk-Typen).
- Übergänge schlicht: „Danach“, „Deshalb“, „Dabei zeigte sich“, „Im Unterschied dazu“.
- Leichte Unebenheiten sind in Ordnung, Fehler nicht.
- Keine Gedankenstriche als Satzverbinder (Komma, Punkt oder Klammer nutzen).
- Wenig Fettdruck, keine Hervorhebungen im Fließtext.
- Englische Fachbegriffe nur, wo sie im Fach üblich sind (Chunk, Embedding, Retrieval), nicht als Stilmittel.

### 3.3 Typische KI-Merkmale, die nicht vorkommen dürfen

**Wörter und Floskeln:**
„nahtlos“, „robust“ (außer als genau definierter Fachbegriff), „entscheidend“, „maßgeblich“, „vielschichtig“, „ganzheitlich“, „im Kern“, „darüber hinaus“, „nicht zuletzt“, „es ist wichtig zu beachten“, „spielt eine zentrale Rolle“, „zusammenfassend lässt sich sagen“, „in der heutigen Zeit“, „Paradigmenwechsel“, „Mehrwert“, „innovativ“, „effizient und effektiv“, „ein wesentlicher Baustein“, „eröffnet neue Möglichkeiten“, „Herausforderungen und Chancen“

**Satzmuster:**
- „Nicht nur …, sondern auch …“
- Dreierreihen von Adjektiven oder Nomen („schnell, präzise und zuverlässig“)
- „Dabei zeigt sich, dass …“ am Anfang jedes zweiten Absatzes
- Rhetorische Fragen („Doch wie lässt sich dieses Problem lösen?“)
- Zusammenfassender Schlusssatz in jedem Absatz
- Symmetrisches „einerseits … andererseits“ als Dauerstruktur
- Doppelpunkt-Einleitungen mit anschließender Aufzählung in jedem Abschnitt

**Aufbau:**
- Gleich lange, gleich gebaute Abschnitte
- Kapitel, die mit einer Wiederholung der Kapitelüberschrift beginnen
- Abschließende „Fazit“-Absätze am Ende jedes Unterkapitels
- Übertriebene Vorsicht bei gemessenen Dingen, übertriebene Sicherheit bei ungemessenen

### 3.4 Beispiel

**So nicht:**
> Die Vorverarbeitung spielt eine zentrale Rolle für die Qualität des gesamten Systems. Durch den Einsatz moderner Parsing-Verfahren werden nicht nur Texte, sondern auch Tabellen und Bilder nahtlos verarbeitet. Dies ermöglicht eine robuste, präzise und effiziente Wissensbasis.

**So:**
> Die Stromabrechnungen enthalten Verbrauch und Preise fast ausschließlich in Tabellen. Ein erster Versuch mit einfachem Text-Splitting zerlegte die Kostenaufstellung so, dass Spaltenköpfe und Werte in unterschiedlichen Chunks landeten. Der Parser erkennt deshalb zuerst die Tabellenbereiche mit `find_tables()` und schließt sie aus dem Fließtext aus. Jede Tabellenzeile wird anschließend mit ihren Spaltennamen serialisiert, etwa „Zeitraum: 01.07.–31.12.2024 | Verbrauch: 1.380 kWh | Arbeitspreis: 32,10 ct/kWh“.

---

## 4. Endkontrolle vor der Abgabe

- [ ] Alle Bewertungskriterien abgedeckt (`requirements.md`, Abschnitt 11)
- [ ] Testmodul-Abschnitt vorhanden, mit Ergebnissen und Qualitätsaussage
- [ ] GraphRAG-Entscheidung begründet
- [ ] 12 Testfragen und Ergebnisse dargestellt
- [ ] Jede Zahl durch `evaluation-log.md` belegt
- [ ] Begriffe einheitlich laut Glossar
- [ ] Keine Ich-/Wir-Form
- [ ] Keine Wörter und Muster aus Abschnitt 3.3 (Suchlauf über die `.tex`-Dateien)
- [ ] Ich kann jeden Absatz mündlich erklären und die Verständnisfragen beantworten
- [ ] In jedem Kapitel eigene Formulierungen ergänzt
- [ ] Laut gelesen, Seitenzahl 5–8 eingehalten
