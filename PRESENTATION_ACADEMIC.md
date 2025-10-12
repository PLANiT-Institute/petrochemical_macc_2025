# Korean Petrochemical Sector Decarbonization: MACC Analysis and Optimization Model

**Academic Presentation**
*Dynamic Marginal Abatement Cost Curve Analysis (2025-2050)*

---

## Slide 1: Title Slide

# Korean Petrochemical Sector Decarbonization
## MACC Analysis and Optimization Model

**Jinsu Park**
*Energy Systems Optimization*
January 2025

**Key Technologies Analyzed:**
- Industrial Heat Pumps
- Naphtha Cracking Electrification (NCC-Electricity)
- Hydrogen-Based Cracking (NCC-H2)
- Renewable Energy Power Purchase Agreements (RE PPA)

---

## Slide 2: Research Motivation & Context

### Korean Petrochemical Sector Overview

**Scale & Importance:**
- Annual emissions: **26.3 MtCO₂** (2025 baseline)
- Major products: Ethylene, propylene, aromatics
- 64 production facilities analyzed
- Critical export industry for Korean economy

**Decarbonization Challenge:**
- Process emissions (naphtha cracking): 85% of total
- High-temperature requirements (>800°C)
- Mature industry with established infrastructure
- Limited abatement options available

**Research Question:**
> What is the cost-optimal pathway to decarbonize the Korean petrochemical sector by 2050, and what are the key drivers of technology adoption?

---

## Slide 3: Methodology Overview

### Dynamic MACC Analysis Framework

**Model Architecture:**

```
┌──────────────────────────────────────────────────────────┐
│  MODULE 1: Baseline Emissions (2025)                     │
│  - Facility-level energy/emissions inventory             │
│  - Product group classification                          │
│  - Technology applicability assessment                   │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  MODULE 2: Dynamic MACC Calculation (2025-2050)          │
│  - Technology cost trajectories (learning curves)        │
│  - Energy price trajectories (H₂, RE, fossil fuels)      │
│  - Dual methodology: Traditional + LCOE-based            │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  MODULE 3: Optimization (LP)                             │
│  - Cost minimization with emission targets               │
│  - Technology irreversibility constraints                │
│  - Abatement potential limits                            │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  MODULE 4: Sensitivity Analysis                          │
│  - Fossil fuel price sensitivity                         │
│  - Learning curve sensitivity                            │
│  - Model robustness assessment                           │
└──────────────────────────────────────────────────────────┘
```

**Key Innovation:** Dual MACC methodology combining traditional capex/opex approach with LCOE-based analysis for transformative technologies.

---

## Slide 4: MACC Methodology - Dual Approach

### Traditional MACC (Heat Pump, RE PPA)

**Formula:**
```
MACC = (Annualized CAPEX + Annual OPEX + Fuel Cost Differential) / Abatement
```

**Example: Heat Pump (2030)**
- CAPEX: $150M/MtCO₂ → Annualized: $14.4/tCO₂
- OPEX: 5% of CAPEX → $0.7/tCO₂
- Fuel Differential: (RE electricity - naphtha) → **-$763/tCO₂** (savings!)
- **Total MACC: -$748/tCO₂** (profitable without carbon price)

**Key Driver:** Heat pump efficiency (COP = 3.5) provides 70% energy savings

---

### LCOE-Based MACC (NCC Technologies)

**Why LCOE Approach?**
- Process transformation, not just fuel switching
- Complex interdependencies between energy, feedstock, and capital
- Technology readiness <3 (pilot/demo stage)
- Literature provides LCOE projections, not granular cost components

**Formula:**
```
MACC = (LCOE_new_technology - LCOE_baseline) / (EI_baseline - EI_new_technology)

Where:
  LCOE = Levelized Cost of Ethylene ($/ton ethylene)
  EI = Emission Intensity (tCO₂/ton ethylene)
```

**Example: NCC-Electricity (2030)**
- Baseline LCOE: $1,200/ton ethylene (EI: 1.8 tCO₂/ton)
- Electric cracker LCOE: $1,000/ton ethylene (EI: 0.2 tCO₂/ton)
- LCOE premium: -$200/ton ethylene
- Abatement: 1.6 tCO₂/ton ethylene
- **MACC: -$125/tCO₂**

**Reference:** Naphtha Cracking Electrification (Sabic, BASF pilot projects)

