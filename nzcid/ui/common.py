"""Streamlit presentation helpers shared by every view.

With ``st.navigation`` the entry script (``app.py``) owns ``set_page_config``
and the CSS injection, so views only render content. Suburb selection is held
in ``st.session_state['focus_suburb']`` so a pick on one page follows the user
to the next.
"""

from __future__ import annotations

import streamlit as st

from .. import config
from ..config import COLORS

FOCUS_KEY = "focus_suburb"


def configure() -> None:
    """Page config + theme CSS. Call once, from the entry script."""
    st.set_page_config(
        page_title="NZ Community Insights Dashboard",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_css()


def _inject_css() -> None:
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {COLORS['bg']}; }}
          h1, h2, h3 {{ color: {COLORS['primary']}; }}
          /* Slim hero banner */
          .nzcid-hero {{
              background: linear-gradient(110deg, {COLORS['primary']}, {COLORS['secondary']});
              color: white; padding: 0.9rem 1.3rem; border-radius: 12px;
              margin-bottom: 0.8rem;
          }}
          .nzcid-hero h1 {{ color: white; margin: 0; font-size: 1.45rem; }}
          .nzcid-hero p {{ color: #e8f3f1; margin: 0.2rem 0 0; font-size: 0.92rem; }}
          /* Metric cards */
          .nzcid-card {{
              background: white; border: 1px solid #e5e9f0; border-radius: 10px;
              padding: 0.7rem 0.9rem; height: 100%;
          }}
          .nzcid-card .label {{ color: {COLORS['muted']}; font-size: 0.72rem;
              text-transform: uppercase; letter-spacing: 0.03em; }}
          .nzcid-card .value {{ color: {COLORS['ink']}; font-size: 1.3rem;
              font-weight: 700; line-height: 1.15; }}
          .nzcid-card .delta-up {{ color: {COLORS['danger']}; font-size: 0.78rem; }}
          .nzcid-card .delta-down {{ color: {COLORS['good']}; font-size: 0.78rem; }}
          .nzcid-pill {{ display:inline-block; padding: 0.15rem 0.65rem;
              border-radius: 999px; font-size: 0.82rem; font-weight:600; }}
          section[data-testid="stSidebar"] {{ background: #ffffff; }}
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
    """HTML for a compact metric card (render inside ``st.markdown``)."""
    delta_html = ""
    if delta is not None:
        cls = "delta-down" if delta_good_when_down else "delta-up"
        delta_html = f"<div class='{cls}'>{delta}</div>"
    return (
        f"<div class='nzcid-card'><div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>{delta_html}</div>"
    )


def grade_pill(score: float) -> str:
    color = (COLORS["good"] if score >= 60 else
             COLORS["warn"] if score >= 45 else COLORS["bad"])
    label = config.livability_grade(score)
    return (
        f"<span class='nzcid-pill' style='background:{color}1a;color:{color}'>"
        f"{label} · {score:.0f}/100</span>"
    )


def get_focus(names: list[str]) -> str:
    """Current focus suburb from session state (defaults to the first name)."""
    cur = st.session_state.get(FOCUS_KEY)
    if cur not in names:
        cur = names[0]
        st.session_state[FOCUS_KEY] = cur
    return cur


def set_focus(name: str) -> None:
    st.session_state[FOCUS_KEY] = name


def focus_picker(names: list[str], label: str = "🎯 Focus community",
                 location=None) -> str:
    """A selectbox bound to the shared focus-suburb state.

    ``location`` is a Streamlit container (e.g. ``st.sidebar``); defaults to
    the current context. No widget ``key`` is used so the options list can
    change (e.g. when a council filter is applied) without stale-state errors.
    """
    target = location or st
    current = get_focus(names)
    choice = target.selectbox(label, names, index=names.index(current))
    if choice != st.session_state.get(FOCUS_KEY):
        set_focus(choice)
    return choice


def page_link(title: str, label: str, icon: str | None = None) -> None:
    """Cross-page link by registered title (robust under ``st.navigation``).

    Looks the page up from the registry the entry script stashes in
    ``st.session_state['_pages']`` and links to the page *object* (avoids the
    path-string lookup bug seen on some Streamlit builds).
    """
    page = st.session_state.get("_pages", {}).get(title)
    if page is not None:
        st.page_link(page, label=label, icon=icon)


def data_disclaimer() -> None:
    st.caption(
        "ℹ️ MVP dataset for the Wellington Region. Indicators are curated and "
        "indicative (Stats NZ, MBIE/Tenancy Services, Ministry of Education "
        "Equity Index, GeoNet, regional hazard portals). Earthquake data is "
        "live from GeoNet. Not for operational or emergency-management use."
    )
