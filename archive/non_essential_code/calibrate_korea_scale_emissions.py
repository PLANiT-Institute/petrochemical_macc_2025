#!/usr/bin/env python3
"""
Calibrate emissions to match Korea-scale breakdown:
- Olefins chain: 25-28 Mt (target: 26.5 Mt)
- Aromatics chain: 12-17 Mt (target: 14.5 Mt)  
- Polymers chain: 8-12 Mt (target: 10 Mt)
- Chlor-vinyls & others: 3-5 Mt (target: 4 Mt)
Total target: ~55 Mt CO₂
"""

import pandas as pd
import numpy as np

def calibrate_korea_scale():
    """Calibrate to Korea-scale emission breakdown"""
    
    print('=== CALIBRATING TO KOREA-SCALE EMISSIONS ===')
    
    # Load current data
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    ci_df = all_sheets['CI'].copy()
    facilities_df = all_sheets['source']
    
    # Target emissions by chain (Mt CO₂)
    targets = {
        'olefins': 26.5,      # Ethylene ~17 Mt, Propylene ~8 Mt, C4s ~1.5 Mt  
        'aromatics': 14.5,    # PX ~8 Mt, Benzene ~3 Mt, Toluene ~2 Mt, Xylene ~1.5 Mt
        'polymers': 10.0,     # Polymerization utilities only
        'chlor_vinyls': 4.0   # EDC/VCM/PVC, SM, etc.
    }
    
    # Product categorization
    product_chains = {
        'olefins': ['Ethylene', 'Propylene', 'Butadiene'],
        'aromatics': ['벤젠', '톨루엔', '자일렌', 'P-X', 'O-X', 'M-X'],
        'polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'ABS', 'EPS', 'PMMA', 'PC', 'PA'],
        'chlor_vinyls': ['EDC', 'VCM', 'PVC', 'SM', 'AN', 'MMA']
    }
    
    # Calculate current emissions by chain
    current_baseline = pd.read_csv('outputs/facility_emissions_final_realistic.csv')
    current_by_chain = {}
    
    for chain, products in product_chains.items():
        current_emissions = current_baseline[current_baseline['product'].isin(products)]['annual_emissions_kt_co2'].sum() / 1000
        current_by_chain[chain] = current_emissions
        scale_factor = targets[chain] / current_emissions if current_emissions > 0 else 1.0
        print(f'{chain.title()} chain: {current_emissions:.1f} → {targets[chain]:.1f} Mt CO₂ (scale: {scale_factor:.2f}x)')
    
    print()
    
    # Apply scaling factors to CI data
    chain_scale_factors = {
        'olefins': targets['olefins'] / current_by_chain['olefins'],
        'aromatics': targets['aromatics'] / current_by_chain['aromatics'], 
        'polymers': targets['polymers'] / current_by_chain['polymers'],
        'chlor_vinyls': targets['chlor_vinyls'] / current_by_chain['chlor_vinyls']
    }
    
    # Energy columns to scale
    energy_columns = ['LNG(GJ/t)', '부생가스(GJ/t)', 'LPG-프로판(GJ/t)', 'LPG-부탄(GJ/t)', 
                     '연료가스(Fuel gas mix)(GJ/t)', '중유(Fuel oil)(GJ/t)', '디젤(GJ/t)', '전력(Baseline)(kWh/t)']
    
    for idx, row in ci_df.iterrows():
        product = row['제품']
        
        # Determine which chain this product belongs to
        scale_factor = 1.0
        for chain, products in product_chains.items():
            if product in products:
                scale_factor = chain_scale_factors[chain]
                break
        
        # Scale energy intensities
        if scale_factor != 1.0:
            for col in energy_columns:
                if col in ci_df.columns and pd.notna(ci_df.loc[idx, col]):
                    ci_df.loc[idx, col] = ci_df.loc[idx, col] * scale_factor
    
    # Update CI sheet
    all_sheets['CI'] = ci_df
    
    # Save calibrated database
    calibrated_file = 'data/korean_petrochemical_korea_scale_baseline.xlsx'
    with pd.ExcelWriter(calibrated_file, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'✓ Saved Korea-scale calibrated database: {calibrated_file}')
    
    # Recalculate emissions with new CI data
    calculate_korea_scale_emissions(calibrated_file)
    
    return calibrated_file

