"""Deterministic audit of one bill against the agreed facts (ADR-0018).

The model used to compare target and actual values itself and failed at it (ISS-107: P1
compared the 2025 price with the 2024 price). Here the code does the comparison; the agent
decides which bill to check, reads the findings and explains them.

Rules (each returns ``ok``, ``deviation`` or ``unverifiable``):
1. Prices: every billed price equals the agreed price that applies at the start of the period.
2. Readings: end reading minus start reading equals the billed consumption (per HT/NT zone).
3. Gas: energy = volume x z-Zahl x Brennwert, and the z-Zahl equals the one of the other bills.
4. Arithmetic: quantity x price = amount, and the positions add up to the invoice total.
5. Advance payments: the bill credits as many advances as agreed for the period.
6. Service charges: billed living area equals the area of the rental contract.
"""

from __future__ import annotations

from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from audit_agent.corpus import DocumentMeta, UtilityType
from audit_agent.facts.extract import first_installment
from audit_agent.facts.models import KIND_LABELS, PRICE_KINDS, Fact, FactKind, FactStore, Role

PRICE_TOLERANCE = Decimal("0.005")
AMOUNT_TOLERANCE = Decimal("0.03")
CENT = Decimal("0.01")


class CheckStatus(StrEnum):
    OK = "ok"
    DEVIATION = "deviation"
    UNVERIFIABLE = "unverifiable"


STATUS_LABELS = {
    CheckStatus.OK: "stimmt",
    CheckStatus.DEVIATION: "ABWEICHUNG",
    CheckStatus.UNVERIFIABLE: "nicht prüfbar",
}


