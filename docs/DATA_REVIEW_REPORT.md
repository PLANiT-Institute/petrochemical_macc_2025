# Project Data Completeness Review

## Data Availability Checklist

### ✅ 1-2-1. Total Energy Consumption
**Available in:**
- `outputs/energy_emission_analysis.csv` - Calculated per facility
- Derived from `product_benchmarks.csv` × `facility_database_with_regions.csv`

### ✅ 1-2-2. Product Output by Facility
**Available in:**
- `data/assets/facility_database_with_regions.csv` - `capacity_kt` column
- `outputs/scenario_results.csv` - `production_t` column (capacity × operating rate)

### ✅ 1-2-3. Energy Consumption by Product
**Available in:**
- `data/assumptions/product_benchmarks.csv` - Energy intensity by product/process
  - Columns: `Naphtha_GJ_per_tonne`, `Electricity_kWh_per_tonne`, `LNG_GJ_per_tonne`, etc.

### ✅ 1-2-4. GHG Emission Factors by Energy Source
**Available in:**
- `data/assumptions/emission_factors.csv`
  - 9 fuel types with `tCO2_per_GJ`, `tCO2_per_kWh` values
  - Sources: IPCC 2019, API Compendium 2021

### ✅ 1-2-5. Carbon Budget Pathways
**Available in:**
- `data/assumptions/carbon_budget_scenarios.csv`
  - 3 scenarios: 1.5°C, 2.0°C, NDC
  - Annual limits from 2025-2050

### ✅ 1-2-6. Costs & Energy Consumption by Mitigation Measures
**Available in:**
- `data/assumptions/technology_parameters.csv`
  - 5 technologies: Heat_Pump, NCC-H2, NCC-Electricity, RE_PPA, RDH
  - CAPEX (2025-2050), OPEX%, COP, H2 consumption, Electricity consumption

### ✅ 1-2-7. Key Energy Price Outlook
**Available in:**
- `data/assumptions/prices/h2_price_trajectory.csv` - H2 prices 2025-2050
- `data/assumptions/prices/re_price_trajectory.csv` - Renewable prices 2025-2050
- `data/assumptions/prices/grid_price_trajectory.csv` - Grid electricity prices
- `data/assumptions/prices/grid_emission_trajectory.csv` - Grid EF trajectory
- `data/assumptions/prices/fuel_price_trajectory.csv` - Fuel prices

---

## 🐛 Potential Bugs / Issues Identified

### 1. Hardcoded Discount Rate
- **File:** `run_scenarios.py`, Line 237
- **Issue:** `DISCOUNT_RATE = 0.08` is hardcoded
- **Recommendation:** Move to `asset_valuation_params.csv` (already has a `discount_rate` column but unused)

### 2. Constant Fuel Prices
- **File:** `data/assumptions/prices/fuel_price_trajectory.csv`
- **Issue:** All fuel prices are constant from 2025-2050 (no trajectory)
- **Impact:** May not reflect real-world fuel price changes
- **Recommendation:** Confirm if intentional or needs updating with IEA projections

### 3. Negative Remaining Life Values
- **File:** `data/assets/facility_database_with_regions.csv`
- **Issue:** Some facilities have `remaining_life < 0` (e.g., -6, -13)
- **Impact:** Already depreciated but still in database. Book value = $0 (handled correctly)
- **Recommendation:** Review if these should be excluded from analdysis

### 4. Unused `discount_rate` in Valuation Params
- **File:** `data/assumptions/asset_valuation_params.csv`
- **Issue:** Has `discount_rate` column (0.05) but code uses hardcoded 0.08
- **Recommendation:** Use CSV value or remove unused column

---

## Summary
| Category | Status | Source File |
|----------|--------|-------------|
| Energy Consumption | ✅ | `product_benchmarks.csv` |
| Product Output | ✅ | `facility_database_with_regions.csv` |
| Energy by Product | ✅ | `product_benchmarks.csv` |
| GHG Emission Factors | ✅ | `emission_factors.csv` |
| Carbon Budgets | ✅ | `carbon_budget_scenarios.csv` |
| Technology Costs | ✅ | `technology_parameters.csv` |
| Energy Prices | ✅ | `prices/*.csv` |

**All 7 data categories are available in CSV files.** 4 potential issues identified for review.
