"""Streamlit presentation helpers shared by every page."""

from __future__ import annotations

import streamlit as st

from .. import config
from ..config import COLORS


def page_setup(title: str, icon: str = "🗺️") -> None:
    """Standard ``set_page_config`` + injected CSS theme. Call first on a page."""
    st.set_page_config(
        page_title=f"{title} · NZCID",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {COLORS['bg']}; }}
          h1, h2, h3 {{ color: {COLORS['primary']}; }}
          .nzcid-hero {{
              background: linear-gradient(110deg, {COLORS['primary']}, {COLORS['secondary']});
              color: white; padding: 1.1rem 1.4rem; border-radius: 12px;
              margin-bottom: 0.6rem;
          }}
          .nzcid-hero h1 {{ color: white; margin: 0; font-size: 1.6rem; }}
          .nzcid-hero p {{ color: #e8f3f1; margin: 0.25rem 0 0; font-size: 0.95rem; }}
          .nzcid-card {{
              background: white; border: 1px solid #e5e9f0; border-radius: 10px;
              padding: 0.75rem 0.9rem; height: 100%;
          }}
          .nzcid-card .label {{ color: {COLORS['muted']}; font-size: 0.78rem;
              text-transform: uppercase; letter-spacing: 0.03em; }}
          .nzcid-card .value {{ color: {COLORS['ink']}; font-size: 1.35rem;
              font-weight: 700; }}
          .nzcid-card .delta-up {{ color: {COLORS['danger']}; font-size: 0.8rem; }}
          .nzcid-card .delta-down {{ color: {COLORS['good']}; font-size: 0.8rem; }}
          .nzcid-pill {{ display:inline-block; padding: 0.15rem 0.6rem;
              border-radius: 999px; font-size: 0.8rem; font-weight:600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='nzcid-hero'><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str | None = None,
                delta_good_when_down: bool = True) -> str:
    """Return HTML for a compact metric card (use inside ``st.markdown``)."""
    delta_html = ""
    if delta is not None:
        cls = "delta-down" if delta_good_when_down else "delta-up"
        delta_html = f"<div class='{cls}'>{delta}</div>"
    return (
        f"<div class='nzcid-card'><div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>{delta_html}</div>"
    )


def grade_pill(score: float) -> str:
    color = (
        COLORS["good"] if score >= 60 else
        COLORS["warn"] if score >= 45 else COLORS["bad"]
    )
    label = config.livability_grade(score)
    return (
        f"<span class='nzcid-pill' style='background:{color}1a;color:{color}'>"
        f"{label} · {score:.0f}/100</span>"
    )


def sidebar_suburb_picker(names: list[str], key: str = "suburb",
                          label: str = "Select a community") -> str:
    """Sidebar suburb selector that remembers the last choice via session state."""
    default = st.session_state.get(key, names[0])
    if default not in names:
        default = names[0]
    return st.sidebar.selectbox(label, names, index=names.index(default), key=key)


def data_disclaimer() -> None:
    st.caption(
        "ℹ️ MVP dataset for the Wellington Region. Indicators are curated and "
        "indicative (from publicly reported ranges: Stats NZ, MBIE/Tenancy "
        "Services, Ministry of Education Equity Index, GeoNet, regional hazard "
        "portals). Earthquake data is live from GeoNet. Not for operational or "
        "emergency-management use."
    )
