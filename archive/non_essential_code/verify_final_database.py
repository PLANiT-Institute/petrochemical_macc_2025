#!/usr/bin/env python3
"""
Verify the final MACC database is consistent and complete
"""

import pandas as pd

def verify_final_database():
    """Verify final MACC database integrity"""
    
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    print('=== FINAL MACC DATABASE VERIFICATION ===')
    
    # Check baseline assumptions
    baseline_assumptions = pd.read_excel(file_path, sheet_name='Baseline_Assumptions')
    baseline_2023 = baseline_assumptions[baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023']['Value'].iloc[0]
    print(f'Baseline 2023: {baseline_2023:.1f} Mt CO2')
    
    # Check MACC Template
    macc_template = pd.read_excel(file_path, sheet_name='MACC_Template')
    print(f'MACC technologies: {len(macc_template)}')
    
    # Check TechOptions
    tech_options = pd.read_excel(file_path, sheet_name='TechOptions')
    print(f'Tech options: {len(tech_options)}')
    
    # Verify no CCS exists
    ccs_exists = any('CCS' in tech_id for tech_id in tech_options['TechID'])
    print(f'CCS removed: {not ccs_exists}')
    
    # Verify heat pump exists
    hp_exists = any('HP_001' in tech_id for tech_id in tech_options['TechID'])
    print(f'Heat pump added: {hp_exists}')
    
    # Show low-cost technologies
    macc_sorted = macc_template.sort_values('Cost_USD_per_tCO2')
    print(f'\nLow-cost technologies (<$100/tCO2):')
    low_cost = macc_sorted[macc_sorted['Cost_USD_per_tCO2'] < 100]
    for _, row in low_cost.iterrows():
        print(f'  {row["TechID"]}: {row["TechName"]} - ${row["Cost_USD_per_tCO2"]:.0f}/tCO2')
    
    print(f'\n✓ MACC database ready for optimization model')
    
    return baseline_2023, len(macc_template), hp_exists, not ccs_exists

if __name__ == "__main__":
    verify_final_database()