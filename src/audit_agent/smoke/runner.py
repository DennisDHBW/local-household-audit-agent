"""Smoke-test steps. Each step talks to Ollama through a small client protocol."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Protocol

import pymupdf
from ollama import Image

from audit_agent.config import Settings
from audit_agent.preflight import ensure_models_available, normalize_model_tag
from audit_agent.smoke import tasks
from audit_agent.smoke.metrics import (
    NANOSECONDS_PER_SECOND,
    EmbeddingResult,
    PrefixReuseResult,
    SmokeReport,
    SpeedResult,
    ToolCallingSummary,
    ToolCallResult,
    VisionResult,
    cosine_similarity,
    extract_numbers,
    is_prefix_reused,
    speed_from_response,
    tool_call_is_correct,
)

BYTES_PER_GB = 1_000_000_000


class OllamaClient(Protocol):
    """The subset of ``ollama.Client`` used here (lets tests inject a fake)."""

    def chat(self, **kwargs: Any) -> Any: ...
    def embed(self, **kwargs: Any) -> Any: ...
    def generate(self, **kwargs: Any) -> Any: ...
    def list(self) -> Any: ...
    def ps(self) -> Any: ...


def _options(settings: Settings, num_predict: int) -> dict[str, Any]:
    return {"num_ctx": settings.num_ctx, "num_predict": num_predict, "temperature": 0}


def unload_model(client: OllamaClient, model: str) -> None:
    """Free the RAM of one model (``keep_alive=0``)."""
    client.generate(model=model, prompt="", keep_alive=0)


def unload_all_running(client: OllamaClient) -> None:
    """Start every run from an empty memory so the 9 GB budget is not exceeded."""
    for running in client.ps().models:
        unload_model(client, running.model)


def resident_gb(client: OllamaClient, model: str) -> float | None:
    """Memory Ollama currently holds for ``model`` (None if it is not loaded)."""
    wanted = normalize_model_tag(model)
    for running in client.ps().models:
        if normalize_model_tag(running.model) == wanted:
            return running.size / BYTES_PER_GB
    return None


def measure_speed(client: OllamaClient, model: str, settings: Settings) -> SpeedResult:
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": tasks.build_speed_prompt()}],
        options=_options(settings, num_predict=64),
        keep_alive="10m",
    )
    return speed_from_response(model, response, resident_gb(client, model))


def measure_prefix_reuse(client: OllamaClient, model: str, settings: Settings) -> PrefixReuseResult:
    tokens: list[int | None] = []
    seconds: list[float | None] = []
    for question in tasks.PREFIX_QUESTIONS:
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": tasks.PREFIX_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            options=_options(settings, num_predict=8),
            keep_alive="10m",
        )
        tokens.append(getattr(response, "prompt_eval_count", None))
        duration = getattr(response, "prompt_eval_duration", None)
        seconds.append(None if duration is None else duration / NANOSECONDS_PER_SECOND)
    return PrefixReuseResult(
        model=model,
        first_prompt_tokens=tokens[0],
        second_prompt_tokens=tokens[1],
        first_prefill_seconds=seconds[0],
        second_prefill_seconds=seconds[1],
        is_prefix_reused=is_prefix_reused(seconds[0], seconds[1]),
    )


def run_tool_calling(client: OllamaClient, model: str, settings: Settings) -> ToolCallingSummary:
    results: list[ToolCallResult] = []
    for task in tasks.TOOL_TASKS:
        started = time.perf_counter()
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": tasks.TOOL_SYSTEM_PROMPT},
                {"role": "user", "content": task.prompt},
            ],
            tools=tasks.TOOLS,
            options=_options(settings, num_predict=200),
            keep_alive="10m",
        )
        seconds = time.perf_counter() - started
        tool_calls = response.message.tool_calls or []
        called_tool = tool_calls[0].function.name if tool_calls else None
        arguments = dict(tool_calls[0].function.arguments) if tool_calls else {}
        is_tool_correct, are_arguments_valid = tool_call_is_correct(
            called_tool, task.expected_tool, arguments, task.expected_arguments
        )
        results.append(
            ToolCallResult(
                task_id=task.task_id,
                called_tool=called_tool,
                arguments=arguments,
                is_tool_correct=is_tool_correct,
                are_arguments_valid=are_arguments_valid,
                seconds=seconds,
            )
        )
    return ToolCallingSummary(model=model, results=results)


def run_embedding(client: OllamaClient, model: str) -> EmbeddingResult:
    response = client.embed(
        model=model,
        input=[
            f"search_query: {tasks.EMBEDDING_QUERY}",
            f"search_document: {tasks.EMBEDDING_RELEVANT}",
            f"search_document: {tasks.EMBEDDING_IRRELEVANT}",
        ],
        keep_alive="2m",
    )
    query, relevant, irrelevant = response.embeddings
    relevant_similarity = cosine_similarity(query, relevant)
    irrelevant_similarity = cosine_similarity(query, irrelevant)
    return EmbeddingResult(
        model=model,
        dimensions=len(query),
        relevant_similarity=relevant_similarity,
        irrelevant_similarity=irrelevant_similarity,
        is_ranking_correct=relevant_similarity > irrelevant_similarity,
    )


def extract_chart_image(pdf_path: Path, page_index: int) -> tuple[bytes, str]:
    """Return the first embedded image of a PDF page (bytes, file extension)."""
    with pymupdf.open(pdf_path) as document:
        images = document[page_index].get_images(full=True)
        if not images:
            raise ValueError(f"No embedded image on page {page_index + 1} of {pdf_path.name}")
        extracted = document.extract_image(images[0][0])
    return extracted["image"], extracted["ext"]


def run_vision(client: OllamaClient, model: str, settings: Settings, out_dir: Path) -> VisionResult:
    image_bytes, extension = extract_chart_image(
        settings.dataset_dir / tasks.VISION_DOCUMENT, tasks.VISION_PAGE_INDEX
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / f"chart.{extension}"
    image_path.write_bytes(image_bytes)

    started = time.perf_counter()
    response = client.chat(
        model=model,
        messages=[
            {"role": "user", "content": tasks.VISION_PROMPT, "images": [Image(value=image_bytes)]}
        ],
        options=_options(settings, num_predict=300),
        keep_alive="5m",
    )
    seconds = time.perf_counter() - started
    caption = response.message.content or ""
    return VisionResult(
        model=model,
        page_image=image_path.name,
        caption=caption,
        expected_values=tasks.VISION_EXPECTED_VALUES,
        found_values=extract_numbers(caption),
        seconds=seconds,
    )


def installed_models(client: OllamaClient) -> list[str]:
    return [entry.model for entry in client.list().models]


def run_all(
    client: OllamaClient,
    settings: Settings,
    run_id: str,
    started_at: str,
    out_dir: Path,
    on_progress: Any = print,
) -> SmokeReport:
    """Run every step one model at a time; a failing step is recorded, not fatal."""
    ensure_models_available(installed_models(client), settings.models.required_for_smoke_test())
    unload_all_running(client)
    report = SmokeReport(run_id=run_id, started_at=started_at, num_ctx=settings.num_ctx)

    def step(label: str, model: str, action: Any) -> None:
        on_progress(f"[{time.strftime('%H:%M:%S')}] {label} ({model}) ...")
        try:
            action()
        except Exception as error:  # a broken step must not hide the other results
            report.errors.append(f"{label} ({model}): {type(error).__name__}: {error}")
            on_progress(f"    FAILED: {error}")
        finally:
            try:
                unload_model(client, model)
            except Exception as error:
                report.errors.append(f"unload {model}: {error}")

    for model in settings.models.agent_candidates:
        step(
            "speed + prefix reuse",
            model,
            lambda m=model: _speed_and_prefix(client, m, settings, report),
        )
        step(
            "tool calling",
            model,
            lambda m=model: report.tool_calling.append(run_tool_calling(client, m, settings)),
        )
    step(
        "speed",
        settings.models.summary,
        lambda: report.speed.append(measure_speed(client, settings.models.summary, settings)),
    )
    step(
        "vision",
        settings.models.vision,
        lambda: setattr(
            report, "vision", run_vision(client, settings.models.vision, settings, out_dir)
        ),
    )
    step(
        "embedding",
        settings.models.embedding,
        lambda: setattr(report, "embedding", run_embedding(client, settings.models.embedding)),
    )
    return report


def _speed_and_prefix(
    client: OllamaClient, model: str, settings: Settings, report: SmokeReport
) -> None:
    report.speed.append(measure_speed(client, model, settings))
    report.prefix_reuse.append(measure_prefix_reuse(client, model, settings))
