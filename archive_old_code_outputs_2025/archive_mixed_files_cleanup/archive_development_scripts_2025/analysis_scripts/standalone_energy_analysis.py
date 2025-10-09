#!/usr/bin/env python3
"""
Standalone Energy Emission Source Analysis
Simple script to analyze energy emissions using correct column names
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def main():
    """Main analysis function"""
    print("🔋 KOREAN PETROCHEMICAL ENERGY EMISSIONS ANALYSIS")
    print("=" * 60)

    # Load data
    file_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"

    # Read facility and carbon intensity data
    facilities = pd.read_excel(file_path, sheet_name='source_Original')
    carbon_intensity = pd.read_excel(file_path, sheet_name='CI_Corrected')

    print(f"✅ Loaded {len(facilities)} facilities")
    print(f"✅ Loaded {len(carbon_intensity)} CI records")

    # Merge data
    merged = facilities.merge(
        carbon_intensity,
        left_on=['products', 'process'],
        right_on=['Product', 'Process'],
        how='left'
    )

    # Calculate energy consumption (GJ/year)
    merged['capacity_t_per_year'] = merged['capacity_1000_t'] * 1000  # Convert to tonnes

    # Energy consumption by source
    energy_consumption = {}

    # Naphtha (feedstock + thermal)
    if 'Naphtha_Feedstock_GJ_per_t' in merged.columns:
        energy_consumption['Naphtha_Feedstock'] = (merged['Naphtha_Feedstock_GJ_per_t'] * merged['capacity_t_per_year']).fillna(0).sum()
    if 'Naphtha_Thermal_GJ_per_t' in merged.columns:
        energy_consumption['Naphtha_Thermal'] = (merged['Naphtha_Thermal_GJ_per_t'] * merged['capacity_t_per_year']).fillna(0).sum()

    # Natural gas and LPG
    if 'LNG_GJ_per_t' in merged.columns:
        energy_consumption['LNG'] = (merged['LNG_GJ_per_t'] * merged['capacity_t_per_year']).fillna(0).sum()
    if 'LPG_Propane_GJ_per_t' in merged.columns:
        energy_consumption['LPG_Propane'] = (merged['LPG_Propane_GJ_per_t'] * merged['capacity_t_per_year']).fillna(0).sum()
    if 'LPG_Butane_GJ_per_t' in merged.columns:
        energy_consumption['LPG_Butane'] = (merged['LPG_Butane_GJ_per_t'] * merged['capacity_t_per_year']).fillna(0).sum()

    # Electricity (convert kWh to GJ)
    if 'Electricity_kWh_per_t' in merged.columns:
        energy_consumption['Electricity'] = (merged['Electricity_kWh_per_t'] * merged['capacity_t_per_year'] * 0.0036).fillna(0).sum()

    # Calculate emissions (using Korean emission factors)
    emission_factors = {
        'Naphtha_Feedstock': 70.5,  # kg CO2/GJ
        'Naphtha_Thermal': 70.5,
        'LNG': 56.1,
        'LPG_Propane': 63.1,
        'LPG_Butane': 64.2,
        'Electricity': 466.0  # Korean grid
    }

    emissions = {}
    for source, consumption_gj in energy_consumption.items():
        if source in emission_factors:
            emissions[source] = consumption_gj * emission_factors[source] / 1000  # tonnes CO2

    # Aggregate by category
    category_emissions = {
        'Naphtha': emissions.get('Naphtha_Feedstock', 0) + emissions.get('Naphtha_Thermal', 0),
        'LPG': emissions.get('LPG_Propane', 0) + emissions.get('LPG_Butane', 0),
        'Natural_Gas': emissions.get('LNG', 0),
        'Electricity': emissions.get('Electricity', 0)
    }

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    sources = list(category_emissions.keys())
    values = list(category_emissions.values())
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']

    wedges, texts, autotexts = ax1.pie(values, labels=sources, autopct='%1.1f%%',
                                      colors=colors, startangle=90)
    ax1.set_title('CO₂ Emissions by Energy Source')

    # Bar chart
    ax2.bar(sources, [v/1e6 for v in values], color=colors)
    ax2.set_title('Annual Emissions (Million tonnes CO₂)')
    ax2.set_ylabel('MtCO₂/year')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('../outputs/simple_energy_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Chart saved: ../outputs/simple_energy_analysis.png")

    # Summary report
    total_emissions = sum(values)
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"Total Annual Emissions: {total_emissions/1e6:.1f} MtCO₂")
    print(f"Total Capacity: {merged['capacity_1000_t'].sum():,.0f} thousand tonnes/year")

    print("\n⚡ ENERGY SOURCE BREAKDOWN:")
    for source, emission in category_emissions.items():
        share = emission / total_emissions * 100
        print(f"{source:12}: {emission/1e6:6.2f} MtCO₂ ({share:5.1f}%)")

    print("\n🏭 PROCESS TYPE BREAKDOWN:")
    for process in merged['process'].unique():
        process_capacity = merged[merged['process'] == process]['capacity_1000_t'].sum()
        companies = merged[merged['process'] == process]['company'].nunique()
        print(f"{process:15}: {process_capacity:8,.0f} kt, {companies:2.0f} companies")

    # Save data
    results_df = pd.DataFrame({
        'Energy_Source': sources,
        'Emissions_MtCO2_per_year': [v/1e6 for v in values],
        'Share_percent': [v/total_emissions*100 for v in values]
    })
    results_df.to_csv('../outputs/simple_energy_results.csv', index=False)
    print(f"\n💾 Data saved: ../outputs/simple_energy_results.csv")

    plt.show()

if __name__ == "__main__":
    main()