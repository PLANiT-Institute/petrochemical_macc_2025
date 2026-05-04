# Korea Petrochemical MACC Model - Complete Reference

#petrochemical #macc #decarbonization #korea #model #net-zero

---

## Overview

This document provides a comprehensive reference for the **Korea Petrochemical Net Zero Pathway Analysis** model, covering decarbonization pathways for Korea's petrochemical industry from 2025 to 2050.

### Key Metrics at a Glance
| Metric | Value |
|--------|-------|
| Analysis Period | 2025-2050 (26 years) |
| Baseline Facilities | 237 |
| With Shaheen Expansion | 243 |
| Total Capacity | 100,066 kt/year |
| Baseline Emissions | 47.0 MtCO2/year |
| Target | Net Zero by 2050 |
| Investment Range | $21.8B - $41.7B |

---

## 10-Step Project Understanding

### Step 1: Project Purpose & Scope
**Korea Petrochemical Net Zero Pathway Analysis (2025-2050)**

This model evaluates decarbonization pathways for Korea's petrochemical industry through facility-level cost-optimized analysis. The analysis develops Marginal Abatement Cost (MACC) curves across 6 distinct scenarios combining different production pathways and green technologies.

**Key Constraints:**
- No CCS/CCUS technologies - focus purely on electrification and green hydrogen
- Complete grid decarbonization assumed by 2050 (Grid EF = 0)
- 70% constant operating rate throughout analysis period

---

### Step 2: Scenario Framework

**6 Scenarios = 3 Production Pathways × 2 NCC Technologies**

#### Production Pathways
| Pathway | Description | Capacity Impact |
|---------|-------------|-----------------|
| **Shaheen (Growth)** | +6 new S-Oil facilities from 2026 | +3.9% capacity (243 facilities) |
| **Restructure 25%** | Retire 25% oldest NCC capacity | -25% NCC capacity |
| **Restructure 40%** | Retire 40% oldest NCC capacity | -40% NCC capacity |

#### NCC Technology Options
| Technology | Description | Energy Source |
|------------|-------------|---------------|
| **NCC-H2** | Green hydrogen furnaces | 0.2 t-H2/t-C2H4 |
| **NCC-Electricity** | Electric crackers (eFurnace) | 5.0 MWh/t-C2H4 |

#### Combined Scenarios
| # | Scenario ID | Production | Technology | Investment |
|---|-------------|------------|------------|------------|
| 1 | shaheen_ncc_h2 | Growth | NCC-H2 | ~$41.7B |
| 2 | shaheen_ncc_elec | Growth | NCC-Electricity | ~$41.4B |
| 3 | restructure_25pct_ncc_h2 | -25% | NCC-H2 | ~$22.8B |
| 4 | restructure_25pct_ncc_elec | -25% | NCC-Electricity | ~$22.5B |
| 5 | restructure_40pct_ncc_h2 | -40% | NCC-H2 | ~$22.3B |
| 6 | restructure_40pct_ncc_elec | -40% | NCC-Electricity | ~$21.8B |

---

### Step 3: Facility Database Structure

**Location:** `data/assets/`

#### Files
- `facility_database_with_regions.csv`: 237 baseline facilities
- `facility_database_with_shaheen.csv`: 243 facilities (includes Shaheen)
- `region_mapping.csv`: Location to region aggregation

#### Database Schema
| Column | Type | Description |
|--------|------|-------------|
| product | string | Primary product (Ethylene, Propylene, Benzene, etc.) |
| process | string | Process type (Naphtha Cracker, BTX Plant, etc.) |
| company | string | Operating company name |
| location | string | Specific facility location |
| region | string | Aggregated region |
| capacity_kt | float | Annual production capacity (kilotons) |
| year_built | integer | Commissioning year |
| age_2025 | integer | Age of facility in 2025 |
| remaining_life | integer | Remaining economic life (40-year assumption) |

#### Regional Distribution
| Region | Facilities | Capacity (kt) | Share |
|--------|-----------|---------------|-------|
| Yeosu Complex | 87 | 37,216 | 37.2% |
| Ulsan Complex | 85 | 31,436 | 31.4% |
| Daesan Complex | 57 | 27,424 | 27.4% |
| Other Regions | 19 | 3,990 | 4.0% |

#### Major Products
| Product | Facilities | Capacity (kt) |
|---------|-----------|---------------|
| Ethylene | 11 | 13,317 |
| P-Xylene | 8 | 10,790 |
| Propylene | 15 | 10,746 |
| Benzene | 19 | 8,612 |
| PP | 15 | 7,394 |

