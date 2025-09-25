#!/usr/bin/env python3
"""
Fix MACC Template by recreating it from TechOptions data
"""

import pandas as pd
import numpy as np

def fix_macc_template():
    """Fix MACC Template by recreating from TechOptions"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    # Read all sheets
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Get tech options
    tech_options = all_sheets['TechOptions']
    baseline_emissions = 49.9  # Mt CO2
    
    print('=== RECREATING MACC TEMPLATE ===')
    print(f'Technologies: {len(tech_options)}')
    
    # Create MACC data from TechOptions
    macc_data = []
    
    for _, tech in tech_options.iterrows():
        tech_id = tech['TechID']
        tech_name = tech['TechName']
        
        # Calculate cost and abatement for each technology
        if tech_id == 'HP_001':
            # Heat pump - already calculated
            cost = 10
            abatement = 7.5
        elif tech_id == 'EE_001':
            # Energy efficiency - profitable
            cost = -69
            abatement = baseline_emissions * 0.3  # 30% potential
        elif 'ETH_' in tech_id:
            # Ethylene technologies
            cost = {'ETH_001': 579, 'ETH_002': 795, 'ETH_003': 254, 'ETH_004': 359}.get(tech_id, 400)
            abatement = baseline_emissions * 0.15  # 15% of baseline each
        elif 'PROP_' in tech_id:
            # Propylene technologies
            cost = {'PROP_001': 388, 'PROP_002': 264}.get(tech_id, 350)
            abatement = baseline_emissions * 0.12
        elif 'BTX_' in tech_id:
            # Aromatics
            cost = {'BTX_001': 1167, 'BTX_002': 1594}.get(tech_id, 1000)
            abatement = baseline_emissions * 0.08
        elif 'PE_' in tech_id:
            # Polyethylene
            cost = {'PE_001': 361, 'PE_002': 209}.get(tech_id, 300)
            abatement = baseline_emissions * 0.05
        elif tech_id == 'PP_001':
            # Polypropylene
            cost = 405
            abatement = baseline_emissions * 0.04
        elif tech_id == 'PX_001':
            # p-Xylene
            cost = 520
            abatement = baseline_emissions * 0.03
        elif tech_id == 'TPA_001':
            # TPA
            cost = 171
            abatement = baseline_emissions * 0.02
        elif tech_id == 'H2_001':
            # Green hydrogen
            cost = 503
            abatement = baseline_emissions * 0.25
        else:
            # Default values
            cost = 400
            abatement = baseline_emissions * 0.05
        
        macc_data.append({
            'TechID': tech_id,
            'TechName': tech_name,
            'Cost_USD_per_tCO2': cost,
            'Abatement_Potential_MtCO2_per_year': abatement,
            'Cumulative_Abatement_MtCO2_per_year': 0,  # Will calculate below
            'TRL': tech.get('TRL', 7),
            'Commercial_Year': tech.get('StartYear_Commercial', 2030),
            'Notes': tech.get('Notes', '')
        })
    
    # Create DataFrame and sort by cost
    macc_df = pd.DataFrame(macc_data)
    macc_df = macc_df.sort_values('Cost_USD_per_tCO2').reset_index(drop=True)
    
    # Calculate cumulative abatement
    macc_df['Cumulative_Abatement_MtCO2_per_year'] = macc_df['Abatement_Potential_MtCO2_per_year'].cumsum()
    
    # Replace the MACC_Template sheet
    all_sheets['MACC_Template'] = macc_df
    
    # Save updated database
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'✓ MACC Template recreated with {len(macc_df)} technologies')
    
    # Display summary
    print(f'\nMACC SUMMARY:')
    print(f'Total abatement: {macc_df["Abatement_Potential_MtCO2_per_year"].sum():.1f} Mt CO2/year')
    print(f'Cost range: ${macc_df["Cost_USD_per_tCO2"].min():.0f} to ${macc_df["Cost_USD_per_tCO2"].max():.0f}/tCO2')
    
    # Show all technologies
    print(f'\nTechnologies by cost:')
    for _, row in macc_df.iterrows():
        print(f'  {row["TechID"]}: ${row["Cost_USD_per_tCO2"]:.0f}/tCO2, {row["Abatement_Potential_MtCO2_per_year"]:.1f} Mt CO2/year')
    
    return macc_df

if __name__ == "__main__":
    fix_macc_template()