"""Population & demographics module."""

import plotly.express as px
import streamlit as st

from nzcid import data_loader
from nzcid.config import COLORS
from nzcid.ui import charts, common


def main() -> None:
    common.page_setup("Demographics", icon="👥")
    common.hero("Population & demographics",
                "Population structure and how communities compare across "
                "the region.")

    names = data_loader.suburb_names()
    selected = common.sidebar_suburb_picker(names)
    common.data_disclaimer()

    row = data_loader.get_suburb(selected)
    suburbs = data_loader.load_suburbs()

    c = st.columns(4)
    facts = [
        ("Population", f"{row['population']:,.0f}"),
        ("Growth (yr)", f"{row['pop_growth_pct']:+.1f}%"),
        ("Median age", f"{row['median_age']:.0f}"),
        ("Median income", f"${row['median_household_income']:,.0f}"),
    ]
    for col, (lbl, val) in zip(c, facts):
        col.markdown(common.metric_card(lbl, val), unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(f"##### Age structure · {selected}")
        st.plotly_chart(charts.population_pyramid(row),
                        use_container_width=True)
        st.caption("Age/sex distribution is modelled from population and "
                   "median age (single-year tables not in MVP).")
    with right:
        st.markdown("##### Population vs. growth across the region")
        fig = px.scatter(
            suburbs, x="population", y="pop_growth_pct",
            size="median_household_income", color="median_age",
            hover_name="suburb", color_continuous_scale="Viridis",
            labels={"population": "Population",
                    "pop_growth_pct": "Annual growth (%)",
                    "median_age": "Median age"},
        )
        fig.add_hline(y=suburbs["pop_growth_pct"].mean(),
                      line_dash="dot", line_color=COLORS["muted"],
                      annotation_text="region avg")
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
        # Highlight the selected suburb.
        sel = suburbs[suburbs["suburb"] == selected]
        fig.add_scatter(x=sel["population"], y=sel["pop_growth_pct"],
                        mode="markers+text", text=sel["suburb"],
                        textposition="top center",
                        marker=dict(size=16, color=COLORS["danger"],
                                    line=dict(width=2, color="white")),
                        showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Median household income by community")
    inc = suburbs.sort_values("median_household_income", ascending=True)
    bar = px.bar(inc, x="median_household_income", y="suburb",
                 orientation="h", labels={"median_household_income": "Income ($)",
                                          "suburb": ""})
    bar.update_traces(marker_color=COLORS["secondary"])
    bar.update_layout(height=max(320, 24 * len(inc)),
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(bar, use_container_width=True)


if __name__ == "__main__":
    main()
