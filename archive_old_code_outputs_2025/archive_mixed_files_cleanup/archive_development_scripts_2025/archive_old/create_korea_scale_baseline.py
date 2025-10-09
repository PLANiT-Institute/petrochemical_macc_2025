#!/usr/bin/env python3
"""
Create Korea-scale baseline matching the target breakdown:
Total: ~52 Mt CO₂
- Olefins: 26.5 Mt (Ethylene ~17, Propylene ~8, C4s ~1.5)
- Aromatics: 14.5 Mt (PX ~8, Benzene ~3, others ~3.5)  
- Polymers: 7.0 Mt (polymerization only)
- Chlor-vinyls: 4.0 Mt
"""

import pandas as pd
import numpy as np

def create_korea_scale_baseline():
    """Create Korea-scale baseline with realistic proportions"""
    
    print('=== CREATING KOREA-SCALE BASELINE ===')
    
    # Load original data
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    baseline_df = pd.read_csv('outputs/facility_emissions_final_realistic.csv')
    
    # Target emissions by chain (Mt CO₂) - more conservative
    targets = {
        'Ethylene': 17.0,
        'Propylene': 8.0,
        'Butadiene': 1.5,
        'P-X': 8.0,
        '벤젠': 3.0,
        '톨루엔': 1.5,
        '자일렌': 1.0,
        'O-X': 0.5,
        'M-X': 0.5,
        'HDPE': 1.5,
        'LDPE': 1.2,
        'L-LDPE': 1.3,
        'PP': 2.0,
        'PS': 0.5,
        'ABS': 0.5,
        'EDC': 1.5,
        'VCM': 1.0,
        'PVC': 1.0,
        'SM': 0.5
    }
    
    # Calculate scale factors for each product
    current_emissions = baseline_df.groupby('product')['annual_emissions_kt_co2'].sum() / 1000
    
    print('PRODUCT-SPECIFIC CALIBRATION:')
    calibrated_data = []
    total_target = 0
    
    for product, target_mt in targets.items():
        current_mt = current_emissions.get(product, 0)
        if current_mt > 0:
            scale_factor = target_mt / current_mt
            print(f'{product:>12}: {current_mt:5.1f} → {target_mt:5.1f} Mt CO₂ (×{scale_factor:.2f})')
        else:
            scale_factor = 1.0
            print(f'{product:>12}: {current_mt:5.1f} → {target_mt:5.1f} Mt CO₂ (new)')
        
        # Apply scaling to individual facilities
        product_facilities = baseline_df[baseline_df['product'] == product].copy()
        product_facilities['annual_emissions_kt_co2'] *= scale_factor
        product_facilities['emission_intensity_t_co2_per_t'] *= scale_factor
        
        calibrated_data.append(product_facilities)
        total_target += target_mt
    
    # Add remaining products with minimal scaling
    remaining_products = baseline_df[~baseline_df['product'].isin(targets.keys())].copy()
    remaining_current = remaining_products['annual_emissions_kt_co2'].sum() / 1000
    remaining_target = 52.0 - total_target  # To reach ~52 Mt total
    
    if remaining_current > 0:
        remaining_scale = remaining_target / remaining_current
        remaining_products['annual_emissions_kt_co2'] *= remaining_scale
        remaining_products['emission_intensity_t_co2_per_t'] *= remaining_scale
        print(f'{"Other products":>12}: {remaining_current:5.1f} → {remaining_target:5.1f} Mt CO₂ (×{remaining_scale:.2f})')
    
    calibrated_data.append(remaining_products)
    
    # Combine all calibrated data
    korea_scale_df = pd.concat(calibrated_data, ignore_index=True)
    
    # Save Korea-scale emissions
    korea_scale_df.to_csv('outputs/facility_emissions_korea_scale_final.csv', index=False)
    
    total_korea_scale = korea_scale_df['annual_emissions_kt_co2'].sum() / 1000
    print(f'\nKOREA-SCALE TOTAL: {total_korea_scale:.1f} Mt CO₂')
    
    # Chain breakdown
    chain_breakdown = {
        'Olefins': ['Ethylene', 'Propylene', 'Butadiene'],
        'Aromatics': ['벤젠', '톨루엔', '자일렌', 'P-X', 'O-X', 'M-X'],
        'Polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'ABS', 'EPS'],
        'Chlor-vinyls': ['EDC', 'VCM', 'PVC', 'SM']
    }
    
    print('\nCHAIN BREAKDOWN:')
    for chain, products in chain_breakdown.items():
        chain_emissions = korea_scale_df[korea_scale_df['product'].isin(products)]['annual_emissions_kt_co2'].sum() / 1000
        print(f'  {chain:>12}: {chain_emissions:5.1f} Mt CO₂')
    
    # Others
    other_products = korea_scale_df[~korea_scale_df['product'].isin([p for products in chain_breakdown.values() for p in products])]
    other_emissions = other_products['annual_emissions_kt_co2'].sum() / 1000
    print(f'  {"Others":>12}: {other_emissions:5.1f} Mt CO₂')
    
    # Top 10 products
    print('\nTOP 10 PRODUCTS:')
    top_products = korea_scale_df.groupby('product')['annual_emissions_kt_co2'].sum().sort_values(ascending=False).head(10)
    for product, emissions in top_products.items():
        print(f'  {product:>12}: {emissions/1000:5.1f} Mt CO₂')
    
    # Update baseline assumptions in optimization database
    update_optimization_baseline(total_korea_scale)
    
    return korea_scale_df

def update_optimization_baseline(korea_scale_total):
    """Update optimization database with Korea-scale baseline"""
    
    print(f'\n=== UPDATING OPTIMIZATION DATABASE ===')
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    # Read all sheets
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Update baseline assumptions
    baseline_assumptions = all_sheets['Baseline_Assumptions'].copy()
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Value'
    ] = korea_scale_total
    
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Source'
    ] = 'Korea-scale calibrated baseline (defensible order-of-magnitude)'
    
    all_sheets['Baseline_Assumptions'] = baseline_assumptions
    
    # Save updated database
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'✓ Updated optimization baseline: {korea_scale_total:.1f} Mt CO₂')

if __name__ == "__main__":
    create_korea_scale_baseline()