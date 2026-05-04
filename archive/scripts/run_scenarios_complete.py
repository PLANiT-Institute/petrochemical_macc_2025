"""
Complete Scenario Runner - Full Coverage Implementation
========================================================
Generates all 6 scenarios with ZERO residual emissions:

Technologies deployed:
1. NCC-H2 or NCC-Electricity: For Naphtha Cracker facilities
2. RDH (RotoDynamic Heater): For BTX Plant high-temperature processes
3. Heat Pump: For low-temperature heat (<165°C) in all processes
4. RE-PPA: For ALL remaining electricity emissions (grid decarbonization)

NO CCS/CCUS - only electrification and renewable energy

Scenarios:
1. Shaheen (Growth) + NCC-H2: Add 6 new Shaheen facilities (254 total)
2. Shaheen (Growth) + NCC-Electricity: Add 6 new Shaheen facilities (254 total)
3. Restructure 25% + NCC-H2: Retire oldest NCC = 25% NCC capacity (239 total)
4. Restructure 25% + NCC-Electricity: Retire oldest NCC = 25% NCC capacity (239 total)
5. Restructure 40% + NCC-H2: Retire oldest NCC = 40% NCC capacity (232 total)
6. Restructure 40% + NCC-Electricity: Retire oldest NCC = 40% NCC capacity (232 total)
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("한국 석유화학 MACC 모델 - Complete Scenario Analysis (Full Coverage)")
print("="*80)

# =============================================================================
# PATHS
# =============================================================================
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')

# =============================================================================
# LOAD DATA
# =============================================================================
print("\nLoading data...")

df_fac = pd.read_csv(DATA_DIR / 'facility_database_with_regions.csv')
df_energy = pd.read_csv(DATA_DIR / 'energy_intensities.csv')
df_ef = pd.read_csv(DATA_DIR / 'emission_factors.csv')
df_grid = pd.read_csv(DATA_DIR / 'grid_emission_trajectory.csv')
df_tech = pd.read_csv(DATA_DIR / 'technology_parameters.csv')

print(f"  Facilities: {len(df_fac)}")
print(f"  Energy intensities: {len(df_energy)}")

# Extract emission factors
ef = {}
for _, row in df_ef.iterrows():
    fuel = row['fuel']
    if pd.notna(row.get('tCO2_per_GJ')):
        ef[fuel] = row['tCO2_per_GJ']
    elif pd.notna(row.get('tCO2_per_kWh')):
        ef[fuel] = row['tCO2_per_kWh']

# Grid emission factor trajectory
grid_ef = df_grid.set_index('year')['grid_ef_tco2_per_mwh'].to_dict()

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

# =============================================================================
# EMISSION CALCULATION FUNCTIONS
# =============================================================================

def calculate_facility_emissions_detailed(fac_row, energy_row, grid_ef_value):
    """Calculate detailed emissions breakdown for a single facility"""
    capacity = fac_row['capacity_kt'] * 1000  # Convert to tonnes
    process = fac_row['process']

    # Fossil fuel emissions by temperature category
    # High-temp: Naphtha cracking, BTX reforming (>500°C)
    # Medium-temp: Steam generation, heating (165-500°C)
    # Low-temp: Pre-heating, utility (<165°C)

    # Calculate fuel emissions by type
    naphtha_emissions = energy_row['Naphtha_GJ_per_tonne'] * capacity * ef.get('Naphtha', 0.0744) / 1000
    lng_emissions = energy_row['LNG_GJ_per_tonne'] * capacity * ef.get('LNG', 0.0561) / 1000
    fuel_gas_emissions = energy_row['Fuel_Gas_GJ_per_tonne'] * capacity * ef.get('Fuel_Gas', 0.0561) / 1000
    byproduct_emissions = energy_row['Byproduct_Gas_GJ_per_tonne'] * capacity * ef.get('Byproduct_Gas', 0.0561) / 1000
    lpg_emissions = energy_row.get('LPG_GJ_per_tonne', 0) * capacity * ef.get('LPG', 0.0631) / 1000
    fuel_oil_emissions = energy_row.get('Fuel_Oil_GJ_per_tonne', 0) * capacity * ef.get('Fuel_Oil', 0.0774) / 1000
    diesel_emissions = energy_row.get('Diesel_GJ_per_tonne', 0) * capacity * ef.get('Diesel', 0.0741) / 1000

    total_fossil = (naphtha_emissions + lng_emissions + fuel_gas_emissions +
                   byproduct_emissions + lpg_emissions + fuel_oil_emissions + diesel_emissions)

    # Categorize by process type for technology applicability
    if process == 'Naphtha Cracker':
        # NCC: High-temp cracking - covered by NCC-H2 or NCC-Electricity
        high_temp_fossil = total_fossil * 0.85  # 85% is high-temp cracking
        low_temp_fossil = total_fossil * 0.15   # 15% is utility/pre-heating
        btx_fossil = 0
    elif process == 'BTX Plant':
        # BTX: High-temp reforming - covered by RDH
        high_temp_fossil = 0
        btx_fossil = total_fossil * 0.80  # 80% is high-temp reforming
        low_temp_fossil = total_fossil * 0.20  # 20% is utility
    else:  # Utility processes
        # Utility: Mostly low-temp heat - covered by Heat Pump
        high_temp_fossil = 0
        btx_fossil = 0
        low_temp_fossil = total_fossil  # All utility is low-temp

    # Electricity emissions (covered by RE-PPA)
    elec_kwh = energy_row['Electricity_kWh_per_tonne'] * capacity
    elec_mwh = elec_kwh / 1000
    elec_emissions = elec_mwh * grid_ef_value / 1000  # kt CO2

    return {
        'total_fossil_kt': total_fossil,
        'ncc_fossil_kt': high_temp_fossil if process == 'Naphtha Cracker' else 0,
        'btx_fossil_kt': btx_fossil,
        'low_temp_fossil_kt': low_temp_fossil,
        'elec_emissions_kt': elec_emissions,
        'elec_mwh': elec_mwh,
        'total_emissions_kt': total_fossil + elec_emissions
    }


def calculate_scenario_emissions(facilities_df, energy_df, year=2050):
    """Calculate detailed emissions for a scenario"""
    grid_ef_value = grid_ef.get(year, 0.07)

    totals = {
        'total_fossil_kt': 0,
        'ncc_fossil_kt': 0,
        'btx_fossil_kt': 0,
        'low_temp_fossil_kt': 0,
        'elec_emissions_kt': 0,
        'elec_mwh': 0,
        'total_emissions_kt': 0
    }

    facility_details = []

    for idx, fac_row in facilities_df.iterrows():
        energy_row = energy_df.iloc[idx]
        em = calculate_facility_emissions_detailed(fac_row, energy_row, grid_ef_value)

        for key in totals:
            totals[key] += em[key]

        facility_details.append({
            'facility_idx': idx,
            'product': fac_row['product'],
            'process': fac_row['process'],
            'company': fac_row['company'],
            'location': fac_row['location'],
            'capacity_kt': fac_row['capacity_kt'],
            'year_built': fac_row['year_built'],
            'age_2025': fac_row['age_2025'],
            'ncc_fossil_kt': em['ncc_fossil_kt'],
            'btx_fossil_kt': em['btx_fossil_kt'],
            'low_temp_fossil_kt': em['low_temp_fossil_kt'],
            'elec_emissions_kt': em['elec_emissions_kt'],
            'total_emissions_kt': em['total_emissions_kt'],
            'elec_mwh': em['elec_mwh']
        })

    return totals, pd.DataFrame(facility_details)


# =============================================================================
# SCENARIO GENERATORS
# =============================================================================

def create_shaheen_scenario():
    """Add Shaheen facilities"""
    fac = df_fac.copy()
    energy = df_energy.copy()

    new_facilities = []
    new_energies = []

    for prod, proc, comp, loc, cpx, cap, yr, naphtha, elec, lng, fg, bp in SHAHEEN_NEW:
        new_fac = {
            'product': prod, 'process': proc, 'company': comp,
            'location': loc, 'complex': cpx, 'capacity_kt': cap,
            'year_built': yr, 'age_2025': -1, 'remaining_life': 41,
            'retirement_year_40yr': 2066
        }
        new_facilities.append(new_fac)

        new_energy = {
            'product': prod, 'process': proc, 'company': comp,
            'location': loc, 'capacity_kt': cap, 'year_built': yr,
            'Naphtha_GJ_per_tonne': naphtha, 'Electricity_kWh_per_tonne': elec,
            'LNG_GJ_per_tonne': lng, 'Fuel_Gas_GJ_per_tonne': fg,
            'Byproduct_Gas_GJ_per_tonne': bp, 'LPG_GJ_per_tonne': 0.0,
            'Fuel_Oil_GJ_per_tonne': 0.0, 'Diesel_GJ_per_tonne': 0.0
        }
        new_energies.append(new_energy)

    fac = pd.concat([fac, pd.DataFrame(new_facilities)], ignore_index=True)
    energy = pd.concat([energy, pd.DataFrame(new_energies)], ignore_index=True)

    return fac, energy, "Shaheen (성장)"


def create_restructure_scenario(retire_pct):
    """Retire oldest NCC facilities"""
    fac = df_fac.copy()
    energy = df_energy.copy()

    # Sort NCC by age (oldest first)
    ncc_mask = fac['process'] == 'Naphtha Cracker'
    ncc_indices = fac[ncc_mask].sort_values('age_2025', ascending=False).index.tolist()

    total_ncc_cap = fac.loc[ncc_indices, 'capacity_kt'].sum()
    target_cap = total_ncc_cap * retire_pct

    # Find facilities to retire
    cumsum = 0
    retire_indices = []
    for idx in ncc_indices:
        if cumsum < target_cap:
            retire_indices.append(idx)
            cumsum += fac.loc[idx, 'capacity_kt']
        else:
            break

    # Create retired facilities list for output
    retired = fac.loc[retire_indices].copy()

    # Remove retired facilities
    fac = fac.drop(retire_indices).reset_index(drop=True)
    energy = energy.drop(retire_indices).reset_index(drop=True)

    name = f"구조조정 {retire_pct*100:.0f}%"
    return fac, energy, name, retired


# =============================================================================
# COST CALCULATION
# =============================================================================

def calculate_capex(abatement_mt, technology, year):
    """Calculate CAPEX for technology deployment"""
    # Technology costs from technology_parameters.csv (50% decline by 2050)
    tech_costs = {
        'NCC-H2': {'2025': 1700, '2030': 1445, '2040': 1105, '2050': 850},
        'NCC-Electricity': {'2025': 1500, '2030': 1275, '2040': 975, '2050': 750},
        'Heat_Pump': {'2025': 800, '2030': 680, '2040': 520, '2050': 400},
        'RDH': {'2025': 900, '2030': 765, '2040': 585, '2050': 450},
        'RE_PPA': {'2025': 50, '2030': 40, '2040': 30, '2050': 25}  # Per MWh basis
    }

    # Interpolate cost for year
    years = [2025, 2030, 2040, 2050]
    costs = [tech_costs[technology][str(y)] for y in years]
    cost = np.interp(year, years, costs)

    # CAPEX = cost per tCO2 * abatement (Mt)
    capex_musd = cost * abatement_mt

    return capex_musd


# =============================================================================
# MAIN SCENARIO ANALYSIS
# =============================================================================

print("\n" + "="*80)
print("GENERATING 6 SCENARIOS (Full Coverage - Net Zero)")
print("="*80)

results = []
all_facility_data = {}

# Generate base scenarios
r25_data = create_restructure_scenario(0.25)
r40_data = create_restructure_scenario(0.40)

scenarios = [
    (create_shaheen_scenario()[0], create_shaheen_scenario()[1], "Shaheen (성장)"),
    (r25_data[0], r25_data[1], r25_data[2]),
    (r40_data[0], r40_data[1], r40_data[2]),
]

# Save retired facilities info
retired_25 = r25_data[3] if len(r25_data) > 3 else None
retired_40 = r40_data[3] if len(r40_data) > 3 else None

technologies = ['NCC-H2', 'NCC-Electricity']

for fac_df, energy_df, scenario_name in scenarios:
    for tech in technologies:
        print(f"\n--- {scenario_name} + {tech} ---")

        # Create scenario ID
        if 'Shaheen' in scenario_name:
            scenario_id = f'shaheen_{tech.lower().replace("-", "_")}'
        elif '25%' in scenario_name:
            scenario_id = f'restructure_25pct_{tech.lower().replace("-", "_")}'
        elif '40%' in scenario_name:
            scenario_id = f'restructure_40pct_{tech.lower().replace("-", "_")}'
        else:
            scenario_id = f'{scenario_name}_{tech}'.lower().replace(' ', '_').replace('-', '_')

        # Calculate baseline statistics
        n_facilities = len(fac_df)
        n_ncc = len(fac_df[fac_df['process'] == 'Naphtha Cracker'])
        n_btx = len(fac_df[fac_df['process'] == 'BTX Plant'])
        n_utility = len(fac_df[fac_df['process'] == 'Utility'])
        total_cap = fac_df['capacity_kt'].sum()
        ncc_cap = fac_df[fac_df['process'] == 'Naphtha Cracker']['capacity_kt'].sum()

        # Calculate detailed BAU emissions at 2050
        totals, facility_details = calculate_scenario_emissions(fac_df, energy_df, 2050)
        bau_mt = totals['total_emissions_kt'] / 1000  # Convert kt to Mt

        # Technology abatement (FULL COVERAGE)
        # 1. NCC-H2 or NCC-Electricity covers NCC fossil emissions
        ncc_abatement_mt = totals['ncc_fossil_kt'] / 1000

        # 2. RDH covers BTX high-temp fossil emissions
        rdh_abatement_mt = totals['btx_fossil_kt'] / 1000

        # 3. Heat Pump covers low-temp fossil emissions (all processes)
        heat_pump_abatement_mt = totals['low_temp_fossil_kt'] / 1000

        # 4. RE-PPA covers ALL electricity emissions
        re_ppa_abatement_mt = totals['elec_emissions_kt'] / 1000

        # Total abatement = BAU (should be 100% coverage)
        total_abatement = ncc_abatement_mt + rdh_abatement_mt + heat_pump_abatement_mt + re_ppa_abatement_mt
        net_emissions = max(0, bau_mt - total_abatement)

        # Calculate CAPEX (average deployment year = 2040)
        capex = 0
        if tech == 'NCC-H2':
            capex += calculate_capex(ncc_abatement_mt, 'NCC-H2', 2040)
        else:
            capex += calculate_capex(ncc_abatement_mt, 'NCC-Electricity', 2040)
        capex += calculate_capex(rdh_abatement_mt, 'RDH', 2040)
        capex += calculate_capex(heat_pump_abatement_mt, 'Heat_Pump', 2040)
        capex += calculate_capex(re_ppa_abatement_mt, 'RE_PPA', 2040)

        capex_billion = capex / 1000

        # Calculate energy requirements
        if tech == 'NCC-H2':
            # H2 for NCC: 0.2 t H2 per t ethylene equivalent
            # Approximate based on abatement
            h2_consumption_kt = ncc_abatement_mt * 1000 * 0.2 / 0.12
            elec_increase_twh = totals['elec_mwh'] / 1e6  # RE-PPA electricity
        else:
            h2_consumption_kt = 0
            # NCC-Electricity: 5 MWh per ton ethylene equivalent + RE-PPA
            ncc_elec_twh = ncc_abatement_mt * 1000 * 5 / 1e6
            elec_increase_twh = ncc_elec_twh + totals['elec_mwh'] / 1e6

        # RDH electricity (Coolbrook RotoDynamic Heater)
        rdh_elec_twh = rdh_abatement_mt * 1000 * 3 / 1e6  # ~3 MWh per tCO2
        elec_increase_twh += rdh_elec_twh

        # Heat pump electricity (COP=4)
        hp_elec_twh = heat_pump_abatement_mt * 1000 * 0.5 / 1e6  # ~0.5 MWh per tCO2
        elec_increase_twh += hp_elec_twh

        print(f"  Facilities: {n_facilities} (NCC: {n_ncc}, BTX: {n_btx}, Utility: {n_utility})")
        print(f"  Capacity: {total_cap:,.0f} kt (NCC: {ncc_cap:,.0f} kt)")
        print(f"  BAU 2050: {bau_mt:.2f} Mt")
        print(f"    - NCC fossil: {ncc_abatement_mt:.2f} Mt (covered by {tech})")
        print(f"    - BTX fossil: {rdh_abatement_mt:.2f} Mt (covered by RDH)")
        print(f"    - Low-temp heat: {heat_pump_abatement_mt:.2f} Mt (covered by Heat Pump)")
        print(f"    - Electricity: {re_ppa_abatement_mt:.2f} Mt (covered by RE-PPA)")
        print(f"  Net 2050: {net_emissions:.2f} Mt (should be ~0)")
        print(f"  CAPEX: ${capex_billion:.1f}B")

        result = {
            'scenario': scenario_name,
            'technology': tech,
            'scenario_id': scenario_id,
            'n_facilities': n_facilities,
            'n_ncc_facilities': n_ncc,
            'n_btx_facilities': n_btx,
            'n_utility_facilities': n_utility,
            'total_capacity_kt': total_cap,
            'ncc_capacity_kt': ncc_cap,
            'bau_2050_mt': bau_mt,
            'net_2050_mt': net_emissions,
            'capex_billion_usd': capex_billion,
            'ncc_abatement_mt': ncc_abatement_mt,
            'rdh_abatement_mt': rdh_abatement_mt,
            'heat_pump_mt': heat_pump_abatement_mt,
            're_ppa_mt': re_ppa_abatement_mt,
            'electricity_twh': elec_increase_twh,
            'h2_kt': h2_consumption_kt
        }
        results.append(result)

        # Save facility details
        output_dir = OUTPUT_DIR / f'scenario_{scenario_id}'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save scenario facilities
        fac_df.to_csv(output_dir / 'scenario_facilities.csv', index=False)
        facility_details.to_csv(output_dir / 'facility_emissions_2050.csv', index=False)

        # Create deployment trajectory
        years = list(range(2025, 2051))
        deployment_data = []
        for year in years:
            totals_year, _ = calculate_scenario_emissions(fac_df, energy_df, year)
            bau_year_mt = totals_year['total_emissions_kt'] / 1000

            # Linear deployment from 2025 to 2050
            deploy_pct = min(1.0, (year - 2025) / 25)
            deployed_abatement = total_abatement * deploy_pct
            actual_emissions = max(0, bau_year_mt - deployed_abatement)

            deployment_data.append({
                'year': year,
                'bau_mt': bau_year_mt,
                'deployed_abatement_mt': deployed_abatement,
                'actual_emissions_mt': actual_emissions,
                'ncc_deployed_mt': ncc_abatement_mt * deploy_pct,
                'rdh_deployed_mt': rdh_abatement_mt * deploy_pct,
                'heat_pump_deployed_mt': heat_pump_abatement_mt * deploy_pct,
                're_ppa_deployed_mt': re_ppa_abatement_mt * deploy_pct,
                'grid_ef': grid_ef.get(year, 0.436 if year == 2025 else 0.07)
            })

        df_deploy = pd.DataFrame(deployment_data)
        df_deploy.to_csv(output_dir / 'deployment_trajectory.csv', index=False)

        # Store for report generation
        all_facility_data[scenario_id] = {
            'facilities': fac_df,
            'facility_emissions': facility_details,
            'deployment': df_deploy,
            'result': result
        }

# =============================================================================
# SAVE SUMMARY
# =============================================================================

df_results = pd.DataFrame(results)
summary_path = OUTPUT_DIR / 'scenario_summary_final.csv'
df_results.to_csv(summary_path, index=False)
print(f"\n✓ Saved: {summary_path}")

# =============================================================================
# PRINT COMPARISON TABLE
# =============================================================================

print("\n" + "="*80)
print("SCENARIO COMPARISON (2050) - FULL COVERAGE")
print("="*80)

print(f"\n{'Scenario':<40} {'Fac':>6} {'NCC':>5} {'BTX':>5} {'BAU Mt':>10} {'Net Mt':>10} {'CAPEX $B':>10}")
print("-"*95)
for _, r in df_results.iterrows():
    label = f"{r['scenario']} + {r['technology']}"
    print(f"{label:<40} {r['n_facilities']:>6} {r['n_ncc_facilities']:>5} {r['n_btx_facilities']:>5} {r['bau_2050_mt']:>10.2f} {r['net_2050_mt']:>10.2f} {r['capex_billion_usd']:>10.1f}")

# =============================================================================
# TECHNOLOGY COVERAGE SUMMARY
# =============================================================================

print("\n" + "="*80)
print("TECHNOLOGY COVERAGE SUMMARY")
print("="*80)

print("""
Technology Coverage (ALL emissions covered - Net Zero achieved):
┌─────────────────────────────────────────────────────────────────────────┐
│ Process Type      │ Emission Source    │ Technology           │ Year   │
├───────────────────┼────────────────────┼──────────────────────┼────────┤
│ Naphtha Cracker   │ High-temp cracking │ NCC-H2 or NCC-Elec   │ 2030+  │
│ BTX Plant         │ High-temp reforming│ RDH (Coolbrook)      │ 2026+  │
│ All Processes     │ Low-temp heat      │ Heat Pump (COP 4.0)  │ 2025+  │
│ All Processes     │ Grid electricity   │ RE-PPA (100% RE)     │ 2025+  │
└─────────────────────────────────────────────────────────────────────────┘