---

### Step 4: Technology Portfolio

**Location:** `data/assumptions/technology_parameters.csv`

#### Technology Summary
| Technology | Application | CAPEX 2025 | CAPEX 2050 | Availability | TRL |
|------------|-------------|------------|------------|--------------|-----|
| **Heat Pump** | Low-temp (<165°C) | $800M/MtCO2 | $400M/MtCO2 | 2025 | 9 |
| **NCC-H2** | Naphtha crackers | $1,700M/MtCO2 | $850M/MtCO2 | 2030 | 7 |
| **NCC-Electricity** | Naphtha crackers | $1,500M/MtCO2 | $750M/MtCO2 | 2030 | 8 |
| **RDH** | High-temp BTX | $900M/MtCO2 | $450M/MtCO2 | 2026 | 8 |
| **RE-PPA** | All electricity | $0 | $0 | 2025 | N/A |

**Key Assumption:** All technologies follow 50% CAPEX reduction learning curve by 2050

#### Technology Details

##### Heat Pump
- **COP (Coefficient of Performance):** 4.0
- **Application:** Low-temperature heat (<165°C)
- **Energy conversion efficiency:** 95%
- **OPEX:** 3% of CAPEX annually
- **Lifetime:** 20 years
- **Source:** Kosmadakis 2020

##### NCC-H2 (Green Hydrogen Furnaces)
- **H2 consumption:** 0.2 t-H2 per t-C2H4 (ethylene)
- **Energy conversion efficiency:** 85%
- **OPEX:** 4% of CAPEX annually
- **Lifetime:** 25 years
- **Application:** 85% of NCC furnace emissions
- **Source:** Lummus Tech 2023, Thunder Said Energy 2023

##### NCC-Electricity (Electric Crackers)
- **Electricity consumption:** 5.0 MWh per t-C2H4
- **Energy conversion efficiency:** 95%
- **OPEX:** 4% of CAPEX annually
- **Lifetime:** 25 years
- **Source:** BASF/SABIC/Linde eFurnace specifications

##### RDH (RotoDynamic Heater)
- **Application:** High-temperature BTX reforming (>400°C)
- **Energy conversion efficiency:** 93%
- **OPEX:** 3% of CAPEX annually
- **Lifetime:** 25 years
- **Source:** Coolbrook technology specifications

##### RE-PPA (Renewable Power Purchase Agreement)
- **CAPEX:** $0 (contract-based procurement)
- **OPEX:** $0 (included in PPA pricing)
- **RE lifecycle emissions:** 0.05 tCO2/MWh

#### Technology Application Logic
```
┌─────────────────────────────────────────────────────────────────┐
│                TECHNOLOGY APPLICATION BY FACILITY TYPE           │
├─────────────────────────────────────────────────────────────────┤
│ 1. NCC FACILITIES (Naphtha Cracker)                             │
│    Primary: NCC-H2 or NCC-Electricity (scenario-dependent)      │
│    Secondary: Heat Pump (for non-naphtha fuels)                 │
│                                                                 │
│ 2. BTX FACILITIES (Benzene, Toluene, Xylene)                    │
│    Technology: RDH (RotoDynamic Heater)                         │
│    Reason: High-temp >400°C, Heat Pump not applicable           │
│                                                                 │
│ 3. OTHER FACILITIES (Polymers, Derivatives, etc.)               │
│    Technology: Heat Pump                                        │
│    COP 4.0: 1 MWh electricity → 4 MWh heat                     │
│                                                                 │
│ 4. ALL FACILITIES (Electricity Emissions)                       │
│    Technology: RE-PPA (Renewable Power Purchase)                │
│    Grid decarbonization: 0.436 (2025) → 0.0 (2050) tCO2/MWh    │
└─────────────────────────────────────────────────────────────────┘
```

---

### Step 5: Price Trajectories

**Location:** `data/assumptions/prices/`

#### Renewable Electricity Price (RE-PPA)
Based on IRENA 2024 and IEA WEO 2024:

| Year | RE Price ($/MWh) |
|------|------------------|
| 2025 | 65.00 |
| 2030 | 55.69 |
| 2040 | 40.87 |
| 2050 | 30.00 |

**Decline rate:** 54% reduction from 2025 to 2050

#### Grid Electricity Price
| Year | Grid Price ($/MWh) | Notes |
|------|-------------------|-------|
| 2025 | 100.00 | Korea industrial rate |
| 2030 | 118.28 | Transition period |
| 2040 | 154.83 | Grid modernization costs |
| 2050 | 191.38 | Full decarbonization achieved |

