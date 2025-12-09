"""
SCENARIO RUNNER - Generates Long-Format Output
==============================================
Runs all 6 scenarios and outputs a single CSV file with facility-level results.

Output: outputs/scenario_results.csv

Methodology:
- Emissions are calculated by fuel source (naphtha, LNG, fuel_gas, byproduct_gas, electricity)
- Technologies target specific emission sources:
  * NCC-H2/Electricity: Naphtha combustion in crackers (100% by 2050)
  * Heat_Pump: LNG/Fuel_Gas/Byproduct_Gas for heat (gradual ramp to 100% by 2050)
  * RE_PPA: Electricity emissions (covered by grid decarbonization - 0 by 2050)
  * RDH: High-temp BTX processes (100% by 2050)

Technology deployment timeline:
- 2025: Baseline only (no technology)
- 2030: 30% deployment
- 2035: 50% deployment
- 2040: 70% deployment
- 2045: 85% deployment
- 2050: 100% deployment (Net Zero)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from modules.utils import DataLoader, EmissionCalculator, PriceCalculator, TechnologyCostCalculator

# Configuration
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Years for analysis (key years only)
YEARS = [2025, 2030, 2035, 2040, 2045, 2050]

# Technology deployment schedule (fraction of eligible facilities converted)
DEPLOYMENT_SCHEDULE = {
    2025: 0.00,  # Baseline year
    2030: 0.30,
    2035: 0.50,
    2040: 0.70,
    2045: 0.85,
    2050: 1.00   # Net Zero target
}

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

    print(f"  Loaded {len(data['facilities'])} baseline facilities")
    print(f"  Loaded {len(data['facilities_shaheen'])} facilities with Shaheen")
    print(f"  Loaded {len(data['tech_params'])} technologies")

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


def calculate_facility_emissions_by_source(facility, intensity, emission_calc, operating_rate):
    """
    Calculate emissions by source for a facility.
    Returns detailed breakdown for technology targeting.
    """
    capacity_tonnes = facility['capacity_kt'] * 1000
    production_tonnes = capacity_tonnes * operating_rate

    # Calculate emissions by fuel type
    emissions_by_source = {}

    # Naphtha (cracker furnace combustion)
    naphtha_gj = intensity.get('Naphtha_GJ_per_tonne', 0) * production_tonnes
    emissions_by_source['naphtha'] = naphtha_gj * 0.0542  # tCO2/GJ

    # Electricity
    elec_kwh = intensity.get('Electricity_kWh_per_tonne', 0) * production_tonnes
    emissions_by_source['electricity_kwh'] = elec_kwh  # Store kWh for grid EF calc

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

    return {
        'capacity_tpy': capacity_tonnes,
        'production_t': production_tonnes,
        'emissions_by_source': emissions_by_source,
        'elec_demand_mwh': elec_kwh / 1000,
        'heat_demand_gj': total_heat_gj,
    }


def calculate_abatement_and_costs(facility_data, process, ncc_tech, year, data, grid_ef):
    """
    Calculate emissions abatement for a facility based on technology deployment.

    Technology application logic:
    - NCC facilities: NCC-H2 or NCC-Electricity for naphtha combustion
                     + Heat Pump for LNG/Fuel_Gas/Byproduct_Gas
    - BTX facilities: RDH for high-temp heat
                     + Heat Pump for remaining fuel gas
    - Other facilities: Heat Pump for all combustion emissions

    All facilities: RE_PPA for electricity (grid EF covers this automatically)

    BAU (Business as Usual) = what emissions would be with 2025 grid EF (no decarbonization)
    Emissions = actual emissions after technology deployment + grid decarbonization
    Abatement = BAU - Emissions (includes both tech deployment and grid improvement)
    """
    emissions = facility_data['emissions_by_source']
    deployment = DEPLOYMENT_SCHEDULE.get(year, 0)

    # Baseline grid EF (2025)
    BASELINE_GRID_EF = 0.436  # tCO2/MWh

    # Calculate BAU emissions (using 2025 baseline grid EF for comparison)
    elec_kwh = emissions['electricity_kwh']
    elec_mwh = elec_kwh / 1000
    bau_elec_emissions = elec_mwh * BASELINE_GRID_EF  # What elec emissions would be at 2025 levels

    combustion_emissions = (
        emissions.get('naphtha', 0) +
        emissions.get('lng', 0) +
        emissions.get('fuel_gas', 0) +
        emissions.get('byproduct_gas', 0)
    )
    bau_emissions = combustion_emissions + bau_elec_emissions

    # Initialize result
    result = {
        'capacity_tpy': facility_data['capacity_tpy'],
        'production_t': facility_data['production_t'],
        'bau_emissions_tco2': bau_emissions,
        'elec_demand_mwh': facility_data['elec_demand_mwh'],
        'heat_demand_gj': facility_data['heat_demand_gj'],
        'h2_demand_t': 0,
        'capex_usd': 0,
        'opex_usd_yr': 0,
        'fuel_cost_usd_yr': 0,
    }

    # Track abatement by source
    abated_naphtha = 0
    abated_lng_fg_bg = 0  # LNG + Fuel_Gas + Byproduct_Gas
    abated_electricity = 0

    # Get prices
    h2_price = data['h2_prices'][data['h2_prices']['year'] == year]['h2_price_usd_per_kg'].iloc[0] \
        if year in data['h2_prices']['year'].values else 3.0
    re_price = data['re_prices'][data['re_prices']['year'] == year]['re_price_usd_per_mwh'].iloc[0] \
        if year in data['re_prices']['year'].values else 50.0

    # Determine technology and calculate abatement
    if is_ncc_facility(process):
        # NCC facility: Use NCC technology for naphtha, Heat Pump for other fuels
        result['technology'] = ncc_tech

        # NCC technology abates naphtha combustion
        naphtha_emissions = emissions.get('naphtha', 0)
        abated_naphtha = naphtha_emissions * deployment

        # Calculate H2 or electricity demand for NCC
        if ncc_tech == 'NCC-H2':
            # H2 demand: 0.2 t-H2 per t-ethylene, roughly 0.12 t-H2 per tCO2 abated
            result['h2_demand_t'] = abated_naphtha * 0.12  # Rough estimate
            result['fuel_cost_usd_yr'] = result['h2_demand_t'] * h2_price * 1000
        else:  # NCC-Electricity
            # ~2.5 MWh per tCO2 abated for electric cracker
            added_elec_mwh = abated_naphtha * 2.5
            result['elec_demand_mwh'] += added_elec_mwh
            result['fuel_cost_usd_yr'] = added_elec_mwh * re_price

        # Heat Pump for other fuel combustion (LNG, Fuel_Gas, Byproduct_Gas)
        other_fuel_emissions = emissions.get('lng', 0) + emissions.get('fuel_gas', 0) + emissions.get('byproduct_gas', 0)
        abated_lng_fg_bg = other_fuel_emissions * deployment

        # Heat pump electricity demand (COP = 4)
        heat_pump_elec_mwh = (facility_data['heat_demand_gj'] - emissions.get('naphtha', 0) / 0.0542) * deployment / 3.6 / 4.0
        heat_pump_elec_mwh = max(0, heat_pump_elec_mwh)
        result['elec_demand_mwh'] += heat_pump_elec_mwh

    elif is_btx_facility(process):
        # BTX facility: RDH for high-temp, Heat Pump for low-temp
        result['technology'] = 'RDH'

        # RDH covers all fuel combustion in BTX
        total_combustion = combustion_emissions
        abated_naphtha = emissions.get('naphtha', 0) * deployment
        abated_lng_fg_bg = (emissions.get('lng', 0) + emissions.get('fuel_gas', 0) + emissions.get('byproduct_gas', 0)) * deployment

        # RDH electricity demand
        rdh_elec_mwh = facility_data['heat_demand_gj'] * deployment / 3.6 * 0.9  # 90% efficiency
        result['elec_demand_mwh'] += rdh_elec_mwh
        result['fuel_cost_usd_yr'] = rdh_elec_mwh * re_price

    else:
        # Other facilities: Heat Pump for all combustion
        result['technology'] = 'Heat_Pump'

        # Heat Pump covers all fuel combustion
        abated_naphtha = emissions.get('naphtha', 0) * deployment
        abated_lng_fg_bg = (emissions.get('lng', 0) + emissions.get('fuel_gas', 0) + emissions.get('byproduct_gas', 0)) * deployment

        # Heat pump electricity (COP = 4)
        hp_elec_mwh = facility_data['heat_demand_gj'] * deployment / 3.6 / 4.0
        result['elec_demand_mwh'] += hp_elec_mwh
        result['fuel_cost_usd_yr'] = hp_elec_mwh * re_price

    # Calculate actual electricity emissions (with current year's grid EF)
    # Baseline electricity uses grid power with current grid_ef
    baseline_elec_emissions = elec_mwh * grid_ef

    # Additional electricity from technology deployment (also uses grid power)
    added_elec_mwh = result['elec_demand_mwh'] - facility_data['elec_demand_mwh']
    added_elec_emissions = added_elec_mwh * grid_ef

    # Total electricity emissions for this year
    total_elec_emissions = baseline_elec_emissions + added_elec_emissions

    # Residual combustion emissions (portion not yet converted by technology)
    residual_combustion = combustion_emissions - abated_naphtha - abated_lng_fg_bg

    # Total actual emissions
    residual_emissions = max(0, residual_combustion + total_elec_emissions)

    result['emissions_tco2'] = residual_emissions
    result['abatement_tco2'] = bau_emissions - residual_emissions
    result['tech_deployed'] = 1 if deployment > 0 else 0

    # CAPEX calculation
    tech_params = data['tech_params']
    tech_name = result['technology'].replace('-', '_')
    tech_row = tech_params[tech_params['technology'].str.contains(tech_name.split('_')[0], case=False)]

    if len(tech_row) > 0:
        tech_row = tech_row.iloc[0]

        # Interpolate CAPEX
        years = [2025, 2030, 2040, 2050]
        capex_values = [
            tech_row.get('capex_2025_musd_per_mtco2', 0),
            tech_row.get('capex_2030_musd_per_mtco2', 0),
            tech_row.get('capex_2040_musd_per_mtco2', 0),
            tech_row.get('capex_2050_musd_per_mtco2', 0)
        ]
        capex_per_mtco2 = np.interp(year, years, capex_values)

        # CAPEX based on abatement
        abatement_mt = result['abatement_tco2'] / 1e6
        result['capex_usd'] = capex_per_mtco2 * abatement_mt * 1e6

        # OPEX
        opex_pct = tech_row.get('opex_pct_capex', 3) / 100
        result['opex_usd_yr'] = result['capex_usd'] * opex_pct

    # Total cost
    lifetime = 25
    capex_annual = result['capex_usd'] / lifetime
    result['total_cost_usd'] = capex_annual + result['opex_usd_yr'] + result.get('fuel_cost_usd_yr', 0)

    # MAC
    if result['abatement_tco2'] > 0:
        result['mac_usd_per_tco2'] = result['total_cost_usd'] / result['abatement_tco2']
    else:
        result['mac_usd_per_tco2'] = 0

    return result


def run_scenario(scenario, data, years):
    """Run a single scenario and return facility-level results"""
    print(f"\n  Running: {scenario['name']}")

    results = []

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

    # Get energy intensities (aligned with facilities)
    intensities = data['intensities']

    # Create emission calculator
    emission_calc = EmissionCalculator(data['emission_factors'])

    # Create facility ID
    facilities['facility_id'] = facilities.apply(
        lambda x: f"{x['company']}_{x['product']}_{x['location']}", axis=1
    )

    for year in years:
        print(f"    Year {year}...")

        # Get operating rate for year
        op_row = op_rate_df[op_rate_df['year'] == year]
        if len(op_row) > 0 and 'operating_rate_pct' in op_row.columns:
            operating_rate = op_row['operating_rate_pct'].iloc[0] / 100
        else:
            operating_rate = 0.70  # Default 70%

        # Get grid emission factor
        grid_row = data['grid_emissions'][data['grid_emissions']['year'] == year]
        grid_ef = grid_row['grid_ef_tco2_per_mwh'].iloc[0] if len(grid_row) > 0 else 0.436

        for idx, facility in facilities.iterrows():
            # Get matching intensity row
            if idx < len(intensities):
                intensity = intensities.iloc[idx]
            else:
                continue

            # Calculate emissions by source
            facility_data = calculate_facility_emissions_by_source(
                facility, intensity, emission_calc, operating_rate
            )

            # Get process type
            process = facility.get('process', '')

            # Calculate abatement and costs
            result = calculate_abatement_and_costs(
                facility_data, process, scenario['ncc_tech'], year, data, grid_ef
            )

            # Add identifiers
            result['year'] = year
            result['scenario'] = scenario['name']
            result['region'] = get_region(facility.get('location', ''))
            result['facility_id'] = facility['facility_id']
            result['company'] = facility.get('company', '')
            result['product'] = facility.get('product', '')
            result['process'] = facility.get('process', '')

            results.append(result)

    return results


def main():
    """Main execution"""
    print("=" * 80)
    print("KOREA PETROCHEMICAL NET ZERO SCENARIO RUNNER")
    print("=" * 80)

    # Load data
    data = load_data()

    # Run all scenarios
    print("\n" + "=" * 80)
    print("RUNNING SCENARIOS")
    print("=" * 80)

    all_results = []

    for scenario in SCENARIOS:
        results = run_scenario(scenario, data, YEARS)
        all_results.extend(results)

    # Convert to DataFrame
    df_results = pd.DataFrame(all_results)

    # Reorder columns
    column_order = [
        'year', 'scenario', 'region', 'facility_id', 'company', 'product', 'process',
        'technology', 'capacity_tpy', 'production_t',
        'bau_emissions_tco2', 'emissions_tco2', 'abatement_tco2',
        'capex_usd', 'opex_usd_yr', 'fuel_cost_usd_yr', 'total_cost_usd', 'mac_usd_per_tco2',
        'elec_demand_mwh', 'h2_demand_t', 'heat_demand_gj',
        'tech_deployed'
    ]

    # Only include columns that exist
    column_order = [c for c in column_order if c in df_results.columns]
    df_results = df_results[column_order]

    # Save output
    output_path = OUTPUT_DIR / 'scenario_results.csv'
    df_results.to_csv(output_path, index=False)

    print("\n" + "=" * 80)
    print("OUTPUT SUMMARY")
    print("=" * 80)
    print(f"  Total rows: {len(df_results):,}")
    print(f"  Scenarios: {df_results['scenario'].nunique()}")
    print(f"  Years: {sorted(df_results['year'].unique())}")
    print(f"  Facilities: {df_results['facility_id'].nunique()}")
    print(f"  Regions: {df_results['region'].unique().tolist()}")
    print(f"\n  Output saved to: {output_path}")

    # Quick validation
    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    # 2025 baseline check
    baseline_2025 = df_results[(df_results['year'] == 2025) & (df_results['scenario'] == 'shaheen_ncc_h2')]
    total_bau = baseline_2025['bau_emissions_tco2'].sum() / 1e6
    print(f"  2025 BAU emissions (shaheen): {total_bau:.2f} MtCO2")

    # 2050 net zero check
    for scenario in df_results['scenario'].unique():
        net_2050 = df_results[(df_results['year'] == 2050) & (df_results['scenario'] == scenario)]['emissions_tco2'].sum() / 1e6
        print(f"  2050 emissions ({scenario}): {net_2050:.2f} MtCO2")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)

    return df_results


if __name__ == '__main__':
    df = main()
