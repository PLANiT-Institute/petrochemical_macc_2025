"""
Corrected Scenarios with Proper Facility Handling
==================================================
1. Shaheen Scenario: Add NEW S-Oil Shaheen facilities (1.8Mt ethylene + associated products)
2. Restructure 25%: Retire oldest 25% of facilities (by age in 2025)
3. Restructure 40%: Retire oldest 40% of facilities (by age in 2025)

Each scenario x 2 technology pathways (NCC-Elec, NCC-H2) = 6 scenarios total
"""

import pandas as pd
import numpy as np
import shutil
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path.cwd()))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

print("="*80)
print("한국 석유화학 MACC 모델 - Corrected Scenario Analysis")
print("="*80)
print()

# =============================================================================
# PATHS
# =============================================================================
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')

# Backup original files
backup_files = {
    'facilities': DATA_DIR / 'facility_database_with_regions.csv',
    'energy': DATA_DIR / 'energy_intensities.csv',
}

for name, path in backup_files.items():
    backup_path = path.with_suffix('.csv.backup')
    if path.exists() and not backup_path.exists():
        shutil.copy(path, backup_path)
        print(f"✓ Backed up: {path.name}")

# =============================================================================
# LOAD BASE DATA
# =============================================================================
print("\n" + "="*80)
print("Loading base facility data...")
print("="*80)

df_fac = pd.read_csv(DATA_DIR / 'facility_database_with_regions.csv')
df_energy = pd.read_csv(DATA_DIR / 'energy_intensities.csv')

print(f"Total facilities: {len(df_fac)}")
print(f"Total capacity: {df_fac['capacity_kt'].sum():,.0f} kt")

# =============================================================================
# SHAHEEN PROJECT DETAILS
# =============================================================================
# Source: S-Oil Shaheen Project (2026 startup)
# - 1,800 kt/yr ethylene (world's largest naphtha cracker)
# - 770 kt/yr propylene
# - 200 kt/yr butadiene
# - 280 kt/yr benzene
# Additional downstream facilities expected

