from modules.optimization_v2 import CostOptimizerV2
from pathlib import Path
import shutil

OUTPUT_DIR = Path('outputs/debug_macc')
BASE_DIR = OUTPUT_DIR / 'module_01'
MACC_DIR = OUTPUT_DIR / 'module_02'
OPT_DIR = OUTPUT_DIR / 'module_03'

print("Starting Debug Opt Run...")

# Data must exist from debug_macc_run.py (which used outputs/debug_macc)
if not MACC_DIR.exists():
    print("Error: MACC output not found. Run debug_macc_run.py first.")
    exit(1)

opt = CostOptimizerV2(str(BASE_DIR), str(MACC_DIR), str(OPT_DIR), force_ncc_technology='NCC-Architecture') 
# Wait, force_ncc_technology takes 'NCC-H2' or 'NCC-Electricity'
# I'll try with 'NCC-H2'

opt = CostOptimizerV2(str(BASE_DIR), str(MACC_DIR), str(OPT_DIR), force_ncc_technology='NCC-H2')
opt.run_complete_analysis()

print("Debug Opt Run Complete")
