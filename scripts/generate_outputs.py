"""
Consolidated Output Generator for Korea Petrochemical MACC Model
=================================================================

Generates all outputs from scenario results:
1. Emission pathway figures (PNG)
2. Summary CSV files
3. Professional reports
4. Stranded asset analysis

Usage:
    python generate_outputs.py              # Generate all outputs
    python generate_outputs.py --figures    # Figures only
    python generate_outputs.py --csv        # CSV files only
    python generate_outputs.py --reports    # Report tables only

Outputs:
- outputs/figures/*.png
- outputs/*.csv
- outputs/professional/*.csv
- outputs/report_tables/*.csv
"""

import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure, TECH_COLORS, REGION_COLORS, SCENARIO_NAMES, SCENARIO_NAMES_KR

# Path configuration - works when run from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Configuration
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
FIGURE_DIR = OUTPUT_DIR / 'figures'
PROFESSIONAL_DIR = OUTPUT_DIR / 'professional'
REPORT_DIR = OUTPUT_DIR / 'report_tables'
DATA_DIR = PROJECT_ROOT / 'data'

# Create directories
for d in [OUTPUT_DIR, FIGURE_DIR, PROFESSIONAL_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

apply_style()


def get_krw_per_usd():
    """Load exchange rate from model_config.csv"""
    config_path = DATA_DIR / 'assumptions' / 'model_config.csv'
    if config_path.exists():
        config = pd.read_csv(config_path)
        usd_row = config[config['parameter'] == 'usd_to_krw']
        if len(usd_row) > 0:
            return usd_row['value'].values[0]
    # Fallback for backwards compatibility
    return 1300


KRW_PER_USD = get_krw_per_usd()


# ============================================================================
# DATA LOADING
# ============================================================================

def load_scenario_results():
    """Load main scenario results"""
    results_path = OUTPUT_DIR / 'scenario_results.csv'
    if not results_path.exists():
        raise FileNotFoundError(
            f"Scenario results not found at {results_path}. "
            f"Run 'python run_scenarios.py' first to generate results."
        )
    return pd.read_csv(results_path)


def load_stranded_assets():
    """Load stranded asset data"""
    summary_path = OUTPUT_DIR / 'stranded_assets_summary.csv'
    if not summary_path.exists():
        print(f"  Warning: Stranded assets summary not found at {summary_path}")
        return pd.DataFrame(), pd.DataFrame()

    summary = pd.read_csv(summary_path)
    try:
        facilities = pd.read_csv(OUTPUT_DIR / 'stranded_assets_facilities.csv')
    except FileNotFoundError:
        facilities = pd.DataFrame()
    return summary, facilities


# ============================================================================
# FIGURE GENERATION
# ============================================================================

def generate_technology_emissions_chart(df, scenario):
    """Generate stacked area chart of emissions by technology"""
    scenario_df = df[df['scenario'] == scenario].copy()

    # Check for empty data
    if len(scenario_df) == 0:
        print(f"    Warning: No data for scenario '{scenario}', skipping technology chart")
        return None

    tech_emissions = scenario_df.groupby(['year', 'technology'])['emissions_tco2'].sum().unstack(fill_value=0)

    # Check for empty result after grouping
    if len(tech_emissions) == 0:
        print(f"    Warning: No technology data for scenario '{scenario}', skipping chart")
        return None

    tech_emissions = tech_emissions / 1e6

    tech_order = ['Baseline', 'NCC-H2', 'NCC-Electricity', 'RDH', 'Heat_Pump']
    cols = [c for c in tech_order if c in tech_emissions.columns]

    if len(cols) == 0:
        print(f"    Warning: No recognized technologies for scenario '{scenario}', skipping chart")
        return None

    tech_emissions = tech_emissions[cols]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [TECH_COLORS.get(t, '#808080') for t in cols]
    tech_emissions.plot.area(ax=ax, color=colors, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Technology - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    filename = FIGURE_DIR / f'emissions_by_technology_{scenario}.png'
    save_figure(plt.gcf(), filename)
    # CSV export
    tidy = tech_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'MtCO2_per_yr'
    tidy['scenario'] = scenario
    save_figure_data(tidy, filename, figure_type='stacked_area')
    return filename


def generate_regional_emissions_chart(df, scenario):
    """Generate stacked area chart of emissions by region"""
    scenario_df = df[df['scenario'] == scenario].copy()

    # Check for empty data
    if len(scenario_df) == 0:
        print(f"    Warning: No data for scenario '{scenario}', skipping regional chart")
        return None

    scenario_df['region_simple'] = scenario_df['region'].apply(
        lambda x: 'Yeosu' if 'Yeosu' in str(x) else (
            'Daesan' if 'Daesan' in str(x) else (
                'Ulsan' if 'Ulsan' in str(x) else 'Other')))

    regional = scenario_df.groupby(['year', 'region_simple'])['emissions_tco2'].sum().unstack(fill_value=0)

    # Check for empty result
    if len(regional) == 0:
        print(f"    Warning: No regional data for scenario '{scenario}', skipping chart")
        return None

    regional = regional / 1e6
    region_order = ['Yeosu', 'Daesan', 'Ulsan', 'Other']
    cols = [c for c in region_order if c in regional.columns]

    if len(cols) == 0:
        print(f"    Warning: No recognized regions for scenario '{scenario}', skipping chart")
        return None

    regional = regional[cols]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [REGION_COLORS.get(r, '#808080') for r in cols]
    regional.plot.area(ax=ax, color=colors, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Region - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    filename = FIGURE_DIR / f'emissions_by_region_{scenario}.png'
    save_figure(plt.gcf(), filename)
    # CSV export
    tidy = regional.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'MtCO2_per_yr'
    tidy['scenario'] = scenario
    save_figure_data(tidy, filename, figure_type='stacked_area')
    return filename


def generate_company_emissions_chart(df, scenario, top_n=10):
    """Generate line chart of emissions by company (top N)"""
    scenario_df = df[df['scenario'] == scenario].copy()

    # Check for empty data
    if len(scenario_df) == 0:
        print(f"    Warning: No data for scenario '{scenario}', skipping company chart")
        return None

    baseline_2025 = scenario_df[scenario_df['year'] == 2025].groupby('company')['emissions_tco2'].sum()

    # Check for empty 2025 baseline
    if len(baseline_2025) == 0:
        print(f"    Warning: No 2025 data for scenario '{scenario}', skipping company chart")
        return None

    top_companies = baseline_2025.nlargest(top_n).index.tolist()

    if len(top_companies) == 0:
        print(f"    Warning: No companies found for scenario '{scenario}', skipping chart")
        return None

    company_df = scenario_df[scenario_df['company'].isin(top_companies)]
    company_emissions = company_df.groupby(['year', 'company'])['emissions_tco2'].sum().unstack(fill_value=0) / 1e6

    fig, ax = plt.subplots(figsize=(12, 6))
    for company in company_emissions.columns:
        ax.plot(company_emissions.index, company_emissions[company], label=company, linewidth=2, marker='o', markersize=3)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Company (Top {top_n}) - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True, fontsize=8)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    filename = FIGURE_DIR / f'emissions_by_company_{scenario}.png'
    save_figure(plt.gcf(), filename)
    # CSV export
    tidy = company_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'MtCO2_per_yr'
    tidy['scenario'] = scenario
    save_figure_data(tidy, filename, figure_type='line')
    return filename


def generate_process_emissions_chart(df, scenario):
    """Generate stacked area chart of emissions by process"""
    scenario_df = df[df['scenario'] == scenario].copy()

    # Check for empty data
    if len(scenario_df) == 0:
        print(f"    Warning: No data for scenario '{scenario}', skipping process chart")
        return None

    process_emissions = scenario_df.groupby(['year', 'process'])['emissions_tco2'].sum().unstack(fill_value=0)

    # Check for empty result
    if len(process_emissions) == 0:
        print(f"    Warning: No process data for scenario '{scenario}', skipping chart")
        return None

    process_emissions = process_emissions / 1e6

    fig, ax = plt.subplots(figsize=(12, 6))
    process_emissions.plot.area(ax=ax, alpha=0.8, linewidth=0)

    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (MtCO2/year)')
    ax.set_title(f'Emission Pathway by Process - {SCENARIO_NAMES.get(scenario, scenario)}')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    filename = FIGURE_DIR / f'emissions_by_process_{scenario}.png'
    save_figure(plt.gcf(), filename)
    # CSV export
    tidy = process_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'MtCO2_per_yr'
    tidy['scenario'] = scenario
    save_figure_data(tidy, filename, figure_type='stacked_area')
    return filename


def generate_all_scenarios_comparison(df):
    """Generate comparison chart of total emissions across all scenarios"""
    total_emissions = df.groupby(['year', 'scenario'])['emissions_tco2'].sum().unstack(fill_value=0) / 1e6

    fig, ax = plt.subplots(figsize=(14, 7))
    for scenario in total_emissions.columns:
        label = SCENARIO_NAMES.get(scenario, scenario)
        ax.plot(total_emissions.index, total_emissions[scenario], label=label, linewidth=2.5)

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Emissions (MtCO2/year)')
    ax.set_title('Emission Pathways - All Scenarios Comparison')
    ax.legend(loc='upper right', frameon=True)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='green', linestyle='--', alpha=0.5, linewidth=1)

    filename = FIGURE_DIR / 'emissions_all_scenarios_comparison.png'
    save_figure(plt.gcf(), filename)
    # CSV export
    tidy = total_emissions.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'MtCO2_per_yr'
    save_figure_data(tidy, filename, figure_type='line')
    return filename


def generate_figures(df):
    """Generate all figures"""
    print("\n" + "=" * 60)
    print("GENERATING FIGURES")
    print("=" * 60)

    scenarios = df['scenario'].unique()

    print("\n1. All-scenario comparison...")
    generate_all_scenarios_comparison(df)
    print(f"   Saved: {FIGURE_DIR / 'emissions_all_scenarios_comparison.png'}")

    for scenario in scenarios:
        print(f"\n2. Generating charts for: {SCENARIO_NAMES.get(scenario, scenario)}")
        generate_technology_emissions_chart(df, scenario)
        print(f"   - emissions_by_technology_{scenario}.png")
        generate_regional_emissions_chart(df, scenario)
        print(f"   - emissions_by_region_{scenario}.png")
        generate_company_emissions_chart(df, scenario)
        print(f"   - emissions_by_company_{scenario}.png")
        generate_process_emissions_chart(df, scenario)
        print(f"   - emissions_by_process_{scenario}.png")


# ============================================================================
# CSV GENERATION
# ============================================================================

def generate_summary_csvs(df):
    """Generate summary CSV files"""
    print("\n" + "=" * 60)
    print("GENERATING SUMMARY CSV FILES")
    print("=" * 60)

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
                'Ulsan' if 'Ulsan' in str(x) else 'Other')))
    emissions_by_region = df_copy.groupby(['year', 'scenario', 'region_simple']).agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
    }).reset_index()
    emissions_by_region.to_csv(OUTPUT_DIR / 'emissions_by_region_year.csv', index=False)
    print(f"  Saved: outputs/emissions_by_region_year.csv")


