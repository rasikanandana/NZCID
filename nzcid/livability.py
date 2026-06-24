"""The livability scoring engine.

Each pillar is built from one or more metrics. Metrics are min-max
normalised to 0-100 across the whole suburb set (so scores are relative
within the region), flipping direction for "lower is better" metrics such
as price and hazard exposure. Pillar scores are the mean of their metric
scores; the overall score is the weighted sum of pillar scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import PILLARS, Metric


def _normalise(series: pd.Series, higher_is_better: bool) -> pd.Series:
    """Scale a column to 0-100. Flat columns map to a neutral 50."""
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(50.0, index=series.index)
    scaled = (series - lo) / (hi - lo) * 100.0
    if not higher_is_better:
        scaled = 100.0 - scaled
    return scaled


def _metric_scores(df: pd.DataFrame, metrics: list[Metric]) -> pd.DataFrame:
    return pd.DataFrame(
        {m.column: _normalise(df[m.column], m.higher_is_better) for m in metrics}
    )


def add_livability(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with pillar columns and a livability score.

    Adds one ``score_<pillar>`` column per pillar plus ``livability_score``
    and an integer ``rank`` (1 = most livable).
    """
    out = df.copy()
    weighted_total = np.zeros(len(out))

    for pillar in PILLARS:
        # A metric may appear in more than one pillar; average within pillar.
        scores = _metric_scores(out, pillar.metrics).mean(axis=1)
        out[f"score_{pillar.key}"] = scores.round(1)
        weighted_total += scores.to_numpy() * pillar.weight

    out["livability_score"] = np.round(weighted_total, 1)
    out["rank"] = (
        out["livability_score"].rank(ascending=False, method="min").astype(int)
    )
    return out


def explain(row: pd.Series, n: int = 2) -> tuple[list[tuple[str, float]],
                                                  list[tuple[str, float]]]:
    """Return the suburb's top ``n`` strengths and weaknesses as pillars.

    Each item is ``(pillar_label, score)``. Used to explain *why* a suburb
    scores the way it does (e.g. an expensive suburb is dragged down by the
    Affordability pillar even if it's pleasant to live in).
    """
    ranked = sorted(PILLARS, key=lambda p: float(row[f"score_{p.key}"]),
                    reverse=True)
    strengths = [(p.label, float(row[f"score_{p.key}"])) for p in ranked[:n]]
    weaknesses = [(p.label, float(row[f"score_{p.key}"])) for p in ranked[-n:]]
    return strengths, weaknesses


def pillar_breakdown(row: pd.Series) -> pd.DataFrame:
    """Per-pillar contribution table for a single suburb (for charts/tooltips)."""
    rows = []
    for pillar in PILLARS:
        score = float(row[f"score_{pillar.key}"])
        rows.append(
            {
                "pillar": pillar.label,
                "key": pillar.key,
                "score": score,
                "weight": pillar.weight,
                "contribution": round(score * pillar.weight, 1),
                "description": pillar.description,
            }
        )
    return pd.DataFrame(rows)
