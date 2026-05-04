# Net Zero Pathways for Korea's Petrochemical Industry: A Facility-Level Marginal Abatement Cost Analysis

## Research Report

**Institution:** PLANiT Institute
**Date:** December 2024
**Version:** 1.0

---

## Abstract

This study presents a comprehensive facility-level marginal abatement cost curve (MACC) analysis for decarbonizing Korea's petrochemical industry from 2025 to 2050. Using a database of 237 baseline facilities (243 with the Shaheen project) representing 100,066 kt/year production capacity, we evaluate six decarbonization scenarios combining three production pathways with two naphtha cracking center (NCC) technology options. Our analysis demonstrates that net-zero emissions by 2050 is technically and economically achievable through a portfolio approach combining electrification, green hydrogen, and renewable energy procurement. Required cumulative investment ranges from $21.8B to $41.7B depending on scenario selection, with annual renewable electricity demand reaching up to 282 TWh by 2050.

**Keywords:** Petrochemical industry, Decarbonization, MACC, Net Zero, Electrification, Green Hydrogen, Korea

---

## 1. Introduction

### 1.1 Background

Korea's petrochemical industry is one of the world's largest, ranking 4th globally in ethylene production capacity. The sector contributes approximately 47 MtCO₂/year at current operating rates (70%), representing a significant portion of Korea's industrial emissions. Under Korea's 2050 Carbon Neutrality Strategy, the petrochemical sector faces substantial pressure to decarbonize while maintaining economic competitiveness.

### 1.2 Research Objectives

This study aims to:
1. Develop a facility-level emissions baseline for Korea's petrochemical industry
2. Evaluate technology options for deep decarbonization
3. Construct marginal abatement cost curves for key technologies
4. Identify optimal deployment pathways under different scenarios
5. Quantify investment requirements and energy infrastructure needs

### 1.3 Scope

The analysis covers:
- **Temporal scope:** 2025-2050
- **Geographic scope:** All major Korean petrochemical complexes (Yeosu, Daesan, Ulsan, Onsan)
- **Emissions scope:** Scope 1 (direct combustion) and Scope 2 (purchased electricity)
- **Technology scope:** Heat pumps, NCC electrification, NCC hydrogen, renewable PPA, RotoDynamic Heater (RDH)

---

## 2. Methodology

### 2.1 Facility Database

The analysis utilizes a comprehensive database of Korean petrochemical facilities:

| Metric | Value |
|--------|-------|
| Baseline facilities (2025) | 237 |
| With Shaheen project (2026+) | 243 |
| Total production capacity | 100,066 kt/year |
| Products covered | 54 types |
| Major complexes | 4 (Yeosu, Daesan, Ulsan, Onsan) |

**Table 1: Regional Distribution of Facilities**

| Region | Facilities | Capacity (kt/yr) | Share (%) |
|--------|-----------|------------------|-----------|
| Yeosu | 87 | 37,216 | 37.2% |
| Ulsan | 85 | 31,436 | 31.4% |
| Daesan | 57 | 27,424 | 27.4% |
| Other | 19 | 3,990 | 4.0% |
| **Total** | **237** | **100,066** | **100%** |

### 2.2 Baseline Emissions Calculation

Baseline emissions are calculated using the following methodology:

**Combustion Emissions:**
$$E_{combustion} = \sum_{f} (C_f \times EF_f)$$

Where:
- $C_f$ = Consumption of fuel $f$ (GJ)
- $EF_f$ = Emission factor for fuel $f$ (tCO₂/GJ)

**Electricity Emissions:**
$$E_{electricity} = C_{elec} \times EF_{grid}$$

Where:
- $C_{elec}$ = Electricity consumption (MWh)
- $EF_{grid}$ = Grid emission factor (tCO₂/MWh)

**Table 2: Emission Factors Applied**

