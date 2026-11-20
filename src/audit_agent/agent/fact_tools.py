"""Tools of the agent v2 on top of the fact store (ADR-0018, ADR-0019).

``plan`` makes the planning step visible, ``get_facts`` returns the value that applies in a
year with its source, ``check_bill`` runs the rules of ``audit_agent.facts.audit``,
``make_overview`` and ``make_chart`` turn facts into a table or a PNG. Every fact the model
sees is registered in the run's ``EvidenceBook`` as the chunk it comes from, so ``[n]`` works
exactly as for search hits.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict, Field, model_validator

from audit_agent.agent.errors import ToolError
from audit_agent.agent.models import Artifact, EvidenceBook
from audit_agent.agent.scope import repair_utility_arguments
from audit_agent.config import Settings
from audit_agent.corpus import DocType, DocumentCatalog, DocumentMeta, TariffKind, UtilityType
from audit_agent.facts import (
    KIND_LABELS,
    STATUS_LABELS,
    CheckStatus,
    Fact,
    FactKind,
    FactStore,
    Role,
    check_bill,
    fmt,
)
from audit_agent.facts.chart import render_chart
from audit_agent.facts.views import Row, Topic, format_value, rows_for, utility_label
from audit_agent.ingestion import DocumentChunk, chunks_path, load_parsed_document
from audit_agent.retrieval import SearchHit

MAX_FACT_LINES = 14


class _Arguments(BaseModel):
    model_config = ConfigDict(extra="ignore")


UTILITY_HELP = "electricity = Strom, gas, water = Wasser, service_charges = Betriebskosten."
TARIFF_HELP = "Nur Strom: household = Lichtstrom, heating = Heizstrom (HT/NT)."


class PlanArguments(_Arguments):
    steps: list[str] = Field(
        min_length=1,
        max_length=6,
        description="2 bis 5 kurze Schritte, je Schritt Werkzeug und Ziel, z. B. "
        "'check_bill Heizstrom 2025', 'get_facts Arbeitspreis NT 2025'.",
    )


class FactName(StrEnum):
    ARBEITSPREIS = "arbeitspreis"
    GRUNDPREIS = "grundpreis"
    WASSERPREIS = "wasserpreis"
    SCHMUTZWASSER = "schmutzwassergebuehr"
    ABSCHLAG = "abschlag"
    VERBRAUCH = "verbrauch"
    ZAEHLERSTAND = "zaehlerstand"
    RECHNUNGSBETRAG = "rechnungsbetrag"
    Z_ZAHL = "z_zahl"
    WOHNFLAECHE = "wohnflaeche"


FACT_KINDS: dict[FactName, tuple[FactKind, ...]] = {
    FactName.ARBEITSPREIS: (FactKind.ENERGY_PRICE,),
    FactName.GRUNDPREIS: (FactKind.BASE_PRICE,),
    FactName.WASSERPREIS: (FactKind.WATER_PRICE,),
    FactName.SCHMUTZWASSER: (FactKind.SEWAGE_FEE,),
    FactName.ABSCHLAG: (FactKind.ADVANCE, FactKind.ADVANCES_CREDITED),
    FactName.VERBRAUCH: (FactKind.CONSUMPTION, FactKind.GAS_VOLUME),
    FactName.ZAEHLERSTAND: (FactKind.METER_READING,),
    FactName.RECHNUNGSBETRAG: (FactKind.INVOICE_TOTAL, FactKind.SERVICE_COSTS),
    FactName.Z_ZAHL: (FactKind.Z_FACTOR, FactKind.CALORIFIC_VALUE),
    FactName.WOHNFLAECHE: (FactKind.LIVING_AREA, FactKind.TOTAL_AREA, FactKind.COST_SHARE),
}


class FactsArguments(_Arguments):
    @model_validator(mode="before")
    @classmethod
    def _repair(cls, data: object) -> object:
        return repair_utility_arguments(data)

    fact: FactName = Field(description="Gesuchte Größe.")
    utility_type: UtilityType | None = Field(default=None, description=UTILITY_HELP)
    tariff_kind: TariffKind | None = Field(default=None, description=TARIFF_HELP)
    year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
        description="Jahr, für das der Wert gelten soll (bei Rechnungen: Abrechnungsjahr).",
    )


class BillArguments(_Arguments):
    @model_validator(mode="before")
    @classmethod
    def _repair(cls, data: object) -> object:
        return repair_utility_arguments(data, needs_utility=True, needs_year=True)

    utility_type: UtilityType = Field(description=UTILITY_HELP)
    tariff_kind: TariffKind | None = Field(default=None, description=TARIFF_HELP)
    year: int = Field(ge=2000, le=2100, description="Abrechnungsjahr der Rechnung.")


class ViewArguments(_Arguments):
    @model_validator(mode="before")
    @classmethod
    def _repair(cls, data: object) -> object:
        return repair_utility_arguments(data)

    topic: Topic = Field(
        description="verbrauch = Verbrauch je Jahr, kosten = Rechnungsbeträge je Jahr, "
        "preise = vereinbarte Preise mit Gültigkeit."
    )
    utility_type: UtilityType | None = Field(default=None, description=UTILITY_HELP)
    tariff_kind: TariffKind | None = Field(default=None, description=TARIFF_HELP)
    from_year: int | None = Field(default=None, ge=2000, le=2100)
    to_year: int | None = Field(default=None, ge=2000, le=2100)


class FactToolResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    hit_numbers: tuple[int, ...] = ()
    artifacts: tuple[Artifact, ...] = ()


class FactTools:
    """Shared state of the fact tools: settings, catalog, fact store, chunk cache, output dir."""

    def __init__(
        self, settings: Settings, catalog: DocumentCatalog, store: FactStore, artifact_dir: Path
    ):
        self._settings = settings
        self._catalog = catalog
        self._store = store
        self.artifact_dir = artifact_dir
        self._chunks: dict[str, dict[str, DocumentChunk]] = {}

    # --- evidence -----------------------------------------------------------------------

    def _chunk(self, fact: Fact) -> DocumentChunk | None:
        if fact.file not in self._chunks:
            path = chunks_path(self._settings.processed_dir, fact.file)
            chunks = load_parsed_document(path).chunks if path.is_file() else ()
            self._chunks[fact.file] = {c.chunk_id: c for c in chunks}
        return self._chunks[fact.file].get(fact.chunk_id)

    def cite(self, fact: Fact, book: EvidenceBook) -> int:
        """Register the source chunk of a fact and return its citation number."""
        chunk = self._chunk(fact)
        hit = SearchHit(
            chunk_id=fact.chunk_id,
            chunk_type=chunk.chunk_type if chunk else "table_row",  # type: ignore[arg-type]
            content=chunk.content if chunk else f"{fact.label}: {fact.value} {fact.unit}",
            heading_stack=chunk.heading_stack if chunk else (),
            page_number=fact.page,
            filename=fact.file,
            base_score=1.0,
            boost=1.0,
            final_score=1.0,
        )
        return book.register(hit)

    def _source(self, fact: Fact, book: EvidenceBook) -> str:
        number = self.cite(fact, book)
        return f"[{number}] {PurePosixPath(fact.file).name}, S. {fact.page}"

    # --- tools --------------------------------------------------------------------------

    def plan(self, args: PlanArguments, book: EvidenceBook) -> FactToolResult:
        steps = "; ".join(f"{i}. {s}" for i, s in enumerate(args.steps, start=1))
        return FactToolResult(text=f"Plan notiert: {steps}. Führe jetzt Schritt 1 aus.")

    def get_facts(self, args: FactsArguments, book: EvidenceBook) -> FactToolResult:
        kinds = FACT_KINDS[args.fact]
        facts = [
            f
            for f in self._store.facts
            if f.kind in kinds
            and (args.utility_type is None or f.utility_type is args.utility_type)
            and (args.tariff_kind is None or f.tariff_kind is args.tariff_kind)
        ]
        agreed = [f for f in facts if f.role is Role.AGREED]
        stated = [f for f in facts if f.role is Role.STATED]
        if args.year is not None:
            agreed = [f for f in agreed if f.valid_from is None or f.valid_from.year <= args.year]
            stated = [f for f in stated if _year_of(f) == args.year]
        if not agreed and not stated:
            scope = _scope(args.utility_type, args.tariff_kind, args.year)
            raise ToolError(
                f"Keine Werte für {args.fact.value} ({scope}). Gibt es die Unterlage? Prüfe mit "
                "list_documents oder suche mit search."
            )
        lines = [
            f"Werte für {args.fact.value} "
            f"({_scope(args.utility_type, args.tariff_kind, args.year)}):"
        ]
        numbers: list[int] = []
        if agreed:
            lines.append("Vereinbart (Vertrag, Preisschreiben, Abschlagsplan, Mietvertrag):")
            current = _current(agreed, args.year)
            for f in sorted(agreed, key=lambda f: (_series(f), f.valid_from or date.min))[
                -MAX_FACT_LINES:
            ]:
                marker = f"  <- gilt {args.year}" if args.year and f in current else ""
                valid = f", gültig ab {f.valid_from:%d.%m.%Y}" if f.valid_from else ""
                lines.append(f"- {_series(f)}: {_value(f)}{valid} {self._source(f, book)}{marker}")
                numbers.append(self.cite(f, book))
        if stated:
            lines.append("Laut Rechnungen und Mitteilungen:")
            for f in sorted(
                stated, key=lambda f: (_series(f), f.on_date or f.valid_to or date.min)
            )[-MAX_FACT_LINES:]:
                when = f"am {f.on_date:%d.%m.%Y}" if f.on_date else f"Zeitraum {_year_of(f)}"
                extra = ""
                if f.quantity is not None and f.amount is not None:
                    extra = (
                        f" für {fmt(f.quantity, f.quantity_unit or '')} = {fmt(f.amount, 'EUR', 2)}"
                    )
                if f.count is not None:
                    extra = f" ({f.count} × {fmt(f.value, 'EUR', 2)})"
                    lines.append(
                        f"- {_series(f)} {when}: {fmt(f.amount or f.value, 'EUR', 2)}{extra} "
                        f"{self._source(f, book)}"
                    )
                else:
                    lines.append(
                        f"- {_series(f)} {when}: {_value(f)}{extra} {self._source(f, book)}"
                    )
                numbers.append(self.cite(f, book))
        return FactToolResult(text="\n".join(lines), hit_numbers=tuple(dict.fromkeys(numbers)))

    def check_bill(self, args: BillArguments, book: EvidenceBook) -> FactToolResult:
        bills = [
            d
            for d in self._catalog.documents
            if d.doc_type is DocType.BILL
            and d.utility_type is args.utility_type
            and (args.tariff_kind is None or d.tariff_kind is args.tariff_kind)
            and d.billing_period_start is not None
            and d.billing_period_start.year == args.year
        ]
        if not bills:
            raise ToolError(
                f"Keine Rechnung für {_scope(args.utility_type, args.tariff_kind, args.year)}. "
                "Diese Unterlage liegt nicht vor; prüfe mit list_documents, welche es gibt."
            )
        texts: list[str] = []
        numbers: list[int] = []
        for bill in bills:  # Strom without tariff_kind: both bills of the year (ISS-114)
            text, cited = self._audit_text(bill, book)
            texts.append(text)
            numbers += cited
        return FactToolResult(text="\n\n".join(texts), hit_numbers=tuple(dict.fromkeys(numbers)))

    def _audit_text(self, bill: DocumentMeta, book: EvidenceBook) -> tuple[str, list[int]]:
        report = check_bill(self._store, bill)
        name = utility_label(bill.utility_type, bill.tariff_kind)
        year = bill.billing_period_start.year if bill.billing_period_start else ""
        lines = [
            f"Prüfung {name}-Rechnung {PurePosixPath(bill.file).name} "
            f"(Zeitraum {bill.billing_period_start:%d.%m.%Y}–{bill.billing_period_end:%d.%m.%Y}):"
        ]
        numbers: list[int] = []
        for check in report.checks:
            cited = list(dict.fromkeys(self.cite(f, book) for f in check.facts))
            numbers += cited
            line = f"- {STATUS_LABELS[check.status]}: {check.name}"
            if check.expected:
                line += f" | Soll {check.expected}"
            if check.actual:
                line += f" | Ist {check.actual}"
            if check.impact_eur is not None and check.status is CheckStatus.DEVIATION:
                side = "zu Ihren Lasten" if check.impact_eur > 0 else "zu Ihren Gunsten"
                line += f" | Auswirkung {fmt(abs(check.impact_eur), 'EUR', 2)} {side}"
            if check.note:
                line += f" | {check.note}"
            lines.append(f"{line} {' '.join(f'[{n}]' for n in cited)}")
        balance = next(
            (f for f in self._store.of_file(bill.file) if f.kind is FactKind.BALANCE), None
        )
        if balance is not None:
            word = "Guthaben" if balance.value < 0 else "Nachzahlung"
            cited = self.cite(balance, book)
            numbers.append(cited)
            lines.append(
                f"- Saldo laut Rechnung: {word} {fmt(abs(balance.value), 'EUR', 2)} [{cited}]"
            )
        deviations = report.deviations
        if deviations:
            total = report.total_impact
            side = "zu Ihren Lasten" if total >= 0 else "zu Ihren Gunsten"
            lines.append(
                f"Ergebnis: {len(deviations)} Abweichung(en), zusammen {fmt(abs(total), 'EUR', 2)} "
                f"{side}. Die Rechnung stimmt nicht."
            )
            parts = [
                f"{c.name}: Soll {c.expected}, Ist {c.actual}"
                + (f", {fmt(abs(c.impact_eur), 'EUR', 2)}" if c.impact_eur is not None else "")
                for c in deviations
            ]
            lines.append(
                f"Kurzfassung für die Antwort: Nein, die {name}-Rechnung {year} "
                f"stimmt nicht. " + "; ".join(parts) + "."
            )
        else:
            unverifiable = sum(c.status is CheckStatus.UNVERIFIABLE for c in report.checks)
            lines.append(
                f"Ergebnis: keine Abweichung in {len(report.checks) - unverifiable} Prüfungen"
                + (f", {unverifiable} nicht prüfbar" if unverifiable else "")
                + ". Die Rechnung stimmt nach diesen Regeln."
            )
            facts = self._store.of_file(bill.file)
            figures = []
            for kind, label in (
                (FactKind.INVOICE_TOTAL, "Rechnungsbetrag"),
                (FactKind.COST_SHARE, "Anteil"),
                (FactKind.SERVICE_COSTS, "Ihr Anteil"),
            ):
                fact = next((f for f in facts if f.kind is kind), None)
                if fact is not None:
                    value = fact.amount if kind is FactKind.SERVICE_COSTS else fact.value
                    unit = "%" if kind is FactKind.COST_SHARE else "EUR"
                    figures.append(f"{label} {fmt(value or fact.value, unit, 2)}")
            if balance is not None:
                word = "Guthaben" if balance.value < 0 else "Nachzahlung"
                figures.append(f"{word} {fmt(abs(balance.value), 'EUR', 2)}")
            lines.append(
                f"Kurzfassung für die Antwort: Ja, die {name}-Rechnung {year} stimmt mit Vertrag, "
                f"Preisschreiben und Zählerständen überein. " + "; ".join(figures) + "."
            )
        return "\n".join(lines), numbers

    def make_overview(self, args: ViewArguments, book: EvidenceBook) -> FactToolResult:
        rows, title = self._rows(args, "Übersicht")
        table = self._table(rows, book)
        artifact = Artifact(kind="table", title=title, markdown=table)
        return FactToolResult(
            text=f"Übersicht erstellt: {title} (wird der Antwort angehängt).\n{table}",
            hit_numbers=_numbers(table),
            artifacts=(artifact,),
        )

    def make_chart(self, args: ViewArguments, book: EvidenceBook) -> FactToolResult:
        rows, title = self._rows(args, "Grafik")
        table = self._table(rows, book)
        png, data = render_chart(rows, args.topic, title, self.artifact_dir)
        artifact = Artifact(
            kind="chart", title=title, markdown=table, image_path=str(png), data_path=str(data)
        )
        return FactToolResult(
            text=f"Grafik erstellt: {title} ({png.name}, wird angehängt). Daten:\n{table}",
            hit_numbers=_numbers(table),
            artifacts=(artifact,),
        )

    def _rows(self, args: ViewArguments, prefix: str) -> tuple[list[Row], str]:
        years = None
        if args.from_year or args.to_year:
            years = (args.from_year or 2000, args.to_year or 2100)
        rows = rows_for(
            args.topic, self._store, self._catalog, args.utility_type, args.tariff_kind, years
        )
        if not rows:
            raise ToolError(
                f"Keine Daten für {args.topic.value} "
                f"({_scope(args.utility_type, args.tariff_kind, None)}). "
                "Prüfe mit list_documents, welche Unterlagen es gibt."
            )
        what = {Topic.CONSUMPTION: "Verbrauch", Topic.COSTS: "Kosten", Topic.PRICES: "Preise"}[
            args.topic
        ]
        scope = (
            utility_label(args.utility_type, args.tariff_kind)
            if args.utility_type
            else "alle Sparten"
        )
        span = ""
        if years:
            span = (
                f" {years[0]}"
                if years[0] == years[1]
                else f" {years[0] if years[0] > 2000 else ''}–{years[1] if years[1] < 2100 else ''}"
            )
        return rows, f"{what} {scope}{span}".strip()

    def _table(self, rows: list[Row], book: EvidenceBook) -> str:
        lines = ["| Reihe | Zeitraum | Wert | Beleg |", "|---|---|---|---|"]
        for row in rows:
            sources = " ".join(f"[{self.cite(f, book)}]" for f in row.facts)
            note = f" ({row.note})" if row.note else ""
            lines.append(f"| {row.series} | {row.period} | {format_value(row)}{note} | {sources} |")
        return "\n".join(lines)


def _numbers(text: str) -> tuple[int, ...]:
    import re

    return tuple(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", text)))


def _year_of(fact: Fact) -> int | None:
    day = fact.valid_from or fact.on_date or fact.valid_to
    return day.year if day else None


def _series(fact: Fact) -> str:
    name = utility_label(fact.utility_type, fact.tariff_kind)
    return f"{name} {KIND_LABELS[fact.kind]}{' ' + fact.zone if fact.zone else ''}"


def _value(fact: Fact) -> str:
    digits = 4 if fact.kind is FactKind.Z_FACTOR else (None if fact.unit in ("kWh", "m³") else 2)
    return fmt(fact.value, fact.unit, digits)


def _current(agreed: list[Fact], year: int | None) -> set[Fact]:
    """Per series the agreed value that applies in the middle of ``year``."""
    if year is None:
        return set()
    middle = date(year, 7, 1)
    best: dict[str, Fact] = {}
    for fact in agreed:
        if fact.applies_on(middle):
            key = _series(fact)
            if key not in best or (fact.valid_from or date.min) > (
                best[key].valid_from or date.min
            ):
                best[key] = fact
    return set(best.values())


def _scope(utility: UtilityType | None, tariff: TariffKind | None, year: int | None) -> str:
    parts = [utility_label(utility, tariff) if utility else "alle Sparten"]
    if year:
        parts.append(str(year))
    return ", ".join(parts)
