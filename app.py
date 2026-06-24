"""NZ Community Insights Dashboard — home page (map + region overview).

Run locally with:  streamlit run app.py
"""

import _bootstrap  # noqa: F401  (adds ./src to sys.path)

import streamlit as st
from streamlit_folium import st_folium

from nzcid import config, data_loader
from nzcid.services import geonet
from nzcid.ui import charts, common, maps


@st.cache_data(ttl=600, show_spinner=False)
def _load_quakes():
    """Cache the live GeoNet feed for 10 minutes (filtered to Wellington)."""
    df = geonet.fetch_recent_quakes(mmi=3)
    return geonet.filter_wellington(df)


def main() -> None:
    common.page_setup("Home", icon="🗺️")
    common.hero(config.APP_NAME, config.APP_TAGLINE)

    suburbs = data_loader.load_suburbs()
    schools = data_loader.load_schools()
    hospitals = data_loader.load_hospitals()

    # ----- Left panel: filters --------------------------------------------- #
    st.sidebar.header("Filters")
    tas = ["All"] + sorted(suburbs["territorial_authority"].unique().tolist())
    ta = st.sidebar.selectbox("Territorial authority", tas)
    view = suburbs if ta == "All" else suburbs[suburbs["territorial_authority"] == ta]

    theme = st.sidebar.selectbox("Map theme", list(maps.THEMES.keys()))
    show_schools = st.sidebar.checkbox("Show schools", value=False)
    show_hospitals = st.sidebar.checkbox("Show hospitals", value=False)
    show_quakes = st.sidebar.checkbox("Show live earthquakes (GeoNet)", value=True)
    selected = common.sidebar_suburb_picker(
        view["suburb"].tolist(), label="Focus community"
    )
    common.data_disclaimer()

    quakes = _load_quakes() if show_quakes else None

    # ----- Region headline metrics ----------------------------------------- #
    c1, c2, c3, c4 = st.columns(4)
    most = suburbs.loc[suburbs["livability_score"].idxmax()]
    afford = suburbs.loc[suburbs["median_house_price"].idxmin()]
    cards = [
        ("Communities", f"{len(suburbs)}", None),
        ("Most livable", f"{most['suburb']}", f"{most['livability_score']:.0f}/100"),
        ("Most affordable", f"{afford['suburb']}",
         f"${afford['median_house_price']:,.0f}"),
        ("Live quakes (region)",
         f"{0 if quakes is None else len(quakes)}", "GeoNet · MMI ≥ 3"),
    ]
    for col, (lbl, val, sub) in zip([c1, c2, c3, c4], cards):
        sub_html = f"<div class='label'>{sub}</div>" if sub else ""
        col.markdown(
            f"<div class='nzcid-card'><div class='label'>{lbl}</div>"
            f"<div class='value'>{val}</div>{sub_html}</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # ----- Centre: map  +  Right: focus snapshot --------------------------- #
    map_col, info_col = st.columns([2.2, 1])

    with map_col:
        fmap = maps.build_map(
            view, theme=theme, selected=selected,
            schools=schools if show_schools else None,
            hospitals=hospitals if show_hospitals else None,
            quakes=quakes,
        )
        st_folium(fmap, height=560, use_container_width=True,
                  returned_objects=[])

    with info_col:
        row = data_loader.get_suburb(selected)
        st.subheader(selected)
        st.markdown(common.grade_pill(row["livability_score"]),
                    unsafe_allow_html=True)
        st.caption(f"{row['territorial_authority']} · "
                   f"Regional rank {int(row['rank'])} of {len(suburbs)}")
        st.plotly_chart(
            charts.livability_gauge(row["livability_score"]),
            use_container_width=True, config={"displayModeBar": False},
        )
        a, b = st.columns(2)
        a.markdown(common.metric_card(
            "Median house price", f"${row['median_house_price']:,.0f}",
            f"{row['house_price_trend_pct']:+.1f}% yr",
            row["house_price_trend_pct"] < 0), unsafe_allow_html=True)
        b.markdown(common.metric_card(
            "Median weekly rent", f"${row['median_rent_weekly']:,.0f}",
            f"{row['rent_trend_pct']:+.1f}% yr",
            row["rent_trend_pct"] < 0), unsafe_allow_html=True)
        st.page_link("pages/1_Community_Profile.py",
                     label="→ Full community profile", icon="🏘️")
        st.page_link("pages/2_Compare.py", label="→ Compare communities",
                     icon="⚖️")

    st.write("")
    st.subheader("Regional livability ranking")
    st.plotly_chart(charts.ranking_bar(suburbs, highlight=selected),
                    use_container_width=True)


if __name__ == "__main__":
    main()
