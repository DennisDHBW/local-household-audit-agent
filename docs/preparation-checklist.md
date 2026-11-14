# Vorbereitungs-Checkliste (vor Phase 1)

> Stand: 2026-11-14. Erledigtes ist abgehakt. Was übrig bleibt, dauert zusammen ca. 15 Minuten.

---

## A. Organisatorisches
- [x] Synthetische Dokumente erlaubt, keine Ich-Form, Code auf GitHub, 5–8 Seiten ohne Anhang (`requirements.md`, 2.2)
- [x] LaTeX-Vorlage festgelegt (DHBW-Template, unter `paper/`)
- [ ] Angaben fürs Titelblatt liefern (Name, Matrikelnummer, Kurs, Studiengang, Dozent), siehe `paper/settings/document.tex`

## B. Repository
- [x] GitHub-Repository angelegt (`DennisDHBW/local-household-audit-agent`)
- [x] Projekt lokal unter `/home/usr0/PycharmProjects/local-household-audit-agent`, `pyproject.toml` (Python 3.13), `.venv`
- [x] Doku-Gerüst, `.gitignore`, LaTeX-Vorlage eingespielt und in sinnvolle Commits aufgeteilt (durch Claude)
- [ ] Erster Push: `git push -u origin main` (Claude hat noch keine Schreibrechte, siehe `ai-workflow.md`, Abschnitt 3)

## C. Claude einrichten
- [ ] **C1 – Projektanweisungen** aus `ai-workflow.md`, Abschnitt 1.1, ins Claude-Projekt kopieren (alte Fassung ersetzen)
- [x] **C2 – Projektwissen:** `requirements.md` und `concept.md` (aktualisiert durch Claude)
- [x] **C3 – Projektordner verbunden**
- [x] **C4 – Skills gespeichert:** `audit-session-closeout`, `audit-reverse-engineering`, `audit-paper-writer` (Aktualisierungen zur neuen Arbeitsweise bestätigen)
- [ ] **C5 – Modell-Standard** für M0: Sonnet 5.5, Effort High

## D. Testkorpus
- [x] 28 synthetische PDFs vorhanden und geprüft (`concept.md`, Abschnitt 4.2): gut geeignet
- [ ] Entscheiden: 1–2 weitere eingebaute Fehler ergänzen? (derzeit nur einer)
- [ ] (M1) `dataset/documents.yaml` und `dataset/ground_truth.yaml` erstellen (macht Claude)

## E. Lokale Umgebung (nur auf deinem Rechner möglich)
Claudes Shell erreicht Ollama nicht. Diese Befehle einmal im Terminal ausführen (ca. 15 GB Download, kann nebenher laufen):
```bash
ollama pull qwen2.5:7b && ollama pull llama3.1:8b && ollama pull gemma3:4b && ollama pull llama3.2 && ollama pull nomic-embed-text
ollama list
```
- [ ] Modelle geladen

## F. Optional, aber hilfreich
- [ ] Referenzprototyp aus der Vorlesung (falls vorhanden) in den Projektordner legen, z. B. unter `reference/`, damit Claude ihn mit dem eigenen Ansatz vergleichen kann
- [ ] Claude-GitHub-App für das Repo installieren, damit Claude selbst pushen kann

## G. Danach: Start mit M0
Neuer Chat, Sonnet 5.5 / High:
```text
Neue Sitzung. Lies docs/status.md. Heute: M0, Setup. Erst Plan.
```
M0 umfasst: Abhängigkeiten und Tooling (`uv`, ruff, pytest), Projektstruktur `src/`, zentrale Konfiguration, Quality-Gate-Skript, Smoke-Test (Geschwindigkeit, Tool-Calling, Embedding, Vision) mit Ergebnis in `evaluation-log.md`, Abschluss von ADR-0004.
