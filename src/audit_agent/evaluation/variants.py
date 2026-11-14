"""The three variants of the comparison (concept.md, 7.1 and 11.1; ADR-0011).

- **B0** full text: as much page text as fits into the context window, one model call.
- **P1** pipeline: one retrieval pass (top 5, no filter, hierarchy boost), one model call.
- **P2** agent: the ReAct loop of M5 with its tools.

All three use the same chat client, model, context size and citation format ``[n]``, so the
comparison measures how the evidence is chosen and not how the model is asked.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from audit_agent.agent.log import RunLog
from audit_agent.agent.loop import ChatClient, chat_arguments, estimate_tokens, model_call_step
from audit_agent.agent.models import AgentRun, ModelCallStep, StepCallback, ToolCallStep
from audit_agent.agent.tools import SearchBackend
from audit_agent.config import Settings
from audit_agent.corpus import DocumentCatalog, Question
from audit_agent.evaluation.models import (
    EvaluationError,
    ShownSource,
    ToolUse,
    VariantAnswer,
    VariantName,
)
from audit_agent.evaluation.prompts import evidence_prompt
from audit_agent.ingestion import ChunkType, ParsedDocument, chunks_path, load_parsed_document
from audit_agent.retrieval import SearchOptions
from audit_agent.retrieval.evidence import render_numbered_hit

PIPELINE_CHUNK_TYPES = frozenset({ChunkType.TEXT, ChunkType.TABLE_ROW, ChunkType.IMAGE})
"""P1 searches what the agent's three search tools search together (summaries see ADR-0008)."""
FULL_TEXT_CHUNK_TYPES = frozenset({ChunkType.TEXT, ChunkType.HEADING, ChunkType.TABLE_ROW})
"""B0 gets the parsed PDF text only, no model-written captions or summaries."""
NO_HITS = "(keine Treffer)"


class Variant(Protocol):
    """Answers one question of the ground truth."""

    name: VariantName

    def answer(self, question: Question, model: str) -> VariantAnswer: ...


class AgentRunner(Protocol):
    """What P2 needs from the agent loop (tests inject a scripted loop)."""

    def run(
        self, question: str, model: str | None = None, on_step: StepCallback | None = None
    ) -> AgentRun: ...


def _ask_once(
    client: ChatClient, settings: Settings, model: str, context: str, question: str
) -> ModelCallStep:
    messages: list[Any] = [
        {"role": "system", "content": evidence_prompt(context)},
        {"role": "user", "content": question},
    ]
    started = time.perf_counter()
    response = client.chat(**chat_arguments(settings, model, messages))
    return model_call_step(
        response,
        index=0,
        offered_tools=False,
        message_count=len(messages),
        seconds=time.perf_counter() - started,
    )


def _single_call_answer(
    variant: VariantName,
    question: Question,
    model: str,
    step: ModelCallStep,
    sources: tuple[ShownSource, ...],
    started: float,
) -> VariantAnswer:
    return VariantAnswer(
        variant=variant,
        question_id=question.id,
        model=model,
        answer=step.content,
        stop_reason="answer" if step.content else "empty_answer",
        seconds=round(time.perf_counter() - started, 1),
        sources=sources,
        model_calls=(step,),
    )


class PipelineVariant:
    """P1: retrieve the top hits once, then let the model write the answer from them."""

    name: VariantName = "p1"

    def __init__(self, settings: Settings, client: ChatClient, backend: SearchBackend):
        self._settings = settings
        self._client = client
        self._backend = backend

    def answer(self, question: Question, model: str) -> VariantAnswer:
        started = time.perf_counter()
        types = set(PIPELINE_CHUNK_TYPES)
        if self._settings.agent.include_table_summaries:
            types.add(ChunkType.TABLE_SUMMARY)
        hits = self._backend.search(question.question, SearchOptions(chunk_types=frozenset(types)))
        limit = self._settings.agent.max_hit_chars
        blocks = [render_numbered_hit(n, hit, limit) for n, hit in enumerate(hits, start=1)]
        sources = tuple(
            ShownSource(
                number=n,
                filename=hit.filename,
                page_number=hit.page_number,
                chunk_type=hit.chunk_type,
            )
            for n, hit in enumerate(hits, start=1)
        )
        context = "\n\n".join(blocks) or NO_HITS
        step = _ask_once(self._client, self._settings, model, context, question.question)
        return _single_call_answer(self.name, question, model, step, sources, started)


class FullTextContext(BaseModel):
    """The B0 context: numbered page blocks in catalog order until the token budget is used."""

    model_config = ConfigDict(frozen=True)

    text: str
    sources: tuple[ShownSource, ...]
    budget_tokens: int
    estimated_tokens: int
    complete_files: tuple[str, ...]
    partial_file: str | None
    """The file whose pages were cut off at the budget (``None`` if a file ended exactly)."""
    missing_files: tuple[str, ...]
    """Files that did not fit at all."""


