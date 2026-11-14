import pytest

from audit_agent.config import Settings
from audit_agent.preflight import MissingModelError
from audit_agent.smoke.report import render_markdown
from audit_agent.smoke.runner import (
    extract_chart_image,
    measure_prefix_reuse,
    measure_speed,
    run_all,
    run_embedding,
    run_tool_calling,
)
from tests.conftest import FakeOllama

SETTINGS = Settings()


def test_speed_measurement_reports_resident_memory(fake_client):
    result = measure_speed(fake_client, "qwen2.5:7b", SETTINGS)

    assert result.prefill_tokens_per_s == pytest.approx(18.0)
    assert result.generation_tokens_per_s == pytest.approx(6.0)
    assert result.resident_gb == pytest.approx(5.5)


def test_prefix_reuse_detected_from_token_counts(fake_client):
    result = measure_prefix_reuse(fake_client, "qwen2.5:7b", SETTINGS)

    assert (result.first_prompt_tokens, result.second_prompt_tokens) == (400, 15)
    assert result.is_prefix_reused


def test_tool_calling_scores_all_tasks(fake_client):
    summary = run_tool_calling(fake_client, "qwen2.5:7b", SETTINGS)

    assert len(summary.results) == 5
    assert summary.tool_accuracy == 1.0
    assert summary.argument_accuracy == 1.0


def test_embedding_ranking(fake_client):
    result = run_embedding(fake_client, "nomic-embed-text")

    assert result.dimensions == 2
    assert result.is_ranking_correct


def test_chart_image_is_extracted_from_corpus_pdf():
    from audit_agent.smoke import tasks

    image, extension = extract_chart_image(
        SETTINGS.dataset_dir / tasks.VISION_DOCUMENT, tasks.VISION_PAGE_INDEX
    )

    assert len(image) > 1000
    assert extension in {"png", "jpeg", "jpg"}


def test_missing_model_fails_before_any_call():
    client = FakeOllama(["qwen2.5:7b"])

    with pytest.raises(MissingModelError):
        run_all(client, SETTINGS, "t", "now", out_dir=None, on_progress=lambda _: None)  # type: ignore[arg-type]


def test_full_run_collects_results_and_unloads_models(fake_client, tmp_path):
    report = run_all(fake_client, SETTINGS, "run-t", "now", tmp_path, on_progress=lambda _: None)

    assert report.errors == []
    assert len(report.speed) == 3  # two agent candidates + summary model
    assert len(report.tool_calling) == 2
    assert report.vision is not None and report.vision.are_all_values_found
    assert report.embedding is not None and report.embedding.is_ranking_correct
    assert "old-model:latest" in fake_client.unloaded  # started from an empty memory
    assert fake_client.loaded == []
    assert (tmp_path / f"chart.{report.vision.page_image.split('.')[-1]}").exists()


def test_failing_step_is_recorded_but_does_not_stop_the_run(tmp_path):
    client = FakeOllama(
        ["qwen2.5:7b", "llama3.1:8b", "llama3.2", "gemma3:4b", "nomic-embed-text"],
        fail_embedding=True,
    )

    report = run_all(client, SETTINGS, "run-t", "now", tmp_path, on_progress=lambda _: None)

    assert report.embedding is None
    assert any("embedding" in error for error in report.errors)
    assert report.vision is not None


def test_markdown_report_contains_all_sections(fake_client, tmp_path):
    report = run_all(fake_client, SETTINGS, "run-t", "now", tmp_path, on_progress=lambda _: None)

    text = render_markdown(report)

    for heading in ("## Geschwindigkeit", "## Tool-Calling", "## Embedding", "## Vision"):
        assert heading in text
    assert "qwen2.5:7b" in text
