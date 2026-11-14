"""Image captions with the vision model (``gemma3:4b``)."""

from __future__ import annotations

from collections.abc import Sequence

from audit_agent.config import Settings
from audit_agent.enrichment.cache import (
    CachedAnswer,
    EnrichmentCache,
    digest_bytes,
    make_cache_key,
)
from audit_agent.enrichment.llm import ChatClient, ask_model, model_options
from audit_agent.enrichment.prompts import build_caption_prompt

TASK = "image_caption"


class ImageCaptioner:
    """Describes one chart image; answers are cached by image content and prompt."""

    def __init__(self, client: ChatClient, settings: Settings, cache: EnrichmentCache) -> None:
        self._client = client
        self._settings = settings
        self._cache = cache
        self._model = settings.models.vision
        self._options = model_options(settings, settings.enrichment.caption_max_tokens)

    @property
    def model(self) -> str:
        return self._model

    def cache_key(self, image: bytes, heading_stack: Sequence[str]) -> str:
        prompt = build_caption_prompt(heading_stack)
        return make_cache_key(TASK, self._model, prompt, self._options, digest_bytes(image))

    def is_cached(self, image: bytes, heading_stack: Sequence[str]) -> bool:
        return self._cache.get(self.cache_key(image, heading_stack)) is not None

    def caption(self, image: bytes, heading_stack: Sequence[str]) -> tuple[CachedAnswer, bool]:
        """Return ``(answer, is_cache_hit)``."""
        prompt = build_caption_prompt(heading_stack)
        return self._cache.get_or_compute(
            self.cache_key(image, heading_stack),
            lambda: ask_model(
                self._client,
                self._model,
                prompt,
                self._options,
                self._settings.enrichment.keep_alive,
                image=image,
            ),
        )
