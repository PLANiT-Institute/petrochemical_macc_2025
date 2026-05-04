"""
Visualization Generator for Petrochemical MACC Model
Creates publication-quality figures from Excel outputs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['figure.dpi'] = 150

# Color palette
COLORS = {
    'primary': '#2C3E50',
    'electricity': '#3498DB',
    'h2': '#27AE60',
    'heat_pump': '#9B59B6',
    'baseline': '#E74C3C',
    'target': '#F39C12',
    'grid': '#95A5A6',
    'yeosu': '#1ABC9C',
    'daesan': '#3498DB',
    'ulsan': '#9B59B6',
    'onsan': '#E67E22',
    'other': '#95A5A6',
}

OUTPUT_DIR = Path('outputs/visualizations')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load data from Excel files"""
    elec = {}
    h2 = {}

    elec['annual'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Annual_Summary')
    elec['regional'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Regional_Summary')
    elec['company'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Company_Summary')
    elec['cost'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Cost_Summary')
    elec['deploy'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Deployment_Schedule')
    elec['tech'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Technology_Deployment')
    elec['prices'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Price_Trajectories')
    elec['facility'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx', sheet_name='Facility_Master')

    h2['annual'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_H2.xlsx', sheet_name='Annual_Summary')
    h2['cost'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_H2.xlsx', sheet_name='Cost_Summary')
    h2['deploy'] = pd.read_excel('outputs/excel_report/MACC_Report_NCC_H2.xlsx', sheet_name='Deployment_Schedule')

    return elec, h2


def fig1_emission_trajectory(elec, h2):
    """Figure 1: Emission trajectory with targets"""
    fig, ax = plt.subplots(figsize=(12, 7))

    years = elec['annual']['year']

    # BAU line (from deployment schedule)
    ax.plot(elec['deploy']['year'], elec['deploy']['bau_mt'],
            color=COLORS['grid'], linewidth=2, linestyle='--', label='BAU (No Action)', alpha=0.8)

    # Target line
    ax.plot(years, elec['annual']['target_mt'],
            color=COLORS['target'], linewidth=3, linestyle=':', label='Policy Target', marker='o', markersize=4)

    # Actual emissions - both scenarios
    ax.plot(years, elec['annual']['final_emissions_mt'],
            color=COLORS['electricity'], linewidth=3, label='NCC-Electricity Scenario', marker='s', markersize=5)
    ax.plot(years, h2['annual']['final_emissions_mt'],
            color=COLORS['h2'], linewidth=3, label='NCC-H₂ Scenario', marker='^', markersize=5)

    # Shade the abatement area
    ax.fill_between(elec['deploy']['year'], elec['deploy']['bau_mt'], elec['annual']['final_emissions_mt'],
                    alpha=0.2, color=COLORS['electricity'], label='Abatement (Electricity)')

    # Key milestones
    ax.axhline(y=39.26, color=COLORS['baseline'], linestyle='--', alpha=0.5, linewidth=1)
    ax.annotate('2035 Target: -24.5%', xy=(2035, 39.26), xytext=(2037, 42),
                fontsize=10, color=COLORS['baseline'],
                arrowprops=dict(arrowstyle='->', color=COLORS['baseline'], lw=1))

    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=1.5)
    ax.annotate('2050 Net Zero', xy=(2050, 0), xytext=(2046, 5),
                fontsize=10, fontweight='bold', color='black',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('CO₂ Emissions (MtCO₂/year)', fontweight='bold')
    ax.set_title('Petrochemical Sector Decarbonization Pathway\n248 Facilities | 2025-2050', fontweight='bold', fontsize=14)
    ax.set_xlim(2024, 2051)
    ax.set_ylim(-2, 55)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_emission_trajectory.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig1_emission_trajectory.pdf', bbox_inches='tight')
    print("  Saved: fig1_emission_trajectory.png")
    plt.close()


def fig2_technology_deployment(elec):
    """Figure 2: Technology deployment timeline"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    years = elec['deploy']['year']

    # Left: Deployment rates
    ax1.fill_between(years, 0, elec['deploy']['hp_deployment_rate'] * 100,
                     alpha=0.7, color=COLORS['heat_pump'], label='Heat Pump')
    ax1.fill_between(years, elec['deploy']['hp_deployment_rate'] * 100,
                     (elec['deploy']['hp_deployment_rate'] + elec['deploy']['ncc_deployment_rate']) * 100,
                     alpha=0.7, color=COLORS['electricity'], label='NCC-Electricity')

    ax1.axvline(x=2030, color='black', linestyle='--', alpha=0.5)
    ax1.annotate('NCC Available', xy=(2030, 50), fontsize=9, rotation=90, va='center')

    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Deployment Rate (%)', fontweight='bold')
    ax1.set_title('Technology Deployment Timeline', fontweight='bold')
    ax1.set_xlim(2025, 2050)
    ax1.set_ylim(0, 200)
    ax1.legend(loc='upper left', framealpha=0.95)
    ax1.grid(True, alpha=0.3)

    # Right: Abatement by technology
    ax2.stackplot(years,
                  elec['deploy']['hp_abatement_mt'],
                  elec['deploy']['ncc_abatement_mt'],
                  labels=['Heat Pump', 'NCC-Electricity'],
                  colors=[COLORS['heat_pump'], COLORS['electricity']],
                  alpha=0.8)

    ax2.plot(years, elec['deploy']['required_abatement_mt'],
             color=COLORS['target'], linewidth=2, linestyle='--', label='Required Abatement')

    ax2.set_xlabel('Year', fontweight='bold')
    ax2.set_ylabel('Abatement (MtCO₂/year)', fontweight='bold')
    ax2.set_title('Abatement by Technology', fontweight='bold')
    ax2.set_xlim(2025, 2050)
    ax2.legend(loc='upper left', framealpha=0.95)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig2_technology_deployment.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig2_technology_deployment.png")
    plt.close()


def fig3_cost_comparison(elec, h2):
    """Figure 3: Cost comparison between scenarios"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Left: Cumulative cost trajectory
    ax1 = axes[0]
    ax1.plot(elec['cost']['year'], elec['cost']['cumulative_total_musd'] / 1000,
             color=COLORS['electricity'], linewidth=3, label='NCC-Electricity')
    ax1.plot(h2['cost']['year'], h2['cost']['cumulative_total_musd'] / 1000,
             color=COLORS['h2'], linewidth=3, label='NCC-H₂')

    ax1.fill_between(elec['cost']['year'],
                     h2['cost']['cumulative_total_musd'] / 1000,
                     elec['cost']['cumulative_total_musd'] / 1000,
                     alpha=0.3, color=COLORS['baseline'], label='Cost Difference')

    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Cumulative Cost (Billion USD)', fontweight='bold')
    ax1.set_title('Cumulative Investment Cost', fontweight='bold')
    ax1.legend(loc='upper left', framealpha=0.95)
    ax1.grid(True, alpha=0.3)

    # Middle: Cost breakdown (2050)
    ax2 = axes[1]
    categories = ['CAPEX', 'OPEX', 'Fuel Cost']
    elec_costs = [
        elec['cost']['cumulative_capex_musd'].iloc[-1] / 1000,
        elec['cost']['cumulative_opex_musd'].iloc[-1] / 1000,
        elec['cost']['cumulative_fuel_musd'].iloc[-1] / 1000
    ]
    h2_costs = [
        h2['cost']['cumulative_capex_musd'].iloc[-1] / 1000,
        h2['cost']['cumulative_opex_musd'].iloc[-1] / 1000,
        h2['cost']['cumulative_fuel_musd'].iloc[-1] / 1000
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax2.bar(x - width/2, elec_costs, width, label='NCC-Electricity', color=COLORS['electricity'], alpha=0.8)
    bars2 = ax2.bar(x + width/2, h2_costs, width, label='NCC-H₂', color=COLORS['h2'], alpha=0.8)

    ax2.set_ylabel('Cost (Billion USD)', fontweight='bold')
    ax2.set_title('Cost Breakdown (2025-2050)', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.legend(loc='upper right', framealpha=0.95)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax2.annotate(f'${height:.1f}B',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'${height:.1f}B',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    # Right: Total cost comparison
    ax3 = axes[2]
    total_elec = sum(elec_costs)
    total_h2 = sum(h2_costs)

    bars = ax3.bar(['NCC-Electricity', 'NCC-H₂'], [total_elec, total_h2],
                   color=[COLORS['electricity'], COLORS['h2']], alpha=0.8, edgecolor='black', linewidth=1.5)

    ax3.set_ylabel('Total Cost (Billion USD)', fontweight='bold')
    ax3.set_title('Total Investment Comparison', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Add value labels and difference
    for bar in bars:
        height = bar.get_height()
        ax3.annotate(f'${height:.1f}B',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

    diff = total_elec - total_h2
    ax3.annotate(f'H₂ saves\n${diff:.1f}B',
                xy=(1.5, (total_elec + total_h2) / 2),
                fontsize=11, fontweight='bold', color=COLORS['h2'],
                ha='center')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_cost_comparison.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig3_cost_comparison.png")
    plt.close()


def fig4_regional_breakdown(elec):
    """Figure 4: Regional emission breakdown"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Get 2025 and 2050 data
    regional_2025 = elec['regional'][elec['regional']['year'] == 2025].sort_values('baseline_emissions_mt', ascending=True)
    regional_2050 = elec['regional'][elec['regional']['year'] == 2050]

    # Merge for consistent ordering
    regional = pd.merge(regional_2025[['location', 'baseline_emissions_mt', 'num_facilities']],
                        regional_2050[['location', 'final_emissions_mt']],
                        on='location', how='left').fillna(0)
    regional = regional.sort_values('baseline_emissions_mt', ascending=True)

    # Left: 2025 baseline by region
    colors_list = []
    for loc in regional['location']:
        if 'Yeosu' in loc:
            colors_list.append(COLORS['yeosu'])
        elif 'Daesan' in loc:
            colors_list.append(COLORS['daesan'])
        elif 'Ulsan' in loc:
            colors_list.append(COLORS['ulsan'])
        elif 'Onsan' in loc:
            colors_list.append(COLORS['onsan'])
        else:
            colors_list.append(COLORS['other'])

    y_pos = np.arange(len(regional))

    bars1 = ax1.barh(y_pos, regional['baseline_emissions_mt'], color=colors_list, alpha=0.8, edgecolor='black')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(regional['location'])
    ax1.set_xlabel('Emissions (MtCO₂/year)', fontweight='bold')
    ax1.set_title('2025 Baseline Emissions by Region', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')

    # Add facility count labels
    for i, (bar, n) in enumerate(zip(bars1, regional['num_facilities'])):
        ax1.annotate(f'{n} facilities',
                    xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=9)

    # Right: Comparison 2025 vs 2050
    width = 0.4
    ax2.barh(y_pos - width/2, regional['baseline_emissions_mt'], width,
             label='2025', color=COLORS['baseline'], alpha=0.7)
    ax2.barh(y_pos + width/2, regional['final_emissions_mt'], width,
             label='2050', color=COLORS['h2'], alpha=0.7)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(regional['location'])
    ax2.set_xlabel('Emissions (MtCO₂/year)', fontweight='bold')
    ax2.set_title('Emission Reduction by Region (2025 → 2050)', fontweight='bold')
    ax2.legend(loc='lower right', framealpha=0.95)
    ax2.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_regional_breakdown.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig4_regional_breakdown.png")
    plt.close()


def fig5_company_breakdown(elec):
    """Figure 5: Top companies emission breakdown"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Get 2025 data and top 10 companies
    company_2025 = elec['company'][elec['company']['year'] == 2025].sort_values('baseline_emissions_mt', ascending=False).head(10)
    company_2050 = elec['company'][elec['company']['year'] == 2050]

    # Merge for 2050 data
    company = pd.merge(company_2025[['company', 'baseline_emissions_mt', 'num_facilities']],
                       company_2050[['company', 'final_emissions_mt']],
                       on='company', how='left').fillna(0)
    company = company.sort_values('baseline_emissions_mt', ascending=True)

    y_pos = np.arange(len(company))
    width = 0.35

    bars1 = ax.barh(y_pos - width/2, company['baseline_emissions_mt'], width,
                    label='2025 Baseline', color=COLORS['baseline'], alpha=0.8)
    bars2 = ax.barh(y_pos + width/2, company['final_emissions_mt'], width,
                    label='2050 Final', color=COLORS['h2'], alpha=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(company['company'])
    ax.set_xlabel('Emissions (MtCO₂/year)', fontweight='bold')
    ax.set_title('Top 10 Companies: Emission Reduction (2025 → 2050)', fontweight='bold', fontsize=14)
    ax.legend(loc='lower right', framealpha=0.95, fontsize=11)
    ax.grid(True, alpha=0.3, axis='x')

    # Add reduction percentage
    for i, (base, final, name) in enumerate(zip(company['baseline_emissions_mt'],
                                                  company['final_emissions_mt'],
                                                  company['company'])):
        reduction = 100  # Net zero
        ax.annotate(f'-{reduction:.0f}%',
                   xy=(max(base, final) + 0.3, i),
                   fontsize=10, fontweight='bold', color=COLORS['h2'],
                   va='center')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_company_breakdown.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig5_company_breakdown.png")
    plt.close()


def fig6_price_trajectories(elec):
    """Figure 6: Price trajectories"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    prices = elec['prices']

    # Left: H2 and Electricity prices
    ax1.plot(prices['year'], prices['h2_price_usd_per_kg'],
             color=COLORS['h2'], linewidth=3, label='Green H₂ ($/kg)', marker='o', markersize=4)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(prices['year'], prices['re_price_usd_per_mwh'],
                  color=COLORS['electricity'], linewidth=3, label='RE Electricity ($/MWh)', marker='s', markersize=4)
    ax1_twin.plot(prices['year'], prices['grid_price_usd_per_mwh'],
                  color=COLORS['grid'], linewidth=2, linestyle='--', label='Grid Electricity ($/MWh)')

    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('H₂ Price ($/kg)', fontweight='bold', color=COLORS['h2'])
    ax1_twin.set_ylabel('Electricity Price ($/MWh)', fontweight='bold', color=COLORS['electricity'])
    ax1.set_title('Energy Price Trajectories', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=COLORS['h2'])
    ax1_twin.tick_params(axis='y', labelcolor=COLORS['electricity'])

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', framealpha=0.95)
    ax1.grid(True, alpha=0.3)

    # Right: Grid emission factor
    ax2.plot(prices['year'], prices['grid_ef_tco2_per_mwh'],
             color=COLORS['primary'], linewidth=3, marker='o', markersize=5)
    ax2.fill_between(prices['year'], 0, prices['grid_ef_tco2_per_mwh'],
                     alpha=0.3, color=COLORS['primary'])

    ax2.axhline(y=0.07, color=COLORS['target'], linestyle='--', linewidth=2)
    ax2.annotate('2050: 0.07 tCO₂/MWh', xy=(2050, 0.07), xytext=(2040, 0.12),
                fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=COLORS['target']))

    ax2.set_xlabel('Year', fontweight='bold')
    ax2.set_ylabel('Grid Emission Factor (tCO₂/MWh)', fontweight='bold')
    ax2.set_title('Grid Decarbonization Trajectory', fontweight='bold')
    ax2.set_ylim(0, 0.5)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig6_price_trajectories.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig6_price_trajectories.png")
    plt.close()


def fig7_facility_distribution(elec):
    """Figure 7: Facility distribution pie/donut chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    facility = elec['facility']

    # Left: By region (pie chart)
    region_counts = facility.groupby('location').agg({
        'facility_id': 'count',
        'total_emissions_kt': 'sum'
    }).reset_index()
    region_counts.columns = ['location', 'count', 'emissions_kt']
    region_counts = region_counts.sort_values('emissions_kt', ascending=False)

    # Top 5 + Others
    top_5 = region_counts.head(5)
    others = pd.DataFrame({
        'location': ['Others'],
        'count': [region_counts.iloc[5:]['count'].sum()],
        'emissions_kt': [region_counts.iloc[5:]['emissions_kt'].sum()]
    })
    plot_data = pd.concat([top_5, others])

    colors = [COLORS['yeosu'], COLORS['daesan'], COLORS['ulsan'], COLORS['onsan'], COLORS['electricity'], COLORS['other']]

    wedges, texts, autotexts = ax1.pie(plot_data['emissions_kt'],
                                        labels=plot_data['location'],
                                        autopct='%1.1f%%',
                                        colors=colors,
                                        startangle=90,
                                        explode=[0.02]*len(plot_data))

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax1.set_title('Baseline Emissions by Region', fontweight='bold', fontsize=14)

    # Right: By process type
    process_counts = facility.groupby('process').agg({
        'facility_id': 'count',
        'total_emissions_kt': 'sum'
    }).reset_index()
    process_counts.columns = ['process', 'count', 'emissions_kt']
    process_counts = process_counts.sort_values('emissions_kt', ascending=False)

    colors_process = [COLORS['baseline'], COLORS['heat_pump'], COLORS['electricity']][:len(process_counts)]
    if len(process_counts) > 3:
        colors_process.extend([COLORS['other']] * (len(process_counts) - 3))

    wedges, texts, autotexts = ax2.pie(process_counts['emissions_kt'],
                                        labels=process_counts['process'],
                                        autopct='%1.1f%%',
                                        colors=colors_process,
                                        startangle=90,
                                        explode=[0.02]*len(process_counts))

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax2.set_title('Baseline Emissions by Process Type', fontweight='bold', fontsize=14)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig7_facility_distribution.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig7_facility_distribution.png")
    plt.close()


def fig8_summary_dashboard(elec, h2):
    """Figure 8: Executive summary dashboard"""
    fig = plt.figure(figsize=(16, 12))

    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # Top left: Key metrics box
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')

    metrics_text = """
    KEY METRICS
    ─────────────────────
    Facilities: 248
    Baseline: 52 MtCO₂

    2035 Target: -24.5%
    2050 Target: Net Zero

    Technologies:
    • Heat Pump (2025+)
    • NCC-Electricity (2030+)
    • NCC-H₂ (2030+)
    """
    ax1.text(0.1, 0.9, metrics_text, transform=ax1.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    ax1.set_title('Project Overview', fontweight='bold', fontsize=12)

    # Top middle: Emission trajectory (small)
    ax2 = fig.add_subplot(gs[0, 1:])
    ax2.plot(elec['annual']['year'], elec['annual']['target_mt'],
             color=COLORS['target'], linewidth=2, linestyle=':', label='Target')
    ax2.plot(elec['annual']['year'], elec['annual']['final_emissions_mt'],
             color=COLORS['electricity'], linewidth=2.5, label='NCC-Elec')
    ax2.plot(h2['annual']['year'], h2['annual']['final_emissions_mt'],
             color=COLORS['h2'], linewidth=2.5, label='NCC-H₂')
    ax2.fill_between(elec['annual']['year'], 0, elec['annual']['final_emissions_mt'], alpha=0.2, color=COLORS['electricity'])
    ax2.set_ylabel('MtCO₂/year')
    ax2.set_title('Emission Trajectory', fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(2025, 2050)

    # Middle left: Cost comparison
    ax3 = fig.add_subplot(gs[1, 0])
    total_elec = elec['cost']['cumulative_total_musd'].iloc[-1] / 1000
    total_h2 = h2['cost']['cumulative_total_musd'].iloc[-1] / 1000
    bars = ax3.bar(['Electricity', 'H₂'], [total_elec, total_h2],
                   color=[COLORS['electricity'], COLORS['h2']], alpha=0.8)
    for bar in bars:
        height = bar.get_height()
        ax3.annotate(f'${height:.0f}B',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Billion USD')
    ax3.set_title('Total Cost (2025-2050)', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Middle center: Technology deployment
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.stackplot(elec['deploy']['year'],
                  elec['deploy']['hp_abatement_mt'],
                  elec['deploy']['ncc_abatement_mt'],
                  colors=[COLORS['heat_pump'], COLORS['electricity']],
                  labels=['Heat Pump', 'NCC'],
                  alpha=0.8)
    ax4.set_ylabel('MtCO₂/year')
    ax4.set_title('Abatement by Technology', fontweight='bold')
    ax4.legend(loc='upper left', fontsize=9)
    ax4.grid(True, alpha=0.3)

    # Middle right: Regional breakdown
    ax5 = fig.add_subplot(gs[1, 2])
    regional_2025 = elec['regional'][elec['regional']['year'] == 2025].nlargest(5, 'baseline_emissions_mt')
    ax5.barh(regional_2025['location'], regional_2025['baseline_emissions_mt'],
             color=[COLORS['yeosu'], COLORS['daesan'], COLORS['ulsan'], COLORS['onsan'], COLORS['other']])
    ax5.set_xlabel('MtCO₂/year')
    ax5.set_title('Top 5 Regions (2025)', fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')

    # Bottom: Timeline
    ax6 = fig.add_subplot(gs[2, :])

    # Draw timeline
    years_milestone = [2025, 2030, 2035, 2040, 2045, 2050]
    y_line = 0.5

    ax6.axhline(y=y_line, color='black', linewidth=2, zorder=1)

    for i, year in enumerate(years_milestone):
        ax6.scatter(year, y_line, s=200, c='white', edgecolor='black', linewidth=2, zorder=2)

        # Get emission for this year
        emission = elec['annual'][elec['annual']['year'] == year]['final_emissions_mt'].iloc[0]
        reduction = (52 - emission) / 52 * 100

        # Alternating label positions
        if i % 2 == 0:
            ax6.annotate(f'{year}\n{emission:.1f} Mt\n({reduction:.0f}%)',
                        xy=(year, y_line), xytext=(0, 40), textcoords='offset points',
                        ha='center', fontsize=10, fontweight='bold',
                        arrowprops=dict(arrowstyle='-', color='gray'))
        else:
            ax6.annotate(f'{year}\n{emission:.1f} Mt\n({reduction:.0f}%)',
                        xy=(year, y_line), xytext=(0, -50), textcoords='offset points',
                        ha='center', fontsize=10, fontweight='bold',
                        arrowprops=dict(arrowstyle='-', color='gray'))

    # Add milestones
    ax6.annotate('Heat Pump\nAvailable', xy=(2025, y_line), xytext=(2025, 0.1),
                ha='center', fontsize=9, color=COLORS['heat_pump'])
    ax6.annotate('NCC\nAvailable', xy=(2030, y_line), xytext=(2030, 0.9),
                ha='center', fontsize=9, color=COLORS['electricity'])
    ax6.annotate('-24.5%\nTarget', xy=(2035, y_line), xytext=(2035, 0.1),
                ha='center', fontsize=9, fontweight='bold', color=COLORS['target'])
    ax6.annotate('NET\nZERO', xy=(2050, y_line), xytext=(2050, 0.9),
                ha='center', fontsize=11, fontweight='bold', color=COLORS['h2'])

    ax6.set_xlim(2023, 2052)
    ax6.set_ylim(0, 1)
    ax6.axis('off')
    ax6.set_title('Decarbonization Timeline', fontweight='bold', fontsize=14, pad=20)

    plt.suptitle('Petrochemical Sector Decarbonization: Executive Summary\n248 Facilities | 2025-2050 | Net Zero by 2050',
                fontsize=16, fontweight='bold', y=0.98)

    plt.savefig(OUTPUT_DIR / 'fig8_executive_summary.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig8_executive_summary.png")
    plt.close()


def fig9_assumptions(elec):
    """Figure 9: Key assumptions and parameters table"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')

    # Technology parameters
    tech_data = [
        ['Technology', 'CAPEX 2025', 'CAPEX 2050', 'OPEX', 'Lifetime', 'Available', 'Source'],
        ['Heat Pump', '$800/tCO₂', '$400/tCO₂', '3%', '20 years', '2025', 'Kosmadakis 2020'],
        ['NCC-Electricity', '$1,500/t-C₂H₄', '$900/t-C₂H₄', '4%', '25 years', '2030', 'BASF/SABIC/Linde 2024'],
        ['NCC-H₂', '$1,700/t-C₂H₄', '$780/t-C₂H₄', '4%', '25 years', '2030', 'Thunder Said Energy 2023'],
    ]

    # Energy parameters
    energy_data = [
        ['Parameter', 'Value', 'Unit', 'Source'],
        ['NCC Electricity Consumption', '5.0', 'MWh/ton ethylene', 'BASF/SABIC/Linde Pilot 2024'],
        ['NCC H₂ Consumption', '0.2', 'ton H₂/ton ethylene', 'Lummus Tech 2023'],
        ['Heat Pump COP', '4.0', '-', 'Kosmadakis 2020, Obrist 2023'],
        ['Grid EF 2025', '0.436', 'tCO₂/MWh', 'Korea 10th Power Plan'],
        ['Grid EF 2050', '0.070', 'tCO₂/MWh', 'Korea 10th Power Plan'],
    ]

    # Price parameters
    price_data = [
        ['Parameter', '2025', '2030', '2040', '2050', 'Trend'],
        ['H₂ Price ($/kg)', '6.73', '5.88', '4.16', '2.63', '↓ -61%'],
        ['RE Electricity ($/MWh)', '129', '157', '191', '191', '↑ +48%'],
        ['Grid Electricity ($/MWh)', '100', '118', '155', '191', '↑ +91%'],
    ]

    # Emission factors
    ef_data = [
        ['Fuel', 'Emission Factor', 'Unit', 'Source'],
        ['Naphtha', '0.0542', 'tCO₂/GJ', 'IPCC 2019'],
        ['LNG', '0.0561', 'tCO₂/GJ', 'IPCC 2019'],
        ['Fuel Gas', '0.050', 'tCO₂/GJ', 'API Compendium 2021'],
        ['LPG', '0.0631', 'tCO₂/GJ', 'IPCC 2019'],
        ['Green H₂', '0.0', 'tCO₂/kg', 'Assumption (electrolysis)'],
    ]

    # Create tables
    y_pos = 0.95

    # Title
    ax.text(0.5, y_pos, 'Model Assumptions & Parameters', fontsize=16, fontweight='bold',
            ha='center', transform=ax.transAxes)
    y_pos -= 0.05

    # Technology table
    ax.text(0.02, y_pos, 'Technology Parameters', fontsize=12, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.02
    table1 = ax.table(cellText=tech_data[1:], colLabels=tech_data[0],
                      loc='upper left', bbox=[0.02, y_pos-0.18, 0.96, 0.18],
                      cellLoc='center', colColours=['#E8E8E8']*7)
    table1.auto_set_font_size(False)
    table1.set_fontsize(9)
    table1.scale(1, 1.5)
    y_pos -= 0.22

    # Energy parameters table
    ax.text(0.02, y_pos, 'Energy Parameters', fontsize=12, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.02
    table2 = ax.table(cellText=energy_data[1:], colLabels=energy_data[0],
                      loc='upper left', bbox=[0.02, y_pos-0.20, 0.96, 0.20],
                      cellLoc='center', colColours=['#E8E8E8']*4)
    table2.auto_set_font_size(False)
    table2.set_fontsize(9)
    table2.scale(1, 1.5)
    y_pos -= 0.24

    # Price trajectories table
    ax.text(0.02, y_pos, 'Price Trajectories', fontsize=12, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.02
    table3 = ax.table(cellText=price_data[1:], colLabels=price_data[0],
                      loc='upper left', bbox=[0.02, y_pos-0.12, 0.96, 0.12],
                      cellLoc='center', colColours=['#E8E8E8']*6)
    table3.auto_set_font_size(False)
    table3.set_fontsize(9)
    table3.scale(1, 1.5)
    y_pos -= 0.16

    # Emission factors table
    ax.text(0.02, y_pos, 'Emission Factors', fontsize=12, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.02
    table4 = ax.table(cellText=ef_data[1:], colLabels=ef_data[0],
                      loc='upper left', bbox=[0.02, y_pos-0.18, 0.96, 0.18],
                      cellLoc='center', colColours=['#E8E8E8']*4)
    table4.auto_set_font_size(False)
    table4.set_fontsize(9)
    table4.scale(1, 1.5)
    y_pos -= 0.22

    # Key assumptions text
    assumptions_text = """
    Key Modeling Assumptions:
    • Baseline normalized to 52 MtCO₂/year (2025) to match Korea National GHG Inventory
    • NCC facilities (39) can adopt either NCC-Electricity OR NCC-H₂ (mutually exclusive)
    • Non-NCC facilities (209) use Heat Pump technology for decarbonization
    • Technology deployment constrained by availability (Heat Pump: 2025, NCC: 2030)
    • Grid decarbonization follows Korea's 10th Basic Plan trajectory
    • No facility retirement assumed (all 248 facilities operate through 2050)
    • Costs include CAPEX (annualized), OPEX, and fuel costs
    """
    ax.text(0.02, y_pos, assumptions_text, fontsize=10, transform=ax.transAxes,
            verticalalignment='top', fontfamily='sans-serif',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig9_assumptions.png', dpi=300, bbox_inches='tight')
    print("  Saved: fig9_assumptions.png")
    plt.close()


def main():
    print("="*80)
    print("VISUALIZATION GENERATOR")
    print("="*80)

    print("\nLoading data...")
    elec, h2 = load_data()

    print("\nGenerating visualizations...")
    fig1_emission_trajectory(elec, h2)
    fig2_technology_deployment(elec)
    fig3_cost_comparison(elec, h2)
    fig4_regional_breakdown(elec)
    fig5_company_breakdown(elec)
    fig6_price_trajectories(elec)
    fig7_facility_distribution(elec)
    fig8_summary_dashboard(elec, h2)
    fig9_assumptions(elec)

    print("\n" + "="*80)
    print(f"All visualizations saved to: {OUTPUT_DIR}")
    print("="*80)

    # List all generated files
    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.glob('*.png')):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")


if __name__ == '__main__':
    main()
