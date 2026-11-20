"""Agent v2 (M8, ADR-0019): fact tools, plan, self-check and artifacts; scripted, no Ollama."""

from __future__ import annotations

from pathlib import Path

import pytest

from audit_agent.agent.loop import AgentLoop
from audit_agent.agent.models import EvidenceBook, NudgeStep
from audit_agent.agent.prompts import unsupported_numbers, wants_chart, wants_overview
from audit_agent.agent.tools import ToolBox, ToolError
from audit_agent.config import AgentSettings, Settings
from audit_agent.corpus import DocumentCatalog
from tests.agent_fakes import FakeBackend, ScriptedChat, answer_reply, make_hit, tool_reply
from tests.test_facts import BILL, CONTRACT, LETTER, _store

CATALOG = DocumentCatalog(documents=(CONTRACT, LETTER, BILL))
CHECK = ("check_bill", {"utility_type": "electricity", "tariff_kind": "heating", "year": 2025})
PLAN = ("plan", {"steps": ["check_bill Heizstrom 2025", "Antwort mit Soll und Ist"]})


def _toolbox(tmp_path: Path) -> ToolBox:
    settings = Settings(project_root=tmp_path)
    backend = FakeBackend(lambda query, options: [make_hit()])
    return ToolBox(settings, backend, CATALOG, facts=_store(), artifact_dir=tmp_path / "charts")


def _loop(tmp_path: Path, replies, **agent_options) -> tuple[AgentLoop, ScriptedChat]:
    settings = Settings(project_root=tmp_path, agent=AgentSettings(**agent_options))
    backend = FakeBackend(lambda query, options: [make_hit()])
    tools = ToolBox(
        settings, backend, CATALOG, facts=_store(), artifact_dir=tmp_path / "charts"
    ).tools()
    chat = ScriptedChat(replies)
    return AgentLoop(settings, chat, tools), chat


def test_v2_offers_plan_first_and_the_fact_tools(tmp_path: Path):
    names = list(_toolbox(tmp_path).tools())
    assert names == [
        "plan",
        "list_documents",
        "check_bill",
        "get_facts",
        "search",
        "make_overview",
        "make_chart",
        "calculate",
    ]


def test_check_bill_tool_reports_the_deviation_with_citations(tmp_path: Path):
    # Arrange
    tool = _toolbox(tmp_path).tools()["check_bill"]
    book = EvidenceBook()

    # Act
    result = tool.run(tool.arguments.model_validate(CHECK[1]), book)

    # Assert
    assert "ABWEICHUNG: Verbrauch NT aus Zählerständen" in result.text
    assert "120,50 EUR zu Ihren Lasten" in result.text
    assert "Kurzfassung für die Antwort: Nein" in result.text
    assert "Die Rechnung stimmt nicht." in result.text
    assert result.hit_numbers and len(book.numbered_hits) == max(result.hit_numbers)


def test_check_bill_without_a_bill_says_so(tmp_path: Path):
    tool = _toolbox(tmp_path).tools()["check_bill"]
    arguments = tool.arguments.model_validate({"utility_type": "gas", "year": 2025})
    with pytest.raises(ToolError, match="liegt nicht vor"):
        tool.run(arguments, EvidenceBook())


def test_get_facts_marks_the_value_that_applies_in_the_year(tmp_path: Path):
    tool = _toolbox(tmp_path).tools()["get_facts"]
    arguments = tool.arguments.model_validate(
        {"fact": "arbeitspreis", "tariff_kind": "heating", "year": 2025}
    )
    text = tool.run(arguments, EvidenceBook()).text
    line = next(line for line in text.splitlines() if "24,10 ct/kWh" in line)
    assert "<- gilt 2025" in line
    assert "<- gilt" not in next(line for line in text.splitlines() if "22,40 ct/kWh" in line)


def test_make_chart_returns_an_artifact_with_png_and_table(tmp_path: Path):
    tool = _toolbox(tmp_path).tools()["make_chart"]
    result = tool.run(tool.arguments.model_validate({"topic": "verbrauch"}), EvidenceBook())
    (artifact,) = result.artifacts
    assert artifact.kind == "chart" and Path(artifact.image_path).is_file()
    assert "| Heizstrom NT | 2025 | 3.420 kWh" in artifact.markdown


