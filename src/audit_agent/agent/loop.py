"""The agent loop: model call -> tool calls -> observations -> ... -> answer (ADR-0006, ADR-0010).

The control flow is ReAct (think, act, observe); only the call format is native tool calling
of the Ollama chat API. The loop is bounded by ``AgentSettings.max_tool_calls`` and by the
context window; at the bound the model has to answer with what it has.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import ValidationError

from audit_agent.agent.models import (
    AgentRun,
    AgentStep,
    EvidenceBook,
    ModelCallStep,
    NudgeReason,
    NudgeStep,
    StepCallback,
    StopReason,
    ToolCallStep,
    ToolInvocation,
)
from audit_agent.agent.prompts import (
    CALCULATE_BEFORE_ANSWER_MESSAGE,
    FORCED_ANSWER_MESSAGE,
    REPEAT_OBSERVATION,
    RETRY_BEFORE_GAP_MESSAGE,
    is_audit_question,
    is_gap_answer,
    system_prompt,
)
from audit_agent.agent.tools import AgentTool, ToolError, clean_arguments
from audit_agent.config import Settings

NANOSECONDS_PER_SECOND = 1_000_000_000
CHARS_PER_TOKEN = 2.4
"""Characters per token of ``llama3.1:8b`` on our German texts, rounded down from measurements.

