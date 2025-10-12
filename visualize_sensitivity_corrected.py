"""
Visualize Corrected Sensitivity Analysis Results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# Load data
sensitivity_dir = Path('outputs/sensitivity')
df_baseline = pd.read_csv(sensitivity_dir / 'macc_baseline.csv')
df_no_fossil = pd.read_csv(sensitivity_dir / 'macc_no_fossil_savings.csv')
df_no_learning = pd.read_csv(sensitivity_dir / 'macc_no_learning.csv')
df_both = pd.read_csv(sensitivity_dir / 'macc_no_fossil_no_learning.csv')

# Technology display names
tech_labels = {
    'Heat_Pump': 'Heat Pump',
    'RE_PPA': 'RE PPA',
    'NCC-Electricity': 'NCC-Electricity',
    'NCC-H2': 'NCC-H2'
}

# Colors
colors = {
    'Heat_Pump': '#2ECC71',
    'RE_PPA': '#F39C12',
    'NCC-Electricity': '#E74C3C',
    'NCC-H2': '#3498DB'
}

# ============================================================================
# 1. MACC Comparison for Key Years (2030 and 2050)
# ============================================================================

def plot_macc_comparison_year(year, output_file):
    """Create side-by-side MACC comparison for a specific year"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'MACC Sensitivity Analysis - Year {year}\n(Corrected: Fossil Fuel Savings)',
                 fontsize=16, fontweight='bold', y=0.995)

    scenarios = [
        ('Baseline', df_baseline, axes[0, 0]),
        ('No Fossil Fuel Savings', df_no_fossil, axes[0, 1]),
        ('No Learning Curves', df_no_learning, axes[1, 0]),
        ('No Fossil + No Learning', df_both, axes[1, 1])
    ]

    for scenario_name, df, ax in scenarios:
        df_year = df[(df['year'] == year) & (df['available'] == True)].copy()
        df_year = df_year.sort_values('total_cost_usd_per_tco2')

        x_pos = 0
        for _, row in df_year.iterrows():
            width = row['abatement_potential_mtco2']
            height = row['total_cost_usd_per_tco2']
            color = colors.get(row['technology'], 'gray')
            label = tech_labels.get(row['technology'], row['technology'])

            ax.bar(x_pos + width/2, height, width=width, color=color,
                   edgecolor='black', linewidth=1, alpha=0.85)

            # Add technology label
            ax.text(x_pos + width/2, height + 20, label,
                   ha='center', va='bottom', fontsize=8, rotation=0)

            x_pos += width

        # Zero line
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.8)

        # Formatting
        ax.set_xlabel('Cumulative Abatement (MtCO2/year)', fontsize=11, fontweight='bold')
        ax.set_ylabel('MACC ($/tCO2)', fontsize=11, fontweight='bold')
        ax.set_title(scenario_name, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add shading for negative costs
        y_min, y_max = ax.get_ylim()
        if y_min < 0:
            ax.axhspan(y_min, 0, alpha=0.08, color='green', zorder=0)
            ax.text(x_pos * 0.02, min(-20, y_min * 0.9), 'Cost-Saving',
                   fontsize=8, style='italic', color='darkgreen')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file.name}")
    plt.close()


plot_macc_comparison_year(2030, sensitivity_dir / 'sensitivity_comparison_2030_corrected.png')
plot_macc_comparison_year(2050, sensitivity_dir / 'sensitivity_comparison_2050_corrected.png')


# ============================================================================
# 2. Technology-Specific MACC Evolution Timeline
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Technology MACC Evolution: Sensitivity to Fossil Fuel Savings & Learning Curves',
             fontsize=16, fontweight='bold')

technologies = ['Heat_Pump', 'RE_PPA', 'NCC-H2', 'NCC-Electricity']

