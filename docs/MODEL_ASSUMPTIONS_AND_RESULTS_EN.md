# Korean Petrochemical MACC Model – Assumptions and Results
**Prepared**: 2025-10-25  
**Model Version**: 2.2  
**Scope**: 248 Korean petrochemical facilities, 2025–2050

---

## 0. Purpose and Usage
- Consolidate model structure, input assumptions, technology parameters, and scenario outputs in one English document.
- Provide file-level references so policy teams, analysts, and developers can trace every value back to its source data.
- Serve as a Word-ready narrative (Markdown format) that can be exported to `.docx` for stakeholder communication.

---

## 1. Model Architecture and Execution

### 1.1 Module Overview (`modules/`)
| Module | Script | Summary | Primary Inputs | Key Outputs |
|--------|--------|---------|----------------|-------------|
| Baseline | `modules/baseline.py` | Builds facility-level 2025 energy and emissions inventory. | `data/baseline_2025_detailed.csv`, `data/energy_intensities.csv` | `outputs/module_01/baseline_2025_detailed.csv`, diagnostic PNGs |
| MACC | `modules/macc.py` | Computes annual technology cost curves with explicit energy balances. | Baseline outputs, `data/technology_parameters.csv`, price trajectories | `outputs/module_02/macc_annual_2025_2050.csv`, comparison charts |
| Optimisation | `modules/optimization.py` | Cost-ordered deployment to meet scenario targets under feasibility rules. | MACC outputs, `data/facility_technology_applicability.csv` | `outputs/module_03/*_deployment.csv`, regional CSVs |
| Financial | `modules/financial.py` | Simplified NPV/IRR on deployment schedules (Module 4 prototype). | Optimisation outputs | `outputs/module_04/financial_summary.csv`, `cash_flow_linear.csv` |

### 1.2 Running the Pipeline
- Full regeneration: `python run_all.py`
- Module-by-module: `python run_module_0X.py` (X = 1–4)
- Reporting and visuals: `python generate_report.py`, LaTeX manuscript in `latex_paper/main.tex`

---

## 2. Core Input Data (`data/`)

### 2.1 High-Priority Files
| Path | Contents | Traceable Fields |
|------|----------|------------------|
| `data/baseline_2025_detailed.csv` | 248-facility inventory (fuel mix, electricity, emissions). | `total_emissions_kt`, energy by fuel, `process`, `location` |
| `data/facility_technology_applicability.csv` | Facility-specific enablement flags. | `heat_pump_applicable`, `ncc_h2_applicable`, `ncc_electric_applicable`, `re_ppa_applicable` |
| `data/technology_parameters.csv` | CAPEX/OPEX learning curves and lifetimes. | `capex_20XX_musd_per_mtco2`, `opex_pct_capex`, `available_year`, `trl` |
| `data/technology_energy_requirements.csv` | Energy switching intensities per product. | `h2_consumption_ton_per_ton_product`, `electricity_consumption_mwh_per_ton_product`, `thermal_efficiency` |
| Price trajectories | `data/h2_price_trajectory.csv`, `data/re_price_trajectory.csv`, `data/grid_price_trajectory.csv`, `data/fuel_price_trajectory.csv` |
| `data/grid_emission_trajectory.csv` | Grid vs. renewable emission factors through 2075. |
| `data/demand_growth_trajectory.csv` | Annual demand growth and cumulative multipliers. |
| `data/model_parameters.csv` | Shared constants (COP 4.0, naphtha combustion intensity, etc.). |

### 2.2 2025 Baseline Snapshot (`outputs/module_01/baseline_2025_detailed.csv`)
- Total emissions: **52.01 MtCO₂** (sum of `total_emissions_kt` ÷ 1000).  
- Facilities covered: **248**, spanning 60 parent companies across 14 industrial clusters.
- Product group split (`outputs/module_01/emissions_by_product.csv`):
  | Group | Emissions (MtCO₂) | Share |
  |-------|-------------------|-------|
  | Olefins | 46.31 | 89.05% |
  | Aromatics | 5.08 | 9.77% |
  | Others (Utilities & Aux) | 0.48 | 0.92% |
  | Polymers | 0.12 | 0.24% |
  | Intermediates | 0.01 | 0.02% |
