"""
Generate data tables and figures for PETROCHEMICAL_DECARBONIZATION_REPORT.md
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# Set up output directories
OUTPUT_DIR = 'outputs/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set matplotlib style
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    try:
        plt.style.use('seaborn-whitegrid')
    except OSError:
        pass  # Use default style
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

def load_data():
    """Load all required data files"""
    scenario_results = pd.read_csv('outputs/scenario_results.csv')
    regional_mac = pd.read_csv('outputs/regional_mac_summary.csv')
    stranded_assets = pd.read_csv('outputs/stranded_assets_summary.csv')
    emissions_by_company = pd.read_csv('outputs/emissions_by_company_summary.csv')

    # Technology parameters - handle potential parsing issues
    try:
        tech_params = pd.read_csv('data/assumptions/technology_parameters.csv', on_bad_lines='skip')
    except Exception:
        tech_params = pd.DataFrame()

    return {
        'scenario_results': scenario_results,
        'regional_mac': regional_mac,
        'stranded_assets': stranded_assets,
        'emissions_by_company': emissions_by_company,
        'tech_params': tech_params
    }

def generate_scenario_summary(df):
    """Generate 6-scenario summary table"""
    # Group by scenario and year=2050 for final state
    summary_2050 = df[df['year'] == 2050].groupby('scenario').agg({
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'total_cost_usd': 'sum',
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()

    # Also get baseline (2025)
    baseline_2025 = df[df['year'] == 2025].groupby('scenario').agg({
        'bau_emissions_tco2': 'sum'
    }).reset_index()
    baseline_2025.columns = ['scenario', 'baseline_emissions_2025']

    # Merge
    summary = summary_2050.merge(baseline_2025, on='scenario')

    # Calculate cumulative costs
    cumulative = df.groupby('scenario').agg({
        'capex_usd': 'sum',
        'total_cost_usd': 'sum'
    }).reset_index()
    cumulative.columns = ['scenario', 'cumulative_capex', 'cumulative_total_cost']

    summary = summary.merge(cumulative, on='scenario')

    # Format values
    summary['baseline_emissions_mt'] = summary['baseline_emissions_2025'] / 1e6
    summary['final_emissions_mt'] = summary['emissions_tco2'] / 1e6
    summary['total_abatement_mt'] = summary['abatement_tco2'] / 1e6
    summary['cumulative_capex_b'] = summary['cumulative_capex'] / 1e9
    summary['cumulative_cost_b'] = summary['cumulative_total_cost'] / 1e9
    summary['elec_demand_twh'] = summary['elec_demand_mwh'] / 1e6
    summary['h2_demand_mt'] = summary['h2_demand_t'] / 1e6

    return summary

def generate_regional_summary(df):
    """Generate regional emissions and costs by scenario"""
    # 2025 baseline
    baseline = df[df['year'] == 2025].groupby(['scenario', 'region']).agg({
        'bau_emissions_tco2': 'sum'
    }).reset_index()
    baseline.columns = ['scenario', 'region', 'baseline_emissions']

    # 2050 final
    final = df[df['year'] == 2050].groupby(['scenario', 'region']).agg({
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()

    # Cumulative
    cumulative = df.groupby(['scenario', 'region']).agg({
        'capex_usd': 'sum',
        'total_cost_usd': 'sum'
    }).reset_index()
    cumulative.columns = ['scenario', 'region', 'cum_capex', 'cum_total_cost']

    regional = baseline.merge(final, on=['scenario', 'region']).merge(cumulative, on=['scenario', 'region'])

    return regional

def generate_company_summary(df, emissions_by_company):
    """Generate company-level analysis"""
    # Join with baseline emissions
    company_analysis = df.groupby(['scenario', 'company']).agg({
        'bau_emissions_tco2': lambda x: x[df.loc[x.index, 'year'] == 2025].sum(),
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'total_cost_usd': 'sum',
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()

    return company_analysis

def generate_technology_deployment(df):
    """Generate technology deployment by year and scenario"""
    deployed = df[df['tech_deployed'] == 1].copy()

    tech_timeline = deployed.groupby(['scenario', 'year', 'technology']).agg({
        'facility_id': 'count',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum'
    }).reset_index()
    tech_timeline.columns = ['scenario', 'year', 'technology', 'facilities_deployed', 'abatement', 'capex']

    return tech_timeline

def plot_macc_curves(df, output_path):
    """Generate MACC curves for all 6 scenarios"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    scenarios = df['scenario'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for idx, scenario in enumerate(sorted(scenarios)):
        ax = axes[idx]
        scenario_data = df[(df['scenario'] == scenario) & (df['year'] == 2050)]

        # Sort by MAC
        scenario_data = scenario_data[scenario_data['mac_usd_per_tco2'] > 0].sort_values('mac_usd_per_tco2')

        if len(scenario_data) > 0:
            cumulative_abatement = scenario_data['abatement_tco2'].cumsum() / 1e6
            mac = scenario_data['mac_usd_per_tco2']

            # Step plot
            ax.step(cumulative_abatement, mac, where='post', linewidth=2, color=colors[idx])
            ax.fill_between(cumulative_abatement, 0, mac, step='post', alpha=0.3, color=colors[idx])

        ax.set_title(scenario.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_xlabel('Cumulative Abatement (Mt CO2)')
        ax.set_ylabel('MAC ($/tCO2)')
        ax.set_ylim(0, 600)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Marginal Abatement Cost Curves by Scenario (2050)', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_emissions_trajectory(df, output_path):
    """Generate emissions trajectory for all scenarios"""
    fig, ax = plt.subplots(figsize=(14, 8))

    scenarios = sorted(df['scenario'].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))
    linestyles = ['-', '--', '-.', ':', '-', '--']

    for idx, scenario in enumerate(scenarios):
        scenario_data = df[df['scenario'] == scenario].groupby('year').agg({
            'emissions_tco2': 'sum'
        }).reset_index()

        emissions_mt = scenario_data['emissions_tco2'] / 1e6
        ax.plot(scenario_data['year'], emissions_mt,
                label=scenario.replace('_', ' ').title(),
                linewidth=2.5, color=colors[idx], linestyle=linestyles[idx % len(linestyles)])

    # Add baseline reference
    baseline = df[df['year'] == 2025].groupby('scenario')['bau_emissions_tco2'].sum().mean() / 1e6
    ax.axhline(y=baseline, color='red', linestyle=':', linewidth=2, alpha=0.7, label='2025 Baseline')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Emissions (Mt CO2)', fontsize=12)
    ax.set_title('Emissions Trajectory by Scenario (2025-2050)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, None)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_regional_heatmap(df, output_path):
    """Generate regional emissions heatmap"""
    # Pivot for heatmap
    pivot_data = df.groupby(['year', 'region'])['emissions_tco2'].sum().unstack() / 1e6

    fig, ax = plt.subplots(figsize=(12, 10))

    im = ax.imshow(pivot_data.T, aspect='auto', cmap='YlOrRd')

    # Labels
    ax.set_xticks(np.arange(len(pivot_data.index))[::5])
    ax.set_xticklabels(pivot_data.index[::5])
    ax.set_yticks(np.arange(len(pivot_data.columns)))
    ax.set_yticklabels(pivot_data.columns)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Region', fontsize=12)
    ax.set_title('Regional Emissions Over Time (Mt CO2) - Shaheen NCC-H2 Scenario', fontsize=14, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Emissions (Mt CO2)', fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_technology_timeline(df, output_path):
    """Generate technology deployment timeline"""
    # Filter for deployed technologies
    deployed = df[df['tech_deployed'] == 1].copy()

    # Count by year and technology
    tech_counts = deployed.groupby(['year', 'technology']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 8))

    tech_counts.plot(kind='bar', stacked=True, ax=ax, width=0.8,
                     colormap='Set2', edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Facilities Deployed', fontsize=12)
    ax.set_title('Technology Deployment Timeline (Shaheen NCC-H2 Scenario)', fontsize=14, fontweight='bold')
    ax.legend(title='Technology', loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Rotate x labels
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_h2_vs_elec_comparison(df, output_path):
    """Generate H2 vs Electric cost comparison"""
    # Compare H2 and Electric scenarios
    h2_scenarios = ['shaheen_ncc_h2', 'restructure_25pct_ncc_h2', 'restructure_40pct_ncc_h2']
    elec_scenarios = ['shaheen_ncc_elec', 'restructure_25pct_ncc_elec', 'restructure_40pct_ncc_elec']

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Cumulative CAPEX
    ax1 = axes[0]
    for scenario in sorted(df['scenario'].unique()):
        scenario_data = df[df['scenario'] == scenario].groupby('year')['capex_usd'].sum().cumsum() / 1e9
        style = '-' if 'h2' in scenario else '--'
        color = 'blue' if 'shaheen' in scenario else ('green' if '25pct' in scenario else 'orange')
        ax1.plot(scenario_data.index, scenario_data.values, label=scenario.replace('_', ' ').title(),
                linestyle=style, linewidth=2, color=color)

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Cumulative CAPEX (Billion $)', fontsize=12)
    ax1.set_title('Cumulative CAPEX by Scenario', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=8, loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Energy demand comparison (2050)
    ax2 = axes[1]
    final_2050 = df[df['year'] == 2050].groupby('scenario').agg({
        'h2_demand_t': 'sum',
        'elec_demand_mwh': 'sum'
    }).reset_index()

    x = np.arange(len(final_2050))
    width = 0.35

    bars1 = ax2.bar(x - width/2, final_2050['h2_demand_t'] / 1e6, width, label='H2 Demand (Mt)', color='steelblue')
    bars2 = ax2.bar(x + width/2, final_2050['elec_demand_mwh'] / 1e6, width, label='Elec Demand (TWh)', color='forestgreen')

    ax2.set_xlabel('Scenario', fontsize=12)
    ax2.set_ylabel('Demand', fontsize=12)
    ax2.set_title('Energy Demand by Scenario (2050)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.replace('_', '\n') for s in final_2050['scenario']], fontsize=8)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_stranded_assets(stranded_df, output_path):
    """Generate stranded assets waterfall"""
    fig, ax = plt.subplots(figsize=(14, 8))

    scenarios = stranded_df['scenario'].tolist()
    x = np.arange(len(scenarios))
    width = 0.35

    values_15c = stranded_df['stranded_value_1.5C_usd'] / 1e9
    values_20c = stranded_df['stranded_value_2.0C_usd'] / 1e9

    bars1 = ax.bar(x - width/2, values_15c, width, label='1.5C Pathway', color='#FF6B6B')
    bars2 = ax.bar(x + width/2, values_20c, width, label='2.0C Pathway', color='#4ECDC4')

    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Stranded Asset Value (Billion $)', fontsize=12)
    ax.set_title('Stranded Asset Risk by Scenario and Climate Pathway', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_', '\n') for s in scenarios], fontsize=9)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'${height:.1f}B',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'${height:.1f}B',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_facility_scatter(df, output_path):
    """Generate facility-level MAC vs Abatement scatter"""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Use 2050 data for one scenario
    scenario_data = df[(df['scenario'] == 'shaheen_ncc_h2') & (df['year'] == 2050)]
    scenario_data = scenario_data[scenario_data['mac_usd_per_tco2'] > 0]

    # Color by region
    regions = scenario_data['region'].unique()
    colors = {'Daesan': '#FF6B6B', 'Yeosu': '#4ECDC4', 'Ulsan': '#45B7D1', 'Other': '#96CEB4'}

    for region in regions:
        region_data = scenario_data[scenario_data['region'] == region]
        ax.scatter(region_data['abatement_tco2'] / 1e3,
                  region_data['mac_usd_per_tco2'],
                  label=region, alpha=0.7, s=100, color=colors.get(region, 'gray'))

    ax.set_xlabel('Abatement Potential (kt CO2)', fontsize=12)
    ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=12)
    ax.set_title('Facility-Level MAC vs Abatement Potential (2050)', fontsize=14, fontweight='bold')
    ax.legend(title='Region', fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def format_table_markdown(df, title, columns_format=None):
    """Format dataframe as markdown table"""
    md = f"\n### {title}\n\n"
    md += df.to_markdown(index=False, floatfmt=".2f")
    return md

def main():
    print("Loading data...")
    data = load_data()

    print("\nGenerating summary tables...")
    scenario_summary = generate_scenario_summary(data['scenario_results'])
    regional_summary = generate_regional_summary(data['scenario_results'])
    tech_deployment = generate_technology_deployment(data['scenario_results'])

    # Save summary tables as CSV for reference
    scenario_summary.to_csv('outputs/report_scenario_summary.csv', index=False)
    regional_summary.to_csv('outputs/report_regional_summary.csv', index=False)
    tech_deployment.to_csv('outputs/report_tech_deployment.csv', index=False)
    print("Saved summary tables to outputs/")

    print("\nGenerating figures...")

    # Filter to one scenario for regional heatmap and tech timeline
    shaheen_h2 = data['scenario_results'][data['scenario_results']['scenario'] == 'shaheen_ncc_h2']

    # Generate all figures
    plot_emissions_trajectory(data['scenario_results'], f'{OUTPUT_DIR}/report_emissions_trajectory.png')
    plot_macc_curves(data['scenario_results'], f'{OUTPUT_DIR}/report_macc_curves.png')
    plot_regional_heatmap(shaheen_h2, f'{OUTPUT_DIR}/report_regional_heatmap.png')
    plot_technology_timeline(shaheen_h2, f'{OUTPUT_DIR}/report_tech_timeline.png')
    plot_h2_vs_elec_comparison(data['scenario_results'], f'{OUTPUT_DIR}/report_h2_vs_elec.png')
    plot_stranded_assets(data['stranded_assets'], f'{OUTPUT_DIR}/report_stranded_assets.png')
    plot_facility_scatter(data['scenario_results'], f'{OUTPUT_DIR}/report_facility_scatter.png')

    print("\n=== SUMMARY STATISTICS ===")
    print("\n--- 6-Scenario Summary (2050) ---")
    print(scenario_summary[['scenario', 'baseline_emissions_mt', 'final_emissions_mt',
                           'cumulative_capex_b', 'elec_demand_twh', 'h2_demand_mt']].to_string(index=False))

    print("\n--- Stranded Assets ---")
    print(data['stranded_assets'].to_string(index=False))

    print("\n--- Top 10 Emitters ---")
    print(data['emissions_by_company'].head(10).to_string(index=False))

    print("\nDone! All figures saved to outputs/figures/")

if __name__ == "__main__":
    main()
