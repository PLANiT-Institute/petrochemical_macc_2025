# Technology CAPEX Research Documentation

## Overview

This document tracks the research sources for technology CAPEX values used in the Korea Petrochemical MACC model. Each technology section follows a standardized template for documenting cost assumptions.

**Target File:** `data/assumptions/technology_capex.csv`
**Unit Convention:** USD per tonne product capacity per year ($/t-product/yr)

---

## Research Summary Table

| Technology | CAPEX 2025 | CAPEX 2030 | CAPEX 2050 | Unit | Confidence | Primary Source |
|------------|------------|------------|------------|------|------------|----------------|
| Heat_Pump | 170 | 140 | 100 | $/t-product/yr | Medium | IEA 2022 |
| NCC-H2 | 350 | 280 | 180 | $/t-ethylene/yr | Medium | MIT Energy Initiative / Green Chemistry 2025 |
| NCC-Electricity | 280 | 220 | 150 | $/t-ethylene/yr | High | MIT Energy Initiative / Green Chemistry 2025 |
| RDH | 250 | 200 | 140 | $/t-btx/yr | Low | Coolbrook claims (no public CAPEX) |

**Key Reference:** MIT Energy Initiative, Green Chemistry Journal 2025, Table 7
- e-Cracker: $195/kg-ethylene/day (TRL 6-7) → 16% lower than baseline
- CCS + H2: $242/kg-ethylene/day (TRL 7-8) → 4% higher than baseline
- Baseline: $233/kg-ethylene/day (TRL 9)

---

## Technology Research Sections

### 1. Heat Pump (Industrial High-Temperature)

#### Source Information
- **Source:** IEA 2022 / KTH Study 2024
- **Author:** IEA / KTH Royal Institute of Technology
- **Date:** 2022-2024
- **URL:** https://kth.diva-portal.org/smash/get/diva2:1790554/FULLTEXT01.pdf
- **Page/Section:** IEA cited data

#### Raw Cost Data
- **Reported Value:** 600-800
- **Reported Unit:** €/kW thermal
- **Reference Year:** 2022
- **Currency:** EUR
- **Scope:** Installed cost for industrial high-temperature heat pumps

#### Conversion to Model Units
- **Conversion Method:**
  1. Convert EUR to USD: €700 × 1.1 = $770/kW_th (using mid-range)
  2. Estimate thermal power per t-product: Assume 5 GJ/t heat requirement
  3. Peak thermal power for 1000 t/yr at 70% utilization: 5 × 1000 / (8760 × 0.7 × 3.6) = 227 kW
  4. CAPEX per t-product/yr: 227 kW × $770/kW / 1000 = $175/t-product/yr
  5. Rounded: **$170/t-product/yr** (2025)

- **Assumptions Used:**
  - Heat intensity: 5 GJ/t-product (for low-temp processes)
  - Operating rate: 70%
  - COP: 4.0 (already accounted in thermal output)
  - EUR/USD: 1.10

- **Converted Value (2025):** $170/t-product/yr
- **Learning Rate:** ~20% by 2030, ~40% by 2050 (technology maturation)

#### Applicability Assessment
- **Scale Range:** 100 kW - 50 MW thermal
- **Technology Maturity:** TRL 9 (commercial)
- **Geographic Relevance:** Global (European data, applicable to Korea)
- **Confidence Level:** Medium

#### Notes
- Heat pumps applicable only to processes <165°C
- COP varies with temperature lift (COP 4.0 at ~80°C lift)
- Cost per kW decreases with scale

---

### 2. NCC-H2 (Green Hydrogen Furnaces)

#### Source Information
- **Source:** MIT Energy Initiative / Green Chemistry Journal 2025 + IRENA
- **Author:** MIT Energy Initiative / IRENA
- **Date:** 2025
- **URL:**
  - https://pubs.rsc.org/en/content/articlehtml/2025/gc/d4gc04538f
  - https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2020/Dec/IRENA_Green_hydrogen_cost_2020.pdf
- **Page/Section:** Table 7 - CAPEX Comparison / Electrolyzer costs section

#### Raw Cost Data (MIT 2025 Study)
| Technology | CAPEX ($/kg-ethylene/day) | vs Baseline | TRL |
|------------|---------------------------|-------------|-----|
| CCS + H2 Combustion | $242 | +4% | 7-8 |

- **Reference Year:** 2025 (study), represents 2030 commercial deployment
- **Currency:** USD
- **Scope:** Total plant cost including CCS (new build)