SHAHEEN_FACILITIES = [
    # Product, Process, Company, Location, Complex, Capacity, Year
    ("Ethylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 1800, 2026),
    ("Propylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 770, 2026),
    ("Butadiene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 200, 2026),
    ("Benzene", "BTX Plant", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 280, 2026),
    # Downstream polymers (estimated based on typical cracker integration)
    ("HDPE", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 400, 2026),
    ("PP", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 500, 2026),
]

print("\n" + "="*80)
print("Shaheen Project Details (2026 Start)")
print("="*80)
shaheen_capacity = sum([f[5] for f in SHAHEEN_FACILITIES])
print(f"Total new capacity: {shaheen_capacity:,} kt")
for product, process, company, location, complex_, capacity, year in SHAHEEN_FACILITIES:
    print(f"  - {product}: {capacity:,} kt ({process})")


# =============================================================================
# FUNCTION: Create Shaheen Scenario
# =============================================================================
def create_shaheen_scenario():
    """Add Shaheen facilities to base facility database"""
    df_shaheen = df_fac.copy()
    df_energy_shaheen = df_energy.copy()

    # Add Shaheen facilities
    new_rows = []
    new_energy_rows = []

    for product, process, company, location, complex_, capacity, year in SHAHEEN_FACILITIES:
        # Find similar facility for energy intensity template
        similar = df_fac[(df_fac['product'] == product) & (df_fac['process'] == process)]

        if len(similar) > 0:
            template = similar.iloc[0]

            # Facility row
            new_row = {
                'product': product,
                'process': process,
                'company': company,
                'location': location,
                'complex': complex_,
                'capacity_kt': capacity,
                'year_built': year,
                'age_2025': -1,  # Not built yet in 2025
                'remaining_life': 41,  # 40 year life from 2026
                'retirement_year_40yr': 2066
            }
            new_rows.append(new_row)

            # Energy intensity row (copy from similar facility)
            energy_similar = df_energy[(df_energy['product'] == product) &
                                       (df_energy['process'] == process)]
            if len(energy_similar) > 0:
                energy_template = energy_similar.iloc[0].to_dict()
                energy_template['company'] = company
                energy_template['location'] = location
                energy_template['capacity_kt'] = capacity
                energy_template['year_built'] = year
                new_energy_rows.append(energy_template)

    # Append new facilities
    df_shaheen = pd.concat([df_shaheen, pd.DataFrame(new_rows)], ignore_index=True)
    df_energy_shaheen = pd.concat([df_energy_shaheen, pd.DataFrame(new_energy_rows)], ignore_index=True)

    print(f"\nShaheen Scenario: {len(df_shaheen)} facilities (+{len(new_rows)} new)")
    print(f"  Total capacity: {df_shaheen['capacity_kt'].sum():,.0f} kt")

    return df_shaheen, df_energy_shaheen


# =============================================================================
# FUNCTION: Create Restructuring Scenario (Retire Oldest X%)
# =============================================================================
def create_restructuring_scenario(retire_pct):
    """Retire oldest X% of facilities based on age_2025"""
    df_restructure = df_fac.copy()

    # Sort by age (oldest first)
    df_restructure = df_restructure.sort_values('age_2025', ascending=False)

    # Calculate how many to retire
    n_total = len(df_restructure)
    n_retire = int(n_total * retire_pct)

    # Get facilities to retire (oldest)
    retire_mask = df_restructure.index[:n_retire]
    retired_facilities = df_restructure.loc[retire_mask]

    # Keep remaining facilities
    df_remaining = df_restructure.drop(retire_mask).reset_index(drop=True)

    # Also filter energy intensities
    df_energy_remain = df_energy[
        df_energy.apply(lambda x: any(
            (df_remaining['product'] == x['product']) &
            (df_remaining['company'] == x['company']) &
            (df_remaining['location'] == x['location'])
        ), axis=1)
    ].copy()

    print(f"\nRestructure {retire_pct*100:.0f}% Scenario:")
    print(f"  Original facilities: {n_total}")
    print(f"  Retired (oldest): {n_retire}")
    print(f"  Remaining: {len(df_remaining)}")
    print(f"  Original capacity: {df_fac['capacity_kt'].sum():,.0f} kt")
    print(f"  Retired capacity: {retired_facilities['capacity_kt'].sum():,.0f} kt")
    print(f"  Remaining capacity: {df_remaining['capacity_kt'].sum():,.0f} kt ({df_remaining['capacity_kt'].sum()/df_fac['capacity_kt'].sum()*100:.1f}%)")

    # Show oldest retired facilities
    print(f"\n  Top 10 oldest retired facilities:")
    for _, row in retired_facilities.head(10).iterrows():
        print(f"    - {row['company']} {row['product']}: {row['capacity_kt']:.0f} kt (built {row['year_built']}, age {row['age_2025']} yrs)")

    return df_remaining, df_energy_remain


# =============================================================================
# FUNCTION: Run Scenario
# =============================================================================
def run_scenario(scenario_name, scenario_id, df_facilities, df_energies, force_tech):
    """Run a single scenario through all modules"""

    print(f"\n{'='*80}")
    print(f"Running: {scenario_name}")
    print(f"Technology: {force_tech}")
    print(f"{'='*80}")

    # Create output directories
    output_base = OUTPUT_DIR / f'corrected_{scenario_id}'
    output_dirs = {
        'baseline': output_base / 'module_01_baseline',
        'macc': output_base / 'module_02_macc',
        'optimization': output_base / 'module_03_optimization'
    }

    for d in output_dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # Save modified facility data
    df_facilities.to_csv(DATA_DIR / 'facility_database_with_regions.csv', index=False)
    df_energies.to_csv(DATA_DIR / 'energy_intensities.csv', index=False)

    try:
        # Module 1: Baseline
        print(">>> Module 1: Baseline Emissions")
        baseline_engine = BaselineAnalyzer(
            data_dir=str(DATA_DIR),
            output_dir=str(output_dirs['baseline'])
        )
        baseline_engine.run_complete_analysis()

        # Module 2: MACC
        print(">>> Module 2: MACC Calculation")
        macc_engine = MACCAnalyzer(
            baseline_output=str(output_dirs['baseline']),
            data_dir=str(DATA_DIR),
            output_dir=str(output_dirs['macc'])
        )
        macc_engine.run_complete_analysis()

        # Module 3: Optimization
        print(f">>> Module 3: Optimization ({force_tech})")
        opt_engine = CostOptimizerV2(
            baseline_output=str(output_dirs['baseline']),
            macc_output=str(output_dirs['macc']),
            output_dir=str(output_dirs['optimization']),
            force_ncc_technology=force_tech
        )
        opt_engine.run_complete_analysis()

        # Extract results
        df_deploy = pd.read_csv(output_dirs['optimization'] / 'policy_target_deployment.csv')
        df_2050 = df_deploy[df_deploy['year'] == 2050].iloc[0]

        result = {
            'scenario': scenario_name,
            'scenario_id': scenario_id,
            'technology': force_tech,
            'n_facilities': len(df_facilities),
            'total_capacity_kt': df_facilities['capacity_kt'].sum(),
            'bau_2050_mt': df_2050['bau_mt'],
            'emissions_2050_mt': df_2050['actual_emissions_mt'],
            'cost_2050_billion': df_2050['cumulative_capex_musd'] / 1000,
            'ncc_h2_mt': df_2050['ncc_h2_mt'],
            'ncc_elec_mt': df_2050['ncc_elec_mt'],
            'heat_pump_mt': df_2050['heat_pump_mt'],
            're_ppa_mt': df_2050['re_ppa_mt'],
            'electricity_twh': df_2050['electricity_consumption_increase_twh'],
            'h2_kt': df_2050['h2_consumption_kt']
        }

        print(f"\n✓ {scenario_name} completed")
        print(f"  Facilities: {result['n_facilities']}")
        print(f"  2050 BAU: {result['bau_2050_mt']:.2f} Mt")
        print(f"  2050 Net: {result['emissions_2050_mt']:.4f} Mt")
        print(f"  CAPEX: ${result['cost_2050_billion']:.1f}B")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":

    results = []

    # Define scenarios
    scenarios = [
        ('Baseline (248 facilities)', 'baseline', df_fac.copy(), df_energy.copy()),
        ('Shaheen (+6 facilities)', 'shaheen', *create_shaheen_scenario()),
        ('Restructure 25% (oldest retired)', 'restructure_25pct', *create_restructuring_scenario(0.25)),
        ('Restructure 40% (oldest retired)', 'restructure_40pct', *create_restructuring_scenario(0.40)),
    ]

    # Technology pathways
    technologies = [
        ('NCC-Electricity', 'ncc_elec'),
        ('NCC-H2', 'ncc_h2'),
    ]

    print("\n" + "="*80)
    print("Running All Scenarios")
    print("="*80)

    for scenario_name, scenario_base, df_fac_scenario, df_energy_scenario in scenarios:
        for tech_name, tech_suffix in technologies:
            scenario_id = f"{scenario_base}_{tech_suffix}"
            full_name = f"{scenario_name} + {tech_name}"

            result = run_scenario(
                full_name,
                scenario_id,
                df_fac_scenario.copy(),
                df_energy_scenario.copy(),
                tech_name
            )

            if result:
                results.append(result)

    # Restore original files
    print("\n" + "="*80)
    print("Restoring original files...")
    print("="*80)

    for name, path in backup_files.items():
        backup_path = path.with_suffix('.csv.backup')
        if backup_path.exists():
            shutil.copy(backup_path, path)
            print(f"✓ Restored: {path.name}")

    # Save results summary
    if results:
        df_results = pd.DataFrame(results)
        summary_path = OUTPUT_DIR / 'corrected_scenarios_summary.csv'
        df_results.to_csv(summary_path, index=False)
        print(f"\n✓ Saved summary: {summary_path}")

        # Print comparison table
        print("\n" + "="*80)
        print("SCENARIO COMPARISON (2050)")
        print("="*80)

        print(f"\n{'Scenario':<45} {'Facilities':>10} {'BAU (Mt)':>10} {'Net (Mt)':>10} {'Cost ($B)':>12}")
        print("-" * 95)

        for _, row in df_results.iterrows():
            print(f"{row['scenario']:<45} {row['n_facilities']:>10} {row['bau_2050_mt']:>10.1f} {row['emissions_2050_mt']:>10.2f} {row['cost_2050_billion']:>12.1f}")

        # Summary statistics
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)

        # Shaheen impact
        shaheen_elec = df_results[df_results['scenario_id'] == 'shaheen_ncc_elec'].iloc[0] if len(df_results[df_results['scenario_id'] == 'shaheen_ncc_elec']) > 0 else None
        baseline_elec = df_results[df_results['scenario_id'] == 'baseline_ncc_elec'].iloc[0] if len(df_results[df_results['scenario_id'] == 'baseline_ncc_elec']) > 0 else None

        if shaheen_elec is not None and baseline_elec is not None:
            print(f"\n1. Shaheen Project Impact:")
            print(f"   - New facilities: +{int(shaheen_elec['n_facilities'] - baseline_elec['n_facilities'])}")
            print(f"   - New capacity: +{(shaheen_elec['total_capacity_kt'] - baseline_elec['total_capacity_kt']):,.0f} kt")
            print(f"   - BAU emissions increase: +{shaheen_elec['bau_2050_mt'] - baseline_elec['bau_2050_mt']:.1f} Mt")
            print(f"   - Additional investment: +${shaheen_elec['cost_2050_billion'] - baseline_elec['cost_2050_billion']:.1f}B")

        # Restructuring impact
        r25_elec = df_results[df_results['scenario_id'] == 'restructure_25pct_ncc_elec'].iloc[0] if len(df_results[df_results['scenario_id'] == 'restructure_25pct_ncc_elec']) > 0 else None
        r40_elec = df_results[df_results['scenario_id'] == 'restructure_40pct_ncc_elec'].iloc[0] if len(df_results[df_results['scenario_id'] == 'restructure_40pct_ncc_elec']) > 0 else None

        if r25_elec is not None and baseline_elec is not None:
            print(f"\n2. Restructuring 25% Impact:")
            print(f"   - Facilities retired: {int(baseline_elec['n_facilities'] - r25_elec['n_facilities'])}")
            print(f"   - Capacity reduction: {(1 - r25_elec['total_capacity_kt']/baseline_elec['total_capacity_kt'])*100:.1f}%")
            print(f"   - BAU emissions reduction: -{baseline_elec['bau_2050_mt'] - r25_elec['bau_2050_mt']:.1f} Mt")
            print(f"   - Investment reduction: -${baseline_elec['cost_2050_billion'] - r25_elec['cost_2050_billion']:.1f}B")

        if r40_elec is not None and baseline_elec is not None:
            print(f"\n3. Restructuring 40% Impact:")
            print(f"   - Facilities retired: {int(baseline_elec['n_facilities'] - r40_elec['n_facilities'])}")
            print(f"   - Capacity reduction: {(1 - r40_elec['total_capacity_kt']/baseline_elec['total_capacity_kt'])*100:.1f}%")
            print(f"   - BAU emissions reduction: -{baseline_elec['bau_2050_mt'] - r40_elec['bau_2050_mt']:.1f} Mt")
            print(f"   - Investment reduction: -${baseline_elec['cost_2050_billion'] - r40_elec['cost_2050_billion']:.1f}B")

    print("\n" + "="*80)
    print("SCENARIO ANALYSIS COMPLETE")
    print("="*80)
