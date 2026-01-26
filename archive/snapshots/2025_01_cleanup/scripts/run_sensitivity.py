
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from modules.utils import StrandedAssetCalculator, DataLoader

# Configuration
OUTPUT_DIR = Path('outputs')
FIG_DIR = OUTPUT_DIR / 'figures'
FIG_DIR.mkdir(exist_ok=True)

plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.family'] = 'sans-serif'

def run_sensitivity():
    print("Running Sensitivity Analysis...")
    
    # Load Base Data
    # data = DataLoader().load_data() # Removed this line as it causes error and is not needed
    
    # Need to manually construct/load necessary data since we are bypassing run_scenarios
    db_facilities = pd.read_csv('outputs/stranded_assets_facilities.csv') # Use output to get the right list incl shaheen
    # But wait, output has results. We need the facility attributes.
    # actually, run_scenarios.py logic for shaheen was adding rows.
    # Let's use the 'outputs/stranded_assets_facilities.csv' for the facility list,
    # as it represents the 'shaheen_ncc_h2' state we care about.
    
    # Filter for Shaheen Scenario
    base_df = pd.read_csv('outputs/stranded_assets_facilities.csv')
    base_df = base_df[base_df['scenario'] == 'shaheen_ncc_h2'].copy()
    
    # We need to recalculate value based on different params.
    # Base params: Life=40, Recovery=0
    
    # Define Sensitivities
    cases = [
        {'name': 'Base Case (40y)', 'life': 40, 'recovery': 0.0},
        {'name': 'Short Life (30y)', 'life': 30, 'recovery': 0.0},
        {'name': 'Long Life (50y)', 'life': 50, 'recovery': 0.0},
        {'name': 'High Recovery (20%)', 'life': 40, 'recovery': 0.2},
    ]
    
    results = []
    
    # Stranding Year is fixed for the scenario (e.g. 2029)
    # Let's get the stranding year from the data
    stranding_year = base_df['stranding_year'].iloc[0] # All rows have same stranding year for this scenario
    
    print(f"Stranding Year (Fixed): {stranding_year}")
    
    # Load Valuation Params (Capex)
    val_params = pd.read_csv('data/asset_valuation_params.csv').set_index('process')
    
    for case in cases:
        total_value = 0
        life = case['life']
        recovery = case['recovery']
        
        for _, row in base_df.iterrows():
            process = row['process']
            
            # Get Params
            if process in val_params.index:
                capex = val_params.loc[process, 'overnight_capex_usd_per_ton']
            else:
                capex = val_params.loc['Other', 'overnight_capex_usd_per_ton']
            
            # Calc
            # Note: inputs in output csv might be formatted differently or missing columns if derived
            # We need capacity in tons. 
            # In output csv: 'stranded_value_usd' is result.
            # But we have 'facility_id' etc. 
            # The output csv doesn't have 'capacity_tpy'.
            # We should join with original inputs.
            # This is getting complicated.
            
            # BETTER APPROACH: Use the calculator logic directly on a reconstructed dataframe
            pass
            
    # RESTARTING LOGIC TO BE ROBUST
    # 1. Load Facility DB + Shaheen Rows
    db = pd.read_csv('data/facility_database_with_regions.csv')
    shaheen_rows = [
        {'facility_id': 'SHAHEEN_1', 'company': 'S-Oil', 'product': 'Ethylene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 1800, 'year_built': 2026},
        {'facility_id': 'SHAHEEN_2', 'company': 'S-Oil', 'product': 'Propylene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 750, 'year_built': 2026},
        {'facility_id': 'SHAHEEN_3', 'company': 'S-Oil', 'product': 'Butadiene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 200, 'year_built': 2026},
        {'facility_id': 'SHAHEEN_4', 'company': 'S-Oil', 'product': 'Benzene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 280, 'year_built': 2026},
        {'facility_id': 'SHAHEEN_5', 'company': 'S-Oil', 'product': 'Toluene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 200, 'year_built': 2026},
        {'facility_id': 'SHAHEEN_6', 'company': 'S-Oil', 'product': 'Xylene', 'process': 'Naphtha Cracker', 'region': 'Ulsan', 'capacity_kt': 350, 'year_built': 2026}
    ]
    db_full = pd.concat([db, pd.DataFrame(shaheen_rows)], ignore_index=True)
    db_full['capacity_tpy'] = db_full['capacity_kt'] * 1000
    
    # Valuation Data
    val_params = pd.read_csv('data/asset_valuation_params.csv').set_index('process')
    
    for case in cases:
        total_risk = 0
        NAME = case['name']
        LIFE = case['life']
        REC = case['recovery']
        
        for _, row in db_full.iterrows():
            proc = row.get('process', 'Other')
            if proc in val_params.index:
                capex = val_params.loc[proc, 'overnight_capex_usd_per_ton']
            else:
                capex = val_params.loc['Other', 'overnight_capex_usd_per_ton']
            
            year_built = row['year_built']
            cap = row['capacity_tpy']
            
            # Depreciation Logic
            replacement_val = capex * cap
            age = stranding_year - year_built
            remaining_life = LIFE - age
            
            if remaining_life <= 0:
                book_val = 0
            else:
                gross_bv = replacement_val * (remaining_life / LIFE)
                recoverable = replacement_val * REC
                # Net Loss = Book Value - Recoverable Amount
                # If Rec > Book Value, loss is 0.
                loss = max(0, gross_bv - recoverable)
                book_val = loss
            
            total_risk += book_val
            
        results.append({'Case': NAME, 'Risk ($B)': total_risk / 1e9})
        
    df_res = pd.DataFrame(results)
    print(df_res)
    
    # Plot Tornado
    base_val = df_res[df_res['Case'] == 'Base Case (40y)']['Risk ($B)'].iloc[0]
    df_res['Delta from Base'] = df_res['Risk ($B)'] - base_val
    
    # Aesthetic Update
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    plt.figure(figsize=(10, 6), dpi=300)
    
    df_res = df_res.sort_values('Risk ($B)', ascending=True)
    
    # Strictly define colors
    final_colors = []
    for r in df_res['Risk ($B)']:
        if abs(r - base_val) < 0.01: final_colors.append('#1f77b4') # Base (Blue)
        elif r < base_val: final_colors.append('#2ca02c') # Less Risk (Green)
        else: final_colors.append('#d62728') # More Risk (Red)
    
    plt.barh(df_res['Case'], df_res['Risk ($B)'], color=final_colors, edgecolor='none', height=0.6)
    plt.axvline(base_val, color='#333333', linestyle='--', alpha=0.7, label='Base Outcome')
    
    plt.title('Sensitivity of Total Risk to Valuation Assumptions', fontweight='bold', pad=15)
    plt.xlabel('Stranded Book Value ($ Billion)')
    plt.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(df_res['Risk ($B)']):
        plt.text(v + 0.3, i, f'${v:.1f}B', va='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'sensitivity_tornado.png')
    print("Generated distinct sensitivity_tornado.png")

if __name__ == "__main__":
    run_sensitivity()
