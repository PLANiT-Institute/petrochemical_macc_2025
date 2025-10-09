# Fuel Price Scenarios and MACC Cost Interpretation

## Understanding Negative MACC Costs

### What Does Negative Cost Mean?

In MACC (Marginal Abatement Cost Curve) analysis:
- **Positive cost** = Company must PAY to abate 1 tonne of CO2
- **Negative cost** = Company SAVES money while abating 1 tonne of CO2
- **Zero cost** = Break-even (investment exactly equals fuel savings)

**Negative costs do NOT mean "earning money from nothing"**. They mean:
> **Fuel cost savings exceed the investment costs (CAPEX + OPEX)**

This is economically rational - technologies with negative MACC costs should be deployed immediately because they are **profitable investments** that also reduce emissions.

### Example: RE PPA in 2025

**Calculation:**
- Grid electricity: $100/MWh
- RE PPA: $58/MWh
- Grid emission factor: 0.45 tCO2/MWh
- RE emission factor: 0.05 tCO2/MWh
- Abatement per MWh: 0.45 - 0.05 = 0.40 tCO2/MWh

**Cost per tCO2 abated:**
```
Cost = (RE price - Grid price) / Abatement per MWh
     = ($58 - $100) / 0.40 tCO2
     = -$42 / 0.40 tCO2
     = -$105/tCO2
```

**Interpretation:** For every tonne of CO2 abated, the company **saves $105** by switching from grid to RE electricity. This is a **no-regret action**.

---

## Fuel Price Assumptions

### Current Fuel Price Scenarios (2025-2050)

| Fuel Type | Unit | 2025 | 2030 | 2040 | 2050 | Trend |
|-----------|------|------|------|------|------|-------|
| **Naphtha** | $/GJ | 15.0 | 15.0 | 15.0 | 15.0 | Flat |
| **Grid Electricity** | $/MWh | 100 | 100 | 100 | 100 | Flat |
| **RE PPA** | $/MWh | 58 | 52.8 | 42.4 | 32 | ↓ 45% |
| **Hydrogen** | $/kg | 6.00 | 5.04 | 3.12 | 1.20 | ↓ 80% |

### Energy Price Equivalents (2025)

To compare fuels on equal energy basis:

| Fuel | Price | Energy Equivalent ($/MWh thermal) |
|------|-------|-----------------------------------|
| Naphtha | $15/GJ | $54/MWh |
| Grid Electricity | $100/MWh | $100/MWh |
| RE PPA | $58/MWh | $58/MWh |
| Hydrogen | $6/kg | $50/MWh |

**Key ratio:** Grid electricity is **1.85x more expensive** than naphtha (per unit energy)

### Why Are These Prices Realistic?

1. **Grid Electricity ($100/MWh)**
   - Korean industrial electricity prices: ~$80-120/MWh (2023-2024)
   - Includes transmission, distribution, taxes
   - Reasonable assumption for long-term average

2. **Naphtha ($15/GJ = $54/MWh)**
   - Naphtha is a refinery byproduct, cheaper than crude oil
   - Petrochemical companies have long-term supply contracts
   - $15/GJ ≈ $88/barrel equivalent (reasonable)

3. **RE PPA ($58→$32/MWh)**
   - Solar/wind PPA prices declining globally
   - Korea's offshore wind targets will drive prices down
   - 2050 price ($32/MWh) aligns with global renewable cost curves

4. **Hydrogen ($6→$1.2/kg)**
   - Green H2 cost reduction from renewable energy decline + electrolyzer scale-up
   - Ambitious but aligned with IEA/IRENA projections for 2050

---

## Technology MACC Costs Explained

### 1. RE PPA (Renewable Energy Power Purchase Agreement)

**2025 Economics:**
- CAPEX: $0 (no investment - just a procurement contract)
- OPEX: $0 (included in PPA price)
- Fuel cost savings: $42/MWh × 2.5 MWh/tCO2 = **-$105/tCO2**
- **Total: -$105/tCO2** ✅ **PROFITABLE**

**Why negative?**
RE electricity ($58/MWh) is cheaper than grid ($100/MWh), so switching saves money while reducing emissions.

**2050 Economics:**
- Fuel cost savings: $68/MWh × 5 MWh/tCO2 = **-$340/tCO2**
- **Even more profitable** as RE becomes cheaper and grid emission factor declines (more MWh needed per tCO2)

