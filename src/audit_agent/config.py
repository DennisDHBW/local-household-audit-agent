"""Central configuration (single source of truth for paths, models and limits).

Every value can be overridden through an environment variable with the prefix ``AUDIT_``
(for example ``AUDIT_OLLAMA_HOST``). Business code must never hard-code paths or model names.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PREFIX = "AUDIT_"

MAX_OLLAMA_MEMORY_GB = 9.0
MAX_LOADED_MODELS = 2


class ModelNames(BaseModel):
    """Ollama model tags per task (see ADR-0004)."""

    model_config = ConfigDict(frozen=True)

    embedding: str = "nomic-embed-text"
    vision: str = "gemma3:4b"
    summary: str = "llama3.2"
    agent: str = "llama3.1:8b"
    agent_candidates: tuple[str, ...] = ("qwen2.5:7b", "llama3.1:8b")

    def required_for_smoke_test(self) -> tuple[str, ...]:
        """All distinct model tags the smoke test needs, in a stable order."""
        ordered = (*self.agent_candidates, self.summary, self.vision, self.embedding)
        return tuple(dict.fromkeys(ordered))


class Settings(BaseModel):
    """Runtime settings of the application."""

    model_config = ConfigDict(frozen=True)

    project_root: Path = PROJECT_ROOT
    ollama_host: str = "http://localhost:11434"
    ollama_timeout_s: float = Field(default=900.0, gt=0)
    num_ctx: int = Field(default=8192, ge=512)
    memory_limit_gb: float = Field(default=MAX_OLLAMA_MEMORY_GB, gt=0)
    max_loaded_models: int = Field(default=MAX_LOADED_MODELS, ge=1)
    models: ModelNames = Field(default_factory=ModelNames)

    @property
    def dataset_dir(self) -> Path:
        return self.project_root / "dataset"

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def vectors_dir(self) -> Path:
        return self.data_dir / "vectors"

    @property
    def eval_dir(self) -> Path:
        return self.data_dir / "eval"

    @property
    def cache_dir(self) -> Path:
        return self.project_root / ".cache"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        """Build settings from defaults plus ``AUDIT_*`` overrides (fail fast on bad values)."""
        env = os.environ if environ is None else environ

        def get(name: str) -> str | None:
            return env.get(f"{ENV_PREFIX}{name}")

        values: dict[str, object] = {}
        for field in ("ollama_host", "ollama_timeout_s", "num_ctx", "memory_limit_gb"):
            raw = get(field.upper())
            if raw is not None:
                values[field] = raw
        if (root := get("PROJECT_ROOT")) is not None:
            values["project_root"] = Path(root)

        model_values: dict[str, object] = {}
        for field in ("embedding", "vision", "summary", "agent"):
            raw = get(f"MODEL_{field.upper()}")
            if raw is not None:
                model_values[field] = raw
        if (candidates := get("MODEL_AGENT_CANDIDATES")) is not None:
            model_values["agent_candidates"] = tuple(
                tag.strip() for tag in candidates.split(",") if tag.strip()
            )
        if model_values:
            values["models"] = ModelNames(**model_values)

        return cls(**values)
