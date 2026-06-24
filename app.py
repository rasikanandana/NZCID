"""NZ Community Insights Dashboard — application entry point.

Uses ``st.navigation`` (the modern multipage API) so navigation is explicit and
robust. Each page lives in ``views/``. Run with:  ``streamlit run app.py``
"""

import streamlit as st

from nzcid import data_loader
from nzcid.ui import common

# Must be the first Streamlit call (also injects the theme CSS).
common.configure()

# Seed the shared focus suburb so every page agrees on a default.
common.get_focus(data_loader.suburb_names())

# ---- Pages ---------------------------------------------------------------- #
PAGES = [
    st.Page("views/explore.py", title="Explore map", icon="🗺️", default=True),
    st.Page("views/profile.py", title="Community profile", icon="🏘️"),
    st.Page("views/compare.py", title="Compare", icon="⚖️"),
    st.Page("views/hazards.py", title="Hazards", icon="⚠️"),
    st.Page("views/demographics.py", title="Demographics", icon="👥"),
    st.Page("views/about.py", title="About", icon="ℹ️"),
]
# Registry used by common.page_link() for robust cross-page links.
st.session_state["_pages"] = {p.title: p for p in PAGES}

# ---- Sidebar branding ----------------------------------------------------- #
with st.sidebar:
    st.markdown("## 🗺️ NZ Community Insights")
    st.caption("Wellington Region · MVP")
    st.caption("  © Rasika Nandana rasikanandana@gmail.com")
    st.divider()

st.navigation(PAGES).run()
