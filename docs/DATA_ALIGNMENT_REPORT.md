# Data & Documentation Alignment Report

## 1. Hardcoded Values Audit

### ✅ Resolved (Now in CSV)
| Value | Location | CSV Column | Status |
|-------|----------|------------|--------|
| 0.127 | utils.py | `h2_demand_factor_per_tco2` | ✅ Fixed |
| 3.18 | utils.py | `elec_demand_factor_per_tco2` | ✅ Fixed |
| 0.93 | utils.py | `energy_conversion_efficiency` | ✅ Fixed |
| 4.0 | utils.py | `cop` | ✅ Already in CSV |
| 0.08 | run_scenarios.py | `discount_rate` | ✅ Fixed |

### ⚠️ Fallback Values (Acceptable)
| Value | Location | Purpose |
|-------|----------|---------|
| 0.127 | utils.py:441 | Fallback if CSV missing |
| 3.18 | utils.py:448 | Fallback if CSV missing |
| 0.93 | utils.py:434 | Fallback if CSV missing |
| 0.08 | run_scenarios.py:243 | Fallback if CSV missing |

### 📍 Physical Constants (Keep Hardcoded)
| Value | Location | Meaning |
|-------|----------|---------|
| 3.6 | utils.py | GJ to MWh conversion factor |
| 1000 | Multiple | kt to tonnes conversion |
| 1e6, 1e9 | utils.py | Number formatting thresholds |

---

## 2. CSV vs Documentation Alignment

### technology_parameters.csv

| CSV Column | Value (NCC-H2) | Documented in .md? | Notes |
|------------|---------------|-------------------|-------|
| `cop` | 4.0 | ✅ Yes | ASSUMPTIONS_AND_METHODOLOGY.md §3.3 |
| `h2_ton_per_ton_ethylene` | 0.2 | ✅ Yes | Documented as "0.2 t-H2/t-C2H4" |
| `elec_mwh_per_ton_ethylene` | 5.0 | ✅ Yes | Documented as "5.0 MWh/t-C2H4" |
| `energy_conversion_efficiency` | 0.85/0.93/0.95 | ✅ Yes | Documented per technology |
| `h2_demand_factor_per_tco2` | 0.127 | ❌ **Missing** | NEW column - needs documentation |
| `elec_demand_factor_per_tco2` | 3.18 | ❌ **Missing** | NEW column - needs documentation |
| `capex_2025_musd_per_mtco2` | 1700 | ✅ Yes | Table in §3.2 |
| `opex_pct_capex` | 4.0 | ✅ Yes | Documented |
| `lifetime_years` | 25 | ✅ Yes | Documented |
| `available_year` | 2030 | ✅ Yes | Documented |
| `trl` | 7 | ✅ Yes | Table in §3.1 |

### emission_factors.csv

| CSV Column | Value | Documented? | Notes |
|------------|-------|-------------|-------|
| Naphtha | 0.0542 tCO2/GJ | ✅ Yes | ASSUMPTIONS_AND_METHODOLOGY.md §7.2 |
| LNG | 0.0561 tCO2/GJ | ✅ Yes | §7.2 |
| Fuel_Gas | 0.050 tCO2/GJ | ✅ Yes | §7.2 |
| Byproduct_Gas | 0.048 tCO2/GJ | ✅ Yes | §7.2 |
| LPG | 0.0631 tCO2/GJ | ✅ Yes | §7.2 |
| Fuel_Oil | 0.0773 tCO2/GJ | ✅ Yes | §7.2 |
| Diesel | 0.0741 tCO2/GJ | ✅ Yes | §7.2 |
| Electricity | 0.436 tCO2/MWh | ✅ Yes | §5.1 (2025 value) |
| H2 | 0.0 tCO2/kg | ✅ Yes | §7.2 |

### asset_valuation_params.csv

| CSV Column | Value | Documented? | Notes |
|------------|-------|-------------|-------|
| `overnight_capex_usd_per_ton` | 1500 (NCC) | ❌ **Missing** | Not in main docs |
| `useful_life_years` | 40 | ✅ Partially | Referenced indirectly |
| `discount_rate` | 0.05 | ⚠️ **Mismatch** | Docs say 8% (§7.5), CSV has 5% |

