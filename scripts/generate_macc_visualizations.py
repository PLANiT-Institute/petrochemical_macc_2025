#!/usr/bin/env python3
"""
MACC Visualization Figures Generator

Creates visualization figures for Korea Petrochemical decarbonization project (2025-2050):
- Production share by product (4 figures)
- Emission pathways (3 figures)
- Transition costs (3 figures)
- Stranded assets (3 figures)

Total: 13 figures
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure, TECH_COLORS, SCENARIO_NAMES, SCENARIO_COLORS, TECH_ORDER

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "outputs"
OUTPUT_DIR = DATA_DIR / "figures"

# Data files
SCENARIO_RESULTS_FILE = DATA_DIR / "scenario_results.csv"
STRANDED_SUMMARY_FILE = DATA_DIR / "stranded_assets_summary.csv"
STRANDED_FACILITIES_FILE = DATA_DIR / "stranded_assets_facilities.csv"

# BTX products
BTX_PRODUCTS = ['Benzene', 'Toluene', 'Xylene']

# Major products for analysis
MAJOR_PRODUCTS = ['Ethylene', 'Propylene', 'BTX']

# Years
YEAR_RANGE = range(2025, 2051)

apply_style()

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_scenario_results():
    """Load the main scenario results data."""
    df = pd.read_csv(SCENARIO_RESULTS_FILE)
    df['technology'] = df['technology'].fillna('Unknown')
    return df


def load_stranded_summary():
    """Load stranded assets summary."""
    return pd.read_csv(STRANDED_SUMMARY_FILE)


def load_stranded_facilities():
    """Load stranded assets by facility."""
    return pd.read_csv(STRANDED_FACILITIES_FILE)


def prepare_btx_data(df):
    """Add BTX as a combined product category."""
    df = df.copy()
    df['product_group'] = df['product'].apply(
        lambda x: 'BTX' if x in BTX_PRODUCTS else x
    )
    return df


# ============================================================================
# PRODUCTION SHARE PLOTTING FUNCTIONS
# ============================================================================

def plot_production_share_single(df, product, ax, title=None):
    """
    Plot 100% stacked area chart for technology share of a single product.
    Shows average across all scenarios.
    """
    if product == 'BTX':
        product_df = df[df['product'].isin(BTX_PRODUCTS)]
    else:
        product_df = df[df['product'] == product]

    # Aggregate by year and technology across all scenarios
    agg = product_df.groupby(['year', 'technology'])['production_t'].sum().reset_index()

    # Pivot to get technologies as columns
    pivot = agg.pivot(index='year', columns='technology', values='production_t').fillna(0)

    # Reorder columns
    cols = [c for c in TECH_ORDER if c in pivot.columns]
    pivot = pivot[cols]

    # Calculate percentages
    total = pivot.sum(axis=1)
    pct = pivot.div(total, axis=0) * 100

    # Plot stacked area
    colors = [TECH_COLORS.get(c, '#cccccc') for c in pct.columns]
    ax.stackplot(pct.index, pct.T.values, labels=pct.columns, colors=colors, alpha=0.85)

    ax.set_xlim(2025, 2050)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Year')
    ax.set_ylabel('Production Share (%)')
    ax.set_title(title or f'{product} Production by Technology')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    return ax


def _production_share_tidy(df, product):
    """Build tidy DataFrame for a production share chart."""
    if product == 'BTX':
        product_df = df[df['product'].isin(BTX_PRODUCTS)]
    else:
        product_df = df[df['product'] == product]
    agg = product_df.groupby(['year', 'technology'])['production_t'].sum().reset_index()
    pivot = agg.pivot(index='year', columns='technology', values='production_t').fillna(0)
    cols = [c for c in TECH_ORDER if c in pivot.columns]
    pivot = pivot[cols]
    total = pivot.sum(axis=1)
    pct = pivot.div(total, axis=0) * 100
    tidy = pct.reset_index().melt(id_vars='year', var_name='category', value_name='value')
    tidy['unit'] = 'pct'
    return tidy


def generate_production_share_figures(df):
    """Generate all production share figures."""
    print("Generating production share figures...")

    # 1a. Ethylene
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_production_share_single(df, 'Ethylene', ax, 'Ethylene Production Share by Technology (2025-2050)')
    fig_path = OUTPUT_DIR / 'production_share_ethylene.png'
    save_figure(fig, fig_path)
    save_figure_data(_production_share_tidy(df, 'Ethylene'), fig_path, figure_type='stacked_area_pct')
    print("  - production_share_ethylene.png")

    # 1b. Propylene
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_production_share_single(df, 'Propylene', ax, 'Propylene Production Share by Technology (2025-2050)')
    fig_path = OUTPUT_DIR / 'production_share_propylene.png'
    save_figure(fig, fig_path)
    save_figure_data(_production_share_tidy(df, 'Propylene'), fig_path, figure_type='stacked_area_pct')
    print("  - production_share_propylene.png")

    # 1c. BTX
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_production_share_single(df, 'BTX', ax, 'BTX Production Share by Technology (2025-2050)')
    fig_path = OUTPUT_DIR / 'production_share_btx.png'
    save_figure(fig, fig_path)
    save_figure_data(_production_share_tidy(df, 'BTX'), fig_path, figure_type='stacked_area_pct')
    print("  - production_share_btx.png")

    # 1d. Overview (2x2 grid)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    plot_production_share_single(df, 'Ethylene', axes[0, 0], 'Ethylene')
    plot_production_share_single(df, 'Propylene', axes[0, 1], 'Propylene')
    plot_production_share_single(df, 'BTX', axes[1, 0], 'BTX (Benzene, Toluene, Xylene)')
    plot_production_share_single(df, 'Butadiene', axes[1, 1], 'Butadiene')

    fig.suptitle('Production Share by Technology (2025-2050)', fontsize=14, fontweight='bold')
    fig_path = OUTPUT_DIR / 'production_share_overview.png'
    save_figure(fig, fig_path)
    # Combine all 4 products with a panel column
    overview_parts = []
    for product, panel in [('Ethylene', 'A'), ('Propylene', 'B'), ('BTX', 'C'), ('Butadiene', 'D')]:
        part = _production_share_tidy(df, product)
        part['panel'] = panel
        overview_parts.append(part)
    save_figure_data(pd.concat(overview_parts, ignore_index=True), fig_path, figure_type='stacked_area_pct')
    print("  - production_share_overview.png")


# ============================================================================
# EMISSION PATHWAY PLOTTING FUNCTIONS
# ============================================================================

def plot_emission_by_technology(df, ax):
    """Plot stacked area of emissions by technology (average across scenarios)."""
    # Aggregate by year and technology
    agg = df.groupby(['year', 'technology'])['emissions_tco2'].sum().reset_index()

    # Pivot
    pivot = agg.pivot(index='year', columns='technology', values='emissions_tco2').fillna(0)

    # Convert to million tonnes
    pivot = pivot / 1e6

    # Reorder columns
    cols = [c for c in TECH_ORDER if c in pivot.columns]
    pivot = pivot[cols]

    # Plot
    colors = [TECH_COLORS.get(c, '#cccccc') for c in pivot.columns]
    ax.stackplot(pivot.index, pivot.T.values, labels=pivot.columns, colors=colors, alpha=0.85)

    ax.set_xlim(2025, 2050)
    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (Million tCO₂)')
    ax.legend(loc='upper right', framealpha=0.9)

    return ax


def plot_emission_by_product(df, ax):
    """Plot stacked area of emissions by product category."""
    # Define product categories
    df = df.copy()
    df['product_cat'] = df['product'].apply(lambda x:
        'BTX' if x in BTX_PRODUCTS else
        'Ethylene' if x == 'Ethylene' else
        'Propylene' if x == 'Propylene' else
        'Butadiene' if x == 'Butadiene' else
        'Downstream'
    )

    # Aggregate by year and product category
    agg = df.groupby(['year', 'product_cat'])['emissions_tco2'].sum().reset_index()

    # Pivot
    pivot = agg.pivot(index='year', columns='product_cat', values='emissions_tco2').fillna(0)

    # Convert to million tonnes
    pivot = pivot / 1e6

    # Order
    order = ['Ethylene', 'Propylene', 'BTX', 'Butadiene', 'Downstream']
    cols = [c for c in order if c in pivot.columns]
    pivot = pivot[cols]

    # Colors for products
    product_colors = {
        'Ethylene': '#2E86AB',
        'Propylene': '#A23B72',
        'BTX': '#F18F01',
        'Butadiene': '#C73E1D',
        'Downstream': '#808080'
    }
    colors = [product_colors.get(c, '#cccccc') for c in pivot.columns]

    ax.stackplot(pivot.index, pivot.T.values, labels=pivot.columns, colors=colors, alpha=0.85)

    ax.set_xlim(2025, 2050)
    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (Million tCO₂)')
    ax.legend(loc='upper right', framealpha=0.9)

    return ax


def plot_emission_scenario_comparison(df, ax):
    """Plot line comparison of emissions across scenarios."""
    # Aggregate by year and scenario
    agg = df.groupby(['year', 'scenario'])['emissions_tco2'].sum().reset_index()

    # Convert to million tonnes
    agg['emissions_mt'] = agg['emissions_tco2'] / 1e6

    for scenario in SCENARIO_NAMES.keys():
        scenario_data = agg[agg['scenario'] == scenario]
        ax.plot(
            scenario_data['year'],
            scenario_data['emissions_mt'],
            label=SCENARIO_NAMES[scenario],
            color=SCENARIO_COLORS[scenario],
            linewidth=2,
            marker='o',
            markersize=3
        )

    ax.set_xlim(2025, 2050)
    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (Million tCO₂)')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)

    return ax


def generate_emission_pathway_figures(df):
    """Generate all emission pathway figures."""
    print("Generating emission pathway figures...")

    # 2a. By technology
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_emission_by_technology(df, ax)
    ax.set_title('CO\u2082 Emissions by Technology (2025-2050)', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'emission_path_by_technology.png'
    save_figure(fig, fig_path)
    # CSV: emissions by technology
    agg = df.groupby(['year', 'technology'])['emissions_tco2'].sum().reset_index()
    agg['emissions_tco2'] = agg['emissions_tco2'] / 1e6
    tidy = agg.rename(columns={'technology': 'category', 'emissions_tco2': 'value'})
    tidy['unit'] = 'MtCO2_per_yr'
    save_figure_data(tidy, fig_path, figure_type='stacked_area')
    print("  - emission_path_by_technology.png")

    # 2b. By product
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_emission_by_product(df, ax)
    ax.set_title('CO\u2082 Emissions by Product Category (2025-2050)', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'emission_path_by_product.png'
    save_figure(fig, fig_path)
    # CSV: emissions by product
    df_p = df.copy()
    df_p['product_cat'] = df_p['product'].apply(lambda x:
        'BTX' if x in BTX_PRODUCTS else
        'Ethylene' if x == 'Ethylene' else
        'Propylene' if x == 'Propylene' else
        'Butadiene' if x == 'Butadiene' else
        'Downstream'
    )
    agg_p = df_p.groupby(['year', 'product_cat'])['emissions_tco2'].sum().reset_index()
    agg_p['emissions_tco2'] = agg_p['emissions_tco2'] / 1e6
    tidy_p = agg_p.rename(columns={'product_cat': 'category', 'emissions_tco2': 'value'})
    tidy_p['unit'] = 'MtCO2_per_yr'
    save_figure_data(tidy_p, fig_path, figure_type='stacked_area')
    print("  - emission_path_by_product.png")

    # 2c. Scenario comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_emission_scenario_comparison(df, ax)
    ax.set_title('CO\u2082 Emission Pathway Comparison by Scenario (2025-2050)', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'emission_path_scenario_comparison.png'
    save_figure(fig, fig_path)
    # CSV: scenario comparison
    agg_s = df.groupby(['year', 'scenario'])['emissions_tco2'].sum().reset_index()
    agg_s['emissions_tco2'] = agg_s['emissions_tco2'] / 1e6
    tidy_s = agg_s.rename(columns={'scenario': 'category', 'emissions_tco2': 'value'})
    tidy_s['unit'] = 'MtCO2_per_yr'
    save_figure_data(tidy_s, fig_path, figure_type='line')
    print("  - emission_path_scenario_comparison.png")


# ============================================================================
# COST VISUALIZATION FUNCTIONS
# ============================================================================

def plot_cumulative_capex(df, ax):
    """Plot cumulative CAPEX investment over time by scenario."""
    # Aggregate by year and scenario
    agg = df.groupby(['year', 'scenario'])['capex_usd'].sum().reset_index()

    for scenario in SCENARIO_NAMES.keys():
        scenario_data = agg[agg['scenario'] == scenario].sort_values('year')
        scenario_data['cumulative_capex'] = scenario_data['capex_usd'].cumsum()

        # Convert to billions
        scenario_data['cumulative_capex_b'] = scenario_data['cumulative_capex'] / 1e9

        ax.plot(
            scenario_data['year'],
            scenario_data['cumulative_capex_b'],
            label=SCENARIO_NAMES[scenario],
            color=SCENARIO_COLORS[scenario],
            linewidth=2,
            marker='o',
            markersize=3
        )

    ax.set_xlim(2025, 2050)
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative CAPEX (Billion USD)')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)

    return ax


def plot_annual_cost_breakdown(df, ax):
    """Plot stacked bar chart of annual cost breakdown (average across scenarios)."""
    # Cost components
    cost_cols = {
        'cost_component_capex_annual_usd': 'Annualized CAPEX',
        'cost_component_opex_annual_usd': 'OPEX',
        'cost_component_new_energy_usd': 'New Energy',
        'cost_component_fuel_savings_usd': 'Fuel Savings (Negative)',
    }

    # Aggregate by year (average across scenarios)
    agg_data = {}
    for col, label in cost_cols.items():
        yearly = df.groupby('year')[col].sum() / len(df['scenario'].unique())
        agg_data[label] = yearly / 1e9  # Convert to billions

    agg_df = pd.DataFrame(agg_data)

    # For savings, make it negative
    agg_df['Fuel Savings (Negative)'] = -agg_df['Fuel Savings (Negative)']

    # Colors
    cost_colors = {
        'Annualized CAPEX': '#2E86AB',
        'OPEX': '#A23B72',
        'New Energy': '#F18F01',
        'Fuel Savings (Negative)': '#27AE60'
    }

    # Plot positive costs as stacked bars
    positive_cols = ['Annualized CAPEX', 'OPEX', 'New Energy']
    bottom = np.zeros(len(agg_df))

    years = agg_df.index.values
    width = 0.8

    for col in positive_cols:
        values = agg_df[col].values
        ax.bar(years, values, width, bottom=bottom, label=col, color=cost_colors[col], alpha=0.85)
        bottom += values

    # Plot savings as negative bars
    savings = agg_df['Fuel Savings (Negative)'].values
    ax.bar(years, savings, width, label='Fuel Savings', color=cost_colors['Fuel Savings (Negative)'], alpha=0.85)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlim(2024, 2051)
    ax.set_xlabel('Year')
    ax.set_ylabel('Annual Cost (Billion USD)')
    ax.legend(loc='upper right', framealpha=0.9)

    return ax


def plot_cost_by_technology(df, ax):
    """Plot cost breakdown by technology type."""
    # Aggregate total costs by technology
    cost_cols = ['capex_usd', 'cost_component_opex_annual_usd', 'cost_component_new_energy_usd']

    agg = df.groupby('technology')[cost_cols].sum()
    agg = agg / 1e9  # Convert to billions

    # Filter to main technologies and reorder
    techs = [t for t in TECH_ORDER if t in agg.index and t != 'Baseline']
    agg = agg.loc[techs]

    x = np.arange(len(techs))
    width = 0.25

    colors = ['#2E86AB', '#A23B72', '#F18F01']
    labels = ['CAPEX', 'OPEX', 'New Energy']

    for i, (col, label, color) in enumerate(zip(cost_cols, labels, colors)):
        ax.bar(x + i*width, agg[col].values, width, label=label, color=color, alpha=0.85)

    ax.set_xticks(x + width)
    ax.set_xticklabels([t.replace('_', ' ') for t in techs])
    ax.set_xlabel('Technology')
    ax.set_ylabel('Total Cost (Billion USD)')
    ax.legend(loc='upper right', framealpha=0.9)

    return ax


def generate_cost_figures(df):
    """Generate all cost visualization figures."""
    print("Generating cost figures...")

    # 3a. Cumulative CAPEX
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_cumulative_capex(df, ax)
    ax.set_title('Cumulative Capital Investment by Scenario (2025-2050)', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'cost_cumulative_capex.png'
    save_figure(fig, fig_path)
    # CSV: cumulative capex by scenario
    rows = []
    agg_c = df.groupby(['year', 'scenario'])['capex_usd'].sum().reset_index()
    for scenario in SCENARIO_NAMES.keys():
        s_data = agg_c[agg_c['scenario'] == scenario].sort_values('year')
        s_data = s_data.copy()
        s_data['cumulative_capex'] = s_data['capex_usd'].cumsum() / 1e9
        for _, row in s_data.iterrows():
            rows.append({'year': int(row['year']), 'category': scenario,
                         'value': row['cumulative_capex'], 'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(rows), fig_path, figure_type='line')
    print("  - cost_cumulative_capex.png")

    # 3b. Annual cost breakdown
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_annual_cost_breakdown(df, ax)
    ax.set_title('Annual Cost Breakdown (Average Across Scenarios)', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'cost_annual_breakdown.png'
    save_figure(fig, fig_path)
    # CSV: annual cost breakdown
    cost_cols = {
        'cost_component_capex_annual_usd': 'Annualized CAPEX',
        'cost_component_opex_annual_usd': 'OPEX',
        'cost_component_new_energy_usd': 'New Energy',
        'cost_component_fuel_savings_usd': 'Fuel Savings',
    }
    n_scenarios = len(df['scenario'].unique())
    cost_rows = []
    for col, label in cost_cols.items():
        yearly = df.groupby('year')[col].sum() / n_scenarios / 1e9
        for yr, val in yearly.items():
            cost_rows.append({'year': int(yr), 'category': label,
                              'value': -val if 'Savings' in label else val,
                              'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(cost_rows), fig_path, figure_type='stacked_bar')
    print("  - cost_annual_breakdown.png")

    # 3c. Cost by technology
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_cost_by_technology(df, ax)
    ax.set_title('Total Cost Breakdown by Technology', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'cost_by_technology.png'
    save_figure(fig, fig_path)
    # CSV: cost by technology
    cost_tech_cols = ['capex_usd', 'cost_component_opex_annual_usd', 'cost_component_new_energy_usd']
    cost_tech_labels = ['CAPEX', 'OPEX', 'New Energy']
    agg_t = df.groupby('technology')[cost_tech_cols].sum() / 1e9
    techs = [t for t in TECH_ORDER if t in agg_t.index and t != 'Baseline']
    agg_t = agg_t.loc[techs]
    tech_rows = []
    for tech in techs:
        for col, label in zip(cost_tech_cols, cost_tech_labels):
            tech_rows.append({'category': tech, 'subcategory': label,
                              'value': agg_t.loc[tech, col], 'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(tech_rows), fig_path, figure_type='grouped_bar')
    print("  - cost_by_technology.png")


# ============================================================================
# STRANDED ASSET VISUALIZATION FUNCTIONS
# ============================================================================

def plot_stranded_timeline(df_facilities, ax):
    """Plot cumulative stranded value over time."""
    # Group by stranding year and sum values
    timeline = df_facilities.groupby(['stranding_year', 'budget_scenario'])['stranded_value_usd'].sum().reset_index()

    # Sort and calculate cumulative
    for budget in ['1.5C', '2.0C']:
        data = timeline[timeline['budget_scenario'] == budget].sort_values('stranding_year')
        if not data.empty:
            data['cumulative'] = data['stranded_value_usd'].cumsum() / 1e9

            color = '#C73E1D' if budget == '1.5C' else '#2E86AB'
            ax.plot(
                data['stranding_year'],
                data['cumulative'],
                label=f'{budget} Budget',
                color=color,
                linewidth=2,
                marker='o',
                markersize=5
            )

    ax.set_xlabel('Stranding Year')
    ax.set_ylabel('Cumulative Stranded Value (Billion USD)')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)

    return ax


def plot_stranded_scenario_comparison(df_summary, ax):
    """Plot bar comparison of stranded values by scenario."""
    scenarios = df_summary['scenario'].values
    x = np.arange(len(scenarios))
    width = 0.35

    # Convert to billions
    values_15c = df_summary['stranded_value_1.5C_usd'].values / 1e9
    values_20c = df_summary['stranded_value_2.0C_usd'].values / 1e9

    ax.bar(x - width/2, values_15c, width, label='1.5°C Budget', color='#C73E1D', alpha=0.85)
    ax.bar(x + width/2, values_20c, width, label='2.0°C Budget', color='#2E86AB', alpha=0.85)

    # Format x labels
    labels = [SCENARIO_NAMES.get(s, s) for s in scenarios]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right')

    ax.set_ylabel('Stranded Asset Value (Billion USD)')
    ax.legend(loc='upper right', framealpha=0.9)

    # Add value labels
    for i, (v15, v20) in enumerate(zip(values_15c, values_20c)):
        ax.annotate(f'${v15:.1f}B', (i - width/2, v15), ha='center', va='bottom', fontsize=8)
        ax.annotate(f'${v20:.1f}B', (i + width/2, v20), ha='center', va='bottom', fontsize=8)

    return ax


def plot_stranded_by_company(df_facilities, ax):
    """Plot top 10 companies by stranded value."""
    # Aggregate by company
    company_agg = df_facilities.groupby('company')['stranded_value_usd'].sum().reset_index()
    company_agg = company_agg.sort_values('stranded_value_usd', ascending=True)

    # Get top 10
    top10 = company_agg.tail(10)

    # Convert to billions
    top10['stranded_b'] = top10['stranded_value_usd'] / 1e9

    # Horizontal bar chart
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(top10)))
    ax.barh(top10['company'], top10['stranded_b'], color=colors, alpha=0.85)

    ax.set_xlabel('Total Stranded Value (Billion USD)')
    ax.set_ylabel('Company')

    # Add value labels
    for i, (company, value) in enumerate(zip(top10['company'], top10['stranded_b'])):
        ax.annotate(f'${value:.1f}B', (value, i), va='center', ha='left', fontsize=9)

    return ax


def generate_stranded_asset_figures(df_summary, df_facilities):
    """Generate all stranded asset figures."""
    print("Generating stranded asset figures...")

    # 4a. Timeline
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stranded_timeline(df_facilities, ax)
    ax.set_title('Cumulative Stranded Asset Value Over Time', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'stranded_timeline.png'
    save_figure(fig, fig_path)
    # CSV: cumulative stranded timeline
    timeline_rows = []
    timeline = df_facilities.groupby(['stranding_year', 'budget_scenario'])['stranded_value_usd'].sum().reset_index()
    for budget in ['1.5C', '2.0C']:
        data = timeline[timeline['budget_scenario'] == budget].sort_values('stranding_year')
        if not data.empty:
            data = data.copy()
            data['cumulative'] = data['stranded_value_usd'].cumsum() / 1e9
            for _, row in data.iterrows():
                timeline_rows.append({'year': int(row['stranding_year']),
                                      'category': f'{budget} Budget',
                                      'value': row['cumulative'],
                                      'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(timeline_rows), fig_path, figure_type='line')
    print("  - stranded_timeline.png")

    # 4b. Scenario comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stranded_scenario_comparison(df_summary, ax)
    ax.set_title('Stranded Asset Value by Scenario and Carbon Budget', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'stranded_scenario_comparison.png'
    save_figure(fig, fig_path)
    # CSV: scenario comparison
    sc_rows = []
    for _, row in df_summary.iterrows():
        sc = row['scenario']
        sc_rows.append({'category': sc, 'subcategory': '1.5C',
                        'value': row['stranded_value_1.5C_usd'] / 1e9, 'unit': 'billion_USD'})
        sc_rows.append({'category': sc, 'subcategory': '2.0C',
                        'value': row['stranded_value_2.0C_usd'] / 1e9, 'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(sc_rows), fig_path, figure_type='grouped_bar')
    print("  - stranded_scenario_comparison.png")

    # 4c. By company
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_stranded_by_company(df_facilities, ax)
    ax.set_title('Top 10 Companies by Stranded Asset Value', fontsize=12, fontweight='bold')
    fig_path = OUTPUT_DIR / 'stranded_by_company.png'
    save_figure(fig, fig_path)
    # CSV: top 10 companies stranded
    company_agg = df_facilities.groupby('company')['stranded_value_usd'].sum().reset_index()
    company_agg = company_agg.sort_values('stranded_value_usd', ascending=False).head(10)
    company_tidy = company_agg.rename(columns={'company': 'category', 'stranded_value_usd': 'value'})
    company_tidy['value'] = company_tidy['value'] / 1e9
    company_tidy['unit'] = 'billion_USD'
    save_figure_data(company_tidy, fig_path, figure_type='bar')
    print("  - stranded_by_company.png")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 60)
    print("MACC Visualization Figures Generator")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Load data
    print("\nLoading data...")
    df = load_scenario_results()
    print(f"  - Loaded {len(df):,} rows from scenario_results.csv")

    df_stranded_summary = load_stranded_summary()
    print(f"  - Loaded {len(df_stranded_summary)} rows from stranded_assets_summary.csv")

    df_stranded_facilities = load_stranded_facilities()
    print(f"  - Loaded {len(df_stranded_facilities):,} rows from stranded_assets_facilities.csv")

    # Generate figures
    print("\n" + "-" * 40)
    generate_production_share_figures(df)

    print("\n" + "-" * 40)
    generate_emission_pathway_figures(df)

    print("\n" + "-" * 40)
    generate_cost_figures(df)

    print("\n" + "-" * 40)
    generate_stranded_asset_figures(df_stranded_summary, df_stranded_facilities)

    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print(f"Output location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