for idx, tech in enumerate(technologies):
    ax = axes[idx // 2, idx % 2]

    # Plot all scenarios
    scenarios = [
        ('Baseline', df_baseline, '-', 'o'),
        ('No Fossil Savings', df_no_fossil, '--', 's'),
        ('No Learning', df_no_learning, '-.', '^'),
        ('No Fossil + No Learning', df_both, ':', 'D')
    ]

    for scenario_name, df, linestyle, marker in scenarios:
        df_tech = df[df['technology'] == tech]
        ax.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
               linestyle=linestyle, marker=marker, linewidth=2,
               markersize=5, label=scenario_name, alpha=0.8)

    # Zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

    # Formatting
    ax.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax.set_ylabel('MACC ($/tCO2)', fontsize=11, fontweight='bold')
    ax.set_title(tech_labels[tech], fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(2024, 2051)

plt.tight_layout()
plt.savefig(sensitivity_dir / 'macc_evolution_timeline_corrected.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: macc_evolution_timeline_corrected.png")
plt.close()


# ============================================================================
# 3. Impact Magnitude: How much does each assumption matter?
# ============================================================================

def calculate_impact(year):
    """Calculate the impact of removing each assumption"""
    impacts = []

    for tech in technologies:
        baseline_cost = df_baseline[(df_baseline['year'] == year) &
                                   (df_baseline['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]

        no_fossil_cost = df_no_fossil[(df_no_fossil['year'] == year) &
                                      (df_no_fossil['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]

        no_learning_cost = df_no_learning[(df_no_learning['year'] == year) &
                                         (df_no_learning['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]

        fossil_impact = no_fossil_cost - baseline_cost
        learning_impact = no_learning_cost - baseline_cost

        impacts.append({
            'technology': tech_labels[tech],
            'year': year,
            'fossil_fuel_savings_impact': fossil_impact,
            'learning_curve_impact': learning_impact
        })

    return impacts


# Calculate impacts for 2030 and 2050
impacts_2030 = calculate_impact(2030)
impacts_2050 = calculate_impact(2050)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Sensitivity Impact Magnitude: How Much Does Each Assumption Matter?\n(Corrected: Fossil Fuel Savings)',
             fontsize=15, fontweight='bold')

for idx, (year, impacts) in enumerate([(2030, impacts_2030), (2050, impacts_2050)]):
    ax = axes[idx]
    df_impact = pd.DataFrame(impacts)

    x = np.arange(len(technologies))
    width = 0.35

    fossil_impacts = df_impact['fossil_fuel_savings_impact'].values
    learning_impacts = df_impact['learning_curve_impact'].values

    bars1 = ax.bar(x - width/2, fossil_impacts, width, label='Fossil Fuel Savings Impact',
                   color='#E74C3C', edgecolor='black', linewidth=1, alpha=0.85)
    bars2 = ax.bar(x + width/2, learning_impacts, width, label='Learning Curve Impact',
                   color='#3498DB', edgecolor='black', linewidth=1, alpha=0.85)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}', ha='center', va='bottom' if height > 0 else 'top',
                   fontsize=9, fontweight='bold')

    ax.set_xlabel('Technology', fontsize=12, fontweight='bold')
    ax.set_ylabel('MACC Impact ($/tCO2)', fontsize=12, fontweight='bold')
    ax.set_title(f'Year {year}', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([tech_labels[t] for t in technologies], rotation=15, ha='right')
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)

plt.tight_layout()
plt.savefig(sensitivity_dir / 'impact_magnitude_corrected.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: impact_magnitude_corrected.png")
plt.close()


# ============================================================================
# 4. Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("CORRECTED SENSITIVITY ANALYSIS SUMMARY")
print("="*80)

for year in [2030, 2050]:
    print(f"\n{year} RESULTS:")
    print("-" * 80)

    for tech in technologies:
        baseline = df_baseline[(df_baseline['year'] == year) &
                              (df_baseline['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]
        no_fossil = df_no_fossil[(df_no_fossil['year'] == year) &
                                 (df_no_fossil['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]
        no_learning = df_no_learning[(df_no_learning['year'] == year) &
                                     (df_no_learning['technology'] == tech)]['total_cost_usd_per_tco2'].iloc[0]

        fossil_impact = no_fossil - baseline
        learning_impact = no_learning - baseline

        print(f"\n{tech_labels[tech]}:")
        print(f"  Baseline MACC:             ${baseline:>7.1f}/tCO2")
        print(f"  Without Fossil Savings:    ${no_fossil:>7.1f}/tCO2  (impact: +${fossil_impact:>6.1f})")
        print(f"  Without Learning:          ${no_learning:>7.1f}/tCO2  (impact: +${learning_impact:>6.1f})")

        if abs(fossil_impact) > abs(learning_impact):
            print(f"  → FOSSIL FUEL SAVINGS is the dominant driver ({abs(fossil_impact)/abs(learning_impact):.1f}x more impact)")
        else:
            print(f"  → LEARNING CURVES is the dominant driver ({abs(learning_impact)/abs(fossil_impact):.1f}x more impact)")

print("\n" + "="*80)
print("All visualizations saved to: outputs/sensitivity/")
print("="*80)
