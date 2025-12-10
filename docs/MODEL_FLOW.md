# Korean Petrochemical MACC Model - Data Flow Documentation

**Version:** 2.0
**Updated:** December 10, 2024

## Overview

This document describes how data flows through the model from raw inputs to final outputs.

---

## 1. DATA INPUTS

### 1.1 Facility Data
**File:** `data/inputs/facilities.csv`
```
product | process | company | location | capacity_kt | year_built
```
- **237 baseline facilities** (243 with Shaheen project)
- NCC (Naphtha Cracker): 41 facilities (Ethylene, Propylene, Butadiene)
- BTX: 48 facilities (Benzene, Toluene, Xylene)
- Polymers & Others: 148 facilities

### 1.2 Energy Intensities
**File:** `data/inputs/energy_intensities.csv`
```
product | process | company | location | capacity_kt | year_built |
Naphtha_GJ_per_tonne | Electricity_kWh_per_tonne | LNG_GJ_per_tonne |
Fuel_Gas_GJ_per_tonne | Byproduct_Gas_GJ_per_tonne | LPG_GJ_per_tonne |
Fuel_Oil_GJ_per_tonne | Diesel_GJ_per_tonne
```

**Energy intensity values (GJ/tonne product):**

| Product | Naphtha | LNG | Fuel_Gas | Byproduct_Gas | Electricity (kWh) |
|---------|---------|-----|----------|---------------|-------------------|
| Ethylene | 29.0 | 2.03 | 0 | 1.12 | 85.4 |
| Propylene | 25.4 | 1.78 | 0 | 1.23 | 191.3 |
| Butadiene | 29.0 | 1.88 | 0 | 1.16 | 400.0 |

**Sources:**
- IEA (2018) "The Future of Petrochemicals" - SEC range: 20-40 GJ/tonne ethylene
- LBNL (2008) "World Best Practice Energy Intensity Values" - 29.1 GJ/tonne ethylene
- ACS (2023) "Optimization of Electric Ethylene Production" - 24.4-29.1 GJ/tonne

### 1.3 Emission Factors
**File:** `data/inputs/emission_factors.csv`
```
fuel | tCO2_per_GJ | tCO2_per_kWh | source
```

| Fuel | tCO₂/GJ | Source |
|------|---------|--------|
| Naphtha | 0.0542 | IPCC 2019, Table 2.3 |
| LNG | 0.0561 | IPCC 2019, Table 2.3 |
| Fuel_Gas | 0.050 | API Compendium 2021 |
| Byproduct_Gas | 0.048 | API Compendium 2021 |
| LPG | 0.0631 | IPCC 2019, Table 2.3 |
| Fuel_Oil | 0.0773 | IPCC 2019, Table 2.3 |
| Diesel | 0.0741 | IPCC 2019, Table 2.3 |
| Green H₂ | 0.0 | Zero-emission electrolysis |

### 1.4 Technology Parameters
**File:** `data/inputs/technology_capex.csv`
```
technology | capex_2025 | capex_2050 | lifetime | opex_pct
```

| Technology | CAPEX 2025 (M$/MtCO₂) | CAPEX 2050 (M$/MtCO₂) | Lifetime | Learning |
|------------|----------------------|----------------------|----------|----------|
| Heat_Pump | 800 | 400 | 20 yr | 50% |
| NCC-H2 | 1,700 | 850 | 25 yr | 50% |
| NCC-Electricity | 1,500 | 750 | 25 yr | 50% |
| RE_PPA | 0 | 0 | 99 yr | - |
| RDH | 900 | 450 | 25 yr | 50% |

### 1.5 Price Trajectories

**Renewable Electricity (RE-PPA):**
- File: `data/price_trajectories/re_price_trajectory.csv`
- 2025: $65/MWh → 2050: $30/MWh (54% decline)
- Source: IRENA 2024, IEA WEO 2024

**Green Hydrogen (LCOH-linked to RE price):**
- File: `data/price_trajectories/h2_price_trajectory.csv`
- 2025: $4.58/kg → 2050: $2.01/kg (56% decline)
- **Critical:** H₂ price is calculated from RE price via LCOH formula

**LCOH Formula:**
```
LCOH = (CAPEX × CRF + OPEX + Stack_Replacement) / H2_Production + Electricity_Cost

Where:
- Electricity = RE price × (39.4 kWh/kg ÷ Efficiency)
- Electrolyzer CAPEX: $1,000/kW (2025) → $500/kW (2050)
- Efficiency: 70% (2025) → 75% (2050)
- Capacity Factor: 90%
```

