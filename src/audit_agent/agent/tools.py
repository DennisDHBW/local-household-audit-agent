"""The six agent tools (concept.md, 7.2; ADR-0010).

Every tool is a small unit: a pydantic model for its arguments (validated, and the source of
the JSON schema that Ollama shows to the model), a description that says *when* to use it, and
a function that returns text for the model. Search tools wrap the ``Retriever`` of M4 and
register every hit in the run's ``EvidenceBook``, so the model can cite hits as ``[3]``.

Two rules of the issues log are enforced in code and not only in the prompt:
- ISS-025: a year filter only works for documents with a billing period, so it is applied
  only together with ``bill``, ``notice`` or ``payment_plan``.
- ISS-007: if a search without year filter finds nothing, it is repeated without filters.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from audit_agent.agent.calculator import (
    CalculationError,
    calculate,
    format_result,
    normalize_expression,
)
from audit_agent.agent.models import EvidenceBook
from audit_agent.config import Settings
from audit_agent.corpus import DocType, DocumentCatalog, DocumentMeta, UtilityType
from audit_agent.ingestion import ChunkType, chunks_path, load_parsed_document
from audit_agent.retrieval import MetadataFilter, SearchHit, SearchOptions
from audit_agent.retrieval.evidence import render_numbered_hit
from audit_agent.retrieval.search import fold

YEAR_FILTER_DOC_TYPES = frozenset({DocType.BILL, DocType.NOTICE, DocType.PAYMENT_PLAN})
"""Document types that have a billing period; only they can be filtered by year (ISS-025)."""
MAX_AMBIGUOUS_FILES = 5
_EMPTY_VALUES = frozenset({"", "null", "none"})


class ToolError(Exception):
    """A tool call that cannot be answered; the message goes back to the model."""


class SearchBackend(Protocol):
    """What the search tools need from the retrieval (lets tests inject a fake)."""

    def search(self, query: str, options: SearchOptions | None = None) -> list[SearchHit]: ...


class ToolResult(BaseModel):
    """Text for the model plus the citation numbers of the hits it contains."""

    model_config = ConfigDict(frozen=True)

    text: str
    hit_numbers: tuple[int, ...] = ()


class _Arguments(BaseModel):
    model_config = ConfigDict(extra="ignore")  # be liberal with surplus arguments (Postel)


class FilterArguments(_Arguments):
    utility_type: UtilityType | None = Field(
        default=None,
        description=(
            "Sparte. Nur setzen, wenn die Frage sie ausdrücklich nennt "
            "(Strom = electricity, Gas = gas, Wasser = water, Nebenkosten = service_charges)."
        ),
    )
    doc_type: DocType | None = Field(
        default=None,
        description=(
            "Dokumentart. Nur setzen, wenn die Frage sie eindeutig verlangt "
            "(bill = Rechnung/Abrechnung, contract = Vertrag, price_adjustment = "
            "Preisanpassung). Im Zweifel weglassen."
        ),
    )
    year: int | None = Field(
        default=None,
        ge=1990,
        le=2100,
        description=(
            "Abrechnungsjahr. Nur zusammen mit doc_type=bill setzen. Verträge und "
            "Preisschreiben haben kein Abrechnungsjahr und würden sonst ausgeschlossen."
        ),
    )


class SearchArguments(FilterArguments):
    query: str = Field(min_length=2, description="Suchanfrage auf Deutsch, mit den Fachbegriffen.")


class OutlineArguments(_Arguments):
    filename: str = Field(
        min_length=2, description="Teil des Dateinamens, z. B. 'Vertragsbestaetigung_SuedVolt'."
    )


class CalculateArguments(_Arguments):
    expression: str = Field(
        min_length=1,
        description="Rechenausdruck mit Zahlen und + - * / **, z. B. '3100 * (0.395 - 0.382)'.",
    )


@dataclass(frozen=True)
class AgentTool:
    """Name, description, argument model and function of one tool."""

    name: str
    description: str
    arguments: type[BaseModel]
    run: Callable[[Any, EvidenceBook], ToolResult]

    def usage(self) -> str:
        """Call shape such as ``search_tables(query*, doc_type, year)``; ``*`` marks required."""
        parameters = tool_parameters(self.arguments)
        required = set(parameters.get("required", []))
        names = [f"{name}*" if name in required else name for name in parameters["properties"]]
        return f"{self.name}({', '.join(names)})"

    def spec(self) -> dict[str, Any]:
        """The tool as Ollama's ``tools=[...]`` entry."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": tool_parameters(self.arguments),
            },
        }


