"""
Quick Baseline Analysis with Corrected Calculations
==================================================
"""

import pandas as pd
from pathlib import Path

def run_baseline_quick():
    """Quick baseline analysis with corrected calculations"""
    
    print("QUICK BASELINE ANALYSIS WITH CORRECTED CALCULATIONS")
    print("=" * 55)
    
    # Load database
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    consumption_df = excel_data['FacilityBaselineConsumption_2023']
    ef_df = excel_data['EmissionFactors_TimeSeries']
    ef_2023 = ef_df[ef_df['Year'] == 2023].iloc[0]
    
    print(f"Loaded {len(consumption_df)} facility records")
    print(f"Emission factors: NG={ef_2023['Natural_Gas_tCO2_per_GJ']:.4f}, Elec={ef_2023['Electricity_tCO2_per_GJ']:.4f} tCO2/GJ")
    
    # Calculate emissions correctly
    facility_results = []
    total_emissions = 0
    total_capacity = 0
    
    for _, row in consumption_df.iterrows():
        capacity = row['Activity_kt_product']
        
        # Energy emissions (correct approach)
        ng_emissions = capacity * row['NaturalGas_GJ_per_t'] * ef_2023['Natural_Gas_tCO2_per_GJ']
        fo_emissions = capacity * row['FuelOil_GJ_per_t'] * ef_2023['Fuel_Oil_tCO2_per_GJ']
        elec_emissions = capacity * row['Electricity_GJ_per_t'] * ef_2023['Electricity_tCO2_per_GJ']
        
        # Process emissions (if column exists)
        if 'ProcessEmissions_tCO2_per_t' in row:
            process_emissions = capacity * row['ProcessEmissions_tCO2_per_t']
        else:
            # Apply 20% process multiplier
            energy_emissions_per_t = (
                row['NaturalGas_GJ_per_t'] * ef_2023['Natural_Gas_tCO2_per_GJ'] +
                row['FuelOil_GJ_per_t'] * ef_2023['Fuel_Oil_tCO2_per_GJ'] +
                row['Electricity_GJ_per_t'] * ef_2023['Electricity_tCO2_per_GJ']
            )
            process_emissions = capacity * energy_emissions_per_t * 0.20
        
        total_facility_emissions = (ng_emissions + fo_emissions + elec_emissions + process_emissions) / 1000
        intensity = total_facility_emissions * 1000 / capacity
        
        facility_results.append({
            'FacilityID': row['FacilityID'],
            'Company': row['Company'],
            'Region': row['Region'],
            'ProcessType': row['ProcessType'],
            'Capacity_kt': capacity,
            'Emissions_ktCO2': total_facility_emissions,
            'Intensity_tCO2_per_t': intensity
        })
        
        total_emissions += total_facility_emissions
        total_capacity += capacity
    
    df_results = pd.DataFrame(facility_results)
    
    # Aggregate by facility
    facility_summary = df_results.groupby(['FacilityID', 'Company', 'Region']).agg({
        'Capacity_kt': 'sum',
        'Emissions_ktCO2': 'sum'
    }).reset_index()
    
    facility_summary['Intensity_tCO2_per_t'] = facility_summary['Emissions_ktCO2'] * 1000 / facility_summary['Capacity_kt']
    facility_summary['Share_Pct'] = (facility_summary['Emissions_ktCO2'] / total_emissions * 100).round(1)
    
    # Results
    industry_intensity = total_emissions * 1000 / total_capacity
    
    print(f"\nBASELINE RESULTS:")
    print(f"  Total Emissions: {total_emissions:,.1f} ktCO2/year")
    print(f"  Total Capacity: {total_capacity:,.0f} kt/year") 
    print(f"  Industry Intensity: {industry_intensity:.1f} tCO2/t")
    print(f"  Benchmark Range: 2.5-4.0 tCO2/t")
    
    if 2.5 <= industry_intensity <= 4.0:
        print(f"  ✅ WITHIN BENCHMARK RANGE")
    else:
        print(f"  ⚠️  Outside benchmark range")
    
    print(f"\nFACILITY SUMMARY:")
    print(facility_summary.to_string(index=False))
    
    # Technology breakdown
    tech_summary = df_results.groupby('ProcessType').agg({
        'Capacity_kt': 'sum',
        'Emissions_ktCO2': 'sum'
    }).reset_index()
    tech_summary['Intensity_tCO2_per_t'] = tech_summary['Emissions_ktCO2'] * 1000 / tech_summary['Capacity_kt']
    tech_summary['Share_Pct'] = (tech_summary['Emissions_ktCO2'] / total_emissions * 100).round(1)
    
    print(f"\nTECHNOLOGY BREAKDOWN:")
    print(tech_summary.to_string(index=False))
    
    # Regional breakdown
    regional_summary = df_results.groupby('Region').agg({
        'Capacity_kt': 'sum',
        'Emissions_ktCO2': 'sum'
    }).reset_index()
    regional_summary['Share_Pct'] = (regional_summary['Emissions_ktCO2'] / total_emissions * 100).round(1)
    
    print(f"\nREGIONAL BREAKDOWN:")
    print(regional_summary.to_string(index=False))
    
    return df_results, total_emissions, industry_intensity

if __name__ == "__main__":
    run_baseline_quick()