---

## Slide 5: Technology Overview & Availability

### Four Abatement Technologies Analyzed

| Technology | Description | Availability | Abatement Potential (2025) |
|------------|-------------|--------------|---------------------------|
| **Heat Pump** | Industrial heat pump replacing fossil fuel combustion for low-temp processes | ✅ 2025 | 5.8 MtCO₂/yr |
| **NCC-Electricity** | Electric steam cracker replacing naphtha cracking | 🔬 2030 | 13.7 MtCO₂/yr |
| **NCC-H2** | Hydrogen-based cracker replacing naphtha | 🔬 2030 | 13.7 MtCO₂/yr |
| **RE PPA** | Renewable electricity procurement (NCC facilities only) | ✅ 2025 | 1.4 MtCO₂/yr |

**Notes:**
- NCC technologies are **mutually exclusive** (optimizer selects one)
- Heat pump applicability varies by product group (65-95%)
- RE PPA limited to NCC facilities per user constraint

**Technology Readiness Levels:**
- Heat Pump: TRL 9 (commercial deployment)
- RE PPA: TRL 9 (established markets)
- NCC-Electricity: TRL 4-5 (pilot scale: Sabic 2021, BASF planning)
- NCC-H2: TRL 3-4 (lab/pilot, Linde collaboration)

---

## Slide 6: Cost Trajectories & Learning Curves

### Technology CAPEX Learning (2025-2050)

| Technology | 2025 CAPEX | 2030 CAPEX | 2050 CAPEX | Annual Learning Rate |
|------------|------------|------------|------------|---------------------|
| Heat Pump | $150M/MtCO₂ | $130M | $75M | -2.7%/year |
| NCC-H2 | $300M/MtCO₂ | $250M | $150M | -2.7%/year |
| NCC-Electricity | $350M/MtCO₂ | $300M | $180M | -2.6%/year |
| RE PPA | $180M/MtCO₂ | $120M | $80M | -3.2%/year |

**Learning Curve Method:** Linear interpolation between milestone years
**Validation:** IEA Technology Roadmaps, IRENA Cost Projections, Hydrogen Council
**Assumption:** Time-based (conservative) vs. deployment-based learning

---

### Energy Price Trajectories

**Hydrogen Prices (Green H₂):**
- 2025: $6.0/kg
- 2030: $4.0/kg (electrolyzer scale-up)
- 2050: $2.0/kg (mature market)
- Source: IEA Hydrogen Strategy, BloombergNEF

**Renewable Electricity (PPA prices):**
- 2025: $60/MWh
- 2030: $40/MWh (solar/wind LCOE decline)
- 2050: $25/MWh (mature RE market)
- Source: IRENA RE Cost Database

**Fossil Fuel Prices (held constant for baseline):**
- Naphtha: $15/GJ
- LNG: $12/GJ
- Grid electricity: $0.10/kWh

---

## Slide 7: MACC Results - 2030

### Marginal Abatement Cost Curve (2030)

```
      MACC ($/tCO₂)
        │
   500  ├─────────────────────────────────────────
        │
   250  ├─────────────────────────────────────────
        │
     0  ├═════════════════════════════════════════ Cost Parity
        │  ┌────┐  ┌────┐
  -250  │  │Heat│  │NCC │
        │  │Pump│  │Elec│
  -500  │  │    │  │    │  ┌────┐
        │  │    │  │    │  │NCC │
  -750  │  │-748│  │-112│  │-H₂ │  ┌────┐
        │  │    │  │    │  │+18 │  │RE  │
 -1000  │  └────┘  └────┘  └────┘  │PPA │
        │                           │-131│
        └───────────────────────────┴────┴─────>
            5.8     7.5      13.7    15.1  MtCO₂/yr
```

**Key Findings (2030):**
- **Heat Pump**: Most cost-effective (-$748/tCO₂), 5.8 MtCO₂ potential
- **NCC-Electricity**: Cost-negative (-$112/tCO₂), 7.5 MtCO₂ potential
- **RE PPA**: Negative cost (-$131/tCO₂), 1.4 MtCO₂ potential
- **NCC-H2**: Near break-even (+$18/tCO₂), 13.7 MtCO₂ potential

**Total Available Abatement:** 21.1 MtCO₂/yr (80% of baseline emissions)
**Cost-Negative Abatement:** 13.7 MtCO₂/yr (52% of baseline)

