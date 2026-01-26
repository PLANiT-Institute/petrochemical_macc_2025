# Korea Petrochemical Industry Decarbonization: Transition Costs and Renewable Energy Pathways

---

## Executive Summary

This analysis examines decarbonization pathways for Korea's petrochemical industry using facility-level modeling of **237-243 production facilities** across **six scenarios**. Key findings:

| Metric | Range Across Scenarios |
|--------|------------------------|
| Baseline Emissions (2025) | 54.8 - 59.2 Mt CO2 |
| Cumulative CAPEX (2025-2050) | $113.5B - $1,242.1B |
| H2 Demand (2050) | 0 - 4.3 Mt/year |
| Electricity Demand (2050) | 18.5 - 273.6 TWh/year |
| Stranded Assets (1.5C) | $14.4B - $24.6B |

---

## 1. Background and Purpose

### 1-1. Background

The scale of greenhouse gas emissions from Korea's petrochemical industry stands at approximately **78 million tonnes** (including upstream and utility processes), significantly higher than the initial 50 million tonne estimate for direct manufacturing. This makes it a critical emitter within the industrial sector. Although most energy consumption originates from naphtha, it remains an energy-intensive industry consuming significant petroleum-based energy. Moreover, with restructuring discussions intensifying due to the accumulated losses of major petrochemical companies over recent years, the Korean economy faces a critical juncture requiring strategic decisions from an economic perspective.

This project seeks to answer the following questions:

1. What scale of renewable energy and electrification is required for the petrochemical industry to meet its carbon budget commitments?
2. What is the cost of the recently discussed petrochemical decarbonization technology, particularly the electric furnace?
3. What are the transition costs and renewable energy adoption levels for each company?
4. What is the carbon budget and carbon neutrality pathway?

---

### 1-2. Key Assumptions

#### 1-2-1. Total Energy Consumption of the Petrochemical Industry
The industry consumes a mix of Naphtha, Electricity, LNG, and various byproduct gases. Naphtha represents the primary feedstock and energy source, with an energy intensity of approximately **29.0 GJ/tonne** for ethylene production.

#### 1-2-2. Product Output by Facility Type in the Petrochemical Industry
The model tracks production for key facilities including Naphtha Crackers (Ethylene, Propylene, Butadiene), BTX Plants (Benzene, Toluene, Xylene), and various utility and polymerization units.

#### 1-2-3. Energy Consumption per Product in the Petrochemical Industry
Energy intensities vary significantly:
- **Ethylene**: ~29 GJ Naphtha + 85.4 kWh Electricity + 2.03 GJ LNG per tonne.
- **Propylene**: ~25.4 GJ Naphtha + 191.3 kWh Electricity + 1.78 GJ LNG per tonne.
- **HDPE**: ~1370.6 kWh Electricity per tonne.

#### 1-2-4. Greenhouse Gas Emission Factors by Energy Source
| Energy Source | Emission Factor | Unit |
|---------------|-----------------|------|
| Naphtha | 0.0542 | tCO2/GJ |
| Grid Electricity | 0.436 | tCO2/MWh |
| LNG | 0.0561 | tCO2/GJ |
| Fuel Gas | 0.050 | tCO2/GJ |
| Byproduct Gas | 0.048 | tCO2/GJ |
| Green Hydrogen | 0.0 | tCO2/kg |

#### 1-2-5. Carbon Budget Pathways for the Petrochemical Industry
Three pathways are defined:
- **1.5C Pathway**: Target of 50M tCO2 in 2025, reaching Net Zero by 2035.
- **2.0C Pathway**: Target of 60M tCO2 in 2025, reaching 10M tCO2 by 2050.
- **NDC Pathway**: Target of 70M tCO2 in 2025, reaching 45M tCO2 by 2050.

#### 1-2-6. Costs and Energy Consumption per Unit of Product for Key Mitigation Measures

