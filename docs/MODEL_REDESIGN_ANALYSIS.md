# MODEL REDESIGN ANALYSIS
## Critical Logic Flaw Identified: 2025-10-28

## 1. PROBLEM STATEMENT

### Current Model Behavior
The optimization model deploys BOTH NCC-H2 and NCC-Electricity simultaneously:
- 2050 NCC-H2 deployment: 23.03 MtCO2 abatement
- 2050 NCC-Electricity deployment: 24.48 MtCO2 abatement
- **Total NCC abatement: 47.51 MtCO2**

### Why This Is Wrong
**NCC-H2 and NCC-Electricity are mutually exclusive alternatives.**

Both technologies replace the SAME emission source:
- Baseline: Naphtha cracking with LNG/Fuel Gas combustion for furnace heating
- NCC-H2: Replace LNG/Fuel Gas with hydrogen combustion
- NCC-Electricity: Replace LNG/Fuel Gas with electric heating

**You cannot replace the same furnace fuel with BOTH hydrogen AND electricity!**

### Physical Reality
A naphtha cracker facility must choose ONE of three options:
1. Status Quo (baseline): LNG/Fuel Gas combustion
2. Convert to hydrogen-fired furnaces (NCC-H2)
3. Convert to electric furnaces (NCC-Electricity)

**Options 2 and 3 cannot coexist in the same facility.**

## 2. ROOT CAUSE ANALYSIS

### Where the Bug Occurs

#### A. MACC Calculation (macc.py)
```python
# Line 244: NCC-H2 potential
ethylene_production_kt = ncc_facilities[ncc_facilities['product'] == 'Ethylene']['capacity_kt'].sum()
abatement_mt = (ethylene_production_kt * 1000 * abatement_per_ton) / 1e6

# Line 327: NCC-Electricity potential  
ethylene_production_kt = ncc_facilities[ncc_facilities['product'] == 'Ethylene']['capacity_kt'].sum()
abatement_mt = (ethylene_production_kt * 1000 * abatement_per_ton) / 1e6
```

**Issue**: Both use the SAME ethylene production as the base. This is correct for CALCULATING the potential of each technology, but the optimization should recognize they are alternatives.

#### B. Optimization (optimization.py)
```python
# Lines 156-179: Deploy technologies in cost order
for _, tech in tech_year.iterrows():
    if remaining <= 0:
        break
    additional_deploy = min(remaining, tech['abatement_potential_mtco2'] - deployed[tech['technology']])
    if additional_deploy > 0:
        deployed[tech['technology']] += additional_deploy
        remaining -= additional_deploy
```

**Issue**: Treats all 4 technologies as independent. No constraint preventing simultaneous NCC-H2 and NCC-Electricity deployment.

#### C. Facility Allocation (optimization.py)
```python
# Lines 448-478: Allocate NCC-H2 and NCC-Electricity independently
df_facilities['abatement_mt'] += df_facilities['ncc_h2_abatement_mt']    # Line 462
df_facilities['abatement_mt'] += df_facilities['ncc_elec_abatement_mt']  # Line 478
```

**Issue**: Adds both abatements to the same facilities, resulting in >100% abatement and negative emissions.

## 3. IMPACT ASSESSMENT

### Overestimated Metrics
| Metric | Current (Wrong) | Corrected (Estimate) | Overestimation |
|--------|----------------|---------------------|----------------|
| Total Abatement 2050 | 56.99 Mt | ~33 Mt | 73% |
| NCC Abatement 2050 | 47.51 Mt | ~24.5 Mt | 94% |
| Total Investment | $47.9 B | ~$26 B | 84% |
| H2 Consumption | 12.9 kt/year | ~6.5 kt/year | 98% |
| Electricity Increase | 129.8 TWh | ~70 TWh | 85% |