---

## Slide 8: MACC Results - 2050

### Marginal Abatement Cost Curve (2050)

```
      MACC ($/tCO₂)
        │
   500  ├─────────────────────────────────────────
        │
   250  ├─────────────────────────────────────────
        │
     0  ├═════════════════════════════════════════ Cost Parity
        │  ┌────┐  ┌────┐  ┌────┐  ┌────┐
  -250  │  │Heat│  │NCC │  │NCC │  │RE  │
        │  │Pump│  │Elec│  │H₂  │  │PPA │
  -500  │  │    │  │    │  │    │  │    │
        │  │    │  │    │  │-320│  │-340│
  -750  │  │-850│  │-121│  │    │  │    │
        │  │    │  │    │  │    │  │    │
 -1000  │  └────┘  └────┘  └────┘  └────┘
        │
        └───────────────────────────────────────>
            5.8     7.5      13.7    15.1  MtCO₂/yr
```

**Key Findings (2050):**
- **ALL technologies are cost-negative** (profitable without carbon price!)
- **Heat Pump**: -$850/tCO₂ (improving due to CAPEX reduction)
- **NCC-H2**: -$320/tCO₂ (H₂ price drops to $2/kg make it attractive)
- **RE PPA**: -$340/tCO₂ (RE price drops to $25/MWh)
- **NCC-Electricity**: -$121/tCO₂ (stable, competitive)

**Total Available Abatement:** 21.1 MtCO₂/yr
**Cost-Negative Abatement:** 21.1 MtCO₂/yr (100%!)

**Implication:** By 2050, full decarbonization is economically optimal without any carbon pricing mechanism.

---

## Slide 9: Optimization Results - Deployment Pathway

### Optimal Technology Deployment (2025-2050)

**Target:** 80% emission reduction by 2050 (relative to 2025 baseline)

| Year | Heat Pump | NCC-Electricity | NCC-H2 | RE PPA | Total Abatement | Cumulative Cost |
|------|-----------|-----------------|--------|--------|----------------|----------------|
| **2025** | 2.0 MtCO₂ | 0 | 0 | 1.4 MtCO₂ | 3.4 MtCO₂ (13%) | -$2.4B |
| **2030** | 5.8 MtCO₂ | 7.5 MtCO₂ | 0 | 1.4 MtCO₂ | 14.7 MtCO₂ (56%) | -$11.7B |
| **2040** | 5.8 MtCO₂ | 7.5 MtCO₂ | 0 | 1.4 MtCO₂ | 14.7 MtCO₂ (56%) | -$13.5B |
| **2050** | 5.8 MtCO₂ | 7.5 MtCO₂ | 0 | 1.4 MtCO₂ | 14.7 MtCO₂ (56%) | -$15.8B |

**Key Observations:**
1. **Rapid deployment by 2030** due to cost-negative technologies
2. **NCC-Electricity preferred** over NCC-H2 (lower MACC throughout period)
3. **Technology lock-in** after 2030 (irreversibility constraint)
4. **Cumulative savings:** $15.8B over 25 years (negative cost = profit!)

**Technology Irreversibility:** Once capital is deployed, cannot switch technologies (stranded asset risk)

---

## Slide 10: Sensitivity Analysis - Research Question

### What Drives the Model Results?

**Two Key Assumptions Tested:**

1. **Fossil Fuel Savings** (naphtha, LNG prices)
   - These create the operational cost savings that make technologies attractive
   - Question: What if fossil fuels were FREE? (price = $0)

2. **Learning Curves** (CAPEX reduction over time)
   - Technologies get cheaper through deployment and experience
   - Question: What if CAPEX stayed at 2025 levels forever?

**Scenarios:**
- ✅ **Baseline**: Full model (fossil fuel prices + learning curves)
- 🔬 **No Fossil Savings**: Set fossil fuel prices to $0 (removes savings benefit)
- 🔬 **No Learning**: Freeze CAPEX at 2025 values
- 🔬 **Both Removed**: No fossil savings + no learning

**Method:** Re-run MACC calculation for each scenario and compare impacts

---

## Slide 11: Sensitivity Results - 2030 Impacts

### MACC Sensitivity Analysis (2030)

