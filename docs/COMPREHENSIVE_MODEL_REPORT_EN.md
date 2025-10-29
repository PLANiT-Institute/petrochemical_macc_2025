# COMPREHENSIVE MODEL REPORT
## Korean Petrochemical Industry MACC Analysis (2025-2050)

**Report Date:** October 28, 2025
**Model Version:** Energy-Based MACC v2.0
**Geographic Scope:** South Korea (248 petrochemical facilities)
**Temporal Scope:** 2025-2050 (26 years)
**Analysis Type:** Marginal Abatement Cost Curve (MACC) with Technology Deployment Optimization

---

## EXECUTIVE SUMMARY

This comprehensive report documents the complete assumptions, methodologies, and outputs of a Marginal Abatement Cost Curve (MACC) analysis for South Korea's petrochemical industry. The model evaluates four decarbonization technologies across 248 facilities to identify cost-effective pathways for achieving emission reduction targets aligned with Korea's Net-Zero goals.

### Key Findings at a Glance

| Metric | Value | Notes |
|--------|-------|-------|
| **Baseline Emissions (2025)** | 52.01 MtCO2/year | All 248 facilities |
| **BAU Emissions (2050)** | 62.19 MtCO2/year | +19.6% due to capacity growth |
| **Maximum Abatement Potential (2050)** | 56.99 MtCO2/year | 90% reduction achievable |
| **Cumulative Investment Required** | $47.9 Billion | Policy Target scenario (2025-2050) |
| **Hydrogen Demand (2050)** | 12.88 Million tons/year | For NCC-H2 technology |
| **Additional RE Electricity (2050)** | 129.8 TWh/year | ~20-25% of current Korean generation |

---

# PART I: MODEL ASSUMPTIONS

## 1. GENERAL PARAMETERS

### 1.1 Analysis Period and Scope

| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| **Base Year** | 2025 | year | Starting point for all projections |
| **End Year** | 2050 | year | Final year of analysis horizon |
| **Analysis Duration** | 26 | years | Total modeling period |
| **Number of Facilities** | 248 | facilities | Complete Korean petrochemical sector coverage |
| **Total Baseline Capacity** | 100,066 | kt/year | Sum of all production capacities |
| **Total Baseline Emissions** | 52.01 | MtCO2/year | 2025 reference emissions |

### 1.2 Methodological Approach

**MACC Calculation Method:**

The model uses an **energy-based methodology** where:

```
MACC (USD/tCO2) = CAPEX_annual + OPEX_annual + Fuel_Cost_Differential
                   ________________________________________________
                                    Abatement_Potential

Where:
• CAPEX_annual = Total CAPEX / Equipment Lifetime (simple annualization)
• OPEX_annual = Total CAPEX × (OPEX % of CAPEX)
• Fuel_Cost_Differential = (New Energy Cost - Old Energy Cost) / Emission Reduction
```

**Critical Principle:** Naphtha feedstock cost remains constant across scenarios and is NOT included in fuel cost differentials. Only combustion fuel costs change.

---

## 2. EMISSION FACTORS

### 2.1 Fossil Fuel Emission Factors

| Fuel Type | Emission Factor | Unit | Source/Notes |
|-----------|----------------|------|--------------|
| **Naphtha (Combustion)** | 0.0542 | tCO2/GJ | Back-calculated to maintain 52 MtCO2 baseline |
| **LNG (Liquefied Natural Gas)** | 0.0149 | tCO2/GJ | Standard IPCC emission factor |
| **Fuel Gas** | 0.0149 | tCO2/GJ | Refinery off-gas, assumed natural gas equivalent |
| **Byproduct Gas** | 0.0149 | tCO2/GJ | Process off-gas, assumed natural gas equivalent |
| **LPG (Liquefied Petroleum Gas)** | 0.0149 | tCO2/GJ | Standard emission factor |
| **Fuel Oil** | 0.0149 | tCO2/GJ | Heavy fuel oil |
| **Diesel** | 0.0149 | tCO2/GJ | Distillate fuel |

**Note on Naphtha EF:** The value 0.0542 tCO2/GJ is higher than typical values (0.0149-0.02 tCO2/GJ) because it was back-calculated to ensure the model reproduces the observed 52 MtCO2 baseline when combined with reported energy consumption data.

### 2.2 Grid Electricity Emission Factors

| Parameter | 2025 Value | 2050 Value | Decline Rate | Source |
|-----------|-----------|-----------|--------------|--------|
| **Grid Emission Factor** | 0.450 tCO2/MWh | 0.250 tCO2/MWh | -0.008/year | Korean 10th Basic Plan for Electricity |
| **RE Lifecycle Emissions** | 0.050 tCO2/MWh | 0.050 tCO2/MWh | Constant | Renewable energy lifecycle analysis |

**Grid Decarbonization Trajectory:**
- Linear decline from 0.45 tCO2/MWh (2025) to 0.25 tCO2/MWh (2050)
- Reflects coal phase-out and renewable energy expansion
- Continues to 0.09 tCO2/MWh by 2070 (net-zero trajectory)

### 2.3 Low-Carbon Fuel Emission Factors

| Fuel Type | Emission Factor | Unit | Notes |
|-----------|----------------|------|-------|
| **Green Hydrogen** | 0.000 | tCO2/kg | Produced from renewable electricity via electrolysis |
| **Renewable Electricity** | 0.050 | tCO2/MWh | Lifecycle emissions (manufacturing, installation, O&M) |

---

## 3. BASELINE PROCESS EMISSIONS (2025)

### 3.1 Ethylene Production (Naphtha Cracker)

**Total Emission Intensity:** 1.739 tCO2/ton ethylene

**Detailed Energy Consumption Breakdown:**

| Energy Source | Consumption | Unit | Emission Factor | Emissions | Notes |
|--------------|-------------|------|----------------|-----------|-------|
| **Naphtha (Fuel)** | 29.00 | GJ/ton | 0.0542 tCO2/GJ | 1.572 tCO2/ton | Process heating only |
| **LNG** | 4.49 | GJ/ton | 0.0149 tCO2/GJ | 0.067 tCO2/ton | Supplementary fuel |
| **Fuel Gas** | 5.62 | GJ/ton | 0.0149 tCO2/GJ | 0.084 tCO2/ton | Recycled off-gas |
| **Byproduct Gas** | 1.12 | GJ/ton | 0.0149 tCO2/GJ | 0.017 tCO2/ton | Internal utilization |
| **TOTAL COMBUSTION** | 40.23 | GJ/ton | - | **1.739 tCO2/ton** | All thermal sources |

**Important Notes:**
- **Naphtha Feedstock (105 GJ/ton)** is NOT included in fuel combustion - it becomes product
- All combustion fuels are ELIMINATED in NCC-H2 and NCC-Electricity scenarios
- Electricity consumption (~800-1,200 kWh/ton) adds ~0.36-0.54 tCO2/ton from grid

**Literature Source:** Typical Korean steam cracker operations, aligned with RSC Green Chemistry 2025 studies

### 3.2 Propylene Production (Naphtha Cracker)

**Total Emission Intensity:** 1.530 tCO2/ton propylene

**Energy Consumption Breakdown:**

| Energy Source | Consumption | Unit | Emissions |
|--------------|-------------|------|-----------|
| **Naphtha (Fuel)** | 25.39 | GJ/ton | 1.376 tCO2/ton |
| **LNG** | 3.93 | GJ/ton | 0.059 tCO2/ton |
| **Fuel Gas** | 5.16 | GJ/ton | 0.077 tCO2/ton |
| **Byproduct Gas** | 1.23 | GJ/ton | 0.018 tCO2/ton |
| **TOTAL COMBUSTION** | 35.71 | GJ/ton | **1.530 tCO2/ton** |

### 3.3 Butadiene Production (Naphtha Cracker)

**Total Emission Intensity:** 1.730 tCO2/ton butadiene

**Energy Consumption Breakdown:**

| Energy Source | Consumption | Unit | Emissions |
|--------------|-------------|------|-----------|
| **Naphtha (Fuel)** | 29.00 | GJ/ton | 1.572 tCO2/ton |
| **LNG** | 4.17 | GJ/ton | 0.062 tCO2/ton |
| **Fuel Gas** | 5.32 | GJ/ton | 0.079 tCO2/ton |
| **Byproduct Gas** | 1.16 | GJ/ton | 0.017 tCO2/ton |
| **TOTAL COMBUSTION** | 39.65 | GJ/ton | **1.730 tCO2/ton** |

---

## 4. DECARBONIZATION TECHNOLOGIES

### 4.1 HEAT PUMP (Industrial High-Temperature)

**Applicability:** All processes with temperature requirements below 165°C
- Primarily: BTX (Benzene, Toluene, Xylene) production
- Utility systems (steam generation, process heating)
- **NOT applicable to:** Naphtha crackers (require >800°C temperatures)

#### Cost Parameters (Annual CAPEX using simple annualization)

| Year | CAPEX (USD/tCO2) | OPEX (USD/tCO2) | Total Fixed Cost | Technology Status |
|------|----------------|----------------|------------------|-------------------|
| **2025** | 900 / 20 = 45.0 | 27.0 (3% of 900) | 72.0 | Available ✓ |
| **2030** | 720 / 20 = 36.0 | 21.6 (3% of 720) | 57.6 | Available ✓ |
| **2040** | 540 / 20 = 27.0 | 16.2 (3% of 540) | 43.2 | Available ✓ |
| **2050** | 450 / 20 = 22.5 | 13.5 (3% of 450) | 36.0 | Available ✓ |

**Note:** CAPEX values are total investment costs annualized by simple division (no discount rate). Lifetime = 20 years.

#### Technical Specifications

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **Coefficient of Performance (COP)** | 4.0 | ratio | Heat output / Electricity input |
| **Maximum Temperature** | 140-165 | °C | Industrial heat pump limit |
| **Energy Efficiency** | 95% | % | Overall system efficiency |
| **Technology Readiness Level** | 9 | TRL (1-9) | Commercially available |
| **Equipment Lifetime** | 20 | years | Operational lifetime |
| **Availability Year** | 2025 | year | Ready for deployment |

#### Energy Conversion Formula

```
Electricity Required (MWh) = Fossil Fuel Replaced (GJ) / COP / 3.6

Example:
• Replace 1,000 GJ fossil fuel heat
• Electricity needed = 1,000 / 4.0 / 3.6 = 69.4 MWh
• Energy savings = 75% (due to COP = 4.0)
```

#### Abatement Potential (2050)

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Abatement** | 1.04 MtCO2/year | With demand growth |
| **Share of Total** | 1.8% | Limited applicability (temperature constraint) |
| **Applicability Rate** | Variable by product | BTX: 60-80%, Olefins: 0% |

**Literature Source:** Industrial heat pump specifications for 140-165°C applications, CAPEX estimates $800-900/kW thermal capacity

---

### 4.2 NCC-H2 (Hydrogen-Fueled Naphtha Cracker)

**Applicability:** Naphtha crackers ONLY
- Ethylene production facilities
- Propylene production (co-product)
- **Requires:** Dedicated hydrogen supply infrastructure

#### Cost Parameters (Annual CAPEX using simple annualization)

| Year | CAPEX (USD/tCO2) | OPEX (USD/tCO2) | Total Fixed Cost | Technology Status |
|------|----------------|----------------|------------------|-------------------|
| **2025** | 1,725 / 25 = 69.0 | 69.0 (4% of 1,725) | 138.0 | Not Available ✗ |
| **2030** | 1,440 / 25 = 57.6 | 57.6 (4% of 1,440) | 115.2 | **NEWLY AVAILABLE ✓** |
| **2040** | 1,035 / 25 = 41.4 | 41.4 (4% of 1,035) | 82.8 | Available ✓ |
| **2050** | 863 / 25 = 34.5 | 34.5 (4% of 863) | 69.0 | Available ✓ |

**Note:** Lifetime = 25 years for major process equipment

#### Technical Specifications

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **H2 Consumption** | 0.18 | ton H2/ton ethylene | Hydrogen fuel requirement |
| **H2 Lower Heating Value** | 120 | MJ/kg | Thermodynamic property |
| **Thermal Efficiency** | 85% | % | H2 combustion efficiency |
| **Technology Readiness Level** | 7 | TRL | Pilot/demonstration scale |
| **Equipment Lifetime** | 25 | years | Major equipment lifetime |
| **Availability Year** | 2030 | year | Expected commercial deployment |

#### Process Transformation

**BEFORE (Baseline):**
- Naphtha feedstock: 105 GJ/ton (becomes product - UNCHANGED)
- Fossil fuel combustion: 40.23 GJ/ton (naphtha, LNG, fuel gas, etc.)
- **Total Emissions:** 1.739 tCO2/ton ethylene

**AFTER (NCC-H2):**
- Naphtha feedstock: 105 GJ/ton (becomes product - UNCHANGED)
- Hydrogen combustion: 0.18 ton H2/ton ethylene (provides process heat)
- **Total Emissions:** ~0.0 tCO2/ton ethylene (green H2)

**KEY INSIGHT:** Naphtha feedstock cost is NOT saved - it continues to be purchased. Only the fuel source changes from fossil to hydrogen.

#### Emission Reduction

| Metric | Value | Notes |
|--------|-------|-------|
| **Baseline Emissions** | 1.739 tCO2/ton ethylene | From fuel combustion |
| **Emissions After NCC-H2** | 0.0 tCO2/ton ethylene | Green H2 (zero emissions) |
| **Abatement per Ton** | 1.739 tCO2/ton ethylene | 100% reduction in combustion emissions |
| **Total Abatement (2050)** | 23.03 MtCO2/year | 40.4% of total abatement potential |

#### Hydrogen Demand Projections

| Year | Ethylene Capacity (kt/year) | H2 Consumption (kt/year) | H2 Consumption (Mt/year) |
|------|---------------------------|------------------------|------------------------|
| **2030** | 12,883 | 0 | 0.0 | (Not yet deployed) |
| **2035** | 13,839 | 678 | 0.68 | Early deployment |
| **2040** | 14,550 | 4,911 | 4.91 | Rapid expansion |
| **2045** | 15,135 | 9,018 | 9.02 | Continued growth |
| **2050** | 15,408 | 12,882 | **12.88** | Near-complete deployment |

**Infrastructure Requirement:** 12.88 million tons/year hydrogen supply by 2050 represents a massive infrastructure challenge requiring dedicated hydrogen production, storage, and distribution networks.

**Literature Source:** RSC Green Chemistry 2025, hydrogen steam cracker studies, CAPEX estimates $2,800-3,000/ton capacity

---

### 4.3 NCC-ELECTRICITY (Electric Naphtha Cracker)

**Applicability:** Naphtha crackers ONLY
- Ethylene production facilities
- Propylene production (co-product)
- **Requires:** Renewable electricity supply (not grid electricity)

#### Cost Parameters (Annual CAPEX using simple annualization)

| Year | CAPEX (USD/tCO2) | OPEX (USD/tCO2) | Total Fixed Cost | Technology Status |
|------|----------------|----------------|------------------|-------------------|
| **2025** | 1,840 / 25 = 73.6 | 64.4 (3.5% of 1,840) | 138.0 | Not Available ✗ |
| **2030** | 1,560 / 25 = 62.4 | 54.6 (3.5% of 1,560) | 117.0 | **NEWLY AVAILABLE ✓** |
| **2040** | 1,150 / 25 = 46.0 | 40.3 (3.5% of 1,150) | 86.3 | Available ✓ |
| **2050** | 940 / 25 = 37.6 | 32.9 (3.5% of 940) | 70.5 | Available ✓ |

#### Technical Specifications

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **Electricity Consumption** | 3.0 | MWh/ton ethylene | RE electricity requirement |
| **Thermal Efficiency** | 95% | % | Electric heating efficiency |
| **Technology Readiness Level** | 6 | TRL | Engineering/development scale |
| **Equipment Lifetime** | 25 | years | Major equipment lifetime |
| **Availability Year** | 2030 | year | Expected commercial deployment |

#### Process Transformation

**BEFORE (Baseline):**
- Naphtha feedstock: 105 GJ/ton (becomes product - UNCHANGED)
- Fossil fuel combustion: 40.23 GJ/ton (provides process heat)
- **Total Emissions:** 1.739 tCO2/ton ethylene

**AFTER (NCC-Electricity):**
- Naphtha feedstock: 105 GJ/ton (becomes product - UNCHANGED)
- RE electricity: 3.0 MWh/ton ethylene (provides process heat)
- **Total Emissions:** ~0.15 tCO2/ton ethylene (RE lifecycle: 3.0 × 0.05)

**KEY INSIGHT:** Like NCC-H2, naphtha feedstock is not eliminated - only the heating method changes from combustion to electric resistance/induction heating.

#### Emission Reduction

| Metric | Value | Notes |
|--------|-------|-------|
| **Baseline Emissions** | 1.739 tCO2/ton ethylene | From fuel combustion |
| **Emissions After NCC-E** | 0.15 tCO2/ton ethylene | RE lifecycle emissions |
| **Abatement per Ton** | 1.589 tCO2/ton ethylene | 91.4% reduction |
| **Total Abatement (2050)** | 24.48 MtCO2/year | 43.0% of total abatement potential |

#### Renewable Electricity Demand Projections

| Year | NCC-E Deployment (MtCO2) | Electricity Consumption (TWh/year) | Notes |
|------|------------------------|---------------------------------|-------|
| **2030** | 7.66 | 40.6 | Initial deployment |
| **2035** | 21.84 | 115.8 | Rapid expansion |
| **2040** | 22.94 | 121.6 | Near-maximum |
| **2045** | 23.87 | 126.5 | Stable high deployment |
| **2050** | 24.48 | **129.8** | Maximum deployment |

**Context:** 129.8 TWh/year represents approximately 20-25% of Korea's current total electricity generation (~600 TWh/year). This massive electricity demand requires significant renewable energy infrastructure expansion.

**Literature Source:** RSC Green Chemistry 2025 (Linde e-cracker: 2.86 MWh/ton, rounded to 3.0), CAPEX estimates $3,000-3,500/ton capacity

---

### 4.4 RE PPA (Renewable Energy Power Purchase Agreement)

**Applicability:** NCC facilities ONLY (user-specified constraint)
- Applies to existing electricity consumption
- Switches grid electricity to renewable electricity via contract
- **No infrastructure changes required**

#### Cost Parameters

| Year | CAPEX | OPEX | Total Fixed Cost | Technology Status |
|------|-------|------|------------------|-------------------|
| **All Years** | 0.0 | 0.0 | 0.0 | Available ✓ (2025+) |

**Note:** RE PPA has zero CAPEX/OPEX because it's a procurement contract, not physical infrastructure. All costs are embedded in the RE electricity price.

#### Technical Specifications

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **Energy Conversion** | 1.0 | ratio | No conversion - direct substitution |
| **Emission Reduction** | Variable | tCO2/MWh | Grid EF - RE EF |
| **Technology Readiness Level** | 9 | TRL | Commercially available |
| **Equipment Lifetime** | 99 | years | Contract-based (no physical asset) |
| **Availability Year** | 2025 | year | Ready for deployment |

#### Process Transformation

**BEFORE (Baseline):**
- Grid electricity consumption: varies by facility
- Grid emission factor (2025): 0.45 tCO2/MWh
- Grid emission factor (2050): 0.25 tCO2/MWh (due to grid decarbonization)

**AFTER (RE PPA):**
- RE electricity consumption: same as grid (no change in amount)
- RE emission factor: 0.05 tCO2/MWh (constant over time)

**Emission Reduction Formula:**
```
Abatement per MWh = Grid_EF(year) - RE_EF
                   = Grid_EF(year) - 0.05

2025: 0.45 - 0.05 = 0.40 tCO2/MWh
2030: 0.41 - 0.05 = 0.36 tCO2/MWh
2050: 0.25 - 0.05 = 0.20 tCO2/MWh
```

**KEY INSIGHT:** RE PPA becomes less cost-effective over time as the grid naturally decarbonizes. Early deployment is more valuable.

#### Abatement Potential

| Metric | Value | Notes |
|--------|-------|-------|
| **Total NCC Electricity Emissions (2025)** | ~18 MtCO2/year | Grid-based electricity |
| **Maximum Abatement (2050)** | 8.44 MtCO2/year | Limited by NCC electricity consumption |
| **Share of Total Abatement** | 14.8% | Modest but cost-effective |

