"""
ENHANCED VISUALIZATIONS RUNNER
Generate additional transition visualizations
Run after optimization (Module 3)
"""

import pandas as pd
from pathlib import Path
from modules.visualizations import TransitionVisualizer

def main():
    print("="*80)
    print("GENERATING ENHANCED TRANSITION VISUALIZATIONS")
    print("="*80)

    # Load required data
    print("\n📁 Loading data...")
    baseline_dir = Path('outputs/module_01')
    optimization_dir = Path('outputs/module_03')

    df_baseline = pd.read_csv(baseline_dir / 'baseline_2025_detailed.csv')
    df_trajectory = pd.read_csv(baseline_dir / 'bau_trajectory_2025_2050.csv')

    # Load a scenario deployment (use Moderate as default)
    scenario_files = list(optimization_dir.glob('*_deployment.csv'))
    if len(scenario_files) == 0:
        print("\n⚠️  No optimization scenarios found. Please run Module 3 first.")
        print("   Run: python run_module_03.py")
        return

    print(f"\n   Found {len(scenario_files)} scenario(s)")

    # Initialize visualizer
    viz = TransitionVisualizer(output_dir='outputs/visualizations')

    # Generate visualizations for each scenario
    for scenario_file in scenario_files:
        scenario_name = scenario_file.stem.replace('_deployment', '')
        print(f"\n{'='*80}")
        print(f"Processing scenario: {scenario_name}")
        print(f"{'='*80}")

        df_deployment = pd.read_csv(scenario_file)

        # 1. Energy transition
        try:
            viz.plot_energy_transition(
                df_deployment, df_baseline,
                save_path=viz.output_dir / f'{scenario_name}_energy_transition.png'
            )
        except Exception as e:
            print(f"   ⚠️  Error creating energy transition plot: {e}")

        # 2. Investment timeline
        try:
            viz.plot_investment_timeline(
                df_deployment,
                save_path=viz.output_dir / f'{scenario_name}_investment_timeline.png'
            )
        except Exception as e:
            print(f"   ⚠️  Error creating investment timeline: {e}")

        # 3. Technology deployment
        try:
            viz.plot_technology_deployment(
                df_deployment,
                save_path=viz.output_dir / f'{scenario_name}_technology_deployment.png'
            )
        except Exception as e:
            print(f"   ⚠️  Error creating technology deployment plot: {e}")

        # 4. Facility transition waterfall (for 2050)
        try:
            allocation_file = optimization_dir / f'{scenario_name}_facility_allocation_2050.csv'
            if allocation_file.exists():
                df_allocation = pd.read_csv(allocation_file)
                viz.plot_facility_transition_waterfall(
                    df_baseline, df_allocation, year=2050,
                    save_path=viz.output_dir / f'{scenario_name}_waterfall_2050.png'
                )
            else:
                print(f"   ⚠️  No facility allocation file found for 2050")
        except Exception as e:
            print(f"   ⚠️  Error creating waterfall chart: {e}")

    # 5. Capacity growth (applies to all scenarios - based on BAU trajectory)
    print(f"\n{'='*80}")
    print("Creating capacity growth visualization")
    print(f"{'='*80}")
    try:
        if 'capacity_multiplier' in df_trajectory.columns:
            viz.plot_capacity_growth(
                df_trajectory,
                save_path=viz.output_dir / 'capacity_growth.png'
            )
        else:
            print("   ⚠️  No capacity growth data available (run Module 1 with updated code)")
    except Exception as e:
        print(f"   ⚠️  Error creating capacity growth plot: {e}")

    print("\n" + "="*80)
    print("✅ ENHANCED VISUALIZATIONS COMPLETE")
    print("="*80)
    print(f"\nOutputs saved to: {viz.output_dir}")
    print("\nGenerated visualizations:")
    print("   - Energy transition (fossil → clean energy)")
    print("   - Investment timeline (annual & cumulative)")
    print("   - Technology deployment schedule")
    print("   - Facility transition waterfall charts")
    print("   - Capacity growth over time")

if __name__ == '__main__':
    main()
