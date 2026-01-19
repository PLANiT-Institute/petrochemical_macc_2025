"""
Corrected Scenarios v2 - Proper Facility-Level Handling
========================================================
This version properly calculates emissions for each scenario by:
1. Modifying BOTH facility database AND energy intensities
2. Properly handling new Shaheen facilities (2026 start)
3. Retiring oldest facilities for restructuring scenarios

Key Fix: The baseline module uses facility counts, so we must
properly add/remove facilities, not just modify multipliers.
"""

import pandas as pd
import numpy as np
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

print("="*80)
print("한국 석유화학 MACC 모델 - Corrected Scenario Analysis v2")
print("="*80)

# =============================================================================
# PATHS
# =============================================================================
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')

# =============================================================================
# LOAD AND BACKUP ORIGINAL DATA
# =============================================================================
print("\nLoading original data...")

# Read originals
df_fac_orig = pd.read_csv(DATA_DIR / 'facility_database_with_regions.csv')
df_energy_orig = pd.read_csv(DATA_DIR / 'energy_intensities.csv')

# Backup
backup_fac = DATA_DIR / 'facility_database_with_regions.csv.original'
backup_energy = DATA_DIR / 'energy_intensities.csv.original'

if not backup_fac.exists():
    df_fac_orig.to_csv(backup_fac, index=False)
    print(f"  ✓ Backed up: facility_database_with_regions.csv")
if not backup_energy.exists():
    df_energy_orig.to_csv(backup_energy, index=False)
    print(f"  ✓ Backed up: energy_intensities.csv")

print(f"\nOriginal: {len(df_fac_orig)} facilities, {df_fac_orig['capacity_kt'].sum():,.0f} kt capacity")

# =============================================================================
# SHAHEEN PROJECT - NEW FACILITIES
# =============================================================================
# Source: S-Oil Shaheen (Onsan, 2026 start)
# - 1,800 kt ethylene, 770 kt propylene, 200 kt butadiene, 280 kt benzene
# - Plus downstream: HDPE, PP

