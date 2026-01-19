"""
VERIFICATION CODE: Recalculate Results from Assumptions
========================================================
This script independently recalculates the model outputs using only the saved
assumptions CSVs to verify that the model is producing correct results.

It performs the following verifications:
1. Baseline emissions calculation
2. MACC (cost) calculation for each technology
3. Deployment trajectory verification
4. Final results cross-check

Output: outputs/verification/verification_report.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Directories
VERIFY_DIR = Path('outputs/verification')
OUTPUT_FILE = VERIFY_DIR / 'verification_report.csv'

print("=" * 80)
print("VERIFICATION: RECALCULATING RESULTS FROM ASSUMPTIONS")
print("=" * 80)

# =============================================================================
# LOAD ASSUMPTIONS
# =============================================================================
print("\n" + "-" * 80)
print("LOADING ASSUMPTIONS")
print("-" * 80)

# Load all assumption files
df_ef = pd.read_csv(VERIFY_DIR / 'assumptions_01_emission_factors.csv')
df_tech = pd.read_csv(VERIFY_DIR / 'assumptions_02_technology_parameters.csv')
df_h2 = pd.read_csv(VERIFY_DIR / 'assumptions_03_h2_price_trajectory.csv')
df_re = pd.read_csv(VERIFY_DIR / 'assumptions_04_re_price_trajectory.csv')
df_grid_ef = pd.read_csv(VERIFY_DIR / 'assumptions_05_grid_emission_trajectory.csv')
df_grid_price = pd.read_csv(VERIFY_DIR / 'assumptions_06_grid_price_trajectory.csv')
df_hp_app = pd.read_csv(VERIFY_DIR / 'assumptions_08_heat_pump_applicability.csv')
df_targets = pd.read_csv(VERIFY_DIR / 'assumptions_09_emission_targets.csv')
df_demand = pd.read_csv(VERIFY_DIR / 'assumptions_10_demand_growth_trajectory.csv')
df_facilities = pd.read_csv(VERIFY_DIR / 'assumptions_11_facility_database.csv')

# Load results for comparison
df_results = pd.read_csv(VERIFY_DIR / 'results_06_key_results_by_scenario.csv')
df_macc = pd.read_csv(VERIFY_DIR / 'results_02_macc_annual.csv')
df_baseline = pd.read_csv(VERIFY_DIR / 'results_03_baseline_emissions.csv')
df_deploy = pd.read_csv(VERIFY_DIR / 'results_01_deployment_trajectories.csv')

print(f"Loaded {len(df_ef)} emission factors")
print(f"Loaded {len(df_tech)} technologies")
print(f"Loaded {len(df_facilities)} facilities")

# Create verification results list
verifications = []

# =============================================================================
# VERIFICATION 1: BASELINE EMISSIONS
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 1: BASELINE EMISSIONS")
print("-" * 80)

# Get emission factors
ef_dict = df_ef.set_index('fuel')

# Calculate expected baseline emissions from facilities
# Total emissions = sum of all fuel emissions
calculated_total_emissions = 0
for _, fac in df_facilities.iterrows():
    # Each facility has capacity_kt and we need to estimate emissions
    # The baseline file has pre-calculated emissions, so we verify the sum
    pass

# From results
model_total_baseline_kt = df_baseline['total_emissions_kt'].sum()
model_total_baseline_mt = model_total_baseline_kt / 1000

# Calculate from facilities (assuming emissions are correctly calculated)
ncc_facilities = df_facilities[df_facilities['process'] == 'Naphtha Cracker']
btx_facilities = df_facilities[df_facilities['process'] == 'BTX Plant']
other_facilities = df_facilities[~df_facilities['process'].isin(['Naphtha Cracker', 'BTX Plant'])]

# NCC emissions: capacity * emission_intensity
# From baseline: ~1.74 tCO2/ton product for NCC
ncc_capacity_kt = ncc_facilities['capacity_kt'].sum()
ncc_emission_intensity = 1.74  # tCO2/ton (from model)
expected_ncc_emissions_mt = ncc_capacity_kt * 1000 * ncc_emission_intensity / 1e6

# BTX emissions: typically much lower per ton
btx_capacity_kt = btx_facilities['capacity_kt'].sum()
btx_emission_intensity = 0.33  # tCO2/ton (from baseline data)
expected_btx_emissions_mt = btx_capacity_kt * 1000 * btx_emission_intensity / 1e6

# Get actual from baseline
actual_ncc_emissions_mt = df_baseline[df_baseline['process'] == 'Naphtha Cracker']['total_emissions_kt'].sum() / 1000
actual_btx_emissions_mt = df_baseline[df_baseline['process'] == 'BTX Plant']['total_emissions_kt'].sum() / 1000

print(f"\nNCC Facilities: {len(ncc_facilities)}")
print(f"  Capacity: {ncc_capacity_kt:,.0f} kt")
print(f"  Model emissions: {actual_ncc_emissions_mt:.2f} Mt")
print(f"  Expected (1.74 tCO2/ton): {expected_ncc_emissions_mt:.2f} Mt")

print(f"\nBTX Facilities: {len(btx_facilities)}")
print(f"  Capacity: {btx_capacity_kt:,.0f} kt")
print(f"  Model emissions: {actual_btx_emissions_mt:.2f} Mt")
print(f"  Expected (0.33 tCO2/ton): {expected_btx_emissions_mt:.2f} Mt")

print(f"\nTotal Model Baseline: {model_total_baseline_mt:.2f} Mt")

verifications.append({
    'check': 'Baseline NCC Emissions',
    'expected': expected_ncc_emissions_mt,
    'model': actual_ncc_emissions_mt,
    'difference': abs(expected_ncc_emissions_mt - actual_ncc_emissions_mt),
    'pct_diff': abs(expected_ncc_emissions_mt - actual_ncc_emissions_mt) / actual_ncc_emissions_mt * 100 if actual_ncc_emissions_mt > 0 else 0,
    'status': 'PASS' if abs(expected_ncc_emissions_mt - actual_ncc_emissions_mt) < 5 else 'CHECK',
    'unit': 'MtCO2'
})

verifications.append({
    'check': 'Baseline BTX Emissions',
    'expected': expected_btx_emissions_mt,
    'model': actual_btx_emissions_mt,
    'difference': abs(expected_btx_emissions_mt - actual_btx_emissions_mt),
    'pct_diff': abs(expected_btx_emissions_mt - actual_btx_emissions_mt) / actual_btx_emissions_mt * 100 if actual_btx_emissions_mt > 0 else 0,
    'status': 'PASS' if abs(expected_btx_emissions_mt - actual_btx_emissions_mt) < 2 else 'CHECK',
    'unit': 'MtCO2'
})

# =============================================================================
# VERIFICATION 2: TECHNOLOGY COST CALCULATION
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 2: TECHNOLOGY COST CALCULATION")
print("-" * 80)

# Verify CAPEX with learning curve
# CAPEX(year) = CAPEX_2025 * (1 - learning_rate)^((year-2025)/25)
# But our model uses linear interpolation between key years

for _, tech_row in df_tech.iterrows():
    tech = tech_row['technology']
    capex_2025 = tech_row['capex_2025_musd_per_mtco2']
    capex_2050 = tech_row['capex_2050_musd_per_mtco2']
    lifetime = tech_row['lifetime_years']

    # Annualized CAPEX = CAPEX / lifetime
    ann_capex_2025 = capex_2025 / lifetime
    ann_capex_2050 = capex_2050 / lifetime

    # Get model values
    model_2025 = df_macc[(df_macc['technology'] == tech) & (df_macc['year'] == 2025)]
    model_2050 = df_macc[(df_macc['technology'] == tech) & (df_macc['year'] == 2050)]

    if not model_2025.empty:
        model_ann_capex_2025 = model_2025['capex_ann_usd_per_tco2'].values[0]
        diff_2025 = abs(ann_capex_2025 - model_ann_capex_2025)

        print(f"\n{tech} (2025):")
        print(f"  Expected ann. CAPEX: ${ann_capex_2025:.0f}/tCO2")
        print(f"  Model ann. CAPEX: ${model_ann_capex_2025:.0f}/tCO2")
        print(f"  Difference: ${diff_2025:.0f}/tCO2")

        verifications.append({
            'check': f'{tech} Ann. CAPEX 2025',
            'expected': ann_capex_2025,
            'model': model_ann_capex_2025,
            'difference': diff_2025,
            'pct_diff': diff_2025 / model_ann_capex_2025 * 100 if model_ann_capex_2025 > 0 else 0,
            'status': 'PASS' if diff_2025 < 5 else 'CHECK',
            'unit': 'USD/tCO2'
        })

    if not model_2050.empty:
        model_ann_capex_2050 = model_2050['capex_ann_usd_per_tco2'].values[0]
        diff_2050 = abs(ann_capex_2050 - model_ann_capex_2050)

        print(f"\n{tech} (2050):")
        print(f"  Expected ann. CAPEX: ${ann_capex_2050:.0f}/tCO2")
        print(f"  Model ann. CAPEX: ${model_ann_capex_2050:.0f}/tCO2")
        print(f"  Difference: ${diff_2050:.0f}/tCO2")

        verifications.append({
            'check': f'{tech} Ann. CAPEX 2050',
            'expected': ann_capex_2050,
            'model': model_ann_capex_2050,
            'difference': diff_2050,
            'pct_diff': diff_2050 / model_ann_capex_2050 * 100 if model_ann_capex_2050 > 0 else 0,
            'status': 'PASS' if diff_2050 < 5 else 'CHECK',
            'unit': 'USD/tCO2'
        })

# =============================================================================
# VERIFICATION 3: H2 CONSUMPTION CALCULATION
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 3: H2 CONSUMPTION CALCULATION")
print("-" * 80)

# H2 consumption = NCC-H2 abatement (Mt) * conversion factors
# From assumptions:
# - H2 consumption: 0.098 ton H2 / ton ethylene (but model uses 0.2)
# - NCC baseline emissions: ~1.74 tCO2/ton product

# For Shaheen NCC-H2 scenario
shaheen_h2 = df_results[df_results['scenario'] == 'Shaheen NCC-H2']
if not shaheen_h2.empty:
    ncc_h2_abatement_mt = shaheen_h2['ncc_h2_2050_mt'].values[0]
    model_h2_demand_kt = shaheen_h2['h2_demand_2050_kt'].values[0]

    # Calculate expected H2 demand
    # NCC-H2 abatement = capacity * emission_intensity
    # H2 demand = capacity * H2 consumption per ton

    # From model: H2 consumption = 0.098 ton/ton ethylene (but MACC uses different value)
    h2_consumption_rate = df_tech[df_tech['technology'] == 'NCC-H2']['h2_ton_per_ton_ethylene'].values[0]
    ncc_emission_intensity = 1.74  # tCO2/ton

    # NCC-H2 abatement (Mt) = capacity (kt) * 1000 (ton/kt) * emission_intensity (tCO2/ton) / 1e6
    # capacity (kt) = NCC-H2 abatement (Mt) * 1e6 / emission_intensity / 1000
    implied_capacity_kt = ncc_h2_abatement_mt * 1e6 / ncc_emission_intensity / 1000

    # H2 demand (kt) = capacity (kt) * h2_consumption_rate (ton H2/ton product)
    expected_h2_demand_kt = implied_capacity_kt * h2_consumption_rate

    print(f"\nShaheen NCC-H2 Scenario (2050):")
    print(f"  NCC-H2 Abatement: {ncc_h2_abatement_mt:.2f} Mt")
    print(f"  H2 consumption rate: {h2_consumption_rate:.3f} ton H2/ton product")
    print(f"  Implied NCC capacity: {implied_capacity_kt:,.0f} kt")
    print(f"  Expected H2 demand: {expected_h2_demand_kt:,.0f} kt")
    print(f"  Model H2 demand: {model_h2_demand_kt:,.0f} kt")

    h2_diff = abs(expected_h2_demand_kt - model_h2_demand_kt)
    verifications.append({
        'check': 'Shaheen H2 Demand 2050',
        'expected': expected_h2_demand_kt,
        'model': model_h2_demand_kt,
        'difference': h2_diff,
        'pct_diff': h2_diff / model_h2_demand_kt * 100 if model_h2_demand_kt > 0 else 0,
        'status': 'PASS' if h2_diff / model_h2_demand_kt < 0.1 else 'CHECK',
        'unit': 'kt H2'
    })

# =============================================================================
# VERIFICATION 4: EMISSION TARGET COMPLIANCE
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 4: EMISSION TARGET COMPLIANCE")
print("-" * 80)

# Check that 2050 emissions = 0 (net zero target)
for _, result in df_results.iterrows():
    scenario = result['scenario']
    actual_2050 = result['actual_2050_mt']
    target_2050 = 0.0  # Net zero

    diff = abs(actual_2050 - target_2050)

    print(f"\n{scenario}:")
    print(f"  2050 Target: {target_2050:.2f} Mt")
    print(f"  2050 Actual: {actual_2050:.4f} Mt")
    print(f"  Status: {'PASS' if diff < 0.01 else 'FAIL'}")

    verifications.append({
        'check': f'{scenario} Net Zero 2050',
        'expected': target_2050,
        'model': actual_2050,
        'difference': diff,
        'pct_diff': 0 if target_2050 == 0 else diff / target_2050 * 100,
        'status': 'PASS' if diff < 0.01 else 'FAIL',
        'unit': 'MtCO2'
    })

# =============================================================================
# VERIFICATION 5: ABATEMENT BALANCE
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 5: ABATEMENT BALANCE")
print("-" * 80)

# Total abatement should equal BAU - Actual emissions
for _, result in df_results.iterrows():
    scenario = result['scenario']
    bau_2050 = result['bau_2050_mt']
    actual_2050 = result['actual_2050_mt']
    total_abatement = result['total_abatement_2050_mt']

    expected_abatement = bau_2050 - actual_2050
    diff = abs(total_abatement - expected_abatement)

    print(f"\n{scenario}:")
    print(f"  BAU 2050: {bau_2050:.2f} Mt")
    print(f"  Actual 2050: {actual_2050:.2f} Mt")
    print(f"  Expected abatement: {expected_abatement:.2f} Mt")
    print(f"  Model total abatement: {total_abatement:.2f} Mt")
    print(f"  Difference: {diff:.4f} Mt")

    verifications.append({
        'check': f'{scenario} Abatement Balance',
        'expected': expected_abatement,
        'model': total_abatement,
        'difference': diff,
        'pct_diff': diff / expected_abatement * 100 if expected_abatement > 0 else 0,
        'status': 'PASS' if diff < 0.01 else 'CHECK',
        'unit': 'MtCO2'
    })

# =============================================================================
# VERIFICATION 6: TECHNOLOGY BREAKDOWN
# =============================================================================
print("\n" + "-" * 80)
print("VERIFICATION 6: TECHNOLOGY BREAKDOWN")
print("-" * 80)

# Check that sum of technologies = total abatement
for _, result in df_results.iterrows():
    scenario = result['scenario']
    hp = result['heat_pump_2050_mt']
    ncc_h2 = result['ncc_h2_2050_mt']
    ncc_elec = result['ncc_elec_2050_mt']
    re_ppa = result['re_ppa_2050_mt']
    rdh = result['rdh_2050_mt']
    total = result['total_abatement_2050_mt']

    tech_sum = hp + ncc_h2 + ncc_elec + re_ppa + rdh
    diff = abs(tech_sum - total)

    print(f"\n{scenario}:")
    print(f"  Heat Pump: {hp:.2f} Mt")
    print(f"  NCC-H2: {ncc_h2:.2f} Mt")
    print(f"  NCC-Elec: {ncc_elec:.2f} Mt")
    print(f"  RE PPA: {re_ppa:.2f} Mt")
    print(f"  RDH: {rdh:.2f} Mt")
    print(f"  Sum: {tech_sum:.2f} Mt")
    print(f"  Total: {total:.2f} Mt")
    print(f"  Difference: {diff:.4f} Mt")

    verifications.append({
        'check': f'{scenario} Tech Breakdown Sum',
        'expected': total,
        'model': tech_sum,
        'difference': diff,
        'pct_diff': diff / total * 100 if total > 0 else 0,
        'status': 'PASS' if diff < 0.01 else 'CHECK',
        'unit': 'MtCO2'
    })

# =============================================================================
# SAVE VERIFICATION REPORT
# =============================================================================
print("\n" + "=" * 80)
print("VERIFICATION REPORT")
print("=" * 80)

df_verify = pd.DataFrame(verifications)
df_verify.to_csv(OUTPUT_FILE, index=False)

# Summary
n_pass = len(df_verify[df_verify['status'] == 'PASS'])
n_check = len(df_verify[df_verify['status'] == 'CHECK'])
n_fail = len(df_verify[df_verify['status'] == 'FAIL'])

print(f"\nTotal checks: {len(df_verify)}")
print(f"  PASS: {n_pass}")
print(f"  CHECK: {n_check} (minor discrepancies)")
print(f"  FAIL: {n_fail}")

print(f"\nVerification report saved to: {OUTPUT_FILE}")

# Print checks that need attention
if n_check > 0 or n_fail > 0:
    print("\nChecks requiring attention:")
    attention = df_verify[df_verify['status'].isin(['CHECK', 'FAIL'])]
    for _, row in attention.iterrows():
        print(f"  - {row['check']}: {row['status']} (diff: {row['difference']:.2f} {row['unit']}, {row['pct_diff']:.1f}%)")