### carbon_budget_scenarios.csv

| Scenario | 2025 Limit | Documented? |
|----------|------------|-------------|
| 1.5C | 50 Mt | ❌ **Missing** | Not detailed in docs |
| 2.0C | 60 Mt | ❌ **Missing** | Not detailed in docs |
| NDC | 70 Mt | ❌ **Missing** | Not detailed in docs |

### Price Trajectories

| File | 2025 Value | Documented? |
|------|------------|-------------|
| h2_price_trajectory.csv | $4.58/kg | ✅ Yes | §4.2 |
| re_price_trajectory.csv | $65/MWh | ✅ Yes | §4.1 |
| grid_price_trajectory.csv | $100/MWh | ✅ Yes | §4.3 |
| grid_emission_trajectory.csv | 0.436 tCO2/MWh | ✅ Yes | §5.1 |
| fuel_price_trajectory.csv | $15/GJ (Naphtha) | ❌ **Missing** | Not documented |

---

## 3. Summary: Missing Documentation

| Data | CSV File | Needs Documentation? |
|------|----------|---------------------|
| `h2_demand_factor_per_tco2` (0.127) | technology_parameters.csv | ✅ **Yes** - New column |
| `elec_demand_factor_per_tco2` (3.18) | technology_parameters.csv | ✅ **Yes** - New column |
| Carbon budget limits (50/60/70 Mt) | carbon_budget_scenarios.csv | ✅ **Yes** - No detail |
| Asset CAPEX ($1500/ton) | asset_valuation_params.csv | ✅ **Yes** - Source needed |
| Fuel price trajectory | fuel_price_trajectory.csv | ✅ **Yes** - No documentation |
| Discount rate (5% vs 8%) | asset_valuation_params.csv | ⚠️ **Mismatch** - Clarify |

---

## 4. Recommendations

1. **Add documentation for new CSV columns:**
   - `h2_demand_factor_per_tco2` = 0.127 (derived from 0.2 t-H2/t-C2H4 × conversion)
   - `elec_demand_factor_per_tco2` = 3.18 (derived from 5.0 MWh/t-C2H4 × conversion)

2. **Clarify discount rate discrepancy:**
   - CSV: 5% (asset_valuation_params.csv)
   - Docs: 8% (ASSUMPTIONS_AND_METHODOLOGY.md §7.5)

3. **Document carbon budget sources:**
   - Add scientific reference for 1.5C/2.0C/NDC budget values

4. **Document fuel price assumptions:**
   - Add fuel_price_trajectory.csv details to docs (currently constant $15/GJ)

---

## 5. EXPANDED: Complete Missing Documentation List

### 5.1 Demand/Scenario Files (data/scenarios/)

| File | Column | Value | Documented? | Notes |
|------|--------|-------|-------------|-------|
| `emission_targets.csv` | reduction_target_pct | 0→15%→24.5%→50%→75%→100% | ❌ **Missing** | NDC/policy basis not explained |
| `demand_growth_trajectory_shaheen.csv` | cumulative_capacity_multiplier | 1.0→1.15 | ❌ **Missing** | Why 15% capacity increase in 2026? |
| `demand_growth_trajectory_shaheen.csv` | operating_rate_pct | 70.0 | ⚠️ Partial | Mentioned but no source |
| `demand_growth_trajectory_restructure_25pct.csv` | All columns | Declining capacity | ❌ **Missing** | No retirement timeline docs |
| `scenario_definitions.csv` | production | shaheen/restructure | ⚠️ Partial | Scenarios listed but logic not detailed |

### 5.2 Technology Parameters (data/assumptions/technology_parameters.csv)

