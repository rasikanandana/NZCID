"""Hazard analysis: live GeoNet earthquakes + exposure indices."""

import streamlit as st

from nzcid import data_loader
from nzcid.config import COLORS, HAZARD_COLUMNS
from nzcid.services import geonet
from nzcid.ui import charts, common


@st.cache_data(ttl=600, show_spinner="Fetching live GeoNet feed…")
def _quakes(mmi: int):
    return geonet.filter_wellington(geonet.fetch_recent_quakes(mmi=mmi))


common.hero("Hazard analysis",
            "Live earthquakes from GeoNet plus flood, tsunami and landslide "
            "exposure indices.")

names = data_loader.suburb_names()
selected = common.focus_picker(names, location=st.sidebar)
mmi = st.sidebar.slider("Min. earthquake intensity (MMI)", -1, 6, 3)
common.data_disclaimer()

row = data_loader.get_suburb(selected)

# ----- Exposure indices ---------------------------------------------------- #
st.markdown(f"### Exposure profile · {selected}")
cols = st.columns(4)
for col, (key, label) in zip(cols, HAZARD_COLUMNS.items()):
    v = float(row[key])
    band = "High" if v >= 60 else "Moderate" if v >= 35 else "Low"
    color = (COLORS["bad"] if v >= 60 else
             COLORS["warn"] if v >= 35 else COLORS["good"])
    col.markdown(
        f"<div class='nzcid-card'><div class='label'>{label}</div>"
        f"<div class='value' style='color:{color}'>{v:.0f}<span "
        f"style='font-size:0.8rem'>/100</span></div>"
        f"<div class='label' style='color:{color}'>{band}</div></div>",
        unsafe_allow_html=True)
st.plotly_chart(charts.hazard_bars(row), width="stretch")

# ----- Live earthquakes ---------------------------------------------------- #
st.markdown("### 🌐 Recent earthquakes (GeoNet, live)")
quakes = geonet.add_distance(_quakes(mmi), row["lat"], row["lon"])

if quakes.empty:
    st.info("No earthquakes in the Wellington Region matched your filter "
            "(or the GeoNet feed is unreachable right now).")
else:
    quakes = quakes.sort_values("time", ascending=False)
    m1, m2, m3 = st.columns(3)
    m1.metric("Quakes shown", len(quakes))
    m2.metric("Strongest", f"M{quakes['magnitude'].max():.1f}")
    nearest = quakes.loc[quakes["distance_km"].idxmin()]
    m3.metric(f"Nearest to {selected}",
              f"{nearest['distance_km']:.0f} km",
              f"M{nearest['magnitude']:.1f}")

    display = quakes.assign(
        When=quakes["time"].apply(geonet.hours_ago),
        Magnitude=quakes["magnitude"].round(1),
        **{"Depth (km)": quakes["depth"].round(0),
           "Distance (km)": quakes["distance_km"]},
    )[["When", "Magnitude", "Depth (km)", "Distance (km)", "locality"]]
    display = display.rename(columns={"locality": "Locality"})
    st.dataframe(display, width="stretch", hide_index=True)
    st.caption("Source: GeoNet (api.geonet.org.nz). Distances measured "
               f"from {selected}.")

st.markdown("---")
st.caption("Flood, tsunami and landslide indices are indicative MVP "
           "composites. For authoritative hazard information consult Greater "
           "Wellington Regional Council and NEMA.")
