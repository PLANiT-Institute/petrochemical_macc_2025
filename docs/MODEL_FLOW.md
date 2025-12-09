# Korean Petrochemical MACC Model - Data Flow Documentation

## Overview

This document describes how data flows through the model from raw inputs to final outputs.

---

## 1. DATA INPUTS

### 1.1 Facility Data
**File:** `data/facility_database.csv`
```
product | process | company | location | capacity_kt | year_built
```
- 248 facilities total
- NCC (Naphtha Cracker): 41 facilities (Ethylene, Propylene, Butadiene)
- BTX: 48 facilities (Benzene, Toluene, Xylene)
- Polymers & Others: 159 facilities

### 1.2 Energy Intensities
**File:** `data/energy_intensities.csv`
```
product | process | company | location | capacity_kt | year_built |
Naphtha_GJ_per_tonne | Electricity_kWh_per_tonne | LNG_GJ_per_tonne |
Fuel_Gas_GJ_per_tonne | Byproduct_Gas_GJ_per_tonne | LPG_GJ_per_tonne |
Fuel_Oil_GJ_per_tonne | Diesel_GJ_per_tonne
```

**Energy intensity values (GJ/tonne product):**

| Product | Naphtha | LNG | Fuel_Gas | Byproduct_Gas | Electricity (kWh) |
|---------|---------|-----|----------|---------------|-------------------|
| Ethylene | 29.0 | 4.49 | 5.62 | 1.12 | 21.8 |
| Propylene | 25.4 | 3.93 | 5.16 | 1.23 | 48.8 |
| Butadiene | 29.0 | 4.17 | 5.32 | 1.16 | 102.2 |

**Sources:**
- IEA (2018) "The Future of Petrochemicals" - SEC range: 20-40 GJ/tonne ethylene
- LBNL (2008) "World Best Practice Energy Intensity Values" - 29.1 GJ/tonne ethylene
- ACS (2023) "Optimization of Electric Ethylene Production" - 24.4-29.1 GJ/tonne

### 1.3 Emission Factors
**File:** `data/emission_factors.csv`
```
fuel | tCO2_per_GJ | tCO2_per_kWh | source
```

| Fuel | tCO2/GJ | Source |
|------|---------|--------|
| Naphtha | 0.0542 | IPCC 2019, Table 2.3 |
| LNG | 0.0561 | IPCC 2019, Table 2.3 |
| Fuel_Gas | 0.0500 | API Compendium 2021 |
| Byproduct_Gas | 0.0480 | API Compendium 2021 |
| LPG | 0.0631 | IPCC 2019, Table 2.3 |
| Fuel_Oil | 0.0773 | IPCC 2019, Table 2.3 |
| Diesel | 0.0741 | IPCC 2019, Table 2.3 |
| Electricity | 0.0045 tCO2/kWh | Korea Grid 2025 |

### 1.4 Technology Parameters
**File:** `data/technology_parameters.csv`
```
technology | capex_2025 | capex_2050 | lifetime | opex_pct
```

| Technology | CAPEX 2025 (M$/MtCO2) | CAPEX 2050 (M$/MtCO2) | Lifetime | Learning |
|------------|----------------------|----------------------|----------|----------|
| Heat_Pump | 800 | 400 | 20 yr | 50% |
| NCC-H2 | 1700 | 850 | 25 yr | 50% |
| NCC-Electricity | 1500 | 750 | 25 yr | 50% |
| RE_PPA | 0 | 0 | 99 yr | - |
| RDH | 900 | 450 | 25 yr | 50% |

### 1.5 Price Trajectories
**Files:**
- `data/h2_price_trajectory.csv` - H2 prices: $4.58/kg (2025) → $2.01/kg (2050)
- `data/re_price_trajectory.csv` - RE prices: $65/MWh (2025) → $30/MWh (2050)
- `data/grid_emission_trajectory.csv` - Grid EF: 0.436 (2025) → 0.0 (2050) tCO2/MWh

### 1.6 Demand Growth Scenarios
**Files:**
- `data/demand_growth_trajectory_shaheen.csv` - Shaheen scenario (100% capacity)
- `data/demand_growth_trajectory_restructure_25pct.csv` - 25% NCC reduction
- `data/demand_growth_trajectory_restructure_40pct.csv` - 40% NCC reduction

---

