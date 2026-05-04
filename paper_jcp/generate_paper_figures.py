"""
FIGURE GENERATOR FOR JCP PAPER
==============================
Reads the consolidated results from paper_jcp/results/jcp_consolidated_results.csv
and generates high-resolution figures for the manuscript.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration
INPUT_FILE = Path('paper_jcp/results/jcp_consolidated_results.csv')
OUTPUT_DIR = Path('paper_jcp/figures')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Plot Styling for Journal
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.figsize'] = (8, 6)
sns.set_context("paper", font_scale=1.2)
sns.set_style("whitegrid")

def load_results():
    if not INPUT_FILE.exists():
        print(f"Error: Results file not found at {INPUT_FILE}")
        return None
    return pd.read_csv(INPUT_FILE)

def plot_mac_curve(df, year, scenario_name):
    """Generate MAC Curve for a specific year and scenario"""
    subset = df[(df['year'] == year) & (df['scenario'] == scenario_name)].copy()
    subset = subset[subset['technology'] != 'Baseline'] # Only abatement measures
    
    # Sort by MAC
    subset = subset.sort_values(by='mac_usd_per_tco2')
    
    # Calculate widths
    subset['width'] = subset['abatement_tco2'] / 1e6 # MtCO2
    subset['cumulative_width'] = subset['width'].cumsum()
    
    if subset.empty:
        print(f"No abatement data for {scenario_name} in {year}")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw bars
    left = 0
    for _, row in subset.iterrows():
        w = row['width']
        h = row['mac_usd_per_tco2']
        color = '#4c72b0' if h < 100 else '#c44e52' # Blue for low cost, Red for high
        ax.bar(left + w/2, h, width=w, color=color, edgecolor='white', alpha=0.9)
        left += w
        
    ax.set_xlabel('Abatement Potential (MtCO2e)')
    ax.set_ylabel('Marginal Abatement Cost ($/tCO2e)')
    ax.set_title(f'Marginal Abatement Cost Curve - {year} ({scenario_name})')
    ax.axhline(0, color='black', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"mac_curve_{scenario_name}_{year}.png")
    plt.close()
    print(f"Saved MAC curve for {scenario_name} {year}")

def plot_transition_cost(df):
    """Plot Total Annual Cost over time by Scenario"""
    # Aggregate by scenario and year
    agg = df.groupby(['scenario', 'year'])['total_cost_usd'].sum().reset_index()
    agg['total_cost_bn'] = agg['total_cost_usd'] / 1e9
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=agg, x='year', y='total_cost_bn', hue='scenario', marker='o')
    plt.xlabel('Year')
    plt.ylabel('Total Annual Transition Cost (Billion USD)')
    plt.title('Transition Cost Trajectory')
    plt.legend(title='Scenario')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "transition_cost_trajectory.png")
    plt.close()
    print("Saved transition cost trajectory")

def plot_tech_mix(df, scenario_name):
    """Stacked Area Chart of Technology Adoption (Production Volume)"""
    subset = df[df['scenario'] == scenario_name].copy()
    
    # Pivot: Year vs Technology (sum of production)
    pivot = subset.pivot_table(index='year', columns='technology', values='production_t', aggfunc='sum').fillna(0)
    pivot = pivot / 1e6 # Convert to Mt
    
    plt.figure(figsize=(10, 6))
    pivot.plot.area(stacked=True, alpha=0.8, cmap='viridis', figsize=(10,6))
    plt.xlabel('Year')
    plt.ylabel('Production Volume (Mt)')
    plt.title(f'Technology Transition - {scenario_name}')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"tech_mix_{scenario_name}.png")
    plt.close()
    print(f"Saved tech mix for {scenario_name}")

def main():
    print("Generating Paper Figures...")
    df = load_results()
    if df is None:
        return
        
    # 1. MAC Curves for 2030, 2040, 2050 for baseline scenario
    for year in [2030, 2040, 2050]:
        plot_mac_curve(df, year, "S1_Baseline_Trends")
        plot_mac_curve(df, year, "S2_NetZero_HighAmbition")
        
    # 2. Transition Cost Comparison
    plot_transition_cost(df)
    
    # 3. Technology Mix for key scenarios
    plot_tech_mix(df, "S1_Baseline_Trends")
    plot_tech_mix(df, "S2_NetZero_HighAmbition")
    
    print(f"Figures saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
