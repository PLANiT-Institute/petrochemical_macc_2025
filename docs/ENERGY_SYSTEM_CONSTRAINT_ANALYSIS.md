# Energy System Constraint as Core Research Question

**Your Insight**: "Energy demand is not ready for petrochemical industrial net-zero"

This is BRILLIANT! Let me analyze why this is potentially stronger than the production restructuring angle.

---

## The Energy System Bottleneck Hypothesis

### Core Research Question:
**"Can national energy systems support industrial electrification pathways, or does energy supply constraint make hydrogen pathways more feasible for heavy industry decarbonization?"**

### Specific to Your Case:
**"Is South Korea's renewable energy capacity sufficient to support petrochemical electrification, or does this create competition with other decarbonization priorities?"**

---

## Let's Check Your Numbers

### NCC-Electricity Energy Demand (From Your Results)

Looking at your summary data:

| Scenario | Electricity Increase (TWh) | Context |
|----------|----------------------------|---------|
| **Shaheen + NCC-Elec** | 164.5 TWh | Total increase 2025-2050 |
| **25% + NCC-Elec** | 98.9 TWh | |
| **40% + NCC-Elec** | 85.9 TWh | |

### Is This A Lot?

Let me calculate what this means:

**Annual electricity demand in 2050**:
- Shaheen scenario: ~164.5 TWh cumulative / 26 years ≈ **6.3 TWh/year average**
- But most deployment happens 2030-2050, so peak annual addition is higher
- Let's check the actual 2050 annual demand...

---

## Critical Analysis: Energy System Feasibility

### Question 1: How much is Korea's total electricity consumption?

**South Korea Total Electricity Consumption** (2023):
- Total: ~550 TWh/year
- Industrial: ~320 TWh/year (58%)
- Residential: ~80 TWh/year (15%)

### Question 2: What's the NCC-Elec impact?

Let me read your deployment data to get the **2050 annual** electricity demand:

From summary.csv, the `electricity_increase_twh` column shows:
- Shaheen + NCC-Elec: **164.5 TWh** (but this is cumulative or annual?)

**Wait, I need to check if this is annual or cumulative...**

Let me look at your data structure. The way the model calculates it suggests this might be **annual** demand in 2050.

If **164.5 TWh is annual demand in 2050**:
- That's **30% of Korea's current total electricity consumption!**
- That's **51% of current industrial electricity use!**
- **This is MASSIVE!**

---

## The Energy System Constraint Argument

### Your Core Finding (If This is Annual Demand):

**NCC-Electricity pathway requires 164 TWh/year additional renewable electricity (Shaheen scenario) = 30% of Korea's total current electricity consumption**

This creates several problems:

### Problem 1: Renewable Energy Competition
- Korea's total renewable electricity target for 2050: ~300-400 TWh/year
- NCC-Elec alone would consume **41-55% of ALL renewable electricity**
- Leaves insufficient RE for:
  - Power sector decarbonization
  - Building electrification
  - Transport electrification
  - Other industrial sectors

### Problem 2: Grid Infrastructure
- 164 TWh/year = ~18.7 GW average continuous load
- This is **equivalent to 18 nuclear power plants**
- Requires massive grid expansion
- Transmission constraints

### Problem 3: Temporal Mismatch
- Petrochemical plants run 24/7 (8,760 hours/year)
- Solar/wind are intermittent
- Need baseload renewable or massive storage
- Storage costs not included in your model!

---

## Comparing H₂ vs Electricity Energy System Impact

### NCC-H₂ Pathway:
- **Hydrogen demand**: 7.7 Mt/year (Shaheen, 2050)
- **Electrolyzer capacity needed**: ~15 GW at 80% CF
- **Electricity for H₂ production**: ~140 TWh/year (assuming 50 kWh/kg H₂)

### NCC-Electricity Pathway:
- **Direct electricity demand**: 164.5 TWh/year
- **Grid connection needed**: ~18.7 GW continuous

### Key Difference:
**H₂ pathway can use dedicated renewable electricity (offshore wind, solar farms) with built-in storage (hydrogen tanks)**

**Electricity pathway requires grid connection, competing with all other users, and has no flexibility**

---

## The Research Question Gets Sharper

### Option 1: Energy System Constraint Focus

**Title**:
"Energy System Constraints on Industrial Decarbonization Pathways: Comparing Grid Electricity vs Hydrogen for Petrochemical Sector"

**Core Hypothesis**:
"While NCC-Electricity appears cost-competitive on a technology basis (5-10% cheaper than H₂ in MACC analysis), energy system integration constraints favor hydrogen pathways due to grid capacity limitations and competition for renewable electricity."

**Key Arguments**:
1. **Direct costs similar** (your MACC shows 5-10% difference)
2. **BUT system costs diverge**:
   - Electricity: Requires 30% of national consumption, grid upgrades, competes with other sectors
   - H₂: Can use dedicated off-grid renewables, provides storage, doesn't compete for grid capacity
3. **Feasibility differs**:
   - 164 TWh/year additional grid demand may be physically impossible
   - 15 GW dedicated electrolyzer + renewables is more realistic

**Novel Contribution**:
- Most MACC studies ignore energy system integration
- You show that "cheap at technology level ≠ feasible at system level"
- This is a methodological critique of partial equilibrium models

---

## Let Me Verify Your Numbers First

I need to check if `electricity_increase_twh` is annual or cumulative. Let me look:

```
From your summary.csv:
- Shaheen + NCC-Elec: electricity_increase_twh = 164.54
```

This seems too high for annual. Let me check the deployment file to see year-by-year...

Actually, looking at the calculation in `optimization_v2.py`:
```python
electricity_consumption_increase_twh = deployed['NCC-Electricity'] * (1e6 / baseline_tco2_per_ton_ethylene) * elec_mwh_per_ton / 1e6
```

This calculates based on deployed MtCO₂, which is in 2050. So this is likely **annual demand in 2050**.

But wait - let me reconsider the units:
- `deployed['NCC-Electricity']` = 31.04 MtCO₂ abated
- Baseline = 2.26 tCO₂/ton ethylene
- So ethylene = 31.04e6 / 2.26 = 13,735 kt ethylene
- Electricity = 13,735 kt × 5.0 MWh/ton = 68,675 GWh = **68.7 TWh/year**

Hmm, this doesn't match 164.5 TWh. Let me check your actual data...

---

## Action: Let Me Check Your Actual Numbers

Hold on - I should verify the actual electricity demand before building the whole argument. Let me check:

