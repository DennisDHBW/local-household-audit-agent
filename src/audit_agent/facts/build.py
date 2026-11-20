"""Build the fact store from ``data/processed`` (no Ollama needed)."""

from __future__ import annotations

from pathlib import Path

from audit_agent.config import Settings
from audit_agent.corpus import load_document_catalog
from audit_agent.facts.extract import extract_document
from audit_agent.facts.models import Fact, FactStore
from audit_agent.ingestion import chunks_path, load_parsed_document


def facts_path(settings: Settings) -> Path:
    return settings.processed_dir / "facts.json"


def build_fact_store(settings: Settings) -> FactStore:
    """Read every parsed document of the catalog and extract its facts."""
    catalog = load_document_catalog(settings.documents_file)
    facts: list[Fact] = []
    for meta in catalog.documents:
        path = chunks_path(settings.processed_dir, meta.file)
        if not path.is_file():
            raise FileNotFoundError(f"{path} fehlt; zuerst die Ingestion laufen lassen")
        facts += extract_document(load_parsed_document(path), meta)
    return FactStore(facts=tuple(facts))


def load_fact_store(settings: Settings) -> FactStore:
    """Load ``facts.json``; build it on the fly if it is missing (it is cheap)."""
    path = facts_path(settings)
    if path.is_file():
        return FactStore.load(path)
    store = build_fact_store(settings)
    store.save(path)
    return store
