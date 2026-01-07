
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Configuration
OUTPUT_DIR = Path('outputs')
FIG_DIR = OUTPUT_DIR / 'figures'
FIG_DIR.mkdir(exist_ok=True)

# Set Aesthethics (Academic Style)
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

def load_data():
    df_res = pd.read_csv(OUTPUT_DIR / 'scenario_results.csv')
    df_sum = pd.read_csv(OUTPUT_DIR / 'stranded_assets_summary.csv')
    df_fac = pd.read_csv(OUTPUT_DIR / 'stranded_assets_facilities.csv')
    return df_res, df_sum, df_fac

def plot_emissions_trajectory(df, filename):
    plt.figure(figsize=(10, 6))
    
    # Filter for key scenarios
    scenarios = ['baseline', 'shaheen_ncc_h2', 'restructure_40pct_ncc_h2']
    labels = {
        'baseline': 'Baseline (No Action)',
        'shaheen_ncc_h2': 'Expansion (Shaheen)',
        'restructure_40pct_ncc_h2': 'Restructuring (Managed Decline)'
    }
    colors = {
        'baseline': '#7f7f7f',      # Gray
        'shaheen_ncc_h2': '#d62728', # Red
        'restructure_40pct_ncc_h2': '#2ca02c' # Green
    }
    styles = {
        'baseline': '--',
        'shaheen_ncc_h2': '-',
        'restructure_40pct_ncc_h2': '-'
    }
    
    for s in scenarios:
        if s not in df['scenario'].unique(): continue
        df_s = df[df['scenario'] == s]
        yearly = df_s.groupby('year')['emissions_tco2'].sum() / 1e6
        plt.plot(yearly.index, yearly.values, label=labels[s], color=colors[s], linestyle=styles[s], linewidth=2.5)
        
    plt.title('Emission Trajectories vs. Carbon Constraints', fontweight='bold', pad=15)
    plt.xlabel('Year')
    plt.ylabel('Annual Emissions (MtCO2e)')
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename)
    print(f"Generated {filename}")

def plot_stranded_value_comparison(df_sum, filename):
    plt.figure(figsize=(8, 6))
    
    # Compare Main Scenarios
    scenarios = ['shaheen_ncc_h2', 'restructure_40pct_ncc_h2']
    names = ['Expansion \n(Shaheen)', 'Restructuring \n(Managed Decline)']
    
    # Extract values
    val_shaheen = df_sum[df_sum['scenario'] == 'shaheen_ncc_h2']['stranded_value_1.5C_usd'].values[0] / 1e9
    val_restruct = df_sum[df_sum['scenario'] == 'restructure_40pct_ncc_h2']['stranded_value_1.5C_usd'].values[0] / 1e9
    
    values = [val_shaheen, val_restruct]
    colors = ['#d62728', '#2ca02c']
    
    bars = plt.bar(names, values, color=colors, width=0.6)
    
    plt.title('Total Stranded Asset Risk (1.5°C Budget)', fontweight='bold', pad=15)
    plt.ylabel('Net Book Value at Risk ($ Billion)')
    plt.ylim(0, max(values)*1.2)
    
    # Annotate
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'${height:.1f}B',
                 ha='center', va='bottom', fontsize=13, fontweight='bold')
                 
    # Add difference annotation
    diff = val_shaheen - val_restruct
    mid = (val_shaheen + val_restruct) / 2
    # plt.annotate(f'Avoided: ${diff:.1f}B', xy=(0.5, mid), xytext=(0.5, mid), ha='center') 
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename)
    print(f"Generated {filename}")

def plot_top_risks(df_fac, filename):
    plt.figure(figsize=(10, 5))
    
    # Top Companies in Shaheen Scenario
    df = df_fac[(df_fac['scenario'] == 'shaheen_ncc_h2') & (df_fac['budget_scenario'] == '1.5C')].copy()
    comp_risk = df.groupby('company')['stranded_value_usd'].sum().sort_values(ascending=True).tail(5)
    values = comp_risk / 1e9
    
    # Modern Color Palette
    plt.barh(comp_risk.index, values, color='#1f77b4', edgecolor='none', height=0.7)
    
    plt.title('Top 5 Companies by Financial Exposure', fontweight='bold', pad=15)
    plt.xlabel('Stranded Book Value ($ Billion)')
    
    for i, v in enumerate(values):
        plt.text(v + 0.2, i, f'${v:.1f}B', va='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    try:
        df_res, df_sum, df_fac = load_data()
        plot_emissions_trajectory(df_res, 'emissions_trajectory.png')
        plot_stranded_value_comparison(df_sum, 'stranded_value_bar.png')
        plot_top_risks(df_fac, 'top_risks_bar.png')
        print("Figures Refined.")
    except Exception as e:
        print(f"Error: {e}")
