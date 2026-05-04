# Archived Results: NCC Naphtha Fuel Savings Bug

**Archive Date**: 2025-01-26
**Status**: INVALID - Do not use these results

---

## What Was Wrong

These results contain **incorrect MAC (Marginal Abatement Cost) calculations** for NCC (Naphtha Cracker) facilities due to a missing check in `run_scenarios.py`.

### The Bug

In `run_scenarios.py`, the fuel savings calculation was **missing the `is_ncc` check**:

```python
# BUGGY CODE (before fix):
fuel_savings += energy_by_source.get('naphtha', 0) * fuel_prices.get('naphtha_usd_per_gj', 0)
# LNG
fuel_savings += energy_by_source.get('lng', 0) * fuel_prices.get('lng_usd_per_gj', 0)
# ... etc
```

This incorrectly counted naphtha feedstock as "fuel savings" for NCC facilities.

### The Fix

```python
# FIXED CODE:
is_ncc = facility_baseline.get('is_ncc', False) or process == 'Naphtha Cracker'
if not is_ncc:
    fuel_savings += energy_by_source.get('naphtha', 0) * fuel_prices.get('naphtha_usd_per_gj', 0)
# LNG (always saved)
fuel_savings += energy_by_source.get('lng', 0) * fuel_prices.get('lng_usd_per_gj', 0)
```

---

## Impact

### Affected Scenarios
- All scenarios with NCC technologies: `*_ncc_h2` and `*_ncc_elec`

### Affected Metrics
| Metric | Bug Effect |
|--------|------------|
| `fuel_savings_usd` | **Massively inflated** (~$435M/yr per large NCC) |
| `mac_usd_per_tco2` | **Artificially negative** (showed profit instead of cost) |
| `total_cost_usd` | **Too low** |

### Example Error

For a 1 Mt/yr NCC facility:
- **Buggy result**: `fuel_savings_usd` = $435M/yr (included $315M from naphtha)
- **Correct result**: `fuel_savings_usd` = ~$120M/yr (LNG/LPG only)
- **MAC Error**: Could show -$50/tCO2 instead of +$200/tCO2

---

## Root Cause

**Code Duplication**: `run_scenarios.py` duplicated fuel savings logic that was already correctly implemented in `modules/capex_calculator.py`. The duplicate missed the NCC exclusion check.

See `docs/NCC_NAPHTHA_LOGIC.md` for the full Single Source of Truth documentation.

---

## Files in This Archive

| File | Description |
|------|-------------|
| `scenario_results.csv` | Combined results (BUGGY) |
| `shaheen_ncc_*.csv` | Shaheen scenario outputs (BUGGY MAC for NCC) |
| `restructure_*_ncc_*.csv` | Restructure scenario outputs (BUGGY MAC for NCC) |
| `regional_*.csv` | Aggregated results (BUGGY) |
| `stranded_assets_*.csv` | May be affected by incorrect economics |
| `emissions_by_*.csv` | Emission totals (likely correct, but verify) |

---

## Corrective Actions

1. **Fixed** `run_scenarios.py` line 200-206 to include `is_ncc` check
2. **Created** `docs/NCC_NAPHTHA_LOGIC.md` as Single Source of Truth
3. **Added** integration test to prevent future inconsistencies
4. **Re-run** `python3 run_scenarios.py` to generate correct results

---

## Verification

After regenerating results, verify with:

```bash
# Check that NCC-Electricity facilities have POSITIVE MAC (not negative)
python3 -c "
import pandas as pd
df = pd.read_csv('outputs/scenario_results.csv')
ncc_elec = df[(df['technology'] == 'NCC-Electricity') & (df['tech_deployed'] == 1)]
print('NCC-Electricity MAC stats:')
print(ncc_elec['mac_usd_per_tco2'].describe())
# All MAC values should be positive
assert (ncc_elec['mac_usd_per_tco2'] > 0).all(), 'ERROR: Found negative MAC!'
print('PASS: All MAC values are positive')
"
```

---

## Prevention

- See `docs/NCC_NAPHTHA_LOGIC.md` for code locations to check
- Run `python -m pytest tests/test_integration.py::TestFuelSavingsConsistency -v`
- Use `scripts/check_ncc_consistency.py` verification script