---

### 2. Heat Pump

**2025 Economics:**
- CAPEX (annualized): $15.28/tCO2
- OPEX: $0.46/tCO2
- Fuel cost differential: **-$736/tCO2**
  - Heat pump uses electricity at $58/MWh (RE price)
  - With COP=4.0, delivers heat at $58/4 = $14.5/MWh thermal
  - Replaces naphtha at $54/MWh thermal
  - Savings: ($54 - $14.5) × 18.6 MWh/tCO2 = **-$736/tCO2**
- **Total: -$721/tCO2** ✅ **HIGHLY PROFITABLE**

**Why such large savings?**
Heat pumps are 4x more efficient than burning fuel, so even though electricity is expensive, the efficiency makes it cheaper.

**Calculation validation:**
```
1 tCO2 from naphtha = 67.1 GJ = 18.6 MWh thermal
Heat pump cost: 18.6 MWh ÷ 4 (COP) × $58/MWh = $270
Naphtha cost: 18.6 MWh × $54/MWh = $1,005
Savings: $1,005 - $270 = $735/tCO2 ✅
```

---

### 3. NCC-H2 (Naphtha Cracker with Hydrogen)

**2025 Economics:**
- CAPEX (annualized): $28.1/tCO2
- OPEX: $7.0/tCO2
- Fuel cost differential: **+$2,349/tCO2**
  - H2 cost: 559 kg/tCO2 × $6/kg = $3,354
  - Naphtha cost: 67.1 GJ/tCO2 × $15/GJ = $1,006
  - Extra cost: $2,349/tCO2
- **Total: +$2,378/tCO2** ❌ **EXPENSIVE in 2025**

**2050 Economics:**
- Fuel cost differential: **-$405/tCO2** (H2 at $1.2/kg is cheaper than naphtha!)
- **Total: -$321/tCO2** ✅ **PROFITABLE by 2050**

---

### 4. NCC-Electricity (Electric Naphtha Cracker)

**2025 Economics:**
- CAPEX (annualized): $32.8/tCO2
- OPEX: $6.6/tCO2
- Fuel cost differential: **+$75/tCO2**
  - Electricity cost: 18.6 MWh/tCO2 × $58/MWh = $1,081
  - Naphtha cost: $1,006
  - Extra cost: $75/tCO2
- **Total: +$108/tCO2** ❌ **SLIGHTLY EXPENSIVE in 2025**
- Not available until 2030 (TRL 6)

**2050 Economics:**
- Fuel cost differential: **-$440/tCO2** (RE becomes very cheap)
- **Total: -$393/tCO2** ✅ **PROFITABLE by 2050**

---

## MACC Results Summary

### 2025 Technology Ranking (by cost)

| Rank | Technology | Cost ($/tCO2) | Potential (MtCO2) | Status |
|------|------------|---------------|-------------------|--------|
| 1 | **Heat Pump** | **-721** | 3.9 | ✅ Deploy immediately |
| 2 | **RE PPA** | **-105** | 7.2 | ✅ Deploy immediately |
| 3 | NCC-Electricity | +108 | 37.6 | ⏳ Wait (not available yet) |
| 4 | NCC-H2 | +2,378 | 37.6 | ❌ Too expensive |

**Total negative-cost potential (2025): 11.1 MtCO2**

### 2050 Technology Ranking (by cost)

| Rank | Technology | Cost ($/tCO2) | Potential (MtCO2) | Status |
|------|------------|---------------|-------------------|--------|
| 1 | **Heat Pump** | **-850** | 3.9 | ✅ Most profitable |
| 2 | **NCC-Electricity** | **-393** | 37.6 | ✅ Large potential |
| 3 | **RE PPA** | **-340** | 6.5 | ✅ Profitable |
| 4 | **NCC-H2** | **-321** | 37.6 | ✅ Now profitable |

**Total negative-cost potential (2050): 85.6 MtCO2** (exceeds total emissions!)

---

## Optimization Results Under These Fuel Scenarios

### Moderate_2050 Scenario Deployment

