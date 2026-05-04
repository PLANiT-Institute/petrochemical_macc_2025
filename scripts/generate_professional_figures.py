"""
Generate professional academic figures for the petrochemical decarbonization report.
Enhanced versions of stranded assets, MACC curves, and new figures.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as path_effects
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure, COLORS, SCENARIO_COLORS, COMPANY_COLORS

# Path configuration - works when run from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'

# Set up output directories
OUTPUT_DIR = str(OUTPUTS_DIR / 'figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)

apply_style()


def load_data():
    """Load all required data files"""
    data = {
        'scenario_results': pd.read_csv(OUTPUTS_DIR / 'scenario_results.csv'),
        'stranded_summary': pd.read_csv(OUTPUTS_DIR / 'stranded_assets_summary.csv'),
        'stranded_facilities': pd.read_csv(OUTPUTS_DIR / 'stranded_assets_facilities.csv'),
        'emissions_by_company': pd.read_csv(OUTPUTS_DIR / 'emissions_by_company_summary.csv'),
    }
    return data


def plot_stranded_assets_professional(data, output_path):
    """
    Generate professional 4-panel stranded assets figure.
    (A) Stranding year timeline
    (B) Stranded value comparison
    (C) Top 5 company exposure
    (D) Cumulative stranding over time
    """
    stranded_summary = data['stranded_summary']
    stranded_facilities = data['stranded_facilities']

    fig = plt.figure(figsize=(18, 14))

    # Panel layout
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

    # =========== Panel A: Stranding Year Timeline ===========
    ax1 = fig.add_subplot(gs[0, 0])

    scenarios = stranded_summary['scenario'].tolist()
    x = np.arange(len(scenarios))
    width = 0.35

    years_15c = stranded_summary['stranding_year_1.5C'].values
    years_20c = stranded_summary['stranding_year_2.0C'].values

    bars1 = ax1.bar(x - width/2, years_15c, width, label='1.5°C Pathway',
                    color='#E74C3C', edgecolor='white', linewidth=1)
    bars2 = ax1.bar(x + width/2, years_20c, width, label='2.0°C Pathway',
                    color='#3498DB', edgecolor='white', linewidth=1)

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_ylabel('Year of Carbon Budget Exhaustion', fontsize=12)
    ax1.set_title('(A) Stranding Year by Scenario and Climate Pathway', fontsize=13, fontweight='bold', pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.replace('_', '\n').replace('ncc', 'NCC').replace('h2', 'H2').replace('elec', 'Elec')
                         for s in scenarios], fontsize=8)
    ax1.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
    ax1.set_ylim(2025, 2055)
    ax1.axhline(y=2035, color='red', linestyle='--', alpha=0.5, linewidth=1.5, label='Net Zero 2035')
    ax1.axhline(y=2050, color='green', linestyle='--', alpha=0.5, linewidth=1.5, label='Net Zero 2050')
    ax1.grid(True, alpha=0.3, axis='y')

    # =========== Panel B: Stranded Value Comparison ===========
    ax2 = fig.add_subplot(gs[0, 1])

    values_15c = stranded_summary['stranded_value_1.5C_usd'].values / 1e9
    values_20c = stranded_summary['stranded_value_2.0C_usd'].values / 1e9

    # Sort by 1.5C value
    sort_idx = np.argsort(values_15c)[::-1]
    sorted_scenarios = [scenarios[i] for i in sort_idx]
    sorted_15c = values_15c[sort_idx]
    sorted_20c = values_20c[sort_idx]

    y_pos = np.arange(len(sorted_scenarios))

    bars1 = ax2.barh(y_pos + 0.2, sorted_15c, 0.35, label='1.5°C Pathway',
                     color='#E74C3C', edgecolor='white')
    bars2 = ax2.barh(y_pos - 0.2, sorted_20c, 0.35, label='2.0°C Pathway',
                     color='#3498DB', edgecolor='white')

    # Value labels
    for i, (v15, v20) in enumerate(zip(sorted_15c, sorted_20c)):
        ax2.text(v15 + 0.5, i + 0.2, f'${v15:.1f}B', va='center', fontsize=9, fontweight='bold')
        ax2.text(v20 + 0.5, i - 0.2, f'${v20:.1f}B', va='center', fontsize=9)

    ax2.set_xlabel('Stranded Asset Value (Billion USD)', fontsize=12)
    ax2.set_title('(B) Stranded Asset Value by Scenario', fontsize=13, fontweight='bold', pad=10)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([s.replace('_', '\n').replace('ncc', 'NCC') for s in sorted_scenarios], fontsize=8)
    ax2.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim(0, max(sorted_15c) * 1.3)

    # =========== Panel C: Top 5 Company Exposure ===========
    ax3 = fig.add_subplot(gs[1, 0])

    # Aggregate stranded facilities by company for 1.5C scenario
    company_stranded = stranded_facilities[
        (stranded_facilities['budget_scenario'] == '1.5C') &
        (stranded_facilities['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum().sort_values(ascending=False)

    top5_companies = company_stranded.head(5)
    others = company_stranded.iloc[5:].sum()

    # Add Others
    plot_data = pd.concat([top5_companies, pd.Series({'Others': others})])

    colors = [COMPANY_COLORS.get(c, '#7f7f7f') for c in plot_data.index]

    bars = ax3.barh(range(len(plot_data)), plot_data.values / 1e9, color=colors, edgecolor='white')

    for i, (bar, val) in enumerate(zip(bars, plot_data.values)):
        ax3.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f'${val/1e9:.2f}B', va='center', fontsize=9, fontweight='bold')

    ax3.set_xlabel('Stranded Asset Value (Billion USD)', fontsize=12)
    ax3.set_title('(C) Top 5 Companies Stranding Exposure (1.5°C, Shaheen H2)', fontsize=13, fontweight='bold', pad=10)
    ax3.set_yticks(range(len(plot_data)))
    ax3.set_yticklabels(plot_data.index, fontsize=10)
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.invert_yaxis()

    # =========== Panel D: Cumulative Stranding Timeline ===========
    ax4 = fig.add_subplot(gs[1, 1])

    # Calculate cumulative stranded value by year for key scenarios
    years = range(2025, 2051)

    for scenario in ['shaheen_ncc_h2', 'restructure_25pct_ncc_h2', 'restructure_40pct_ncc_h2']:
        scenario_data = stranded_facilities[
            (stranded_facilities['scenario'] == scenario) &
            (stranded_facilities['budget_scenario'] == '1.5C')
        ]

        cumulative = []
        for year in years:
            cum_val = scenario_data[scenario_data['stranding_year'] <= year]['stranded_value_usd'].sum()
            cumulative.append(cum_val / 1e9)

        label = scenario.replace('_ncc_h2', '').replace('_', ' ').title()
        ax4.plot(years, cumulative, linewidth=2.5, label=label,
                color=SCENARIO_COLORS[scenario], marker='o', markersize=4, markevery=5)

    ax4.fill_between(years, 0, cumulative, alpha=0.1, color=SCENARIO_COLORS['restructure_40pct_ncc_h2'])

    ax4.set_xlabel('Year', fontsize=12)
    ax4.set_ylabel('Cumulative Stranded Value (Billion USD)', fontsize=12)
    ax4.set_title('(D) Cumulative Stranding Under 1.5°C Pathway', fontsize=13, fontweight='bold', pad=10)
    ax4.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(2025, 2050)

    # Add reference line
    ax4.axvline(x=2035, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
    ax4.text(2035.5, ax4.get_ylim()[1] * 0.9, 'Net Zero\n2035', fontsize=9, color='red', alpha=0.7)

    plt.suptitle('Stranded Asset Analysis: Korea Petrochemical Industry',
                 fontsize=16, fontweight='bold', y=1.02)

    save_figure(fig, output_path)
    print(f"Saved: {output_path}")

    # CSV export: 4-panel stranded assets
    csv_rows = []
    # Panel A: stranding years
    for _, row in stranded_summary.iterrows():
        sc = row['scenario']
        csv_rows.append({'panel': 'A', 'category': sc, 'subcategory': '1.5C',
                         'value': row['stranding_year_1.5C'], 'unit': 'year'})
        csv_rows.append({'panel': 'A', 'category': sc, 'subcategory': '2.0C',
                         'value': row['stranding_year_2.0C'], 'unit': 'year'})
    # Panel B: stranded values
    for _, row in stranded_summary.iterrows():
        sc = row['scenario']
        csv_rows.append({'panel': 'B', 'category': sc, 'subcategory': '1.5C',
                         'value': row['stranded_value_1.5C_usd'] / 1e9, 'unit': 'billion_USD'})
        csv_rows.append({'panel': 'B', 'category': sc, 'subcategory': '2.0C',
                         'value': row['stranded_value_2.0C_usd'] / 1e9, 'unit': 'billion_USD'})
    # Panel C: top 5 companies
    company_stranded_csv = stranded_facilities[
        (stranded_facilities['budget_scenario'] == '1.5C') &
        (stranded_facilities['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum().sort_values(ascending=False)
    for comp, val in company_stranded_csv.head(5).items():
        csv_rows.append({'panel': 'C', 'category': comp, 'value': val / 1e9, 'unit': 'billion_USD'})
    others_val = company_stranded_csv.iloc[5:].sum() if len(company_stranded_csv) > 5 else 0
    csv_rows.append({'panel': 'C', 'category': 'Others', 'value': others_val / 1e9, 'unit': 'billion_USD'})
    # Panel D: cumulative stranding timeline
    for scenario in ['shaheen_ncc_h2', 'restructure_25pct_ncc_h2', 'restructure_40pct_ncc_h2']:
        s_data = stranded_facilities[
            (stranded_facilities['scenario'] == scenario) &
            (stranded_facilities['budget_scenario'] == '1.5C')
        ]
        for yr in range(2025, 2051):
            cum_val = s_data[s_data['stranding_year'] <= yr]['stranded_value_usd'].sum()
            csv_rows.append({'panel': 'D', 'year': yr, 'category': scenario,
                             'value': cum_val / 1e9, 'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(csv_rows), output_path, figure_type='multi_panel')


def plot_macc_curves_enhanced(data, output_path):
    """
    Generate publication-quality MACC curves with carbon price thresholds.
    """
    df = data['scenario_results']

    fig, axes = plt.subplots(2, 3, figsize=(20, 14))
    axes = axes.flatten()

    scenarios = sorted(df['scenario'].unique())

    # Carbon price reference lines
    carbon_prices = [50, 100, 200]
    price_colors = ['#27AE60', '#F39C12', '#E74C3C']

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]
        scenario_data = df[(df['scenario'] == scenario) & (df['year'] == 2050)]

        # Filter positive MAC and sort
        scenario_data = scenario_data[scenario_data['mac_usd_per_tco2'] > 0].sort_values('mac_usd_per_tco2')

        if len(scenario_data) > 0:
            cumulative_abatement = scenario_data['abatement_tco2'].cumsum() / 1e6
            mac = scenario_data['mac_usd_per_tco2']

            # Create step plot with gradient fill
            ax.fill_between(cumulative_abatement, 0, mac, step='post',
                           alpha=0.4, color=SCENARIO_COLORS[scenario])
            ax.step(cumulative_abatement, mac, where='post', linewidth=2.5,
                   color=SCENARIO_COLORS[scenario])

            # Add carbon price reference lines
            for price, color in zip(carbon_prices, price_colors):
                ax.axhline(y=price, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
                if idx == 0:  # Only label on first subplot
                    ax.text(cumulative_abatement.max() * 0.95, price + 10,
                           f'${price}/tCO₂', fontsize=9, color=color, ha='right', fontweight='bold')

            # Calculate and display summary statistics
            total_abatement = cumulative_abatement.max()
            avg_mac = (scenario_data['mac_usd_per_tco2'] * scenario_data['abatement_tco2']).sum() / \
                      scenario_data['abatement_tco2'].sum()

            # Stats box
            stats_text = f'Total: {total_abatement:.1f} Mt CO₂\nAvg MAC: ${avg_mac:.0f}/t'
            props = dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='gray')
            ax.text(0.97, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', horizontalalignment='right', bbox=props)

        # Format title
        title = scenario.replace('_', ' ').replace('ncc', 'NCC').replace('h2', 'H2').replace('elec', 'Elec')
        ax.set_title(title.title(), fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Cumulative Abatement (Mt CO₂)', fontsize=11)
        ax.set_ylabel('MAC ($/tCO₂)', fontsize=11)
        ax.set_ylim(0, 500)
        ax.set_xlim(0, None)
        ax.grid(True, alpha=0.3)

        # Add zero line
        ax.axhline(y=0, color='black', linewidth=0.5)

    # Overall title
    plt.suptitle('Marginal Abatement Cost Curves by Scenario (2050)\nwith Carbon Price Reference Lines',
                 fontsize=16, fontweight='bold', y=1.02)

    # Add legend for carbon prices
    legend_elements = [plt.Line2D([0], [0], color=c, linestyle='--', linewidth=2, label=f'${p}/tCO₂')
                      for p, c in zip(carbon_prices, price_colors)]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
               bbox_to_anchor=(0.5, -0.02), fontsize=11, frameon=True, fancybox=True)

    save_figure(fig, output_path)
    print(f"Saved: {output_path}")

    # CSV export: MACC curves enhanced
    macc_rows = []
    for scenario in sorted(df['scenario'].unique()):
        scenario_data = df[(df['scenario'] == scenario) & (df['year'] == 2050)]
        scenario_data = scenario_data[scenario_data['mac_usd_per_tco2'] > 0].sort_values('mac_usd_per_tco2')
        if len(scenario_data) > 0:
            cum_abatement = scenario_data['abatement_tco2'].cumsum() / 1e6
            for ca, mac in zip(cum_abatement, scenario_data['mac_usd_per_tco2']):
                macc_rows.append({'category': scenario,
                                  'value': mac,
                                  'subcategory': f'{ca:.3f}',
                                  'unit': 'USD_per_tCO2'})
    save_figure_data(pd.DataFrame(macc_rows), output_path, figure_type='macc_step')


def plot_top5_companies(data, output_path):
    """
    Generate comprehensive Top 5 Companies analysis figure (6 panels).
    """
    df = data['scenario_results']
    emissions_df = data['emissions_by_company']
    stranded_fac = data['stranded_facilities']

    # Get top 5 companies
    top5 = emissions_df.head(5)['company'].tolist()

    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.25)

    # =========== Panel A: Baseline Emissions ===========
    ax1 = fig.add_subplot(gs[0, 0])

    emissions_plot = emissions_df.head(10).copy()
    emissions_plot['emissions_mt'] = emissions_plot['Total_Emission_tCO2'] / 1e6

    colors = [COMPANY_COLORS.get(c, '#7f7f7f') for c in emissions_plot['company']]
    bars = ax1.barh(range(len(emissions_plot)), emissions_plot['emissions_mt'], color=colors, edgecolor='white')

    for i, bar in enumerate(bars):
        val = emissions_plot.iloc[i]['emissions_mt']
        pct = val / emissions_plot['emissions_mt'].sum() * 100
        ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f'{val:.1f} Mt ({pct:.1f}%)', va='center', fontsize=9)

    ax1.set_xlabel('Baseline Emissions (Mt CO₂)', fontsize=11)
    ax1.set_title('(A) Top 10 Companies by Baseline Emissions', fontsize=13, fontweight='bold', pad=10)
    ax1.set_yticks(range(len(emissions_plot)))
    ax1.set_yticklabels(emissions_plot['company'], fontsize=10)
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3, axis='x')

    # =========== Panel B: Stranding Risk Comparison ===========
    ax2 = fig.add_subplot(gs[0, 1])

    # Calculate company stranding for both pathways
    stranding_15c = stranded_fac[
        (stranded_fac['budget_scenario'] == '1.5C') &
        (stranded_fac['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum() / 1e9

    stranding_20c = stranded_fac[
        (stranded_fac['budget_scenario'] == '2.0C') &
        (stranded_fac['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum() / 1e9

    top5_stranding = pd.DataFrame({
        '1.5°C': stranding_15c.reindex(top5).fillna(0),
        '2.0°C': stranding_20c.reindex(top5).fillna(0)
    })

    x = np.arange(len(top5))
    width = 0.35

    bars1 = ax2.bar(x - width/2, top5_stranding['1.5°C'], width, label='1.5°C', color='#E74C3C', edgecolor='white')
    bars2 = ax2.bar(x + width/2, top5_stranding['2.0°C'], width, label='2.0°C', color='#3498DB', edgecolor='white')

    ax2.set_ylabel('Stranded Value (Billion USD)', fontsize=11)
    ax2.set_title('(B) Stranding Risk by Company (Shaheen H2)', fontsize=13, fontweight='bold', pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(top5, fontsize=9, rotation=15, ha='right')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, alpha=0.3, axis='y')

    # =========== Panel C: Company MACC Curves ===========
    ax3 = fig.add_subplot(gs[1, :])

    scenario = 'shaheen_ncc_h2'
    scenario_data = df[(df['scenario'] == scenario) & (df['year'] == 2050)]

    for company in top5:
        company_data = scenario_data[scenario_data['company'] == company]
        company_data = company_data[company_data['mac_usd_per_tco2'] > 0].sort_values('mac_usd_per_tco2')

        if len(company_data) > 0:
            cumulative_abatement = company_data['abatement_tco2'].cumsum() / 1e6
            mac = company_data['mac_usd_per_tco2']

            ax3.step(cumulative_abatement, mac, where='post', linewidth=2.5,
                    label=company, color=COMPANY_COLORS[company])
            ax3.fill_between(cumulative_abatement, 0, mac, step='post', alpha=0.15,
                            color=COMPANY_COLORS[company])

    # Add carbon price reference
    ax3.axhline(y=100, color='gray', linestyle='--', alpha=0.7, linewidth=1.5)
    ax3.text(ax3.get_xlim()[1] * 0.95, 110, '$100/tCO₂', fontsize=10, color='gray', ha='right')

    ax3.set_xlabel('Cumulative Abatement (Mt CO₂)', fontsize=11)
    ax3.set_ylabel('MAC ($/tCO₂)', fontsize=11)
    ax3.set_title('(C) Company-Level MACC Curves (2050, Shaheen H2)', fontsize=13, fontweight='bold', pad=10)
    ax3.legend(loc='upper left', frameon=True, fancybox=True, ncol=2)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 400)

    # =========== Panel D: Transition Cost ===========
    ax4 = fig.add_subplot(gs[2, 0])

    # Calculate cumulative CAPEX by company
    company_capex = df[df['company'].isin(top5)].groupby('company')['capex_usd'].sum() / 1e9
    company_capex = company_capex.reindex(top5)

    colors = [COMPANY_COLORS[c] for c in top5]
    bars = ax4.bar(range(len(top5)), company_capex.values, color=colors, edgecolor='white')

    for i, bar in enumerate(bars):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${company_capex.values[i]:.1f}B', ha='center', fontsize=9, fontweight='bold')

    ax4.set_ylabel('Cumulative CAPEX (Billion USD)', fontsize=11)
    ax4.set_title('(D) Transition Investment by Company', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xticks(range(len(top5)))
    ax4.set_xticklabels(top5, fontsize=9, rotation=15, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')

    # =========== Panel E: Technology Mix ===========
    ax5 = fig.add_subplot(gs[2, 1])

    # Get 2050 technology deployment by company
    deployed_2050 = df[(df['year'] == 2050) & (df['tech_deployed'] == 1) & (df['company'].isin(top5))]
    tech_mix = deployed_2050.groupby(['company', 'technology']).size().unstack(fill_value=0)
    tech_mix = tech_mix.reindex(top5)

    if len(tech_mix.columns) > 0:
        tech_mix.plot(kind='bar', stacked=True, ax=ax5, colormap='Set2', edgecolor='white', width=0.7)
        ax5.set_ylabel('Number of Facilities', fontsize=11)
        ax5.set_title('(E) Technology Mix by Company (2050)', fontsize=13, fontweight='bold', pad=10)
        ax5.set_xticklabels(top5, fontsize=9, rotation=15, ha='right')
        ax5.legend(title='Technology', loc='upper right', fontsize=9)
        ax5.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Top 5 Companies Analysis: Korea Petrochemical Industry',
                 fontsize=16, fontweight='bold', y=1.01)

    save_figure(fig, output_path)
    print(f"Saved: {output_path}")

    # CSV export: top 5 companies multi-panel
    t5_rows = []
    # Panel A: baseline emissions
    emissions_top10 = emissions_df.head(10)
    for _, row in emissions_top10.iterrows():
        t5_rows.append({'panel': 'A', 'category': row['company'],
                        'value': row['Total_Emission_tCO2'] / 1e6, 'unit': 'MtCO2'})
    # Panel B: stranding risk
    stranding_15c = stranded_fac[
        (stranded_fac['budget_scenario'] == '1.5C') &
        (stranded_fac['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum() / 1e9
    stranding_20c = stranded_fac[
        (stranded_fac['budget_scenario'] == '2.0C') &
        (stranded_fac['scenario'] == 'shaheen_ncc_h2')
    ].groupby('company')['stranded_value_usd'].sum() / 1e9
    for comp in top5:
        t5_rows.append({'panel': 'B', 'category': comp, 'subcategory': '1.5C',
                        'value': stranding_15c.get(comp, 0), 'unit': 'billion_USD'})
        t5_rows.append({'panel': 'B', 'category': comp, 'subcategory': '2.0C',
                        'value': stranding_20c.get(comp, 0), 'unit': 'billion_USD'})
    # Panel C: company MACC (step data)
    scenario = 'shaheen_ncc_h2'
    scenario_data = df[(df['scenario'] == scenario) & (df['year'] == 2050)]
    for company in top5:
        cd = scenario_data[scenario_data['company'] == company]
        cd = cd[cd['mac_usd_per_tco2'] > 0].sort_values('mac_usd_per_tco2')
        if len(cd) > 0:
            cum_a = cd['abatement_tco2'].cumsum() / 1e6
            for ca, mac in zip(cum_a, cd['mac_usd_per_tco2']):
                t5_rows.append({'panel': 'C', 'category': company,
                                'value': mac, 'unit': 'USD_per_tCO2'})
    # Panel D: transition CAPEX
    company_capex = df[df['company'].isin(top5)].groupby('company')['capex_usd'].sum() / 1e9
    for comp in top5:
        t5_rows.append({'panel': 'D', 'category': comp,
                        'value': company_capex.get(comp, 0), 'unit': 'billion_USD'})
    # Panel E: technology mix
    deployed_2050 = df[(df['year'] == 2050) & (df['tech_deployed'] == 1) & (df['company'].isin(top5))]
    tech_mix = deployed_2050.groupby(['company', 'technology']).size().reset_index(name='value')
    for _, row in tech_mix.iterrows():
        t5_rows.append({'panel': 'E', 'category': row['company'],
                        'subcategory': row['technology'], 'value': row['value'],
                        'unit': 'facility_count'})
    save_figure_data(pd.DataFrame(t5_rows), output_path, figure_type='multi_panel')


def plot_data_architecture(output_path):
    """
    Generate technical data architecture flowchart.
    """
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Colors
    input_color = '#3498DB'
    module_color = '#27AE60'
    engine_color = '#F39C12'
    output_color = '#9B59B6'

    # =========== INPUT LAYER ===========
    # Title
    ax.text(50, 97, 'DATA ARCHITECTURE: Petrochemical MACC Model',
            ha='center', va='center', fontsize=18, fontweight='bold')

    # Input boxes
    input_boxes = [
        (10, 82, 'data/assets/\n\nfacility_database.csv\nregion_mapping.csv\n(237 facilities)', 'ASSETS'),
        (32, 82, 'data/assumptions/\n\ntechnology_parameters.csv\nproduct_benchmarks.csv\nemission_factors.csv', 'ASSUMPTIONS'),
        (54, 82, 'data/scenarios/\n\nscenario_definitions.csv\nemission_targets.csv\ndemand_trajectory.csv', 'SCENARIOS'),
        (76, 82, 'data/assumptions/prices/\n\nh2_price_trajectory.csv\nre_price_trajectory.csv\ngrid_price_trajectory.csv', 'PRICES'),
    ]

    for x, y, text, title in input_boxes:
        rect = FancyBboxPatch((x-9, y-12), 18, 20, boxstyle="round,pad=0.02",
                              facecolor=input_color, alpha=0.3, edgecolor=input_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y+6, title, ha='center', va='center', fontsize=11, fontweight='bold', color=input_color)
        ax.text(x, y-3, text, ha='center', va='center', fontsize=8, family='monospace')

    # INPUT LAYER label
    ax.add_patch(FancyBboxPatch((2, 68), 96, 28, boxstyle="round,pad=0.01",
                                facecolor='none', edgecolor=input_color, linewidth=2, linestyle='--'))
    ax.text(50, 95, 'INPUT DATA LAYER', ha='center', va='center', fontsize=12,
            fontweight='bold', color=input_color, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # =========== CALCULATION MODULES ===========
    module_boxes = [
        (15, 52, 'DataLoader\n\nmerge(facility,\nbenchmark)\non (product, process)', 'modules/utils.py'),
        (37, 52, 'EmissionCalculator\n\nE = Σ(fuel_gj × EF)\n+ elec × grid_ef', ''),
        (59, 52, 'TechCostCalculator\n\nCAPEX(year) =\ninterp(2025→2050)', ''),
        (81, 52, 'StrandedAssetCalc\n\nV = Σ(asset_value\n× (1 - age/life))', ''),
    ]

    for x, y, text, subtitle in module_boxes:
        rect = FancyBboxPatch((x-10, y-10), 20, 18, boxstyle="round,pad=0.02",
                              facecolor=module_color, alpha=0.3, edgecolor=module_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=8, family='monospace')

    # MODULE LAYER label
    ax.add_patch(FancyBboxPatch((2, 40), 96, 26, boxstyle="round,pad=0.01",
                                facecolor='none', edgecolor=module_color, linewidth=2, linestyle='--'))
    ax.text(50, 64, 'CALCULATION MODULES (modules/utils.py)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=module_color,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # =========== OPTIMIZATION ENGINE ===========
    engine_y = 26
    engine_boxes = [
        (18, engine_y, 'For year t:\ncalc BAU\nemissions'),
        (38, engine_y, 'gap = Σ(E_i)\n- target_t'),
        (58, engine_y, 'candidates =\nsort_by(LCOA)'),
        (78, engine_y, 'while gap > 0:\n  deploy()'),
    ]

    for i, (x, y, text) in enumerate(engine_boxes):
        rect = FancyBboxPatch((x-8, y-6), 16, 12, boxstyle="round,pad=0.02",
                              facecolor=engine_color, alpha=0.3, edgecolor=engine_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=9, family='monospace')

        # Add arrows between boxes
        if i < len(engine_boxes) - 1:
            ax.annotate('', xy=(engine_boxes[i+1][0]-8, engine_y), xytext=(x+8, engine_y),
                       arrowprops=dict(arrowstyle='->', color=engine_color, lw=2))

    # ENGINE LAYER label
    ax.add_patch(FancyBboxPatch((2, 17), 96, 20, boxstyle="round,pad=0.01",
                                facecolor='none', edgecolor=engine_color, linewidth=2, linestyle='--'))
    ax.text(50, 35, 'OPTIMIZATION ENGINE (run_scenarios.py)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=engine_color,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # =========== OUTPUT LAYER ===========
    output_boxes = [
        (20, 6, 'outputs/\nscenario_results.csv\n(6×26×237 rows, 8.6MB)'),
        (45, 6, 'outputs/\nregional_mac_summary.csv\nemissions_by_company.csv'),
        (70, 6, 'outputs/\nstranded_assets_summary.csv\nstranded_assets_facilities.csv'),
    ]

    for x, y, text in output_boxes:
        rect = FancyBboxPatch((x-12, y-5), 24, 10, boxstyle="round,pad=0.02",
                              facecolor=output_color, alpha=0.3, edgecolor=output_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=8, family='monospace')

    # OUTPUT LAYER label
    ax.add_patch(FancyBboxPatch((2, -1), 96, 16, boxstyle="round,pad=0.01",
                                facecolor='none', edgecolor=output_color, linewidth=2, linestyle='--'))
    ax.text(50, 13, 'OUTPUT RESULTS', ha='center', va='center',
            fontsize=12, fontweight='bold', color=output_color,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # =========== VERTICAL ARROWS ===========
    # Input to Modules
    for x in [10, 32, 54, 76]:
        ax.annotate('', xy=(x, 66), xytext=(x, 70),
                   arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

    # Modules to Engine
    ax.annotate('', xy=(50, 37), xytext=(50, 42),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Engine to Output
    ax.annotate('', xy=(50, 15), xytext=(50, 20),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=input_color, alpha=0.3, edgecolor=input_color, label='Input Data'),
        mpatches.Patch(facecolor=module_color, alpha=0.3, edgecolor=module_color, label='Calculation Modules'),
        mpatches.Patch(facecolor=engine_color, alpha=0.3, edgecolor=engine_color, label='Optimization Engine'),
        mpatches.Patch(facecolor=output_color, alpha=0.3, edgecolor=output_color, label='Output Results'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10, frameon=True)

    save_figure(fig, output_path)
    print(f"Saved: {output_path}")

    # CSV export: data architecture metadata (structured description of model components)
    arch_rows = [
        # Input layer
        {'layer': 'INPUT', 'component': 'assets', 'description': 'facility_database.csv, region_mapping.csv',
         'detail': '237 facilities', 'unit': 'files'},
        {'layer': 'INPUT', 'component': 'assumptions', 'description': 'technology_parameters.csv, product_benchmarks.csv, emission_factors.csv',
         'detail': 'model parameters', 'unit': 'files'},
        {'layer': 'INPUT', 'component': 'scenarios', 'description': 'scenario_definitions.csv, emission_targets.csv, demand_trajectory.csv',
         'detail': 'scenario configs', 'unit': 'files'},
        {'layer': 'INPUT', 'component': 'prices', 'description': 'h2_price_trajectory.csv, re_price_trajectory.csv, grid_price_trajectory.csv',
         'detail': 'price trajectories', 'unit': 'files'},
        # Module layer
        {'layer': 'MODULE', 'component': 'DataLoader', 'description': 'merge(facility, benchmark) on (product, process)',
         'detail': 'modules/utils.py', 'unit': 'function'},
        {'layer': 'MODULE', 'component': 'EmissionCalculator', 'description': 'E = sum(fuel_gj * EF) + elec * grid_ef',
         'detail': 'modules/utils.py', 'unit': 'function'},
        {'layer': 'MODULE', 'component': 'TechCostCalculator', 'description': 'CAPEX(year) = interp(2025->2050)',
         'detail': 'modules/utils.py', 'unit': 'function'},
        {'layer': 'MODULE', 'component': 'StrandedAssetCalc', 'description': 'V = sum(asset_value * (1 - age/life))',
         'detail': 'modules/utils.py', 'unit': 'function'},
        # Engine layer
        {'layer': 'ENGINE', 'component': 'step1', 'description': 'For year t: calc BAU emissions',
         'detail': 'run_scenarios.py', 'unit': 'step'},
        {'layer': 'ENGINE', 'component': 'step2', 'description': 'gap = sum(E_i) - target_t',
         'detail': 'run_scenarios.py', 'unit': 'step'},
        {'layer': 'ENGINE', 'component': 'step3', 'description': 'candidates = sort_by(LCOA)',
         'detail': 'run_scenarios.py', 'unit': 'step'},
        {'layer': 'ENGINE', 'component': 'step4', 'description': 'while gap > 0: deploy()',
         'detail': 'run_scenarios.py', 'unit': 'step'},
        # Output layer
        {'layer': 'OUTPUT', 'component': 'scenario_results', 'description': 'scenario_results.csv (6x26x237 rows)',
         'detail': '8.6MB', 'unit': 'file'},
        {'layer': 'OUTPUT', 'component': 'summaries', 'description': 'regional_mac_summary.csv, emissions_by_company.csv',
         'detail': 'aggregated', 'unit': 'files'},
        {'layer': 'OUTPUT', 'component': 'stranded_assets', 'description': 'stranded_assets_summary.csv, stranded_assets_facilities.csv',
         'detail': 'risk analysis', 'unit': 'files'},
    ]
    save_figure_data(pd.DataFrame(arch_rows), output_path, figure_type='architecture_diagram')


def main():
    print("Loading data...")
    data = load_data()

    print("\nGenerating professional figures...")

    # Generate all enhanced figures
    plot_stranded_assets_professional(data, f'{OUTPUT_DIR}/report_stranded_assets_v2.png')
    plot_macc_curves_enhanced(data, f'{OUTPUT_DIR}/report_macc_curves_v2.png')
    plot_top5_companies(data, f'{OUTPUT_DIR}/report_top5_companies.png')
    plot_data_architecture(f'{OUTPUT_DIR}/report_data_architecture.png')

    print("\nDone! All professional figures saved to outputs/figures/")


if __name__ == "__main__":
    main()
