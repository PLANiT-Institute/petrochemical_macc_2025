# Materials and Methods

## 3.1. Study Scope and System Boundaries

This study conducts a comprehensive techno-economic analysis of decarbonization pathways for the South Korean petrochemical industry, focusing on facilities with annual production capacity exceeding 100,000 tonnes. The analysis covers three major industrial clusters (Ulsan, Yeosu, and Daesan) which collectively account for approximately 80% of national petrochemical production and 39 major facilities (Figure 1).

**System Boundaries:** The analysis encompasses cradle-to-gate emissions from feedstock extraction through product manufacturing at facility boundaries. Scope 1 emissions include fuel combustion and process emissions, while Scope 2 emissions account for electricity consumption. Scope 3 emissions (feedstock-related) are analyzed separately but excluded from the main transition optimization due to data limitations.

**Temporal Scope:** The analysis spans 2025-2050 with annual time steps, capturing technology deployment dynamics and learning curves. The base year (2025) represents current operational conditions using verified facility data.

## 3.2. Data Collection and Facility Database Development

### 3.2.1. Primary Data Sources
We constructed a comprehensive facility-level database through triangulation of multiple data sources:

- **Company Annual Reports and Sustainability Reports (2020-2024):** Production capacities, energy consumption patterns, and operational parameters
- **Korea Petrochemical Industry Association (KPIA) Statistics:** Sector-wide production data and facility locations
- **National Energy Statistics (Korea Energy Economics Institute):** Fuel consumption patterns and energy intensities
- **Ministry of Environment Emission Inventories:** Verified GHG emission data for major facilities
- **Industry Consultations:** Technical validation of process parameters and technology readiness

### 3.2.2. Energy Intensity and Emission Factors
Baseline energy consumption for each process was calculated using specific energy consumption (SEC) values validated against facility-specific data:

**Table 1: Baseline Energy Intensity by Process Type**

| Process | Energy Type | SEC Range (GJ/t-product) | Data Sources |
|---------|-------------|--------------------------|--------------|
| Naphtha Cracking | Natural Gas | 15.2-18.5 | Company reports, IEA (2023) |
| Polyolefin Production | Mixed | 8.5-12.3 | KPIA statistics, literature |
| Utility Systems | Mixed | 3.2-5.8 | KEPCO data, facility audits |

Emission factors follow IPCC Tier 2 methodology:
- Natural gas: 56.1 kgCO2/GJ (IPCC, 2006)
- Grid electricity: 0.443 tCO2/MWh (KEPCO, 2024)
- Process emissions: facility-specific monitoring data

## 3.3. Technology Characterization and Cost Modeling

### 3.3.1. Decarbonization Technology Portfolio
We evaluated six core decarbonization technologies across different temperature ranges and applications:

**High-Temperature Applications (>800°C):**
- **Electric Naphtha Cracking (NCC-E):** Resistance heating replacing natural gas furnaces
- **Hydrogen Naphtha Cracking (NCC-H2):** Clean hydrogen combustion with turbine integration

**Medium-Temperature Applications (200-800°C):**
- **Radiant Denominator Heating (RDH):** Electric radiant heating for BTX processes
- **Hydrogen Burner Retrofit:** Existing furnace modification for hydrogen blending

**Low-Temperature Applications (<200°C):**
- **Industrial Heat Pumps:** Advanced compression cycles for process heating
- **Renewable Energy PPAs:** Green electricity procurement for utility loads

### 3.3.2. Cost Structure and Learning Rates
Technology costs incorporate CAPEX, OPEX, energy cost differentials, and learning curves:

**CAPEX Calculation:**
$$CAPEX_{t} = CAPEX_{base} \times \left(1 - \alpha \times \log\left(\frac{C_{t}}{C_{base}}\right)\right)$$

Where α is the learning rate parameter (0.12-0.18 depending on technology), and C represents cumulative deployment.

**OPEX Components:**
- Fixed OPEX: 2-4% of initial CAPEX annually
- Variable OPEX: Energy cost differentials based on price trajectories
- Maintenance costs: Technology-specific scaling factors

**Table 2: Technology Cost Parameters**

| Technology | Base CAPEX ($/t-product/yr) | Learning Rate | Fixed OPEX (%) | Availability |
|------------|----------------------------|--------------|----------------|--------------|
| NCC-Electric | 280 | 15% | 3% | 2030 |
| NCC-Hydrogen | 350 | 12% | 4% | 2030 |
| RDH System | 200 | 10% | 3% | 2026 |
| Heat Pump | 100 | 8% | 2% | 2025 |
| H2 Burner Retrofit | 150 | 5% | 2% | 2028 |