SHAHEEN_NEW = [
    # (product, process, company, location, complex, capacity, year, naphtha_gj, elec_kwh, lng_gj, fuel_gas_gj, byproduct_gj)
    # Ethylene: use existing NCC intensities from S-Oil (similar to existing 182kt facility)
    ("Ethylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 1800, 2026, 29.0, 21.8, 4.5, 5.6, 1.1),
    ("Propylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 770, 2026, 25.4, 48.8, 3.9, 5.2, 1.2),
    ("Butadiene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 200, 2026, 24.5, 100.0, 3.0, 4.0, 0.8),
    ("Benzene", "BTX Plant", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 280, 2026, 0.0, 9.3, 2.5, 3.2, 0.6),
    ("HDPE", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 400, 2026, 0.0, 200.0, 0.0, 0.0, 0.0),
    ("PP", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 500, 2026, 0.0, 1.4, 0.0, 0.0, 0.0),
]

print("\n" + "="*80)
print("SHAHEEN PROJECT (2026)")
print("="*80)
shaheen_capacity = sum([x[5] for x in SHAHEEN_NEW])
print(f"New capacity: {shaheen_capacity:,} kt")
for prod, proc, comp, loc, cpx, cap, yr, *_ in SHAHEEN_NEW:
    print(f"  - {prod} ({proc}): {cap:,} kt")


# =============================================================================
# SCENARIO GENERATORS
# =============================================================================

def create_baseline_scenario():
    """Return baseline data unchanged"""
    return df_fac_orig.copy(), df_energy_orig.copy(), "Baseline (248 facilities)"


def create_shaheen_scenario():
    """Add Shaheen facilities to baseline"""
    df_fac = df_fac_orig.copy()
    df_energy = df_energy_orig.copy()

    for prod, proc, comp, loc, cpx, cap, yr, naphtha, elec, lng, fg, bp in SHAHEEN_NEW:
        # Add to facility database
        new_fac = {
            'product': prod,
            'process': proc,
            'company': comp,
            'location': loc,
            'complex': cpx,
            'capacity_kt': cap,
            'year_built': yr,
            'age_2025': -1,
            'remaining_life': 41,
            'retirement_year_40yr': 2066
        }
        df_fac = pd.concat([df_fac, pd.DataFrame([new_fac])], ignore_index=True)

        # Add to energy intensities
        new_energy = {
            'product': prod,
            'process': proc,
            'company': comp,
            'location': loc,
            'capacity_kt': cap,
            'year_built': yr,
            'Naphtha_GJ_per_tonne': naphtha,
            'Electricity_kWh_per_tonne': elec,
            'LNG_GJ_per_tonne': lng,
            'Fuel_Gas_GJ_per_tonne': fg,
            'Byproduct_Gas_GJ_per_tonne': bp,
            'LPG_GJ_per_tonne': 0.0,
            'Fuel_Oil_GJ_per_tonne': 0.0,
            'Diesel_GJ_per_tonne': 0.0
        }
        df_energy = pd.concat([df_energy, pd.DataFrame([new_energy])], ignore_index=True)

    return df_fac, df_energy, f"Shaheen (+{len(SHAHEEN_NEW)} facilities)"


def create_restructure_scenario(retire_pct):
    """Retire oldest X% of facilities"""
    df_fac = df_fac_orig.copy()
    df_energy = df_energy_orig.copy()

    # Sort by age (oldest first - highest age_2025)
    df_fac_sorted = df_fac.sort_values('age_2025', ascending=False).reset_index(drop=True)

    # Calculate retirement
    n_total = len(df_fac_sorted)
    n_retire = int(n_total * retire_pct)

    # Get retired facilities info
    retired = df_fac_sorted.head(n_retire)
    retired_cap = retired['capacity_kt'].sum()

    print(f"\n  Restructure {retire_pct*100:.0f}%: {n_retire} facilities retired")
    print(f"    Capacity reduction: {retired_cap:,.0f} kt ({retired_cap/df_fac['capacity_kt'].sum()*100:.1f}%)")
    print(f"    Oldest retired:")
    for _, row in retired.head(5).iterrows():
        print(f"      - {row['company']} {row['product']}: {row['capacity_kt']:.0f} kt (built {row['year_built']})")

    # Keep remaining
    df_fac_remain = df_fac_sorted.tail(n_total - n_retire).reset_index(drop=True)

    # Filter energy to match remaining facilities
    # Create key for matching
    df_fac_remain['key'] = df_fac_remain['product'] + '|' + df_fac_remain['company'] + '|' + df_fac_remain['location']
    df_energy['key'] = df_energy['product'] + '|' + df_energy['company'] + '|' + df_energy['location']

    df_energy_remain = df_energy[df_energy['key'].isin(df_fac_remain['key'])].copy()

    # Drop key columns
    df_fac_remain = df_fac_remain.drop('key', axis=1)
    df_energy_remain = df_energy_remain.drop('key', axis=1)

    return df_fac_remain, df_energy_remain, f"Restructure {retire_pct*100:.0f}% ({n_total - n_retire} facilities)"


# =============================================================================
# RUN SCENARIO
# =============================================================================

def run_scenario(scenario_name, scenario_id, df_fac, df_energy, force_tech):
    """Run single scenario through all modules"""

    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name} + {force_tech}")
    print(f"{'='*80}")
    print(f"  Facilities: {len(df_fac)}")
    print(f"  Capacity: {df_fac['capacity_kt'].sum():,.0f} kt")

    # Output directories
    output_base = OUTPUT_DIR / f'corrected_v2_{scenario_id}'
    dirs = {
        'baseline': output_base / 'module_01_baseline',
        'macc': output_base / 'module_02_macc',
        'opt': output_base / 'module_03_optimization'
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # Write scenario-specific data
    df_fac.to_csv(DATA_DIR / 'facility_database_with_regions.csv', index=False)
    df_energy.to_csv(DATA_DIR / 'energy_intensities.csv', index=False)

    try:
        # Module 1
        print("  >>> Module 1: Baseline")
        baseline = BaselineAnalyzer(str(DATA_DIR), str(dirs['baseline']))
        baseline.run_complete_analysis()

        # Module 2
        print("  >>> Module 2: MACC")
        macc = MACCAnalyzer(str(dirs['baseline']), str(DATA_DIR), str(dirs['macc']))
        macc.run_complete_analysis()

        # Module 3
        print(f"  >>> Module 3: Optimization ({force_tech})")
        opt = CostOptimizerV2(str(dirs['baseline']), str(dirs['macc']), str(dirs['opt']), force_tech)
        opt.run_complete_analysis()

        # Read results
        deploy = pd.read_csv(dirs['opt'] / 'policy_target_deployment.csv')
        r2050 = deploy[deploy['year'] == 2050].iloc[0]

        result = {
            'scenario': scenario_name,
            'technology': force_tech,
            'scenario_id': scenario_id,
            'n_facilities': len(df_fac),
            'capacity_kt': df_fac['capacity_kt'].sum(),
            'bau_2050_mt': r2050['bau_mt'],
            'net_2050_mt': r2050['actual_emissions_mt'],
            'capex_billion': r2050['cumulative_capex_musd'] / 1000,
            'ncc_h2_mt': r2050['ncc_h2_mt'],
            'ncc_elec_mt': r2050['ncc_elec_mt'],
            'heat_pump_mt': r2050['heat_pump_mt'],
            're_ppa_mt': r2050['re_ppa_mt'],
            'electricity_twh': r2050['electricity_consumption_increase_twh'],
            'h2_kt': r2050['h2_consumption_kt']
        }

        print(f"\n  ✓ COMPLETE")
        print(f"    BAU 2050: {result['bau_2050_mt']:.2f} Mt")
        print(f"    Net 2050: {result['net_2050_mt']:.4f} Mt")
        print(f"    CAPEX: ${result['capex_billion']:.1f}B")

        return result

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    results = []

    # Generate scenarios
    scenarios = [
        create_baseline_scenario(),
        create_shaheen_scenario(),
        create_restructure_scenario(0.25),
        create_restructure_scenario(0.40),
    ]

    technologies = ['NCC-Electricity', 'NCC-H2']

    # Run all combinations
    for df_fac, df_energy, name in scenarios:
        for tech in technologies:
            scenario_id = name.split('(')[0].strip().lower().replace(' ', '_').replace('+', '') + '_' + tech.lower().replace('-', '_')
            result = run_scenario(name, scenario_id, df_fac.copy(), df_energy.copy(), tech)
            if result:
                results.append(result)

    # Restore originals
    print("\n" + "="*80)
    print("Restoring original data...")
    shutil.copy(backup_fac, DATA_DIR / 'facility_database_with_regions.csv')
    shutil.copy(backup_energy, DATA_DIR / 'energy_intensities.csv')
    print("  ✓ Restored")

    # Save summary
    if results:
        df_results = pd.DataFrame(results)
        summary_path = OUTPUT_DIR / 'corrected_v2_scenarios_summary.csv'
        df_results.to_csv(summary_path, index=False)
        print(f"\n  ✓ Saved: {summary_path}")

        # Print comparison
        print("\n" + "="*80)
        print("SCENARIO COMPARISON (2050)")
        print("="*80)
        print(f"\n{'Scenario':<50} {'Facilities':>10} {'BAU':>10} {'Net':>10} {'CAPEX':>12}")
        print("-"*95)
        for _, r in df_results.iterrows():
            print(f"{r['scenario'] + ' + ' + r['technology']:<50} {r['n_facilities']:>10} {r['bau_2050_mt']:>10.1f} {r['net_2050_mt']:>10.2f} ${r['capex_billion']:>10.1f}B")

        # Key metrics
        print("\n" + "="*80)
        print("KEY INSIGHTS")
        print("="*80)

        base_elec = df_results[(df_results['scenario'].str.contains('Baseline')) & (df_results['technology'] == 'NCC-Electricity')].iloc[0]
        shaheen_elec = df_results[(df_results['scenario'].str.contains('Shaheen')) & (df_results['technology'] == 'NCC-Electricity')]
        r25_elec = df_results[(df_results['scenario'].str.contains('25%')) & (df_results['technology'] == 'NCC-Electricity')]
        r40_elec = df_results[(df_results['scenario'].str.contains('40%')) & (df_results['technology'] == 'NCC-Electricity')]

        if len(shaheen_elec) > 0:
            s = shaheen_elec.iloc[0]
            print(f"\n1. SHAHEEN Project Impact (vs Baseline):")
            print(f"   New facilities: +{s['n_facilities'] - base_elec['n_facilities']}")
            print(f"   New capacity: +{(s['capacity_kt'] - base_elec['capacity_kt']):,.0f} kt")
            print(f"   BAU emissions: +{s['bau_2050_mt'] - base_elec['bau_2050_mt']:.1f} Mt")
            print(f"   Investment: +${s['capex_billion'] - base_elec['capex_billion']:.1f}B")

        if len(r25_elec) > 0:
            s = r25_elec.iloc[0]
            print(f"\n2. RESTRUCTURE 25% Impact (vs Baseline):")
            print(f"   Facilities retired: {base_elec['n_facilities'] - s['n_facilities']}")
            print(f"   Capacity reduction: {(1 - s['capacity_kt']/base_elec['capacity_kt'])*100:.1f}%")
            print(f"   BAU reduction: -{base_elec['bau_2050_mt'] - s['bau_2050_mt']:.1f} Mt")
            print(f"   Investment saved: -${base_elec['capex_billion'] - s['capex_billion']:.1f}B")

        if len(r40_elec) > 0:
            s = r40_elec.iloc[0]
            print(f"\n3. RESTRUCTURE 40% Impact (vs Baseline):")
            print(f"   Facilities retired: {base_elec['n_facilities'] - s['n_facilities']}")
            print(f"   Capacity reduction: {(1 - s['capacity_kt']/base_elec['capacity_kt'])*100:.1f}%")
            print(f"   BAU reduction: -{base_elec['bau_2050_mt'] - s['bau_2050_mt']:.1f} Mt")
            print(f"   Investment saved: -${base_elec['capex_billion'] - s['capex_billion']:.1f}B")

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