NO CCS/CCUS - Only electrification and renewable energy solutions
""")

# =============================================================================
# ABATEMENT BREAKDOWN
# =============================================================================

print("\n" + "="*80)
print("ABATEMENT BY TECHNOLOGY (2050)")
print("="*80)

for _, r in df_results.iterrows():
    label = f"{r['scenario']} + {r['technology']}"
    print(f"\n{label}:")
    print(f"  {r['technology']}: {r['ncc_abatement_mt']:.2f} Mt ({r['ncc_abatement_mt']/r['bau_2050_mt']*100:.1f}%)")
    print(f"  RDH (BTX):    {r['rdh_abatement_mt']:.2f} Mt ({r['rdh_abatement_mt']/r['bau_2050_mt']*100:.1f}%)")
    print(f"  Heat Pump:    {r['heat_pump_mt']:.2f} Mt ({r['heat_pump_mt']/r['bau_2050_mt']*100:.1f}%)")
    print(f"  RE-PPA:       {r['re_ppa_mt']:.2f} Mt ({r['re_ppa_mt']/r['bau_2050_mt']*100:.1f}%)")
    print(f"  Total:        {r['ncc_abatement_mt']+r['rdh_abatement_mt']+r['heat_pump_mt']+r['re_ppa_mt']:.2f} Mt")
    print(f"  Net 2050:     {r['net_2050_mt']:.2f} Mt")

# =============================================================================
# SAVE RETIRED FACILITIES INFO
# =============================================================================

if retired_25 is not None:
    retired_25.to_csv(OUTPUT_DIR / 'restructure_25pct_retired_facilities.csv', index=False)
    print(f"\n✓ Saved retired facilities list (25%): {len(retired_25)} NCC facilities")

if retired_40 is not None:
    retired_40.to_csv(OUTPUT_DIR / 'restructure_40pct_retired_facilities.csv', index=False)
    print(f"✓ Saved retired facilities list (40%): {len(retired_40)} NCC facilities")

print("\n" + "="*80)
print("COMPLETE - ALL SCENARIOS ACHIEVE NET ZERO")
print("="*80)
