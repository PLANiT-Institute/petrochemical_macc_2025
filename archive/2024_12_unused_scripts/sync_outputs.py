import shutil
from pathlib import Path

# Paths
OUTPUT_DIR = Path('outputs')
STREAMLIT_DIR = Path('streamlit_data')
STREAMLIT_DIR.mkdir(exist_ok=True)

# Copy summary
src = OUTPUT_DIR / 'scenario_summary_v3.csv'
dst = OUTPUT_DIR / 'scenario_summary_final.csv'
if src.exists():
    shutil.copy(src, dst)
    print(f"Copied {src.name} -> {dst.name}")
else:
    print(f"Error: {src} not found")

# Determine best scenario for "default" data
# Usually Shaheen + NCC-Electricity (Growth + Electrification)
scenario_dir = OUTPUT_DIR / 'scenario_shaheen_ncc_electricity'
if not scenario_dir.exists():
    print("Warning: Shaheen scenario not found, checking others...")
    # fallback to first found
    found = list(OUTPUT_DIR.glob('scenario_*'))
    if found:
        scenario_dir = found[0]
    else:
        print("Error: No scenario outputs found")
        exit(1)

print(f"Using {scenario_dir.name} for default data")

files_to_sync = [
    ('module_01_baseline/bau_trajectory_2025_2050.csv', 'bau_trajectory_2025_2050.csv'),
    ('module_01_baseline/baseline_2025_detailed.csv', 'baseline_2025_detailed.csv'),
    ('module_01_baseline/emissions_by_product.csv', 'emissions_by_product.csv'),
    ('module_01_baseline/emissions_by_company.csv', 'emissions_by_company.csv'),
    ('module_03_optimization/linear_default_deployment.csv', 'optimization_trajectory.csv'), # fallback if policy missing
    ('module_03_optimization/policy_target_deployment.csv', 'optimization_trajectory.csv'),
     ('module_02_macc/macc_annual_2025_2050.csv', 'macc_annual_2025_2050.csv')   
]

# Note: creating optimization_trajectory.csv from policy_target if available
for src_rel, dst_name in files_to_sync:
    src_path = scenario_dir / src_rel
    dst_path = STREAMLIT_DIR / dst_name
    
    if src_path.exists():
        shutil.copy(src_path, dst_path)
        print(f"  Synced {dst_name}")
    else:
        if 'linear_default' in src_rel: continue # fallback, ignore valid miss
        print(f"  Warning: {src_rel} not found")

print("Sync Complete")
