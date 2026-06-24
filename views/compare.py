"""Side-by-side comparison of two communities."""

import pandas as pd
import streamlit as st

from nzcid import data_loader
from nzcid.ui import charts, common

# (label, column, format, lower_is_better)
COMPARE_ROWS = [
    ("Median house price", "median_house_price", "${:,.0f}", True),
    ("Median weekly rent", "median_rent_weekly", "${:,.0f}", True),
    ("House price trend", "house_price_trend_pct", "{:+.1f}%", None),
    ("Population", "population", "{:,.0f}", None),
    ("Population growth", "pop_growth_pct", "{:+.1f}%", False),
    ("Median age", "median_age", "{:.0f} yrs", None),
    ("Median household income", "median_household_income", "${:,.0f}", False),
    ("Employment rate", "employment_rate", "{:.0f}%", False),
    ("Schools nearby", "schools_count", "{:.0f}", False),
    ("Hospitals ≤10 km", "hospitals_within_10km", "{:.0f}", False),
    ("Transport score", "transport_score", "{:.0f}/100", False),
    ("Walkability", "walkability_score", "{:.0f}/100", False),
    ("Sunshine hours", "sunshine_hours", "{:,.0f}", False),
    ("Flood exposure", "flood_exposure", "{:.0f}/100", True),
    ("Earthquake exposure", "earthquake_exposure", "{:.0f}/100", True),
    ("Tsunami exposure", "tsunami_exposure", "{:.0f}/100", True),
    ("Livability score", "livability_score", "{:.1f}/100", False),
]


def _winner(a: float, b: float, lower_is_better) -> str:
    if lower_is_better is None or a == b:
        return "tie"
    if lower_is_better:
        return "a" if a < b else "b"
    return "a" if a > b else "b"


common.hero("Compare communities",
            "Put two Wellington communities head-to-head.")

names = data_loader.suburb_names()
focus = common.get_focus(names)
c1, c2 = st.columns(2)
a_name = c1.selectbox("Community A", names, index=names.index(focus))
default_b = "Johnsonville" if "Johnsonville" in names else names[
    1 if names[0] == a_name else 0]
b_name = c2.selectbox("Community B", names, index=names.index(default_b))
common.data_disclaimer()

if a_name == b_name:
    st.warning("Pick two different communities to compare.")
    st.stop()

a = data_loader.get_suburb(a_name)
b = data_loader.get_suburb(b_name)

h1, h2 = st.columns(2)
for col, row in ((h1, a), (h2, b)):
    col.metric(row["suburb"], f"{row['livability_score']:.1f}/100",
               f"Rank {int(row['rank'])}")
    col.markdown(common.grade_pill(row["livability_score"]),
                 unsafe_allow_html=True)

st.markdown("#### Pillar comparison")
st.plotly_chart(charts.comparison_radar([a, b], [a_name, b_name]),
                width="stretch")

st.markdown("#### Indicator-by-indicator")
records = []
for label, col, fmt, lib in COMPARE_ROWS:
    av, bv = float(a[col]), float(b[col])
    win = _winner(av, bv, lib)
    records.append({
        "Indicator": label,
        a_name: ("✅ " if win == "a" else "") + fmt.format(av),
        b_name: ("✅ " if win == "b" else "") + fmt.format(bv),
    })
table = pd.DataFrame(records).set_index("Indicator")
st.dataframe(table, width="stretch", height=640)

a_wins = sum(_winner(float(a[c]), float(b[c]), lib) == "a"
             for _, c, _, lib in COMPARE_ROWS if lib is not None)
b_wins = sum(_winner(float(a[c]), float(b[c]), lib) == "b"
             for _, c, _, lib in COMPARE_ROWS if lib is not None)
st.info(f"On directional indicators, **{a_name}** leads on {a_wins} and "
        f"**{b_name}** leads on {b_wins}. ✅ marks the stronger value per row.")
