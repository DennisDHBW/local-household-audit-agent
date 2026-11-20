"""Load and validate ``documents.yaml`` and ``ground_truth.yaml`` (fail fast)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from audit_agent.corpus.models import DocumentCatalog, GroundTruth, QuestionSet


class CorpusError(Exception):
    """A corpus file is missing, unreadable or invalid."""


def _read_yaml(path: Path) -> object:
    if not path.is_file():
        raise CorpusError(f"corpus file not found: {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise CorpusError(f"{path.name}: invalid YAML: {error}") from error


def load_document_catalog(path: Path) -> DocumentCatalog:
    """Read ``documents.yaml`` into a validated catalog."""
    try:
        return DocumentCatalog.model_validate(_read_yaml(path))
    except ValidationError as error:
        raise CorpusError(f"{path.name}: {error}") from error


def load_ground_truth(path: Path) -> GroundTruth:
    """Read ``ground_truth.yaml`` into a validated ground truth."""
    try:
        return GroundTruth.model_validate(_read_yaml(path))
    except ValidationError as error:
        raise CorpusError(f"{path.name}: {error}") from error


def load_question_set(path: Path) -> QuestionSet:
    """Read the held-out questions (``holdout_questions.yaml``)."""
    try:
        return QuestionSet.model_validate(_read_yaml(path))
    except ValidationError as error:
        raise CorpusError(f"{path.name}: {error}") from error


def missing_files(catalog: DocumentCatalog, dataset_dir: Path) -> list[str]:
    """Catalog entries without a PDF, and PDFs without a catalog entry."""
    listed = {d.file for d in catalog.documents}
    present = {p.relative_to(dataset_dir).as_posix() for p in dataset_dir.rglob("*.pdf")}
    return sorted(listed - present) + sorted(present - listed)