| Fuel | tCO₂/GJ | Source |
|------|---------|--------|
| Naphtha | 0.0542 | IPCC 2019 |
| LNG | 0.0561 | IPCC 2019 |
| Fuel Gas | 0.050 | API Compendium 2021 |
| Byproduct Gas | 0.048 | API Compendium 2021 |
| LPG | 0.0631 | IPCC 2019 |
| Fuel Oil | 0.0773 | IPCC 2019 |

### 2.3 Technology Assessment

Five decarbonization technologies are evaluated:

**Table 3: Technology Portfolio**

| Technology | Application | Available | TRL |
|------------|-------------|-----------|-----|
| Heat Pump | Low-temp processes (<165°C) | 2025 | 9 |
| NCC-H₂ | Naphtha cracker furnaces | 2030 | 7 |
| NCC-Electricity | Electric crackers | 2030 | 8 |
| RE-PPA | All grid electricity | 2025 | N/A |
| RDH | High-temp BTX (>200°C) | 2026 | 8 |

### 2.4 MACC Calculation

The marginal abatement cost for each technology is calculated as:

$$MAC = \frac{CAPEX_{ann} + OPEX_{ann} + \Delta FuelCost}{Abatement}$$

Where:
- $CAPEX_{ann}$ = Annualized capital expenditure ($/year)
- $OPEX_{ann}$ = Annual operating expenditure ($/year)
- $\Delta FuelCost$ = Fuel cost differential ($/year)
- $Abatement$ = Annual emission reduction (tCO₂/year)

### 2.5 LCOH Methodology

Green hydrogen price is dynamically calculated using the Levelized Cost of Hydrogen (LCOH) formula:

$$LCOH = \frac{CAPEX \times CRF + OPEX + Stack_{replacement}}{H_2\ Production} + Electricity\ Cost$$

**Key Parameters:**
- Electrolyzer CAPEX: $1,000/kW (2025) → $500/kW (2050)
- Efficiency: 70% (2025) → 75% (2050)
- Capacity factor: 90%
- Lifetime: 20 years
- Discount rate: 8%

This methodology ensures that hydrogen prices are linked to renewable electricity prices, reflecting the true cost dynamics of green hydrogen production.

---

## 3. Scenario Design

### 3.1 Production Pathways

Three production pathways are evaluated:

| Pathway | Description | Facilities | Capacity Impact |
|---------|-------------|------------|-----------------|
| Shaheen (Growth) | Baseline + S-Oil Shaheen project | 243 | +3.9% |
| Restructure 25% | Retire 25% oldest NCC capacity | 237 | -25% NCC |
| Restructure 40% | Retire 40% oldest NCC capacity | 237 | -40% NCC |

### 3.2 NCC Technology Options

Two mutually exclusive NCC decarbonization technologies:

| Technology | Energy Vector | Consumption | Infrastructure |
|------------|---------------|-------------|----------------|
| NCC-H₂ | Green Hydrogen | 0.2 t-H₂/t-ethylene | H₂ pipeline + storage |
| NCC-Electricity | Renewable electricity | 5.0 MWh/t-ethylene | Grid upgrade |

### 3.3 Combined Scenarios

The six scenarios analyzed:

| # | Scenario ID | Production | Technology |
|---|-------------|------------|------------|
| 1 | shaheen_ncc_h2 | Shaheen (Growth) | NCC-H₂ |
| 2 | shaheen_ncc_elec | Shaheen (Growth) | NCC-Electricity |
| 3 | restructure_25pct_ncc_h2 | Restructure 25% | NCC-H₂ |
| 4 | restructure_25pct_ncc_elec | Restructure 25% | NCC-Electricity |
| 5 | restructure_40pct_ncc_h2 | Restructure 40% | NCC-H₂ |
| 6 | restructure_40pct_ncc_elec | Restructure 40% | NCC-Electricity |

---

## 4. Key Assumptions

### 4.1 Price Trajectories

**Table 4: Renewable Electricity Price Trajectory**

| Year | RE Price ($/MWh) | Decline from 2025 |
|------|------------------|-------------------|
| 2025 | 65.00 | Baseline |
| 2030 | 55.69 | -14% |
| 2040 | 40.87 | -37% |
| 2050 | 30.00 | -54% |