**Note:** Grid price increases reflect infrastructure investment costs for decarbonization.

#### Green Hydrogen Price (LCOH-Derived)
**Critical: H2 price is calculated from RE price via LCOH formula.**

```
LCOH = (CAPEX × CRF + OPEX + Stack_Replacement) / Annual_H2_Production + Electricity_Cost

Where:
- CRF = Capital Recovery Factor (8% discount rate, 20-year lifetime)
- Electricity consumption = 39.4 kWh/kg H2 (HHV) ÷ Efficiency
- Capacity factor = 90%
```

| Year | H2 Price ($/kg) | RE Price | Electrolyzer CAPEX | Efficiency |
|------|-----------------|----------|-------------------|------------|
| 2025 | 4.58 | $65/MWh | $1,000/kW | 70% |
| 2030 | 3.91 | $56/MWh | $900/kW | 71% |
| 2035 | 3.33 | $48/MWh | $800/kW | 72% |
| 2040 | 2.82 | $41/MWh | $700/kW | 73% |
| 2045 | 2.39 | $35/MWh | $600/kW | 74% |
| 2050 | 2.01 | $30/MWh | $500/kW | 75% |

**Decline rate:** 56% reduction from 2025 to 2050

#### Fuel Prices (Constant 2025-2050)
| Fuel | Price | Unit |
|------|-------|------|
| Naphtha | $15.0 | USD/GJ |
| LNG | $12.0 | USD/GJ |
| Fuel Gas | $10.0 | USD/GJ |
| LPG | $14.0 | USD/GJ |
| Fuel Oil | $13.0 | USD/GJ |
| Diesel | $16.0 | USD/GJ |

---

### Step 6: Emission Calculation Methodology

**Location:** `modules/utils.py` - EmissionCalculator class

#### Baseline Emissions Formula
```
Total Emissions = Combustion Emissions + Electricity Emissions

Combustion Emissions = Σ(Fuel_i_GJ × Emission_Factor_i_tCO2/GJ)
Electricity Emissions = MWh × Grid_EF_tCO2/MWh
```

#### Emission Factors
| Source | Emission Factor | Unit | Reference |
|--------|-----------------|------|-----------|
| Naphtha | 0.0542 | tCO2/GJ | IPCC 2019, Table 2.3 |
| LNG | 0.0561 | tCO2/GJ | IPCC 2019, Table 2.3 |
| Fuel Gas | 0.050 | tCO2/GJ | API Compendium 2021 |
| Byproduct Gas | 0.048 | tCO2/GJ | API Compendium 2021 |
| LPG | 0.0631 | tCO2/GJ | IPCC 2019, Table 2.3 |
| Fuel Oil | 0.0773 | tCO2/GJ | IPCC 2019, Table 2.3 |
| Diesel | 0.0741 | tCO2/GJ | IPCC 2019, Table 2.3 |
| Grid Electricity | 0.436 (2025) | tCO2/MWh | Korea Grid 2025 |
| Green H2 | 0.0 | tCO2/kg | Zero-emission electrolysis |

#### Calculation Steps
1. **Production** = capacity_kt × 1000 × operating_rate × capacity_multiplier
2. **For each fuel:**
   - Energy = Intensity_per_tonne × Production_tonnes
   - Emissions = Energy × Emission_Factor
3. **Separate tracking:** combustion emissions vs electricity emissions

---

### Step 7: MACC/LCOA Optimization Logic

**Location:** `run_scenarios.py`

#### MAC (Marginal Abatement Cost) Formula
```
MAC ($/tCO2) = Annual Total Cost / Abatement Potential

Where:
Annual Total Cost = Annualized CAPEX + Annual OPEX + New Energy Cost - Fuel Savings

Annualized CAPEX = Total CAPEX / Lifetime_years
Annual OPEX = Total CAPEX × (opex_pct_capex / 100)
New Energy Cost = H2_cost + Electricity_cost
Fuel Savings = Σ(Energy_by_source × Fuel_Price)
```

#### LCOA (Levelized Cost of Abatement) Formula
For intertemporal optimization:

```
LCOA_t ($/tCO2) = NPV(Annual Costs from year t to 2050) / Total Abatement

Where:
NPV = Σ[(Annual_Cost_n) / (1 + r)^(n-t)] for n = t to 2050
Total_Abatement = Σ[Abatement_n] for n = t to 2050
r (Discount Rate) = 8%
```

