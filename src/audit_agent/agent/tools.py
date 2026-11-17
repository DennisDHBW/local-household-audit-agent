"""The agent tools (five after ADR-0014) (concept.md, 7.2; ADR-0010).

Every tool is a small unit: a pydantic model for its arguments (validated, and the source of
the JSON schema that Ollama shows to the model), a description that says *when* to use it, and
a function that returns text for the model. Search tools wrap the ``Retriever`` of M4 and
register every hit in the run's ``EvidenceBook``, so the model can cite hits as ``[3]``.

Rules of the issues log that are enforced in code and not only in the prompt (ADR-0014):
- ISS-006/052: one ``search`` over text and table chunks; the model cannot guess the chunk type.
- ISS-007: the model may filter by utility type only; document type and year are not offered.
  ``include_counterpart`` adds the matching contract or bill for audit questions.
- ISS-051: an empty filtered search is reported with the inventory, never repeated unfiltered.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
from audit_agent.retrieval import (
    MetadataFilter,
    SearchHit,
    SearchOptions,
    new_quantity_hits,
    quantity_query,
)
from audit_agent.retrieval.evidence import render_numbered_hit
from audit_agent.retrieval.search import fold

YEAR_FILTER_DOC_TYPES = frozenset({DocType.BILL, DocType.NOTICE, DocType.PAYMENT_PLAN})
"""Document types that have a billing period; only they can be filtered by year (ISS-025)."""
BASIS_DOC_TYPES = frozenset({DocType.CONTRACT, DocType.PRICE_ADJUSTMENT})
"""Documents that say what should be charged; the counterpart of a bill (ISS-007)."""
COUNTERPART_HITS = 2
"""Hits added by ``include_counterpart`` per missing document family."""
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


class SearchArguments(_Arguments):
    query: str = Field(
        min_length=2,
        description=(
            "Suchanfrage auf Deutsch, mit den Fachbegriffen. Jahr und Dokumentart "
            "(Vertrag, Rechnung) gehören in die Anfrage, nicht in einen Filter."
        ),
    )
    utility_type: UtilityType | None = Field(
        default=None,
        description=(
            "Sparte. Nur setzen, wenn die Frage sie ausdrücklich nennt "
            "(Strom = electricity, Gas = gas, Wasser = water, Fernwärme = district_heating, "
            "Nebenkosten = service_charges)."
        ),
    )
    include_counterpart: bool = Field(
        default=False,
        description=(
            "true bei Prüffragen (stimmt die Rechnung mit Vertrag oder Preisschreiben "
            "überein?): liefert zusätzlich Treffer aus dem Gegenstück (Vertrag bzw. Rechnung)."
        ),
    )


class OutlineArguments(_Arguments):
    filename: str = Field(
        min_length=2, description="Teil des Dateinamens, z. B. 'Vertragsbestaetigung_SuedVolt'."
    )


_OPERAND_PAIRS = (("a", "b"), ("x", "y"), ("left", "right"))
_OPERATOR_KEYS = ("operator", "op", "operation")
_OPERATORS = {
    "+": "+",
    "plus": "+",
    "add": "+",
    "-": "-",
    "minus": "-",
    "subtract": "-",
    "*": "*",
    "mal": "*",
    "times": "*",
    "multiply": "*",
    "/": "/",
    "durch": "/",
    "divide": "/",
}


def _expression_from_operands(data: Mapping[str, Any]) -> str | None:
    """``a``, ``b`` and an operator written as separate arguments -> one expression.

    ``llama3.1:8b`` calls ``calculate`` with ``{"a": ..., "b": ...}`` (ISS-063). Without an
    operator the intended calculation is unknown; then the error shows the right shape with
    the model's own numbers and the model has to choose the operator.
    """
    for first, second in _OPERAND_PAIRS:
        if first not in data or second not in data:
            continue
        left, right = str(data[first]).strip(), str(data[second]).strip()
        operator = next(
            (
                _OPERATORS.get(str(data[key]).strip().lower())
                for key in _OPERATOR_KEYS
                if key in data
            ),
            None,
        )
        if operator is None:
            raise ValueError(
                f"Es fehlt expression. Schreibe die ganze Rechnung in dieses eine Argument, "
                f'z. B. expression="{left} - {right}" (Operator + - * / nach Bedarf).'
            )
        wrapped = [f"({v})" if v.startswith("-") else v for v in (left, right)]
        return f"{wrapped[0]} {operator} {wrapped[1]}"
    return None


class CalculateArguments(_Arguments):
    expression: str = Field(
        min_length=1,
        description="Rechenausdruck mit Zahlen und + - * / **, z. B. '3100 * (0.395 - 0.382)'.",
    )

    @model_validator(mode="before")
    @classmethod
    def _accept_operands(cls, data: Any) -> Any:
        """Be liberal (Postel): build ``expression`` from operands if it is missing."""
        if not isinstance(data, Mapping) or str(data.get("expression") or "").strip():
            return data
        expression = _expression_from_operands(data)
        return data if expression is None else {**data, "expression": expression}


@dataclass(frozen=True)
class AgentTool:
    """Name, description, argument model and function of one tool."""

    name: str
    description: str
    arguments: type[BaseModel]
    run: Callable[[Any, EvidenceBook], ToolResult]

    def usage(self) -> str:
        """Call shape such as ``search(query*, utility_type)``; ``*`` marks required."""
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
        """The five tools by name, in the order they are offered to the model."""
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
                "search",
                "Durchsucht Fließtext und Tabellen aller Dokumente: Preise, Verbräuche, "
                "Beträge, Zählerstände, Vertragsklauseln, Kündigungsfristen, Laufzeiten, "
                "Preisanpassungsschreiben. Das richtige Werkzeug für fast jede Frage.",
                SearchArguments,
                self._search_text_and_tables,
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

    def _search_text_and_tables(self, args: SearchArguments, book: EvidenceBook) -> ToolResult:
        types = {ChunkType.TEXT, ChunkType.TABLE_ROW}
        if self._settings.agent.include_table_summaries:
            types.add(ChunkType.TABLE_SUMMARY)
        return self._search(args, book, frozenset(types))

    def _search_images(self, args: SearchArguments, book: EvidenceBook) -> ToolResult:
        return self._search(args, book, frozenset({ChunkType.IMAGE}))

    def _search(
        self, args: SearchArguments, book: EvidenceBook, chunk_types: frozenset[ChunkType]
    ) -> ToolResult:
        metadata_filter = MetadataFilter(utility_type=args.utility_type)
        hits = self._backend.search(
            args.query, SearchOptions(metadata_filter=metadata_filter, chunk_types=chunk_types)
        )
        notes: list[str] = []
        quantity = quantity_query(args.query) if self._settings.agent.quantity_hits else None
        if hits and quantity is not None:
            extra = new_quantity_hits(
                self._backend.search,
                quantity,
                SearchOptions(metadata_filter=metadata_filter, chunk_types=chunk_types),
                hits,
                self._settings.agent.quantity_hits,
            )
            if extra:
                hits = [*hits, *extra]
                notes.append(
                    f'Hinweis: Weitere Treffer stammen aus einer Suche nur nach "{quantity}".'
                )
        if hits and args.include_counterpart:
            extra, note = self._counterpart_hits(quantity or args.query, args, hits, chunk_types)
            hits = [*hits, *extra]
            notes.append(note)
        header = f'Treffer für "{args.query}" (Filter: {describe_filter(metadata_filter)}):'
        if not hits:
            return ToolResult(text="\n".join([header, "Keine Treffer.", self._inventory()]))
        numbers = tuple(book.register(hit) for hit in hits)
        limit = self._settings.agent.max_hit_chars
        blocks = [render_numbered_hit(n, hit, limit) for n, hit in zip(numbers, hits, strict=True)]
        return ToolResult(text="\n".join([header, *notes, *blocks]), hit_numbers=numbers)

    def _counterpart_hits(
        self,
        query: str,
        args: SearchArguments,
        hits: list[SearchHit],
        chunk_types: frozenset[ChunkType],
    ) -> tuple[list[SearchHit], str]:
        """Extra hits from the document family that the first search did not reach (ISS-007).

        ``query`` is the quantity query if there is one: the long question would find the same
        document chunks again (ISS-072).
        """
        found = {self._doc_type_of(hit) for hit in hits}
        wanted = []
        if DocType.BILL not in found:
            wanted.append(DocType.BILL)
        if not found & BASIS_DOC_TYPES:
            wanted.extend(sorted(BASIS_DOC_TYPES))
        seen = {hit.chunk_id for hit in hits}
        extra: list[SearchHit] = []
        for doc_type in wanted:
            options = SearchOptions(
                metadata_filter=MetadataFilter(utility_type=args.utility_type, doc_type=doc_type),
                chunk_types=chunk_types,
                top_k=COUNTERPART_HITS,
            )
            extra += [h for h in self._backend.search(query, options) if h.chunk_id not in seen]
        if not extra:
            return [], "Hinweis: Im Gegenstück (Vertrag bzw. Rechnung) gibt es keine Treffer."
        return (
            extra,
            "Hinweis: Die letzten Treffer stammen aus dem Gegenstück (Vertrag bzw. Rechnung).",
        )

    def _doc_type_of(self, hit: SearchHit) -> DocType | None:
        for document in self._catalog.documents:
            if _file_name(document.file) == _file_name(hit.filename):
                return document.doc_type
        return None

    def _inventory(self) -> str:
        """What exists, so that an empty search can be read as "not in the documents" (ISS-051)."""
        by_utility: dict[str, set[str]] = {}
        for document in self._catalog.documents:
            by_utility.setdefault(document.utility_type.value, set()).add(document.doc_type.value)
        parts = [
            f"{utility} ({', '.join(sorted(types))})"
            for utility, types in sorted(by_utility.items())
        ]
        return (
            "Vorhanden sind Unterlagen zu: " + "; ".join(parts) + ". "
            "Gibt es dazu nichts, sage das; wiederhole die Suche nicht mit anderer Sparte."
        )

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