**Literature Source:** Renewable energy procurement contracts, corporate PPA market analysis

---

## 5. FUEL PRICE TRAJECTORIES

### 5.1 Fossil Fuel Prices (Constant Real Terms)

**Assumption:** All fossil fuel prices remain constant in real (inflation-adjusted) terms from 2025-2050.

| Fuel Type | Price | Unit | 2025-2050 Trajectory | Notes |
|-----------|-------|------|---------------------|-------|
| **Naphtha** | 15.0 | USD/GJ | Constant | Petrochemical feedstock |
| **LNG** | 12.0 | USD/GJ | Constant | Liquefied natural gas |
| **Fuel Gas** | 10.0 | USD/GJ | Constant | Refinery off-gas |
| **LPG** | 14.0 | USD/GJ | Constant | Liquefied petroleum gas |
| **Fuel Oil** | 13.0 | USD/GJ | Constant | Heavy fuel oil |
| **Diesel** | 16.0 | USD/GJ | Constant | Distillate fuel |
| **Grid Electricity** | 0.10 | USD/kWh | Constant | 100 USD/MWh equivalent |

**Rationale:** Conservative assumption avoids speculation on future fossil fuel prices. Real-world volatility would affect relative economics of technologies.

### 5.2 Hydrogen Price Trajectory

**Price Decline:** From $12/kg (2025) to $2/kg (2050)

| Year | H2 Price (USD/kg) | Decline from 2025 | Key Drivers |
|------|------------------|------------------|-------------|
| **2025** | 12.00 | Baseline | Current green H2 production cost via electrolysis |
| **2026** | 11.60 | -3.3% | Early learning curve effects |
| **2027** | 11.20 | -6.7% | Electrolyzer CAPEX reduction |
| **2028** | 10.80 | -10.0% | RE electricity cost decline |
| **2029** | 10.40 | -13.3% | Scale economies emerging |
| **2030** | 10.00 | -16.7% | Early commercial deployment |
| **2035** | 8.00 | -33.3% | Mass production, improved efficiency |
| **2040** | 6.00 | -50.0% | Mature technology, high volume |
| **2045** | 4.00 | -66.7% | Global market development |
| **2050** | 2.00 | -83.3% | Long-term target cost |

**Annual Decline Rate:** ~6.7% per year (compounded)

**Price Trajectory Formula:**
```
H2_Price(year) = 12.0 - 0.4 × (year - 2025)
```

**Sources:**
- IEA Hydrogen Technology Roadmap
- Bloomberg NEF Green Hydrogen Cost Projections
- Industry cost reduction targets (Hydrogen Council)
- Korean Hydrogen Economy Roadmap

**Cost Drivers:**
1. **Electrolyzer CAPEX:** $1,000/kW (2025) → $200/kW (2050)
2. **RE Electricity:** $50-70/MWh (2025) → $20-30/MWh (2050)
3. **Capacity Factor:** 40% (2025) → 70% (2050) due to better grid integration
4. **O&M Costs:** Decline with learning and automation

**Sensitivity:** NCC-H2 economics are highly sensitive to H2 price. A +$2/kg increase in 2050 would raise NCC-H2 MACC by ~$200/tCO2.

### 5.3 Renewable Electricity (RE PPA) Price Trajectory

**Price Decline:** From $130/MWh (2025) to $55/MWh (2050)

| Year | RE Price (USD/MWh) | Decline from 2025 | Key Drivers |
|------|-------------------|------------------|-------------|
| **2025** | 130 | Baseline | Current corporate PPA rates in Korea |
| **2026** | 127 | -2.3% | Early solar/wind cost reductions |
| **2027** | 124 | -4.6% | Technology improvements |
| **2028** | 121 | -6.9% | Scale economies |
| **2029** | 118 | -9.2% | Grid integration improvements |
| **2030** | 115 | -11.5% | Competitive auction results |
| **2035** | 100 | -23.1% | Grid parity approaching |
| **2040** | 85 | -34.6% | Below grid electricity cost |
| **2045** | 70 | -46.2% | Mature renewable market |
| **2050** | 55 | -57.7% | Long-term competitive pricing |

**Annual Decline Rate:** ~3.5% per year (compounded)

**Price Trajectory Formula:**
```
RE_Price(year) = 130 - 3.0 × (year - 2025)
```

**Sources:**
- Bloomberg New Energy Finance (BNEF)
- Corporate PPA market data (Korea)
- Korean renewable energy auction results
- Global renewable energy cost tracking (IRENA)

**Cost Drivers:**
1. **Solar PV:** Module efficiency improvements (22% → 28%)
2. **Offshore Wind:** Larger turbines (8 MW → 15 MW), higher capacity factors
3. **Grid Integration:** Better forecasting, storage deployment
4. **Policy Support:** RPS (Renewable Portfolio Standard), FIT mechanisms

**Comparison with Grid Electricity:**
- 2025: RE ($130/MWh) > Grid ($100/MWh) → Premium of +30%
- 2035: RE ($100/MWh) = Grid ($100/MWh) → Parity
- 2050: RE ($55/MWh) < Grid ($100/MWh) → Discount of -45%

---

## 6. GRID DECARBONIZATION TRAJECTORY

### 6.1 Korean Power Grid Emission Factor Evolution

**Baseline (2025):** 0.450 tCO2/MWh (coal-heavy power mix)
**Target (2050):** 0.250 tCO2/MWh (renewable-dominant mix)
**Net-Zero Trajectory (2070):** 0.090 tCO2/MWh

| Year | Grid EF (tCO2/MWh) | Reduction from 2025 | Annual Decline | Key Milestones |
|------|-------------------|---------------------|----------------|----------------|
| **2025** | 0.450 | Baseline | - | Coal: ~40%, Gas: ~25%, Nuclear: ~25%, RE: ~10% |
| **2030** | 0.410 | -8.9% | -0.008/year | RE expansion to 20%, coal reduction |
| **2035** | 0.370 | -17.8% | -0.008/year | Coal phase-out begins, offshore wind ramp-up |
| **2040** | 0.330 | -26.7% | -0.008/year | Coal <20%, RE >35%, grid flexibility improvements |
| **2045** | 0.290 | -35.6% | -0.008/year | Near-complete coal exit, RE >45% |
| **2050** | 0.250 | -44.4% | -0.008/year | **10th Basic Plan target**: RE >60%, coal <5% |
| **2060** | 0.170 | -62.2% | -0.008/year | Net-zero transition acceleration |
| **2070** | 0.090 | -80.0% | -0.008/year | Deep decarbonization, minimal residual emissions |

**Trajectory Formula:**
```
Grid_EF(year) = 0.45 - 0.008 × (year - 2025)
```

**Sources:**
- Korea's 10th Basic Plan for Electricity Supply and Demand
- Korean NDC (Nationally Determined Contribution) 2030
- Net-zero scenario modeling (Korea Energy Economics Institute)
- IEA Korea Energy Policy Review

**Policy Drivers:**
1. **Coal Retirement:** 24 GW → 5 GW (2025-2050)
2. **Nuclear Capacity:** Maintained at ~20-25 GW
3. **Renewable Expansion:** 25 GW → 120+ GW (solar + wind)
4. **Gas Bridge Fuel:** Temporary increase, then decline post-2040
5. **Grid Flexibility:** Battery storage, demand response, interconnections

**Implications for RE PPA:**
- As grid decarbonizes, RE PPA becomes less attractive (lower emission reduction per MWh)
- RE PPA abatement value (2025): 0.40 tCO2/MWh
- RE PPA abatement value (2050): 0.20 tCO2/MWh
- **Strategy:** Prioritize early RE PPA deployment when grid is dirtier

---

## 7. DEMAND GROWTH TRAJECTORY

### 7.1 Petrochemical Capacity Expansion (2025-2050)

**Total Capacity Growth:** +28.8% by 2050 (cumulative multiplier: 1.288)

| Period | Annual Growth Rate | Cumulative Multiplier | Period Growth | Market Phase |
|--------|-------------------|----------------------|---------------|--------------|
| **2025** | 0.0% | 1.000 | Baseline | Starting point |
| **2026-2030** | 1.5%/year | 1.000 → 1.077 | +7.7% | Early expansion, strong demand |
| **2031-2035** | 1.3%/year | 1.077 → 1.149 | +6.7% | Moderate growth, market maturation |
| **2036-2040** | 1.0%/year | 1.149 → 1.207 | +5.0% | Maturing market, slower growth |
| **2041-2045** | 0.8%/year | 1.207 → 1.256 | +4.1% | Late-stage growth, saturation approaching |
| **2046-2050** | 0.5%/year | 1.256 → 1.288 | +2.5% | Near saturation, minimal expansion |

**Detailed Annual Trajectory (Sample Years):**

| Year | Annual Growth Rate | Cumulative Multiplier | Description |
|------|-------------------|----------------------|-------------|
| 2025 | 0.0% | 1.000 | Baseline year - no growth |
| 2026 | 1.5% | 1.015 | Early growth period |
| 2030 | 1.5% | 1.077 | 2030 milestone |
| 2035 | 1.3% | 1.149 | 2035 milestone |
| 2040 | 1.0% | 1.207 | 2040 milestone |
| 2045 | 0.8% | 1.256 | 2045 milestone |
| 2050 | 0.5% | 1.288 | **2050 final: +28.8% total growth** |

**Impact on Emissions:**

```
Emissions(year) = Baseline_Emissions × Capacity_Multiplier(year) × Grid_Decarbonization_Factor(year)

Example (2050):
Fossil Emissions = 44.0 MtCO2 × 1.288 = 56.7 MtCO2 (no grid effect)
Electricity Emissions = 8.0 MtCO2 × 1.288 × (0.25/0.45) = 5.7 MtCO2 (with grid decarbonization)
Total BAU = 56.7 + 5.7 = 62.4 MtCO2 (close to actual 62.19 MtCO2)
```

**Sources:**
- Korean Petrochemical Industry Association (KPIA) projections
- Historical capacity expansion trends (2010-2024)
- Regional demand forecasts (Asia-Pacific petrochemical outlook)
- Aligned with moderate growth scenario (no major new crackers assumed)

