# NYC Energy Equity Benchmarking System

**Tools:** Power BI | SQL | Python | Power Automate  
**Data Source:** NYC Mayor's Office of Sustainability — Building Energy Benchmarking (public dataset)  
**Status:** In Progress — Dashboard publishing week of April 21, 2026

---

## Problem

NYC building energy data exists publicly but sits flat and unsegmented. Program teams making investment decisions in clean energy and affordable housing had no quick way to identify which buildings or neighborhoods were underperforming — or where interventions would have the highest impact.

---

## What I Built

- Power BI dashboard with DAX measures scoring 26,000+ buildings across 5 boroughs on energy efficiency tiers
- Row-level security configured across 5 borough-based stakeholder roles so each team sees only their program scope
- SQL and Python pipeline to clean, validate, and model raw benchmarking data
- Power Automate workflow triggering threshold-based alerts when buildings exceed borough benchmarks — eliminating weekly manual pulls

---

## Key Findings

- Identified buildings consuming up to 52% above borough benchmarks *(to be updated with final number)*
- Bottom-performing properties surfaced as a prioritized intervention list for program teams
- Automated alerting replaced manual weekly reporting cycle with a zero-touch workflow

---

## Folder Structure

```
energy-equity-benchmarking/
│
├── sql/                  # Queries for efficiency scoring and tier segmentation
│   └── efficiency_scoring.sql
│
├── python/               # Data cleaning and transformation scripts
│   └── clean_transform.py
│
├── dashboards/           # Power BI screenshots and notes (publishing this week)
│   └── README.md
│
└── data/                 # Data source info and schema notes
    └── data_source.md
```

---

## Data Source

NYC Open Data — Building Energy and Water Data Disclosure  
Link: https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-2022/usc3-8zwd

---

## Contact

Akshitha Addagatla  
akshitha4413@gmail.com | [LinkedIn](https://www.linkedin.com/in/akshitha-addagatla-6658932a1/)
