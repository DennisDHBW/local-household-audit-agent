"""Tests for the pure parts of ``scripts/m9_probe.py`` (M9-0); no Ollama needed."""

from __future__ import annotations

import importlib.util
import json
import sys
from types import ModuleType
from typing import Any

import pytest
from ollama import ChatResponse, GenerateResponse, Message

from audit_agent.config import PROJECT_ROOT


@pytest.fixture(scope="module")
def probe() -> ModuleType:
    path = PROJECT_ROOT / "scripts" / "m9_probe.py"
    spec = importlib.util.spec_from_file_location("m9_probe", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["m9_probe"] = module
    spec.loader.exec_module(module)
    return module


def _chat(content: str, prompt_tokens: int = 1200, prefill_ns: int = 60_000_000_000) -> Any:
    return ChatResponse(
        model="m",
        message=Message(role="assistant", content=content),
        prompt_eval_count=prompt_tokens,
        prompt_eval_duration=prefill_ns,
        eval_count=80,
        eval_duration=16_000_000_000,
        load_duration=3_000_000_000,
        done_reason="stop",
    )


class FakeClient:
    """Answers every frame call with the gold frame of F1 and records the arguments."""

    def __init__(self, frame_json: str):
        self.frame_json = frame_json
        self.calls: list[dict[str, Any]] = []

    def chat(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return _chat(self.frame_json if "format" in kwargs else "{}")

    def generate(self, **kwargs: Any) -> Any:
        raise AssertionError("not used")


def _frame(probe: ModuleType, *tasks: Any, follow_up: bool = False) -> Any:
    return probe.QueryFrame(tasks=list(tasks), search_query="x", is_follow_up=follow_up)


def test_examples_and_gold_frames_only_use_schema_fields(probe: ModuleType) -> None:
    # Arrange
    fields = set(probe.SubTask.model_fields)
    prompt = probe.frame_system_prompt()

    # Act
    gold_fields = {name for q in probe.PROBE_QUESTIONS for gold in q.gold_tasks for name in gold}

    # Assert
    assert gold_fields <= fields
    for example in probe.EXAMPLES:
        assert example.frame.model_dump_json() in prompt
    assert prompt.count("JSON: ") == len(probe.EXAMPLES)
    assert len(probe.PROBE_QUESTIONS) == 8


def test_score_frame_pairs_tasks_in_any_order(probe: ModuleType) -> None:
    # Arrange
    question = next(q for q in probe.PROBE_QUESTIONS if q.id == "F7")
    gas = probe._task(probe.Intent.FACT, "gas", probe.Period.YEARS, years=[2025])
    power = probe._task(probe.Intent.OVERVIEW, "electricity", probe.Period.YEARS, years=[2025])

    # Act
    score = probe.score_frame(_frame(probe, gas, power), question)

    # Assert
    assert score.exact
    assert score.total == 9  # 2 x 4 fields + is_follow_up


def test_score_frame_counts_missing_and_extra_tasks(probe: ModuleType) -> None:
    # Arrange
    f7 = next(q for q in probe.PROBE_QUESTIONS if q.id == "F7")
    f1 = probe.PROBE_QUESTIONS[0]
    gas = probe._task(probe.Intent.FACT, "gas", probe.Period.YEARS, years=[2025])
    water = probe._task(probe.Intent.FACT, "water", probe.Period.YEARS, years=[2025])

    # Act
    missing = probe.score_frame(_frame(probe, gas), f7)
    extra = probe.score_frame(_frame(probe, water, gas), f1)
    nothing = probe.score_frame(None, f1)

    # Assert
    assert (missing.matched, missing.total) == (5, 9)
    assert (extra.matched, extra.total, extra.mismatches) == (5, 6, ["tasks+1"])
    assert nothing.matched == 0 and not nothing.exact


def test_parse_frame_tells_json_from_schema_errors(probe: ModuleType) -> None:
    # Arrange
    valid = _frame(probe, probe._task(probe.Intent.CLAUSE, "rent", probe.Period.NONE))

    # Act
    results = [
        probe.parse_frame(valid.model_dump_json()),
        probe.parse_frame('{"tasks": []}'),
        probe.parse_frame("Gerne, hier ist"),
    ]

    # Assert
    assert [(json_ok, frame is not None) for json_ok, frame, _ in results] == [
        (True, True),
        (True, False),
        (False, False),
    ]


def test_call_metrics_reads_chat_and_generate_responses(probe: ModuleType) -> None:
    # Arrange
    generated = GenerateResponse(model="m", response="<tool_call>", eval_count=30)

    # Act
    chat = probe.call_metrics(_chat("{}"), 70.0)
    raw = probe.call_metrics(generated, 5.0)

    # Assert
    assert chat["prefill_seconds"] == 60.0 and chat["generated_tokens"] == 80
    assert raw["content"] == "<tool_call>" and raw["tool_calls"] == []


def test_probe_model_runs_frames_and_cache_sequences(probe: ModuleType) -> None:
    # Arrange
    gold = _frame(
        probe, probe._task(probe.Intent.FACT, "water", probe.Period.YEARS, years=[2025])
    ).model_dump_json()
    client = FakeClient(gold)

    # Act
    calls = probe.probe_model(client, "m", {"num_ctx": 8192}, "5m", True, "2026-11-21")
    summary = probe.summarize_model(calls)

    # Assert
    assert [call["part"] for call in calls].count("frame") == 8
    assert all(kwargs["think"] is False for kwargs in client.calls)
    assert "Heute: 2026-11-21" in client.calls[0]["messages"][1]["content"]
    assert summary["json_valid"] == summary["schema_valid"] == summary["calls"] == 9
    assert summary["exact_frames"] == 1  # only F1 has this gold frame
    assert summary["cold_prefill_tps"] == 20.0
    assert summary["alt_separate_third_prefill_seconds"] == 60.0


def test_probe_model_omits_think_for_models_without_thinking(probe: ModuleType) -> None:
    # Arrange
    client = FakeClient("{}")

    # Act
    probe.probe_model(client, "m", {}, "5m", False, "2026-11-21")

    # Assert
    assert all("think" not in kwargs for kwargs in client.calls)


def test_render_markdown_lists_models_and_mismatches(probe: ModuleType) -> None:
    # Arrange
    calls = probe.probe_model(FakeClient("{}"), "m", {}, "5m", False, "2026-11-21")
    result = {
        "run_id": "run-x",
        "started": "2026-11-21 20:00",
        "num_ctx": 8192,
        "models": {
            "m": {"calls": calls, "summary": probe.summarize_model(calls), "memory_mb": 5000},
            "n": {"missing": True},
        },
        "iss126": {"chat": {"generated_tokens": 31, "content": ""}, "raw": {"content": "x"}},
    }

    # Act
    text = probe.render_markdown(result)

    # Assert
    assert "| m | 9/9 | 0/9 |" in text
    assert "| n | nicht geladen |" in text
    assert "- m F1:" in text and "## ISS-126" in text


def test_render_qwen25_prompt_puts_tools_into_the_system_block(probe: ModuleType) -> None:
    # Arrange
    spec = {"type": "function", "function": {"name": "search", "description": "Suche"}}

    # Act
    prompt = probe.render_qwen25_prompt("System", [spec], "Frage?")

    # Assert
    assert prompt.startswith("<|im_start|>system\nSystem\n\n# Tools")
    assert json.dumps({"type": "function", "function": spec["function"]}) in prompt
    assert prompt.endswith("<|im_start|>user\nFrage?<|im_end|>\n<|im_start|>assistant\n")
