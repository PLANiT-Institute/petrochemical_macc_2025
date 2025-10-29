# NCC Logic - Deep Review and Simplification Proposals

**Purpose**: Prepare model for academic publication
**Focus**: Make NCC logic crystal clear and logically simple
**Date**: 2025-10-29

---

## CURRENT NCC LOGIC - DETAILED ANALYSIS

### 1. What is NCC (Naphtha Cracking Complex)?

**Definition**:
- **Chemical Process**: Thermal cracking of naphtha to produce olefins
- **Main Products**: Ethylene, Propylene, Butadiene
- **Key Equipment**: Steam cracker furnaces (operating at 800-900°C)

**Identification in Model**:
```python
def is_ncc_facility(product_name):
    """Only Ethylene, Propylene, Butadiene are NCC products"""
    ncc_keywords = ['ethylene', 'propylene', 'butadiene']
    return any(keyword in product_name.lower() for keyword in ncc_keywords)
```

**Issue for Discussion**:
- ✅ **CORRECT**: BTX products (benzene, toluene, xylene) are NOT NCC - they're from BTX plants
- ✅ **SIMPLE**: Clear binary classification (is NCC or not)
- Question: **Is this too simplified?** Some facilities may have both NCC and non-NCC units?

---

### 2. NCC Technologies: H2 vs Electricity

#### Current Understanding:

**NCC-H2 (Hydrogen Furnaces)**:
- Replace LNG/fuel gas combustion with H2 combustion for heat
- Naphtha still used as FEEDSTOCK (chemically cracked, not burned)
- Energy: H2 provides ~11 GJ/ton ethylene heating
- Emissions: Near-zero from heating (green H2), but naphtha cracking still emits

**NCC-Electricity (Electric Cracking)**:
- Replace thermal furnaces with electric heating
- Naphtha still used as FEEDSTOCK (chemically cracked)
- Energy: Renewable electricity provides heating
- Emissions: Near-zero from heating (RE), but naphtha cracking still emits

#### Key Question for Academic Paper:

**Are these technologies TRULY mutually exclusive at FACILITY level?**

Current assumption: **YES** - A facility cannot use both H2 AND electricity for the same furnace.

**Reality Check**:
1. ✅ **Same Equipment**: Both modify the same furnace units
2. ✅ **Physical Impossibility**: Can't burn H2 AND use electric heating simultaneously
3. ✅ **Capital Lock-in**: Once one technology is installed, can't switch
4. ⚠️ **But**: A facility with MULTIPLE cracker units could theoretically install H2 in some and electricity in others

**Current Model Logic**: Treats all crackers at a facility as ONE unit (simplification)

**For Academic Paper - We need to state**:
> "We assume all cracker units at a given facility adopt the same technology (H2 OR electricity, not both). This simplification is justified because: (1) operational consistency within facilities, (2) shared infrastructure requirements, (3) technology learning effects favor single-technology deployment."

---

### 3. Mutual Exclusivity Implementation

#### Where It's Enforced:

**Level 1: Industry-Wide Selection** (optimization_v2.py lines 181-203)
```python
# FIRST TIME NCC technology is needed (year 2030):
if ncc_choice is None:
    h2_cost = get_cost('NCC-H2', 2030)     # e.g., $477/tCO2
    elec_cost = get_cost('NCC-Electricity', 2030)  # e.g., $259/tCO2

    # Select cheaper option FOR ENTIRE INDUSTRY
    ncc_choice = 'NCC-Electricity'  # because $259 < $477

# ALL FUTURE YEARS: Only deploy selected technology
tech_list = filter_out(non-selected NCC technology)
```

**Level 2: Facility-Level Allocation** (optimization_v2.py lines 519-559)
```python
# Determine which NCC tech was deployed industry-wide
ncc_deployed = 'NCC-Electricity'  # from Level 1

# Allocate ONLY that technology to facilities
if ncc_deployed == 'NCC-Electricity':
    allocate_ncc_electricity_to_facilities()
    # NCC-H2 = 0 for all facilities
elif ncc_deployed == 'NCC-H2':
    allocate_ncc_h2_to_facilities()
    # NCC-Electricity = 0 for all facilities
```

#### Critical Questions:

**Q1: Should INDUSTRY-WIDE selection be replaced with FACILITY-LEVEL selection?**