- Top clusters (`outputs/module_01/emissions_by_location.csv`):
  | Cluster | Baseline MtCO₂ |
  |---------|----------------|
  | Yeosu | 21.05 |
  | Daesan | 17.73 |
  | Ulsan | 7.97 |
  | Onsan | 5.13 |
  | Incheon | 0.08 |
- Energy mix by product (`outputs/module_01/product_group_energy_mix.csv`): Olefins derive 71.5% of combustion energy from naphtha, 14.1% from fuel gas, 11.0% from LNG; polymers/intermediates are nearly 100% electricity.

### 2.3 BAU Emission Trajectory (`outputs/module_01/bau_trajectory_2025_2050.csv`)
- Fossil-combustion emissions grow from 43.64 Mt (2025) to 56.20 Mt (2050).
- Grid-emission factor declines from 0.45 tCO₂/MWh (2025) to 0.25 tCO₂/MWh (2050).
- Total BAU emissions reach 62.19 MtCO₂ by 2050 absent mitigation.

---

## 3. Technology Portfolio and Assumptions

### 3.1 Common Rules
- **Irreversibility**: Cumulative deployment shares are non-decreasing year-on-year (`modules/optimization.py`).
- **Mutual Exclusivity**: No facility can deploy both NCC-H₂ and NCC-Electricity concurrently (`data/facility_technology_applicability.csv` flags enforced in optimisation).
- **Renewable Electricity**: Electrified options use RE contracts with lifecycle emissions of 0.05 tCO₂/MWh (`data/grid_emission_trajectory.csv:re_ef_tco2_per_mwh`).
- **Feedstock Invariance**: Energy switches do not alter naphtha feed volumes, only combustion (`data/technology_energy_requirements.csv:naphtha_becomes_feedstock_only`).
- **Annualised CAPEX**: Module 2 divides upfront CAPEX by lifetime instead of discounted cash-flow (`modules/macc.py`).

### 3.2 Technology Parameters (`data/technology_parameters.csv`)
| Technology | Applicability | First Year | CAPEX 2025 ($/tCO₂) | CAPEX 2050 | OPEX (% CAPEX) | Lifetime (yr) | TRL |
|------------|---------------|------------|---------------------|------------|----------------|---------------|-----|
| Heat Pump | BTX + Utilities (<165 °C) | 2025 | 900 | 450 | 3.0 | 20 | 9 |
| RE PPA | All electricity loads | 2025 | 0 | 0 | 0.0 | 99 | – |
| NCC-Electricity | Naphtha crackers | 2030 | 1,840 | 940 | 3.5 | 25 | 6 |
| NCC-H₂ | Naphtha crackers | 2030 | 1,725 | 863 | 4.0 | 25 | 7 |

### 3.3 Energy and Performance Assumptions (`data/technology_energy_requirements.csv`, `data/model_parameters.csv`)
- **Heat Pump**: COP 4.0, replaces 1 GJ fossil heat with 0.25 GJ electricity, 95% thermal efficiency.
- **RE PPA**: No CAPEX/OPEX; emissions reduction equals `(grid_ef – 0.05) × electricity_load`.
- **NCC-Electricity**: 3.0 MWh/ton ethylene (rounded from RSC Green Chemistry 2025), removes 29 GJ/ton fossil combustion, efficiency 95%.
- **NCC-H₂**: 0.18 ton H₂/ton ethylene (aligned with `model_parameters.csv`), 85% thermal efficiency, eliminates all cracker combustion.
- **Hydrogen Pricing**: Falls from $12/kg (2025) to $2/kg (2050) (`data/h2_price_trajectory.csv`).
- **Renewable Pricing**: RE PPA declines from $130/MWh (2025) to $55/MWh (2050) (`data/re_price_trajectory.csv`); grid price held at $100/MWh (`data/grid_price_trajectory.csv`).