## 2. CALCULATION FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA INPUTS                                        │
│  facility_database.csv + energy_intensities.csv + emission_factors.csv      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MODULE 1: BASELINE (baseline.py)                         │
│                                                                              │
│  For each facility:                                                          │
│    emissions_kt = Σ (energy_GJ × emission_factor_tCO2/GJ)                   │
│                                                                              │
│  Example (Ethylene):                                                         │
│    Naphtha:       29.0 GJ/t × 0.0542 tCO2/GJ = 1.572 tCO2/t                │
│    LNG:           4.49 GJ/t × 0.0561 tCO2/GJ = 0.252 tCO2/t                │
│    Fuel_Gas:      5.62 GJ/t × 0.0500 tCO2/GJ = 0.281 tCO2/t                │
│    Byproduct_Gas: 1.12 GJ/t × 0.0480 tCO2/GJ = 0.054 tCO2/t                │
│    ─────────────────────────────────────────────────                        │
│    COMBUSTION:    2.158 tCO2/ton                                            │
│                                                                              │
│  Output: df_baseline with total_emissions_kt per facility                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE 2: MACC (macc.py)                              │
│                                                                              │
│  For each technology and year:                                               │
│                                                                              │
│    1. Calculate abatement potential:                                         │
│       potential_mt = applicable_emissions × applicability_factor             │
│                                                                              │
│    2. Calculate MACC cost:                                                   │
│       ann_capex = capex / lifetime                                          │
│       ann_opex = capex × opex_pct                                           │
│       fuel_cost = (H2_price × H2_rate) / emission_intensity                 │
│       MACC = ann_capex + ann_opex + fuel_cost                               │
│                                                                              │
│  Output: MACC costs ($/tCO2) and abatement potentials (MtCO2) per tech     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MODULE 3: OPTIMIZATION (optimization_v2.py)                │
│                                                                              │
│  For each year 2025-2050:                                                    │
│                                                                              │
│    1. Set emission target (e.g., 2035 = 24.5% reduction)                    │
│                                                                              │
│    2. Deploy technologies in cost order:                                     │
│       1st: RE_PPA (grid electricity, ~$0/tCO2)                              │
│       2nd: Heat_Pump (non-NCC fossil, ~$301/tCO2)                           │
│       3rd: RDH (BTX high-temp when H2 selected, ~$1086/tCO2)                │
│       4th: NCC-H2 OR NCC-Electricity (mutually exclusive)                   │
│                                                                              │
│    3. Calculate H2 demand:                                                   │
│       h2_demand_kt = (NCC_abatement_mt × 1e6 / emission_intensity)          │
│                      × h2_consumption_rate                                   │
│                                                                              │
│  Output: Yearly deployment, costs, H2 demand                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUTS                                         │
│                                                                              │
│  outputs/scenarios_*/                                                        │
│    ├── module_01_baseline/                                                   │
│    │   ├── baseline_emissions.csv      (facility-level baseline)            │
│    │   └── facility_summary.csv        (aggregated by product)              │
│    ├── module_02_macc/                                                       │
│    │   └── macc_results.csv            (tech costs by year)                 │
│    └── module_03_deployment/                                                 │
│        └── deployment_pathway.csv      (yearly deployment plan)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. KEY CALCULATIONS

### 3.1 Emission Intensity Calculation
**Location:** `modules/baseline.py:92` → `EmissionCalculator.calculate_total_emissions()`

```python
For each facility:
  combustion_emissions = (
      naphtha_gj × 0.0542 +
      lng_gj × 0.0561 +
      fuel_gas_gj × 0.0500 +
      byproduct_gas_gj × 0.0480 +
      lpg_gj × 0.0631 +
      fuel_oil_gj × 0.0773 +
      diesel_gj × 0.0741
  )
  electricity_emissions = electricity_kwh × 0.0045
  total_emissions = combustion + electricity
```

**NCC Weighted Average:**
```
Total NCC Combustion = 51.85 Mt
Total NCC Capacity = 25.32 Mt
Average Intensity = 51.85 / 25.32 = 2.048 tCO2/ton
```

### 3.2 MACC Cost Calculation
**Location:** `modules/macc.py:264-310`

```python
# NCC-H2 Cost (2050 example)
ann_capex = $850M / 25yr = $34/tCO2
ann_opex = $850M × 4% = $34/tCO2
h2_cost = 0.2 ton H2/ton × 1000 kg × $2.01/kg = $402/ton product
fuel_cost = $402 / 2.048 tCO2/ton = $196/tCO2

TOTAL MACC = $34 + $34 + $196 = $264/tCO2
```

### 3.3 H2 Demand Calculation
**Location:** `modules/optimization_v2.py:245-255`

```python
# Shaheen NCC-H2 (2050)
ncc_h2_abatement = 50.62 MtCO2
emission_intensity = 2.048 tCO2/ton
h2_consumption = 0.2 ton H2/ton product

product_volume = 50.62 × 1e6 / 2.048 / 1000 = 24,717 kt
h2_demand = 24,717 × 0.2 = 4,943 kt H2
```

