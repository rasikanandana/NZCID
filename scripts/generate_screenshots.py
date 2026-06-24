"""Generate branded PNG visuals from the real data for LinkedIn / portfolio use.

Run:  python scripts/generate_screenshots.py [output_dir]

Produces standalone, high-resolution images derived from the same charts and
dataset the app uses. (Full in-browser app screenshots need a running browser;
these chart exports are produced headlessly via Plotly + kaleido.)
"""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nzcid import data_loader  # noqa: E402
from nzcid.config import COLORS  # noqa: E402
from nzcid.livability import pillar_breakdown  # noqa: E402
from nzcid.ui import charts  # noqa: E402

W, H = 1200, 750


def _brand(fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
    """Apply consistent branding/layout for export."""
    fig.update_layout(
        template="plotly_white",
        width=W, height=H,
        title=dict(
            text=f"<b>{title}</b>"
                 + (f"<br><span style='font-size:15px;color:{COLORS['muted']}'>"
                    f"{subtitle}</span>" if subtitle else ""),
            x=0.5, xanchor="center", font=dict(size=26, color=COLORS["primary"]),
        ),
        margin=dict(l=70, r=60, t=110, b=120),
        font=dict(family="Arial, Helvetica, sans-serif", size=15),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig.add_annotation(
        text="NZ Community Insights Dashboard · Wellington Region MVP · "
             "data indicative (Stats NZ, MBIE, MoE, GeoNet)",
        xref="paper", yref="paper", x=0.5, y=-0.16, showarrow=False,
        font=dict(size=12, color=COLORS["muted"]),
    )
    return fig


def map_overview(df, out: Path) -> None:
    """Map-style bubble view (no network/tiles): communities by lon/lat,
    colour = livability, size = population."""
    import math
    # The inner-city suburbs sit on top of each other geographically; skip
    # their labels to keep the image readable (still visible in the live app).
    skip = {"Te Aro", "Thorndon", "Mount Victoria", "Newtown", "Kelburn"}
    d = df.copy()
    d["label"] = d["suburb"].where(~d["suburb"].isin(skip), "")
    fig = px.scatter(
        d, x="lon", y="lat",
        color="livability_score", size="population",
        text="label", color_continuous_scale=["#E76F51", "#E9C46A", "#2A9D8F"],
        size_max=46, hover_name="suburb",
        labels={"livability_score": "Livability"},
    )
    fig.update_traces(textposition="middle right",
                      textfont=dict(size=11, color=COLORS["ink"]),
                      marker=dict(line=dict(width=1.2, color="white")))
    # Aspect correction so the region isn't horizontally squashed.
    lat0 = math.radians(float(df["lat"].mean()))
    fig.update_yaxes(scaleanchor="x", scaleratio=1.0 / math.cos(lat0),
                     showgrid=False, zeroline=False, visible=False)
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    _brand(fig, "Wellington Region communities",
           "Colour = livability score (green better) · circle size = population")
    fig.update_layout(plot_bgcolor="#eaf1f6")
    fig.write_image(str(out), scale=2)


def ranking(df, out: Path) -> None:
    fig = charts.ranking_bar(df)
    _brand(fig, "Livability ranking", "Custom 0–100 index across six weighted pillars")
    fig.update_layout(height=H, width=W, margin=dict(l=140, r=60, t=110, b=120))
    fig.write_image(str(out), scale=2)


def compare(df, out: Path) -> None:
    a, b = data_loader.get_suburb("Petone"), data_loader.get_suburb("Karori")
    fig = charts.comparison_radar([a, b], ["Petone", "Karori"])
    _brand(fig, "Compare communities", "Petone vs Karori across the six livability pillars")
    fig.update_layout(height=H, width=W)
    fig.write_image(str(out), scale=2)


def hazards(out: Path) -> None:
    row = data_loader.get_suburb("Petone")
    fig = charts.hazard_bars(row)
    _brand(fig, "Hazard exposure · Petone",
           "Flood / earthquake / tsunami / landslide exposure (0–100, higher = more)")
    fig.update_layout(height=H, width=W)
    fig.write_image(str(out), scale=2)


def gauge(out: Path) -> None:
    row = data_loader.get_suburb("Paraparaumu")
    score = float(row["livability_score"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 64, "color": COLORS["primary"]}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["good"]},
            "steps": [
                {"range": [0, 30], "color": "#fde8e4"},
                {"range": [30, 45], "color": "#fcf2dd"},
                {"range": [45, 60], "color": "#eef6ec"},
                {"range": [60, 75], "color": "#dcefe9"},
                {"range": [75, 100], "color": "#c9e8df"},
            ],
            "threshold": {"line": {"color": COLORS["primary"], "width": 4},
                          "value": score},
        },
        domain={"x": [0.12, 0.88], "y": [0.0, 0.74]},
    ))
    _brand(fig, "Livability score · Paraparaumu",
           "Region's top-ranked community — 62/100, graded \"Very good\"")
    fig.update_layout(height=H, width=W)
    fig.write_image(str(out), scale=2)


def pillars(df, out: Path) -> None:
    row = data_loader.get_suburb("Karori")
    fig = charts.pillar_bars(pillar_breakdown(row))
    _brand(fig, "Why this score? · Karori",
           "Strong incomes & low tsunami risk, but expensive (Affordability) and low growth")
    fig.update_layout(height=H, width=W, margin=dict(l=160, r=60, t=110, b=120))
    fig.write_image(str(out), scale=2)


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = data_loader.load_suburbs()
    map_overview(df, out_dir / "01_map_overview.png")
    ranking(df, out_dir / "02_livability_ranking.png")
    compare(df, out_dir / "03_compare_petone_karori.png")
    hazards(out_dir / "04_hazards_petone.png")
    gauge(out_dir / "05_livability_gauge.png")
    pillars(df, out_dir / "06_why_this_score_karori.png")
    print(f"Wrote screenshots to {out_dir.resolve()}")
    for p in sorted(out_dir.glob("*.png")):
        print(" ", p.name, f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