def calculate_korea_scale_emissions(data_file):
    """Calculate emissions with Korea-scale calibrated data"""
    
    print('\n=== RECALCULATING WITH KOREA-SCALE CI DATA ===')
    
    # Load calibrated data
    facilities_df = pd.read_excel(data_file, sheet_name='source')
    ci_df = pd.read_excel(data_file, sheet_name='CI')
    ci2_df = pd.read_excel(data_file, sheet_name='CI2')
    
    # Clean capacity data
    facilities_df['capacity_1000_t'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    active_facilities = facilities_df[facilities_df['capacity_1000_t'] > 0]
    
    # Create CI mapping
    ci_map = {}
    for _, row in ci_df.iterrows():
        key = (row['제품'], row['공정'])
        ci_map[key] = {
            'LNG_GJ_per_t': row.get('LNG(GJ/t)', 0) or 0,
            'electricity_kWh_per_t': row.get('전력(Baseline)(kWh/t)', 0) or 0,
            'fuel_gas_GJ_per_t': row.get('연료가스(Fuel gas mix)(GJ/t)', 0) or 0,
            'fuel_oil_GJ_per_t': row.get('중유(Fuel oil)(GJ/t)', 0) or 0
        }
    
    # Emission factors
    ef_row = ci2_df.iloc[0]
    emission_factors = {
        'LNG': 0.056,
        'electricity': 0.0045, 
        'fuel_gas': 0.058,
        'fuel_oil': 0.077
    }
    
    # Calculate emissions
    emissions_data = []
    total_emissions = 0
    
    for _, facility in active_facilities.iterrows():
        product = facility['products']
        process = facility['process']
        capacity_kt = facility['capacity_1000_t']
        
        # Find CI data
        ci_key = (product, process)
        if ci_key in ci_map:
            ci_data = ci_map[ci_key]
        else:
            # Fallback to product-only match
            product_matches = [k for k in ci_map.keys() if k[0] == product]
            if product_matches:
                ci_data = ci_map[product_matches[0]]
            else:
                ci_data = {'LNG_GJ_per_t': 8.0, 'electricity_kWh_per_t': 400.0, 'fuel_gas_GJ_per_t': 4.0, 'fuel_oil_GJ_per_t': 1.0}
        
        # Calculate emissions
        annual_production_kt = capacity_kt
        
        lng_emissions = ci_data['LNG_GJ_per_t'] * annual_production_kt * emission_factors['LNG']
        electricity_emissions = ci_data['electricity_kWh_per_t'] * annual_production_kt * emission_factors['electricity']
        fuel_gas_emissions = ci_data['fuel_gas_GJ_per_t'] * annual_production_kt * emission_factors['fuel_gas']
        fuel_oil_emissions = ci_data['fuel_oil_GJ_per_t'] * annual_production_kt * emission_factors['fuel_oil']
        
        total_emissions_kt = lng_emissions + electricity_emissions + fuel_gas_emissions + fuel_oil_emissions
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
            'emission_intensity_t_co2_per_t': total_emissions_kt / capacity_kt if capacity_kt > 0 else 0
        })
    
    emissions_df = pd.DataFrame(emissions_data)
    
    # Save Korea-scale emissions
    emissions_df.to_csv('outputs/facility_emissions_korea_scale.csv', index=False)
    
    print(f'Korea-scale Total Emissions: {total_emissions/1000:.1f} Mt CO₂')
    
    # Breakdown by chain
    product_chains = {
        'Olefins': ['Ethylene', 'Propylene', 'Butadiene'],
        'Aromatics': ['벤젠', '톨루엔', '자일렌', 'P-X', 'O-X', 'M-X'],
        'Polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'ABS', 'EPS', 'PMMA', 'PC', 'PA'],
        'Chlor-vinyls': ['EDC', 'VCM', 'PVC', 'SM', 'AN', 'MMA']
    }
    
    print('\nKOREA-SCALE BREAKDOWN:')
    chain_total = 0
    for chain, products in product_chains.items():
        chain_emissions = emissions_df[emissions_df['product'].isin(products)]['annual_emissions_kt_co2'].sum() / 1000
        chain_total += chain_emissions
        print(f'  {chain}: {chain_emissions:.1f} Mt CO₂')
    
    other_emissions = total_emissions/1000 - chain_total
    print(f'  Other/unclassified: {other_emissions:.1f} Mt CO₂')
    print(f'  TOTAL: {total_emissions/1000:.1f} Mt CO₂')
    
    return emissions_df

if __name__ == "__main__":
    calibrate_korea_scale()