def test_loop_records_plan_artifacts_and_answers(tmp_path: Path):
    # Arrange
    replies = [
        tool_reply(("plan", {"steps": ["make_chart Verbrauch"]})),
        tool_reply(("make_chart", {"topic": "verbrauch"})),
        answer_reply("Die Grafik zeigt 580 kWh HT und 3.420 kWh NT [1][2]."),
    ]
    loop, _ = _loop(tmp_path, replies)

    # Act
    run = loop.run("Zeig mir den Heizstromverbrauch als Grafik.")

    # Assert
    assert run.plan == ("make_chart Verbrauch",)
    assert [a.kind for a in run.artifacts] == ["chart"]
    assert not [s for s in run.steps if isinstance(s, NudgeStep)]


def test_audit_question_without_check_bill_is_questioned_once(tmp_path: Path):
    # Arrange
    replies = [
        tool_reply(("search", {"query": "Heizstrom 2025"})),
        answer_reply("Ja, die Rechnung stimmt [1]."),
        tool_reply(CHECK),
        answer_reply("Nein: NT 3.920 statt 3.420 kWh, 120,50 EUR zu viel [3]."),
    ]
    loop, chat = _loop(tmp_path, replies)

    # Act
    run = loop.run("Ist die Heizstromabrechnung 2025 korrekt?")

    # Assert
    nudges = [s.reason for s in run.steps if isinstance(s, NudgeStep)]
    assert nudges == ["check"]
    assert run.answer.startswith("Nein")