**Methodology:**
- All facility capacities scale proportionally with multiplier
- No new facilities assumed (existing facilities expand)
- Consistent with Korean government industrial policy

---

## 8. FACILITY DATABASE

### 8.1 Overview Statistics

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Facilities** | 248 | Complete Korean petrochemical sector |
| **Total Production Capacity** | 100,066 kt/year | Sum of all products |
| **Total Baseline Emissions** | 52.01 MtCO2/year | 2025 reference year |
| **Number of Parent Companies** | 13 | Major petrochemical operators |
| **Number of Locations** | 7 | Major industrial complexes |
| **Number of Product Types** | 60+ | Diverse product portfolio |

### 8.2 Emissions by Product Group

| Product Group | Facilities | Capacity (kt/year) | Emissions (MtCO2/year) | Share of Total | Average Intensity (tCO2/kt) |
|--------------|-----------|-------------------|----------------------|----------------|---------------------------|
| **Olefins** | 39 | 25,317 | 46.31 | 89.05% | 1,829 |
| **Aromatics** | 37 | 14,374 | 5.08 | 9.77% | 353 |
| **Polymers** | 57 | 18,105 | 0.12 | 0.24% | 7 |
| **Other** | 108 | 39,315 | 0.48 | 0.92% | 12 |
| **Intermediates** | 7 | 2,955 | 0.01 | 0.02% | 4 |
| **TOTAL** | **248** | **100,066** | **52.01** | **100%** | **520 avg** |

**Key Insights:**
- **Olefins dominate:** 89% of emissions from only 16% of facilities
- **High-intensity processes:** Naphtha crackers are the primary target for decarbonization
- **Low-hanging fruit:** Polymers and intermediates already have low emission intensity

### 8.3 Emissions by Company (Top 10)

**Note:** Specific company data is available in output files but anonymized in this summary.

| Rank | Company Type | Emissions (MtCO2/year) | Facilities | Share | Average per Facility |
|------|-------------|----------------------|-----------|-------|-------------------|
| 1-3 | Major Integrated | 5-10 each | 15-25 each | 30-50% total | 0.3-0.6 |
| 4-7 | Mid-sized | 2-5 each | 5-15 each | 20-30% total | 0.2-0.4 |
| 8-10 | Smaller Specialized | 0.5-2 each | 3-8 each | 5-10% total | 0.1-0.3 |

### 8.4 Emissions by Location

| Location | Facilities | Approximate Emissions (MtCO2/year) | Share | Major Products |
|----------|-----------|----------------------------------|-------|----------------|
| **Yeosu** | ~40-50 | 15-20 | 30-40% | Olefins, aromatics, intermediates |
| **Ulsan** | ~50-60 | 10-15 | 20-30% | Ethylene, polymers, BTX |
| **Daesan** | ~30-40 | 8-12 | 15-25% | Naphtha crackers, polyolefins |
| **Onsan** | ~20-30 | 3-6 | 6-12% | Specialty chemicals |
| **Other** | ~80-100 | 5-10 | 10-15% | Distributed facilities |

**Geographic Concentration:** ~70-80% of emissions from 3 major coastal industrial complexes (Yeosu, Ulsan, Daesan)

---

# PART II: MODEL OUTPUTS

## 1. MODULE 1: BASELINE ANALYSIS

### 1.1 2025 Baseline Emissions Summary

**Total Annual Emissions:** 52.01 MtCO2/year

#### Breakdown by Fuel Type

| Fuel Source | Emissions (MtCO2/year) | Share of Total | Energy Consumption (Approximate) |
|------------|----------------------|----------------|-------------------------------|
| **Naphtha (Combustion)** | ~35-40 | 67-77% | ~650,000-740,000 TJ/year |
| **Grid Electricity** | ~8-10 | 15-19% | ~18,000-22,000 GWh/year |
| **LNG** | ~2-3 | 4-6% | ~135,000-200,000 TJ/year |
| **Fuel Gas** | ~1-2 | 2-4% | ~67,000-135,000 TJ/year |
| **Other Fuels** | ~0.5-1 | 1-2% | ~30,000-50,000 TJ/year |
| **TOTAL** | **52.01** | **100%** | **~900,000-1,100,000 TJ/year** |

**Note:** Naphtha feedstock (~2,600,000 TJ/year for ethylene production alone) is NOT included in energy consumption totals.

#### Baseline Energy Costs (2025)

| Fuel Type | Energy Consumption | Unit Price | Annual Cost (Million USD) | Share of Total Cost |
|-----------|-------------------|-----------|-------------------------|-------------------|
| **Naphtha** | 650,000 TJ | $15/GJ | ~$9,750M | 85-90% |
| **Grid Electricity** | 18,000 GWh | $0.10/kWh | ~$1,800M | 8-12% |
| **LNG** | 150,000 TJ | $12/GJ | ~$1,800M | 3-5% |
| **Other** | - | - | ~$300M | 1-2% |
| **TOTAL** | - | - | **~$13,650M** | **100%** |

**Insight:** Fuel costs represent a significant operational expense. Even modest carbon pricing ($50/tCO2) would add $2.6 billion annually, increasing total fuel costs by ~19%.

### 1.2 Business-as-Usual (BAU) Trajectory (2025-2050)

**Scenario Description:** All 248 facilities operate indefinitely (no retirement), with capacity expansion following demand growth trajectory and grid electricity decarbonization.

#### BAU Emissions Over Time

| Year | BAU Emissions (MtCO2/year) | Fossil Fuel Emissions | Electricity Emissions | Capacity Multiplier | Change from 2025 |
|------|--------------------------|---------------------|---------------------|-------------------|------------------|
| **2025** | 52.01 | 44.01 | 8.00 | 1.000 | Baseline |
| **2030** | 55.21 | 47.39 | 7.82 | 1.077 | +6.2% |
| **2035** | 58.05 | 50.58 | 7.47 | 1.149 | +11.6% |
| **2040** | 60.08 | 53.13 | 6.95 | 1.207 | +15.5% |
| **2045** | 61.58 | 55.27 | 6.31 | 1.256 | +18.4% |
| **2050** | 62.19 | 56.66 | 5.53 | 1.288 | +19.6% |

**Trajectory Drivers:**
1. **Upward Pressure:** Capacity expansion (+28.8% by 2050)
2. **Downward Pressure:** Grid decarbonization (-44.4% grid EF by 2050)
3. **Net Effect:** +19.6% emissions increase by 2050

**Cumulative BAU Emissions (2025-2050):** 1,471 MtCO2

#### BAU vs. Frozen 2025 Scenario

If there were no capacity growth and no grid decarbonization:

| Year | BAU Actual | Frozen 2025 | Difference | Drivers |
|------|-----------|-------------|-----------|---------|
| 2030 | 55.21 | 52.01 | +3.20 | Capacity +7.7%, Grid -8.9% partially offset |
| 2040 | 60.08 | 52.01 | +8.07 | Capacity +20.7%, Grid -26.7% partially offset |
| 2050 | 62.19 | 52.01 | +10.18 | Capacity +28.8%, Grid -44.4% partially offset |

**Implication:** Without intervention, emissions grow 20% by 2050 despite significant grid decarbonization.

### 1.3 Alternative Scenario: 50-Year Facility Retirement

**Scenario Description:** Facilities retire after 50 years of operation based on their year_built.

#### Impact of Retirement on BAU Trajectory

| Year | Active Facilities | Retired Facilities | Capacity Remaining | BAU with Retirement (MtCO2) | BAU w/o Retirement (MtCO2) | Reduction from Retirement |
|------|------------------|-------------------|-------------------|---------------------------|--------------------------|-------------------------|
| 2025 | 248 | 0 | 100% | 52.01 | 52.01 | 0% |
| 2030 | 245 | 3 | 98% | 54.10 | 55.21 | -2.0% |
| 2040 | 215 | 33 | 87% | 52.27 | 60.08 | -13.0% |
| 2050 | 180 | 68 | 73% | 45.40 | 62.19 | -27.0% |

**Note:** This retirement scenario is NOT used in the main analysis. The primary model assumes infinite facility lifetimes (all facilities operate forever).

---

## 2. MODULE 2: MACC ANALYSIS

### 2.1 MACC Costs by Technology and Year

#### 2025 MACC Costs (Only 2 Technologies Available)

| Technology | Abatement Potential (MtCO2/year) | CAPEX Annual ($/tCO2) | OPEX Annual ($/tCO2) | Fuel Cost Diff ($/tCO2) | **Total MACC ($/tCO2)** |
|-----------|-------------------------------|---------------------|-------------------|----------------------|----------------------|
| **Heat Pump** | 0.81 | 45.0 | 27.0 | 177.97 | **249.97** |
| **RE PPA** | 7.21 | 0.0 | 0.0 | 325.00 | **325.00** |
| NCC-H2 | 20.80 | 69.0 | 69.0 | 1,242.09 | 1,380.09 (NOT AVAILABLE) |
| NCC-Electricity | 19.01 | 73.6 | 64.4 | 245.44 | 383.44 (NOT AVAILABLE) |

**Total Available Abatement (2025):** 8.02 MtCO2/year (15.4% of baseline)

#### 2030 MACC Costs (All 4 Technologies Available)

| Technology | Abatement Potential (MtCO2/year) | CAPEX Annual ($/tCO2) | OPEX Annual ($/tCO2) | Fuel Cost Diff ($/tCO2) | **Total MACC ($/tCO2)** |
|-----------|-------------------------------|---------------------|-------------------|----------------------|----------------------|
| **Heat Pump** | 0.87 | 36.0 | 21.6 | 157.43 | **215.03** |
| **RE PPA** | 7.68 | 0.0 | 0.0 | 319.44 | **319.44** |
| **NCC-Electricity** | 20.47 | 62.4 | 54.6 | 217.12 | **334.12** ✓ NEW |
| **NCC-H2** | 22.40 | 57.6 | 57.6 | 1,035.08 | **1,150.28** ✓ NEW |

**Total Available Abatement (2030):** 51.42 MtCO2/year (93.2% of BAU)

**Cost Order (2030):**
1. Heat Pump: $215/tCO2 (lowest cost)
2. RE PPA: $319/tCO2
3. NCC-Electricity: $334/tCO2
4. NCC-H2: $1,150/tCO2 (highest cost)

#### 2040 MACC Costs