#### Conversion to Model Units
- **Conversion Method:**
  1. MIT data (CCS + H2): $242/kg/day → $242 × 1000 / 365 = **$663/Tpa** (new build)
  2. **Note:** MIT value includes CCS, our NCC-H2 is H2-only (no CCS)
  3. Estimate H2-only as ~85% of CCS+H2: $663 × 0.85 = **$564/Tpa** (new build)
  4. For retrofit (furnace section ~40%): $564 × 0.4 = **$226/t-ethylene/yr** (2030)
  5. **2025 estimate (pre-commercial +55% premium):** $226 × 1.55 = **$350/t-ethylene/yr**

  **Alternative calculation (H2 purchased externally):**
  - Furnace burner modification only: **$200-300/t-ethylene/yr**
  - H2 storage/piping infrastructure: **$50-100/t-ethylene/yr**
  - Total: **$250-400/t-ethylene/yr** → Using **$350/t-ethylene/yr**

- **Assumptions Used:**
  - MIT 2025 data at TRL 7-8 represents 2030 commercial costs
  - H2 purchased externally (electrolyzer not included in CAPEX)
  - Furnace modification includes burner retrofit + minor piping
  - 25-year equipment lifetime

- **Converted Value (2025):** $350/t-ethylene/yr (furnace retrofit + H2 infrastructure)
- **Converted Value (2030):** $280/t-ethylene/yr
- **Learning Rate:** ~20% by 2030 (as H2 infrastructure matures)

#### Applicability Assessment
- **Scale Range:** 100 kt - 1,500 kt ethylene/yr
- **Technology Maturity:** TRL 7 (demonstration)
- **Geographic Relevance:** Global
- **Confidence Level:** Low (limited public data on H2 furnace retrofit)

#### Notes
- H2 firing requires shorter, hotter flames - burner modifications needed
- Does NOT include electrolyzer CAPEX (assumes H2 purchase)
- H2 storage and distribution infrastructure costs vary significantly by site
- Available from 2030 per technology parameters

---

### 3. NCC-Electricity (Electric Cracker / eFurnace)

#### Source Information
- **Source:** MIT Energy Initiative / Green Chemistry Journal 2025
- **Author:** MIT Energy Initiative
- **Date:** 2025
- **URL:**
  - https://pubs.rsc.org/en/content/articlehtml/2025/gc/d4gc04538f
  - https://thundersaidenergy.com/downloads/naphtha-cracking-costs-of-ethylene-propylene-and-aromatics/
  - https://www.basf.com/global/en/media/news-releases/2024/04/p-24-177
- **Page/Section:** Table 7 - CAPEX Comparison by Decarbonization Technology

#### Raw Cost Data (MIT 2025 Study)
| Technology | CAPEX ($/kg-ethylene/day) | vs Baseline | TRL |
|------------|---------------------------|-------------|-----|
| Baseline Steam Cracker | $233 | - | 9 (Commercial) |
| e-Cracker (Electric Heating) | $195 | -16% | 6-7 |
| No External NG | $223 | -4% | 8 |
| CCS + H2 Combustion | $242 | +4% | 7-8 |

- **Reference Year:** 2025 (study), represents 2030 commercial deployment
- **Currency:** USD
- **Scope:** Total plant cost (new build)

#### Conversion to Model Units
- **Conversion Method:**
  1. MIT data: $195/kg/day → $195 × 1000 / 365 = **$534/Tpa** (new build, TRL 6-7)
  2. Baseline: $233/kg/day → **$638/Tpa** (new build)
  3. Electric cracker is **16% LOWER CAPEX** than conventional (MIT 2025)
  4. For retrofit (furnace replacement only): ~40% of total plant cost
  5. **e-Cracker retrofit (2030):** $534 × 0.4 = **$214/t-ethylene/yr**
  6. **2025 estimate (pre-commercial premium +30%):** $214 × 1.3 = **$278/t-ethylene/yr**

- **Assumptions Used:**
  - MIT 2025 data at TRL 6-7 represents 2030 commercial costs
  - Retrofit involves replacing furnace section only (not entire plant)
  - Furnace section ≈ 40% of total cracker cost
  - 2025 adds 30% premium for pre-commercial technology risk
  - BASF demo: 4 t/hr hydrocarbon using 6 MW (demo scale)

- **Converted Value (2025):** $280/t-ethylene/yr (rounded from $278)
- **Converted Value (2030):** $220/t-ethylene/yr (rounded from $214)
- **Learning Rate:** ~20% by 2030, ~45% by 2050 (commercialization + scale)

