"""
Generate Emission Pathway Visualizations for Korea Petrochemical MACC Model
===========================================================================

Creates emission trajectory charts showing:
1. Emissions by fuel source (derived from energy × emission factors)
2. Emissions by technology (Baseline, NCC-H2, NCC-Elec, RDH, Heat_Pump)
3. Emissions by company (Top 10 companies)
4. Emissions by region (Yeosu, Daesan, Ulsan, Other)

Outputs:
- PNG figures in outputs/figures/
- CSV summary files in outputs/
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure, TECH_COLORS, REGION_COLORS, FUEL_COLORS, SCENARIO_NAMES

# Path configuration - works when run from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Configuration
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
FIGURE_DIR = OUTPUT_DIR / 'figures'
DATA_DIR = PROJECT_ROOT / 'data'

FIGURE_DIR.mkdir(parents=True, exist_ok=True)

apply_style()


def load_data():
    """Load scenario results and assumptions"""
    results = pd.read_csv(OUTPUT_DIR / 'scenario_results.csv')
    emission_factors = pd.read_csv(DATA_DIR / 'assumptions' / 'emission_factors.csv')

    # Create emission factor lookup
    ef_lookup = {}
    for _, row in emission_factors.iterrows():
        fuel = row['fuel']
        if pd.notna(row['tCO2_per_GJ']):
            ef_lookup[fuel.lower()] = row['tCO2_per_GJ']

    return results, ef_lookup


def generate_technology_emissions_chart(df, scenario, save=True):
    """
    Generate stacked area chart of emissions by technology over time
    """
    scenario_df = df[df['scenario'] == scenario].copy()

    # Aggregate emissions by year and technology
    tech_emissions = scenario_df.groupby(['year', 'technology'])['emissions_tco2'].sum().unstack(fill_value=0)
    tech_emissions = tech_emissions / 1e6  # Convert to MtCO2

    # Ensure consistent ordering
    tech_order = ['Baseline', 'NCC-H2', 'NCC-Electricity', 'RDH', 'Heat_Pump']
    cols = [c for c in tech_order if c in tech_emissions.columns]
    tech_emissions = tech_emissions[cols]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Stacked area plot
    colors = [TECH_COLORS.get(t, '#808080') for t in cols]
    tech_emissions.plot.area(ax=ax, color=colors, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Technology - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    if save:
        filename = FIGURE_DIR / f'emissions_by_technology_{scenario}.png'
        save_figure(plt.gcf(), filename)
        print(f"  Saved: {filename}")
        # CSV export
        tidy = tech_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
        tidy['unit'] = 'MtCO2_per_yr'
        tidy['scenario'] = scenario
        save_figure_data(tidy, filename, figure_type='stacked_area')
    else:
        plt.close()

    return tech_emissions


def generate_company_emissions_chart(df, scenario, top_n=10, save=True):
    """
    Generate line chart of emissions by company (top N) over time
    """
    scenario_df = df[df['scenario'] == scenario].copy()

    # Get top N companies by 2025 emissions
    baseline_2025 = scenario_df[scenario_df['year'] == 2025].groupby('company')['emissions_tco2'].sum()
    top_companies = baseline_2025.nlargest(top_n).index.tolist()

    # Aggregate emissions for top companies
    company_emissions = scenario_df[scenario_df['company'].isin(top_companies)].groupby(
        ['year', 'company'])['emissions_tco2'].sum().unstack(fill_value=0)
    company_emissions = company_emissions / 1e6  # Convert to MtCO2

    # Sort columns by 2025 emissions
    col_order = baseline_2025.loc[top_companies].sort_values(ascending=False).index.tolist()
    company_emissions = company_emissions[[c for c in col_order if c in company_emissions.columns]]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Line plot
    for i, company in enumerate(company_emissions.columns):
        ax.plot(company_emissions.index, company_emissions[company],
                label=company, linewidth=2, marker='o', markersize=3)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Company (Top {top_n}) - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True, fontsize=8)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    if save:
        filename = FIGURE_DIR / f'emissions_by_company_{scenario}.png'
        save_figure(plt.gcf(), filename)
        print(f"  Saved: {filename}")
        # CSV export
        tidy = company_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
        tidy['unit'] = 'MtCO2_per_yr'
        tidy['scenario'] = scenario
        save_figure_data(tidy, filename, figure_type='line')
    else:
        plt.close()

    return company_emissions


def generate_regional_emissions_chart(df, scenario, save=True):
    """
    Generate stacked area chart of emissions by region over time
    """
    scenario_df = df[df['scenario'] == scenario].copy()

    # Simplify region names
    scenario_df['region_simple'] = scenario_df['region'].apply(
        lambda x: 'Yeosu' if 'Yeosu' in str(x) else (
            'Daesan' if 'Daesan' in str(x) else (
                'Ulsan' if 'Ulsan' in str(x) else 'Other'
            )
        )
    )

    # Aggregate emissions by year and region
    regional_emissions = scenario_df.groupby(['year', 'region_simple'])['emissions_tco2'].sum().unstack(fill_value=0)
    regional_emissions = regional_emissions / 1e6  # Convert to MtCO2

    # Ensure consistent ordering
    region_order = ['Yeosu', 'Daesan', 'Ulsan', 'Other']
    cols = [c for c in region_order if c in regional_emissions.columns]
    regional_emissions = regional_emissions[cols]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Stacked area plot
    colors = [REGION_COLORS.get(r, '#808080') for r in cols]
    regional_emissions.plot.area(ax=ax, color=colors, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Region - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    if save:
        filename = FIGURE_DIR / f'emissions_by_region_{scenario}.png'
        save_figure(plt.gcf(), filename)
        print(f"  Saved: {filename}")
        # CSV export
        tidy = regional_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
        tidy['unit'] = 'MtCO2_per_yr'
        tidy['scenario'] = scenario
        save_figure_data(tidy, filename, figure_type='stacked_area')
    else:
        plt.close()

    return regional_emissions


def generate_process_emissions_chart(df, scenario, save=True):
    """
    Generate stacked area chart of emissions by process type over time
    (Naphtha Cracker, BTX Plant, Utility as proxy for fuel mix)
    """
    scenario_df = df[df['scenario'] == scenario].copy()

    # Aggregate emissions by year and process
    process_emissions = scenario_df.groupby(['year', 'process'])['emissions_tco2'].sum().unstack(fill_value=0)
    process_emissions = process_emissions / 1e6  # Convert to MtCO2

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Stacked area plot
    process_emissions.plot.area(ax=ax, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Process - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    if save:
        filename = FIGURE_DIR / f'emissions_by_process_{scenario}.png'
        save_figure(plt.gcf(), filename)
        print(f"  Saved: {filename}")
        # CSV export
        tidy = process_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
        tidy['unit'] = 'MtCO2_per_yr'
        tidy['scenario'] = scenario
        save_figure_data(tidy, filename, figure_type='stacked_area')
    else:
        plt.close()

    return process_emissions


def generate_all_scenarios_comparison(df, save=True):
    """
    Generate comparison chart of total emissions across all scenarios
    """
    # Aggregate total emissions by year and scenario
    total_emissions = df.groupby(['year', 'scenario'])['emissions_tco2'].sum().unstack(fill_value=0)
    total_emissions = total_emissions / 1e6  # Convert to MtCO2

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))

    # Line plot for each scenario
    for scenario in total_emissions.columns:
        label = SCENARIO_NAMES.get(scenario, scenario)
        ax.plot(total_emissions.index, total_emissions[scenario],
                label=label, linewidth=2.5)

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Emissions (MtCO2/year)')
    ax.set_title('Emission Pathways - All Scenarios Comparison')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # Add net zero line
    ax.axhline(y=0, color='green', linestyle='--', alpha=0.5, linewidth=1)

    if save:
        filename = FIGURE_DIR / 'emissions_all_scenarios_comparison.png'
        save_figure(plt.gcf(), filename)
        print(f"  Saved: {filename}")
        # CSV export
        tidy = total_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
        tidy['unit'] = 'MtCO2_per_yr'
        save_figure_data(tidy, filename, figure_type='line')
    else:
        plt.close()

    return total_emissions


def generate_summary_csvs(df):
    """
    Generate summary CSV files for professional outputs
    """
    print("\n" + "="*60)
    print("GENERATING SUMMARY CSV FILES")
    print("="*60)

    # 1. Emissions by year and scenario
    emissions_by_scenario = df.groupby(['year', 'scenario']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
    }).reset_index()
    emissions_by_scenario.to_csv(OUTPUT_DIR / 'emissions_by_scenario_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_scenario_year.csv")

    # 2. Emissions by technology and year
    emissions_by_tech = df.groupby(['year', 'scenario', 'technology']).agg({
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
    }).reset_index()
    emissions_by_tech.to_csv(OUTPUT_DIR / 'emissions_by_technology_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_technology_year.csv")

    # 3. Emissions by company and year
    emissions_by_company = df.groupby(['year', 'scenario', 'company']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
    }).reset_index()
    emissions_by_company.to_csv(OUTPUT_DIR / 'emissions_by_company_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_company_year.csv")

    # 4. Emissions by region and year
    df_copy = df.copy()
    df_copy['region_simple'] = df_copy['region'].apply(
        lambda x: 'Yeosu' if 'Yeosu' in str(x) else (
            'Daesan' if 'Daesan' in str(x) else (
                'Ulsan' if 'Ulsan' in str(x) else 'Other'
            )
        )
    )
    emissions_by_region = df_copy.groupby(['year', 'scenario', 'region_simple']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
    }).reset_index()
    emissions_by_region.to_csv(OUTPUT_DIR / 'emissions_by_region_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_region_year.csv")

    # 5. Emissions by process and year
    emissions_by_process = df.groupby(['year', 'scenario', 'process']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
    }).reset_index()
    emissions_by_process.to_csv(OUTPUT_DIR / 'emissions_by_process_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_process_year.csv")


def main():
    """Main execution"""
    print("="*60)
    print("GENERATING EMISSION PATHWAY VISUALIZATIONS")
    print("="*60)

    # Load data
    df, ef_lookup = load_data()
    scenarios = df['scenario'].unique()

    print(f"\nLoaded {len(df):,} rows for {len(scenarios)} scenarios")

    # Generate all-scenario comparison
    print("\n1. Generating all-scenario comparison...")
    generate_all_scenarios_comparison(df)

    # Generate per-scenario charts
    for scenario in scenarios:
        print(f"\n2. Generating charts for: {SCENARIO_NAMES.get(scenario, scenario)}")

        print("   - Technology emissions...")
        generate_technology_emissions_chart(df, scenario)

        print("   - Company emissions (Top 10)...")
        generate_company_emissions_chart(df, scenario)

        print("   - Regional emissions...")
        generate_regional_emissions_chart(df, scenario)

        print("   - Process emissions...")
        generate_process_emissions_chart(df, scenario)

    # Generate summary CSVs
    generate_summary_csvs(df)

    print("\n" + "="*60)
    print("COMPLETED!")
    print("="*60)
    print(f"Figures saved to: {FIGURE_DIR}")
    print(f"CSV files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
