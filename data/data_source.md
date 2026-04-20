# Data Source

## Dataset
NYC Building Energy and Water Data Disclosure (2022)

## Source
NYC Open Data — Mayor's Office of Sustainability
https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-2022/usc3-8zwd

## How to Download
1. Go to the link above
2. Click "Export" → CSV
3. Save as `nyc_energy_benchmarking_raw.csv`
4. Place in the `data/` folder
5. Run `python/clean_transform.py`

## Key Fields Used

| Field | Description |
|-------|-------------|
| BBL | Building identifier (Borough-Block-Lot) |
| Borough | NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island) |
| Primary Property Type | Building use category (Multifamily, Office, Retail, etc.) |
| Site EUI (kBtu/ft²) | Energy Use Intensity — primary efficiency metric |
| Total GHG Emissions | Greenhouse gas output in metric tons CO2e |
| Energy Star Score | EPA benchmark score (1-100) |
| Gross Floor Area | Building size in square feet |

## Schema Notes
- Site EUI is the core metric — lower = more efficient
- Borough median EUI used as the comparison benchmark per building type
- Records with missing or zero EUI removed during cleaning
- Outliers above 99th percentile removed (likely data entry errors)
