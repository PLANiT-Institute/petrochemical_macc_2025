#!/usr/bin/env python3
"""Test H2 calculation from MACC data"""

import pandas as pd

# Read MACC 2050 data
macc_df = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_02_macc/macc_annual_2025_2050.csv')
macc_2050 = macc_df[macc_df['year'] == 2050]
macc_ncc_h2 = macc_2050[macc_2050['technology'] == 'NCC-H2'].iloc[0]

print("=== MACC 2050 NCC-H2 Data ===")
print(f"H2 consumption (ton/ton C2H4): {macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']}")
print(f"Baseline emissions (tCO2/ton C2H4): {macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']}")
print(f"Ethylene production (kt): {macc_ncc_h2['ethylene_production_kt']}")

# Read summary
summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')
shaheen_h2 = summary[summary['scenario_id'] == 'shaheen_ncc_h2'].iloc[0]

deployed_mt = shaheen_h2['ncc_h2_mt']
h2_kt_from_summary = shaheen_h2['h2_consumption_kt']

print(f"\n=== Deployment from Summary ===")
print(f"NCC-H2 deployed (MtCO2): {deployed_mt}")
print(f"H2 consumption (kt) from summary: {h2_kt_from_summary}")

# Calculate H2 using optimization formula
h2_ton_per_ton = macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']
baseline_tco2_per_ton = macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']

h2_kt_calculated = deployed_mt * (1e6 / baseline_tco2_per_ton) * h2_ton_per_ton / 1000

print(f"\n=== Calculated H2 (using optimization formula) ===")
print(f"{deployed_mt} MtCO2 / {baseline_tco2_per_ton:.3f} tCO2/ton = {deployed_mt * 1e6 / baseline_tco2_per_ton / 1000:.2f} kt ethylene")
print(f"{deployed_mt * 1e6 / baseline_tco2_per_ton / 1000:.2f} kt × {h2_ton_per_ton} ton H2/ton = {h2_kt_calculated:.2f} kt H2")

print(f"\nExpected: {h2_kt_calculated:.2f} kt H2")
print(f"Actual from summary: {h2_kt_from_summary:.2f} kt H2")
print(f"Ratio: {h2_kt_from_summary / h2_kt_calculated:.3f}")

# Calculate from ethylene production in MACC
ethylene_kt_from_macc = macc_ncc_h2['ethylene_production_kt']
h2_from_ethylene = ethylene_kt_from_macc * h2_ton_per_ton

print(f"\n=== Direct from MACC ethylene production ===")
print(f"{ethylene_kt_from_macc:.2f} kt ethylene × {h2_ton_per_ton} ton H2/ton = {h2_from_ethylene:.2f} kt H2")
