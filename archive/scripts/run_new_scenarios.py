"""
Run 3 Specific Scenarios:
1. BAU (No Tech)
2. Cost-Effective (Optimization)
3. Restructuring (30% Oldest NCC Retired + Optimization)
"""

import pandas as pd
import numpy as np
import shutil
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2
from modules.utils import save_csv_output

def run_bau_scenario(output_dir):
    """Run Scenario 1: BAU (No Tech)"""
    print("\n" + "="*80)
    print("SCENARIO 1: BAU (Business As Usual)")
    print("="*80)
    
    # Run baseline analysis
    baseline = BaselineAnalyzer(output_dir=output_dir / 'module_01')
    baseline.run_complete_analysis(include_retirement_scenario=False)
    
    # Get trajectory
    df_bau = baseline.df_trajectory
    
    # Save simple summary
    summary = df_bau[['year', 'total_emissions_mt', 'fossil_emissions_mt', 'electricity_emissions_mt']].copy()
    summary['scenario'] = 'BAU'
    save_csv_output(summary, output_dir / 'bau_summary.csv')
    
    return summary

def run_cost_effective_scenario(output_dir):
    """Run Scenario 2: Cost-Effective (Optimization)"""
    print("\n" + "="*80)
    print("SCENARIO 2: Cost-Effective Optimization")
    print("="*80)
    
    # 1. Baseline
    baseline = BaselineAnalyzer(output_dir=output_dir / 'module_01')
    baseline.run_complete_analysis(include_retirement_scenario=False)
    
    # 2. MACC
    macc = MACCAnalyzer(
        baseline_output=output_dir / 'module_01',
        output_dir=output_dir / 'module_02'
    )
    macc.run_complete_analysis()
    
    # 3. Optimization
    optimizer = CostOptimizerV2(
        baseline_output=output_dir / 'module_01',
        macc_output=output_dir / 'module_02',
        output_dir=output_dir / 'module_03'
    )
    
    # Run for Policy_Target (Net Zero)
    results = optimizer.optimize_scenario('Policy_Target')
    
    # Save summary
    results['scenario'] = 'Cost-Effective'
    save_csv_output(results, output_dir / 'cost_effective_summary.csv')
    
    return results

def run_restructuring_scenario(output_dir):
    """Run Scenario 3: Restructuring (30% Oldest NCC Retired)"""
    print("\n" + "="*80)
    print("SCENARIO 3: Restructuring (30% Oldest NCC Retired)")
    print("="*80)
    
    # Create temp data directory
    temp_data_dir = Path('data_restructured')
    if temp_data_dir.exists():
        shutil.rmtree(temp_data_dir)
    temp_data_dir.mkdir()
    
    # Copy all CSVs from data/ to data_restructured/
    for file in Path('data').glob('*.csv'):
        shutil.copy(file, temp_data_dir)
        
    # 1. Filter Facility Database
    print("  Filtering facility database...")
    df_fac = pd.read_csv(temp_data_dir / 'facility_database_with_regions.csv')
    
    # Identify NCCs
    df_ncc = df_fac[df_fac['process'] == 'Naphtha Cracker'].copy()
    total_ncc_capacity = df_ncc['capacity_kt'].sum()
    target_retirement = total_ncc_capacity * 0.30
    
    print(f"  Total NCC Capacity: {total_ncc_capacity:.1f} kt")
    print(f"  Target Retirement (30%): {target_retirement:.1f} kt")
    
    # Sort by year_built (oldest first)
    df_ncc_sorted = df_ncc.sort_values('year_built')
    
    # Identify facilities to retire
    retired_indices = []
    retired_capacity = 0
    
    for idx, row in df_ncc_sorted.iterrows():
        if retired_capacity < target_retirement:
            retired_indices.append(idx)
            retired_capacity += row['capacity_kt']
            print(f"    - Retiring: {row['company']} {row['location']} ({row['capacity_kt']} kt, Built {row['year_built']})")
    
    print(f"  Actual Retired: {retired_capacity:.1f} kt ({(retired_capacity/total_ncc_capacity)*100:.1f}%)")
    
    # Remove retired facilities
    df_fac_filtered = df_fac.drop(retired_indices)
    df_fac_filtered.to_csv(temp_data_dir / 'facility_database_with_regions.csv', index=False)
    
    # 2. Run Analysis with Filtered Data
    # Baseline
    baseline = BaselineAnalyzer(data_dir=temp_data_dir, output_dir=output_dir / 'module_01')
    baseline.run_complete_analysis(include_retirement_scenario=False)
    
    # MACC
    macc = MACCAnalyzer(
        data_dir=temp_data_dir,
        baseline_output=output_dir / 'module_01',
        output_dir=output_dir / 'module_02'
    )
    macc.run_complete_analysis()
    
    # Optimization
    optimizer = CostOptimizerV2(
        baseline_output=output_dir / 'module_01',
        macc_output=output_dir / 'module_02',
        output_dir=output_dir / 'module_03'
    )
    
    results = optimizer.optimize_scenario('Policy_Target')
    
    # Save summary
    results['scenario'] = 'Restructuring'
    save_csv_output(results, output_dir / 'restructuring_summary.csv')
    
    # Cleanup
    # shutil.rmtree(temp_data_dir)
    
    return results

