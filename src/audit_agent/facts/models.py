"""Typed facts of the fact store (ADR-0018).

A fact is one number that the code read from a table row or a fixed sentence of a document,
together with what it means (kind, zone, unit), when it applies (validity or reading date),
whether it is the agreed value (contract, price letter, payment plan) or the stated value of a
bill, and the chunk it comes from. The agent never sees a fact without its source chunk, so
every number it reports stays citable.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from audit_agent.corpus import DocType, TariffKind, UtilityType


class FactKind(StrEnum):
    ENERGY_PRICE = "energy_price"
    """Arbeitspreis in ct/kWh (zone HT/NT for Heizstrom)."""
    BASE_PRICE = "base_price"
    """Grundpreis in EUR/Monat."""
    WATER_PRICE = "water_price"
    """Trinkwasser-Verbrauchspreis in EUR/m³."""
    SEWAGE_FEE = "sewage_fee"
    """Schmutzwassergebühr in EUR/m³."""
    ADVANCE = "advance"
    """Agreed advance payment per installment (EUR/Monat or EUR/Quartal)."""
    ADVANCES_CREDITED = "advances_credited"
    """Advance payments a bill deducts: ``count`` x ``value``, total in ``amount``."""
    METER_READING = "meter_reading"
    """Zählerstand on ``on_date``."""
    CONSUMPTION = "consumption"
    """Consumption a bill states (kWh or m³) for the period ending ``valid_to``."""
    GAS_VOLUME = "gas_volume"
    """Gas volume in m³ a bill states."""
    Z_FACTOR = "z_factor"
    """Zustandszahl of a gas bill."""
    CALORIFIC_VALUE = "calorific_value"
    """Brennwert of a gas bill in kWh/m³."""
    INVOICE_TOTAL = "invoice_total"
    """Gross total of a bill."""
    POSITION = "position"
    """Other line item of a bill (bonus, cost type of a service charge statement)."""
    LIVING_AREA = "living_area"
    TOTAL_AREA = "total_area"
    COST_SHARE = "cost_share"
    """Share of the tenant in percent."""
    BALANCE = "balance"
    """Nachzahlung (positive) or Guthaben (negative) a bill states."""
    SERVICE_COSTS = "service_costs"
    """Sum of a service charge statement: object costs in ``value``, tenant share in ``amount``."""


class Role(StrEnum):
    AGREED = "agreed"
    """Contract, price letter, payment plan or rental contract: what should be charged."""
    STATED = "stated"
    """Bill or notice: what was charged or measured."""


PRICE_KINDS = frozenset(
    {FactKind.ENERGY_PRICE, FactKind.BASE_PRICE, FactKind.WATER_PRICE, FactKind.SEWAGE_FEE}
)

KIND_LABELS: dict[FactKind, str] = {
    FactKind.ENERGY_PRICE: "Arbeitspreis",
    FactKind.BASE_PRICE: "Grundpreis",
    FactKind.WATER_PRICE: "Trinkwasserpreis",
    FactKind.SEWAGE_FEE: "Schmutzwassergebühr",
    FactKind.ADVANCE: "Abschlag/Vorauszahlung",
    FactKind.ADVANCES_CREDITED: "angerechnete Abschläge",
    FactKind.METER_READING: "Zählerstand",
    FactKind.CONSUMPTION: "Verbrauch",
    FactKind.GAS_VOLUME: "Gasvolumen",
    FactKind.Z_FACTOR: "z-Zahl",
    FactKind.CALORIFIC_VALUE: "Brennwert",
    FactKind.INVOICE_TOTAL: "Rechnungsbetrag",
    FactKind.POSITION: "Position",
    FactKind.LIVING_AREA: "Wohnfläche",
    FactKind.TOTAL_AREA: "Gesamtwohnfläche",
    FactKind.COST_SHARE: "Umlageanteil",
    FactKind.SERVICE_COSTS: "umlagefähige Betriebskosten",
    FactKind.BALANCE: "Saldo",
}


class Fact(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: FactKind
    role: Role
    value: Decimal
    unit: str = ""
    zone: str | None = None
    """``HT`` or ``NT`` for the two-rate meter of the Heizstrom, otherwise ``None``."""
    label: str = ""
    """Original row label, e.g. ``Arbeitspreis Niedertarif (NT)``."""
    valid_from: date | None = None
    valid_to: date | None = None
    on_date: date | None = None
    quantity: Decimal | None = None
    quantity_unit: str | None = None
    amount: Decimal | None = None
    count: int | None = None
    file: str
    page: int
    chunk_id: str
    utility_type: UtilityType
    tariff_kind: TariffKind | None = None
    doc_type: DocType
    contract_id: str | None = None

    def applies_on(self, day: date) -> bool:
        """True if the fact is valid on ``day`` (agreed values)."""
        if self.valid_from is not None and self.valid_from > day:
            return False
        return self.valid_to is None or self.valid_to >= day


class FactStore(BaseModel):
    """All facts of the corpus; built by ``audit_agent.facts`` and stored as JSON."""

    model_config = ConfigDict(frozen=True)

    facts: tuple[Fact, ...]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=1) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> FactStore:
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def of_file(self, file: str, kind: FactKind | None = None) -> list[Fact]:
        return [f for f in self.facts if f.file == file and (kind is None or f.kind is kind)]

    def select(
        self,
        kinds: Iterable[FactKind],
        *,
        role: Role | None = None,
        utility_type: UtilityType | None = None,
        tariff_kind: TariffKind | None = None,
        contract_id: str | None = None,
        zone: str | None = None,
        any_zone: bool = False,
    ) -> list[Fact]:
        wanted = set(kinds)
        return [
            f
            for f in self.facts
            if f.kind in wanted
            and (role is None or f.role is role)
            and (utility_type is None or f.utility_type is utility_type)
            and (tariff_kind is None or f.tariff_kind is tariff_kind)
            and (contract_id is None or f.contract_id == contract_id)
            and (any_zone or f.zone == zone)
        ]

    def agreed(
        self,
        kind: FactKind,
        on: date,
        *,
        contract_id: str | None,
        utility_type: UtilityType,
        zone: str | None = None,
    ) -> Fact | None:
        """The agreed value that applies on ``on``: the one with the latest ``valid_from``.

        Same contract first; service charges fall back to the rental contract, which has its
        own contract number.
        """
        candidates = [
            f
            for f in self.select([kind], role=Role.AGREED, contract_id=contract_id, zone=zone)
            if f.applies_on(on)
        ]
        if not candidates and utility_type in (UtilityType.SERVICE_CHARGES, UtilityType.RENT):
            candidates = [
                f
                for f in self.facts
                if f.kind is kind
                and f.role is Role.AGREED
                and f.utility_type in (UtilityType.SERVICE_CHARGES, UtilityType.RENT)
                and f.applies_on(on)
            ]
        if not candidates:
            return None
        return max(candidates, key=lambda f: (f.valid_from or date.min, f.chunk_id))
