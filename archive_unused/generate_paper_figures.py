import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.5)

OUTPUT_DIR = Path('outputs/figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_emissions_pathway():
    """Generate BAU vs Net Zero emissions trajectory"""
    print("Generating Emissions Pathway Figure...")
    
    # Mock data based on model outputs (ideally load from CSV)
    years = np.arange(2025, 2051)
    
    # BAU: 52 Mt in 2025 -> 53.3 Mt in 2050 (slight growth)
    bau = np.linspace(52.0, 53.3, len(years))
    
    # Net Zero: 52 Mt -> 0 Mt (S-curve or linear)
    # Using the target trajectory
    net_zero = np.interp(years, [2025, 2035, 2050], [52.0, 39.26, 0.0])
    
    df = pd.DataFrame({
        'Year': years,
        'BAU': bau,
        'Net Zero Pathway': net_zero
    })
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['Year'], df['BAU'], '--', color='gray', label='Business as Usual (BAU)', linewidth=2)
    plt.plot(df['Year'], df['Net Zero Pathway'], '-', color='#2E75B6', label='Net Zero Pathway', linewidth=3)
    
    plt.fill_between(df['Year'], df['BAU'], df['Net Zero Pathway'], color='#2E75B6', alpha=0.1, label='Abatement')
    
    plt.title('Decarbonization Pathway for Korean Petrochemical Industry', pad=20)
    plt.ylabel('Emissions (MtCO$_2$/year)')
    plt.xlabel('Year')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 60)
    plt.xlim(2025, 2050)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_emissions_pathway.png', dpi=300)
    plt.close()

def generate_cost_waterfall():
    """Generate 2050 Cost Waterfall"""
    print("Generating Cost Waterfall Figure...")
    
    # Data from report
    categories = ['CAPEX', 'OPEX', 'Energy Cost']
    values = [18.2, 4.1, 15.0] # Billions
    total = sum(values)
    
    plt.figure(figsize=(8, 6))
    
    # Cumulative sum for waterfall effect
    bottom = 0
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, (cat, val) in enumerate(zip(categories, values)):
        plt.bar(cat, val, bottom=bottom, color=colors[i], label=cat, width=0.6)
        # Add text
        plt.text(i, bottom + val/2, f'${val:.1f}B', ha='center', va='center', color='white', fontweight='bold')
        bottom += val
        
    # Total bar
    plt.bar('Total', total, color='gray', width=0.6)
    plt.text(3, total + 0.5, f'${total:.1f}B', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Cumulative Investment & Cost (2025-2050)', pad=20)
    plt.ylabel('Billions USD (Real 2024)')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_cost_waterfall.png', dpi=300)
    plt.close()

def generate_scenario_comparison():
    """Generate Scenario Comparison Bar Chart"""
    print("Generating Scenario Comparison Figure...")
    
    scenarios = ['NCC-Electricity', 'NCC-H2']
    capex = [900, 780] # $/t
    energy_cost = [8.0, 4.5] # $B/yr in 2050
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # CAPEX Comparison
    ax1.bar(scenarios, capex, color=['#1f77b4', '#2ca02c'], alpha=0.8)
    ax1.set_title('Technology CAPEX (2050)')
    ax1.set_ylabel('USD / ton Ethylene')
    for i, v in enumerate(capex):
        ax1.text(i, v + 10, f'${v}', ha='center')
        
    # Energy Cost Comparison
    ax2.bar(scenarios, energy_cost, color=['#1f77b4', '#2ca02c'], alpha=0.8)
    ax2.set_title('Annual Energy Cost (2050)')
    ax2.set_ylabel('Billion USD / year')
    for i, v in enumerate(energy_cost):
        ax2.text(i, v + 0.1, f'${v}B', ha='center')
        
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_scenario_comparison.png', dpi=300)
    plt.close()

def main():
    generate_emissions_pathway()
    generate_cost_waterfall()
    generate_scenario_comparison()
    print(f"Figures generated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
