#!/usr/bin/env python3
"""
Create Realistic Plant Sizes
============================

Break down mega-facilities into realistic individual plant sizes
to fix the cost calculation issue.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_realistic_plants():
    """Break down facilities into realistic plant sizes"""
    
    print("CREATING REALISTIC PLANT SIZES")
    print("=" * 50)
    
    # Load data
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    facilities_df = excel_data['RegionalFacilities'].copy()
    consumption_df = excel_data['FacilityBaselineConsumption_202'].copy()
    
    print("Current mega-facilities:")
    current_total = consumption_df.groupby('FacilityID')['Activity_kt_product'].sum()
    for facility_id, capacity in current_total.sort_values(ascending=False).items():
        facility_info = facilities_df[facilities_df['FacilityID'] == facility_id].iloc[0]
        print(f"  {facility_id} ({facility_info['Company']}): {capacity:,} kt/year")
    
    # Realistic plant sizes by process type
    realistic_sizes = {
        'NCC': 300,   # kt/year per plant
        'BTX': 250,   # kt/year per plant  
        'C4': 150     # kt/year per plant
    }
    
    print(f"\nBreaking down into realistic plant sizes:")
    for process, size in realistic_sizes.items():
        print(f"  {process}: {size} kt/year per plant")
    
    # Create new plant-level data
    new_facilities = []
    new_consumption = []
    
    facility_counter = 1
    
    for _, facility in facilities_df.iterrows():
        original_id = facility['FacilityID']
        region = facility['Region']
        company = facility['Company']
        
        # Get consumption data for this facility
        facility_consumption = consumption_df[consumption_df['FacilityID'] == original_id]
        
        for _, process in facility_consumption.iterrows():
            process_type = process['ProcessType']
            total_capacity = process['Activity_kt_product']
            
            # Calculate number of plants needed
            plant_size = realistic_sizes[process_type]
            num_plants = max(1, round(total_capacity / plant_size))
            capacity_per_plant = total_capacity / num_plants
            
            print(f"\\n{original_id} {process_type}: {total_capacity:,} kt → {num_plants} plants × {capacity_per_plant:.0f} kt")
            
            # Create individual plants
            for i in range(num_plants):
                plant_id = f"P{facility_counter:03d}"
                plant_name = f"{company} {process_type} Plant {i+1}"
                
                # New facility record
                new_facilities.append({
                    'FacilityID': plant_id,
                    'OriginalFacilityID': original_id,
                    'FacilityName': plant_name,
                    'Company': company,
                    'Region': region,
                    'ProcessType': process_type,
                    'PlantNumber': i + 1
                })
                
                # New consumption record
                new_consumption.append({
                    'FacilityID': plant_id,
                    'ProcessType': process_type,
                    'Activity_kt_product': capacity_per_plant,
                    'NaturalGas_GJ_per_t': process['NaturalGas_GJ_per_t'],
                    'FuelOil_GJ_per_t': process['FuelOil_GJ_per_t'],
                    'Electricity_GJ_per_t': process['Electricity_GJ_per_t'],
                    'Naphtha_t_per_t': process.get('Naphtha_t_per_t', 0),
                    'LPG_t_per_t': process.get('LPG_t_per_t', 0),
                    'Reformate_t_per_t': process.get('Reformate_t_per_t', 0)
                })
                
                facility_counter += 1
    
    # Convert to DataFrames
    new_facilities_df = pd.DataFrame(new_facilities)
    new_consumption_df = pd.DataFrame(new_consumption)
    
    print(f"\\nRESULT:")
    print(f"  Original: 8 mega-facilities → {len(new_facilities_df)} realistic plants")
    print(f"  Capacity verification: {consumption_df['Activity_kt_product'].sum():,} → {new_consumption_df['Activity_kt_product'].sum():.0f} kt/year")
    
    # Show new structure
    print(f"\\nNew plant size distribution:")
    for process_type in ['NCC', 'BTX', 'C4']:
        plants = new_consumption_df[new_consumption_df['ProcessType'] == process_type]
        if len(plants) > 0:
            avg_size = plants['Activity_kt_product'].mean()
            print(f"  {process_type}: {len(plants)} plants, avg {avg_size:.0f} kt/year (range: {plants['Activity_kt_product'].min():.0f}-{plants['Activity_kt_product'].max():.0f})")
    
    # Save updated database
    print(f"\\nSAVING REALISTIC PLANT STRUCTURE...")
    
    # Update sheets
    all_sheets = excel_data.copy()
    all_sheets['RegionalFacilities'] = new_facilities_df
    all_sheets['FacilityBaselineConsumption_202'] = new_consumption_df
    
    # Create backup
    backup_path = Path("data/Korea_Petrochemical_MACC_Database_MEGA_FACILITIES.xlsx")
    if not backup_path.exists():
        excel_path.rename(backup_path)
        print(f"📁 Backup created: {backup_path}")
    
    # Save new version
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Realistic plant structure saved")
    print(f"   • {len(new_facilities_df)} individual plants")
    print(f"   • Typical plant size: 150-300 kt/year")
    print(f"   • Ready for realistic cost calculations")
    
    return new_facilities_df, new_consumption_df

if __name__ == "__main__":
    create_realistic_plants()