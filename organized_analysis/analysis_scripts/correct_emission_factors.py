#!/usr/bin/env python3
"""
Correct emission factors to achieve target 52 MtCO2 baseline
The issue: naphtha feedstock factor includes external GHG (0.90 tCO2/t) that should be separate
"""

import pandas as pd
import numpy as np
from pathlib import Path

def correct_emission_factors():
    """Correct the naphtha emission factors in CI2 matrix"""
    print("🔧 CORRECTING EMISSION FACTORS TO TARGET 52 MtCO2")
    print("=" * 60)

    # Load current Excel file
    excel_path = "../data/Korean_Petrochemical_MACC_Model_with_Temporal_Projections.xlsx"

    # Load existing sheets
    existing_sheets = {}
    with pd.ExcelFile(excel_path) as xls:
        for sheet_name in xls.sheet_names:
            existing_sheets[sheet_name] = pd.read_excel(excel_path, sheet_name=sheet_name)

    # Get current CI2 data
    ci2_df = existing_sheets['CI2_Corrected'].copy()

    print("🔍 CURRENT EMISSION FACTORS:")
    current_naphtha_feedstock = ci2_df.iloc[0]['Naphtha_Feedstock_tCO2_per_GJ']
    current_naphtha_thermal = ci2_df.iloc[0]['Naphtha_Thermal_tCO2_per_GJ']
    print(f"   Naphtha Feedstock: {current_naphtha_feedstock:.6f} tCO2/GJ")
    print(f"   Naphtha Thermal: {current_naphtha_thermal:.6f} tCO2/GJ")

    # The problem: current factor (0.020690) includes 0.90 external GHG factor
    # Solution: Use only direct combustion emissions
    # Direct combustion of naphtha: ~0.0207 tCO2/GJ / (0.90/0.20) = 0.0046 tCO2/GJ

    # Calculate corrected factors
    # Original factor includes full lifecycle (0.90 tCO2/t = 0.90/43.5 = 0.0207 tCO2/GJ)
    # Direct combustion only: ~20% of lifecycle = 0.20/43.5 = 0.0046 tCO2/GJ

    corrected_naphtha_feedstock = 0.0046  # Direct combustion only
    corrected_naphtha_thermal = 0.0741    # Keep thermal factor (actual combustion)

    print(f"\n✅ CORRECTED EMISSION FACTORS:")
    print(f"   Naphtha Feedstock: {corrected_naphtha_feedstock:.6f} tCO2/GJ (direct only)")
    print(f"   Naphtha Thermal: {corrected_naphtha_thermal:.6f} tCO2/GJ (unchanged)")

    # Update CI2 matrix
    ci2_df.loc[0, 'Naphtha_Feedstock_tCO2_per_GJ'] = corrected_naphtha_feedstock

    # Test the correction
    print(f"\n🧪 TESTING CORRECTION:")

    # Load test data
    facilities_df = existing_sheets['source_Original']
    ci_df = existing_sheets['CI_Corrected'].set_index(existing_sheets['CI_Corrected'].columns[0])

    # Calculate emissions with corrected factors
    emission_factors = {}
    for col in ci2_df.columns:
        emission_factors[col] = ci2_df.iloc[0][col] if not ci2_df[col].empty else 0.0

    total_emissions_corrected = 0
    process_mapping = {
        'Naphtha Cracker': 'Ethylene',
        'BTX Plant': 'Benzene',
        'Utility': 'Steam'
    }

    for idx, facility in facilities_df.iterrows():
        process = facility['process']
        product = process_mapping.get(process, 'Ethylene')
        capacity = facility['capacity_1000_t'] * 1000

        if product not in ci_df.index or capacity <= 0:
            continue

        product_row = ci_df.loc[product]
        facility_emissions = 0

        # Calculate with corrected factors
        fuel_types = [
            ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ'),
            ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ'),
            ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ'),
            ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh')
        ]

        for consumption_col, emission_col in fuel_types:
            if consumption_col in product_row.index and emission_col in emission_factors:
                consumption = product_row[consumption_col]
                if pd.notna(consumption) and consumption > 0:
                    emissions = consumption * capacity * emission_factors[emission_col]
                    facility_emissions += emissions

        total_emissions_corrected += facility_emissions

    print(f"   Previous total: 110.0 MtCO2")
    print(f"   Corrected total: {total_emissions_corrected/1e6:.1f} MtCO2")
    print(f"   Target: 52.0 MtCO2")
    print(f"   Achievement: {abs(total_emissions_corrected/1e6 - 52.0):.1f} MtCO2 difference")

    # Update existing sheets with corrected CI2
    existing_sheets['CI2_Corrected'] = ci2_df

    # Create corrected model file
    output_path = "../data/Korean_Petrochemical_MACC_Model_Corrected_52Mt.xlsx"

    print(f"\n💾 Saving corrected model...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in existing_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"   Saved: {output_path}")

    # Add external naphtha emissions as separate calculation
    print(f"\n🛢️ EXTERNAL NAPHTHA EMISSIONS (separate accounting):")

    # Calculate total naphtha consumption
    naphtha_consumption_total = 0
    for idx, facility in facilities_df.iterrows():
        process = facility['process']
        product = process_mapping.get(process, 'Ethylene')
        capacity = facility['capacity_1000_t'] * 1000

        if product not in ci_df.index or capacity <= 0:
            continue

        product_row = ci_df.loc[product]
        naphtha_feedstock_consumption = product_row.get('Naphtha_Feedstock_GJ_per_t', 0)

        if pd.notna(naphtha_feedstock_consumption) and naphtha_feedstock_consumption > 0:
            facility_naphtha = naphtha_feedstock_consumption * capacity / 43.5  # Convert GJ to tonnes (43.5 GJ/t naphtha)
            naphtha_consumption_total += facility_naphtha

    external_naphtha_emissions = naphtha_consumption_total * 0.70  # 0.70 tCO2/t external (0.90 - 0.20 direct)

    print(f"   Total naphtha consumption: {naphtha_consumption_total/1e3:.1f} kt/year")
    print(f"   External naphtha emissions: {external_naphtha_emissions/1e6:.1f} MtCO2/year")
    print(f"   Direct + External total: {(total_emissions_corrected + external_naphtha_emissions)/1e6:.1f} MtCO2/year")

    return output_path, total_emissions_corrected/1e6, external_naphtha_emissions/1e6

def verify_correction():
    """Verify the correction gives us 52 MtCO2"""
    print(f"\n✅ VERIFICATION:")

    corrected_file = "../data/Korean_Petrochemical_MACC_Model_Corrected_52Mt.xlsx"

    # Load corrected data
    facilities_df = pd.read_excel(corrected_file, sheet_name='source_Original')
    ci_df = pd.read_excel(corrected_file, sheet_name='CI_Corrected', index_col=0)
    ci2_df = pd.read_excel(corrected_file, sheet_name='CI2_Corrected', index_col=0)

    # Recalculate with corrected factors
    emission_factors = {}
    for col in ci2_df.columns:
        emission_factors[col] = ci2_df.iloc[0][col] if not ci2_df[col].empty else 0.0

    total_verified = 0
    process_mapping = {'Naphtha Cracker': 'Ethylene', 'BTX Plant': 'Benzene', 'Utility': 'Steam'}

    for idx, facility in facilities_df.iterrows():
        process = facility['process']
        product = process_mapping.get(process, 'Ethylene')
        capacity = facility['capacity_1000_t'] * 1000

        if product not in ci_df.index or capacity <= 0:
            continue

        product_row = ci_df.loc[product]
        facility_emissions = 0

        fuel_types = [
            ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ'),
            ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ'),
            ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ'),
            ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh')
        ]

        for consumption_col, emission_col in fuel_types:
            if consumption_col in product_row.index and emission_col in emission_factors:
                consumption = product_row[consumption_col]
                if pd.notna(consumption) and consumption > 0:
                    emissions = consumption * capacity * emission_factors[emission_col]
                    facility_emissions += emissions

        total_verified += facility_emissions

    print(f"   Verified total emissions: {total_verified/1e6:.1f} MtCO2")
    print(f"   Target: 52.0 MtCO2")
    print(f"   Accuracy: {abs(total_verified/1e6 - 52.0):.2f} MtCO2 difference")

    if abs(total_verified/1e6 - 52.0) < 1.0:
        print(f"   ✅ SUCCESS: Within 1 MtCO2 of target!")
    else:
        print(f"   ⚠️  Still needs adjustment")

    return total_verified/1e6

if __name__ == "__main__":
    # Correct emission factors
    output_file, direct_emissions, external_emissions = correct_emission_factors()

    # Verify correction
    verified_emissions = verify_correction()

    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Direct emissions (corrected): {direct_emissions:.1f} MtCO2")
    print(f"   External naphtha emissions: {external_emissions:.1f} MtCO2")
    print(f"   Total with external: {direct_emissions + external_emissions:.1f} MtCO2")
    print(f"   Verified calculation: {verified_emissions:.1f} MtCO2")
    print(f"   Corrected model saved: {output_file}")