def generate_professional_csvs(df):
    """Generate professional CSV outputs for stakeholders"""
    print("\n" + "=" * 60)
    print("GENERATING PROFESSIONAL CSV OUTPUTS")
    print("=" * 60)

    # 1. Executive Summary
    print("  Generating executive summary...")
    summaries = []
    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario]
        baseline_2025 = scenario_df[scenario_df['year'] == 2025]
        baseline_emissions = baseline_2025['bau_emissions_tco2'].sum()
        final_2050 = scenario_df[scenario_df['year'] == 2050]
        final_emissions = final_2050['emissions_tco2'].sum()
        total_abatement = scenario_df['abatement_tco2'].sum()
        deployed = scenario_df[scenario_df['tech_deployed'] == 1]
        total_capex = deployed['capex_usd'].sum()
        tech_counts = deployed.groupby('technology')['facility_id'].nunique()

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
            'electricity_demand_2050_twh': final_2050['elec_demand_mwh'].sum() / 1e6,
            'hydrogen_demand_2050_kt': final_2050['h2_demand_t'].sum() / 1e3,
        })

    pd.DataFrame(summaries).to_csv(PROFESSIONAL_DIR / 'executive_summary.csv', index=False)
    print(f"  Saved: professional/executive_summary.csv")

    # 2. Technology Deployment Timeline
    print("  Generating technology deployment timeline...")
    deployed = df[df['tech_deployed'] == 1].copy()
    if len(deployed) > 0:
        tech_timeline = deployed.groupby(['year', 'scenario', 'technology']).agg({
            'facility_id': 'count',
            'abatement_tco2': 'sum',
            'capex_usd': 'sum',
        }).reset_index()
        tech_timeline['scenario_name'] = tech_timeline['scenario'].map(SCENARIO_NAMES).fillna(tech_timeline['scenario'])
        tech_timeline['abatement_mtco2'] = tech_timeline['abatement_tco2'] / 1e6
        tech_timeline['capex_million_usd'] = tech_timeline['capex_usd'] / 1e6
        tech_timeline.rename(columns={'facility_id': 'facilities_deployed'}, inplace=True)
        tech_timeline.to_csv(PROFESSIONAL_DIR / 'technology_deployment.csv', index=False)
        print(f"  Saved: professional/technology_deployment.csv")


