"""Table summaries with the small text model (``llama3.2``)."""

from __future__ import annotations

from collections.abc import Sequence

from audit_agent.config import Settings
from audit_agent.enrichment.cache import CachedAnswer, EnrichmentCache, make_cache_key
from audit_agent.enrichment.llm import ChatClient, ask_model, model_options
from audit_agent.enrichment.prompts import build_summary_prompt

TASK = "table_summary"


class TableSummarizer:
    """Summarises one table from its serialised rows; answers are cached by prompt text."""

    def __init__(self, client: ChatClient, settings: Settings, cache: EnrichmentCache) -> None:
        self._client = client
        self._settings = settings
        self._cache = cache
        self._model = settings.models.summary
        self._options = model_options(settings, settings.enrichment.summary_max_tokens)

    @property
    def model(self) -> str:
        return self._model

    def cache_key(
        self, heading_stack: Sequence[str], columns: Sequence[str], row_texts: Sequence[str]
    ) -> str:
        prompt = build_summary_prompt(heading_stack, columns, row_texts)
        return make_cache_key(TASK, self._model, prompt, self._options)

    def is_cached(
        self, heading_stack: Sequence[str], columns: Sequence[str], row_texts: Sequence[str]
    ) -> bool:
        return self._cache.get(self.cache_key(heading_stack, columns, row_texts)) is not None

    def summarize(
        self, heading_stack: Sequence[str], columns: Sequence[str], row_texts: Sequence[str]
    ) -> tuple[CachedAnswer, bool]:
        """Return ``(answer, is_cache_hit)``."""
        prompt = build_summary_prompt(heading_stack, columns, row_texts)
        return self._cache.get_or_compute(
            self.cache_key(heading_stack, columns, row_texts),
            lambda: ask_model(
                self._client,
                self._model,
                prompt,
                self._options,
                self._settings.enrichment.keep_alive,
            ),
        )
