"""Fixed audit flow (ADR-0016): plan, search, read, compute, with fakes and without Ollama."""

import json

import pytest

from audit_agent.agent import AgentLoop, ToolBox, ToolCallStep
from audit_agent.agent.audit_flow import (
    PLAN_SCHEMA,
    READING_SCHEMA,
    render_findings,
    run_audit_flow,
)
from audit_agent.agent.models import AuditCheckResult, AuditFlowStep, ModelCallStep, NudgeStep
from audit_agent.config import AgentSettings, Settings
from tests.agent_fakes import (
    BILL_FILE,
    CONTRACT_FILE,
    FakeBackend,
    ScriptedChat,
    answer_reply,
    make_catalog,
    make_hit,
)

QUESTION = "Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?"
TARGET_TEXT = "Preisblatt\nArbeitspreis | 38,20 ct/kWh brutto"
ACTUAL_TEXT = "Rechnung\nArbeitspreis | 3.100 kWh | 39,50 ct/kWh"


def _plan(*checks: tuple[str, str, str]) -> str:
    return json.dumps(
        {"checks": [{"quantity": q, "target_query": t, "actual_query": a} for q, t, a in checks]}
    )


def _reading(target: str, target_hit: int, actual: str, actual_hit: int, unit="ct/kWh") -> str:
    return json.dumps(
        {
            "target_value": target,
            "target_hit": target_hit,
            "actual_value": actual,
            "actual_hit": actual_hit,
            "unit": unit,
        }
    )


def _step(tool: str, hits: tuple[int, ...] = (), observation: str = "", valid: bool = True):
    return ToolCallStep(
        index=0,
        tool=tool,
        arguments={},
        is_valid=valid,
        observation=observation,
        seconds=0.0,
        hit_numbers=hits,
    )


class _Flow:
    """Scripted pieces of the flow: model answers in order, searches by query, hit texts."""

    def __init__(self, replies, searches, texts):
        self._replies = list(replies)
        self._searches = searches
        self._texts = texts
        self.schemas = []
        self.tool_calls = []

    def ask_model(self, messages, schema):
        self.schemas.append(schema)
        return self._replies.pop(0)

    def run_tool(self, name, arguments):
        self.tool_calls.append((name, arguments))
        if name == "calculate":
            left, right = arguments["expression"].split(" - ")
            value = round(float(left) - float(right), 6)
            return _step("calculate", observation=f"{arguments['expression']} = {value:g}")
        return self._searches[arguments["query"]]

    def hit_content(self, number):
        return self._texts.get(number, "")

    def run(self, max_checks=3):
        return run_audit_flow(QUESTION, self.ask_model, self.run_tool, self.hit_content, max_checks)


def _flow(reading: str, plan: str | None = None, actual_text: str = ACTUAL_TEXT) -> _Flow:
    plan = plan or _plan(("Arbeitspreis", "Arbeitspreis Preisschreiben 2025", "Arbeitspreis 2025"))
    return _Flow(
        [plan, reading],
        {
            "Arbeitspreis Preisschreiben 2025": _step("search", (1,), "[1] ..."),
            "Arbeitspreis 2025": _step("search", (2,), "[2] ..."),
        },
        {1: TARGET_TEXT, 2: actual_text},
    )


def test_deviation_is_computed_from_cited_hits():
    # Arrange
    flow = _flow(_reading("38,20", 1, "39,50", 2))

    # Act
    results, message = flow.run()

    # Assert
    (check,) = results
    assert check.status == "deviation"
    assert (check.target_value, check.actual_value) == (38.2, 39.5)
    assert check.difference == "1.3"
    assert check.target_line == "Arbeitspreis | 38,20 ct/kWh brutto"
    assert flow.tool_calls[-1] == ("calculate", {"expression": "39.5 - 38.2"})
    assert flow.schemas == [PLAN_SCHEMA, READING_SCHEMA]
    assert "ABWEICHUNG" in message and "[1]" in message and "[2]" in message


def test_equal_values_are_reported_as_equal():
    # Arrange
    flow = _flow(
        _reading("38,20", 1, "38,20", 2), actual_text="Arbeitspreis | 3.100 kWh | 38,20 ct/kWh"
    )

    # Act
    (check,), message = flow.run()

    # Assert
    assert check.status == "equal" and check.difference == "0"
    assert "gleich" in message


def test_number_that_is_not_in_the_cited_hit_is_not_used():
    # Arrange: the model invents 40,00; the hit says 39,50
    flow = _flow(_reading("38,20", 1, "40,00", 2))

    # Act
    (check,), message = flow.run()

    # Assert
    assert check.status == "not_verified" and check.difference is None
    assert all(name != "calculate" for name, _ in flow.tool_calls)
    assert "steht nicht im Treffer" in message


def test_hit_from_the_other_side_is_not_accepted():
    # Arrange: 39,50 stands in hit 2, but the target search only returned hit 1
    flow = _flow(_reading("39,50", 2, "39,50", 2))

    # Act
    (check,), _ = flow.run()

    # Assert
    assert check.status == "not_verified"