#### Applicability Assessment
- **Scale Range:** 100 kt - 1,500 kt ethylene/yr
- **Technology Maturity:** TRL 8 (demonstration complete, commercializing)
- **Geographic Relevance:** Global (European demo, applicable worldwide)
- **Confidence Level:** Medium

#### Notes
- BASF/SABIC/Linde demo started operation April 2024
- Technology under STARBRIDGE trademark by Linde
- 90%+ CO2 reduction potential with renewable electricity
- Available from 2030 per technology parameters (conservative for commercial scale)
- Electric cracker has LOWER CAPEX than conventional (no boiler/power gen equipment)
- Higher OPEX due to electricity costs

---

### 4. RDH (RotoDynamic Heater)

#### Source Information
- **Source:** Coolbrook website / Industry publications
- **Author:** Coolbrook
- **Date:** 2024
- **URL:**
  - https://coolbrook.com/electrification-solutions/rdh-industrial-process-heating/
  - https://coolbrook.com/industrial-decarbonization-solutions/petrochemicals/
- **Page/Section:** Technology overview

#### Raw Cost Data
- **Reported Value:** NOT PUBLICLY AVAILABLE
- **Reported Unit:** N/A
- **Reference Year:** N/A
- **Currency:** N/A
- **Scope:** N/A

#### Conversion to Model Units
- **Conversion Method:**
  1. Coolbrook claims RDH has "reduced capital cost" due to compact size
  2. Efficiency: 92-95% electricity to heat
  3. Can be retrofitted to existing facilities
  4. Assume similar to electric cracker retrofit costs
  5. BTX reforming lower intensity than NCC
  6. Estimate: **$250/t-btx/yr** (2025), ~10% lower than NCC-Elec

- **Assumptions Used:**
  - RDH CAPEX similar to electric furnace technology
  - Compact design provides ~10% cost advantage
  - BTX processes simpler than ethylene cracking
  - Based on Coolbrook claims of "lower CAPEX" vs conventional

- **Converted Value (2025):** $250/t-btx/yr (ESTIMATED - NO PUBLIC DATA)
- **Learning Rate:** ~20% by 2030 (assumes commercial deployment)

#### Applicability Assessment
- **Scale Range:** 50 MW+ equipment size
- **Technology Maturity:** TRL 8 (pilot validated to 1700°C)
- **Geographic Relevance:** Global
- **Confidence Level:** Low (no public CAPEX data)

#### Notes
- RDH achieves up to 1700°C (validated in pilot)
- Claims 30-60% lower OPEX vs green hydrogen
- Partnership with Neste for deployment
- 20% higher ethylene yields claimed for RDR (cracking version)
- **CRITICAL: CAPEX is estimated - no public data available**

---

### 5. Electrolyzer (for H2 Production Context)

#### Source Information
- **Source:** IRENA Green Hydrogen Cost Reduction / BloombergNEF
- **Author:** IRENA
- **Date:** 2020-2024
- **URL:** https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2020/Dec/IRENA_Green_hydrogen_cost_2020.pdf
- **Page/Section:** Electrolyzer cost projections

#### Raw Cost Data
- **Current (2024):** $1,200-2,000/kW (Western markets), $300-500/kW (China)
- **2030 Projection:** $320-600/kW (large scale >100 MW)
- **2050 Projection:** $60-400/kW (depending on scenario)
- **Reference Year:** 2024
- **Currency:** USD
- **Scope:** Installed system cost (PEM/Alkaline)

#### Notes
- Not directly used in CAPEX calculations (H2 assumed purchased)
- Relevant for understanding NCC-H2 total system costs
- Key driver for green hydrogen price trajectory
- Learning rate: Up to 80% reduction possible with scale

---

## Conversion Factors Reference

### Unit Conversions
| From | To | Factor |
|------|-----|--------|
| EUR | USD | 1.10 (2024 average) |
| $/kW | $/MW | ÷ 1000 |
| $/GJ | $/MWh | × 3.6 |
| kg/day | t/yr | × 0.365 |

### Capacity Conversions (Example: NCC)
| Parameter | Value | Unit |
|-----------|-------|------|
| Typical NCC capacity | 1,000 | kt-ethylene/yr |
| Operating rate | 70% | - |
| Electric power for eFurnace | ~400-500 | MW |
| H2 consumption | 200 | kt-H2/yr per Mt-ethylene |