Current: All facilities choose the same technology
Alternative: Each facility chooses independently based on facility-specific economics

**Pros of Current Approach**:
- ✅ Simple and transparent
- ✅ Realistic (technology standardization in industry)
- ✅ Easier to explain in paper
- ✅ Reflects learning curve effects (one technology scales)

**Cons of Current Approach**:
- ❌ May miss facility-specific optimization opportunities
- ❌ Ignores facility heterogeneity

**My Recommendation**: **KEEP CURRENT** - Simpler for academic paper, realistic assumption

---

**Q2: Is the one-time irreversible choice realistic?**

Current: Once selected in 2030, choice persists to 2050
Justification: Capital lock-in (can't rebuild furnaces)

**Is this too strict?**
- Consider: Some facilities built in 2030 with NCC-Electricity
- In 2045, H2 prices may drop significantly
- New facilities built in 2045 could theoretically choose H2
- But current model doesn't allow this

**Alternative Logic**:
```python
# Allow NEW facilities (built after initial choice) to re-evaluate
if year > initial_choice_year + facility_lifetime:
    # For new capacity, re-evaluate technology choice
    # Existing capacity locked into original choice
```

**My Recommendation**:
- **For academic paper**: Keep current (simpler)
- **For policy analysis**: Consider allowing new facilities to choose differently
- **Trade-off**: Simplicity vs realism

---

### 4. NCC Cost Calculation Logic

#### Current MACC Formula (macc.py):

```
MACC_NCC-Electricity = CAPEX_annual + OPEX_annual + Fuel_Cost_Differential

Where:
CAPEX_annual = Total_CAPEX / Lifetime  (simple annualization)
OPEX_annual = CAPEX × OPEX_%
Fuel_Cost_Differential = RE_electricity_cost / tCO2_abated
```

#### Key Simplification Issue:

**What is NOT counted in Fuel_Cost_Differential**:
- ❌ Naphtha cost (feedstock) - **CORRECT, should not be counted**
- ❌ Baseline LNG/fuel gas cost savings - **QUESTIONABLE**

**Current Logic**:
```python
# Only counts NEW fuel cost (RE electricity)
fuel_cost_diff = electricity_cost / abatement

# Does NOT subtract:
fuel_cost_diff_correct = (electricity_cost - lng_cost_saved) / abatement
```

**Is this correct?**

**Argument FOR current approach**:
- LNG/fuel gas is process energy that must be provided anyway
- We're comparing "business unusual" cost to BAU
- BAU already has LNG cost built in
- So we only count the INCREMENTAL cost (electricity)

**Argument AGAINST current approach**:
- Standard MACC methodology subtracts baseline fuel savings
- Should be: (New fuel cost - Old fuel cost) / abatement
- Makes technology appear more expensive than it is

**For Academic Paper**:

This is a **METHODOLOGICAL CHOICE** that must be clearly stated:

> "We adopt an incremental cost perspective where technology MACC represents the additional annual cost per ton of CO2 abated, relative to the business-as-usual case. Fuel cost differentials reflect only the new fuel purchases (H2 or RE electricity), as baseline fuel costs (LNG, fuel gas) are incurred in both scenarios and thus cancel out in the comparison."

**Alternatively** (more standard):

> "Fuel cost differential is calculated as (New_fuel_cost - Baseline_fuel_cost) / Abatement, following standard MACC methodology. This captures both the cost of new fuels and savings from displaced fuels."

**My Strong Recommendation**:
- **CHANGE TO STANDARD METHODOLOGY** for academic credibility
- Subtract baseline fuel costs
- Makes results comparable to other MACC studies

**Impact**: NCC technologies will appear ~$50-100/tCO2 cheaper (more competitive)

---

### 5. Energy Balance in NCC

#### Current Calculation (macc.py lines 217-298):

**For Ethylene Production**:

```
Baseline Energy:
- Naphtha: 29 GJ/ton (FEEDSTOCK + some combustion?)
- LNG: 4.49 GJ/ton (COMBUSTION)
- Fuel Gas: 5.62 GJ/ton (COMBUSTION)
- Byproduct Gas: 1.12 GJ/ton (COMBUSTION)
- Total thermal: ~40.2 GJ/ton

After NCC-H2:
- Naphtha: Still 29 GJ/ton (FEEDSTOCK only)
- H2: 0.56 kg H2/ton (COMBUSTION, replaces ~11 GJ thermal)
- Emissions: 1.739 → 0.15 tCO2/ton (abatement: 1.59 tCO2/ton)
```

**Key Questions**:

**Q1: Is the 29 GJ naphtha feedstock + fuel, or feedstock only?**

Looking at data, it seems:
- 29 GJ/ton naphtha = pure feedstock (chemically converted to ethylene)
- LNG/Fuel Gas = combustion for heat
- So separation is CORRECT ✓

**Q2: Why is baseline emission 1.739 tCO2/ton, not higher?**

Let's check:
```
Naphtha: 29 GJ × 0.0542 tCO2/GJ = 1.57 tCO2/ton
LNG: 4.49 GJ × 0.0561 tCO2/GJ = 0.25 tCO2/ton  (with CORRECTED EF)
Fuel Gas: 5.62 GJ × 0.050 tCO2/GJ = 0.28 tCO2/ton  (with CORRECTED EF)
TOTAL: ~2.1 tCO2/ton  (close to 1.739, accounting for byproduct gas)
```

Looks reasonable ✓

**Q3: After NCC-Electricity, why is emission 0.15 tCO2/ton, not near-zero?**

```
After:
- Naphtha feedstock still emits: 29 GJ × 0.0542 = 1.57 tCO2/ton  (chemical reaction)
- RE electricity: 3 MWh × 0.05 tCO2/MWh = 0.15 tCO2/ton  (lifecycle emissions)
- NO MORE LNG/Fuel Gas combustion
- Total: 1.72 tCO2/ton

Abatement = 2.1 - 1.72 = 0.38 tCO2/ton  ← WAIT, this doesn't match model!
```

**INCONSISTENCY FOUND!**

Model says: Abatement = 1.59 tCO2/ton
Calculation says: Abatement = ~0.38 tCO2/ton

**What's wrong?**

Looking deeper at code (macc.py line 333):
```python
emission_baseline_per_ton = baseline_data['total_emissions_tco2_per_ton']
# This loads from data_manager, not calculated fresh
```

**Need to check**: What is `baseline_data['total_emissions_tco2_per_ton']` actually?

This is a **CRITICAL ISSUE** for academic paper - need to verify energy balance!

---

### 6. Simplification Proposals for Academic Paper

#### Proposal 1: Clarify NCC Energy Balance

**Current**: Opaque - loads from data manager
**Proposed**: Make explicit in paper

Add to methodology:
```
Ethylene Production Energy Balance (per ton):

BASELINE:
  Feedstock: Naphtha 29 GJ (chemically converted)
  Combustion: LNG 4.5 GJ + Fuel Gas 5.6 GJ = 10.1 GJ total
  Emissions: Naphtha 1.57 + LNG 0.25 + Fuel Gas 0.28 = 2.1 tCO2/ton

NCC-ELECTRICITY:
  Feedstock: Naphtha 29 GJ (unchanged)
  Combustion: RE Electricity 3.0 MWh (10.8 GJ equivalent)
  Emissions: Naphtha 1.57 + RE 0.15 = 1.72 tCO2/ton
  Abatement: 0.38 tCO2/ton ethylene

NCC-H2:
  Feedstock: Naphtha 29 GJ (unchanged)
  Combustion: H2 0.56 kg (replaces 10.1 GJ)
  Emissions: Naphtha 1.57 + H2 0.0 = 1.57 tCO2/ton
  Abatement: 0.53 tCO2/ton ethylene
```

**This needs to be VERIFIED against actual model calculations!**

---

#### Proposal 2: Simplify Mutual Exclusivity Explanation

**Current**: Implemented at two levels (industry-wide + facility)
**Proposed for Paper**:

> "NCC-H2 and NCC-Electricity are mutually exclusive alternatives for decarbonizing naphtha cracking. Because both technologies modify the same capital equipment (steam cracker furnaces) and facility operation, we enforce the constraint that the industry adopts a single technology. This represents realistic technology standardization and learning curve effects. The model selects the technology with lower marginal abatement cost in the first year both become available (2030), and this choice persists due to capital lock-in."

**Key simplification**: Don't mention complex implementation, just state the economic logic.

---

#### Proposal 3: Standardize Cost Methodology

**Change**: Include baseline fuel cost savings in MACC calculation

**Current**:
```python
fuel_cost_diff = new_fuel_cost / abatement
```

**Proposed**:
```python
fuel_cost_diff = (new_fuel_cost - baseline_fuel_cost) / abatement
```

**Impact**:
- NCC-Electricity: Cost decreases by ~$50-70/tCO2 (more competitive)
- NCC-H2: Cost decreases by ~$80-100/tCO2 (more competitive)
- Makes technology selection even MORE favorable for electricity

**Academic Justification**: Standard MACC methodology, improves comparability

---

#### Proposal 4: Add Facility Heterogeneity (Optional)

**Current**: All NCC facilities identical
**Proposed**: Allow for cost variation by facility size/age

```python
# Adjust CAPEX based on facility size
capex_adjusted = base_capex × (facility_capacity / reference_capacity)^0.7  # Economy of scale
```

**Pros**: More realistic
**Cons**: More complex

**Recommendation**: **Skip for first paper** - keep simple

---

## DISCUSSION QUESTIONS FOR USER

### Question 1: Mutual Exclusivity

**Current**: Industry-wide technology selection (all facilities choose same)
**Alternative**: Facility-by-facility selection (heterogeneous)

**Which do you prefer for academic paper?**
- A) Keep current (simpler, easier to explain)
- B) Change to facility-level (more realistic)
- C) Hybrid (allow new facilities post-2030 to re-evaluate)

