"""Address / place geocoding via OpenStreetMap Nominatim.

Free and key-free. Restricted to New Zealand and biased to the Wellington
Region. Returns ``None`` on any failure (offline, rate-limited, no match) so
the UI can degrade gracefully. Note: Nominatim asks for a descriptive
User-Agent and at most ~1 request/second.
"""

from __future__ import annotations

from typing import NamedTuple

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Wellington Region viewbox (lon/lat, lon/lat) to prefer local matches.
_VIEWBOX = "174.5,-40.6,175.4,-41.7"


class GeoResult(NamedTuple):
    lat: float
    lon: float
    label: str


def geocode_nz(query: str, timeout: float = 8.0) -> GeoResult | None:
    """Geocode an address / suburb / place within New Zealand."""
    query = (query or "").strip()
    if not query:
        return None
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "nz",
                "viewbox": _VIEWBOX,
                "bounded": 0,
                "addressdetails": 0,
            },
            headers={"User-Agent": "NZCID-dashboard/0.1 (portfolio project)"},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None
    if not data:
        return None
    try:
        top = data[0]
        return GeoResult(float(top["lat"]), float(top["lon"]), top["display_name"])
    except (KeyError, IndexError, TypeError, ValueError):
        return None
