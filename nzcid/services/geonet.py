"""GeoNet earthquake feed integration.

GeoNet (https://www.geonet.org.nz) publishes a public, key-free GeoJSON
quake feed. We fetch it live, fall back gracefully to an empty result if
the network is unavailable, and expose helpers to compute distance from a
selected community.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pandas as pd
import requests

GEONET_QUAKE_URL = "https://api.geonet.org.nz/quake"
# Wellington Region bounding box (lon/lat) used to filter the national feed.
WELLINGTON_BBOX = {"min_lat": -41.7, "max_lat": -40.7, "min_lon": 174.5, "max_lon": 175.3}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def fetch_recent_quakes(mmi: int = 3, timeout: float = 8.0) -> pd.DataFrame:
    """Fetch recent NZ earthquakes from GeoNet.

    ``mmi`` is the minimum Modified Mercalli Intensity (GeoNet accepts -1..8).
    Returns an empty DataFrame (with the right columns) on any failure so the
    UI never crashes when offline.
    """
    columns = [
        "publicid", "time", "magnitude", "depth", "mmi", "locality", "lat", "lon",
    ]
    try:
        resp = requests.get(
            GEONET_QUAKE_URL,
            params={"MMI": mmi},
            headers={"Accept": "application/vnd.geo+json;version=2"},
            timeout=timeout,
        )
        resp.raise_for_status()
        features = resp.json().get("features", [])
    except (requests.RequestException, ValueError):
        return pd.DataFrame(columns=columns)

    records = []
    for feat in features:
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [None, None])
        records.append(
            {
                "publicid": props.get("publicID"),
                "time": props.get("time"),
                "magnitude": props.get("magnitude"),
                "depth": props.get("depth"),
                "mmi": props.get("mmi"),
                "locality": props.get("locality"),
                "lon": coords[0],
                "lat": coords[1],
            }
        )

    df = pd.DataFrame(records, columns=columns)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    return df


def add_distance(df: pd.DataFrame, lat: float, lon: float) -> pd.DataFrame:
    """Append a ``distance_km`` column measured from (lat, lon)."""
    if df.empty:
        out = df.copy()
        out["distance_km"] = pd.Series(dtype=float)
        return out
    out = df.copy()
    out["distance_km"] = out.apply(
        lambda r: haversine_km(lat, lon, r["lat"], r["lon"]), axis=1
    ).round(1)
    return out


def filter_wellington(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only quakes inside the Wellington Region bounding box."""
    if df.empty:
        return df
    b = WELLINGTON_BBOX
    mask = (
        df["lat"].between(b["min_lat"], b["max_lat"])
        & df["lon"].between(b["min_lon"], b["max_lon"])
    )
    return df[mask].reset_index(drop=True)


def hours_ago(ts) -> str:
    """Human-friendly 'time since' label for a UTC timestamp."""
    if pd.isna(ts):
        return "—"
    delta = datetime.now(timezone.utc) - ts.to_pydatetime()
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return f"{int(delta.total_seconds() / 60)} min ago"
    if hours < 48:
        return f"{int(hours)} h ago"
    return f"{int(hours / 24)} d ago"
