# Dashboards

## Status
Power BI dashboard publishing week of April 21, 2026. Screenshots will be added here once complete.

---

## Power BI Build Notes

### Data Model
- Import clean CSV output from `python/clean_transform.py`
- One fact table: `nyc_energy_benchmarking_clean`
- One calculated table: `borough_benchmarks` (created via DAX)

---

### DAX Measures to Build

```
-- Average EUI across filtered selection
Avg Site EUI = AVERAGE(nyc_energy_benchmarking_clean[site_eui])

-- Count of critical buildings
Critical Buildings =
CALCULATE(
    COUNTROWS(nyc_energy_benchmarking_clean),
    nyc_energy_benchmarking_clean[efficiency_tier] = "Critical - Intervention Needed"
)

-- % of total that are critical
% Critical =
DIVIDE(
    [Critical Buildings],
    COUNTROWS(nyc_energy_benchmarking_clean),
    0
)

-- Average % above borough median for critical tier only
Avg Overconsumption % =
CALCULATE(
    AVERAGE(nyc_energy_benchmarking_clean[pct_above_borough_median]),
    nyc_energy_benchmarking_clean[efficiency_tier] = "Critical - Intervention Needed"
)

-- Dynamic borough benchmark line for visuals
Borough Median EUI =
CALCULATE(
    MEDIAN(nyc_energy_benchmarking_clean[site_eui]),
    ALLEXCEPT(nyc_energy_benchmarking_clean, nyc_energy_benchmarking_clean[borough])
)
```

---

### Row-Level Security Setup

In Power BI Desktop → Modeling → Manage Roles:

Create one role per borough:

| Role Name       | Table Filter                                      |
|----------------|---------------------------------------------------|
| Manhattan       | [borough] = "Manhattan"                           |
| Brooklyn        | [borough] = "Brooklyn"                            |
| Queens          | [borough] = "Queens"                              |
| Bronx           | [borough] = "Bronx"                               |
| Staten Island   | [borough] = "Staten Island"                       |

Test via: Modeling → View As → select each role to verify filtering works.

---

### Dashboard Pages

Page 1 — Executive Summary
- KPI cards: Total Buildings, Critical Count, % Critical, Avg Overconsumption %
- Bar chart: Efficiency tier breakdown by borough
- Map visual: Buildings plotted by lat/long, colored by efficiency tier

Page 2 — Intervention Priority List
- Table: Top 100 critical buildings ranked by % above borough median
- Filters: Borough, Property Type, Year Built
- Conditional formatting: Red = Critical, Yellow = Low, Green = High

Page 3 — Borough Deep Dive
- Slicer: Borough selector (drives RLS preview in edit mode)
- Trend: EUI distribution vs borough median benchmark line
- Scatter: GHG Emissions vs Site EUI colored by tier

---

### Power Automate Alert Flow

Trigger: Scheduled — weekly on Monday 8am
Action: Filter buildings where pct_above_borough_median > 50
Output: Send email with count of newly flagged buildings + link to dashboard
```
