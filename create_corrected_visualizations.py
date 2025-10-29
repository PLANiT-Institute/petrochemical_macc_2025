"""
Generate comprehensive visualizations for corrected model (V2)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def create_all_visualizations():
    """Create comprehensive visualizations for corrected model"""

    output_dir = Path('outputs/module_03_v2/visualizations')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load corrected model results
    df_deployment = pd.read_csv('outputs/module_03_v2/policy_target_deployment_corrected.csv')
    df_allocation = pd.read_csv('outputs/module_03_v2/policy_target_facility_allocation_2050.csv')

    # Load original model for comparison
    try:
        df_original = pd.read_csv('outputs/module_03/policy_target_deployment.csv')
        has_comparison = True
    except:
        has_comparison = False
        print("Original model results not found, skipping comparison plots")

    print("="*80)
    print("GENERATING CORRECTED MODEL VISUALIZATIONS")
    print("="*80)

    # 1. Technology Deployment Trajectory (Corrected)
    create_deployment_trajectory(df_deployment, output_dir)

    # 2. Emission Trajectory Comparison (BAU vs Actual)
    create_emission_trajectory(df_deployment, output_dir)

    # 3. Investment Profile Over Time
    create_investment_profile(df_deployment, output_dir)

    # 4. Energy System Impacts
    create_energy_impacts(df_deployment, output_dir)

    # 5. Facility-Level Distribution
    create_facility_distribution(df_allocation, output_dir)

    # 6. Regional Analysis
    create_regional_analysis(df_allocation, output_dir)

    # 7. Technology Cost Comparison
    create_technology_cost_comparison(output_dir)

    # 8. Original vs Corrected Comparison
    if has_comparison:
        create_model_comparison(df_original, df_deployment, output_dir)

    # 9. Model Structure Diagram
    create_model_structure_diagram(output_dir)

    print(f"\n✓ All visualizations saved to: {output_dir}")
    print("="*80)

def create_deployment_trajectory(df, output_dir):
    """Technology deployment stacked area chart"""
    print("Creating deployment trajectory...")

    fig, ax = plt.subplots(figsize=(14, 8))

    # Prepare data
    years = df['year']
    heat_pump = df['heat_pump_mt']
    ncc_h2 = df['ncc_h2_mt']
    ncc_elec = df['ncc_elec_mt']
    re_ppa = df['re_ppa_mt']

    # Stack plot
    ax.fill_between(years, 0, heat_pump, label='Heat Pump', alpha=0.8, color='#2ECC71')
    ax.fill_between(years, heat_pump, heat_pump + ncc_h2, label='NCC-H2', alpha=0.8, color='#3498DB')
    ax.fill_between(years, heat_pump + ncc_h2, heat_pump + ncc_h2 + ncc_elec,
                    label='NCC-Electricity', alpha=0.8, color='#E74C3C')
    ax.fill_between(years, heat_pump + ncc_h2 + ncc_elec,
                    heat_pump + ncc_h2 + ncc_elec + re_ppa,
                    label='RE PPA', alpha=0.8, color='#F39C12')

    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Abatement (MtCO2/year)', fontsize=14, fontweight='bold')
    ax.set_title('Technology Deployment Trajectory (Corrected Model V2)',
                fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(2025, 2050)

    # Add text annotation
    final_year = df[df['year'] == 2050].iloc[0]
    ax.text(2050, final_year['total_deployed_mt'] + 2,
           f"2050: {final_year['total_deployed_mt']:.1f} MtCO2",
           fontsize=12, fontweight='bold', ha='right')

    plt.tight_layout()
    plt.savefig(output_dir / 'deployment_trajectory_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: deployment_trajectory_corrected.png")

def create_emission_trajectory(df, output_dir):
    """BAU vs Actual emissions trajectory"""
    print("Creating emission trajectory...")

    fig, ax = plt.subplots(figsize=(14, 8))

    years = df['year']
    bau = df['bau_mt']
    actual = df['actual_emissions_mt']
    target = df['target_mt']

    # Plot lines
    ax.plot(years, bau, label='BAU (No Action)', color='gray',
           linestyle='--', linewidth=2.5, marker='o', markersize=4)
    ax.plot(years, actual, label='Actual with Technologies', color='green',
           linewidth=3, marker='s', markersize=5)
    ax.plot(years, target, label='Policy Target', color='red',
           linestyle=':', linewidth=2.5, marker='^', markersize=5)

    # Fill area between BAU and Actual (abatement)
    ax.fill_between(years, bau, actual, alpha=0.3, color='lightgreen',
                    label='Abatement')

    # Fill area between Actual and Target (shortfall)
    ax.fill_between(years, target, actual, where=(actual > target),
                    alpha=0.3, color='lightcoral', label='Shortfall')

    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Emissions (MtCO2/year)', fontsize=14, fontweight='bold')
    ax.set_title('Emission Trajectory: Policy Target Scenario (Corrected Model V2)',
                fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(2025, 2050)

    # Add milestone annotations
    milestones = [2025, 2030, 2040, 2050]
    for year in milestones:
        row = df[df['year'] == year].iloc[0]
        reduction = ((bau.iloc[0] - row['actual_emissions_mt']) / bau.iloc[0]) * 100
        ax.annotate(f'{year}\n{reduction:.1f}% reduction',
                   xy=(year, row['actual_emissions_mt']),
                   xytext=(year, row['actual_emissions_mt'] - 8),
                   fontsize=9, ha='center',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_dir / 'emission_trajectory_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: emission_trajectory_corrected.png")

def create_investment_profile(df, output_dir):
    """Investment profile over time"""
    print("Creating investment profile...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    years = df['year']
    cumulative = df['cumulative_capex_musd'] / 1000  # Convert to billions

    # Calculate annual investment
    annual_investment = cumulative.diff().fillna(cumulative.iloc[0])

    # Left plot: Cumulative investment
    ax1.plot(years, cumulative, linewidth=3, color='#3498DB', marker='o')
    ax1.fill_between(years, 0, cumulative, alpha=0.3, color='#3498DB')
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cumulative CAPEX (Billion USD)', fontsize=12, fontweight='bold')
    ax1.set_title('Cumulative Investment (Corrected Model V2)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add final value annotation
    final_capex = cumulative.iloc[-1]
    ax1.text(2050, final_capex, f'${final_capex:.1f}B',
            fontsize=12, fontweight='bold', ha='right', va='bottom')

    # Right plot: Annual investment
    ax2.bar(years, annual_investment, width=0.8, color='#E74C3C', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Annual CAPEX (Billion USD)', fontsize=12, fontweight='bold')
    ax2.set_title('Annual Investment Profile (Corrected Model V2)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Add average line
    avg_annual = annual_investment.mean()
    ax2.axhline(avg_annual, color='red', linestyle='--', linewidth=2,
               label=f'Average: ${avg_annual:.2f}B/year')
    ax2.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'investment_profile_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: investment_profile_corrected.png")

def create_energy_impacts(df, output_dir):
    """Energy system impacts (H2, Electricity)"""
    print("Creating energy impacts...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    years = df['year']
    h2 = df['h2_consumption_kt']
    elec = df['electricity_consumption_increase_twh']

    # Left: H2 consumption
    ax1.plot(years, h2, linewidth=3, color='#3498DB', marker='o', markersize=6)
    ax1.fill_between(years, 0, h2, alpha=0.3, color='#3498DB')
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('H2 Consumption (kt/year)', fontsize=12, fontweight='bold')
    ax1.set_title('Hydrogen Demand (Corrected Model V2)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add annotation if H2 = 0
    if h2.max() == 0:
        ax1.text(0.5, 0.5, 'NCC-Electricity Selected\n(No H2 Required)',
                transform=ax1.transAxes, fontsize=14, ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    # Right: Electricity increase
    ax2.plot(years, elec, linewidth=3, color='#E74C3C', marker='s', markersize=6)
    ax2.fill_between(years, 0, elec, alpha=0.3, color='#E74C3C')
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Electricity Increase (TWh/year)', fontsize=12, fontweight='bold')
    ax2.set_title('Additional Electricity Demand (Corrected Model V2)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add percentage of Korea's total
    final_elec = elec.iloc[-1]
    korea_total = 600  # TWh approximate
    pct = (final_elec / korea_total) * 100
    ax2.text(2050, final_elec, f'{final_elec:.1f} TWh\n({pct:.1f}% of Korea total)',
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_dir / 'energy_impacts_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: energy_impacts_corrected.png")

def create_facility_distribution(df, output_dir):
    """Facility-level technology distribution"""
    print("Creating facility distribution...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Count facilities by technology
    hp_count = (df['tech_heat_pump_pct'] > 0).sum()
    h2_count = (df['tech_ncc_h2_pct'] > 0).sum()
    elec_count = (df['tech_ncc_elec_pct'] > 0).sum()
    re_count = (df['tech_re_ppa_pct'] > 0).sum()
    no_tech = (df['abatement_mt'] == 0).sum()

    # 1. Pie chart: Facilities by technology
    labels = ['Heat Pump', 'NCC-Electricity', 'RE PPA', 'No Technology']
    sizes = [hp_count, elec_count, re_count, no_tech]
    colors = ['#2ECC71', '#E74C3C', '#F39C12', '#95A5A6']
    explode = (0.05, 0.05, 0.05, 0)

    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Facilities by Technology Deployment\n(Corrected Model V2)',
                 fontsize=13, fontweight='bold')

    # 2. Histogram: Abatement percentage distribution
    abatement_pct = (df['abatement_mt'] * 1000 / df['total_emissions_kt']) * 100
    abatement_pct = abatement_pct[abatement_pct > 0]  # Only facilities with abatement

    ax2.hist(abatement_pct, bins=20, color='#3498DB', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Abatement Percentage (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Facilities', fontsize=11, fontweight='bold')
    ax2.set_title('Abatement Percentage Distribution\n(Corrected Model V2)',
                 fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axvline(abatement_pct.mean(), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {abatement_pct.mean():.1f}%')
    ax2.legend()

    # 3. Bar chart: Top 10 facilities by abatement
    top10 = df.nlargest(10, 'abatement_mt')
    labels_top10 = [f"{row['company'][:15]}...\n{row['product']}" for _, row in top10.iterrows()]

    ax3.barh(range(len(top10)), top10['abatement_mt'], color='#E74C3C', alpha=0.7, edgecolor='black')
    ax3.set_yticks(range(len(top10)))
    ax3.set_yticklabels(labels_top10, fontsize=9)
    ax3.set_xlabel('Abatement (MtCO2)', fontsize=11, fontweight='bold')
    ax3.set_title('Top 10 Facilities by Abatement\n(Corrected Model V2)',
                 fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.invert_yaxis()

    # 4. Scatter: Baseline vs 2050 emissions
    ax4.scatter(df['total_emissions_kt']/1000, df['emissions_2050_kt']/1000,
               alpha=0.6, s=50, color='#3498DB', edgecolor='black', linewidth=0.5)

    # Add diagonal line (no abatement)
    max_val = max(df['total_emissions_kt'].max(), df['emissions_2050_kt'].max()) / 1000
    ax4.plot([0, max_val], [0, max_val], 'r--', linewidth=2, alpha=0.7, label='No Abatement')

    ax4.set_xlabel('Baseline Emissions (MtCO2)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('2050 Emissions (MtCO2)', fontsize=11, fontweight='bold')
    ax4.set_title('Baseline vs 2050 Emissions\n(Corrected Model V2)',
                 fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()

    plt.tight_layout()
    plt.savefig(output_dir / 'facility_distribution_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: facility_distribution_corrected.png")

def create_regional_analysis(df, output_dir):
    """Regional distribution analysis"""
    print("Creating regional analysis...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Group by location
    regional = df.groupby('location').agg({
        'facility_id': 'count',
        'total_emissions_kt': 'sum',
        'abatement_mt': 'sum',
        'emissions_2050_kt': 'sum'
    }).reset_index()

    regional.columns = ['location', 'facilities', 'baseline_mt', 'abatement_mt', 'emissions_2050_mt']
    regional['baseline_mt'] = regional['baseline_mt'] / 1000
    regional['emissions_2050_mt'] = regional['emissions_2050_mt'] / 1000
    regional['reduction_pct'] = (regional['abatement_mt'] / regional['baseline_mt']) * 100

    regional = regional.sort_values('baseline_mt', ascending=False)

    # Left: Stacked bar (baseline vs 2050 by region)
    x = range(len(regional))
    width = 0.35

    ax1.bar(x, regional['baseline_mt'], width, label='Baseline',
           color='#95A5A6', alpha=0.7, edgecolor='black')
    ax1.bar([i + width for i in x], regional['emissions_2050_mt'], width,
           label='2050 (with abatement)', color='#2ECC71', alpha=0.7, edgecolor='black')

    ax1.set_xlabel('Region', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Emissions (MtCO2)', fontsize=12, fontweight='bold')
    ax1.set_title('Regional Emissions: Baseline vs 2050\n(Corrected Model V2)',
                 fontsize=14, fontweight='bold')
    ax1.set_xticks([i + width/2 for i in x])
    ax1.set_xticklabels(regional['location'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Right: Reduction percentage by region
    colors_reduction = ['#E74C3C' if r < 50 else '#F39C12' if r < 60 else '#2ECC71'
                       for r in regional['reduction_pct']]

    ax2.barh(range(len(regional)), regional['reduction_pct'],
            color=colors_reduction, alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(regional)))
    ax2.set_yticklabels(regional['location'], fontsize=11)
    ax2.set_xlabel('Reduction Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Regional Reduction Rates\n(Corrected Model V2)',
                 fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.invert_yaxis()

    # Add value labels
    for i, (pct, facilities) in enumerate(zip(regional['reduction_pct'], regional['facilities'])):
        ax2.text(pct + 1, i, f'{pct:.1f}% ({int(facilities)} facilities)',
                va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_dir / 'regional_analysis_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: regional_analysis_corrected.png")

def create_technology_cost_comparison(output_dir):
    """Technology cost evolution comparison"""
    print("Creating technology cost comparison...")

    # Load MACC data
    df_macc = pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Filter available technologies
    df_available = df_macc[df_macc['available'] == True]

    # Left: Cost evolution by technology
    for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
        df_tech = df_available[df_available['technology'] == tech]
        if not df_tech.empty:
            ax1.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
                    label=tech.replace('_', ' '), linewidth=2.5, marker='o', markersize=5)

    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Cost (USD/tCO2)', fontsize=12, fontweight='bold')
    ax1.set_title('Technology Cost Evolution\n(Corrected Model V2)',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(2025, 2050)

    # Highlight 2030 (technology selection year)
    ax1.axvline(2030, color='red', linestyle='--', linewidth=2, alpha=0.5,
               label='Technology Selection Year')

    # Right: 2030 cost comparison (bar chart)
    df_2030 = df_available[df_available['year'] == 2030]

    techs = []
    costs = []
    for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
        df_t = df_2030[df_2030['technology'] == tech]
        if not df_t.empty:
            techs.append(tech.replace('_', ' '))
            costs.append(df_t['total_cost_usd_per_tco2'].iloc[0])

    colors_cost = ['#2ECC71', '#3498DB', '#E74C3C', '#F39C12']
    bars = ax2.bar(techs, costs, color=colors_cost[:len(techs)], alpha=0.7, edgecolor='black', linewidth=2)

    # Highlight selected technology
    selected_idx = techs.index('NCC-Electricity') if 'NCC-Electricity' in techs else -1
    if selected_idx >= 0:
        bars[selected_idx].set_edgecolor('red')
        bars[selected_idx].set_linewidth(4)
        ax2.text(selected_idx, costs[selected_idx] + 20, '✓ SELECTED',
                ha='center', fontsize=12, fontweight='bold', color='red')

    ax2.set_ylabel('Total Cost (USD/tCO2)', fontsize=12, fontweight='bold')
    ax2.set_title('Technology Cost Comparison (2030)\n(Corrected Model V2)',
                 fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticklabels(techs, rotation=15, ha='right')

    # Add value labels
    for i, (tech, cost) in enumerate(zip(techs, costs)):
        ax2.text(i, cost, f'${cost:.0f}', ha='center', va='bottom',
                fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'technology_cost_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: technology_cost_comparison.png")

def create_model_comparison(df_original, df_corrected, output_dir):
    """Compare original vs corrected model"""
    print("Creating model comparison...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    years = df_corrected['year']

    # 1. Total abatement comparison
    ax1.plot(years, df_original['total_deployed_mt'], label='Original (WRONG)',
            color='red', linewidth=3, marker='x', markersize=7, linestyle='--')
    ax1.plot(years, df_corrected['total_deployed_mt'], label='Corrected (V2)',
            color='green', linewidth=3, marker='o', markersize=6)
    ax1.fill_between(years, df_corrected['total_deployed_mt'], df_original['total_deployed_mt'],
                     alpha=0.3, color='red', label='Overestimation')
    ax1.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Abatement (MtCO2)', fontsize=11, fontweight='bold')
    ax1.set_title('Total Abatement: Original vs Corrected', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 2. NCC technologies comparison
    width = 0.35
    x = np.arange(len(['2030', '2040', '2050']))
    milestone_years = [2030, 2040, 2050]

    original_ncc = []
    corrected_ncc = []
    for year in milestone_years:
        orig = df_original[df_original['year'] == year]
        corr = df_corrected[df_corrected['year'] == year]
        original_ncc.append(orig['ncc_h2_mt'].iloc[0] + orig['ncc_elec_mt'].iloc[0])
        corrected_ncc.append(corr['ncc_h2_mt'].iloc[0] + corr['ncc_elec_mt'].iloc[0])

    ax2.bar(x - width/2, original_ncc, width, label='Original (H2+Elec)',
           color='red', alpha=0.7, edgecolor='black')
    ax2.bar(x + width/2, corrected_ncc, width, label='Corrected (Elec only)',
           color='green', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('NCC Abatement (MtCO2)', fontsize=11, fontweight='bold')
    ax2.set_title('NCC Technology Deployment: Original vs Corrected', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['2030', '2040', '2050'])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Add percentage labels
    for i, (orig, corr) in enumerate(zip(original_ncc, corrected_ncc)):
        diff_pct = ((orig - corr) / orig) * 100 if orig > 0 else 0
        ax2.text(i, max(orig, corr) + 2, f'{diff_pct:.0f}% over',
                ha='center', fontsize=9, color='red', fontweight='bold')

    # 3. Investment comparison
    ax3.plot(years, df_original['cumulative_capex_musd']/1000, label='Original (WRONG)',
            color='red', linewidth=3, linestyle='--')
    ax3.plot(years, df_corrected['cumulative_capex_musd']/1000, label='Corrected (V2)',
            color='green', linewidth=3)
    ax3.fill_between(years, df_corrected['cumulative_capex_musd']/1000,
                     df_original['cumulative_capex_musd']/1000,
                     alpha=0.3, color='red')
    ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Cumulative CAPEX (Billion USD)', fontsize=11, fontweight='bold')
    ax3.set_title('Investment: Original vs Corrected', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    # Add savings annotation
    orig_final = df_original['cumulative_capex_musd'].iloc[-1] / 1000
    corr_final = df_corrected['cumulative_capex_musd'].iloc[-1] / 1000
    savings = orig_final - corr_final
    savings_pct = (savings / orig_final) * 100
    ax3.text(2050, (orig_final + corr_final)/2,
            f'Savings:\n${savings:.1f}B\n({savings_pct:.1f}%)',
            fontsize=11, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    # 4. Emissions trajectory comparison
    ax4.plot(years, df_original['actual_emissions_mt'], label='Original (WRONG)',
            color='red', linewidth=3, marker='x', linestyle='--')
    ax4.plot(years, df_corrected['actual_emissions_mt'], label='Corrected (V2)',
            color='green', linewidth=3, marker='o')
    ax4.plot(years, df_corrected['target_mt'], label='Policy Target',
            color='blue', linewidth=2, linestyle=':')
    ax4.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Emissions (MtCO2/year)', fontsize=11, fontweight='bold')
    ax4.set_title('Emission Trajectory: Original vs Corrected', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)

    # Highlight unrealistic target
    ax4.axhspan(df_corrected['actual_emissions_mt'].iloc[-1],
               df_corrected['target_mt'].iloc[-1],
               alpha=0.2, color='red', label='Unrealistic target')

    plt.tight_layout()
    plt.savefig(output_dir / 'model_comparison_original_vs_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: model_comparison_original_vs_corrected.png")

def create_model_structure_diagram(output_dir):
    """Create model structure flowchart"""
    print("Creating model structure diagram...")

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, 'MACC Model Structure (Corrected V2)',
           ha='center', fontsize=18, fontweight='bold', transform=ax.transAxes)

    # Module boxes
    modules = [
        {'name': 'Module 1: Baseline Analysis', 'y': 0.80, 'color': '#3498DB',
         'content': '• Calculate 2025 emissions\n• Project BAU trajectory\n• Include demand growth\n• Grid decarbonization'},

        {'name': 'Module 2: MACC Calculation', 'y': 0.60, 'color': '#2ECC71',
         'content': '• 4 Technologies:\n  - Heat Pump (non-NCC)\n  - NCC-H2 (alternative 1)\n  - NCC-Electricity (alternative 2)\n  - RE PPA (all facilities)\n• Cost evolution 2025-2050'},

        {'name': 'Module 3: Optimization', 'y': 0.35, 'color': '#E74C3C',
         'content': '• Cost-ordered deployment\n• NCC MUTUAL EXCLUSIVITY ✓\n• Technology irreversibility\n• Emission target compliance'},

        {'name': 'Output: Technology Deployment', 'y': 0.10, 'color': '#F39C12',
         'content': '• 248 facility allocations\n• Investment requirements\n• H2 and electricity demand\n• Emission reductions'}
    ]

    for i, module in enumerate(modules):
        # Box
        from matplotlib.patches import FancyBboxPatch
        box = FancyBboxPatch((0.1, module['y'] - 0.08), 0.8, 0.14,
                            boxstyle="round,pad=0.01",
                            facecolor=module['color'],
                            edgecolor='black',
                            linewidth=2,
                            alpha=0.7,
                            transform=ax.transAxes)
        ax.add_patch(box)

        # Title
        ax.text(0.5, module['y'] + 0.05, module['name'],
               ha='center', va='top', fontsize=13, fontweight='bold',
               color='white', transform=ax.transAxes)

        # Content
        ax.text(0.5, module['y'] - 0.03, module['content'],
               ha='center', va='top', fontsize=10,
               color='white', transform=ax.transAxes,
               linespacing=1.5)

        # Arrow to next module
        if i < len(modules) - 1:
            ax.annotate('', xy=(0.5, modules[i+1]['y'] + 0.06),
                       xytext=(0.5, module['y'] - 0.09),
                       arrowprops=dict(arrowstyle='->', lw=3, color='black'),
                       xycoords='axes fraction', textcoords='axes fraction')

    # Add critical fix callout
    from matplotlib.patches import FancyBboxPatch
    callout = FancyBboxPatch((0.65, 0.35), 0.32, 0.12,
                            boxstyle="round,pad=0.01",
                            facecolor='yellow',
                            edgecolor='red',
                            linewidth=3,
                            alpha=0.9,
                            transform=ax.transAxes)
    ax.add_patch(callout)

    ax.text(0.81, 0.43, '🔧 CRITICAL FIX',
           ha='center', fontsize=11, fontweight='bold',
           color='red', transform=ax.transAxes)
    ax.text(0.81, 0.38, 'NCC-H2 OR NCC-Elec\n(not both!)',
           ha='center', fontsize=9, color='black',
           transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig(output_dir / 'model_structure_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: model_structure_diagram.png")

if __name__ == '__main__':
    create_all_visualizations()
