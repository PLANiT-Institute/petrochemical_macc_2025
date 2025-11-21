#!/usr/bin/env python3
"""
Generate publication-quality figures for Carbon Neutrality journal paper
High-resolution, professional formatting for academic publication
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication-quality style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Color scheme - colorblind-friendly
COLORS = {
    'ncc_h2': '#0173B2',      # Blue
    'ncc_elec': '#DE8F05',    # Orange
    're_ppa': '#029E73',      # Green
    'heat_pump': '#CC78BC',   # Purple
    'shaheen': '#0173B2',
    'restructure_25': '#DE8F05',
    'restructure_40': '#029E73'
}

OUTPUT_DIR = Path('outputs/paper_figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("GENERATING PUBLICATION-QUALITY FIGURES FOR PAPER")
print("="*80)

# ============================================================================
# FIGURE 1: 6-Scenario Cost Comparison (Main Result)
# ============================================================================
print("\n[1/7] Figure 1: Six-Scenario Cost Comparison...")

summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Prepare data
scenarios = ['Shaheen\n(Growth)', '25% Reduction', '40% Reduction']
h2_costs = [31.4, 15.1, 13.0]
elec_costs = [33.3, 16.7, 14.5]
x = np.arange(len(scenarios))
width = 0.35

# Plot costs
bars1 = ax1.bar(x - width/2, h2_costs, width, label='NCC-H₂', color=COLORS['ncc_h2'], edgecolor='black', linewidth=0.5)
bars2 = ax1.bar(x + width/2, elec_costs, width, label='NCC-Electricity', color=COLORS['ncc_elec'], edgecolor='black', linewidth=0.5)

ax1.set_ylabel('Cumulative CAPEX (Billion USD, 2025-2050)', fontweight='bold')
ax1.set_xlabel('Production Pathway', fontweight='bold')
ax1.set_title('(a) Total Decarbonization Cost by 2050', fontweight='bold', loc='left')
ax1.set_xticks(x)
ax1.set_xticklabels(scenarios)
ax1.legend(loc='upper right', frameon=True, edgecolor='black')
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_ylim(0, 37)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'${height:.1f}B',
                ha='center', va='bottom', fontsize=8, fontweight='bold')

# Plot cost difference
cost_diff = [elec - h2 for elec, h2 in zip(elec_costs, h2_costs)]
cost_diff_pct = [100 * (elec - h2) / h2 for elec, h2 in zip(elec_costs, h2_costs)]

bars3 = ax2.bar(x, cost_diff, width*2, color='#999999', edgecolor='black', linewidth=0.5)
ax2.set_ylabel('Cost Difference (Billion USD)', fontweight='bold')
ax2.set_xlabel('Production Pathway', fontweight='bold')
ax2.set_title('(b) NCC-Electricity Premium over NCC-H₂', fontweight='bold', loc='left')
ax2.set_xticks(x)
ax2.set_xticklabels(scenarios)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_ylim(0, 2.5)

# Add value labels
for i, bar in enumerate(bars3):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'${height:.1f}B\n({cost_diff_pct[i]:.1f}%)',
            ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure1_Six_Scenario_Comparison.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure1_Six_Scenario_Comparison.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure1_Six_Scenario_Comparison.png")

# ============================================================================
# FIGURE 2: Technology Deployment by Pathway
# ============================================================================
print("[2/7] Figure 2: Technology Deployment Breakdown...")

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

scenario_data = [
    ('Shaheen (성장) + NCC-H2', 'shaheen_ncc_h2', 'Shaheen Growth\n+ NCC-H₂'),
    ('Shaheen (성장) + NCC-Electricity', 'shaheen_ncc_elec', 'Shaheen Growth\n+ NCC-Electricity'),
    ('구조조정 25% + NCC-H2', 'restructure_25pct_ncc_h2', '25% Reduction\n+ NCC-H₂'),
    ('구조조정 25% + NCC-Electricity', 'restructure_25pct_ncc_elec', '25% Reduction\n+ NCC-Electricity'),
    ('구조조정 40% + NCC-H2', 'restructure_40pct_ncc_h2', '40% Reduction\n+ NCC-H₂'),
    ('구조조정 40% + NCC-Electricity', 'restructure_40pct_ncc_elec', '40% Reduction\n+ NCC-Electricity'),
]

for idx, (scenario_name, scenario_id, title) in enumerate(scenario_data):
    ax = axes[idx]

    row = summary[summary['scenario_id'] == scenario_id].iloc[0]

    technologies = []
    values = []
    colors = []

    if row['ncc_h2_mt'] > 0:
        technologies.append('NCC-H₂')
        values.append(row['ncc_h2_mt'])
        colors.append(COLORS['ncc_h2'])

    if row['ncc_elec_mt'] > 0:
        technologies.append('NCC-Elec')
        values.append(row['ncc_elec_mt'])
        colors.append(COLORS['ncc_elec'])

    if row['re_ppa_mt'] > 0:
        technologies.append('RE PPA')
        values.append(row['re_ppa_mt'])
        colors.append(COLORS['re_ppa'])

    if row['heat_pump_mt'] > 0:
        technologies.append('Heat Pump')
        values.append(row['heat_pump_mt'])
        colors.append(COLORS['heat_pump'])

    # Pie chart
    wedges, texts, autotexts = ax.pie(values, labels=technologies, autopct='%1.1f%%',
                                        colors=colors, startangle=90,
                                        textprops={'fontsize': 8, 'fontweight': 'bold'},
                                        wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})

    for autotext in autotexts:
        autotext.set_color('white')

    ax.set_title(f'{title}\n${row["cost_2050_billion_usd"]:.1f}B',
                 fontweight='bold', fontsize=9)

plt.suptitle('Technology Deployment by Scenario (2050)', fontweight='bold', fontsize=13, y=0.98)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure2_Technology_Deployment.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure2_Technology_Deployment.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure2_Technology_Deployment.png")

# ============================================================================
# FIGURE 3: MACC Curves (2025, 2030, 2050)
# ============================================================================
print("[3/7] Figure 3: MACC Curves Evolution...")

macc_df = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_02_macc/macc_annual_2025_2050.csv')

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

years = [2025, 2030, 2050]
tech_map = {
    'Heat_Pump': ('Heat Pump', COLORS['heat_pump']),
    'NCC-H2': ('NCC-H₂', COLORS['ncc_h2']),
    'NCC-Electricity': ('NCC-Electricity', COLORS['ncc_elec']),
    'RE_PPA': ('RE PPA', COLORS['re_ppa'])
}

for idx, year in enumerate(years):
    ax = axes[idx]
    macc_year = macc_df[macc_df['year'] == year].copy()
    macc_year = macc_year[macc_year['available'] == True].sort_values('total_cost_usd_per_tco2')

    # Calculate cumulative abatement
    macc_year['cumulative_abatement'] = macc_year['abatement_potential_mtco2'].cumsum()

    prev_x = 0
    for _, row in macc_year.iterrows():
        tech_label, color = tech_map.get(row['technology'], (row['technology'], '#999999'))

        x_start = prev_x
        x_end = row['cumulative_abatement']
        y = row['total_cost_usd_per_tco2']

        ax.barh(y, x_end - x_start, left=x_start, height=20,
                color=color, edgecolor='black', linewidth=0.5, label=tech_label)

        prev_x = x_end

    ax.set_xlabel('Cumulative Abatement Potential (MtCO₂)', fontweight='bold')
    ax.set_ylabel('Cost (USD/tCO₂)', fontweight='bold')
    ax.set_title(f'({chr(97+idx)}) MACC Curve {year}', fontweight='bold', loc='left')
    ax.grid(axis='both', alpha=0.3, linestyle='--')
    ax.set_ylim(0, 300)

    # Remove duplicate labels
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', frameon=True, edgecolor='black')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure3_MACC_Curves.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure3_MACC_Curves.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure3_MACC_Curves.png")

# ============================================================================
# FIGURE 4: Technology Cost Evolution (2025-2050)
# ============================================================================
print("[4/7] Figure 4: Technology Cost Evolution...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Get cost trajectories
years_range = range(2025, 2051)
costs_by_tech = {tech: [] for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']}

for year in years_range:
    macc_year = macc_df[macc_df['year'] == year]
    for tech in costs_by_tech.keys():
        tech_row = macc_year[macc_year['technology'] == tech]
        if len(tech_row) > 0:
            costs_by_tech[tech].append(tech_row.iloc[0]['total_cost_usd_per_tco2'])
        else:
            costs_by_tech[tech].append(np.nan)

# Plot absolute costs
for tech, costs in costs_by_tech.items():
    label, color = tech_map.get(tech, (tech, '#999999'))
    ax1.plot(years_range, costs, marker='o', markersize=3, label=label,
             color=color, linewidth=2)

ax1.set_xlabel('Year', fontweight='bold')
ax1.set_ylabel('Abatement Cost (USD/tCO₂)', fontweight='bold')
ax1.set_title('(a) Technology Cost Trajectories', fontweight='bold', loc='left')
ax1.legend(loc='upper right', frameon=True, edgecolor='black')
ax1.grid(alpha=0.3, linestyle='--')
ax1.set_ylim(0, 300)

# Plot cost reduction %
base_costs = {tech: costs[0] for tech, costs in costs_by_tech.items()}
for tech, costs in costs_by_tech.items():
    label, color = tech_map.get(tech, (tech, '#999999'))
    cost_reduction = [100 * (1 - c/base_costs[tech]) if not np.isnan(c) else np.nan for c in costs]
    ax2.plot(years_range, cost_reduction, marker='o', markersize=3, label=label,
             color=color, linewidth=2)

ax2.set_xlabel('Year', fontweight='bold')
ax2.set_ylabel('Cost Reduction from 2025 (%)', fontweight='bold')
ax2.set_title('(b) Learning Curve Effect', fontweight='bold', loc='left')
ax2.legend(loc='lower right', frameon=True, edgecolor='black')
ax2.grid(alpha=0.3, linestyle='--')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure4_Cost_Evolution.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure4_Cost_Evolution.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure4_Cost_Evolution.png")

# ============================================================================
# FIGURE 5: Hydrogen Demand Trajectory
# ============================================================================
print("[5/7] Figure 5: Hydrogen Demand Trajectories...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Load deployment data for all H2 scenarios
h2_scenarios = [
    ('shaheen_ncc_h2', 'Shaheen Growth', COLORS['shaheen']),
    ('restructure_25pct_ncc_h2', '25% Reduction', COLORS['restructure_25']),
    ('restructure_40pct_ncc_h2', '40% Reduction', COLORS['restructure_40'])
]

for scenario_id, label, color in h2_scenarios:
    deployment = pd.read_csv(f'outputs/scenarios_{scenario_id}/module_03_optimization/policy_target_deployment.csv')

    ax1.plot(deployment['year'], deployment['h2_consumption_kt']/1000,
             marker='o', markersize=4, label=label, color=color, linewidth=2)

    # Cumulative H2
    cumulative = deployment['h2_consumption_kt'].cumsum() / 1000
    ax2.plot(deployment['year'], cumulative,
             marker='o', markersize=4, label=label, color=color, linewidth=2)

ax1.set_xlabel('Year', fontweight='bold')
ax1.set_ylabel('Annual H₂ Demand (Mt H₂/year)', fontweight='bold')
ax1.set_title('(a) Annual Hydrogen Demand', fontweight='bold', loc='left')
ax1.legend(loc='upper left', frameon=True, edgecolor='black')
ax1.grid(alpha=0.3, linestyle='--')
ax1.set_ylim(0, 9)

ax2.set_xlabel('Year', fontweight='bold')
ax2.set_ylabel('Cumulative H₂ Consumption (Mt H₂)', fontweight='bold')
ax2.set_title('(b) Cumulative Hydrogen Demand (2025-2050)', fontweight='bold', loc='left')
ax2.legend(loc='upper left', frameon=True, edgecolor='black')
ax2.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure5_Hydrogen_Demand.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure5_Hydrogen_Demand.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure5_Hydrogen_Demand.png")

# ============================================================================
# FIGURE 6: Emissions Trajectory Comparison
# ============================================================================
print("[6/7] Figure 6: Emissions Trajectories...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# All 6 scenarios
all_scenarios = [
    ('shaheen_ncc_h2', 'Shaheen + H₂', COLORS['ncc_h2'], '-'),
    ('shaheen_ncc_elec', 'Shaheen + Elec', COLORS['ncc_elec'], '--'),
    ('restructure_25pct_ncc_h2', '25% + H₂', COLORS['ncc_h2'], '-'),
    ('restructure_25pct_ncc_elec', '25% + Elec', COLORS['ncc_elec'], '--'),
    ('restructure_40pct_ncc_h2', '40% + H₂', COLORS['ncc_h2'], '-'),
    ('restructure_40pct_ncc_elec', '40% + Elec', COLORS['ncc_elec'], '--'),
]

# Plot actual emissions
for scenario_id, label, color, linestyle in all_scenarios:
    deployment = pd.read_csv(f'outputs/scenarios_{scenario_id}/module_03_optimization/policy_target_deployment.csv')

    ax1.plot(deployment['year'], deployment['actual_emissions_mt'],
             label=label, color=color, linestyle=linestyle, linewidth=1.5, alpha=0.8)

# Add BAU trajectories
shaheen_bau = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_01_baseline/bau_trajectory_2025_2050.csv')
ax1.plot(shaheen_bau['year'], shaheen_bau['total_emissions_mt'],
         label='BAU (Shaheen)', color='red', linestyle=':', linewidth=2)

restructure_25_bau = pd.read_csv('outputs/scenarios_restructure_25pct_ncc_h2/module_01_baseline/bau_trajectory_2025_2050.csv')
ax1.plot(restructure_25_bau['year'], restructure_25_bau['total_emissions_mt'],
         label='BAU (25%)', color='orange', linestyle=':', linewidth=2)

restructure_40_bau = pd.read_csv('outputs/scenarios_restructure_40pct_ncc_h2/module_01_baseline/bau_trajectory_2025_2050.csv')
ax1.plot(restructure_40_bau['year'], restructure_40_bau['total_emissions_mt'],
         label='BAU (40%)', color='green', linestyle=':', linewidth=2)

ax1.set_xlabel('Year', fontweight='bold')
ax1.set_ylabel('Emissions (MtCO₂)', fontweight='bold')
ax1.set_title('(a) Emissions Trajectories with Decarbonization', fontweight='bold', loc='left')
ax1.legend(loc='upper right', frameon=True, edgecolor='black', fontsize=7, ncol=2)
ax1.grid(alpha=0.3, linestyle='--')
ax1.set_ylim(0, 75)

# Abatement comparison
for scenario_id, label, color, linestyle in all_scenarios:
    deployment = pd.read_csv(f'outputs/scenarios_{scenario_id}/module_03_optimization/policy_target_deployment.csv')
    abatement = deployment['bau_mt'] - deployment['actual_emissions_mt']

    ax2.plot(deployment['year'], abatement,
             label=label, color=color, linestyle=linestyle, linewidth=1.5, alpha=0.8)

ax2.set_xlabel('Year', fontweight='bold')
ax2.set_ylabel('Annual Abatement (MtCO₂/year)', fontweight='bold')
ax2.set_title('(b) Annual Emissions Abatement', fontweight='bold', loc='left')
ax2.legend(loc='upper left', frameon=True, edgecolor='black', fontsize=7, ncol=2)
ax2.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure6_Emissions_Trajectories.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure6_Emissions_Trajectories.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure6_Emissions_Trajectories.png")

# ============================================================================
# FIGURE 7: Baseline Emissions Structure (2025)
# ============================================================================
print("[7/7] Figure 7: Baseline Emissions Structure...")

baseline = pd.read_csv('outputs/scenarios_shaheen_ncc_h2/module_01_baseline/baseline_2025_detailed.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# By product
product_emissions = baseline.groupby('product')['total_emissions_kt'].sum().sort_values(ascending=False)
top_products = product_emissions.head(10)

bars = ax1.barh(range(len(top_products)), top_products.values/1000,
                color=COLORS['ncc_h2'], edgecolor='black', linewidth=0.5)
ax1.set_yticks(range(len(top_products)))
ax1.set_yticklabels(top_products.index)
ax1.set_xlabel('Emissions (MtCO₂/year)', fontweight='bold')
ax1.set_title('(a) Baseline Emissions by Product (2025)', fontweight='bold', loc='left')
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
            f'{width:.1f}',
            ha='left', va='center', fontsize=8, fontweight='bold')

# By fuel type
fuel_columns = [col for col in baseline.columns if col.startswith('emissions_')]
fuel_totals = {}
for col in fuel_columns:
    fuel_name = col.replace('emissions_', '').replace('_kt', '').upper()
    fuel_totals[fuel_name] = baseline[col].sum() / 1000

fuel_df = pd.DataFrame(list(fuel_totals.items()), columns=['Fuel', 'Emissions'])
fuel_df = fuel_df.sort_values('Emissions', ascending=False)
fuel_df = fuel_df[fuel_df['Emissions'] > 0]

colors_fuel = plt.cm.Set3(range(len(fuel_df)))
wedges, texts, autotexts = ax2.pie(fuel_df['Emissions'], labels=fuel_df['Fuel'], autopct='%1.1f%%',
                                     colors=colors_fuel, startangle=90,
                                     textprops={'fontsize': 8, 'fontweight': 'bold'},
                                     wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})

for autotext in autotexts:
    autotext.set_color('black')

ax2.set_title('(b) Baseline Emissions by Fuel Type (2025)', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Figure7_Baseline_Structure.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'Figure7_Baseline_Structure.pdf', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: Figure7_Baseline_Structure.png")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*80)
print("FIGURE GENERATION COMPLETE")
print("="*80)
print(f"\nAll figures saved to: {OUTPUT_DIR}/")
print("\nGenerated figures:")
print("  1. Figure1_Six_Scenario_Comparison.png/pdf - Main cost comparison")
print("  2. Figure2_Technology_Deployment.png/pdf - Technology mix by scenario")
print("  3. Figure3_MACC_Curves.png/pdf - MACC evolution 2025-2050")
print("  4. Figure4_Cost_Evolution.png/pdf - Technology learning curves")
print("  5. Figure5_Hydrogen_Demand.png/pdf - H₂ demand trajectories")
print("  6. Figure6_Emissions_Trajectories.png/pdf - Emissions pathways")
print("  7. Figure7_Baseline_Structure.png/pdf - 2025 baseline breakdown")
print("\n✓ All figures are publication-ready at 300 DPI in PNG and PDF formats")
print("="*80)
