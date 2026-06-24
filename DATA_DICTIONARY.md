# Data dictionary — NZ Community Insights Dashboard (Wellington MVP)

Three CSVs power the app, all in `nzcid/data/`. Values are a **curated,
indicative MVP dataset** drawn from publicly reported ranges (Stats NZ,
MBIE/Tenancy Services bond data, Ministry of Education Equity Index, GeoNet,
and regional-council hazard portals). They demonstrate the platform — they are
**not an official source** and must not be used for property, financial or
emergency-management decisions. Earthquakes shown in the app are **live** from
GeoNet, not from these files.

---

## `suburbs.csv` — one row per community (17 rows)

| Column | Units | Meaning |
|---|---|---|
| `suburb` | text | Community name |
| `territorial_authority` | text | Council (Wellington City, Lower Hutt, Upper Hutt, Porirua City, Kapiti Coast) |
| `lat`, `lon` | degrees | Approximate community centroid |
| `median_house_price` | NZD | Indicative median dwelling sale price |
| `house_price_trend_pct` | % / yr | Year-on-year change (negative = falling) |
| `median_rent_weekly` | NZD / week | Indicative median rent |
| `rent_trend_pct` | % / yr | Year-on-year change |
| `population` | people | Usual resident population |
| `pop_growth_pct` | % / yr | Annual population growth |
| `median_age` | years | Median age of residents |
| `median_household_income` | NZD / yr | Median household income |
| `employment_rate` | % | Share of working-age residents employed |
| `schools_count` | count | Schools in/near the community |
| `avg_school_eqi` | index | Mean Ministry of Education **Equity Index** (EQI). Roughly 344–569; **lower = less socio-economic barrier** to achievement |
| `hospitals_within_10km` | count | Public/private hospitals within ~10 km |
| `transport_score` | 0–100 | Public-transport access (higher = better) |
| `walkability_score` | 0–100 | Walkability (higher = better) |
| `avg_temp_c` | °C | Average annual temperature |
| `annual_rainfall_mm` | mm / yr | Average annual rainfall |
| `sunshine_hours` | hours / yr | Average annual sunshine |
| `flood_exposure` | 0–100 | Flood exposure (higher = **more** exposed) |
| `earthquake_exposure` | 0–100 | Earthquake shaking exposure (soft-soil sites amplify shaking, so they score higher) |
| `tsunami_exposure` | 0–100 | Tsunami inundation exposure. **Inland / elevated suburbs are 0** (e.g. Karori, Kelburn, Tawa, Johnsonville, Upper Hutt); harbour/coast low-lying suburbs are high (e.g. Petone, Island Bay) |
| `landslide_exposure` | 0–100 | Landslide susceptibility (steep hill suburbs score higher) |

**Hazard columns are exposure, where higher = worse.** In the livability index
they are inverted (less exposure → higher resilience score).

---

## `schools.csv` — one row per school (37 rows)

| Column | Units | Meaning |
|---|---|---|
| `name` | text | School name |
| `suburb` | text | Community it sits in (joins to `suburbs.csv`) |
| `lat`, `lon` | degrees | School location |
| `type` | text | Primary / Intermediate / Secondary / Composite |
| `eqi` | index | Equity Index (lower = less barrier) |
| `roll` | count | Approximate student roll |

---

## `hospitals.csv` — one row per hospital (6 rows)

| Column | Units | Meaning |
|---|---|---|
| `name` | text | Hospital name |
| `suburb` | text | Community it sits in |
| `lat`, `lon` | degrees | Hospital location |
| `type` | text | Public (tertiary/secondary/community) or Private |

---

## How the livability score is built (0–100)

1. Each input metric is **min-max normalised to 0–100 across all 17 suburbs**,
   so scores are *relative within the Wellington Region*.
2. Direction is flipped for "lower is better" metrics (price, rent, hazard
   exposure, rainfall).
3. Each **pillar** score is the mean of its metric scores.
4. The overall score is the weighted sum of the six pillars:

| Pillar | Weight | Built from |
|---|---|---|
| Affordability | 25% | house price, weekly rent |
| Accessibility | 20% | schools, hospitals, transport, walkability |
| Hazard resilience | 20% | flood, earthquake, tsunami, landslide exposure (inverted) |
| Economic | 15% | household income, employment |
| Environment | 10% | sunshine, rainfall |
| Community | 10% | population growth, amenities |

This is why an expensive, established suburb (e.g. **Karori**, ~$1.09 M median)
can sit mid-to-lower table: Affordability (25%) and low population growth pull
it down even though its incomes and tsunami-safety are strong. The Community
Profile page shows each suburb's strengths and drags under **"Why this score?"**.
