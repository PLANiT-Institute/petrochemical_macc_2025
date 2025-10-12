"""
Visualize Sensitivity Analysis Results
Creates comparison charts showing impact of key assumptions
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

def load_sensitivity_data():
    """Load all sensitivity scenario results"""
    sensitivity_dir = Path('outputs/sensitivity')

    scenarios = {
        'Baseline\n(Full Model)': 'macc_baseline.csv',
        'No Fuel\nDifferential': 'macc_no_fuel_diff.csv',
        'No Learning\nCurves': 'macc_no_learning.csv',
        'No Fuel Diff\n+ No Learning': 'macc_no_fuel_no_learning.csv',
    }

    data = {}
    for name, filename in scenarios.items():
        df = pd.read_csv(sensitivity_dir / filename)
        data[name] = df

    return data

def plot_technology_comparison(data, year=2030):
    """Plot MACC comparison for all technologies at a given year"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Sensitivity Analysis: MACC Comparison ({year})', fontsize=16, fontweight='bold')

    technologies = ['Heat_Pump', 'RE_PPA', 'NCC-H2', 'NCC-Electricity']
    tech_labels = ['Heat Pump', 'RE PPA', 'NCC-H2', 'NCC-Electricity']

    for idx, (tech, label) in enumerate(zip(technologies, tech_labels)):
        ax = axes[idx // 2, idx % 2]

        # Extract MACC values for this technology
        macc_values = []
        scenario_labels = []

        for scenario_name, df in data.items():
            tech_data = df[(df['technology'] == tech) & (df['year'] == year)]
            if len(tech_data) > 0:
                macc = tech_data['total_cost_usd_per_tco2'].iloc[0]
                macc_values.append(macc)
                scenario_labels.append(scenario_name)

        # Create bar chart
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#c0392b']
        bars = ax.barh(range(len(macc_values)), macc_values, color=colors)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, macc_values)):
            ax.text(val + (5 if val > 0 else -5), i, f'${val:.0f}',
                   va='center', ha='left' if val > 0 else 'right', fontweight='bold')

        ax.set_yticks(range(len(scenario_labels)))
        ax.set_yticklabels(scenario_labels)
        ax.set_xlabel('MACC ($/tCO₂)', fontweight='bold')
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
        ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_file = f'outputs/sensitivity/sensitivity_comparison_{year}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_macc_evolution(data):
    """Plot how MACC evolves over time for each scenario"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('MACC Evolution Over Time (2025-2050)', fontsize=16, fontweight='bold')

    technologies = ['Heat_Pump', 'RE_PPA', 'NCC-H2', 'NCC-Electricity']
    tech_labels = ['Heat Pump', 'RE PPA', 'NCC-H2', 'NCC-Electricity']

    for idx, (tech, label) in enumerate(zip(technologies, tech_labels)):
        ax = axes[idx // 2, idx % 2]

        for scenario_name, df in data.items():
            tech_data = df[df['technology'] == tech].sort_values('year')
            years = tech_data['year']
            macc = tech_data['total_cost_usd_per_tco2']

            ax.plot(years, macc, marker='o', label=scenario_name, linewidth=2, markersize=4)

        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('MACC ($/tCO₂)', fontweight='bold')
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        ax.legend(loc='best', framealpha=0.9, fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    output_file = 'outputs/sensitivity/macc_evolution_timeline.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_impact_magnitude(data):
    """Plot the magnitude of impact for each assumption"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Impact of Key Assumptions on MACC', fontsize=16, fontweight='bold')

    technologies = ['Heat_Pump', 'RE_PPA', 'NCC-H2', 'NCC-Electricity']
    tech_labels = ['Heat Pump', 'RE PPA', 'NCC-H2', 'NCC-Elec']

    # 2030 Impact
    baseline_2030 = []
    no_fuel_2030 = []
    no_learning_2030 = []

    for tech in technologies:
        baseline_val = data['Baseline\n(Full Model)'][(data['Baseline\n(Full Model)']['technology'] == tech) & (data['Baseline\n(Full Model)']['year'] == 2030)]['total_cost_usd_per_tco2'].iloc[0]
        no_fuel_val = data['No Fuel\nDifferential'][(data['No Fuel\nDifferential']['technology'] == tech) & (data['No Fuel\nDifferential']['year'] == 2030)]['total_cost_usd_per_tco2'].iloc[0]
        no_learning_val = data['No Learning\nCurves'][(data['No Learning\nCurves']['technology'] == tech) & (data['No Learning\nCurves']['year'] == 2030)]['total_cost_usd_per_tco2'].iloc[0]

        baseline_2030.append(baseline_val)
        no_fuel_2030.append(no_fuel_val - baseline_val)  # Impact
        no_learning_2030.append(no_learning_val - baseline_val)  # Impact

    x = np.arange(len(tech_labels))
    width = 0.35

    bars1 = ax1.bar(x - width/2, no_fuel_2030, width, label='Removing Fuel Differential', color='#e74c3c')
    bars2 = ax1.bar(x + width/2, no_learning_2030, width, label='Removing Learning Curves', color='#f39c12')

    ax1.set_ylabel('MACC Change ($/tCO₂)', fontweight='bold')
    ax1.set_title('Impact on MACC (2030)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tech_labels)
    ax1.legend()
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (5 if height > 0 else -5),
                    f'{height:.0f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

    # 2050 Impact
    baseline_2050 = []
    no_fuel_2050 = []
    no_learning_2050 = []

    for tech in technologies:
        baseline_val = data['Baseline\n(Full Model)'][(data['Baseline\n(Full Model)']['technology'] == tech) & (data['Baseline\n(Full Model)']['year'] == 2050)]['total_cost_usd_per_tco2'].iloc[0]
        no_fuel_val = data['No Fuel\nDifferential'][(data['No Fuel\nDifferential']['technology'] == tech) & (data['No Fuel\nDifferential']['year'] == 2050)]['total_cost_usd_per_tco2'].iloc[0]
        no_learning_val = data['No Learning\nCurves'][(data['No Learning\nCurves']['technology'] == tech) & (data['No Learning\nCurves']['year'] == 2050)]['total_cost_usd_per_tco2'].iloc[0]

        baseline_2050.append(baseline_val)
        no_fuel_2050.append(no_fuel_val - baseline_val)
        no_learning_2050.append(no_learning_val - baseline_val)

    bars1 = ax2.bar(x - width/2, no_fuel_2050, width, label='Removing Fuel Differential', color='#e74c3c')
    bars2 = ax2.bar(x + width/2, no_learning_2050, width, label='Removing Learning Curves', color='#f39c12')

    ax2.set_ylabel('MACC Change ($/tCO₂)', fontweight='bold')
    ax2.set_title('Impact on MACC (2050)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(tech_labels)
    ax2.legend()
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    ax2.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (5 if height > 0 else -5),
                    f'{height:.0f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

    plt.tight_layout()
    output_file = 'outputs/sensitivity/impact_magnitude.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def create_summary_table():
    """Create formatted summary table"""
    df_comparison = pd.read_csv('outputs/sensitivity/comparison_summary.csv')

    # Pivot tables
    pivot_2030 = df_comparison.pivot(index='technology', columns='scenario', values='macc_2030')
    pivot_2050 = df_comparison.pivot(index='technology', columns='scenario', values='macc_2050')

    print("\n" + "="*80)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("="*80)

    print("\n2030 MACC Comparison ($/tCO2):")
    print(pivot_2030.to_string())

    print("\n2050 MACC Comparison ($/tCO2):")
    print(pivot_2050.to_string())

    # Calculate % impact
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)

    for tech in ['Heat_Pump', 'RE_PPA']:
        baseline = pivot_2030.loc[tech, 'baseline']
        no_fuel = pivot_2030.loc[tech, 'no_fuel_diff']
        impact = no_fuel - baseline

        print(f"\n{tech} (2030):")
        print(f"  Baseline MACC: ${baseline:.0f}/tCO2")
        print(f"  Without fuel differential: ${no_fuel:.0f}/tCO2")
        print(f"  Impact: ${impact:.0f}/tCO2 ({abs(impact):.0f} worse)")
        print(f"  → Fuel savings are CRITICAL for this technology!")

    for tech in ['Heat_Pump', 'NCC-H2']:
        baseline_2030 = pivot_2030.loc[tech, 'baseline']
        baseline_2050 = pivot_2050.loc[tech, 'baseline']
        no_learning_2030 = pivot_2030.loc[tech, 'no_learning']
        no_learning_2050 = pivot_2050.loc[tech, 'no_learning']
        impact_2030 = no_learning_2030 - baseline_2030
        impact_2050 = no_learning_2050 - baseline_2050

        print(f"\n{tech} - Learning Curve Impact:")
        print(f"  2030: ${impact_2030:.0f}/tCO2 impact")
        print(f"  2050: ${impact_2050:.0f}/tCO2 impact")
        if abs(impact_2030) < 10:
            print(f"  → Learning curves have MINIMAL impact on this technology")
        else:
            print(f"  → Learning curves are IMPORTANT for this technology")

if __name__ == '__main__':
    print("\n" + "="*80)
    print("VISUALIZING SENSITIVITY ANALYSIS RESULTS")
    print("="*80)

    # Load data
    data = load_sensitivity_data()
    print(f"\n✓ Loaded {len(data)} scenarios")

    # Create visualizations
    print("\nGenerating visualizations...")
    plot_technology_comparison(data, year=2030)
    plot_technology_comparison(data, year=2050)
    plot_macc_evolution(data)
    plot_impact_magnitude(data)

    # Create summary
    create_summary_table()

    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print("Output directory: outputs/sensitivity/")