*Source: IRENA 2024, IEA WEO 2024*

**Table 5: Green Hydrogen Price Trajectory (LCOH-derived)**

| Year | H₂ Price ($/kg) | RE Price | Electrolyzer CAPEX | Efficiency |
|------|-----------------|----------|-------------------|------------|
| 2025 | 4.58 | $65/MWh | $1,000/kW | 70% |
| 2030 | 3.91 | $56/MWh | $900/kW | 71% |
| 2040 | 2.82 | $41/MWh | $700/kW | 73% |
| 2050 | 2.01 | $30/MWh | $500/kW | 75% |

### 4.2 Grid Decarbonization

Korea's grid is assumed to fully decarbonize by 2050:

| Year | Grid EF (tCO₂/MWh) | Reduction |
|------|-------------------|-----------|
| 2025 | 0.436 | Baseline |
| 2030 | 0.349 | -20% |
| 2040 | 0.140 | -68% |
| 2050 | 0.000 | -100% |

### 4.3 Technology CAPEX Learning

All technologies assume 50% CAPEX reduction by 2050:

| Technology | 2025 | 2050 | Unit |
|------------|------|------|------|
| Heat Pump | 800 | 400 | M$/MtCO₂ |
| NCC-H₂ | 1,700 | 850 | M$/MtCO₂ |
| NCC-Electricity | 1,500 | 750 | M$/MtCO₂ |
| RDH | 900 | 450 | M$/MtCO₂ |

---

## 5. Results

### 5.1 Baseline Emissions

**Table 6: Baseline Emissions Summary**

| Metric | 100% Operating Rate | 70% Operating Rate |
|--------|---------------------|-------------------|
| Total Emissions (2025) | 67.14 MtCO₂ | 47.00 MtCO₂ |
| NCC Share | 85.3% | 85.3% |
| Aromatics Share | 13.7% | 13.7% |
| Other Share | 1.0% | 1.0% |

**Emissions by Fuel Source (at 70% operating rate):**

| Fuel | Emissions (MtCO₂) | Share |
|------|-------------------|-------|
| Naphtha | 26.58 | 56.5% |
| Fuel Gas | 5.96 | 12.7% |
| Electricity | 5.86 | 12.5% |
| LNG | 4.48 | 9.5% |
| Byproduct Gas | 2.74 | 5.8% |
| Other | 1.38 | 3.0% |

### 5.2 Technology Contribution

**Figure 1: Technology Deployment Order**

The model deploys technologies in cost-effectiveness order:

1. **RE-PPA** (2025+): Switches grid electricity to renewable energy
2. **Heat Pump** (2025+): Replaces fossil fuel combustion for low-temperature processes
3. **RDH** (2026+): Addresses high-temperature BTX processes
4. **NCC-H₂ or NCC-Electricity** (2030+): Decarbonizes naphtha cracker furnaces

### 5.3 Technology Synergy: RE-PPA and Heat Pump

A critical finding of this analysis is the synergistic relationship between RE-PPA and Heat Pump technologies:

**Two-Step Decarbonization Process:**
1. Heat Pump replaces fossil fuel combustion with grid electricity
2. RE-PPA decarbonizes both baseline electricity AND new Heat Pump electricity demand

This synergy enables complete decarbonization of non-NCC facilities:

| Step | Transformation | Emission Factor |
|------|----------------|-----------------|
| Before | Fossil fuel combustion | ~0.05-0.08 tCO₂/GJ |
| After HP | Grid electricity (COP 4.0) | 0.436 tCO₂/MWh (2025) |
| After RE-PPA | Renewable electricity | 0.05 tCO₂/MWh |

### 5.4 Scenario Results

**Table 7: Scenario Comparison (2050)**

