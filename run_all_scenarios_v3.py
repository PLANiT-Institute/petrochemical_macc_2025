"""
Complete Scenario Runner v3 - Correct Facility-Level Implementation
====================================================================
This script properly implements all 6 scenarios:

1. Shaheen (Growth) + NCC-H2: Add 6 new Shaheen facilities (254 total)
2. Shaheen (Growth) + NCC-Electricity: Add 6 new Shaheen facilities (254 total)
3. Restructure 25% + NCC-H2: Retire oldest NCC facilities = 25% NCC capacity (239 total)
4. Restructure 25% + NCC-Electricity: Retire oldest NCC facilities = 25% NCC capacity (239 total)
5. Restructure 40% + NCC-H2: Retire oldest NCC facilities = 40% NCC capacity (232 total)
6. Restructure 40% + NCC-Electricity: Retire oldest NCC facilities = 40% NCC capacity (232 total)

Key Changes from Previous Versions:
- Restructuring applies ONLY to NCC (Naphtha Cracker) facilities
- Retire oldest NCC facilities until reaching 25% or 40% of NCC capacity
- Actually modifies facility and energy intensity databases
- Properly syncs both databases to maintain index alignment
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
print("한국 석유화학 MACC 모델 - Complete Scenario Runner v3")
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

df_fac_orig = pd.read_csv(DATA_DIR / 'facility_database_with_regions.csv')
df_energy_orig = pd.read_csv(DATA_DIR / 'energy_intensities.csv')

# Backup
backup_fac = DATA_DIR / 'facility_database_with_regions.csv.backup'
backup_energy = DATA_DIR / 'energy_intensities.csv.backup'

df_fac_orig.to_csv(backup_fac, index=False)
df_energy_orig.to_csv(backup_energy, index=False)
print(f"  ✓ Backed up original files")

print(f"\nOriginal: {len(df_fac_orig)} facilities, {df_fac_orig['capacity_kt'].sum():,.0f} kt capacity")

# Verify NCC facilities
ncc_orig = df_fac_orig[df_fac_orig['process'] == 'Naphtha Cracker']
print(f"NCC facilities: {len(ncc_orig)}, {ncc_orig['capacity_kt'].sum():,.0f} kt capacity")

# =============================================================================
# SHAHEEN PROJECT - NEW FACILITIES
# =============================================================================
SHAHEEN_NEW = [
    # (product, process, company, location, complex, capacity, year, naphtha, elec, lng, fuel_gas, byproduct)
    ("Ethylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 1800, 2026, 29.0, 21.8, 4.5, 5.6, 1.1),
    ("Propylene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 770, 2026, 25.4, 48.8, 3.9, 5.2, 1.2),
    ("Butadiene", "Naphtha Cracker", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 200, 2026, 24.5, 100.0, 3.0, 4.0, 0.8),
    ("Benzene", "BTX Plant", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 280, 2026, 0.0, 9.3, 2.5, 3.2, 0.6),
    ("HDPE", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 400, 2026, 0.0, 200.0, 0.0, 0.0, 0.0),
    ("PP", "Utility", "S-Oil Shaheen", "Onsan", "Ulsan Complex", 500, 2026, 0.0, 1.4, 0.0, 0.0, 0.0),
]

print("\n" + "="*80)
print("SHAHEEN PROJECT (S-Oil, 2026)")
print("="*80)
shaheen_capacity = sum([x[5] for x in SHAHEEN_NEW])
print(f"New capacity: {shaheen_capacity:,} kt")
for prod, proc, comp, loc, cpx, cap, yr, *_ in SHAHEEN_NEW:
    print(f"  - {prod} ({proc}): {cap:,} kt")


# =============================================================================
# SCENARIO GENERATORS
# =============================================================================

def create_shaheen_scenario():
    """Add Shaheen facilities to baseline"""
    df_fac = df_fac_orig.copy()
    df_energy = df_energy_orig.copy()

    new_facilities = []
    new_energies = []

    for prod, proc, comp, loc, cpx, cap, yr, naphtha, elec, lng, fg, bp in SHAHEEN_NEW:
        new_fac = {
            'product': prod,
            'process': proc,
            'company': comp,
            'location': loc,
            'complex': cpx,
            'capacity_kt': cap,
            'year_built': yr,
            'age_2025': -1,  # Not yet built in 2025
            'remaining_life': 41,
            'retirement_year_40yr': 2066
        }
        new_facilities.append(new_fac)

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
        new_energies.append(new_energy)

    df_fac = pd.concat([df_fac, pd.DataFrame(new_facilities)], ignore_index=True)
    df_energy = pd.concat([df_energy, pd.DataFrame(new_energies)], ignore_index=True)

    return df_fac, df_energy, "Shaheen (성장)", len(df_fac)


def create_restructure_scenario(retire_pct):
    """Retire oldest NCC facilities representing X% of NCC capacity"""
    df_fac = df_fac_orig.copy()
    df_energy = df_energy_orig.copy()

    # Find NCC facilities
    ncc_mask = df_fac['process'] == 'Naphtha Cracker'
    ncc_fac = df_fac[ncc_mask].copy()
    ncc_fac = ncc_fac.sort_values('age_2025', ascending=False)  # oldest first

    total_ncc_cap = ncc_fac['capacity_kt'].sum()
    target_cap = total_ncc_cap * retire_pct

    # Find facilities to retire
    cumsum = 0
    retire_indices = []
    for idx, row in ncc_fac.iterrows():
        if cumsum < target_cap:
            retire_indices.append(idx)
            cumsum += row['capacity_kt']
        else:
            break

    retired_cap = df_fac.loc[retire_indices, 'capacity_kt'].sum()

    print(f"\n  Restructure {retire_pct*100:.0f}% NCC:")
    print(f"    Target: {target_cap:,.0f} kt ({retire_pct*100:.0f}% of {total_ncc_cap:,.0f} kt NCC)")
    print(f"    Retired: {len(retire_indices)} NCC facilities, {retired_cap:,.0f} kt ({retired_cap/total_ncc_cap*100:.1f}%)")
    print(f"    Oldest retired:")
    for idx in retire_indices[:5]:
        row = df_fac.loc[idx]
        print(f"      - {row['company']} {row['product']} ({row['location']}): {row['capacity_kt']:.0f} kt, built {int(row['year_built'])}")

    # Remove retired facilities from both dataframes
    df_fac_remain = df_fac.drop(retire_indices).reset_index(drop=True)
    df_energy_remain = df_energy.drop(retire_indices).reset_index(drop=True)

    name = f"구조조정 {retire_pct*100:.0f}%"
    return df_fac_remain, df_energy_remain, name, len(df_fac_remain)


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

    ncc_count = len(df_fac[df_fac['process'] == 'Naphtha Cracker'])
    ncc_cap = df_fac[df_fac['process'] == 'Naphtha Cracker']['capacity_kt'].sum()
    print(f"  NCC Facilities: {ncc_count}, {ncc_cap:,.0f} kt")

    # Output directories
    output_base = OUTPUT_DIR / f'scenario_{scenario_id}'
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

    # Also save scenario facility list
    df_fac.to_csv(output_base / 'scenario_facilities.csv', index=False)

    # Module 1: Baseline
    print("  >>> Module 1: Baseline")
    baseline = BaselineAnalyzer(str(DATA_DIR), str(dirs['baseline']))
    baseline.run_complete_analysis()

    # Module 2: MACC
    print("  >>> Module 2: MACC")
    macc = MACCAnalyzer(str(dirs['baseline']), str(DATA_DIR), str(dirs['macc']))
    macc.run_complete_analysis()

    # Module 3: Optimization
    print(f"  >>> Module 3: Optimization ({force_tech})")
    opt = CostOptimizerV2(
        baseline_output=str(dirs['baseline']),
        macc_output=str(dirs['macc']),
        output_dir=str(dirs['opt']),
        force_ncc_technology=force_tech
    )
    opt.run_complete_analysis()

    # Read results
    deploy = pd.read_csv(dirs['opt'] / 'policy_target_deployment.csv')
    r2050 = deploy[deploy['year'] == 2050].iloc[0]

    # Read facility allocation
    alloc_path = dirs['opt'] / 'policy_target_facility_allocation_2050.csv'
    if alloc_path.exists():
        alloc = pd.read_csv(alloc_path)
        n_alloc = len(alloc)
    else:
        n_alloc = 0

    result = {
        'scenario': scenario_name,
        'technology': force_tech,
        'scenario_id': scenario_id,
        'n_facilities': len(df_fac),
        'n_ncc_facilities': ncc_count,
        'total_capacity_kt': df_fac['capacity_kt'].sum(),
        'ncc_capacity_kt': ncc_cap,
        'bau_2050_mt': r2050['bau_mt'],
        'net_2050_mt': r2050['actual_emissions_mt'],
        'capex_billion_usd': r2050['cumulative_capex_musd'] / 1000,
        'ncc_h2_mt': r2050['ncc_h2_mt'],
        'ncc_elec_mt': r2050['ncc_elec_mt'],
        'heat_pump_mt': r2050['heat_pump_mt'],
        're_ppa_mt': r2050['re_ppa_mt'],
        'electricity_twh': r2050['electricity_consumption_increase_twh'],
        'h2_kt': r2050['h2_consumption_kt'],
        'n_facilities_allocated': n_alloc
    }

    print(f"\n  ✓ COMPLETE")
    print(f"    BAU 2050: {result['bau_2050_mt']:.2f} Mt")
    print(f"    Net 2050: {result['net_2050_mt']:.4f} Mt")
    print(f"    CAPEX: ${result['capex_billion_usd']:.1f}B")

    return result


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    results = []

    # Define scenarios
    print("\n" + "="*80)
    print("GENERATING SCENARIOS")
    print("="*80)

    scenarios = [
        create_shaheen_scenario(),
        create_restructure_scenario(0.25),
        create_restructure_scenario(0.40),
    ]

    technologies = ['NCC-H2', 'NCC-Electricity']

    # Run all 6 combinations
    for df_fac, df_energy, name, n_fac in scenarios:
        for tech in technologies:
            # Create scenario ID
            if 'Shaheen' in name:
                scenario_id = 'shaheen_' + tech.lower().replace('-', '_')
            elif '25%' in name:
                scenario_id = 'restructure_25pct_' + tech.lower().replace('-', '_')
            elif '40%' in name:
                scenario_id = 'restructure_40pct_' + tech.lower().replace('-', '_')
            else:
                scenario_id = name.lower().replace(' ', '_') + '_' + tech.lower().replace('-', '_')

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
        summary_path = OUTPUT_DIR / 'scenario_summary_v3.csv'
        df_results.to_csv(summary_path, index=False)
        print(f"\n  ✓ Saved: {summary_path}")

        # Print comparison
        print("\n" + "="*80)
        print("SCENARIO COMPARISON (2050)")
        print("="*80)

        print(f"\n{'Scenario':<45} {'Fac':>5} {'NCC':>5} {'BAU Mt':>10} {'Net Mt':>10} {'CAPEX $B':>10}")
        print("-"*95)
        for _, r in df_results.iterrows():
            label = f"{r['scenario']} + {r['technology']}"
            print(f"{label:<45} {r['n_facilities']:>5} {r['n_ncc_facilities']:>5} {r['bau_2050_mt']:>10.1f} {r['net_2050_mt']:>10.2f} {r['capex_billion_usd']:>10.1f}")

        # Key insights
        print("\n" + "="*80)
        print("KEY INSIGHTS")
        print("="*80)

        shaheen = df_results[df_results['scenario'].str.contains('Shaheen')].iloc[0]
        r25 = df_results[df_results['scenario'].str.contains('25%')].iloc[0]
        r40 = df_results[df_results['scenario'].str.contains('40%')].iloc[0]

        print(f"\n1. SHAHEEN Project (Growth Scenario):")
        print(f"   Total facilities: {shaheen['n_facilities']} (+6 new)")
        print(f"   NCC facilities: {shaheen['n_ncc_facilities']}")
        print(f"   BAU emissions 2050: {shaheen['bau_2050_mt']:.1f} Mt")

        print(f"\n2. RESTRUCTURE 25% NCC:")
        print(f"   Total facilities: {r25['n_facilities']} (-9 NCC)")
        print(f"   NCC facilities: {r25['n_ncc_facilities']}")
        print(f"   BAU emissions 2050: {r25['bau_2050_mt']:.1f} Mt")
        print(f"   BAU reduction: {shaheen['bau_2050_mt'] - r25['bau_2050_mt']:.1f} Mt")

        print(f"\n3. RESTRUCTURE 40% NCC:")
        print(f"   Total facilities: {r40['n_facilities']} (-16 NCC)")
        print(f"   NCC facilities: {r40['n_ncc_facilities']}")
        print(f"   BAU emissions 2050: {r40['bau_2050_mt']:.1f} Mt")
        print(f"   BAU reduction: {shaheen['bau_2050_mt'] - r40['bau_2050_mt']:.1f} Mt")

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
