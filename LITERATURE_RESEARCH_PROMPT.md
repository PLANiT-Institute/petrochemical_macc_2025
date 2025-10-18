# Literature Research Prompt for MACC Model Parameters

## Context
I am developing a Marginal Abatement Cost Curve (MACC) model for the Korean petrochemical industry (248 facilities, 52 MtCO2/year baseline emissions in 2025). The model evaluates four decarbonization technologies:
1. **RE PPA** (Renewable Energy Power Purchase Agreement)
2. **NCC-H2** (Hydrogen-based Steam Cracker)
3. **NCC-Electricity** (Electric Steam Cracker / e-Cracker)
4. **Heat Pump** (Industrial Heat Pump for process heat)

I need you to conduct comprehensive literature research to update model parameters with **peer-reviewed sources, industry reports, and techno-economic analyses**.

---

## Research Tasks

### **TASK 1: NCC-H2 (Hydrogen Steam Cracker) Technology Parameters**

**Required Data:**

1. **Capital Expenditure (CAPEX)**
   - **Format needed:** USD per ton of annual ethylene capacity OR USD per tCO2 abated
   - **Conversion if needed:** If given as USD/ton capacity, please convert to USD/tCO2 using:
     - Baseline emissions: 1.739 tCO2/ton ethylene (from fossil fuel combustion)
     - Facility lifetime: 25-30 years
   - **Year:** 2025 estimate (or latest available with escalation to 2025)
   - **Technology scope:** Steam cracker using green hydrogen instead of fossil fuel combustion
   - **Include:** Equipment costs, installation, integration with existing infrastructure
   - **Sources preferred:** IEA reports, academic papers (Chemical Engineering journals), industry feasibility studies

2. **Operating Expenditure (OPEX)**
   - **Format needed:** % of CAPEX per year OR USD/ton ethylene
   - **Include:** Maintenance, labor, utilities (excluding hydrogen fuel cost)
   - **Exclude:** Hydrogen purchase cost (this is tracked separately as "fuel cost")

3. **Hydrogen Consumption**
   - **Format needed:** kg H2 per kg ethylene produced OR ton H2 per ton ethylene
   - **Current assumption:** 0.20 ton H2/ton ethylene
   - **Need verification from:** Energy balance studies, pilot projects, simulation papers
   - **Context:** Hydrogen replaces ~29 GJ/ton of fossil fuel combustion energy

4. **Technology Readiness Level (TRL)**
   - Current TRL (2025)
   - Expected commercial deployment timeline
   - Known pilot/demonstration projects

**Example of ideal citation format:**
```
Source: Smith et al. (2023), "Techno-economic assessment of hydrogen-based ethylene production"
Journal: Energy Conversion and Management
Data: CAPEX = $2,500/ton capacity (2023 USD), OPEX = 4% of CAPEX
H2 consumption = 0.18 ton H2/ton ethylene
Assumptions: Green H2 at $4/kg, 25-year plant lifetime
Note: Convert to 2025 using 2% annual escalation
```

---

### **TASK 2: NCC-Electricity (Electric Steam Cracker) Technology Parameters**

**Required Data:**

1. **Capital Expenditure (CAPEX)**
   - **Format needed:** USD per ton of annual ethylene capacity OR USD per tCO2 abated
   - **Conversion:** Same as NCC-H2 above
   - **Year:** 2025 estimate
   - **Technology scope:** Electrically-heated cracker furnaces (e-cracker) or plasma cracking
   - **Include:** Electrical infrastructure, transformers, cracker modifications
   - **Sources preferred:** BASF/Sabic/Linde feasibility studies, DOE reports, academic papers

2. **Operating Expenditure (OPEX)**
   - **Format needed:** % of CAPEX per year OR USD/ton ethylene
   - **Exclude:** Electricity purchase cost (tracked separately)

3. **Electricity Consumption**
   - **Format needed:** MWh per ton ethylene produced
   - **Current assumption:** 3.0 MWh/ton ethylene
   - **Need verification from:** Energy balance calculations, pilot data
   - **Context:** Electricity replaces ~29 GJ/ton fossil fuel (=8.06 MWh thermal)
   - **Expected efficiency:** ~60-70% (accounting for electrical heating efficiency)

4. **Technology Readiness Level**
   - Current TRL (2025)
   - Commercial readiness timeline
   - Existing demonstration projects (BASF, etc.)

**Example citation:**
```
Source: Johnson & Lee (2024), "Electrification of steam cracking: A pathway to net-zero"
Report: International Energy Agency - Energy Technology Perspectives 2024
Data: CAPEX = $3,200/ton capacity (2024 USD), OPEX = 3.5% of CAPEX
Electricity = 2.8 MWh/ton ethylene
Grid emissions factor: 0.45 tCO2/MWh (baseline), declining to 0.1 by 2050
```

