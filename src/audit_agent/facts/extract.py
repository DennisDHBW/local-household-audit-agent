"""Rule-based extraction of facts from the parsed chunks (ADR-0018).

No model is involved: table rows are serialized as ``Spalte: Wert | Spalte: Wert`` by the
parser (ADR-0007), so the rules work on column names and row labels. They are written for the
layouts of this corpus (SüdVolt, NeckarEnergie, Stadtwerke Mosbach, Hausverwaltung) and say so
openly; a new provider layout needs new rules, just like the parser.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from decimal import Decimal

from audit_agent.corpus import DocType, DocumentMeta
from audit_agent.facts.models import Fact, FactKind, Role
from audit_agent.ingestion import ChunkType, DocumentChunk, ParsedDocument

NUMBER = re.compile(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|-?\d+(?:,\d+)?")
DATE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
COUNT_TIMES = re.compile(r"(\d+)\s*[×x]\s*(" + NUMBER.pattern + r")\s*EUR")
LABEL_KEYS = frozenset(
    {
        "Preisbestandteil",
        "Tarifbestandteil",
        "Leistungs- / Gebührenart",
        "Position",
        "Abrechnungsposition",
        "Mietbestandteil",
        "Kostenart (gemäß § 2 BetrKV)",
        "Messwert / Kennzahl",
        "Fälligkeit",
    }
)
AGREED_DOC_TYPES = frozenset({DocType.CONTRACT, DocType.PRICE_ADJUSTMENT, DocType.PAYMENT_PLAN})
MONTHS = {
    "januar": 1,
    "februar": 2,
    "märz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ])")


def to_decimal(text: str) -> Decimal:
    return Decimal(text.replace(".", "").replace(",", "."))


def first_number(text: str | None) -> Decimal | None:
    if not text:
        return None
    match = NUMBER.search(text)
    return to_decimal(match.group(0)) if match else None


def first_date(text: str | None) -> date | None:
    if not text:
        return None
    match = DATE.search(text)
    if not match:
        return None
    day, month, year = (int(g) for g in match.groups())
    return date(year, month, day)


def row_pairs(content: str) -> list[tuple[str, str]]:
    """``"A: 1 | B: 2"`` -> ``[("A", "1"), ("B", "2")]``; a part without colon has no value."""
    pairs = []
    for part in content.split(" | "):
        key, sep, value = part.partition(": ")
        pairs.append((key.strip(), value.strip()) if sep else (part.strip(), ""))
    return pairs


def zone_of(label: str) -> str | None:
    folded = f" {label.lower()} "
    if "hochtarif" in folded or " ht " in folded or "(ht)" in folded:
        return "HT"
    if "niedertarif" in folded or " nt " in folded or "(nt)" in folded:
        return "NT"
    return None


def price_kind(label: str) -> FactKind | None:
    """Kind of a price row from its label; ``None`` for rows that are not prices we track."""
    folded = label.lower()
    if "jahresäquivalent" in folded or "/ jahr" in folded or "bonus" in folded:
        return None
    if "abschlag" in folded or "vorauszahlung" in folded:
        return FactKind.ADVANCE
    if "arbeitspreis" in folded:
        return FactKind.ENERGY_PRICE
    if "trinkwasser-verbrauchspreis" in folded:
        return FactKind.WATER_PRICE
    if "schmutzwasser" in folded:
        return FactKind.SEWAGE_FEE
    if "grundpreis" in folded:
        return FactKind.BASE_PRICE
    return None


def unit_for(kind: FactKind, label: str) -> str:
    folded = label.lower()
    if kind is FactKind.ENERGY_PRICE:
        return "ct/kWh"
    if kind in (FactKind.WATER_PRICE, FactKind.SEWAGE_FEE):
        return "EUR/m³"
    if kind is FactKind.ADVANCE:
        return "EUR/Quartal" if "viertel" in folded or "quartal" in folded else "EUR/Monat"
    return "EUR/Monat"


def quantity_of(text: str) -> tuple[Decimal | None, str | None]:
    """Quantity column of a bill position: ``3.100 kWh``, ``74 m³``, ``12 Monate`` or a year."""
    if "kWh" in text:
        return first_number(text), "kWh"
    if "m³" in text:
        return first_number(text), "m³"
    if "Monat" in text:
        return first_number(text), "Monate"
    if "–" in text or " - " in text:  # 01.01. – 31.12.2025
        return Decimal(12), "Monate"
    return None, None


class _Builder:
    """Collects the facts of one document; shared metadata goes into every fact."""

    def __init__(self, meta: DocumentMeta):
        self.meta = meta
        self.facts: list[Fact] = []
        self.role = Role.AGREED if meta.doc_type in AGREED_DOC_TYPES else Role.STATED
        if meta.utility_type.value == "rent":
            self.role = Role.AGREED

    def add(self, chunk: DocumentChunk, kind: FactKind, value: Decimal, **extra: object) -> None:
        meta = self.meta
        defaults: dict[str, object] = {}
        if self.role is Role.AGREED:
            defaults["valid_from"] = meta.valid_from or meta.document_date
        else:
            defaults["valid_from"] = meta.billing_period_start
            defaults["valid_to"] = meta.billing_period_end
        defaults.update(extra)
        self.facts.append(
            Fact(
                kind=kind,
                role=defaults.pop("role", self.role),  # type: ignore[arg-type]
                value=value,
                file=meta.file,
                page=chunk.page_number,
                chunk_id=chunk.chunk_id,
                utility_type=meta.utility_type,
                tariff_kind=meta.tariff_kind,
                doc_type=meta.doc_type,
                contract_id=meta.contract_id,
                **defaults,  # type: ignore[arg-type]
            )
        )


def extract_document(document: ParsedDocument, meta: DocumentMeta) -> list[Fact]:
    """All facts of one parsed document."""
    builder = _Builder(meta)
    for chunk in document.chunks:
        if chunk.chunk_type is ChunkType.TABLE_ROW:
            _row_facts(builder, chunk)
        elif chunk.chunk_type is ChunkType.TEXT:
            _text_facts(builder, chunk)
    return _dedupe(builder.facts)


def _dedupe(facts: list[Fact]) -> list[Fact]:
    """Drop repeated facts (summary box and table total, every row of a payment plan)."""
    seen: set[tuple[object, ...]] = set()
    kept = []
    for fact in facts:
        if fact.kind is FactKind.ADVANCE:
            key: tuple[object, ...] = (fact.kind, fact.value, fact.unit, fact.contract_id)
        else:
            key = (fact.kind, fact.zone, fact.value, fact.on_date, fact.valid_from, fact.label)
        if fact.kind is FactKind.INVOICE_TOTAL:
            key = (fact.kind, fact.value)
        if key in seen:
            continue
        seen.add(key)
        kept.append(fact)
    return kept


def _row_facts(b: _Builder, chunk: DocumentChunk) -> None:
    pairs = row_pairs(chunk.content)
    first_key, first_value = pairs[0]
    columns = dict(pairs)
    if first_key == "Zählernummer" and len(pairs) > 1:
        _meter_row(b, chunk, columns)
        return
    if first_key not in LABEL_KEYS:
        _summary_row(b, chunk, first_key, first_value)
        return
    label = first_value
    if first_key == "Messwert / Kennzahl":
        if "zählerstand" in label.lower():
            day = first_date(columns.get("Stichtag / Zeitraum"))
            value = first_number(columns.get("Wert"))
            if day and value is not None:
                b.add(chunk, FactKind.METER_READING, value, unit="kWh", on_date=day, label=label)
        return
    if first_key == "Fälligkeit":
        day = first_date(label)
        gross = next((v for k, v in pairs if k.startswith("Brutto")), None)
        if day and gross:
            b.add(
                chunk,
                FactKind.ADVANCE,
                first_number(gross) or Decimal(0),
                unit="EUR/Monat",
                valid_from=day,
                label="Abschlagsplan",
                role=Role.AGREED,
            )
        return
    if first_key == "Kostenart (gemäß § 2 BetrKV)":
        _service_row(b, chunk, label, pairs)
        return
    if first_key == "Mietbestandteil":
        if "betriebskosten" in label.lower() and "Monatlich" in columns:
            b.add(
                chunk,
                FactKind.ADVANCE,
                first_number(columns["Monatlich"]) or Decimal(0),
                unit="EUR/Monat",
                label=label,
            )
        return
    if b.meta.doc_type is DocType.BILL:
        _bill_position(b, chunk, label, columns)
    else:
        _agreed_price(b, chunk, label, pairs)


def _agreed_price(
    b: _Builder, chunk: DocumentChunk, label: str, pairs: list[tuple[str, str]]
) -> None:
    kind = price_kind(label)
    if kind is None:
        return
    unit_text = dict(pairs).get("Einheit", "")
    if "jahr" in unit_text.lower():
        return
    new = [(k, v) for k, v in pairs if k.startswith("Neu Brutto")]
    if new:
        key, value = new[0]
        start = next((first_date(k) for k, _ in pairs if "(ab " in k and first_date(k)), None)
    else:
        found = [(k, v) for k, v in pairs if k.startswith("Brutto")]
        if not found:
            return
        key, value = found[0]
        start = None
    number = first_number(value)
    if number is None:
        return
    extra: dict[str, object] = {
        "unit": unit_for(kind, label),
        "label": label,
        "zone": zone_of(label),
    }
    if start is not None:
        extra["valid_from"] = start
    b.add(chunk, kind, number, **extra)


def _bill_position(b: _Builder, chunk: DocumentChunk, label: str, columns: dict[str, str]) -> None:
    amount = first_number(columns.get("Betrag Brutto") or columns.get("Brutto"))
    folded = label.lower()
    if folded.startswith("abzüglich geleistete"):
        if amount is not None:
            _credited(b, chunk, label, amount)
        return
    if folded.startswith(("guthaben", "nachzahlung")) and amount is not None:
        _balance(b, chunk, label, amount)
        return
    if any(word in folded for word in ("zwischensumme", "guthaben", "nachzahlung")):
        return  # subtotals and balances are no line items
    if "rechnungsbetrag" in folded or "gesamtkosten" in folded:
        if amount is not None:
            b.add(chunk, FactKind.INVOICE_TOTAL, amount, unit="EUR", label=label)
        return
    price_text = columns.get("Preis Brutto") or columns.get("Einzelpreis Brutto")
    kind = price_kind(label)
    if kind is None or kind is FactKind.ADVANCE or not price_text:
        if amount is not None:
            b.add(chunk, FactKind.POSITION, amount, unit="EUR", label=label, amount=amount)
        return
    quantity, quantity_unit = quantity_of(
        columns.get("Zeitraum / Menge") or columns.get("Menge / Zeitraum") or ""
    )
    price = first_number(price_text)
    if price is None:
        return
    b.add(
        chunk,
        kind,
        price,
        unit=unit_for(kind, label),
        zone=zone_of(label),
        label=label,
        quantity=quantity,
        quantity_unit=quantity_unit,
        amount=amount,
    )


def _meter_row(b: _Builder, chunk: DocumentChunk, columns: dict[str, str]) -> None:
    zone = columns.get("Zählwerk") or None
    if "Zählerstand" in columns:
        day = first_date(columns.get("Datum"))
        reading = first_number(columns["Zählerstand"])
        unit = "m³" if "m³" in columns["Zählerstand"] else "kWh"
        if day and reading is not None:
            b.add(
                chunk,
                FactKind.METER_READING,
                reading,
                unit=unit,
                zone=zone,
                on_date=day,
                label="Zählerstand",
                valid_from=None,
                valid_to=None,
            )
            used = first_number(columns.get("Verbrauch"))
            if used is not None:
                b.add(chunk, FactKind.CONSUMPTION, used, unit=unit, zone=zone, label="Verbrauch")
        return
    for key, value in columns.items():  # gas: "Stand 01.01.2025: 8.120 m³ (K)"
        if key.startswith("Stand ") and first_date(key):
            number = first_number(value)
            if number is not None:
                b.add(
                    chunk,
                    FactKind.METER_READING,
                    number,
                    unit="m³",
                    on_date=first_date(key),
                    label="Zählerstand",
                    valid_from=None,
                    valid_to=None,
                )
    for key, kind, unit in (
        ("Volumen", FactKind.GAS_VOLUME, "m³"),
        ("z-Zahl", FactKind.Z_FACTOR, ""),
        ("Brennwert", FactKind.CALORIFIC_VALUE, "kWh/m³"),
        ("Energiemenge", FactKind.CONSUMPTION, "kWh"),
    ):
        number = first_number(columns.get(key))
        if number is not None:
            b.add(chunk, kind, number, unit=unit, label=key)


def _summary_row(b: _Builder, chunk: DocumentChunk, key: str, value: str) -> None:
    folded = key.lower()
    number = first_number(value)
    if number is None or b.meta.doc_type is not DocType.BILL:
        return
    if folded.startswith("rechnungsbetrag") or folded.startswith("gesamtkosten"):
        b.add(chunk, FactKind.INVOICE_TOTAL, number, unit="EUR", label=key)
    elif folded.startswith("abzüglich geleistete"):
        _credited(b, chunk, key, number)
    elif folded.startswith(("guthaben", "nachzahlung")):
        _balance(b, chunk, key, number)


def _balance(b: _Builder, chunk: DocumentChunk, label: str, number: Decimal) -> None:
    """Guthaben is stored negative, Nachzahlung positive, whatever sign the PDF prints."""
    value = -abs(number) if label.lower().startswith("guthaben") else abs(number)
    b.add(chunk, FactKind.BALANCE, value, unit="EUR", label=label)


def _credited(b: _Builder, chunk: DocumentChunk, key: str, total: Decimal) -> None:
    match = COUNT_TIMES.search(key)
    if not match:
        return
    b.add(
        chunk,
        FactKind.ADVANCES_CREDITED,
        to_decimal(match.group(2)),
        unit="EUR",
        count=int(match.group(1)),
        amount=abs(total),
        label=key,
    )


def _service_row(
    b: _Builder, chunk: DocumentChunk, label: str, pairs: list[tuple[str, str]]
) -> None:
    columns = dict(pairs)
    share = next((v for k, v in pairs if k.startswith("Ihr Anteil")), None)
    share_amount = first_number(share)
    folded = label.lower()
    if folded.startswith("abzüglich geleistete"):
        if share_amount is not None:
            _credited(b, chunk, label, share_amount)
        return
    if folded.startswith(("guthaben", "nachzahlung")) and share_amount is not None:
        _balance(b, chunk, label, share_amount)
        return
    total = first_number(columns.get("Gesamtkosten Objekt"))
    if total is None or share_amount is None:
        return
    kind = FactKind.SERVICE_COSTS if folded.startswith("summe") else FactKind.POSITION
    b.add(chunk, kind, total, unit="EUR", amount=share_amount, label=label)


AREA_AGREED = re.compile(
    r"Wohnfläche der Mietwohnung beträgt vereinbarungsgemäß (" + NUMBER.pattern + r") m²"
)
AREA_TOTAL = re.compile(r"Gesamtwohnfläche [^.]*?beträgt (" + NUMBER.pattern + r") m²")
AREA_BILLED = re.compile(
    r"Wohnfläche ("
    + NUMBER.pattern
    + r") m² von ("
    + NUMBER.pattern
    + r") m² = ("
    + NUMBER.pattern
    + r") %"
)
AMOUNT_EUR = re.compile(r"(" + NUMBER.pattern + r")\s*EUR")


def _text_facts(b: _Builder, chunk: DocumentChunk) -> None:
    text = " ".join(chunk.content.split())
    if (m := AREA_AGREED.search(text)) and b.role is Role.AGREED:
        b.add(chunk, FactKind.LIVING_AREA, to_decimal(m.group(1)), unit="m²", label="Wohnfläche")
        if t := AREA_TOTAL.search(text):
            b.add(
                chunk,
                FactKind.TOTAL_AREA,
                to_decimal(t.group(1)),
                unit="m²",
                label="Gesamtwohnfläche",
            )
    if (m := AREA_BILLED.search(text)) and b.role is Role.STATED:
        b.add(chunk, FactKind.LIVING_AREA, to_decimal(m.group(1)), unit="m²", label="Wohnfläche")
        b.add(
            chunk, FactKind.TOTAL_AREA, to_decimal(m.group(2)), unit="m²", label="Gesamtwohnfläche"
        )
        b.add(chunk, FactKind.COST_SHARE, to_decimal(m.group(3)), unit="%", label="Umlageanteil")
    for sentence in SENTENCE.split(text):
        _advance_sentence(b, chunk, sentence)


def _advance_sentence(b: _Builder, chunk: DocumentChunk, sentence: str) -> None:
    """Agreed advance payment from a fixed sentence, e.g. "Ihr neuer monatlicher Abschlag
    beträgt ab 15.02.2026 jeweils 120,00 EUR brutto"."""
    folded = sentence.lower()
    is_advance = (
        "abschlag " in folded
        or "abschlag beträgt" in folded
        or "vorauszahlung beträgt" in folded
        or "vorauszahlung für" in folded
    )
    if not is_advance or not any(w in folded for w in ("beträgt", " auf ", "bleibt")):
        return
    anchor = min(i for i in (folded.find("abschlag"), folded.find("vorauszahlung")) if i >= 0)
    amount = AMOUNT_EUR.search(sentence, anchor)  # the amount after the word, not a balance
    if not amount:
        return
    start: date | None = None
    if m := re.search(r"ab (\d{2}\.\d{2}\.\d{4})", sentence):
        start = first_date(m.group(1))
    elif m := re.search(r"ab (" + "|".join(MONTHS) + r") (\d{4})", folded):
        start = date(int(m.group(2)), MONTHS[m.group(1)], 1)
    elif m := re.search(r"für (\d{4})", sentence):
        start = date(int(m.group(1)), 1, 1)
    else:
        start = b.meta.valid_from or b.meta.document_date
    unit = "EUR/Quartal" if "viertel" in folded or "quartal" in folded else "EUR/Monat"
    b.add(
        chunk,
        FactKind.ADVANCE,
        to_decimal(amount.group(1)),
        unit=unit,
        valid_from=start,
        valid_to=None,
        label="Abschlag laut Schreiben",
        role=Role.AGREED,
    )


def first_installment(period_start: date) -> date:
    """Advance payments start on the 15th of the second month (Feb 15 for a calendar year)."""
    return period_start + timedelta(days=45)
