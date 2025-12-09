# Korea Petrochemical Net Zero Pathway Analysis
## Assumptions and Methodology Documentation

**Version:** Final v1.0
**Date:** December 2024
**Project:** Korea Petrochemical Industry Decarbonization Pathway Analysis
**Analysis Period:** 2025-2050

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Scenario Framework](#2-scenario-framework)
3. [Technology Assumptions](#3-technology-assumptions)
4. [Energy Price Trajectories](#4-energy-price-trajectories)
5. [Grid Decarbonization](#5-grid-decarbonization)
6. [Facility Database](#6-facility-database)
7. [Emission Calculation Methodology](#7-emission-calculation-methodology)
8. [Key Exclusions](#8-key-exclusions)
9. [Data Sources](#9-data-sources)

---

## 1. Executive Summary

This analysis evaluates six decarbonization pathways for Korea's petrochemical industry, combining three production scenarios with two NCC (Naphtha Cracking Center) technology options. The study covers **248 baseline facilities** across four major petrochemical complexes with a total capacity of **100,066 kt/year** (2025 baseline). The Shaheen project adds 6 additional facilities starting in 2026, bringing the total to 254 facilities.

### Key Findings
- All six scenarios achieve **Net Zero by 2050**
- Investment range: **$13.4B - $22.1B** depending on scenario
- No CCS/CCUS technologies included - focus on electrification and green hydrogen
- Complete grid decarbonization assumed by 2050 (Grid EF = 0)

---

## 2. Scenario Framework

### 2.1 Production Pathways (3 options)

| Pathway | Description | Impact on Capacity |
|---------|-------------|-------------------|
| **Shaheen (Growth)** | Baseline + 6 new S-Oil Shaheen facilities (built 2026) | +3.9% capacity (254 facilities total) |
| **Restructure 25%** | Retire 25% oldest NCC capacity | -25% NCC capacity |
| **Restructure 40%** | Retire 40% oldest NCC capacity | -40% NCC capacity |

### 2.2 NCC Technology Options (2 options)

| Technology | Description | Energy Source |
|------------|-------------|---------------|
| **NCC-H2** | Green hydrogen furnaces | Green H2 (0.2 t-H2/t-C2H4) |
| **NCC-Electricity** | Electric crackers (eFurnace) | Renewable electricity (5.0 MWh/t-C2H4) |

### 2.3 Six Combined Scenarios

| # | Scenario ID | Production | Technology |
|---|-------------|------------|------------|
| 1 | shaheen_ncc_h2 | Shaheen (Growth) | NCC-H2 |
| 2 | shaheen_ncc_electricity | Shaheen (Growth) | NCC-Electricity |
| 3 | restructure_25pct_ncc_h2 | Restructure 25% | NCC-H2 |
| 4 | restructure_25pct_ncc_electricity | Restructure 25% | NCC-Electricity |
| 5 | restructure_40pct_ncc_h2 | Restructure 40% | NCC-H2 |
| 6 | restructure_40pct_ncc_electricity | Restructure 40% | NCC-Electricity |

---

## 3. Technology Assumptions

### 3.1 Technology Portfolio

Four decarbonization technologies are considered:

| Technology | Application | TRL | Available From |
|------------|-------------|-----|----------------|
| **Heat Pump** | All processes <165°C | 9 | 2025 |
| **NCC-H2** | Naphtha crackers only | 7 | 2030 |
| **NCC-Electricity** | Naphtha crackers only | 8 | 2030 |
| **RE-PPA** | All grid electricity | N/A | 2025 |
| **RDH** | High-temp BTX (Coolbrook) | 8 | 2026 |

### 3.2 CAPEX Learning Curve

All technologies assume **50% CAPEX reduction by 2050** based on technology learning curves.

| Technology | CAPEX 2025 | CAPEX 2030 | CAPEX 2040 | CAPEX 2050 | Unit |
|------------|------------|------------|------------|------------|------|
| Heat Pump | 800 | 680 | 520 | 400 | M$/MtCO2 |
| NCC-H2 | 1,700 | 1,445 | 1,105 | 850 | M$/MtCO2 |
| NCC-Electricity | 1,500 | 1,275 | 975 | 750 | M$/MtCO2 |
| RDH | 900 | 765 | 585 | 450 | M$/MtCO2 |
| RE-PPA | 0 | 0 | 0 | 0 | M$/MtCO2 |

### 3.3 Technology Parameters

#### Heat Pump
- **COP (Coefficient of Performance):** 4.0
- **Application:** Low-temperature heat (<165°C)
- **Energy conversion efficiency:** 95%
- **OPEX:** 3% of CAPEX annually
- **Lifetime:** 20 years
- **Source:** Kosmadakis 2020

#### NCC-H2 (Green Hydrogen Furnaces)
- **H2 consumption:** 0.2 t-H2 per t-C2H4 (ethylene)
- **Energy conversion efficiency:** 85%
- **OPEX:** 4% of CAPEX annually
- **Lifetime:** 25 years
- **Application:** 85% of NCC furnace emissions

#### NCC-Electricity (Electric Crackers)
- **Electricity consumption:** 5.0 MWh per t-C2H4
- **Energy conversion efficiency:** 95%
- **OPEX:** 4% of CAPEX annually
- **Lifetime:** 25 years
- **Source:** BASF/SABIC/Linde eFurnace specifications

#### RE-PPA (Renewable Power Purchase Agreement)
- **CAPEX:** $0 (contract-based procurement)
- **OPEX:** $0 (included in PPA pricing)
- **Application:** All grid electricity consumption
- **RE lifecycle emissions:** 0.05 tCO2/MWh

#### RDH (RotoDynamic Heater)
- **Application:** High-temperature BTX reforming
- **Energy conversion efficiency:** 93%
- **OPEX:** 3% of CAPEX annually
- **Lifetime:** 25 years
- **Source:** Coolbrook technology specifications

---

## 4. Energy Price Trajectories

### 4.1 Green Hydrogen Price (LCOH)

Based on PLANiT LCOH calculation model:

| Year | H2 Price ($/kg) | Key Assumptions |
|------|-----------------|-----------------|
| 2025 | 4.58 | RE=$65/MWh, Electrolyzer=$1000/kW, Eff=70% |
| 2030 | 3.91 | RE cost decline, electrolyzer learning |
| 2040 | 2.82 | Continued cost reduction |
| 2050 | 2.01 | Target: ~$2/kg (IEA Net Zero) |

**Decline rate:** 56% reduction from 2025 to 2050

### 4.2 Renewable Electricity Price (RE-PPA)

Based on IRENA 2024 and IEA WEO 2024:

| Year | RE Price ($/MWh) |
|------|------------------|
| 2025 | 65.00 |
| 2030 | 55.69 |
| 2040 | 40.87 |
| 2050 | 30.00 |

**Decline rate:** 54% reduction from 2025 to 2050

### 4.3 Grid Electricity Price

| Year | Grid Price ($/MWh) | Notes |
|------|-------------------|-------|
| 2025 | 85.00 | Korea industrial rate |
| 2030 | 80.00 | Gradual transition |
| 2040 | 60.00 | Higher RE penetration |
| 2050 | 35.00 | Near RE-PPA parity |

---

## 5. Grid Decarbonization

### 5.1 Grid Emission Factor Trajectory

Korea's grid is assumed to fully decarbonize by 2050:

| Year | Grid EF (tCO2/MWh) | Reduction from 2025 |
|------|-------------------|---------------------|
| 2025 | 0.436 | Baseline |
| 2030 | 0.349 | -20% |
| 2040 | 0.140 | -68% |
| 2050 | 0.000 | -100% (Net Zero) |

### 5.2 Implications for RE-PPA

- **2025-2049:** RE-PPA provides emission reduction by switching from carbon-intensive grid to renewable electricity
- **2050:** Grid EF = 0, so RE-PPA provides no additional abatement (grid is already clean)
- RE-PPA covers both:
  1. Existing facility electricity consumption
  2. New electricity demand from Heat Pump deployment

---

## 6. Facility Database

### 6.1 Coverage Summary

| Metric | Value |
|--------|-------|
| Baseline facilities (2025) | 248 |
| With Shaheen (2026+) | 254 |
| Total capacity (baseline) | 100,066 kt/year |
| Products covered | 54 types |
| Regions | 4 major complexes |

### 6.2 Regional Distribution

| Region | Facilities | Capacity (kt) | Share |
|--------|-----------|---------------|-------|
| Yeosu Complex | 87 | 37,216 | 37.2% |
| Ulsan Complex | 85 | 31,436 | 31.4% |
| Daesan Complex | 57 | 27,424 | 27.4% |
| Other Regions | 19 | 3,990 | 4.0% |

### 6.3 Major Products

| Product | Facilities | Capacity (kt) |
|---------|-----------|---------------|
| Ethylene | 11 | 13,317 |
| P-Xylene | 8 | 10,790 |
| Propylene | 15 | 10,746 |
| Benzene | 19 | 8,612 |
| PP | 15 | 7,394 |
| TPA | 6 | 4,920 |
| HDPE | 11 | 4,795 |

---

## 7. Emission Calculation Methodology

### 7.1 Baseline Emissions (Scope 1 + 2)

Emissions are calculated by fuel type and electricity:

```
Total Emissions = Fuel Combustion Emissions + Electricity Emissions

Fuel Combustion = Σ (Fuel_i × EF_i)
Electricity = Electricity_consumption × Grid_EF
```

### 7.2 Emission Factors

| Source | Emission Factor | Unit |
|--------|-----------------|------|
| Naphtha | 0.0693 | tCO2/GJ |
| LNG | 0.0561 | tCO2/GJ |
| Fuel Gas | 0.0630 | tCO2/GJ |
| LPG | 0.0631 | tCO2/GJ |
| Fuel Oil | 0.0774 | tCO2/GJ |
| Diesel | 0.0741 | tCO2/GJ |
| Grid Electricity | 0.436 (2025) | tCO2/MWh |

### 7.3 Abatement Calculation

For each technology:

```
Abatement = Baseline_Emissions × Technology_Coverage × Efficiency

Where:
- NCC-H2/Elec covers 85% of NCC furnace emissions
- Heat Pump covers applicable low-temp processes
- RE-PPA covers all electricity emissions (baseline + HP)
```

### 7.4 Operating Rate Assumptions

| Year | Operating Rate |
|------|----------------|
| 2025-2050 | 70% |

---

## 8. Key Exclusions

The following are explicitly **NOT included** in this analysis:

### 8.1 CCS/CCUS
- No Carbon Capture and Storage technologies
- Focus on direct emission reduction through electrification and green hydrogen

### 8.2 Process Emissions
- Only combustion and electricity emissions covered
- Chemical process emissions (e.g., from cracking reactions) not included

### 8.3 Scope 3 Emissions
- Only Scope 1 (direct) and Scope 2 (electricity) emissions
- Upstream/downstream value chain emissions excluded

### 8.4 Feedstock Change
- Assumes continued naphtha-based production
- No bio-based or recycled feedstock scenarios

---

## 9. Data Sources

### 9.1 Technology Data
| Source | Application |
|--------|-------------|
| IRENA 2024 | RE price trajectories |
| IEA WEO 2024 | Energy price projections |
| PLANiT LCOH Model | Green hydrogen pricing |
| Kosmadakis 2020 | Heat pump COP |
| BASF/SABIC/Linde | Electric cracker specifications |
| Coolbrook | RDH technology parameters |

### 9.2 Facility Data
| Source | Application |
|--------|-------------|
| KPIA | Korean petrochemical facility database |
| Company reports | Capacity and operational data |
| KEEI | Energy consumption patterns |

### 9.3 Emission Factors
| Source | Application |
|--------|-------------|
| IPCC 2006 Guidelines | Fuel emission factors |
| Korea MOE | Grid emission factor |

---

## Appendix A: Calculation Examples

### A.1 NCC-H2 Abatement Example

For a 1,000 kt/year ethylene facility:
```
Annual ethylene production = 1,000 kt × 70% operating rate = 700 kt
H2 required = 700 kt × 0.2 t-H2/t-C2H4 = 140 kt H2
Furnace emissions covered = 85% × baseline NCC emissions
```

### A.2 Heat Pump COP Calculation

```
Energy delivered = Electricity input × COP
For COP = 4.0:
  1 MWh electricity → 4 MWh thermal energy
  Replaces: 4 MWh × 3.6 GJ/MWh = 14.4 GJ fossil fuel
```

### A.3 RE-PPA Abatement

```
RE-PPA abatement = Electricity (MWh) × (Grid_EF - RE_EF)
Where RE_EF = 0.05 tCO2/MWh (lifecycle)

Example (2030):
  100,000 MWh × (0.349 - 0.05) = 29,900 tCO2 abatement
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | PLANiT | Initial release |

---

*This document provides a comprehensive overview of all assumptions used in the Korea Petrochemical Net Zero Pathway Analysis. For questions or clarifications, please contact the project team.*
