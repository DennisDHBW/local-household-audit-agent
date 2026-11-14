import pytest

from audit_agent.preflight import (
    MissingModelError,
    ensure_models_available,
    find_missing_models,
    normalize_model_tag,
)


def test_normalize_adds_latest_tag():
    assert normalize_model_tag("llama3.2") == "llama3.2:latest"
    assert normalize_model_tag("qwen2.5:7b") == "qwen2.5:7b"


def test_tag_without_version_matches_latest():
    assert find_missing_models(["llama3.2:latest"], ["llama3.2"]) == []


def test_missing_models_are_reported_in_order():
    missing = find_missing_models(["gemma3:4b"], ["qwen2.5:7b", "gemma3:4b", "llama3.2"])
    assert missing == ["qwen2.5:7b", "llama3.2"]


def test_error_contains_pull_command():
    with pytest.raises(MissingModelError, match="ollama pull qwen2.5:7b"):
        ensure_models_available([], ["qwen2.5:7b"])
