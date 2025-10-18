# AI Prompt: Detailed MACC Cost Breakdown Analysis

**Purpose**: Deep-dive cost analysis of each decarbonization technology in the Korean Petrochemical MACC Model

---

## Context

You are analyzing a Marginal Abatement Cost Curve (MACC) model for the Korean petrochemical industry (2025-2050). The model uses a **dual methodology**:

1. **Category A (Traditional MACC)**: Heat Pump, RE PPA
   - Formula: `MACC = (CAPEX_ann + OPEX_ann + ΔFuel_cost) / Abatement`

2. **Category B (LCOE Premium)**: NCC-H2, NCC-Electricity
   - Formula: `MACC = (LCOE_new - LCOE_baseline) / Emission_intensity`

**Baseline**: 52.0 MtCO2/year from 248 petrochemical facilities in Korea (2025)

---

## Technology Data Provided

### 1. Heat Pump (Industrial Heat Electrification)

**Target Application**: All low-temperature heating processes (<165°C)
**Abatement Potential**: 5.11 MtCO2/year
**Technology Readiness**: TRL 9 (Commercial)

**Key Parameters**:
```
COP (Coefficient of Performance): 4.0
CAPEX (2025): $150 M/MtCO2 abated
CAPEX trajectory: $150M (2025) → $120M (2030) → $90M (2040) → $75M (2050)
  → Learning rate: -50% over 25 years = -2.7% per year
  → Method: Linear interpolation between milestone years
  → Basis: IEA Heat Pumps Technology Roadmap (2022)
OPEX: 3.0% of CAPEX annually
Lifetime: 20 years
Discount rate: 8%
```

**Price Assumptions**:
```
Baseline fuel (naphtha): $15.0/GJ (2025) → $19.0/GJ (2050), +27%
Electricity (grid): $100/MWh (2025) → $120/MWh (2030) → $140/MWh (2050)
Grid emission factor: 0.45 tCO2/MWh (2025) → 0.25 tCO2/MWh (2050)
```

**Energy Conversion**:
```
1 GJ thermal from naphtha = 0.278 MWh electricity with COP 4.0
Cost comparison:
  Naphtha: $15/GJ = $15 per GJ thermal
  Heat pump: $100/MWh ÷ 4.0 COP = $25/MWh = $6.94/GJ thermal equivalent

Fuel savings per GJ: $15 - $6.94 = $8.06/GJ
```

**2030 Example Calculation**:
```
CAPEX annual = $120M/MtCO2 × 5.11 MtCO2 / 20 years × CRF(8%, 20yr) = $12.22/tCO2
OPEX annual = $12.22 × 3.0% = $0.37/tCO2
Fuel cost change = -$736/tCO2 (massive savings from fuel→electricity switch)

MACC = $12.22 + $0.37 - $736 = -$723.4/tCO2 (highly cost-negative)
```

**Questions for Deep Analysis**:
1. How sensitive is the MACC to electricity price changes (±20%)?
2. What is the break-even COP (where MACC = $0)?
3. How does CAPEX learning rate (current: -5% per 5 years) affect economics?
4. What is the payback period at different fuel/electricity price ratios?
5. How does the MACC change if we assume blue hydrogen production instead of grid electricity?

---

### 2. RE PPA (Renewable Energy Purchase Agreement)

**Target Application**: All grid electricity consumption (replaces grid power)
**Abatement Potential**: 7.21 MtCO2 (2025) → 1.14 MtCO2 (2050) (decreases as grid decarbonizes)
**Technology Readiness**: TRL 9 (Commercial)

**Key Parameters**:
```
CAPEX: $0 (no upfront investment, operational cost only)
OPEX: $0 (only RE power cost)
Contract type: 15-25 year PPA
RE price: $150/MWh (2025) → $120/MWh (2030) → $80/MWh (2050)
Grid price: $100/MWh (2025) → $120/MWh (2030) → $150/MWh (2050)
```

**Grid Decarbonization Timeline**:
```
2025: 0.45 tCO2/MWh (35% coal, 30% LNG, 25% nuclear, 10% RE)
2030: 0.41 tCO2/MWh (20% coal, 35% LNG, 30% nuclear, 15% RE) ← Grid parity achieved
2040: 0.33 tCO2/MWh (10% coal, 30% LNG, 20% nuclear, 40% RE)
2050: 0.25 tCO2/MWh (0% coal, 20% LNG, 10% nuclear, 70% RE)
```