### 3.4 Literature Backing
- **Electrified steam cracking**: Woo et al. (2025), RSC Green Chemistry (`data/technology_energy_requirements.csv:literature_source`).
- **Industrial heat pumps**: IEA (2023) Industrial Heat Pumps report.
- **Hydrogen retrofit**: Estimated from RSC 2025 thermal demand (23 GJ/ton) and H₂ LHV 120 MJ/kg.
- **Renewable cost trends**: IRENA (2023) Renewable Power Generation Costs; Korean 10th Basic Electricity Plan (2023) for grid mix.

---

## 4. Price, Emission, and Demand Trajectories
| Year | Naphtha ($/GJ) `data/fuel_price_trajectory.csv` | Grid Power ($/MWh) `data/grid_price_trajectory.csv` | RE PPA ($/MWh) `data/re_price_trajectory.csv` | H₂ ($/kg) `data/h2_price_trajectory.csv` | Grid EF (tCO₂/MWh) `data/grid_emission_trajectory.csv` |
|------|---------------------------------------|-----------------------------------------|-----------------------------------|---------------------------|-------------------------------------|
| 2025 | 15.0 | 100 | 130 | 12.0 | 0.45 |
| 2030 | 15.0 | 100 | 115 | 10.0 | 0.41 |
| 2040 | 15.0 | 100 | 85 | 6.0 | 0.33 |
| 2050 | 15.0 | 100 | 55 | 2.0 | 0.25 |

Demand growth multipliers increase to 1.288 by 2050 (`data/demand_growth_trajectory.csv:cumulative_multiplier`), implying a 28.8% production uplift relative to 2025.

---

## 5. MACC Results (Module 2)

### 5.1 Cost Components (`outputs/module_02/macc_annual_2025_2050.csv`)
| Year | Technology | Abatement Potential (MtCO₂) | CAPEX ($/tCO₂) | OPEX ($/tCO₂) | Fuel Delta ($/tCO₂) | Total ($/tCO₂) |
|------|------------|-----------------------------|----------------|---------------|---------------------|----------------|
| 2025 | Heat Pump | 0.81 | 45.0 | 27.0 | 178.0 | 250.0 |
| 2025 | NCC-Electricity | 19.01 | 73.6 | 64.4 | 245.4 | 383.4 |
| 2025 | NCC-H₂ | 20.80 | 69.0 | 69.0 | 1,242.1 | 1,380.1 |
| 2025 | RE PPA | 7.21 | 0.0 | 0.0 | 325.0 | 325.0 |
| 2050 | Heat Pump | 1.04 | 23.1 | 13.5 | 75.3 | 111.3 |
| 2050 | NCC-Electricity | 24.48 | 37.6 | 32.9 | 103.8 | 174.3 |
| 2050 | NCC-H₂ | 26.79 | 34.6 | 34.5 | 207.0 | 276.1 |
| 2050 | RE PPA | 8.36 | 0.0 | 0.0 | 275.0 | 275.0 |

> Costs fall with CAPEX learning and cheaper RE/H₂ inputs; hydrogen remains the most expensive option until late 2040s even after price declines.

### 5.2 Maximum Annual Abatement (2050)
- Heat Pump: **1.04 MtCO₂**
- NCC-Electricity: **24.48 MtCO₂**
- NCC-H₂: **26.79 MtCO₂**
- RE PPA: **8.36 MtCO₂**

---

## 6. Optimisation Scenarios (Module 3)

### 6.1 Emission Trajectories (`outputs/module_03/*_deployment.csv`, `outputs/module_03/scenario_summary_for_latex.csv`)
| Scenario | 2030 Emissions (MtCO₂) | 2050 Emissions (MtCO₂) | 2050 Heat Pump (Mt) | 2050 NCC-Elec (Mt) | 2050 NCC-H₂ (Mt) | 2050 RE PPA (Mt) | 2050 H₂ Demand (kt) | Δ Electricity (TWh) | Cumulative CAPEX (M$) |
|----------|------------------------|-------------------------|---------------------|--------------------|------------------|------------------|---------------------|---------------------|-----------------------|
| Conservative | 48.0 | 20.0 | 1.04 | 24.48 | 8.24 | 8.43 | 4.61 | 129.76 | 30,259 |
| Moderate | 46.0 | 10.0 | 1.04 | 24.48 | 18.23 | 8.44 | 10.20 | 129.76 | 39,450 |
| Aggressive | 42.0 | 5.0 | 1.04 | 24.48 | 23.23 | 8.44 | 12.99 | 129.76 | 46,468 |
| Policy Target | 39.0 | 5.2 | 1.04 | 24.48 | 23.03 | 8.44 | 12.88 | 129.76 | 47,866 |

