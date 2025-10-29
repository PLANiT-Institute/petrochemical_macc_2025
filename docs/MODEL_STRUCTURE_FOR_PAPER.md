# Korean Petrochemical MACC Model - Structure Documentation

**For Academic Publication**

## Model Components

### 1. Core Modules

#### Module 1: Baseline Analysis (`baseline.py`)
- **Purpose**: Calculate 2025 baseline emissions and BAU trajectory
- **Inputs**: Facility database, energy intensities, emission factors
- **Outputs**: Baseline emissions (66.2 MtCO2), BAU trajectory (2025-2050)
- **Key Functions**:
  - `calculate_baseline_2025()`: Facility-level emission calculation
  - `project_bau_trajectory()`: Future emissions with grid decarbonization

#### Module 2: MACC Analysis (`macc.py`)
- **Purpose**: Calculate Marginal Abatement Cost Curves
- **Approach**: Energy-based methodology (explicit fuel tracking)
- **Inputs**: Baseline, technology parameters, price trajectories
- **Outputs**: Technology costs ($/tCO2) for each year 2025-2050
- **Key Functions**:
  - `calculate_macc_annual()`: Annual MACC for all technologies
  - `_calculate_heat_pump_macc()`: Heat pump cost calculation
  - `_calculate_ncc_h2_macc()`: NCC-H2 cost calculation
  - `_calculate_ncc_electricity_macc()`: NCC-Electricity cost calculation
  - `_calculate_re_ppa_macc()`: RE PPA cost calculation

#### Module 3: Cost Optimization (`optimization_v2.py`)
- **Purpose**: Find least-cost technology deployment pathway
- **Algorithm**: Greedy cost-ordered deployment with constraints
- **Key Constraints**:
  - NCC-H2 and NCC-Electricity are mutually exclusive
  - Technology irreversibility (no capacity reduction)
  - Annual emission targets
- **Inputs**: BAU trajectory, MACC, emission scenarios
- **Outputs**: Deployment schedule, investment requirements, facility allocation
- **Key Functions**:
  - `optimize_scenario()`: Main optimization loop
  - `create_facility_level_allocation()`: Allocate tech to specific facilities

### 2. Supporting Modules

#### Utils (`utils.py`)
- Data loaders
- Emission calculators
- Cost calculators
- Utility functions (is_ncc_facility, save functions)

#### Data Manager (`data_manager.py`)
- Centralized data loading
- Data validation
- Parameter management

## Data Structure

### Input Data Files (11 core files)

1. **facility_database.csv** (248 rows)
   - Columns: product, process, company, location, capacity_kt, year_built

2. **energy_intensities.csv** (248 rows)
   - Energy consumption per ton of product
   - Columns: Naphtha_GJ_per_tonne, Electricity_kWh_per_tonne, LNG_GJ_per_tonne, etc.

3. **emission_factors.csv**
   - Emission factors for each fuel type
   - Key values: LNG (0.0561 tCO2/GJ), Naphtha (0.0542 tCO2/GJ)

4. **technology_parameters.csv**
   - CAPEX, OPEX, lifetime, technical parameters for each technology
   - 4 technologies: Heat_Pump, NCC-H2, NCC-Electricity, RE_PPA

5. **h2_price_trajectory.csv**
   - Hydrogen prices 2025-2050
   - Range: $6.00/kg (2025) → $2.00/kg (2050)

6. **re_price_trajectory.csv**
   - Renewable electricity prices 2025-2050
   - Range: $90/MWh (2025) → $50/MWh (2050)

7. **fuel_price_trajectory.csv**
   - Fossil fuel prices (naphtha, LNG, etc.)
   - Assumed constant at 2025 levels

8. **grid_emission_trajectory.csv**
   - Korean grid emission factor 2025-2050
   - Declines: 0.45 tCO2/MWh (2025) → 0.25 tCO2/MWh (2050)

9. **demand_growth_trajectory.csv**
   - Capacity growth projections
   - Total growth: 28.8% by 2050

10. **emission_scenarios_clean.csv**
    - Policy scenarios (e.g., 90% reduction target)

11. **heat_pump_applicability.csv**
    - Heat pump applicability by product group

## Model Flow

```
[Facility Database] → [Module 1: Baseline] → [Baseline Emissions: 66.2 MtCO2]
                                           ↓
[Technology Params] → [Module 2: MACC] → [Technology Costs by Year]
[Price Trajectories]                    ↓
                                           ↓
[Emission Scenarios] → [Module 3: Optimization] → [Deployment Pathway]
                                                 → [Investment: $30.4B]
                                                 → [2050 Emissions: 50.1 MtCO2]
```

## Key Simplifications for Academic Paper

### What Makes This Model Clean:

1. **Energy-Based Approach**: Explicit fuel tracking, no black-box LCOE
2. **Greedy Algorithm**: Simple, transparent optimization
3. **Clear Constraints**: Only 2 constraints (mutual exclusivity + irreversibility)
4. **Validated Data**: All data from peer-reviewed sources (IEA, IRENA, IPCC)
5. **Modular Structure**: 3 independent modules, easy to understand

### Model Assumptions (to state in paper):

1. **No facility retirement**: All 248 facilities operate throughout 2025-2050
2. **Simple annualization**: CAPEX/lifetime (no discount rate for simplicity)
3. **Four technologies only**: Heat Pump, NCC-H2, NCC-Electricity, RE PPA
4. **Perfect foresight**: Prices known in advance
5. **No uncertainty**: Deterministic optimization

## Files NOT Used (Archived)

- `optimization.py` - Old version (before mutual exclusivity fix)
- `financial.py` - Not used
- `sensitivity.py` - Standalone analysis, not core model
- Various redundant data files

## Code Quality

- **Total lines of code**: ~2,000 lines (3 modules + 2 support)
- **Documentation**: All functions documented with docstrings
- **Validation**: Comprehensive test suite (`test_corrected_model.py`)
- **Data sources**: All cited with references

---

**Ready for Academic Publication**: Yes
**Model Complexity**: Low (good for reproducibility)
**Data Transparency**: High (all sources cited)