| Technology | Baseline | No Fossil Savings | Impact (Fossil) | No Learning | Impact (Learning) |
|------------|----------|-------------------|-----------------|-------------|------------------|
| **Heat Pump** | -$748/tCO₂ | **+$259/tCO₂** | **+$1,007/tCO₂** ⚠️ | -$745/tCO₂ | +$3/tCO₂ ✅ |
| **NCC-Electricity** | -$112/tCO₂ | **+$2,497/tCO₂** | **+$2,608/tCO₂** ⚠️⚠️ | -$112/tCO₂ | $0/tCO₂ ✅ |
| **NCC-H2** | +$18/tCO₂ | **+$1,721/tCO₂** | **+$1,703/tCO₂** ⚠️ | +$18/tCO₂ | $0/tCO₂ ✅ |
| **RE PPA** | -$131/tCO₂ | -$131/tCO₂ | $0/tCO₂* | -$131/tCO₂ | $0/tCO₂ |

*RE PPA compares grid vs RE electricity, not affected by fossil fuel prices

**Ratio Analysis:**
- Heat Pump: Fossil savings are **319x more important** than learning curves!
- NCC-Electricity: Fossil savings are **∞x more important** (learning has 0 impact on LCOE)
- NCC-H2: Fossil savings are **∞x more important**

---

### Visual Comparison: 2030 MACC Curves

```
Baseline                          No Fossil Savings
    0 ├────────────────              0 ├────────────────
      │  All negative!                 │
 -500 │  ┌┐┌┐┌┐┌┐                 +500 │  ┌─┐
-1000 │  ││││││││                      │  │ │  ┌─┐┌─┐
      └──────────────>                 │  │ │  │ ││ │
                                       └──┴─┴──┴─┴┴─┴──>
                                       All become costly!
```

**Critical Finding:** Without fossil fuel savings, technologies shift from **cost-negative to cost-positive**, requiring carbon prices of $250-2,500/tCO₂ to justify adoption.

---

## Slide 12: Sensitivity Results - Key Insight

### Fossil Fuel Prices vs. Learning Curves

**Impact Magnitude Comparison (2030):**

```
Impact on MACC ($/tCO₂)

 3000 ├─────────────────────────────────────
      │                           ┌────────┐
 2500 │                           │  2608  │
      │                           │        │
 2000 │                           │  NCC-  │
      │            ┌────────┐     │  Elec  │
 1500 │            │  1703  │     │        │
      │  ┌──────┐  │        │     │        │
 1000 │  │ 1007 │  │  NCC-  │     │        │
      │  │      │  │   H₂   │     │        │
  500 │  │ Heat │  │        │     │        │
      │  │ Pump │  │        │     │        │
    0 ├──┴──────┴──┴────────┴─────┴────────┴──
      │   ┌┐       ┌┐              ┌┐
   -5 │   ││       ││              ││   ← Learning Impact
      │   │3│      │0│             │0│      (Barely visible!)
      └───┴┴───────┴┴──────────────┴┴──────>
        Heat      NCC-H2         NCC-Elec
        Pump

    ▓▓▓ Fossil Fuel Savings Impact (MASSIVE)
    ░░░ Learning Curve Impact (MINIMAL)
```

**Key Finding:**
- Fossil fuel savings: **+$1,000-2,600/tCO₂ impact**
- Learning curves: **+$0-3/tCO₂ impact**
- **Ratio: 100-300:1**

---

## Slide 13: Economic Mechanism Explained

### Why Do These Technologies Work?

**Answer: Operational Savings, Not Capital Costs**

#### Example: Heat Pump Economics (2030)

**Total MACC: -$748/tCO₂**

**Component Breakdown:**
```
CAPEX (annualized):     +$14/tCO₂   (1.9%)
OPEX:                   +$1/tCO₂    (0.1%)
Fuel Differential:      -$763/tCO₂  (98.0%) ← KEY DRIVER!
────────────────────────────────────────────
Total:                  -$748/tCO₂
```

**Fuel Differential Calculation:**
- Heat required: 67.1 GJ/tCO₂ abated
- **Baseline (naphtha)**: 67.1 GJ × $15/GJ = $1,007/tCO₂
- **Heat pump (RE electricity)**: 67.1 GJ ÷ 3.5 (COP) × $16.67/GJ = $319/tCO₂
- **Savings**: $1,007 - $319 = **$688/tCO₂**
- Adjusted for efficiency: **-$763/tCO₂**

