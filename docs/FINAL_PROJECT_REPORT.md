# Korean Petrochemical Industry Decarbonization Model
## Comprehensive Project Report

**Prepared by:** PLANiT Institute
**Date:** December 2024 (Updated: December 10, 2024)
**Version:** 2.1

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Model Framework](#2-model-framework)
3. [Baseline Analysis (2025)](#3-baseline-analysis-2025)
4. [Regional Analysis](#4-regional-analysis)
5. [Company Analysis](#5-company-analysis)
6. [Technology Options](#6-technology-options)
7. [Cost Assumptions](#7-cost-assumptions)
8. [Scenario Results](#8-scenario-results)
9. [Appendix: Calculation Formulas](#appendix-calculation-formulas)

---

## 1. Executive Summary

This report presents a comprehensive analysis of decarbonization pathways for Korea's petrochemical industry from 2025 to 2050.

### Key Findings

| Metric | Value |
|--------|-------|
| **Total Facilities Analyzed** | 237 (243 with Shaheen) |
| **Total Capacity** | 100,066 kt/year |
| **Baseline Emissions (100% Op)** | 66.19 MtCO₂/year |
| **Baseline Emissions (70% Op)** | 46.34 MtCO₂/year |
| **Operating Rate Assumption** | 70% (Flat 2025-2050) |
| **2035 Target** | 43.5 MtCO₂ (24.5% reduction) |
| **2050 Target** | 0 MtCO₂ (Net Zero) |

### Critical Insight
**The model successfully achieves Net Zero by 2050.** The integration of RotoDynamic Heater (RDH) technology for high-temperature processes, combined with comprehensive NCC electrification and renewable energy procurement, eliminates the residual emissions gap.

---

## 2. Model Framework

### 2.1 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA INPUTS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  facility_database_with_regions.csv  →  237 facilities                  │
│  energy_intensity.csv                →  Energy consumption by process   │
│  emission_factors.csv                →  CO₂ factors by fuel type        │
│  demand_growth_trajectory.csv        →  Operating rate (70%)            │
│  grid_emission_trajectory.csv        →  Grid EF (0.436→0.0 tCO₂/MWh)   │
│  re_price_trajectory.csv             →  RE-PPA price (PLANiT Institute) │
│  technology_parameters.csv           →  Tech specs (CAPEX, efficiency)  │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MODULES                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  baseline.py       →  Baseline emissions & BAU projection               │
│  macc.py           →  Marginal Abatement Cost Curves                   │
│  lcoh.py           →  Levelized Cost of Hydrogen (PLANiT)              │
│  optimization_v2.py →  Cost-effective technology selection             │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        OUTPUTS                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Regional transition plans                                              │
│  Company-level investment requirements                                  │
│  Annual emission pathways                                               │
│  Technology adoption schedules                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Assumptions

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Operating Rate | 70% | Current market crisis (Chinese overcapacity) |
| Capacity Growth | 1.5%→0.5%/yr | Declining growth as market matures |
| Facility Lifetime | Infinite (BAU) | No natural retirement assumed |
| Carbon Price | Not modeled | Policy constraint approach instead |
| Discount Rate | 8% | WACC for industrial projects |


---

## 2.3 Energy Calculation & Forecast Logic (Methodology)

### A. Baseline (2017) Calculation
The baseline emissions are calculated using a **Hybrid Approach** that combines high-level user data with bottom-up facility intensity data.

1.  **User Provided Data (Top-Down):** Total consumption for **LPG** (3,592 kTOE), **LNG** (1,372 kTOE), and **Electricity** (3,929 kTOE). This serves as the "Control Total" for the industry.
2.  **Facility Data (Bottom-Up):** `data/energy_intensities.csv` containing production capacity (kt) and energy intensity factors (Energy/tonne) for 248 facilities.
3.  **Fuel Gas & Off-Gases:** Since user data did not specify Fuel Gas, the total volume is derived directly from the bottom-up sum of specific facility intensities (4,500+ kTOE equivalent), ensuring process-specific emissions are captured.

**Allocation Logic:**
*   **Sector Split (NCC vs Non-NCC):** Derived from the bottom-up summation of the CSV data.
    *   *Naphtha/Fuel Gas:* Allocation strictly follows facility-level intensities.
    *   *Electricity/LPG/LNG:* The relative share from the CSV is used to split the User Provided Total.

### B. 2024 Forecast Logic
*   **Driver:** Ethylene production growth from ~8.7 Mt (2017) to ~9.6 Mt (2024). Ratio: **1.10**.
*   **Allocation Method:** **Global Uniform Scalar**. We apply a 1.10 multiplier to the aggregate industry energy consumption.
    *   *Logic:* In the absence of facility-specific operational data for 2024, we assume the aggregate industry energy consumption scales linearly with the net production increase. This effectively treats the growth as a distributed system-wide increase (10%).

---


## 3. Baseline Analysis (2025)

### 3.1 Emission Composition at 100% Capacity

| Fuel Source | Emissions (ktCO₂) | Share (%) |
|-------------|------------------|-----------|
| **Naphtha** | 37,968 | 57.4% |
| **Fuel Gas** | 8,510 | 12.9% |
| **Electricity** | 8,372 | 12.6% |
| **LNG** | 6,402 | 9.7% |
| **Byproduct Gas** | 3,913 | 5.9% |
| **Other** | 1,028 | 1.6% |
| **Total** | **66,193** | **100%** |

### 3.2 Emission Composition by Product Group

| Product Group | Capacity (kt) | Emissions (MtCO₂) | Share (%) | EF (tCO₂/t) |
|--------------|--------------|-------------------|-----------|-------------|
| **Olefins** | 25,317 | 56.49 | 85.3% | 2.23 |
| **Aromatics** | 14,374 | 9.09 | 13.7% | 0.63 |
| **Other** | 39,315 | 0.48 | 0.7% | 0.01 |
| **Polymers** | 18,105 | 0.12 | 0.2% | 0.007 |
| **Intermediates** | 2,955 | 0.01 | 0.02% | 0.004 |

> **Key Insight:** Olefins (primarily ethylene from naphtha crackers) dominate emissions at 85.3%. This is the primary target for NCC-Electricity technology.

### 3.3 Operating Rate Impact

| Metric | 100% Operation | 70% Operation | Difference |
|--------|---------------|---------------|------------|
| Emissions (2025) | 66.19 MtCO₂ | 46.34 MtCO₂ | -19.85 Mt |
| Emissions (2050 BAU) | 76.20 MtCO₂ | 53.34 MtCO₂ | -22.86 Mt |

The 70% operating rate assumption reduces baseline emissions by approximately 30%, already bringing 2025 emissions below the 2018 reference level (57.6 MtCO₂).

---

## 4. Regional Analysis

### 4.1 Regional Emission Summary

| Rank | Region | Capacity (kt) | Emissions (MtCO₂) | Share (%) | Facilities |
|------|--------|--------------|-------------------|-----------|------------|
| 1 | **Yeosu** | 37,216 | 26.42 | 39.9% | 87 |
| 2 | **Daesan** | 27,424 | 22.40 | 33.8% | 57 |
| 3 | **Ulsan** | 24,105 | 10.42 | 15.7% | 71 |
| 4 | **Onsan** | 7,331 | 6.63 | 10.0% | 14 |
| 5 | Incheon | 2,100 | 0.22 | 0.3% | 2 |
| 6 | Gwangyang | 390 | 0.09 | 0.1% | 3 |
| 7-14 | Others | 1,500 | 0.01 | <0.1% | 14 |
| | **Total** | **100,066** | **66.19** | **100%** | **237** |

### 4.2 Regional Detailed Breakdown

#### 4.2.1 Yeosu Industrial Complex

**Overview:**
- **Location:** South Jeolla Province
- **Facilities:** 87 (35% of national total)
- **Capacity:** 37,216 kt/year (37% of national capacity)
- **Emissions:** 26.42 MtCO₂/year (40% of national emissions)

**Emission Breakdown:**

| Fuel Source | Emissions (ktCO₂) | Share (%) |
|-------------|------------------|-----------|
| Naphtha | 16,101 | 60.9% |
| Fuel Gas | 3,600 | 13.6% |
| LNG | 3,179 | 12.0% |
| Electricity | 2,807 | 10.6% |
| Other | 737 | 2.8% |

**Key Companies in Yeosu:**
| Company | Emissions (ktCO₂) |
|---------|------------------|
| Yeochon NCC | 9,472 |
| LG Chem | 6,800 |
| GS Caltex | 3,200 |

**Decarbonization Implications:**
- Largest concentration of NCC facilities → Priority for NCC-Electricity deployment
- High naphtha dependency (61%) → Significant abatement potential
- Grid infrastructure upgrade needed for 40+ TWh electricity demand

---

#### 4.2.2 Daesan Industrial Complex

**Overview:**
- **Location:** South Chungcheong Province
- **Facilities:** 57 (23% of national total)
- **Capacity:** 27,424 kt/year (27% of national capacity)
- **Emissions:** 22.40 MtCO₂/year (34% of national emissions)

**Emission Breakdown:**

| Fuel Source | Emissions (ktCO₂) | Share (%) |
|-------------|------------------|-----------|
| Naphtha | 12,967 | 57.9% |
| Fuel Gas | 3,128 | 14.0% |
| Electricity | 2,901 | 13.0% |
| LNG | 2,769 | 12.4% |
| Other | 634 | 2.8% |

**Key Companies in Daesan:**
| Company | Emissions (ktCO₂) |
|---------|------------------|
| Lotte Chemical | 5,500 |
| Hanwha TotalEnergies | 4,800 |
| S-Oil | 2,100 |

**Decarbonization Implications:**
- Second-largest emission hub after Yeosu
- Mix of NCC and downstream facilities
- Electricity share higher (13%) → Grid decarbonization beneficial

---

#### 4.2.3 Ulsan Industrial Complex

**Overview:**
- **Location:** Ulsan Metropolitan City
- **Facilities:** 71 (29% of national total)
- **Capacity:** 24,105 kt/year (24% of national capacity)
- **Emissions:** 10.42 MtCO₂/year (16% of national emissions)

**Emission Breakdown:**

| Fuel Source | Emissions (ktCO₂) | Share (%) |
|-------------|------------------|-----------|
| Naphtha | 5,273 | 50.6% |
| Electricity | 1,716 | 16.5% |
| Fuel Gas | 1,643 | 15.8% |
| LNG | 1,446 | 13.9% |
| Other | 339 | 3.3% |

**Key Companies in Ulsan:**
| Company | Emissions (ktCO₂) |
|---------|------------------|
| SK Geocentric | 4,978 |
| HD Hyundai Chemical | 2,500 |
| Kumho Petrochemical | 624 |

**Decarbonization Implications:**
- Higher electricity share (16.5%) → More benefit from grid decarbonization
- Mixed facility age profile → Partial retirement potential
- SK facilities (oldest NCCs) → Priority for restructuring scenario

---

#### 4.2.4 Onsan Industrial Complex

**Overview:**
- **Location:** Ulsan Metropolitan City (adjacent to Ulsan Complex)
- **Facilities:** 14 (6% of national total)
- **Capacity:** 7,331 kt/year (7% of national capacity)
- **Emissions:** 6.63 MtCO₂/year (10% of national emissions)

**Emission Breakdown:**

| Fuel Source | Emissions (ktCO₂) | Share (%) |
|-------------|------------------|-----------|
| Naphtha | 3,628 | 54.7% |
| Fuel Gas | 1,004 | 15.1% |
| Electricity | 906 | 13.7% |
| LNG | 885 | 13.3% |
| Other | 206 | 3.1% |

**Key Companies in Onsan:**
| Company | Emissions (ktCO₂) |
|---------|------------------|
| HD Hyundai Chemical | 2,820 |
| Daehan Oil Chemical | 3,789 |

---

### 4.3 Regional Transition Requirements

| Region | 2025 Emissions (70% Op) | RE_PPA Demand (TWh) | NCC-Elec Demand (TWh) | Total Investment ($B) |
|--------|------------------------|--------------------|-----------------------|----------------------|
| Yeosu | 18.49 Mt | 6.4 | 47.2 | 9.8 |
| Daesan | 15.68 Mt | 6.6 | 40.3 | 8.3 |
| Ulsan | 7.29 Mt | 3.9 | 26.4 | 5.1 |
| Onsan | 4.64 Mt | 2.1 | 18.2 | 3.5 |
| **Total** | **46.34 Mt** | **19.0** | **132.1** | **26.7** |

---

## 5. Company Analysis

### 5.1 Top 20 Emitting Companies

| Rank | Company | Capacity (kt) | Emissions (MtCO₂) | Share (%) | Main Location |
|------|---------|--------------|-------------------|-----------|---------------|
| 1 | **LG Chem** | 15,462 | 11.36 | 17.2% | Yeosu, Daesan |
| 2 | **Yeochon NCC** | 5,246 | 9.47 | 14.3% | Yeosu |
| 3 | **Lotte Chemical** | 11,372 | 9.31 | 14.1% | Daesan |
| 4 | **Hanwha TotalEnergies** | 9,040 | 6.59 | 10.0% | Daesan |
| 5 | **HD Hyundai Chemical** | 4,479 | 5.32 | 8.0% | Ulsan, Onsan |
| 6 | **GS Caltex** | 6,050 | 5.02 | 7.6% | Yeosu |
| 7 | **SK Geocentric** | 6,803 | 4.98 | 7.5% | Ulsan |
| 8 | **Daehan Oil Chemical** | 2,783 | 3.79 | 5.7% | Onsan |
| 9 | **S-Oil** | 4,894 | 3.22 | 4.9% | Daesan |
| 10 | **SK Energy** | 620 | 1.32 | 2.0% | Ulsan |
| 11 | SK Advanced | 600 | 1.28 | 1.9% | Ulsan |
| 12 | Hyosung Chemical | 920 | 1.07 | 1.6% | Ulsan |
| 13 | HD Hyundai Oilbank | 2,218 | 1.02 | 1.5% | Daesan |
| 14 | Taekwang Industrial | 1,590 | 0.65 | 1.0% | Ulsan |
| 15 | Kumho Petrochemical | 2,728 | 0.62 | 0.9% | Ulsan, Yeosu |
| 16-20 | Others | 5,450 | 1.18 | 1.8% | Various |
| | **Total (Top 20)** | **89,255** | **65.20** | **98.5%** | - |

### 5.2 Company Investment Requirements

For each company to achieve its portion of Net Zero by 2050:

| Company | Current Emissions | Required Abatement | Est. Investment | Electricity Demand |
|---------|------------------|-------------------|-----------------|-------------------|
| LG Chem | 11.36 Mt | 11.36 Mt | $4.2B | 28.5 TWh |
| Yeochon NCC | 9.47 Mt | 9.47 Mt | $3.5B | 23.7 TWh |
| Lotte Chemical | 9.31 Mt | 9.31 Mt | $3.4B | 23.3 TWh |
| Hanwha TotalEnergies | 6.59 Mt | 6.59 Mt | $2.4B | 16.5 TWh |
| HD Hyundai Chemical | 5.32 Mt | 5.32 Mt | $2.0B | 13.3 TWh |

---

## 6. Technology Options

### 6.1 Technology Summary

| Technology | Applicability | Available | Emissions | Energy Requirement |
|------------|--------------|-----------|-----------|-------------------|
| **NCC-Electricity** | NCC only | 2030 | 0 (with RE) | 5.0 MWh/t ethylene |
| **NCC-H2** | NCC only | 2030 | 0 (Green H2) | 0.2 t H2/t ethylene |
| **Heat Pump** | Non-NCC (<165°C) | 2025 | Grid-dependent | Varies by COP |
| **RDH** | Non-NCC (>165°C) | 2030 | 0 (with RE) | 0.32 MWh/GJ heat |
| **RE_PPA** | All | 2025 | ~0 | N/A (procurement) |

### 6.2 Technology Selection Logic

The model selects technologies based on **cost-effectiveness** (lowest $/tCO₂ abated):

```
Priority Order (2030):
1. RE_PPA         $130/tCO₂  → Reduces grid electricity emissions
2. Heat_Pump     $326/tCO₂  → Replaces fossil fuel combustion (low-temp)
3. NCC-Electricity $457/tCO₂  → Replaces NCC fossil combustion with RE
4. RDH           $1086/tCO₂ → Replaces fossil fuel combustion (high-temp)
5. NCC-H2        $954/tCO₂  → Not cost-effective vs NCC-Electricity
```

### 6.3 Electricity vs Hydrogen Distinction

| Criterion | NCC-Electricity | NCC-H2 |
|-----------|----------------|--------|
| Energy Vector | Direct Electricity | Green Hydrogen |
| Consumption | 5.0 MWh/t | 0.2 t H2/t (~11.3 MWh/t) |
| Infrastructure | Grid upgrade | H2 pipeline + storage |
| Cost (2030) | $457/tCO₂ | $954/tCO₂ |
| **Preferred?** | **Yes** | No |

The model always selects **NCC-Electricity** over **NCC-H2** because:
1. Lower electricity consumption (5.0 vs 11.3 MWh equivalent)
2. No intermediate conversion losses
3. Lower infrastructure requirements

---

## 7. Cost Assumptions

### 7.1 Renewable Electricity Price (RE-PPA) Trajectory

Based on IRENA 2024 and IEA WEO 2024:

| Year | RE Price ($/MWh) | Decline from 2025 |
|------|------------------|-------------------|
| 2025 | 65.00 | Baseline |
| 2030 | 55.69 | -14% |
| 2035 | 47.71 | -27% |
| 2040 | 40.87 | -37% |
| 2045 | 35.02 | -46% |
| 2050 | 30.00 | -54% |

### 7.2 Grid Emission Factor Trajectory

| Year | Grid EF (tCO₂/MWh) | Reduction vs 2025 |
|------|-------------------|-------------------|
| 2025 | 0.436 | 0% |
| 2030 | 0.349 | -20% |
| 2035 | 0.280 | -36% |
| 2040 | 0.140 | -68% |
| 2045 | 0.070 | -84% |
| 2050 | 0.000 | -100% (Net Zero) |

### 7.3 Hydrogen Price (Dynamic LCOH - Source: PLANiT Institute)

**Critical: H₂ price is calculated from RE price via LCOH formula.**

The model calculates hydrogen price dynamically using:

```
LCOH = (CAPEX × CRF + OPEX + Stack_Replacement) / H2_Production + Electricity_Cost

Where:
- CAPEX: $1,000/kW (2025) → $500/kW (2050)
- Efficiency: 70% (2025) → 75% (2050)
- Capacity Factor: 90%
- Lifetime: 20 years
- Electricity: RE price (drives H₂ cost)
```

| Year | RE Price ($/MWh) | Electrolyzer CAPEX ($/kW) | Efficiency | LCOH ($/kg) |
|------|-----------------|---------------------------|------------|-------------|
| 2025 | 65 | 1,000 | 70% | 4.58 |
| 2030 | 56 | 900 | 71% | 3.91 |
| 2035 | 48 | 800 | 72% | 3.33 |
| 2040 | 41 | 700 | 73% | 2.82 |
| 2045 | 35 | 600 | 74% | 2.39 |
| 2050 | 30 | 500 | 75% | 2.01 |

**Decline rate:** 56% reduction from 2025 to 2050

### 7.4 Technology CAPEX Evolution

| Technology | 2025 | 2030 | 2040 | 2050 | Unit |
|------------|------|------|------|------|------|
| NCC-Electricity | 1,500 | 1,350 | 1,050 | 900 | $/t-C₂H₄/yr |
| NCC-H2 | 1,700 | 1,300 | 935 | 780 | $/t-C₂H₄/yr |
| Heat Pump | 800 | 640 | 480 | 400 | $/tCO₂ capacity |

---

## 8. Scenario Results

### 8.1 Scenario Definitions

| Scenario | Description |
|----------|-------------|
| **BAU** | No technology adoption; emissions grow with capacity |
| **Cost-Effective** | Adopt lowest-cost technologies to meet targets |
| **Restructuring** | Retire 30% oldest NCC capacity before optimization |

### 8.2 Emission Trajectories

| Year | BAU (Mt) | Cost-Effective (Mt) | Restructuring (Mt) | Target (Mt) |
|------|----------|--------------------|--------------------|-------------|
| 2025 | 46.34 | 46.34 | 31.44 | 66.20 |
| 2030 | 49.90 | 37.24 | 25.21 | 53.30 |
| 2035 | 52.84 | 30.38 | 20.54 | **43.50** |
| 2040 | 55.03 | 23.52 | 15.87 | 26.90 |
| 2045 | 56.45 | 6.70 | 6.70 | 13.40 |
| 2050 | 53.34 | **0.00** | **0.00** | **0.00** |

### 8.3 Final Comparison (2050)

| Metric | BAU | Cost-Effective | Restructuring |
|--------|-----|----------------|---------------|
| **Emissions** | 53.34 Mt | **0.00 Mt** | **0.00 Mt** |
| **Reduction vs BAU** | 0% | **100%** | **100%** |
| **Total Investment** | $0 | $37.3B | $37.3B |
| **Annual Elec. Demand** | 0 TWh | 230 TWh | 230 TWh |
| **NCC Capacity Retired** | 0 kt | 0 kt | 8,314 kt |
| **Achieves Net Zero?** | No | **Yes** | **Yes** |

### 8.4 Gap Analysis

**Why Net Zero is Achieved:**
The integration of **RotoDynamic Heater (RDH)** technology allows for the decarbonization of high-temperature non-NCC processes (formerly a 17.5 Mt gap). Combined with **comprehensive NCC electrification** (covering all products) and **RE-PPA** covering all electricity consumption (including new demand from heat pumps), the model successfully eliminates all residual emissions.

| Source | Residual Emissions | Reason |
|--------|-------------------|--------|
| Non-NCC Facilities | 0.00 MtCO₂ | RDH + Heat Pump cover 100% of heat demand |
| Grid Electricity (2050) | 0.00 MtCO₂ | RE_PPA covers all electricity consumption |

---

## Appendix: Calculation Formulas

### A.1 Emission Factor Calculation

```
Total_Emissions = Σ (Fuel_Consumption × Emission_Factor)

Where:
- Naphtha EF = 0.0542 tCO₂/GJ (IPCC 2019)
- LNG EF = 0.0561 tCO₂/GJ (IPCC 2019)
- Fuel Gas EF = 0.050 tCO₂/GJ (API Compendium 2021)
- Byproduct Gas EF = 0.048 tCO₂/GJ (API Compendium 2021)
- LPG EF = 0.0631 tCO₂/GJ (IPCC 2019)
- Electricity EF = Grid_EF (varies by year: 0.436→0.0 tCO₂/MWh)
```

### A.2 Heat Pump Abatement

```
Abatement = Fossil_Emissions × Applicability - Electricity_Emissions

Electricity_Consumption = Fossil_Energy / COP / 3.6 [MWh]
Electricity_Emissions = Electricity_Consumption × Grid_EF

MACC = (CAPEX_ann + OPEX + Elec_Cost) / Abatement
```

### A.3 NCC-Electricity Abatement

```
Abatement = Baseline_Emissions (100% since using zero-emission RE)
*Note: Applied to ALL NCC products (Ethylene, Propylene, BTX, etc.)*

Electricity_Consumption = 5.0 MWh × Ethylene_Production [ton]
Electricity_Cost = RE_Price × Electricity_Consumption

MACC = (CAPEX_ann + OPEX + Elec_Cost) / Abatement
```

### A.4 LCOH (PLANiT Institute)

```
LCOH = CAPEX_Component + OPEX_Component + Stack_Component + Electricity_Component

CAPEX_Component = (CAPEX × CRF) / H2_per_kW_year
CRF = (r × (1+r)^n) / ((1+r)^n - 1)
H2_per_kW_year = 8760 × Capacity_Factor / (39.4 / Efficiency)
Electricity_Component = RE_Price × (39.4 / Efficiency) / 1000
```

---

## Data Attribution

| Data Component | Source |
|----------------|--------|
| Facility Database | Korea Petrochemical Industry Association (KPIA) |
| Emission Factors | IPCC Guidelines (2019) |
| Energy Intensity | Industry benchmarks |
| **RE-PPA Price Trajectory** | **PLANiT Institute (2025)** |
| **LCOH Methodology** | **PLANiT Institute (2025)** |
| Grid EF Trajectory | Korea Energy Agency |
| Technology CAPEX | Thunder Said Energy, IEA, McKinsey |
| **RDH Specifications** | **Coolbrook (2024)** |

---

*© PLANiT Institute 2025. All rights reserved.*