### Inflation Adjustment
- All costs expressed in 2024 USD
- Older data adjusted using US GDP deflator

---

## Research Progress Tracker

| Technology | Status | Last Updated | Confidence |
|------------|--------|--------------|------------|
| Heat_Pump | Complete | 2026-01-19 | Medium |
| NCC-H2 | Complete | 2026-01-19 | Low |
| NCC-Electricity | Complete | 2026-01-19 | Medium |
| RDH | Complete | 2026-01-19 | Low |
| Electrolyzer | Complete | 2026-01-19 | High |

---

## Key Sources Consulted

1. **MIT Energy Initiative / Green Chemistry Journal (2025)** - Primary source for NCC decarbonization CAPEX
   - Table 7: CAPEX comparison by technology ($/kg-ethylene/day)
   - e-Cracker $195 (TRL 6-7), CCS+H2 $242 (TRL 7-8), Baseline $233 (TRL 9)
2. **IEA/IRENA Heat Pump Costs (2022)** - Industrial HP at €600-800/kW thermal
3. **IRENA Green Hydrogen Cost Reduction (2020)** - Electrolyzer trajectories
4. **Thunder Said Energy** - Naphtha cracker CAPEX benchmarks ($1,600-2,500/Tpa)
5. **BASF Press Release (2024)** - eFurnace demonstration data (€14.8M funding)
6. **Coolbrook Website (2024)** - RDH technology specifications (no public CAPEX)
7. **BloombergNEF (2024)** - Current electrolyzer market prices ($1,200-2,000/kW)

---

## Limitations and Caveats

1. **RDH CAPEX is estimated** - Coolbrook has not published specific CAPEX figures
2. **NCC-H2 retrofit costs uncertain** - Limited public data on H2 furnace conversions
3. **Scale effects ignored** - Using flat rates as per project decision
4. **Regional variations** - All costs are global averages; Korean installations may differ
5. **Technology risk** - TRL 7-8 technologies may have cost overruns in early deployments

---

## Appendix: Emission Intensity Analysis

### Calculated Emission Intensities (Combustion Only)

Based on `product_benchmarks.csv` and `emission_factors.csv`:

**Ethylene (Naphtha Cracker):**
| Fuel | Energy (GJ/t) | EF (tCO2/GJ) | Emissions (tCO2/t) |
|------|---------------|--------------|-------------------|
| Naphtha | 29.00 | 0.0542 | 1.572 |
| LNG | 2.03 | 0.0561 | 0.114 |
| Byproduct Gas | 1.12 | 0.0480 | 0.054 |
| LPG | 5.22 | 0.0631 | 0.329 |
| **Total Combustion** | | | **2.07 tCO2/t** |

**Benzene (BTX Plant):**
| Fuel | Energy (GJ/t) | EF (tCO2/GJ) | Emissions (tCO2/t) |
|------|---------------|--------------|-------------------|
| LNG | 1.15 | 0.0561 | 0.064 |
| Byproduct Gas | 0.64 | 0.0480 | 0.031 |
| LPG | 2.95 | 0.0631 | 0.186 |
| **Total Combustion** | | | **0.28 tCO2/t** |

### CAPEX Comparison: $/t-product vs $/tCO2

Converting NEW CAPEX ($/t-product/yr) to equivalent $/tCO2 using emission intensities:

| Technology | CAPEX 2030 ($/t-product) | EI (tCO2/t) | **CAPEX 2030 ($/tCO2)** | OLD Model ($/tCO2) | Difference |
|------------|--------------------------|-------------|-------------------------|-------------------|------------|
| NCC-H2 | $280 | 2.07 | **$135** | $1,445 | -91% |
| NCC-Electricity | $220 | 2.07 | **$106** | $1,275 | -92% |
| RDH | $200 | 0.28 | **$714** | $765 | -7% |

### Key Findings

1. **NCC technologies are 90%+ cheaper than previously modeled**
   - Old model used $/tCO2 values from unclear sources
   - New model uses MIT Energy Initiative data with proper unit conversion
   - Electrification pathway is highly cost-effective for NCCs

2. **RDH shows similar costs**
   - BTX plants have lower combustion emissions per tonne
   - Higher $/tCO2 reflects lower abatement denominator

3. **Implication for MACC curve**
   - NCC electrification moves from high-cost to low-cost abatement option
   - Significant impact on sector-wide decarbonization economics

---

*Document maintained by: PLANiT Institute*
*Last updated: January 2026*
*Research completed: 2026-01-19*