### Facility-Level Consequences
- Abatement percentages >100% (e.g., 233% for Lotte Chemical Daesan)
- Negative 2050 emissions (e.g., -323 kt for facility #1)
- Physically impossible results

## 4. CORRECT MODEL LOGIC

### Technology Relationships

```
All Facilities (248)
│
├─ NCC Facilities (~40)
│  │
│  ├─ Option A: NCC-H2 (hydrogen furnaces)
│  ├─ Option B: NCC-Electricity (electric furnaces)  
│  └─ Option C: Status Quo (baseline)
│  │
│  └─ MUTUALLY EXCLUSIVE: Choose ONE option per facility
│
└─ Non-NCC Facilities (~208)
   └─ Heat Pump (for low-temperature heat)

All Facilities
└─ RE PPA (renewable electricity, independent of furnace choice)
```

### Key Principles
1. **NCC Technologies are Alternatives**: A facility deploys NCC-H2 OR NCC-Electricity, never both
2. **Technology Selection**: Choose the lower-cost alternative in each year
3. **Irreversibility**: Once a choice is made (H2 or Electricity), it persists due to capital lock-in
4. **Independent Technologies**: Heat Pump (non-NCC) and RE PPA (electricity source) are independent

## 5. REDESIGN APPROACH

### Step 1: MACC Calculation (No Change Needed)
- Continue calculating separate MACC curves for NCC-H2 and NCC-Electricity
- Both use same abatement potential (correct for comparison)
- Cost comparison determines which is economically preferred

### Step 2: Optimization Logic (Major Change Required)
```python
# For each year:
1. Get available technologies and costs
2. Rank by cost: [Heat_Pump, RE_PPA, NCC-H2, NCC-Electricity]
3. **NEW**: Identify best NCC option:
   - Compare NCC-H2 cost vs NCC-Electricity cost
   - Select cheaper one as "NCC_Preferred"
   - Set abatement potential of other to 0 for this deployment round
4. Deploy technologies considering:
   - Heat_Pump: non-NCC facilities only
   - RE_PPA: all facilities (electricity source)
   - NCC_Preferred: NCC facilities only
5. Track deployed NCC technology choice (irreversible)
```

### Step 3: Facility Allocation (Major Change Required)
```python
# For each facility:
if facility is NCC:
    if NCC-H2 was deployed:
        allocate NCC-H2 proportionally
    elif NCC-Electricity was deployed:
        allocate NCC-Electricity proportionally
    # Never allocate both!
else:
    allocate Heat_Pump if deployed
    
# All facilities:
allocate RE_PPA if deployed (independent)

# Calculate final emissions:
emissions_2050 = baseline - sum(abatements)
assert emissions_2050 >= 0  # Must be non-negative!
```

## 6. IMPLEMENTATION PLAN

### Phase 1: Create Corrected Versions
- Create `macc_v2.py` with NCC alternative logic
- Create `optimization_v2.py` with mutual exclusivity
- Create new allocation function

### Phase 2: Validation
- Run corrected model on Policy Target scenario
- Verify no negative emissions
- Verify abatement percentages ≤100%
- Check cost reasonableness

### Phase 3: Comparison
- Generate side-by-side comparison: old vs new
- Document all changes in metrics
- Update Word/LaTeX reports

### Phase 4: Full Re-run
- Re-run all scenarios with corrected model
- Update all outputs
- Regenerate visualizations

## 7. EXPECTED CORRECTED RESULTS (Preliminary Estimates)

### Policy Target 2050
- Total Abatement: ~33 Mt (vs 57 Mt currently)
- NCC Technology: Either 24.5 Mt H2 OR 24.5 Mt Elec (not both)
- Investment: ~$26 B (vs $47.9 B currently)
- 2050 Emissions: ~19 Mt (vs 5.2 Mt currently)

**Note**: May not achieve 90% reduction target with corrected model. Policy targets may need adjustment.

---
**Status**: Analysis Complete
**Next**: Begin implementation of corrected model