**2030 Example Calculation**:
```
RE price: $120/MWh
Grid price: $120/MWh
Grid emission factor: 0.41 tCO2/MWh

Abatement per MWh = 0.41 tCO2/MWh (switching from grid to RE)
Cost difference = $120/MWh (RE) - $120/MWh (Grid) = $0/MWh

MACC = $0 / 0.41 tCO2 = $0/tCO2 (grid parity!)
```

**2050 Example Calculation**:
```
RE price: $80/MWh (learning curve)
Grid price: $150/MWh (infrastructure cost inflation)
Grid emission factor: 0.25 tCO2/MWh (still some LNG)

Cost difference = $80/MWh - $150/MWh = -$70/MWh (RE cheaper!)
Abatement per MWh = 0.25 tCO2/MWh

MACC = -$70/MWh / 0.25 tCO2 = -$280/tCO2 (cost-negative)
```

**Questions for Deep Analysis**:
1. What is the optimal PPA contract length considering price trajectory uncertainty?
2. How does curtailment risk (solar/wind intermittency) affect the effective MACC?
3. What is the "real" MACC if we include grid connection costs ($5-10M per site)?
4. How does the declining abatement potential (grid decarbonization) affect cumulative investment strategy?
5. Should companies deploy RE PPA early (2025-2030) or wait until grid parity (2030+)?

---

### 3. NCC-H2 (Naphtha Cracker with Hydrogen Feedstock)

**Target Application**: Naphtha steam crackers only (ethylene production)
**Abatement Potential**: 37.60 MtCO2/year
**Technology Readiness**: TRL 7 (Pilot scale, BASF demonstration)

**Key Parameters (LCOE-based)**:
```
Baseline LCOE: $746/ton ethylene (conventional naphtha cracker)
NCC-H2 LCOE: $850/ton (2025) → $750/ton (2030) → $500/ton (2050)

Baseline emission intensity: 0.869 tCO2/ton ethylene
NCC-H2 emission intensity: 0.900 tCO2/ton (2025, blue H2) → 0.100 tCO2/ton (2050, green H2)

H2 consumption: 0.559 kg H2/tCO2 abated (calculated from stoichiometry)
H2 price: $6.0/kg (2025, blue H2) → $5.0/kg (2030) → $1.2/kg (2050, green H2)
```

**Why LCOE Method?**
Naphtha crackers are complex integrated processes. CAPEX/OPEX are difficult to separate from feedstock costs. Using LCOE (Levelized Cost of Ethylene) from peer-reviewed literature (Woo et al. 2025, Green Chemistry) is more accurate.

**2030 Example Calculation**:
```
LCOE baseline: $746/ton ethylene
LCOE NCC-H2: $750/ton ethylene
LCOE premium: $750 - $746 = $4/ton ethylene

Emission reduction: 0.869 - 0.650 = 0.219 tCO2/ton ethylene

MACC = $4/ton / 0.219 tCO2 = $18.26/tCO2 (slightly cost-positive)
```

**2050 Example Calculation**:
```
LCOE baseline: $746/ton ethylene
LCOE NCC-H2: $500/ton ethylene (green H2 at $1.2/kg)
LCOE premium: $500 - $746 = -$246/ton ethylene (cost-negative!)

Emission reduction: 0.869 - 0.100 = 0.769 tCO2/ton ethylene

MACC = -$246/ton / 0.769 tCO2 = -$319.9/tCO2 (highly cost-negative)
```

**H2 Consumption Breakdown**:
```
For 1 tCO2 abated:
  H2 needed: 0.559 kg
  H2 cost (2030): 0.559 kg × $5.0/kg = $2.80
  H2 cost (2050): 0.559 kg × $1.2/kg = $0.67

H2 cost trajectory is the KEY driver of NCC-H2 MACC
```

**Questions for Deep Analysis**:
1. Break down the LCOE into: CAPEX, OPEX, Feedstock (H2), Energy (electricity/steam). What % is each?
2. What is the "green H2 price threshold" where NCC-H2 becomes cost-competitive with conventional? (Target: MACC < $50/tCO2)
3. How does the MACC change if blue H2 (with CCS) is used throughout (no green H2 transition)?
4. What is the sensitivity to H2 purity requirements (99.99% vs 99.9%)? Higher purity → higher cost.
5. How much electricity is needed for the cracker operation itself (separate from H2 production)?
6. What is the water consumption for H2 production (electrolysis)? Is this a constraint in Korea?

---

### 4. NCC-Electricity (Electric Steam Cracker / E-Cracker)

**Target Application**: Naphtha steam crackers only (ethylene production)
**Abatement Potential**: 37.60 MtCO2/year
**Technology Readiness**: TRL 6 (BASF-SABIC joint pilot in 2023)

