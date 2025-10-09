"""
Fix Emission Targets for Realistic Korean NDC Alignment
======================================================

This script fixes the emission targets to align with Korean petrochemical industry reality:
- Current: ~15 MtCO2 (from our baseline)
- Target trajectory should be aligned with Korean NDC (15%, 50%, 80% reduction by 2030, 2040, 2050)
"""

import pandas as pd
from pathlib import Path

def fix_emission_targets():
    """Fix emission targets to realistic Korean NDC values"""
    
    print("FIXING EMISSION TARGETS FOR KOREAN NDC ALIGNMENT")
    print("=" * 50)
    
    # Load current database
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    # Load all sheets
    with pd.ExcelFile(excel_path) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Current emission targets (wrong)
    current_targets = all_sheets['EmissionsTargets']
    print("Current emission targets:")
    print(current_targets)
    
    # Create realistic targets based on our 14.8 MtCO2 baseline
    baseline_emissions = 14.8  # MtCO2 from our analysis
    
    realistic_targets = pd.DataFrame({
        'Year': [2030, 2035, 2040, 2045, 2050],
        'Target_MtCO2': [
            baseline_emissions * 0.85,  # 15% reduction by 2030
            baseline_emissions * 0.675, # 32.5% reduction by 2035  
            baseline_emissions * 0.50,  # 50% reduction by 2040
            baseline_emissions * 0.325, # 67.5% reduction by 2045
            baseline_emissions * 0.20   # 80% reduction by 2050
        ],
        'Pathway': ['Linear', 'Linear', 'Linear', 'Linear', 'Linear'],
        'Sector': ['Petrochemicals', 'Petrochemicals', 'Petrochemicals', 'Petrochemicals', 'Petrochemicals']
    })
    
    # Round to 1 decimal place
    realistic_targets['Target_MtCO2'] = realistic_targets['Target_MtCO2'].round(1)
    
    print("\nRealistic emission targets (Korean NDC aligned):")
    print(realistic_targets)
    
    # Calculate reduction percentages
    realistic_targets['Reduction_Pct'] = ((baseline_emissions - realistic_targets['Target_MtCO2']) / baseline_emissions * 100).round(1)
    
    print("\nReduction percentages:")
    for _, row in realistic_targets.iterrows():
        print(f"  {row['Year']}: {row['Reduction_Pct']:.1f}% reduction → {row['Target_MtCO2']:.1f} MtCO2")
    
    # Replace in database
    all_sheets['EmissionsTargets'] = realistic_targets
    
    # Create backup
    backup_path = Path("data/Korea_Petrochemical_MACC_Database_BACKUP_TARGETS.xlsx")
    if not backup_path.exists():
        excel_path.rename(backup_path)
        print(f"Backup created: {backup_path}")
    
    # Save updated database
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Updated database saved: {excel_path}")
    print(f"   EmissionsTargets sheet updated with realistic Korean NDC targets")

if __name__ == "__main__":
    fix_emission_targets()