"""Explore map — the redesigned home view.

UX goals:
  * Button-style controls (segmented control + pills) instead of buried
    dropdowns/checkboxes.
  * Click a suburb on the map to focus it; the snapshot panel updates live.
  * The focus suburb is shared across every page via session state.
"""

import streamlit as st
from streamlit_folium import st_folium

from nzcid import data_loader
from nzcid.services import geonet
from nzcid.ui import charts, common, maps

# Friendly labels for the overlay buttons -> internal flags.
OVERLAYS = {"🏫 Schools": "schools", "🏥 Hospitals": "hospitals",
            "🌐 Earthquakes": "quakes"}


@st.cache_data(ttl=600, show_spinner=False)
def _quakes():
    """Live GeoNet quakes (Wellington), cached for 10 minutes."""
    return geonet.filter_wellington(geonet.fetch_recent_quakes(mmi=3))


def render() -> None:
    suburbs = data_loader.load_suburbs()
    schools = data_loader.load_schools()
    hospitals = data_loader.load_hospitals()

    common.hero(
        "Explore Wellington communities",
        "Choose what the map shows, click a suburb to focus it, and read its "
        "livability snapshot on the right.",
    )

    # ---------- Control bar (buttons, not dropdowns) ----------------------- #
    c1, c2 = st.columns([3, 2])
    with c1:
        indicator = st.segmented_control(
            "🎨 Colour the map by",
            options=list(maps.THEMES.keys()),
            default="Livability score",
            key="map_indicator",
        ) or "Livability score"
    with c2:
        chosen = st.pills(
            "👁️ Show on map",
            options=list(OVERLAYS.keys()),
            selection_mode="multi",
            default=["🌐 Earthquakes"],
            key="map_overlays",
        ) or []
    flags = {OVERLAYS[o] for o in chosen}

    f1, f2 = st.columns([1, 1])
    tas = ["All councils"] + sorted(suburbs["territorial_authority"].unique())
    ta = f1.selectbox("🏛️ Filter by council", tas)
    view = (suburbs if ta == "All councils"
            else suburbs[suburbs["territorial_authority"] == ta])
    if view.empty:
        view = suburbs
    focus = common.focus_picker(view["suburb"].tolist(), location=f2)

    quakes = _quakes() if "quakes" in flags else None
    st.caption("💡 Tip: click any suburb circle on the map to focus it. "
               "Larger / greener circles score better on the selected indicator.")

    # ---------- Map (centre) + snapshot (right) ---------------------------- #
    map_col, info_col = st.columns([2.3, 1])

    with map_col:
        fmap = maps.build_map(
            view, theme=indicator, selected=focus,
            schools=schools if "schools" in flags else None,
            hospitals=hospitals if "hospitals" in flags else None,
            quakes=quakes,
        )
        state = st_folium(
            fmap, key="explore_map", height=560,
            use_container_width=True,  # st_folium's own param (pixels or full width)
            returned_objects=["last_object_clicked"],
        )
        clicked = (state or {}).get("last_object_clicked")
        if clicked and clicked.get("lat") is not None:
            near = data_loader.nearest_suburb(clicked["lat"], clicked["lng"])
            if near in set(view["suburb"]) and near != focus:
                common.set_focus(near)
                st.rerun()

    with info_col:
        row = data_loader.get_suburb(focus)
        st.markdown(f"#### {focus}")
        st.markdown(common.grade_pill(row["livability_score"]),
                    unsafe_allow_html=True)
        st.caption(f"{row['territorial_authority']} · regional rank "
                   f"{int(row['rank'])} of {len(suburbs)}")
        st.plotly_chart(
            charts.livability_gauge(row["livability_score"]),
            width="stretch", config={"displayModeBar": False},
        )
        a, b = st.columns(2)
        a.markdown(common.metric_card(
            "House price", f"${row['median_house_price']:,.0f}",
            f"{row['house_price_trend_pct']:+.1f}%/yr",
            row["house_price_trend_pct"] < 0), unsafe_allow_html=True)
        b.markdown(common.metric_card(
            "Weekly rent", f"${row['median_rent_weekly']:,.0f}",
            f"{row['rent_trend_pct']:+.1f}%/yr",
            row["rent_trend_pct"] < 0), unsafe_allow_html=True)
        st.write("")
        common.page_link("Community profile", "Full profile", icon="🏘️")
        common.page_link("Compare", "Compare with another suburb", icon="⚖️")
        common.page_link("Hazards", "Hazard detail", icon="⚠️")

    # ---------- Region ranking -------------------------------------------- #
    st.markdown("#### Regional livability ranking")
    st.plotly_chart(charts.ranking_bar(suburbs, highlight=focus),
                    width="stretch")
    common.data_disclaimer()


render()
