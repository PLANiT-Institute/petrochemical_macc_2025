"""
Cost-Optimized Scenario Runner
==============================
Integrates the CostOptimizerV2 module to find least-cost pathways
that meet 2035 and 2050 emission constraints.

Emission Constraints:
- 2035: 43.5 Mt (24.5% reduction from 2018 baseline of 57.6 Mt)
- 2050: 0.0 Mt (Net Zero)

Production Scenarios:
- Shaheen (성장): +15% capacity from 2026
- Restructure 25%: -30.9% capacity from 2026
- Restructure 40%: -40% capacity by 2040

NCC Technologies (mutually exclusive):
- NCC-H2: Hydrogen-based cracking
- NCC-Electricity: Electric cracking
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

print("="*80)
print("COST-OPTIMIZED SCENARIO RUNNER")
print("="*80)

# =============================================================================
# CONFIGURATION
# =============================================================================
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Production scenarios with capacity multipliers
PRODUCTION_SCENARIOS = {
    'shaheen': {
        'name': 'Shaheen (성장)',
        'name_en': 'Shaheen Growth',
        'growth_column': 'scenario_shaheen',
        'description': '+15% capacity from Shaheen project'
    },
    'restructure_25pct': {
        'name': '구조조정 25%',
        'name_en': 'Restructure 25%',
        'growth_column': 'scenario_restructure_25pct',
        'description': '-30.9% capacity reduction'
    },
    'restructure_40pct': {
        'name': '구조조정 40%',
        'name_en': 'Restructure 40%',
        'growth_column': 'scenario_restructure_40pct',
        'description': '-40% capacity reduction by 2040'
    }
}

# NCC Technology options (mutually exclusive)
NCC_TECHNOLOGIES = ['NCC-H2', 'NCC-Electricity']

# Emission constraints (from Korea NDC - emission_scenarios_clean.csv)
# These are ABSOLUTE targets from Korea's policy:
# - 2018 baseline: 57.6 Mt
# - 2035 target: 43.5 Mt (24.5% reduction from 2018)
# - 2050 target: 0.0 Mt (Net Zero)
#
# For each production scenario, we SCALE these targets proportionally
# based on the scenario's BAU relative to baseline BAU

# Load the actual emission constraints from file
df_emission_constraints = pd.read_csv(DATA_DIR / 'emission_scenarios_clean.csv')
POLICY_TARGETS = {}
for _, row in df_emission_constraints.iterrows():
    POLICY_TARGETS[int(row['year'])] = row['target_mt']

print("\nPolicy Emission Targets (from emission_scenarios_clean.csv):")
for year in [2025, 2030, 2035, 2040, 2045, 2050]:
    if year in POLICY_TARGETS:
        print(f"  {year}: {POLICY_TARGETS[year]:.1f} Mt")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def create_scenario_emission_constraints(scenario_id, bau_trajectory):
    """
    Create emission constraints scaled to scenario's BAU

    Uses ACTUAL policy targets from emission_scenarios_clean.csv:
    - 2025: 66.2 Mt (baseline)
    - 2030: 53.3 Mt
    - 2035: 43.5 Mt (24.5% reduction from 2018 baseline of 57.6 Mt)
    - 2040: 26.9 Mt
    - 2045: 13.4 Mt
    - 2050: 0.0 Mt (Net Zero)

    For different production scenarios, scale proportionally:
    - Shaheen: BAU is higher, so targets are scaled UP
    - Restructure: BAU is lower, so targets are scaled DOWN
    """
    constraints = {}

    # Get baseline BAU (2025) from policy file
    policy_baseline_2025 = POLICY_TARGETS[2025]  # 66.2 Mt

    # Get this scenario's BAU at 2025
    scenario_bau_2025 = bau_trajectory[bau_trajectory['year'] == 2025]['total_emissions_mt'].iloc[0]

    # Calculate scaling factor (scenario BAU / policy baseline)
    # For Shaheen: BAU is similar, so scale ~1.0
    # For Restructure: BAU starts same but declines, we scale based on trajectory
    scale_factor_2025 = scenario_bau_2025 / policy_baseline_2025

    # Key years with targets from policy file
    policy_years = sorted(POLICY_TARGETS.keys())

    for year in range(2025, 2051):
        scenario_bau_year = bau_trajectory[bau_trajectory['year'] == year]['total_emissions_mt'].iloc[0]

        if year in POLICY_TARGETS:
            # Use actual policy target, scaled by scenario's BAU ratio
            # Scale factor changes each year based on how scenario BAU compares to baseline BAU
            baseline_bau_year = bau_trajectory[bau_trajectory['year'] == year]['total_emissions_mt'].iloc[0]

            # For year-specific scaling, use ratio of scenario BAU to policy baseline BAU
            # Policy targets assume baseline trajectory, so we scale to scenario trajectory
            year_scale = scenario_bau_year / policy_baseline_2025

            # Target = policy target * (scenario BAU / baseline BAU)
            # But ensure we don't exceed scenario's BAU for that year
            scaled_target = POLICY_TARGETS[year] * year_scale
            constraints[year] = min(scaled_target, scenario_bau_year)
        else:
            # Interpolate between known policy years
            before_years = [y for y in policy_years if y < year]
            after_years = [y for y in policy_years if y > year]

            if before_years and after_years:
                y1 = before_years[-1]
                y2 = after_years[0]

                # Get the scaled targets for surrounding years
                t1 = constraints.get(y1, POLICY_TARGETS[y1] * (scenario_bau_year / policy_baseline_2025))
                t2_raw = POLICY_TARGETS[y2] * (scenario_bau_year / policy_baseline_2025)

                # Linear interpolation
                progress = (year - y1) / (y2 - y1)
                constraints[year] = t1 + (t2_raw - t1) * progress
            else:
                # Fallback
                constraints[year] = scenario_bau_year

    return constraints


def save_scenario_emission_file(scenario_id, constraints, output_path):
    """Save emission constraints to CSV file for optimizer"""
    rows = []
    for year, target in constraints.items():
        rows.append({
            'scenario_name': f'{scenario_id}_target',
            'constraint_type': 'annual_path',
            'year': year,
            'target_mt': target,
            'description': f'Target for {scenario_id}'
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def run_baseline_for_scenario(scenario_id, scenario_config, demand_growth_df):
    """Run baseline calculation with scenario-specific demand growth"""
    print(f"\n{'='*60}")
    print(f"Running baseline for: {scenario_config['name']}")
    print(f"{'='*60}")

    # Create modified demand growth file for this scenario
    growth_column = scenario_config['growth_column']

    # Create demand growth trajectory
    df_growth = pd.DataFrame({
        'year': demand_growth_df['year'],
        'cumulative_capacity_multiplier': demand_growth_df[growth_column],
        'operating_rate_pct': 100.0  # Full operation
    })

    # Save temporary demand growth file
    temp_growth_path = DATA_DIR / f'demand_growth_trajectory_{scenario_id}.csv'
    df_growth.to_csv(temp_growth_path, index=False)

    # Also save as default file for baseline module
    df_growth.to_csv(DATA_DIR / 'demand_growth_trajectory.csv', index=False)

    # Run baseline calculation
    output_dir = OUTPUT_DIR / f'scenario_{scenario_id}' / 'module_01_baseline'
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline = BaselineAnalyzer(
        data_dir=str(DATA_DIR),
        output_dir=str(output_dir)
    )
    baseline.run_complete_analysis()

    # Read BAU trajectory
    bau_trajectory = pd.read_csv(output_dir / 'bau_trajectory_2025_2050.csv')

    return bau_trajectory, output_dir


def run_macc_for_scenario(scenario_id, baseline_dir):
    """Run MACC calculation for scenario"""
    print(f"\nRunning MACC analysis for: {scenario_id}")

    output_dir = OUTPUT_DIR / f'scenario_{scenario_id}' / 'module_02_macc'
    output_dir.mkdir(parents=True, exist_ok=True)

    macc = MACCAnalyzer(
        baseline_output=str(baseline_dir),
        data_dir=str(DATA_DIR),
        output_dir=str(output_dir)
    )
    macc.run_complete_analysis()

    return output_dir


def run_optimization_for_scenario(scenario_id, ncc_tech, baseline_dir, macc_dir, emission_constraints):
    """Run cost optimization with emission constraints"""
    print(f"\nRunning cost optimization: {scenario_id} + {ncc_tech}")

    output_dir = OUTPUT_DIR / f'scenario_{scenario_id}_{ncc_tech.lower().replace("-", "_")}' / 'module_03_optimization'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save emission constraints to file
    constraints_file = output_dir / 'emission_constraints.csv'
    save_scenario_emission_file(scenario_id, emission_constraints, constraints_file)

    # Run optimizer with forced NCC technology
    optimizer = CostOptimizerV2(
        baseline_output=str(baseline_dir),
        macc_output=str(macc_dir),
        output_dir=str(output_dir),
        scenario_file=str(constraints_file),
        force_ncc_technology=ncc_tech
    )

    results = optimizer.run_complete_analysis()

    return results, output_dir


def create_annual_regional_trajectory(scenario_id, ncc_tech, optimization_results, baseline_dir):
    """Create annual regional trajectory from optimization results"""

    # Get deployment data
    scenario_key = f'{scenario_id}_target'
    if scenario_key not in optimization_results:
        scenario_key = list(optimization_results.keys())[0]

    df_deployment = optimization_results[scenario_key]

    # Load baseline facility data
    df_baseline = pd.read_csv(baseline_dir / 'baseline_2025_detailed.csv')

    # Map location to region
    location_to_region = {
        'Daesan': 'Daesan',
        'Yeosu': 'Yeosu',
        'Ulsan': 'Ulsan',
        'Onsan': 'Ulsan',
        'Seosan': 'Daesan',
        'Gunsan': 'Other',
        'Incheon': 'Other'
    }
    df_baseline['region'] = df_baseline['location'].map(location_to_region).fillna('Other')

    # Calculate regional baseline emissions
    regional_baseline = df_baseline.groupby('region').agg({
        'total_emissions_kt': 'sum',
        'capacity_kt': 'sum'
    }).reset_index()

    total_emissions = regional_baseline['total_emissions_kt'].sum()
    regional_baseline['emission_share'] = regional_baseline['total_emissions_kt'] / total_emissions

    # Create annual trajectory
    annual_data = []

    for _, row in df_deployment.iterrows():
        year = row['year']

        for _, reg in regional_baseline.iterrows():
            region = reg['region']
            share = reg['emission_share']

            # Distribute emissions and abatement by regional share
            bau_emissions = row['bau_mt'] * 1000 * share  # kt

            # Technology abatement (distributed by share)
            ncc_abate = (row['ncc_h2_mt'] + row['ncc_elec_mt']) * 1000 * share
            rdh_abate = 0  # RDH not in current optimizer output, would need to add
            hp_abate = row['heat_pump_mt'] * 1000 * share
            re_ppa_abate = row['re_ppa_mt'] * 1000 * share

            total_abate = ncc_abate + rdh_abate + hp_abate + re_ppa_abate
            actual_emissions = max(0, bau_emissions - total_abate)

            # Electricity demand from deployment
            elec_demand = row.get('electricity_consumption_increase_twh', 0) * 1e6 * share  # MWh

            # Grid emission factor for the year
            df_grid = pd.read_csv(DATA_DIR / 'grid_emission_trajectory.csv')
            grid_ef = df_grid[df_grid['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

            annual_data.append({
                'year': year,
                'region': region,
                'n_facilities': int(len(df_baseline[df_baseline['region'] == region])),
                'capacity_kt': reg['capacity_kt'],
                'bau_emissions_kt': bau_emissions,
                'ncc_abatement_kt': ncc_abate,
                'rdh_abatement_kt': rdh_abate,
                'hp_abatement_kt': hp_abate,
                're_ppa_abatement_kt': re_ppa_abate,
                'total_abatement_kt': total_abate,
                'actual_emissions_kt': actual_emissions,
                'elec_demand_mwh': elec_demand,
                'grid_ef': grid_ef
            })

    return pd.DataFrame(annual_data)


def create_scenario_summary(all_results):
    """Create summary of all scenarios"""
    summary = []

    for result in all_results:
        scenario_id = result['scenario_id']
        ncc_tech = result['ncc_tech']
        df_deployment = result['deployment']

        # Get 2050 values
        row_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]
        row_2025 = df_deployment[df_deployment['year'] == 2025].iloc[0]

        summary.append({
            'scenario': result['scenario_name'],
            'technology': ncc_tech,
            'scenario_id': f"{scenario_id}_{ncc_tech.lower().replace('-', '_')}",
            'n_facilities': result.get('n_facilities', 248),
            'n_ncc_facilities': result.get('n_ncc_facilities', 44),
            'n_btx_facilities': result.get('n_btx_facilities', 48),
            'n_utility_facilities': result.get('n_utility_facilities', 156),
            'total_capacity_kt': result.get('total_capacity_kt', 0),
            'ncc_capacity_kt': result.get('ncc_capacity_kt', 0),
            'bau_2050_mt': row_2050['bau_mt'],
            'net_2050_mt': row_2050['actual_emissions_mt'],
            'capex_billion_usd': row_2050['cumulative_capex_musd'] / 1000,
            'ncc_abatement_mt': row_2050['ncc_h2_mt'] + row_2050['ncc_elec_mt'],
            'rdh_abatement_mt': 0,  # Not tracked separately
            'heat_pump_mt': row_2050['heat_pump_mt'],
            're_ppa_mt': row_2050['re_ppa_mt'],
            'h2_demand_kt': row_2050.get('h2_consumption_kt', 0),
            'electricity_twh': row_2050.get('electricity_consumption_increase_twh', 0)
        })

    return pd.DataFrame(summary)


# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    print("\n" + "="*80)
    print("STARTING COST-OPTIMIZED SCENARIO ANALYSIS")
    print("="*80)

    # Load demand growth scenarios
    df_demand_growth = pd.read_csv(DATA_DIR / 'demand_growth_trajectory_scenarios.csv')

    all_results = []

    # Run each production scenario
    for scenario_id, scenario_config in PRODUCTION_SCENARIOS.items():
        print(f"\n{'#'*80}")
        print(f"# PRODUCTION SCENARIO: {scenario_config['name']}")
        print(f"{'#'*80}")

        # Step 1: Run baseline
        bau_trajectory, baseline_dir = run_baseline_for_scenario(
            scenario_id, scenario_config, df_demand_growth
        )

        # Step 2: Create emission constraints scaled to this scenario's BAU
        emission_constraints = create_scenario_emission_constraints(scenario_id, bau_trajectory)

        print(f"\nEmission constraints for {scenario_id}:")
        for year in [2025, 2030, 2035, 2040, 2050]:
            print(f"  {year}: {emission_constraints[year]:.2f} Mt")

        # Step 3: Run MACC
        macc_dir = run_macc_for_scenario(scenario_id, baseline_dir)

        # Step 4: Run optimization for each NCC technology
        for ncc_tech in NCC_TECHNOLOGIES:
            print(f"\n{'-'*60}")
            print(f"NCC Technology: {ncc_tech}")
            print(f"{'-'*60}")

            # Run optimization
            opt_results, opt_dir = run_optimization_for_scenario(
                scenario_id, ncc_tech, baseline_dir, macc_dir, emission_constraints
            )

            # Get deployment data
            scenario_key = list(opt_results.keys())[0]
            df_deployment = opt_results[scenario_key]

            # Create annual regional trajectory
            df_annual = create_annual_regional_trajectory(
                scenario_id, ncc_tech, opt_results, baseline_dir
            )

            # Save outputs
            output_scenario_dir = OUTPUT_DIR / f'scenario_{scenario_id}_{ncc_tech.lower().replace("-", "_")}'
            output_scenario_dir.mkdir(parents=True, exist_ok=True)

            df_deployment.to_csv(output_scenario_dir / 'deployment_trajectory.csv', index=False)
            df_annual.to_csv(output_scenario_dir / 'annual_regional_trajectory.csv', index=False)

            # Store results
            all_results.append({
                'scenario_id': scenario_id,
                'scenario_name': scenario_config['name'],
                'ncc_tech': ncc_tech,
                'deployment': df_deployment,
                'annual_regional': df_annual,
                'n_facilities': 248,  # Would need to count from baseline
                'n_ncc_facilities': 44,
                'n_btx_facilities': 48,
                'n_utility_facilities': 156
            })

            # Print summary
            row_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]
            row_2035 = df_deployment[df_deployment['year'] == 2035].iloc[0]

            print(f"\n  Results for {scenario_config['name']} + {ncc_tech}:")
            print(f"    BAU 2050: {row_2050['bau_mt']:.2f} Mt")
            print(f"    Target 2035: {emission_constraints[2035]:.2f} Mt")
            print(f"    Actual 2035: {row_2035['actual_emissions_mt']:.2f} Mt")
            print(f"    Target 2050: {emission_constraints[2050]:.2f} Mt")
            print(f"    Actual 2050: {row_2050['actual_emissions_mt']:.2f} Mt")
            print(f"    CAPEX: ${row_2050['cumulative_capex_musd']/1000:.2f}B")

    # Create scenario summary
    df_summary = create_scenario_summary(all_results)
    df_summary.to_csv(OUTPUT_DIR / 'scenario_summary_final.csv', index=False)

    print("\n" + "="*80)
    print("SCENARIO ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("\nScenario Summary:")
    print(df_summary[['scenario', 'technology', 'bau_2050_mt', 'net_2050_mt', 'capex_billion_usd']].to_string())

    return all_results


if __name__ == '__main__':
    main()
