"""Reading a tool call that the model wrote as text (ISS-061)."""

import pytest

from audit_agent.agent.text_calls import TextCall, parse_text_call

TOOLS = {"search", "calculate"}


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (
            '{"name": "search", "parameters": {"query": "Abschlag"}}',
            TextCall("search", {"query": "Abschlag"}),
        ),
        (
            'Ich suche nach dem Wert. {"name": "search", "parameters": {"query": "Abschlag"}}',
            TextCall("search", {"query": "Abschlag"}),
        ),
        (
            'Ich rechne.\n```json\n{"name": "calculate", "arguments": {"expression": "2*3"}}\n```',
            TextCall("calculate", {"expression": "2*3"}),
        ),
        (
            '  {"name": "search", "parameters": {"query": "a", "filter": {"year": 2024}}}  \n',
            TextCall("search", {"query": "a", "filter": {"year": 2024}}),
        ),
    ],
)
def test_a_json_call_that_ends_the_message_is_read(content, expected):
    assert parse_text_call(content, TOOLS) == expected


@pytest.mark.parametrize(
    "content",
    [
        "",
        "Der Arbeitspreis beträgt 34,80 ct/kWh [1].",
        '{"name": "unbekannt", "parameters": {"query": "a"}}',
        '{"name": "search", "parameters": "query=a"}',
        '{"name": "search"}',
        '{"name": 5, "parameters": {}}',
        '["search", {"query": "a"}]',
        '{"name": "search", "parameters": {"query": "a"}} Das war der Aufruf.',
        '{"name": "search", "parameters": {"query": "a"',
        '{"preis": 34.8} und {"name": "search"}',
    ],
)
def test_everything_else_stays_an_answer(content):
    assert parse_text_call(content, TOOLS) is None
