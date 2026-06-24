"""Central configuration: theme palette, file paths and the livability model.

Tweaking the weights or sub-metric definitions here changes the whole app,
so the scoring model lives in one place rather than being scattered through
the UI code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
DATA_DIR = Path(__file__).resolve().parent / "data"
SUBURBS_CSV = DATA_DIR / "suburbs.csv"
SCHOOLS_CSV = DATA_DIR / "schools.csv"
HOSPITALS_CSV = DATA_DIR / "hospitals.csv"

# --------------------------------------------------------------------------- #
# Branding / theme — an NZ-inspired blue & green palette
# --------------------------------------------------------------------------- #
APP_NAME = "NZ Community Insights Dashboard"
APP_TAGLINE = (
    "Compare New Zealand communities on affordability, livability, "
    "accessibility and hazard exposure."
)

COLORS = {
    "primary": "#0B4F6C",     # deep harbour blue
    "secondary": "#1B998B",   # pounamu green
    "accent": "#F4A259",      # warm sand
    "danger": "#D7263D",      # hazard red
    "good": "#2A9D8F",
    "warn": "#E9C46A",
    "bad": "#E76F51",
    "ink": "#1F2933",
    "muted": "#6B7280",
    "bg": "#F5F7FA",
}

# Map centre for the Wellington Region MVP.
MAP_CENTER = (-41.22, 174.85)
MAP_ZOOM = 10

# --------------------------------------------------------------------------- #
# Livability model
# --------------------------------------------------------------------------- #
# A "metric" is one input column. ``higher_is_better`` tells the normaliser
# which direction is good (cheaper housing is better, more hazard is worse).
@dataclass(frozen=True)
class Metric:
    column: str
    higher_is_better: bool
    label: str


@dataclass(frozen=True)
class Pillar:
    """A weighted group of metrics that contributes to the livability score."""

    key: str
    label: str
    weight: float          # share of the 0-100 score (weights sum to 1.0)
    metrics: list[Metric] = field(default_factory=list)
    description: str = ""


# The six pillars described in the project brief. Weights sum to 1.0.
PILLARS: list[Pillar] = [
    Pillar(
        key="affordability",
        label="Affordability",
        weight=0.25,
        description="Lower house prices and rents score higher.",
        metrics=[
            Metric("median_house_price", False, "Median house price"),
            Metric("median_rent_weekly", False, "Median weekly rent"),
        ],
    ),
    Pillar(
        key="accessibility",
        label="Accessibility",
        weight=0.20,
        description="Schools, hospitals, public transport and walkability.",
        metrics=[
            Metric("schools_count", True, "Schools nearby"),
            Metric("hospitals_within_10km", True, "Hospitals within 10 km"),
            Metric("transport_score", True, "Public transport score"),
            Metric("walkability_score", True, "Walkability"),
        ],
    ),
    Pillar(
        key="economic",
        label="Economic",
        weight=0.15,
        description="Household income and employment.",
        metrics=[
            Metric("median_household_income", True, "Median household income"),
            Metric("employment_rate", True, "Employment rate"),
        ],
    ),
    Pillar(
        key="environment",
        label="Environment",
        weight=0.10,
        description="Sunshine, comfortable temperatures and lower rainfall.",
        metrics=[
            Metric("sunshine_hours", True, "Annual sunshine hours"),
            Metric("annual_rainfall_mm", False, "Annual rainfall"),
        ],
    ),
    Pillar(
        key="community",
        label="Community",
        weight=0.10,
        description="Population growth and local amenities.",
        metrics=[
            Metric("pop_growth_pct", True, "Population growth"),
            Metric("schools_count", True, "Local amenities (schools proxy)"),
        ],
    ),
    Pillar(
        key="hazard",
        label="Hazard resilience",
        weight=0.20,
        description="Lower flood, earthquake, tsunami and landslide exposure.",
        metrics=[
            Metric("flood_exposure", False, "Flood exposure"),
            Metric("earthquake_exposure", False, "Earthquake exposure"),
            Metric("tsunami_exposure", False, "Tsunami exposure"),
            Metric("landslide_exposure", False, "Landslide exposure"),
        ],
    ),
]

HAZARD_COLUMNS = {
    "flood_exposure": "Flood",
    "earthquake_exposure": "Earthquake",
    "tsunami_exposure": "Tsunami",
    "landslide_exposure": "Landslide",
}


def livability_grade(score: float) -> str:
    """Map a 0-100 livability score to a human-friendly band."""
    if score >= 75:
        return "Excellent"
    if score >= 60:
        return "Very good"
    if score >= 45:
        return "Good"
    if score >= 30:
        return "Fair"
    return "Challenging"