| Technology | Application | Available | CAPEX 2025 | CAPEX 2050 | Key Specification |
|------------|-------------|-----------|------------|------------|-------------------|
| Heat Pump | <165C processes | 2025 | $800/tCO2 | $400/tCO2 | COP 4.0 |
| NCC-H2 | Naphtha crackers | 2030 | $1,700/tCO2 | $850/tCO2 | 0.2 t-H2/t-ethylene |
| NCC-Electricity | Naphtha crackers | 2030 | $1,500/tCO2 | $750/tCO2 | 5.0 MWh/t-ethylene |
| RDH | High-temp BTX | 2026 | $900/tCO2 | $450/tCO2 | 93% efficiency |
| RE-PPA | Grid electricity | 2025 | $0 | $0 | Renewable PPA |

All technologies assume **50% CAPEX decline** by 2050 via learning curves.

#### 1-2-7. Key Energy Price Projections

| Energy Source | 2025 | 2030 | 2040 | 2050 |
|---------------|------|------|------|------|
| Green H2 ($/kg) | 4.58 | 3.50 | 2.50 | 2.01 |
| RE-PPA ($/MWh) | 65 | 55 | 40 | 30 |
| Grid Electricity ($/MWh) | 100 | 120 | 150 | 191 |
| Grid EF (tCO2/MWh) | 0.436 | 0.35 | 0.15 | 0.0 |

---

### 1-3. Model Design

This project encompasses a total of **237-243 interconnected production facilities**, across **six scenarios**.

#### 1-3-1. Scenario Definitions

| Scenario | Production Pathway | NCC Technology | Facilities | Description |
|----------|-------------------|----------------|------------|-------------|
| shaheen_ncc_h2 | Shaheen (Growth) | Hydrogen | 243 | +6 new S-Oil facilities from 2026 |
| shaheen_ncc_elec | Shaheen (Growth) | Electric | 243 | +6 new S-Oil facilities from 2026 |
| restructure_25pct_ncc_h2 | 25% Restructure | Hydrogen | 237 | Retire 25% oldest NCC capacity |
| restructure_25pct_ncc_elec | 25% Restructure | Electric | 237 | Retire 25% oldest NCC capacity |
| restructure_40pct_ncc_h2 | 40% Restructure | Hydrogen | 237 | Retire 40% oldest NCC capacity |
| restructure_40pct_ncc_elec | 40% Restructure | Electric | 237 | Retire 40% oldest NCC capacity |

#### 1-3-2. Definition of Stranded Assets
Stranded assets are defined based on the remaining net book value (NBV) of facilities that are forced into early retirement or high-cost retrofits to meet carbon budgets. The model uses a 25-year lifetime for major assets.

#### 1-3-3. Cost Optimization
The model uses a Marginal Abatement Cost Curve (MACC) approach to prioritize the lowest-cost abatement measures at each facility, subject to technology readiness (TRL) and available carbon budgets.

#### 1-3-4. Model Limitations
- Linear interpolation for CAPEX declines.
- Static production capacity unless explicitly restructured in specific scenarios.
- Grid emission factors are based on fixed national trajectories.

---

## 2. Scenario Results

### 2-1. Six-Scenario Summary

#### Table 2-1-1: Comprehensive Scenario Comparison (2025-2050)

| Scenario | Baseline Emissions (Mt) | Final Emissions (Mt) | Cumulative CAPEX ($B) | Elec Demand 2050 (TWh) | H2 Demand 2050 (Mt) |
|----------|------------------------|----------------------|----------------------|----------------------|---------------------|
| shaheen_ncc_h2 | 59.25 | 0.0 | 825.87 | 166.43 | 4.28 |
| shaheen_ncc_elec | 59.25 | 0.0 | 1,242.06 | 273.58 | 0.00 |
| restructure_25pct_ncc_h2 | 54.81 | 0.0 | 157.68 | 18.49 | 2.33 |
| restructure_25pct_ncc_elec | 54.81 | 0.0 | 160.34 | 76.89 | 0.00 |
| restructure_40pct_ncc_h2 | 54.81 | 0.0 | 113.47 | 40.97 | 2.03 |
| restructure_40pct_ncc_elec | 54.81 | 0.0 | 115.45 | 93.32 | 0.00 |

**Key Findings:**
- **All scenarios achieve Net Zero by 2050** through technology deployment
- **Restructuring scenarios** reduce cumulative CAPEX by 85-91% vs. Shaheen scenarios
- **H2-based scenarios** consistently have lower cumulative CAPEX than electric alternatives
- **Electric scenarios** require 4-15x more electricity infrastructure

