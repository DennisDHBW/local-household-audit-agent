"""The test set is the question catalog of ``dataset/ground_truth.yaml`` (concept.md, 11.1).

There is no separate ``testset.yaml``: questions, facts, sources and expected tools are
maintained in one place only (DRY).
"""

from __future__ import annotations

from collections.abc import Sequence

from audit_agent.corpus import CorpusError, GroundTruth, Question


def select_questions(truth: GroundTruth, ids: Sequence[str] | None = None) -> list[Question]:
    """Questions in the given order; ``None`` selects all of them in catalog order."""
    by_id = {question.id: question for question in truth.questions}
    if ids is None:
        return list(truth.questions)
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        raise CorpusError(f"unknown question ids: {unknown}; known: {sorted(by_id)}")
    return [by_id[i] for i in dict.fromkeys(ids)]