| Technology | Abatement Potential (MtCO2/year) | Total MACC ($/tCO2) | Cost Change from 2030 |
|-----------|-------------------------------|-------------------|---------------------|
| **Heat Pump** | 0.98 | **156.30** | -27.3% |
| **RE PPA** | 8.26 | **307.14** | -3.9% |
| **NCC-Electricity** | 22.94 | **241.92** | -27.6% |
| **NCC-H2** | 24.72 | **500.18** | -56.5% |

**Cost Order (2040):**
1. Heat Pump: $156/tCO2
2. NCC-Electricity: $242/tCO2
3. RE PPA: $307/tCO2
4. NCC-H2: $500/tCO2

**Key Change:** NCC-Electricity becomes more cost-effective than RE PPA due to RE price decline and NCC-E CAPEX learning.

#### 2050 MACC Costs (Final State)

| Technology | Abatement Potential (MtCO2/year) | Total MACC ($/tCO2) | Cost Change from 2025 |
|-----------|-------------------------------|-------------------|---------------------|
| **Heat Pump** | 1.04 | **131.19** | -47.5% |
| **NCC-Electricity** | 24.48 | **202.55** | -47.2% (from 2030) |
| **NCC-H2** | 23.03 | **297.79** | -78.4% (from 2030) |
| **RE PPA** | 8.44 | **299.45** | -7.9% |

**Cost Order (2050):**
1. Heat Pump: $131/tCO2 (lowest)
2. NCC-Electricity: $203/tCO2
3. NCC-H2: $298/tCO2
4. RE PPA: $299/tCO2 (highest)

**Key Transformation:** NCC-H2 becomes competitive with RE PPA by 2050 due to dramatic hydrogen price decline ($12/kg → $2/kg).

### 2.2 MACC Cost Evolution (2025-2050)

#### Heat Pump Cost Trajectory

| Year | Total MACC ($/tCO2) | CAPEX Component | OPEX Component | Fuel Cost Component | RE Price ($/MWh) |
|------|-------------------|----------------|----------------|-------------------|-----------------|
| 2025 | 249.97 | 45.0 | 27.0 | 177.97 | 130 |
| 2030 | 215.03 | 36.0 | 21.6 | 157.43 | 115 |
| 2035 | 185.58 | 31.5 | 18.9 | 135.18 | 100 |
| 2040 | 156.30 | 27.0 | 16.2 | 113.10 | 85 |
| 2045 | 131.66 | 24.0 | 14.4 | 93.26 | 70 |
| 2050 | 131.19 | 22.5 | 13.5 | 95.19 | 55 |

**Driver:** RE price decline is the primary cost reducer (fuel cost component drops 47%).

#### NCC-H2 Cost Trajectory

| Year | Total MACC ($/tCO2) | CAPEX Component | OPEX Component | Fuel Cost Component | H2 Price ($/kg) |
|------|-------------------|----------------|----------------|-------------------|----------------|
| 2030 | 1,150.28 | 57.6 | 57.6 | 1,035.08 | 10.0 |
| 2035 | 794.89 | 50.4 | 50.4 | 694.09 | 8.0 |
| 2040 | 500.18 | 41.4 | 41.4 | 417.38 | 6.0 |
| 2045 | 367.76 | 37.8 | 37.8 | 292.16 | 4.0 |
| 2050 | 297.79 | 34.5 | 34.5 | 228.79 | 2.0 |

**Driver:** H2 price decline is the dominant factor (fuel cost component drops 78% from 2030-2050).

**Critical Insight:** NCC-H2 cost-competitiveness is heavily dependent on achieving aggressive H2 price targets. If H2 price remains at $6/kg in 2050 (instead of $2/kg), NCC-H2 MACC would be ~$700/tCO2 instead of $298/tCO2.

#### NCC-Electricity Cost Trajectory

| Year | Total MACC ($/tCO2) | CAPEX Component | OPEX Component | Fuel Cost Component | RE Price ($/MWh) |
|------|-------------------|----------------|----------------|-------------------|-----------------|
| 2030 | 334.12 | 62.4 | 54.6 | 217.12 | 115 |
| 2035 | 288.48 | 54.6 | 47.8 | 186.08 | 100 |
| 2040 | 241.92 | 46.0 | 40.3 | 155.62 | 85 |
| 2045 | 201.74 | 42.0 | 36.8 | 122.94 | 70 |
| 2050 | 202.55 | 37.6 | 32.9 | 132.05 | 55 |

**Driver:** Balanced contribution from CAPEX learning (-49%) and RE price decline (-52% fuel cost).

#### RE PPA Cost Trajectory

| Year | Total MACC ($/tCO2) | RE Price ($/MWh) | Grid EF (tCO2/MWh) | Abatement per MWh |
|------|-------------------|----------------|-------------------|------------------|
| 2025 | 325.00 | 130 | 0.450 | 0.40 |
| 2030 | 319.44 | 115 | 0.410 | 0.36 |
| 2035 | 312.50 | 100 | 0.370 | 0.32 |
| 2040 | 307.14 | 85 | 0.330 | 0.28 |
| 2045 | 304.35 | 70 | 0.290 | 0.24 |
| 2050 | 299.45 | 55 | 0.250 | 0.20 |

**Driver:** RE price decline (+benefits) is offset by grid decarbonization (-benefits), resulting in minimal net cost change.

**Critical Insight:** RE PPA becomes less attractive over time as grid decarbonizes. Early deployment (2025-2035) provides better value.

### 2.3 Cumulative MACC Curves

#### 2025 MACC Curve

```
MACC ($/tCO2)
    500 |
        |
    400 |
        |                       (NCC-H2: Not Available)
    300 |        ┌────┐
        |        │ RE │         (NCC-E: Not Available)
    200 |  ┌────┤PPA │
        |  │ HP │    │
    100 |  │    │    │
        |  │    │    │
      0 |──┴────┴────┴─────────────────────────────────
        0  0.81 8.02           (Abatement MtCO2/year)

Legend: HP = Heat Pump, RE PPA = Renewable PPA
```

**Total Abatement Available (2025):** 8.02 MtCO2/year

#### 2030 MACC Curve (All Technologies Available)

```
MACC ($/tCO2)
  1,200 |
        |                                   ┌──────────┐
  1,000 |                                   │  NCC-H2  │
        |                                   │          │
    800 |                                   │          │
        |                                   │          │
    600 |                                   │          │
        |                                   │          │
    400 |        ┌────┬─────────────┬───────┤          │
        |        │ RE │   NCC-E     │       │          │
    200 |  ┌───��┤PPA │             │       │          │
        |  │ HP │    │             │       │          │
      0 |──┴────┴────┴─────────────┴───────┴──────────┴─
        0  0.87 8.55  29.02                51.42
                                    (Abatement MtCO2/year)
```

**Cost-Effective Abatement (<$350/tCO2):** ~29 MtCO2/year
**Total Abatement Available:** 51.42 MtCO2/year

#### 2050 MACC Curve (Final State)

```
MACC ($/tCO2)
    500 |
        |
    400 |
        |
    300 |                    ┌──────────┬───────┐
        |                    │  NCC-H2  │ RE PPA│
    200 |        ┌───────────┤          │       │
        |        │   NCC-E   │          │       │
    100 |  ┌────┤           │          │       │
        |  │ HP │           │          │       │
      0 |──┴────┴───────────┴──────────┴───────┴─
        0  1.04  25.52       48.55      56.99
                                (Abatement MtCO2/year)
```

**Cost-Effective Abatement (<$200/tCO2):** ~1 MtCO2/year (Heat Pump only)
**Cost-Effective Abatement (<$300/tCO2):** ~49 MtCO2/year (all except RE PPA)
**Total Abatement Available:** 56.99 MtCO2/year

**Key Transformation:** By 2050, three technologies (Heat Pump, NCC-E, NCC-H2) cluster in the $130-300/tCO2 range, making them all potentially cost-competitive depending on carbon pricing levels.

---

## 3. MODULE 3: COST OPTIMIZATION & DEPLOYMENT PATHWAYS

### 3.1 Policy Target Scenario

**Emission Reduction Targets (Aligned with Korean NDC):**
- **2030:** 39.0 MtCO2/year (25% reduction from 2025 baseline)
- **2040:** 19.1 MtCO2/year (63% reduction from baseline)
- **2050:** 5.2 MtCO2/year (90% reduction from baseline)

### 3.2 Technology Deployment Mix by Year

#### 2025-2029: Early Phase (Limited Technology Availability)

| Year | Target (MtCO2) | Total Deployed (MtCO2) | Heat Pump | NCC-H2 | NCC-E | RE PPA |
|------|---------------|----------------------|-----------|--------|-------|--------|
| 2025 | 52.0 | 0.01 | 0.01 | 0 | 0 | 0 |
| 2026 | 49.4 | 3.24 | 0.82 | 0 | 0 | 2.42 |
| 2027 | 46.8 | 6.46 | 0.83 | 0 | 0 | 5.63 |
| 2028 | 44.2 | 8.34 | 0.85 | 0 | 0 | 7.49 |
| 2029 | 41.6 | 8.44 | 0.86 | 0 | 0 | 7.58 |

**Strategy:** Maximize deployment of available technologies (Heat Pump + RE PPA) to prepare for more aggressive reductions.

#### 2030: Technology Transition Year

| Technology | Deployment (MtCO2/year) | Share of Abatement | MACC ($/tCO2) | Cumulative CAPEX ($M) |
|-----------|------------------------|-------------------|--------------|---------------------|
| Heat Pump | 0.87 | 5.4% | 215 | $156M |
| RE PPA | 7.68 | 47.3% | 319 | $0 (contract) |
| **NCC-Electricity** | 7.66 | 47.3% | 334 | **$10,157M** ✓ NEW |
| NCC-H2 | 0.0 | 0% | 1,150 | $0 (too expensive) |
| **TOTAL** | **16.21** | **100%** | - | **$10,313M** |

**Key Decision:** NCC-Electricity becomes available and is immediately deployed at scale due to better cost-effectiveness than NCC-H2.

**2030 Outcome:**
- Target: 39.0 MtCO2
- Actual: 39.0 MtCO2 (target met exactly)
- BAU: 55.2 MtCO2
- Reduction: 29.4% from BAU

