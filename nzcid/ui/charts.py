"""Reusable Plotly figures used across the dashboard pages."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ..config import COLORS, PILLARS, livability_grade


def _score_color(score: float) -> str:
    if score >= 65:
        return COLORS["good"]
    if score >= 45:
        return COLORS["warn"]
    return COLORS["bad"]


def livability_gauge(score: float, title: str = "Livability") -> go.Figure:
    """A 0-100 gauge for the headline livability score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "", "font": {"size": 40}},
            title={"text": f"{title}<br><span style='font-size:0.8em;color:gray'>"
                           f"{livability_grade(score)}</span>"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": _score_color(score)},
                "steps": [
                    {"range": [0, 30], "color": "#fde8e4"},
                    {"range": [30, 45], "color": "#fcf2dd"},
                    {"range": [45, 60], "color": "#eef6ec"},
                    {"range": [60, 75], "color": "#dcefe9"},
                    {"range": [75, 100], "color": "#c9e8df"},
                ],
                "threshold": {
                    "line": {"color": COLORS["primary"], "width": 3},
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=60, b=10))
    return fig


def pillar_bars(breakdown: pd.DataFrame) -> go.Figure:
    """Horizontal bars of each pillar's 0-100 score."""
    bd = breakdown.sort_values("score")
    fig = go.Figure(
        go.Bar(
            x=bd["score"],
            y=bd["pillar"],
            orientation="h",
            marker_color=[_score_color(s) for s in bd["score"]],
            text=[f"{s:.0f}" for s in bd["score"]],
            textposition="auto",
            hovertemplate="%{y}: %{x:.0f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        height=300,
        xaxis=dict(range=[0, 100], title="Score (0-100)"),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    return fig


def comparison_radar(rows: list[pd.Series], names: list[str]) -> go.Figure:
    """Radar/spider chart comparing pillar scores of two or more suburbs."""
    categories = [p.label for p in PILLARS]
    palette = [COLORS["primary"], COLORS["secondary"], COLORS["accent"]]
    fig = go.Figure()
    for i, (row, name) in enumerate(zip(rows, names)):
        values = [float(row[f"score_{p.key}"]) for p in PILLARS]
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=name,
                line_color=palette[i % len(palette)],
                opacity=0.75,
            )
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=420,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    return fig


def hazard_bars(row: pd.Series) -> go.Figure:
    """Exposure bars (0-100) for the four hazard types — higher = more risk."""
    from ..config import HAZARD_COLUMNS

    labels = list(HAZARD_COLUMNS.values())
    values = [float(row[c]) for c in HAZARD_COLUMNS]
    colors = [
        COLORS["bad"] if v >= 60 else COLORS["warn"] if v >= 35 else COLORS["good"]
        for v in values
    ]
    fig = go.Figure(
        go.Bar(
            x=labels, y=values, marker_color=colors,
            text=[f"{v:.0f}" for v in values], textposition="auto",
            hovertemplate="%{x} exposure: %{y:.0f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        height=300, yaxis=dict(range=[0, 100], title="Exposure (0-100)"),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    return fig


def trend_line(label: str, current: float, trend_pct: float, periods: int = 6,
               prefix: str = "$") -> go.Figure:
    """Reconstruct a simple back-cast trend line from a current value + YoY %.

    Used for the house-price / rent mini trends. Clearly an indicative
    projection, not measured history.
    """
    yrs = list(range(2026 - periods + 1, 2027))
    factor = 1 + trend_pct / 100.0
    # Walk backwards from the current value using the annual growth factor.
    series = [current]
    for _ in range(periods - 1):
        series.append(series[-1] / factor)
    series = series[::-1]
    fig = go.Figure(
        go.Scatter(
            x=yrs, y=series, mode="lines+markers",
            line=dict(color=COLORS["primary"], width=3),
            fill="tozeroy", fillcolor="rgba(11,79,108,0.08)",
            hovertemplate=f"%{{x}}: {prefix}%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.update_layout(
        height=220, title=label, margin=dict(l=10, r=10, t=40, b=20),
        yaxis=dict(title=None), xaxis=dict(dtick=1),
    )
    return fig


def population_pyramid(row: pd.Series) -> go.Figure:
    """Modelled age/sex pyramid derived from population and median age.

    We don't ship per-suburb single-year age tables in the MVP, so we model
    a plausible distribution centred on the suburb's median age. Labelled as
    modelled in the UI.
    """
    bands = ["0-9", "10-19", "20-29", "30-39", "40-49",
             "50-59", "60-69", "70-79", "80+"]
    centres = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85])
    median = float(row["median_age"])
    pop = float(row["population"])
    # Gaussian-ish weighting around the median age, with a youthful floor.
    weights = np.exp(-((centres - median) ** 2) / (2 * 16.0 ** 2)) + 0.15
    weights /= weights.sum()
    totals = weights * pop
    male = (totals * 0.49).round().astype(int)
    female = (totals * 0.51).round().astype(int)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=bands, x=-male, orientation="h", name="Male",
        marker_color=COLORS["primary"],
        hovertemplate="Male %{y}: %{customdata:,}<extra></extra>",
        customdata=male,
    ))
    fig.add_trace(go.Bar(
        y=bands, x=female, orientation="h", name="Female",
        marker_color=COLORS["secondary"],
        hovertemplate="Female %{y}: %{x:,}<extra></extra>",
    ))
    maxv = int(max(male.max(), female.max()) * 1.1) if pop else 1
    fig.update_layout(
        barmode="relative", height=360,
        xaxis=dict(title="Population (modelled)",
                   tickvals=[-maxv, -maxv // 2, 0, maxv // 2, maxv],
                   ticktext=[f"{maxv:,}", f"{maxv // 2:,}", "0",
                             f"{maxv // 2:,}", f"{maxv:,}"]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.18),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    return fig


def ranking_bar(df: pd.DataFrame, highlight: str | None = None) -> go.Figure:
    """Region-wide livability ranking bar chart."""
    d = df.sort_values("livability_score", ascending=True)
    colors = [
        COLORS["accent"] if highlight and s == highlight else COLORS["secondary"]
        for s in d["suburb"]
    ]
    fig = go.Figure(
        go.Bar(
            x=d["livability_score"], y=d["suburb"], orientation="h",
            marker_color=colors, text=d["livability_score"], textposition="auto",
            hovertemplate="%{y}: %{x:.1f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        height=max(320, 24 * len(d)), xaxis=dict(range=[0, 100], title="Livability"),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    return fig
