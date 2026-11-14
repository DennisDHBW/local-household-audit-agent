"""Search: vector candidates, optional metadata filter and hierarchy boost (ADR-0002).

``final_score = base_score * boost`` with ``base_score = 1 - cosine distance`` and
``boost = 1.5`` if a query term occurs in file name, folder or headings (else ``1.0``).
Every hit carries the three numbers, so a score can be recomputed by hand.
"""

from __future__ import annotations

import json
import re
from typing import Any

from chromadb.api.models.Collection import Collection

from audit_agent.config import Settings
from audit_agent.ingestion import ChunkType
from audit_agent.retrieval.index import EmbeddingClient, date_number, embed_texts
from audit_agent.retrieval.models import (
    MetadataFilter,
    RetrievalError,
    SearchHit,
    SearchOptions,
)

_STOPWORD_TEXT = (
    "aber als also am an auch auf aus bei bis dann das dass dem den der des die dir doch du "
    "ein eine einem einen einer eines er es für gibt gilt gelten hat hatte haben ich im in ist "
    "kein keine laut man mein meine meinen meinem meiner mich mir mit nach nicht noch nur ob oder "
    "sich sie sind so über um und unter von vor war waren was welche welchen welcher welches "
    "wenn wer werden wie wird wir wo wurde wurden zu zum zur"
)

_WORD = re.compile(r"[^\W_]+")
"""Letters and digits; the underscore of file names separates words."""
_FOLDING = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def fold(text: str) -> str:
    """Lower case with umlauts spelled out (file names use ``ue``, queries use ``ü``)."""
    return text.lower().translate(_FOLDING)


STOPWORDS = frozenset(fold(word) for word in _STOPWORD_TEXT.split())
"""German function words that never count as search terms (folded like the query)."""


def tokenize_query(query: str, min_chars: int) -> tuple[str, ...]:
    """Distinct query words without stop words and very short words, folded."""
    words = (fold(word) for word in _WORD.findall(query))
    kept = (w for w in words if len(w) >= min_chars and w not in STOPWORDS)
    return tuple(dict.fromkeys(kept))


def path_matches(
    terms: tuple[str, ...], filename: str, heading_stack: tuple[str, ...], min_chars: int
) -> tuple[str, ...]:
    """Terms that occur in the path of a chunk.

    A term matches if it is part of the path text, or if a path word (at least
    ``min_chars`` letters) is the beginning of the term, so that the compound
    ``Stromrechnung`` matches the folder word ``Strom``.
    """
    path_text = fold(" ".join((filename, *heading_stack)))
    words = [word for word in _WORD.findall(path_text) if len(word) >= min_chars]
    words = [word for word in words if not word.isdigit()]
    return tuple(
        term for term in terms if term in path_text or any(term.startswith(w) for w in words)
    )


def build_where(options: SearchOptions) -> dict[str, Any] | None:
    """ChromaDB ``where`` clause for the filter options (``None`` = no restriction)."""
    selected: MetadataFilter = options.metadata_filter
    conditions: list[dict[str, Any]] = []
    for field in ("utility_type", "doc_type", "contract_id"):
        value = getattr(selected, field)
        if value is not None:
            conditions.append({field: {"$eq": getattr(value, "value", value)}})
    if selected.period_start is not None and selected.period_end is not None:
        conditions.append({"period_start": {"$lte": date_number(selected.period_end)}})
        conditions.append({"period_end": {"$gte": date_number(selected.period_start)}})
    if options.chunk_types is not None:
        types = sorted(chunk_type.value for chunk_type in options.chunk_types)
        conditions.append({"chunk_type": {"$in": types}})
    if options.require_heading:
        conditions.append({"has_heading": {"$eq": True}})
    if not conditions:
        return None
    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


class Retriever:
    """Searches the chunk collection; the embedding client and collection are injected."""

    def __init__(self, settings: Settings, client: EmbeddingClient, collection: Collection):
        self._settings = settings
        self._client = client
        self._collection = collection

    def embed_query(self, query: str) -> list[float]:
        """Embedding of a query with the ``search_query:`` task prefix."""
        retrieval = self._settings.retrieval
        text = f"{retrieval.query_task_prefix}{query}"
        return embed_texts(
            self._client, self._settings.models.embedding, [text], retrieval.keep_alive
        )[0]

    def search(
        self,
        query: str,
        options: SearchOptions | None = None,
        query_vector: list[float] | None = None,
    ) -> list[SearchHit]:
        """Top hits for a query; pass ``query_vector`` to reuse an embedding."""
        options = options or SearchOptions()
        retrieval = self._settings.retrieval
        if not query.strip():
            raise RetrievalError("empty query")
        total = self._collection.count()
        if total == 0:
            raise RetrievalError("the index is empty; run `python -m audit_agent.retrieval index`")
        vector = query_vector if query_vector is not None else self.embed_query(query)
        result = self._collection.query(
            query_embeddings=[vector],
            n_results=min(retrieval.candidate_count, total),
            where=build_where(options),
            include=["documents", "metadatas", "distances"],
        )
        terms = tokenize_query(query, retrieval.min_term_chars)
        hits = [
            self._to_hit(chunk_id, content, metadata, distance, terms, options)
            for chunk_id, content, metadata, distance in zip(
                result["ids"][0],
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
                strict=True,
            )
        ]
        hits_ranked = sorted(hits, key=lambda h: (-h.final_score, -h.base_score, h.chunk_id))
        return hits_ranked[: options.top_k or retrieval.top_k]

    def _to_hit(
        self,
        chunk_id: str,
        content: str,
        metadata: dict[str, Any],
        distance: float,
        terms: tuple[str, ...],
        options: SearchOptions,
    ) -> SearchHit:
        retrieval = self._settings.retrieval
        heading_stack = tuple(json.loads(metadata["heading_stack"]))
        matched = (
            path_matches(terms, metadata["filename"], heading_stack, retrieval.min_term_chars)
            if options.use_hierarchy_boost
            else ()
        )
        boost = retrieval.hierarchy_boost if matched else 1.0
        base_score = 1.0 - distance
        return SearchHit(
            chunk_id=chunk_id,
            chunk_type=ChunkType(metadata["chunk_type"]),
            content=content,
            heading_stack=heading_stack,
            page_number=metadata["page_number"],
            filename=metadata["filename"],
            base_score=base_score,
            boost=boost,
            final_score=base_score * boost,
            matched_terms=matched,
        )
