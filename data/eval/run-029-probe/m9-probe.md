# M9-0 Machbarkeitsprobe (run-029-probe)

Ollama 0.35.1 · 2026-11-21 20:08 · num_ctx 8192 · temperature 0

| Modell | gültiges JSON | Schema | Thinking | Rahmen exakt | Felder | Laden s | Prefill kalt s (Tok/s) | Prefill warm s | Wiederholung s | Decode Tok/s | Rahmen s | Wechsel getrennt s | Wechsel gemeinsam s | RAM MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:7b | 9/9 | 9/9 | 0 | 7/8 | 42/43 | 10.85 | 67.34 (21.4) | 1.81 | 0.18 | 6.0 | 13.12 | 1.98 | 3.32 | 5911 |
| qwen3:8b | 9/9 | 9/9 | 0 | 7/8 | 42/43 | 13.13 | 79.75 (18.1) | 4.21 | 0.21 | 4.9 | 18.21 | 3.94 | 6.76 | 6773 |
| qwen3.5:4b | 9/9 | 9/9 | 0 | 7/8 | 42/43 | 7.46 | 39.01 (34.0) | 31.07 | 0.3 | 7.9 | 38.71 | 29.22 | 26.15 | 7574 |
| granite4:tiny-h | 9/9 | 9/9 | 0 | 5/8 | 39/43 | 9.1 | 19.83 (69.9) | 15.26 | 0.16 | 17.5 | 18.73 | 13.99 | 12.82 | 7867 |

Prefill warm: Median der Fragen F2–F8 (gleicher Präfix). Wiederholung: F1 ein zweites Mal, identischer Prompt. Wechsel: dritter Aufruf der Folge Rahmen → Antwort → Rahmen, mit getrennten oder einem gemeinsamen Systemprompt.

## Abweichungen vom Gold-Rahmen

- qwen2.5:7b F3: utility='other'
- qwen3:8b F3: utility='electricity'
- qwen3.5:4b F3: utility='electricity'
- granite4:tiny-h F3: utility='electricity'
- granite4:tiny-h F5: utility='other', period='years'
- granite4:tiny-h F6: utility='other'

## ISS-126

Angeboten: calculate, get_facts, list_documents, plan, search

- first / chat: 1672 Prompt-Token, 64 Token, done_reason stop, Werkzeugaufrufe [{'name': 'plan', 'arguments': {'steps': ['check_bill Heizstrom 2024', 'get_facts verbrauch Heizstrom 2024', 'get_facts rechnungsbetrag Heizstrom 2024']}}], Text '', Fehler None
- first / raw: 1734 Prompt-Token, 65 Token, done_reason stop, Werkzeugaufrufe [], Text '<tool_call>\n{"name": "plan", "arguments": {"steps": ["check_bill Heizstrom 2024", "get_facts verbrauch 2024", "calculate 3100 * (0.395 - 0.382)"]}}\n</tool_call>', Fehler None
- after_plan / chat: 1817 Prompt-Token, 32 Token, done_reason stop, Werkzeugaufrufe [], Text '', Fehler None
- after_plan / raw: 1879 Prompt-Token, 41 Token, done_reason stop, Werkzeugaufrufe [], Text '<tool_call>\n{"name": "check_bill", "arguments": {"utility_type": "district_heating", "tariff_kind": "heating", "year": 2024}}\n</tool_call>', Fehler None
