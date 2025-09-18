#!/usr/bin/env python3
"""
Update MACC for Korea-scale 52 Mt baseline
"""

import pandas as pd

def update_korea_scale_macc():
    """Update MACC for 52 Mt Korea-scale baseline"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    macc_template = all_sheets['MACC_Template'].copy()
    baseline_emissions = 52.0  # Korea-scale
    
    print('=== UPDATING FOR 52 Mt KOREA-SCALE BASELINE ===')
    
    # Scale abatement potentials to 52 Mt baseline (from 49.9 Mt)
    scale_factor = 52.0 / 49.9
    
    for idx, row in macc_template.iterrows():
        current_abatement = row['Abatement_Potential_MtCO2_per_year']
        new_abatement = current_abatement * scale_factor
        macc_template.loc[idx, 'Abatement_Potential_MtCO2_per_year'] = new_abatement
    
    # Sort and recalculate cumulative
    macc_template = macc_template.sort_values('Cost_USD_per_tCO2').reset_index(drop=True)
    macc_template['Cumulative_Abatement_MtCO2_per_year'] = macc_template['Abatement_Potential_MtCO2_per_year'].cumsum()
    
    # Update baseline assumptions
    baseline_assumptions = all_sheets['Baseline_Assumptions']
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Value'
    ] = 52.0
    
    # Save updates
    all_sheets['MACC_Template'] = macc_template
    all_sheets['Baseline_Assumptions'] = baseline_assumptions
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'✓ Updated to {baseline_emissions} Mt CO₂ baseline')
    print(f'Total abatement potential: {macc_template["Abatement_Potential_MtCO2_per_year"].sum():.1f} Mt CO₂/year')
    
    # Show top technologies
    print('\nTop abatement technologies:')
    for _, row in macc_template.head(8).iterrows():
        print(f'  {row["TechID"]}: ${row["Cost_USD_per_tCO2"]:.0f}/tCO₂, {row["Abatement_Potential_MtCO2_per_year"]:.1f} Mt CO₂/year')
    
    return macc_template

if __name__ == "__main__":
    update_korea_scale_macc()