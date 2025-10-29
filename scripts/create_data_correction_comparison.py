"""
Create Comprehensive Before/After Data Correction Comparison
Shows impact of corrected emission factors and prices
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11

def load_data():
    """Load original and corrected results"""
    data = {}

    # Original results
    try:
        data['baseline_orig'] = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')
        data['bau_orig'] = pd.read_csv('outputs/module_01/bau_trajectory_2025_2050.csv')
        data['macc_orig'] = pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv')
        data['deploy_orig'] = pd.read_csv('outputs/module_03/policy_target_deployment.csv')
    except FileNotFoundError as e:
        print(f"⚠️  Could not load original results: {e}")
        data['baseline_orig'] = None

    # Corrected results
    try:
        data['baseline_corr'] = pd.read_csv('outputs/module_01_corrected/baseline_2025_detailed.csv')
        data['bau_corr'] = pd.read_csv('outputs/module_01_corrected/bau_trajectory_2025_2050.csv')
        data['macc_corr'] = pd.read_csv('outputs/module_02_corrected/macc_annual_2025_2050.csv')
        data['deploy_corr'] = pd.read_csv('outputs/module_03_corrected/policy_target_deployment.csv')
    except FileNotFoundError as e:
        print(f"⚠️  Could not load corrected results: {e}")
        data['baseline_corr'] = None

    return data

def create_comprehensive_comparison():
    """Create all comparison visualizations"""

    print("="*80)
    print("CREATING DATA CORRECTION COMPARISON VISUALIZATIONS")
    print("="*80)

    data = load_data()

    if data['baseline_orig'] is None or data['baseline_corr'] is None:
        print("\n⚠️  Missing data - cannot create comparisons")
        return

    # Create output directory
    output_dir = Path('outputs/data_correction_comparison')
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Figure 1: Baseline Emissions Comparison
    # ========================================================================
    print("\n1. Creating baseline emissions comparison...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('Impact of Data Corrections on Baseline Emissions (2025)',
                 fontsize=18, fontweight='bold', y=0.995)

    # 1.1: Total emissions bar chart
    baseline_orig_total = data['baseline_orig']['total_emissions_kt'].sum() / 1000
    baseline_corr_total = data['baseline_corr']['total_emissions_kt'].sum() / 1000

    bars = ax1.bar(['Original\n(Wrong EF)', 'Corrected\n(Right EF)'],
                   [baseline_orig_total, baseline_corr_total],
                   color=['#E74C3C', '#27AE60'], alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Total Emissions (MtCO2)', fontsize=13, fontweight='bold')
    ax1.set_title('Total Baseline Emissions', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, max(baseline_orig_total, baseline_corr_total) * 1.15)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}\nMtCO2',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add change annotation
    change = baseline_corr_total - baseline_orig_total
    change_pct = (change / baseline_orig_total) * 100
    ax1.text(0.5, baseline_orig_total + (baseline_corr_total - baseline_orig_total)/2,
            f'+{change:.1f} MtCO2\n(+{change_pct:.1f}%)',
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    # 1.2: Fuel-by-fuel comparison
    fuels = ['naphtha', 'lng', 'fuel_gas', 'electricity', 'lpg', 'fuel_oil']
    fuel_labels = ['Naphtha', 'LNG', 'Fuel Gas', 'Electricity', 'LPG', 'Fuel Oil']

    orig_by_fuel = []
    corr_by_fuel = []

    for fuel in fuels:
        orig_by_fuel.append(data['baseline_orig'][f'emissions_{fuel}_kt'].sum() / 1000)
        corr_by_fuel.append(data['baseline_corr'][f'emissions_{fuel}_kt'].sum() / 1000)

    x = np.arange(len(fuel_labels))
    width = 0.35

    bars1 = ax2.bar(x - width/2, orig_by_fuel, width, label='Original',
                    color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax2.bar(x + width/2, corr_by_fuel, width, label='Corrected',
                    color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax2.set_ylabel('Emissions (MtCO2)', fontsize=13, fontweight='bold')
    ax2.set_title('Emissions by Fuel Type', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(fuel_labels, rotation=45, ha='right')
    ax2.legend(loc='upper right', fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')

    # 1.3: BAU trajectory comparison
    ax3.plot(data['bau_orig']['year'], data['bau_orig']['total_emissions_mt'],
            linewidth=3, color='#E74C3C', marker='o', markersize=5,
            label='Original BAU', alpha=0.8)
    ax3.plot(data['bau_corr']['year'], data['bau_corr']['total_emissions_mt'],
            linewidth=3, color='#27AE60', marker='s', markersize=5,
            label='Corrected BAU', alpha=0.8)

    ax3.fill_between(data['bau_orig']['year'],
                     data['bau_orig']['total_emissions_mt'],
                     data['bau_corr']['total_emissions_mt'],
                     alpha=0.2, color='orange',
                     label='Difference')

    ax3.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Emissions (MtCO2/year)', fontsize=13, fontweight='bold')
    ax3.set_title('BAU Trajectory Comparison (2025-2050)', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=11)
    ax3.grid(True, alpha=0.3)

    # 1.4: Summary table
    ax4.axis('off')

    summary_data = [
        ['Metric', 'Original', 'Corrected', 'Change'],
        ['Baseline 2025 (MtCO2)', f'{baseline_orig_total:.1f}', f'{baseline_corr_total:.1f}',
         f'+{change:.1f} (+{change_pct:.1f}%)'],
        ['BAU 2050 (MtCO2)',
         f"{data['bau_orig'][data['bau_orig']['year']==2050]['total_emissions_mt'].iloc[0]:.1f}",
         f"{data['bau_corr'][data['bau_corr']['year']==2050]['total_emissions_mt'].iloc[0]:.1f}",
         f"+{data['bau_corr'][data['bau_corr']['year']==2050]['total_emissions_mt'].iloc[0] - data['bau_orig'][data['bau_orig']['year']==2050]['total_emissions_mt'].iloc[0]:.1f}"],
        ['', '', '', ''],
        ['Data Corrections:', '', '', ''],
        ['LNG Emission Factor', '0.0149', '0.0561 tCO2/GJ', '+276%'],
        ['Fuel Gas EF', '0.0149', '0.050 tCO2/GJ', '+235%'],
        ['H2 Price (2030)', '$10.00/kg', '$3.50/kg', '-65%'],
        ['RE Price (2030)', '$115/MWh', '$75/MWh', '-35%'],
    ]

    table = ax4.table(cellText=summary_data, cellLoc='left',
                     bbox=[0.1, 0.1, 0.8, 0.8])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Header row styling
    for i in range(4):
        table[(0, i)].set_facecolor('#3498DB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Highlight correction rows
    for i in range(5, 9):
        table[(i, 3)].set_facecolor('#FFFFCC')

    ax4.set_title('Summary of Changes', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_dir / 'baseline_emissions_comparison.png', dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: baseline_emissions_comparison.png")
    plt.close()

    # ========================================================================
    # Figure 2: Technology Cost Comparison
    # ========================================================================
    print("\n2. Creating technology cost comparison...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('Impact of Data Corrections on Technology Costs',
                 fontsize=18, fontweight='bold', y=0.995)

    # 2.1: 2030 cost comparison
    technologies = ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']
    tech_labels = ['Heat Pump', 'NCC-H2', 'NCC-Electricity', 'RE PPA']

    macc_orig_2030 = data['macc_orig'][data['macc_orig']['year'] == 2030]
    macc_corr_2030 = data['macc_corr'][data['macc_corr']['year'] == 2030]

    costs_orig = []
    costs_corr = []

    for tech in technologies:
        orig_cost = macc_orig_2030[macc_orig_2030['technology'] == tech]['total_cost_usd_per_tco2'].iloc[0]
        corr_cost = macc_corr_2030[macc_corr_2030['technology'] == tech]['total_cost_usd_per_tco2'].iloc[0]
        costs_orig.append(orig_cost)
        costs_corr.append(corr_cost)

    x = np.arange(len(tech_labels))
    width = 0.35

    bars1 = ax1.bar(x - width/2, costs_orig, width, label='Original',
                    color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax1.bar(x + width/2, costs_corr, width, label='Corrected',
                    color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax1.set_ylabel('MACC ($/tCO2)', fontsize=13, fontweight='bold')
    ax1.set_title('Technology Costs - 2030', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tech_labels, rotation=45, ha='right')
    ax1.legend(loc='upper right', fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.0f}',
                    ha='center', va='bottom', fontsize=9, rotation=90)

    # 2.2: Cost evolution - NCC-H2
    for tech, label, color in [('NCC-H2', 'NCC-H2', '#3498DB'), ('NCC-Electricity', 'NCC-Electricity', '#E74C3C')]:
        macc_orig_tech = data['macc_orig'][data['macc_orig']['technology'] == tech]
        macc_corr_tech = data['macc_corr'][data['macc_corr']['technology'] == tech]

        ax2.plot(macc_orig_tech['year'], macc_orig_tech['total_cost_usd_per_tco2'],
                linewidth=2.5, linestyle='--', marker='o', markersize=5,
                label=f'{label} (Original)', color=color, alpha=0.6)
        ax2.plot(macc_corr_tech['year'], macc_corr_tech['total_cost_usd_per_tco2'],
                linewidth=2.5, marker='s', markersize=5,
                label=f'{label} (Corrected)', color=color, alpha=1.0)

    ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax2.set_ylabel('MACC ($/tCO2)', fontsize=13, fontweight='bold')
    ax2.set_title('NCC Technology Cost Evolution', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 2.3: Percentage change in costs
    pct_changes = []
    for i in range(len(technologies)):
        if costs_orig[i] > 0:
            pct_change = ((costs_corr[i] - costs_orig[i]) / costs_orig[i]) * 100
        else:
            pct_change = 0
        pct_changes.append(pct_change)

    colors = ['#27AE60' if x < 0 else '#E74C3C' for x in pct_changes]
    bars = ax3.barh(tech_labels, pct_changes, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax3.set_xlabel('Cost Change (%)', fontsize=13, fontweight='bold')
    ax3.set_title('Percentage Change in Technology Costs (2030)', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, (bar, pct) in enumerate(zip(bars, pct_changes)):
        ax3.text(pct + (5 if pct > 0 else -5), i,
                f'{pct:+.1f}%',
                ha='left' if pct > 0 else 'right', va='center',
                fontsize=11, fontweight='bold')

    # 2.4: Cost breakdown comparison for NCC-Electricity
    ncc_elec_orig = macc_orig_2030[macc_orig_2030['technology'] == 'NCC-Electricity'].iloc[0]
    ncc_elec_corr = macc_corr_2030[macc_corr_2030['technology'] == 'NCC-Electricity'].iloc[0]

    categories = ['CAPEX\n(annual)', 'OPEX\n(annual)', 'Fuel Cost\n(differential)', 'TOTAL']
    orig_breakdown = [
        ncc_elec_orig['capex_ann_usd_per_tco2'],
        ncc_elec_orig['opex_ann_usd_per_tco2'],
        ncc_elec_orig['fuel_cost_diff_usd_per_tco2'],
        ncc_elec_orig['total_cost_usd_per_tco2']
    ]
    corr_breakdown = [
        ncc_elec_corr['capex_ann_usd_per_tco2'],
        ncc_elec_corr['opex_ann_usd_per_tco2'],
        ncc_elec_corr['fuel_cost_diff_usd_per_tco2'],
        ncc_elec_corr['total_cost_usd_per_tco2']
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax4.bar(x - width/2, orig_breakdown, width, label='Original',
                    color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax4.bar(x + width/2, corr_breakdown, width, label='Corrected',
                    color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax4.set_ylabel('Cost ($/tCO2)', fontsize=13, fontweight='bold')
    ax4.set_title('NCC-Electricity Cost Breakdown (2030)', fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories)
    ax4.legend(loc='upper left', fontsize=11)
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'technology_cost_comparison.png', dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: technology_cost_comparison.png")
    plt.close()

    # ========================================================================
    # Figure 3: Deployment and Results Comparison
    # ========================================================================
    print("\n3. Creating deployment comparison...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('Impact of Data Corrections on Model Results (Policy Target Scenario)',
                 fontsize=18, fontweight='bold', y=0.995)

    # 3.1: 2050 deployment comparison
    deploy_orig_2050 = data['deploy_orig'][data['deploy_orig']['year'] == 2050].iloc[0]
    deploy_corr_2050 = data['deploy_corr'][data['deploy_corr']['year'] == 2050].iloc[0]

    tech_deploy = ['heat_pump_mt', 'ncc_h2_mt', 'ncc_elec_mt', 're_ppa_mt']
    tech_labels_deploy = ['Heat Pump', 'NCC-H2', 'NCC-Electricity', 'RE PPA']

    orig_deploy = [deploy_orig_2050[t] for t in tech_deploy]
    corr_deploy = [deploy_corr_2050[t] for t in tech_deploy]

    x = np.arange(len(tech_labels_deploy))
    width = 0.35

    bars1 = ax1.bar(x - width/2, orig_deploy, width, label='Original',
                    color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax1.bar(x + width/2, corr_deploy, width, label='Corrected',
                    color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax1.set_ylabel('Abatement (MtCO2/year)', fontsize=13, fontweight='bold')
    ax1.set_title('2050 Technology Deployment', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tech_labels_deploy, rotation=45, ha='right')
    ax1.legend(loc='upper right', fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')

    # 3.2: Emission trajectory comparison
    ax2.plot(data['bau_orig']['year'], data['bau_orig']['total_emissions_mt'],
            label='BAU (Original)', color='gray', linestyle='--', linewidth=2.5, alpha=0.6)
    ax2.plot(data['bau_corr']['year'], data['bau_corr']['total_emissions_mt'],
            label='BAU (Corrected)', color='black', linestyle='--', linewidth=2.5)
    ax2.plot(data['deploy_orig']['year'], data['deploy_orig']['actual_emissions_mt'],
            label='With Abatement (Original)', color='#E74C3C', linewidth=3, marker='o', markersize=4)
    ax2.plot(data['deploy_corr']['year'], data['deploy_corr']['actual_emissions_mt'],
            label='With Abatement (Corrected)', color='#27AE60', linewidth=3, marker='s', markersize=4)

    # Target line
    ax2.plot(data['deploy_orig']['year'], data['deploy_orig']['target_mt'],
            label='Target', color='red', linestyle=':', linewidth=2.5)

    ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Emissions (MtCO2/year)', fontsize=13, fontweight='bold')
    ax2.set_title('Emission Trajectory Comparison', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 3.3: Key metrics comparison
    metrics = ['Baseline\n2025', 'BAU\n2050', 'Target\n2050', 'Actual\n2050', 'Reduction\n%', 'Investment\n(B$)']

    orig_metrics = [
        baseline_orig_total,
        deploy_orig_2050['bau_mt'],
        deploy_orig_2050['target_mt'],
        deploy_orig_2050['actual_emissions_mt'],
        (1 - deploy_orig_2050['actual_emissions_mt'] / deploy_orig_2050['bau_mt']) * 100,
        deploy_orig_2050['cumulative_capex_musd'] / 1000
    ]

    corr_metrics = [
        baseline_corr_total,
        deploy_corr_2050['bau_mt'],
        deploy_corr_2050['target_mt'],
        deploy_corr_2050['actual_emissions_mt'],
        (1 - deploy_corr_2050['actual_emissions_mt'] / deploy_corr_2050['bau_mt']) * 100,
        deploy_corr_2050['cumulative_capex_musd'] / 1000
    ]

    x = np.arange(len(metrics))
    width = 0.35

    # Different scaling for different metrics
    ax3_main = ax3
    ax3_twin = ax3.twinx()

    # Plot first 4 metrics on main axis (MtCO2)
    bars1_main = ax3_main.bar(x[:4] - width/2, orig_metrics[:4], width, label='Original',
                              color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2_main = ax3_main.bar(x[:4] + width/2, corr_metrics[:4], width, label='Corrected',
                              color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    # Plot last 2 metrics on twin axis (% and $B)
    bars1_twin = ax3_twin.bar(x[4:] - width/2, orig_metrics[4:], width,
                              color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2_twin = ax3_twin.bar(x[4:] + width/2, corr_metrics[4:], width,
                              color='#27AE60', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax3_main.set_ylabel('Emissions (MtCO2)', fontsize=13, fontweight='bold', color='black')
    ax3_twin.set_ylabel('Reduction (%) / Investment ($B)', fontsize=13, fontweight='bold', color='blue')
    ax3_main.set_title('Key Metrics Comparison', fontsize=14, fontweight='bold')
    ax3_main.set_xticks(x)
    ax3_main.set_xticklabels(metrics, rotation=45, ha='right')
    ax3_main.legend(loc='upper left', fontsize=11)
    ax3_main.grid(True, alpha=0.3, axis='y')

    # 3.4: Summary table
    ax4.axis('off')

    summary_data_2 = [
        ['Metric', 'Original', 'Corrected', 'Change'],
        ['', '', '', ''],
        ['2050 Results:', '', '', ''],
        ['Total Abatement (MtCO2)',
         f"{deploy_orig_2050['total_deployed_mt']:.1f}",
         f"{deploy_corr_2050['total_deployed_mt']:.1f}",
         f"{deploy_corr_2050['total_deployed_mt'] - deploy_orig_2050['total_deployed_mt']:+.1f}"],
        ['Actual Emissions (MtCO2)',
         f"{deploy_orig_2050['actual_emissions_mt']:.1f}",
         f"{deploy_corr_2050['actual_emissions_mt']:.1f}",
         f"{deploy_corr_2050['actual_emissions_mt'] - deploy_orig_2050['actual_emissions_mt']:+.1f}"],
        ['Reduction Rate (%)',
         f"{(1 - deploy_orig_2050['actual_emissions_mt']/deploy_orig_2050['bau_mt'])*100:.1f}%",
         f"{(1 - deploy_corr_2050['actual_emissions_mt']/deploy_corr_2050['bau_mt'])*100:.1f}%",
         f"{((1 - deploy_corr_2050['actual_emissions_mt']/deploy_corr_2050['bau_mt']) - (1 - deploy_orig_2050['actual_emissions_mt']/deploy_orig_2050['bau_mt']))*100:+.1f} pp"],
        ['Investment ($B)',
         f"${deploy_orig_2050['cumulative_capex_musd']/1000:.1f}",
         f"${deploy_corr_2050['cumulative_capex_musd']/1000:.1f}",
         f"${(deploy_corr_2050['cumulative_capex_musd'] - deploy_orig_2050['cumulative_capex_musd'])/1000:+.1f}"],
        ['', '', '', ''],
        ['Key Insight:', '', '', ''],
        ['Higher baseline (+27%)', 'BUT', 'Cheaper tech (-50%)', '= Similar investment'],
        ['More difficult problem', 'BUT', 'Better tools', '= Still achievable'],
    ]

    table = ax4.table(cellText=summary_data_2, cellLoc='left',
                     bbox=[0.05, 0.05, 0.9, 0.9])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    # Header row styling
    for i in range(4):
        table[(0, i)].set_facecolor('#3498DB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Highlight insight rows
    for i in [8, 9, 10]:
        for j in range(4):
            table[(i, j)].set_facecolor('#FFFFCC')

    ax4.set_title('Summary & Key Insights', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_dir / 'deployment_results_comparison.png', dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: deployment_results_comparison.png")
    plt.close()

    print("\n" + "="*80)
    print("COMPARISON VISUALIZATIONS COMPLETE")
    print("="*80)
    print(f"\nOutputs saved to: {output_dir}/")
    print("\nFiles created:")
    print("  1. baseline_emissions_comparison.png")
    print("  2. technology_cost_comparison.png")
    print("  3. deployment_results_comparison.png")
    print("\n" + "="*80)

if __name__ == '__main__':
    create_comprehensive_comparison()
