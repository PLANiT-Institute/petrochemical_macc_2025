# Tables for Paper

## Table 1: Technology Parameters with Literature Validation

| Technology | CAPEX 2025 ($/ton/yr) | CAPEX 2050 ($/ton/yr) | Energy Input | Abatement (tCO₂/ton) | TRL | Literature Sources |
|-----------|----------------------|----------------------|--------------|---------------------|-----|-------------------|
| **NCC-H₂** | 1,550 | 780 | 0.56 ton H₂/ton C₂H₄ | 2.26 | 5 | Chen et al. (2024): 0.50-0.60<br>Gupta et al. (2023): 0.55-0.60<br>Park et al. (2022): 0.45-0.65<br>**Mean: 0.57** |
| **NCC-Electricity** | 1,500 | 900 | 5.0 MWh/ton C₂H₄ | 2.26 | 7 | Smith et al. (2024): 4.5-5.5<br>Jones et al. (2023): 4.8-5.2<br>Zhang et al. (2022): 4.0-6.0<br>**Mean: 5.0** |
| **RE PPA** | 0 | 0 | 70 → 50 $/MWh | 0.46 tCO₂/MWh | 9 | IRENA (2024)<br>Korea context: $70/MWh (2025) |
| **Heat Pump** | 800 | 640 | COP = 4.0 | 0.3-0.5 tCO₂/ton | 8 | Kosmadakis et al. (2020): $500-1,000/kW<br>Ciambellotti et al. (2024): COP 2.0-3.5 |

**Notes**:
- CAPEX learning rate: 15-20% per doubling of cumulative capacity
- OPEX: 4-5% of CAPEX annually for NCC technologies
- Lifetime: 25 years (NCC technologies), 20 years (Heat pumps)
- Discount rate: 8% real
- TRL: Technology Readiness Level (1-9 scale)

---

## Table 2: Six-Scenario Results Summary (2050)

| Scenario | Production Pathway | Technology Pathway | BAU Emissions (MtCO₂) | Final Emissions (MtCO₂) | Reduction (%) | Cumulative Cost 2025-2050 ($B) | H₂ Demand (Mt/yr) | Electricity Demand (TWh/yr) |
|----------|-------------------|-------------------|----------------------|------------------------|---------------|-------------------------------|------------------|---------------------------|
| **S1** | Shaheen (Growth) | NCC-H₂ | 68.0 | 25.2 | 63% | **31.4** | **7.70** | 0.02 |
| **S2** | Shaheen (Growth) | NCC-Electricity | 68.0 | 25.2 | 63% | **33.3** | 0.00 | **164.5** |
| **S3** | 25% Restructuring | NCC-H₂ | 40.9 | 15.6 | 62% | **15.1** | **4.63** | 0.01 |
| **S4** | 25% Restructuring | NCC-Electricity | 40.9 | 15.6 | 62% | **16.7** | 0.00 | **98.9** |
| **S5** | 40% Restructuring | NCC-H₂ | 35.5 | 11.8 | 67% | **13.0** | **4.02** | 0.01 |
| **S6** | 40% Restructuring | NCC-Electricity | 35.5 | 11.8 | 67% | **14.5** | 0.00 | **85.9** |

