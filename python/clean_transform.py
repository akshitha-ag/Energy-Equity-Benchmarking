# ============================================================
# NYC Energy Equity Benchmarking System
# Python Script: Data Cleaning & Transformation
# Author: Akshitha Addagatla
# Data: NYC Building Energy Benchmarking (public dataset)
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# STEP 1: Load raw data
# ============================================================
# Download from:
# https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-2022/usc3-8zwd

RAW_FILE = "data/nyc_energy_benchmarking_raw.csv"
OUTPUT_FILE = "data/nyc_energy_benchmarking_clean.csv"

print("Loading raw data...")
df = pd.read_csv(RAW_FILE, low_memory=False)
print(f"Raw shape: {df.shape}")


# ============================================================
# STEP 2: Standardize column names
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^\w]", "_", regex=True)
)

# Rename key columns for clarity
column_map = {
    "bbl__10_digits_": "bbl",
    "property_name": "property_name",
    "address_1__self_reported_": "address",
    "borough": "borough",
    "primary_property_type___self_selected_": "primary_property_type",
    "year_built": "year_built",
    "site_eui__kbtu_ft²_": "site_eui",
    "total_ghg_emissions__metric_tons_co2e_": "total_ghg_emissions",
    "energy_star_score": "energy_star_score",
    "self_reported_gross_floor_area__ft²_": "gross_floor_area_sqft",
}

df.rename(columns={k: v for k, v in column_map.items() if k in df.columns}, inplace=True)

print(f"\nColumns after rename: {list(df.columns)}")


# ============================================================
# STEP 3: Data validation — flag issues before dropping
# ============================================================

print("\n--- Data Quality Report ---")
print(f"Total records: {len(df):,}")
print(f"Missing site_eui: {df['site_eui'].isna().sum():,}")
print(f"Missing borough: {df['borough'].isna().sum():,}")
print(f"Zero or negative site_eui: {(df['site_eui'] <= 0).sum():,}")
print(f"Missing gross_floor_area: {df['gross_floor_area_sqft'].isna().sum():,}")

# Schema drift check — expected columns must be present
required_cols = ["bbl", "borough", "site_eui", "gross_floor_area_sqft", "primary_property_type"]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Schema drift detected — missing columns: {missing_cols}")
else:
    print("\nSchema check passed — all required columns present.")


# ============================================================
# STEP 4: Clean and filter
# ============================================================

df_clean = df.copy()

# Drop rows with missing key fields
df_clean = df_clean.dropna(subset=["site_eui", "borough", "gross_floor_area_sqft"])

# Remove zero/negative EUI values (data entry errors)
df_clean = df_clean[df_clean["site_eui"] > 0]

# Remove extreme outliers (above 99th percentile — likely errors)
p99 = df_clean["site_eui"].quantile(0.99)
df_clean = df_clean[df_clean["site_eui"] <= p99]

# Standardize borough names
borough_map = {
    "manhattan": "Manhattan",
    "brooklyn": "Brooklyn",
    "queens": "Queens",
    "bronx": "Bronx",
    "staten island": "Staten Island",
}
df_clean["borough"] = df_clean["borough"].str.strip().str.lower().map(borough_map)
df_clean = df_clean.dropna(subset=["borough"])

# Fill missing energy star scores with 0 (not scored)
df_clean["energy_star_score"] = df_clean["energy_star_score"].fillna(0)

print(f"\nClean shape: {df_clean.shape}")
print(f"Records removed: {len(df) - len(df_clean):,}")


# ============================================================
# STEP 5: Feature engineering — efficiency scoring
# ============================================================

# Borough + property type median EUI (the benchmark)
df_clean["borough_median_eui"] = df_clean.groupby(
    ["borough", "primary_property_type"]
)["site_eui"].transform("median")

# % above or below borough median
df_clean["pct_above_borough_median"] = (
    (df_clean["site_eui"] - df_clean["borough_median_eui"])
    / df_clean["borough_median_eui"] * 100
).round(2)

# Efficiency tier assignment
def assign_tier(row):
    p25 = row["borough_median_eui"] * 0.75  # approx p25
    p75 = row["borough_median_eui"] * 1.25  # approx p75
    eui = row["site_eui"]
    if eui <= p25:
        return "High Efficiency"
    elif eui <= row["borough_median_eui"]:
        return "Medium Efficiency"
    elif eui <= p75:
        return "Low Efficiency"
    else:
        return "Critical - Intervention Needed"

df_clean["efficiency_tier"] = df_clean.apply(assign_tier, axis=1)

# Borough rank within critical tier
df_clean["borough_rank"] = df_clean.groupby("borough")["pct_above_borough_median"].rank(
    ascending=False, method="dense"
)


# ============================================================
# STEP 6: Key findings summary
# ============================================================

print("\n--- Key Findings ---")

total = len(df_clean)
critical = df_clean[df_clean["efficiency_tier"] == "Critical - Intervention Needed"]
print(f"Total buildings analyzed: {total:,}")
print(f"Critical buildings (intervention needed): {len(critical):,} ({len(critical)/total*100:.1f}%)")
print(f"Max % above borough median: {df_clean['pct_above_borough_median'].max():.1f}%")

print("\nCritical buildings by borough:")
print(
    df_clean.groupby("borough")
    .apply(lambda x: pd.Series({
        "total": len(x),
        "critical": (x["efficiency_tier"] == "Critical - Intervention Needed").sum(),
        "pct_critical": round((x["efficiency_tier"] == "Critical - Intervention Needed").sum() / len(x) * 100, 1)
    }))
    .to_string()
)


# ============================================================
# STEP 7: Export clean data for Power BI
# ============================================================

df_clean.to_csv(OUTPUT_FILE, index=False)
print(f"\nClean data exported to: {OUTPUT_FILE}")
print(f"Final record count: {len(df_clean):,}")


# ============================================================
# STEP 8: Quick EDA visualization
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribution of efficiency tiers by borough
tier_counts = df_clean.groupby(["borough", "efficiency_tier"]).size().unstack(fill_value=0)
tier_counts.plot(kind="bar", ax=axes[0], colormap="RdYlGn_r")
axes[0].set_title("Efficiency Tier Distribution by Borough")
axes[0].set_xlabel("Borough")
axes[0].set_ylabel("Building Count")
axes[0].tick_params(axis="x", rotation=45)
axes[0].legend(loc="upper right", fontsize=8)

# % above borough median distribution
axes[1].hist(
    df_clean[df_clean["pct_above_borough_median"] > 0]["pct_above_borough_median"],
    bins=50, color="#e74c3c", edgecolor="white", alpha=0.8
)
axes[1].set_title("Distribution: % Above Borough Median (Underperformers)")
axes[1].set_xlabel("% Above Borough Median EUI")
axes[1].set_ylabel("Building Count")

plt.tight_layout()
plt.savefig("dashboards/eda_overview.png", dpi=150, bbox_inches="tight")
print("\nEDA chart saved to dashboards/eda_overview.png")
plt.show()
