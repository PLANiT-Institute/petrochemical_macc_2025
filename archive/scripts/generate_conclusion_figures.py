"""
Generate conclusion figures and summary statements for the petrochemical
decarbonization report.

Produces 5 figures + 5 conclusion bullet points derived from scenario results.
"""

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from modules.utils import save_figure_data

# Path configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
FIGURES_DIR = OUTPUTS_DIR / 'figures'
PRICES_DIR = PROJECT_ROOT / 'data' / 'assumptions' / 'prices'

os.makedirs(FIGURES_DIR, exist_ok=True)

# Professional matplotlib settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Scenario definitions
SCENARIOS = {
    'S1': {'label': 'S1: Flat + Coupled', 'suffix': 'flat_coupled',
            'elec': 'flat', 'h2': 'coupled'},
    'S2': {'label': 'S2: Flat + Decoupled', 'suffix': 'flat_decoupled',
            'elec': 'flat', 'h2': 'decoupled'},
    'S3': {'label': 'S3: Rising + Coupled', 'suffix': 'rising_coupled',
            'elec': 'rising', 'h2': 'coupled'},
    'S4': {'label': 'S4: Rising + Decoupled', 'suffix': 'rising_decoupled',
            'elec': 'rising', 'h2': 'decoupled'},
}

REGION_COLORS = {
    'Daesan': '#2196F3',
    'Yeosu': '#4CAF50',
    'Ulsan': '#FF9800',
    'Other': '#9E9E9E',
}

