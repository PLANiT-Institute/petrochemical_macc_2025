#!/usr/bin/env python3
"""Test H2 consumption calculation"""

import pandas as pd

# Read MACC data
macc_df = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_02_macc/macc_annual_2025_2050.csv')

# Get 2050 NCC-H2 data
macc_2050 = macc_df[macc_df['year'] == 2050]
macc_ncc_h2 = macc_2050[macc_2050['technology'] == 'NCC-H2'].iloc[0]

print("=== MACC Data for NCC-H2 in 2050 ===")
print(f"H2 consumption (ton/ton ethylene): {macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']}")
print(f"Baseline tCO2/ton ethylene: {macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']}")

# Read deployment data
summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')
shaheen_h2 = summary[summary['scenario_id'] == 'shaheen_ncc_h2'].iloc[0]

deployed_mt = shaheen_h2['ncc_h2_mt']
print(f"\n=== Deployment (from summary.csv) ===")
print(f"NCC-H2 deployed (MtCO2): {deployed_mt}")

# Calculate H2 consumption
h2_ton_per_ton_ethylene = macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']
baseline_tco2_per_ton_ethylene = macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']

# Convert: deployed MtCO2 → Mt ethylene → kt H2
# 1 MtCO2 abated = (1e6 tCO2) / (baseline_tco2_per_ton_ethylene) = tons ethylene
# tons ethylene * h2_ton_per_ton_ethylene = tons H2 → / 1000 = kt H2
h2_consumption_kt = deployed_mt * (1e6 / baseline_tco2_per_ton_ethylene) * h2_ton_per_ton_ethylene / 1000

print(f"\n=== Calculated H2 Consumption ===")
print(f"Expected H2 (kt): {h2_consumption_kt:.2f}")
print(f"Actual H2 (kt) from summary: {shaheen_h2['h2_consumption_kt']:.2f}")
print(f"Ratio: {shaheen_h2['h2_consumption_kt'] / h2_consumption_kt:.3f}")

# Calculate what the old parameter would give
old_h2_param = 0.2
expected_with_old = deployed_mt * (1e6 / baseline_tco2_per_ton_ethylene) * old_h2_param / 1000
print(f"\n=== If using old 0.2 parameter ===")
print(f"Expected H2 (kt): {expected_with_old:.2f}")
print(f"Ratio to actual: {shaheen_h2['h2_consumption_kt'] / expected_with_old:.3f}")
