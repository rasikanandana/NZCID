"""Folium map construction with toggleable thematic layers."""

from __future__ import annotations

import branca.colormap as cm
import folium
import pandas as pd

from .. import config
from ..config import COLORS

# Which numeric column drives the colour/size of the suburb circles, and how
# to format it in the tooltip.
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


def _radius(value: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 12.0
    return 8.0 + (value - lo) / (hi - lo) * 18.0


def build_map(
    suburbs: pd.DataFrame,
    theme: str = "Livability score",
    selected: str | None = None,
    schools: pd.DataFrame | None = None,
    hospitals: pd.DataFrame | None = None,
    quakes: pd.DataFrame | None = None,
) -> folium.Map:
    """Build the main interactive map.

    The chosen ``theme`` colours/sizes the suburb circles; schools, hospitals
    and live earthquakes are added as separate toggleable feature groups.
    """
    column, fmt, invert = THEMES.get(theme, THEMES["Livability score"])
    values = suburbs[column]
    lo, hi = float(values.min()), float(values.max())

    # Green→red ramp; inverted for "bad when high" themes like price/hazard.
    palette = ["#2A9D8F", "#E9C46A", "#E76F51"]
    if invert:
        colormap = cm.LinearColormap(palette, vmin=lo, vmax=hi)
    else:
        colormap = cm.LinearColormap(palette[::-1], vmin=lo, vmax=hi)
    colormap.caption = theme

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
            f"Livability: {r['livability_score']:.0f}/100 (rank {int(r['rank'])})"
        )
        folium.CircleMarker(
            location=(r["lat"], r["lon"]),
            radius=_radius(float(r[column]), lo, hi),
            color=COLORS["ink"] if is_sel else colormap(r[column]),
            weight=3 if is_sel else 1,
            fill=True, fill_color=colormap(r[column]),
            fill_opacity=0.85,
            tooltip=folium.Tooltip(tip, sticky=True),
            popup=folium.Popup(f"<b>{r['suburb']}</b>", max_width=200),
        ).add_to(suburb_layer)
    suburb_layer.add_to(fmap)

    if schools is not None and not schools.empty:
        grp = folium.FeatureGroup(name="Schools", show=False)
        for _, s in schools.iterrows():
            folium.Marker(
                location=(s["lat"], s["lon"]),
                icon=folium.Icon(color="darkblue", icon="graduation-cap", prefix="fa"),
                tooltip=f"{s['name']} · {s['type']} · EQI {s['eqi']}",
            ).add_to(grp)
        grp.add_to(fmap)

    if hospitals is not None and not hospitals.empty:
        grp = folium.FeatureGroup(name="Hospitals", show=False)
        for _, h in hospitals.iterrows():
            folium.Marker(
                location=(h["lat"], h["lon"]),
                icon=folium.Icon(color="red", icon="plus-square", prefix="fa"),
                tooltip=f"{h['name']} · {h['type']}",
            ).add_to(grp)
        grp.add_to(fmap)

    if quakes is not None and not quakes.empty:
        grp = folium.FeatureGroup(name="Recent earthquakes (GeoNet)", show=True)
        for _, q in quakes.iterrows():
            mag = q.get("magnitude") or 0
            folium.CircleMarker(
                location=(q["lat"], q["lon"]),
                radius=3 + float(mag) * 2,
                color="#7a0019", fill=True, fill_color=COLORS["danger"],
                fill_opacity=0.5,
                tooltip=(f"M{mag:.1f} · depth {q.get('depth', 0):.0f} km<br>"
                         f"{q.get('locality', '')}"),
            ).add_to(grp)
        grp.add_to(fmap)

    colormap.add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap
