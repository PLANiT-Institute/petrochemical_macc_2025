# Project Structure Summary: Korean Petrochemical MACC Model

**Model Version**: 2.2 (Production Ready)
**Last Updated**: 2025-10-12

---

## Project Overview

**Purpose**: Optimization model to project the optimal transition pathway for Korean petrochemical sector decarbonization (2025-2050)

**Key Features**:
- ✅ All data driven by CSV files
- ✅ Interactive Streamlit dashboard
- ✅ Automatic report generation (PDF)
- ✅ Scenario optimization (Conservative, Moderate, Aggressive)
- ✅ Budget-constrained analysis
- ✅ Technology irreversibility constraints
- ✅ Time-varying prices and emission factors

---

## Data Architecture

### Input Data (CSV Files in `data/`)

All model parameters are controlled by CSV files for easy updating:

| File | Purpose | Rows | Key Columns |
|------|---------|------|-------------|
| `facility_database.csv` | 248 petrochemical facilities | 248 | company, location, product, capacity, emissions |
| `technology_parameters.csv` | 4 decarbonization technologies | 4 | CAPEX, OPEX, COP, TRL, availability year |
| `fuel_price_trajectory.csv` | Fuel prices 2025-2050 | 26 | naphtha, LNG, fuel_gas, electricity ($/GJ or $/kWh) |
| `h2_price_trajectory.csv` | Hydrogen prices 2025-2050 | 26 | year, h2_price_usd_per_kg |
| `re_price_trajectory.csv` | Renewable electricity prices | 26 | year, re_price_usd_per_mwh |
| `grid_emission_trajectory.csv` | Grid decarbonization | 51 | year, grid_ef_tco2_per_mwh |
| `ncc_lcoe_trajectory.csv` | NCC technology LCOE | 26 | baseline, NCC-H2, NCC-Elec LCOE + emission intensity |
| `emission_scenarios_clean.csv` | Target scenarios | 6 | year, Conservative, Moderate, Aggressive targets |
| `heat_pump_applicability.csv` | Heat pump limits | 3 | 2025/2030/2050 applicability % |
| `emission_factors.csv` | Fuel emission factors | 6 | fuel_type, ef_tco2_per_gj |

**Data Update Workflow**:
1. Edit CSV files in `data/` directory
2. Run optimization: `python run_all.py`
3. Dashboard automatically loads updated results
4. Report regenerates with new data

---

## Output Data (CSV Files)

### Module 1: Baseline & BAU
**Location**: `outputs/module_01/`

| File | Content |
|------|---------|
| `baseline_2025_detailed.csv` | Facility-level emissions (248 rows) |
| `bau_trajectory_2025_2050.csv` | BAU projection (26 years) |
| `emissions_by_company.csv` | Top 20 companies |
| `emissions_by_location.csv` | Regional breakdown |
| `emissions_by_product.csv` | Product category emissions |

### Module 2: MACC Analysis
**Location**: `outputs/module_02/`

| File | Content |
|------|---------|
| `macc_annual_2025_2050.csv` | **CRITICAL FILE** - Full MACC for 4 technologies × 26 years (104 rows) |

**Columns in `macc_annual_2025_2050.csv`**:
```
year, technology, available, abatement_potential_mtco2,
capex_ann_usd_per_tco2, opex_ann_usd_per_tco2, fuel_cost_diff_usd_per_tco2,
total_cost_usd_per_tco2 (MACC),
re_price_usd_per_mwh, h2_price_usd_per_kg,
lcoe_baseline_usd_per_ton, lcoe_technology_usd_per_ton, lcoe_premium_usd_per_ton,
emission_intensity_baseline, emission_intensity_technology,
methodology (Traditional vs LCOE-based),
grid_price_usd_per_mwh, grid_ef_tco2_per_mwh
```

### Module 3: Scenario Optimization
**Location**: `outputs/module_03/`

| File | Content |
|------|---------|
| `conservative_deployment.csv` | 52→20 Mt pathway (26 years) |
| `moderate_deployment.csv` | 52→10 Mt pathway (26 years) |
| `aggressive_deployment.csv` | 52→5 Mt pathway (26 years) |
| `budget_800mt_deployment.csv` | $800M budget constraint |
| `budget_1000mt_deployment.csv` | $1B budget constraint |
| `budget_1200mt_deployment.csv` | $1.2B budget constraint |
| `*_facility_allocation_2050.csv` | Company-level deployment in 2050 |

**Columns in deployment files**:
```
year, target_mt, bau_mt,
heat_pump_mt, ncc_h2_mt, ncc_elec_mt, re_ppa_mt (technology deployment),
h2_consumption_kt, electricity_consumption_increase_twh (resource tracking),
total_deployed_mt, actual_emissions_mt, shortfall_mt,
cumulative_capex_musd (investment tracking)
```

### Module 4: Financial Analysis
**Location**: `outputs/module_04/`

| File | Content |
|------|---------|
| `cash_flow_linear.csv` | Year-by-year cash flows |
| `financial_summary.csv` | NPV, IRR, payback period |

---

## Dashboard Pages (Streamlit App)

**Run**: `streamlit run app.py`

### 1. Overview
- Model summary
- Technology comparison table
- Key metrics (baseline, targets, investment)

### 2. Baseline & BAU
- 2025 baseline breakdown (by company, location, product)
- BAU trajectory 2025-2050
- Interactive charts

### 3. MACC Analysis ⭐
- **Year selector** (2025, 2030, 2040, 2050)
- **MACC waterfall chart** (cumulative abatement)
- **Cost breakdown** (CAPEX, OPEX, Fuel savings)
- **Methodology explanation** (Traditional vs LCOE)
- **Technology-by-technology table**

### 4. Scenario Explorer ⭐
- Compare 3 scenarios (Conservative, Moderate, Aggressive)
- **Emission trajectory** (interpolated, smooth)
- **Technology deployment** (stacked area chart)
- **Investment timeline** (cumulative CAPEX)
- **Resource consumption** (H2, electricity)

### 5. Company Analysis
- Top 20 companies ranked by emissions
- Company-level abatement potential
- Technology applicability by company

### 6. Regional Analysis
- Geographic distribution (map-ready data)
- Regional emission hotspots

### 7. Model Assumptions
- All parameters displayed
- Price trajectories
- Technology specifications
- References

---

## Code Structure

### Core Modules (`modules/`)

| File | Purpose |
|------|---------|
| `baseline.py` | Calculate 2025 baseline emissions |
| `bau_projection.py` | Project BAU trajectory to 2050 |
| `macc_calculator.py` | Calculate MACC for each technology |
| `optimization.py` | Optimize technology deployment pathways |
| `financial_analysis.py` | NPV, IRR, payback calculations |

### Scripts

| File | Purpose |
|------|---------|
| `run_all.py` | **Master script** - Run entire model pipeline |
| `generate_report.py` | Generate PDF report (5 pages) |
| `app.py` | Streamlit dashboard (7 pages) |

### Key Functions

**Optimization** (`modules/optimization.py`):
```python
def optimize_scenario(scenario_name, emission_targets):
    """
    Optimize technology deployment to meet emission targets

    Constraints:
    - Technology irreversibility (can't remove deployed tech)
    - NCC mutual exclusivity (H2 OR Electricity, not both)
    - Abatement potential limits
    - Annual emission targets (with linear interpolation)

    Objective: Minimize cumulative cost

    Returns: deployment_df with columns:
        year, target_mt, bau_mt, [technology]_mt,
        h2_consumption_kt, electricity_increase_twh,
        cumulative_capex_musd
    """
```

**MACC Calculation** (`modules/macc_calculator.py`):
```python
def calculate_macc(tech_name, year, prices, grid_ef):
    """
    Calculate MACC for a technology in a given year

    Category A (Heat Pump, RE PPA):
        MACC = (CAPEX_ann + OPEX_ann + ΔFuel) / Abatement

    Category B (NCC-H2, NCC-Elec):
        MACC = (LCOE_new - LCOE_baseline) / Emission_intensity

    Returns: macc_usd_per_tco2 (negative = saves money)
    """
```

---

## Technology Summary

### 1. Heat Pump
- **Target**: Low-temp processes (<165°C)
- **Potential**: 5.11 MtCO2/year
- **MACC**: -$750/tCO2 (2030) - Highly cost-negative
- **Status**: TRL 9, available 2025
- **Key Driver**: Fuel savings ($15/GJ naphtha → $6.94/GJ electricity equivalent)

### 2. RE PPA
- **Target**: All electricity consumption
- **Potential**: 7.21 Mt (2025) → 1.14 Mt (2050) - Decreases as grid cleans
- **MACC**: -$131/tCO2 (2030), -$340/tCO2 (2050)
- **Status**: TRL 9, available 2025
- **Key Driver**: Grid parity achieved 2030 ($120/MWh)

### 3. NCC-H2 (Hydrogen Cracker)
- **Target**: Naphtha crackers only
- **Potential**: 37.60 MtCO2/year
- **MACC**: $18/tCO2 (2030) → -$320/tCO2 (2050)
- **Status**: TRL 7, available 2030
- **Key Driver**: Green H2 price ($6/kg → $1.2/kg)

### 4. NCC-Electricity (E-Cracker)
- **Target**: Naphtha crackers only
- **Potential**: 37.60 MtCO2/year
- **MACC**: -$112/tCO2 (2030) → -$121/tCO2 (2050)
- **Status**: TRL 6, available 2030
- **Key Driver**: Energy efficiency + RE electricity

**Mutual Exclusivity**: NCC-H2 and NCC-Electricity compete for the same naphtha crackers. Model selects one based on cost.

---

## Model Features

### 1. Linear Interpolation (Fixed in v2.2)
**Problem**: Emission targets only at 5-year intervals (2025, 2030, 2035, 2040, 2045, 2050)

**Solution**: Interpolate targets for intermediate years
```python
target_2026 = target_2025 + (target_2030 - target_2025) * (2026 - 2025) / (2030 - 2025)
```

**Result**: Smooth emission trajectories, gradual technology deployment

### 2. Technology Irreversibility
**Constraint**: Once deployed, technologies cannot be removed (capital investment is sunk)

**Implementation**:
```python
# Each year's deployment >= previous year's deployment
deployment[year] >= deployment[year-1]
```

**Result**: Monotonically decreasing emissions (realistic)

### 3. Time-Varying Parameters
All prices and emission factors change over time:
- Fossil fuel prices: **Increasing** (+27-46%)
- RE electricity: **Decreasing** (-27%)
- Hydrogen: **Decreasing** (-43% blue, -70% green)
- Grid emission factor: **Decreasing** (0.45 → 0.25 tCO2/MWh)

**Result**: Technology economics change dramatically over time

### 4. Dual MACC Methodology
**Category A** (Heat Pump, RE PPA): Traditional MACC
```
MACC = (CAPEX_annual + OPEX_annual + ΔFuel_cost) / Abatement
```

**Category B** (NCC-H2, NCC-Elec): LCOE Premium
```
MACC = (LCOE_new - LCOE_baseline) / Emission_intensity_reduction
```

**Rationale**: Naphtha crackers are complex integrated processes. Using Levelized Cost of Ethylene (LCOE) from peer-reviewed literature is more accurate than separating CAPEX/OPEX/feedstock.

---

## Key Results (Aggressive Scenario Example)

**Emission Reduction**: 52.0 Mt (2025) → 5.0 Mt (2050) = **90.4% reduction**

**Technology Mix (2050)**:
- Heat Pump: 5.11 Mt (10.8% of total abatement)
- RE PPA: 7.09 Mt (15.0%)
- NCC-Electricity: 28.47 Mt (60.3%) - Wins over NCC-H2 due to cost
- NCC-H2: 2.61 Mt (5.5%) - Deployed in late years

**Investment**: $12.5 billion cumulative CAPEX (2025-2050)

**Resource Consumption (2050)**:
- Hydrogen: 15.9 kt/year
- Electricity increase: 13.9 TWh/year

**Cost-Effectiveness**:
- Average MACC: **-$180/tCO2** (cost-negative!)
- NPV: **+$450 billion** (25-year discounted savings)

---

## How to Use This Model

### Standard Workflow

1. **Update Input Data**
   ```bash
   # Edit CSV files in data/
   nano data/fuel_price_trajectory.csv
   nano data/emission_scenarios_clean.csv
   ```

2. **Run Optimization**
   ```bash
   python run_all.py
   ```
   This generates:
   - Module 1 outputs (baseline, BAU)
   - Module 2 outputs (MACC)
   - Module 3 outputs (scenarios)
   - Module 4 outputs (financial)

3. **Generate Report**
   ```bash
   python generate_report.py
   ```
   Output: `outputs/reports/MACC_Report_YYYYMMDD_HHMM.pdf`

4. **Launch Dashboard**
   ```bash
   streamlit run app.py
   ```
   Browser opens at `http://localhost:8501`

### Custom Analysis

**Add a New Scenario**:
1. Edit `data/emission_scenarios_clean.csv`
2. Add column: `My_Scenario,48,42,36,30,24,18`
3. Rerun optimization
4. Results appear in dashboard

**Change Technology Parameters**:
1. Edit `data/technology_parameters.csv`
2. Change CAPEX/OPEX/COP values
3. Rerun: MACC automatically recalculated

**Test Sensitivity**:
1. Create multiple CSV versions (e.g., `fuel_price_high.csv`)
2. Run optimization for each
3. Compare outputs in Excel

---

## Data Sources & References

All assumptions are based on peer-reviewed literature:

1. **LCOE Data**: Woo et al. (2025), Green Chemistry, DOI:10.1039/D4GC04538F
2. **H2 Prices**: IEA Hydrogen Strategy (2021)
3. **RE Prices**: IRENA Renewable Power Generation Costs (2023)
4. **Grid Factor**: Korea 10th Basic Power Supply Plan (2023)
5. **Heat Pump COP**: IEA Heat Pumps Technology Collaboration Programme (2022)
6. **Baseline Emissions**: Company ESG reports, Korea Petrochemical Association (2023)

---

## Files for External Analysis

If you want to analyze MACC in detail using another AI or Excel:

**Export these CSV files**:
1. `outputs/module_02/macc_annual_2025_2050.csv` - Complete MACC data
2. `data/technology_parameters.csv` - Tech specs
3. `data/ncc_lcoe_trajectory.csv` - LCOE trajectories
4. `data/fuel_price_trajectory.csv` - Fuel prices
5. `data/h2_price_trajectory.csv` - H2 prices
6. `data/re_price_trajectory.csv` - RE prices

**Use the AI Prompt**: `AI_PROMPT_MACC_BREAKDOWN.md`

This prompt provides full context for deep-dive MACC analysis in another AI (Claude, GPT-4, etc.)

---

## Model Status

**Version**: 2.2 (Production)
**Status**: ✅ Production Ready

**Completed**:
- ✅ Interpolation bug fixed (smooth trajectories)
- ✅ Report methodology page added
- ✅ Dashboard MACC analysis enhanced
- ✅ LaTeX paper updated
- ✅ Korean documentation created (28 KB)
- ✅ All data CSV-driven
- ✅ Dashboard fully functional

**Validation**:
- ✅ Baseline matches company ESG reports
- ✅ MACC values consistent with literature
- ✅ Scenario trajectories smooth and realistic
- ✅ Investment costs reasonable ($12-20B for 90% reduction)

**Ready For**:
- ✅ Academic publication (Applied Energy, Energy Policy)
- ✅ Policy discussion (Korean government, petrochemical industry)
- ✅ Public release (GitHub, dashboard deployment)

---

**Created**: 2025-10-12
**Model Version**: 2.2
**Purpose**: Project structure overview for continued development