def compare_scenarios(bau, cost_eff, restructure, output_dir):
    """Generate comparison table"""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    
    comparison = []
    
    # BAU
    bau_2050 = bau[bau['year'] == 2050].iloc[0]
    comparison.append({
        'Scenario': '1. BAU',
        'Emissions 2050 (Mt)': bau_2050['total_emissions_mt'],
        'Reduction (%)': 0.0,
        'Total Cost ($B)': 0.0,
        'NCC Capacity (kt)': 11962, # Hardcoded baseline
        'H2 Demand (kt)': 0,
        'Elec Demand (TWh)': 0
    })
    
    # Cost Effective
    ce_2050 = cost_eff[cost_eff['year'] == 2050].iloc[0]
    ce_cost = cost_eff['cumulative_capex_musd'].iloc[-1] / 1000 # Approximation
    comparison.append({
        'Scenario': '2. Cost-Effective',
        'Emissions 2050 (Mt)': ce_2050['actual_emissions_mt'],
        'Reduction (%)': ((52 - ce_2050['actual_emissions_mt']) / 52) * 100,
        'Total Cost ($B)': ce_cost, # Only CAPEX for now
        'NCC Capacity (kt)': 11962,
        'H2 Demand (kt)': ce_2050['h2_consumption_kt'],
        'Elec Demand (TWh)': ce_2050['electricity_consumption_increase_twh']
    })
    
    # Restructuring
    re_2050 = restructure[restructure['year'] == 2050].iloc[0]
    re_cost = restructure['cumulative_capex_musd'].iloc[-1] / 1000
    comparison.append({
        'Scenario': '3. Restructuring (30%)',
        'Emissions 2050 (Mt)': re_2050['actual_emissions_mt'],
        'Reduction (%)': ((52 - re_2050['actual_emissions_mt']) / 52) * 100, # Note: Baseline was lower!
        'Total Cost ($B)': re_cost,
        'NCC Capacity (kt)': 11962 * 0.7, # Approx
        'H2 Demand (kt)': re_2050['h2_consumption_kt'],
        'Elec Demand (TWh)': re_2050['electricity_consumption_increase_twh']
    })
    
    df_comp = pd.DataFrame(comparison)
    print(df_comp)
    df_comp.to_csv(output_dir / 'final_scenario_comparison.csv', index=False)

def main():
    base_output = Path('outputs/new_scenarios')
    base_output.mkdir(parents=True, exist_ok=True)
    
    # Run scenarios
    bau = run_bau_scenario(base_output / 'bau')
    cost_eff = run_cost_effective_scenario(base_output / 'cost_effective')
    restructure = run_restructuring_scenario(base_output / 'restructuring')
    
    # Compare
    compare_scenarios(bau, cost_eff, restructure, base_output)

if __name__ == "__main__":
    main()