| Scenario | Emissions (Mt) | Investment ($B) | Elec Demand (TWh) |
|----------|----------------|-----------------|-------------------|
| Shaheen + NCC-H₂ | 0.0 | 41.7 | 112 + H₂ demand |
| Shaheen + NCC-Elec | 0.0 | 41.4 | 282 |
| Restructure 25% + NCC-H₂ | 0.0 | 22.8 | 84 + H₂ demand |
| Restructure 25% + NCC-Elec | 0.0 | 22.5 | 211 |
| Restructure 40% + NCC-H₂ | 0.0 | 22.3 | 67 + H₂ demand |
| Restructure 40% + NCC-Elec | 0.0 | 21.8 | 169 |

**Key Finding:** All scenarios achieve Net Zero by 2050.

### 5.5 Regional Investment Requirements

**Table 8: Regional Investment Summary (Shaheen + NCC-Electricity Scenario)**

| Region | 2025 Emissions | 2050 Investment | 2050 Elec Demand |
|--------|----------------|-----------------|------------------|
| Yeosu | 18.49 MtCO₂ | $15.4B | 113 TWh |
| Daesan | 15.68 MtCO₂ | $13.1B | 95 TWh |
| Ulsan | 11.94 MtCO₂ | $10.2B | 73 TWh |
| Other | 0.89 MtCO₂ | $2.7B | 1 TWh |
| **Total** | **47.00 MtCO₂** | **$41.4B** | **282 TWh** |

### 5.6 Emission Pathway

**Table 9: Emission Trajectory (Shaheen + NCC-Electricity)**

| Year | BAU Emissions | Target | Actual | Reduction |
|------|---------------|--------|--------|-----------|
| 2025 | 47.0 MtCO₂ | 47.0 | 47.0 | 0% |
| 2030 | 50.8 MtCO₂ | 40.6 | 38.2 | 24.8% |
| 2035 | 53.8 MtCO₂ | 35.5 | 30.1 | 44.0% |
| 2040 | 56.0 MtCO₂ | 26.9 | 20.0 | 64.3% |
| 2045 | 57.4 MtCO₂ | 13.4 | 9.1 | 84.2% |
| 2050 | 53.3 MtCO₂ | 0.0 | 0.0 | 100% |

---

## 6. Discussion

### 6.1 Technology Selection

The analysis reveals that **NCC-Electricity is more cost-effective than NCC-H₂** in most scenarios due to:

1. **Lower energy intensity**: 5.0 MWh/t-ethylene vs. ~11.3 MWh equivalent for H₂
2. **No conversion losses**: Direct electricity use vs. electrolysis + combustion
3. **Simpler infrastructure**: Grid connection vs. H₂ pipeline network

However, NCC-H₂ offers advantages in:
- Lower annual energy costs by 2050 (due to declining LCOH)
- Potential for H₂ co-benefits (mobility, other industries)
- Flexibility in energy storage

### 6.2 Infrastructure Requirements

The electrification pathway requires substantial grid infrastructure investment:

| Metric | 2025 | 2050 |
|--------|------|------|
| Petrochemical electricity demand | ~8 TWh | 282 TWh |
| Increase | - | 35x |
| Grid capacity needed | - | ~40 GW dedicated |

### 6.3 Sensitivity Analysis

Key sensitivities identified:

1. **RE price**: ±20% RE price → ±15% in total abatement cost
2. **CAPEX learning**: Slower learning (30% vs 50%) → +25% investment
3. **Grid EF trajectory**: Delayed decarbonization → Higher MAC for RE-PPA

### 6.4 Limitations

1. **Process emissions excluded**: Chemical reaction emissions not included
2. **Scope 3 excluded**: Upstream and downstream emissions not analyzed
3. **No CCS/CCUS**: Carbon capture technologies not considered
4. **Constant operating rate**: 70% assumed throughout study period

---

## 7. Conclusions

### 7.1 Key Findings

