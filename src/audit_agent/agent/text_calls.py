"""Tool calls that a model wrote as text instead of as a native tool call (ISS-061).

``llama3.1:8b`` sometimes ends its message with ``{"name": "search", "parameters": {...}}``.
Ollama's tool calling does not recognise that, so the loop took the text for the answer.
The reader below finds such a call, but only in the shape that was observed: a JSON object
that ends the message, names a tool the agent has, and carries its arguments as an object.
Everything else stays an answer, so an answer that merely quotes JSON is not misread.
"""

from __future__ import annotations

import json
import re
from collections.abc import Container
from dataclasses import dataclass
from typing import Any

_ARGUMENT_KEYS = ("parameters", "arguments")
_FENCE_END = re.compile(r"\s*`{3}\s*$")
_DECODER = json.JSONDecoder()


@dataclass(frozen=True)
class TextCall:
    """A tool call read from message text."""

    name: str
    arguments: dict[str, Any]


def parse_text_call(content: str, known_tools: Container[str]) -> TextCall | None:
    """The tool call that ends ``content``, or ``None`` if the text is a normal answer."""
    text = _FENCE_END.sub("", content.strip())
    start = text.find("{")
    while start != -1:
        call = _call_at(text, start, known_tools)
        if call is not None:
            return call
        start = text.find("{", start + 1)
    return None


def _call_at(text: str, start: int, known_tools: Container[str]) -> TextCall | None:
    try:
        value, end = _DECODER.raw_decode(text, start)
    except json.JSONDecodeError:
        return None
    if text[end:].strip() or not isinstance(value, dict):
        return None
    name = value.get("name")
    if not isinstance(name, str) or name not in known_tools:
        return None
    for key in _ARGUMENT_KEYS:
        arguments = value.get(key)
        if isinstance(arguments, dict):
            return TextCall(name=name, arguments=arguments)
    return None
