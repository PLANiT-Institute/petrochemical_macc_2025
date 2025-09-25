#!/usr/bin/env python3
"""
Run BAU analysis with corrected 52 MtCO2 baseline
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def run_corrected_bau_analysis():
    """Run BAU analysis with corrected emission factors"""
    print("🚀 CORRECTED BAU ANALYSIS (52 MtCO2 BASELINE)")
    print("=" * 60)

    # Use calibrated model
    excel_path = "../data/Korean_Petrochemical_MACC_Model_Calibrated_52Mt.xlsx"

    # Load data
    facilities_df = pd.read_excel(excel_path, sheet_name='source_Original')
    ci_df = pd.read_excel(excel_path, sheet_name='CI_Corrected', index_col=0)
    ci2_df = pd.read_excel(excel_path, sheet_name='CI2_Corrected', index_col=0)

    print(f"📊 Using calibrated emission factors:")
    print(f"   Naphtha Feedstock: {ci2_df.iloc[0]['Naphtha_Feedstock_tCO2_per_GJ']:.6f} tCO2/GJ")

    # Calculate facility-level emissions
    emission_factors = {col: ci2_df.iloc[0][col] for col in ci2_df.columns}
    process_mapping = {'Naphtha Cracker': 'Ethylene', 'BTX Plant': 'Benzene', 'Utility': 'Steam'}

    facility_emissions = []
    total_baseline = 0

    for idx, facility in facilities_df.iterrows():
        process = facility['process']
        product = process_mapping.get(process, 'Ethylene')
        capacity = facility['capacity_1000_t'] * 1000

        if product not in ci_df.index or capacity <= 0:
            continue

        product_row = ci_df.loc[product]
        facility_total = 0

        for consumption_col, emission_col in [('LNG_GJ_per_t', 'LNG_tCO2_per_GJ'),
                                             ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ'),
                                             ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ'),
                                             ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh')]:
            if consumption_col in product_row.index and emission_col in emission_factors:
                consumption = product_row[consumption_col]
                if pd.notna(consumption) and consumption > 0:
                    facility_total += consumption * capacity * emission_factors[emission_col]

        if facility_total > 0:
            facility_emissions.append({
                'facility_id': idx,
                'company': facility['company'],
                'process': process,
                'capacity_kt': facility['capacity_1000_t'],
                'operational_year': facility['year'],
                'age_2025': 2025 - facility['year'],
                'emissions_tco2': facility_total
            })
            total_baseline += facility_total

    print(f"✅ Corrected baseline: {total_baseline/1e6:.1f} MtCO2/year")

    # Create BAU pathways
    facility_df = pd.DataFrame(facility_emissions)
    lifetime_scenarios = {'25-year': 25, '30-year': 30, '40-year': 40, '50-year': 50}
    pathway_results = {}

    for scenario_name, lifetime in lifetime_scenarios.items():
        yearly_data = []

        for year in range(2025, 2051):
            active_facilities = facility_df[year - facility_df['operational_year'] <= lifetime]
            total_emissions = active_facilities['emissions_tco2'].sum()
            num_active = len(active_facilities)

            yearly_data.append({
                'year': year,
                'emissions_mtco2': total_emissions / 1e6,
                'active_facilities': num_active
            })

        pathway_results[scenario_name] = pd.DataFrame(yearly_data)

    # Create corrected visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    colors = {'25-year': '#d62728', '30-year': '#ff7f0e', '40-year': '#1f77b4', '50-year': '#2ca02c'}

    # Plot emissions
    ax1.set_facecolor('#f8f8f8')
    ax1.grid(True, alpha=0.3, color='white', linewidth=1)

    for scenario_name, data in pathway_results.items():
        ax1.plot(data['year'], data['emissions_mtco2'],
                color=colors[scenario_name], linewidth=3,
                label=f"{scenario_name} facility lifetime")

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Emissions (Mt CO₂)', fontsize=12)
    ax1.set_title('Korean Petrochemical Industry - BAU Emission Pathways\\n(Corrected to 52 Mt Baseline)',
                 fontsize=14, fontweight='bold', pad=20)
    ax1.legend(fontsize=11, loc='upper right')
    ax1.set_xlim(2024, 2051)
    ax1.set_ylim(0, 55)

    # Plot active facilities
    ax2.set_facecolor('#f8f8f8')
    ax2.grid(True, alpha=0.3, color='white', linewidth=1)

    for scenario_name, data in pathway_results.items():
        ax2.plot(data['year'], data['active_facilities'],
                color=colors[scenario_name], linewidth=3,
                label=f"{scenario_name} lifetime")

    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Number of Active Facilities', fontsize=12)
    ax2.set_title('Active Facilities Over Time', fontsize=14, fontweight='bold', pad=20)
    ax2.legend(fontsize=11, loc='upper right')
    ax2.set_xlim(2024, 2051)

    plt.tight_layout()

    # Save corrected chart
    output_path = Path("../outputs/bau_emission_pathways_corrected_52mt.png")
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Corrected BAU chart saved: {output_path}")

    plt.show()

    # Show corrected results
    print(f"\\n📈 CORRECTED BAU PATHWAY RESULTS:")
    for scenario_name, data in pathway_results.items():
        emissions_2025 = data[data['year'] == 2025]['emissions_mtco2'].iloc[0]
        emissions_2050 = data[data['year'] == 2050]['emissions_mtco2'].iloc[0]
        reduction = (1 - emissions_2050/emissions_2025) * 100 if emissions_2025 > 0 else 0
        print(f"   {scenario_name}: {emissions_2025:.1f} → {emissions_2050:.1f} Mt ({reduction:.1f}% reduction)")

    return pathway_results

if __name__ == "__main__":
    results = run_corrected_bau_analysis()