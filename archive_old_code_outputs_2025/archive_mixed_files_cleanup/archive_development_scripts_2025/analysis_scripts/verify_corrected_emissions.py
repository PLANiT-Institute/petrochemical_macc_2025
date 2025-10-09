#!/usr/bin/env python3
"""
Verify that the corrected energy intensities produce realistic total emissions (~52 MtCO2)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_corrected_emissions():
    """Verify the corrected model produces realistic total emissions"""

    data_path = Path(__file__).parent.parent / "data"
    corrected_file = data_path / "Korean_MACC_Model_CORRECTED_INTENSITIES.xlsx"
    outputs_path = Path(__file__).parent.parent / "outputs" / "corrected_verification"
    outputs_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("🔍 VERIFYING CORRECTED EMISSION INTENSITIES")
    print("="*70)

    try:
        # Load corrected data
        facility_data = pd.read_excel(corrected_file, sheet_name='FacilityBaselineConsumption')
        ci_data = pd.read_excel(corrected_file, sheet_name='CI_Corrected')
        ci2_data = pd.read_excel(corrected_file, sheet_name='CI2_Corrected')

        print(f"\n📊 Data loaded:")
        print(f"   Facilities: {facility_data.shape}")
        print(f"   Energy intensities: {ci_data.shape}")
        print(f"   Emission factors: {ci2_data.shape}")

        # Calculate total emissions
        total_emissions_tco2 = 0
        total_capacity_kt = 0

        # Process each facility
        facility_emissions = []

        for idx, facility in facility_data.iterrows():
            facility_name = facility.iloc[0]
            process_type = facility.iloc[1] if len(facility) > 1 else None

            # Find matching CI row
            ci_match = ci_data[ci_data.iloc[:,0] == process_type]
            if ci_match.empty and process_type:
                # Try partial matching
                for ci_idx, ci_row in ci_data.iterrows():
                    if str(ci_row.iloc[0]).lower() in str(process_type).lower():
                        ci_match = ci_data.iloc[[ci_idx]]
                        break

            if not ci_match.empty:
                ci_row = ci_match.iloc[0]

                # Get production capacity (try different column positions)
                production_kt = 0
                for col_idx in range(2, min(10, len(facility))):
                    if pd.notna(facility.iloc[col_idx]) and facility.iloc[col_idx] > 0:
                        production_kt = facility.iloc[col_idx]
                        break

                if production_kt > 0:
                    total_capacity_kt += production_kt

                    # Calculate energy consumption
                    total_energy_intensity = 0
                    energy_breakdown = {}

                    for ci_col_idx, ci_col in enumerate(ci_data.columns):
                        if 'gj_per_t' in str(ci_col).lower() and pd.notna(ci_row.iloc[ci_col_idx]):
                            energy_val = ci_row.iloc[ci_col_idx]
                            total_energy_intensity += energy_val

                            if 'naphtha' in str(ci_col).lower():
                                energy_breakdown['naphtha'] = energy_val
                            elif 'lng' in str(ci_col).lower():
                                energy_breakdown['lng'] = energy_val
                            elif 'byproduct' in str(ci_col).lower():
                                energy_breakdown['byproduct_gas'] = energy_val
                            elif 'electricity' in str(ci_col).lower():
                                energy_breakdown['electricity'] = energy_val

                    # Calculate emissions using corrected intensities
                    total_energy_gj = total_energy_intensity * production_kt * 1000  # kt to t

                    # Apply typical emission factors
                    # Naphtha: 0.0561 tCO2/GJ, Natural gas: 0.0515 tCO2/GJ, Electricity: varies by grid
                    emissions_tco2 = 0

                    if 'naphtha' in energy_breakdown:
                        naphtha_emissions = energy_breakdown['naphtha'] * production_kt * 1000 * 0.0561
                        emissions_tco2 += naphtha_emissions

                    if 'lng' in energy_breakdown:
                        lng_emissions = energy_breakdown['lng'] * production_kt * 1000 * 0.0515
                        emissions_tco2 += lng_emissions

                    if 'byproduct_gas' in energy_breakdown:
                        # Assume similar to natural gas
                        bg_emissions = energy_breakdown['byproduct_gas'] * production_kt * 1000 * 0.05
                        emissions_tco2 += bg_emissions

                    if 'electricity' in energy_breakdown:
                        # Korean grid factor ~0.5 tCO2/MWh = 0.139 tCO2/GJ
                        elec_emissions = energy_breakdown['electricity'] * production_kt * 1000 * 0.139
                        emissions_tco2 += elec_emissions

                    total_emissions_tco2 += emissions_tco2

                    facility_emissions.append({
                        'facility': facility_name,
                        'process': process_type,
                        'capacity_kt': production_kt,
                        'energy_intensity_gj_per_t': total_energy_intensity,
                        'total_energy_gj': total_energy_gj,
                        'emissions_tco2': emissions_tco2,
                        'emission_intensity_tco2_per_t': emissions_tco2 / (production_kt * 1000) if production_kt > 0 else 0
                    })

        # Convert to MtCO2
        total_emissions_mtco2 = total_emissions_tco2 / 1_000_000

        print(f"\n🎯 VERIFICATION RESULTS:")
        print(f"   Total capacity: {total_capacity_kt:,.0f} kt")
        print(f"   Total emissions: {total_emissions_mtco2:.1f} MtCO₂")
        print(f"   Average emission intensity: {total_emissions_tco2 / (total_capacity_kt * 1000):.2f} tCO₂/t")

        # Compare with targets
        target_emissions = 52.0
        ratio_to_target = total_emissions_mtco2 / target_emissions

        print(f"\n📊 COMPARISON WITH KOREAN INDUSTRY:")
        print(f"   Target emissions: {target_emissions:.1f} MtCO₂")
        print(f"   Calculated emissions: {total_emissions_mtco2:.1f} MtCO₂")
        print(f"   Ratio: {ratio_to_target:.2f}")

        if ratio_to_target <= 1.2 and ratio_to_target >= 0.8:
            print(f"   Status: ✅ GOOD - Within 20% of target")
        elif ratio_to_target <= 2.0:
            print(f"   Status: ⚠️ ACCEPTABLE - Within 2x of target")
        else:
            print(f"   Status: ❌ NEEDS ADJUSTMENT - Still too high")

        # Save detailed results
        results_df = pd.DataFrame(facility_emissions)
        results_file = outputs_path / "corrected_emission_verification.csv"
        results_df.to_csv(results_file, index=False)

        # Summary report
        summary_file = outputs_path / "verification_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("CORRECTED MODEL VERIFICATION SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total Capacity: {total_capacity_kt:,.0f} kt\n")
            f.write(f"Total Emissions: {total_emissions_mtco2:.1f} MtCO₂\n")
            f.write(f"Target Emissions: {target_emissions:.1f} MtCO₂\n")
            f.write(f"Ratio to Target: {ratio_to_target:.2f}\n\n")
            f.write(f"Energy Intensity Corrections Applied:\n")
            f.write(f"- Ethylene: 35.0 GJ/t (vs 184.3 before)\n")
            f.write(f"- Propylene: 31.5 GJ/t (vs 168.1 before)\n")
            f.write(f"- BTX: 20-26 GJ/t (vs 70-80 before)\n")

        print(f"\n📁 Results saved:")
        print(f"   {results_file}")
        print(f"   {summary_file}")

        return total_emissions_mtco2, ratio_to_target

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    verify_corrected_emissions()