RUN-007: the B0 prompt (tables with many numbers) had 2.5 characters per token, the probe
text 2.8 (``scripts/probe_context.py``). The former value 3 underestimated the prompt, and
Ollama cut it to half of ``num_ctx`` (ISS-041).
"""
LIMIT_OBSERVATION = (
    "FEHLER: Das Limit der Werkzeugaufrufe ist erreicht. Antworte mit den vorhandenen Belegen."
)


class ChatClient(Protocol):
    """Subset of ``ollama.Client`` used by the loop (tests inject a fake)."""

    def chat(self, **kwargs: Any) -> Any: ...


def estimate_tokens(text: str) -> int:
    """Rough, deliberately high token count of a text (characters / ``CHARS_PER_TOKEN``)."""
    return int(len(text) / CHARS_PER_TOKEN) + 1


def _seconds(nanoseconds: int | None) -> float | None:
    return None if nanoseconds is None else nanoseconds / NANOSECONDS_PER_SECOND


def _invocations(message: Any) -> list[Any]:
    return list(message.tool_calls or [])


def _message_text(message: Any) -> str:
    """Content of a dict or ``Message`` plus the arguments of its tool calls."""
    content = message.get("content") if isinstance(message, dict) else message.content
    calls = "" if isinstance(message, dict) else str([c.function for c in _invocations(message)])
    return f"{content or ''}{calls}"


def chat_arguments(settings: Settings, model: str, messages: list[Any]) -> dict[str, Any]:
    """Arguments of one chat call; the agent and the evaluation variants use the same ones."""
    agent = settings.agent
    return {
        "model": model,
        "messages": messages,
        "options": {
            "num_ctx": settings.num_ctx,
            "num_predict": agent.num_predict,
            "temperature": agent.temperature,
        },
        "keep_alive": agent.keep_alive,
    }


def model_call_step(
    response: Any, index: int, offered_tools: bool, message_count: int, seconds: float
) -> ModelCallStep:
    """Log record of one chat response (token counts and durations as Ollama reports them)."""
    message = response.message
    return ModelCallStep(
        index=index,
        offered_tools=offered_tools,
        message_count=message_count,
        prompt_tokens=getattr(response, "prompt_eval_count", None),
        prefill_seconds=_seconds(getattr(response, "prompt_eval_duration", None)),
        generated_tokens=getattr(response, "eval_count", None),
        decode_seconds=_seconds(getattr(response, "eval_duration", None)),
        seconds=round(seconds, 2),
        content=(message.content or "").strip(),
        tool_calls=tuple(
            ToolInvocation(name=call.function.name, arguments=dict(call.function.arguments or {}))
            for call in _invocations(message)
        ),
    )


def _validation_summary(error: ValidationError) -> str:
    parts = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "Argumente"
        parts.append(f"{location}: {item['msg']}")
    return "; ".join(parts)


class AgentLoop:
    """Runs one question to an answer. Stateless between questions."""

    def __init__(self, settings: Settings, client: ChatClient, tools: Mapping[str, AgentTool]):
        self._settings = settings
        self._client = client
        self._tools = dict(tools)
        self._specs = [tool.spec() for tool in tools.values()]
        self._spec_tokens = estimate_tokens(json.dumps(self._specs, ensure_ascii=False))

    def run(
        self, question: str, model: str | None = None, on_step: StepCallback | None = None
    ) -> AgentRun:
        """Answer one question; ``on_step`` sees every step as soon as it is finished."""
        agent = self._settings.agent
        model = model or self._settings.models.agent
        started = time.perf_counter()
        book = EvidenceBook()
        steps: list[AgentStep] = []
        messages: list[Any] = [
            {"role": "system", "content": system_prompt(agent.max_tool_calls)},
            {"role": "user", "content": question},
        ]

        def emit(step: AgentStep) -> None:
            steps.append(step)
            if on_step is not None:
                on_step(step, book)

        def nudge(message: Any, reason: NudgeReason, text: str) -> None:
            messages.extend([message, {"role": "user", "content": text}])
            emit(NudgeStep(index=len(steps), message=text, reason=reason))

        tool_call_count = 0
        forced: StopReason | None = None
        is_gap_questioned = False
        is_calculate_questioned = False
        is_calculated = False
        is_audit = is_audit_question(question)
        seen_calls: set[tuple[str, str]] = set()
        answer = ""
        stop_reason: StopReason = "answer"
        while True:
            if forced is not None:
                messages.append({"role": "user", "content": FORCED_ANSWER_MESSAGE})
            response, model_step = self._call_model(
                model, messages, len(steps), offer_tools=forced is None
            )
            emit(model_step)
            message = response.message
            calls = [] if forced is not None else _invocations(message)
            if not calls:
                answer = (message.content or "").strip()
                if (
                    forced is None
                    and not is_gap_questioned
                    and tool_call_count < agent.min_searches_before_gap
                    and is_gap_answer(answer)
                ):
                    is_gap_questioned = True
                    nudge(message, "gap", RETRY_BEFORE_GAP_MESSAGE)
                    continue
                if (
                    forced is None
                    and is_audit
                    and not is_calculated
                    and not is_calculate_questioned
                    and tool_call_count > 0
                    and answer
                    and not is_gap_answer(answer)
                ):
                    is_calculate_questioned = True
                    nudge(message, "calculate", CALCULATE_BEFORE_ANSWER_MESSAGE)
                    continue
                stop_reason = forced or ("answer" if answer else "empty_answer")
                break

            messages.append(message)
            for call in calls:
                if tool_call_count >= agent.max_tool_calls:
                    observation = LIMIT_OBSERVATION
                    messages.append(
                        {"role": "tool", "tool_name": call.function.name, "content": observation}
                    )
                    continue
                tool_call_count += 1
                tool_step = self._execute(call, book, seen_calls, index=len(steps))
                emit(tool_step)
                if tool_step.tool == "calculate" and tool_step.is_valid and not tool_step.is_repeat:
                    is_calculated = True
                messages.append(
                    {"role": "tool", "tool_name": tool_step.tool, "content": tool_step.observation}
                )
            if tool_call_count >= agent.max_tool_calls:
                forced = "tool_limit"
            elif self._is_context_full(messages):
                forced = "context_limit"

        return AgentRun(
            question=question,
            model=model,
            answer=answer,
            stop_reason=stop_reason,
            tool_call_count=tool_call_count,
            seconds=round(time.perf_counter() - started, 1),
            steps=tuple(steps),
            sources=book.numbered_hits,
        )

    def _is_context_full(self, messages: list[Any]) -> bool:
        """True if one more observation and the answer would not fit into the context.

        The size is estimated from the text itself: Ollama's ``prompt_eval_count`` leaves out
        tokens that came from its prompt cache, so it cannot tell how full the window is.
        """
        agent = self._settings.agent
        used = self._spec_tokens + sum(estimate_tokens(_message_text(m)) for m in messages)
        free = self._settings.num_ctx - agent.num_predict - agent.context_reserve_tokens
        return used > free

    def _call_model(
        self, model: str, messages: list[Any], index: int, offer_tools: bool
    ) -> tuple[Any, ModelCallStep]:
        arguments = chat_arguments(self._settings, model, messages)
        if offer_tools:
            arguments["tools"] = self._specs
        started = time.perf_counter()
        response = self._client.chat(**arguments)
        step = model_call_step(
            response,
            index=index,
            offered_tools=offer_tools,
            message_count=len(messages),
            seconds=time.perf_counter() - started,
        )
        return response, step

    def _execute(
        self, call: Any, book: EvidenceBook, seen: set[tuple[str, str]], index: int
    ) -> ToolCallStep:
        """Validate the arguments and run the tool; every failure becomes an observation.

        ``seen`` holds the valid calls of this question (name and validated arguments). A call
        that was made before is not run again: the model gets ``REPEAT_OBSERVATION`` (ISS-058).
        """
        name = call.function.name
        raw = dict(call.function.arguments or {})
        started = time.perf_counter()
        is_valid = True
        is_repeat = False
        hit_numbers: tuple[int, ...] = ()
        tool = self._tools.get(name)
        if tool is None:
            is_valid = False
            observation = (
                f"FEHLER: Unbekanntes Werkzeug {name!r}. Verfügbar: {', '.join(self._tools)}."
            )
        else:
            try:
                arguments = tool.arguments.model_validate(clean_arguments(raw))
            except ValidationError as error:
                is_valid = False
                observation = (
                    f"FEHLER: Ungültige Argumente für {name}: {_validation_summary(error)}. "
                    f"Richtiger Aufruf: {tool.usage()} (* = Pflicht)."
                )
            else:
                key = (name, arguments.model_dump_json())
                if key in seen:
                    is_repeat = True
                    observation = REPEAT_OBSERVATION
                else:
                    seen.add(key)
                    try:
                        result = tool.run(arguments, book)
                        observation, hit_numbers = result.text, result.hit_numbers
                    except ToolError as error:
                        is_valid = False
                        observation = f"FEHLER: {error}"
        return ToolCallStep(
            index=index,
            tool=name,
            arguments=raw,
            is_valid=is_valid,
            observation=observation,
            seconds=round(time.perf_counter() - started, 2),
            hit_numbers=hit_numbers,
            is_repeat=is_repeat,
        )
