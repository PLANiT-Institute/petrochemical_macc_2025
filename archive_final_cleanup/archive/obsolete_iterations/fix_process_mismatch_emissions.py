#!/usr/bin/env python3
"""
Fix process mismatch between facilities and CI data
Key issue: BTX Plant products (P-X, O-X, M-X) are classified as 'Utility' in CI sheet
"""

import pandas as pd
import numpy as np

def analyze_current_mismatch():
    """Analyze the current process mismatch"""
    
    facilities_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='source')
    ci_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='CI')
    ci2_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='CI2')
    
    facilities_df['capacity_numeric'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    all_facilities = facilities_df[facilities_df['capacity_numeric'] > 0]
    
    print('=== CURRENT PROCESS MISMATCH ANALYSIS ===')
    
    # Products that are mismatched
    mismatched_products = ['P-X', 'O-X', 'M-X', 'C-H']
    
    for product in mismatched_products:
        facility_data = all_facilities[all_facilities['products'] == product]
        ci_data = ci_df[ci_df['제품'] == product]
        
        if not facility_data.empty and not ci_data.empty:
            facility_process = facility_data['process'].iloc[0]
            ci_process = ci_data['공정'].iloc[0]
            capacity = facility_data['capacity_numeric'].sum()
            
            print(f'{product}:')
            print(f'  Facilities process: {facility_process}')
            print(f'  CI process: {ci_process}')
            print(f'  Total capacity: {capacity:.0f} kt/year')
            print()
    
    return all_facilities, ci_df, ci2_df

def fix_process_assignments():
    """Fix the CI sheet to match facility process assignments"""
    
    all_facilities, ci_df, ci2_df = analyze_current_mismatch()
    
    print('=== FIXING PROCESS ASSIGNMENTS ===')
    
    # Strategy: Update CI sheet to match facility process assignments
    # P-X, O-X, M-X should be BTX Plant process, not Utility
    
    corrected_ci = ci_df.copy()
    
    # Map products to their correct processes based on facilities data
    process_corrections = {
        'P-X': 'BTX Plant',
        'O-X': 'BTX Plant', 
        'M-X': 'BTX Plant',
        'C-H': 'Naphtha Cracker'  # C-H is often a cracker byproduct
    }
    
    # Apply corrections
    for product, correct_process in process_corrections.items():
        mask = corrected_ci['제품'] == product
        if mask.any():
            old_process = corrected_ci.loc[mask, '공정'].iloc[0]
            corrected_ci.loc[mask, '공정'] = correct_process
            print(f'Corrected {product}: {old_process} → {correct_process}')
    
    # Also need to assign appropriate energy intensities for BTX Plant products
    # P-X, O-X, M-X are xylene separation processes - energy intensive
    
    # Update energy intensities to reflect BTX Plant operations
    btx_energy_corrections = {
        'P-X': {
            'LNG(GJ/t)': 0.8,  # Higher for separation process
            '전력(Baseline)(kWh/t)': 450,  # High electricity for separation
            '연료가스(Fuel gas mix)(GJ/t)': 0.2
        },
        'O-X': {
            'LNG(GJ/t)': 0.7,
            '전력(Baseline)(kWh/t)': 350,
            '연료가스(Fuel gas mix)(GJ/t)': 0.15
        },
        'M-X': {
            'LNG(GJ/t)': 0.7,
            '전력(Baseline)(kWh/t)': 350,
            '연료가스(Fuel gas mix)(GJ/t)': 0.15
        },
        'C-H': {
            'LNG(GJ/t)': 0.5,  # Lower for smaller volume product
            '전력(Baseline)(kWh/t)': 200,
            '연료가스(Fuel gas mix)(GJ/t)': 0.1
        }
    }
    
    for product, energy_data in btx_energy_corrections.items():
        mask = corrected_ci['제품'] == product
        if mask.any():
            for energy_type, value in energy_data.items():
                if energy_type in corrected_ci.columns:
                    corrected_ci.loc[mask, energy_type] = value
            print(f'Updated energy intensities for {product}')
    
    return corrected_ci, ci2_df

def calculate_corrected_emissions():
    """Calculate emissions with corrected process assignments"""
    
    corrected_ci, ci2_df = fix_process_assignments()
    
    # Load facilities data
    facilities_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='source')
    facilities_df['capacity_numeric'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    all_facilities = facilities_df[facilities_df['capacity_numeric'] > 0]
    
    print('\n=== CALCULATING CORRECTED EMISSIONS ===')
    
    # Create mapping from corrected CI data
    ci_map = {}
    for _, row in corrected_ci.iterrows():
        key = (row['제품'], row['공정'])
        ci_map[key] = {
            'LNG_GJ_per_t': row.get('LNG(GJ/t)', 0) or 0,
            'electricity_kWh_per_t': row.get('전력(Baseline)(kWh/t)', 0) or 0,
            'fuel_gas_GJ_per_t': row.get('연료가스(Fuel gas mix)(GJ/t)', 0) or 0,
            'fuel_oil_GJ_per_t': row.get('중유(Fuel oil)(GJ/t)', 0) or 0
        }
    
    # Get emission factors from CI2 data
    ef_row = ci2_df.iloc[0]
    emission_factors = {
        'LNG': ef_row.get('LNG( tCO₂/GJ )', 0.056),
        'electricity': ef_row.get('전력(Baseline)( tCO₂/kWh )', 0.45),
        'fuel_gas': ef_row.get('연료가스(Fuel gas mix)( tCO₂/GJ )', 0.058),
        'fuel_oil': ef_row.get('중유(Fuel oil)( tCO₂/GJ )', 0.077)
    }
    
    # Calculate emissions for each facility
    emissions_data = []
    total_emissions = 0
    
    for _, facility in all_facilities.iterrows():
        if facility['capacity_numeric'] == 0:
            continue
            
        product = facility['products']
        process = facility['process']
        capacity_kt = facility['capacity_numeric']
        
        # Find matching CI data
        ci_key = (product, process)
        if ci_key in ci_map:
            ci_data = ci_map[ci_key]
        else:
            # Fallback: look for same product with different process
            product_matches = [k for k in ci_map.keys() if k[0] == product]
            if product_matches:
                ci_key = product_matches[0]
                ci_data = ci_map[ci_key]
            else:
                # Default values for unknown products
                ci_data = {
                    'LNG_GJ_per_t': 2.0,
                    'electricity_kWh_per_t': 300.0,
                    'fuel_gas_GJ_per_t': 1.0,
                    'fuel_oil_GJ_per_t': 0.5
                }
        
        # Calculate annual emissions (kt CO2)
        annual_production_kt = capacity_kt
        
        lng_emissions = (ci_data['LNG_GJ_per_t'] * annual_production_kt * 
                       emission_factors['LNG'])
        
        electricity_emissions = (ci_data['electricity_kWh_per_t'] * annual_production_kt * 
                               emission_factors['electricity'])
        
        fuel_gas_emissions = (ci_data['fuel_gas_GJ_per_t'] * annual_production_kt * 
                            emission_factors['fuel_gas'])
        
        fuel_oil_emissions = (ci_data['fuel_oil_GJ_per_t'] * annual_production_kt * 
                            emission_factors['fuel_oil'])
        
        total_emissions_kt = (lng_emissions + electricity_emissions + 
                            fuel_gas_emissions + fuel_oil_emissions)
        
        total_emissions += total_emissions_kt
        
        emissions_data.append({
            'facility_id': f"{facility['company']}_{facility['location']}_{product}_{facility['year']}",
            'company': facility['company'],
            'location': facility['location'],
            'product': product,
            'process': process,
            'start_year': facility['year'],
            'capacity_kt': capacity_kt,
            'annual_emissions_kt_co2': total_emissions_kt,
            'emission_intensity_t_co2_per_t': total_emissions_kt / capacity_kt if capacity_kt > 0 else 0,
            'lng_emissions': lng_emissions,
            'electricity_emissions': electricity_emissions,
            'fuel_gas_emissions': fuel_gas_emissions,
            'fuel_oil_emissions': fuel_oil_emissions
        })
    
    emissions_df = pd.DataFrame(emissions_data)
    
    print(f'Total emissions (all facilities): {total_emissions/1000:.1f} Mt CO₂')
    print(f'Number of facilities: {len(emissions_df)}')
    
    # Breakdown by product
    product_emissions = emissions_df.groupby('product')['annual_emissions_kt_co2'].sum().sort_values(ascending=False)
    print('\nTop 10 emitting products:')
    for product, emissions in product_emissions.head(10).items():
        print(f'  {product}: {emissions/1000:.1f} Mt CO₂')
    
    return emissions_df, corrected_ci, total_emissions

def save_corrected_data():
    """Save corrected CI data and emissions"""
    
    emissions_df, corrected_ci, total_emissions = calculate_corrected_emissions()
    
    # Save corrected emissions
    emissions_df.to_csv('outputs/facility_emissions_corrected_processes.csv', index=False)
    
    # Save corrected CI data to new Excel file
    original_file = 'data/petro_data_v1.0_final.xlsx'
    
    # Read all other sheets
    with pd.ExcelFile(original_file) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            if sheet_name not in ['CI']:
                all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Add corrected CI sheet
    all_sheets['CI'] = corrected_ci
    
    # Save to new file
    output_file = 'data/petro_data_v1.0_process_corrected.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'\n=== RESULTS SAVED ===')
    print(f'Corrected CI data: {output_file}')
    print(f'Corrected emissions: outputs/facility_emissions_corrected_processes.csv')
    print(f'\nTotal Korean petrochemical emissions: {total_emissions/1000:.1f} Mt CO₂')
    
    return output_file, total_emissions

if __name__ == "__main__":
    save_corrected_data()