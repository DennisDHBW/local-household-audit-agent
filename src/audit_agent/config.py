"""Central configuration (single source of truth for paths, models and limits).

Every value can be overridden through an environment variable with the prefix ``AUDIT_``
(for example ``AUDIT_OLLAMA_HOST``). Business code must never hard-code paths or model names.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PREFIX = "AUDIT_"

MAX_OLLAMA_MEMORY_GB = 9.0
MAX_LOADED_MODELS = 2


class ModelNames(BaseModel):
    """Ollama model tags per task (see ADR-0004)."""

    model_config = ConfigDict(frozen=True)

    embedding: str = "nomic-embed-text"
    vision: str = "gemma3:4b"
    summary: str = "llama3.2"
    agent: str = "qwen2.5:7b"
    agent_candidates: tuple[str, ...] = ("qwen2.5:7b", "llama3.1:8b")
    judge: str = "audit-judge"
    """RAGAS judge: ``qwen2.5:7b`` with a fixed context (``scripts/audit-judge.Modelfile``)."""

    def required_for_smoke_test(self) -> tuple[str, ...]:
        """All distinct model tags the smoke test needs, in a stable order."""
        ordered = (*self.agent_candidates, self.summary, self.vision, self.embedding)
        return tuple(dict.fromkeys(ordered))


class ParserSettings(BaseModel):
    """Tunable parameters of the PDF parser (concept.md, section 5.1)."""

    model_config = ConfigDict(frozen=True)

    min_chars: int = Field(default=20, ge=1)
    """Paragraphs shorter than this are merged into the following paragraph."""
    max_block_chars: int = Field(default=1500, ge=100)
    """Upper bound per text chunk; ``nomic-embed-text`` handles about 2.048 tokens."""
    header_zone_ratio: float = Field(default=0.04, ge=0, lt=0.5)
    """Top share of a page that holds running headers (page number) and is skipped."""
    footer_zone_ratio: float = Field(default=0.06, ge=0, lt=0.5)
    """Bottom share of a page that holds letter footers (bank, register) and is skipped."""
    heading_size_factor: float = Field(default=1.0, ge=1)
    """A bold line counts as heading if its font is this much larger than the body font."""
    cell_gap_pt: float = Field(default=5.0, ge=0)
    """Horizontal gap (points) that separates two table cells within one row."""
    min_image_width_pt: float = Field(default=50.0, ge=0)
    """Images narrower than this are decoration and not extracted."""


class EnrichmentSettings(BaseModel):
    """Parameters of the model-based enrichment (concept.md, section 5.2)."""

    model_config = ConfigDict(frozen=True)

    caption_max_tokens: int = Field(default=600, ge=16)
    """Generation limit for one image caption."""
    summary_max_tokens: int = Field(default=256, ge=16)
    """Generation limit for one table summary (at most three sentences)."""
    keep_alive: str = "10m"
    """How long Ollama keeps a model loaded between two enrichment calls."""


class RetrievalSettings(BaseModel):
    """Parameters of index and search (concept.md, section 10.9; ADR-0002, ADR-0009)."""

    model_config = ConfigDict(frozen=True)

    collection_name: str = "chunks"
    """Name of the ChromaDB collection in ``data/vectors/``."""
    document_task_prefix: str = "search_document: "
    """Task prefix ``nomic-embed-text`` expects in front of every indexed text."""
    query_task_prefix: str = "search_query: "
    """Task prefix ``nomic-embed-text`` expects in front of every search query."""
    embed_batch_size: int = Field(default=16, ge=1)
    """Texts per embedding call while building the index."""
    candidate_count: int = Field(default=20, ge=1)
    """Candidates the vector search returns before the hierarchy boost is applied."""
    top_k: int = Field(default=5, ge=1)
    """Hits that are returned after re-ranking."""
    hierarchy_boost: float = Field(default=1.5, ge=1)
    """Score multiplier for hits whose path (file, folder, headings) contains a query term."""
    min_term_chars: int = Field(default=3, ge=1)
    """Query words shorter than this are ignored by the hierarchy boost."""
    keep_alive: str = "5m"
    """How long Ollama keeps the embedding model loaded between two calls."""

    @model_validator(mode="after")
    def _check_top_k(self) -> RetrievalSettings:
        if self.top_k > self.candidate_count:
            raise ValueError("top_k must not exceed candidate_count")
        return self


class AgentSettings(BaseModel):
    """Parameters of the agent loop (concept.md, section 7.4; ADR-0010)."""

    model_config = ConfigDict(frozen=True)

    tool_set: Literal["v1", "v2"] = "v2"
    """v1: search tools of M5/M6 (ADR-0014); v2: plan, fact store, bill audit, overview and
    chart tools (ADR-0019)."""
    max_tool_calls: int = Field(default=10, ge=1)
    """Tool calls per question (valid or invalid); protects against endless loops on slow CPUs.

    6 until M6; 10 since M8 because ``plan`` and the artifact tools add steps (ADR-0019)."""
    verify_answer: bool = True
    """v2 self-check before an answer is accepted: audit question without ``check_bill``,
    requested chart or overview missing, numbers that no tool result contains (ADR-0019)."""
    max_hit_chars: int = Field(default=600, ge=100)
    """Characters of one hit shown to the model; the evidence view keeps the full text."""
    max_list_rows: int = Field(default=40, ge=1)
    """Rows of one ``list_documents`` answer."""
    num_predict: int = Field(default=600, ge=64)
    """Generation limit per model call (tool call or final answer)."""
    context_reserve_tokens: int = Field(default=1200, ge=0)
    """Free context kept for the next observation and the answer; below it the loop stops."""
    temperature: float = Field(default=0.0, ge=0)
    keep_alive: str = "10m"
    """How long Ollama keeps the agent model loaded between two calls."""
    include_table_summaries: bool = False
    """Show ``table_summary`` hits to the model; off since RUN-005 (it quoted one as evidence)."""
    min_searches_before_gap: int = Field(default=2, ge=0)
    """Fewer tool calls than this and a "not in the documents" answer is questioned once."""
    quantity_hits: int = Field(default=2, ge=0)
    """Extra hits of a second search with the billing quantity only (M6h); 0 switches it off.

    Without it a question with a year and a document word finds the document, not the row with
    the number (ISS-072). The counterpart search uses the same short query.
    """
    require_citation: bool = True
    """Ask once for hit numbers if an answer with numbers has none (M6h; prompts.py)."""
    audit_flow_enabled: bool = False
    """Run the fixed audit flow (plan, search, read, compute) for check questions (ADR-0016).

    Off by default: RUN-017 showed no gain (ISS-070, ISS-071); the code stays as a documented
    negative result and for a later revision.
    """
    audit_max_checks: int = Field(default=3, ge=1)
    """Quantities the flow checks per question; each one costs two searches and a model call."""


class EvaluationSettings(BaseModel):
    """Parameters of the test module (concept.md, section 11; ADR-0011)."""

    model_config = ConfigDict(frozen=True)

    full_text_reserve_tokens: int = Field(default=300, ge=0)
    """B0: tokens kept free for the question and the chat template besides the answer."""
    judge_num_ctx: int = Field(default=8192, ge=512)
    """Context of the RAGAS judge; must equal ``num_ctx`` in ``scripts/audit-judge.Modelfile``.

    Ollama's OpenAI endpoint takes no per-request ``num_ctx``, so the model alias fixes it.
    """
    judge_max_tokens: int = Field(default=2048, ge=64)
    """Output limit of one judge call; 1024 cut the statement list of a long answer (RUN-009)."""


class Settings(BaseModel):
    """Runtime settings of the application."""

    model_config = ConfigDict(frozen=True)

    project_root: Path = PROJECT_ROOT
    ollama_host: str = "http://localhost:11434"
    ollama_timeout_s: float = Field(default=900.0, gt=0)
    num_ctx: int = Field(default=8192, ge=512)
    memory_limit_gb: float = Field(default=MAX_OLLAMA_MEMORY_GB, gt=0)
    max_loaded_models: int = Field(default=MAX_LOADED_MODELS, ge=1)
    models: ModelNames = Field(default_factory=ModelNames)
    parser: ParserSettings = Field(default_factory=ParserSettings)
    enrichment: EnrichmentSettings = Field(default_factory=EnrichmentSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)

    @property
    def dataset_dir(self) -> Path:
        return self.project_root / "dataset"

    @property
    def documents_file(self) -> Path:
        return self.dataset_dir / "documents.yaml"

    @property
    def ground_truth_file(self) -> Path:
        return self.dataset_dir / "ground_truth.yaml"

    @property
    def holdout_file(self) -> Path:
        return self.dataset_dir / "holdout_questions.yaml"

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def vectors_dir(self) -> Path:
        return self.data_dir / "vectors"

    @property
    def eval_dir(self) -> Path:
        return self.data_dir / "eval"

    @property
    def images_dir(self) -> Path:
        return self.processed_dir / "images"

    @property
    def cache_dir(self) -> Path:
        return self.project_root / ".cache"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        """Build settings from defaults plus ``AUDIT_*`` overrides (fail fast on bad values)."""
        env = os.environ if environ is None else environ

        def get(name: str) -> str | None:
            return env.get(f"{ENV_PREFIX}{name}")

        values: dict[str, object] = {}
        for field in ("ollama_host", "ollama_timeout_s", "num_ctx", "memory_limit_gb"):
            raw = get(field.upper())
            if raw is not None:
                values[field] = raw
        if (root := get("PROJECT_ROOT")) is not None:
            values["project_root"] = Path(root)

        model_values: dict[str, object] = {}
        for field in ("embedding", "vision", "summary", "agent", "judge"):
            raw = get(f"MODEL_{field.upper()}")
            if raw is not None:
                model_values[field] = raw
        if (candidates := get("MODEL_AGENT_CANDIDATES")) is not None:
            model_values["agent_candidates"] = tuple(
                tag.strip() for tag in candidates.split(",") if tag.strip()
            )
        if model_values:
            values["models"] = ModelNames(**model_values)

        return cls(**values)
