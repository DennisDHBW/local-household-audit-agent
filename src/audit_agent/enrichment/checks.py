"""Plausibility check for table summaries: every number must come from the table itself."""

from __future__ import annotations

from audit_agent.numbers import extract_numbers

SMALL_INTEGER_LIMIT = 12
"""Plain integers up to this value (counts, months) are not checked: ``drei`` vs ``3``."""


def unsupported_numbers(summary: str, source: str) -> list[float]:
    """Numbers in ``summary`` that do not occur in ``source`` (sorted, without duplicates).

    ``source`` should hold the table rows and the heading path. Dates such as ``01.01.2024``
    are not parsed as numbers and therefore not checked. A hit does not prove an error
    (the model may round), it marks the summary for a manual look.
    """
    allowed = set(extract_numbers(source))
    unsupported = {
        number
        for number in extract_numbers(summary)
        if number not in allowed
        and not (number.is_integer() and 0 <= number <= SMALL_INTEGER_LIMIT)
    }
    return sorted(unsupported)