![Emissions Trajectory](../outputs/figures/report_emissions_trajectory.png)
*Figure 2-1: Emissions trajectory by scenario (2025-2050)*

---

### 2-2. Regional Analysis

#### 2-2-1. Regional Baseline Emissions

| Region | Baseline Emissions (Mt CO2) | Share of Total |
|--------|----------------------------|----------------|
| Yeosu | 22.41 | 37.8% |
| Daesan | 17.22 | 29.1% |
| Ulsan | 14.81 - 19.24* | 25.0% - 32.5% |
| Other | 0.38 | 0.6% |

*Ulsan emissions vary between 14.81 Mt (restructure scenarios) and 19.24 Mt (Shaheen scenarios due to new S-Oil facilities)

#### 2-2-2. Regional Transition Costs by Scenario

| Region | Scenario | Cumulative CAPEX ($B) | Cumulative Total Cost ($B) | H2 Demand (Mt) |
|--------|----------|----------------------|---------------------------|----------------|
| **Yeosu** | shaheen_ncc_h2 | 323.72 | 31.59 | 1.65 |
| **Yeosu** | shaheen_ncc_elec | 468.42 | -23.62 | 0.00 |
| **Daesan** | shaheen_ncc_h2 | 231.03 | 23.08 | 1.33 |
| **Daesan** | shaheen_ncc_elec | 382.38 | -18.61 | 0.00 |
| **Ulsan** | shaheen_ncc_h2 | 268.06 | 25.12 | 1.31 |
| **Ulsan** | shaheen_ncc_elec | 388.19 | -19.23 | 0.00 |
| **Other** | shaheen_ncc_h2 | 3.06 | 0.24 | 0.00 |

**Note:** Negative total costs indicate net fuel savings exceeding new energy costs over the analysis period.

![Regional Heatmap](../outputs/figures/report_regional_heatmap.png)
*Figure 2-2: Regional emissions evolution over time (Shaheen NCC-H2 scenario)*

---

### 2-3. Company Analysis

#### 2-3-1. Top 10 Emitters - Baseline Emissions

| Rank | Company | Baseline Emissions (Mt CO2) | Share |
|------|---------|---------------------------|-------|
| 1 | LG Chem | 14.36 | 18.4% |
| 2 | Lotte Chemical | 11.20 | 14.3% |
| 3 | Yeochon NCC | 8.62 | 11.0% |
| 4 | Hanwha TotalEnergies | 7.44 | 9.5% |
| 5 | GS Caltex | 5.19 | 6.6% |
| 6 | SK Geocentric | 5.01 | 6.4% |
| 7 | HD Hyundai Chemical | 4.96 | 6.3% |
| 8 | Daehan Oil Chemical | 3.86 | 4.9% |
| 9 | S-Oil | 2.98 | 3.8% |
| 10 | Hanwha Solutions | 2.01 | 2.6% |

**The top 4 companies account for 53.2% of total industry emissions.**

#### 2-3-2. Company Emissions by Region

| Company | Daesan | Yeosu | Ulsan | Other |
|---------|--------|-------|-------|-------|
| LG Chem | 4.14 Mt | 5.87 Mt | - | - |
| Lotte Chemical | 3.92 Mt | 4.56 Mt | 1.15 Mt | - |
| Yeochon NCC | - | 8.62 Mt | - | - |
| Hanwha TotalEnergies | 7.44 Mt | - | - | - |
| GS Caltex | - | 5.19 Mt | - | - |
| SK Geocentric | - | - | 5.01 Mt | - |

---

### 2-4. Scenario Comparison: H2 vs Electric

#### 2-4-1. Cost-Effectiveness Comparison

| Metric | H2 Scenarios (Avg) | Electric Scenarios (Avg) | Difference |
|--------|-------------------|-------------------------|------------|
| Cumulative CAPEX ($B) | 365.68 | 505.95 | H2 28% lower |
| Electricity Demand (TWh) | 75.30 | 147.93 | Electric 96% higher |
| H2 Demand (Mt) | 2.88 | 0.00 | H2 scenarios only |
| Net Operating Savings | Positive | Negative | H2 more favorable |

