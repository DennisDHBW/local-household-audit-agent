"""Plausibility check for table summaries: every number must come from the table itself."""

from __future__ import annotations

import re

from audit_agent.numbers import extract_numbers

SMALL_INTEGER_LIMIT = 12
"""Plain integers up to this value (counts, months) are not checked: ``drei`` vs ``3``."""

_DATE = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b\d{1,2}[./]\d{4}\b")


def _date_parts(text: str) -> set[float]:
    """Day, month and year of every date in ``text`` (``16.10.2024`` -> 16, 10, 2024).

    A summary may write the date in words ("16. Oktober 2024"), which is not an error.
    """
    return {float(part) for date in _DATE.findall(text) for part in re.split(r"[./]", date)}


def unsupported_numbers(summary: str, source: str) -> list[float]:
    """Numbers in ``summary`` that do not occur in ``source`` (sorted, without duplicates).

    ``source`` should hold the table rows and the heading path. Dates such as ``01.01.2024``
    are not parsed as numbers; their day, month and year count as present. A hit does not
    prove an error (the model may round), it marks the summary for a manual look.
    """
    allowed = set(extract_numbers(source)) | _date_parts(source)
    unsupported = {
        number
        for number in extract_numbers(summary)
        if number not in allowed
        and not (number.is_integer() and 0 <= number <= SMALL_INTEGER_LIMIT)
    }
    return sorted(unsupported)
