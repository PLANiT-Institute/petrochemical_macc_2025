from modules.baseline import BaselineAnalyzer
from pathlib import Path

DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs/debug_baseline')

print("Starting Debug Baseline Run...")
base = BaselineAnalyzer(str(DATA_DIR), str(OUTPUT_DIR))
base.run_complete_analysis()
print("Debug Baseline Run Complete")
