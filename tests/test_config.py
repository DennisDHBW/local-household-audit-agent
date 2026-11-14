from pathlib import Path

import pytest
from pydantic import ValidationError

from audit_agent.config import PROJECT_ROOT, Settings


def test_defaults_point_to_project_folders():
    # Arrange / Act
    settings = Settings()

    # Assert
    assert settings.project_root == PROJECT_ROOT
    assert settings.dataset_dir == PROJECT_ROOT / "dataset"
    assert settings.eval_dir == PROJECT_ROOT / "data" / "eval"
    assert settings.memory_limit_gb == 9.0
    assert settings.max_loaded_models == 2


def test_environment_overrides_defaults(tmp_path: Path):
    # Arrange
    environ = {
        "AUDIT_OLLAMA_HOST": "http://example:1234",
        "AUDIT_NUM_CTX": "4096",
        "AUDIT_PROJECT_ROOT": str(tmp_path),
        "AUDIT_MODEL_AGENT": "llama3.1:8b",
        "AUDIT_MODEL_AGENT_CANDIDATES": "llama3.1:8b, qwen2.5:7b",
    }

    # Act
    settings = Settings.from_env(environ)

    # Assert
    assert settings.ollama_host == "http://example:1234"
    assert settings.num_ctx == 4096
    assert settings.data_dir == tmp_path / "data"
    assert settings.models.agent == "llama3.1:8b"
    assert settings.models.agent_candidates == ("llama3.1:8b", "qwen2.5:7b")
    assert settings.models.embedding == "nomic-embed-text"


def test_invalid_value_fails_fast():
    with pytest.raises(ValidationError):
        Settings.from_env({"AUDIT_NUM_CTX": "10"})


def test_required_models_are_distinct_and_ordered():
    # Arrange
    settings = Settings.from_env({"AUDIT_MODEL_SUMMARY": "qwen2.5:7b"})

    # Act
    required = settings.models.required_for_smoke_test()

    # Assert
    assert required == ("qwen2.5:7b", "llama3.1:8b", "gemma3:4b", "nomic-embed-text")


def test_agent_settings_defaults_match_the_concept():
    # Arrange / Act
    agent = Settings().agent

    # Assert
    assert agent.max_tool_calls == 6
    assert agent.temperature == 0
    assert agent.max_hit_chars >= 100
