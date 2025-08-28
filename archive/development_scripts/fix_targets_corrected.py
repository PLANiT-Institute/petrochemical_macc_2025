"""
Fix Emission Targets for Corrected Baseline (40.7 MtCO2)
========================================================

Update emission targets to align with corrected baseline emissions of 40.7 MtCO2.
Korean NDC reductions: 15%, 50%, 80% by 2030, 2040, 2050.
"""

import pandas as pd
from pathlib import Path

def fix_targets_corrected():
    """Fix emission targets for corrected baseline"""
    
    print("FIXING EMISSION TARGETS FOR CORRECTED BASELINE")
    print("=" * 50)
    
    # Load database
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    # Corrected baseline from our analysis
    baseline_emissions = 40.7  # MtCO2 from corrected calculation
    
    print(f"Corrected baseline: {baseline_emissions} MtCO2/year")
    
    # Create realistic targets based on corrected baseline
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
    
    # Calculate reduction percentages
    realistic_targets['Reduction_Pct'] = ((baseline_emissions - realistic_targets['Target_MtCO2']) / baseline_emissions * 100).round(1)
    
    print("\\nCorrected emission targets:")
    print(realistic_targets)
    
    print("\\nReduction percentages:")
    for _, row in realistic_targets.iterrows():
        print(f"  {row['Year']}: {row['Reduction_Pct']:.1f}% reduction → {row['Target_MtCO2']:.1f} MtCO2")
    
    # Update database
    all_sheets = excel_data.copy()
    all_sheets['EmissionsTargets'] = realistic_targets
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\\n✅ Updated database saved: {excel_path}")
    print(f"   EmissionsTargets sheet updated with corrected baseline targets")
    
    return realistic_targets

if __name__ == "__main__":
    fix_targets_corrected()