#!/usr/bin/env python3
"""
Generate updated MACC curve with heat pump and without CCS
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_updated_macc():
    """Generate updated MACC curve"""
    
    # Load the updated MACC database
    file_path = 'data/korean_petrochemical_macc_optimization.xlsx'
    
    # Read MACC Template
    macc_template = pd.read_excel(file_path, sheet_name='MACC_Template')
    
    print('=== GENERATING UPDATED MACC CURVE ===')
    print(f'Total technologies: {len(macc_template)}')
    
    # Sort by cost and prepare for plotting
    macc_sorted = macc_template.sort_values('Cost_USD_per_tCO2').reset_index(drop=True)
    macc_sorted['Cumulative_Abatement_MtCO2_per_year'] = macc_sorted['Abatement_Potential_MtCO2_per_year'].cumsum()
    
    # Create MACC curve plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot bars for each technology
    colors = ['green' if cost < 0 else 'lightblue' if cost < 100 else 'orange' if cost < 300 else 'red' 
             for cost in macc_sorted['Cost_USD_per_tCO2']]
    
    bars = ax.bar(macc_sorted['Cumulative_Abatement_MtCO2_per_year'] - macc_sorted['Abatement_Potential_MtCO2_per_year']/2,
                  macc_sorted['Cost_USD_per_tCO2'],
                  width=macc_sorted['Abatement_Potential_MtCO2_per_year'],
                  color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Add technology labels
    for idx, row in macc_sorted.iterrows():
        x_pos = row['Cumulative_Abatement_MtCO2_per_year'] - row['Abatement_Potential_MtCO2_per_year']/2
        y_pos = row['Cost_USD_per_tCO2'] + 20 if row['Cost_USD_per_tCO2'] > 0 else row['Cost_USD_per_tCO2'] - 30
        
        # Rotate text for better readability
        ax.text(x_pos, y_pos, row['TechID'], 
               ha='center', va='center', fontsize=8, rotation=45, weight='bold')
    
    # Formatting
    ax.set_xlabel('Cumulative Abatement Potential (Mt CO₂/year)', fontsize=12, weight='bold')
    ax.set_ylabel('Cost (USD/tonne CO₂)', fontsize=12, weight='bold')
    ax.set_title('Korean Petrochemical MACC Curve (Updated - No CCS, With Heat Pump)\n49.9 Mt CO₂ Baseline', 
                fontsize=14, weight='bold', pad=20)
    
    # Add horizontal line at zero cost
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.7)
    
    # Add baseline emission reference
    baseline_emissions = 49.9
    ax.axvline(x=baseline_emissions, color='red', linestyle='--', linewidth=2, alpha=0.8, 
              label=f'2023 Baseline: {baseline_emissions} Mt CO₂')
    
    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    
    # Set reasonable y-axis limits
    y_max = max(macc_sorted['Cost_USD_per_tCO2']) * 1.1
    y_min = min(macc_sorted['Cost_USD_per_tCO2']) * 1.1 if min(macc_sorted['Cost_USD_per_tCO2']) < 0 else -50
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.savefig('outputs/korean_petrochemical_macc_curve_updated.png', dpi=300, bbox_inches='tight')
    plt.savefig('outputs/korean_petrochemical_macc_curve_updated.pdf', bbox_inches='tight')
    print('✓ MACC curve saved to outputs/korean_petrochemical_macc_curve_updated.png')
    
    # Save updated MACC data
    macc_sorted.to_csv('outputs/macc_analysis_updated.csv', index=False)
    print('✓ MACC data saved to outputs/macc_analysis_updated.csv')
    
    # Display summary
    print(f'\nMACC CURVE SUMMARY:')
    print(f'Total abatement potential: {macc_sorted["Abatement_Potential_MtCO2_per_year"].sum():.1f} Mt CO₂/year')
    print(f'Baseline emissions: {baseline_emissions} Mt CO₂/year')
    print(f'Cost range: ${macc_sorted["Cost_USD_per_tCO2"].min():.0f} to ${macc_sorted["Cost_USD_per_tCO2"].max():.0f}/tCO₂')
    
    # Low-cost options
    low_cost = macc_sorted[macc_sorted['Cost_USD_per_tCO2'] < 100]
    print(f'\nLow-cost technologies (<$100/tCO₂): {len(low_cost)}')
    for _, row in low_cost.iterrows():
        print(f'  {row["TechID"]}: ${row["Cost_USD_per_tCO2"]:.0f}/tCO₂, {row["Abatement_Potential_MtCO2_per_year"]:.1f} Mt CO₂/year')
    
    return macc_sorted

if __name__ == "__main__":
    generate_updated_macc()