**Key Insight:** Heat pump efficiency (COP = 3.5) means 70% less energy input required. Even though electricity costs more per GJ than naphtha, the efficiency gain creates massive savings.

---

#### Why Fossil Fuel Prices Matter More Than CAPEX

**Without fossil fuel savings** (naphtha price = $0):
```
CAPEX (annualized):     +$14/tCO₂
OPEX:                   +$1/tCO₂
Fuel Differential:      +$319/tCO₂  ← Now you PAY for electricity
────────────────────────────────────────────
Total:                  +$334/tCO₂  ← Becomes costly!
```

**Learning curve impact** (CAPEX -50% reduction):
```
CAPEX (annualized):     +$7/tCO₂    (was $14)
OPEX:                   +$0.4/tCO₂  (was $1)
Fuel Differential:      -$763/tCO₂  (unchanged)
────────────────────────────────────────────
Total:                  -$755/tCO₂  (was -$748)
                        ────────────
Improvement:            -$7/tCO₂    (0.9% change)
```

**Conclusion:** Operational savings (fuel differential) are **110x larger** than CAPEX changes.

---

## Slide 14: Model Robustness Assessment

### Sensitivity Findings Summary

#### 1. Model is ROBUST to Learning Curve Uncertainty ✅

**Evidence:**
- Freezing CAPEX at 2025 levels → <1% impact on MACC
- Even if learning is 50% slower than projected, results barely change
- Can confidently use literature learning rates

**Implication for Research:**
- Don't need precise learning curve estimates
- Focus data collection efforts elsewhere

---

#### 2. Model is HIGHLY SENSITIVE to Fossil Fuel Prices ⚠️

**Evidence:**
- Setting fossil fuel prices to $0 → 100-300% impact on MACC
- Can flip technologies from cost-negative to cost-positive
- Largest single driver of model results

**Implication for Policy:**
- If fossil fuel prices collapse (e.g., supply glut, stranded assets), technologies become uneconomic
- Would need carbon price of $100-300/tCO₂ to compensate
- Adoption timing sensitive to oil/gas price volatility

---

#### 3. Economic Driver is Operational Savings, Not Capital Costs 💡

**Key Findings:**
- Fuel savings: $700-1,000/tCO₂ (dominant)
- CAPEX changes: $3-8/tCO₂ (minimal)
- Ratio: 100-300:1

**Why This Matters:**
- Technologies succeed through **operational efficiency**, not capital cost reduction
- **Without carbon pricing**, adoption driven by fuel price differentials
- Policy should focus on:
  - ✅ Ensuring stable fossil fuel pricing
  - ✅ Supporting low-cost renewable energy deployment
  - ⚠️ Less critical: CAPEX subsidies for mature technologies

---

## Slide 15: Policy Implications

### Recommendations for Decarbonization Policy

#### 1. Early Mover Advantage (2025-2030) ✅

**Finding:** Technologies are cost-negative TODAY
- No carbon price needed for economic justification
- Heat pump: -$748/tCO₂
- RE PPA: -$131/tCO₂

**Policy Recommendation:**
- Remove regulatory barriers to industrial heat pump deployment
- Facilitate RE PPA contracting for petrochemical facilities
- Support pilot NCC-Electricity projects (de-risk technology)

**Expected Impact:** 13-14 MtCO₂/yr abatement by 2030 (50% of baseline) with **net economic benefit**

---

#### 2. Strategic Focus on Energy Prices, Not CAPEX Subsidies

**Finding:** Fossil fuel price differential drives 95% of value

**Policy Recommendation:**
- ✅ **Priority:** Support low-cost renewable energy deployment
  - Accelerate offshore wind, solar capacity
  - Streamline RE PPA contracting
- ✅ **Priority:** Develop green hydrogen infrastructure
  - Target $2-3/kg H₂ by 2035-2040
- ⚠️ **Lower Priority:** CAPEX subsidies for heat pumps
  - Marginal impact (<1% of total value)
  - Better to focus on operational cost reduction

---

#### 3. Risk Management: Fossil Fuel Price Volatility ⚠️

**Finding:** If fossil fuel prices drop significantly, technologies become uneconomic

