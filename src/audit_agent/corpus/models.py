"""Typed models for the document metadata and the ground truth of the test corpus.

``DocumentMeta`` is what the agent may filter on (concept.md, section 5.2). Everything
that reveals the planted errors lives only in ``GroundTruth`` and is used by the evaluation.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UtilityType(StrEnum):
    """Sparte of a document (filter value)."""

    ELECTRICITY = "electricity"
    GAS = "gas"
    DISTRICT_HEATING = "district_heating"
    WATER = "water"
    SERVICE_CHARGES = "service_charges"
    RENT = "rent"
    TELECOM = "telecom"
    INSURANCE = "insurance"
    OTHER = "other"


class TariffKind(StrEnum):
    """Kind of electricity supply; only set for electricity documents (ADR-0018)."""

    HOUSEHOLD = "household"
    """Haushaltsstrom (Lichtstrom), one-rate meter."""
    HEATING = "heating"
    """Heizstrom for night storage heaters, two-rate meter (HT/NT)."""


class DocType(StrEnum):
    """Dokumentart (filter value)."""

    CONTRACT = "contract"
    PAYMENT_PLAN = "payment_plan"
    PRICE_ADJUSTMENT = "price_adjustment"
    BILL = "bill"
    NOTICE = "notice"
    HANDOVER_PROTOCOL = "handover_protocol"
    POLICY = "policy"


class QuestionCategory(StrEnum):
    STANDARD = "standard"
    EDGE_CASE = "edge_case"
    NEGATIVE = "negative"
    ADDITIONAL = "additional"
    VISUAL = "visual"
    """Overview table or chart requested (M8, ADR-0019)."""


REQUIRED_QUESTION_COUNTS: dict[QuestionCategory, int] = {
    QuestionCategory.STANDARD: 5,
    QuestionCategory.EDGE_CASE: 4,
    QuestionCategory.NEGATIVE: 2,
    QuestionCategory.ADDITIONAL: 3,
}
"""Minimum per category: lecture 5/2/2 plus 3 additional (ISS-040); M8 adds more (ADR-0019)."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DocumentMeta(_Frozen):
    """Metadata of one PDF, maintained by hand in ``dataset/documents.yaml``."""

    file: str = Field(description="Path relative to the dataset folder, POSIX style")
    utility_type: UtilityType
    doc_type: DocType
    provider: str = Field(min_length=1)
    contract_id: str | None = None
    document_date: date
    billing_period_start: date | None = None
    billing_period_end: date | None = None
    valid_from: date | None = None
    tariff_kind: TariffKind | None = None
    is_noise_document: bool = False

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if not self.file.lower().endswith(".pdf"):
            raise ValueError(f"{self.file}: file must be a .pdf")
        if self.tariff_kind is not None and self.utility_type is not UtilityType.ELECTRICITY:
            raise ValueError(f"{self.file}: tariff_kind is only allowed for electricity")
        if (self.billing_period_start is None) != (self.billing_period_end is None):
            raise ValueError(f"{self.file}: billing period needs both start and end")
        if (
            self.billing_period_start
            and self.billing_period_end
            and self.billing_period_start > self.billing_period_end
        ):
            raise ValueError(f"{self.file}: billing period start is after its end")
        return self


class DocumentCatalog(_Frozen):
    documents: tuple[DocumentMeta, ...]

    @model_validator(mode="after")
    def _check_unique_files(self) -> Self:
        duplicates = [f for f, n in Counter(d.file for d in self.documents).items() if n > 1]
        if duplicates:
            raise ValueError(f"duplicate files in documents.yaml: {sorted(duplicates)}")
        return self

    def by_file(self, file: str) -> DocumentMeta:
        for document in self.documents:
            if document.file == file:
                return document
        raise KeyError(file)


class SourceRef(_Frozen):
    """Expected source of an answer: document file and page (1-based)."""

    file: str
    page: int = Field(ge=1)


class ExpectedFact(_Frozen):
    """One checkable fact of an expected answer (number or text)."""

    label: str
    value: Decimal | str
    unit: str | None = None
    tolerance: Decimal = Field(default=Decimal("0.01"), ge=0)


