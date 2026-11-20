"""Generate the M8 corpus documents 31 to 35 (ADR-0018, ISS-109).

Run with an environment that has WeasyPrint installed (not a project dependency, the corpus is
generated once and committed):

    uv run --with weasyprint python scripts/generate_m8_documents.py

Documents 31 to 34 add a second electricity contract for heating (night storage heaters with a
two-rate meter, HT = Hochtarif, NT = Niedertarif) to the household; the existing SüdVolt
documents 01 to 06 are the household electricity (Lichtstrom). Document 35 is the water bill
2026. Two documents carry a planted error, every other number is computed here so that each
sum in the PDFs is consistent:

- E4 (document 34): the NT consumption is 3.920 kWh although the meter readings give 3.420 kWh.
- E5 (document 35): only 4 x 120,00 EUR advance payments are credited, the fee notice
  (document 14) raised the quarterly advance to 125,00 EUR from Q1/2026.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from weasyprint import HTML

DATASET = Path(__file__).resolve().parents[1] / "dataset"
CENT = Decimal("0.01")
VAT = Decimal("1.19")
WATER_VAT = Decimal("1.07")

CONTRACT_ID = "SV-2024-99317"
METER = "1EMH0098765432"


def money(value: Decimal) -> str:
    """German amount without unit, e.g. 1.234,56."""
    text = f"{value.quantize(CENT, ROUND_HALF_UP):,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def whole(value: Decimal | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def net(gross: Decimal, vat: Decimal = VAT) -> Decimal:
    return cents(gross / vat)


SV_CSS = """
@page { size: A4; margin: 14mm 16mm 22mm 16mm;
  @bottom-left { content: 'SüdVolt Energie GmbH · Energieweg 12 · 69115 Heidelberg\\A Amtsgericht Mannheim HRB 719402 · USt-IdNr. DE298441021'; white-space: pre; font-size: 6.8pt; color: #666; }
  @bottom-right { content: 'Geschäftsführung: Dipl.-Kfm. M. Brenner, Dr. S. Vogt\\A Sparkasse Heidelberg · IBAN DE44 6725 0020 0009 1827 36'; white-space: pre; text-align: right; font-size: 6.8pt; color: #666; } }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 8.6pt; color: #222; }
table { width: 100%; border-collapse: collapse; }
th { background: #0f4d36; color: #fff; text-align: left; padding: 5px 6px; font-size: 8.2pt; font-weight: bold; }
td { padding: 5px 6px; }
tr.z td { background: #f2f6f4; }
.r { text-align: right; }
.b { font-weight: bold; }
.head { display: flex; justify-content: space-between; }
.logo { color: #0f4d36; font-size: 15pt; font-weight: bold; }
.svc { text-align: right; font-size: 7.6pt; color: #444; }
.box { border: 1px solid #b9d8c9; background: #f3faf6; padding: 8px 10px; width: 66mm; float: right; }
.box td { padding: 2px 0; font-size: 7.8pt; }
h1 { color: #0f4d36; font-size: 12pt; margin: 18px 0 8px 0; clear: both; }
h2 { border-left: 4px solid #0f4d36; background: #eef7f2; padding: 5px 8px; font-size: 10pt; margin: 14px 0 6px 0; }
.sum { border: 1px solid #0f4d36; margin: 10px 0; }
.sum td { padding: 4px 10px; }
.sum tr.tot td { border-top: 2px solid #0f4d36; color: #0f4d36; font-weight: bold; font-size: 10pt; }
.sepa { background: #f4f4f4; border: 1px solid #ddd; padding: 6px 8px; font-size: 7.8pt; margin-top: 8px; }
.tot td { background: #dff0e7; font-weight: bold; }
"""

SWM_CSS = """
@page { size: A4; margin: 14mm 16mm 22mm 16mm;
  @bottom-left { content: 'Stadtwerke Mosbach GmbH · Am Henschelberg 6 · 74821 Mosbach\\A Amtsgericht Mannheim HRB 440198 · USt-IdNr. DE144021908'; white-space: pre; font-size: 6.8pt; color: #1f5f8b; }
  @bottom-right { content: 'Geschäftsführung: Dipl.-Ing. R. Hofstätter\\A Sparkasse Neckartal-Odenwald · IBAN DE71 6745 0048 0000 1122 33'; white-space: pre; text-align: right; font-size: 6.8pt; color: #1f5f8b; } }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 8.6pt; color: #222; }
table { width: 100%; border-collapse: collapse; }
th { background: #1f5f8b; color: #fff; text-align: left; padding: 5px 6px; font-size: 8.2pt; font-weight: bold; }
td { padding: 5px 6px; }
tr.z td { background: #f1f6fa; }
.r { text-align: right; }
.b { font-weight: bold; }
.head { display: flex; justify-content: space-between; border-top: 3px solid #1f5f8b; padding-top: 6px; }
.logo { color: #1f5f8b; font-size: 15pt; font-weight: bold; }
.svc { text-align: right; font-size: 7.6pt; color: #1f5f8b; }
.box { border: 1px solid #a9c8de; background: #f3f8fc; padding: 8px 10px; width: 66mm; float: right; }
.box td { padding: 2px 0; font-size: 7.8pt; }
h1 { color: #1f5f8b; font-size: 12pt; margin: 18px 0 8px 0; clear: both; }
h2 { border-left: 4px solid #1f5f8b; background: #eef4f9; padding: 5px 8px; font-size: 10pt; margin: 14px 0 6px 0; }
.sum { border: 1px solid #1f5f8b; margin: 10px 0; }
.sum td { padding: 4px 10px; }
.sum tr.tot td { border-top: 2px solid #1f5f8b; color: #1f5f8b; font-weight: bold; font-size: 10pt; }
.tot td { background: #e3eef7; font-weight: bold; }
"""

ADDRESS = "<p>Herrn<br><b>Lukas Weber</b><br>Hauptstraße 42<br>74821 Mosbach</p>"


def _box(title: str, rows: list[tuple[str, str]]) -> str:
    body = "".join(f'<tr><td>{k}:</td><td class="r b">{v}</td></tr>' for k, v in rows)
    return f'<div class="box"><b>{title}</b><table>{body}</table></div>'


def _sv_head(title: str, rows: list[tuple[str, str]]) -> str:
    return f"""<div class="head"><div class="logo">SüdVolt<br><span style="font-size:6.5pt">ENERGIE GMBH · HEIDELBERG</span></div>
<div class="svc"><b>Kundenservice Privatkunden</b><br>Telefon: 0800 555 2400 (Mo–Fr 7–20 Uhr)<br>service@suedvolt-energie.de · www.suedvolt-energie.de</div></div>
{_box(title, rows)}
<p style="margin-top:6mm;font-size:6.8pt;color:#0f4d36">SüdVolt Energie GmbH · Energieweg 12 · 69115 Heidelberg</p>
{ADDRESS}"""


def _rows(rows: list[list[str]], right_from: int) -> str:
    out = ""
    for i, row in enumerate(rows):
        cells = "".join(
            f'<td class="r">{c}</td>' if j >= right_from else f"<td>{c}</td>"
            for j, c in enumerate(row)
        )
        out += f'<tr class="z">{cells}</tr>' if i % 2 else f"<tr>{cells}</tr>"
    return out


def _header(cols: list[str], right_from: int) -> str:
    cells = "".join(
        f'<th class="r">{c}</th>' if j >= right_from else f"<th>{c}</th>"
        for j, c in enumerate(cols)
    )
    return f"<tr>{cells}</tr>"


# --- Heizstrom (night storage, two-rate meter) --------------------------------------------

PRICES_2024 = {"base": Decimal("8.90"), "ht": Decimal("31.90"), "nt": Decimal("22.40")}
PRICES_2025 = {"base": Decimal("9.90"), "ht": Decimal("33.50"), "nt": Decimal("24.10")}
ADVANCE = {2024: Decimal("85.00"), 2025: Decimal("95.00"), 2026: Decimal("105.00")}


def heating_contract() -> str:
    p = PRICES_2024
    price_rows = [
        [
            "Grundpreis (inkl. Messstellenbetrieb Zweitarifzähler)",
            "EUR / Monat",
            f"{money(net(p['base']))} EUR",
            f"{money(p['base'])} EUR",
        ],
        [
            "Arbeitspreis Hochtarif HT (06:00–22:00 Uhr)",
            "ct / kWh",
            f"{money(net(p['ht']))} ct",
            f"{money(p['ht'])} ct",
        ],
        [
            "Arbeitspreis Niedertarif NT (22:00–06:00 Uhr)",
            "ct / kWh",
            f"{money(net(p['nt']))} ct",
            f"{money(p['nt'])} ct",
        ],
        [
            "Monatlicher Abschlag (11 Teilbeträge Feb–Dez, jeweils 15.)",
            "EUR / Monat",
            f"{money(net(ADVANCE[2024]))} EUR",
            f"{money(ADVANCE[2024])} EUR",
        ],
    ]
    terms = [
        ["Vertragsbeginn / Erstlaufzeit", "01.01.2024 – 31.12.2024 (12 Monate)"],
        [
            "Kündigungsfrist",
            "1 Monat zum Ablauf der Erstvertragslaufzeit in Textform; danach unbefristet mit 1 Monat Frist kündbar.",
        ],
        [
            "Niedertarifzeit (NT)",
            "täglich 22:00–06:00 Uhr; Freigabe der Speicherheizung durch den Netzbetreiber",
        ],
        ["Prognostizierter Jahresverbrauch", "HT 600 kWh / NT 3.200 kWh (2 Nachtspeicheröfen)"],
    ]
    return f"""<html><head><style>{SV_CSS}</style></head><body>
{_sv_head("Vertragsbestätigung Heizstrom", [("Datum", "12.12.2023"), ("Kundennummer", "KD-884120"), ("Vertragskonto", CONTRACT_ID), ("Lieferstelle", "Hauptstraße 42, 74821 Mosbach"), ("Zählernummer", METER), ("Zählerart", "Zweitarifzähler HT/NT"), ("Marktlokations-ID", "50123456790")])}
<h1>Ihre Vertragsbestätigung Heizstrom „SüdVolt WärmeStrom Duo“</h1>
<p>Sehr geehrter Herr Weber,<br><br>vielen Dank für Ihren Auftrag. Wir beliefern Ihre Nachtspeicherheizung (2 Speicheröfen, separater
Zweitarifzähler {METER}) in der Hauptstraße 42, 74821 Mosbach, ab dem 01.01.2024 mit Heizstrom. Der Heizstrom wird getrennt von Ihrem
Haushaltsstrom (Vertragskonto SV-2024-99104) gemessen und abgerechnet.</p>
<h2>1. Ihre Preise ab 01.01.2024</h2>
<table>{_header(["Preisbestandteil", "Einheit", "Netto", "Brutto (inkl. 19 % USt.)"], 2)}{_rows(price_rows, 2)}</table>
<h2>2. Vertragsdaten</h2>
<table>{_header(["Vertragsdetail", "Vereinbarung"], 9)}{_rows(terms, 9)}</table>
<p style="margin-top:10px">Den ersten Abschlag ziehen wir am 15.02.2024 per SEPA-Lastschrift von Ihrem Konto IBAN DE89 6745 0048 0012 3456 78 ein.
Es gelten unsere Allgemeinen Bedingungen für die Belieferung mit Heizstrom (Stand 10/2023).</p>
<p>Mit freundlichen Grüßen<br>SüdVolt Energie GmbH</p>
</body></html>"""


def heating_price_change() -> str:
    old, new = PRICES_2024, PRICES_2025
    rows = [
        [
            "Grundpreis (EUR / Monat)",
            f"{money(net(old['base']))} EUR",
            f"{money(old['base'])} EUR",
            f"{money(net(new['base']))} EUR",
            f"{money(new['base'])} EUR",
        ],
        [
            "Arbeitspreis Hochtarif HT (ct / kWh)",
            f"{money(net(old['ht']))} ct",
            f"{money(old['ht'])} ct",
            f"{money(net(new['ht']))} ct",
            f"{money(new['ht'])} ct",
        ],
        [
            "Arbeitspreis Niedertarif NT (ct / kWh)",
            f"{money(net(old['nt']))} ct",
            f"{money(old['nt'])} ct",
            f"{money(net(new['nt']))} ct",
            f"{money(new['nt'])} ct",
        ],
    ]
    return f"""<html><head><style>{SV_CSS}</style></head><body>
{_sv_head("Preisänderung Heizstrom", [("Datum", "15.11.2024"), ("Kundennummer", "KD-884120"), ("Vertragskonto", CONTRACT_ID), ("Lieferstelle", "Hauptstraße 42, 74821 Mosbach"), ("Zählernummer", METER), ("Gültig ab", "01.01.2025")])}
<h1>Preisänderung Ihres Heizstromtarifs „SüdVolt WärmeStrom Duo“ zum 01.01.2025</h1>
<p>Sehr geehrter Herr Weber,<br><br>gestiegene Netzentgelte für unterbrechbare Verbrauchseinrichtungen sowie höhere Beschaffungskosten
machen eine Anpassung Ihrer Heizstrompreise notwendig. Ab dem 01.01.2025 gelten folgende Preise:</p>
<table>{_header(["Preisbestandteil", "Bisher Netto", "Bisher Brutto", "Neu Netto (ab 01.01.2025)", "Neu Brutto (inkl. 19 % USt.)"], 1)}{_rows(rows, 1)}</table>
<p style="margin-top:10px">Sie haben das Recht, den Vertrag ohne Einhaltung einer Frist zum Wirksamwerden der Preisänderung zu kündigen.
Ihr monatlicher Abschlag wird mit der Jahresrechnung 2024 neu festgelegt.</p>
<p>Mit freundlichen Grüßen<br>SüdVolt Energie GmbH</p>
</body></html>"""


def heating_bill(
    year: int, readings: dict[str, tuple[int, int]], billed_nt: int | None = None
) -> tuple[str, dict[str, Decimal]]:
    """Heating electricity bill; ``billed_nt`` overrides the NT quantity (planted error E4)."""
    prices = PRICES_2024 if year == 2024 else PRICES_2025
    ht_kwh = readings["HT"][1] - readings["HT"][0]
    nt_kwh = billed_nt if billed_nt is not None else readings["NT"][1] - readings["NT"][0]
    ht_gross = cents(Decimal(ht_kwh) * prices["ht"] / 100)
    nt_gross = cents(Decimal(nt_kwh) * prices["nt"] / 100)
    base_gross = prices["base"] * 12
    total_gross = ht_gross + nt_gross + base_gross
    nets = [net(ht_gross), net(nt_gross), net(base_gross)]
    total_net = sum(nets, Decimal(0))
    vat = total_gross - total_net
    advance = ADVANCE[year] * 11
    balance = total_gross - advance
    date = {2024: "18.01.2025", 2025: "20.01.2026"}[year]
    due = {2024: "05.02.2025", 2025: "05.02.2026"}[year]
    reading_rows = [
        [
            METER,
            "HT",
            f"01.01.{year}",
            "Anfangsstand"
            + (" aus Vorjahresrechnung (K)" if year > 2024 else " Einbau Zweitarifzähler (M)"),
            f"{whole(readings['HT'][0])} kWh",
            "-",
        ],
        [
            METER,
            "HT",
            f"31.12.{year}",
            "Kundenablesung (K)",
            f"{whole(readings['HT'][1])} kWh",
            f"{whole(ht_kwh)} kWh",
        ],
        [
            METER,
            "NT",
            f"01.01.{year}",
            "Anfangsstand"
            + (" aus Vorjahresrechnung (K)" if year > 2024 else " Einbau Zweitarifzähler (M)"),
            f"{whole(readings['NT'][0])} kWh",
            "-",
        ],
        [
            METER,
            "NT",
            f"31.12.{year}",
            "Kundenablesung (K)",
            f"{whole(readings['NT'][1])} kWh",
            f"{whole(nt_kwh)} kWh",
        ],
    ]
    position_rows = [
        [
            "Arbeitspreis Hochtarif (HT)",
            f"{whole(ht_kwh)} kWh",
            f"{money(net(prices['ht']))} ct/kWh",
            f"{money(prices['ht'])} ct/kWh",
            f"{money(nets[0])} EUR",
            f"{money(ht_gross)} EUR",
        ],
        [
            "Arbeitspreis Niedertarif (NT)",
            f"{whole(nt_kwh)} kWh",
            f"{money(net(prices['nt']))} ct/kWh",
            f"{money(prices['nt'])} ct/kWh",
            f"{money(nets[1])} EUR",
            f"{money(nt_gross)} EUR",
        ],
        [
            "Grundpreis (12 Monate)",
            f"01.01. – 31.12.{year}",
            f"{money(net(prices['base']))} EUR/Mon.",
            f"{money(prices['base'])} EUR/Mon.",
            f"{money(nets[2])} EUR",
            f"{money(base_gross)} EUR",
        ],
    ]
    html = f"""<html><head><style>{SV_CSS}</style></head><body>
{_sv_head(f"Jahresrechnung Heizstrom {year}", [("Datum", date), ("Kundennummer", "KD-884120"), ("Vertragskonto", CONTRACT_ID), ("Lieferstelle", "Hauptstraße 42, 74821 Mosbach"), ("Zählernummer", METER), ("Rechnungs-Nr.", f"RE-{year + 1}-1{year - 2000}877"), ("Abrechnungszeitraum", f"01.01.{year} – 31.12.{year}")])}
<h1>Ihre Jahresrechnung Heizstrom für den Zeitraum 01.01.{year} bis 31.12.{year}</h1>
<p>Sehr geehrter Herr Weber,<br><br>für die Heizstromlieferung an Ihre Nachtspeicherheizung in der Hauptstraße 42, 74821 Mosbach,
im Zeitraum vom <b>01.01.{year} bis 31.12.{year}</b> rechnen wir wie folgt ab:</p>
<table class="sum">
<tr><td>Rechnungsbetrag Heizstromlieferung {year} (inkl. 19 % USt.)</td><td class="r b">{money(total_gross)} EUR</td></tr>
<tr><td>Abzüglich geleistete Abschlagszahlungen (11 × {money(ADVANCE[year])} EUR, Feb–Dez {year})</td><td class="r">-{money(advance)} EUR</td></tr>
<tr class="tot"><td>Nachzahlungsbetrag (fällig am {due})</td><td class="r">{money(balance)} EUR</td></tr></table>
<div class="sepa"><b>Zahlungshinweis (SEPA-Lastschrift):</b> Den Nachzahlungsbetrag von <b>{money(balance)} EUR</b> ziehen wir am {due} von Ihrem
Konto IBAN DE89 6745 0048 0012 3456 78 ein. Ihr neuer monatlicher Heizstrom-Abschlag beträgt ab 15.02.{year + 1} jeweils
<b>{money(ADVANCE[year + 1])} EUR brutto</b> (11 Abschläge Feb–Dez {year + 1}).</div>
<h2>1. Ermittlung Ihres Heizstromverbrauchs (Zweitarifzähler {METER})</h2>
<table>{_header(["Zählernummer", "Zählwerk", "Datum", "Ableseart", "Zählerstand", "Verbrauch"], 4)}{_rows(reading_rows, 4)}</table>
<h2>2. Detailberechnung der Heizstromkosten (Tarif: SüdVolt WärmeStrom Duo)</h2>
<table>{_header(["Abrechnungsposition", "Zeitraum / Menge", "Preis Netto", "Preis Brutto", "Betrag Netto", "Betrag Brutto"], 2)}{_rows(position_rows, 2)}
<tr class="tot"><td colspan="4">Rechnungsbetrag inkl. 19 % Umsatzsteuer ({money(vat)} EUR USt.)</td><td class="r">{money(total_net)} EUR</td><td class="r">{money(total_gross)} EUR</td></tr></table>
<p style="margin-top:10px;font-size:7.6pt;color:#555">Hinweis: Hochtarif (HT) 06:00–22:00 Uhr, Niedertarif (NT) 22:00–06:00 Uhr. Die Freigabezeiten
der Speicherheizung legt der Netzbetreiber fest.</p>
</body></html>"""
    return html, {
        "total_gross": total_gross,
        "balance": balance,
        "ht_kwh": Decimal(ht_kwh),
        "nt_kwh": Decimal(nt_kwh),
    }


# --- Water 2026 -----------------------------------------------------------------------------


def water_bill_2026() -> tuple[str, dict[str, Decimal]]:
    start, end = 386, 458
    volume = Decimal(end - start)
    drink, base, sewage = Decimal("2.42"), Decimal("6.80"), Decimal("2.98")
    drink_gross = cents(volume * drink)
    base_gross = base * 12
    sewage_gross = cents(volume * sewage)
    total_gross = drink_gross + base_gross + sewage_gross
    drink_net, base_net = net(drink_gross, WATER_VAT), net(base_gross, WATER_VAT)
    total_net = drink_net + base_net + sewage_gross
    vat = total_gross - total_net
    credited = Decimal("120.00") * 4  # planted error E5: 4 x 125,00 EUR were agreed and paid
    balance = total_gross - credited
    reading_rows = [
        ["8WAS445566", "01.01.2026", "Anfangsstand Vorjahresbescheid (M)", f"{start} m³", "-"],
        [
            "8WAS445566",
            "31.12.2026",
            "Funkablesung Stadtwerke (M)",
            f"{end} m³",
            f"{whole(volume)} m³",
        ],
    ]
    position_rows = [
        [
            "Trinkwasser-Verbrauchspreis",
            f"{whole(volume)} m³",
            f"{money(drink)} EUR/m³",
            "7 %",
            f"{money(drink_net)} EUR",
            f"{money(drink_gross)} EUR",
        ],
        [
            "Trinkwasser-Grundpreis (Q3=2,5)",
            "12 Monate",
            f"{money(base)} EUR/Mon.",
            "7 %",
            f"{money(base_net)} EUR",
            f"{money(base_gross)} EUR",
        ],
        [
            "Schmutzwassergebühr (Frischwassermaßstab)",
            f"{whole(volume)} m³",
            f"{money(sewage)} EUR/m³",
            "0 %",
            f"{money(sewage_gross)} EUR",
            f"{money(sewage_gross)} EUR",
        ],
    ]
    word = (
        "Guthaben zu Ihren Gunsten (Erstattung am 15.02.2027)"
        if balance < 0
        else "Nachzahlung (fällig am 15.02.2027)"
    )
    html = f"""<html><head><style>{SWM_CSS}</style></head><body>
<div class="head"><div class="logo">Stadtwerke Mosbach<br><span style="font-size:6.5pt">WASSERVERSORGUNG · STADTENTWÄSSERUNG</span></div>
<div class="svc">Kundenzentrum Am Henschelberg 6<br>Tel. 06261 8905-0 · wasser@swm-mosbach.de</div></div>
{_box("Jahresbescheid Wasser 2026", [("Bescheid- / Schreibdatum", "01.02.2027"), ("Kunden- / Kassenzeichen", "SWM-33910"), ("Verbrauchsstelle", "Hauptstraße 42 (2. OG re.)"), ("Wohnungswasserzähler", "8WAS445566 (WE03)"), ("Bescheid-Nr.", "SWM-W-2027-0391"), ("Zeitraum", "01.01.2026 – 31.12.2026")])}
<p style="margin-top:6mm;font-size:6.8pt;color:#1f5f8b">Stadtwerke Mosbach GmbH · Am Henschelberg 6 · 74821 Mosbach</p>
{ADDRESS}
<h1>Verbrauchsabrechnung Trinkwasser und Gebührenbescheid Schmutzwasser 2026</h1>
<p>Sehr geehrter Herr Weber,<br><br>für die Lieferung von Trinkwasser sowie die Schmutzwasserbeseitigung an Ihrer Verbrauchsstelle Hauptstraße 42,
74821 Mosbach, im Kalenderjahr 2026 rechnen wir wie folgt ab:</p>
<table class="sum">
<tr><td>Gesamtkosten Trinkwasser &amp; Schmutzwasser 2026</td><td class="r b">{money(total_gross)} EUR</td></tr>
<tr><td>Abzüglich geleistete Quartals-Vorauszahlungen (4 × 120,00 EUR in 2026)</td><td class="r">-{money(credited)} EUR</td></tr>
<tr class="tot"><td>{word}</td><td class="r">{money(balance)} EUR</td></tr></table>
<h2>1. Zählerstandsermittlung (Wohnungswasserzähler 8WAS445566)</h2>
<table>{_header(["Zählernummer", "Datum", "Ableseart", "Zählerstand", "Verbrauch"], 3)}{_rows(reading_rows, 3)}</table>
<h2>2. Entgelt- und Gebührenberechnung 2026</h2>
<table>{_header(["Position", "Menge / Zeitraum", "Einzelpreis Brutto", "USt.", "Netto", "Brutto"], 2)}{_rows(position_rows, 2)}
<tr class="tot"><td colspan="4">Gesamtkosten Trinkwasser &amp; Schmutzwasser 2026 ({money(vat)} EUR USt. 7 %)</td><td class="r">{money(total_net)} EUR</td><td class="r">{money(total_gross)} EUR</td></tr></table>
<p style="margin-top:10px">Ihre vierteljährliche Vorauszahlung für 2027 beträgt weiterhin 125,00 EUR. Rechtsbehelfsbelehrung: Gegen die Festsetzung der
Schmutzwassergebühr kann innerhalb eines Monats nach Bekanntgabe Widerspruch bei der Großen Kreisstadt Mosbach, Hauptstraße 29, 74821 Mosbach, erhoben werden.</p>
</body></html>"""
    return html, {"total_gross": total_gross, "balance": balance, "credited": credited}


def main() -> None:
    folder = DATASET / "01_electricity_suedvolt"
    outputs: list[tuple[Path, str, dict[str, Decimal]]] = []
    outputs.append(
        (folder / "31_Heizstrom_Vertragsbestaetigung_SuedVolt_2024.pdf", heating_contract(), {})
    )
    html, values = heating_bill(2024, {"HT": (2000, 2620), "NT": (9500, 12680)})
    outputs.append((folder / "32_Heizstrom_Jahresabrechnung_2024_SuedVolt.pdf", html, values))
    outputs.append(
        (folder / "33_Heizstrom_Preisanpassung_SuedVolt_2025.pdf", heating_price_change(), {})
    )
    html, values = heating_bill(2025, {"HT": (2620, 3200), "NT": (12680, 16100)}, billed_nt=3920)
    outputs.append((folder / "34_Heizstrom_Jahresabrechnung_2025_SuedVolt.pdf", html, values))
    html, values = water_bill_2026()
    outputs.append(
        (
            DATASET / "03_water_stadtwerke_mosbach" / "35_Wasser_Jahresbescheid_2026_SWM.pdf",
            html,
            values,
        )
    )
    for path, page, numbers in outputs:
        HTML(string=page).write_pdf(path)
        print(path.name, {k: str(v) for k, v in numbers.items()})


if __name__ == "__main__":
    main()
