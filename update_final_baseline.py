#!/usr/bin/env python3
"""
Update optimization database with actual 91 Mt baseline
"""

import pandas as pd

def update_final_baseline():
    """Update optimization database with correct 91 Mt baseline"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Update baseline assumptions
    baseline_assumptions = all_sheets['Baseline_Assumptions']
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Value'
    ] = 91.0
    
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Source'
    ] = 'All facilities active (no shutdowns before 2029)'
    
    # Scale MACC Template abatement potentials to 91 Mt baseline
    macc_template = all_sheets['MACC_Template'].copy()
    scale_factor = 91.0 / 52.0  # Previous target was 52 Mt
    
    for idx, row in macc_template.iterrows():
        current_abatement = row['Abatement_Potential_MtCO2_per_year']
        new_abatement = current_abatement * scale_factor
        macc_template.loc[idx, 'Abatement_Potential_MtCO2_per_year'] = new_abatement
    
    # Sort and recalculate cumulative
    macc_template = macc_template.sort_values('Cost_USD_per_tCO2').reset_index(drop=True)
    macc_template['Cumulative_Abatement_MtCO2_per_year'] = macc_template['Abatement_Potential_MtCO2_per_year'].cumsum()
    
    # Save updates
    all_sheets['Baseline_Assumptions'] = baseline_assumptions
    all_sheets['MACC_Template'] = macc_template
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print('=== UPDATED OPTIMIZATION DATABASE ===')
    print(f'Baseline: 91.0 Mt CO₂ (all facilities active until 2029)')
    print(f'Total abatement potential: {macc_template["Abatement_Potential_MtCO2_per_year"].sum():.1f} Mt CO₂/year')
    
    print('\nTop 5 MACC technologies:')
    for _, row in macc_template.head(5).iterrows():
        print(f'  {row["TechID"]}: ${row["Cost_USD_per_tCO2"]:.0f}/tCO₂, {row["Abatement_Potential_MtCO2_per_year"]:.1f} Mt CO₂/year')

if __name__ == "__main__":
    update_final_baseline()