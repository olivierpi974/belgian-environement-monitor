# 🏭 Belgian Industrial CO2 Monitor

## Context

**Final Project — Data Engineering Bootcamp, TechnoFutur TIC (Charleroi)**

*May 2026 | Full-time development (~7 hours/day over 3 weeks)*

An end-to-end data pipeline tracking CO2 emissions across Belgian industrial sites (2007–2024), built to answer: *How do Belgian industrial CO2 emissions evolve, and which sectors concentrate the highest releases?*

### Background

Over recent decades, GHG emissions have decreased at both individual and industrial levels. While national GHG emissions (CO2-equivalent) have declined by 32% since 1990, Belgium is not on track to meet its 2030 targets. This project focuses on one key lever: verified CO2 emissions from industrial installations covered by the European Union Emissions Trading System (EU ETS).

Most existing studies on CO2 emissions focus either on national aggregated data or on pan-European installation-level datasets. This project provides a **reproducible data infrastructure** targeting **Belgian industrial CO2 emissions** at both national and sector level, built on a structured Medallion pipeline designed to scale to installation level in future iterations.

**Primary use cases:**

- Consultancy firms working on environmental and sustainability mandates
- Corporate social responsibility departments of industrial companies seeking reproducible sector benchmarking tools

---

## 🎯 KPI

**V1 Focus:** CO2 emissions (tonnes) by sector and year

**V2 Roadmap:** Carbon intensity as secondary KPI (CO2 emissions / energy consumed)

---

## 📊 Data Sources

| File | Content | Granularity | Records |
| --- | --- | --- | --- |
| `F1_4_Air_Releases_Facilities.csv` | CO2 emissions per industrial site | Site × Year × Pollutant | ~372k |
| `F5_2_LCP_Energy_Emissions.csv` | Energy consumption per LCP installation | LCP × Year × Fuel type | ~401k |
| `F6_1_IED_Installations.csv` | Installation-to-site mapping | Cross-reference | ~478k |

**Source:** European Industrial Emissions Portal (E-PRTR v16.0, February 2026)

**Coverage:** Belgium | Period: 2007–2024 | 105 unique industrial sites

---

## 🏗️ Architecture

**Design Pattern:** Medallion Architecture (Bronze → Silver → Gold)

**Orchestration:** Manual, local Python pipeline on PostgreSQL

[ architecture Image]

### Layer Responsibilities

**Bronze Layer**

- Raw ingestion of CSV files into PostgreSQL
- No transformations or filters
- Single `date_ingest` timestamp per run
- Pattern: `if_exists='replace'` (full reload)

**Silver Layer**

- Data cleaning: null handling, type casting, trimming
- Filtering: Belgium perimeter only
- Business transformations: unit harmonization (ktoe → GWh), city-to-region mapping
- Quality checks: monitoring table logs row counts, nulls, duration per step

**Gold Layer**

- Dimensional model (star schema) with 5 dimensions and 1 fact table
- Surrogate keys and foreign key resolution
- Ready for Power BI visualization

### Fact & Dimension Tables

**Fact Table:**

- `fact_emissions_air` — Grain: Site × Year × Pollutant
    - Measures: `emitted_pollutant_tonnes`
    - Foreign keys: `fk_site_id`, `fk_pollutant_id`, `fk_sector_id`, `fk_year_id`

**Dimension Tables:**

- `dim_site` — FacilityInspireId, name, city, region, latitude, longitude
- `dim_sector` — E-PRTR sector code and label
- `dim_pollutant` — Pollutant code, name, unit
- `dim_year` — Year, decade
- `dim_region` — NUTS2 region (Wallonia, Flanders, Brussels)

---

## 📈 Power BI Dashboard (4 pages)

1. **National Overview** — CO2 trajectory 2007–2024 (vs. EU ETS -62% target)
2. **Sectoral Analysis** — Top 10 sectors by emissions and year-over-year trends
3. **Regional Breakdown** — Regional distribution across Wallonia, Flanders, Brussels
4. **Geographic View** — Interactive map of industrial sites (latitude/longitude)

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Pipeline Orchestration** | Python 3.12 |
| **Database** | PostgreSQL 16 |
| **Data Processing** | pandas, SQLAlchemy, psycopg2 |
| **Visualization** | Power BI Desktop |
| **Package Manager** | uv (Python) |
| **Version Control** | Git + GitHub |

---

## 🚀 How to Run the Pipeline

### Prerequisites

- PostgreSQL 16+ installed and running
- psql client available
- Python 3.12+
- `uv` package manager (installation guide)

### Step 1: Environment Setup

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials:
# - DB_HOST
# - DB_PORT
# - DB_USER
# - DB_PASSWORD
# - DB_NAME
```

Install dependencies:

```bash
uv sync
```

### Step 2: Database Initialization

Run the SQL setup scripts **in order**:

```bash
# 1. Create PostgreSQL user
psql -d postgres -f sql/00_create_user.sql

