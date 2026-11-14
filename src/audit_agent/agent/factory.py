"""Wiring: settings + Ollama client -> retriever -> tools -> agent loop (CLI and UI share it)."""

from __future__ import annotations

from typing import Protocol

from audit_agent.agent.loop import AgentLoop, ChatClient
from audit_agent.agent.tools import ToolBox
from audit_agent.config import Settings
from audit_agent.corpus import load_document_catalog
from audit_agent.retrieval import Retriever, get_collection, open_vector_client
from audit_agent.retrieval.index import EmbeddingClient


class OllamaClient(ChatClient, EmbeddingClient, Protocol):
    """Chat and embedding in one client (the real ``ollama.Client`` is both)."""


def create_agent(settings: Settings, client: OllamaClient) -> AgentLoop:
    """The agent on top of the existing index; fails fast if the index is missing."""
    catalog = load_document_catalog(settings.documents_file)
    collection = get_collection(settings, open_vector_client(settings))
    retriever = Retriever(settings, client, collection)
    return AgentLoop(settings, client, ToolBox(settings, retriever, catalog).tools())
