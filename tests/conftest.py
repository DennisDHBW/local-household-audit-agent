"""Shared fakes: a scripted Ollama client so that no test needs a running LLM."""

from types import SimpleNamespace

import pytest
from ollama import ChatResponse, Message

from audit_agent.smoke import tasks

CHART_CAPTION = "2022: 3.480 kWh, 2023: 3.390 kWh, 2024: 3.250 kWh"


class FakeOllama:
    """Implements the subset of ``ollama.Client`` the smoke test uses."""

    def __init__(self, installed: list[str], fail_embedding: bool = False):
        self.installed = installed
        self.fail_embedding = fail_embedding
        self.unloaded: list[str] = []
        self.loaded: list[str] = ["old-model:latest"]
        self._prefix_calls = 0

    def list(self):
        return SimpleNamespace(models=[SimpleNamespace(model=tag) for tag in self.installed])

    def ps(self):
        models = [SimpleNamespace(model=tag, size=5_500_000_000) for tag in self.loaded]
        return SimpleNamespace(models=models)

    def generate(self, **kwargs):
        if kwargs.get("keep_alive") == 0:
            self.unloaded.append(kwargs["model"])
            self.loaded = [m for m in self.loaded if m != kwargs["model"]]

    def embed(self, **kwargs):
        if self.fail_embedding:
            raise RuntimeError("embedding service down")
        return SimpleNamespace(embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])

    def chat(self, **kwargs):
        model = kwargs["model"]
        if model not in self.loaded:
            self.loaded.append(model)
        messages = kwargs["messages"]
        if "tools" in kwargs:
            return self._tool_response(model, messages[-1]["content"])
        if "images" in messages[-1]:
            return _response(model, CHART_CAPTION)
        if messages[0]["role"] == "system":
            self._prefix_calls += 1
            prefill_ns = 20_000_000_000 if self._prefix_calls % 2 == 1 else 500_000_000
            return _response(model, "ok", prompt_tokens=400, prefill_ns=prefill_ns)
        return _response(model, "Zusammenfassung", prompt_tokens=360)

    @staticmethod
    def _tool_response(model, prompt):
        task = next(t for t in tasks.TOOL_TASKS if t.prompt == prompt)
        arguments = {
            key: (value if value != "*" else "Arbeitspreis")
            for key, value in task.expected_arguments.items()
        }
        call = Message.ToolCall(
            function=Message.ToolCall.Function(name=task.expected_tool, arguments=arguments)
        )
        message = Message(role="assistant", content="", tool_calls=[call])
        return ChatResponse(model=model, message=message)


def _response(model, content, prompt_tokens=360, prefill_ns=20_000_000_000):
    return ChatResponse(
        model=model,
        message=Message(role="assistant", content=content),
        prompt_eval_count=prompt_tokens,
        prompt_eval_duration=prefill_ns,
        eval_count=60,
        eval_duration=10_000_000_000,
        load_duration=2_000_000_000,
    )


ALL_MODELS = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "llama3.2:latest",
    "gemma3:4b",
    "nomic-embed-text:latest",
]


@pytest.fixture
def fake_client() -> FakeOllama:
    return FakeOllama(ALL_MODELS)