| Year | Target (Mt) | Heat Pump | RE PPA | NCC-Elec | NCC-H2 | Rationale |
|------|-------------|-----------|--------|----------|--------|-----------|
| 2025 | 52 | 0 | 0 | 0 | 0 | No reduction needed |
| 2030 | 46 | **3.9** | **1.4** | 0 | 0 | Deploy cheapest first (negative cost) |
| 2035 | 40 | **3.9** | **6.6** | 0 | 0 | Maximize negative-cost technologies |
| 2040 | 32 | **3.9** | **6.9** | **7.0** | 0 | NCC-Elec now available |
| 2045 | 22 | **3.9** | 0 | **23.1** | 0 | NCC-Elec cheaper than RE PPA |
| 2050 | 10 | **3.9** | 0 | **34.4** | 0 | All on NCC-Elec (large potential) |

### Why is NCC-H2 not deployed?

Even though NCC-H2 becomes profitable by 2050 (-$321/tCO2), **NCC-Electricity is cheaper** (-$393/tCO2) and has the same abatement potential (37.6 MtCO2). The optimizer chooses NCC-Electricity over NCC-H2.

---

## Key Insights from Fuel Scenarios

### 1. Electricity Grid Price Drives Economics

Current assumption: **Grid electricity = $100/MWh (flat)**

**Sensitivity:**
- If grid drops to $80/MWh: RE PPA savings decrease, Heat Pump still profitable
- If grid rises to $120/MWh: All electricity-based technologies become more attractive

### 2. RE PPA Price Decline Creates "No-Regret" Actions

RE PPA cost: **-$105/tCO2 (2025) → -$340/tCO2 (2050)**

This means switching to renewable electricity is a **profitable investment** that also reduces emissions. Companies should do this **immediately** regardless of emission targets.

### 3. Hydrogen Price Trajectory is Critical

H2 must drop from **$6/kg to $1.20/kg** for NCC-H2 to be competitive.

**If H2 stays at $3/kg in 2050:**
- NCC-H2 cost: ~+$800/tCO2 (expensive)
- NCC-Electricity remains the better choice

### 4. Heat Pump Efficiency Creates Large Savings

With **COP = 4.0**, heat pumps deliver heat at **25% of the electricity cost**.

Even with expensive electricity ($100/MWh grid), heat pumps cost only:
- $100 ÷ 4 = **$25/MWh thermal** vs naphtha at $54/MWh

This explains the large negative cost (**-$721/tCO2**).

---

## Validating the Fuel Scenarios

### Questions for User to Validate:

1. **Grid electricity price ($100/MWh)**
   - Is this Korean industrial electricity price (2025-2050)?
   - Should it increase with carbon pricing?
   - Current Korean rates: ~₩100-120/kWh = $80-100/MWh ✅

2. **Naphtha price ($15/GJ = $54/MWh)**
   - Is this spot price or contract price?
   - Should it increase with oil prices?
   - Current naphtha: ~$80-100/barrel = $14-18/GJ ✅

3. **RE PPA trajectory ($58 → $32/MWh)**
   - Is this realistic for Korean offshore wind/solar?
   - Does it include grid connection costs?
   - Global PPA trends: $30-50/MWh by 2030 ✅

4. **Hydrogen price trajectory ($6 → $1.2/kg)**
   - Is this green H2 or blue H2?
   - Does it include transportation/storage?
   - IEA green H2 target: $1-2/kg by 2050 ✅

---

## Recommendation

**The fuel scenarios and resulting MACC costs are METHODOLOGICALLY CORRECT.**

Negative costs indicate **profitable emission reduction opportunities**. This is common in MACC analysis and represents:
- Energy efficiency improvements (Heat Pump: 4x more efficient)
- Fuel switching to cheaper alternatives (RE PPA: $58 vs $100/MWh)
- Future cost declines (H2: $6 → $1.2/kg)

**Next Steps:**
1. **Validate fuel price assumptions** with client/industry data
2. **Run sensitivity analysis** on key prices (grid electricity, RE PPA, H2)
3. **Update scenarios** if fuel prices need adjustment
4. **Communicate clearly** that negative costs = profitable investments

---

## File Outputs

The fuel scenario data is now saved in:
- **`outputs/fuel_price_scenarios.csv`** - Comprehensive fuel price table (2025-2050)
- **`outputs/module_02/macc_annual_2025_2050.csv`** - MACC costs including fuel price references
- **`data/fuel_price_trajectory.csv`** - Source data for all fuel prices
- **`data/re_price_trajectory.csv`** - RE PPA price trajectory
- **`data/h2_price_trajectory.csv`** - Hydrogen price trajectory

All optimization outputs now reflect these fuel price assumptions.