**Key Parameters (LCOE-based)**:
```
Baseline LCOE: $746/ton ethylene (conventional)
E-Cracker LCOE: $743/ton (2025) → $730/ton (2030) → $690/ton (2050)

Baseline emission intensity: 0.869 tCO2/ton ethylene
E-Cracker emission intensity: 0.806 tCO2/ton (2025, grid) → 0.406 tCO2/ton (2050, cleaner grid)

Electricity consumption: 10 MWh/ton ethylene
Electricity price: $100/MWh (2025 grid) → $120/MWh (2030) → $80/MWh (2050 RE)
Grid emission factor: 0.45 tCO2/MWh (2025) → 0.25 tCO2/MWh (2050)
```

**Why Already Cost-Competitive in 2025?**
E-crackers are more energy-efficient than conventional. Even with grid electricity, fuel savings outweigh electricity cost.

**2025 Example Calculation**:
```
LCOE baseline: $746/ton ethylene
LCOE E-Cracker: $743/ton ethylene
LCOE premium: $743 - $746 = -$3/ton (slightly cheaper!)

Emission reduction: 0.869 - 0.806 = 0.063 tCO2/ton ethylene

MACC = -$3/ton / 0.063 tCO2 = -$47.6/tCO2 (cost-negative already)
```

**2050 Example Calculation**:
```
LCOE baseline: $746/ton ethylene
LCOE E-Cracker: $690/ton ethylene (with RE at $80/MWh)
LCOE premium: $690 - $746 = -$56/ton ethylene

Emission reduction: 0.869 - 0.406 = 0.463 tCO2/ton ethylene

MACC = -$56/ton / 0.463 tCO2 = -$121.0/tCO2 (highly cost-negative)
```

**Electricity Consumption Breakdown**:
```
For 1 ton ethylene production:
  Electricity needed: 10 MWh
  Electricity cost (2030, grid): 10 MWh × $120/MWh = $1,200
  Electricity cost (2050, RE): 10 MWh × $80/MWh = $800

Compare to conventional:
  Fuel cost: ~$500-600/ton ethylene
  → E-Cracker is MORE expensive in electricity alone
  → BUT more efficient overall (less heat loss, better yield)
```

**Questions for Deep Analysis**:
1. Break down E-Cracker LCOE: CAPEX, OPEX, Electricity. What % is each?
2. What is the actual ethylene yield improvement compared to conventional? (Assume 3-5%)
3. How much does yield improvement contribute to cost competitiveness?
4. What is the CAPEX for retrofitting an existing cracker vs building a new E-Cracker?
5. How does the MACC change if we assume dedicated RE (solar/wind) instead of grid power?
6. What is the load factor (capacity utilization)? E-Crackers may have less downtime → higher productivity.
7. Are there any byproduct differences (propylene, BTX)? Does this affect economics?

---

## Comparative Analysis Questions

### Cross-Technology Comparisons

1. **Portfolio Optimization**: Given a budget of $10 billion over 25 years, what is the optimal deployment sequence?
   - Heat Pump: Immediate large savings, small abatement
   - RE PPA: Medium savings, declining abatement
   - NCC-H2: Future technology, large abatement potential
   - NCC-Electricity: Already cost-negative, large abatement

2. **Risk Analysis**: Rank technologies by risk factors:
   - Technology risk (TRL)
   - Price risk (fuel/electricity/H2 volatility)
   - Policy risk (carbon pricing, subsidies)
   - Market risk (demand for ethylene)

3. **Timeline Sensitivity**: How does deployment timing affect NPV?
   - Early action (2025-2030): Higher CAPEX, but longer savings period
   - Late action (2040-2050): Lower CAPEX (learning curve), but shorter savings period

4. **Grid Decarbonization Impact**:
   - Heat Pump: Abatement decreases as grid cleans up (less emissions from electricity)
   - RE PPA: Abatement decreases (grid already clean)
   - E-Cracker: Abatement decreases (grid already clean)
   - H2-Cracker: Less affected (if green H2 from dedicated RE)

5. **Carbon Price Sensitivity**: At what carbon price does each technology become attractive?
   - Heat Pump: Already negative MACC → Deploy regardless
   - RE PPA: Negative after 2030 → Deploy regardless
   - NCC-H2: Break-even at ~$50/tCO2 (2035)
   - NCC-Electricity: Already negative MACC → Deploy regardless

---

## Data Sources & References

All data is based on peer-reviewed literature and official projections:

1. **LCOE Data**: Woo et al. (2025), "Techno-Economic Assessment of Low-Carbon Ethylene Production", Green Chemistry, DOI:10.1039/D4GC04538F
2. **H2 Prices**: IEA Hydrogen Strategy (2021), Hydrogen Council (2021)
3. **RE Prices**: IRENA Renewable Power Generation Costs (2023)
4. **Grid Emission Factor**: Korea 10th Basic Power Supply Plan (2023)
5. **Heat Pump COP**: IEA Heat Pumps Technology Collaboration Programme (2022)
6. **Discount Rate**: WACC for Korean petrochemical industry (Bloomberg, 2023)

---

## Your Task

**Please provide a detailed cost breakdown analysis for [TECHNOLOGY NAME]**, including:

1. **Component-by-component cost breakdown** (CAPEX, OPEX, fuel/electricity, O&M, etc.)
2. **Sensitivity analysis** for key parameters (±20% on critical inputs)
3. **Break-even analysis** (carbon price, fuel price, electricity price thresholds)
4. **Learning curve projection** (how much cost reduction is realistic by 2050?)
5. **Risk assessment** (technology, price, policy risks with quantified impacts)
6. **Deployment recommendation** (when to deploy, how much to deploy, under what conditions)

**Output Format**:
- Excel-compatible CSV with year-by-year breakdown (2025-2050)
- Sensitivity tornado chart data
- Break-even curves
- Summary recommendation (1-page executive summary)

**Critical Assumptions to Validate**:
- Are the price trajectories realistic? (fuel, electricity, H2)
- Is the technology learning rate achievable? (CAPEX reduction)
- Are there hidden costs? (infrastructure, training, permitting)
- Are there hidden benefits? (yield improvements, byproduct value)

---

## Example Output Template (for one technology)

```csv
year,capex_musd,opex_musd,fuel_cost_musd,electricity_cost_musd,h2_cost_musd,total_cost_musd,abatement_mt,macc_usd_per_tco2,npv_musd,cumulative_savings_musd
2025,150,4.5,0,20,0,174.5,5.11,-720,100,100
2026,120,3.6,0,22,0,145.6,5.11,-710,180,280
...
2050,75,2.25,0,15,0,92.25,5.11,-850,5000,50000
```

**Sensitivity Analysis Example**:
```csv
parameter,baseline_value,low_case_value,high_case_value,macc_change_low,macc_change_high
electricity_price_usd_per_mwh,120,96,144,-50,+50
capex_musd,150,120,180,-30,+40
cop,4.0,3.5,4.5,+80,-60
```

---

## Additional Context Files Available

If you need more detailed data, please request:

1. `data/technology_parameters.csv` - Full technology specifications
2. `data/ncc_lcoe_trajectory.csv` - Year-by-year LCOE for all NCC technologies
3. `data/fuel_price_trajectory.csv` - Fuel price projections (2025-2050)
4. `data/h2_price_trajectory.csv` - Hydrogen price projections
5. `data/re_price_trajectory.csv` - Renewable electricity price projections
6. `data/grid_emission_trajectory.csv` - Grid decarbonization timeline
7. `outputs/module_02/macc_annual_2025_2050.csv` - Full MACC results for all technologies

---

## Final Notes

- All costs in **2025 USD**
- All emissions in **tCO2** (not tCO2e)
- Discount rate: **8%** (real WACC)
- Lifetime: **20 years** (Heat Pump, RE PPA), **25 years** (NCC technologies)
- Energy units: **GJ** (thermal), **MWh** (electricity), **kg** (hydrogen)

**Key Insight**: The model shows that **Heat Pump, RE PPA, and E-Cracker are already cost-negative** (they save money while reducing emissions). The only question is deployment speed and investment availability, not whether to deploy.

**Critical Path**: H2-Cracker economics depend entirely on green H2 price reaching $1.5-2.0/kg by 2040-2050. This is the bottleneck for achieving deep decarbonization (>80% reduction).

---

**END OF PROMPT**

---

## How to Use This Prompt

1. **Copy the entire prompt** above (from "# AI Prompt" to "END OF PROMPT")
2. **Paste into another AI** (Claude, GPT-4, etc.)
3. **Specify which technology** you want analyzed (Heat Pump, RE PPA, NCC-H2, or NCC-Electricity)
4. **Provide the relevant CSV data files** from the `data/` directory
5. **Request specific analyses** (sensitivity analysis, break-even, learning curve, etc.)

The AI will provide a detailed, component-level cost breakdown with sensitivity analysis, break-even thresholds, and deployment recommendations.

---

**Created**: 2025-10-12
**Model Version**: 2.2
**Purpose**: Deep-dive MACC cost analysis using external AI
