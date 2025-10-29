"""
Run Complete Model with Corrected Data
Tracks changes from original results
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

def save_comparison(original, corrected, metric_name, output_file):
    """Save comparison of original vs corrected results"""
    comparison = {
        'metric': metric_name,
        'original': original,
        'corrected': corrected,
        'change_absolute': corrected - original,
        'change_percent': ((corrected - original) / original * 100) if original != 0 else 0
    }

    # Append to JSON file
    comparisons_file = Path('outputs/data_correction_comparison.json')
    if comparisons_file.exists():
        with open(comparisons_file, 'r') as f:
            comparisons = json.load(f)
    else:
        comparisons = []

    comparisons.append(comparison)

    with open(comparisons_file, 'w') as f:
        json.dump(comparisons, f, indent=2)

    return comparison

def main():
    print("="*80)
    print("RUNNING MODEL WITH CORRECTED DATA")
    print("="*80)
    print("\nData Corrections Applied:")
    print("  1. LNG emission factor: 0.0149 → 0.0561 tCO2/GJ (+276%)")
    print("  2. Fuel Gas emission factor: 0.0149 → 0.050 tCO2/GJ (+235%)")
    print("  3. H2 price (2025): $12.00 → $6.00/kg (-50%)")
    print("  4. H2 price (2030): $10.00 → $3.50/kg (-65%)")
    print("  5. RE price (2025): $130 → $90/MWh (-31%)")
    print("  6. RE price (2030): $115 → $75/MWh (-35%)")
    print("\n" + "="*80)

    # Load original results for comparison (if they exist)
    try:
        original_baseline = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')
        original_baseline_total = original_baseline['total_emissions_kt'].sum() / 1000
        print(f"\n📊 Original Baseline (2025): {original_baseline_total:.2f} MtCO2")
    except:
        original_baseline_total = None
        print("\n⚠️  No original baseline found for comparison")

    # ========================================================================
    # MODULE 1: BASELINE ANALYSIS
    # ========================================================================
    print("\n" + "="*80)
    print("MODULE 1: BASELINE ANALYSIS (WITH CORRECTED EMISSION FACTORS)")
    print("="*80)

    baseline = BaselineAnalyzer(
        data_dir='data',
        output_dir='outputs/module_01_corrected'
    )

    results = baseline.run_complete_analysis(include_retirement_scenario=False)

    # Compare baseline emissions
    corrected_baseline_total = results['baseline']['total_emissions_kt'].sum() / 1000
    print(f"\n📊 Corrected Baseline (2025): {corrected_baseline_total:.2f} MtCO2")

    if original_baseline_total:
        change = corrected_baseline_total - original_baseline_total
        change_pct = (change / original_baseline_total) * 100
        print(f"   Change: {change:+.2f} MtCO2 ({change_pct:+.1f}%)")
        save_comparison(original_baseline_total, corrected_baseline_total,
                       'baseline_2025_emissions_mt', 'baseline_comparison.csv')

    # ========================================================================
    # MODULE 2: MACC ANALYSIS
    # ========================================================================
    print("\n" + "="*80)
    print("MODULE 2: MACC ANALYSIS (WITH CORRECTED PRICES)")
    print("="*80)

    macc = MACCAnalyzer(
        baseline_output='outputs/module_01_corrected',
        data_dir='data',
        output_dir='outputs/module_02_corrected'
    )

    macc_results = macc.run_complete_analysis()

    # Compare MACC costs for 2030
    df_macc = macc_results['macc']
    macc_2030 = df_macc[df_macc['year'] == 2030]

    print("\n📊 Technology Costs (2030):")
    for _, row in macc_2030.iterrows():
        if row['available']:
            print(f"   {row['technology']:20s}: ${row['total_cost_usd_per_tco2']:7.0f}/tCO2")

    # ========================================================================
    # MODULE 3: COST OPTIMIZATION
    # ========================================================================
    print("\n" + "="*80)
    print("MODULE 3: COST OPTIMIZATION (WITH CORRECTED DATA)")
    print("="*80)

    optimizer = CostOptimizerV2(
        baseline_output='outputs/module_01_corrected',
        macc_output='outputs/module_02_corrected',
        output_dir='outputs/module_03_corrected',
        scenario_file='data/emission_scenarios_clean.csv'
    )

    opt_results = optimizer.run_complete_analysis()

    # Extract Policy Target results
    policy_target = opt_results.get('Policy_Target')
    if policy_target is not None:
        deploy_2050 = policy_target[policy_target['year'] == 2050].iloc[0]

        print("\n📊 2050 Deployment (Corrected Data):")
        print(f"   Heat Pump:       {deploy_2050['heat_pump_mt']:6.2f} MtCO2")
        print(f"   NCC-H2:          {deploy_2050['ncc_h2_mt']:6.2f} MtCO2")
        print(f"   NCC-Electricity: {deploy_2050['ncc_elec_mt']:6.2f} MtCO2")
        print(f"   RE PPA:          {deploy_2050['re_ppa_mt']:6.2f} MtCO2")
        print(f"   ─────────────────────────────")
        print(f"   Total:           {deploy_2050['total_deployed_mt']:6.2f} MtCO2")
        print(f"\n   BAU 2050:        {deploy_2050['bau_mt']:6.2f} MtCO2")
        print(f"   Actual 2050:     {deploy_2050['actual_emissions_mt']:6.2f} MtCO2")
        print(f"   Reduction:       {(1 - deploy_2050['actual_emissions_mt']/deploy_2050['bau_mt'])*100:5.1f}%")
        print(f"\n   Investment:      ${deploy_2050['cumulative_capex_musd']/1000:5.2f} Billion")
        print(f"   H2 Consumption:  {deploy_2050['h2_consumption_kt']:6.1f} kt/year")
        print(f"   Elec Increase:   {deploy_2050['electricity_consumption_increase_twh']:6.1f} TWh/year")

    # ========================================================================
    # CREATE COMPARISON REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("GENERATING COMPARISON REPORT")
    print("="*80)

    # Load comparison data
    try:
        with open('outputs/data_correction_comparison.json', 'r') as f:
            comparisons = json.load(f)

        print("\n📊 Summary of Changes:")
        for comp in comparisons:
            print(f"\n   {comp['metric']}:")
            print(f"      Original:  {comp['original']:.2f}")
            print(f"      Corrected: {comp['corrected']:.2f}")
            print(f"      Change:    {comp['change_absolute']:+.2f} ({comp['change_percent']:+.1f}%)")
    except:
        print("\n⚠️  Could not load comparison data")

    print("\n" + "="*80)
    print("MODEL RUN COMPLETE")
    print("="*80)
    print(f"\nOutputs saved to:")
    print(f"  - outputs/module_01_corrected/")
    print(f"  - outputs/module_02_corrected/")
    print(f"  - outputs/module_03_corrected/")
    print(f"  - outputs/data_correction_comparison.json")
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
