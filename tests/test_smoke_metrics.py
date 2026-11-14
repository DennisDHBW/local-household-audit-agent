import pytest
from ollama import ChatResponse, Message

from audit_agent.numbers import extract_numbers, parse_number
from audit_agent.smoke.metrics import (
    ToolCallingSummary,
    ToolCallResult,
    cosine_similarity,
    is_prefix_reused,
    speed_from_response,
    tokens_per_second,
    tool_call_is_correct,
)


def test_tokens_per_second_from_nanoseconds():
    assert tokens_per_second(18, 1_000_000_000) == pytest.approx(18.0)


@pytest.mark.parametrize(("count", "duration"), [(None, 5), (5, None), (0, 5), (5, 0)])
def test_tokens_per_second_unknown_when_data_missing(count, duration):
    assert tokens_per_second(count, duration) is None


def test_speed_from_response_uses_ollama_fields():
    # Arrange
    response = ChatResponse(
        model="m",
        message=Message(role="assistant", content="x"),
        prompt_eval_count=360,
        prompt_eval_duration=20_000_000_000,
        eval_count=60,
        eval_duration=10_000_000_000,
        load_duration=3_000_000_000,
    )

    # Act
    result = speed_from_response("m", response, resident_gb=5.5)

    # Assert
    assert result.prefill_tokens_per_s == pytest.approx(18.0)
    assert result.generation_tokens_per_s == pytest.approx(6.0)
    assert result.load_seconds == pytest.approx(3.0)
    assert result.resident_gb == 5.5


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [(20.0, 1.0, True), (20.0, 19.0, False), (None, 1.0, False), (20.0, None, False)],
)
def test_prefix_reuse_heuristic(first, second, expected):
    assert is_prefix_reused(first, second) is expected


def test_cosine_similarity():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_cosine_similarity_rejects_bad_input():
    with pytest.raises(ValueError):
        cosine_similarity([1, 2], [1])
    with pytest.raises(ValueError):
        cosine_similarity([0, 0], [1, 1])


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("3.480", 3480.0),
        ("3480", 3480.0),
        ("1.234,56", 1234.56),
        ("34,80", 34.8),
        ("3,480", 3480.0),
    ],
)
def test_parse_number_handles_german_and_english_formats(token, expected):
    assert parse_number(token) == pytest.approx(expected)


def test_extract_numbers_finds_chart_values():
    text = "2022: 3.480 kWh, 2023: 3.390 kWh, 2024: 3250 kWh."
    assert {3480.0, 3390.0, 3250.0, 2022.0} <= set(extract_numbers(text))


def test_tool_call_correct_with_matching_arguments():
    ok = tool_call_is_correct(
        "search_tables",
        "search_tables",
        {"query": "Arbeitspreis", "utility_type": "Electricity"},
        {"query": "*", "utility_type": "electricity"},
    )
    assert ok == (True, True)


def test_tool_call_with_wrong_argument_value():
    result = tool_call_is_correct(
        "search_tables",
        "search_tables",
        {"query": "x", "utility_type": "gas"},
        {"utility_type": "water"},
    )
    assert result == (True, False)


def test_tool_call_with_missing_argument():
    result = tool_call_is_correct("calculate", "calculate", {}, {"expression": "3100"})
    assert result == (True, False)


def test_wrong_tool_invalidates_arguments():
    assert tool_call_is_correct("calculate", "search_tables", {"query": "x"}, {"query": "*"}) == (
        False,
        False,
    )
    assert tool_call_is_correct(None, "calculate", {}, {}) == (False, False)


def test_tool_calling_summary_accuracy():
    # Arrange
    def result(is_tool_correct, are_arguments_valid):
        return ToolCallResult(
            task_id="t",
            called_tool="x",
            arguments={},
            is_tool_correct=is_tool_correct,
            are_arguments_valid=are_arguments_valid,
            seconds=1.0,
        )

    summary = ToolCallingSummary(
        model="m",
        results=[result(True, True), result(True, False), result(False, False), result(True, True)],
    )

    # Assert
    assert summary.tool_accuracy == 0.75
    assert summary.argument_accuracy == 0.5
