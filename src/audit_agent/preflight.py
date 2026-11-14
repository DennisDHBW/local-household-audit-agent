"""Fail-fast checks before anything talks to Ollama."""

from __future__ import annotations

from collections.abc import Iterable


class MissingModelError(RuntimeError):
    """Raised when required Ollama models are not installed."""


def normalize_model_tag(tag: str) -> str:
    """Return the tag with an explicit version (``llama3.2`` -> ``llama3.2:latest``)."""
    return tag if ":" in tag else f"{tag}:latest"


def find_missing_models(installed: Iterable[str], required: Iterable[str]) -> list[str]:
    """Return the required tags that are not installed, preserving the given order."""
    available = {normalize_model_tag(tag) for tag in installed}
    return [tag for tag in required if normalize_model_tag(tag) not in available]


def ensure_models_available(installed: Iterable[str], required: Iterable[str]) -> None:
    """Raise :class:`MissingModelError` with a ready-to-run ``ollama pull`` hint."""
    missing = find_missing_models(installed, required)
    if missing:
        pulls = " && ".join(f"ollama pull {tag}" for tag in missing)
        raise MissingModelError(f"Missing Ollama models: {', '.join(missing)}. Run: {pulls}")
