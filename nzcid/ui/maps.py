"""Folium map construction with thematic colouring and point overlays.

Design choices that make the map readable:
  * Circle **size = population** (constant across themes) so a suburb doesn't
    change size when you switch indicator — only its **colour** encodes the
    selected indicator.
  * Schools / hospitals use emoji ``DivIcon`` markers (render everywhere, no
    icon-font dependency) and carry type / EQI in the tooltip.
  * Earthquake markers include date & time (NZ) in the hover tooltip.
"""

from __future__ import annotations

import branca.colormap as cm
import folium
import pandas as pd

from .. import config
from ..config import COLORS

# Which numeric column drives the circle *colour*, and how to format it, and
# whether high values are "bad" (so the colour ramp is inverted).
THEMES = {
    "Livability score": ("livability_score", "{:.0f}/100", False),
    "Median house price": ("median_house_price", "${:,.0f}", True),
    "Median weekly rent": ("median_rent_weekly", "${:,.0f}", True),
    "Population": ("population", "{:,.0f}", False),
    "Population growth %": ("pop_growth_pct", "{:.1f}%", False),
    "Flood exposure": ("flood_exposure", "{:.0f}/100", True),
    "Earthquake exposure": ("earthquake_exposure", "{:.0f}/100", True),
    "Tsunami exposure": ("tsunami_exposure", "{:.0f}/100", True),
}

# School-type → marker tint (just for the tooltip label emphasis).
_SCHOOL_EMOJI = "🏫"
_HOSPITAL_EMOJI = "🏥"


def _radius(value: float, lo: float, hi: float) -> float:
    """Map a value into a 8–26 px circle radius."""
    if hi == lo:
        return 14.0
    return 8.0 + (value - lo) / (hi - lo) * 18.0


def _emoji_marker(lat, lon, emoji, tooltip):
    return folium.Marker(
        location=(lat, lon),
        icon=folium.DivIcon(
            html=(f"<div style='font-size:17px;line-height:17px;"
                  f"text-shadow:0 0 2px #fff,0 0 2px #fff'>{emoji}</div>"),
            icon_size=(18, 18), icon_anchor=(9, 9),
        ),
        tooltip=folium.Tooltip(tooltip, sticky=True),
    )


def build_map(
    suburbs: pd.DataFrame,
    theme: str = "Livability score",
    selected: str | None = None,
    schools: pd.DataFrame | None = None,
    hospitals: pd.DataFrame | None = None,
    quakes: pd.DataFrame | None = None,
    pin: tuple[float, float, str] | None = None,
) -> folium.Map:
    """Build the main interactive map. ``theme`` colours the suburb circles;
    overlays are added only when their DataFrame is supplied."""
    column, fmt, invert = THEMES.get(theme, THEMES["Livability score"])
    values = suburbs[column]
    lo, hi = float(values.min()), float(values.max())

    # Size always encodes population, regardless of the colour theme.
    pop_lo, pop_hi = float(suburbs["population"].min()), float(suburbs["population"].max())

    # Green→amber→red ramp; inverted for "bad when high" themes (price/hazard).
    palette = ["#2A9D8F", "#E9C46A", "#E76F51"]
    colormap = cm.LinearColormap(
        palette if invert else palette[::-1], vmin=lo, vmax=hi)
    colormap.caption = f"{theme}  (circle size = population)"

    fmap = folium.Map(
        location=config.MAP_CENTER, zoom_start=config.MAP_ZOOM,
        tiles="CartoDB positron", control_scale=True,
    )

    suburb_layer = folium.FeatureGroup(name=f"Suburbs · {theme}", show=True)
    for _, r in suburbs.iterrows():
        is_sel = selected == r["suburb"]
        tip = (
            f"<b>{r['suburb']}</b><br>{r['territorial_authority']}<br>"
            f"{theme}: {fmt.format(r[column])}<br>"
            f"Population: {r['population']:,.0f}<br>"
            f"Livability: {r['livability_score']:.0f}/100 (rank {int(r['rank'])})"
        )
        folium.CircleMarker(
            location=(r["lat"], r["lon"]),
            radius=_radius(float(r["population"]), pop_lo, pop_hi),
            color=COLORS["ink"] if is_sel else "#ffffff",
            weight=3 if is_sel else 1,
            fill=True, fill_color=colormap(r[column]),
            fill_opacity=0.88,
            tooltip=folium.Tooltip(tip, sticky=True),
            popup=folium.Popup(f"<b>{r['suburb']}</b>", max_width=200),
        ).add_to(suburb_layer)
    suburb_layer.add_to(fmap)

    if schools is not None and not schools.empty:
        grp = folium.FeatureGroup(name="Schools", show=False)
        for _, s in schools.iterrows():
            roll = f" · roll {int(s['roll'])}" if "roll" in s and pd.notna(s["roll"]) else ""
            _emoji_marker(
                s["lat"], s["lon"], _SCHOOL_EMOJI,
                f"<b>{s['name']}</b><br>{s['type']} · EQI {int(s['eqi'])}{roll}",
            ).add_to(grp)
        grp.add_to(fmap)

    if hospitals is not None and not hospitals.empty:
        grp = folium.FeatureGroup(name="Hospitals", show=False)
        for _, h in hospitals.iterrows():
            _emoji_marker(
                h["lat"], h["lon"], _HOSPITAL_EMOJI,
                f"<b>{h['name']}</b><br>{h['type']}",
            ).add_to(grp)
        grp.add_to(fmap)

    if quakes is not None and not quakes.empty:
        grp = folium.FeatureGroup(name="Recent earthquakes (GeoNet)", show=True)
        for _, q in quakes.iterrows():
            mag = q.get("magnitude") or 0
            when = ""
            t = q.get("time")
            if t is not None and pd.notna(t):
                # GeoNet times are UTC; show local NZ time for readability.
                try:
                    nz = t.tz_convert("Pacific/Auckland")
                    when = f"<br>{nz:%d %b %Y, %I:%M %p} NZ"
                except Exception:
                    when = f"<br>{t:%d %b %Y %H:%M} UTC"
            folium.CircleMarker(
                location=(q["lat"], q["lon"]),
                radius=3 + float(mag) * 2,
                color="#7a0019", fill=True, fill_color=COLORS["danger"],
                fill_opacity=0.5,
                tooltip=folium.Tooltip(
                    f"<b>M{mag:.1f}</b> · depth {q.get('depth', 0):.0f} km"
                    f"<br>{q.get('locality', '')}{when}", sticky=True),
            ).add_to(grp)
        grp.add_to(fmap)

    if pin is not None:
        plat, plon, plabel = pin
        folium.Marker(
            location=(plat, plon),
            icon=folium.DivIcon(
                html="<div style='font-size:24px;line-height:24px'>📍</div>",
                icon_size=(24, 24), icon_anchor=(12, 24)),
            tooltip=folium.Tooltip(f"📍 {plabel}", sticky=True),
        ).add_to(fmap)

    colormap.add_to(fmap)
    # Overlays are toggled from the app's button bar, so no LayerControl here.
    return fmap
