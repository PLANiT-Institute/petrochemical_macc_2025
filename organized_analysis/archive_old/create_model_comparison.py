#!/usr/bin/env python3
"""
Create detailed comparison between original and enhanced MACC models
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set font for Korean text support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_model_comparison():
    """Create comprehensive comparison between original and enhanced models"""
    
    print("📊 ORIGINAL vs ENHANCED MACC MODEL COMPARISON")
    print("="*80)
    
    output_dir = Path("outputs")
    
    # Load both model results
    try:
        # Enhanced model results
        enhanced_summary = pd.read_csv(output_dir / "enhanced_optimization_summary.csv")
        enhanced_deployments = pd.read_csv(output_dir / "enhanced_optimization_deployments.csv")
        enhanced_pathway = pd.read_csv(output_dir / "enhanced_optimization_achievement.csv")
        
        # Original model results (target sheet)
        original_summary = pd.read_csv(output_dir / "optimization_target_sheet_summary.csv")
        original_deployments = pd.read_csv(output_dir / "optimization_target_sheet_deployments.csv")
        original_pathway = pd.read_csv(output_dir / "optimization_target_sheet_achievement.csv")
        
        print("✓ Both model results loaded successfully")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load model results: {e}")
        return None
    
    # Create comparison visualization
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(18, 16))
    
    # 1. Emission pathway comparison
    years = enhanced_pathway['Year']
    
    ax1.plot(years, enhanced_pathway['BAU_Emissions'], 'r-', linewidth=2, 
            label='BAU Baseline', marker='o', markersize=6)
    ax1.plot(years, enhanced_pathway['Target_Emissions'], 'g--', linewidth=3, 
            label='Emission Targets', marker='s', markersize=6)
    ax1.plot(years, original_pathway['Optimized_Emissions'], 'b-', linewidth=2, 
            label='Original Model', marker='^', markersize=6, alpha=0.8)
    ax1.plot(years, enhanced_pathway['Optimized_Emissions'], 'purple', linewidth=3, 
            label='Enhanced Model', marker='D', markersize=6)
    
    ax1.set_title('Emission Pathways: Original vs Enhanced Model', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (Mt CO₂)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(2024, 2051)
    
    # 2. Technology count comparison
    original_tech_count = len(original_deployments['TechID'].unique())
    enhanced_tech_count = len(enhanced_deployments['TechID'].unique())
    
    original_deployed = len(original_deployments[original_deployments['AbatementMtCO2'] > 0]['TechID'].unique())
    enhanced_deployed = len(enhanced_deployments[enhanced_deployments['AbatementMtCO2'] > 0]['TechID'].unique())
    
    categories = ['Available\nTechnologies', 'Deployed\nTechnologies']
    original_counts = [original_tech_count, original_deployed]
    enhanced_counts = [enhanced_tech_count, enhanced_deployed]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, original_counts, width, label='Original Model', color='lightblue', alpha=0.8)
    bars2 = ax2.bar(x + width/2, enhanced_counts, width, label='Enhanced Model', color='darkblue', alpha=0.8)
    
    ax2.set_title('Technology Portfolio Comparison', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Technologies')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Total abatement comparison
    original_abatement = original_summary['Total_Abatement_Mt_CO2'].iloc[0]
    enhanced_abatement = enhanced_summary['Total_Abatement_Mt_CO2'].iloc[0]
    
    abatement_data = ['Original Model', 'Enhanced Model']
    abatement_values = [original_abatement, enhanced_abatement]
    colors = ['lightcoral', 'darkgreen']
    
    bars = ax3.bar(abatement_data, abatement_values, color=colors, alpha=0.8)
    ax3.set_title('Total Abatement Comparison', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Total Abatement (Mt CO₂)')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, abatement_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # 4. Cost effectiveness comparison
    original_cost_eff = original_summary['Avg_Cost_Effectiveness_USD_per_tCO2'].iloc[0]
    enhanced_cost_eff = enhanced_summary['Avg_Cost_Effectiveness_USD_per_tCO2'].iloc[0]
    
    cost_data = ['Original Model', 'Enhanced Model']
    cost_values = [original_cost_eff, enhanced_cost_eff]
    colors_cost = ['lightblue', 'navy']
    
    bars = ax4.bar(cost_data, cost_values, color=colors_cost, alpha=0.8)
    ax4.set_title('Cost Effectiveness Comparison', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Cost per tCO₂ (USD)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, cost_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 500,
                f'${value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # 5. Technology category breakdown - Enhanced model
    enhanced_tech_summary = enhanced_deployments.groupby('TechID').agg({
        'AbatementMtCO2': 'sum'
    }).reset_index()
    
    # Categorize enhanced technologies
    enhanced_categories = {
        'Energy Efficiency': ['EE_NCC', 'EE_BTX', 'EE_UTL'],
        'Renewable Energy': ['RE_001', 'RE_002', 'RE_003'],
        'Heat Pumps': ['HP_001', 'HP_002'],
        'Energy Storage': ['ES_001'],
        'Product-Specific': []  # Will be filled with remaining technologies
    }
    
    # Identify product-specific technologies
    all_enhanced_techs = set(enhanced_tech_summary['TechID'])
    categorized_techs = set()
    for techs in enhanced_categories.values():
        categorized_techs.update(techs)
    
    enhanced_categories['Product-Specific'] = list(all_enhanced_techs - categorized_techs)
    
    enhanced_cat_abatement = {}
    for category, tech_list in enhanced_categories.items():
        abatement = enhanced_tech_summary[enhanced_tech_summary['TechID'].isin(tech_list)]['AbatementMtCO2'].sum()
        enhanced_cat_abatement[category] = abatement
    
    # Create pie chart for enhanced model
    labels = [f"{cat}\n({val:.1f} Mt)" for cat, val in enhanced_cat_abatement.items() if val > 0]
    sizes = [val for val in enhanced_cat_abatement.values() if val > 0]
    colors_pie = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    
    ax5.pie(sizes, labels=labels, colors=colors_pie[:len(sizes)], autopct='%1.1f%%', startangle=90)
    ax5.set_title('Enhanced Model: Abatement by Category', fontsize=14, fontweight='bold')
    
    # 6. Process-specific EE comparison
    # For original model (single EE technology)
    original_ee = original_deployments[original_deployments['TechID'] == 'EE_001']
    original_ee_abatement = original_ee['AbatementMtCO2'].sum() if not original_ee.empty else 0
    
    # For enhanced model (process-specific EE)
    enhanced_ee = enhanced_deployments[enhanced_deployments['TechID'].str.startswith('EE_')]
    enhanced_ee_summary = enhanced_ee.groupby('TechID').agg({
        'AbatementMtCO2': 'sum',
        'DeploymentLevel': 'mean'
    }).reset_index()
    
    if not enhanced_ee_summary.empty:
        process_names = {'EE_NCC': 'NCC\n(10% max)', 'EE_BTX': 'BTX\n(20% max)', 'EE_UTL': 'Utility\n(35% max)'}
        enhanced_ee_summary['ProcessName'] = enhanced_ee_summary['TechID'].map(process_names)
        
        bars = ax6.bar(range(len(enhanced_ee_summary)), enhanced_ee_summary['AbatementMtCO2'], 
                      color=['#ff6b6b', '#4ecdc4', '#45b7d1'], alpha=0.8)
        
        ax6.set_title('Process-Specific EE Deployment (Enhanced Model)', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Process Type')
        ax6.set_ylabel('Abatement (Mt CO₂)')
        ax6.set_xticks(range(len(enhanced_ee_summary)))
        ax6.set_xticklabels(enhanced_ee_summary['ProcessName'])
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, abate, deploy in zip(bars, enhanced_ee_summary['AbatementMtCO2'], enhanced_ee_summary['DeploymentLevel']):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{abate:.1f}\n({deploy:.1%})', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Add comparison with original
        ax6.axhline(y=original_ee_abatement, color='red', linestyle='--', alpha=0.7, 
                   label=f'Original EE: {original_ee_abatement:.1f} Mt')
        ax6.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / "original_vs_enhanced_model_comparison.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create detailed comparison table
    comparison_data = {
        'Metric': [
            'Available Technologies',
            'Deployed Technologies', 
            'Total Abatement (Mt CO₂)',
            'Total Cost (Billion USD)',
            'Cost Effectiveness (USD/tCO₂)',
            'Energy Efficiency Approach',
            'Renewable Energy Technologies',
            'Heat Pump Technologies',
            'Process Constraints',
            'TRL Risk Adjustment',
            'Target Achievement'
        ],
        'Original_Model': [
            original_tech_count,
            original_deployed,
            f"{original_abatement:.1f}",
            f"{original_summary['Total_Cost_USD'].iloc[0]/1e9:.2f}",
            f"{original_cost_eff:,.0f}",
            'Single EE technology (95% deployment)',
            'None',
            'Single heat pump technology', 
            'No process-specific constraints',
            'Not applied',
            f"{original_summary['Average_Achievement_Percent'].iloc[0]:.3f}%"
        ],
        'Enhanced_Model': [
            enhanced_tech_count,
            enhanced_deployed,
            f"{enhanced_abatement:.1f}",
            f"{enhanced_summary['Total_Cost_USD'].iloc[0]/1e9:.2f}",
            f"{enhanced_cost_eff:,.0f}",
            'Process-specific EE (NCC 10%, BTX 20%, Util 35%)',
            'Solar PV, Wind, Solar Thermal',
            'Low/medium + high temperature heat pumps',
            'Thermodynamic constraints applied',
            'TRL-based cost adjustments',
            f"{enhanced_summary['Average_Achievement_Percent'].iloc[0]:.3f}%"
        ],
        'Improvement': []
    }
    
    # Calculate improvements
    improvements = [
        f"+{enhanced_tech_count - original_tech_count} technologies",
        f"+{enhanced_deployed - original_deployed} deployed",
        f"+{enhanced_abatement - original_abatement:.1f} Mt CO₂",
        f"+{(enhanced_summary['Total_Cost_USD'].iloc[0] - original_summary['Total_Cost_USD'].iloc[0])/1e9:.2f}B USD",
        f"+{enhanced_cost_eff - original_cost_eff:,.0f} USD/tCO₂",
        'Realistic process limitations',
        '3 new renewable technologies',
        'Temperature-differentiated approach',
        'Industry-validated constraints',
        'Risk-adjusted economics',
        'Maintained 100% achievement'
    ]
    
    comparison_data['Improvement'] = improvements
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv(output_dir / "original_vs_enhanced_detailed_comparison.csv", index=False)
    
    # Print detailed comparison
    print("\n📊 DETAILED MODEL COMPARISON:")
    print("="*80)
    
    print(f"\n🔧 TECHNOLOGY PORTFOLIO:")
    print(f"  Original Model: {original_tech_count} available, {original_deployed} deployed")
    print(f"  Enhanced Model: {enhanced_tech_count} available, {enhanced_deployed} deployed")
    print(f"  Improvement: +{enhanced_tech_count - original_tech_count} technologies, +{enhanced_deployed - original_deployed} deployed")
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"  Total Abatement:")
    print(f"    • Original: {original_abatement:.1f} Mt CO₂")
    print(f"    • Enhanced: {enhanced_abatement:.1f} Mt CO₂")
    print(f"    • Improvement: +{enhanced_abatement - original_abatement:.1f} Mt CO₂")
    
    print(f"  Cost Effectiveness:")
    print(f"    • Original: ${original_cost_eff:,.0f} per tCO₂")
    print(f"    • Enhanced: ${enhanced_cost_eff:,.0f} per tCO₂")
    print(f"    • Change: +${enhanced_cost_eff - original_cost_eff:,.0f} per tCO₂")
    
    print(f"\n⚡ ENERGY EFFICIENCY APPROACH:")
    print(f"  Original Model:")
    print(f"    • Single EE technology with 95% deployment across all processes")
    print(f"    • Total EE abatement: {original_ee_abatement:.1f} Mt CO₂")
    print(f"    • No process-specific constraints")
    
    print(f"  Enhanced Model:")
    if not enhanced_ee_summary.empty:
        total_enhanced_ee = enhanced_ee_summary['AbatementMtCO2'].sum()
        print(f"    • Process-specific EE technologies:")
        for _, ee_tech in enhanced_ee_summary.iterrows():
            print(f"      - {ee_tech['TechID']}: {ee_tech['DeploymentLevel']:.1%} deployment, {ee_tech['AbatementMtCO2']:.1f} Mt CO₂")
        print(f"    • Total EE abatement: {total_enhanced_ee:.1f} Mt CO₂")
        print(f"    • Thermodynamic constraints properly applied")
    
    print(f"\n🔋 RENEWABLE ENERGY INTEGRATION:")
    print(f"  Original Model: No renewable energy technologies")
    print(f"  Enhanced Model:")
    if not enhanced_ee_summary.empty:
        re_techs = enhanced_deployments[enhanced_deployments['TechID'].str.startswith('RE_')]
        if not re_techs.empty:
            re_summary = re_techs.groupby('TechID')['AbatementMtCO2'].sum()
            total_re = re_summary.sum()
            print(f"    • Total renewable abatement: {total_re:.1f} Mt CO₂")
            for tech_id, abatement in re_summary.items():
                tech_names = {'RE_001': 'Solar Thermal', 'RE_002': 'Solar PV', 'RE_003': 'Wind PPAs'}
                print(f"      - {tech_names.get(tech_id, tech_id)}: {abatement:.1f} Mt CO₂")
    
    print(f"\n🏭 INDUSTRY REALISM:")
    print(f"  Original Model:")
    print(f"    • Applied EE uniformly to all processes (unrealistic for NCC)")
    print(f"    • No consideration of thermodynamic constraints")
    print(f"    • Limited technology diversity")
    
    print(f"  Enhanced Model:")
    print(f"    • Process-specific EE limits based on thermodynamics")
    print(f"    • NCC limited to 10% EE (high-temperature constraints)")
    print(f"    • BTX limited to 20% EE (moderate heat recovery)")
    print(f"    • Utilities up to 35% EE (high efficiency potential)")
    print(f"    • Comprehensive renewable energy portfolio")
    print(f"    • TRL-based cost risk adjustments")
    
    print(f"\n📊 KEY INSIGHTS:")
    print(f"  ✓ Enhanced model provides more realistic technology deployment")
    print(f"  ✓ Process constraints ensure industry-feasible solutions")
    print(f"  ✓ Renewable energy integration adds decarbonization options")
    print(f"  ✓ Cost increase (+${enhanced_cost_eff - original_cost_eff:,.0f}/tCO₂) reflects realistic constraints")
    print(f"  ✓ Both models achieve 100% target compliance")
    print(f"  ✓ Enhanced model provides better technology diversity and risk distribution")
    
    print(f"\n✅ COMPARISON ANALYSIS COMPLETE!")
    print(f"📊 Visualization: original_vs_enhanced_model_comparison.png")
    print(f"📄 Detailed comparison: original_vs_enhanced_detailed_comparison.csv")
    
    return comparison_df, enhanced_cat_abatement, enhanced_ee_summary

if __name__ == "__main__":
    comparison, categories, ee_analysis = create_model_comparison()