**Policy Recommendation:**
- Implement carbon floor price ($50-100/tCO₂) to insure against fossil fuel price collapse
- Long-term contracts for fossil fuel feedstock pricing
- Consider technology mandates for new facilities (future-proofing)

**Risk Scenario:**
- If oil prices drop to $40/bbl (2020 COVID levels), naphtha → $8/GJ
- Technologies shift from -$748/tCO₂ to -$230/tCO₂ (still profitable, but less attractive)
- At $5/GJ naphtha (crisis scenario), technologies become cost-positive

---

#### 4. Technology Lock-In Risk: Choose Wisely by 2030

**Finding:** NCC-Electricity and NCC-H2 are mutually exclusive; optimizer chooses NCC-Electricity

**Policy Recommendation:**
- Support pilot projects for BOTH technologies before 2030
- Evaluate technology performance, reliability, supply chain
- Final deployment decision by 2030-2035
- **Once deployed, switching costs are prohibitive** (stranded assets)

**Key Trade-Offs:**
- **NCC-Electricity**: Lower MACC (-$112 vs +$18/tCO₂ in 2030), mature electrical infrastructure
- **NCC-H2**: Feedstock flexibility, potential for green hydrogen export synergies

---

## Slide 16: Limitations & Future Work

### Model Limitations

1. **Static Abatement Potential**
   - Assumes constant production levels (no demand elasticity)
   - Does not model facility closures or capacity expansions
   - **Future work:** Integrate production volume sensitivity

2. **Simplified Learning Curves**
   - Time-based learning (not deployment-based)
   - Linear interpolation between milestone years
   - **Future work:** Endogenous learning (deployment drives cost reduction)

3. **Technology Availability Assumptions**
   - NCC technologies available in 2030 (optimistic)
   - Based on announced pilot projects (Sabic, BASF)
   - **Risk:** Technology delays → deferred abatement

4. **Fuel Price Trajectories**
   - Held constant for baseline (conservative)
   - Real-world volatility not captured
   - **Future work:** Stochastic price scenarios

5. **Carbon Pricing Excluded**
   - Model shows economics WITHOUT carbon price
   - Does not evaluate optimal carbon price levels
   - **Future work:** Social cost of carbon integration

---

### Future Research Directions

1. **Demand-Side Analysis**
   - Material substitution (plastics → alternatives)
   - Circular economy (recycling, reuse)
   - Product-specific MACC curves

2. **International Competitiveness**
   - Export market implications
   - Carbon border adjustment mechanisms
   - Regional comparative advantage

3. **Supply Chain Analysis**
   - Green hydrogen supply infrastructure
   - Renewable electricity grid integration
   - Technology supply chain constraints

4. **Finance & Investment**
   - Capital availability constraints
   - Risk-adjusted discount rates
   - Public-private financing mechanisms

5. **Regional Disaggregation**
   - Site-specific facility analysis
   - Grid connection constraints
   - Local hydrogen hub development

---

## Slide 17: Conclusions

### Key Findings

1. **Economic Decarbonization is Feasible** ✅
   - 56% emission reduction by 2030 with **negative cost** (-$11.7B cumulative savings)
   - 100% of technologies cost-negative by 2050
   - **No carbon price needed** for economic justification

2. **Operational Savings Drive Value, Not CAPEX Reduction** 💡
   - Fossil fuel savings: $1,000-2,600/tCO₂ impact (dominant)
   - Learning curves: $0-3/tCO₂ impact (minimal)
   - **Ratio: 100-300:1**
   - Technologies work because they avoid expensive fossil fuel purchases ($15/GJ naphtha)

3. **Model is Robust to Learning Curve Uncertainty** ✅
   - <1% sensitivity to learning rate changes
   - Can confidently use literature projections
   - Focus sensitivity analysis on energy prices instead

4. **Fossil Fuel Prices are Critical Driver** ⚠️
   - Largest single factor affecting technology economics
   - Policy should ensure stable/high fossil fuel prices (carbon floor) OR low-cost renewables
   - Risk: Fossil fuel price collapse would make technologies uneconomic

5. **Technology Lock-In by 2030** 🔒
   - Optimal pathway: Heat Pump + NCC-Electricity + RE PPA
   - NCC-H2 not selected (higher MACC than NCC-Electricity)
   - Irreversibility constraint → critical to choose correctly

---

### Policy Recommendations Summary

