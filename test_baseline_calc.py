#!/usr/bin/env python3
"""Test baseline emissions calculation"""

import pandas as pd

# Read baseline data
baseline = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_01_baseline/baseline_2025_detailed.csv')

# Filter to ethylene NCC facilities (product is Ethylene)
ethylene_ncc = baseline[baseline['product'] == 'Ethylene']

print(f"=== Ethylene NCC Facilities ===")
print(f"Number of facilities: {len(ethylene_ncc)}")

total_emissions_kt = ethylene_ncc['total_emissions_kt'].sum()
total_capacity_kt = ethylene_ncc['capacity_kt'].sum()

print(f"\nTotal emissions (kt CO2): {total_emissions_kt:.2f}")
print(f"Total capacity (kt ethylene): {total_capacity_kt:.2f}")

# CORRECT calculation
emission_per_ton_correct = (total_emissions_kt / total_capacity_kt)  # Already in tCO2/ton since both in kt
print(f"\nCORRECT baseline (tCO2/ton ethylene): {emission_per_ton_correct:.2f}")

# WRONG calculation (what the code does)
emission_per_ton_wrong = (total_emissions_kt / total_capacity_kt) * 1000
print(f"WRONG baseline (current code): {emission_per_ton_wrong:.2f}")

print(f"\nExpected H2 with CORRECT baseline:")
print(f"  56.27 MtCO2 / {emission_per_ton_correct:.2f} tCO2/ton = {56.27e6 / emission_per_ton_correct / 1000:.2f} kt ethylene")
print(f"  {56.27e6 / emission_per_ton_correct / 1000:.2f} kt ethylene × 0.56 ton H2/ton ethylene = {56.27e6 / emission_per_ton_correct / 1000 * 0.56:.2f} kt H2")

print(f"\nExpected H2 with WRONG baseline:")
print(f"  56.27 MtCO2 / {emission_per_ton_wrong:.2f} tCO2/ton = {56.27e6 / emission_per_ton_wrong / 1000:.2f} kt ethylene")
print(f"  {56.27e6 / emission_per_ton_wrong / 1000:.2f} kt ethylene × 0.56 ton H2/ton ethylene = {56.27e6 / emission_per_ton_wrong / 1000 * 0.56:.2f} kt H2")