class Check(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    status: CheckStatus
    expected: str = ""
    """Target value (Soll) with unit."""
    actual: str = ""
    """Billed value (Ist) with unit."""
    impact_eur: Decimal | None = None
    """Effect on the invoice; positive = the customer pays too much."""
    note: str = ""
    facts: tuple[Fact, ...] = ()


class AuditReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    checks: tuple[Check, ...]

    @property
    def deviations(self) -> list[Check]:
        return [c for c in self.checks if c.status is CheckStatus.DEVIATION]

    @property
    def total_impact(self) -> Decimal:
        return sum((c.impact_eur or Decimal(0) for c in self.deviations), Decimal(0))


def fmt(value: Decimal, unit: str = "", digits: int | None = None) -> str:
    """German number: ``1.234,56``; integers without decimals unless ``digits`` is given."""
    if digits is None:
        digits = 0 if value == value.to_integral_value() and unit in ("kWh", "m³", "") else 2
        if unit == "" and value != value.to_integral_value():
            digits = 4
    quant = Decimal(1).scaleb(-digits)
    text = f"{value.quantize(quant, ROUND_HALF_UP):,.{digits}f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} {unit}".strip()


def _euro(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def _price_effect(kind: FactKind, difference: Decimal, quantity: Decimal | None) -> Decimal | None:
    if quantity is None:
        return None
    if kind is FactKind.ENERGY_PRICE:
        return _euro(difference * quantity / 100)
    return _euro(difference * quantity)


def check_bill(store: FactStore, meta: DocumentMeta) -> AuditReport:
    """Run all rules that fit the bill's utility; rules without data report ``unverifiable``."""
    facts = store.of_file(meta.file)
    checks: list[Check] = []
    if meta.utility_type in (UtilityType.SERVICE_CHARGES, UtilityType.RENT):
        checks += _service_area(store, meta, facts)
    else:
        checks += _prices(store, meta, facts)
        checks += _readings(meta, facts)
        if meta.utility_type is UtilityType.GAS:
            checks += _gas(store, meta, facts)
    checks += _arithmetic(facts)
    checks += _advances(store, meta, facts)
    return AuditReport(file=meta.file, checks=tuple(checks))


def _prices(store: FactStore, meta: DocumentMeta, facts: list[Fact]) -> list[Check]:
    start = meta.billing_period_start
    checks = []
    for billed in (f for f in facts if f.kind in PRICE_KINDS and f.role is Role.STATED):
        name = f"{KIND_LABELS[billed.kind]}{' ' + billed.zone if billed.zone else ''}"
        agreed = (
            store.agreed(
                billed.kind,
                start,
                contract_id=meta.contract_id,
                utility_type=meta.utility_type,
                zone=billed.zone,
            )
            if start
            else None
        )
        if agreed is None:
            checks.append(
                Check(
                    name=name,
                    status=CheckStatus.UNVERIFIABLE,
                    actual=fmt(billed.value, billed.unit, 2),
                    note="kein Vertrag oder Preisschreiben mit diesem Preis für den Zeitraum",
                    facts=(billed,),
                )
            )
            continue
        difference = billed.value - agreed.value
        is_ok = abs(difference) <= PRICE_TOLERANCE
        valid = f"gültig ab {agreed.valid_from:%d.%m.%Y}" if agreed.valid_from else ""
        checks.append(
            Check(
                name=name,
                status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
                expected=f"{fmt(agreed.value, agreed.unit, 2)} ({valid})",
                actual=fmt(billed.value, billed.unit, 2),
                impact_eur=None
                if is_ok
                else _price_effect(billed.kind, difference, billed.quantity),
                note="" if is_ok else f"Differenz {fmt(difference, billed.unit, 2)}",
                facts=(agreed, billed),
            )
        )
    return checks


def _readings(meta: DocumentMeta, facts: list[Fact]) -> list[Check]:
    checks = []
    zones = sorted({f.zone or "" for f in facts if f.kind is FactKind.METER_READING})
    for zone_key in zones:
        zone = zone_key or None
        readings = sorted(
            (f for f in facts if f.kind is FactKind.METER_READING and f.zone == zone),
            key=lambda f: f.on_date,  # type: ignore[arg-type, return-value]
        )
        if len(readings) < 2:
            continue
        first, last = readings[0], readings[-1]
        measured = last.value - first.value
        unit = last.unit
        stated_kinds = (
            (FactKind.GAS_VOLUME,)
            if meta.utility_type is UtilityType.GAS
            else (FactKind.CONSUMPTION,)
        )
        stated = [f for f in facts if f.kind in stated_kinds and f.zone == zone and f.unit == unit]
        priced = [
            f
            for f in facts
            if f.kind in (FactKind.ENERGY_PRICE, FactKind.WATER_PRICE)
            and f.zone == zone
            and f.quantity_unit == unit
        ]
        name = f"Verbrauch{' ' + zone if zone else ''} aus Zählerständen"
        billed_values = {f.value for f in stated} | {
            f.quantity for f in priced if f.quantity is not None
        }
        if not billed_values:
            continue
        wrong = sorted(v for v in billed_values if v != measured)
        if not wrong:
            checks.append(
                Check(
                    name=name,
                    status=CheckStatus.OK,
                    expected=_difference_text(last.value, first.value, measured, unit),
                    actual=fmt(measured, unit),
                    facts=(first, last, *stated[:1]),
                )
            )
            continue
        billed = wrong[0]
        price = next((f for f in priced if f.quantity == billed), None)
        impact = _price_effect(price.kind, billed - measured, price.value) if price else None
        if price and price.kind is FactKind.ENERGY_PRICE:
            impact = _euro((billed - measured) * price.value / 100)
        checks.append(
            Check(
                name=name,
                status=CheckStatus.DEVIATION,
                expected=_difference_text(last.value, first.value, measured, unit),
                actual=f"abgerechnet {fmt(billed, unit)}",
                impact_eur=impact,
                note=f"Differenz {fmt(billed - measured, unit)}",
                facts=(
                    first,
                    last,
                    *(f for f in stated if f.value == billed),
                    *([price] if price else []),
                ),
            )
        )
    return checks


def _gas(store: FactStore, meta: DocumentMeta, facts: list[Fact]) -> list[Check]:
    def one(kind: FactKind) -> Fact | None:
        return next((f for f in facts if f.kind is kind), None)

    volume, z, calorific = (
        one(FactKind.GAS_VOLUME),
        one(FactKind.Z_FACTOR),
        one(FactKind.CALORIFIC_VALUE),
    )
    energy = next((f for f in facts if f.kind is FactKind.CONSUMPTION and f.unit == "kWh"), None)
    price = next((f for f in facts if f.kind is FactKind.ENERGY_PRICE), None)
    checks = []
    if volume and z and calorific and energy:
        computed = (volume.value * z.value * calorific.value).quantize(Decimal(1), ROUND_HALF_UP)
        is_ok = abs(computed - energy.value) <= 1
        checks.append(
            Check(
                name="Umrechnung m³ in kWh",
                status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
                expected=(
                    f"{fmt(volume.value, 'm³')} × {fmt(z.value, '', 4)} × "
                    f"{fmt(calorific.value, 'kWh/m³', 3)} = {fmt(computed, 'kWh')}"
                ),
                actual=fmt(energy.value, "kWh"),
                facts=(volume, z, calorific, energy),
            )
        )
    if z:
        others = [
            f
            for f in store.select([FactKind.Z_FACTOR], contract_id=meta.contract_id)
            if f.file != meta.file
        ]
        if not others:
            checks.append(
                Check(
                    name="z-Zahl",
                    status=CheckStatus.UNVERIFIABLE,
                    actual=fmt(z.value, "", 4),
                    note="keine andere Gasrechnung zum Vergleich",
                    facts=(z,),
                )
            )
        else:
            reference = Counter(f.value for f in others).most_common(1)[0][0]
            source = next(f for f in others if f.value == reference)
            is_ok = z.value == reference
            impact = None
            if not is_ok and volume and calorific and price:
                wrong = (volume.value * z.value * calorific.value).quantize(
                    Decimal(1), ROUND_HALF_UP
                )
                right = (volume.value * reference * calorific.value).quantize(
                    Decimal(1), ROUND_HALF_UP
                )
                impact = _euro((wrong - right) * price.value / 100)
            checks.append(
                Check(
                    name="z-Zahl",
                    status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
                    expected=f"{fmt(reference, '', 4)} (wie in den anderen Gasrechnungen)",
                    actual=fmt(z.value, "", 4),
                    impact_eur=impact,
                    note=""
                    if is_ok
                    else "die z-Zahl hängt von Höhe und Druck der Verbrauchsstelle ab",
                    facts=(source, z, *([price] if price else [])),
                )
            )
    return checks


def _arithmetic(facts: list[Fact]) -> list[Check]:
    checks = []
    for f in facts:
        if f.kind not in PRICE_KINDS or f.quantity is None or f.amount is None:
            continue
        expected = f.value * f.quantity / (100 if f.kind is FactKind.ENERGY_PRICE else 1)
        if abs(_euro(expected) - f.amount) > AMOUNT_TOLERANCE:
            checks.append(
                Check(
                    name=f"Betrag {f.label}",
                    status=CheckStatus.DEVIATION,
                    expected=fmt(_euro(expected), "EUR", 2),
                    actual=fmt(f.amount, "EUR", 2),
                    impact_eur=_euro(f.amount - expected),
                    facts=(f,),
                )
            )
    totals = {f.value for f in facts if f.kind is FactKind.INVOICE_TOTAL}
    items = [
        f
        for f in facts
        if (f.kind in PRICE_KINDS and f.amount is not None)
        or (f.kind is FactKind.POSITION and f.utility_type not in (UtilityType.SERVICE_CHARGES,))
    ]
    service = next((f for f in facts if f.kind is FactKind.SERVICE_COSTS), None)
    if service is not None:
        parts = [f for f in facts if f.kind is FactKind.POSITION]
        total_share = sum((f.amount or Decimal(0) for f in parts), Decimal(0))
        is_ok = abs(total_share - (service.amount or Decimal(0))) <= AMOUNT_TOLERANCE
        checks.append(
            Check(
                name="Summe der Kostenarten",
                status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
                expected=fmt(total_share, "EUR", 2),
                actual=fmt(service.amount or Decimal(0), "EUR", 2),
                facts=(service,),
            )
        )
        return checks
    if totals and items:
        summed = sum((f.amount or Decimal(0) for f in items), Decimal(0))
        total = max(totals)
        is_ok = abs(summed - total) <= AMOUNT_TOLERANCE and len(totals) == 1
        total_fact = next(f for f in facts if f.kind is FactKind.INVOICE_TOTAL and f.value == total)
        checks.append(
            Check(
                name="Summe der Positionen",
                status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
                expected=fmt(summed, "EUR", 2),
                actual=fmt(total, "EUR", 2),
                facts=(total_fact,),
            )
        )
    return checks


def _advances(store: FactStore, meta: DocumentMeta, facts: list[Fact]) -> list[Check]:
    credited = next((f for f in facts if f.kind is FactKind.ADVANCES_CREDITED), None)
    if credited is None or meta.billing_period_start is None or credited.count is None:
        return []
    agreed = store.agreed(
        FactKind.ADVANCE,
        first_installment(meta.billing_period_start),
        contract_id=meta.contract_id,
        utility_type=meta.utility_type,
    )
    if agreed is None:
        return [
            Check(
                name="angerechnete Abschläge",
                status=CheckStatus.UNVERIFIABLE,
                actual=f"{credited.count} × {fmt(credited.value, 'EUR', 2)}",
                note="kein vereinbarter Abschlag für den Zeitraum gefunden",
                facts=(credited,),
            )
        ]
    is_ok = agreed.value == credited.value
    impact = None if is_ok else _euro((agreed.value - credited.value) * credited.count)
    return [
        Check(
            name="angerechnete Abschläge",
            status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
            expected=_times_text(credited.count, agreed.value, agreed.value * credited.count),
            actual=_times_text(credited.count, credited.value, credited.amount or Decimal(0)),
            impact_eur=impact,
            note=""
            if is_ok
            else "es wurden weniger Abschläge angerechnet als vereinbart und gezahlt",
            facts=(agreed, credited),
        )
    ]


def _service_area(store: FactStore, meta: DocumentMeta, facts: list[Fact]) -> list[Check]:
    billed = next((f for f in facts if f.kind is FactKind.LIVING_AREA), None)
    service = next((f for f in facts if f.kind is FactKind.SERVICE_COSTS), None)
    if billed is None or meta.billing_period_start is None:
        return []
    agreed = store.agreed(
        FactKind.LIVING_AREA,
        meta.billing_period_start,
        contract_id=meta.contract_id,
        utility_type=meta.utility_type,
    )
    total = store.agreed(
        FactKind.TOTAL_AREA,
        meta.billing_period_start,
        contract_id=meta.contract_id,
        utility_type=meta.utility_type,
    )
    if agreed is None:
        return [
            Check(
                name="Wohnfläche",
                status=CheckStatus.UNVERIFIABLE,
                actual=fmt(billed.value, "m²", 2),
                note="kein Mietvertrag mit Wohnfläche gefunden",
                facts=(billed,),
            )
        ]
    is_ok = agreed.value == billed.value
    impact = None
    if not is_ok and service is not None and total is not None and service.amount is not None:
        right = _euro(service.value * agreed.value / total.value)
        impact = _euro(service.amount - right)
    note = ""
    if not is_ok and total is not None and service is not None:
        right_share = (agreed.value / total.value * 100).quantize(CENT, ROUND_HALF_UP)
        note = (
            f"richtiger Anteil {fmt(agreed.value, 'm²', 2)} / {fmt(total.value, 'm²', 2)} = "
            f"{fmt(right_share, '%', 2)}, also "
            f"{fmt(_euro(service.value * agreed.value / total.value), 'EUR', 2)} statt "
            f"{fmt(service.amount or Decimal(0), 'EUR', 2)}"
        )
    return [
        Check(
            name="Wohnfläche",
            status=CheckStatus.OK if is_ok else CheckStatus.DEVIATION,
            expected=f"{fmt(agreed.value, 'm²', 2)} laut Mietvertrag",
            actual=fmt(billed.value, "m²", 2),
            impact_eur=impact,
            note=note,
            facts=(agreed, billed, *([total] if total else []), *([service] if service else [])),
        )
    ]


def _difference_text(end: Decimal, start: Decimal, result: Decimal, unit: str) -> str:
    return f"{fmt(end, unit)} − {fmt(start, unit)} = {fmt(result, unit)}"


def _times_text(count: int, each: Decimal, total: Decimal) -> str:
    return f"{count} × {fmt(each, 'EUR', 2)} = {fmt(total, 'EUR', 2)}"
