"""Generate the two faulty corpus documents 29 and 30 (ISS-004, ADR-0005).

Run with an environment that has WeasyPrint installed (it is deliberately not a project
dependency, the corpus is generated once and committed):

    python scripts/generate_error_documents.py

Document 29 is a gas bill 2026 with a wrong z-Zahl (conversion factor 1.0000 instead of 0.9560).
Document 30 is a service-charge statement 2026 with a wrong living area (82 m2 instead of
78 m2 according to the rental contract). All amounts are computed here, so every sum in the
PDFs is internally consistent; only the planted error makes the documents wrong.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from weasyprint import HTML

DATASET = Path(__file__).resolve().parents[1] / "dataset"
CENT = Decimal("0.01")
VAT = Decimal("1.19")

BASE_CSS = """
@page { size: A4; margin: 14mm 16mm 22mm 16mm; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 8.6pt; color: #222; }
table { width: 100%; border-collapse: collapse; }
th { background: #222; color: #fff; text-align: left; padding: 5px 6px; font-size: 8.2pt; }
td { padding: 5px 6px; border-bottom: 1px solid #ddd; }
.r { text-align: right; }
.b { font-weight: bold; }
"""


def money(value: Decimal) -> str:
    """Format as German currency amount without unit, e.g. 1.234,56."""
    text = f"{value.quantize(CENT, ROUND_HALF_UP):,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def whole(value: Decimal | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def gas_bill() -> tuple[str, dict[str, Decimal]]:
    volume = Decimal(10380 - 9320)
    z_factor = Decimal("1.0000")  # planted error, correct value is 0.9560 (documents 08 and 10)
    calorific = Decimal("11.150")
    energy = int((volume * z_factor * calorific).quantize(Decimal(1), ROUND_HALF_UP))
    price_gross = Decimal("0.0995")
    work_gross = cents(Decimal(energy) * price_gross)
    base_gross = Decimal("16.00") * 12
    total_gross = work_gross + base_gross
    advance = Decimal("125.00") * 11
    credit = advance - total_gross
    work_net, base_net = cents(work_gross / VAT), cents(base_gross / VAT)
    total_net = work_net + base_net
    vat = total_gross - total_net
    html = f"""
<html><head><style>{BASE_CSS}
@page {{ @bottom-left {{ content: 'NeckarEnergie Versorgung AG · Neckarpromenade 8 · 74076 Heilbronn\\A Amtsgericht Stuttgart HRB 104892 · USt-IdNr. DE812940115'; white-space: pre; font-size: 6.8pt; color: #666; }}
@bottom-right {{ content: 'Vorstand: Dr. M. Kästner (Vors.), Dipl.-Ing. T. Rehm\\A Volksbank Heilbronn · IBAN DE12 6209 0100 0041 8820 00'; white-space: pre; text-align: right; font-size: 6.8pt; color: #666; }} }}
.head {{ border-bottom: 2px solid #e8601c; padding-bottom: 6px; display: flex; justify-content: space-between; }}
.logo {{ color: #e8601c; font-size: 15pt; font-weight: bold; }}
.box {{ border: 1px solid #f0b890; background: #fff5ec; padding: 8px 10px; width: 62mm; float: right; }}
.box td {{ border: 0; padding: 2px 0; font-size: 7.8pt; }}
h1 {{ border-left: 4px solid #e8601c; padding-left: 8px; font-size: 12pt; margin: 18px 0 8px 0; clear: both; }}
h2 {{ background: #f1f1f1; border-bottom: 2px solid #e8601c; padding: 5px 6px; font-size: 10pt; margin: 14px 0 6px 0; }}
.sum {{ border: 2px solid #e8601c; background: #fff5ec; margin: 10px 0; }}
.sum td {{ border: 0; padding: 4px 10px; }}
.sepa {{ background: #f3f3f3; border: 1px solid #ddd; padding: 6px 8px; font-size: 7.8pt; margin-top: 8px; }}
.tot td {{ background: #fdebd9; color: #8a3b0c; font-weight: bold; }}
</style></head><body>
<div class="head"><div>
<b>Kundenservice Erdgas &amp; Wärme</b><br>Tel. 07131 998 100 · service@neckarenergie.de</div>
<div class="logo">NeckarEnergie</div></div>
<div class="box"><b style="color:#8a3b0c">Jahresrechnung Erdgas 2026</b><table>
<tr><td>Datum:</td><td class="r b">27.01.2027</td></tr>
<tr><td>Kundennummer:</td><td class="r b">NE-440219</td></tr>
<tr><td>Vertragsnummer:</td><td class="r b">GV-2024-7731</td></tr>
<tr><td>Verbrauchsstelle:</td><td class="r b">Hauptstraße 42, 74821 Mosbach</td></tr>
<tr><td>Gaszählernummer:</td><td class="r b">7GAS99887766</td></tr>
<tr><td>Marktlokations-ID:</td><td class="r b">40987654321</td></tr>
<tr><td>Rechnungs-Nr.:</td><td class="r b">GAS-2027-1204</td></tr>
<tr><td>Zeitraum:</td><td class="r b">01.01.2026 – 31.12.2026</td></tr></table></div>
<p style="margin-top:26mm;font-size:6.8pt;color:#c0501c">NeckarEnergie Versorgung AG · Postfach 1420 · 74004 Heilbronn</p>
<p>Herrn<br><b>Lukas Weber</b><br>Hauptstraße 42<br>74821 Mosbach</p>
<h1>Ihre Erdgas-Jahresrechnung für den Zeitraum 01.01.2026 bis 31.12.2026</h1>
<p>Sehr geehrter Herr Weber,<br><br>für die Erdgaslieferung an Ihre Verbrauchsstelle Hauptstraße 42, 74821 Mosbach, im
Kalenderjahr 2026 (365 Tage) rechnen wir wie folgt ab:</p>
<table class="sum">
<tr><td>Rechnungsbetrag Erdgaslieferung 2026 (inkl. 19 % USt.)</td><td class="r b">{money(total_gross)} EUR</td></tr>
<tr><td>Abzüglich geleistete Abschlagszahlungen (11 × 125,00 EUR, Feb–Dez 2026)</td><td class="r">-{money(advance)} EUR</td></tr>
<tr class="tot"><td style="border-top:2px solid #e8601c">Guthaben zu Ihren Gunsten (Gutschrift am 12.02.2027)</td><td class="r" style="border-top:2px solid #e8601c">-{money(credit)} EUR</td></tr></table>
<div class="sepa"><b>Gutschrift:</b> Das Guthaben von <b>{money(credit)} EUR</b> überweisen wir am 12.02.2027 auf Ihr Konto
IBAN DE89 6745 0048 0012 3456 78. Ihr monatlicher Abschlag ab 15.02.2027 beträgt unverändert 125,00 EUR brutto.</div>
<h2>1. Thermische Gasabrechnung nach DVGW-Arbeitsblatt G 685</h2>
<table><tr><th>Zählernummer</th><th class="r">Stand 01.01.2026</th><th class="r">Stand 31.12.2026</th><th class="r">Volumen</th><th class="r">z-Zahl</th><th class="r">Brennwert</th><th class="r">Energiemenge</th></tr>
<tr><td>7GAS99887766</td><td class="r">9.320 m³ (K)</td><td class="r">10.380 m³ (K)</td><td class="r">{whole(volume)} m³</td><td class="r">1,0000</td><td class="r">11,150 kWh/m³</td><td class="r b">{whole(energy)} kWh</td></tr></table>
<h2>2. Entgeltberechnung (Tarif: NeckarGas Komfort 24)</h2>
<table><tr><th>Abrechnungsposition</th><th>Zeitraum / Menge</th><th class="r">Preis Netto</th><th class="r">Preis Brutto</th><th class="r">Betrag Netto</th><th class="r">Betrag Brutto</th></tr>
<tr><td>Arbeitspreis Erdgas</td><td>{whole(energy)} kWh</td><td class="r">8,36 ct/kWh</td><td class="r">9,95 ct/kWh</td><td class="r">{money(work_net)} EUR</td><td class="r">{money(work_gross)} EUR</td></tr>
<tr><td>Grundpreis Erdgas</td><td>12 Monate</td><td class="r">13,45 EUR/Mon.</td><td class="r">16,00 EUR/Mon.</td><td class="r">{money(base_net)} EUR</td><td class="r">{money(base_gross)} EUR</td></tr>
<tr class="tot"><td colspan="4">Rechnungsbetrag inkl. 19 % Umsatzsteuer ({money(vat)} EUR USt.)</td><td class="r">{money(total_net)} EUR</td><td class="r">{money(total_gross)} EUR</td></tr></table>
</body></html>"""
    values = {"energy": Decimal(energy), "total_gross": total_gross, "credit": credit}
    return html, values


def service_charges() -> tuple[str, dict[str, Decimal]]:
    area_stated, area_total = (
        Decimal("82.00"),
        Decimal("312.00"),
    )  # planted error: contract says 78.00
    share = area_stated / area_total
    share_pct = f"{(share * 100).quantize(CENT, ROUND_HALF_UP)}".replace(".", ",")
    rows = [
        ("Niederschlagswasser &amp; Allgemeinwasser (Garten/ Treppenhaus)", Decimal("650.00")),
        ("Müllabfuhr und Straßenreinigung", Decimal("1300.00")),
        ("Wohngebäude- und Haus- &amp; Grundbesitzerhaftpflicht", Decimal("1680.00")),
        ("Grundsteuer B (Stadt Mosbach)", Decimal("960.00")),
        ("Hausmeisterdienst und Treppenhausreinigung", Decimal("1640.00")),
        ("Gartenpflege Außenanlagen", Decimal("900.00")),
        ("Allgemeinstrom (Treppenhaus &amp; Kellerbeleuchtung)", Decimal("340.00")),
    ]
    body, total, mine = "", Decimal(0), Decimal(0)
    for i, (name, amount) in enumerate(rows):
        part = cents(amount * share)
        total, mine = total + amount, mine + part
        shade = ' style="background:#f3f3f3"' if i % 2 else ""
        body += (
            f"<tr{shade}><td>{name}</td><td>Wohnfläche ({share_pct}&nbsp;%)</td>"
            f'<td class="r">{money(amount)} EUR</td><td class="r">{money(part)} EUR</td></tr>'
        )
    advance = Decimal("160.00") * 12
    balance = mine - advance  # positive = back payment
    word = "Nachzahlung zu Ihren Lasten (Zahlung bis 31.03.2027)" if balance > 0 else "Guthaben"
    wages = [
        (
            "Hausmeistertätigkeit &amp; Treppenhausreinigung",
            "Gebäudeservice Odenwald GmbH",
            Decimal("1300.00"),
        ),
        ("Gartenpflege und Winterdienst", "Gartenbau Grünschnitt e.K.", Decimal("740.00")),
    ]
    wage_rows, wage_total, wage_mine = "", Decimal(0), Decimal(0)
    for kind, firm, wage in wages:
        part = cents(wage * share)
        wage_total, wage_mine = wage_total + wage, wage_mine + part
        wage_rows += (
            f'<tr><td>{kind}</td><td>{firm}</td><td class="r">{money(wage)} EUR</td>'
            f'<td class="r">{money(part)} EUR</td></tr>'
        )
    html = f"""
<html><head><style>{BASE_CSS}
body {{ font-family: 'DejaVu Serif', serif; }}
@page {{ @bottom-left {{ content: 'Hausverwaltung Kraichgau & Neckar GmbH · Schlossgasse 4 · 74821 Mosbach\\A Amtsgericht Mannheim HRB 441205 · Mitglied im VDIV Baden-Württemberg'; white-space: pre; font-size: 6.8pt; color: #666; }}
@bottom-right {{ content: 'Geschäftsführer: Dipl.-Betriebsw. (FH) W. Brecht\\A Tel. 06261 9182-0 · info@hv-kraichgau.de'; white-space: pre; text-align: right; font-size: 6.8pt; color: #666; }} }}
.top {{ display: flex; justify-content: space-between; border-bottom: 2px solid #444; padding-bottom: 8px; }}
h1 {{ text-align: center; font-size: 11.5pt; border-bottom: 1px solid #444; padding: 10px 0; margin: 14px 0; }}
td, th {{ font-size: 8.2pt; }}
.sub td {{ background: #e9e9e9; font-weight: bold; }}
h3 {{ font-size: 10pt; margin: 18px 0 6px 0; }}
</style></head><body>
<div class="top"><div><b>HAUSVERWALTUNG</b><br>Kraichgau &amp; Neckar GmbH</div>
<div style="text-align:right;font-size:7.8pt">Mieter: Herr Lukas Weber<br>Abrechnungsdatum: 11.03.2027</div></div>
<h1>BETRIEBSKOSTENABRECHNUNG 2026 (§ 556 BGB)</h1>
<p>Sehr geehrter Herr Weber, für Ihre Mietwohnung Hauptstraße 42, 74821 Mosbach (2. OG rechts,
Wohnfläche {str(area_stated).replace(".", ",")} m² von {str(area_total).replace(".", ",")} m² = <b>{share_pct} %</b>), rechnen wir die
Betriebskosten für den Zeitraum vom <b>01.01.2026 bis 31.12.2026</b> (365 Tage) wie folgt ab:</p>
<table><tr><th>Kostenart (gemäß § 2 BetrKV)</th><th>Umlageschlüssel</th><th class="r">Gesamtkosten Objekt</th><th class="r">Ihr Anteil ({share_pct} %)</th></tr>
{body}
<tr class="sub"><td colspan="2">Summe umlagefähige Betriebskosten 2026</td><td class="r">{money(total)} EUR</td><td class="r">{money(mine)} EUR</td></tr>
<tr><td colspan="3">Abzüglich geleistete Betriebskostenvorauszahlungen (12 × 160,00 EUR)</td><td class="r">-{money(advance)} EUR</td></tr>
<tr class="sub"><td colspan="3">{word}</td><td class="r">{money(balance)} EUR</td></tr></table>
<h3>Bescheinigung nach § 35a EStG (BMF-Muster Anlage 2)</h3>
<p style="font-size:7.6pt">In der Jahresabrechnung 2026 für das Objekt Hauptstraße 42, 74821 Mosbach (Wohnung 2. OG rechts), sind folgende anteilige
Aufwendungen für haushaltsnahe Dienstleistungen (§ 35a Abs. 2 S. 1 Alt. 2 EStG, reine Lohnkosten ohne Material) enthalten:</p>
<table><tr><th>Leistungsart (§ 35a Abs. 2 EStG)</th><th>Auftragnehmer</th><th class="r">Gesamter Lohnanteil</th><th class="r">Anteil Mieter ({share_pct} %)</th></tr>
{wage_rows}
<tr class="sub"><td colspan="2">Summe steuerlich relevanter Aufwendungen (§ 35a Abs. 2 EStG)</td><td class="r">{money(wage_total)} EUR</td><td class="r">{money(wage_mine)} EUR</td></tr></table>
<p style="font-size:7.6pt;color:#555;margin-top:10px">Hinweis: Die Entscheidung darüber, welche Positionen im Rahmen der Einkommensteuererklärung berücksichtigt werden können,
obliegt ausschließlich der zuständigen Finanzbehörde.</p>
</body></html>"""
    return html, {"total": total, "mine": mine, "balance": balance}


def main() -> None:
    gas_html, gas_values = gas_bill()
    out = DATASET / "02_gas_neckarenergie" / "29_Gas_Jahresabrechnung_2026_NeckarEnergie.pdf"
    HTML(string=gas_html).write_pdf(out)
    print(out.name, {k: str(v) for k, v in gas_values.items()})
    sc_html, sc_values = service_charges()
    out = (
        DATASET
        / "04_housing_utilities_contractors"
        / "30_Nebenkostenabrechnung_2026_Hausverwaltung.pdf"
    )
    HTML(string=sc_html).write_pdf(out)
    print(out.name, {k: str(v) for k, v in sc_values.items()})


if __name__ == "__main__":
    main()
