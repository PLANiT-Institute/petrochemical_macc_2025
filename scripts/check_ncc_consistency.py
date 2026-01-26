#!/usr/bin/env python3
"""
NCC Naphtha Logic Consistency Checker

Verifies that all code locations handling NCC/naphtha fuel savings
have the correct exclusion logic.

Usage:
    python scripts/check_ncc_consistency.py

Exit codes:
    0 = All checks passed
    1 = One or more checks failed
"""

import re
import sys
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
            'pattern': r"is_ncc = facility_baseline\.get\('is_ncc'.*\).*\n.*if not is_ncc:",
            'description': 'run_scenarios.py checks is_ncc before naphtha savings'
        },
    ]

    all_passed = True
    print("=" * 60)
    print("NCC Naphtha Logic Consistency Check")
    print("=" * 60)
    print()

    for check in checks:
        if not check['file'].exists():
            print(f"[SKIP] {check['file'].name}: File not found")
            continue

        content = check['file'].read_text()
        if re.search(check['pattern'], content, re.MULTILINE):
            print(f"[PASS] {check['file'].name}")
            print(f"       {check['description']}")
        else:
            print(f"[FAIL] {check['file'].name}")
            print(f"       MISSING: {check['description']}")
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("RESULT: All checks PASSED")
        print("NCC naphtha exclusion logic is consistent across codebase")
    else:
        print("RESULT: FAILED")
        print("NCC logic is INCONSISTENT - review the failing files")
        print()
        print("See docs/NCC_NAPHTHA_LOGIC.md for the correct implementation")
    print("=" * 60)

    return all_passed


def check_test_coverage():
    """Verify the integration test exists."""
    root = Path(__file__).parent.parent
    test_file = root / 'tests' / 'test_integration.py'

    if not test_file.exists():
        print("[WARN] tests/test_integration.py not found")
        return False

    content = test_file.read_text()
    if 'TestFuelSavingsConsistency' in content:
        print("[INFO] TestFuelSavingsConsistency class found in test_integration.py")
        return True
    else:
        print("[WARN] TestFuelSavingsConsistency class not found in test_integration.py")
        return False


if __name__ == '__main__':
    print()
    passed = check_ncc_logic()
    print()
    check_test_coverage()
    print()

    sys.exit(0 if passed else 1)