@pytest.mark.parametrize(
    "reading",
    [_reading("", 0, "39,50", 2), _reading("38,20", 1, "", 0), "kein JSON"],
)
def test_missing_value_or_broken_reading_is_not_found(reading):
    # Arrange
    flow = _flow(reading)

    # Act
    (check,), message = flow.run()

    # Assert
    assert check.status == "not_found"
    assert "nicht gefunden" in message


def test_search_without_hits_is_not_found_and_skips_the_reading():
    # Arrange
    flow = _Flow(
        [_plan(("Arbeitspreis", "a a", "b b"))],
        {"a a": _step("search", (), "Keine Treffer."), "b b": _step("search", (2,), "[2]")},
        {},
    )

    # Act
    (check,), _ = flow.run()

    # Assert
    assert check.status == "not_found" and len(flow.schemas) == 1


def test_same_query_is_searched_once_and_plan_is_cut_to_the_limit():
    # Arrange: two checks share a query, duplicate quantity, third check over the limit
    plan = _plan(
        ("Arbeitspreis", "gleiche Suche", "gleiche Suche"),
        ("arbeitspreis", "x x", "y y"),
        ("Grundpreis", "gleiche Suche", "gleiche Suche"),
        ("Verbrauch", "v v", "w w"),
    )
    shared = _step("search", (1, 2), "[1] [2]")
    flow = _Flow(
        [plan, _reading("38,20", 1, "39,50", 2), _reading("38,20", 1, "39,50", 2)],
        {"gleiche Suche": shared},
        {1: TARGET_TEXT, 2: ACTUAL_TEXT},
    )

    # Act
    results, _ = flow.run(max_checks=2)

    # Assert
    assert [check.quantity for check in results] == ["Arbeitspreis", "Grundpreis"]
    assert [name for name, _ in flow.tool_calls].count("search") == 1


def test_invalid_plan_gives_no_checks_and_no_message():
    # Arrange
    flow = _Flow(["{}"], {}, {})

    # Act
    results, message = flow.run()

    # Assert
    assert results == () and message == ""


def test_findings_name_missing_quantities():
    # Arrange
    results = (AuditCheckResult(quantity="Wohnfläche", status="not_found"),)

    # Act
    message = render_findings(results)

    # Assert
    assert "Wohnfläche" in message and "Suche selbst weiter" in message


def _flow_loop(replies, backend):
    settings = Settings(agent=AgentSettings(audit_flow_enabled=True))
    chat = ScriptedChat(replies)
    tools = ToolBox(settings, backend, make_catalog()).tools()
    return AgentLoop(settings, chat, tools), chat


def test_loop_runs_the_flow_before_the_model_answers():
    # Arrange
    def responder(query, options):
        if "Preisschreiben" in query:
            return [make_hit("c1", filename=CONTRACT_FILE, content=TARGET_TEXT)]
        return [make_hit("c2", filename=BILL_FILE, content=ACTUAL_TEXT)]

    replies = [
        answer_reply(
            _plan(("Arbeitspreis", "Arbeitspreis Preisschreiben 2025", "Arbeitspreis Rechnung"))
        ),
        answer_reply(_reading("38,20", 1, "39,50", 2)),
        answer_reply("Abweichung 1,30 ct/kWh [1][2]."),
    ]
    loop, chat = _flow_loop(replies, FakeBackend(responder))

    # Act
    run = loop.run(QUESTION)

    # Assert
    flow_steps = [s for s in run.steps if isinstance(s, AuditFlowStep)]
    assert [c.status for c in flow_steps[0].checks] == ["deviation"]
    tool_steps = [s for s in run.steps if isinstance(s, ToolCallStep)]
    assert [(s.tool, s.is_flow_call) for s in tool_steps] == [
        ("search", True),
        ("search", True),
        ("calculate", True),
    ]
    assert run.tool_call_count == 0  # flow calls do not use the model's tool budget
    assert not [s for s in run.steps if isinstance(s, NudgeStep)]  # calculated by the flow
    assert chat.requests[0]["format"] == PLAN_SCHEMA and "tools" not in chat.requests[0]
    assert chat.requests[1]["format"] == READING_SCHEMA
    final = chat.requests[2]
    assert "tools" in final and "format" not in final
    assert "Prüfablauf" in final["messages"][-1]["content"]
    assert run.answer.startswith("Abweichung") and len(run.sources) == 2
    assert [s for s in run.steps if isinstance(s, ModelCallStep)][0].offered_tools is False


def test_loop_without_findings_continues_as_before():
    # Arrange: the plan is useless, the model answers directly
    loop, chat = _flow_loop(
        [answer_reply("{}"), answer_reply("Ich weiß es nicht.")], FakeBackend(lambda q, o: [])
    )

    # Act
    run = loop.run(QUESTION)

    # Assert
    assert run.answer == "Ich weiß es nicht."
    assert [m["role"] for m in chat.requests[1]["messages"]] == ["system", "user"]


def test_flow_is_skipped_for_questions_that_are_not_checks():
    # Arrange
    loop, chat = _flow_loop([answer_reply("Sechs Wochen.")], FakeBackend(lambda q, o: []))

    # Act
    run = loop.run("Welche Kündigungsfrist gilt?")

    # Assert
    assert len(chat.requests) == 1 and not [s for s in run.steps if isinstance(s, AuditFlowStep)]
