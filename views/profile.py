"""Detailed single-community profile."""

import streamlit as st

from nzcid import data_loader
from nzcid.livability import pillar_breakdown
from nzcid.ui import charts, common

names = data_loader.suburb_names()
selected = common.focus_picker(names, location=st.sidebar)
common.data_disclaimer()

row = data_loader.get_suburb(selected)
suburbs = data_loader.load_suburbs()

common.hero(selected, f"{row['territorial_authority']} · Wellington Region")

top = st.columns([1, 2])
with top[0]:
    st.plotly_chart(charts.livability_gauge(row["livability_score"]),
                    width="stretch", config={"displayModeBar": False})
    st.markdown(common.grade_pill(row["livability_score"]),
                unsafe_allow_html=True)
    st.caption(f"Regional rank {int(row['rank'])} of {len(suburbs)}")
with top[1]:
    st.markdown("##### Livability pillar breakdown")
    st.plotly_chart(charts.pillar_bars(pillar_breakdown(row)),
                    width="stretch")

# ----- Housing ------------------------------------------------------------- #
st.markdown("### 🏠 Housing")
h = st.columns(2)
h[0].plotly_chart(
    charts.trend_line("Median house price (indicative)",
                      float(row["median_house_price"]),
                      float(row["house_price_trend_pct"])),
    width="stretch")
h[1].plotly_chart(
    charts.trend_line("Median weekly rent (indicative)",
                      float(row["median_rent_weekly"]),
                      float(row["rent_trend_pct"]), prefix="$"),
    width="stretch")

# ----- Population & economy ------------------------------------------------ #
st.markdown("### 👥 Population & economy")
cols = st.columns(4)
facts = [
    ("Population", f"{row['population']:,.0f}", None, True),
    ("Population growth", f"{row['pop_growth_pct']:+.1f}%", None, False),
    ("Median age", f"{row['median_age']:.0f} yrs", None, True),
    ("Median household income", f"${row['median_household_income']:,.0f}",
     None, False),
]
for col, (lbl, val, d, dn) in zip(cols, facts):
    col.markdown(common.metric_card(lbl, val, d, dn), unsafe_allow_html=True)

# ----- Accessibility ------------------------------------------------------- #
st.markdown("### 🚌 Accessibility")
cols = st.columns(4)
acc = [
    ("Schools nearby", f"{row['schools_count']:.0f}"),
    ("Avg school EQI", f"{row['avg_school_eqi']:.0f}"),
    ("Hospitals ≤10 km", f"{row['hospitals_within_10km']:.0f}"),
    ("Transport score", f"{row['transport_score']:.0f}/100"),
]
for col, (lbl, val) in zip(cols, acc):
    col.markdown(common.metric_card(lbl, val), unsafe_allow_html=True)
st.caption("Equity Index (EQI): lower numbers indicate less socio-economic "
           "barrier to achievement.")

# ----- Climate ------------------------------------------------------------- #
st.markdown("### 🌤️ Climate")
cols = st.columns(3)
clim = [
    ("Avg temperature", f"{row['avg_temp_c']:.1f} °C"),
    ("Annual rainfall", f"{row['annual_rainfall_mm']:,.0f} mm"),
    ("Sunshine hours", f"{row['sunshine_hours']:,.0f} hrs/yr"),
]
for col, (lbl, val) in zip(cols, clim):
    col.markdown(common.metric_card(lbl, val), unsafe_allow_html=True)

# ----- Hazards summary ----------------------------------------------------- #
st.markdown("### ⚠️ Hazard exposure")
st.plotly_chart(charts.hazard_bars(row), width="stretch")
common.page_link("Hazards", "Detailed hazard analysis", icon="⚠️")