#### Optimization Algorithm
For each year (2025-2050):
1. Calculate baseline emissions (BAU) for all facilities
2. Determine current emissions based on deployment status
3. Calculate emission gap = Current_Emissions - Target_Emissions
4. If gap > 0:
   - Calculate LCOA for all undeployed facilities
   - Rank by LCOA (cheapest first)
   - Deploy facilities until gap ≤ 0
5. Record annual results

#### Cost Breakdown Example (NCC-H2, 1000 kt ethylene facility, 2025)
```
Annual Production = 1,000 kt × 70% = 700 kt
H2 Required = 700 kt × 0.2 t-H2/t-C2H4 = 140 kt H2

Total CAPEX = $1,700M/MtCO2 × 1.1 MtCO2 = $1,870M
Annual CAPEX = $1,870M / 25 years = $74.8M
Annual OPEX = $1,870M × 4% = $74.8M
H2 Cost = 140 kt × $4.58/kg × 1000 = $640M
Fuel Savings = ~$203M (avoided naphtha)

Total Annual Cost = $74.8M + $74.8M + $640M - $203M = $587M
MAC = $587M / 1.1 MtCO2 = $534/tCO2
```

---

### Step 8: Grid Decarbonization Trajectory

**Location:** `data/assumptions/prices/grid_emission_trajectory.csv`

| Year | Grid EF (tCO2/MWh) | Reduction from 2025 |
|------|-------------------|---------------------|
| 2025 | 0.436 | Baseline |
| 2030 | 0.349 | -20% |
| 2035 | 0.244 | -44% |
| 2040 | 0.140 | -68% |
| 2045 | 0.070 | -84% |
| 2050 | 0.000 | -100% (Net Zero) |

**Implications:**
- **2025-2049:** RE-PPA provides emission reduction by switching from grid to renewable electricity
- **2050:** Grid EF = 0, so RE-PPA provides no additional abatement (grid is already clean)
- RE-PPA covers both existing electricity consumption and new demand from electrification

---

### Step 9: Data Architecture

```
data/
├── assets/                          # Facility databases
│   ├── facility_database_with_regions.csv    (237 facilities)
│   ├── facility_database_with_shaheen.csv    (243 facilities)
│   └── region_mapping.csv                    (location→region)
│
├── assumptions/                     # Technology & price parameters
│   ├── technology_parameters.csv    (5 technologies, CAPEX learning curves)
│   ├── emission_factors.csv         (8 fuels, IPCC factors)
│   ├── product_benchmarks.csv       (58 product-process energy intensities)
│   ├── asset_valuation_params.csv   (depreciation, discount rates)
│   ├── carbon_budget_scenarios.csv  (1.5°C, 2.0°C, NDC budgets)
│   └── prices/
│       ├── h2_price_trajectory.csv          (LCOH-derived, 2025-2050)
│       ├── re_price_trajectory.csv          (IRENA 2024 based)
│       ├── grid_price_trajectory.csv        (Korea industrial)
│       ├── grid_emission_trajectory.csv     (decarbonization path)
│       └── fuel_price_trajectory.csv        (constant prices)
│
└── scenarios/                       # Scenario configurations
    ├── scenario_definitions.csv             (6 scenarios)
    ├── emission_targets.csv                 (Net Zero pathway)
    ├── demand_growth_trajectory_shaheen.csv
    ├── demand_growth_trajectory_restructure_25pct.csv
    └── demand_growth_trajectory_restructure_40pct.csv
```

---

### Step 10: Output & Visualization

#### Output Files (`outputs/`)
| File | Description |
|------|-------------|
| `scenario_results.csv` | Combined results (all scenarios, all years, all facilities) |
| `regional_mac_summary.csv` | Regional aggregates by scenario/year |
| `regional_abatement_summary.csv` | Regional emissions/abatement |
| `stranded_assets_summary.csv` | Stranded asset analysis |
| `{scenario_name}.csv` | Individual scenario files (6 files) |