![H2 vs Electric Comparison](../outputs/figures/report_h2_vs_elec.png)
*Figure 2-3: Cumulative CAPEX and energy demand comparison by scenario*

#### 2-4-2. MACC Curves by Scenario

![MACC Curves](../outputs/figures/report_macc_curves.png)
*Figure 2-4: Marginal Abatement Cost Curves for all six scenarios (2050)*

---

## 3. Gap Analysis: Targets vs. Reality

> [!CAUTION]
> There is a severe "Carbon Gap" between current industry emissions and required targets.

### 3-1. Carbon Budget Pathways

| Year | Baseline (Mt) | 1.5C Target (Mt) | 1.5C Gap (Mt) | 2.0C Target (Mt) | 2.0C Gap (Mt) | NDC Target (Mt) | NDC Gap (Mt) |
|------|---------------|------------------|---------------|------------------|---------------|-----------------|--------------|
| 2025 | 59.25 | 50.0 | **9.25** | 60.0 | -0.75 | 70.0 | -10.75 |
| 2030 | 59.25 | 25.0 | **34.25** | 50.0 | 9.25 | 65.0 | -5.75 |
| 2035 | 59.25 | 0.0 | **59.25** | 40.0 | 19.25 | 60.0 | -0.75 |
| 2040 | 59.25 | 0.0 | **59.25** | 30.0 | 29.25 | 55.0 | 4.25 |
| 2050 | 59.25 | 0.0 | **59.25** | 10.0 | 49.25 | 45.0 | 14.25 |

### 3-2. Technology Availability Constraints

| Period | Available Technologies | Abatement Potential | Constraint |
|--------|----------------------|---------------------|------------|
| 2025-2029 | Heat Pump, RDH | Limited (~10-15%) | NCC technologies not yet available |
| 2030-2035 | All technologies | Full deployment possible | Significant CAPEX required |
| 2035-2050 | All technologies | Net Zero achievable | Declining costs enable deployment |

**Critical Finding:** The 1.5C pathway requires Net Zero by 2035, but NCC technologies (which address 70%+ of emissions) are not available until 2030. This creates a **structural impossibility** for the 1.5C pathway without drastic capacity restructuring.

---

## 4. Implications

### 4-1. Renewable Energy Infrastructure Requirements

#### 4-1-1. Electricity Demand by Scenario (2050)

| Scenario | Added Electricity (TWh) | Equivalent RE Capacity (GW)* |
|----------|------------------------|------------------------------|
| shaheen_ncc_h2 | 166.43 | 47.6 |
| shaheen_ncc_elec | 273.58 | 78.2 |
| restructure_25pct_ncc_h2 | 18.49 | 5.3 |
| restructure_25pct_ncc_elec | 76.89 | 22.0 |
| restructure_40pct_ncc_h2 | 40.97 | 11.7 |
| restructure_40pct_ncc_elec | 93.32 | 26.7 |

*Assuming 40% capacity factor for renewable generation

#### 4-1-2. Green Hydrogen Demand by Scenario (2050)

| Scenario | H2 Demand (Mt/year) | Electrolyzer Capacity (GW)* |
|----------|--------------------|-----------------------------|
| shaheen_ncc_h2 | 4.28 | 85.6 |
| restructure_25pct_ncc_h2 | 2.33 | 46.6 |
| restructure_40pct_ncc_h2 | 2.03 | 40.5 |

*Assuming 50 kg H2/kW/year electrolyzer output

---

### 4-2. Stranded Assets Analysis

#### 4-2-1. Stranded Asset Values by Scenario

| Scenario | 1.5C Stranding Year | 1.5C Stranded Value | 2.0C Stranding Year | 2.0C Stranded Value |
|----------|--------------------|--------------------|--------------------|--------------------|
| shaheen_ncc_h2 | 2029 | $22.98B | 2050 | $5.27B |
| shaheen_ncc_elec | 2028 | $24.61B | 2042 | $10.43B |
| restructure_25pct_ncc_h2 | 2032 | $14.41B | 2050 | $3.45B |
| restructure_25pct_ncc_elec | 2032 | $14.41B | 2050 | $3.45B |
| restructure_40pct_ncc_h2 | 2030 | $16.75B | 2050 | $3.45B |
| restructure_40pct_ncc_elec | 2030 | $16.75B | 2050 | $3.45B |

