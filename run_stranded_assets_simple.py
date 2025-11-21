"""
Run Simplified Stranded Asset Analysis

Pure emission-path driven retirement model:
- Facilities that cannot meet emission targets → RETIRE
- Stranded Asset = Book Value of Retired Facilities
"""

import pandas as pd
from pathlib import Path
from modules.stranded_assets_simple import StrandedAssetAnalyzerSimple


def load_scenario_deployments(scenarios_list):
    """Load deployment data for scenarios"""
    deployments = {}

    for scenario in scenarios_list:
        filepath = Path(f'outputs/{scenario}/module_03_optimization/policy_target_deployment.csv')

        if filepath.exists():
            df = pd.read_csv(filepath)
            deployments[scenario] = df
            print(f"✓ Loaded: {scenario}")
        else:
            print(f"⚠️  Not found: {scenario}")

    return deployments


def main():
    print("="*80)
    print("SIMPLIFIED STRANDED ASSET ANALYSIS")
    print("Emission-Path Driven Retirement Model")
    print("="*80)

    # Define scenarios
    scenarios = [
        'scenarios_shaheen_ncc_h2',
        'scenarios_shaheen_ncc_elec',
        'scenarios_restructure_25pct_ncc_h2',
        'scenarios_restructure_25pct_ncc_elec',
        'scenarios_restructure_40pct_ncc_h2',
        'scenarios_restructure_40pct_ncc_elec',
    ]

    print(f"\nLoading {len(scenarios)} scenarios...")
    scenario_deployments = load_scenario_deployments(scenarios)

    if not scenario_deployments:
        print("\n❌ No scenario data found.")
        return

    # Initialize analyzer
    analyzer = StrandedAssetAnalyzerSimple(
        baseline_output='outputs/module_01',
        output_dir='outputs/module_04_stranded_assets_simple'
    )

    # Run analysis with 80% threshold
    # (Facilities requiring >80% emission reduction must retire)
    # Lower threshold = more facilities forced to retire
    results = analyzer.run_complete_analysis(
        scenario_deployments,
        retirement_threshold=0.80
    )

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nKey Outputs:")
    print(f"   - facility_book_values.csv")
    print(f"   - stranding_summary_timeline.csv")
    print(f"   - stranding_summary_2050.csv")
    print(f"   - facility_retirement_*.csv (per scenario)")
    print(f"   - Visualizations (PNG)")


if __name__ == '__main__':
    main()
