#!/usr/bin/env python3
"""
Create comprehensive visualizations for the cost analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set font and style
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('default')

def create_cost_analysis_visualizations():
    """Create comprehensive visualizations for all cost analysis components"""
    
    print("📊 CREATING COMPREHENSIVE COST ANALYSIS VISUALIZATIONS")
    print("="*80)
    
    # Run the analysis first to get data
    from create_comprehensive_cost_analysis import create_comprehensive_cost_analysis
    results = create_comprehensive_cost_analysis()
    
    output_dir = Path("outputs")
    
    # Extract data from results
    npv_results = results['npv_results']
    baseline_npvs = results['baseline_npvs']
    annual_costs_df = results['annual_costs_df']
    stranded_analysis = results['stranded_analysis']
    stranding_timeline_df = results['stranding_timeline_df']
    portfolio_shares_df = results['portfolio_shares_df']
    enhanced_pathway = results['enhanced_pathway']
    scenario_results = results['scenario_results']
    financial_params = results['financial_params']
    
    # Create comprehensive figure with all analyses
    fig = plt.figure(figsize=(28, 24))
    gs = fig.add_gridspec(5, 4, hspace=0.3, wspace=0.3)
    
    # 🔹 1. OVERALL COST OUTCOMES
    
    # 1a. NPV Comparison Bar Chart
    ax1 = fig.add_subplot(gs[0, 0])
    
    scenario_names = ['Optimized'] + list(baseline_npvs.keys())
    scenario_npvs = [npv_results['Total_NPV_Billion_USD']] + [baseline_npvs[s]['Total_NPV'] for s in baseline_npvs.keys()]
    
    colors = ['green', 'red', 'orange', 'purple']
    bars = ax1.bar(range(len(scenario_names)), scenario_npvs, color=colors, alpha=0.8)
    
    ax1.set_title('Total Cost NPV Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylabel('NPV (Billion USD)')
    ax1.set_xticks(range(len(scenario_names)))
    ax1.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels and savings
    for i, (bar, value) in enumerate(zip(bars, scenario_npvs)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'${value:.1f}B', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        if i > 0:  # Show savings compared to optimized
            savings = scenario_npvs[0] - value
            savings_pct = (savings / value) * 100 if value != 0 else 0
            ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{savings_pct:+.1f}%', ha='center', va='center', 
                    color='white', fontweight='bold', fontsize=9)
    
    # 1b. Cost Component Breakdown
    ax2 = fig.add_subplot(gs[0, 1])
    
    components = ['CAPEX', 'OPEX', 'Carbon', 'Stranded']
    optimized_values = [
        npv_results['CAPEX_NPV_Billion_USD'],
        npv_results['OPEX_NPV_Billion_USD'], 
        npv_results['Carbon_NPV_Billion_USD'],
        npv_results['Stranded_NPV_Billion_USD']
    ]
    
    colors_comp = ['blue', 'green', 'orange', 'red']
    bars = ax2.bar(components, optimized_values, color=colors_comp, alpha=0.8)
    
    ax2.set_title('Optimized Pathway Cost Breakdown', fontsize=14, fontweight='bold')
    ax2.set_ylabel('NPV (Billion USD)')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, optimized_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'${value:.1f}B', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 1c. Annual Cost Timeline
    ax3 = fig.add_subplot(gs[0, 2:])
    
    ax3.stackplot(annual_costs_df['Year'], 
                 annual_costs_df['CAPEX_USD'] / 1e9,
                 annual_costs_df['OPEX_USD'] / 1e9,
                 annual_costs_df['Carbon_Payments_USD'] / 1e9,
                 annual_costs_df['Stranded_Value_USD'] / 1e9,
                 labels=['CAPEX', 'OPEX', 'Carbon Payments', 'Stranded Value'],
                 colors=colors_comp, alpha=0.8)
    
    ax3.set_title('Annual Cost Components Timeline', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Annual Cost (Billion USD)')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 🔹 2. STRANDED ASSET RISK
    
    # 2a. Stranded Value by Age Cohort
    ax4 = fig.add_subplot(gs[1, 0])
    
    cohorts = stranded_analysis['Age_Cohort'].astype(str)
    stranded_values = stranded_analysis['Expected_Stranded_Value_Million_USD'] / 1000  # Convert to billions
    
    bars = ax4.bar(range(len(cohorts)), stranded_values, 
                  color=plt.cm.Reds(np.linspace(0.3, 0.9, len(cohorts))), alpha=0.8)
    
    ax4.set_title('Expected Stranded Value by Age Cohort', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Facility Age Cohort')
    ax4.set_ylabel('Stranded Value (Billion USD)')
    ax4.set_xticks(range(len(cohorts)))
    ax4.set_xticklabels(cohorts, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, stranded_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'${value:.1f}B', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 2b. Stranding Timeline
    ax5 = fig.add_subplot(gs[1, 1])
    
    ax5.plot(stranding_timeline_df['Year'], stranding_timeline_df['Annual_Stranded_Value_Million_USD'],
            marker='o', linewidth=2, markersize=6, color='red', alpha=0.8)
    
    ax5.set_title('Annual Stranded Value Timeline', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Annual Stranded Value (Million USD)')
    ax5.grid(True, alpha=0.3)
    
    # 2c. Asset Risk Heatmap
    ax6 = fig.add_subplot(gs[1, 2:])
    
    # Create risk matrix data
    risk_data = stranded_analysis[['Age_Cohort', 'Facility_Count', 'Book_Value_Million_USD', 'Stranding_Risk']].copy()
    risk_data['Risk_Level'] = pd.cut(risk_data['Stranding_Risk'], bins=[0, 0.2, 0.5, 0.8, 1.0], 
                                    labels=['Low', 'Medium', 'High', 'Critical'])
    
    # Create heatmap data
    heatmap_data = risk_data.pivot_table(values='Book_Value_Million_USD', 
                                        index='Age_Cohort', columns='Risk_Level', 
                                        fill_value=0, aggfunc='sum')
    
    if not heatmap_data.empty:
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='Reds', ax=ax6,
                   cbar_kws={'label': 'Book Value (Million USD)'})
        ax6.set_title('Asset Risk Matrix: Book Value by Age and Risk Level', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Risk Level')
        ax6.set_ylabel('Age Cohort')
    
    # 🔹 3. INVESTMENT & RETIREMENT TIMING
    
    # 3a. Annual CAPEX Schedule
    ax7 = fig.add_subplot(gs[2, 0])
    
    bars = ax7.bar(annual_costs_df['Year'], annual_costs_df['CAPEX_USD'] / 1e9, 
                  color='blue', alpha=0.7)
    
    ax7.set_title('Annual CAPEX Investment Schedule', fontsize=14, fontweight='bold')
    ax7.set_xlabel('Year')
    ax7.set_ylabel('CAPEX (Billion USD)')
    ax7.grid(True, alpha=0.3, axis='y')
    
    # Highlight peak investment years
    max_capex_year = annual_costs_df.loc[annual_costs_df['CAPEX_USD'].idxmax(), 'Year']
    max_capex_value = annual_costs_df['CAPEX_USD'].max() / 1e9
    ax7.text(max_capex_year, max_capex_value + 0.02, f'Peak: ${max_capex_value:.1f}B',
            ha='center', va='bottom', fontweight='bold', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # 3b. Technology Portfolio Evolution
    ax8 = fig.add_subplot(gs[2, 1:3])
    
    # Create technology share evolution
    tech_evolution = portfolio_shares_df.pivot(index='Year', columns='TechID', values='Portfolio_Share').fillna(0)
    
    # Select top technologies for clarity
    if not tech_evolution.empty:
        tech_totals = tech_evolution.sum().sort_values(ascending=False)
        top_techs = tech_totals.head(6).index
        tech_evolution_top = tech_evolution[top_techs]
        
        # Create stacked area plot
        ax8.stackplot(tech_evolution_top.index, *[tech_evolution_top[col] for col in tech_evolution_top.columns],
                     labels=tech_evolution_top.columns, alpha=0.8)
        
        ax8.set_title('Technology Portfolio Share Evolution', fontsize=14, fontweight='bold')
        ax8.set_xlabel('Year')
        ax8.set_ylabel('Portfolio Share')
        ax8.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax8.grid(True, alpha=0.3)
    
    # 3c. Investment Lumpiness Analysis
    ax9 = fig.add_subplot(gs[2, 3])
    
    # Calculate 5-year rolling average to show smoothness
    annual_costs_df['CAPEX_5yr_avg'] = annual_costs_df['CAPEX_USD'].rolling(window=5, center=True).mean()
    
    ax9.plot(annual_costs_df['Year'], annual_costs_df['CAPEX_USD'] / 1e9, 
            'o-', label='Annual CAPEX', alpha=0.7, linewidth=2)
    ax9.plot(annual_costs_df['Year'], annual_costs_df['CAPEX_5yr_avg'] / 1e9, 
            '--', label='5-Year Average', linewidth=3, color='red')
    
    ax9.set_title('Investment Smoothness Analysis', fontsize=14, fontweight='bold')
    ax9.set_xlabel('Year')
    ax9.set_ylabel('CAPEX (Billion USD)')
    ax9.legend()
    ax9.grid(True, alpha=0.3)
    
    # 🔹 4. EMISSIONS PATHWAY
    
    # 4a. Annual Emissions Trajectory
    ax10 = fig.add_subplot(gs[3, :2])
    
    ax10.fill_between(enhanced_pathway['Year'], enhanced_pathway['BAU_Emissions'], 
                     enhanced_pathway['Optimized_Emissions'], alpha=0.3, color='green',
                     label='Abatement Achieved')
    ax10.plot(enhanced_pathway['Year'], enhanced_pathway['BAU_Emissions'], 
             'r-', linewidth=3, marker='o', markersize=8, label='BAU Pathway')
    ax10.plot(enhanced_pathway['Year'], enhanced_pathway['Target_Emissions'], 
             'g--', linewidth=3, marker='s', markersize=8, label='Emission Targets')
    ax10.plot(enhanced_pathway['Year'], enhanced_pathway['Optimized_Emissions'], 
             'b-', linewidth=3, marker='^', markersize=8, label='Optimized Pathway')
    
    ax10.set_title('Emissions Pathway and Target Compliance', fontsize=14, fontweight='bold')
    ax10.set_xlabel('Year')
    ax10.set_ylabel('Emissions (Mt CO₂)')
    ax10.legend()
    ax10.grid(True, alpha=0.3)
    
    # Add compliance indicators
    for _, row in enhanced_pathway.iterrows():
        compliance = "✓" if row['Target_Compliance'] else "⚠"
        ax10.text(row['Year'], row['Optimized_Emissions'] + 1, compliance, 
                 ha='center', va='bottom', fontweight='bold', fontsize=12,
                 color='green' if row['Target_Compliance'] else 'orange')
    
    # 4b. Cumulative Emissions Analysis
    ax11 = fig.add_subplot(gs[3, 2:])
    
    ax11.plot(enhanced_pathway['Year'], enhanced_pathway['Cumulative_BAU_Mt'], 
             'r-', linewidth=3, label='BAU Cumulative', alpha=0.8)
    ax11.plot(enhanced_pathway['Year'], enhanced_pathway['Cumulative_Optimized_Mt'], 
             'b-', linewidth=3, label='Optimized Cumulative')
    ax11.fill_between(enhanced_pathway['Year'], enhanced_pathway['Cumulative_BAU_Mt'], 
                     enhanced_pathway['Cumulative_Optimized_Mt'], alpha=0.3, color='green',
                     label='Cumulative Abatement')
    
    ax11.set_title('Cumulative Emissions and Carbon Budget', fontsize=14, fontweight='bold')
    ax11.set_xlabel('Year')
    ax11.set_ylabel('Cumulative Emissions (Mt CO₂)')
    ax11.legend()
    ax11.grid(True, alpha=0.3)
    
    # Add final values
    final_abatement = enhanced_pathway['Cumulative_Abatement_Mt'].iloc[-1]
    ax11.text(2045, enhanced_pathway['Cumulative_Optimized_Mt'].iloc[-1] + 20,
             f'Total Abatement\n{final_abatement:.0f} Mt CO₂', 
             ha='center', va='bottom', fontweight='bold', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))
    
    # 🔹 5. RISK & UNCERTAINTY ANALYSIS
    
    # 5a. Cost Distribution by Carbon Price Scenario
    ax12 = fig.add_subplot(gs[4, 0])
    
    scenario_names_risk = list(scenario_results.keys())
    scenario_npvs_risk = [scenario_results[s]['NPV_Billion_USD'] for s in scenario_names_risk]
    
    colors_risk = ['blue', 'green', 'red']
    bars = ax12.bar(scenario_names_risk, scenario_npvs_risk, 
                   color=colors_risk, alpha=0.8)
    
    ax12.set_title('Total Cost by Carbon Price Scenario', fontsize=14, fontweight='bold')
    ax12.set_xlabel('Carbon Price Scenario')
    ax12.set_ylabel('Total NPV (Billion USD)')
    ax12.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, scenario_npvs_risk):
        height = bar.get_height()
        ax12.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'${value:.1f}B', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 5b. CVaR Analysis
    ax13 = fig.add_subplot(gs[4, 1])
    
    # Box plot of scenario costs
    ax13.boxplot(scenario_npvs_risk, labels=['Cost Distribution'])
    ax13.set_title('Cost Distribution and Risk Metrics', fontsize=14, fontweight='bold')
    ax13.set_ylabel('NPV (Billion USD)')
    ax13.grid(True, alpha=0.3)
    
    # Add statistics
    mean_cost = np.mean(scenario_npvs_risk)
    cvar_95 = np.percentile(scenario_npvs_risk, 95)
    ax13.axhline(y=mean_cost, color='red', linestyle='--', alpha=0.7, label=f'Mean: ${mean_cost:.1f}B')
    ax13.axhline(y=cvar_95, color='orange', linestyle='--', alpha=0.7, label=f'CVaR 95%: ${cvar_95:.1f}B')
    ax13.legend()
    
    # 5c. Scenario Pathway Comparison
    ax14 = fig.add_subplot(gs[4, 2:])
    
    # Create scenario-specific carbon cost timelines
    carbon_price_scenarios = financial_params['carbon_price_scenarios']
    
    for i, (scenario_name, price_path) in enumerate(carbon_price_scenarios.items()):
        # Interpolate prices for full timeline
        years_full = list(range(2025, 2051))
        prices_interpolated = []
        
        for year in years_full:
            if year <= 2025:
                price = price_path['2025']
            elif year <= 2030:
                progress = (year - 2025) / (2030 - 2025)
                price = price_path['2025'] + progress * (price_path['2030'] - price_path['2025'])
            elif year <= 2040:
                progress = (year - 2030) / (2040 - 2030)
                price = price_path['2030'] + progress * (price_path['2040'] - price_path['2030'])
            else:
                progress = (year - 2040) / (2050 - 2040)
                price = price_path['2040'] + progress * (price_path['2050'] - price_path['2040'])
            
            prices_interpolated.append(price)
        
        ax14.plot(years_full, prices_interpolated, linewidth=3, alpha=0.8,
                 label=f'{scenario_name} Scenario', color=colors_risk[i])
    
    ax14.set_title('Carbon Price Scenarios Timeline', fontsize=14, fontweight='bold')
    ax14.set_xlabel('Year')
    ax14.set_ylabel('Carbon Price (USD/tCO₂)')
    ax14.legend()
    ax14.grid(True, alpha=0.3)
    
    # Add cost range annotation
    cost_range_text = f"Total Cost Range: ${min(scenario_npvs_risk):.1f}B - ${max(scenario_npvs_risk):.1f}B"
    ax14.text(0.02, 0.98, cost_range_text, transform=ax14.transAxes,
             ha='left', va='top', fontweight='bold', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / "comprehensive_cost_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed data tables
    print(f"\n💾 SAVING DETAILED ANALYSIS DATA:")
    
    # 1. Overall cost outcomes summary
    cost_summary = pd.DataFrame({
        'Metric': ['Total NPV', 'CAPEX NPV', 'OPEX NPV', 'Carbon Payments NPV', 'Stranded Assets NPV'],
        'Optimized_Billion_USD': [
            npv_results['Total_NPV_Billion_USD'],
            npv_results['CAPEX_NPV_Billion_USD'],
            npv_results['OPEX_NPV_Billion_USD'],
            npv_results['Carbon_NPV_Billion_USD'],
            npv_results['Stranded_NPV_Billion_USD']
        ]
    })
    
    # Add baseline comparisons
    for scenario, results in baseline_npvs.items():
        cost_summary[f'{scenario}_Billion_USD'] = [
            results['Total_NPV'], results['CAPEX_NPV'], results['OPEX_NPV'],
            results['Carbon_NPV'], results['Stranded_NPV']
        ]
    
    cost_summary.to_csv(output_dir / "cost_outcomes_summary.csv", index=False)
    
    # 2. Annual cost breakdown
    annual_costs_df.to_csv(output_dir / "annual_cost_breakdown.csv", index=False)
    
    # 3. Stranded asset analysis
    stranded_analysis.to_csv(output_dir / "stranded_asset_analysis.csv", index=False)
    stranding_timeline_df.to_csv(output_dir / "stranding_timeline.csv", index=False)
    
    # 4. Technology portfolio evolution
    if not portfolio_shares_df.empty:
        portfolio_shares_df.to_csv(output_dir / "technology_portfolio_evolution.csv", index=False)
    
    # 5. Enhanced emissions pathway
    enhanced_pathway.to_csv(output_dir / "emissions_pathway_detailed.csv", index=False)
    
    # 6. Risk scenario analysis
    risk_scenario_summary = pd.DataFrame({
        'Scenario': list(scenario_results.keys()),
        'NPV_Billion_USD': [scenario_results[s]['NPV_Billion_USD'] for s in scenario_results.keys()]
    })
    risk_scenario_summary.to_csv(output_dir / "risk_scenario_analysis.csv", index=False)
    
    print(f"  ✓ cost_outcomes_summary.csv")
    print(f"  ✓ annual_cost_breakdown.csv") 
    print(f"  ✓ stranded_asset_analysis.csv")
    print(f"  ✓ stranding_timeline.csv")
    print(f"  ✓ technology_portfolio_evolution.csv")
    print(f"  ✓ emissions_pathway_detailed.csv")
    print(f"  ✓ risk_scenario_analysis.csv")
    
    print(f"\n📊 COMPREHENSIVE COST ANALYSIS COMPLETE!")
    print(f"  📈 Main visualization: comprehensive_cost_analysis.png")
    print(f"  📄 {7} detailed data files generated")
    
    return {
        'cost_summary': cost_summary,
        'annual_costs': annual_costs_df,
        'stranded_analysis': stranded_analysis,
        'portfolio_evolution': portfolio_shares_df,
        'emissions_pathway': enhanced_pathway,
        'risk_scenarios': risk_scenario_summary
    }

if __name__ == "__main__":
    visualization_results = create_cost_analysis_visualizations()