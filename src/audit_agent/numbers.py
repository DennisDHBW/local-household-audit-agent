"""Number parsing shared by the smoke test and the enrichment checks."""

from __future__ import annotations

import re

_NUMBER_TOKEN = re.compile(r"\d[\d.,]*\d|\d")
_GERMAN_THOUSANDS = re.compile(r"\d{1,3}(\.\d{3})+(,\d+)?")
_ENGLISH_THOUSANDS = re.compile(r"\d{1,3}(,\d{3})+(\.\d+)?")


def parse_number(token: str) -> float | None:
    """Parse ``3.480``, ``3,480``, ``3480`` or ``1.234,56`` (Postel's law: be liberal)."""
    if _GERMAN_THOUSANDS.fullmatch(token):
        token = token.replace(".", "").replace(",", ".")
    elif _ENGLISH_THOUSANDS.fullmatch(token):
        token = token.replace(",", "")
    else:
        token = token.replace(",", ".")
    try:
        return float(token)
    except ValueError:
        return None


def extract_numbers(text: str) -> list[float]:
    """All numbers found in ``text``, normalised."""
    parsed = (parse_number(match) for match in _NUMBER_TOKEN.findall(text))
    return [value for value in parsed if value is not None]