def generate_report_tables(df, stranded_summary, stranded_facilities):
    """Generate report tables for NCC stranded asset analysis"""
    print("\n" + "=" * 60)
    print("GENERATING REPORT TABLES")
    print("=" * 60)

    # Table 1: Scenario Comparison
    print("  Generating scenario comparison table...")
    rows = []
    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario]
        baseline_2025 = scenario_df[scenario_df['year'] == 2025]
        final_2050 = scenario_df[scenario_df['year'] == 2050]
        deployed = scenario_df[scenario_df['tech_deployed'] == 1]

        stranded_row = stranded_summary[stranded_summary['scenario'] == scenario]
        if len(stranded_row) > 0 and 'stranding_year_1.5C' in stranded_row.columns:
            stranding_year_15c = int(stranded_row['stranding_year_1.5C'].iloc[0])
        else:
            stranding_year_15c = None

        rows.append({
            'scenario': scenario,
            'scenario_name_kr': SCENARIO_NAMES_KR.get(scenario, scenario),
            'total_facilities': baseline_2025['facility_id'].nunique(),
            'emissions_2025_mtco2': baseline_2025['emissions_tco2'].sum() / 1e6,
            'emissions_2050_mtco2': final_2050['emissions_tco2'].sum() / 1e6,
            'total_capex_billion_usd': deployed['capex_usd'].sum() / 1e9,
            'h2_demand_2050_kt': final_2050['h2_demand_t'].sum() / 1e3,
            'elec_demand_2050_twh': final_2050['elec_demand_mwh'].sum() / 1e6,
            'stranding_year_15c': stranding_year_15c,
        })

    pd.DataFrame(rows).to_csv(REPORT_DIR / 'table1_scenario_comparison.csv', index=False, encoding='utf-8-sig')
    print(f"  Saved: report_tables/table1_scenario_comparison.csv")

    # Table 2: Stranded Asset Summary
    print("  Generating stranded asset summary...")
    if len(stranded_facilities) > 0:
        ncc_stranded = stranded_facilities[stranded_facilities['process'] == 'Naphtha Cracker'].copy()
        summary_rows = []
        for _, row in stranded_summary.iterrows():
            scenario = row['scenario']
            ncc_15c = ncc_stranded[(ncc_stranded['scenario'] == scenario) & (ncc_stranded['budget_scenario'] == '1.5C')]
            ncc_value_15c = ncc_15c['stranded_value_usd'].sum() if len(ncc_15c) > 0 else 0

            summary_rows.append({
                'scenario': scenario,
                'scenario_name_kr': SCENARIO_NAMES_KR.get(scenario, scenario),
                'stranding_year_15c': int(row['stranding_year_1.5C']),
                'ncc_stranded_15c_billion_usd': ncc_value_15c / 1e9,
                'ncc_stranded_15c_trillion_krw': (ncc_value_15c * KRW_PER_USD) / 1e12,
                'stranding_year_20c': int(row['stranding_year_2.0C']),
            })

        pd.DataFrame(summary_rows).to_csv(REPORT_DIR / 'table2_stranded_summary.csv', index=False, encoding='utf-8-sig')
        print(f"  Saved: report_tables/table2_stranded_summary.csv")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Generate outputs from scenario results')
    parser.add_argument('--figures', action='store_true', help='Generate figures only')
    parser.add_argument('--csv', action='store_true', help='Generate CSV files only')
    parser.add_argument('--reports', action='store_true', help='Generate report tables only')
    args = parser.parse_args()

    # If no specific args, generate all
    generate_all = not (args.figures or args.csv or args.reports)

    print("=" * 60)
    print("KOREA PETROCHEMICAL MACC MODEL - OUTPUT GENERATOR")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load data
    df = load_scenario_results()
    stranded_summary, stranded_facilities = load_stranded_assets()
    print(f"\nLoaded {len(df):,} rows for {df['scenario'].nunique()} scenarios")

    # Generate outputs
    if args.figures or generate_all:
        generate_figures(df)

    if args.csv or generate_all:
        generate_summary_csvs(df)
        generate_professional_csvs(df)

    if args.reports or generate_all:
        generate_report_tables(df, stranded_summary, stranded_facilities)

    print("\n" + "=" * 60)
    print("OUTPUT GENERATION COMPLETE")
    print("=" * 60)
    print(f"Figures: {FIGURE_DIR}")
    print(f"CSV summaries: {OUTPUT_DIR}")
    print(f"Professional outputs: {PROFESSIONAL_DIR}")
    print(f"Report tables: {REPORT_DIR}")


if __name__ == '__main__':
    main()
