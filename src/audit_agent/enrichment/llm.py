"""The small part of the Ollama client that enrichment uses (tests inject a fake)."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Protocol

from ollama import Image

from audit_agent.config import Settings
from audit_agent.enrichment.cache import CachedAnswer


class EnrichmentError(RuntimeError):
    """Raised when enrichment cannot continue (missing input, empty model answer)."""


class ChatClient(Protocol):
    """Subset of ``ollama.Client`` used by the enrichment."""

    def chat(self, **kwargs: Any) -> Any: ...
    def generate(self, **kwargs: Any) -> Any: ...
    def list(self) -> Any: ...
    def ps(self) -> Any: ...


def model_options(settings: Settings, num_predict: int) -> dict[str, Any]:
    """Generation options; part of the cache key, so a change recomputes the answers."""
    return {"num_ctx": settings.num_ctx, "num_predict": num_predict, "temperature": 0}


def ask_model(
    client: ChatClient,
    model: str,
    prompt: str,
    options: dict[str, Any],
    keep_alive: str,
    image: bytes | None = None,
) -> CachedAnswer:
    """One chat call with a single user message (optionally with one image)."""
    message: dict[str, Any] = {"role": "user", "content": prompt}
    if image is not None:
        message["images"] = [Image(value=image)]
    started = time.perf_counter()
    response = client.chat(model=model, messages=[message], options=options, keep_alive=keep_alive)
    seconds = time.perf_counter() - started
    text = (response.message.content or "").strip()
    if not text:
        raise EnrichmentError(f"{model} returned an empty answer")
    return CachedAnswer(text=text, model=model, seconds=seconds)


def unload_model(client: ChatClient, model: str) -> None:
    """Free the RAM of one model (``keep_alive=0``)."""
    client.generate(model=model, prompt="", keep_alive=0)


def unload_all_running(client: ChatClient) -> None:
    """Start from an empty memory so the 9 GB budget (ADR-0004) cannot be exceeded."""
    for running in client.ps().models:
        unload_model(client, running.model)


def installed_models(client: ChatClient) -> Sequence[str]:
    return [entry.model for entry in client.list().models]