def tool_parameters(model: type[BaseModel]) -> dict[str, Any]:
    """JSON schema of an argument model without ``$ref``, ``title``, ``default`` and null types."""
    schema = model.model_json_schema()
    definitions: dict[str, Any] = schema.pop("$defs", {})

    def resolve(node: Any) -> Any:
        if isinstance(node, list):
            return [resolve(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            target = definitions[node["$ref"].rsplit("/", 1)[-1]]
            return resolve({**target, **{k: v for k, v in node.items() if k != "$ref"}})
        options = [o for o in node.get("anyOf", []) if o.get("type") != "null"]
        if "anyOf" in node and len(options) == 1:
            return resolve({**options[0], **{k: v for k, v in node.items() if k != "anyOf"}})
        resolved: dict[str, Any] = {}
        for key, value in node.items():
            if key in ("title", "default"):
                continue
            if key == "properties":
                resolved[key] = {name: resolve(sub) for name, sub in value.items()}
            else:
                resolved[key] = resolve(value)
        return resolved

    result: dict[str, Any] = resolve(schema)
    return result


def clean_arguments(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Make model-written arguments digestible: drop empty values, flatten ``filter``."""
    flat: dict[str, Any] = {}
    for key, value in raw.items():
        if key in ("filter", "filters") and isinstance(value, Mapping):
            flat.update(value)
        else:
            flat[key] = value
    return {
        key: value
        for key, value in flat.items()
        if value is not None and str(value).strip().lower() not in _EMPTY_VALUES
    }


def describe_filter(metadata_filter: MetadataFilter) -> str:
    """``Sparte=electricity, Art=bill, Jahr=2024`` (``keine`` without any filter)."""
    parts = []
    if metadata_filter.utility_type:
        parts.append(f"Sparte={metadata_filter.utility_type.value}")
    if metadata_filter.doc_type:
        parts.append(f"Art={metadata_filter.doc_type.value}")
    if metadata_filter.period_start:
        parts.append(f"Jahr={metadata_filter.period_start.year}")
    return ", ".join(parts) or "keine"


def matches_year(document: DocumentMeta, year: int) -> bool:
    """Year of the billing period; else of ``valid_from``; else of the document date.

    The order is the one ``_document_line`` prints, so the shown date explains the match.
    """
    if document.billing_period_start and document.billing_period_end:
        return document.billing_period_start.year <= year <= document.billing_period_end.year
    if document.valid_from:
        return document.valid_from.year == year
    return document.document_date.year == year


def _file_name(path: str) -> str:
    return PurePosixPath(path).name


class ToolBox:
    """Builds the tools; holds the shared, read-only dependencies."""

    def __init__(self, settings: Settings, backend: SearchBackend, catalog: DocumentCatalog):
        self._settings = settings
        self._backend = backend
        self._catalog = catalog

    def tools(self) -> dict[str, AgentTool]:
        """The six tools by name, in the order they are offered to the model."""
        tools = [
            AgentTool(
                "list_documents",
                "Listet die vorhandenen Unterlagen (Dateiname, Sparte, Art, Vertragsnummer, "
                "Zeitraum). Nutze es zuerst, wenn unklar ist, ob es ein Dokument gibt (z. B. "
                "für ein Jahr oder eine Sparte). Leere Liste heißt: Die Unterlage liegt nicht vor. "
                "Mit Filtern aufrufen, sonst ist die Liste lang.",
                FilterArguments,
                self._list_documents,
            ),
            AgentTool(
                "search_documents",
                "Durchsucht den Fließtext der Dokumente: Vertragsklauseln, Kündigungsfristen, "
                "Laufzeiten, Preisanpassungsschreiben, Hinweise. Nicht für Preise, Verbräuche "
                "und Beträge: Zahlen stehen meist in Tabellen (search_tables).",
                SearchArguments,
                self._search_documents,
            ),
            AgentTool(
                "search_tables",
                "Durchsucht Tabellenzeilen: Arbeitspreis, Grundpreis, Verbrauch, Zählerstände, "
                "Kostenarten und Beträge von Verträgen, Rechnungen und Abrechnungen.",
                SearchArguments,
                self._search_tables,
            ),
            AgentTool(
                "search_images",
                "Durchsucht die Beschreibungen von Diagrammen und Grafiken (z. B. Verbrauch "
                "der Vorjahre). Die Beschreibung ist eine KI-Lesehilfe und kein Beleg.",
                SearchArguments,
                self._search_images,
            ),
            AgentTool(
                "get_document_outline",
                "Zeigt die Gliederung (Überschriften mit Seite) eines Dokuments. "
                "Nutze es, um in einem langen Vertrag den richtigen Abschnitt zu finden.",
                OutlineArguments,
                self._outline,
            ),
            AgentTool(
                "calculate",
                "Rechnet einen arithmetischen Ausdruck exakt aus. Nutze es für jede Berechnung "
                "(Summen, Differenzen, Prozent, anteilige Beträge), nie im Kopf.",
                CalculateArguments,
                self._calculate,
            ),
        ]
        return {tool.name: tool for tool in tools}

    def _list_documents(self, args: FilterArguments, book: EvidenceBook) -> ToolResult:
        rows = [
            document
            for document in self._catalog.documents
            if (args.utility_type is None or document.utility_type is args.utility_type)
            and (args.doc_type is None or document.doc_type is args.doc_type)
            and (args.year is None or matches_year(document, args.year))
        ]
        selection = describe_filter(
            MetadataFilter.for_year(args.year, args.utility_type, args.doc_type)
            if args.year
            else MetadataFilter(utility_type=args.utility_type, doc_type=args.doc_type)
        )
        if not rows:
            return ToolResult(
                text=f"Keine Dokumente (Filter: {selection}). Diese Unterlagen liegen nicht vor."
            )
        limit = self._settings.agent.max_list_rows
        lines = [f"{len(rows)} Dokumente (Filter: {selection}):"]
        lines += [self._document_line(document) for document in rows[:limit]]
        if len(rows) > limit:
            lines.append(f"… {len(rows) - limit} weitere; Filter enger setzen.")
        return ToolResult(text="\n".join(lines))

    @staticmethod
    def _document_line(document: DocumentMeta) -> str:
        if document.billing_period_start and document.billing_period_end:
            when = f"Zeitraum {document.billing_period_start}..{document.billing_period_end}"
        elif document.valid_from:
            when = f"gültig ab {document.valid_from}"
        else:
            when = f"Datum {document.document_date}"
        contract = document.contract_id or "-"
        return (
            f"{_file_name(document.file)} | {document.utility_type.value} / "
            f"{document.doc_type.value} | {contract} | {when}"
        )

    def _search_documents(self, args: SearchArguments, book: EvidenceBook) -> ToolResult:
        return self._search(args, book, frozenset({ChunkType.TEXT}))

    def _search_tables(self, args: SearchArguments, book: EvidenceBook) -> ToolResult:
        types = {ChunkType.TABLE_ROW}
        if self._settings.agent.include_table_summaries:
            types.add(ChunkType.TABLE_SUMMARY)
        return self._search(args, book, frozenset(types))

    def _search_images(self, args: SearchArguments, book: EvidenceBook) -> ToolResult:
        return self._search(args, book, frozenset({ChunkType.IMAGE}))

    def _search(
        self, args: SearchArguments, book: EvidenceBook, chunk_types: frozenset[ChunkType]
    ) -> ToolResult:
        metadata_filter, notes = self._effective_filter(args)
        hits = self._backend.search(
            args.query, SearchOptions(metadata_filter=metadata_filter, chunk_types=chunk_types)
        )
        if (
            not hits
            and metadata_filter != MetadataFilter()
            and metadata_filter.period_start is None
        ):
            notes.append(
                f"Keine Treffer mit Filter ({describe_filter(metadata_filter)}); "
                "Wiederholung ohne Filter."
            )
            metadata_filter = MetadataFilter()
            hits = self._backend.search(args.query, SearchOptions(chunk_types=chunk_types))
        header = f'Treffer für "{args.query}" (Filter: {describe_filter(metadata_filter)}):'
        if not hits:
            hint = "Keine Treffer. Prüfe mit list_documents, ob es die Unterlage gibt."
            return ToolResult(text="\n".join([header, *notes, hint]))
        numbers = tuple(book.register(hit) for hit in hits)
        limit = self._settings.agent.max_hit_chars
        blocks = [render_numbered_hit(n, hit, limit) for n, hit in zip(numbers, hits, strict=True)]
        return ToolResult(text="\n".join([header, *notes, *blocks]), hit_numbers=numbers)

    @staticmethod
    def _effective_filter(args: SearchArguments) -> tuple[MetadataFilter, list[str]]:
        """Filter as the model asked for it, minus a year without a suitable document type."""
        notes: list[str] = []
        year = args.year
        if year is not None and args.doc_type not in YEAR_FILTER_DOC_TYPES:
            notes.append(
                "Hinweis: Jahresfilter ignoriert; er gilt nur zusammen mit doc_type=bill, "
                "notice oder payment_plan."
            )
            year = None
        fields = {"utility_type": args.utility_type, "doc_type": args.doc_type}
        if year is None:
            return MetadataFilter(**fields), notes
        return MetadataFilter.for_year(year, **fields), notes

    def _outline(self, args: OutlineArguments, book: EvidenceBook) -> ToolResult:
        wanted = fold(args.filename)
        matches = [d for d in self._catalog.documents if wanted in fold(_file_name(d.file))]
        if not matches:
            raise ToolError(f"Kein Dokument passt zu {args.filename!r}. Nutze list_documents.")
        if len(matches) > 1:
            names = ", ".join(_file_name(d.file) for d in matches[:MAX_AMBIGUOUS_FILES])
            raise ToolError(f"{len(matches)} Dokumente passen zu {args.filename!r}: {names}")
        document = matches[0]
        path: Path = chunks_path(self._settings.processed_dir, document.file)
        if not path.is_file():
            raise ToolError(f"{_file_name(document.file)} ist noch nicht verarbeitet.")
        chunks = load_parsed_document(path).chunks
        headings = [chunk for chunk in chunks if chunk.chunk_type is ChunkType.HEADING]
        if not headings:
            return ToolResult(text=f"{_file_name(document.file)} hat keine Überschriften.")
        lines = [f"Gliederung von {_file_name(document.file)}:"]
        for heading in headings:
            indent = "  " * (len(heading.heading_stack) - 1)
            lines.append(f"S. {heading.page_number} {indent}{heading.content}")
        return ToolResult(text="\n".join(lines))

    def _calculate(self, args: CalculateArguments, book: EvidenceBook) -> ToolResult:
        try:
            value = calculate(args.expression)
        except CalculationError as error:
            raise ToolError(f"Rechnung nicht möglich: {error}") from error
        return ToolResult(text=f"{normalize_expression(args.expression)} = {format_result(value)}")
