"""
SCENARIO RUNNER - Cost-Optimized with Emission Constraints
==========================================================
Runs all 6 scenarios with ANNUAL results (2025-2050).

Outputs (separate files per scenario):
- outputs/{scenario_name}.csv - Facility-level annual results
- outputs/regional_mac_summary.csv - Regional MAC curves by scenario/year
- outputs/regional_abatement_summary.csv - Regional abatement by scenario/year
- outputs/scenario_results.csv - Combined results (all scenarios)

Emission Constraints (from baseline):
- 2035: 24.5% reduction (Korea industry sector NDC target)
- 2050: 100% reduction (Net Zero)

Optimization Approach:
- Cost-optimization: Deploy technologies by MAC order (lowest cost first)
- Facilities are ranked by MAC and deployed until emission target is met
- Each facility gets an installation year based on when it's needed to meet targets

Technology application logic:
- NCC facilities: NCC-H2 or NCC-Electricity for naphtha combustion
                 + Heat Pump for LNG/Fuel_Gas/Byproduct_Gas
- BTX facilities: RDH for high-temp heat
- Other facilities: Heat Pump for all combustion emissions
- All facilities: Grid decarbonization handles electricity (0 by 2050)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from modules.utils import DataLoader

# Configuration
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Years for analysis - ANNUAL from 2025 to 2050
YEARS = list(range(2025, 2051))  # 26 years

# Key emission reduction targets (will be interpolated for annual)
KEY_TARGETS = {
    2025: 0.000,   # 0% reduction (baseline)
    2030: 0.150,   # 15% reduction
    2035: 0.245,   # 24.5% reduction (Korea industry NDC)
    2040: 0.500,   # 50% reduction
    2045: 0.750,   # 75% reduction
    2050: 1.000,   # 100% reduction (Net Zero)
}

# Interpolate emission targets for all years
def interpolate_targets(key_targets, years):
    """Interpolate emission targets for annual years"""
    key_years = sorted(key_targets.keys())
    key_values = [key_targets[y] for y in key_years]
    return {y: np.interp(y, key_years, key_values) for y in years}

EMISSION_TARGETS = interpolate_targets(KEY_TARGETS, YEARS)

# Scenarios: 6 combinations
SCENARIOS = [
    {'name': 'shaheen_ncc_h2', 'production': 'shaheen', 'ncc_tech': 'NCC-H2'},
    {'name': 'shaheen_ncc_elec', 'production': 'shaheen', 'ncc_tech': 'NCC-Electricity'},
    {'name': 'restructure_25pct_ncc_h2', 'production': 'restructure_25pct', 'ncc_tech': 'NCC-H2'},
    {'name': 'restructure_25pct_ncc_elec', 'production': 'restructure_25pct', 'ncc_tech': 'NCC-Electricity'},
    {'name': 'restructure_40pct_ncc_h2', 'production': 'restructure_40pct', 'ncc_tech': 'NCC-H2'},
    {'name': 'restructure_40pct_ncc_elec', 'production': 'restructure_40pct', 'ncc_tech': 'NCC-Electricity'},
]


def load_data():
    """Load all input data"""
    print("=" * 80)
    print("LOADING INPUT DATA")
    print("=" * 80)

    loader = DataLoader(DATA_DIR)

    data = {
        'facilities': loader.load_facilities(),
        'facilities_shaheen': pd.read_csv(DATA_DIR / 'facility_database_with_shaheen.csv'),
        'intensities': loader.load_energy_intensities(),
        'emission_factors': loader.load_emission_factors(),
        'tech_params': loader.load_technology_params(),
        'h2_prices': loader.load_h2_prices(),
        're_prices': loader.load_re_prices(),
        'grid_emissions': loader.load_grid_emissions(),
        'grid_prices': loader.load_grid_prices(),
        'fuel_prices': pd.read_csv(DATA_DIR / 'fuel_price_trajectory.csv'),
    }

    # Load operating rate trajectories
    data['op_rate_shaheen'] = pd.read_csv(DATA_DIR / 'demand_growth_trajectory_shaheen.csv')
    data['op_rate_restructure_25'] = pd.read_csv(DATA_DIR / 'demand_growth_trajectory_restructure_25pct.csv')
    data['op_rate_restructure_40'] = pd.read_csv(DATA_DIR / 'demand_growth_trajectory_restructure_40pct.csv')

    # Create intensity lookup by key (company, product, location) for safe matching
    intensities = data['intensities']
    intensities['_key'] = intensities['company'] + '_' + intensities['product'] + '_' + intensities['location']
    data['intensity_lookup'] = intensities.set_index('_key').to_dict('index')

    print(f"  Loaded {len(data['facilities'])} baseline facilities")
    print(f"  Loaded {len(data['facilities_shaheen'])} facilities with Shaheen")
    print(f"  Loaded {len(data['tech_params'])} technologies")
    print(f"  Created intensity lookup with {len(data['intensity_lookup'])} entries")

    return data


def get_region(location):
    """Map location to region"""
    region_map = {
        'Yeosu': 'Yeosu',
        'Daesan': 'Daesan',
        'Ulsan': 'Ulsan',
        'Onsan': 'Ulsan',  # Onsan is part of Ulsan complex
    }
    return region_map.get(location, 'Other')


def is_ncc_facility(process):
    """Check if facility is a naphtha cracker"""
    return process == 'Naphtha Cracker'


def is_btx_facility(process):
    """Check if facility is a BTX aromatics plant"""
    return process == 'BTX Plant'


def calculate_facility_baseline(facility, intensity, operating_rate, grid_ef, capacity_multiplier=1.0):
    """
    Calculate baseline emissions for a facility (no technology deployment).

    Args:
        facility: Facility data row
        intensity: Energy intensity data row
        operating_rate: Operating rate (0-1)
        grid_ef: Grid emission factor (tCO2/MWh)
        capacity_multiplier: Capacity multiplier for restructure scenarios (0-1)
    """
    capacity_tonnes = facility['capacity_kt'] * 1000
    # Apply both capacity multiplier (restructure) and operating rate
    production_tonnes = capacity_tonnes * capacity_multiplier * operating_rate

    # Calculate emissions by fuel type
    emissions_by_source = {}

    # Naphtha (cracker furnace combustion)
    naphtha_gj = intensity.get('Naphtha_GJ_per_tonne', 0) * production_tonnes
    emissions_by_source['naphtha'] = naphtha_gj * 0.0542  # tCO2/GJ

    # Electricity
    elec_kwh = intensity.get('Electricity_kWh_per_tonne', 0) * production_tonnes
    elec_mwh = elec_kwh / 1000
    emissions_by_source['electricity'] = elec_mwh * grid_ef

    # LNG (steam/utilities)
    lng_gj = intensity.get('LNG_GJ_per_tonne', 0) * production_tonnes
    emissions_by_source['lng'] = lng_gj * 0.0561  # tCO2/GJ

    # Fuel Gas (process heat)
    fuel_gas_gj = intensity.get('Fuel_Gas_GJ_per_tonne', 0) * production_tonnes
    emissions_by_source['fuel_gas'] = fuel_gas_gj * 0.050  # tCO2/GJ

    # Byproduct Gas
    byproduct_gas_gj = intensity.get('Byproduct_Gas_GJ_per_tonne', 0) * production_tonnes
    emissions_by_source['byproduct_gas'] = byproduct_gas_gj * 0.048  # tCO2/GJ

    # Total heat demand (for Heat Pump sizing)
    total_heat_gj = naphtha_gj + lng_gj + fuel_gas_gj + byproduct_gas_gj

    # Combustion emissions (abatable by technology)
    combustion_emissions = (
        emissions_by_source['naphtha'] +
        emissions_by_source['lng'] +
        emissions_by_source['fuel_gas'] +
        emissions_by_source['byproduct_gas']
    )

    # Total baseline emissions
    total_emissions = combustion_emissions + emissions_by_source['electricity']

    return {
        'capacity_tpy': capacity_tonnes,
        'production_t': production_tonnes,
        'emissions_by_source': emissions_by_source,
        'combustion_emissions': combustion_emissions,
        'elec_emissions': emissions_by_source['electricity'],
        'total_emissions': total_emissions,
        'elec_demand_mwh': elec_mwh,
        'heat_demand_gj': total_heat_gj,
    }


def calculate_facility_mac(facility_baseline, process, ncc_tech, year, data, grid_ef):
    """
    Calculate MAC for full technology deployment at a facility.
    Used for ranking facilities by cost-effectiveness.
    """
    emissions = facility_baseline['emissions_by_source']

    # Get prices for the year
    h2_price = data['h2_prices'][data['h2_prices']['year'] == year]['h2_price_usd_per_kg'].iloc[0] \
        if year in data['h2_prices']['year'].values else 3.0
    re_price = data['re_prices'][data['re_prices']['year'] == year]['re_price_usd_per_mwh'].iloc[0] \
        if year in data['re_prices']['year'].values else 50.0

    # Calculate potential abatement (combustion emissions only - electricity handled by grid)
    potential_abatement = facility_baseline['combustion_emissions']

    if potential_abatement <= 0:
        return float('inf'), 'None', 0, 0, 0, 0, 0, 0.0, 25

    # Determine technology and calculate costs
    if is_ncc_facility(process):
        technology = ncc_tech
        naphtha_emissions = emissions.get('naphtha', 0)
        other_fuel_emissions = emissions.get('lng', 0) + emissions.get('fuel_gas', 0) + emissions.get('byproduct_gas', 0)

        if ncc_tech == 'NCC-H2':
            # H2 demand: 0.2 t-H2/t-C2H4 from tech spec
            # Convert from emissions: factor = 0.2 / (29.0 GJ/t * 0.0542 tCO2/GJ) = 0.127
            h2_demand_t = naphtha_emissions * 0.127
            fuel_cost = h2_demand_t * h2_price * 1000
            added_elec_mwh = 0
        else:
            # Electricity demand: 5.0 MWh/t-C2H4 from tech spec
            # Convert from emissions: factor = 5.0 / (29.0 GJ/t * 0.0542 tCO2/GJ) = 3.18
            h2_demand_t = 0
            added_elec_mwh = naphtha_emissions * 3.18
            fuel_cost = added_elec_mwh * re_price

        # Heat pump for other fuels
        heat_gj = facility_baseline['heat_demand_gj'] - emissions.get('naphtha', 0) / 0.0542
        heat_gj = max(0, heat_gj)
        hp_elec_mwh = heat_gj / 3.6 / 4.0
        added_elec_mwh += hp_elec_mwh
        fuel_cost += hp_elec_mwh * re_price

    elif is_btx_facility(process):
        technology = 'RDH'
        h2_demand_t = 0
        # RDH efficiency is 93%, so electricity needed = heat / efficiency
        # Convert GJ to MWh (÷3.6) then divide by efficiency (0.93)
        rdh_elec_mwh = facility_baseline['heat_demand_gj'] / 3.6 / 0.93
        added_elec_mwh = rdh_elec_mwh
        fuel_cost = rdh_elec_mwh * re_price

    else:
        technology = 'Heat_Pump'
        h2_demand_t = 0
        hp_elec_mwh = facility_baseline['heat_demand_gj'] / 3.6 / 4.0
        added_elec_mwh = hp_elec_mwh
        fuel_cost = hp_elec_mwh * re_price

    # Get CAPEX - use exact matching to avoid NCC-H2/NCC-Electricity confusion
    tech_params = data['tech_params']
    tech_row = tech_params[tech_params['technology'] == technology]

    if len(tech_row) > 0:
        tech_row = tech_row.iloc[0]
        years_capex = [2025, 2030, 2040, 2050]
        capex_values = [
            tech_row.get('capex_2025_musd_per_mtco2', 0),
            tech_row.get('capex_2030_musd_per_mtco2', 0),
            tech_row.get('capex_2040_musd_per_mtco2', 0),
            tech_row.get('capex_2050_musd_per_mtco2', 0)
        ]
        capex_per_mtco2 = np.interp(year, years_capex, capex_values)

        abatement_mt = potential_abatement / 1e6
        capex_usd = capex_per_mtco2 * abatement_mt * 1e6
        opex_pct = tech_row.get('opex_pct_capex', 3) / 100
        opex_usd = capex_usd * opex_pct
        lifetime = tech_row.get('lifetime_years', 25)  # Use technology-specific lifetime
    else:
        capex_usd = 0
        opex_usd = 0
        opex_pct = 0.0  # No technology, no OPEX
        lifetime = 25  # Default fallback

    # Total annualized cost
    capex_annual = capex_usd / lifetime
    total_cost = capex_annual + opex_usd + fuel_cost

    # MAC
    mac = total_cost / potential_abatement if potential_abatement > 0 else float('inf')

    return mac, technology, potential_abatement, capex_usd, total_cost, h2_demand_t, added_elec_mwh, opex_pct, lifetime


def determine_installation_schedule(facilities_mac_data, baseline_emissions, target_years):
    """
    Determine when each facility should install technology based on MAC ranking
    and emission reduction targets.

    Returns dict: {facility_id: installation_year}
    """
    # Sort facilities by MAC (lowest first)
    sorted_facilities = sorted(facilities_mac_data, key=lambda x: x['mac'])

    installation_schedule = {}
    cumulative_abatement = 0

    # For each target year, determine which facilities need to be deployed
    for year in sorted(target_years.keys()):
        if year == 2025:
            continue  # No deployment in baseline year

        target_reduction = target_years[year]
        required_abatement = baseline_emissions * target_reduction

        # Deploy facilities until we meet the target
        for fac in sorted_facilities:
            if fac['facility_id'] in installation_schedule:
                continue  # Already scheduled

            if cumulative_abatement >= required_abatement:
                break  # Target met

            # Schedule this facility for installation
            installation_schedule[fac['facility_id']] = year
            cumulative_abatement += fac['potential_abatement']

    # Any remaining facilities get installed in 2050
    for fac in sorted_facilities:
        if fac['facility_id'] not in installation_schedule:
            installation_schedule[fac['facility_id']] = 2050

    return installation_schedule


def run_scenario(scenario, data, years):
    """Run a single scenario with cost-optimized deployment"""
    print(f"\n  Running: {scenario['name']}")

    # Select facilities based on production pathway
    if scenario['production'] == 'shaheen':
        facilities = data['facilities_shaheen'].copy()
        op_rate_df = data['op_rate_shaheen']
    elif scenario['production'] == 'restructure_25pct':
        facilities = data['facilities'].copy()
        op_rate_df = data['op_rate_restructure_25']
    elif scenario['production'] == 'restructure_40pct':
        facilities = data['facilities'].copy()
        op_rate_df = data['op_rate_restructure_40']
    else:
        facilities = data['facilities'].copy()
        op_rate_df = data['op_rate_shaheen']

    intensity_lookup = data['intensity_lookup']

    # Create facility ID (also used as key for intensity lookup)
    facilities['facility_id'] = facilities.apply(
        lambda x: f"{x['company']}_{x['product']}_{x['location']}", axis=1
    )

    # STEP 1: Calculate baseline emissions and MAC for each facility
    print(f"    Calculating facility MACs...")

    # Get 2025 parameters for TRUE baseline (used for emission targets)
    op_row_2025 = op_rate_df[op_rate_df['year'] == 2025]
    operating_rate_2025 = op_row_2025['operating_rate_pct'].iloc[0] / 100 if len(op_row_2025) > 0 else 0.70
    capacity_multiplier_2025 = op_row_2025['cumulative_capacity_multiplier'].iloc[0] if len(op_row_2025) > 0 else 1.0
    grid_ef_2025 = 0.436  # 2025 grid emission factor

    # Use 2035 for MAC calculation (when most deployment happens)
    mac_year = 2035
    op_row = op_rate_df[op_rate_df['year'] == mac_year]
    operating_rate = op_row['operating_rate_pct'].iloc[0] / 100 if len(op_row) > 0 else 0.70
    capacity_multiplier = op_row['cumulative_capacity_multiplier'].iloc[0] if len(op_row) > 0 else 1.0

    grid_row = data['grid_emissions'][data['grid_emissions']['year'] == mac_year]
    grid_ef = grid_row['grid_ef_tco2_per_mwh'].iloc[0] if len(grid_row) > 0 else 0.436

    facilities_mac_data = []
    total_baseline_emissions_2025 = 0  # TRUE 2025 baseline for targets
    skipped_facilities = 0

    for idx, facility in facilities.iterrows():
        # Use key-based matching instead of fragile row-position matching
        facility_key = facility['facility_id']
        if facility_key not in intensity_lookup:
            skipped_facilities += 1
            continue

        intensity = intensity_lookup[facility_key]
        process = facility.get('process', '')

        # Calculate TRUE 2025 baseline for emission targets
        baseline_2025 = calculate_facility_baseline(facility, intensity, operating_rate_2025, grid_ef_2025, capacity_multiplier_2025)
        total_baseline_emissions_2025 += baseline_2025['combustion_emissions']

        # Calculate baseline at MAC year for cost ranking
        baseline = calculate_facility_baseline(facility, intensity, operating_rate, grid_ef, capacity_multiplier)

        # Calculate MAC
        mac, technology, potential_abatement, capex, total_cost, h2_demand, elec_demand, _, _ = \
            calculate_facility_mac(baseline, process, scenario['ncc_tech'], mac_year, data, grid_ef)

        facilities_mac_data.append({
            'facility_id': facility['facility_id'],
            'idx': idx,
            'mac': mac,
            'technology': technology,
            'potential_abatement': potential_abatement,
            'capex': capex,
            'total_cost': total_cost,
            'h2_demand': h2_demand,
            'elec_demand': elec_demand,
        })

    # STEP 2: Determine installation schedule based on emission targets
    print(f"    Determining installation schedule (target-based)...")
    print(f"    2025 baseline combustion emissions: {total_baseline_emissions_2025/1e6:.2f} MtCO2")
    installation_schedule = determine_installation_schedule(
        facilities_mac_data, total_baseline_emissions_2025, EMISSION_TARGETS
    )

    # Print schedule summary
    schedule_summary = {}
    for fac_id, install_year in installation_schedule.items():
        schedule_summary[install_year] = schedule_summary.get(install_year, 0) + 1
    print(f"    Installation schedule: {dict(sorted(schedule_summary.items()))}")

    # STEP 3: Run simulation for each year
    results = []

    for year in years:
        print(f"    Year {year}...")

        # Get operating rate, capacity multiplier, and grid EF for year
        op_row = op_rate_df[op_rate_df['year'] == year]
        operating_rate = op_row['operating_rate_pct'].iloc[0] / 100 if len(op_row) > 0 else 0.70
        capacity_multiplier = op_row['cumulative_capacity_multiplier'].iloc[0] if len(op_row) > 0 else 1.0

        grid_row = data['grid_emissions'][data['grid_emissions']['year'] == year]
        grid_ef = grid_row['grid_ef_tco2_per_mwh'].iloc[0] if len(grid_row) > 0 else 0.436

        # Baseline grid EF (2025) for BAU comparison
        BASELINE_GRID_EF = 0.436

        # Get prices
        h2_price = data['h2_prices'][data['h2_prices']['year'] == year]['h2_price_usd_per_kg'].iloc[0] \
            if year in data['h2_prices']['year'].values else 3.0
        re_price = data['re_prices'][data['re_prices']['year'] == year]['re_price_usd_per_mwh'].iloc[0] \
            if year in data['re_prices']['year'].values else 50.0

        for idx, facility in facilities.iterrows():
            # Use key-based matching instead of fragile row-position matching
            facility_id = facility['facility_id']
            if facility_id not in intensity_lookup:
                continue

            intensity = intensity_lookup[facility_id]
            process = facility.get('process', '')

            # Calculate baseline emissions with capacity multiplier
            baseline = calculate_facility_baseline(facility, intensity, operating_rate, grid_ef, capacity_multiplier)

            # BAU emissions (with 2025 grid EF and capacity multiplier)
            baseline_2025_grid = calculate_facility_baseline(facility, intensity, operating_rate, BASELINE_GRID_EF, capacity_multiplier)
            bau_emissions = baseline_2025_grid['total_emissions']

            # Check if technology is deployed
            install_year = installation_schedule.get(facility_id, 2050)
            tech_deployed = 1 if year >= install_year else 0

            # Find MAC data for this facility
            fac_mac = next((f for f in facilities_mac_data if f['facility_id'] == facility_id), None)

            if tech_deployed and fac_mac and fac_mac['mac'] < float('inf'):
                # Technology is deployed
                technology = fac_mac['technology']

                # Recalculate with current year prices
                mac, _, potential_abatement, capex, total_cost, h2_demand, added_elec, opex_pct, lifetime = \
                    calculate_facility_mac(baseline, process, scenario['ncc_tech'], year, data, grid_ef)

                # Emissions after technology (only electricity remains, combustion eliminated)
                emissions = baseline['elec_emissions'] + added_elec * grid_ef
                abatement = bau_emissions - emissions

                # Calculate cost components using technology-specific parameters
                opex_usd_yr = capex * opex_pct
                capex_annual = capex / lifetime
                fuel_cost_usd_yr = total_cost - capex_annual - opex_usd_yr

                result = {
                    'technology': technology,
                    'emissions_tco2': max(0, emissions),
                    'abatement_tco2': max(0, abatement),
                    'capex_usd': capex,
                    'total_cost_usd': total_cost,
                    'mac_usd_per_tco2': mac if mac < float('inf') else 0,
                    'elec_demand_mwh': baseline['elec_demand_mwh'] + added_elec,
                    'h2_demand_t': h2_demand,
                    'tech_deployed': 1,
                    'install_year': install_year,
                    'opex_usd_yr': opex_usd_yr,
                    'fuel_cost_usd_yr': max(0, fuel_cost_usd_yr),
                }
            else:
                # No technology deployed yet
                result = {
                    'technology': 'Baseline',  # Use 'Baseline' instead of 'None' to avoid pandas NaN interpretation
                    'emissions_tco2': baseline['total_emissions'],
                    'abatement_tco2': max(0, bau_emissions - baseline['total_emissions']),  # Grid improvement only
                    'capex_usd': 0,
                    'total_cost_usd': 0,
                    'mac_usd_per_tco2': 0,
                    'elec_demand_mwh': baseline['elec_demand_mwh'],
                    'h2_demand_t': 0,
                    'tech_deployed': 0,
                    'install_year': install_year,
                    'opex_usd_yr': 0,
                    'fuel_cost_usd_yr': 0,
                }

            # Add common fields
            result.update({
                'year': year,
                'scenario': scenario['name'],
                'region': get_region(facility.get('location', '')),
                'facility_id': facility_id,
                'company': facility.get('company', ''),
                'product': facility.get('product', ''),
                'process': process,
                'capacity_tpy': baseline['capacity_tpy'],
                'production_t': baseline['production_t'],
                'bau_emissions_tco2': bau_emissions,
                'heat_demand_gj': baseline['heat_demand_gj'],
            })

            results.append(result)

    return results


def main():
    """Main execution"""
    print("=" * 80)
    print("KOREA PETROCHEMICAL NET ZERO - COST-OPTIMIZED SCENARIO RUNNER")
    print("=" * 80)
    print(f"\nYears: {YEARS[0]} - {YEARS[-1]} (annual, {len(YEARS)} years)")
    print("\nKey Emission Targets:")
    for year, target in KEY_TARGETS.items():
        print(f"  {year}: {target*100:.1f}% reduction")

    # Load data
    data = load_data()

    # Run all scenarios
    print("\n" + "=" * 80)
    print("RUNNING SCENARIOS")
    print("=" * 80)

    all_results = []
    scenario_dfs = {}  # Store individual scenario DataFrames

    for scenario in SCENARIOS:
        results = run_scenario(scenario, data, YEARS)
        all_results.extend(results)

        # Create DataFrame for this scenario
        df_scenario = pd.DataFrame(results)
        scenario_dfs[scenario['name']] = df_scenario

    # Convert combined results to DataFrame
    df_results = pd.DataFrame(all_results)

    # Reorder columns
    column_order = [
        'year', 'scenario', 'region', 'facility_id', 'company', 'product', 'process',
        'technology', 'capacity_tpy', 'production_t',
        'bau_emissions_tco2', 'emissions_tco2', 'abatement_tco2',
        'capex_usd', 'opex_usd_yr', 'fuel_cost_usd_yr', 'total_cost_usd', 'mac_usd_per_tco2',
        'elec_demand_mwh', 'h2_demand_t', 'heat_demand_gj',
        'tech_deployed', 'install_year'
    ]

    # Only include columns that exist
    column_order = [c for c in column_order if c in df_results.columns]
    df_results = df_results[column_order]

    # ==================== SAVE OUTPUTS ====================
    print("\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)

    # 1. Save combined results
    output_path = OUTPUT_DIR / 'scenario_results.csv'
    df_results.to_csv(output_path, index=False)
    print(f"  ✓ Combined results: {output_path}")

    # 2. Save separate files for each scenario
    for scenario_name, df_scenario in scenario_dfs.items():
        df_scenario = df_scenario[column_order]
        scenario_path = OUTPUT_DIR / f'{scenario_name}.csv'
        df_scenario.to_csv(scenario_path, index=False)
        print(f"  ✓ Scenario file: {scenario_path}")

    # 3. Generate and save Regional MAC Summary
    regional_mac_data = []
    for scenario_name in df_results['scenario'].unique():
        df_s = df_results[df_results['scenario'] == scenario_name]
        for year in YEARS:
            df_y = df_s[df_s['year'] == year]
            for region in df_y['region'].unique():
                df_r = df_y[df_y['region'] == region]
                total_abatement = df_r['abatement_tco2'].sum()
                total_cost = df_r['total_cost_usd'].sum()
                mac = total_cost / total_abatement if total_abatement > 0 else 0
                regional_mac_data.append({
                    'scenario': scenario_name,
                    'year': year,
                    'region': region,
                    'abatement_tco2': total_abatement,
                    'total_cost_usd': total_cost,
                    'mac_usd_per_tco2': mac,
                    'facilities_deployed': df_r[df_r['tech_deployed'] == 1]['facility_id'].nunique(),
                    'total_facilities': df_r['facility_id'].nunique(),
                })

    df_regional_mac = pd.DataFrame(regional_mac_data)
    mac_path = OUTPUT_DIR / 'regional_mac_summary.csv'
    df_regional_mac.to_csv(mac_path, index=False)
    print(f"  ✓ Regional MAC summary: {mac_path}")

    # 4. Generate and save Regional Abatement Summary
    regional_abatement_data = []
    for scenario_name in df_results['scenario'].unique():
        df_s = df_results[df_results['scenario'] == scenario_name]
        baseline_2025 = df_s[df_s['year'] == 2025]['bau_emissions_tco2'].sum()

        for year in YEARS:
            df_y = df_s[df_s['year'] == year]
            for region in df_y['region'].unique():
                df_r = df_y[df_y['region'] == region]
                regional_abatement_data.append({
                    'scenario': scenario_name,
                    'year': year,
                    'region': region,
                    'bau_emissions_tco2': df_r['bau_emissions_tco2'].sum(),
                    'emissions_tco2': df_r['emissions_tco2'].sum(),
                    'abatement_tco2': df_r['abatement_tco2'].sum(),
                    'abatement_mt': df_r['abatement_tco2'].sum() / 1e6,
                    'capex_usd': df_r['capex_usd'].sum(),
                    'elec_demand_mwh': df_r['elec_demand_mwh'].sum(),
                    'h2_demand_t': df_r['h2_demand_t'].sum(),
                })

    df_regional_abatement = pd.DataFrame(regional_abatement_data)
    abatement_path = OUTPUT_DIR / 'regional_abatement_summary.csv'
    df_regional_abatement.to_csv(abatement_path, index=False)
    print(f"  ✓ Regional abatement summary: {abatement_path}")

    # ==================== OUTPUT SUMMARY ====================
    print("\n" + "=" * 80)
    print("OUTPUT SUMMARY")
    print("=" * 80)
    print(f"  Total rows: {len(df_results):,}")
    print(f"  Scenarios: {df_results['scenario'].nunique()}")
    print(f"  Years: {YEARS[0]} - {YEARS[-1]} ({len(YEARS)} annual)")
    print(f"  Facilities: {df_results['facility_id'].nunique()}")
    print(f"  Regions: {df_results['region'].unique().tolist()}")

    # ==================== VALIDATION ====================
    print("\n" + "=" * 80)
    print("VALIDATION - EMISSION TARGETS (Key Years)")
    print("=" * 80)

    validation_years = [2025, 2030, 2035, 2040, 2045, 2050]
    for scenario_name in df_results['scenario'].unique():
        print(f"\n  {scenario_name}:")
        df_s = df_results[df_results['scenario'] == scenario_name]

        baseline_2025 = df_s[df_s['year'] == 2025]['bau_emissions_tco2'].sum() / 1e6

        for year in validation_years:
            df_y = df_s[df_s['year'] == year]
            emissions = df_y['emissions_tco2'].sum() / 1e6
            reduction = (1 - emissions / baseline_2025) * 100 if baseline_2025 > 0 else 0
            target = EMISSION_TARGETS.get(year, 0) * 100
            deployed = df_y[df_y['tech_deployed'] == 1]['facility_id'].nunique()

            status = "✓" if reduction >= target - 1 else "✗"
            print(f"    {year}: {emissions:.2f} Mt ({reduction:.1f}% red, target {target:.1f}%) "
                  f"[{deployed} deployed] {status}")

    print("\n" + "=" * 80)
    print("DONE - All outputs saved to outputs/")
    print("=" * 80)

    return df_results


if __name__ == '__main__':
    df = main()
