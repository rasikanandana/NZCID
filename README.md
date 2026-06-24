# 🗺️ NZ Community Insights Dashboard (NZCID)

> Helping New Zealanders compare communities on **affordability, livability,
> accessibility and natural-hazard exposure.**

An interactive Streamlit dashboard for exploring and comparing New Zealand
communities. **MVP scoped to the Wellington Region** (17 communities), built as
a portfolio piece demonstrating GIS/geospatial analytics, dashboard
development, data engineering, and hazard-resilience analysis.

![Python](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/streamlit-app-FF4B4B)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

---

## ✨ Features

| Module | What it does |
|---|---|
| **🗺️ Interactive map** | Folium map with toggleable thematic layers (livability, house price, rent, population, growth, hazards) plus schools, hospitals and **live GeoNet earthquakes**. |
| **🏘️ Community profile** | Housing trends, population & economy, accessibility (schools + EQI, hospitals, transport), climate, and hazard exposure for any community. |
| **⚖️ Compare** | Head-to-head of two communities — radar chart, indicator-by-indicator table with winner highlighting, and a verdict (e.g. *Petone vs Johnsonville*). |
| **📈 Livability index** | Custom 0–100 score across six weighted pillars, shown as a gauge with regional ranking. |
| **⚠️ Hazards** | Live GeoNet earthquakes filtered to the region with distance-from-community, plus flood / tsunami / landslide exposure indices. |
| **👥 Demographics** | Modelled population pyramid, population-vs-growth bubble chart, income comparison. |

## 🧮 Livability index methodology

Each community scores **0–100**. Every input metric is min-max normalised
across the region (scores are *relative within Wellington*), with direction
flipped for "lower is better" metrics (price, hazard exposure). Pillar scores
are the mean of their metrics; the overall score is the weighted sum:

| Pillar | Weight | Built from |
|---|---|---|
| Affordability | 25% | House price, weekly rent |
| Accessibility | 20% | Schools, hospitals, transport, walkability |
| Hazard resilience | 20% | Flood, earthquake, tsunami, landslide exposure |
| Economic | 15% | Household income, employment |
| Environment | 10% | Sunshine hours, rainfall |
| Community | 10% | Population growth, amenities |

Defined in [`nzcid/config.py`](nzcid/config.py); computed in
[`nzcid/livability.py`](nzcid/livability.py). Tweak weights in one place
and the whole app updates.

## 🚀 Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create an app pointing
   at `app.py` on this branch.
3. Dependencies install from `requirements.txt`; no secrets are required.

> The live GeoNet earthquake feed needs outbound HTTPS to `api.geonet.org.nz`.
> Streamlit Cloud allows this; in restricted/offline environments the app
> degrades gracefully and simply hides the live layer.

## 🧪 Tests

```bash
python -m pytest -q
```

Covers the scoring engine (bounds, direction, ranking, purity), data integrity,
and the GeoNet helpers (offline — no network needed).

## 🗂️ Project structure

```
app.py                       # Home: map + region overview
pages/
  1_Community_Profile.py
  2_Compare.py
  3_Hazards.py
  4_Demographics.py
  5_About.py
nzcid/                       # importable package at the repo root
  config.py                  # palette, paths, livability pillars & weights
  data_loader.py             # cached CSV loaders
  livability.py              # scoring engine
  services/geonet.py         # live GeoNet earthquake API
  ui/
    common.py                # theme/CSS + Streamlit helpers
    charts.py                # Plotly figures (gauge, radar, pyramid, …)
    maps.py                  # Folium map + thematic layers
  data/
    suburbs.csv              # core indicator table
    schools.csv, hospitals.csv
tests/                       # pytest suite
```

## 📊 Data sources & provenance

| Domain | Intended source | MVP status |
|---|---|---|
| Earthquakes | [GeoNet](https://www.geonet.org.nz/) quake API | **Live** |
| Housing | Stats NZ, MBIE / Tenancy Services bond data | Curated sample |
| Population & income | Stats NZ (Census, Datafinder) | Curated sample |
| Schools & EQI | Ministry of Education | Curated sample |
| Hospitals | Health NZ / Te Whatu Ora | Curated sample |
| Hazards | LINZ, Greater Wellington RC, NZ SeaRise | Indicative composite |
| Climate | NIWA, MetService | Curated averages |

> ⚠️ **Disclaimer:** apart from the live GeoNet feed, indicators are curated
> and *indicative*, drawn from publicly reported ranges to demonstrate the
> platform. They are **not an official source** and must not be used for
> property, financial, or emergency-management decisions.

## 🛣️ Roadmap

1. **MVP (now):** Wellington Region, curated indicators, live GeoNet, livability
   index, profiles, compare, hazards, demographics.
2. **Next:** live Stats NZ / MBIE APIs, real suburb boundary polygons for
   choropleths, GTFS transit travel-times, NIWA climate.
3. **Later:** nationwide coverage, PostgreSQL + PostGIS backend, saved
   comparisons.

## 📜 License

See [LICENSE](LICENSE).
