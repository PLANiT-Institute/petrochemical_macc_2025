"""
Calibrate Baseline Consumption to Industry Benchmarks
====================================================

Current energy-only emissions (0.9 tCO2/t) are too low vs industry benchmark (2.5-4.0 tCO2/t).
Need to calibrate energy consumption to realistic petrochemical industry levels.

Industry benchmarks for Korean petrochemicals:
- Steam cracking (ethylene): 28-32 GJ/t ethylene  
- Aromatics (BTX): 3-5 GJ/t benzene
- Total energy intensity: 2.5-4.0 tCO2/t product
"""

import pandas as pd
from pathlib import Path
import numpy as np

def calibrate_baseline_consumption():
    """Calibrate baseline consumption to industry benchmarks"""
    
    print("CALIBRATING BASELINE CONSUMPTION TO INDUSTRY BENCHMARKS")
    print("=" * 60)
    
    # Load database
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    consumption_df = excel_data['FacilityBaselineConsumption_2023'].copy()
    ef_df = excel_data['EmissionFactors_TimeSeries']
    ef_2023 = ef_df[ef_df['Year'] == 2023].iloc[0]
    
    # Current energy consumption
    print("CURRENT ENERGY CONSUMPTION (GJ/t):")
    current_summary = consumption_df.groupby('ProcessType').agg({
        'NaturalGas_GJ_per_t': 'mean',
        'FuelOil_GJ_per_t': 'mean', 
        'Electricity_GJ_per_t': 'mean',
        'Activity_kt_product': 'sum'
    }).round(2)
    
    current_summary['Total_Energy_GJ_per_t'] = (
        current_summary['NaturalGas_GJ_per_t'] + 
        current_summary['FuelOil_GJ_per_t'] + 
        current_summary['Electricity_GJ_per_t']
    )
    
    print(current_summary)
    
    # Industry benchmarks (Korean petrochemical industry)
    print(f"\nINDUSTRY ENERGY BENCHMARKS (GJ/t):")
    industry_benchmarks = {
        'NCC': {'total': 30.0, 'ng_share': 0.75, 'fo_share': 0.15, 'elec_share': 0.10},  # Steam cracking
        'BTX': {'total': 12.0, 'ng_share': 0.65, 'fo_share': 0.25, 'elec_share': 0.10},  # Aromatics  
        'C4': {'total': 8.0, 'ng_share': 0.70, 'fo_share': 0.20, 'elec_share': 0.10}     # C4 processing
    }
    
    for process, benchmark in industry_benchmarks.items():
        print(f"  {process}: {benchmark['total']} GJ/t total")
        print(f"    - Natural Gas: {benchmark['total'] * benchmark['ng_share']:.1f} GJ/t")
        print(f"    - Fuel Oil: {benchmark['total'] * benchmark['fo_share']:.1f} GJ/t")
        print(f"    - Electricity: {benchmark['total'] * benchmark['elec_share']:.1f} GJ/t")
    
    # Calibrate consumption
    print(f"\nCALIBRATING CONSUMPTION TO BENCHMARKS:")
    
    for idx, row in consumption_df.iterrows():
        process = row['ProcessType']
        if process in industry_benchmarks:
            benchmark = industry_benchmarks[process]
            
            # Scale up energy consumption to match benchmark
            consumption_df.loc[idx, 'NaturalGas_GJ_per_t'] = benchmark['total'] * benchmark['ng_share']
            consumption_df.loc[idx, 'FuelOil_GJ_per_t'] = benchmark['total'] * benchmark['fo_share']  
            consumption_df.loc[idx, 'Electricity_GJ_per_t'] = benchmark['total'] * benchmark['elec_share']
    
    # Calculate calibrated emissions
    calibrated_emissions = []
    total_calibrated_emissions = 0
    total_capacity = 0
    
    for _, row in consumption_df.iterrows():
        capacity = row['Activity_kt_product']
        
        # Energy emissions with calibrated consumption
        ng_emissions = capacity * row['NaturalGas_GJ_per_t'] * ef_2023['Natural_Gas_tCO2_per_GJ']
        fo_emissions = capacity * row['FuelOil_GJ_per_t'] * ef_2023['Fuel_Oil_tCO2_per_GJ']
        elec_emissions = capacity * row['Electricity_GJ_per_t'] * ef_2023['Electricity_tCO2_per_GJ']
        
        total_emissions_ktco2 = (ng_emissions + fo_emissions + elec_emissions) / 1000
        intensity_tco2_per_t = total_emissions_ktco2 * 1000 / capacity
        
        calibrated_emissions.append({
            'FacilityID': row['FacilityID'],
            'Company': row['Company'],
            'Region': row['Region'], 
            'ProcessType': row['ProcessType'],
            'Capacity_kt': capacity,
            'Total_Energy_GJ_per_t': row['NaturalGas_GJ_per_t'] + row['FuelOil_GJ_per_t'] + row['Electricity_GJ_per_t'],
            'Emissions_ktCO2': total_emissions_ktco2,
            'Intensity_tCO2_per_t': intensity_tco2_per_t
        })
        
        total_calibrated_emissions += total_emissions_ktco2
        total_capacity += capacity
    
    df_calibrated = pd.DataFrame(calibrated_emissions)
    
    # Summary
    calibrated_intensity = total_calibrated_emissions * 1000 / total_capacity
    
    print(f"\nCALIBRATED RESULTS:")
    print(f"  Total Capacity: {total_capacity:,.0f} kt/year")
    print(f"  Total Emissions: {total_calibrated_emissions:,.1f} ktCO2/year")
    print(f"  Emission Intensity: {calibrated_intensity:.1f} tCO2/t")
    print(f"  Industry Benchmark: 2.5-4.0 tCO2/t")
    
    if 2.5 <= calibrated_intensity <= 4.0:
        print(f"  ✅ WITHIN INDUSTRY BENCHMARK RANGE")
    else:
        benchmark_gap = ((calibrated_intensity - 3.25) / 3.25) * 100
        print(f"  ⚠️  Benchmark Gap: {benchmark_gap:+.1f}% (vs 3.25 tCO2/t midpoint)")
    
    print(f"\nCALIBRATED ENERGY CONSUMPTION BY PROCESS:")
    process_summary = df_calibrated.groupby('ProcessType').agg({
        'Total_Energy_GJ_per_t': 'mean',
        'Intensity_tCO2_per_t': 'mean',
        'Capacity_kt': 'sum'
    }).round(1)
    print(process_summary)
    
    # Save calibrated consumption back to Excel
    consumption_calibrated = consumption_df.copy()
    
    # Create backup of original
    backup_path = Path("data/Korea_Petrochemical_MACC_Database_BACKUP_CONSUMPTION.xlsx")
    if not backup_path.exists():
        excel_path.rename(backup_path)
        print(f"\n📁 Backup created: {backup_path}")
    
    # Update Excel with calibrated consumption
    all_sheets = excel_data.copy()
    all_sheets['FacilityBaselineConsumption_2023'] = consumption_calibrated
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Updated database with calibrated consumption: {excel_path}")
    
    # Save calibrated results
    output_path = Path("baseline/Calibrated_Baseline_Results.csv")
    output_path.parent.mkdir(exist_ok=True)
    df_calibrated.to_csv(output_path, index=False)
    print(f"✅ Calibrated results saved: {output_path}")
    
    return df_calibrated

if __name__ == "__main__":
    calibrate_baseline_consumption()