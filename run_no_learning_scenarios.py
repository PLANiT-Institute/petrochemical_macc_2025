"""
No Learning Curve Scenarios
===========================
Run all 6 scenarios with CAPEX fixed at 2025 levels (no learning curve)

This creates a sensitivity analysis to understand the impact of technology
cost reductions on the net zero transition economics.

Scenarios:
- 3 Production pathways: Shaheen, 구조조정 25%, 구조조정 40%
- 2 Technology pathways: NCC-H2, NCC-Electricity
- All with CAPEX fixed at 2025 levels
"""

import pandas as pd
import shutil
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path.cwd()))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

print("="*80)
print("한국 석유화학 MACC 모델 - No Learning Curve Sensitivity Analysis")
print("CAPEX fixed at 2025 levels (no technology cost reduction)")
print("="*80)
print()

# =============================================================================
# Step 1: Create technology_parameters with NO learning curve
# =============================================================================
print("Step 1: Creating technology parameters with no learning curve...")

# Backup original
original_tech = Path('data/technology_parameters.csv')
backup_tech = Path('data/technology_parameters_original_backup.csv')

if original_tech.exists():
    shutil.copy(original_tech, backup_tech)
    print(f"  ✓ Backed up original: {backup_tech}")

# Read and modify
df_tech = pd.read_csv(original_tech)
print("\nOriginal CAPEX values:")
print(df_tech[['technology', 'capex_2025_musd_per_mtco2', 'capex_2030_musd_per_mtco2',
               'capex_2040_musd_per_mtco2', 'capex_2050_musd_per_mtco2']])

# Set all years to 2025 values (no learning curve)
df_tech['capex_2030_musd_per_mtco2'] = df_tech['capex_2025_musd_per_mtco2']
df_tech['capex_2040_musd_per_mtco2'] = df_tech['capex_2025_musd_per_mtco2']
df_tech['capex_2050_musd_per_mtco2'] = df_tech['capex_2025_musd_per_mtco2']

print("\nNo Learning Curve CAPEX values (all fixed at 2025):")
print(df_tech[['technology', 'capex_2025_musd_per_mtco2', 'capex_2030_musd_per_mtco2',
               'capex_2040_musd_per_mtco2', 'capex_2050_musd_per_mtco2']])

# Save modified version
df_tech.to_csv(original_tech, index=False)
print("\n  ✓ Updated technology_parameters.csv with no learning curve")

# =============================================================================
# Step 2: Run 6 scenarios with no learning curve
# =============================================================================
print("\n" + "="*80)
print("Step 2: Running 6 scenarios with No Learning Curve")
print("="*80)

# Load scenario data
df_scenarios = pd.read_csv('data/demand_growth_trajectory_scenarios.csv')

# Define production scenarios
production_scenarios = {
    'shaheen': {
        'name': 'Shaheen (성장)',
        'column': 'scenario_shaheen',
        'description': 'S-Oil Shaheen project (+1.8Mt, 2026), then fixed'
    },
    'restructure_25pct': {
        'name': '구조조정 25%',
        'column': 'scenario_restructure_25pct',
        'description': '2026: -3.7Mt (25% reduction), then fixed'
    },
    'restructure_40pct': {
        'name': '구조조정 40%',
        'column': 'scenario_restructure_40pct',
        'description': '2040: Gradual 40% reduction'
    }
}

# Define technology pathways
technology_pathways = {
    'ncc_h2': {
        'name': 'NCC-H2',
        'force_tech': 'NCC-H2',
        'description': 'Hydrogen-fueled cracker (0.2 ton H2/ton C2H4)'
    },
    'ncc_elec': {
        'name': 'NCC-Electricity',
        'force_tech': 'NCC-Electricity',
        'description': 'Electric cracker with renewable electricity (5.0 MWh/ton C2H4)'
    }
}

# Backup original demand growth file
original_demand = Path('data/demand_growth_trajectory.csv')
backup_demand = Path('data/demand_growth_trajectory_original_backup.csv')

if original_demand.exists():
    shutil.copy(original_demand, backup_demand)
    print(f"\n  ✓ Backed up demand growth: {backup_demand}")

# Run each scenario combination
results_summary = []

