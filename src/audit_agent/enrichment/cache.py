"""Disk cache for model answers (SHA-256 keys over everything that shapes the model input)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import diskcache
from pydantic import BaseModel, ConfigDict


class CachedAnswer(BaseModel):
    """One model answer plus how it came about."""

    model_config = ConfigDict(frozen=True)

    text: str
    model: str
    seconds: float
    """Wall-clock time of the original model call (not of a cache hit)."""
    is_truncated: bool = False
    """The model hit the token limit, so the text may end in the middle of a sentence."""


def digest_bytes(data: bytes) -> str:
    """SHA-256 of raw bytes (used for image content)."""
    return hashlib.sha256(data).hexdigest()


def make_cache_key(
    task: str,
    model: str,
    prompt: str,
    options: Mapping[str, Any],
    image_digest: str | None = None,
) -> str:
    """Cache key: changes whenever the task, model, full prompt, options or image change.

    The prompt text itself is part of the key, so editing a prompt template invalidates the
    old answers automatically; no separate prompt version has to be maintained.
    """
    payload = json.dumps(
        {
            "task": task,
            "model": model,
            "prompt": prompt,
            "options": dict(options),
            "image": image_digest,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EnrichmentCache:
    """Thin wrapper around ``diskcache.Cache`` that stores :class:`CachedAnswer` objects."""

    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self._cache = diskcache.Cache(str(directory))

    def get(self, key: str) -> CachedAnswer | None:
        raw = self._cache.get(key)
        return None if raw is None else CachedAnswer.model_validate(raw)

    def set(self, key: str, answer: CachedAnswer) -> None:
        self._cache.set(key, answer.model_dump())

    def get_or_compute(
        self, key: str, compute: Callable[[], CachedAnswer]
    ) -> tuple[CachedAnswer, bool]:
        """Return ``(answer, is_cache_hit)``; only successful answers are stored."""
        cached = self.get(key)
        if cached is not None:
            return cached, True
        answer = compute()
        self.set(key, answer)
        return answer, False

    def close(self) -> None:
        self._cache.close()
