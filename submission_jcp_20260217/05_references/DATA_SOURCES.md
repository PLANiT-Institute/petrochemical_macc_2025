# Korea Petrochemical MACC Model - Dataset Documentation

**Last Updated:** January 2025
**Model Version:** planit_report_v0.5

This document explains how datasets are used in the Korea Petrochemical MACC (Marginal Abatement Cost Curve) model, including data structure, flow, transformations, and extension guidelines.

---

## 1. Data Directory Structure

```
data/
├── assets/                          # Facility inventory
│   ├── facility_database_with_regions.csv
│   ├── facility_database_with_shaheen.csv
│   └── region_mapping.csv
│
├── assumptions/                     # Technical & economic parameters
│   ├── model_config.csv            # Global parameters (discount rate, conversions)
│   ├── technology_parameters.csv   # Tech specs (COP, efficiency, TRL)
│   ├── technology_capex.csv        # Capital costs ($/t-product/yr)
│   ├── product_benchmarks.csv      # Energy intensity by product
│   ├── emission_factors.csv        # tCO2 per unit energy
│   ├── asset_valuation_params.csv  # Stranded asset calculations
│   ├── stranded_asset_params.csv   # Abandonment cost parameters
│   ├── kor_petro_spline_comparison.csv  # Science-based pathways
│   └── prices/
│       ├── h2_price_trajectory.csv
│       ├── re_price_trajectory.csv
│       ├── grid_price_trajectory.csv
│       ├── grid_emission_trajectory.csv
│       └── fuel_price_trajectory.csv
│
└── scenarios/                       # Scenario definitions
    ├── scenario_definitions.csv
    ├── demand_growth_trajectory_shaheen.csv
    ├── demand_growth_trajectory_restructure_25pct.csv
    └── demand_growth_trajectory_restructure_40pct.csv
```

---

## 2. Key Datasets & Their Purposes

### A. Facility Data (Assets)

| File | Purpose | Key Columns |
|------|---------|-------------|
| `facility_database_with_regions.csv` | Core facility inventory (~60-70 facilities) | company, product, process, location, capacity_kt, year_built |
| `facility_database_with_shaheen.csv` | Variant with Shaheen expansion | Same + additional capacity |
| `region_mapping.csv` | Maps locations to regions | location, region |

### B. Energy Intensities

| File | Purpose | Usage |
|------|---------|-------|
| `product_benchmarks.csv` | Energy per tonne of product | 40+ product-process pairs with GJ/t and kWh/t |

**Key Fuels Tracked:**
- Naphtha (GJ/t) - feedstock for NCC, fuel for others
- LNG, Fuel Gas, Byproduct Gas, LPG, Fuel Oil, Diesel (GJ/t)
- Electricity (kWh/t)

### C. Technology Parameters

| File | Purpose | Key Values |
|------|---------|------------|
| `technology_parameters.csv` | Tech specs | Heat_Pump COP=4.0, NCC-H2 0.2 t-H2/t-ethylene |
| `technology_capex.csv` | Capital costs over time | $/t-product/yr declining 2025→2050 |

**Technologies Modeled:**
- **Heat_Pump**: COP=4.0, TRL=9, available 2025
- **NCC-H2**: 0.2 t-H2/t-ethylene, TRL=7, available 2030
- **NCC-Electricity**: 5.0 MWh/t-ethylene, TRL=8, available 2030
- **RDH**: 93% efficiency, TRL=8, available 2026

### D. Emission Factors

| Fuel | Emission Factor | Unit |
|------|-----------------|------|
| Naphtha | 0.0542 | tCO2/GJ |
| LNG | 0.0561 | tCO2/GJ |
| Fuel Gas | 0.050 | tCO2/GJ |
| Electricity | 0.000436 | tCO2/kWh |
| Green H2 | 0 | tCO2/kg |

### E. Price Trajectories (2025-2050)

| File | 2025 Value | 2050 Value | Trend |
|------|------------|------------|-------|
| H2 price | $4.58/kg | $2.01/kg | -56% |
| RE price | ~$65/MWh | ~$30/MWh | Declining |
| Grid EF | ~0.436 tCO2/MWh | ~0.0 tCO2/MWh | Grid decarbonizes |

### F. Scenario Definitions

**4 Active Scenarios:**

| Scenario | Production | NCC Tech | Pathway |
|----------|------------|----------|---------|
| shaheen_ncc_h2_15c | Shaheen | H2-based | 1.5°C strict |
| shaheen_ncc_h2_20c | Shaheen | H2-based | 2.0°C overshoot |
| shaheen_ncc_elec_15c | Shaheen | Electric | 1.5°C strict |
| shaheen_ncc_elec_20c | Shaheen | Electric | 2.0°C overshoot |

---

## 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LOADING (load_data)                    │
└─────────────────────────────────────────────────────────────────┘
                               │
    ┌──────────────────────────┼──────────────────────────┐
    ▼                          ▼                          ▼
┌─────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Facilities │      │   Intensities    │      │  Price & EF      │
│  (assets)   │      │  (benchmarks)    │      │  Trajectories    │
└─────────────┘      └──────────────────┘      └──────────────────┘
    │                          │                          │
    └──────────┬───────────────┘                          │
               ▼                                          │
    ┌──────────────────────┐                              │
    │   intensity_lookup   │                              │
    │  (facility → energy) │                              │
    └──────────────────────┘                              │
               │                                          │
               ▼                                          │
