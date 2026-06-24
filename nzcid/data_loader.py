"""Load and cache the bundled Wellington Region datasets.

Data here is a curated, representative MVP dataset assembled for portfolio
purposes. Values are indicative and drawn from publicly reported ranges
(Stats NZ, MBIE/Tenancy Services bond data, GeoNet, Ministry of Education
Equity Index, regional council hazard portals). They are NOT an official
source of truth — see README for the data-provenance notes.
"""

from __future__ import annotations

import functools

import pandas as pd

from . import config


# ``functools.lru_cache`` keeps the CSVs in memory for the life of the
# process. Streamlit re-runs the script on every interaction, so without
# caching we would re-read the files constantly.
@functools.lru_cache(maxsize=1)
def load_suburbs() -> pd.DataFrame:
    """Return the suburb indicator table with the livability score attached."""
    from .livability import add_livability  # local import avoids a cycle

    df = pd.read_csv(config.SUBURBS_CSV)
    df = df.sort_values("suburb").reset_index(drop=True)
    return add_livability(df)


@functools.lru_cache(maxsize=1)
def load_schools() -> pd.DataFrame:
    return pd.read_csv(config.SCHOOLS_CSV)


@functools.lru_cache(maxsize=1)
def load_hospitals() -> pd.DataFrame:
    return pd.read_csv(config.HOSPITALS_CSV)


def suburb_names() -> list[str]:
    return load_suburbs()["suburb"].tolist()


def get_suburb(name: str) -> pd.Series:
    """Return a single suburb row as a Series (raises if not found)."""
    df = load_suburbs()
    match = df[df["suburb"] == name]
    if match.empty:
        raise KeyError(f"Unknown suburb: {name!r}")
    return match.iloc[0]