![Stranded Assets](../outputs/figures/report_stranded_assets.png)
*Figure 4-1: Stranded asset risk by scenario and climate pathway*

**Key Findings:**
- **1.5C pathway creates $14.4B - $24.6B in stranded assets** across all scenarios
- **Electric scenarios have higher stranding risk** due to earlier required action
- **Restructuring reduces stranding by 30-40%** compared to growth scenarios
- **2.0C pathway significantly reduces stranding** ($3.45B - $10.43B range)

---

### 4-3. Financial Analysis

#### 4-3-1. Cumulative Investment Requirements (2025-2050)

| Scenario | Cumulative CAPEX ($B) | Cumulative OPEX ($B)* | Net Total Cost ($B) |
|----------|----------------------|----------------------|---------------------|
| shaheen_ncc_h2 | 825.87 | 165.17 | 80.04 |
| shaheen_ncc_elec | 1,242.06 | 248.41 | -61.22 |
| restructure_25pct_ncc_h2 | 157.68 | 31.54 | 5.99 |
| restructure_25pct_ncc_elec | 160.34 | 32.07 | -19.89 |
| restructure_40pct_ncc_h2 | 113.47 | 22.69 | 3.56 |
| restructure_40pct_ncc_elec | 115.45 | 23.09 | -15.00 |

*Estimated at 20% of cumulative CAPEX

**Key Findings:**
- **Restructuring scenarios reduce CAPEX by 85-91%** compared to growth scenarios
- **Electric scenarios show negative net costs** due to fuel savings exceeding new energy costs
- **H2 scenarios have positive net costs** due to higher H2 prices vs. electricity savings

---

## 5. Technology Deployment Timeline

### 5-1. Technology Availability Schedule

| Technology | TRL (2025) | Available From | First Major Deployment |
|------------|------------|----------------|------------------------|
| Heat Pump | 9 | 2025 | 2026 |
| RDH | 8 | 2026 | 2026 |
| NCC-Electricity | 8 | 2030 | 2039-2041 |
| NCC-H2 | 7 | 2030 | 2039-2041 |

### 5-2. Deployment Waves by Scenario (Shaheen NCC-H2)

| Year | Heat Pump Facilities | RDH Facilities | NCC-H2 Facilities | Total Deployed |
|------|---------------------|----------------|-------------------|----------------|
| 2026 | 53 | 0 | 0 | 53 |
| 2030 | 53 | 0 | 0 | 53 |
| 2035 | 53 | 0 | 0 | 53 |
| 2040 | 53 | 35 | 7 | 95 |
| 2045 | 53 | 35 | 25 | 113 |
| 2050 | 53 | 35 | 41 | 129 |

![Technology Timeline](../outputs/figures/report_tech_timeline.png)
*Figure 5-1: Technology deployment timeline (Shaheen NCC-H2 scenario)*

### 5-3. CAPEX Trajectory by Technology

| Technology | CAPEX 2025 ($M/MtCO2) | CAPEX 2030 | CAPEX 2040 | CAPEX 2050 | Decline |
|------------|----------------------|------------|------------|------------|---------|
| Heat Pump | 800 | 680 | 520 | 400 | 50% |
| NCC-H2 | 1,700 | 1,445 | 1,105 | 850 | 50% |
| NCC-Electricity | 1,500 | 1,275 | 975 | 750 | 50% |
| RDH | 900 | 765 | 585 | 450 | 50% |

---

## 6. Facility-Level Analysis

### 6-1. Facility Distribution by Region and Process

| Region | Naphtha Crackers | BTX Plants | Utility/Other | Total |
|--------|------------------|------------|---------------|-------|
| Daesan | 4 | 12 | 39 | 55 |
| Yeosu | 4 | 14 | 67 | 85 |
| Ulsan | 3 | 18 | 64 | 85 |
| Other | 0 | 4 | 14 | 18 |
| **Total** | **11** | **48** | **184** | **243** |