#### Output Schema (scenario_results.csv)
| Column | Description |
|--------|-------------|
| year | Simulation year (2025-2050) |
| scenario | Scenario name |
| facility_id | Unique facility identifier |
| product | Product type |
| process | Process type |
| region | Regional complex |
| capacity_kt | Facility capacity |
| production_tonnes | Annual production |
| bau_emissions_tco2 | Baseline emissions |
| emissions_tco2 | Actual emissions |
| abatement_tco2 | Emission reduction |
| technology | Deployed technology |
| install_year | Technology deployment year |
| capex_total_usd | Total capital cost |
| capex_annual_usd | Annualized capital cost |
| opex_annual_usd | Annual operating cost |
| new_energy_cost_usd | New energy costs (H2/electricity) |
| fuel_savings_usd | Avoided fuel costs |
| total_cost_usd | Net annual cost |
| mac_usd_per_tco2 | Marginal abatement cost |
| electricity_mwh | Electricity demand |
| h2_demand_tonnes | Hydrogen demand |

#### Visualization Dashboard (`streamlit_app.py`)
**Pages:**
1. **Regional Outlook** - Regional metrics, H2 demand, cost pathways
2. **Scenario Comparison** - Summary cards, bar charts, MACC curves
3. **Stranded Assets** - Facility-level stranded asset analysis
4. **Technology Details** - Technology parameters, CAPEX evolution
5. **Facility Results** - Searchable facility table with detailed results
6. **Energy Infrastructure** - Electricity and H2 demand by scenario

---

## Key Assumptions Summary

### Energy & Technology Assumptions
| Assumption | Value | Source |
|------------|-------|--------|
| Facility useful life | 40 years | Industry standard |
| Heat pump COP | 4.0 | Kosmadakis 2020 |
| NCC-H2 consumption | 0.2 t-H2/t-C2H4 | Lummus Tech 2023 |
| NCC-Electricity consumption | 5.0 MWh/t-C2H4 | BASF/SABIC/Linde 2024 |
| CAPEX learning curve | 50% by 2050 | Industry consensus |
| Green H2 emissions | 0.0 tCO2/kg | Electrolysis assumption |
| Grid EF 2050 | 0.0 tCO2/MWh | Korea Net Zero target |

### Economic Assumptions
| Assumption | Value | Notes |
|------------|-------|-------|
| Operating rate | 70% | Constant 2025-2050 |
| Discount rate | 8% | NPV calculations |
| Fossil fuel prices | Constant | 2025 levels through 2050 |
| Grid price trajectory | +91% | $100→$191/MWh |
| RE price trajectory | -54% | $65→$30/MWh |
| H2 price trajectory | -56% | $4.58→$2.01/kg |

### Emission Reduction Targets
| Year | Reduction (%) |
|------|---------------|
| 2025 | 0% (baseline) |
| 2030 | 15% |
| 2035 | 24.5% |
| 2040 | 50% |
| 2045 | 75% |
| 2050 | 100% (Net Zero) |

---

## Key Exclusions

The following are **NOT included** in this analysis:

1. **CCS/CCUS** - No carbon capture technologies; focus on electrification and green hydrogen
2. **Process Emissions** - Only combustion and electricity emissions; chemical process emissions excluded
3. **Scope 3 Emissions** - Only Scope 1 (direct) and Scope 2 (electricity)
4. **Feedstock Change** - Assumes continued naphtha-based production; no bio-based or recycled feedstock
5. **Carbon Pricing** - No explicit carbon price mechanism in cost calculations
6. **Demand Volatility** - Fixed 70% operating rate; no demand variability modeling

---

## Code Structure

### Core Modules
| File | Description | Key Functions |
|------|-------------|---------------|
| `modules/utils.py` | Core calculation library | EmissionCalculator, PriceCalculator, TechnologyCostCalculator, StrandedAssetCalculator |
| `run_scenarios.py` | Main execution script | `run_scenario()`, `calculate_facility_mac_v2()`, `calculate_lcoa()` |
| `streamlit_app.py` | Interactive dashboard | Multi-page visualization |

### Running the Model
```bash
# Run all scenarios
python run_scenarios.py

# Launch dashboard
streamlit run streamlit_app.py
```

---

## Parameter Derivation Notes

### NCC-Electricity: 5.0 MWh/t-ethylene

**Model Value:** 5.0 MWh per tonne ethylene

**Derivation:**
```
Steam cracker furnace heat duty: 15-18 GJ/t-ethylene (literature consensus)
Conversion: 18 GJ ÷ 3.6 GJ/MWh = 5.0 MWh/t-ethylene
```

**Sources:**
- Ren, T., Patel, M.K., Blok, K. (2006). "Olefins from conventional and heavy feedstocks: Energy use in steam cracking and alternative processes." *Energy*, 31, 425-451. DOI: 10.1016/j.energy.2005.04.001
- US DOE OSTI/1481737: Heat demand for ethane steam crackers = 17.7 GJ/t-C2H4
- BASF/SABIC/Linde (2024): World's first electrically heated steam cracker demonstration plant at Ludwigshafen

