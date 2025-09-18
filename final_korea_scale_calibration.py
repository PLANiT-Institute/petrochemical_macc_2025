#!/usr/bin/env python3
"""
Final precise calibration to Korea-scale targets
"""

import pandas as pd

def final_korea_scale_calibration():
    """Apply precise calibration to match Korea-scale breakdown exactly"""
    
    print('=== FINAL KOREA-SCALE CALIBRATION ===')
    
    # Korea-scale targets (your specification)
    chain_targets = {
        'Olefins': 26.5,      # 25-28 Mt (midpoint)
        'Aromatics': 14.5,    # 12-17 Mt (midpoint)  
        'Polymers': 10.0,     # 8-12 Mt (midpoint)
        'Chlor-vinyls': 4.0   # 3-5 Mt (midpoint)
    }
    
    # Product groupings
    chains = {
        'Olefins': ['Ethylene', 'Propylene', 'Butadiene'],
        'Aromatics': ['벤젠', '톨루엔', '자일렌', 'P-X', 'O-X', 'M-X'],
        'Polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'ABS', 'EPS', 'PMMA'],
        'Chlor-vinyls': ['EDC', 'VCM', 'PVC', 'SM', 'AN']
    }
    
    # Current emissions by product
    emissions_df = pd.read_csv('outputs/facility_emissions_final_realistic.csv')
    current_by_product = emissions_df.groupby('product')['annual_emissions_kt_co2'].sum() / 1000
    
    # Calculate current chain totals
    current_chains = {}
    for chain, products in chains.items():
        current_total = sum(current_by_product.get(product, 0) for product in products)
        current_chains[chain] = current_total
    
    # Calculate scale factors by chain
    scale_factors_by_product = {}
    
    print('CHAIN-LEVEL CALIBRATION:')
    for chain, target in chain_targets.items():
        current = current_chains[chain]
        if current > 0:
            chain_scale = target / current
            print(f'{chain:>12}: {current:5.1f} → {target:5.1f} Mt CO₂ (×{chain_scale:.2f})')
            
            # Apply scale factor to all products in this chain
            for product in chains[chain]:
                scale_factors_by_product[product] = chain_scale
        else:
            print(f'{chain:>12}: No emissions found')
    
    # Load CI data and apply scaling
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    ci_df = all_sheets['CI'].copy()
    
    # Apply product-specific scale factors
    energy_columns = ['LNG(GJ/t)', '부생가스(GJ/t)', 'LPG-프로판(GJ/t)', 'LPG-부탄(GJ/t)', 
                     '연료가스(Fuel gas mix)(GJ/t)', '중유(Fuel oil)(GJ/t)', '디젤(GJ/t)', '전력(Baseline)(kWh/t)']
    
    for idx, row in ci_df.iterrows():
        product = row['제품']
        
        if product in scale_factors_by_product:
            scale_factor = scale_factors_by_product[product]
            
            # Scale energy intensities
            for col in energy_columns:
                if col in ci_df.columns and pd.notna(ci_df.loc[idx, col]):
                    current_value = ci_df.loc[idx, col]
                    ci_df.loc[idx, col] = float(current_value * scale_factor)
    
    # Update sheets
    all_sheets['CI'] = ci_df
    
    # Update baseline to total target (55 Mt)
    target_total = sum(chain_targets.values())
    baseline_assumptions = all_sheets['Baseline_Assumptions']
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Value'
    ] = target_total
    
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Source'
    ] = 'Korea-scale defensible breakdown (plant-gate intensities, no double counting)'
    
    all_sheets['Baseline_Assumptions'] = baseline_assumptions
    
    # Save calibrated database
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'\\n✓ Final Korea-scale calibration applied')
    print(f'Target total: {target_total:.1f} Mt CO₂')
    
    # Verify calibration
    verify_final_calibration(target_total, chain_targets, chains)

def verify_final_calibration(target_total, chain_targets, chains):
    """Verify the final calibration"""
    
    print('\\n=== VERIFYING FINAL CALIBRATION ===')
    
    # Recalculate emissions
    from emission_pathway_analysis import EmissionPathwayAnalyzer
    
    analyzer = EmissionPathwayAnalyzer()
    emissions_df = analyzer.calculate_current_emissions()
    
    total_emissions = emissions_df['annual_emissions_kt_co2'].sum() / 1000
    current_by_product = emissions_df.groupby('product')['annual_emissions_kt_co2'].sum() / 1000
    
    print(f'Recalculated total: {total_emissions:.1f} Mt CO₂')
    print(f'Target total: {target_total:.1f} Mt CO₂')
    
    print('\\nChain verification:')
    for chain, target in chain_targets.items():
        actual = sum(current_by_product.get(product, 0) for product in chains[chain])
        match = "✓" if abs(actual - target) < 1.0 else "⚠"
        print(f'  {chain:>12}: {actual:5.1f} Mt CO₂ (target: {target:.1f}) {match}')
    
    # Save final emissions
    emissions_df.to_csv('outputs/facility_emissions_korea_scale_final.csv', index=False)
    print(f'\\n✓ Saved final Korea-scale emissions')

if __name__ == "__main__":
    final_korea_scale_calibration()