for prod_key, prod_info in production_scenarios.items():
    for tech_key, tech_info in technology_pathways.items():
        scenario_id = f"{prod_key}_{tech_key}_no_learning"
        scenario_name = f"{prod_info['name']} + {tech_info['name']} (No Learning)"

        print("\n" + "="*80)
        print(f"시나리오 실행: {scenario_name}")
        print(f"생산량: {prod_info['description']}")
        print(f"기술 경로: {tech_info['description']}")
        print(f"CAPEX: Fixed at 2025 levels (NO learning curve)")
        print("="*80)

        # Create scenario-specific demand growth file
        df_scenario = df_scenarios[['year', prod_info['column']]].copy()
        df_scenario.columns = ['year', 'cumulative_capacity_multiplier']
        df_scenario.to_csv('data/demand_growth_trajectory.csv', index=False)

        # Create scenario-specific output directories
        output_base = Path('outputs') / f'scenarios_{scenario_id}'
        output_dirs = {
            'baseline': output_base / 'module_01_baseline',
            'macc': output_base / 'module_02_macc',
            'optimization': output_base / 'module_03_optimization'
        }

        for output_dir in output_dirs.values():
            output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Module 1: Baseline
            print(">>> Module 1: Baseline Emissions & BAU Trajectory")
            baseline_engine = BaselineAnalyzer(
                data_dir='data',
                output_dir=str(output_dirs['baseline'])
            )
            baseline_engine.run_complete_analysis()
            print("   ✓ Module 1 완료")

            # Module 2: MACC
            print(">>> Module 2: MACC Calculation")
            macc_engine = MACCAnalyzer(
                baseline_output=str(output_dirs['baseline']),
                data_dir='data',
                output_dir=str(output_dirs['macc'])
            )
            macc_engine.run_complete_analysis()
            print("   ✓ Module 2 완료")

            # Module 3: Optimization (with forced NCC technology)
            print(f">>> Module 3: Cost Optimization (Forcing {tech_info['name']})")
            opt_engine = CostOptimizerV2(
                baseline_output=str(output_dirs['baseline']),
                macc_output=str(output_dirs['macc']),
                output_dir=str(output_dirs['optimization']),
                force_ncc_technology=tech_info['force_tech']
            )
            opt_engine.run_complete_analysis()
            print("   ✓ Module 3 완료")

            # Extract key results
            df_deployment = pd.read_csv(output_dirs['optimization'] / 'policy_target_deployment.csv')
            df_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]

            results_summary.append({
                'scenario': scenario_name,
                'scenario_id': scenario_id,
                'production_pathway': prod_info['name'],
                'technology_pathway': tech_info['name'],
                'learning_curve': 'No (Fixed at 2025)',
                'bau_emissions_2050_mt': df_2050['bau_mt'],
                'emissions_2050_mt': df_2050['actual_emissions_mt'],
                'cost_2050_billion_usd': df_2050['cumulative_capex_musd'] / 1000,
                'ncc_h2_mt': df_2050['ncc_h2_mt'],
                'ncc_elec_mt': df_2050['ncc_elec_mt'],
                're_ppa_mt': df_2050['re_ppa_mt'],
                'heat_pump_mt': df_2050['heat_pump_mt'],
                'h2_consumption_kt': df_2050['h2_consumption_kt'],
                'electricity_increase_twh': df_2050['electricity_consumption_increase_twh']
            })

            print(f"\n✓ {scenario_name} 시나리오 완료")
            print(f"  2050 BAU 배출량: {df_2050['bau_mt']:.2f} MtCO2")
            print(f"  2050 실제 배출량: {df_2050['actual_emissions_mt']:.2f} MtCO2")
            print(f"  누적 CAPEX: ${df_2050['cumulative_capex_musd']/1000:.1f} billion USD")

        except Exception as e:
            print(f"   ✗ {scenario_name} 실행 중 오류:")
            print(f"      {str(e)}")
            import traceback
            traceback.print_exc()
            continue

# =============================================================================
# Step 3: Restore original files
# =============================================================================
print("\n" + "="*80)
print("Step 3: Restoring original files")
print("="*80)

# Restore technology parameters
if backup_tech.exists():
    shutil.copy(backup_tech, original_tech)
    print(f"  ✓ Restored technology_parameters.csv")

# Restore demand growth
if backup_demand.exists():
    shutil.copy(backup_demand, original_demand)
    print(f"  ✓ Restored demand_growth_trajectory.csv")

# =============================================================================
# Step 4: Save comparison summary
# =============================================================================
print("\n" + "="*80)
print("Step 4: Saving comparison summary")
print("="*80)

if results_summary:
    df_summary = pd.DataFrame(results_summary)

    # Save no-learning summary
    summary_path = Path('outputs/scenarios_no_learning_curve/summary.csv')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(summary_path, index=False)
    print(f"  ✓ Saved: {summary_path}")

    # Load original learning curve results for comparison
    original_summary_path = Path('outputs/scenarios_comparison_6scenarios/summary.csv')
    if original_summary_path.exists():
        df_original = pd.read_csv(original_summary_path)
        df_original['learning_curve'] = 'Yes (Default)'

        # Combine for comparison
        df_combined = pd.concat([df_original, df_summary], ignore_index=True)
        combined_path = Path('outputs/scenarios_learning_curve_comparison/summary.csv')
        combined_path.parent.mkdir(parents=True, exist_ok=True)
        df_combined.to_csv(combined_path, index=False)
        print(f"  ✓ Saved combined comparison: {combined_path}")

# =============================================================================
# Step 5: Print comparison
# =============================================================================
print("\n" + "="*80)
print("No Learning Curve Results (2050)")
print("="*80)

if results_summary:
    print(f"\n{'Scenario':<40s} {'Emissions':>10s} {'Cost (B$)':>12s}")
    print("-" * 65)

    for row in results_summary:
        print(f"{row['scenario']:<40s} {row['emissions_2050_mt']:>10.2f} {row['cost_2050_billion_usd']:>12.1f}")

# Compare with learning curve
if original_summary_path.exists():
    print("\n" + "="*80)
    print("Impact of Learning Curve on Total CAPEX")
    print("="*80)

    df_original = pd.read_csv(original_summary_path)

    print(f"\n{'Production + Tech':<35s} {'With Learning':>15s} {'No Learning':>15s} {'Difference':>15s}")
    print("-" * 85)

    for _, orig_row in df_original.iterrows():
        # Find matching no-learning row
        prod = orig_row['production_pathway']
        tech = orig_row['technology_pathway']

        match = [r for r in results_summary
                 if r['production_pathway'] == prod and r['technology_pathway'] == tech]

        if match:
            no_learn_cost = match[0]['cost_2050_billion_usd']
            learn_cost = orig_row['cost_2050_billion_usd']
            diff = no_learn_cost - learn_cost
            pct_diff = (diff / learn_cost) * 100

            print(f"{prod} + {tech:<15s} ${learn_cost:>12.1f}B ${no_learn_cost:>12.1f}B ${diff:>+12.1f}B ({pct_diff:+.0f}%)")

print("\n" + "="*80)
print("모든 No Learning Curve 시나리오 실행 완료")
print("="*80)
