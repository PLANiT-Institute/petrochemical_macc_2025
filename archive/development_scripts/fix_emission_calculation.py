"""
Fix Emission Calculation for Realistic Industry Benchmark Alignment
================================================================

The current model includes feedstock emissions (Naphtha, LPG, Reformate) which inflates 
emission intensity to 853 tCO2/t vs industry benchmark 2.5-4.0 tCO2/t.

For petrochemical MACC analysis, we should only count ENERGY-related emissions:
- Natural Gas (process heating, steam)
- Fuel Oil (heating)  
- Electricity (purchased power)

Feedstock carbon becomes part of the product and should be excluded from Scope 1 emissions.
"""

import pandas as pd
from pathlib import Path

def fix_emission_calculation():
    """Fix emission calculation to exclude feedstock emissions"""
    
    print("FIXING EMISSION CALCULATION FOR INDUSTRY BENCHMARK ALIGNMENT")
    print("=" * 60)
    
    # Load database
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    consumption_df = excel_data['FacilityBaselineConsumption_2023']
    ef_df = excel_data['EmissionFactors_TimeSeries']
    ef_2023 = ef_df[ef_df['Year'] == 2023].iloc[0]
    
    print("Current emission factors (tCO2/GJ):")
    print(f"  Natural Gas: {ef_2023['Natural_Gas_tCO2_per_GJ']:.4f}")
    print(f"  Fuel Oil: {ef_2023['Fuel_Oil_tCO2_per_GJ']:.4f}")
    print(f"  Electricity: {ef_2023['Electricity_tCO2_per_GJ']:.4f}")
    
    print(f"\nFeedstock emission factors (tCO2/t) - TO BE EXCLUDED:")
    print(f"  Naphtha: {ef_2023['Naphtha_tCO2_per_t']:.2f}")
    print(f"  LPG: {ef_2023['LPG_tCO2_per_t']:.2f}")
    print(f"  Reformate: {ef_2023['Reformate_tCO2_per_t']:.2f}")
    
    # Calculate corrected emissions (ENERGY ONLY)
    corrected_emissions = []
    total_energy_emissions = 0
    total_feedstock_emissions = 0
    total_capacity = 0
    
    for _, row in consumption_df.iterrows():
        capacity = row['Activity_kt_product']
        
        # ENERGY emissions (KEEP THESE)
        ng_emissions = capacity * row['NaturalGas_GJ_per_t'] * ef_2023['Natural_Gas_tCO2_per_GJ']
        fo_emissions = capacity * row['FuelOil_GJ_per_t'] * ef_2023['Fuel_Oil_tCO2_per_GJ'] 
        elec_emissions = capacity * row['Electricity_GJ_per_t'] * ef_2023['Electricity_tCO2_per_GJ']
        
        energy_emissions_ktco2 = (ng_emissions + fo_emissions + elec_emissions) / 1000
        
        # FEEDSTOCK emissions (EXCLUDE THESE)
        naphtha_emissions = capacity * row.get('Naphtha_t_per_t', 0) * ef_2023['Naphtha_tCO2_per_t'] / 1000
        lpg_emissions = capacity * row.get('LPG_t_per_t', 0) * ef_2023['LPG_tCO2_per_t'] / 1000
        reformate_emissions = capacity * row.get('Reformate_t_per_t', 0) * ef_2023['Reformate_tCO2_per_t'] / 1000
        
        feedstock_emissions_ktco2 = naphtha_emissions + lpg_emissions + reformate_emissions
        
        corrected_emissions.append({
            'FacilityID': row['FacilityID'],
            'Company': row['Company'],
            'Region': row['Region'],
            'ProcessType': row['ProcessType'],
            'Capacity_kt': capacity,
            'Energy_Emissions_ktCO2': energy_emissions_ktco2,
            'Feedstock_Emissions_ktCO2': feedstock_emissions_ktco2,
            'Old_Total_ktCO2': energy_emissions_ktco2 + feedstock_emissions_ktco2,
            'New_Total_ktCO2': energy_emissions_ktco2,  # CORRECTED
            'Old_Intensity_tCO2_per_t': (energy_emissions_ktco2 + feedstock_emissions_ktco2) * 1000 / capacity,
            'New_Intensity_tCO2_per_t': energy_emissions_ktco2 * 1000 / capacity  # CORRECTED
        })
        
        total_energy_emissions += energy_emissions_ktco2
        total_feedstock_emissions += feedstock_emissions_ktco2
        total_capacity += capacity
    
    df_corrected = pd.DataFrame(corrected_emissions)
    
    # Summary by facility
    facility_summary = df_corrected.groupby(['FacilityID', 'Company', 'Region']).agg({
        'Capacity_kt': 'sum',
        'New_Total_ktCO2': 'sum',
        'Old_Total_ktCO2': 'sum'
    }).reset_index()
    
    facility_summary['New_Intensity_tCO2_per_t'] = facility_summary['New_Total_ktCO2'] * 1000 / facility_summary['Capacity_kt']
    facility_summary['Old_Intensity_tCO2_per_t'] = facility_summary['Old_Total_ktCO2'] * 1000 / facility_summary['Capacity_kt']
    
    print(f"\nINDUSTRY TOTALS:")
    print(f"  Total Capacity: {total_capacity:,.0f} kt/year")
    print(f"  Energy Emissions: {total_energy_emissions:,.1f} ktCO2/year")
    print(f"  Feedstock Emissions: {total_feedstock_emissions:,.1f} ktCO2/year (EXCLUDED)")
    print(f"  Old Total: {total_energy_emissions + total_feedstock_emissions:,.1f} ktCO2/year")
    print(f"  New Total: {total_energy_emissions:,.1f} ktCO2/year")
    
    print(f"\nEMISSION INTENSITY COMPARISON:")
    old_intensity = (total_energy_emissions + total_feedstock_emissions) * 1000 / total_capacity
    new_intensity = total_energy_emissions * 1000 / total_capacity
    print(f"  Old Intensity: {old_intensity:.1f} tCO2/t")
    print(f"  New Intensity: {new_intensity:.1f} tCO2/t")
    print(f"  Industry Benchmark: 2.5-4.0 tCO2/t")
    
    benchmark_gap = ((new_intensity - 3.25) / 3.25) * 100  # vs mid-point
    print(f"  Benchmark Gap: {benchmark_gap:+.1f}% (vs 3.25 tCO2/t midpoint)")
    
    if 2.5 <= new_intensity <= 4.0:
        print(f"  ✅ WITHIN INDUSTRY BENCHMARK RANGE")
    else:
        print(f"  ⚠️  Still outside benchmark range")
    
    print(f"\nFACILITY SUMMARY:")
    print(facility_summary[['Company', 'Region', 'Capacity_kt', 'New_Total_ktCO2', 'New_Intensity_tCO2_per_t']].to_string(index=False))
    
    # Save corrected baseline
    output_path = Path("baseline/Corrected_Baseline_Energy_Only.csv")
    output_path.parent.mkdir(exist_ok=True)
    df_corrected.to_csv(output_path, index=False)
    print(f"\n✅ Corrected baseline saved: {output_path}")
    
    # Create new baseline for model use
    corrected_baseline = consumption_df.copy()
    corrected_baseline['Corrected_Emissions_ktCO2'] = df_corrected['New_Total_ktCO2']
    corrected_baseline['Corrected_Intensity_tCO2_per_t'] = df_corrected['New_Intensity_tCO2_per_t']
    
    return df_corrected, facility_summary

if __name__ == "__main__":
    fix_emission_calculation()