| Column | Value | Documented? | Document Location |
|--------|-------|-------------|-------------------|
| `cop` | 4.0 | ✅ Yes | ASSUMPTIONS_AND_METHODOLOGY.md §3.3 |
| `h2_ton_per_ton_ethylene` | 0.2 | ✅ Yes | §3.3 |
| `elec_mwh_per_ton_ethylene` | 5.0 | ✅ Yes | §3.3 |
| `energy_conversion_efficiency` | 0.85/0.93/0.95 | ✅ Yes | §3.3 |
| `h2_demand_factor_per_tco2` | 0.127 | ❌ **NEW - Missing** | Derivation formula needed |
| `elec_demand_factor_per_tco2` | 3.18 | ❌ **NEW - Missing** | Derivation formula needed |
| `trl` | 7/8/9 | ✅ Yes | §3.1 |
| `available_year` | 2025/2026/2030 | ✅ Yes | §3.1 |
| `capex_*` columns | Multiple | ✅ Yes | §3.2 |
| `opex_pct_capex` | 3.0/4.0 | ✅ Yes | §3.3 |
| `lifetime_years` | 20/25 | ✅ Yes | §3.3 |

### 5.3 Asset Valuation (data/assumptions/asset_valuation_params.csv)

| Column | Value | Documented? | Notes |
|--------|-------|-------------|-------|
| `overnight_capex_usd_per_ton` | 500-1500 | ❌ **Missing** | No source for NCC=$1500, BTX=$800 |
| `useful_life_years` | 30/40 | ⚠️ Partial | Referenced but no source |
| `discount_rate` | 0.05 | ⚠️ **MISMATCH** | Docs say 8%, CSV has 5% |

### 5.4 Carbon Budgets (data/assumptions/carbon_budget_scenarios.csv)

| Column | 2025 Value | Documented? | Notes |
|--------|------------|-------------|-------|
| `budget_1.5C_tco2` | 50,000,000 | ❌ **Missing** | No IPCC/IEA source cited |
| `budget_2.0C_tco2` | 60,000,000 | ❌ **Missing** | No source |
| `budget_NDC_tco2` | 70,000,000 | ❌ **Missing** | Korea NDC basis not explained |

### 5.5 Price Trajectories (data/assumptions/prices/)

| File | 2025 Value | Documented? | Notes |
|------|------------|-------------|-------|
| `h2_price_trajectory.csv` | $4.58/kg | ✅ Yes | LCOH formula in docs |
| `re_price_trajectory.csv` | $65/MWh | ✅ Yes | IRENA/IEA sources cited |
| `grid_price_trajectory.csv` | $100/MWh | ✅ Yes | §4.3 |
| `grid_emission_trajectory.csv` | 0.436 tCO2/MWh | ✅ Yes | §5.1 |
| `fuel_price_trajectory.csv` | All constant | ❌ **Missing** | Why no price changes 2025-2050? |

### 5.6 Product Benchmarks (data/assumptions/product_benchmarks.csv)

| Data | Documented? | Document |
|------|-------------|----------|
| Ethylene energy intensity | ✅ Yes | ENERGY_INTENSITY_SOURCES.md |
| Propylene energy intensity | ✅ Yes | ENERGY_INTENSITY_SOURCES.md |
| Butadiene energy intensity | ✅ Yes | ENERGY_INTENSITY_SOURCES.md |
| BTX energy intensity | ✅ Yes | ENERGY_INTENSITY_SOURCES.md |
| Polymer energy intensity | ⚠️ Partial | Generic values, few sources |

### 5.7 Emission Factors (data/assumptions/emission_factors.csv)

| Fuel | Documented? | Source in Docs |
|------|-------------|----------------|
| All fuels | ✅ Yes | IPCC 2019/API 2021 cited in §7.2 |

---

## 6. Summary: Priority Documentation Gaps

| Priority | Data Item | Status |
|----------|-----------|--------|
| 🔴 High | Discount rate (5% vs 8%) | Inconsistent |
| 🔴 High | Carbon budget sources (1.5C/2.0C/NDC) | Missing |
| 🔴 High | Demand trajectory capacity multipliers | Missing |
| 🟡 Medium | Emission reduction target pathway | Source missing |
| 🟡 Medium | CAPEX per ton ($1500 NCC) | Source missing |
| 🟡 Medium | Fuel price trajectories (constant) | Explanation missing |
| 🟢 Low | Conversion factors (0.127, 3.18) | Need derivation formula |
| 🟢 Low | Polymer energy intensities | Need more sources |
