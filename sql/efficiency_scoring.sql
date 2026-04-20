-- ============================================================
-- NYC Energy Equity Benchmarking System
-- SQL Queries: Efficiency Scoring & Tier Segmentation
-- Author: Akshitha Addagatla
-- Data: NYC Building Energy Benchmarking (public dataset)
-- ============================================================


-- ------------------------------------------------------------
-- STEP 1: Clean and filter raw benchmarking data
-- ------------------------------------------------------------
-- Remove records with missing energy use intensity (Site EUI)
-- Focus on properties with complete borough and building type data

CREATE OR REPLACE VIEW vw_clean_buildings AS
SELECT
    bbl,
    property_name,
    address,
    borough,
    primary_property_type,
    year_built,
    largest_property_use_type,
    site_eui_kbtu_per_sqft,         -- Key metric: energy use per sq ft
    total_ghg_emissions_metric_tons,
    energy_star_score,
    property_gfa_self_reported_sqft
FROM nyc_energy_benchmarking
WHERE
    site_eui_kbtu_per_sqft IS NOT NULL
    AND site_eui_kbtu_per_sqft > 0
    AND borough IS NOT NULL
    AND property_gfa_self_reported_sqft > 0;


-- ------------------------------------------------------------
-- STEP 2: Calculate borough-level benchmarks
-- ------------------------------------------------------------
-- Median Site EUI per borough used as the comparison baseline

CREATE OR REPLACE VIEW vw_borough_benchmarks AS
SELECT
    borough,
    primary_property_type,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY site_eui_kbtu_per_sqft) AS median_eui,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY site_eui_kbtu_per_sqft) AS p75_eui,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY site_eui_kbtu_per_sqft) AS p25_eui,
    COUNT(*) AS building_count
FROM vw_clean_buildings
GROUP BY borough, primary_property_type;


-- ------------------------------------------------------------
-- STEP 3: Score each building against its borough benchmark
-- ------------------------------------------------------------
-- Calculate % above or below median for each building
-- Assign efficiency tier: High / Medium / Low / Critical

CREATE OR REPLACE VIEW vw_efficiency_scores AS
SELECT
    b.bbl,
    b.property_name,
    b.address,
    b.borough,
    b.primary_property_type,
    b.site_eui_kbtu_per_sqft,
    bm.median_eui AS borough_median_eui,
    ROUND(
        ((b.site_eui_kbtu_per_sqft - bm.median_eui) / bm.median_eui) * 100, 2
    ) AS pct_above_borough_median,
    CASE
        WHEN b.site_eui_kbtu_per_sqft <= bm.p25_eui  THEN 'High Efficiency'
        WHEN b.site_eui_kbtu_per_sqft <= bm.median_eui THEN 'Medium Efficiency'
        WHEN b.site_eui_kbtu_per_sqft <= bm.p75_eui  THEN 'Low Efficiency'
        ELSE 'Critical — Intervention Needed'
    END AS efficiency_tier,
    b.energy_star_score,
    b.total_ghg_emissions_metric_tons
FROM vw_clean_buildings b
LEFT JOIN vw_borough_benchmarks bm
    ON b.borough = bm.borough
    AND b.primary_property_type = bm.primary_property_type;


-- ------------------------------------------------------------
-- STEP 4: Prioritized intervention list
-- ------------------------------------------------------------
-- Surface bottom-performing buildings ranked by how far above
-- benchmark they are — gives program teams an action-ready list

CREATE OR REPLACE VIEW vw_intervention_priority AS
SELECT
    bbl,
    property_name,
    address,
    borough,
    primary_property_type,
    site_eui_kbtu_per_sqft,
    borough_median_eui,
    pct_above_borough_median,
    efficiency_tier,
    total_ghg_emissions_metric_tons,
    RANK() OVER (
        PARTITION BY borough
        ORDER BY pct_above_borough_median DESC
    ) AS borough_rank
FROM vw_efficiency_scores
WHERE efficiency_tier = 'Critical — Intervention Needed'
ORDER BY pct_above_borough_median DESC;


-- ------------------------------------------------------------
-- STEP 5: Summary stats for Power BI dashboard cards
-- ------------------------------------------------------------

SELECT
    borough,
    COUNT(*) AS total_buildings,
    COUNT(CASE WHEN efficiency_tier = 'Critical — Intervention Needed' THEN 1 END) AS critical_count,
    ROUND(
        COUNT(CASE WHEN efficiency_tier = 'Critical — Intervention Needed' THEN 1 END) * 100.0
        / COUNT(*), 1
    ) AS pct_critical,
    ROUND(AVG(pct_above_borough_median), 1) AS avg_pct_above_median,
    ROUND(MAX(pct_above_borough_median), 1) AS max_pct_above_median
FROM vw_efficiency_scores
GROUP BY borough
ORDER BY pct_critical DESC;
