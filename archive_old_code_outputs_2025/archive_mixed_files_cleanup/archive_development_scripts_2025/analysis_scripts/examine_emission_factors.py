#!/usr/bin/env python3
"""
Examine actual emission factors in Excel file to identify why they're too high
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def examine_emission_factors():
    """Examine the actual emission factors in the Excel file"""

    data_path = Path(__file__).parent.parent / "data"
    excel_file = data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"

    print("\n" + "=" * 70)
    print("🔍 EXAMINING EMISSION FACTORS IN EXCEL MODEL")
    print("=" * 70)

    try:
        # Load CI_Corrected (Carbon Intensity data)
        ci_data = pd.read_excel(excel_file, sheet_name='CI_Corrected')
        print(f"\n📊 CI_Corrected sheet: {ci_data.shape}")
        print("\nColumns:")
        for i, col in enumerate(ci_data.columns):
            print(f"   {i}: {col}")

        print(f"\nFirst 10 rows of CI_Corrected:")
        for idx, row in ci_data.head(10).iterrows():
            print(f"   Row {idx}: {row.iloc[0]} | {[f'{col}={val}' for col, val in zip(ci_data.columns[1:6], row.iloc[1:6]) if pd.notna(val)]}")

        # Load CI2_Corrected (Emission factors)
        ci2_data = pd.read_excel(excel_file, sheet_name='CI2_Corrected')
        print(f"\n📊 CI2_Corrected sheet: {ci2_data.shape}")
        print("\nColumns:")
        for i, col in enumerate(ci2_data.columns):
            print(f"   {i}: {col}")

        print(f"\nAll rows of CI2_Corrected:")
        for idx, row in ci2_data.iterrows():
            print(f"   Row {idx}: {row.iloc[0]} | {[f'{col}={val}' for col, val in zip(ci2_data.columns[1:], row.iloc[1:]) if pd.notna(val)]}")

        # Look for problematic values
        print("\n🚨 POTENTIAL ISSUES IDENTIFIED:")

        # Check CI2 for high emission factors
        for idx, row in ci2_data.iterrows():
            fuel_type = str(row.iloc[0])
            for col_idx, col in enumerate(ci2_data.columns[1:], 1):
                if 'tco2' in col.lower() and pd.notna(row.iloc[col_idx]):
                    factor_value = row.iloc[col_idx]
                    if factor_value > 0.1:  # Typical emission factors are 0.05-0.08 tCO2/GJ
                        print(f"   HIGH: {fuel_type} - {col} = {factor_value:.4f}")
                    elif factor_value > 0.08:
                        print(f"   ELEVATED: {fuel_type} - {col} = {factor_value:.4f}")

        # Check CI for high energy intensities
        high_energy_processes = []
        for idx, row in ci_data.iterrows():
            process = str(row.iloc[0])
            total_energy = 0

            for col_idx, col in enumerate(ci_data.columns[1:], 1):
                if 'gj_per_t' in col.lower() and pd.notna(row.iloc[col_idx]):
                    energy_value = row.iloc[col_idx]
                    total_energy += energy_value

                    if energy_value > 50:  # Very high energy intensity
                        print(f"   HIGH ENERGY: {process} - {col} = {energy_value:.1f} GJ/t")

            if total_energy > 100:  # Extremely high total energy
                high_energy_processes.append((process, total_energy))

        if high_energy_processes:
            print(f"\n   PROCESSES WITH VERY HIGH TOTAL ENERGY INTENSITY:")
            for process, energy in high_energy_processes:
                print(f"     {process}: {energy:.1f} GJ/t")

        # Research typical values
        print(f"\n📚 TYPICAL INDUSTRY VALUES FOR COMPARISON:")
        print(f"   Naphtha Cracker (Ethylene): 28-35 GJ/t, 1.5-2.5 tCO2/t")
        print(f"   BTX/Aromatics: 15-25 GJ/t, 0.8-1.5 tCO2/t")
        print(f"   Polyethylene: 20-28 GJ/t, 1.0-1.8 tCO2/t")
        print(f"   Emission factors: 0.0561 tCO2/GJ (naphtha), 0.0515 tCO2/GJ (natural gas)")

        # Calculate what the corrected factors should be
        target_total_mt = 52
        current_total_mt = 261.5
        scaling_factor = target_total_mt / current_total_mt

        print(f"\n🎯 CORRECTION NEEDED:")
        print(f"   Current total: {current_total_mt} MtCO2")
        print(f"   Target total: {target_total_mt} MtCO2")
        print(f"   Scaling factor needed: {scaling_factor:.3f}")
        print(f"   This suggests emission factors should be ~{1/scaling_factor:.1f}x lower")

    except Exception as e:
        logger.error(f"Error examining emission factors: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    examine_emission_factors()