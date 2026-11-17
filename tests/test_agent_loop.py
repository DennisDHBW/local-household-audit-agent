"""Agent loop, step log, report and evidence view with a scripted chat client."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from audit_agent.agent import (
    AgentLoop,
    AgentRun,
    EvidenceBook,
    ModelCallStep,
    NumberedHit,
    ToolBox,
    ToolCallStep,
)
from audit_agent.agent.evidence_view import evidence_sections
from audit_agent.agent.log import RunLog
from audit_agent.agent.loop import LIMIT_OBSERVATION, estimate_tokens
from audit_agent.agent.models import NudgeStep
from audit_agent.agent.prompts import (
    CALCULATE_BEFORE_ANSWER_MESSAGE,
    CITE_BEFORE_ANSWER_MESSAGE,
    FORCED_ANSWER_MESSAGE,
    GAP_ANSWER,
    REPEAT_FAILED_OBSERVATION,
    REPEAT_OBSERVATION,
    RETRY_BEFORE_GAP_MESSAGE,
    is_audit_question,
    is_gap_answer,
    system_prompt,
)
from audit_agent.agent.report import evaluate_run, render_markdown
from audit_agent.config import AgentSettings, Settings
from audit_agent.corpus import ExpectedFact, Question, QuestionCategory, SourceRef
from audit_agent.evaluation.metrics import is_fact_in_answer
from audit_agent.ingestion import ChunkType
from audit_agent.retrieval import RetrievalError
from tests.agent_fakes import (
    BILL_FILE,
    CONTRACT_FILE,
    FakeBackend,
    ScriptedChat,
    answer_reply,
    make_catalog,
    make_hit,
    tool_reply,
)

SEARCH = ("search", {"query": "Arbeitspreis"})
CALCULATE = ("calculate", {"expression": "2*3"})


def _loop(replies, backend=None, is_flow_enabled=False, **settings_options):
    """Loop with scripted replies; the audit flow is off unless a test asks for it (ADR-0016)."""
    agent = settings_options.pop("agent", AgentSettings())
    agent = agent.model_copy(update={"audit_flow_enabled": is_flow_enabled})
    settings = Settings(agent=agent, **settings_options)
    backend = backend or FakeBackend(lambda query, options: [make_hit()])
    chat = ScriptedChat(replies)
    tools = ToolBox(settings, backend, make_catalog()).tools()
    return AgentLoop(settings, chat, tools), chat


def test_direct_answer_without_tools():
    # Arrange
    loop, chat = _loop([answer_reply("Das weiß ich nicht.")])

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.answer == "Das weiß ich nicht."
    assert run.stop_reason == "answer" and run.tool_call_count == 0
    assert [type(step) for step in run.steps] == [ModelCallStep]
    assert len(chat.requests[0]["tools"]) == 5
    assert chat.requests[0]["messages"][0]["role"] == "system"
    assert chat.requests[0]["messages"][1] == {"role": "user", "content": "Frage?"}


def test_tool_call_observation_goes_back_to_the_model():
    # Arrange
    loop, chat = _loop([tool_reply(CALCULATE), answer_reply("Ergebnis 6 [1].")])

    # Act
    run = loop.run("Was ist 2*3?")

    # Assert
    assert run.answer == "Ergebnis 6 [1]." and run.tool_call_count == 1
    assert [step.kind for step in run.steps] == ["model_call", "tool_call", "model_call"]
    tool_message = chat.requests[1]["messages"][-1]
    assert tool_message == {"role": "tool", "tool_name": "calculate", "content": "2*3 = 6"}
    assert chat.requests[1]["messages"][-2].tool_calls[0].function.name == "calculate"
    assert run.called_tools == ("calculate",)


def test_search_hits_become_numbered_sources():
    # Arrange
    loop, _ = _loop([tool_reply(SEARCH), answer_reply("34,80 ct/kWh [1].")])

    # Act
    run = loop.run("Arbeitspreis?")

    # Assert
    assert [(s.number, s.hit.chunk_id) for s in run.sources] == [(1, "c1")]
    tool_step = run.steps[1]
    assert isinstance(tool_step, ToolCallStep) and tool_step.hit_numbers == (1,)


def test_invalid_arguments_and_unknown_tools_become_error_observations():
    # Arrange
    replies = [
        tool_reply(("search", {"doc_type": "Rechnung"})),
        tool_reply(("make_coffee", {})),
        answer_reply("Fertig."),
    ]
    loop, chat = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    first, second = run.steps[1], run.steps[3]
    assert not first.is_valid and "Ungültige Argumente für search" in first.observation
    assert "query" in first.observation and "Pflicht" in first.observation
    assert "Richtiger Aufruf: search(" in first.observation
    assert not second.is_valid and "Unbekanntes Werkzeug 'make_coffee'" in second.observation
    assert run.tool_call_count == 2  # invalid calls count against the limit
    assert chat.requests[1]["messages"][-1]["content"] == first.observation


def test_tool_errors_become_observations():
    # Arrange
    loop, _ = _loop([tool_reply(("calculate", {"expression": "abs(1)"})), answer_reply("ok")])

    # Act
    step = loop.run("Frage?").steps[1]

    # Assert
    assert not step.is_valid and step.observation.startswith("FEHLER: Rechnung nicht möglich")


def test_tool_limit_forces_an_answer_without_tools():
    # Arrange
    replies = [tool_reply(CALCULATE), tool_reply(CALCULATE), answer_reply("Mit den Belegen: 6.")]
    loop, chat = _loop(replies, agent=AgentSettings(max_tool_calls=2))

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.stop_reason == "tool_limit" and run.tool_call_count == 2
    assert run.answer == "Mit den Belegen: 6."
    assert "tools" in chat.requests[1] and "tools" not in chat.requests[2]
    assert chat.requests[2]["messages"][-1] == {"role": "user", "content": FORCED_ANSWER_MESSAGE}
    assert run.steps[-1].offered_tools is False


def test_calls_beyond_the_limit_in_one_reply_are_refused_but_answered():
    # Arrange
    replies = [tool_reply(CALCULATE, CALCULATE), answer_reply("Antwort.")]
    loop, chat = _loop(replies, agent=AgentSettings(max_tool_calls=1))

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.tool_call_count == 1
    contents = [m["content"] for m in chat.requests[1]["messages"] if isinstance(m, dict)]
    assert contents.count(LIMIT_OBSERVATION) == 1


def test_context_guard_stops_searching_when_the_window_is_nearly_full():
    # Arrange: the tool schemas alone (about 2000 tokens) leave no room in a 4096 window
    loop, chat = _loop([tool_reply(CALCULATE), answer_reply("Notantwort.")], num_ctx=4096)

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.stop_reason == "context_limit" and run.answer == "Notantwort."
    assert "tools" not in chat.requests[1]


def test_context_guard_leaves_the_default_window_alone_after_one_small_call():
    # Arrange
    loop, chat = _loop([tool_reply(CALCULATE), answer_reply("Sechs.")])

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.stop_reason == "answer" and "tools" in chat.requests[1]


def test_gap_answer_after_one_search_is_questioned_once():
    # Arrange
    replies = [
        tool_reply(SEARCH),
        answer_reply(GAP_ANSWER),
        tool_reply(("list_documents", {})),
        answer_reply("Gefunden: 34,80 ct/kWh [1]."),
    ]
    loop, chat = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.answer == "Gefunden: 34,80 ct/kWh [1]." and run.stop_reason == "answer"
    assert [step.kind for step in run.steps].count("nudge") == 1
    nudge_request = chat.requests[2]["messages"]
    assert nudge_request[-1] == {"role": "user", "content": RETRY_BEFORE_GAP_MESSAGE}
    assert nudge_request[-2].content == GAP_ANSWER
    assert run.tool_call_count == 2


def test_gap_answer_is_accepted_after_enough_searches_and_not_questioned_twice():
    # Arrange
    enough = [tool_reply(SEARCH), tool_reply(("list_documents", {})), answer_reply(GAP_ANSWER)]
    twice = [answer_reply(GAP_ANSWER), answer_reply(GAP_ANSWER)]

    # Act
    after_two_calls = _loop(enough)[0].run("Frage?")
    questioned_once = _loop(twice)[0].run("Frage?")

    # Assert
    assert "nudge" not in [step.kind for step in after_two_calls.steps]
    assert after_two_calls.answer == GAP_ANSWER
    assert [step.kind for step in questioned_once.steps].count("nudge") == 1
    assert questioned_once.answer == GAP_ANSWER


AUDIT_QUESTION = "Ist die Gasabrechnung 2026 korrekt?"


def test_repeated_call_is_not_run_again_and_counts_against_the_limit():
    # Arrange: the second call has the same arguments plus an empty filter the model made up
    first_call = ("search", {"query": "Arbeitspreis", "utility_type": "electricity"})
    second_call = ("search", {"query": "Arbeitspreis", "utility_type": "electricity", "year": ""})
    backend = FakeBackend(lambda query, options: [make_hit()])
    loop, chat = _loop(
        [tool_reply(first_call), tool_reply(second_call), answer_reply("Fertig.")], backend=backend
    )

    # Act
    run = loop.run("Frage?")

    # Assert
    first, second = run.steps[1], run.steps[3]
    assert not first.is_repeat and first.state == "ok"
    assert second.is_repeat and second.is_valid and second.state == "Wiederholung"
    assert second.observation == REPEAT_OBSERVATION and second.hit_numbers == ()
    assert len(backend.calls) == 1
    assert run.tool_call_count == 2
    assert chat.requests[2]["messages"][-1]["content"] == REPEAT_OBSERVATION


def test_other_arguments_or_tools_are_no_repeat():
    # Arrange
    replies = [
        tool_reply(SEARCH),
        tool_reply(("search", {"query": "Grundpreis"})),
        tool_reply(("search_images", {"query": "Arbeitspreis"})),
        answer_reply("Fertig."),
    ]
    loop, _ = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    tool_steps = [step for step in run.steps if isinstance(step, ToolCallStep)]
    assert [step.is_repeat for step in tool_steps] == [False, False, False]


TEXT_CALL = 'Ich werde danach suchen. {"name": "search", "parameters": {"query": "Abschlag"}}'


def test_tool_call_written_as_text_is_run_like_a_native_call():
    # Arrange: S5 of RUN-013 ended its message with the call as text
    backend = FakeBackend(lambda query, options: [make_hit()])
    loop, chat = _loop(
        [answer_reply(TEXT_CALL), answer_reply("34,80 ct/kWh [1].")], backend=backend
    )

    # Act
    run = loop.run("Wie hoch ist der Arbeitspreis?")

    # Assert
    tool_step = next(step for step in run.steps if isinstance(step, ToolCallStep))
    assert tool_step.tool == "search" and tool_step.is_valid and tool_step.is_text_call
    assert tool_step.arguments == {"query": "Abschlag"} and tool_step.hit_numbers == (1,)
    assert backend.calls[0][0] == "Abschlag"
    assert run.tool_call_count == 1 and run.answer == "34,80 ct/kWh [1]."
    assert run.sources[0].number == 1 and run.stop_reason == "answer"
    last_message = chat.requests[1]["messages"][-1]
    assert last_message["role"] == "tool" and last_message["tool_name"] == "search"


def test_native_calls_are_no_text_calls():
    # Arrange
    loop, _ = _loop([tool_reply(SEARCH), answer_reply("Fertig.")])

    # Act
    run = loop.run("Frage?")

    # Assert
    assert [step.is_text_call for step in run.steps if isinstance(step, ToolCallStep)] == [False]


def test_text_that_is_no_valid_call_stays_the_answer():
    # Arrange: unknown tool, and a call text after the tool limit (no tools are offered then)
    unknown = [answer_reply('{"name": "web_search", "parameters": {"query": "a"}}')]
    at_limit = [tool_reply(SEARCH), answer_reply(TEXT_CALL)]

    # Act
    unknown_run = _loop(unknown)[0].run("Frage?")
    limit_run = _loop(at_limit, agent=AgentSettings(max_tool_calls=1))[0].run("Frage?")

    # Assert
    assert unknown_run.tool_call_count == 0 and unknown_run.answer.startswith("{")
    assert limit_run.tool_call_count == 1 and limit_run.answer == TEXT_CALL
    assert limit_run.stop_reason == "tool_limit"


def test_text_call_counts_against_the_limit_and_the_repeat_guard():
    # Arrange: the same call as native call, then as text
    replies = [tool_reply(("search", {"query": "Abschlag"})), answer_reply(TEXT_CALL)]
    replies.append(answer_reply("Fertig."))
    loop, _ = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    first, second = [step for step in run.steps if isinstance(step, ToolCallStep)]
    assert not first.is_repeat and second.is_repeat and second.is_text_call
    assert run.tool_call_count == 2


def test_identical_invalid_call_is_not_answered_with_the_same_error_again():
    # Arrange: G4 of RUN-013 called calculate twice with the same wrong arguments
    wrong = ("calculate", {"a": "1.963,28", "b": "-1.920,00"})
    other_wrong = ("calculate", {"a": "1", "b": "2"})
    replies = [tool_reply(wrong), tool_reply(wrong), tool_reply(other_wrong), answer_reply("Ok.")]
    loop, chat = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    first, second, third = [step for step in run.steps if isinstance(step, ToolCallStep)]
    assert not first.is_valid and not first.is_repeat and first.state == "FEHLER"
    assert "expression" in first.observation
    assert not second.is_valid and second.is_repeat and second.state == "FEHLER (Wiederholung)"
    assert second.observation == REPEAT_FAILED_OBSERVATION
    assert not third.is_repeat and "expression" in third.observation
    assert run.tool_call_count == 3
    assert chat.requests[2]["messages"][-1]["content"] == REPEAT_FAILED_OBSERVATION


def test_repeated_tool_error_is_blocked_and_a_corrected_call_runs():
    # Arrange
    missing = ("get_document_outline", {"filename": "gibtesnicht"})
    calculate_wrong = ("calculate", {"a": "6", "b": "2"})
    calculate_right = ("calculate", {"a": "6", "b": "2", "operator": "/"})
    replies = [
        tool_reply(missing),
        tool_reply(missing),
        tool_reply(calculate_wrong),
        tool_reply(calculate_right),
        answer_reply("3 [1]."),
    ]
    loop, _ = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    steps = [step for step in run.steps if isinstance(step, ToolCallStep)]
    assert [(s.is_valid, s.is_repeat) for s in steps] == [
        (False, False),
        (False, True),
        (False, False),
        (True, False),
    ]
    assert steps[3].observation == "6 / 2 = 3"


def test_audit_question_answered_without_calculate_is_questioned_once():
    # Arrange
    replies = [
        tool_reply(SEARCH),
        answer_reply("Die Abrechnung ist korrekt."),
        tool_reply(CALCULATE),
        answer_reply("Abweichung 6 EUR [1]."),
    ]
    loop, chat = _loop(replies)

    # Act
    run = loop.run(AUDIT_QUESTION)

    # Assert
    nudges = [step for step in run.steps if isinstance(step, NudgeStep)]
    assert [nudge.reason for nudge in nudges] == ["calculate"]
    assert nudges[0].label == "Rückfrage: Prüffrage ohne calculate beantwortet"
    assert chat.requests[2]["messages"][-1]["content"] == CALCULATE_BEFORE_ANSWER_MESSAGE
    assert run.answer == "Abweichung 6 EUR [1]." and run.tool_call_count == 2


def test_calculate_nudge_is_not_repeated_and_the_second_answer_is_accepted():
    # Arrange
    replies = [tool_reply(SEARCH), answer_reply("Korrekt."), answer_reply("Wirklich korrekt.")]
    loop, _ = _loop(replies)

    # Act
    run = loop.run(AUDIT_QUESTION)

    # Assert
    assert [step.kind for step in run.steps].count("nudge") == 1
    assert run.answer == "Wirklich korrekt." and run.stop_reason == "answer"


def test_calculate_nudge_is_skipped_when_it_would_not_help():
    # Arrange
    calculated = [tool_reply(SEARCH), tool_reply(CALCULATE), answer_reply("Abweichung 6 EUR [1].")]
    single_fact = [tool_reply(SEARCH), answer_reply("34,80 ct/kWh [1].")]
    no_search = [answer_reply("Das weiß ich nicht.")]
    gap = [tool_reply(SEARCH), tool_reply(("list_documents", {})), answer_reply(GAP_ANSWER)]

    # Act
    runs = [
        _loop(calculated)[0].run(AUDIT_QUESTION),
        _loop(single_fact)[0].run("Wie hoch ist der Arbeitspreis?"),
        _loop(no_search)[0].run(AUDIT_QUESTION),
        _loop(gap)[0].run(AUDIT_QUESTION),
    ]

    # Assert
    for run in runs:
        assert "nudge" not in [step.kind for step in run.steps]


def test_repeated_calculate_does_not_count_as_calculated():
    # Arrange: the first calculate counts, the identical second one is blocked, no nudge follows
    replies = [tool_reply(CALCULATE), tool_reply(CALCULATE), answer_reply("Ergebnis 6 [1].")]
    loop, _ = _loop(replies)

    # Act
    run = loop.run(AUDIT_QUESTION)

    # Assert
    assert "nudge" not in [step.kind for step in run.steps]
    assert run.steps[3].is_repeat


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Stimmt die Stromabrechnung 2024 mit den Vertragspreisen überein?", True),
        ("Wurde in der Stromabrechnung 2025 der angekündigte neue Arbeitspreis angewendet?", True),
        ("Ist mein Anteil an den Betriebskosten 2025 korrekt berechnet?", True),
        ("Ist die Gasabrechnung 2026 korrekt?", True),
        ("Passt der abgerechnete Gasverbrauch 2025 zu den Zählerständen?", True),
        ("Welche Kündigungsfrist gilt für den Gasvertrag?", False),
        ("Wie hoch war der Wasserverbrauch 2025 laut Zählerständen?", False),
        ("Welchen Grundpreis zahle ich für Fernwärme?", False),
        ("Wie hoch ist mein aktueller monatlicher Stromabschlag?", False),
        ("Wie hoch war meine Stromrechnung 2023?", False),
    ],
)
def test_is_audit_question(question, expected):
    assert is_audit_question(question) is expected


def test_is_gap_answer_and_system_prompt_use_the_same_sentence():
    assert is_gap_answer(GAP_ANSWER)
    assert is_gap_answer("Das liegt nicht vor.")
    assert not is_gap_answer("Der Arbeitspreis beträgt 34,80 ct/kWh.")
    assert GAP_ANSWER in system_prompt(6)
    assert "brutto" in system_prompt(6)


def test_empty_answer_is_reported():
    # Arrange
    loop, _ = _loop([answer_reply("")])

    # Act / Assert
    assert loop.run("Frage?").stop_reason == "empty_answer"


def test_on_step_sees_every_step_and_the_growing_book():
    # Arrange
    loop, _ = _loop([tool_reply(SEARCH), answer_reply("Fertig.")])
    seen: list[tuple[str, int]] = []

    # Act
    loop.run("Frage?", on_step=lambda step, book: seen.append((step.kind, len(book.numbered_hits))))

    # Assert
    assert seen == [("model_call", 0), ("tool_call", 1), ("model_call", 1)]


def test_retrieval_errors_are_not_swallowed():
    # Arrange
    def broken(query, options):
        raise RetrievalError("index missing")

    loop, _ = _loop([tool_reply(SEARCH)], backend=FakeBackend(broken))

    # Act / Assert
    with pytest.raises(RetrievalError):
        loop.run("Frage?")


def test_model_call_step_records_timing_from_the_response():
    # Arrange
    loop, _ = _loop([answer_reply("Ja.", prompt_tokens=420, prefill_seconds=7.5)])

    # Act
    step = loop.run("Frage?").steps[0]

    # Assert
    assert (step.prompt_tokens, step.prefill_seconds, step.generated_tokens) == (420, 7.5, 20)
    assert step.decode_seconds == 4.0 and step.offered_tools is True


def test_system_prompt_names_the_tool_limit_and_estimate_tokens_is_monotonic():
    assert "höchstens 6 Werkzeugaufrufe" in system_prompt(6)
    assert estimate_tokens("a" * 300) > estimate_tokens("a" * 30)


def test_run_log_writes_steps_incrementally_and_a_summary(tmp_path):
    # Arrange
    loop, _ = _loop([tool_reply(SEARCH), answer_reply("Fertig [1].")])
    log = RunLog(tmp_path / "out" / "q.jsonl")

    # Act
    run = loop.run("Frage?", on_step=log)
    lines_before_finish = (tmp_path / "out" / "q.jsonl").read_text(encoding="utf-8").splitlines()
    log.finish(run)
    records = [
        json.loads(line)
        for line in (tmp_path / "out" / "q.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    # Assert
    assert len(lines_before_finish) == 3
    assert [record["kind"] for record in records] == [
        "model_call",
        "tool_call",
        "model_call",
        "run",
    ]
    assert records[-1]["run"]["answer"] == "Fertig [1]."
    assert "steps" not in records[-1]["run"]
    assert records[-1]["run"]["sources"][0]["number"] == 1


def test_run_log_truncates_an_old_file(tmp_path):
    # Arrange
    path = tmp_path / "q.jsonl"
    path.write_text("old\n", encoding="utf-8")

    # Act
    RunLog(path)

    # Assert
    assert path.read_text(encoding="utf-8") == ""


def _question(**overrides):
    values = {
        "id": "S2",
        "category": QuestionCategory.STANDARD,
        "question": "Arbeitspreis?",
        "expected_answer": "34,80 ct/kWh",
        "facts": (ExpectedFact(label="Arbeitspreis", value=Decimal("34.80"), unit="ct/kWh"),),
        "sources": (SourceRef(file=BILL_FILE, page=1),),
        "expected_tools": ("search",),
        "tests": "Tabellensuche",
    }
    return Question(**{**values, **overrides})


def _run(answer, sources=(), tools=("search",)):
    steps = tuple(
        ToolCallStep(index=i, tool=tool, arguments={}, is_valid=True, observation="", seconds=0.1)
        for i, tool in enumerate(tools)
    )
    return AgentRun(
        question="q",
        model="m",
        answer=answer,
        stop_reason="answer",
        tool_call_count=len(tools),
        seconds=1.0,
        steps=steps,
        sources=tuple(sources),
    )


@pytest.mark.parametrize(
    ("value", "unit", "answer", "expected"),
    [
        (Decimal("34.80"), "ct/kWh", "Der Arbeitspreis beträgt 34,80 ct/kWh.", True),
        (Decimal("0.348"), "EUR/kWh", "Der Arbeitspreis beträgt 34,80 ct/kWh.", True),
        (Decimal("34.80"), "ct/kWh", "Der Arbeitspreis beträgt 0,348 EUR/kWh.", True),
        (Decimal("1189"), "EUR", "Gesamt 1.189,00 EUR", True),
        (Decimal("34.80"), "ct/kWh", "Der Arbeitspreis beträgt 39,50 ct/kWh.", False),
        (Decimal("3480"), "kWh", "Der Verbrauch beträgt 3.480 kWh.", True),
        (Decimal("3480"), "kWh", "Der Arbeitspreis beträgt 34,80 ct/kWh.", False),
        (Decimal("0.956"), None, "Die z-Zahl ist 95,6.", False),
        ("Hausverwaltung", None, "Die hausverwaltung schickt…", True),
        ("Hausverwaltung", None, "Unbekannt.", False),
    ],
)
def test_is_fact_in_answer(value, unit, answer, expected):
    fact = ExpectedFact(label="x", value=value, unit=unit)
    assert is_fact_in_answer(fact, answer) is expected


def test_evaluate_run_for_an_answerable_question():
    # Arrange
    found = NumberedHit(number=1, hit=make_hit())

    # Act
    good = evaluate_run(_question(), _run("34,80 ct/kWh [1]", [found]))
    bad = evaluate_run(_question(), _run("Keine Ahnung", [], tools=("search_images",)))

    # Assert
    assert good.are_tools_ok and not good.missing_files and not good.missing_facts
    assert good.admits_gap is None
    assert not bad.are_tools_ok
    assert bad.missing_files == (BILL_FILE,) and bad.missing_facts == ("Arbeitspreis",)


def test_evaluate_run_for_a_negative_question_checks_the_honest_gap():
    # Arrange
    negative = _question(
        id="N1",
        category=QuestionCategory.NEGATIVE,
        is_answerable=False,
        facts=(),
        sources=(),
        expected_tools=("list_documents",),
    )

    # Act
    honest = evaluate_run(
        negative, _run("Dazu liegen keine Angaben vor.", tools=("list_documents",))
    )
    invented = evaluate_run(negative, _run("Sie betrug 1.000 EUR.", tools=("list_documents",)))

    # Assert
    assert honest.admits_gap is True and invented.admits_gap is False


def test_render_markdown_has_summary_tool_steps_and_prefill_rate():
    # Arrange
    loop, _ = _loop([tool_reply(SEARCH), answer_reply("34,80 ct/kWh [1].", prompt_tokens=360)])
    run = loop.run("Arbeitspreis?")

    # Act
    markdown = render_markdown("llama3.1:8b", [(_question(), run)])

    # Assert
    assert "Modell: `llama3.1:8b`" in markdown
    assert "| S2 | search | search | ja |" in markdown
    assert "## S2: Arbeitspreis?" in markdown
    assert "- search(" in markdown
    assert "| 2 | 360 | 2.0 | 180 |" in markdown  # 360 tokens / 2 s


def test_evidence_sections_group_by_document_and_keep_citation_numbers():
    # Arrange
    hits = (
        NumberedHit(number=1, hit=make_hit("a", content="Arbeitspreis 34,80", base_score=0.7)),
        NumberedHit(
            number=2,
            hit=make_hit("b", ChunkType.TABLE_SUMMARY, content="Zusammenfassung", base_score=0.5),
        ),
        NumberedHit(
            number=3,
            hit=make_hit("c", ChunkType.TEXT, CONTRACT_FILE, "Kündigungsfrist", ("Vertrag",)),
        ),
    )

    # Act
    sections = evidence_sections(hits)

    # Assert
    titles = [title for title, _ in sections]
    assert titles[0].startswith("04_Strom_Jahresabrechnung_2024.pdf")
    body = dict(sections)[titles[0]]
    assert "**[1]** S. 1 · Tabellenzeile" in body and "**[2]**" in body
    assert "(KI, kein Beleg)" in body and "Arbeitspreis 34,80" in body
    assert "**[3]**" in dict(sections)[titles[1]]


def test_evidence_book_numbers_each_chunk_once():
    # Arrange
    book = EvidenceBook()

    # Act
    numbers = [book.register(make_hit(c)) for c in ("a", "b", "a")]

    # Assert
    assert numbers == [1, 2, 1] and book.number_of("b") == 2 and book.number_of("zzz") is None


def test_streamlit_app_renders_the_first_page_without_ollama():
    # Arrange
    from streamlit.testing.v1 import AppTest

    app = Path(__file__).parents[1] / "src" / "audit_agent" / "agent" / "app.py"

    # Act
    page = AppTest.from_file(str(app), default_timeout=30).run()

    # Assert
    assert not page.exception
    assert page.title[0].value == "Energie- & Nebenkosten-Auditor"
    assert page.button[0].disabled  # no question yet


def test_answer_with_numbers_and_no_hit_number_is_questioned_once():
    # Arrange
    replies = [tool_reply(SEARCH), answer_reply("34,80 ct/kWh."), answer_reply("34,80 ct/kWh [1].")]
    loop, chat = _loop(replies)

    # Act
    run = loop.run("Wie hoch ist der Arbeitspreis?")

    # Assert
    nudges = [step for step in run.steps if step.kind == "nudge"]
    assert [nudge.reason for nudge in nudges] == ["cite"]
    assert run.answer == "34,80 ct/kWh [1]."
    assert chat.requests[-1]["messages"][-1]["content"] == CITE_BEFORE_ANSWER_MESSAGE


def test_cite_nudge_is_asked_once_and_skipped_when_it_would_not_help():
    # Arrange
    uncited_twice = [tool_reply(SEARCH), answer_reply("34,80 ct/kWh."), answer_reply("34,80 ct.")]
    no_number = [tool_reply(SEARCH), answer_reply("Ja, das stimmt.")]
    no_search = [answer_reply("Es sind 5 Dokumente.")]
    gap = [tool_reply(SEARCH), tool_reply(SEARCH), answer_reply(GAP_ANSWER)]

    # Act
    first = _loop(uncited_twice)[0].run("Wie hoch ist der Arbeitspreis?")
    others = [_loop(replies)[0].run("Frage?") for replies in (no_number, no_search, gap)]

    # Assert
    assert [s.reason for s in first.steps if s.kind == "nudge"] == ["cite"]
    assert first.answer == "34,80 ct."
    for run in others:
        assert "nudge" not in [step.kind for step in run.steps]


def test_cite_nudge_can_be_switched_off():
    # Arrange
    loop, _ = _loop(
        [tool_reply(SEARCH), answer_reply("34,80 ct/kWh.")],
        agent=AgentSettings(require_citation=False),
    )

    # Act
    run = loop.run("Wie hoch ist der Arbeitspreis?")

    # Assert
    assert "nudge" not in [step.kind for step in run.steps]
