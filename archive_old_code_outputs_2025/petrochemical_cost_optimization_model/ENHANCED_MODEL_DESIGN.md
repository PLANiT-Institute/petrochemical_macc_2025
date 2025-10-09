# Enhanced Petrochemical Cost Optimization Model
## Design Specification v2.0

---

## Overview

This document specifies the enhanced model architecture that produces:
- Validated baseline (52 MtCO₂ in 2025)
- Three emission target scenarios (A: Budget, B: Point Targets, C: Linear)
- Energy flow tracking (fossil → RE → H₂)
- Stranded asset analysis
- Interaction-aware MACCs

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Data Sources (Korean_Petrochemical_MACC_Model_English.xlsx)│
│  • facilities_df (248 facilities)                           │
│  • ci_df (energy intensity matrix)                          │
│  • ci2_df (emission factors)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MODULE 1: Enhanced Baseline Analysis                       │
│  ✓ Calibrated to 52 MtCO₂ (±3%)                            │
│  ✓ Direct/Indirect split validation (64%/34%)              │
│  ✓ By-product share ~70% of direct                         │
│  ✓ Energy balance (67.7 Mtoe, naphtha 82.9%)              │
│  → baseline_2025_totals.csv                                │
│  → qa_checks.csv                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MODULE 2: Interaction-Aware MACC Generation                │
│  • Carbon price sweep ($0-$500/tCO₂)                       │
│  • System re-optimization at each price point              │
│  • Precedence-aware marginal costs                         │
│  → macc_wedges.csv (2030/2040/2050)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MODULE 3: Multi-Scenario MILP Optimization                 │
│  Scenarios:                                                  │
│  • A: Cumulative budget constraint                          │
│  • B: Point targets (35% by 2035, 100% by 2050)           │
│  • C: Linear path to zero                                   │
│                                                              │
│  Decision Variables:                                         │
│  • deploy[f,t,y]: Deploy tech t at facility f in year y    │
│  • retire[f,y]: Retire facility f in year y                │
│  • derate[f,y]: Capacity reduction                         │
│                                                              │
│  Constraints:                                                │
│  • Emission targets (scenario-dependent)                    │
│  • Technology ramp rates                                    │
│  • Supply caps (bio-naphtha, H₂)                           │
│  • Mass/energy balance                                      │
│  • Retrofit downtime                                        │
│                                                              │
│  Objective: min NPV(CAPEX + OPEX + fuel + carbon           │
│                     - byproduct credits - salvage)          │
│                                                              │
│  → pathway_yearly.csv                                       │
│  → facility_deployments.csv                                 │
│  → energy_flow.csv (Sankey-ready)                          │
│  → stranding_events.csv                                     │
│  → company_yearly.csv                                       │
│  → results_by_scenario.csv                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### 1. baseline_2025_totals.csv
```
metric,value,unit,target,status
total_emissions,52.0,MtCO2,52.0,PASS
direct_emissions,33.3,MtCO2,33.3,PASS
indirect_emissions,17.7,MtCO2,17.7,PASS
byproduct_share_of_direct,70.0,%,70.0,PASS
total_energy,67.7,Mtoe,67.7,PASS
naphtha_share,82.9,%,82.9,PASS
ncc_emission_share,46.0,%,46.0,PASS
```

### 2. pathway_yearly.csv
```
scenario,year,total_emissions_mtco2,scope1_mtco2,scope2_mtco2,
cumulative_emissions_mtco2,target_emissions_mtco2,target_met,
total_capex_musd,annual_opex_musd,fuel_cost_musd,power_cost_musd,
h2_cost_musd,carbon_cost_musd,byproduct_credit_musd,
shadow_carbon_price_usd_tco2,
naphtha_feedstock_pj,naphtha_thermal_pj,byproduct_gas_pj,
byproduct_oil_pj,ng_pj,grid_electricity_pj,re_ppa_pj,
onsite_re_pj,blue_h2_pj,green_h2_pj
```

### 3. energy_flow.csv (Sankey-ready)
```
scenario,year,source_carrier,intermediate_carrier,sink_process,
energy_gj,emission_intensity_kgco2_gj
```

### 4. macc_wedges.csv
```
scenario,target_year,wedge_id,technology,
capacity_mt,abatement_mtco2,marginal_cost_usd_tco2,
cumulative_abatement_mtco2,prerequisite_wedges,
interaction_factor
```

### 5. facility_deployments.csv
```
scenario,facility_id,company,location,process,capacity_t,
deploy_year,technology,capex_musd,annual_opex_musd,
emission_reduction_tco2_yr,project_life_yr,npv_musd,
retired,retirement_year,derated,derate_factor
```

### 6. stranding_events.csv
```
scenario,facility_id,company,event_year,event_type,
capacity_affected_t,asset_nbv_musd,lost_future_cf_npv_musd,
salvage_value_musd,total_stranding_cost_musd,trigger_reason
```

### 7. stranding_financials.csv
```
scenario,company,total_stranded_nbv_musd,lost_cf_npv_musd,
salvage_musd,net_stranding_musd,facilities_affected,
capacity_stranded_mt,job_impact,mitigation_cost_musd
```

### 8. company_yearly.csv
```
scenario,year,company,capacity_mt,emissions_mtco2,
capex_musd,opex_musd,revenue_musd,ebitda_musd,
stranded_assets_musd,tech_portfolio,risk_score
```

### 9. results_by_scenario.csv
```
scenario,total_npv_musd,total_capex_musd,total_opex_musd,
total_abatement_mtco2,avg_cost_usd_tco2,
stranded_assets_musd,target_met,feasible,
peak_investment_year,peak_investment_musd
```

---

## Technology Specifications

### Enhanced Technology Matrix

| Technology | Applicable Processes | CAPEX 2025 ($/t) | Emission Reduction | Bio-naphtha Cap | H₂ Ramp | Notes |
|-----------|---------------------|------------------|-------------------|-----------------|---------|-------|
| Bio-Naphtha | Naphtha Cracker | 400 | 85% | 30% by 2030, 70% by 2050 | - | Supply constrained |
| NCC H₂ Blue | Naphtha Cracker | 1000 | 75% | - | 2 Mt/yr by 2030 | Pipeline required |
| NCC H₂ Green | Naphtha Cracker | 1200 | 95% | - | 0.5 Mt/yr by 2030, 5 Mt/yr by 2050 | Electrolyzer |
| NCC Electricity | Naphtha Cracker | 600 | 65% | - | - | Grid EF dependent |
| Heat Pump | BTX, Utility | 200 | 45% | - | - | Temp limited |
| Renewable PPA | All | 250 | 80% (indirect) | - | Grid integration 40% | Virtual |
| On-site Solar/Wind | All | 300 | 95% (indirect) | - | Land constraint | Physical |

### Supply Trajectories

**Bio-naphtha availability:**
- 2025: 10% of naphtha demand
- 2030: 30%
- 2040: 50%
- 2050: 70%

**Hydrogen (blue) availability:**
- 2025: 0.5 Mt/yr
- 2030: 2.0 Mt/yr
- 2040: 4.0 Mt/yr
- 2050: 6.0 Mt/yr

**Hydrogen (green) availability:**
- 2025: 0.1 Mt/yr
- 2030: 0.5 Mt/yr
- 2040: 3.0 Mt/yr
- 2050: 10.0 Mt/yr

**Grid emission factor trajectory:**
- 2025: 0.46 kgCO₂/kWh
- 2030: 0.35 kgCO₂/kWh
- 2040: 0.20 kgCO₂/kWh
- 2050: 0.05 kgCO₂/kWh

---

## Emission Target Scenarios

### Scenario A: Carbon Budget
- **Cumulative 2025-2050 ≤ Budget_MtCO₂**
- Budget = 780 MtCO₂ (15 Mt/yr average)
- Optimizer determines optimal timing

