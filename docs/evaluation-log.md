# Evaluations-Logbuch

> Jeder Testlauf wird hier festgehalten, auch Fehlschläge. Ohne festgehaltene Konfiguration sind Ergebnisse später nicht vergleichbar.
> Rohdaten (CSV/JSON) liegen unter `data/eval/<run-id>/`, hier stehen nur Zusammenfassung und Deutung.

## Vorlage

```markdown
### RUN-000 – <Zweck, z. B. "Baseline P1 vs. P2, erster Lauf">
- **Datum / Commit:**
- **Varianten:** B0 (Volltext) / P1 (Pipeline) / P2 (Agent)
- **Konfiguration:** Modell(e), num_ctx, top_k, Boost-Faktor, Filter an/aus, Testset-Version
- **Dauer:** gesamt … min, pro Frage Ø … s
- **Ergebnisse (Kurz):**

| Metrik | B0 | P1 | P2 |
|---|---|---|---|
| Numerische Korrektheit | | | |
| Fehlererkennungsrate | | | |
| Fehlalarmrate | | | |
| Quellen-Korrektheit | | | |
| Distractor Rate | | | |
| Tool-Wahl-Korrektheit | – | – | |
| Negativ-Erkennung | | | |
| RAGAS Faithfulness | | | |
| RAGAS Context Precision | | | |
| Latenz Ø (s) | | | |

- **Auffällige Einzelfälle:** (Frage-ID, was ging schief, an welcher Stelle: Parser / Retrieval / Tool-Wahl / Synthese)
- **Meine Deutung (eigene Worte):**
- **Konsequenz / nächster Schritt:**
```

---

## Läufe

*(noch keine)*
