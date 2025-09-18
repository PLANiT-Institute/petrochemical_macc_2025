#!/usr/bin/env python3
"""
Calibrate to Korea-scale 52 Mt CO₂ breakdown with all facilities active
"""

import pandas as pd

def calibrate_to_korea_scale():
    """Calibrate CI data to match Korea-scale 52 Mt CO₂ breakdown"""
    
    print('=== CALIBRATING TO KOREA-SCALE 52 Mt CO₂ ===')
    
    # Load data
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    facilities_df = all_sheets['source']
    ci_df = all_sheets['CI'].copy()
    
    # Target Korea-scale breakdown (Mt CO₂)
    korea_scale_targets = {
        # Olefins chain: 25-28 Mt
        'Ethylene': 16.5,          # 15-18 Mt
        'Propylene': 8.5,          # 7-10 Mt  
        'Butadiene': 1.5,          # 1-2 Mt
        
        # Aromatics chain: 12-17 Mt (single allocation)
        '벤젠': 3.0,               # Benzene
        '톨루엔': 2.0,             # Toluene
        '자일렌': 1.5,             # Xylene
        'P-X': 7.0,               # PX share 6-10 Mt
        'O-X': 0.5,               # Minor xylene
        'M-X': 0.5,               # Minor xylene
        
        # Polymers utilities: 8-12 Mt (polymerization only)
        'HDPE': 2.0,
        'LDPE': 2.0,
        'L-LDPE': 2.0,
        'PP': 2.5,
        'PS': 1.0,
        'ABS': 0.5,
        
        # Chlor-vinyls & others: 3-5 Mt
        'EDC': 1.5,
        'VCM': 1.0,
        'PVC': 1.0,
        'SM': 0.5
    }
    
    # Calculate current emissions by product
    facilities_df['capacity_1000_t'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    
    # Get current baseline (91 Mt) breakdown by product
    current_emissions = pd.read_csv('outputs/facility_emissions_korea_scale_final.csv')
    current_by_product = current_emissions.groupby('product')['annual_emissions_kt_co2'].sum() / 1000
    
    # Calculate scale factors for each product
    print('PRODUCT-SPECIFIC CALIBRATION:')
    
    total_target = sum(korea_scale_targets.values())
    scale_factors = {}
    
    for product, target_mt in korea_scale_targets.items():
        current_mt = current_by_product.get(product, 0)
        if current_mt > 0:
            scale_factor = target_mt / current_mt
        else:
            scale_factor = 1.0
        
        scale_factors[product] = scale_factor
        print(f'{product:>12}: {current_mt:5.1f} → {target_mt:5.1f} Mt CO₂ (×{scale_factor:.2f})')
    
    # Apply scale factors to CI data
    energy_columns = ['LNG(GJ/t)', '부생가스(GJ/t)', 'LPG-프로판(GJ/t)', 'LPG-부탄(GJ/t)', 
                     '연료가스(Fuel gas mix)(GJ/t)', '중유(Fuel oil)(GJ/t)', '디젤(GJ/t)', '전력(Baseline)(kWh/t)']
    
    for idx, row in ci_df.iterrows():
        product = row['제품']
        
        if product in scale_factors:
            scale_factor = scale_factors[product]
            
            # Scale energy intensities
            for col in energy_columns:
                if col in ci_df.columns and pd.notna(ci_df.loc[idx, col]):
                    current_value = ci_df.loc[idx, col]
                    ci_df.loc[idx, col] = current_value * scale_factor
    
    # Update CI sheet
    all_sheets['CI'] = ci_df
    
    # Save calibrated database
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'\\n✓ CI data calibrated to Korea-scale targets')
    print(f'Target total: {total_target:.1f} Mt CO₂')
    
    # Verify by recalculating emissions
    verify_korea_scale_calibration(total_target)

def verify_korea_scale_calibration(target_total):
    """Verify the calibration by recalculating emissions"""
    
    print('\\n=== VERIFYING KOREA-SCALE CALIBRATION ===')
    
    # Recalculate emissions with updated CI data
    from emission_pathway_analysis import EmissionPathwayAnalyzer
    
    analyzer = EmissionPathwayAnalyzer()
    emissions_df = analyzer.calculate_current_emissions()
    
    total_emissions = emissions_df['annual_emissions_kt_co2'].sum() / 1000
    
    print(f'Recalculated total: {total_emissions:.1f} Mt CO₂')
    print(f'Target: {target_total:.1f} Mt CO₂')
    print(f'Match: {"✓" if abs(total_emissions - target_total) < 2.0 else "⚠"}')
    
    # Chain breakdown
    chain_breakdown = {
        'Olefins': ['Ethylene', 'Propylene', 'Butadiene'],
        'Aromatics': ['벤젠', '톨루엔', '자일렌', 'P-X', 'O-X', 'M-X'],
        'Polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'ABS'],
        'Chlor-vinyls': ['EDC', 'VCM', 'PVC', 'SM']
    }
    
    print('\\nChain breakdown:')
    for chain, products in chain_breakdown.items():
        chain_emissions = emissions_df[emissions_df['product'].isin(products)]['annual_emissions_kt_co2'].sum() / 1000
        print(f'  {chain:>12}: {chain_emissions:5.1f} Mt CO₂')
    
    # Save Korea-scale emissions
    emissions_df.to_csv('outputs/facility_emissions_korea_scale_52mt.csv', index=False)
    print(f'\\n✓ Saved Korea-scale emissions: outputs/facility_emissions_korea_scale_52mt.csv')
    
    return emissions_df

if __name__ == "__main__":
    calibrate_to_korea_scale()