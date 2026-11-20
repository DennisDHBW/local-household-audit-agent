"""The agent loop: model call -> tool calls -> observations -> ... -> answer (ADR-0006, ADR-0010).

The control flow is ReAct (think, act, observe); only the call format is native tool calling
of the Ollama chat API. The loop is bounded by ``AgentSettings.max_tool_calls`` and by the
context window; at the bound the model has to answer with what it has.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from typing import Any, Protocol

from ollama import Message
from pydantic import ValidationError

from audit_agent.agent.audit_flow import run_audit_flow
from audit_agent.agent.models import (
    AgentRun,
    AgentStep,
    Artifact,
    AuditFlowStep,
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
    CHART_BEFORE_ANSWER_MESSAGE,
    CHECK_BEFORE_ANSWER_MESSAGE,
    CITE_BEFORE_ANSWER_MESSAGE,
    FORCED_ANSWER_MESSAGE,
    NUMBERS_BEFORE_ANSWER_MESSAGE,
    OVERVIEW_BEFORE_ANSWER_MESSAGE,
    PLAN_HINT,
    PLAN_STEP_MISSING_MESSAGE,
    REPEAT_FAILED_OBSERVATION,
    REPEAT_OBSERVATION,
    RETRY_BEFORE_GAP_MESSAGE,
    RETRY_BEFORE_GAP_MESSAGE_V2,
    VERDICT_MISMATCH_MESSAGE,
    answer_says_correct,
    drop_trailing_gap,
    has_citation,
    is_audit_question,
    is_gap_answer,
    system_prompt,
    system_prompt_v2,
    unsupported_numbers,
    wants_chart,
    wants_overview,
)
from audit_agent.agent.scope import CURRENT_QUESTION, REPAIR_NOTES, route_tools
from audit_agent.agent.text_calls import TextCall, parse_text_call
from audit_agent.agent.tools import AgentTool, ToolError, clean_arguments
from audit_agent.config import Settings

NANOSECONDS_PER_SECOND = 1_000_000_000
HISTORY_TURNS = 2
HISTORY_ANSWER_CHARS = 600
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


def _native_call(call: TextCall) -> Any:
    """A text call in the shape of a native one, so that the loop treats both the same."""
    function = Message.ToolCall.Function(name=call.name, arguments=call.arguments)
    return Message.ToolCall(function=function)


class _CallMemory:
    """The calls of one question: what ran (``valid``) and what failed (``failed``).

    A valid call is identified by its tool and validated arguments, a failed one by its tool
    and cleaned raw arguments (they never became a validated model). Neither is run twice.
    """

    def __init__(self) -> None:
        self.valid: set[tuple[str, str]] = set()
        self.failed: set[tuple[str, str]] = set()


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
        self._active_specs = self._specs
        self._spec_tokens = estimate_tokens(json.dumps(self._specs, ensure_ascii=False))

    def run(
        self,
        question: str,
        model: str | None = None,
        on_step: StepCallback | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> AgentRun:
        """Answer one question; ``on_step`` sees every step as soon as it is finished.

        ``history`` holds earlier questions and answers of the same chat (oldest first); the
        last two turns go into the prompt so that "und jetzt als Grafik?" works (ADR-0019).
        """
        agent = self._settings.agent
        model = model or self._settings.models.agent
        is_v2 = agent.tool_set == "v2"
        started = time.perf_counter()
        book = EvidenceBook()
        steps: list[AgentStep] = []
        prompt = system_prompt_v2 if is_v2 else system_prompt
        messages: list[Any] = [{"role": "system", "content": prompt(agent.max_tool_calls)}]
        for earlier_question, earlier_answer in (history or [])[-HISTORY_TURNS:]:
            messages.append({"role": "user", "content": earlier_question})
            messages.append({"role": "assistant", "content": earlier_answer[:HISTORY_ANSWER_CHARS]})
        messages.append({"role": "user", "content": question})
        context_text = " ".join(q for q, _ in (history or [])[-HISTORY_TURNS:]) + " " + question
        question_token = CURRENT_QUESTION.set(context_text)
        self._active_specs = self._specs
        if is_v2 and agent.route_tools:
            offered = route_tools(question, context_text)
            self._active_specs = [
                tool.spec() for name, tool in self._tools.items() if name in offered
            ]
        is_plan_hinted = not is_v2

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
        is_cite_questioned = False
        is_calculated = False
        is_audit = is_audit_question(question)
        verify = is_v2 and agent.verify_answer
        asked: set[NudgeReason] = set()
        memory = _CallMemory()
        answer = ""
        stop_reason: StopReason = "answer"

        if is_audit and agent.audit_flow_enabled:
            is_calculated = self._run_audit_flow(
                question, model, messages, book, memory, emit, lambda: len(steps)
            )

        while True:
            if forced is not None:
                messages.append({"role": "user", "content": FORCED_ANSWER_MESSAGE})
            response, model_step = self._call_model(
                model, messages, len(steps), offer_tools=forced is None
            )
            emit(model_step)
            message = response.message
            calls = [] if forced is not None else _invocations(message)
            is_text_call = False
            if not calls and forced is None:
                text_call = parse_text_call(message.content or "", self._tools)
                if text_call is not None:
                    calls, is_text_call = [_native_call(text_call)], True
            if not calls:
                answer = (message.content or "").strip()
                if is_v2:
                    answer = drop_trailing_gap(answer)
                if (
                    forced is None
                    and not is_gap_questioned
                    and tool_call_count < agent.min_searches_before_gap
                    and is_gap_answer(answer)
                ):
                    is_gap_questioned = True
                    nudge(
                        message,
                        "gap",
                        RETRY_BEFORE_GAP_MESSAGE_V2 if is_v2 else RETRY_BEFORE_GAP_MESSAGE,
                    )
                    continue
                if verify and forced is None and tool_call_count > 0:
                    reason = self._self_check(question, context_text, answer, steps, asked)
                    if reason is not None:
                        asked.add(reason[0])
                        nudge(message, reason[0], reason[1])
                        continue
                if (
                    not is_v2
                    and forced is None
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
                if (
                    forced is None
                    and agent.require_citation
                    and not is_cite_questioned
                    and tool_call_count > 0
                    and any(char.isdigit() for char in answer)
                    and not has_citation(answer)
                    and not is_gap_answer(answer)
                ):
                    is_cite_questioned = True
                    nudge(message, "cite", CITE_BEFORE_ANSWER_MESSAGE)
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
                tool_step = self._execute(call, book, memory, len(steps), is_text_call)
                emit(tool_step)
                if tool_step.tool == "calculate" and tool_step.is_valid and not tool_step.is_repeat:
                    is_calculated = True
                content = tool_step.observation
                if not is_plan_hinted and tool_step.tool != "plan":
                    is_plan_hinted = True  # cheap: no extra model call (ISS-114)
                    content += "\n" + PLAN_HINT
                elif tool_step.tool == "plan":
                    is_plan_hinted = True
                messages.append({"role": "tool", "tool_name": tool_step.tool, "content": content})
            if tool_call_count >= agent.max_tool_calls:
                forced = "tool_limit"
            elif self._is_context_full(messages):
                forced = "context_limit"

        CURRENT_QUESTION.reset(question_token)
        self._active_specs = self._specs
        artifacts = tuple(
            a for s in steps if isinstance(s, ToolCallStep) and not s.is_repeat for a in s.artifacts
        )
        return AgentRun(
            question=question,
            model=model,
            answer=answer,
            stop_reason=stop_reason,
            tool_call_count=tool_call_count,
            seconds=round(time.perf_counter() - started, 1),
            steps=tuple(steps),
            sources=book.numbered_hits,
            artifacts=artifacts,
        )

    def _unplanned(self, steps: list[AgentStep], used: set[str]) -> list[str]:
        """Result tools named in the plan that never ran (search and lists are optional)."""
        plan = next(
            (s for s in steps if isinstance(s, ToolCallStep) and s.tool == "plan" and s.is_valid),
            None,
        )
        if plan is None:
            return []
        text = " ".join(str(step) for step in plan.arguments.get("steps", []) or [])
        wanted = ("check_bill", "get_facts", "make_chart", "make_overview")
        return [
            name for name in wanted if name in text and name in self._tools and name not in used
        ]

    def _self_check(
        self,
        question: str,
        context_text: str,
        answer: str,
        steps: list[AgentStep],
        asked: set[NudgeReason],
    ) -> tuple[NudgeReason, str] | None:
        """The v2 self-check before an answer is accepted; each reason is asked once.

        Order: missing audit, missing chart, missing overview, numbers without source.
        A "not in the documents" answer is not questioned here (the gap rule handles it).
        """
        if is_gap_answer(answer):
            return None
        valid = [s for s in steps if isinstance(s, ToolCallStep) and s.is_valid]
        used = {s.tool for s in valid}
        if "check" not in asked and is_audit_question(question) and "check_bill" not in used:
            return "check", CHECK_BEFORE_ANSWER_MESSAGE
        if "chart" not in asked and wants_chart(context_text) and "make_chart" not in used:
            return "chart", CHART_BEFORE_ANSWER_MESSAGE
        if (
            "overview" not in asked
            and wants_overview(question)
            and not used & {"make_overview", "make_chart"}
        ):
            return "overview", OVERVIEW_BEFORE_ANSWER_MESSAGE
        if "verdict" not in asked:
            audits = [s.observation for s in valid if s.tool == "check_bill"]
            results: set[bool] = set()  # True = check_bill found the bill wrong
            for observation in audits:
                if "Die Rechnung stimmt nicht." in observation:
                    results.add(True)
                if "Die Rechnung stimmt nach diesen Regeln." in observation:
                    results.add(False)
            says_correct = answer_says_correct(answer)
            if len(results) == 1 and says_correct is not None:
                is_wrong = next(iter(results))
                if says_correct == is_wrong:
                    result = "Rechnung stimmt nicht" if is_wrong else "Rechnung stimmt"
                    return "verdict", VERDICT_MISMATCH_MESSAGE.format(result=result)
        if "plan" not in asked:
            missing_steps = self._unplanned(steps, used)
            if missing_steps:
                return "plan", PLAN_STEP_MISSING_MESSAGE.format(tools=", ".join(missing_steps))
        if "numbers" not in asked:
            sources = [s.observation for s in valid] + [context_text]
            missing = unsupported_numbers(answer, sources)
            if missing:
                return "numbers", NUMBERS_BEFORE_ANSWER_MESSAGE.format(
                    numbers=", ".join(missing[:6])
                )
        return None

    def _run_audit_flow(
        self,
        question: str,
        model: str,
        messages: list[Any],
        book: EvidenceBook,
        memory: _CallMemory,
        emit: Callable[[AgentStep], None],
        next_index: Callable[[], int],
    ) -> bool:
        """Run the fixed audit flow (ADR-0016); True if it computed a difference.

        The flow's model calls and tool calls are logged like any other step. Its findings
        go to the model as one message; without findings the loop continues as before.
        """
        started = time.perf_counter()

        def ask_model(flow_messages: list[dict[str, str]], schema: dict[str, Any]) -> str:
            response, step = self._call_model(
                model, flow_messages, next_index(), offer_tools=False, output_format=schema
            )
            emit(step)
            return str(response.message.content or "")

        def run_tool(name: str, arguments: dict[str, object]) -> ToolCallStep:
            call = Message.ToolCall(
                function=Message.ToolCall.Function(name=name, arguments=arguments)
            )
            step = self._execute(call, book, memory, next_index(), False, is_flow_call=True)
            emit(step)
            return step

        def hit_content(number: int) -> str:
            hits = book.numbered_hits
            return hits[number - 1].hit.content if 1 <= number <= len(hits) else ""

        checks, finding = run_audit_flow(
            question,
            ask_model,
            run_tool,
            hit_content,
            self._settings.agent.audit_max_checks,
        )
        emit(
            AuditFlowStep(
                index=next_index(),
                checks=checks,
                message=finding,
                seconds=round(time.perf_counter() - started, 1),
            )
        )
        if finding:
            messages.append({"role": "user", "content": finding})
        return any(check.difference is not None for check in checks)

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
        self,
        model: str,
        messages: list[Any],
        index: int,
        offer_tools: bool,
        output_format: dict[str, Any] | None = None,
    ) -> tuple[Any, ModelCallStep]:
        arguments = chat_arguments(self._settings, model, messages)
        if offer_tools:
            arguments["tools"] = self._active_specs
        if output_format is not None:
            arguments["format"] = output_format
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
        self,
        call: Any,
        book: EvidenceBook,
        memory: _CallMemory,
        index: int,
        is_text_call: bool,
        is_flow_call: bool = False,
    ) -> ToolCallStep:
        """Validate the arguments and run the tool; every failure becomes an observation.

        A call that ran before, or that failed before with the same arguments, is not run
        again: the model gets ``REPEAT_OBSERVATION`` or ``REPEAT_FAILED_OBSERVATION``
        (ISS-058, ISS-063).
        """
        name = call.function.name
        raw = dict(call.function.arguments or {})
        started = time.perf_counter()
        is_valid = True
        is_repeat = False
        hit_numbers: tuple[int, ...] = ()
        artifacts: tuple[Artifact, ...] = ()
        notes_token = None
        tool = self._tools.get(name)
        failed_key = (name, json.dumps(clean_arguments(raw), sort_keys=True, default=str))
        if tool is None:
            is_valid = False
            observation = (
                f"FEHLER: Unbekanntes Werkzeug {name!r}. Verfügbar: {', '.join(self._tools)}."
            )
        elif failed_key in memory.failed:
            is_valid, is_repeat = False, True
            observation = REPEAT_FAILED_OBSERVATION
        else:
            notes_token = REPAIR_NOTES.set([])
            try:
                arguments = tool.arguments.model_validate(clean_arguments(raw))
                repairs = list(REPAIR_NOTES.get() or [])
            except ValidationError as error:
                repairs = []
                is_valid = False
                memory.failed.add(failed_key)
                observation = (
                    f"FEHLER: Ungültige Argumente für {name}: {_validation_summary(error)}. "
                    f"Richtiger Aufruf: {tool.usage()} (* = Pflicht)."
                )
            else:
                key = (name, arguments.model_dump_json())
                if key in memory.valid:
                    is_repeat = True
                    observation = REPEAT_OBSERVATION
                else:
                    memory.valid.add(key)
                    try:
                        result = tool.run(arguments, book)
                        observation, hit_numbers = result.text, result.hit_numbers
                        artifacts = result.artifacts
                        if repairs:
                            observation = (
                                f"Hinweis: Argumente angepasst ({'; '.join(repairs)}).\n"
                                + observation
                            )
                    except ToolError as error:
                        is_valid = False
                        memory.failed.add(failed_key)
                        observation = f"FEHLER: {error}"
        if notes_token is not None:
            REPAIR_NOTES.reset(notes_token)
        return ToolCallStep(
            index=index,
            tool=name,
            arguments=raw,
            is_valid=is_valid,
            observation=observation,
            seconds=round(time.perf_counter() - started, 2),
            hit_numbers=hit_numbers,
            is_repeat=is_repeat,
            is_text_call=is_text_call,
            is_flow_call=is_flow_call,
            artifacts=artifacts,
        )