## 3.4. Transition Pathway Optimization Framework

### 3.4.1. Objective Function
The model optimizes technology deployment to minimize total transition costs while meeting emission targets:

$$\min \sum_{i=1}^{N} \sum_{t=2025}^{2050} \left( \frac{CAPEX_{i,t}}{annuity\_factor} + OPEX_{i,t} + EC_{i,t} - FS_{i,t} \right) \times \delta_{i,t}$$

Subject to:
1. Emission constraint: $\sum_{i} E_{i,t}^{base} - E_{i,t}^{new} \le E_{target,t}$
2. Technology constraint: $\sum_{j} x_{i,j,t} \le 1$ (maximum one technology per facility)
3. Capacity constraint: $P_{i,t}^{new} \le P_{i}^{max}$

Where δ represents deployment decisions, EC represents energy cost changes, and FS represents fuel savings. Marginal abatement cost (MAC) values are then derived as diagnostic indicators from optimized outcomes for technology prioritization and result interpretation.

### 3.4.2. Carbon Budget Pathways
Emission targets follow science-aligned trajectories derived from the IEA Net Zero by 2050 scenario:

**Table 3: Emission Reduction Pathways (% of 2025 baseline)**

| Year | 1.5°C Pathway | 2.0°C Pathway |
|------|--------------|--------------|
| 2025 | 100.0 | 100.0 |
| 2030 | 81.8 | 156.3 |
| 2040 | 40.9 | 78.2 |
| 2050 | 0.0 | 0.0 |

The 2.0°C pathway includes temporary overshoot (up to 156% of baseline) in 2030, reflecting delayed action scenarios.

### 3.4.3. Price Trajectories and Economic Parameters
Future energy prices follow expert elicitation and market projections:

**Electricity Prices:** 
- 2025: $65/MWh (current grid mix)
- 2030: $55/MWh (increased renewables)
- 2050: $30/MWh (high renewable penetration)

**Green Hydrogen Prices:**
- 2025: $4.58/kg (electrolysis)
- 2030: $3.50/kg (scale economies)
- 2050: $2.01/kg (technology maturity)

**Economic Parameters:**
- Discount rate: 8% (industry standard)
- Plant lifetime: 25 years (typical for petrochemical facilities)
- Carbon price trajectory: Integrated with emission pathways

## 3.5. Scenario Analysis Framework

We developed three distinct scenarios to explore transition pathway uncertainties:

### 3.5.1. Baseline Trends Scenario (S1)
- Carbon pathway: 2.0°C trajectory with delayed action
- Technology deployment: Conservative adoption based on current policies
- Infrastructure: Moderate grid expansion, limited hydrogen infrastructure
- Timeframe: Gradual technology rollout starting 2030

### 3.5.2. Net Zero High Ambition Scenario (S2)
- Carbon pathway: 1.5°C trajectory requiring immediate action
- Technology deployment: Aggressive electrification and hydrogen adoption
- Infrastructure: Extensive grid reinforcement and hydrogen backbone development
- Timeframe: Rapid technology deployment starting 2025

### 3.5.3. Technology Constraints Scenario (S3)
- Carbon pathway: 1.5°C trajectory with infrastructure limitations
- Technology deployment: Constrained electrification, higher hydrogen dependence
- Infrastructure: Limited grid expansion, accelerated hydrogen infrastructure
- Timeframe: Modified deployment reflecting real-world constraints

## 3.6. Model Validation and Sensitivity Analysis

### 3.6.1. Validation Approach
Model validation involved multiple verification steps:
- **Historical Backtesting:** 2015-2020 period using known technology deployments
- **Facility-Level Validation:** Comparison with company-reported investment plans
- **Expert Review:** Technical validation by industry practitioners and academic experts

### 3.6.2. Sensitivity Analysis
We conducted comprehensive sensitivity analysis on key parameters:
- Energy prices (±30% variation)
- Technology learning rates (±50% variation)
- Carbon pricing mechanisms ($0-200/tCO2)
- Infrastructure deployment timelines (±5 years)

Monte Carlo simulation with 10,000 iterations quantified result uncertainty and identified critical parameters affecting transition pathways.
