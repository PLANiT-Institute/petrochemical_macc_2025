"""
JCP PAPER EXPERIMENT RUNNER
===========================
This script runs the specific scenarios used for the Journal of Cleaner Production paper.
It ensures reproducibility by freezing the scenario definitions and outputting to a dedicated folder.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utils import DataLoader
from run_scenarios import load_data, run_scenario

# Configuration
OUTPUT_DIR = Path('paper_jcp/results')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Define Paper Scenarios explicitly
PAPER_SCENARIOS = [
    {
        "name": "S1_Baseline_Trends",
        "description": "Current trends (2.0C target, standard params)",
        "production": "shaheen",
        "ncc_tech": "NCC-Electricity", # Default assumed tech for cost basis
        "price_scenario": "rising_coupled", # Default price assumption
        "carbon_pathway": "2.0C"
    },
    {
        "name": "S2_NetZero_HighAmbition",
        "description": "1.5C target with accelerated transition",
        "production": "shaheen",
        "ncc_tech": "NCC-Electricity",
        "price_scenario": "rising_coupled",
        "carbon_pathway": "1.5C"
    },
    {
        "name": "S3_Tech_Constraints",
        "description": "1.5C target but with higher reliance on Hydrogen vs Electrification",
        "production": "shaheen", 
        "ncc_tech": "NCC-H2", 
        "price_scenario": "rising_coupled",
        "carbon_pathway": "1.5C"
    }
]

def main():
    print("Initializing JCP Paper Experiments...")
    
    # Load Data (using the shared data loader to ensure consistency)
    data = load_data(validate=True)
    
    years = list(range(2025, 2051))
    
    all_results = []
    
    for scenario in PAPER_SCENARIOS:
        print(f"\nProcessing Paper Scenario: {scenario['name']}")
        
        # Run Simulation
        results = run_scenario(scenario, data, years)
        
        # Save individual results
        df = pd.DataFrame(results)
        filename = OUTPUT_DIR / f"{scenario['name']}.csv"
        df.to_csv(filename, index=False)
        print(f"  Saved to {filename}")
        
        all_results.extend(results)
        
    # Save Consolidated Results
    combined_df = pd.DataFrame(all_results)
    combined_df.to_csv(OUTPUT_DIR / "jcp_consolidated_results.csv", index=False)
    print(f"\nAll experiments completed. Consolidated results saved to {OUTPUT_DIR / 'jcp_consolidated_results.csv'}")

if __name__ == "__main__":
    main()