def test_chart_request_without_chart_is_questioned(tmp_path: Path):
    replies = [
        tool_reply(("get_facts", {"fact": "verbrauch", "tariff_kind": "heating"})),
        answer_reply("Verbrauch NT 3.920 kWh [1]."),
        tool_reply(("make_chart", {"topic": "verbrauch"})),
        answer_reply("Die Grafik zeigt den Verbrauch [2]."),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run("Erstelle ein Diagramm zum Heizstromverbrauch.")
    assert [s.reason for s in run.steps if isinstance(s, NudgeStep)] == ["chart"]
    assert run.artifacts


def test_numbers_without_source_are_questioned_once(tmp_path: Path):
    replies = [
        tool_reply(("get_facts", {"fact": "arbeitspreis", "tariff_kind": "heating", "year": 2025})),
        answer_reply("Der NT-Preis beträgt 26,40 ct/kWh [1]."),
        answer_reply("Der NT-Preis beträgt 24,10 ct/kWh [1]."),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run("Welcher NT-Preis gilt 2025 für den Heizstrom?")
    nudges = [s for s in run.steps if isinstance(s, NudgeStep)]
    assert [n.reason for n in nudges] == ["numbers"] and "26,4" in nudges[0].message
    assert "24,10" in run.answer


def test_follow_up_question_sees_the_history(tmp_path: Path):
    replies = [
        tool_reply(("make_chart", {"topic": "kosten"})),
        answer_reply("Grafik erstellt [1]."),
    ]
    loop, chat = _loop(tmp_path, replies)
    loop.run(
        "und jetzt als Grafik?", history=[("Was kostete Heizstrom 2025?", "1.257,82 EUR [1].")]
    )
    messages = chat.requests[0]["messages"]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]


def test_unsupported_numbers_ignore_years_counts_dates_and_cent_euro_scaling():
    sources = ["Arbeitspreis 33,50 ct/kWh, Betrag 194,30 EUR"]
    answer = (
        "2025 galt ab 01.01.2025 ein Preis von 0,335 EUR/kWh [1]; 3 Zonen; 194,30 EUR; 99,99 EUR."
    )
    assert unsupported_numbers(answer, sources) == ["99,99"]


def test_request_detection_for_charts_and_overviews():
    assert wants_chart("Zeig das als Diagramm") and not wants_overview("Zeig das als Diagramm")
    assert wants_overview("Gib mir eine Übersicht über alle Kosten 2025")


def test_arguments_from_the_smoke_test_are_repaired(tmp_path: Path):
    # Arrange: the three wrong calls of run-023 (ISS-114)
    replies = [
        tool_reply(
            (
                "check_bill",
                {"utility_type": "district_heating", "year": 2025, "tariff_kind": "heating"},
            )
        ),
        answer_reply("Nein, NT 3.920 statt 3.420 kWh, 120,50 EUR zu viel [1]."),
    ]
    loop, _ = _loop(tmp_path, replies)

    # Act
    run = loop.run("Ist die Heizstromabrechnung 2025 korrekt?")

    # Assert
    (step,) = [s for s in run.steps if getattr(s, "tool", "") == "check_bill"]
    assert step.is_valid and step.observation.startswith("Hinweis: Argumente angepasst")
    assert "ABWEICHUNG" in step.observation


def test_repair_drops_tariff_for_water_and_both_tariffs_and_fills_from_question():
    from audit_agent.agent.fact_tools import BillArguments, ViewArguments
    from audit_agent.agent.scope import CURRENT_QUESTION

    token = CURRENT_QUESTION.set("Ist der Heizstromabrechnung 2025 korrekt?")
    try:
        water = BillArguments.model_validate(
            {"utility_type": "water", "year": 2026, "tariff_kind": "household"}
        )
        both = ViewArguments.model_validate(
            {"topic": "verbrauch", "tariff_kind": "household,heating"}
        )
        filled = BillArguments.model_validate({})
    finally:
        CURRENT_QUESTION.reset(token)
    assert water.tariff_kind is None and water.utility_type == "water"
    assert both.tariff_kind is None
    assert (filled.utility_type, filled.tariff_kind, filled.year) == (
        "electricity",
        "heating",
        2025,
    )


def test_trailing_gap_sentence_after_a_real_answer_is_dropped():
    from audit_agent.agent.prompts import GAP_ANSWER, drop_trailing_gap

    assert drop_trailing_gap(f"3.420 kWh [1].\n\n{GAP_ANSWER}") == "3.420 kWh [1]."
    assert drop_trailing_gap(GAP_ANSWER) == GAP_ANSWER


def test_routing_offers_tools_by_question_type():
    from audit_agent.agent.scope import route_tools

    audit = route_tools("Ist die Heizstromabrechnung 2025 korrekt?", "")
    chart = route_tools("und jetzt?", "Zeig den Verbrauch als Grafik. und jetzt?")
    fact = route_tools("Welche Kündigungsfrist gilt?", "")
    assert "check_bill" in audit and "make_chart" not in audit
    assert "make_chart" in chart and "check_bill" not in chart
    assert {"get_facts", "search"} <= fact and "check_bill" not in fact


def test_offered_specs_follow_the_route(tmp_path: Path):
    replies = [answer_reply("Dazu liegen in den Unterlagen keine Angaben vor.")] * 2
    loop, chat = _loop(tmp_path, replies)
    loop.run("Erstelle ein Diagramm zum Wasserverbrauch.")
    offered = [spec["function"]["name"] for spec in chat.requests[0]["tools"]]
    assert offered == ["plan", "list_documents", "get_facts", "make_chart", "calculate"]


def test_planned_result_tool_that_never_ran_is_questioned(tmp_path: Path):
    replies = [
        tool_reply(("plan", {"steps": ["get_facts Verbrauch", "make_chart Verbrauch"]})),
        tool_reply(("get_facts", {"fact": "verbrauch", "tariff_kind": "heating"})),
        answer_reply("NT 3.420 kWh [1]."),
        tool_reply(("make_chart", {"topic": "verbrauch"})),
        answer_reply("Die Grafik zeigt den Verbrauch [3]."),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run("Wie hoch war der Heizstromverbrauch?")
    assert [s.reason for s in run.steps if isinstance(s, NudgeStep)] == ["plan"]
    assert run.artifacts


def test_verdict_against_check_bill_is_questioned(tmp_path: Path):
    replies = [
        tool_reply(CHECK),
        answer_reply("Ja, die Heizstromabrechnung 2025 stimmt [1]."),
        answer_reply(
            "Nein, die Heizstrom-Rechnung 2025 stimmt nicht: NT 3.920 statt 3.420 kWh [1]."
        ),
    ]
    loop, _ = _loop(tmp_path, replies)
    run = loop.run("Ist die Heizstromabrechnung 2025 korrekt?")
    assert [s.reason for s in run.steps if isinstance(s, NudgeStep)] == ["verdict"]
    assert run.answer.startswith("Nein")


def test_answer_verdict_detection():
    from audit_agent.agent.prompts import answer_says_correct

    assert answer_says_correct("Nein, die Rechnung stimmt nicht. Ja doch.") is False
    assert answer_says_correct("Ja, die Rechnung ist korrekt [1].") is True
    assert answer_says_correct("Der Verbrauch beträgt 72 m³ [1].") is None


def test_plain_strom_means_household_and_seit_keeps_the_end_open():
    from audit_agent.agent.fact_tools import FactsArguments, ViewArguments
    from audit_agent.agent.scope import CURRENT_QUESTION

    token = CURRENT_QUESTION.set(
        "Wie haben sich die Gaspreise seit 2024 entwickelt? Mein Stromabschlag?"
    )
    try:
        view = ViewArguments.model_validate({"topic": "preise", "from_year": 2024, "to_year": 2024})
        facts = FactsArguments.model_validate({"fact": "abschlag", "utility_type": "electricity"})
    finally:
        CURRENT_QUESTION.reset(token)
    assert view.to_year is None
    assert facts.tariff_kind == "household"