---

### **TASK 3: Heat Pump Technology Parameters**

**Required Data:**

1. **Capital Expenditure (CAPEX)**
   - **Format needed:** USD per MtCO2 abated per year OR USD per MW thermal capacity
   - **Current assumption:** $900M per MtCO2/year abated
   - **Year:** 2025 estimate
   - **Technology scope:** High-temperature industrial heat pumps (up to 200°C for BTX plants)
   - **Application:** Replace fossil fuel combustion in aromatics separation (BTX plants)
   - **Sources preferred:** IEA Heat Pump reports, EHPA studies, industrial case studies

2. **Operating Expenditure (OPEX)**
   - **Format needed:** % of CAPEX per year
   - **Current assumption:** 3% of CAPEX

3. **Coefficient of Performance (COP)**
   - **Format needed:** Dimensionless ratio (heat output / electrical input)
   - **Current assumption:** 4.0
   - **Temperature range:** Heat delivery at 100-200°C (BTX separation processes)
   - **Need:** COP values at different temperature lifts

4. **Applicability**
   - Which petrochemical processes can use heat pumps?
   - Maximum temperature limitations
   - Integration challenges

**Example citation:**
```
Source: European Heat Pump Association (2023), "Large-scale heat pumps in industry"
Data: CAPEX = €800/kW thermal (≈ $900/kW), COP = 3.5-4.5 at 150°C delivery
OPEX = 2-4% of CAPEX (maintenance only, excluding electricity)
Suitable for: Distillation, separation processes <200°C
```

---

### **TASK 4: Energy Price Trajectories (South Korea, 2025-2050)**

**Required Data:**

1. **Green Hydrogen Price**
   - **Format needed:** USD/kg H2 (Lower Heating Value basis)
   - **Current assumption:** $12/kg (2025), declining to $2/kg (2050)
   - **Need:** Realistic trajectory for South Korea/Asia
   - **Sources:** IEA Hydrogen reports, BloombergNEF, IRENA, Korean government H2 roadmap
   - **Include:** Production method (electrolysis), transport costs, storage

2. **Renewable Electricity (RE PPA) Price**
   - **Format needed:** USD/MWh
   - **Current assumption:** $130/MWh (2025), declining to $55/MWh (2050)
   - **Need:** South Korea corporate PPA prices (solar/wind)
   - **Context:** Compared to grid price of $100/MWh (₩100/kWh = $0.10/kWh)
   - **Sources:** Korean RE PPA market data, KEPCO tariffs, Bloomberg energy market reports

3. **Grid Electricity Price (Industrial)**
   - **Format needed:** USD/MWh or USD/kWh
   - **Current assumption:** $100/MWh (₩100/kWh)
   - **Need:** South Korean industrial electricity tariff
   - **Year range:** 2025-2050 projection
   - **Sources:** KEPCO, Korean Ministry of Trade, IEA Korea energy outlook

4. **Fossil Fuel Prices**
   - **Naphtha:** USD/GJ (current: $15/GJ)
   - **LNG:** USD/GJ (current: $15/GJ)
   - Need: Asian spot prices or South Korean import prices

**Example citation:**
```
Source: IEA (2024), "Global Hydrogen Review 2024"
Data for South Korea/Asia:
- Green H2: $10/kg (2025), $6/kg (2030), $3/kg (2040), $2/kg (2050)
- Assumptions: Electrolyzer CAPEX $500/kW (2025) → $200/kW (2050)
- RE electricity at $40-50/MWh

Source: KEPCO (2024), "Industrial Tariff Schedule"
- Large industrial users: ₩110/kWh (2024) = $0.11/kWh = $110/MWh
- Includes transmission/distribution costs
```

---

### **TASK 5: Emission Factors**

**Required Data:**

1. **South Korean Electricity Grid Emission Factor**
   - **Format needed:** tCO2/MWh
   - **Current assumption:** 0.45 tCO2/MWh (2025), declining to 0.23 tCO2/MWh (2050)
   - **Need:** Official Korean grid mix projections under net-zero scenarios
   - **Sources:** Korean government NDC reports, IEA Korea, Ministry of Environment

2. **Naphtha Combustion Emission Factor**
   - **Format needed:** tCO2/GJ (LHV basis)
   - **Current value:** 0.0542 tCO2/GJ (back-calculated to match 52 MtCO2 total)
   - **Need verification:** Standard IPCC value for naphtha combustion
   - **Note:** This seems high compared to typical ~0.073 tCO2/GJ for naphtha

3. **Renewable Electricity Lifecycle Emission Factor**
   - **Format needed:** tCO2/MWh (lifecycle)
   - **Current assumption:** 0.05 tCO2/MWh
   - **Need:** Solar/wind lifecycle emissions for South Korea

