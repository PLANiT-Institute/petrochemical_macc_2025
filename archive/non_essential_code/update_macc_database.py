#!/usr/bin/env python3
"""
Update MACC database: remove CCS, add heat pump, update with final baseline
"""

import pandas as pd

def update_macc_database():
    """Update MACC database with heat pump and final baseline"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    # Read current data
    with pd.ExcelFile(file_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Load baseline emissions for abatement potential calculation
    baseline_df = pd.read_csv('outputs/facility_emissions_final_realistic.csv')
    total_baseline_emissions = baseline_df['annual_emissions_kt_co2'].sum() / 1000  # Mt CO2
    
    print(f'Total baseline emissions: {total_baseline_emissions:.1f} Mt CO2')
    
    # Update MACC Template with heat pump
    macc_template = all_sheets['MACC_Template'].copy()
    
    # Check if heat pump already exists in MACC_Template
    if 'HP_001' not in macc_template['TechID'].values:
        # Calculate heat pump MACC parameters
        # Heat pump: 15% emission reduction potential across all processes
        hp_abatement_potential = total_baseline_emissions * 0.15  # Mt CO2/year
        
        # Cost calculation for heat pump
        # CAPEX: 85 Million KRW per kt capacity
        # Assuming 10% of total capacity adopts heat pumps
        total_capacity = baseline_df['capacity_kt'].sum() * 0.1  # 10% adoption
        capex_total = 85 * total_capacity  # Million KRW
        
        # Annualized cost (15-year lifetime, 7% discount rate)
        discount_rate = 0.07
        lifetime = 15
        annuity_factor = (discount_rate * (1 + discount_rate)**lifetime) / ((1 + discount_rate)**lifetime - 1)
        annual_cost = capex_total * annuity_factor  # Million KRW/year
        
        # Convert to USD (1 USD = 1300 KRW approximately)
        annual_cost_usd = annual_cost / 1300  # Million USD/year
        
        # Cost per tonne CO2 abated
        cost_per_tco2 = (annual_cost_usd * 1e6) / (hp_abatement_potential * 1e6)  # USD per tCO2
        
        print(f'Heat pump abatement potential: {hp_abatement_potential:.1f} Mt CO2/year')
        print(f'Heat pump cost: ${cost_per_tco2:.0f}/tCO2')
        
        # Add heat pump to MACC Template
        hp_macc_data = {
            'TechID': 'HP_001',
            'TechName': 'Industrial Heat Pump Systems',
            'Cost_USD_per_tCO2': cost_per_tco2,
            'Abatement_Potential_MtCO2_per_year': hp_abatement_potential,
            'Cumulative_Abatement_MtCO2_per_year': 0,  # Will be calculated later
            'TRL': 8,
            'Commercial_Year': 2025,
            'Notes': 'High-temperature heat pumps for process heating'
        }
        
        new_macc_row = pd.DataFrame([hp_macc_data])
        macc_template = pd.concat([macc_template, new_macc_row], ignore_index=True)
        
        # Sort by cost and recalculate cumulative abatement
        macc_template = macc_template.sort_values('Cost_USD_per_tCO2').reset_index(drop=True)
        macc_template['Cumulative_Abatement_MtCO2_per_year'] = macc_template['Abatement_Potential_MtCO2_per_year'].cumsum()
        
        all_sheets['MACC_Template'] = macc_template
        print('✓ Heat pump added to MACC Template')
    else:
        print('Heat pump already exists in MACC Template')
    
    # Update baseline assumptions with final realistic baseline
    baseline_assumptions = all_sheets['Baseline_Assumptions'].copy()
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Value'
    ] = total_baseline_emissions
    
    baseline_assumptions.loc[
        baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023', 'Source'
    ] = 'Final realistic baseline with corrected CI data'
    
    all_sheets['Baseline_Assumptions'] = baseline_assumptions
    
    # Save updated database
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'✓ Updated baseline assumptions: {total_baseline_emissions:.1f} Mt CO2')
    
    # Display final technology list
    tech_options = all_sheets['TechOptions']
    print(f'\nFinal technology list ({len(tech_options)} technologies):')
    for idx, row in tech_options.iterrows():
        print(f'{idx+1:2d}. {row["TechID"]}: {row["TechName"]}')
    
    return total_baseline_emissions

if __name__ == "__main__":
    update_macc_database()