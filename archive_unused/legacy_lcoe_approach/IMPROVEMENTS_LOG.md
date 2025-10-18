# Model Improvements Log
**Date:** 2025-10-11
**Version:** 2.2

## Issues Identified and Fixed

### Issue #1: NCC Technologies Double-Counting ✅ FIXED
**Problem:**
- NCC-H2 and NCC-Electricity both showed 37.60 MtCO2 abatement potential
- This made total abatement 86 MtCO2 > baseline 52 MtCO2

**Root Cause:**
- Both technologies target the same naphtha cracker facilities
- They are **mutually exclusive** - one facility can only choose ONE technology

**Fix Applied:**
- Added clear documentation in code explaining mutual exclusivity
- Added interpretation box in dashboard showing:
  - "NCC Technologies (choose one): 37.60 MtCO2"
  - "Maximum Realistic Abatement: 49.84 MtCO2"
  - Warning note about mutual exclusivity

**Technical Note:**
- This is standard MACC practice - show maximum potential for each option
- Optimizer correctly chooses only one per facility based on cost

---

### Issue #2: Heat Pump Only Targeted Naphtha ✅ FIXED
**Problem:**
- Heat Pump abatement was only 3.89 MtCO2
- Only counted naphtha combustion emissions
- Ignored LNG, fuel gas, and other fossil fuels

**Root Cause:**
- Code line 109 only summed `emissions_naphtha_kt`
- Did not include other fossil fuel columns

**Fix Applied:**
- Modified `_calculate_heat_pump_macc()` to sum ALL fossil fuel emissions:
  ```python
  fossil_emissions = (
      emissions_naphtha_kt +
      emissions_lng_kt +
      emissions_fuel_gas_kt +
      emissions_lpg_kt +
      emissions_fuel_oil_kt +
      emissions_diesel_kt
  )
  ```

**Result:**
- Heat Pump abatement: 3.89 → **5.11 MtCO2** (+31%)
- Now correctly captures all combustion heat that can be replaced

---

### Issue #3: Clarity on Cost Components ✅ ADDRESSED
**Problem:**
- Users saw negative MACC costs and wondered if CAPEX was included
- Not clear that fuel savings exceed investment costs

**Fix Applied:**
- Added "MACC Cost Breakdown" section showing:
  - 🔴 CAPEX + OPEX (always positive)
  - 🟢 Fuel Cost Differential (savings)
  - 🔵 Total MACC Cost (net)

**Example (Heat Pump 2030):**
- CAPEX+OPEX: +$12.59/tCO2 ✅ Investment cost
- Fuel Savings: -$760.63/tCO2 ✅ Huge savings from not buying naphtha
- **Total: -$748/tCO2** = Net benefit!

---

## Current Model State (2030)

### Abatement Potentials
| Technology | Abatement (MtCO2) | Cost ($/tCO2) | Status |
|------------|-------------------|---------------|--------|
| Heat Pump | 5.11 | -748 | ✅ Cost-saving |
| RE PPA | 7.13 | -131 | ✅ Cost-saving |
| NCC-Electricity | 37.60 | -112 | ✅ Cost-saving |
| NCC-H2 | 37.60 | +18 | Small cost |

### Maximum Realistic Abatement
- **NCC (choose one):** 37.60 MtCO2
- **Other technologies:** 12.24 MtCO2
- **TOTAL:** 49.84 MtCO2
- **vs Baseline:** 52.00 MtCO2
- **Max Reduction:** 95.9%

### Technology Overlaps
✅ **No Overlaps:**
- Heat Pump → Fossil fuel combustion
- RE PPA → Grid electricity
- NCC → Naphtha cracker transformation

⚠️ **Mutual Exclusivity:**
- NCC-H2 vs NCC-Electricity → Same facilities, different tech paths

---

## Validation Checks

### ✅ Energy Balance
- Total baseline: 52.00 MtCO2
- Max abatement: 49.84 MtCO2 (95.9%)
- Remaining: 2.16 MtCO2 (non-abatable or infeasible)

### ✅ Cost Components
- All CAPEX properly annualized (CRF at 8%)
- OPEX calculated as % of CAPEX
- Fuel differentials use actual price trajectories

### ✅ Time Dynamics
- RE PPA abatement decreases (grid decarbonizes)
- H2 cost decreases ($6/kg → $1.2/kg)
- RE price decreases ($58/MWh → $32/MWh)

---

## Next Steps (If Needed)

### Optional Improvements
1. **Sensitivity Analysis:** Test different fuel price scenarios
2. **Learning Curves:** Add technology cost reductions from deployment
3. **Regional Constraints:** Model grid capacity limitations
4. **Phasing:** Add realistic deployment rate constraints

### Documentation
1. Update MACC_METHODOLOGY_ACADEMIC.md with fixes
2. Add validation section to README
3. Create user guide for dashboard