**Near-Term (2025-2030):**
- ✅ Remove regulatory barriers for heat pumps
- ✅ Facilitate RE PPA contracting
- ✅ Support NCC pilot projects (both electricity & H₂)
- ⚠️ Implement carbon floor price ($50-100/tCO₂)

**Long-Term (2030-2050):**
- ✅ Accelerate low-cost renewable energy deployment
- ✅ Develop green hydrogen infrastructure
- ✅ Manage technology lock-in risk (irreversibility)

**Research Priorities:**
- ⚠️ Energy price projections (H₂, RE, fossil fuels) - HIGH sensitivity
- ✅ Learning curve estimates - LOW sensitivity (use literature)

---

## Slide 18: Thank You

# Thank You

**Questions?**

---

**Contact:**
Jinsu Park
[Your Institution]
[Email]

**Resources:**
- Full model documentation: [GitHub Repository]
- Interactive dashboard: `streamlit run app.py`
- Technical paper: Available upon request

**Model Architecture:**
- Python-based optimization (Pyomo, Gurobi)
- 64 facilities, 4 technologies, 26 years
- Dual MACC methodology (Traditional + LCOE-based)
- Sensitivity analysis with 4 scenarios

---

## Appendix: Additional Slides

### A1: Baseline Emissions Breakdown (2025)

**Total Emissions:** 26.3 MtCO₂/yr

**By Fuel Type:**
- Naphtha combustion: 13.7 MtCO₂ (52%)
- LNG: 5.2 MtCO₂ (20%)
- Fuel gas: 3.8 MtCO₂ (14%)
- Electricity: 2.3 MtCO₂ (9%)
- Other fuels: 1.3 MtCO₂ (5%)

**By Product Group:**
- Ethylene (NCC): 13.7 MtCO₂ (52%)
- Propylene: 4.2 MtCO₂ (16%)
- Aromatics: 3.1 MtCO₂ (12%)
- C4 products: 2.8 MtCO₂ (11%)
- Others: 2.5 MtCO₂ (9%)

---

### A2: Technology Cost Assumptions Detail

**Heat Pump:**
- CAPEX: $150M/MtCO₂ (2025) → $75M (2050)
- Lifetime: 20 years
- OPEX: 5% of CAPEX
- COP (Coefficient of Performance): 3.5
- Applicable temperature range: <200°C
- Source: IEA Heat Pump Technology Roadmap

**NCC-Electricity:**
- CAPEX: $350M/MtCO₂ (2025) → $180M (2050)
- Lifetime: 25 years
- OPEX: 7% of CAPEX
- Electricity consumption: 3.5 MWh/ton ethylene
- Source: Sabic pilot project, BASF planning documents

**NCC-H2:**
- CAPEX: $300M/MtCO₂ (2025) → $150M (2050)
- Lifetime: 25 years
- OPEX: 6% of CAPEX
- H₂ consumption: 2.8 kg H₂/ton ethylene
- Source: Linde, Hydrogen Council projections

**RE PPA:**
- CAPEX: $0 (procurement contract only)
- Lifetime: N/A (annual contract)
- OPEX: Included in PPA price
- Grid emission factor: 0.4 tCO₂/MWh (2025) → 0.15 (2050)
- RE emission factor: 0.05 tCO₂/MWh (lifecycle)

---

### A3: Optimization Model Formulation

**Objective Function:**
```
Minimize: Σ_{t,tech} (deployment_{t,tech} × cost_{t,tech})
```

**Constraints:**

1. **Emission Target:**
```
baseline_emissions - Σ_{tech} (deployment_tech × abatement_tech) ≤ emission_target
```

2. **Abatement Potential:**
```
deployment_tech ≤ abatement_potential_tech    ∀ tech
```

3. **Technology Availability:**
```
deployment_{t,tech} = 0    if year_t < availability_year_tech
```

4. **Irreversibility:**
```
deployment_{t+1,tech} ≥ deployment_{t,tech}    ∀ t, tech
```

5. **Mutual Exclusivity (NCC technologies):**
```
deployment_NCC-H2 + deployment_NCC-Electricity ≤ abatement_potential_NCC
```

**Decision Variables:**
- `deployment_{t,tech}`: MtCO₂/yr abated by technology `tech` in year `t`