**Example citation:**
```
Source: Korean Ministry of Environment (2023), "10th Basic Plan for Electricity Supply and Demand"
Data: Grid emission factor trajectory
- 2025: 0.436 tCO2/MWh
- 2030: 0.349 tCO2/MWh (40% coal, 30% gas, 25% nuclear, 5% renewables)
- 2040: 0.250 tCO2/MWh (20% coal, 25% gas, 30% nuclear, 25% renewables)
- 2050: 0.150 tCO2/MWh (net-zero target)
```

---

### **TASK 6: Baseline Energy Consumption Verification**

**Required Data:**

1. **Naphtha Fuel Consumption in Steam Cracking**
   - **Format needed:** GJ per ton ethylene produced (fuel only, not feedstock)
   - **Current assumption:** 29 GJ/ton ethylene (revised from 105.47 GJ)
   - **Need verification:** Is this realistic for Korean naphtha crackers?
   - **Sources:** Best Available Technology (BAT) benchmarks, Korean petrochemical industry reports

2. **Energy Balance Check**
   - Total energy: Naphtha fuel (29 GJ) + LNG (4.49 GJ) + Fuel gas (5.62 GJ) = ~40 GJ/ton ethylene
   - Is this consistent with industry benchmarks?
   - Typical range: 30-50 GJ/ton ethylene depending on efficiency

**Example citation:**
```
Source: Ren et al. (2006), "Best available techniques assessment for steam cracking"
Journal: Applied Energy
Data: Modern naphtha crackers (2000s technology):
- Fuel consumption: 38-45 GJ/ton ethylene (HHV basis)
- Feedstock: 2.7-3.0 ton naphtha/ton ethylene
- Breakdown: Process furnace (60%), utilities (25%), other (15%)
```

---

## Output Format Requirements

For each parameter, please provide:

1. **Data value** with units clearly specified
2. **Source citation** (Author, Year, Title, Publication)
3. **Geographic scope** (Global average, Asia, South Korea specific)
4. **Year of data** and any escalation/projection methodology
5. **Assumptions** underlying the data (e.g., plant size, technology maturity)
6. **Uncertainty range** if available (low/base/high estimates)
7. **Your assessment** of data quality (high/medium/low confidence)

**Example output table:**

| Parameter | Value | Unit | Source | Year | Geography | Confidence | Notes |
|-----------|-------|------|--------|------|-----------|------------|-------|
| NCC-H2 CAPEX | $2,800 | USD/ton capacity | IEA (2024) | 2025 | Global | Medium | Assumes 1000 kt/y plant scale |
| H2 consumption | 0.19 | ton H2/ton C2H4 | Wang (2023) | 2023 | Simulation | High | Energy balance validated |
| Grid EF (Korea) | 0.436 | tCO2/MWh | MOE (2023) | 2025 | South Korea | High | Official government data |

---

## Critical Validation Points

Please flag if you find:
1. **Contradictory data** from multiple sources (explain discrepancy)
2. **Missing data** for critical parameters (suggest proxy/assumption)
3. **Outdated data** (>5 years old) - note if more recent sources not found
4. **Geographic mismatch** (e.g., EU data applied to Korea) - suggest adjustment factors

---

## Priority Ranking

**High Priority** (needed for credible MACC):
- NCC-H2 CAPEX and H2 consumption
- NCC-Electricity CAPEX and electricity consumption
- Korean grid emission factor trajectory
- Green H2 price trajectory for Asia

**Medium Priority** (refinement):
- Heat Pump COP and applicability
- RE PPA prices in Korea
- OPEX percentages

**Low Priority** (can use assumptions):
- Naphtha price trajectory
- Technology lifetime variations

---

## Additional Context

**Model Structure:**
- MACC = (CAPEX_annual + OPEX_annual + Fuel_cost) / Abatement_potential
- CAPEX_annual = CAPEX × Capital_Recovery_Factor (8% discount rate, 25-year lifetime)
- Fuel_cost = New fuel cost ONLY (fossil fuel savings are NOT counted)
- Abatement = Baseline emissions - New technology emissions

**Korean Petrochemical Industry:**
- 41 naphtha crackers (11.5 Mt ethylene/year capacity)
- 47 BTX plants (aromatics)
- 160 downstream polymer/chemical facilities
- Total baseline: 52 MtCO2/year (2025)

**Target audience for model:**
- Korean government policy makers
- Petrochemical industry stakeholders
- Academic publication in energy/environment journals

---

## Deliverable

Please provide a **comprehensive literature review document** organized by the 6 tasks above, with:
- Summary table of all recommended parameter updates
- Full citations (APA format)
- Assessment of data gaps and recommended assumptions
- Comparison of our current assumptions vs. literature values
- Recommended "base case", "conservative", and "optimistic" scenarios if uncertainty is high

**Estimated word count:** 3,000-5,000 words with 30-50 citations

Thank you for your thorough research!
