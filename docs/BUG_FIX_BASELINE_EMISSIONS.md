# Critical Bug Fix: Baseline Emissions Calculation

**Date**: 2025-11-11
**Status**: ✅ FIXED
**Severity**: CRITICAL - 1000x calculation error

---

## Summary

Found and fixed a critical bug in `modules/macc.py` that was causing H₂ consumption to appear correct even though a different bug was present.

---

## The Bug

### Location
`modules/macc.py` lines 256 and 345 (NCC-H₂ and NCC-Electricity)

### Incorrect Code
```python
emission_baseline_per_ton = (total_emissions_kt / total_capacity_kt) * 1000  # tCO2/ton
```

### Problem
- `total_emissions_kt` = emissions in kilotons (kt)
- `total_capacity_kt` = capacity in kilotons (kt)
- Ratio: `kt / kt` = already in `tCO2/ton` units
- **Multiplying by 1000 creates a 1000x error!**

### Actual Values
- **CORRECT**: 2.26 tCO2/ton ethylene
- **WRONG** (before fix): 2,256.65 tCO2/ton ethylene (1000x too high!)

---

## Impact on H₂ Consumption

### The Canceling Bug Effect

Two bugs were canceling each other out:

1. **Bug #1**: H₂ parameter updated from 0.2 → 0.56 ton/ton (+180%)
2. **Bug #2**: Baseline emissions 1000x too high (2.26 → 2256.65)

**Result**:
```
H₂ = deployed_MtCO2 × (1 / baseline_tCO2_per_ton) × h2_ton_per_ton

BEFORE FIX:
H₂ = 56.27 MtCO2 × (1 / 2256.65) × 0.56 = 13.96 kt H₂

AFTER FIX:
H₂ = 56.27 MtCO2 × (1 / 2.26) × 0.56 = 13,964 kt H₂
```

**The baseline bug divided by 1000, canceling out the H₂ parameter increase!**

---

## Correct Calculation

### Shaheen + NCC-H₂ Scenario

**Deployment**: 56.27 MtCO2 abated

**Step 1: Convert to ethylene production**
```
Ethylene = 56.27e6 tCO2 / 2.26 tCO2/ton = 24,935 kt ethylene
```

**Step 2: Calculate H₂ consumption**
```
H₂ = 24,935 kt ethylene × 0.56 ton H₂/ton ethylene = 13,964 kt H₂
```

**Expected Results**:
- **Shaheen + NCC-H₂**: ~14,000 kt H₂/year (~88 kt cumulative)
- **25% + NCC-H₂**: ~9,800 kt H₂/year (~61 kt cumulative)
- **40% + NCC-H₂**: ~8,400 kt H₂/year (~53 kt cumulative)

---

## Fix Applied

### Corrected Code
```python
# Both in kt, so ratio gives tCO2/ton directly (no need to multiply by 1000!)
emission_baseline_per_ton = total_emissions_kt / total_capacity_kt  # tCO2/ton
```

### Files Modified
1. `modules/macc.py` - Fixed baseline emissions calculation (2 occurrences)

---

## Verification

Run test script:
```bash
python test_baseline_calc.py
```

Expected output:
```
CORRECT baseline (tCO2/ton ethylene): 2.26
Expected H2 with CORRECT baseline: 13963.72 kt H2
```

---

## Next Steps

1. ✅ Fix applied to `modules/macc.py`
2. 🔄 Re-running all 6 scenarios with correct calculation
3. ⏳ Verify H₂ consumption ~14,000 kt/yr (Shaheen scenario)
4. ⏳ Update comparison reports with ACTUAL corrected results
5. ⏳ Proceed with paper draft

---

## Lesson Learned

**Always check unit conversions!**

When both numerator and denominator are in the same unit (kt/kt), the ratio already gives the desired unit without additional conversion factors.

---

**Status**: 🔄 Scenarios re-running with corrected baseline emissions calculation...
