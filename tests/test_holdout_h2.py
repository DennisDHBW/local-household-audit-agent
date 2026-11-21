"""The sealed question set H2 (M9, ISS-130) must stay unchanged until the code freeze."""

from __future__ import annotations

import hashlib

import yaml

from audit_agent.config import PROJECT_ROOT

H2_FILE = PROJECT_ROOT / "dataset" / "holdout_h2.yaml"
SEAL_FILE = PROJECT_ROOT / "dataset" / "holdout_h2.sha256"


def test_h2_matches_its_seal() -> None:
    # Arrange
    expected = SEAL_FILE.read_text(encoding="utf-8").split()[0]

    # Act
    actual = hashlib.sha256(H2_FILE.read_bytes()).hexdigest()

    # Assert
    assert actual == expected, "H2 changed after sealing (see ISS-130)"


def test_h2_ids_are_unique_and_follow_ups_point_backwards() -> None:
    # Arrange
    questions = yaml.safe_load(H2_FILE.read_text(encoding="utf-8"))["questions"]

    # Act
    ids = [question["id"] for question in questions]
    follows = {q["id"]: q["follows"] for q in questions if "follows" in q}

    # Assert
    assert 20 <= len(ids) <= 24 and len(set(ids)) == len(ids)
    assert all(ids.index(target) < ids.index(source) for source, target in follows.items())