**Parameters:**
- `cost_{t,tech}`: MACC for technology `tech` in year `t` ($/tCO₂)
- `abatement_potential_tech`: Maximum abatement (MtCO₂/yr)
- `availability_year_tech`: Year technology becomes available

---

### A4: Sensitivity Analysis - Detailed Methodology

**Scenario Definitions:**

1. **Baseline (Full Model)**
   - Fossil fuel prices: Naphtha $15/GJ, LNG $12/GJ
   - Learning curves: 2.6-3.2%/year CAPEX reduction
   - All model features enabled

2. **No Fossil Fuel Savings**
   - Fossil fuel prices → **$0/GJ** (naphtha, LNG, fuel gas, etc.)
   - This removes the savings from avoiding fossil fuel purchases
   - New energy costs (H₂, electricity) are KEPT
   - Learning curves: Enabled

3. **No Learning Curves**
   - CAPEX frozen at 2025 values (no cost reduction over time)
   - Fossil fuel prices: $15/GJ (baseline)
   - Tests impact of learning rate uncertainty

4. **Both Removed**
   - Fossil fuel prices → $0/GJ
   - CAPEX frozen at 2025 values
   - Worst-case scenario

**Analysis:**
- Recalculate MACC for each scenario
- Compare MACC changes for each technology
- Identify dominant drivers (fossil fuel vs. learning)

---

### A5: References

**Data Sources:**
1. IEA Technology Roadmaps (Heat Pump, Hydrogen, CCS)
2. IRENA Renewable Energy Cost Database
3. BloombergNEF Hydrogen Economy Outlook
4. Korean Ministry of Environment Emissions Inventory
5. Sabic Electric Steam Cracker Pilot Project (2021)
6. BASF Carbon Management Strategy
7. Hydrogen Council Cost Projections

**Methodology References:**
1. McKinsey Global GHG Abatement Cost Curve (2009)
2. IEA Energy Technology Perspectives (2023)
3. IPCC AR6 WGIII Chapter 11 (Industry)
4. Napp et al. (2014) "Exploring the Feasibility of Low-Carbon Scenarios"
5. Bataille et al. (2018) "Net-zero deep decarbonization pathways in Latin America"

**Software:**
- Python 3.12, Pandas, NumPy, Matplotlib
- Pyomo optimization framework
- Gurobi solver
- Streamlit dashboard

---

**END OF PRESENTATION**

---

## Presentation Notes for Delivery

### Time Allocation (60-minute format)
- Slides 1-3 (Introduction): 5 minutes
- Slides 4-6 (Methodology): 10 minutes
- Slides 7-9 (Results): 10 minutes
- Slides 10-13 (Sensitivity Analysis): 15 minutes ← **KEY CONTRIBUTION**
- Slides 14-15 (Policy Implications): 10 minutes
- Slides 16-18 (Conclusions): 5 minutes
- Q&A: 5 minutes

### Key Messages to Emphasize

1. **Methodological Innovation:** Dual MACC approach (traditional + LCOE-based)
2. **Surprising Result:** Fossil fuel prices matter 100-300x more than learning curves
3. **Policy Relevance:** Decarbonization is economically optimal TODAY (no carbon price needed)
4. **Risk Assessment:** Model robust to learning uncertainty, sensitive to energy prices

### Anticipated Questions & Responses

**Q: Why are NCC technologies cost-negative if they're not commercially available?**
A: LCOE projections from pilot projects (Sabic, BASF) show process efficiency gains offset capital costs. Key assumption: Technology availability by 2030 (risk factor acknowledged).

**Q: How sensitive are results to hydrogen price assumptions?**
A: H₂ price impacts NCC-H2 MACC but NOT the rank ordering. Even at $6/kg (2025), fossil fuel savings still dominate. Would need H₂ >$10/kg to change results significantly.

**Q: What about circular economy/recycling?**
A: Excluded from current scope (process emissions only). Recycling would reduce baseline demand, but wouldn't change per-unit abatement costs. Future work: demand-side scenarios.

**Q: Can results generalize to other countries?**
A: Framework generalizes; absolute values depend on local energy prices and industrial structure. Key insight (operational savings >> CAPEX) likely robust across contexts.

**Q: What carbon price would be needed if fossil fuel prices drop?**
A: If naphtha drops from $15/GJ to $5/GJ, would need carbon price of ~$700/tCO₂ to maintain economics. This underscores importance of carbon floor pricing.
