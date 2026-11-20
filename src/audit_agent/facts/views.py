"""Overviews and chart data from the fact store (ADR-0018).

Three topics, each a list of rows with their source facts so that every cell stays citable:
- ``verbrauch``: consumption per bill year, from the meter readings (Heizstrom per HT/NT zone),
  gas as stated energy in kWh.
- ``kosten``: gross invoice total per bill year.
- ``preise``: agreed prices with the date from which they apply.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from audit_agent.corpus import DocType, DocumentCatalog, DocumentMeta, TariffKind, UtilityType
from audit_agent.facts.audit import fmt
from audit_agent.facts.models import KIND_LABELS, PRICE_KINDS, Fact, FactKind, FactStore, Role

TRACKED_UTILITIES = (
    UtilityType.ELECTRICITY,
    UtilityType.GAS,
    UtilityType.WATER,
    UtilityType.SERVICE_CHARGES,
)


class Topic(StrEnum):
    CONSUMPTION = "verbrauch"
    COSTS = "kosten"
    PRICES = "preise"


class Row(BaseModel):
    model_config = ConfigDict(frozen=True)

    series: str
    """E.g. ``Heizstrom NT`` or ``Gas Arbeitspreis``."""
    period: str
    """Year (``2025``) or validity (``ab 01.01.2025``)."""
    value: Decimal
    unit: str
    facts: tuple[Fact, ...]
    note: str = ""


def utility_label(utility: UtilityType, tariff: TariffKind | None) -> str:
    if utility is UtilityType.ELECTRICITY:
        return "Heizstrom" if tariff is TariffKind.HEATING else "Lichtstrom"
    return {
        UtilityType.GAS: "Gas",
        UtilityType.WATER: "Wasser",
        UtilityType.SERVICE_CHARGES: "Betriebskosten",
        UtilityType.DISTRICT_HEATING: "Fernwärme",
    }.get(utility, utility.value)


def _bills(
    catalog: DocumentCatalog,
    utility: UtilityType | None,
    tariff: TariffKind | None,
    years: tuple[int, int] | None,
) -> list[DocumentMeta]:
    bills = [
        d
        for d in catalog.documents
        if d.doc_type is DocType.BILL
        and d.utility_type in TRACKED_UTILITIES
        and (utility is None or d.utility_type is utility)
        and (tariff is None or d.tariff_kind is tariff)
        and d.billing_period_start is not None
        and (years is None or years[0] <= d.billing_period_start.year <= years[1])
    ]
    return sorted(
        bills, key=lambda d: (utility_label(d.utility_type, d.tariff_kind), d.billing_period_start)
    )


def rows_for(
    topic: Topic,
    store: FactStore,
    catalog: DocumentCatalog,
    utility: UtilityType | None = None,
    tariff: TariffKind | None = None,
    years: tuple[int, int] | None = None,
) -> list[Row]:
    if topic is Topic.PRICES:
        return _price_rows(store, utility, tariff, years)
    rows: list[Row] = []
    for bill in _bills(catalog, utility, tariff, years):
        name = utility_label(bill.utility_type, bill.tariff_kind)
        year = str(bill.billing_period_start.year)  # type: ignore[union-attr]
        facts = store.of_file(bill.file)
        if topic is Topic.COSTS:
            total = next((f for f in facts if f.kind is FactKind.INVOICE_TOTAL), None)
            service = next((f for f in facts if f.kind is FactKind.SERVICE_COSTS), None)
            if service is not None and service.amount is not None:
                rows.append(
                    Row(
                        series=name,
                        period=year,
                        value=service.amount,
                        unit="EUR",
                        facts=(service,),
                        note="Ihr Anteil vor Abzug der Vorauszahlungen",
                    )
                )
            elif total is not None:
                rows.append(
                    Row(series=name, period=year, value=total.value, unit="EUR", facts=(total,))
                )
        else:
            rows += _consumption(name, year, bill, facts)
    return rows


def _consumption(name: str, year: str, bill: DocumentMeta, facts: list[Fact]) -> list[Row]:
    if bill.utility_type is UtilityType.GAS:
        energy = next(
            (f for f in facts if f.kind is FactKind.CONSUMPTION and f.unit == "kWh"), None
        )
        return (
            [
                Row(
                    series=name,
                    period=year,
                    value=energy.value,
                    unit="kWh",
                    facts=(energy,),
                    note="laut Rechnung",
                )
            ]
            if energy
            else []
        )
    rows = []
    zones = sorted({f.zone or "" for f in facts if f.kind is FactKind.METER_READING})
    for zone_key in zones:
        zone = zone_key or None
        readings = sorted(
            (f for f in facts if f.kind is FactKind.METER_READING and f.zone == zone),
            key=lambda f: f.on_date,
        )  # type: ignore[arg-type, return-value]
        if len(readings) < 2:
            continue
        value = readings[-1].value - readings[0].value
        rows.append(
            Row(
                series=f"{name} {zone}" if zone else name,
                period=year,
                value=value,
                unit=readings[-1].unit,
                facts=(readings[0], readings[-1]),
                note="aus Zählerständen",
            )
        )
    return rows


def _price_rows(
    store: FactStore,
    utility: UtilityType | None,
    tariff: TariffKind | None,
    years: tuple[int, int] | None,
) -> list[Row]:
    rows = []
    agreed = [
        f
        for f in store.facts
        if f.kind in PRICE_KINDS
        and f.role is Role.AGREED
        and f.utility_type in TRACKED_UTILITIES
        and (utility is None or f.utility_type is utility)
        and (tariff is None or f.tariff_kind is tariff)
        and (years is None or f.valid_from is None or f.valid_from.year <= years[1])
    ]
    for f in sorted(
        agreed,
        key=lambda f: (
            utility_label(f.utility_type, f.tariff_kind),
            f.kind.value,
            f.zone or "",
            f.valid_from,
        ),
    ):
        zone = f" {f.zone}" if f.zone else ""
        series = f"{utility_label(f.utility_type, f.tariff_kind)} {KIND_LABELS[f.kind]}{zone}"
        period = f"ab {f.valid_from:%d.%m.%Y}" if f.valid_from else "-"
        rows.append(Row(series=series, period=period, value=f.value, unit=f.unit, facts=(f,)))
    return rows


def format_value(row: Row) -> str:
    digits = 2 if row.unit not in ("kWh", "m³") else None
    return fmt(row.value, row.unit, digits)