#### 2035: Ramp-Up Phase

| Technology | Deployment (MtCO2/year) | Share of Abatement | Cumulative CAPEX ($M) |
|-----------|------------------------|-------------------|---------------------|
| Heat Pump | 0.93 | 2.9% | $172M |
| **NCC-H2** | 1.21 | 3.8% | **$1,045M** ✓ NEW |
| NCC-Electricity | 21.84 | 68.1% | $25,109M |
| RE PPA | 8.07 | 25.2% | $0 |
| **TOTAL** | **32.05** | **100%** | **$27,940M** |

**Key Decision:** NCC-H2 begins deployment as H2 price drops below $8/kg, making it competitive for some applications.

**2035 Outcome:**
- Target: 26.0 MtCO2
- Actual: 26.0 MtCO2 (target met)
- BAU: 58.05 MtCO2
- Reduction: 55.2% from BAU

#### 2040: Acceleration Phase

| Technology | Deployment (MtCO2/year) | Share of Abatement | Cumulative CAPEX ($M) |
|-----------|------------------------|-------------------|---------------------|
| Heat Pump | 0.98 | 2.4% | $188M |
| NCC-H2 | 8.78 | 21.4% | $7,574M |
| NCC-Electricity | 22.94 | 55.9% | $27,808M |
| RE PPA | 8.31 | 20.3% | $0 |
| **TOTAL** | **41.01** | **100%** | **$35,809M** |

**2040 Outcome:**
- Target: 19.1 MtCO2
- Actual: 19.1 MtCO2 (target met)
- BAU: 60.08 MtCO2
- Reduction: 68.3% from BAU

#### 2045: Deep Decarbonization Phase

| Technology | Deployment (MtCO2/year) | Share of Abatement | Cumulative CAPEX ($M) |
|-----------|------------------------|-------------------|---------------------|
| Heat Pump | 1.02 | 2.0% | $203M |
| NCC-H2 | 16.12 | 32.7% | $13,906M |
| NCC-Electricity | 23.87 | 48.4% | $28,275M |
| RE PPA | 8.44 | 17.1% | $0 |
| **TOTAL** | **49.45** | **100%** | **$42,415M** |

**2045 Outcome:**
- Target: 12.1 MtCO2
- Actual: 12.1 MtCO2 (target met)
- BAU: 61.58 MtCO2
- Reduction: 80.3% from BAU

#### 2050: Final State (Maximum Deployment)

| Technology | Deployment (MtCO2/year) | Share of Total | MACC ($/tCO2) | Cumulative CAPEX ($M) |
|-----------|------------------------|---------------|--------------|---------------------|
| Heat Pump | 1.04 | 1.8% | 131 | **$945M** |
| NCC-H2 | 23.03 | 40.4% | 298 | **$19,864M** |
| NCC-Electricity | 24.48 | 43.0% | 203 | **$22,980M** |
| RE PPA | 8.44 | 14.8% | 299 | **$0** (contract) |
| **TOTAL** | **56.99** | **100%** | - | **$47,866M** |

**2050 Outcome:**
- Target: 5.2 MtCO2
- Actual: 5.2 MtCO2 (target met)
- BAU: 62.19 MtCO2
- Reduction: 91.6% from BAU
- **Reduction from 2025 Baseline:** 90.0%

**Final State Summary:**
- Maximum technically feasible abatement achieved
- All cost-effective technologies fully deployed
- Residual 5.2 MtCO2 likely from:
  - Process emissions (non-energy)
  - Facilities where no technology is applicable
  - Technical/operational constraints

### 3.3 Deployment Timeline Visualization

```
Technology Deployment Over Time (MtCO2/year)

60 |                                              ╔═══════╗
   |                                              ║ Total ║
50 |                                         ╔════╣ 57.0  ║
   |                                    ╔════╝    ╚═══════╝
40 |                               ╔════╝
   |                          ╔════╝
30 |                     ╔════╝                   NCC-E: 43%
   |                ╔════╝
20 |           ╔════╝                             NCC-H2: 40%
   |      ╔════╝
10 |  ╔═══╝                                       RE PPA: 15%
   |══╝
 0 |━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  HP: 2%
   2025  2030  2035  2040  2045  2050

Legend:
■ Heat Pump (green)
■ RE PPA (orange)
■ NCC-Electricity (red)
■ NCC-H2 (blue)
```

### 3.4 Emission Trajectory Compliance

| Year | Target | BAU | Actual with Tech | Total Deployed | Reduction from BAU | Target Met? |
|------|--------|-----|-----------------|---------------|-------------------|------------|
| 2025 | 52.0 | 52.01 | 52.00 | 0.01 | -0.0% | ✓ Yes |
| 2030 | 39.0 | 55.21 | 39.00 | 16.21 | -29.4% | ✓ Yes |
| 2035 | 26.0 | 58.05 | 26.00 | 32.05 | -55.2% | ✓ Yes |
| 2040 | 19.1 | 60.08 | 19.07 | 41.01 | -68.3% | ✓ Yes |
| 2045 | 12.1 | 61.58 | 12.13 | 49.45 | -80.3% | ✓ Yes |
| 2050 | 5.2 | 62.19 | 5.20 | 56.99 | -91.6% | ✓ Yes |

**Cumulative Emissions (2025-2050):**
- BAU Trajectory: 1,471 MtCO2
- With Technology Deployment: 658.5 MtCO2
- **Total Reduction: 812.5 MtCO2 (55.2% reduction)**

---

## 4. ENERGY TRANSITION IMPACTS

### 4.1 Hydrogen Demand Growth

| Year | NCC-H2 Deployment (MtCO2) | Ethylene Production (kt/year) | H2 Consumption (kt/year) | H2 Consumption (Mt/year) |
|------|--------------------------|------------------------------|-------------------------|----------------------|
| 2025 | 0 | 11,962 | 0 | 0.0 |
| 2030 | 0 | 12,883 | 0 | 0.0 |
| 2035 | 1.21 | 13,839 | 678 | 0.68 |
| 2040 | 8.78 | 14,550 | 4,911 | 4.91 |
| 2045 | 16.12 | 15,135 | 9,018 | 9.02 |
| 2050 | 23.03 | 15,408 | 12,882 | **12.88** |

**Annual H2 Demand Growth (2035-2050):** 12.2 Mt / 15 years = 0.81 Mt/year average

**Peak Deployment Period (2040-2045):**
- 2040: 4.91 Mt/year
- 2045: 9.02 Mt/year
- **Increase: 4.11 Mt in 5 years** (rapid ramp-up phase)

**Infrastructure Requirements by 2050:**
- **Production Capacity:** 12.88 Mt/year green H2
  - Assuming 50 kWh/kg H2: 644 TWh/year electrolyzer electricity
  - At 30% capacity factor: ~245 GW electrolyzer capacity
- **Storage:** ~1-2 Mt buffer capacity (30-60 days supply)
- **Distribution:** Dedicated hydrogen pipelines or repurposed natural gas infrastructure
- **Production Sites:** Likely co-located with petrochemical complexes (Yeosu, Ulsan, Daesan)

**Comparison with Korean H2 Economy Roadmap:**
- Korean 2050 H2 target (all sectors): ~27 Mt/year
- Petrochemical sector share: **48% of total national H2 demand**

### 4.2 Renewable Electricity Demand Increase

| Year | Heat Pump (TWh) | NCC-E (TWh) | Total RE Increase (TWh) | % of Current Korean Generation |
|------|----------------|------------|------------------------|------------------------------|
| 2025 | 0.00 | 0 | 0.00 | 0% |
| 2030 | 0.00 | 40.6 | 40.62 | 6.8% |
| 2035 | 0.00 | 115.8 | 115.76 | 19.3% |
| 2040 | 0.00 | 121.6 | 121.60 | 20.3% |
| 2045 | 0.00 | 126.5 | 126.53 | 21.1% |
| 2050 | 0.00 | 129.8 | **129.76** | **21.6%** |

**Note:** Heat Pump electricity consumption is minimal in the optimization results due to limited applicability (temperature constraints).

**Context:**
- Current Korean electricity generation: ~600 TWh/year
- Additional 130 TWh/year = +21.6% increase
- This is IN ADDITION to projected baseline electricity demand growth

**RE Generation Requirements:**
- Assuming 25% capacity factor (solar/wind mix): ~60 GW additional RE capacity
- Current Korean RE capacity (2024): ~25 GW
- **Required expansion: 2.4x current RE capacity for petrochemical sector alone**

**Grid Integration Challenges:**
- 130 TWh/year represents massive base-load demand
- Requires grid flexibility, storage, and transmission upgrades
- Petrochemical facilities may need on-site RE generation + storage

### 4.3 Total Energy System Transformation (2050)

**Combined Impact:**

| Energy Carrier | New Demand | Current Equivalent | Infrastructure Required |
|---------------|-----------|-------------------|----------------------|
| **Hydrogen** | 12.88 Mt/year | 48% of national H2 target | 245 GW electrolyzers, pipelines |
| **RE Electricity** | 129.8 TWh/year | 21.6% of current generation | 60 GW solar/wind |
| **Total Electrolyzer Electricity** | 644 TWh/year | ~100% of current generation | - |
| **COMBINED RE ELECTRICITY** | 774 TWh/year | **129% of current total generation** | **Massive RE expansion** |

**Critical Insight:** The total renewable electricity requirement (direct + for H2 production) exceeds Korea's current total electricity generation. This highlights the massive scale of energy system transformation required.

**Regional Concentration:**
- 70-80% of demand concentrated in 3 coastal complexes (Yeosu, Ulsan, Daesan)
- Opportunity for offshore wind development nearby
- May require dedicated RE generation zones with transmission corridors

---

## 5. INVESTMENT ANALYSIS

### 5.1 Investment Timeline

| Period | New CAPEX ($Billion) | Cumulative CAPEX ($Billion) | Average Annual CAPEX ($B/year) | Primary Technologies |
|--------|-------------------|---------------------------|------------------------------|---------------------|
| **2025** | $0.007 | $0.007 | $0.007 | Heat Pump (minimal) |
| **2026-2030** | $10.306 | $10.313 | $2.06 | HP + RE PPA + NCC-E starts |
| **2031-2035** | $17.627 | $27.940 | $3.53 | **PEAK INVESTMENT PERIOD** |
| **2036-2040** | $7.869 | $35.809 | $1.57 | Continued NCC-E + NCC-H2 |
| **2041-2045** | $6.606 | $42.415 | $1.32 | NCC-H2 acceleration |
| **2046-2050** | $5.451 | $47.866 | $1.09 | Final deployment |
| **TOTAL (2025-2050)** | **$47.866** | **$47.866** | **$1.91** | All technologies |

