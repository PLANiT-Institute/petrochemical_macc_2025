# NCC Naphtha Logic - Single Source of Truth

## Core Principle

In **Naphtha Cracker (NCC)** facilities, naphtha is **FEEDSTOCK** that is chemically cracked into products (ethylene, propylene, etc.), **NOT combustion fuel**.

Therefore:
- **NO fuel savings** from naphtha - it's still used as feedstock even with e-cracker or H2-cracker
- **NO naphtha combustion emissions** counted for NCC facilities
- Only **LNG, LPG, fuel gas, and byproduct gas** are actual heating fuels that can be saved

---

## Why This Matters

The ~29 GJ/t naphtha intensity represents **feedstock energy content**, not heating fuel. If this is incorrectly treated as fuel:

| Incorrect Treatment | Impact |
|---------------------|--------|
| Naphtha counted as fuel savings | **Massively inflated fuel savings** (29 GJ/t vs ~8 GJ/t actual fuels) |
| Results in **negative MAC** | Technologies appear to "pay for themselves" incorrectly |
| Wrong facility economics | Investment decisions based on false economics |

### Example Impact

For a 1 Mt/yr NCC facility with naphtha at $15/GJ:
- **Incorrect**: 29 GJ/t × 1,000,000 t × $15/GJ = **$435M/yr false savings**
- **Correct**: Only LNG/LPG savings (~8 GJ/t) = ~$120M/yr actual savings

---

## Code Locations (Must Stay Consistent)

### 1. `modules/capex_calculator.py` - MACCalculator._calculate_fuel_savings()

**Lines 385-424** - Central fuel savings calculation

```python
def _calculate_fuel_savings(self, facility_baseline, fuel_prices):
    """
    IMPORTANT: For NCC (Naphtha Cracker) facilities, naphtha is FEEDSTOCK that is
    cracked into products, NOT combustion fuel. Therefore, there are NO fuel savings
    from naphtha - it's still used as feedstock even with e-cracker or H2 cracker.
    """
    energy_by_source = facility_baseline.get('energy_by_source', {})
    is_ncc = facility_baseline.get('is_ncc', False)

    fuel_savings = 0.0

    for internal_key, price_key in fuel_mapping.items():
        # Skip naphtha for NCC - it's feedstock, not fuel
        if internal_key == 'naphtha' and is_ncc:
            continue

        energy_gj = energy_by_source.get(internal_key, 0)
        price = fuel_prices.get(price_key, 0)
        fuel_savings += energy_gj * price
```

### 2. `modules/utils.py` - EmissionCalculator.calculate_baseline_metrics()

**Lines 257-354** - Baseline calculation sets `is_ncc` flag and excludes naphtha from heat demand

```python
def calculate_baseline_metrics(self, facility_row, intensities_row, operating_rate, ...):
    """
    IMPORTANT: For NCC (Naphtha Cracker) facilities, naphtha is FEEDSTOCK (cracked into products),
    NOT combustion fuel. The 29 GJ/t naphtha represents feedstock energy content.
    Only LNG, LPG, and byproduct gas are actual heating fuels that produce emissions.
    """
    # Check if this is an NCC facility - naphtha is feedstock, not fuel
    is_ncc = process == 'Naphtha Cracker' if process else False

    # ... later in the function ...

    if is_ncc:
        # Naphtha is feedstock in NCC - no combustion emissions
        emissions_by_source['naphtha'] = 0.0
        # Exclude naphtha from heat demand (it's feedstock, not heating fuel)
        total_heat_gj -= energy_by_source['naphtha']

    return {
        # ...
        'is_ncc': is_ncc,  # Flag for downstream use
    }
```

### 3. `run_scenarios.py` - calculate_facility_mac_v2()

**Lines 200-219** - Fuel savings calculation (duplicated logic)

```python
# Naphtha - SKIP for NCC facilities (naphtha is feedstock, not fuel)
# In Naphtha Cracker facilities, naphtha is FEEDSTOCK that gets chemically transformed,
# not combustion fuel. Even with e-cracker or H2-cracker, naphtha is still required.
# See docs/ASSUMPTIONS_AND_METHODOLOGY.md for details.
is_ncc = facility_baseline.get('is_ncc', False) or process == 'Naphtha Cracker'
if not is_ncc:
    fuel_savings += energy_by_source.get('naphtha', 0) * fuel_prices.get('naphtha_usd_per_gj', 0)
```

---

## Verification Script

Run this Python snippet to check consistency across all files:

```python
#!/usr/bin/env python3
"""Verify NCC naphtha logic consistency across codebase."""

import re
from pathlib import Path

def check_ncc_logic():
    """Check all files have the NCC naphtha exclusion logic."""

    root = Path(__file__).parent.parent

    checks = [
        {
            'file': root / 'modules' / 'capex_calculator.py',
            'pattern': r"if internal_key == 'naphtha' and is_ncc:\s+continue",
            'description': 'MACCalculator._calculate_fuel_savings() has naphtha skip'
        },
        {
            'file': root / 'modules' / 'utils.py',
            'pattern': r"is_ncc = process == 'Naphtha Cracker'",
            'description': 'EmissionCalculator.calculate_baseline_metrics() sets is_ncc flag'
        },
        {
            'file': root / 'run_scenarios.py',
            'pattern': r"is_ncc = facility_baseline\.get\('is_ncc'.*\)\s+if not is_ncc:",
            'description': 'run_scenarios.py checks is_ncc before naphtha savings'
        },
    ]

    all_passed = True
    print("NCC Naphtha Logic Consistency Check")
    print("=" * 50)

    for check in checks:
        content = check['file'].read_text()
        if re.search(check['pattern'], content, re.MULTILINE):
            print(f"[PASS] {check['file'].name}: {check['description']}")
        else:
            print(f"[FAIL] {check['file'].name}: {check['description']}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All checks PASSED - NCC logic is consistent")
    else:
        print("FAILED - NCC logic is INCONSISTENT")
        print("Review the files and ensure all have the naphtha exclusion check")

    return all_passed

if __name__ == '__main__':
    import sys
    sys.exit(0 if check_ncc_logic() else 1)
```

Save as `scripts/check_ncc_consistency.py` and run:
```bash
python scripts/check_ncc_consistency.py
```

---

## Test Coverage

### Unit Test: `tests/test_calculators.py`

**Lines 443-474** - Tests MACCalculator correctly excludes naphtha for NCC

```python
def test_ncc_naphtha_not_in_fuel_savings(self, ...):
    """NCC naphtha should not contribute to fuel savings (it's feedstock)"""
    facility_baseline = {
        'energy_by_source': {
            'naphtha': 2_900_000,  # Large naphtha feedstock
            'lng': 100_000
        },
        'is_ncc': True,  # This is an NCC facility
    }

    result = mac_calc.calculate_mac(facility_baseline, 'NCC-H2', 2030, fuel_prices)

    # Fuel savings should NOT include naphtha (feedstock)
    # Only LNG should contribute to savings
    expected_lng_savings = 100_000 * 12.0
    assert result['fuel_savings_usd'] == pytest.approx(expected_lng_savings, rel=1e-3)
```

### Integration Test: `tests/test_integration.py`

**Class: TestFuelSavingsConsistency** - Verifies all calculation paths match

---

## Change History

| Date | Issue | Fix |
|------|-------|-----|
| 2025-01-26 | `run_scenarios.py` missing NCC check | Added `is_ncc` check at line 204 |
| 2025-01-26 | Buggy results archived | See `archive/buggy_results_2025_01_26/` |

---

## Related Documentation

- `docs/ASSUMPTIONS_AND_METHODOLOGY.md` - Full methodology explanation
- `docs/MODEL_FLOW.md` - Data flow through the model
- `data/assumptions/product_benchmarks.csv` - Energy intensity data
- `data/assumptions/emission_factors.csv` - Emission factors by fuel

---

## Quick Reference: Is It NCC?

| Product | Process | Is NCC? | Naphtha Treatment |
|---------|---------|---------|-------------------|
| Ethylene | Naphtha Cracker | **YES** | Feedstock (no fuel savings) |
| Propylene | Naphtha Cracker | **YES** | Feedstock (no fuel savings) |
| Butadiene | Naphtha Cracker | **YES** | Feedstock (no fuel savings) |
| Benzene | BTX Plant | NO | Fuel (count savings) |
| Toluene | BTX Plant | NO | Fuel (count savings) |
| Xylene | BTX Plant | NO | Fuel (count savings) |
| Any | Utility | NO | Fuel (count savings) |

---

## Maintainer Notes

When modifying fuel savings calculations:

1. **Always check `is_ncc` flag** before including naphtha
2. **Update ALL three locations** if changing the logic
3. **Run integration tests** to verify consistency:
   ```bash
   python -m pytest tests/test_integration.py::TestFuelSavingsConsistency -v
   ```
4. **Update this document** if adding new code locations
