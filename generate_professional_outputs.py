"""
Generate Professional CSV Outputs for Korea Petrochemical MACC Model
====================================================================

Creates structured CSV files for external stakeholders:
1. Executive Summary - Key metrics by scenario
2. Emission Pathways - Annual emissions by various dimensions
3. Investment Summary - CAPEX and cost breakdowns
4. Technology Roadmap - Technology deployment timeline
5. Stranded Assets - NCC stranding analysis
6. Facility Details - Complete facility-level data

Outputs:
- outputs/professional/*.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

# Configuration
OUTPUT_DIR = Path('outputs')
PROFESSIONAL_DIR = OUTPUT_DIR / 'professional'
DATA_DIR = Path('data')

PROFESSIONAL_DIR.mkdir(parents=True, exist_ok=True)

SCENARIO_NAMES = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_elec': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_elec': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_elec': 'Restructure 40% + NCC-Elec',
}


def load_data():
    """Load all required data"""
    results = pd.read_csv(OUTPUT_DIR / 'scenario_results.csv')
    stranded_params = pd.read_csv(DATA_DIR / 'assumptions' / 'stranded_asset_params.csv')
    facility_db = pd.read_csv(DATA_DIR / 'assets' / 'facility_database_with_shaheen.csv')
    return results, stranded_params, facility_db


def generate_executive_summary(df):
    """
    Generate executive summary with key metrics per scenario
    """
    print("  Generating executive summary...")

    summaries = []
    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario]

        # Baseline (2025)
        baseline_2025 = scenario_df[scenario_df['year'] == 2025]
        baseline_emissions = baseline_2025['bau_emissions_tco2'].sum()

        # Final (2050)
        final_2050 = scenario_df[scenario_df['year'] == 2050]
        final_emissions = final_2050['emissions_tco2'].sum()

        # Cumulative metrics (sum over all years)
        total_abatement = scenario_df['abatement_tco2'].sum()
        total_capex = scenario_df[scenario_df['tech_deployed'] == 1]['capex_usd'].sum()

        # Technology deployment counts
        deployed = scenario_df[scenario_df['tech_deployed'] == 1]
        tech_counts = deployed.groupby('technology')['facility_id'].nunique()

        # Energy demands (2050)
        elec_demand_2050 = final_2050['elec_demand_mwh'].sum()
        h2_demand_2050 = final_2050['h2_demand_t'].sum()

        summaries.append({
            'scenario': scenario,
            'scenario_name': SCENARIO_NAMES.get(scenario, scenario),
            'baseline_emissions_mtco2': baseline_emissions / 1e6,
            'final_emissions_2050_mtco2': final_emissions / 1e6,
            'reduction_pct': (1 - final_emissions / baseline_emissions) * 100 if baseline_emissions > 0 else 0,
            'total_abatement_mtco2': total_abatement / 1e6,
            'total_capex_billion_usd': total_capex / 1e9,
            'ncc_h2_facilities': tech_counts.get('NCC-H2', 0),
            'ncc_elec_facilities': tech_counts.get('NCC-Electricity', 0),
            'rdh_facilities': tech_counts.get('RDH', 0),
            'heat_pump_facilities': tech_counts.get('Heat_Pump', 0),
            'electricity_demand_2050_twh': elec_demand_2050 / 1e6,
            'hydrogen_demand_2050_kt': h2_demand_2050 / 1e3,
        })

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(PROFESSIONAL_DIR / 'executive_summary.csv', index=False)
    return summary_df


def generate_annual_emissions_summary(df):
    """
    Generate annual emissions summary by scenario
    """
    print("  Generating annual emissions summary...")

    annual = df.groupby(['year', 'scenario']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': lambda x: x[df.loc[x.index, 'tech_deployed'] == 1].sum(),
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum',
    }).reset_index()

    # Add derived columns
    annual['scenario_name'] = annual['scenario'].map(SCENARIO_NAMES)
    annual['bau_emissions_mtco2'] = annual['bau_emissions_tco2'] / 1e6
    annual['emissions_mtco2'] = annual['emissions_tco2'] / 1e6
    annual['abatement_mtco2'] = annual['abatement_tco2'] / 1e6
    annual['capex_million_usd'] = annual['capex_usd'] / 1e6
    annual['electricity_twh'] = annual['elec_demand_mwh'] / 1e6
    annual['hydrogen_kt'] = annual['h2_demand_t'] / 1e3

    # Select output columns
    output_cols = ['year', 'scenario', 'scenario_name', 'bau_emissions_mtco2',
                   'emissions_mtco2', 'abatement_mtco2', 'capex_million_usd',
                   'electricity_twh', 'hydrogen_kt']
    annual[output_cols].to_csv(PROFESSIONAL_DIR / 'annual_emissions_summary.csv', index=False)
    return annual


def generate_regional_breakdown(df):
    """
    Generate regional breakdown by scenario and year
    """
    print("  Generating regional breakdown...")

    # Simplify region names
    df_copy = df.copy()
    df_copy['region_name'] = df_copy['region'].apply(
        lambda x: 'Yeosu Complex' if 'Yeosu' in str(x) else (
            'Daesan Complex' if 'Daesan' in str(x) else (
                'Ulsan Complex' if 'Ulsan' in str(x) else 'Other Regions'
            )
        )
    )

    regional = df_copy.groupby(['year', 'scenario', 'region_name']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': lambda x: x[df_copy.loc[x.index, 'tech_deployed'] == 1].sum(),
        'facility_id': 'count',
    }).reset_index()

    regional['scenario_name'] = regional['scenario'].map(SCENARIO_NAMES)
    regional['bau_emissions_mtco2'] = regional['bau_emissions_tco2'] / 1e6
    regional['emissions_mtco2'] = regional['emissions_tco2'] / 1e6
    regional['abatement_mtco2'] = regional['abatement_tco2'] / 1e6
    regional['capex_million_usd'] = regional['capex_usd'] / 1e6
    regional.rename(columns={'facility_id': 'facility_count'}, inplace=True)

    output_cols = ['year', 'scenario', 'scenario_name', 'region_name',
                   'bau_emissions_mtco2', 'emissions_mtco2', 'abatement_mtco2',
                   'capex_million_usd', 'facility_count']
    regional[output_cols].to_csv(PROFESSIONAL_DIR / 'regional_breakdown.csv', index=False)
    return regional


def generate_company_breakdown(df):
    """
    Generate company breakdown by scenario and year
    """
    print("  Generating company breakdown...")

    company = df.groupby(['year', 'scenario', 'company']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': lambda x: x[df.loc[x.index, 'tech_deployed'] == 1].sum(),
        'facility_id': 'count',
        'capacity_tpy': 'sum',
    }).reset_index()

    company['scenario_name'] = company['scenario'].map(SCENARIO_NAMES)
    company['bau_emissions_mtco2'] = company['bau_emissions_tco2'] / 1e6
    company['emissions_mtco2'] = company['emissions_tco2'] / 1e6
    company['abatement_mtco2'] = company['abatement_tco2'] / 1e6
    company['capex_million_usd'] = company['capex_usd'] / 1e6
    company['capacity_mtpy'] = company['capacity_tpy'] / 1e6
    company.rename(columns={'facility_id': 'facility_count'}, inplace=True)

    output_cols = ['year', 'scenario', 'scenario_name', 'company',
                   'bau_emissions_mtco2', 'emissions_mtco2', 'abatement_mtco2',
                   'capex_million_usd', 'facility_count', 'capacity_mtpy']
    company[output_cols].to_csv(PROFESSIONAL_DIR / 'company_breakdown.csv', index=False)
    return company


def generate_technology_deployment(df):
    """
    Generate technology deployment timeline
    """
    print("  Generating technology deployment timeline...")

    deployed = df[df['tech_deployed'] == 1].copy()

    tech_timeline = deployed.groupby(['year', 'scenario', 'technology']).agg({
        'facility_id': 'count',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'capacity_tpy': 'sum',
    }).reset_index()

    tech_timeline['scenario_name'] = tech_timeline['scenario'].map(SCENARIO_NAMES)
    tech_timeline['abatement_mtco2'] = tech_timeline['abatement_tco2'] / 1e6
    tech_timeline['capex_million_usd'] = tech_timeline['capex_usd'] / 1e6
    tech_timeline['capacity_mtpy'] = tech_timeline['capacity_tpy'] / 1e6
    tech_timeline.rename(columns={'facility_id': 'facilities_deployed'}, inplace=True)

    output_cols = ['year', 'scenario', 'scenario_name', 'technology',
                   'facilities_deployed', 'abatement_mtco2', 'capex_million_usd', 'capacity_mtpy']
    tech_timeline[output_cols].to_csv(PROFESSIONAL_DIR / 'technology_deployment.csv', index=False)
    return tech_timeline


def generate_stranded_asset_analysis(df, stranded_params, facility_db):
    """
    Generate stranded asset analysis for NCC facilities

    Args:
        df: Scenario results DataFrame
        stranded_params: Stranded asset parameters from CSV
        facility_db: Facility database with year_built information
    """
    print("  Generating stranded asset analysis...")

    # Get NCC facilities that transition (technology != Baseline at some point)
    ncc_facilities = df[df['process'] == 'Naphtha Cracker'].copy()

    # Create a lookup for year_built from facility database
    # facility_id format is typically "company_product_location_N"
    # We need to match by company, product, and location/complex
    year_built_lookup = {}
    for _, fac_row in facility_db.iterrows():
        key = (fac_row['company'], fac_row['product'], fac_row.get('location', ''))
        if key not in year_built_lookup and pd.notna(fac_row.get('year_built')):
            year_built_lookup[key] = int(fac_row['year_built'])

    # Find first year where technology changes from Baseline
    stranded_list = []

    for scenario in ncc_facilities['scenario'].unique():
        scenario_df = ncc_facilities[ncc_facilities['scenario'] == scenario]

        for facility_id in scenario_df['facility_id'].unique():
            fac_df = scenario_df[scenario_df['facility_id'] == facility_id].sort_values('year')

            # Find transition year (first year where tech_deployed = 1 and technology != Baseline)
            deployed = fac_df[(fac_df['tech_deployed'] == 1) & (fac_df['technology'] != 'Baseline')]

            if len(deployed) > 0:
                transition_year = deployed['year'].min()

                # Get facility details from 2025 baseline
                baseline_row = fac_df[fac_df['year'] == 2025].iloc[0] if len(fac_df[fac_df['year'] == 2025]) > 0 else fac_df.iloc[0]

                # Get stranded asset parameters from CSV (required - no fallbacks)
                params = stranded_params[stranded_params['process'] == 'Naphtha Cracker']
                if len(params) == 0:
                    raise ValueError("Naphtha Cracker parameters not found in stranded_asset_params.csv")
                overnight_capex = params['overnight_capex_usd_per_ton'].iloc[0]
                useful_life = params['useful_life_years'].iloc[0]
                abandonment_cost = params['abandonment_cost_usd_per_ton'].iloc[0]

                capacity_t = baseline_row['capacity_tpy']

                # Get install_year from facility database, or estimate from age_2025 if available
                company = baseline_row['company']
                product = baseline_row['product']
                location = baseline_row.get('region', '').split()[0] if pd.notna(baseline_row.get('region')) else ''

                # Try to find year_built in lookup
                install_year = year_built_lookup.get((company, product, location))

                # If not found, try to estimate from age_2025 if available in df
                if install_year is None and 'age_2025' in baseline_row and pd.notna(baseline_row['age_2025']):
                    install_year = 2025 - int(baseline_row['age_2025'])

                # Last resort: use average age estimation (20 years old in 2025)
                if install_year is None:
                    install_year = 2005
                remaining_life = max(0, install_year + useful_life - transition_year)
                book_value = capacity_t * overnight_capex * (remaining_life / useful_life)
                abandonment_total = capacity_t * abandonment_cost
                stranded_value = book_value + abandonment_total

                stranded_list.append({
                    'scenario': scenario,
                    'scenario_name': SCENARIO_NAMES.get(scenario, scenario),
                    'facility_id': facility_id,
                    'company': baseline_row['company'],
                    'region': baseline_row['region'],
                    'product': baseline_row['product'],
                    'capacity_tpy': capacity_t,
                    'transition_year': transition_year,
                    'new_technology': deployed['technology'].iloc[0],
                    'assumed_install_year': install_year,
                    'remaining_life_years': remaining_life,
                    'book_value_usd': book_value,
                    'abandonment_cost_usd': abandonment_total,
                    'total_stranded_value_usd': stranded_value,
                })

    if stranded_list:
        stranded_df = pd.DataFrame(stranded_list)

        # Convert to millions
        stranded_df['book_value_million_usd'] = stranded_df['book_value_usd'] / 1e6
        stranded_df['abandonment_cost_million_usd'] = stranded_df['abandonment_cost_usd'] / 1e6
        stranded_df['total_stranded_value_million_usd'] = stranded_df['total_stranded_value_usd'] / 1e6
        stranded_df['capacity_ktpy'] = stranded_df['capacity_tpy'] / 1e3

        output_cols = ['scenario', 'scenario_name', 'facility_id', 'company', 'region', 'product',
                       'capacity_ktpy', 'transition_year', 'new_technology', 'assumed_install_year',
                       'remaining_life_years', 'book_value_million_usd', 'abandonment_cost_million_usd',
                       'total_stranded_value_million_usd']
        stranded_df[output_cols].to_csv(PROFESSIONAL_DIR / 'stranded_assets_ncc.csv', index=False)

        # Summary by scenario
        summary = stranded_df.groupby(['scenario', 'scenario_name']).agg({
            'facility_id': 'count',
            'capacity_tpy': 'sum',
            'book_value_usd': 'sum',
            'abandonment_cost_usd': 'sum',
            'total_stranded_value_usd': 'sum',
        }).reset_index()
        summary.rename(columns={'facility_id': 'stranded_facility_count'}, inplace=True)
        summary['total_capacity_mtpy'] = summary['capacity_tpy'] / 1e6
        summary['book_value_billion_usd'] = summary['book_value_usd'] / 1e9
        summary['abandonment_cost_billion_usd'] = summary['abandonment_cost_usd'] / 1e9
        summary['total_stranded_value_billion_usd'] = summary['total_stranded_value_usd'] / 1e9

        summary_cols = ['scenario', 'scenario_name', 'stranded_facility_count', 'total_capacity_mtpy',
                        'book_value_billion_usd', 'abandonment_cost_billion_usd', 'total_stranded_value_billion_usd']
        summary[summary_cols].to_csv(PROFESSIONAL_DIR / 'stranded_assets_summary.csv', index=False)

        return stranded_df
    else:
        print("    No stranded assets found")
        return pd.DataFrame()


def generate_investment_breakdown(df):
    """
    Generate investment breakdown by year, scenario, and technology
    """
    print("  Generating investment breakdown...")

    deployed = df[df['tech_deployed'] == 1].copy()

    investment = deployed.groupby(['year', 'scenario', 'technology']).agg({
        'capex_usd': 'sum',
        'opex_usd_yr': 'sum',
        'cost_component_new_energy_usd': 'sum',
        'cost_component_fuel_savings_usd': 'sum',
        'total_cost_usd': 'sum',
        'facility_id': 'count',
    }).reset_index()

    investment['scenario_name'] = investment['scenario'].map(SCENARIO_NAMES)
    investment['capex_million_usd'] = investment['capex_usd'] / 1e6
    investment['opex_million_usd'] = investment['opex_usd_yr'] / 1e6
    investment['energy_cost_million_usd'] = investment['cost_component_new_energy_usd'] / 1e6
    investment['fuel_savings_million_usd'] = investment['cost_component_fuel_savings_usd'] / 1e6
    investment['total_cost_million_usd'] = investment['total_cost_usd'] / 1e6
    investment.rename(columns={'facility_id': 'facility_count'}, inplace=True)

    output_cols = ['year', 'scenario', 'scenario_name', 'technology',
                   'capex_million_usd', 'opex_million_usd', 'energy_cost_million_usd',
                   'fuel_savings_million_usd', 'total_cost_million_usd', 'facility_count']
    investment[output_cols].to_csv(PROFESSIONAL_DIR / 'investment_breakdown.csv', index=False)
    return investment


def generate_macc_data(df):
    """
    Generate MACC curve data for plotting
    """
    print("  Generating MACC curve data...")

    # Get 2050 data with deployed technologies
    macc_data = df[(df['year'] == 2050) & (df['tech_deployed'] == 1)].copy()

    if len(macc_data) == 0:
        print("    No deployed technologies found in 2050")
        return pd.DataFrame()

    macc_output = macc_data[['scenario', 'facility_id', 'company', 'product', 'process',
                             'region', 'technology', 'mac_usd_per_tco2', 'abatement_tco2',
                             'capex_usd']].copy()

    macc_output['scenario_name'] = macc_output['scenario'].map(SCENARIO_NAMES)
    macc_output['abatement_mtco2'] = macc_output['abatement_tco2'] / 1e6
    macc_output['capex_million_usd'] = macc_output['capex_usd'] / 1e6

    # Sort by MAC for MACC curve
    macc_output = macc_output.sort_values(['scenario', 'mac_usd_per_tco2'])

    # Calculate cumulative abatement per scenario
    macc_output['cumulative_abatement_mtco2'] = macc_output.groupby('scenario')['abatement_mtco2'].cumsum()

    output_cols = ['scenario', 'scenario_name', 'facility_id', 'company', 'product', 'process',
                   'region', 'technology', 'mac_usd_per_tco2', 'abatement_mtco2',
                   'cumulative_abatement_mtco2', 'capex_million_usd']
    macc_output[output_cols].to_csv(PROFESSIONAL_DIR / 'macc_curve_data.csv', index=False)
    return macc_output


def main():
    """Main execution"""
    print("="*60)
    print("GENERATING PROFESSIONAL CSV OUTPUTS")
    print("="*60)

    # Load data
    df, stranded_params, facility_db = load_data()
    print(f"\nLoaded {len(df):,} rows")

    # Generate all outputs
    print("\n1. Executive Summary")
    generate_executive_summary(df)

    print("\n2. Annual Emissions Summary")
    generate_annual_emissions_summary(df)

    print("\n3. Regional Breakdown")
    generate_regional_breakdown(df)

    print("\n4. Company Breakdown")
    generate_company_breakdown(df)

    print("\n5. Technology Deployment")
    generate_technology_deployment(df)

    print("\n6. Stranded Asset Analysis")
    generate_stranded_asset_analysis(df, stranded_params, facility_db)

    print("\n7. Investment Breakdown")
    generate_investment_breakdown(df)

    print("\n8. MACC Curve Data")
    generate_macc_data(df)

    print("\n" + "="*60)
    print("COMPLETED!")
    print("="*60)
    print(f"All files saved to: {PROFESSIONAL_DIR}")


if __name__ == '__main__':
    main()