LOCATION_TO_REGION = {
    'Daesan': 'Daesan',
    'Yeosu': 'Yeosu',
    'Onsan': 'Ulsan',
    'Ulsan': 'Ulsan',
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Load all required datasets."""
    data = {}
    data['results'] = pd.read_csv(OUTPUTS_DIR / 'scenario_results.csv')
    data['stranded_summary'] = pd.read_csv(OUTPUTS_DIR / 'stranded_assets_summary.csv')
    data['stranded_facilities'] = pd.read_csv(OUTPUTS_DIR / 'stranded_assets_facilities.csv')
    data['regional'] = pd.read_csv(OUTPUTS_DIR / 'regional_abatement_summary.csv')

    # Price trajectories
    data['elec_flat'] = pd.read_csv(PRICES_DIR / 'elec_price_flat.csv')
    data['elec_rising'] = pd.read_csv(PRICES_DIR / 'grid_price_trajectory.csv')
    data['h2_decoupled'] = pd.read_csv(PRICES_DIR / 'h2_price_trajectory.csv')
    data['electrolyser'] = pd.read_csv(PRICES_DIR / 'electrolyser_params.csv')
    data['re_price'] = pd.read_csv(PRICES_DIR / 're_price_trajectory.csv')
    return data


def compute_coupled_h2_price(data):
    """Compute coupled LCOH trajectory from RE price + electrolyser params."""
    re = data['re_price'].set_index('year')['re_price_usd_per_mwh']
    ep = data['electrolyser'].set_index('year')
    years = ep.index
    lcoh = {}
    for y in years:
        capex_kw = ep.loc[y, 'capex_usd_per_kw']
        opex_kw = ep.loc[y, 'opex_usd_per_kw_yr']
        eff = ep.loc[y, 'efficiency_kwh_per_kg']
        cf = ep.loc[y, 'capacity_factor']
        lifespan = ep.loc[y, 'lifespan_years']
        dr = ep.loc[y, 'discount_rate']
        # CRF
        crf = dr * (1 + dr)**lifespan / ((1 + dr)**lifespan - 1)
        # Annual production per kW
        annual_kg_per_kw = cf * 8760 / eff
        # CAPEX per kg
        capex_per_kg = (capex_kw * crf) / annual_kg_per_kw
        opex_per_kg = opex_kw / annual_kg_per_kw
        # Energy cost per kg
        elec_usd_kwh = re.get(y, 50.0) / 1000.0
        energy_per_kg = elec_usd_kwh * eff
        lcoh[y] = capex_per_kg + opex_per_kg + energy_per_kg
    return pd.Series(lcoh)


def compute_scenario_kpis(data):
    """Compute KPIs for each S1-S4 scenario."""
    df = data['results']
    df_str = data['stranded_summary']

    kpis = {}
    for s_key, s_def in SCENARIOS.items():
        suffix = s_def['suffix']
        h2_scenario = f'shaheen_ncc_h2_{suffix}'
        elec_scenario = f'shaheen_ncc_elec_{suffix}'

        # Validate scenarios exist in results
        h2_df = df[df['scenario'] == h2_scenario]
        elec_df = df[df['scenario'] == elec_scenario]
        if len(h2_df) == 0:
            print(f"  Warning: scenario '{h2_scenario}' not found in results, skipping {s_key}")
            continue
        if len(elec_df) == 0:
            print(f"  Warning: scenario '{elec_scenario}' not found in results, skipping {s_key}")
            continue

        # Cumulative total cost 2025-2050
        h2_cost = h2_df['total_cost_usd'].sum()
        elec_cost = elec_df['total_cost_usd'].sum()

        best_tech = 'H2' if h2_cost <= elec_cost else 'Elec'
        best_scenario = h2_scenario if best_tech == 'H2' else elec_scenario
        best_cost = min(h2_cost, elec_cost)

        # Max-year added electricity demand for winning tech
        best_df = df[df['scenario'] == best_scenario]
        elec_by_year = best_df.groupby('year')['added_elec_mwh'].sum()
        max_elec_mwh = elec_by_year.max() if len(elec_by_year) > 0 else 0

        # Stranded assets (1.5C) for winning tech
        str_row = df_str[df_str['scenario'] == best_scenario]
        stranded_15c = str_row['stranded_value_1.5C_usd'].values[0] if len(str_row) > 0 else 0

        kpis[s_key] = {
            'label': s_def['label'],
            'suffix': suffix,
            'h2_cost': h2_cost,
            'elec_cost': elec_cost,
            'best_tech': best_tech,
            'best_tech_label': 'H\u2082-based' if best_tech == 'H2' else 'e-Cracker',
            'best_cost': best_cost,
            'max_elec_twh': max_elec_mwh / 1e6,
            'stranded_15c': stranded_15c,
            'h2_scenario': h2_scenario,
            'elec_scenario': elec_scenario,
            'best_scenario': best_scenario,
        }
    return kpis


# ---------------------------------------------------------------------------
# Figure 1 — Cumulative Cost Trajectory (Line Chart)
# ---------------------------------------------------------------------------

def fig1_cumulative_cost_trajectory(data):
    """Show how transition costs accumulate over 2025-2050 for each scenario."""
    df_reg = data['regional']

    # Color schemes: H2 = blue family, Elec = magenta/red family
    h2_colors = {
        'S1': '#90CAF9', 'S2': '#42A5F5', 'S3': '#1E88E5', 'S4': '#0D47A1',
    }
    elec_colors = {
        'S1': '#F48FB1', 'S2': '#EC407A', 'S3': '#D81B60', 'S4': '#880E4F',
    }

    fig, ax = plt.subplots(figsize=(12, 7))

    lines_h2 = {}
    lines_elec = {}

    for s_key, s_def in SCENARIOS.items():
        suffix = s_def['suffix']
        for tech, tech_label, color_map, line_store in [
            ('h2', 'H\u2082', h2_colors, lines_h2),
            ('elec', 'Elec', elec_colors, lines_elec),
        ]:
            scenario_name = f'shaheen_ncc_{tech}_{suffix}'
            yearly = df_reg[df_reg['scenario'] == scenario_name].groupby('year')['total_cost_usd'].sum()
            yearly = yearly.sort_index()
            cumulative = yearly.cumsum() / 1e9

            line, = ax.plot(cumulative.index, cumulative.values,
                            color=color_map[s_key], linewidth=2.0,
                            label=f'{s_key} {tech_label}')
            line_store[s_key] = cumulative

            # Label final value at 2050
            if 2050 in cumulative.index:
                final_val = cumulative.loc[2050]
                ax.annotate(f'${final_val:.0f}B',
                            xy=(2050, final_val),
                            xytext=(5, 0), textcoords='offset points',
                            fontsize=7.5, color=color_map[s_key],
                            fontweight='bold', va='center')

    # Shaded bands between H2 and Elec for each scenario
    for s_key in SCENARIOS:
        h2_cum = lines_h2[s_key]
        elec_cum = lines_elec[s_key]
        common_years = h2_cum.index.intersection(elec_cum.index)
        ax.fill_between(common_years,
                        h2_cum.loc[common_years].values,
                        elec_cum.loc[common_years].values,
                        alpha=0.08, color='#9E9E9E')

    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative Transition Cost ($B)')
    ax.set_title('Cumulative Transition Cost Trajectories (2025\u20132050)',
                 fontsize=14, fontweight='bold')
    ax.set_xlim(2025, 2052)

    # Legend grouped by tech
    h2_handles = [plt.Line2D([0], [0], color=h2_colors[s], lw=2, label=f'{s} H\u2082')
                  for s in SCENARIOS]
    elec_handles = [plt.Line2D([0], [0], color=elec_colors[s], lw=2, label=f'{s} Elec')
                    for s in SCENARIOS]
    legend = ax.legend(handles=h2_handles + elec_handles, ncol=2,
                       loc='upper left', framealpha=0.9, fontsize=9)

    ax.grid(axis='y', alpha=0.3)

    out = FIGURES_DIR / 'fig1_cost_trajectory.png'
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved {out}')
    # CSV export
    f1_rows = []
    for s_key, s_def in SCENARIOS.items():
        suffix = s_def['suffix']
        for tech, tech_label in [('h2', 'H2'), ('elec', 'Elec')]:
            scenario_name = f'shaheen_ncc_{tech}_{suffix}'
            yearly = df_reg[df_reg['scenario'] == scenario_name].groupby('year')['total_cost_usd'].sum()
            yearly = yearly.sort_index()
            cumulative = yearly.cumsum() / 1e9
            for yr, val in cumulative.items():
                f1_rows.append({'year': int(yr), 'category': f'{s_key} {tech_label}',
                                'value': val, 'unit': 'billion_USD', 'scenario': scenario_name})
    save_figure_data(pd.DataFrame(f1_rows), out, figure_type='line')


# ---------------------------------------------------------------------------
# Figure 2 — Cost Component Waterfall (Butterfly / Paired Bar)
# ---------------------------------------------------------------------------

def fig2_cost_component_waterfall(data):
    """Decompose cost difference between H2 and e-Cracker by component."""
    df_reg = data['regional']

    components = [
        ('annual_capex_usd', 'CAPEX', '#1565C0'),
        ('annual_opex_usd', 'OPEX', '#00897B'),
        ('annual_new_energy_usd', 'New Energy', '#FB8C00'),
        ('annual_fuel_savings_usd', 'Fuel Savings', '#43A047'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle('Cost Component Breakdown: H\u2082 vs e-Cracker by Scenario (2025\u20132050)',
                 fontsize=14, fontweight='bold', y=1.02)

    scenario_grid = [('S1', axes[0, 0]), ('S2', axes[0, 1]),
                     ('S3', axes[1, 0]), ('S4', axes[1, 1])]

    for s_key, ax in scenario_grid:
        suffix = SCENARIOS[s_key]['suffix']
        h2_scenario = f'shaheen_ncc_h2_{suffix}'
        elec_scenario = f'shaheen_ncc_elec_{suffix}'

        h2_data = df_reg[df_reg['scenario'] == h2_scenario]
        elec_data = df_reg[df_reg['scenario'] == elec_scenario]

        comp_labels = []
        h2_vals = []
        elec_vals = []

        for col, label, color in components:
            h2_sum = h2_data[col].sum() / 1e9
            elec_sum = elec_data[col].sum() / 1e9
            comp_labels.append(label)
            # Fuel savings are negative costs (subtract from total)
            if 'savings' in col:
                h2_vals.append(-h2_sum)
                elec_vals.append(-elec_sum)
            else:
                h2_vals.append(h2_sum)
                elec_vals.append(elec_sum)

        # Net totals
        h2_net = sum(h2_vals)
        elec_net = sum(elec_vals)
        comp_labels.append('Net Total')
        h2_vals.append(h2_net)
        elec_vals.append(elec_net)

        y_pos = np.arange(len(comp_labels))
        bar_colors = [c[2] for c in components] + ['#424242']

        # H2 bars go left (negative), Elec bars go right (positive)
        ax.barh(y_pos, [-v for v in h2_vals], height=0.35, align='center',
                color=bar_colors, alpha=0.8, edgecolor='white', linewidth=0.5)
        ax.barh(y_pos, elec_vals, height=0.35, align='center',
                color=bar_colors, alpha=0.5, edgecolor='white', linewidth=0.5,
                hatch='///')

        # Value labels
        for i, (hv, ev) in enumerate(zip(h2_vals, elec_vals)):
            if abs(hv) > 0.5:
                ax.text(-hv - 0.3 * np.sign(hv), i, f'${abs(hv):.0f}B',
                        ha='right' if hv > 0 else 'left', va='center', fontsize=7)
            if abs(ev) > 0.5:
                ax.text(ev + 0.3 * np.sign(ev), i, f'${abs(ev):.0f}B',
                        ha='left' if ev > 0 else 'right', va='center', fontsize=7)

        ax.axvline(0, color='#212121', linewidth=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(comp_labels, fontsize=9)
        ax.set_title(f"{SCENARIOS[s_key]['label']}", fontsize=11, fontweight='bold')
        ax.set_xlabel('$B (cumulative 2025\u20132050)', fontsize=9)
        ax.grid(axis='x', alpha=0.2)

        # H2/Elec direction labels
        xlim = ax.get_xlim()
        ax.text(xlim[0] * 0.5, len(comp_labels) - 0.2, '\u2190 H\u2082',
                ha='center', fontsize=8, color='#1565C0', fontweight='bold')
        ax.text(xlim[1] * 0.5, len(comp_labels) - 0.2, 'Elec \u2192',
                ha='center', fontsize=8, color='#AD1457', fontweight='bold')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='gray', alpha=0.8, label='H\u2082-based (solid)'),
        Patch(facecolor='gray', alpha=0.5, hatch='///', label='e-Cracker (hatched)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2,
               framealpha=0.9, fontsize=10, bbox_to_anchor=(0.5, -0.02))

    fig.tight_layout()

    out = FIGURES_DIR / 'fig2_cost_waterfall.png'
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved {out}')
    # CSV export
    f2_rows = []
    for s_key, s_def_local in SCENARIOS.items():
        suffix = s_def_local['suffix']
        h2_scenario = f'shaheen_ncc_h2_{suffix}'
        elec_scenario = f'shaheen_ncc_elec_{suffix}'
        h2_data = df_reg[df_reg['scenario'] == h2_scenario]
        elec_data = df_reg[df_reg['scenario'] == elec_scenario]
        for col, label, _ in components:
            h2_sum = h2_data[col].sum() / 1e9
            elec_sum = elec_data[col].sum() / 1e9
            sign = -1 if 'savings' in col else 1
            f2_rows.append({'panel': s_key, 'category': label, 'subcategory': 'H2',
                            'value': sign * h2_sum, 'unit': 'billion_USD'})
            f2_rows.append({'panel': s_key, 'category': label, 'subcategory': 'Elec',
                            'value': sign * elec_sum, 'unit': 'billion_USD'})
    save_figure_data(pd.DataFrame(f2_rows), out, figure_type='butterfly_bar')


# ---------------------------------------------------------------------------
# Figure 3 — Emission Reduction Pathway (Line Chart)
# ---------------------------------------------------------------------------

def fig3_emission_pathway(data):
    """Show decarbonization trajectory vs BAU baseline across scenarios."""
    df_reg = data['regional']

    # Color scheme consistent with Fig 1
    h2_colors = {
        'S1': '#90CAF9', 'S2': '#42A5F5', 'S3': '#1E88E5', 'S4': '#0D47A1',
    }
    elec_colors = {
        'S1': '#F48FB1', 'S2': '#EC407A', 'S3': '#D81B60', 'S4': '#880E4F',
    }

    fig, ax = plt.subplots(figsize=(12, 7))

    # BAU baseline (same across scenarios — use first scenario)
    first_scenario = df_reg['scenario'].iloc[0]
    bau = df_reg[df_reg['scenario'] == first_scenario].groupby('year')['bau_emissions_tco2'].sum()
    bau_mt = bau.sort_index() / 1e6
    ax.plot(bau_mt.index, bau_mt.values, color='#424242', linewidth=2.5,
            linestyle='--', label='BAU Baseline', zorder=5)

    # Track best (lowest emission) trajectory for shading
    best_emissions = None

    for s_key, s_def in SCENARIOS.items():
        suffix = s_def['suffix']
        for tech, tech_label, color_map, ls in [
            ('h2', 'H\u2082', h2_colors, '-'),
            ('elec', 'Elec', elec_colors, '-'),
        ]:
            scenario_name = f'shaheen_ncc_{tech}_{suffix}'
            yearly = df_reg[df_reg['scenario'] == scenario_name].groupby('year')['emissions_tco2'].sum()
            yearly_mt = yearly.sort_index() / 1e6

            ax.plot(yearly_mt.index, yearly_mt.values,
                    color=color_map[s_key], linewidth=1.5, linestyle=ls,
                    label=f'{s_key} {tech_label}')

            if best_emissions is None or yearly_mt.iloc[-1] < best_emissions.iloc[-1]:
                best_emissions = yearly_mt

    # Shade between BAU and best-performing scenario
    if best_emissions is not None:
        common_years = bau_mt.index.intersection(best_emissions.index)
        ax.fill_between(common_years,
                        bau_mt.loc[common_years].values,
                        best_emissions.loc[common_years].values,
                        alpha=0.12, color='#4CAF50', label='Max Abatement')

    # Annotate 50% reduction milestone
    if best_emissions is not None:
        bau_2025 = bau_mt.iloc[0]
        half = bau_2025 * 0.5
        for yr in best_emissions.index:
            if best_emissions.loc[yr] <= half:
                ax.axhline(half, color='#BDBDBD', linewidth=0.8, linestyle=':')
                ax.annotate(f'50% reduction ({yr})',
                            xy=(yr, best_emissions.loc[yr]),
                            xytext=(yr + 1, half + 2),
                            fontsize=9, color='#616161',
                            arrowprops=dict(arrowstyle='->', color='#9E9E9E'))
                break

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Emissions (Mt CO\u2082/year)')
    ax.set_title('Emission Reduction Pathways vs BAU Baseline (2025\u20132050)',
                 fontsize=14, fontweight='bold')
    ax.set_xlim(2025, 2050)

    # Legend
    h2_handles = [plt.Line2D([0], [0], color=h2_colors[s], lw=1.5, label=f'{s} H\u2082')
                  for s in SCENARIOS]
    elec_handles = [plt.Line2D([0], [0], color=elec_colors[s], lw=1.5, label=f'{s} Elec')
                    for s in SCENARIOS]
    bau_handle = plt.Line2D([0], [0], color='#424242', lw=2.5, ls='--', label='BAU')
    abate_handle = mpatches.Patch(color='#4CAF50', alpha=0.12, label='Max Abatement')
    ax.legend(handles=[bau_handle, abate_handle] + h2_handles + elec_handles,
              ncol=2, loc='upper right', framealpha=0.9, fontsize=8.5)

    ax.grid(axis='y', alpha=0.3)

    out = FIGURES_DIR / 'fig3_emission_pathway.png'
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved {out}')
    # CSV export
    f3_rows = []
    first_scenario = df_reg['scenario'].iloc[0]
    bau_s = df_reg[df_reg['scenario'] == first_scenario].groupby('year')['bau_emissions_tco2'].sum().sort_index() / 1e6
    for yr, val in bau_s.items():
        f3_rows.append({'year': int(yr), 'category': 'BAU Baseline', 'value': val,
                        'unit': 'MtCO2_per_yr'})
    for s_key, s_def_local in SCENARIOS.items():
        suffix = s_def_local['suffix']
        for tech, tech_label in [('h2', 'H2'), ('elec', 'Elec')]:
            scenario_name = f'shaheen_ncc_{tech}_{suffix}'
            yearly = df_reg[df_reg['scenario'] == scenario_name].groupby('year')['emissions_tco2'].sum().sort_index() / 1e6
            for yr, val in yearly.items():
                f3_rows.append({'year': int(yr), 'category': f'{s_key} {tech_label}',
                                'value': val, 'unit': 'MtCO2_per_yr', 'scenario': scenario_name})
    save_figure_data(pd.DataFrame(f3_rows), out, figure_type='line')


# ---------------------------------------------------------------------------
# Figure 4 — Bubble Scatter: Company Stranded Assets
# ---------------------------------------------------------------------------

def fig4_bubble_stranded(data):
    """Create bubble scatter of company-level stranded asset exposure."""
    df_strand = data['stranded_facilities']

    # Use S3 scenario (rising+coupled, H2-based, 1.5C)
    s3_scenario = 'shaheen_ncc_h2_rising_coupled'
    df_s3 = df_strand[(df_strand['scenario'] == s3_scenario) &
                       (df_strand['budget_scenario'] == '1.5C')]

    if len(df_s3) == 0:
        print('  Warning: No stranded facility data for S3 1.5C scenario')
        return

    # Map locations to regions
    df_s3 = df_s3.copy()
    df_s3['region'] = df_s3['location'].map(LOCATION_TO_REGION).fillna('Other')

    grouped = df_s3.groupby('company').agg(
        stranded_value=('stranded_value_usd', 'sum'),
        total_capacity=('capacity_kt', 'sum'),
        region=('region', 'first')
    ).reset_index()

    grouped['vulnerability'] = grouped['stranded_value'] / grouped['total_capacity']
    grouped = grouped.sort_values('stranded_value', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Bubble size
    max_val = grouped['stranded_value'].max()
    sizes = (grouped['stranded_value'] / max_val) * 2000
    sizes = sizes.clip(lower=50)  # minimum visible size

    colors = [REGION_COLORS.get(r, '#9E9E9E') for r in grouped['region']]

    y_pos = np.arange(len(grouped))
    ax.scatter(grouped['vulnerability'] / 1e6, y_pos, s=sizes,
               c=colors, alpha=0.7, edgecolors='white', linewidths=1.5, zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(grouped['company'], fontsize=10)
    ax.set_xlabel('Stranded-to-Capacity Ratio ($M/kt)', fontsize=12)
    ax.set_title('Company Stranded Asset Exposure (S3: Rising+Coupled, 1.5\u00b0C)',
                 fontsize=14, fontweight='bold')

    # Annotate stranded values
    for i, row in enumerate(grouped.itertuples()):
        val_b = row.stranded_value / 1e9
        if val_b >= 0.1:
            ax.annotate(f'${val_b:.1f}B', (row.vulnerability / 1e6, i),
                        textcoords='offset points', xytext=(15, 0),
                        fontsize=8, va='center', color='#424242')

    # Legend for regions
    handles = [mpatches.Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
    ax.legend(handles=handles, title='Region', loc='lower right', framealpha=0.9)

    # Size legend
    ref_values = [1e9, 5e9, 10e9]
    ref_labels = ['$1B', '$5B', '$10B']
    for val, label in zip(ref_values, ref_labels):
        if val <= max_val * 1.2:
            sz = (val / max_val) * 2000
            ax.scatter([], [], s=sz, c='#B0BEC5', edgecolors='white',
                       linewidths=1.5, label=label)
    ax.legend(handles=handles, title='Region', loc='lower right', framealpha=0.9)

    ax.grid(axis='x', alpha=0.3)

    out = FIGURES_DIR / 'fig4_bubble_stranded.png'
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved {out}')
    # CSV export
    f4_df = grouped[['company', 'stranded_value', 'total_capacity', 'region', 'vulnerability']].copy()
    f4_df = f4_df.rename(columns={'company': 'category', 'stranded_value': 'value'})
    f4_df['unit'] = 'USD'
    save_figure_data(f4_df, out, figure_type='bubble_scatter')


# ---------------------------------------------------------------------------
# Figure 5 — Annual Cost & Infrastructure Demand (Dual-Panel)
# ---------------------------------------------------------------------------

def fig5_annual_cost_infrastructure(data, kpis):
    """Show year-by-year cost burden and infrastructure buildout requirements."""
    df_reg = data['regional']

    # Pick best-tech decoupled scenario (S2 or S4 — whichever is cheaper)
    s2_cost = kpis['S2']['best_cost']
    s4_cost = kpis['S4']['best_cost']
    if s2_cost <= s4_cost:
        chosen_key = 'S2'
    else:
        chosen_key = 'S4'
    chosen_tech = kpis[chosen_key]['best_tech'].lower()
    chosen_suffix = SCENARIOS[chosen_key]['suffix']
    chosen_scenario = f'shaheen_ncc_{chosen_tech}_{chosen_suffix}'
    chosen_label = f"{SCENARIOS[chosen_key]['label']} ({kpis[chosen_key]['best_tech_label']})"

    df_s = df_reg[df_reg['scenario'] == chosen_scenario].copy()
    regions = ['Daesan', 'Yeosu', 'Ulsan', 'Other']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    fig.suptitle(f'Annual Transition Cost & Infrastructure Demand\n{chosen_label}',
                 fontsize=14, fontweight='bold', y=1.02)

    # --- Top panel: Annual cost by region (stacked area) ---
    years = sorted(df_s['year'].unique())
    region_costs = {}
    for region in regions:
        costs_by_year = []
        for yr in years:
            mask = (df_s['year'] == yr) & (df_s['region'] == region)
            costs_by_year.append(df_s.loc[mask, 'total_cost_usd'].sum() / 1e9)
        region_costs[region] = costs_by_year

    ax1.stackplot(years,
                  *[region_costs[r] for r in regions],
                  labels=regions,
                  colors=[REGION_COLORS[r] for r in regions],
                  alpha=0.8)
    ax1.set_ylabel('Annual Transition Cost ($B/year)')
    ax1.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    # --- Bottom panel: Infrastructure demand (elec TWh + H2 Mt) ---
    elec_by_year = df_s.groupby('year')['elec_demand_mwh'].sum().sort_index() / 1e6  # TWh
    h2_by_year = df_s.groupby('year')['h2_demand_t'].sum().sort_index() / 1e6  # Mt

    color_elec = '#FF9800'
    color_h2 = '#1565C0'

    ax2.plot(elec_by_year.index, elec_by_year.values,
             color=color_elec, linewidth=2.0, marker='o', markersize=3,
             label='Electricity Demand (TWh)')
    ax2.set_ylabel('Electricity Demand (TWh)', color=color_elec)
    ax2.tick_params(axis='y', labelcolor=color_elec)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(h2_by_year.index, h2_by_year.values,
                  color=color_h2, linewidth=2.0, marker='s', markersize=3,
                  label='H\u2082 Demand (Mt)')
    ax2_twin.set_ylabel('H\u2082 Demand (Mt)', color=color_h2)
    ax2_twin.tick_params(axis='y', labelcolor=color_h2)
    ax2_twin.spines['right'].set_visible(True)

    ax2.set_xlabel('Year')

    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', framealpha=0.9, fontsize=9)

    ax2.grid(axis='y', alpha=0.3)

    fig.tight_layout()

    out = FIGURES_DIR / 'fig5_annual_cost_infra.png'
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved {out}')
    # CSV export
    f5_rows = []
    # Panel A: annual cost by region
    for region in regions:
        for yr, val in zip(years, region_costs[region]):
            f5_rows.append({'year': int(yr), 'category': region, 'value': val,
                            'unit': 'billion_USD_per_yr', 'panel': 'A'})
    # Panel B: infrastructure demand
    for yr, val in elec_by_year.items():
        f5_rows.append({'year': int(yr), 'category': 'Electricity Demand', 'value': val,
                        'unit': 'TWh', 'panel': 'B'})
    for yr, val in h2_by_year.items():
        f5_rows.append({'year': int(yr), 'category': 'H2 Demand', 'value': val,
                        'unit': 'Mt', 'panel': 'B'})
    save_figure_data(pd.DataFrame(f5_rows), out, figure_type='multi_panel')


# ---------------------------------------------------------------------------
# Conclusion statements
# ---------------------------------------------------------------------------

def generate_conclusions(kpis, data):
    """Generate 5 conclusion bullet points from computed data."""
    df_reg = data['regional']
    df_strand = data['stranded_facilities']

    # 1. Electricity price dominance
    s1_best = min(kpis['S1']['h2_cost'], kpis['S1']['elec_cost'])
    s3_best = min(kpis['S3']['h2_cost'], kpis['S3']['elec_cost'])
    elec_impact_pct = abs(s3_best - s1_best) / s1_best * 100

    stmt1 = (
        f"1. Electricity price dominance: If electricity prices rise to ~$191/MWh by 2050, "
        f"transition costs increase by {elec_impact_pct:.0f}% compared to flat pricing. "
        f"The best technology under rising prices is {kpis['S3']['best_tech_label']}, "
        f"while flat pricing favors {kpis['S1']['best_tech_label']}."
    )

    # 2. H2 decoupling advantage
    s3_cost_b = kpis['S3']['best_cost'] / 1e9
    s4_cost_b = kpis['S4']['best_cost'] / 1e9
    coupling_diff_pct = abs(s4_cost_b - s3_cost_b) / s3_cost_b * 100

    stmt2 = (
        f"2. H\u2082 decoupling effect: Switching from coupled to decoupled hydrogen pricing "
        f"(under rising electricity) changes the best-case transition cost by "
        f"{coupling_diff_pct:.1f}% (${s3_cost_b:.1f}B vs ${s4_cost_b:.1f}B)."
    )

    # 3. Stable electricity favors e-Cracker
    s1_h2_b = kpis['S1']['h2_cost'] / 1e9
    s1_elec_b = kpis['S1']['elec_cost'] / 1e9

    stmt3 = (
        f"3. Flat electricity pricing outcome: Under flat electricity ($77/MWh), "
        f"the lower-cost technology is {kpis['S1']['best_tech_label']} "
        f"(H\u2082: ${s1_h2_b:.1f}B vs e-Cracker: ${s1_elec_b:.1f}B cumulative cost)."
    )

    # 4. Stranded asset concentration
    s3_strand = df_strand[
        (df_strand['scenario'] == 'shaheen_ncc_h2_rising_coupled') &
        (df_strand['budget_scenario'] == '1.5C')
    ].copy()
    s3_strand['region'] = s3_strand['location'].map(LOCATION_TO_REGION).fillna('Other')
    region_strand = s3_strand.groupby('region')['stranded_value_usd'].sum()
    total_strand = region_strand.sum()
    yeosu_daesan_share = 0
    for r in ['Yeosu', 'Daesan']:
        if r in region_strand.index:
            yeosu_daesan_share += region_strand[r]
    yd_pct = yeosu_daesan_share / total_strand * 100 if total_strand > 0 else 0

    company_strand = s3_strand.groupby('company')['stranded_value_usd'].sum().sort_values(ascending=False)
    top_companies = ', '.join(company_strand.head(3).index.tolist())

    stmt4 = (
        f"4. Stranded asset concentration: Under 1.5\u00b0C budgets, Yeosu and Daesan "
        f"account for {yd_pct:.0f}% of total stranded assets (${total_strand/1e9:.1f}B total). "
        f"The most exposed companies are {top_companies}."
    )

    # 5. Regional transition cost disparity
    s3_reg = df_reg[df_reg['scenario'] == 'shaheen_ncc_h2_rising_coupled']
    reg_costs = s3_reg.groupby('region')['total_cost_usd'].sum().sort_values(ascending=False)
    top_region = reg_costs.index[0] if len(reg_costs) > 0 else 'Unknown'
    top_cost_b = reg_costs.iloc[0] / 1e9 if len(reg_costs) > 0 else 0

    stmt5 = (
        f"5. Regional cost disparity: {top_region} faces the highest absolute transition cost "
        f"(${top_cost_b:.1f}B cumulative), driven by NCC concentration. "
        f"Regional cost ranking: {', '.join(f'{r} (${v/1e9:.1f}B)' for r, v in reg_costs.items())}."
    )

    statements = [stmt1, stmt2, stmt3, stmt4, stmt5]
    return statements


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('Loading data...')
    data = load_data()

    print('Computing scenario KPIs...')
    kpis = compute_scenario_kpis(data)

    # Print KPI summary
    for s_key, k in kpis.items():
        print(f"  {s_key}: Best={k['best_tech_label']}, "
              f"Cost=${k['best_cost']/1e9:.1f}B, "
              f"Stranded=${k['stranded_15c']/1e9:.1f}B")

    print('\nGenerating figures...')
    fig1_cumulative_cost_trajectory(data)
    fig2_cost_component_waterfall(data)
    fig3_emission_pathway(data)
    fig4_bubble_stranded(data)
    fig5_annual_cost_infrastructure(data, kpis)

    print('\nGenerating conclusion statements...')
    statements = generate_conclusions(kpis, data)

    out_path = OUTPUTS_DIR / 'conclusion_statements.txt'
    with open(out_path, 'w') as f:
        f.write('CONCLUSION STATEMENTS\n')
        f.write('=' * 60 + '\n\n')
        for stmt in statements:
            f.write(stmt + '\n\n')
    print(f'  Saved {out_path}')

    print('\n' + '=' * 60)
    print('CONCLUSION STATEMENTS')
    print('=' * 60)
    for stmt in statements:
        print(f'\n{stmt}')

    print('\nDone.')


if __name__ == '__main__':
    main()
