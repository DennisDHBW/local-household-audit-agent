"""Model-based enrichment: image captions and table summaries with a disk cache."""

from audit_agent.enrichment.cache import CachedAnswer, EnrichmentCache, make_cache_key
from audit_agent.enrichment.captioner import ImageCaptioner
from audit_agent.enrichment.checks import unsupported_numbers
from audit_agent.enrichment.llm import EnrichmentError
from audit_agent.enrichment.pipeline import (
    EnrichedItem,
    EnrichmentKind,
    EnrichmentReport,
    run_enrichment,
)
from audit_agent.enrichment.summarizer import TableSummarizer

__all__ = [
    "CachedAnswer",
    "EnrichedItem",
    "EnrichmentCache",
    "EnrichmentError",
    "EnrichmentKind",
    "EnrichmentReport",
    "ImageCaptioner",
    "TableSummarizer",
    "make_cache_key",
    "run_enrichment",
    "unsupported_numbers",
]
