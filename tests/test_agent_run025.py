"""Fixes after the night run run-025 (ISS-117): real model outputs of that run as test data.

No Ollama: the chat is scripted, the fact store is the small Heizstrom store of the fact tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from audit_agent.agent.loop import REPEAT_LIMIT, AgentLoop
from audit_agent.agent.models import NudgeStep
from audit_agent.agent.prompts import (
    GAP_ANSWER,
    drop_trailing_gap,
    is_english,
    needs_citation,
    strip_step_talk,
    unsupported_numbers,
)
from audit_agent.agent.scope import CURRENT_QUESTION
from audit_agent.agent.tools import ToolBox
from audit_agent.config import AgentSettings, Settings
from audit_agent.corpus import DocumentCatalog
from tests.agent_fakes import FakeBackend, ScriptedChat, answer_reply, make_hit, tool_reply
from tests.test_facts import BILL, CONTRACT, LETTER, _store

CATALOG = DocumentCatalog(documents=(CONTRACT, LETTER, BILL))
CHECK = ("check_bill", {"utility_type": "electricity", "tariff_kind": "heating", "year": 2025})
AUDIT = "Ist die Heizstromabrechnung 2025 korrekt?"

# Model outputs of run-025 (P2, qwen2.5:7b), shortened where marked.
S2_PLAN_ONLY = (
    "Plan:\n1. **check_bill** Heizstrom 2025, um zu überprüfen, ob der Heizstromtarif 38.20 "
    "ct/kWh beträgt.\n2. **make_overview** um die Ergebnisse zu summenarisieren.\n\n"
    "Lass uns den ersten Schritt ausführen."
)
H1_PLAN_ONLY = (
    "Zur Überprüfung gehe ich wie folgt vor:\n\n1. check_bill heating 2025 to verify if the "
    "applied prices match the working prices [2] and [4].\n2. make_overview to provide an "
    "overview of the heating costs for 2025.\n\nNow, I will execute the first step."
)
H1_ENGLISH = (
    "Based on the facts provided:\n\n- The HT (Nachtspeicher) working price for 2025 is 33.50 "
    "ct/kWh [2].\n- The NT (Heiztag) working price for 2025 is 24.10 ct/kWh [4].\n\nThese "
    "prices are valid according to the contract and invoices for 2025."
)
S3_WITH_PLAN = (
    "Der Wasserverbrauch 2025 laut Zählerständen betrug 74 m³ [1].\n\nPlan für die nächsten "
    "Schritte:\n1. check_bill water 2025 - Überprüfen, ob der Verbrauch in der Rechnung stimmt."
    "\n2. make_overview - Übersicht der Wasserabrechnung 2025 erstellen.\n\n"
    "[1] 15_Wasser_Jahresbescheid_2025_SWM.pdf, S. 1"
)
H3_WITH_PLAN = (  # shortened
    "Prüfung der Heizstromabrechnung 2024 ist erfolgreich. Die Rechnung stimmt mit dem Vertrag, "
    "Preisschreiben und Zählerständen überein.\n\nPlan:\n1. check_bill Lichtstrom 2024 "
    "[Stromverbrauch und Rechnungsbetrag] [15]\n2. get_facts Wohnfläche 2024 [16]\n\n"
    "Nächster Schritt: check_bill Lichtstrom 2024."
)
V1_MIXED = (  # shortened
    "Grafik erstellt: Verbrauch Lichtstrom 2024–2025 (verbrauch-lichtstrom-2024-2025.png, wird "
    "angehängt).\n\nPlan:\n1. make_chart Verbrauch Lichtstrom 2024-2025 [bereits erstellt]\n"
    "2. check_bill Heizstrom 2024-2025\n\nNächster Schritt: \n2. check_bill Heizstrom 2024-2025, "
    "um den Heizstromverbrauch zu überprüfen.\n\nErgebnis: \n- Lichtstrom 2024: 3.250 kWh [1] [2]"
    "\n- Lichtstrom 2025: 3.100 kWh [3] [4]"
)
G2_NOT_NEEDED = (
    "Schritt 2, der Aufruf von `get_facts`, ist nicht mehr notwendig, da die Prüfung der "
    "Betriebskosten-Rechnung 2025 bereits bestätigt hat, dass alles korrekt berechnet ist."
)
G4_ANNOUNCE = "Schritt 2, get_facts, ist noch nicht ausgeführt. Lassen Sie mich das jetzt tun:"
N1_FOOTNOTE = (
    f"{GAP_ANSWER} Lassen Sie uns mit der Prüfung beginnen, indem wir zuerst die Rechnung für "
    "das Jahr 2023 überprüfen, ob sie vorhanden ist. [1]\n\n[1] Hinweis: Argumente angepasst "
    "(tariff_kind aus der Frage ergänzt: household)."
)
VERDICT = "Nein, die Heizstrom-Rechnung 2025 stimmt nicht: NT 3.920 statt 3.420 kWh [3]."


def _loop(tmp_path: Path, replies, **agent_options) -> tuple[AgentLoop, ScriptedChat]:
    settings = Settings(project_root=tmp_path, agent=AgentSettings(**agent_options))
    backend = FakeBackend(lambda query, options: [make_hit()])
    tools = ToolBox(
        settings, backend, CATALOG, facts=_store(), artifact_dir=tmp_path / "charts"
    ).tools()
    chat = ScriptedChat(replies)
    return AgentLoop(settings, chat, tools), chat


def _nudges(run) -> list[str]:
    return [step.reason for step in run.steps if isinstance(step, NudgeStep)]


# --- Cleaning the answer --------------------------------------------------------------------


@pytest.mark.parametrize("text", [S2_PLAN_ONLY, H1_PLAN_ONLY, G2_NOT_NEEDED, G4_ANNOUNCE])
def test_answers_that_only_announce_steps_become_empty(text: str):
    assert strip_step_talk(text) == ""


def test_plans_after_a_real_answer_are_removed_and_the_answer_stays():
    assert strip_step_talk(S3_WITH_PLAN) == (
        "Der Wasserverbrauch 2025 laut Zählerständen betrug 74 m³ [1].\n\n"
        "[1] 15_Wasser_Jahresbescheid_2025_SWM.pdf, S. 1"
    )
    assert strip_step_talk(H3_WITH_PLAN).endswith("Zählerständen überein.")
    v1 = strip_step_talk(V1_MIXED)
    assert "Plan" not in v1 and "check_bill" not in v1
    assert v1.startswith("Grafik erstellt") and "3.100 kWh [3] [4]" in v1


def test_overview_lists_and_verdicts_are_not_step_talk():
    overview = "Hier ist die Übersicht:\n\n- Heizstrom: 1.257,82 EUR [1]\n- Gas: 1.555,43 EUR [2]"
    verdict = "Nein, stimmt nicht.\n\nZur Kurzfassung:\n- Soll: 500,00 EUR [11]\n- Ist: 480,00 EUR"
    assert strip_step_talk(overview) == overview
    assert strip_step_talk(verdict) == verdict


def test_a_footnote_with_a_number_does_not_replace_the_gap_answer():
    assert drop_trailing_gap(strip_step_talk(N1_FOOTNOTE)) == GAP_ANSWER
    assert drop_trailing_gap(f"74 m³ [1].\n\n{GAP_ANSWER}") == "74 m³ [1]."


def test_english_answers_and_dot_decimals_are_recognized():
    assert is_english(H1_ENGLISH)
    assert not is_english(VERDICT) and not is_english(S3_WITH_PLAN)
    assert unsupported_numbers(H1_ENGLISH, ["HT 33,50 ct/kWh, NT 24,10 ct/kWh"]) == []


def test_years_alone_need_no_citation():
    assert not needs_citation(strip_step_talk(H3_WITH_PLAN))
    assert needs_citation("Der Verbrauch betrug 74 m³.")


# --- Loop -----------------------------------------------------------------------------------


def test_plan_written_as_text_is_questioned_and_the_tool_runs_next(tmp_path: Path):
    # Arrange: S2 of run-025 answered with its plan instead of calling check_bill
    replies = [
        tool_reply(("get_facts", {"fact": "preise", "tariff_kind": "heating", "year": 2025})),
        answer_reply(S2_PLAN_ONLY),
        tool_reply(CHECK),
        answer_reply(VERDICT),
    ]
    loop, _ = _loop(tmp_path, replies)

    # Act
    run = loop.run(AUDIT)

    # Assert
    assert _nudges(run) == ["steps"]
    assert run.called_tools == ("get_facts", "check_bill")
    assert run.answer == VERDICT and not run.is_fallback_answer


def test_no_plan_hint_is_added_to_tool_results(tmp_path: Path):
    replies = [tool_reply(CHECK), answer_reply(VERDICT)]
    loop, chat = _loop(tmp_path, replies)
    loop.run(AUDIT)
    tool_messages = [m for m in chat.requests[-1]["messages"] if m.get("role") == "tool"]
    assert tool_messages and "plan" not in tool_messages[0]["content"].split("\n")[-1]


def test_empty_answer_gets_one_answer_call_without_tools(tmp_path: Path):
    # Arrange: S1 and Z3 of run-025 ended with an empty answer
    replies = [tool_reply(CHECK), answer_reply(""), answer_reply(VERDICT)]
    loop, chat = _loop(tmp_path, replies)

    # Act
    run = loop.run(AUDIT)

    # Assert
    assert _nudges(run) == ["empty"]
    assert "tools" not in chat.requests[-1]
    assert run.answer == VERDICT and run.stop_reason == "answer"


def test_self_check_question_cannot_make_the_answer_worse(tmp_path: Path):
    # Arrange: G4 of run-025 had the right verdict, then the plan check led to a gap answer
    replies = [
        tool_reply(("plan", {"steps": ["check_bill Heizstrom 2025", "get_facts Heizstrom"]})),
        tool_reply(CHECK),
        answer_reply(VERDICT),
        answer_reply(G4_ANNOUNCE),
    ]
    loop, _ = _loop(tmp_path, replies)

    # Act
    run = loop.run(AUDIT)

    # Assert
    assert _nudges(run) == ["plan"]
    assert run.answer == VERDICT and run.is_fallback_answer


def test_gap_after_a_self_check_question_keeps_the_answer(tmp_path: Path):
    replies = [
        tool_reply(("plan", {"steps": ["check_bill Heizstrom 2025", "get_facts Heizstrom"]})),
        tool_reply(CHECK),
        answer_reply(VERDICT),
        answer_reply(f"{GAP_ANSWER} Es wurde bereits gezeigt, dass die Rechnung falsch ist."),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run(AUDIT)
    assert run.answer == VERDICT and run.is_fallback_answer


def test_a_wrong_verdict_is_never_the_fallback(tmp_path: Path):
    replies = [
        tool_reply(CHECK),
        answer_reply("Ja, die Heizstromabrechnung 2025 stimmt [1]."),
        answer_reply(""),
        answer_reply(""),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run(AUDIT)
    assert _nudges(run) == ["verdict", "empty"]
    assert run.answer == "" and run.stop_reason == "empty_answer"


def test_repeated_calls_force_an_answer(tmp_path: Path):
    # Arrange: N1 of run-025 alternated between the same calls until the tool limit
    same = ("list_documents", {"utility_type": "electricity", "doc_type": "bill", "year": 2023})
    replies = [tool_reply(same)] * (REPEAT_LIMIT + 1) + [answer_reply(GAP_ANSWER)]
    loop, chat = _loop(tmp_path, replies)

    # Act
    run = loop.run("Wie hoch war meine Stromrechnung 2023?")

    # Assert
    assert run.stop_reason == "repeat_limit"
    assert run.tool_call_count == REPEAT_LIMIT + 1
    assert "tools" not in chat.requests[-1]


def test_gap_answer_needs_a_full_text_search_first(tmp_path: Path):
    # Arrange: S4 of run-025 gave up after get_facts and list_documents; the values stood in
    # the consumption chart of a bill, which only search finds
    replies = [
        tool_reply(("get_facts", {"fact": "verbrauch", "tariff_kind": "heating", "year": 2022})),
        tool_reply(("list_documents", {"utility_type": "electricity", "year": 2022})),
        answer_reply(GAP_ANSWER),
        tool_reply(("search", {"query": "Verbrauch Vorjahr 2022 Diagramm"})),
        answer_reply("2022 waren es 3.480 kWh [1]."),
    ]
    loop, _ = _loop(tmp_path, replies)

    # Act
    run = loop.run("Wie hoch war der Heizstromverbrauch 2022?")

    # Assert
    assert _nudges(run) == ["gap"]
    assert run.called_tools[-1] == "search" and run.answer.startswith("2022")


def test_english_answer_is_questioned_once(tmp_path: Path):
    replies = [
        tool_reply(("get_facts", {"fact": "arbeitspreis", "tariff_kind": "heating", "year": 2025})),
        answer_reply(H1_ENGLISH),
        answer_reply("HT 33,50 ct/kWh [2], NT 24,10 ct/kWh [4]."),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run("Welche HT- und NT-Arbeitspreise gelten 2025 für den Heizstrom?")
    assert _nudges(run) == ["language"]
    assert run.answer.startswith("HT 33,50")


def test_the_question_scope_is_reset_after_an_error(tmp_path: Path):
    loop, _ = _loop(tmp_path, [])
    with pytest.raises(IndexError):
        loop.run(AUDIT)
    assert CURRENT_QUESTION.get() == ""


# --- Argument repair ------------------------------------------------------------------------


def _validate(model, question: str, data: dict):
    token = CURRENT_QUESTION.set(question)
    try:
        return model.model_validate(data)
    finally:
        CURRENT_QUESTION.reset(token)


def test_a_year_the_question_does_not_name_is_dropped():
    from audit_agent.agent.fact_tools import BillArguments, FactsArguments

    current = _validate(
        FactsArguments,
        "Wie hoch ist mein aktueller monatlicher Stromabschlag?",
        {"fact": "abschlag", "utility_type": "electricity", "year": 2023},
    )
    named = _validate(
        FactsArguments,
        "Welche HT- und NT-Arbeitspreise gelten 2025 für den Heizstrom?",
        {"fact": "arbeitspreis", "tariff_kind": "heating", "year": 2025},
    )
    bill = _validate(
        BillArguments, "Stimmt meine Gasrechnung?", {"utility_type": "gas", "year": 2025}
    )
    assert current.year is None and named.year == 2025
    assert bill.year == 2025  # check_bill needs a year; the model's choice stays


def test_fernwaerme_in_the_question_stays_fernwaerme():
    from audit_agent.agent.fact_tools import FactsArguments

    data = {"fact": "grundpreis", "utility_type": "district_heating", "tariff_kind": "heating"}
    asked = _validate(FactsArguments, "Welchen Grundpreis zahle ich für Fernwärme?", data)
    confused = _validate(FactsArguments, "Welchen Grundpreis hat der Heizstrom?", data)
    assert (asked.utility_type, asked.tariff_kind) == ("district_heating", None)
    assert (confused.utility_type, confused.tariff_kind) == ("electricity", "heating")


def test_tables_and_charts_take_their_scope_from_the_question():
    from audit_agent.agent.fact_tools import ViewArguments

    overview = _validate(
        ViewArguments,
        "Gib mir eine Übersicht über alle Kosten 2025.",
        {"topic": "kosten", "utility_type": "electricity", "from_year": 2025, "to_year": 2025},
    )
    chart = _validate(
        ViewArguments,
        "Erstelle eine Grafik zum Stromverbrauch 2024 und 2025, getrennt nach Licht- und "
        "Heizstrom.",
        {"topic": "verbrauch", "utility_type": "electricity", "tariff_kind": "household"},
    )
    gas = _validate(
        ViewArguments,
        "Wie haben sich die Gaspreise entwickelt? Zeig das als Grafik.",
        {"topic": "preise", "utility_type": "gas"},
    )
    assert overview.utility_type is None
    assert (chart.utility_type, chart.tariff_kind) == ("electricity", None)
    assert gas.utility_type == "gas"
