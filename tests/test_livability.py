"""Tests for the livability scoring engine and data integrity."""

import pandas as pd
import pytest

from nzcid import config, data_loader
from nzcid.livability import _normalise, add_livability, explain, pillar_breakdown


def test_pillar_weights_sum_to_one():
    assert abs(sum(p.weight for p in config.PILLARS) - 1.0) < 1e-9


def test_normalise_basic_range_and_direction():
    s = pd.Series([0, 50, 100])
    up = _normalise(s, higher_is_better=True)
    assert up.tolist() == [0.0, 50.0, 100.0]
    down = _normalise(s, higher_is_better=False)
    assert down.tolist() == [100.0, 50.0, 0.0]


def test_normalise_flat_series_is_neutral():
    s = pd.Series([7, 7, 7])
    assert _normalise(s, True).tolist() == [50.0, 50.0, 50.0]


def test_scores_bounded_and_ranked():
    df = data_loader.load_suburbs()
    assert df["livability_score"].between(0, 100).all()
    # Ranks are dense from 1 and the best score has rank 1.
    assert df["rank"].min() == 1
    best = df.loc[df["livability_score"].idxmax()]
    assert best["rank"] == 1


def test_pillar_columns_present():
    df = data_loader.load_suburbs()
    for p in config.PILLARS:
        col = f"score_{p.key}"
        assert col in df.columns
        assert df[col].between(0, 100).all()


def test_breakdown_contribution_matches_total():
    df = data_loader.load_suburbs()
    row = df.iloc[0]
    bd = pillar_breakdown(row)
    total = bd["contribution"].sum()
    # Allow small rounding drift from per-pillar rounding.
    assert abs(total - row["livability_score"]) < 1.5


def test_cheaper_suburb_scores_higher_on_affordability():
    df = data_loader.load_suburbs()
    cheap = df.loc[df["median_house_price"].idxmin()]
    pricey = df.loc[df["median_house_price"].idxmax()]
    assert cheap["score_affordability"] > pricey["score_affordability"]


def test_dataset_has_no_missing_values():
    df = pd.read_csv(config.SUBURBS_CSV)
    assert not df.isnull().any().any()
    assert len(df) >= 10


def test_supporting_datasets_load():
    assert not data_loader.load_schools().empty
    assert not data_loader.load_hospitals().empty


def test_add_livability_is_pure():
    df = pd.read_csv(config.SUBURBS_CSV)
    before = df.copy()
    add_livability(df)
    pd.testing.assert_frame_equal(df, before)  # input unchanged


def test_explain_returns_strengths_and_weaknesses():
    row = data_loader.get_suburb("Karori")
    strengths, weaknesses = explain(row, n=2)
    assert len(strengths) == 2 and len(weaknesses) == 2
    # Strengths score at least as high as weaknesses.
    assert min(s for _, s in strengths) >= max(w for _, w in weaknesses)
    # Karori is expensive, so Affordability should be among its weaknesses.
    assert "Affordability" in {label for label, _ in weaknesses}


def test_inland_suburbs_have_zero_tsunami_exposure():
    df = data_loader.load_suburbs()
    inland = ["Karori", "Kelburn", "Tawa", "Johnsonville", "Upper Hutt"]
    for name in inland:
        assert df.loc[df["suburb"] == name, "tsunami_exposure"].iloc[0] == 0


def test_nearest_suburb_matches_centroid():
    petone = data_loader.get_suburb("Petone")
    assert data_loader.nearest_suburb(petone["lat"], petone["lon"]) == "Petone"


def test_schools_cover_multiple_types():
    types = set(data_loader.load_schools()["type"])
    assert {"Primary", "Secondary"}.issubset(types)
