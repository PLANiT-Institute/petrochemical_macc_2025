from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from pathlib import Path
import shutil

DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs/debug_macc')
BASE_DIR = OUTPUT_DIR / 'module_01'
MACC_DIR = OUTPUT_DIR / 'module_02'

print("Starting Debug MACC Run...")

# Clean up
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True)

# Run Baseline first (required for MACC)
print(" running Baseline...")
base = BaselineAnalyzer(str(DATA_DIR), str(BASE_DIR))
base.run_complete_analysis()

# Run MACC
print(" running MACC...")
macc = MACCAnalyzer(str(BASE_DIR), str(DATA_DIR), str(MACC_DIR))
macc.run_complete_analysis()

print("Debug MACC Run Complete")