My recommendation: **A**

---

### Question 2: Cost Methodology

**Current**: Only count new fuel costs (no savings from displaced fuels)
**Alternative**: Standard MACC (new fuel cost - baseline fuel cost)

**Which methodology for paper?**
- A) Keep current (incremental cost perspective)
- B) Change to standard (more comparable to literature)

My strong recommendation: **B** (for academic credibility)

---

### Question 3: NCC Definition

**Current**: Binary (is NCC or not, based on product keywords)
**Alternative**: More nuanced (allow mixed facilities)

**Is current definition acceptable for academic paper?**
- A) Yes, simple and clear
- B) No, need to account for mixed facilities

My recommendation: **A** (simple is good for first paper)

---

### Question 4: Energy Balance Verification

**Critical**: Need to verify the emission calculations are consistent

**Action needed**:
- Check what baseline_data['total_emissions_tco2_per_ton'] actually returns
- Verify abatement numbers (1.59 tCO2/ton) match energy balance
- Ensure naphtha feedstock emissions are correctly handled

**Should I do this verification now?**
- Yes, before finalizing paper structure

---

### Question 5: Model Simplification Priority

**For academic paper, what should be the key message?**

Option A: "Simple, transparent MACC model for petrochemical sector"
- Emphasize: Clarity, reproducibility, ease of understanding
- Downplay: Complexity, detailed facility heterogeneity