- All scenarios saturate NCC-Electricity by 2050; the difference stems from hydrogen uptake.
- Renewable electricity requirements add ~130 TWh across scenarios, concentrated in cracker electrification.

### 6.2 Regional Deployment (Aggressive, 2050) `outputs/module_03/Aggressive_regional_deployment.csv`
- Daesan: net **–2.02 MtCO₂** (RE over-contracting leads to net-negative Scope 1+2).
- Yeosu: net **–2.62 MtCO₂**, deploying NCC options across 13 facilities.
- Onsan: **–0.50 MtCO₂**, with RE PPA coverage above 70%.
- Ulsan: near-neutral (**–0.13 MtCO₂**), limited hydrogen adoption due to facility constraints.

### 6.3 Policy Compliance
- Emission ceilings follow `data/emission_scenarios_clean.csv` (linear drop to 26 Mt in 2035, 5.2 Mt in 2050).
- The optimisation enforces monotone emissions (E\_y ≤ E\_{y–1}) and technology availability years.

---

## 7. Financial Prototype (Module 4)
- Input schedule: first available scenario (`outputs/module_03/conservative_deployment.csv`).
- Carbon pricing: $50/tCO₂ in 2025, +5% annually (`modules/financial.py:FinancialAnalyzer.calculate_npv_irr`).
- Cost placeholder: uniform $150 M per MtCO₂ deployed; OPEX at 3% of CAPEX.

### 7.1 Results (`outputs/module_04/cash_flow_linear.csv`, `outputs/module_04/financial_summary.csv`)
| Metric | Value (M$) |
|--------|------------|
| Carbon benefit | 60,744 |
| CAPEX spend | 75,147 |
| OPEX spend | 2,254 |
| Net cash flow (undiscounted) | –16,658 |
| NPV @ 5% | –9,666 |
| IRR | Not converged (negative cash flow path) |

> These values are illustrative only; technology-specific financial parameters are not yet differentiated.

---

## 8. Verification and QA Touchpoints
- **Baseline reconciliation**: Sum `total_emissions_kt` in `outputs/module_01/baseline_2025_detailed.csv` to confirm 52.01 MtCO₂ (match against national statistics).
- **MACC audit**: For any year, recompute `capex_ann + opex_ann + fuel_delta` from `outputs/module_02/macc_annual_2025_2050.csv` to verify `total_cost_usd_per_tco2`.
- **Scenario validation**: Compare `actual_emissions_mt` columns against policy caps in `outputs/module_03/*_deployment.csv`.
- **Regional consistency**: Aggregate `num_facilities` in `outputs/module_03/*_regional_deployment.csv` to recover 248 facilities.
- **Financial sensitivity**: Update `modules/financial.py` parameters (CAPEX, OPEX, carbon price) before citing monetised outcomes externally.

---

## 9. References
1. Woo, J. et al. (2025). *Techno-economic analysis of low-carbon ethylene production via electrified steam cracking*. RSC Green Chemistry.
2. IEA (2023). *Industrial Heat Pumps: Technologies and Applications*.
3. IEA (2021). *Net Zero by 2050*.
4. KEEI (2023). *2050 Carbon Neutrality Scenario – Industrial Sector Analysis*.
5. Korea Ministry of Trade, Industry and Energy (2023). *10th Basic Electricity Plan*.
6. IRENA (2023). *Renewable Power Generation Costs*.

---

**Contact**: Project research team (see `README_DATA_DRIVEN.md` for roles and emails).  
**Last Updated**: 2025-10-25