**Peak Investment Year:** 2034-2035 (~$3.5-4 billion/year)

**Investment Front-Loading:**
- 58% of total investment ($27.9B) occurs in first 10 years (2025-2035)
- Critical for meeting 2030 and 2035 targets
- Requires significant early capital mobilization

### 5.2 Investment by Technology (Cumulative 2025-2050)

| Technology | CAPEX ($Billion) | Share | Abatement (MtCO2/year) | CAPEX per Abatement ($M/MtCO2) |
|-----------|----------------|-------|----------------------|---------------------------|
| **Heat Pump** | $0.95 | 2.0% | 1.04 | $912 |
| **NCC-H2** | $19.86 | 41.5% | 23.03 | $863 |
| **NCC-Electricity** | $22.98 | 48.0% | 24.48 | $939 |
| **RE PPA** | $0.00 | 0% | 8.44 | $0 |
| **TOTAL** | **$47.87** | **100%** | **56.99** | **$840 avg** |

**Insights:**
- **NCC technologies dominate:** 89.5% of total investment
- **Similar unit costs:** NCC-H2 and NCC-E both ~$860-940M per MtCO2 abatement potential
- **RE PPA is capital-free:** All costs embedded in electricity prices (OpEx not CapEx)

### 5.3 Annual Investment Profile

```
Annual CAPEX ($Billion/year)

$4.0 |
     |     ╔═══╗
$3.5 |     ║   ║
     |     ║   ║  ← PEAK INVESTMENT PERIOD (2031-2035)
$3.0 |     ║   ║
     |     ║   ║
$2.5 |     ║   ║
     |     ║   ║
$2.0 | ╔═══╣   ╠═══╗
     | ║   ║   ║   ║
$1.5 | ║   ║   ║   ╠═══╗
     | ║   ║   ║   ║   ║
$1.0 | ║   ║   ║   ║   ╠═══╗
     | ║   ║   ║   ║   ║   ║
$0.5 | ║   ║   ║   ║   ║   ║
     | ║   ║   ║   ║   ║   ║
$0.0 |─╨───╨───╨───╨───╨───╨─────
     2025 2030 2035 2040 2045 2050
```

**Investment Phasing:**
1. **Ramp-up (2025-2030):** $2.1B/year average - Deploy available technologies
2. **Peak (2031-2035):** $3.5B/year average - NCC-H2 and NCC-E scale-up
3. **Plateau (2036-2045):** $1.3-1.6B/year - Continued expansion
4. **Completion (2046-2050):** $1.1B/year - Final facilities converted

### 5.4 Financing Requirements

**Total Capital Required:** $47.9 billion (2025-2050)

**Potential Financing Sources:**

| Financing Source | Potential Contribution | Notes |
|----------------|----------------------|-------|
| **Corporate Equity** | 30-40% ($14-19B) | Company balance sheets |
| **Project Finance (Bank Loans)** | 40-50% ($19-24B) | Asset-backed lending |
| **Green Bonds** | 10-15% ($5-7B) | Sustainability-linked financing |
| **Government Grants/Subsidies** | 10-20% ($5-10B) | Climate fund, industrial policy |
| **Carbon Credits/Revenue** | 5-10% ($2-5B) | Korea ETS, international markets |

**Debt Service Requirements (Assuming 50% Debt at 5% Interest):**
- Total Debt: $23.9 billion
- Annual Interest: $1.2 billion/year
- Principal Repayment (20-year amortization): $1.2 billion/year
- **Total Debt Service: ~$2.4 billion/year**

**Return on Investment Analysis:**

Assuming carbon price of $150/tCO2 in 2040:
- Annual Abatement Value: 41 MtCO2 × $150/tCO2 = $6.15 billion/year
- Annual Debt Service: $2.4 billion/year
- Annual Fuel Cost Savings: Variable (depends on H2 vs. fossil fuel prices)
- **Net Positive Cash Flow Potential: Yes (if carbon price >$150/tCO2)**

---

# PART III: SCENARIO COMPARISON & SENSITIVITY

## 1. SCENARIO COMPARISON

### 1.1 Emission Targets Across Scenarios

**Note:** Main analysis focuses on Policy Target scenario. Other scenarios (Conservative, Moderate, Aggressive) available in output files.

| Scenario | 2030 Target | 2040 Target | 2050 Target | Cumulative 2025-2050 | Alignment |
|----------|------------|------------|------------|---------------------|-----------|
| **Policy Target** | 39.0 | 19.1 | 5.2 | 658.5 MtCO2 | Korean NDC |
| Conservative | 45.0 | 30.0 | 20.0 | ~800 MtCO2 | Slower pace |
| Moderate | 42.0 | 25.0 | 12.0 | ~730 MtCO2 | Balanced |
| Aggressive | 35.0 | 15.0 | 2.0 | ~550 MtCO2 | Accelerated |

### 1.2 Technology Mix Comparison (2050)

| Scenario | Heat Pump | NCC-H2 | NCC-E | RE PPA | Total | CAPEX ($B) |
|----------|-----------|--------|-------|--------|-------|-----------|
| **Policy Target** | 1.04 | 23.03 | 24.48 | 8.44 | 56.99 | $47.9 |
| (Other scenarios available in output files) | - | - | - | - | - | - |

---

## 2. INTERNATIONAL COMPARISONS

### 2.1 MACC Costs vs. Global Studies

| Study/Region | Technology | MACC (USD/tCO2) | Year | Comparison to This Study |
|-------------|-----------|----------------|------|----------------------|
| **This Study (Korea)** | Heat Pump | 250 | 2025 | Baseline |
| IEA Net Zero Petrochemicals | Industrial Heat Pump | 180-220 | 2025 | 12-28% lower (economies of scale?) |
| McKinsey Global MACC | Process Electrification | 200-300 | 2025 | Aligned |
| **This Study (Korea)** | NCC-H2 | 1,150 | 2030 | Baseline |
| Material Economics (EU) | H2-based Crackers | 800-1,200 | 2030 | Aligned (upper range) |
| **This Study (Korea)** | NCC-H2 | 298 | 2050 | Baseline |
| IEA Hydrogen Roadmap | Industrial H2 Applications | 250-400 | 2050 | Aligned |

**Conclusion:** Korean MACC estimates are generally consistent with international studies, with slightly higher near-term costs potentially reflecting:
- Technology immaturity in Korean context
- Smaller scale vs. EU/global markets
- Conservative assumptions on learning curves

### 2.2 Hydrogen Price Assumptions vs. Global Targets

| Source | 2030 H2 Price | 2050 H2 Price | Notes |
|--------|--------------|--------------|-------|
| **This Study** | $10/kg | $2/kg | Aggressive learning curve |
| IEA Hydrogen Roadmap | $8-12/kg | $1.50-3/kg | Aligned with this study |
| BNEF Green H2 Outlook | $6-10/kg | $1-2/kg | Slightly more optimistic |
| Hydrogen Council | $10-15/kg | $2-4/kg | Aligned with this study |
| US DOE Targets | - | $1/kg | Very aggressive (H2Shot) |

**Assessment:** This study's H2 price trajectory ($12 → $2/kg) is within the range of major global forecasts but toward the optimistic end.

---

# PART IV: LIMITATIONS & UNCERTAINTIES

## 1. MODEL LIMITATIONS

### 1.1 Technology Assumptions

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| **NCC Commercial Availability** | Assumed 2030 may be optimistic | Sensitivity: 2030 → 2035 delay |
| **Heat Pump COP** | Constant 4.0 may not hold for all applications | Conservative estimate (industrial proven) |
| **Learning Curves** | Assume continuous deployment; disruptions could slow | Based on historical technology curves |
| **Technology Interactions** | Assumed independent; may have synergies/conflicts | Simplification for tractability |

### 1.2 Price Projections

| Assumption | Uncertainty | Impact on MACC |
|-----------|-------------|---------------|
| **H2 Price ($2/kg by 2050)** | HIGH | +$2/kg → +$200/tCO2 NCC-H2 MACC |
| **RE Price ($55/MWh by 2050)** | MEDIUM | +$20/MWh → +$67/tCO2 NCC-E MACC |
| **Fossil Fuel Prices (Constant)** | MEDIUM | Volatility could change relative economics |
| **Grid EF (0.25 tCO2/MWh by 2050)** | MEDIUM | Slower grid decarb increases RE PPA value |

### 1.3 Operational Assumptions

| Assumption | Reality Check | Consequence |
|-----------|--------------|-------------|
| **No Facility Retirement** | Some facilities may retire before 2050 | Overestimates BAU emissions |
| **Linear Deployment** | Actual adoption may be lumpy | Optimization is idealized |
| **Perfect Foresight** | Model knows future prices; reality doesn't | Real decisions face uncertainty |
| **No Operational Constraints** | Assumes all facilities can adopt all applicable technologies | May overestimate feasible abatement |

## 2. DATA QUALITY

### 2.1 High-Confidence Data
- ✓ Baseline emissions (facility-level measurements)
- ✓ Current fuel prices (market data)
- ✓ Existing technology performance (Heat Pump, RE PPA)
- ✓ Grid emission factors (official government data)

### 2.2 Medium-Confidence Data
- ~ Future fuel price trajectories (industry projections)
- ~ NCC technology CAPEX (literature-based, not Korea-specific)
- ~ Demand growth (aligned with forecasts but uncertain)
- ~ Facility-level technology applicability (product-based assumptions)

### 2.3 Low-Confidence Data
- ⚠ Long-term H2 prices 2040-2050 (highly speculative)
- ⚠ NCC technology availability timeline (dependent on global R&D)
- ⚠ Facility operational lifetimes (no data on retirement plans)

## 3. RECOMMENDED SENSITIVITY ANALYSES

For future model refinements, test:

1. **Hydrogen Price Range:**
   - Low: $1/kg (2050)
   - Base: $2/kg (2050)
   - High: $4/kg (2050)
   - Impact: NCC-H2 MACC ranges from $180/tCO2 to $500/tCO2

2. **NCC Technology Availability Delay:**
   - Base: 2030
   - Delayed: 2035
   - Impact: Cannot meet 2035 target; investments shift to 2035-2040

3. **Demand Growth:**
   - Low: 0%/year (no growth)
   - Base: 1.5% → 0.5% (declining)
   - High: 2.5%/year (constant)
   - Impact: ±30% on 2050 abatement requirements

4. **Carbon Pricing:**
   - $50/tCO2 to $500/tCO2 range
   - Impact: Economic viability of technologies without subsidies

5. **CAPEX Variation:**
   - ±30% for all technologies
   - Impact: ±$14B total investment, MACC shifts by ±$50-150/tCO2

---

# PART V: POLICY RECOMMENDATIONS

## 1. NEAR-TERM ACTIONS (2025-2030)

### 1.1 Technology Development
- **Fund NCC-H2 and NCC-E pilots:** $500M-1B government R&D support for demonstration projects
- **Accelerate Heat Pump deployment:** Tax credits, accelerated depreciation for installations
- **Facilitate RE PPA market:** Streamline permitting, guarantee grid access for corporate PPAs

### 1.2 Carbon Pricing
- **Strengthen K-ETS:** Gradual price floor increase from current ~$20/tCO2 to $100/tCO2 by 2030
- **Border Carbon Adjustment:** Protect domestic industry from carbon leakage
- **Revenue recycling:** Use carbon auction revenues to fund technology subsidies

### 1.3 Infrastructure Planning
- **Hydrogen backbone:** Begin planning national H2 pipeline network
- **Grid upgrades:** Transmission capacity to petrochemical hubs (Yeosu, Ulsan, Daesan)
- **RE development zones:** Designate offshore wind areas near industrial complexes

## 2. MID-TERM ACTIONS (2030-2040)

### 2.1 Financial Support
- **CAPEX subsidies:** 30-50% grants for first-of-a-kind NCC conversions
- **Green loans:** Low-interest financing (2-3%) for decarbonization projects
- **Loan guarantees:** De-risk early commercial projects

### 2.2 Market Creation
- **Green product premiums:** Certification for low-carbon petrochemicals
- **Procurement mandates:** Government/SOE preference for green products
- **International carbon markets:** Link K-ETS with EU ETS, Japan JCM

### 2.3 Technology Standards
- **Emission performance standards:** Gradually tightening limits for new/retrofit facilities
- **Technology certification:** Ensure NCC-H2/E meet safety and environmental standards

## 3. LONG-TERM ACTIONS (2040-2050)

### 3.1 Phase Out Subsidies
- Reduce direct CAPEX support as technologies reach cost-competitiveness
- Maintain carbon pricing to sustain economic incentive

### 3.2 Workforce Transition
- Retraining programs for fossil fuel operations → H2/RE operations
- Support for affected workers/communities

### 3.3 Net-Zero Completion
- Address residual emissions (<5 MtCO2) through:
  - CCS for process emissions
  - Negative emissions (BECCS, DAC)
  - High-quality offsets

---

# APPENDICES

## Appendix A: Glossary of Terms

| Term | Definition |
|------|------------|
| **MACC** | Marginal Abatement Cost Curve - graphical representation of emission reduction costs |
| **NCC** | Naphtha Cracking Complex - petrochemical facility producing olefins |
| **RE PPA** | Renewable Energy Power Purchase Agreement - long-term contract for renewable electricity |
| **COP** | Coefficient of Performance - heat pump efficiency (heat output / electricity input) |
| **TRL** | Technology Readiness Level - 1 (basic research) to 9 (commercial deployment) |
| **BAU** | Business-as-Usual - baseline scenario with no intervention |
| **NDC** | Nationally Determined Contribution - country's emission reduction pledge under Paris Agreement |
| **MtCO2** | Million tons of CO2 equivalent |
| **GJ** | Gigajoule (10^9 joules) - energy unit |
| **TWh** | Terawatt-hour (10^12 watt-hours) - large-scale electricity unit |
| **kt** | Kiloton (1,000 tons) - production capacity unit |
| **CAPEX** | Capital Expenditure - upfront investment costs |
| **OPEX** | Operating Expenditure - ongoing operational costs |
| **LCOE** | Levelized Cost of Energy - average cost per unit of energy over project lifetime |
| **K-ETS** | Korea Emissions Trading Scheme - national carbon market |
| **BTX** | Benzene, Toluene, Xylene - aromatic petrochemical products |

## Appendix B: Unit Conversions

| From | To | Conversion Factor |
|------|-----|------------------|
| GJ | MWh | ÷ 3.6 |
| MWh | GJ | × 3.6 |
| kt | Mt | ÷ 1,000 |
| Mt | kt | × 1,000 |
| USD/GJ | USD/MWh | × 3.6 |
| USD/kWh | USD/MWh | × 1,000 |
| tCO2/GJ | tCO2/MWh | × 3.6 |
| kg H2 | GJ (LHV) | × 0.120 |

## Appendix C: Methodology Summary

### MACC Calculation
```
MACC (USD/tCO2) = (CAPEX_annual + OPEX_annual + Fuel_Cost_Diff) / Abatement

Where:
• CAPEX_annual = Total CAPEX / Equipment Lifetime (simple annualization, no discount rate)
• OPEX_annual = Total CAPEX × (OPEX % of CAPEX)
• Fuel_Cost_Diff = (New Energy Cost - Baseline Energy Cost) / Emission Reduction
• Abatement = Baseline Emissions - Emissions After Technology Deployment
```

### Optimization Algorithm
1. **Sort technologies by MACC** (lowest to highest cost)
2. **For each year:**
   - Deploy cheapest available technology to meet emission target
   - Track cumulative deployment (irreversible - capacity only increases)
   - Update CAPEX, H2 consumption, electricity consumption
3. **Constraints:**
   - Technology availability years (NCC-H2/E available from 2030)
   - Abatement potential limits (cannot exceed technical maximum)
   - Irreversibility (deployed capacity cannot decrease)

## Appendix D: Data Sources

**Primary Sources:**
1. Korean Petrochemical Industry Association (KPIA) - facility database, production data
2. Korean Ministry of Environment - emission reporting, permits
3. IEA Energy Technology Perspectives 2023 - technology costs, learning curves
4. Bloomberg NEF Hydrogen Economy Outlook 2024 - H2 price projections
5. RSC Green Chemistry 2025 - NCC-Electricity technology study (Linde e-cracker)
6. Korean 10th Basic Plan for Electricity Supply and Demand - grid emission trajectory
7. Material Economics Industrial Transformation 2050 - NCC-H2 cost estimates

**Secondary Sources:**
8. McKinsey Global GHG Abatement Cost Curve
9. IPCC AR6 Chapter 11 (Industry Sector)
10. Hydrogen Council Cost Competitiveness Study 2024
11. Korean NDC 2030 targets (government submission to UNFCCC)
12. IRENA Renewable Power Generation Costs 2023
13. Company annual reports and sustainability disclosures

## Appendix E: Model File Structure

**Key Data Files:**
- [data/baseline_2025_detailed.csv](data/baseline_2025_detailed.csv) - 248 facilities with energy and emissions
- [data/technology_parameters.csv](data/technology_parameters.csv) - CAPEX/OPEX by technology and year
- [data/h2_price_trajectory.csv](data/h2_price_trajectory.csv) - Hydrogen price 2025-2050
- [data/re_price_trajectory.csv](data/re_price_trajectory.csv) - RE electricity price 2025-2050
- [data/grid_emission_trajectory.csv](data/grid_emission_trajectory.csv) - Grid EF 2025-2070

**Key Output Files:**
- [outputs/module_01/baseline_2025_detailed.csv](outputs/module_01/baseline_2025_detailed.csv) - Baseline analysis
- [outputs/module_02/macc_annual_2025_2050.csv](outputs/module_02/macc_annual_2025_2050.csv) - MACC by technology-year
- [outputs/module_03/policy_target_deployment.csv](outputs/module_03/policy_target_deployment.csv) - Deployment pathway
- [outputs/module_03/policy_target_facility_allocation_2050.csv](outputs/module_03/policy_target_facility_allocation_2050.csv) - Facility-level tech mix

---

## DOCUMENT INFORMATION

**Report Title:** Comprehensive MACC Analysis - Korean Petrochemical Industry Decarbonization (2025-2050)

**Model Version:** Energy-Based MACC v2.0 (October 2024)

**Report Date:** October 28, 2025

**Geographic Scope:** South Korea (248 petrochemical facilities)

**Temporal Scope:** 2025-2050 (26 years)

**Emission Scope:** Direct emissions (Scope 1: fuel combustion) + Purchased electricity (Scope 2: grid emissions)

**Methodology:** Energy-based MACC with cost optimization under emission constraints

**Contact:** [Model maintainer contact information]

**Citation:** [Recommended citation format for academic/policy use]

---

**END OF COMPREHENSIVE REPORT**

**Total Length:** ~50 pages (formatted in Word: 12pt font, 1.15 spacing)

**Last Updated:** 2025-10-28

---

## USAGE NOTES FOR MICROSOFT WORD

This Markdown document can be directly copied into Microsoft Word. For best formatting:

1. **Copy the entire document** (Ctrl+A, Ctrl+C from this viewer)
2. **Paste into Word** using "Keep Source Formatting" or "Merge Formatting"
3. **Apply styles:**
   - Heading 1: Part titles (PART I, PART II, etc.)
   - Heading 2: Major sections (1., 2., 3.)
   - Heading 3: Subsections (1.1, 1.2, etc.)
   - Heading 4: Sub-subsections (1.1.1, 1.1.2, etc.)
4. **Tables:** May need slight formatting adjustments (borders, shading)
5. **Code blocks:** Format as "Fixed Width" or "Courier New" font
6. **Page numbers:** Insert footer with page numbering
7. **Table of Contents:** Use Word's automatic TOC feature (References → Table of Contents)

**Recommended Word Settings:**
- Font: Calibri or Arial 11-12pt
- Line Spacing: 1.15 or 1.5
- Margins: Normal (1" all sides)
- Page Size: A4 or Letter
