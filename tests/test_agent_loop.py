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
from audit_agent.agent.prompts import FORCED_ANSWER_MESSAGE, system_prompt
from audit_agent.agent.report import evaluate_run, is_fact_in_answer, render_markdown
from audit_agent.config import AgentSettings, Settings
from audit_agent.corpus import ExpectedFact, Question, QuestionCategory, SourceRef
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

SEARCH = ("search_tables", {"query": "Arbeitspreis"})
CALCULATE = ("calculate", {"expression": "2*3"})


def _loop(replies, backend=None, **settings_options):
    settings = Settings(**settings_options)
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
    assert len(chat.requests[0]["tools"]) == 6
    assert chat.requests[0]["messages"][0]["role"] == "system"
    assert chat.requests[0]["messages"][1] == {"role": "user", "content": "Frage?"}


def test_tool_call_observation_goes_back_to_the_model():
    # Arrange
    loop, chat = _loop([tool_reply(CALCULATE), answer_reply("Ergebnis 6.")])

    # Act
    run = loop.run("Was ist 2*3?")

    # Assert
    assert run.answer == "Ergebnis 6." and run.tool_call_count == 1
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
        tool_reply(("search_tables", {"doc_type": "Rechnung"})),
        tool_reply(("make_coffee", {})),
        answer_reply("Fertig."),
    ]
    loop, chat = _loop(replies)

    # Act
    run = loop.run("Frage?")

    # Assert
    first, second = run.steps[1], run.steps[3]
    assert not first.is_valid and "Ungültige Argumente für search_tables" in first.observation
    assert "query" in first.observation and "doc_type" in first.observation
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
    # Arrange: free = 2048 - 600 - 1200 = 248 tokens; the first call already used 300
    replies = [tool_reply(CALCULATE, prompt_tokens=300), answer_reply("Notantwort.")]
    loop, chat = _loop(replies, num_ctx=2048)

    # Act
    run = loop.run("Frage?")

    # Assert
    assert run.stop_reason == "context_limit" and run.answer == "Notantwort."
    assert "tools" not in chat.requests[1]


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
        "expected_tools": ("search_tables",),
        "tests": "Tabellensuche",
    }
    return Question(**{**values, **overrides})


def _run(answer, sources=(), tools=("search_tables",)):
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
    ("value", "answer", "expected"),
    [
        (Decimal("34.80"), "Der Arbeitspreis beträgt 34,80 ct/kWh.", True),
        (Decimal("0.348"), "Der Arbeitspreis beträgt 34,80 ct/kWh.", True),
        (Decimal("1189"), "Gesamt 1.189,00 EUR", True),
        (Decimal("34.80"), "Der Arbeitspreis beträgt 39,50 ct/kWh.", False),
        ("Hausverwaltung", "Die hausverwaltung schickt…", True),
        ("Hausverwaltung", "Unbekannt.", False),
    ],
)
def test_is_fact_in_answer(value, answer, expected):
    assert is_fact_in_answer(ExpectedFact(label="x", value=value), answer) is expected


def test_evaluate_run_for_an_answerable_question():
    # Arrange
    found = NumberedHit(number=1, hit=make_hit())

    # Act
    good = evaluate_run(_question(), _run("34,80 ct/kWh [1]", [found]))
    bad = evaluate_run(_question(), _run("Keine Ahnung", [], tools=("search_documents",)))

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
    assert "| S2 | search_tables | search_tables | ja |" in markdown
    assert "## S2: Arbeitspreis?" in markdown
    assert "- search_tables(" in markdown
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