**Grid Emission Factor:**
- File: `data/price_trajectories/grid_emission_trajectory.csv`
- 2025: 0.436 tCO₂/MWh → 2050: 0.0 tCO₂/MWh (100% reduction)

**Grid Electricity Price:**
- File: `data/price_trajectories/grid_price_trajectory.csv`
- 2025: $100/MWh → 2050: $191/MWh (grid decarbonization investment)

### 1.6 Demand Growth Scenarios
**Files:**
- `data/inputs/operating_rate_shaheen.csv` - Shaheen scenario (100% capacity + growth)
- `data/inputs/operating_rate_restructure_25pct.csv` - 25% NCC reduction
- `data/inputs/operating_rate_restructure_40pct.csv` - 40% NCC reduction

---

## 2. CALCULATION FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA INPUTS                                        │
│  facilities.csv + energy_intensities.csv + emission_factors.csv             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MODULE 1: BASELINE (baseline.py)                         │
│                                                                              │
│  For each facility:                                                          │
│    emissions_kt = Σ (energy_GJ × emission_factor_tCO₂/GJ)                   │
│                                                                              │
│  Example (Ethylene):                                                         │
│    Naphtha:       29.0 GJ/t × 0.0542 tCO₂/GJ = 1.572 tCO₂/t                │
│    LNG:           2.03 GJ/t × 0.0561 tCO₂/GJ = 0.114 tCO₂/t                │
│    Byproduct_Gas: 1.12 GJ/t × 0.048 tCO₂/GJ = 0.054 tCO₂/t                 │
│    ─────────────────────────────────────────────────                        │
│    COMBUSTION:    ~1.78 tCO₂/ton                                            │
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
│  Output: MACC costs ($/tCO₂) and abatement potentials (MtCO₂) per tech     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MODULE 3: OPTIMIZATION (optimization_v2.py)                │
│                                                                              │
│  For each year 2025-2050:                                                    │
│                                                                              │
│    1. Set emission target (e.g., 2035 = 24.5% reduction, 2050 = Net Zero)  │
│                                                                              │
│    2. Deploy technologies in cost order:                                     │
│       1st: RE_PPA (grid electricity switching)                              │
│       2nd: Heat_Pump (non-NCC fossil, <165°C)                               │
│       3rd: RDH (BTX high-temp)                                              │
│       4th: NCC-H2 OR NCC-Electricity (mutually exclusive)                   │
│                                                                              │
│    3. Calculate H2 demand:                                                   │
│       h2_demand_kt = (NCC_abatement_mt × 1e6 / emission_intensity)          │
│                      × h2_consumption_rate                                   │
│                                                                              │
│  Output: Yearly deployment, costs, H2/electricity demand                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUTS                                         │
│                                                                              │
│  outputs/scenario_results.csv                                               │
│    - Complete scenario results (all 6 scenarios, facility-level)            │
│    - Columns: year, scenario, facility_id, technology, emissions,           │
│               abatement, capex, opex, elec_demand, h2_demand                │
│                                                                              │
│  reports/Korea_Petrochemical_NetZero_Analysis_*.xlsx                        │
│    - Client-ready Excel reports with multiple analysis sheets               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. KEY CALCULATIONS

### 3.1 Emission Intensity Calculation
**Location:** `modules/baseline.py` → `EmissionCalculator.calculate_total_emissions()`

```python
For each facility:
  combustion_emissions = (
      naphtha_gj × 0.0542 +
      lng_gj × 0.0561 +
      fuel_gas_gj × 0.050 +
      byproduct_gas_gj × 0.048 +
      lpg_gj × 0.0631 +
      fuel_oil_gj × 0.0773 +
      diesel_gj × 0.0741
  )
  electricity_emissions = electricity_kwh × grid_ef_tco2_per_kwh
  total_emissions = combustion + electricity
```

### 3.2 LCOH Calculation (RE → H₂ Price Link)
**Location:** `modules/lcoh.py` → `calculate_lcoh()`

```python
# Key parameters
H2_HHV = 39.4  # kWh/kg (Higher Heating Value)
elec_per_kg = H2_HHV / efficiency  # e.g., 39.4 / 0.70 = 56.3 kWh/kg

# Capital component
crf = (r × (1+r)^n) / ((1+r)^n - 1)  # Capital Recovery Factor
capex_component = (electrolyzer_capex × crf) / h2_per_kw_year

# Electricity component (drives H₂ price)
elec_component = re_price × elec_per_kg / 1000  # $/kg H₂

# Total LCOH
lcoh = capex_component + opex_component + stack_component + elec_component
```

### 3.3 MACC Cost Calculation
**Location:** `modules/macc.py`

```python
# NCC-H2 Cost Example (2050)
ann_capex = $850M / 25yr = $34/tCO₂
ann_opex = $850M × 4% = $34/tCO₂
h2_cost = 0.2 ton H₂/ton × 1000 kg × $2.01/kg = $402/ton product
fuel_cost = $402 / 2.048 tCO₂/ton = $196/tCO₂

TOTAL MACC = $34 + $34 + $196 = $264/tCO₂
```

---

## 4. SCENARIO DEFINITIONS

| Scenario | NCC Strategy | Facilities | Description |
|----------|--------------|------------|-------------|
| shaheen_ncc_h2 | Hydrogen | 243 | Full NCC with H₂ fuel switch |
| shaheen_ncc_elec | Electrification | 243 | Full NCC with electrification |
| restructure_25pct_ncc_h2 | Hydrogen | 237 | 25% NCC capacity reduction |
| restructure_25pct_ncc_elec | Electrification | 237 | 25% NCC capacity reduction |
| restructure_40pct_ncc_h2 | Hydrogen | 237 | 40% NCC capacity reduction |
| restructure_40pct_ncc_elec | Electrification | 237 | 40% NCC capacity reduction |

---

## 5. TECHNOLOGY APPLICABILITY

| Technology | Applicable To | Notes |
|------------|---------------|-------|
| RE_PPA | All grid electricity | Switches to zero-emission RE |
| Heat_Pump | Non-NCC fossil (<165°C) | Low-temp processes only |
| RDH | BTX (high-temp) | RotoDynamic Heater (Coolbrook) |
| NCC-H2 | NCC combustion | Mutually exclusive with NCC-Elec |
| NCC-Electricity | NCC combustion | Mutually exclusive with NCC-H2 |

---

## 6. DATA SOURCES & REFERENCES

### Energy Intensity Sources
1. **IEA (2018)** - "The Future of Petrochemicals"
2. **LBNL (2008)** - "World Best Practice Energy Intensity Values"
3. **ACS (2023)** - "Optimization of Electric Ethylene Production"

### Emission Factor Sources
1. **IPCC (2019)** - 2019 Refinement to 2006 IPCC Guidelines, Table 2.3
2. **API Compendium (2021)** - Compendium of Greenhouse Gas Emissions Methodologies

### Price Trajectory Sources
1. **IRENA 2024** - Renewable electricity price trends
2. **IEA WEO 2024** - Energy price projections
3. **PLANiT Institute (2025)** - LCOH methodology and RE-PPA price trajectory

---

## 7. FILE STRUCTURE

```
petrochemical_macc_2025/
├── data/
│   ├── inputs/
│   │   ├── facilities.csv              # 237 baseline facilities
│   │   ├── facilities_with_shaheen.csv # 243 with Shaheen project
│   │   ├── energy_intensities.csv      # Energy use per facility
│   │   ├── emission_factors.csv        # Fuel emission factors
│   │   ├── technology_capex.csv        # Tech costs & lifetimes
│   │   └── operating_rate_*.csv        # Scenario operating rates
│   └── price_trajectories/
│       ├── h2_price_trajectory.csv     # H₂ prices 2025-2050 (LCOH-derived)
│       ├── re_price_trajectory.csv     # RE prices 2025-2050
│       ├── grid_price_trajectory.csv   # Grid prices 2025-2050
│       └── grid_emission_trajectory.csv # Grid EF 2025-2050
├── modules/
│   ├── __init__.py
│   ├── baseline.py                     # Module 1: Baseline calculation
│   ├── macc.py                         # Module 2: MACC calculation
│   ├── optimization_v2.py              # Module 3: Deployment optimization
│   ├── lcoh.py                         # LCOH calculation (RE→H₂ link)
│   └── utils.py                        # Data loading utilities
├── outputs/
│   └── scenario_results.csv            # Complete scenario results
├── reports/
│   └── Korea_Petrochemical_NetZero_Analysis_*.xlsx
├── run_scenarios.py                    # Main scenario runner
├── analyze_results.py                  # Excel report generator
└── streamlit_app.py                    # Interactive dashboard
```

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 2024 | Initial release |
| 2.0 | Dec 10, 2024 | Updated facility count (237); Corrected emission factors; Added LCOH formula; Updated file paths; Synchronized with data files |
