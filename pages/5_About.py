"""About / methodology page."""

import pandas as pd
import streamlit as st

from nzcid import __version__
from nzcid.config import PILLARS
from nzcid.ui import common


def main() -> None:
    common.page_setup("About", icon="ℹ️")
    common.hero("About this dashboard",
                "Methodology, data sources and roadmap.")

    st.markdown(f"""
**NZ Community Insights Dashboard** helps New Zealanders compare communities
on affordability, livability, accessibility and natural-hazard exposure.

This is an **MVP scoped to the Wellington Region** ({pd_count()} communities),
built as a portfolio piece to demonstrate GIS/geospatial analytics, dashboard
development, data engineering and hazard-resilience analysis. Version `{__version__}`.
""")

    st.markdown("### Livability index methodology")
    st.markdown("""
Each community is scored **0–100**. Every input metric is min-max normalised
across the region (so scores are *relative* within Wellington), with the
direction flipped for "lower is better" metrics such as price and hazard
exposure. Pillar scores are the mean of their metrics; the overall score is
the weighted sum of the six pillars below.
""")
    weights = pd.DataFrame([
        {"Pillar": p.label, "Weight": f"{p.weight:.0%}",
         "Built from": p.description} for p in PILLARS
    ]).set_index("Pillar")
    st.dataframe(weights, use_container_width=True)

    st.markdown("### Data sources")
    st.markdown("""
| Domain | Intended source | Status in MVP |
|---|---|---|
| Earthquakes | GeoNet quake API | **Live** |
| Housing (prices, rent) | Stats NZ, MBIE / Tenancy Services bond data | Curated sample |
| Population & income | Stats NZ (Census, Datafinder) | Curated sample |
| Schools & EQI | Ministry of Education | Curated sample |
| Hospitals | Health NZ / Te Whatu Ora | Curated sample |
| Hazards (flood/tsunami/landslide) | LINZ, GWRC, NZ SeaRise | Indicative composite |
| Weather/climate | NIWA, MetService | Curated averages |

Curated values are indicative and drawn from publicly reported ranges. They
are **not an official source** and must not be used for property, financial or
emergency-management decisions.
""")

    st.markdown("### Roadmap")
    st.markdown("""
1. **Now (MVP):** Wellington Region, curated indicators, live GeoNet feed,
   livability index, profiles, comparison, hazards, demographics.
2. **Next:** wire live Stats NZ / MBIE APIs, real suburb boundary polygons
   (choropleths), GTFS transit travel-times, NIWA climate.
3. **Later:** nationwide coverage, PostgreSQL + PostGIS backend, user accounts
   and saved comparisons.
""")
    common.data_disclaimer()


def pd_count() -> int:
    from nzcid import data_loader
    return len(data_loader.suburb_names())


if __name__ == "__main__":
    main()