**Validation:**
- RSC Green Chemistry (2025): Electric cracker requires 2.86 MWh/t additional electricity for furnace electrification
- I&EC Research (2023): Minimum energy requirement 1.75 MWh/t for electrified cracker

---

### NCC-H2: 0.2 t-H2/t-ethylene

**Model Value:** 0.2 tonnes H2 per tonne ethylene (200 kg H2/t-C2H4)

**Derivation:**
```
Steam cracker furnace heat duty: 18 GJ/t-ethylene
Hydrogen LHV (Lower Heating Value): 120 MJ/kg = 0.12 GJ/kg
Combustion efficiency: 85%

Calculation:
H2 required = Heat Duty ÷ (H2 LHV × Efficiency)
H2 required = 18 GJ ÷ (0.12 GJ/kg × 0.85)
H2 required = 18 ÷ 0.102 = 176 kg/t-ethylene

→ 200 kg/t (0.2 t) includes ~15% safety margin
```

**Parameter Sources:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Furnace heat duty | 15-18 GJ/t | Ren et al. (2006); US DOE OSTI/1481737 |
| Hydrogen LHV | 120 MJ/kg | Physical constant (NIST) |
| Combustion efficiency | 85% | Ipieca (2022): Industrial furnaces 80-92%, boilers 85-95% |

**Efficiency Source Detail:**
- Ipieca (2022). "Estimating petroleum industry value chain (Scope 3) greenhouse gas emissions." Section on combustion efficiency.
- Industrial furnaces: 80-92% thermal efficiency
- Industrial boilers: 85-95% thermal efficiency
- 85% represents conservative mid-range estimate for hydrogen-fired furnaces

**Validation:**
- RSC Green Chemistry (2025): H2 co-product from cracking = 65.1 kg/t (indicates ~135 kg/t external H2 needed, consistent with calculation)
- Decarbonisation Technology (2023): Hydrogen firing can reduce furnace CO2 by 100% when using pure hydrogen

---

### Derived Demand Factors (in model)

The model uses demand factors per tCO2 abated, derived from the above:

| Technology | Per-Product Value | Per-CO2 Value | Derivation |
|------------|-------------------|---------------|------------|
| NCC-H2 | 0.2 t-H2/t-C2H4 | 0.127 t-H2/tCO2 | 0.2 ÷ 1.57 tCO2/t-C2H4 |
| NCC-Electricity | 5.0 MWh/t-C2H4 | 3.18 MWh/tCO2 | 5.0 ÷ 1.57 tCO2/t-C2H4 |

Where 1.57 tCO2/t-ethylene is the baseline NCC furnace emission intensity.

---

### Undocumented Parameters (Requires Further Research)

The following parameters lack authoritative sources:

| Parameter | Value | Status |
|-----------|-------|--------|
| NCC-H2 CAPEX | $1,700 M/MtCO2 (2025) | No direct source |
| NCC-Electricity CAPEX | $1,500 M/MtCO2 (2025) | No direct source |
| 50% CAPEX learning curve | By 2050 | Assumption without citation |

**Recommended Sources to Investigate:**
- IEA Energy Technology Perspectives reports
- McKinsey decarbonization studies
- DECHEMA technology roadmaps

---

## References

### Technology Data
1. BASF/SABIC/Linde (2024) - Electric cracker pilot
2. Toribio-Ramirez et al. (2025) - E-cracker CAPEX
3. Lummus Tech (2023) - H2 cracker case study
4. Thunder Said Energy (2023) - H2 cracker economics
5. Kosmadakis (2020) - Heat pump COP values
6. Coolbrook (2024) - RDH technology specifications

### Price & Emission Data
7. IRENA 2024 - Renewable electricity price trajectories
8. IEA WEO 2024 - Energy price projections
9. IPCC 2019 - Fuel emission factors (Table 2.3)
10. API Compendium 2021 - Refinery gas emission factors
11. Korea MOE - Grid emission factor trajectory

### Attribution
This model incorporates data and methodologies from **PLANiT Institute (2025)**:
- RE PPA Price Trajectory
- LCOH Calculation Methodology

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2025 | Initial comprehensive documentation |
| 1.1 | January 2025 | Added Parameter Derivation Notes section with NCC-H2/NCC-Electricity source verification |

---

*This document provides a complete reference for the Korea Petrochemical MACC Model. For questions or clarifications, refer to the project documentation in `/docs/`.*