### Scenario B: Point Targets
- 2025: 52 MtCO₂ (baseline)
- 2030: 39 MtCO₂ (25% reduction)
- 2035: 33.8 MtCO₂ (35% reduction)
- 2040: 26 MtCO₂ (50% reduction)
- 2050: 0 MtCO₂ (100% reduction, net-zero)

### Scenario C: Linear Path
- 2025: 52 MtCO₂
- Linear decline: -2.08 MtCO₂/year
- 2050: 0 MtCO₂

---

## QA Validation Framework

### Baseline Validation (2025)
```python
checks = {
    'total_emissions': (52.0, 0.03),  # 52 ± 3%
    'direct_indirect_ratio': (64/34, 0.05),
    'byproduct_direct_share': (0.70, 0.05),
    'total_energy_mtoe': (67.7, 0.05),
    'naphtha_energy_share': (0.829, 0.05),
    'ncc_emission_share': (0.46, 0.05)
}
```

### Annual Validation
```python
checks = {
    'mass_balance': ±1%,
    'energy_balance': ±1%,
    'capacity_utilization': 0.75-0.95,
    'adoption_caps': bio-naphtha ≤ cap(year),
    'build_rate': Δcapacity ≤ max_rate,
    'shadow_price_smooth': monotonic where binding
}
```

---

## Implementation Plan

### Phase 1: Module 1 Enhancement (Day 1)
- Add QA validation framework
- Implement detailed energy flow tracking
- Create baseline_2025_totals output
- Validate against all targets

### Phase 2: Module 2 Implementation (Day 2)
- Build carbon price sweep mechanism
- Implement system re-optimization
- Generate interaction-aware MACCs
- Export macc_wedges tables

### Phase 3: Module 3 Refactoring (Day 3-4)
- Convert to Pyomo MILP framework
- Add scenario logic (A/B/C)
- Implement stranded asset variables
- Add energy flow tracking
- Add supply constraints

### Phase 4: Outputs & Visualization (Day 5)
- Standardize all CSV/Parquet outputs
- Build Sankey diagram generator
- Create MACC visualization
- Build stranded asset heat maps
- Company scorecards

### Phase 5: Testing & Validation (Day 6)
- Run all scenarios
- Validate QA checks
- Sensitivity analysis
- Documentation

---

## Expected Outputs Per Run

### Excel Report
- Executive Summary
- Scenario Comparison
- Pathway Analysis
- Technology Deployment
- Stranded Assets
- Company Scorecards
- Energy Flows
- QA Validation

### CSV/Parquet Files
- baseline_2025_totals.csv
- pathway_yearly.csv
- energy_flow.csv
- renewables_yearly.csv
- hydrogen_yearly.csv
- macc_wedges.csv
- facility_deployments.csv
- stranding_events.csv
- stranding_financials.csv
- stranding_summary_company.csv
- company_yearly.csv
- results_by_scenario.csv
- qa_checks.csv
- lineage_map.csv

### Visualizations
- Emissions vs Targets (3 scenarios)
- Energy Flow Sankey (animated)
- Technology Adoption Ramps
- MACC 2030/2040/2050
- Stranded Assets Waterfall
- Company Scorecards
- Shadow Carbon Price

---

## Key Performance Indicators

### Financial
- Total NPV (2025-2050)
- Total CAPEX requirement
- Average abatement cost ($/tCO₂)
- Stranded asset cost
- Peak annual investment

### Environmental
- Total abatement (MtCO₂)
- Target achievement (%)
- Scope 1 vs Scope 2 trajectory
- RE penetration (%)
- H₂ adoption (Mt/yr)

### Operational
- Facilities affected (#)
- Technologies deployed (#)
- Retirement rate (%/yr)
- Capacity derated (%)
- Build rate compliance (%)

---

This design provides a comprehensive, validated, and interaction-aware model for petrochemical sector decarbonization planning.