class Question(_Frozen):
    id: str = Field(pattern=r"^[SGNZHWVT]\d{1,2}$")
    category: QuestionCategory
    question: str
    expected_answer: str
    facts: tuple[ExpectedFact, ...] = ()
    sources: tuple[SourceRef, ...] = ()
    expected_tools: tuple[str, ...] = ()
    expected_tools_v2: tuple[str, ...] = ()
    """Expected tools of the v2 tool set (ADR-0019) where they differ from ``expected_tools``,
    e.g. ``check_bill`` instead of ``search`` and ``calculate`` (ISS-118)."""
    is_answerable: bool = True
    planted_error: str | None = None
    """Id of the built-in error this question should uncover (``E1`` …), if any."""
    expected_artifact: Literal["table", "chart"] | None = None
    """The answer must come with this artifact (``make_overview`` or ``make_chart``)."""
    tests: str

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if (self.category is QuestionCategory.NEGATIVE) == self.is_answerable:
            raise ValueError(
                f"{self.id}: is_answerable must be false exactly for negative questions"
            )
        if self.is_answerable and not self.sources:
            raise ValueError(f"{self.id}: answerable questions need at least one source")
        return self


class PlantedError(_Frozen):
    """A deliberately built-in error of a document (basis of the detection rate)."""

    id: str = Field(pattern=r"^E\d$")
    file: str
    related_files: tuple[str, ...] = ()
    description: str
    facts: tuple[ExpectedFact, ...] = ()


class AuditCheck(_Frozen):
    """Expected verdict when the agent audits one bill (basis of false-alarm rate)."""

    file: str
    is_correct: bool
    planted_error_id: str | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.is_correct == (self.planted_error_id is not None):
            raise ValueError(f"{self.file}: planted_error_id must be set exactly for faulty bills")
        return self


class GroundTruth(_Frozen):
    questions: tuple[Question, ...]
    planted_errors: tuple[PlantedError, ...]
    audit_checks: tuple[AuditCheck, ...]

    @model_validator(mode="after")
    def _check_catalog(self) -> Self:
        ids = [q.id for q in self.questions]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate question ids")
        counts = Counter(q.category for q in self.questions)
        for category, required in REQUIRED_QUESTION_COUNTS.items():
            if counts[category] < required:
                found = counts[category]
                raise ValueError(
                    f"expected at least {required} questions of category {category}, found {found}"
                )
        error_ids = {e.id for e in self.planted_errors}
        if len(error_ids) != len(self.planted_errors):
            raise ValueError("duplicate planted error ids")
        checks = {c.file for c in self.audit_checks}
        if len(checks) != len(self.audit_checks):
            raise ValueError("duplicate files in audit_checks")
        referenced = {c.planted_error_id for c in self.audit_checks if c.planted_error_id}
        if referenced != error_ids:
            raise ValueError("audit_checks and planted_errors must reference the same error ids")
        for error in self.planted_errors:
            if error.file not in checks:
                raise ValueError(f"{error.id}: faulty document missing in audit_checks")
        asked = [q.planted_error for q in self.questions if q.planted_error]
        if sorted(asked) != sorted(error_ids):
            raise ValueError(
                f"every planted error needs exactly one question; questions cover {sorted(asked)}"
            )
        return self

    def referenced_files(self) -> set[str]:
        """All document files mentioned anywhere in the ground truth."""
        files = {s.file for q in self.questions for s in q.sources}
        files |= {e.file for e in self.planted_errors}
        files |= {f for e in self.planted_errors for f in e.related_files}
        files |= {c.file for c in self.audit_checks}
        return files


class QuestionSet(_Frozen):
    """Held-out questions (``holdout_questions.yaml``): only for the final run (ISS-108)."""

    questions: tuple[Question, ...]

    @model_validator(mode="after")
    def _check_ids(self) -> Self:
        ids = [q.id for q in self.questions]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate question ids")
        return self