# 2. Create database
psql -d postgres -f sql/01_create_database.sql

# 3. Create schemas
psql -d belgian_environnement_data -f sql/02_create_schema.sql

# 4. Create tables and monitoring schema
psql -d belgian_environnement_data -f sql/03_create_table.sql
```

### Step 3: Prepare Data

Download the E-PRTR dataset from the EEA portal:

- Extract the ZIP file
- Place CSV files in the `data/` directory (or adjust paths in `main.py`)

### Step 4: Run the Pipeline

```bash
uv run src/main.py
```

The pipeline will:

1. Ingest raw data into Bronze
2. Clean and transform into Silver
3. Build dimensional model in Gold
4. Log monitoring metrics (row counts, durations, quality checks)

Output: PostgreSQL tables ready for Power BI import via ODBC

---

## 📁 Project Structure

[project structure image]

---

## 📊 Deliverables

**Code Artifacts:**

- ✅ Medallion architecture pipeline (Bronze → Silver → Gold)
- ✅ PostgreSQL database with 14 tables (3 raw, 7 cleaned, 5 dimensional model)
- ✅ Monitoring system tracking row counts, nulls, and execution time per layer
- ✅ Python logging to both console and file (`logs/pipeline.log`)

**Analytical Outputs:**

- ✅ Power BI dashboard (4 pages, 105 Belgian sites, 18 years of data)
- ✅ Sector-level CO2 trends and rankings
- ✅ Regional breakdown (Wallonia, Flanders, Brussels)

**Documentation:**

- ✅ README with setup instructions
- ✅ Inline code comments (French + English)
- ✅ Known limitations and future roadmap

---

## ⚠️ Known Limitations for V1

### Bronze Layer

The bronze layer lacks historical records: it uses `if_exists='replace'` instead of `append`. This is sufficient for an initial release but would require transactional wrapping (TRUNCATE + INSERT in a single transaction) for production use.

### Data & Perimeter

- **F6_1 join (LCP → Site)** — Partially implemented using BallTree geospatial matching; the overall matching score is unvalidated. Impact: Carbon intensity calculations available only for ~60% of sites.
- **Flanders coverage** — LCP installation mapping is less complete for Flanders region, reducing energy-based KPIs for that region.
- **Carbon Intensity (CO2/GWh)** — Computable only for sites with successfully matched LCP installations, which limits the analytical scope. Full coverage planned for V2 with improved matching logic.

### Simplified Approach

- **City-to-Region mapping** — Uses a static lookup table instead of geospatial matching (e.g., geopandas with NUTS2 polygons). Accurate for Belgium but not scalable to other regions.

### Code Quality

- **`main.py` refactoring needed (V2)** — Repeated monitoring patterns and column lists should be extracted to utility modules using a context manager approach.
- **Error handling** — Inconsistent between layers; Gold layer creation functions lack `try/except` blocks present in Bronze/Silver.

---

## 🔮 Roadmap (V2 & Beyond)

**V2 Priorities:**

- [ ]  Implement SCD Type 2 on `dim_sites` (valid_from, valid_to, is_current) to track site changes over time
- [ ]  Make Bronze layer atomicity explicit (TRUNCATE + INSERT in single transaction)
- [ ]  Improve F6_1 matching: profile GPS vs. site name stability, define a more robust business key
- [ ]  Add reverse geocoding for missing city values using geolocation APIs
- [ ]  Refactor `main.py` using context managers for monitoring instrumentation

**V3+ (Nice-to-haves):**

- [ ]  Introduce carbon intensity as primary KPI (CO2/GWh by sector and year)
- [ ]  Add meteorological data enrichment (temperature, wind) to correlate with winter energy peaks
- [ ]  Implement dbt for transformation orchestration
- [ ]  Deploy to Microsoft Fabric for cloud-scale analytics
- [ ]  Add anomaly detection (Isolation Forest) for outlier emissions

---

## 📝 Notes for Recruiters

This project demonstrates:

- **Full-stack data engineering:** from raw data ingestion to dimensional modeling to BI
- **Best practices:** Medallion architecture, monitoring, logging, Git workflow
- **Attention to limitations:** Honest documentation of gaps (vs. overstating V1 capabilities)
- **Scalability thinking:** Architecture designed to extend to installation level, multi-country coverage, and ML-based enrichment

The codebase is intentionally kept **simple and readable** for a 3-week sprint, prioritizing *completeness* over *over-engineering.*

---

**Author:** Olivier Picaud | **Last updated:** August 2026

**Repository:** github.com/olivierpi974/belgian-environnement-monitor