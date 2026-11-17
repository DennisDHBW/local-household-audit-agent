"""Embedding index, search with metadata filter and hierarchy boost, evidence view."""

from audit_agent.retrieval.evidence import (
    EvidenceChapter,
    EvidenceDocument,
    build_evidence,
    render_evidence_text,
)
from audit_agent.retrieval.index import (
    IndexReport,
    build_index,
    embedding_text,
    get_collection,
    hierarchy_prefix,
    open_vector_client,
)
from audit_agent.retrieval.models import (
    MetadataFilter,
    RetrievalError,
    SearchHit,
    SearchOptions,
)
from audit_agent.retrieval.quantity import (
    new_quantity_hits,
    quantity_query,
    utility_in_query,
    with_query_utility,
)
from audit_agent.retrieval.search import Retriever, build_where, path_matches, tokenize_query

__all__ = [
    "EvidenceChapter",
    "EvidenceDocument",
    "IndexReport",
    "MetadataFilter",
    "RetrievalError",
    "Retriever",
    "SearchHit",
    "SearchOptions",
    "build_evidence",
    "build_index",
    "build_where",
    "embedding_text",
    "get_collection",
    "hierarchy_prefix",
    "new_quantity_hits",
    "open_vector_client",
    "path_matches",
    "quantity_query",
    "render_evidence_text",
    "tokenize_query",
    "utility_in_query",
    "with_query_utility",
]
