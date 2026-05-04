import sys
import shutil
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
STREAMLIT_DIR = Path('streamlit_data')

def run_update():
    print("="*80)
    print("UPDATING SYSTEM TO 2024 BASELINE")
    print("="*80)

    # 1. Run Baseline (Module 01)
    print("\n>>> Module 1: Baseline Analysis")
    base_dir = OUTPUT_DIR / 'module_01'
    base = BaselineAnalyzer(str(DATA_DIR), str(base_dir))
    base.run_complete_analysis()

    # 2. Run MACC (Module 02)
    print("\n>>> Module 2: MACC Analysis")
    macc_dir = OUTPUT_DIR / 'module_02'
    macc = MACCAnalyzer(str(base_dir), str(DATA_DIR), str(macc_dir))
    macc.run_complete_analysis()

    # 3. Run Optimization (Module 03) - Standard Scenario (NCC-Electricity preferred)
    print("\n>>> Module 3: Optimization (Net Zero Pathway)")
    opt_dir = OUTPUT_DIR / 'module_03'
    # Use NCC-Electricity as it's the dominant tech in the report
    opt = CostOptimizerV2(str(base_dir), str(macc_dir), str(opt_dir), forced_ncc_tech='NCC-Electricity')
    opt.run_complete_analysis()

    # 4. Update Streamlit Data
    print("\n>>> Updating Streamlit Data...")
    STREAMLIT_DIR.mkdir(exist_ok=True)
    
    files_to_copy = [
        (base_dir / 'bau_trajectory_2025_2050.csv', 'bau_trajectory_2025_2050.csv'),
        (base_dir / 'baseline_2025_detailed.csv', 'baseline_2025_detailed.csv'),
        (opt_dir / 'optimization_trajectory.csv', 'optimization_trajectory.csv'),
        (opt_dir / 'macc_annual_2025_2050.csv', 'macc_annual_2025_2050.csv'),
        # Add others if needed by Streamlit
        (base_dir / 'emissions_by_product.csv', 'emissions_by_product.csv'),
        (base_dir / 'emissions_by_company.csv', 'emissions_by_company.csv'),
    ]

    for src, dst_name in files_to_copy:
        if src.exists():
            shutil.copy(src, STREAMLIT_DIR / dst_name)
            print(f"  - Copied {dst_name}")
        else:
            print(f"  ! Warning: {src} not found")

    # 5. Generate Excel Report
    print("\n>>> Generating Excel Report...")
    try:
        subprocess.run([sys.executable, 'generate_report.py'], check=True)
        print("  - Report generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"  ! Error generating report: {e}")

    print("\n" + "="*80)
    print("SYSTEM UPDATE COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_update()