### 6-2. Facility-Level MAC Distribution

![Facility Scatter](../outputs/figures/report_facility_scatter.png)
*Figure 6-1: Facility-level MAC vs abatement potential (2050)*

**Key Observations:**
- **Naphtha crackers** have the highest abatement potential (>100 kt CO2/facility)
- **MAC ranges from $50-500/tCO2** depending on facility and technology
- **Yeosu facilities** cluster at higher abatement potential
- **Ulsan facilities** show more cost variation

---

## 7. Conclusions and Recommendations

### 7-1. Key Conclusions

1. **All scenarios achieve Net Zero by 2050** - Technical feasibility confirmed across all pathways
2. **Restructuring significantly reduces costs** - 85-91% CAPEX reduction vs. growth scenarios
3. **H2 scenarios have lower CAPEX** but require massive hydrogen infrastructure
4. **Electric scenarios have higher CAPEX** but potentially negative net costs due to fuel savings
5. **1.5C pathway is structurally challenging** due to technology availability constraints
6. **Stranded asset risk is substantial** ($14-25B under 1.5C pathway)

### 7-2. Policy Implications

| Policy Area | Recommendation | Rationale |
|-------------|----------------|-----------|
| **Production Planning** | Consider 25-40% capacity restructuring | Reduces CAPEX by 85%+, manages stranding risk |
| **Technology Investment** | Prioritize H2 infrastructure | Lower total system cost, enables flexibility |
| **Carbon Pricing** | Align with 2.0C pathway | 1.5C is technically infeasible before 2030 |
| **RE Deployment** | Plan for 50-80 GW additional capacity | Required for either H2 or electric pathways |

### 7-3. Limitations

> [!IMPORTANT]
> This analysis has the following limitations:
> - Does not account for potential demand shifts to bio-based or recycled feedstocks
> - Assumes fixed technology cost reduction trajectories
> - Grid emission factors follow government projections (may vary)
> - Does not model regional grid constraints or hydrogen transport infrastructure

---

## Appendix A: Methodology

### A-1. Data Sources

| Data Type | Source | Update Frequency |
|-----------|--------|------------------|
| Facility Database | KPIA, company reports | Annual |
| Energy Intensities | IEA, KIER benchmarks | 2-3 years |
| Technology Costs | IRENA, academic literature | Annual |
| Price Trajectories | IEA WEO, BNEF | Annual |

### A-2. Model Equations

**Baseline Emissions:**
```
E_baseline = Sum(Production_i × EI_i × EF_fuel)
```

**Marginal Abatement Cost:**
```
MAC = (CAPEX_annual + OPEX + New_Energy_Cost - Fuel_Savings) / Abatement
```

**Levelized Cost of Abatement:**
```
LCOA = Sum(Annual_Cost_t / (1+r)^t) / Sum(Abatement_t)
```
where r = 8% discount rate

---

## Appendix B: Complete Company Emissions List

| Company | Total Emissions (tCO2) |
|---------|----------------------|
| LG Chem | 14,358,266 |
| Lotte Chemical | 11,197,668 |
| Yeochon NCC | 8,617,271 |
| Hanwha TotalEnergies | 7,440,228 |
| GS Caltex | 5,190,277 |
| SK Geocentric | 5,006,242 |
| HD Hyundai Chemical | 4,960,305 |
| Daehan Oil Chemical | 3,858,611 |
| S-Oil | 2,981,254 |
| Hanwha Solutions | 2,006,378 |
| Kumho Petrochemical | 1,499,946 |
| SK Energy | 1,191,309 |
| SK Advanced | 1,152,880 |
| Hyosung Chemical | 1,104,148 |
| Taekwang Industrial | 1,041,685 |
| HDHyundai Oilbank | 907,458 |
| Hanwha Impact | 682,928 |
| Samnam Petrochemical | 512,196 |
| Caprolactam | 507,861 |
| Korea INEOS Styrolution | 402,279 |
| Others (41 companies) | 3,634,127 |
| **Total** | **78,247,366** |

---

*Report generated: January 2026*
*Data vintage: 2025*
*Model version: MACC v0.4*
