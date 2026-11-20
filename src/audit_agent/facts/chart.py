"""Render a chart from overview rows as PNG plus JSON with the plotted data (ADR-0018)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display on the laptop service or in tests

import matplotlib.pyplot as plt  # noqa: E402

from audit_agent.facts.views import Row, Topic  # noqa: E402

COLORS = ("#2a6f97", "#e07a1f", "#3a8a5c", "#8e5aa8", "#b5443b", "#6b7a8f")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "grafik"


def render_chart(rows: list[Row], topic: Topic, title: str, out_dir: Path) -> tuple[Path, Path]:
    """Bars per period for consumption and costs, steps over time for prices."""
    out_dir.mkdir(parents=True, exist_ok=True)
    name = slug(title)
    png, data = out_dir / f"{name}.png", out_dir / f"{name}.json"
    series = list(dict.fromkeys(r.series for r in rows))
    periods = list(dict.fromkeys(r.period for r in rows))
    units = sorted({r.unit for r in rows})
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=110)
    if topic is Topic.PRICES:
        for i, name_ in enumerate(series):
            points = [r for r in rows if r.series == name_]
            ax.plot(
                [r.period for r in points],
                [float(r.value) for r in points],
                marker="o",
                color=COLORS[i % len(COLORS)],
                label=name_,
            )
    else:
        width = 0.8 / max(len(series), 1)
        for i, name_ in enumerate(series):
            values = {r.period: float(r.value) for r in rows if r.series == name_}
            xs = [p + (i - (len(series) - 1) / 2) * width for p in range(len(periods))]
            bars = ax.bar(
                xs,
                [values.get(p, 0.0) for p in periods],
                width=width,
                color=COLORS[i % len(COLORS)],
                label=name_,
            )
            ax.bar_label(
                bars, labels=[_label(values.get(p)) for p in periods], fontsize=7, padding=2
            )
        ax.set_xticks(range(len(periods)), periods)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(", ".join(units))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)
    payload = {
        "title": title,
        "topic": topic.value,
        "rows": [
            {
                "series": r.series,
                "period": r.period,
                "value": str(r.value),
                "unit": r.unit,
                "sources": [f"{f.file} S. {f.page}" for f in r.facts],
            }
            for r in rows
        ],
    }
    data.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return png, data


def _label(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:,.0f}" if value >= 100 else f"{value:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")