---

## 4. SCENARIO DEFINITIONS

| Scenario | NCC Strategy | NCC Capacity | Description |
|----------|--------------|--------------|-------------|
| Shaheen NCC-H2 | Hydrogen | 100% | Full NCC with H2 fuel switch |
| Shaheen NCC-Elec | Electrification | 100% | Full NCC with electrification |
| Restructure 25% H2 | Hydrogen | 75% | 25% NCC capacity reduction |
| Restructure 25% Elec | Electrification | 75% | 25% NCC capacity reduction |
| Restructure 40% H2 | Hydrogen | 60% | 40% NCC capacity reduction |
| Restructure 40% Elec | Electrification | 60% | 40% NCC capacity reduction |

---

## 5. TECHNOLOGY APPLICABILITY

| Technology | Applicable To | Applicability % | Notes |
|------------|---------------|-----------------|-------|
| RE_PPA | All facilities | 100% | Grid electricity only |
| Heat_Pump | Non-NCC fossil | 10-60% | Varies by process temp |
| RDH | BTX (high-temp) | 40% | Gap after Heat Pump |
| NCC-H2 | NCC combustion | 100% | Mutually exclusive with NCC-Elec |
| NCC-Electricity | NCC combustion | 100% | Mutually exclusive with NCC-H2 |

---

## 6. DATA SOURCES & REFERENCES

### Energy Intensity Sources
1. **IEA (2018)** - "The Future of Petrochemicals"
   - Steam cracker SEC: 20-40 GJ/tonne ethylene
   - [IEA Report](https://www.iea.org/reports/the-future-of-petrochemicals)

2. **LBNL (2008)** - "World Best Practice Energy Intensity Values"
   - Ethylene: 29.1 GJ/tonne (naphtha cracker)
   - [OSTI Report](https://www.osti.gov/servlets/purl/927032)

3. **ACS Industrial & Engineering Chemistry Research (2023)**
   - Electric cracker: 24.4 GJ/tonne ethylene
   - [ACS Publication](https://pubs.acs.org/doi/10.1021/acs.iecr.3c02226)

4. **ScienceDirect (2017)** - "Intensification of Ethylene Production"
   - Naphtha cracker: 1.8-2.0 kgCO2/kg ethylene
   - [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2095809917308160)

### Emission Factor Sources
1. **IPCC (2019)** - 2019 Refinement to 2006 IPCC Guidelines, Table 2.3
   - Naphtha: 0.0542 tCO2/GJ
   - LNG: 0.0561 tCO2/GJ

2. **API Compendium (2021)** - Compendium of Greenhouse Gas Emissions Methodologies
   - Fuel Gas: 0.050 tCO2/GJ
   - Byproduct Gas: 0.048 tCO2/GJ

---

## 7. FILE STRUCTURE (Active Files Only)

```
petrochemical_macc_2025/
├── data/
│   ├── facility_database.csv              # 248 facilities
│   ├── energy_intensities.csv             # Energy use per facility
│   ├── emission_factors.csv               # Fuel emission factors
│   ├── technology_parameters.csv          # Tech costs & lifetimes
│   ├── h2_price_trajectory.csv            # H2 prices 2025-2050
│   ├── re_price_trajectory.csv            # RE prices 2025-2050
│   ├── grid_emission_trajectory.csv       # Grid EF 2025-2050
│   ├── demand_growth_trajectory_shaheen.csv
│   ├── demand_growth_trajectory_restructure_25pct.csv
│   └── demand_growth_trajectory_restructure_40pct.csv
├── modules/
│   ├── __init__.py
│   ├── baseline.py                        # Module 1: Baseline calculation
│   ├── macc.py                            # Module 2: MACC calculation
│   ├── optimization_v2.py                 # Module 3: Deployment optimization
│   ├── lcoh.py                            # LCOH calculation helper
│   └── utils.py                           # Data loading utilities
├── outputs/
│   ├── scenarios_shaheen_ncc_h2/
│   ├── scenarios_shaheen_ncc_elec/
│   ├── scenarios_restructure_25pct_ncc_h2/
│   ├── scenarios_restructure_25pct_ncc_elec/
│   ├── scenarios_restructure_40pct_ncc_h2/
│   ├── scenarios_restructure_40pct_ncc_elec/
│   └── verification/
├── run_all_scenarios_v3.py                # Main scenario runner
├── streamlit_app.py                       # Dashboard
└── MODEL_FLOW.md                          # This file
```
