"""
Run Module 4: Stranded Asset Analysis

Calculates stranded assets for Korea's petrochemical industry under various
decarbonization scenarios by analyzing:
- Asset book values
- Retrofit costs
- Premature retirement losses
- Regional and sectoral impacts
"""

import pandas as pd
from pathlib import Path
from modules.stranded_assets import StrandedAssetAnalyzer


def load_scenario_deployments(scenarios_list):
    """Load deployment data for multiple scenarios"""
    deployments = {}

    for scenario in scenarios_list:
        # Convert scenario name to filename format
        filename = scenario.lower().replace(' ', '_').replace('-', '_')
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
    print("KOREA PETROCHEMICAL STRANDED ASSET ANALYSIS")
    print("="*80)

    # Define scenarios to analyze
    scenarios = [
        'scenarios_shaheen_ncc_h2',
        'scenarios_shaheen_ncc_elec',
        'scenarios_restructure_25pct_ncc_h2',
        'scenarios_restructure_25pct_ncc_elec',
        'scenarios_restructure_40pct_ncc_h2',
        'scenarios_restructure_40pct_ncc_elec',
    ]

    print(f"\nAnalyzing {len(scenarios)} scenarios...")

    # Load deployment data
    scenario_deployments = load_scenario_deployments(scenarios)

    if not scenario_deployments:
        print("\n❌ No scenario data found. Please run optimization module first.")
        return

    # Initialize analyzer
    analyzer = StrandedAssetAnalyzer(
        baseline_output='outputs/module_01',
        macc_output='outputs/module_02',
        optimization_output='outputs',
        output_dir='outputs/module_04_stranded_assets'
    )

    # Run complete analysis
    results = analyzer.run_complete_analysis(scenario_deployments)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nKey outputs:")
    print(f"   - Facility asset valuations")
    print(f"   - Stranded asset summary by scenario")
    print(f"   - Regional and sectoral breakdowns")
    print(f"   - Visualizations")
    print(f"\nOutputs saved to: outputs/module_04_stranded_assets/")


if __name__ == '__main__':
    main()