1. **Net Zero is achievable**: All six scenarios reach net-zero emissions by 2050
2. **Investment range**: $21.8B - $41.7B depending on scenario
3. **Electrification preferred**: NCC-Electricity more cost-effective than NCC-H₂
4. **Technology synergy**: RE-PPA + Heat Pump enables complete non-NCC decarbonization
5. **Grid is critical**: Up to 282 TWh/year renewable electricity needed

### 7.2 Policy Implications

1. **Grid infrastructure priority**: Massive renewable electricity expansion required
2. **Technology support**: Incentives needed for early NCC-Electricity deployment
3. **Regional coordination**: Yeosu and Daesan require concentrated investment
4. **Industry restructuring**: Capacity retirement can significantly reduce investment needs

### 7.3 Future Research

1. Include process emissions and Scope 3 analysis
2. Evaluate CCS/CCUS as complementary technology
3. Dynamic operating rate scenarios
4. Detailed infrastructure requirement studies
5. Employment transition analysis

---

## References

1. BASF, SABIC, Linde. (2024). World's First Demonstration Plant for Large-Scale Electrically Heated Steam Cracking Furnaces. Press Release.
2. Coolbrook. (2024). RotoDynamic Heater Technology Specification. Technical Whitepaper.
3. IEA. (2018). The Future of Petrochemicals. Paris: IEA Publications.
4. IEA. (2024). World Energy Outlook 2024. Paris: IEA Publications.
5. IPCC. (2019). 2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories.
6. IRENA. (2024). Renewable Power Generation Costs in 2023. Abu Dhabi: IRENA.
7. Kosmadakis, G. (2020). Industrial High Temperature Heat Pumps. Renewable and Sustainable Energy Reviews.
8. Korea Petrochemical Industry Association. (2024). Korean Petrochemical Industry Statistics.
9. LBNL. (2008). World Best Practice Energy Intensity Values for Selected Industrial Sectors.
10. Lummus Technology. (2023). Net Zero Ethylene Technology. Technical Brochure.
11. McKinsey & Company. (2024). Decarbonizing the Chemical Industry. Global Insight.
12. PLANiT Institute. (2025). Korea Petrochemical Industry Decarbonization Model. Internal Documentation.
13. Thunder Said Energy. (2023). Hydrogen vs Electrification in Industrial Heat. Research Report.

---

## Appendix A: Data Sources

| Data Component | Source | Year |
|----------------|--------|------|
| Facility Database | Korea Petrochemical Industry Association | 2024 |
| Emission Factors | IPCC Guidelines | 2019 |
| Energy Intensity | Industry benchmarks, IEA | 2018-2024 |
| RE-PPA Price | PLANiT Institute (IRENA, IEA) | 2025 |
| LCOH Methodology | PLANiT Institute | 2025 |
| Grid EF | Korea Energy Agency | 2024 |
| Technology CAPEX | Thunder Said Energy, IEA, McKinsey | 2023-2024 |
| RDH Specifications | Coolbrook | 2024 |

---

## Appendix B: Model Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA INPUTS                                    │
│  facilities.csv, energy_intensities.csv, emission_factors.csv           │
│  price_trajectories/, technology_parameters.csv                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 1: BASELINE (baseline.py)                      │
│  Calculate facility-level emissions from energy consumption              │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 2: MACC (macc.py)                             │
│  Calculate marginal abatement costs for each technology                 │
│  - Heat Pump MACC (using grid electricity)                              │
│  - NCC-H2 MACC (using LCOH-derived H2 price)                           │
│  - NCC-Electricity MACC (using RE price)                                │
│  - RE-PPA MACC (grid → RE switching)                                    │
│  - RDH MACC (high-temp electrification)                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                MODULE 3: OPTIMIZATION (optimization_v2.py)              │
│  Deploy technologies in cost-effectiveness order                        │
│  - NCC-H2 and NCC-Electricity are mutually exclusive                    │
│  - Technology irreversibility (capital lock-in)                         │
│  - Meet annual emission targets                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            OUTPUTS                                       │
│  Scenario results, facility allocations, regional summaries             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*© PLANiT Institute 2024-2025. All rights reserved.*