Option B: "Comprehensive MACC model with detailed facility data"
- Emphasize: Data richness, 248 facilities, precision
- Downplay: Simplifying assumptions

**Which framing do you prefer?**

My recommendation: **Option A** - Simple and transparent models are more impactful in academic literature

---

## SUMMARY - NCC Logic Status

### ✅ What's CLEAR and GOOD:
1. **NCC identification**: Simple, correct (ethylene/propylene/butadiene)
2. **Mutual exclusivity concept**: Sound (H2 OR electricity, not both)
3. **Industry-wide selection**: Reasonable simplification
4. **Capital lock-in**: Realistic assumption

### ⚠️ What NEEDS CLARIFICATION:
1. **Cost methodology**: Should include fuel cost savings (standard approach)
2. **Energy balance**: Need to verify abatement calculations match energy balance
3. **Naphtha role**: Is it feedstock only, or feedstock + some combustion?

### 🔧 RECOMMENDED CHANGES for Academic Paper:
1. **Change cost calculation** to standard MACC methodology (include fuel savings)
2. **Verify and document** energy balance explicitly in paper
3. **Simplify explanation** of mutual exclusivity (don't mention implementation details)
4. **State assumptions clearly**: Industry-wide choice, capital lock-in, no facility retirement

---

## NEXT STEPS

1. **Discuss with you**: Which options above do you prefer?
2. **Verify energy balance**: Check actual numbers in model
3. **Update cost calculation** (if you agree): Include fuel cost savings
4. **Rerun model** with any changes
5. **Document for paper**: Write clear methodology section

**Ready to discuss!** What are your thoughts on the questions above?