┌─────────────────────────────────────────────────────────────────┐
│               CALCULATORS (initialized with data)                │
│  EmissionCalculator, PriceCalculator, CapexCalculator, etc.     │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SCENARIO SIMULATION LOOP                        │
│                    (2025 → 2050 annually)                        │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  For each year:                       │
    │  1. Get op_rate, cap_mult, grid_ef   │
    │  2. For each facility:               │
    │     - Calculate baseline emissions   │
    │     - Calculate tech cost & MAC      │
    │     - Rank by LCOA                   │
    │  3. Deploy until target met          │
    │  4. Record results                   │
    └──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUTS                                  │
│  scenario_results.csv, regional_mac_summary.csv, figures/       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Transformations

### Step 1: Baseline Emission Calculation

**Input:** facility row + intensity row + operating parameters

```python
production_t = capacity_kt × 1000 × cap_mult × op_rate
energy_gj = intensity_gj_per_t × production_t
emissions_tco2 = energy_gj × emission_factor_tco2_per_gj
```

**Special Case - NCC Facilities:**
- Naphtha is **feedstock** (cracked into products), NOT combustion fuel
- Only LNG, LPG, byproduct gas counted as combustion emissions
- Heat demand excludes naphtha energy content

### Step 2: Technology Abatement & Cost

**For NCC-H2:**
```
H2_demand = production_t × 0.2 t-H2/t-ethylene
Abatement = combustion_emissions (H2 replaces fuel)
```

**For NCC-Electricity:**
```
Added_elec = production_t × 5.0 MWh/t-ethylene
Abatement = combustion_emissions
```

### Step 3: MAC Calculation

```
MAC = (CAPEX_annual + OPEX + New_Energy_Cost - Fuel_Savings) / Abatement

Where:
- CAPEX_annual = (capacity × capex_rate) / lifetime
- OPEX = CAPEX_total × opex_pct
- New_Energy_Cost = H2_cost + Elec_cost
- Fuel_Savings = Σ(fuel_GJ × fuel_price)
```

---

## 5. Data Dependencies

### Critical Dependencies (Model fails if missing)

1. `product_benchmarks` must cover ALL facility [product, process] pairs
2. `emission_factors` must include ALL fuels in benchmarks
3. `technology_parameters` must define ALL referenced technologies
4. `technology_capex` must have 2025, 2030, 2040, 2050 anchor years
5. `demand_growth_trajectory_{type}` must exist for each scenario
6. `grid_emission_trajectory` must cover 2025-2050
7. `model_config` must have discount_rate and gj_to_mwh

### Relationship Diagram

```
facility_database ──┐
                    ├──→ [merge on product,process] ──→ facility_with_intensity
product_benchmarks ─┘
        │
        ▼
emission_factors ──→ baseline_emissions
        │
        ▼
technology_parameters + technology_capex ──→ tech_cost + abatement
        │
        ▼
price_trajectories ──→ MAC calculation
        │
        ▼
scenario_definitions + spline_targets ──→ deployment_decisions
```

---

## 6. How to Modify/Extend the Model

### Adding a New Facility

1. Add row to `facility_database_with_*.csv` with columns:
   - `company`, `product`, `process`, `location`, `capacity_kt`, `year_built`
2. Ensure matching [product, process] exists in `product_benchmarks.csv`
3. Verify location exists in `region_mapping.csv`

### Adding a New Technology

1. Add row to `technology_parameters.csv` with required columns:
   - `technology`, `cop` (if applicable), `efficiency`, `trl`, `available_year`
   - For NCC technologies: `h2_consumption` or `elec_consumption`
2. Add row to `technology_capex.csv` with cost trajectory:
   - Columns: `technology`, `2025`, `2030`, `2040`, `2050`, `unit`
3. Update scenario code in `run_scenarios.py` if new technology class (beyond Heat_Pump, NCC-*, RDH)

### Changing Price Assumptions

1. Edit corresponding file in `data/assumptions/prices/`:
   - `h2_price_trajectory.csv` - Green hydrogen prices
   - `re_price_trajectory.csv` - Renewable electricity PPA prices
   - `grid_emission_trajectory.csv` - Grid decarbonization pathway
   - `fuel_price_trajectory.csv` - Fossil fuel prices
2. Ensure year coverage (2025-2050) with columns: `year`, `price`
3. Model interpolates linearly between specified years

### Adding a New Scenario

1. Add row to `scenario_definitions.csv` with columns:
   - `scenario_name`, `production_type`, `ncc_technology`, `pathway`, `description`
2. Create `demand_growth_trajectory_{production_type}.csv` if new production type:
   - Columns: `year`, `capacity_multiplier`, `operating_rate`
3. Optionally specify different pathway targets in `kor_petro_spline_comparison.csv`

---

## 7. Code References

| File | Purpose |
|------|---------|
| `modules/data_loader.py` | DataLoader class with validation |
| `modules/utils.py` | EmissionCalculator, PriceCalculator, etc. |
| `modules/capex_calculator.py` | CapexCalculator, MACCalculator |
| `run_scenarios.py` | Main simulation loop |

---

## 8. Verification Commands

```bash
# Verify data loading works
python3 -c "
from modules.data_loader import DataLoader
loader = DataLoader('data')
print('Model config:', loader.load_model_config())
print('Facilities:', len(loader.load_facilities()), 'rows')
print('Benchmarks:', len(loader.load_benchmarks()), 'rows')
"

# Run full scenario simulation
python3 run_scenarios.py
```
