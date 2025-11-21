#!/usr/bin/env python3
"""Calculate cumulative H2 consumption 2025-2050"""

import pandas as pd

# Read deployment data
deployment = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_03_optimization/policy_target_deployment.csv')

# Read MACC data
macc_df = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_02_macc/macc_annual_2025_2050.csv')

print("=== Annual H2 Consumption (Shaheen + NCC-H2) ===\n")
print(f"{'Year':<6} {'NCC-H2 Deployed':<20} {'H2 per ton':<12} {'Baseline':<12} {'H2 Consumption':<15}")
print(f"{'':6} {'(MtCO2)':<20} {'(ton/ton)':<12} {'(tCO2/ton)':<12} {'(kt H2/yr)':<15}")
print("-" * 85)

cumulative_h2 = 0

for _, row in deployment.iterrows():
    year = int(row['year'])
    ncc_h2_mt = row['NCC-H2']

    # Get MACC data for this year
    macc_year = macc_df[macc_df['year'] == year]
    macc_ncc_h2 = macc_year[macc_year['technology'] == 'NCC-H2'].iloc[0]

    h2_per_ton = macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']
    baseline_tco2 = macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']

    # Calculate H2
    h2_kt = ncc_h2_mt * (1e6 / baseline_tco2) * h2_per_ton / 1000

    cumulative_h2 += h2_kt

    if year % 5 == 0 or year == 2025:
        print(f"{year:<6} {ncc_h2_mt:>18.2f}  {h2_per_ton:>10.2f}  {baseline_tco2:>10.3f}  {h2_kt:>13.1f}")

print("=" * 85)
print(f"CUMULATIVE H2 CONSUMPTION (2025-2050): {cumulative_h2:.1f} kt H2")
print(f"AVERAGE ANNUAL H2 CONSUMPTION: {cumulative_h2 / 26:.1f} kt H2/year")
print(f"2050 ANNUAL H2 CONSUMPTION: {h2_kt:.1f} kt H2/year")
