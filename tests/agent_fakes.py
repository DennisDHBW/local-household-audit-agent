"""Fakes for the agent tests: a scripted chat client and a search backend without Ollama."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from ollama import ChatResponse, Message

from audit_agent.corpus import DocType, DocumentCatalog, DocumentMeta, UtilityType
from audit_agent.ingestion import ChunkType
from audit_agent.retrieval import SearchHit, SearchOptions

BILL_FILE = "01_electricity_x/04_Strom_Jahresabrechnung_2024.pdf"
CONTRACT_FILE = "01_electricity_x/01_Strom_Vertrag_2024.pdf"
NOTICE_FILE = "01_electricity_x/03_Strom_Preisanpassung_2025.pdf"
GAS_FILE = "02_gas_y/10_Gas_Jahresabrechnung_2025.pdf"


def make_catalog() -> DocumentCatalog:
    common = {"provider": "Test GmbH", "contract_id": "V-1"}
    return DocumentCatalog(
        documents=(
            DocumentMeta(
                file=CONTRACT_FILE,
                utility_type=UtilityType.ELECTRICITY,
                doc_type=DocType.CONTRACT,
                document_date=date(2023, 12, 12),
                valid_from=date(2024, 1, 1),
                **common,
            ),
            DocumentMeta(
                file=NOTICE_FILE,
                utility_type=UtilityType.ELECTRICITY,
                doc_type=DocType.PRICE_ADJUSTMENT,
                document_date=date(2024, 11, 15),
                valid_from=date(2025, 1, 1),
                **common,
            ),
            DocumentMeta(
                file=BILL_FILE,
                utility_type=UtilityType.ELECTRICITY,
                doc_type=DocType.BILL,
                document_date=date(2025, 1, 18),
                billing_period_start=date(2024, 1, 1),
                billing_period_end=date(2024, 12, 31),
                **common,
            ),
            DocumentMeta(
                file=GAS_FILE,
                utility_type=UtilityType.GAS,
                doc_type=DocType.BILL,
                provider="Gas AG",
                contract_id="G-9",
                document_date=date(2026, 1, 20),
                billing_period_start=date(2025, 1, 1),
                billing_period_end=date(2025, 12, 31),
            ),
        )
    )


def make_hit(
    chunk_id: str = "c1",
    chunk_type: ChunkType = ChunkType.TABLE_ROW,
    filename: str = BILL_FILE,
    content: str = "Arbeitspreis | 3.250 kWh | 34,80 ct/kWh",
    heading_stack: tuple[str, ...] = ("Jahresrechnung",),
    page_number: int = 1,
    base_score: float = 0.6,
) -> SearchHit:
    return SearchHit(
        chunk_id=chunk_id,
        chunk_type=chunk_type,
        content=content,
        heading_stack=heading_stack,
        page_number=page_number,
        filename=filename,
        base_score=base_score,
        boost=1.0,
        final_score=base_score,
    )


class FakeBackend:
    """Search backend that answers with ``responder`` and remembers every call."""

    def __init__(self, responder: Callable[[str, SearchOptions | None], list[SearchHit]]):
        self._responder = responder
        self.calls: list[tuple[str, SearchOptions | None]] = []

    def search(self, query: str, options: SearchOptions | None = None) -> list[SearchHit]:
        self.calls.append((query, options))
        return self._responder(query, options)


def answer_reply(text: str, prompt_tokens: int = 100, prefill_seconds: float = 2.0) -> ChatResponse:
    return ChatResponse(
        model="fake",
        message=Message(role="assistant", content=text),
        prompt_eval_count=prompt_tokens,
        prompt_eval_duration=int(prefill_seconds * 1e9),
        eval_count=20,
        eval_duration=4_000_000_000,
    )


def tool_reply(*calls: tuple[str, dict[str, Any]], prompt_tokens: int = 100) -> ChatResponse:
    tool_calls = [
        Message.ToolCall(function=Message.ToolCall.Function(name=name, arguments=arguments))
        for name, arguments in calls
    ]
    return ChatResponse(
        model="fake",
        message=Message(role="assistant", content="", tool_calls=tool_calls),
        prompt_eval_count=prompt_tokens,
        prompt_eval_duration=int(2.0 * 1e9),
        eval_count=15,
        eval_duration=3_000_000_000,
    )


class ScriptedChat:
    """Returns the prepared replies in order; keeps a copy of every request."""

    def __init__(self, replies: list[ChatResponse]):
        self._replies = list(replies)
        self.requests: list[dict[str, Any]] = []

    def chat(self, **kwargs: Any) -> ChatResponse:
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return self._replies.pop(0)