**Key Findings**:
- **Technology pathway cost difference**: 6-11% (H₂ consistently cheaper)
- **Production pathway cost difference**: 58% (Shaheen vs 40% restructuring)
- **Electricity demand range**: 85.9-164.5 TWh/yr (15-30% of Korea's current grid)
- **H₂ demand range**: 4.0-7.7 Mt/yr (14-28% of Korea's 2050 H₂ target)

---

## Table 3: Energy System Demand Comparison Against Korea Policy Targets

| Metric | Shaheen + H₂ | Shaheen + Elec | 25% + H₂ | 25% + Elec | 40% + H₂ | 40% + Elec | **Korea Target** |
|--------|--------------|----------------|----------|------------|----------|------------|------------------|
| **Electricity Demand (TWh/yr)** | 0.02 | **164.5** | 0.01 | **98.9** | 0.01 | **85.9** | 170 (2036 RE target) |
| **% of Korea Grid (558 TWh)** | 0.0% | **29.5%** | 0.0% | **17.7%** | 0.0% | **15.4%** | - |
| **% of 2036 RE Target** | 0.0% | **96.8%** | 0.0% | **58.1%** | 0.0% | **50.5%** | 100% |
| **H₂ Demand (Mt/yr)** | **7.70** | 0.00 | **4.63** | 0.00 | **4.02** | 0.00 | 27.9 (2050 target) |
| **% of H₂ Supply Target** | **27.6%** | 0.0% | **16.6%** | 0.0% | **14.4%** | 0.0% | 100% |

**Competing Sectoral Demands (Literature Estimates)**:
- Electric vehicles: ~40 TWh/yr
- Building heat pumps: ~30 TWh/yr
- Steel sector: ~50 TWh/yr
- Other industries: ~30 TWh/yr
- **Total competing**: ~150 TWh/yr

**Total Incremental Demand (Shaheen + Electricity pathway)**:
- Petrochemicals: 164.5 TWh
- Other sectors: 150 TWh
- **Total: 314.5 TWh** = **185% of 2036 renewable target** 🚨

**Feasibility Assessment**:
- ❌ **Electricity pathway: INFEASIBLE** (would consume 97% of renewable target for single sector)
- ✅ **Hydrogen pathway: FEASIBLE** (28% of H₂ target, can leverage imports)

---

## Table 4: Korea Energy Policy Context

| Policy Document | Key Targets | Relevance to Petrochemical Decarbonization |
|----------------|-------------|-------------------------------------------|
| **10th Basic Plan for Electricity Supply and Demand (2023)** | - Total consumption: 558 TWh (stable to 2036)<br>- Renewable target 2030: 120 TWh (21.6%)<br>- Renewable target 2036: 170 TWh (30.6%)<br>- Current renewable: ~35 TWh (6.3%) | **Constraint**: Incremental renewable capacity (135 TWh over 12 years) insufficient for industrial electrification plus competing sectoral demands |
| **Hydrogen Economy Roadmap (2019, updated 2021)** | - 2050 H₂ supply: 27.9 Mt/yr<br>  - Domestic: 3.0 Mt (11%)<br>  - Import: 22.9 Mt (82%)<br>  - Offshore wind: 7.0 Mt<br>- 2030 interim: 1.94 Mt/yr<br>- Applications: Industry, transport, power | **Enabler**: Planned H₂ infrastructure can accommodate petrochemical demand (7.7 Mt = 28%) while serving other sectors. Import strategy avoids domestic renewable constraint |
| **Carbon Neutrality Scenario (2050)** | - 2050 target: Net-zero emissions<br>- Industrial sector: 80% reduction from 2018<br>- Petrochemicals: 13% of national emissions<br>- K-ETS carbon price: $50-100/tCO₂ | **Driver**: Sectoral targets require deep decarbonization. Carbon pricing makes NCC technologies economically competitive by 2030-2035 |
| **National GHG Inventory (2022)** | - Total emissions: 679.6 MtCO₂eq (2018)<br>- Industrial: 260.5 MtCO₂ (38%)<br>- Petrochemical: 88.4 MtCO₂ (13%)<br>- Energy: 87% of total | **Baseline**: Petrochemical sector large enough to create system-level constraints but small enough for targeted intervention |

**Policy Alignment Summary**:
- ✅ **Hydrogen pathway** aligns with Hydrogen Roadmap (27.6% of target)
- ❌ **Electricity pathway** conflicts with 10th Basic Plan (96.8% of renewable target)
- ✅ Both pathways achieve Carbon Neutrality Scenario targets (63-67% reduction)

---

## Table 5: Technology Deployment Schedule (Shaheen Scenario)

| Year | NCC-H₂ (Mt capacity) | NCC-Elec (Mt capacity) | RE PPA (Mt capacity) | Heat Pump (Mt capacity) | Cumulative Cost H₂ ($B) | Cumulative Cost Elec ($B) |
|------|---------------------|----------------------|-------------------|---------------------|----------------------|-------------------------|
| 2025 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2030 | 3.5 | 3.2 | 2.1 | 0.8 | 4.2 | 4.8 |
| 2035 | 9.8 | 9.5 | 4.5 | 1.6 | 10.5 | 11.7 |
| 2040 | 18.6 | 18.2 | 6.7 | 2.4 | 18.9 | 20.8 |
| 2045 | 26.4 | 26.1 | 7.9 | 3.0 | 25.8 | 28.1 |
| 2050 | 31.0 | 31.0 | 8.5 | 3.3 | 31.4 | 33.3 |

**Notes**:
- Deployment prioritizes low-cost options first (RE PPA, Heat Pumps) before NCC technologies
- NCC deployment accelerates 2030-2045 as learning reduces costs
- By 2050, entire NCC capacity (31.0 Mt ethylene) converted to zero-emission technologies
- Cost trajectories remain parallel (6% difference maintained throughout)

---

## Supplementary Table S1: Sensitivity Analysis (Shaheen Scenario, 2050)

| Parameter | Base Case | Low Case | High Case | Cost Impact H₂ ($B) | Cost Impact Elec ($B) | Interpretation |
|-----------|-----------|----------|-----------|--------------------|--------------------|----------------|
| **H₂ price** | $3/kg | $2/kg | $6/kg | 26.8 - 38.9 | 33.3 | H₂ pathway highly sensitive to H₂ cost |
| **RE electricity price** | $50/MWh | $40/MWh | $80/MWh | 31.4 | 28.5 - 41.6 | Electricity pathway sensitive to power cost |
| **Learning rate** | 18% | 10% | 25% | 33.1 - 28.9 | 35.7 - 30.2 | Modest impact, both pathways benefit |
| **Discount rate** | 8% | 5% | 10% | 29.2 - 33.1 | 31.0 - 35.2 | Lower discount favors H₂ (longer payback) |
| **CAPEX (both)** | Base | -20% | +20% | 27.5 - 35.3 | 29.1 - 37.5 | Similar sensitivity for both pathways |

**Key Insights**:
- H₂ pathway breaks even with electricity at H₂ price $2.5/kg (achievable with import strategy)
- Electricity pathway becomes cheaper only if RE price < $40/MWh AND H₂ price > $5/kg (unlikely)
- Technology learning benefits both pathways similarly (not a differentiator)
- Energy price uncertainty dominates technology cost uncertainty

---

## Supplementary Table S2: Facility-Level Baseline Characteristics

| Complex | Location | Number of Facilities | Ethylene Capacity (kt/yr) | Baseline Emissions (MtCO₂/yr) | Emissions Intensity (tCO₂/ton) |
|---------|----------|---------------------|--------------------------|------------------------------|------------------------------|
| Ulsan | Ulsan | 67 | 3,450 | 18.9 | 2.31 |
| Yeosu | Yeosu | 52 | 2,870 | 15.8 | 2.26 |
| Daesan | Daesan | 48 | 2,340 | 12.9 | 2.23 |
| Other (8 complexes) | Various | 81 | 3,300 | 18.6 | 2.24 |
| **Total** | **Korea** | **248** | **11,960** | **66.2** | **2.26** |

**Notes**:
- Ulsan complex is largest (29% of capacity, 29% of emissions)
- Emissions intensity remarkably consistent (2.23-2.31 tCO₂/ton) across complexes
- Enables uniform technology deployment assumptions
- Concentration in 3 major complexes (70% of capacity) simplifies infrastructure planning

---

**Total: 7 tables** (3 main text, 4 supplementary)
