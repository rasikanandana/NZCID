"""Tests for the GeoNet service (no network required)."""

import pandas as pd

from nzcid.services import geonet


def test_haversine_known_distance():
    # Wellington CBD to Lower Hutt is roughly 13-16 km.
    d = geonet.haversine_km(-41.2865, 174.7762, -41.2090, 174.9030)
    assert 10 < d < 20


def test_add_distance_on_empty_frame():
    empty = pd.DataFrame(columns=["lat", "lon", "magnitude"])
    out = geonet.add_distance(empty, -41.0, 174.0)
    assert "distance_km" in out.columns
    assert out.empty


def test_filter_wellington_bbox():
    df = pd.DataFrame({
        "lat": [-41.2, -36.8],   # Wellington, Auckland
        "lon": [174.8, 174.7],
        "magnitude": [3.0, 4.0],
    })
    out = geonet.filter_wellington(df)
    assert len(out) == 1
    assert out.iloc[0]["lat"] == -41.2


def test_add_distance_values():
    df = pd.DataFrame({"lat": [-41.2865], "lon": [174.7762], "magnitude": [3.0]})
    out = geonet.add_distance(df, -41.2865, 174.7762)
    assert out.iloc[0]["distance_km"] == 0.0