def page_blocks(document: ParsedDocument) -> list[tuple[int, str]]:
    """Text, headings and table rows of each page, in reading order."""
    pages: dict[int, list[str]] = {}
    for chunk in document.chunks:
        if chunk.chunk_type in FULL_TEXT_CHUNK_TYPES:
            pages.setdefault(chunk.page_number, []).append(chunk.content)
    return [(page, "\n".join(lines)) for page, lines in sorted(pages.items())]


def full_text_budget(settings: Settings) -> int:
    """Tokens left for the documents after prompt, question reserve and answer."""
    return (
        settings.num_ctx
        - settings.agent.num_predict
        - settings.evaluation.full_text_reserve_tokens
        - estimate_tokens(evidence_prompt(""))
    )


def build_full_text_context(settings: Settings, catalog: DocumentCatalog) -> FullTextContext:
    """Fill the budget with whole pages, file by file in catalog order; stop at the first miss.

    Fails fast if a processed file is missing (run the ingestion first). The token count is
    the conservative estimate of the agent (characters / 3), so Ollama never cuts the prompt.
    """
    budget = full_text_budget(settings)
    blocks: list[str] = []
    sources: list[ShownSource] = []
    complete: list[str] = []
    partial: str | None = None
    used = 0
    files = [document.file for document in catalog.documents]
    for index, file in enumerate(files):
        path = chunks_path(settings.processed_dir, file)
        if not path.exists():
            raise EvaluationError(f"{path} is missing; run `python -m audit_agent.ingestion`")
        pages = page_blocks(load_parsed_document(path))
        for position, (page, body) in enumerate(pages):
            number = len(sources) + 1
            block = f"[{number}] {PurePosixPath(file).name}, S. {page}\n{body}"
            cost = estimate_tokens(block) + 1
            if used + cost > budget:
                partial = file if position > 0 else None
                missing = files[index + 1 :] if partial else files[index:]
                return FullTextContext(
                    text="\n\n".join(blocks),
                    sources=tuple(sources),
                    budget_tokens=budget,
                    estimated_tokens=used,
                    complete_files=tuple(complete),
                    partial_file=partial,
                    missing_files=tuple(missing),
                )
            used += cost
            blocks.append(block)
            sources.append(ShownSource(number=number, filename=file, page_number=page))
        complete.append(file)
    return FullTextContext(
        text="\n\n".join(blocks),
        sources=tuple(sources),
        budget_tokens=budget,
        estimated_tokens=used,
        complete_files=tuple(complete),
        partial_file=None,
        missing_files=(),
    )


class FullTextVariant:
    """B0: the same full-text context for every question (Ollama may reuse it as prefix)."""

    name: VariantName = "b0"

    def __init__(self, settings: Settings, client: ChatClient, context: FullTextContext):
        self._settings = settings
        self._client = client
        self._context = context

    def answer(self, question: Question, model: str) -> VariantAnswer:
        started = time.perf_counter()
        step = _ask_once(self._client, self._settings, model, self._context.text, question.question)
        return _single_call_answer(self.name, question, model, step, self._context.sources, started)


def answer_from_run(question: Question, run: AgentRun) -> VariantAnswer:
    """Translate an agent run of M5 into the common answer record."""
    return VariantAnswer(
        variant="p2",
        question_id=question.id,
        model=run.model,
        answer=run.answer,
        stop_reason=run.stop_reason,
        seconds=run.seconds,
        sources=tuple(
            ShownSource(
                number=source.number,
                filename=source.hit.filename,
                page_number=source.hit.page_number,
                chunk_type=source.hit.chunk_type,
            )
            for source in run.sources
        ),
        tool_uses=tuple(
            ToolUse(name=step.tool, arguments=step.arguments, is_valid=step.is_valid)
            for step in run.steps
            if isinstance(step, ToolCallStep)
        ),
        model_calls=tuple(step for step in run.steps if isinstance(step, ModelCallStep)),
    )


class AgentVariant:
    """P2: the agent loop; every step is also logged to ``p2-<question>.jsonl``."""

    name: VariantName = "p2"

    def __init__(self, agent: AgentRunner, log_dir: Path | None = None):
        self._agent = agent
        self._log_dir = log_dir

    def answer(self, question: Question, model: str) -> VariantAnswer:
        log = RunLog(self._log_dir / f"p2-{question.id}.jsonl") if self._log_dir else None
        run = self._agent.run(question.question, model=model, on_step=log)
        if log is not None:
            log.finish(run)
        return answer_from_run(question, run)


def needs_index(names: Sequence[VariantName]) -> bool:
    """P1 and P2 search the vector index (and therefore need the embedding model)."""
    return any(name in ("p1", "p2") for name in names)
