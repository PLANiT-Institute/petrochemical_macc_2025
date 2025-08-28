#!/usr/bin/env python3
"""
Enhanced Korean Petrochemical MACC Optimization Model
====================================================

Combines the optimization logic from simple.py with comprehensive
visualization, investment planning, and scenario analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pulp
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")

from archive.development_scripts.run_optimization_model_v3_facility_based import (
    load_facility_based_data, 
    calculate_facility_baseline_emissions,
    calculate_process_baseline_emissions,
    calculate_alternative_emissions, 
    calculate_technology_costs
)

def create_simple_viable_options(facilities_df, consumption_df, technologies_df, costs_df, 
                                emission_factors_ts_df, fuel_costs_ts_df, target_year):
    """Create viable options using simpler logic"""
    
    print(f"Creating viable options for {target_year}...")
    
    # Get year-specific factors
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == target_year].iloc[0]
    fc_year = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == target_year].iloc[0]
    
    # Merge technology and cost data
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    
    viable_options = []
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        
        # Get baseline consumption for this facility
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        for _, process_row in facility_consumption.iterrows():
            process_type = process_row['ProcessType']
            capacity = process_row['Activity_kt_product']
            
            # Get applicable technologies
            applicable_techs = tech_costs[
                (tech_costs['TechGroup'] == process_type) &
                (tech_costs['CommercialYear'] <= target_year) &
                (tech_costs['TechnicalReadiness'] >= facility['TechnicalReadiness_Level'])
            ]
            
            # Calculate baseline emissions
            baseline_emissions = calculate_process_baseline_emissions(process_row, ef_year)
            
            for _, tech in applicable_techs.iterrows():
                # Calculate alternative emissions
                alt_emissions = calculate_alternative_emissions(tech, capacity, ef_year)
                
                # Calculate abatement
                abatement_potential = baseline_emissions - alt_emissions
                
                if abatement_potential > 0:  # Only positive abatement
                    # Calculate costs
                    try:
                        costs_result = calculate_technology_costs(tech, capacity, fc_year, facility)
                        annual_cost = costs_result['AnnualCost_USD']
                        lcoa = annual_cost / (abatement_potential * 1000)
                        
                        if 0 < lcoa < 25000:  # Reasonable cost threshold
                            viable_options.append({
                                'FacilityID': facility_id,
                                'Company': facility['Company'],
                                'Region': facility['Region'],
                                'ProcessType': process_type,
                                'TechID': tech['TechID'],
                                'TechnologyCategory': tech['TechnologyCategory'],
                                'Capacity_kt_per_year': capacity,
                                'BaselineEmissions_ktCO2': baseline_emissions,
                                'AlternativeEmissions_ktCO2': alt_emissions,
                                'AbatementPotential_ktCO2': abatement_potential,
                                'LCOA_USD_per_tCO2': lcoa,
                                'AnnualCost_USD': annual_cost,
                                'CAPEX_Million_USD': costs_result.get('CAPEX_Million_USD', 0),
                                'TechnicalReadiness': tech['TechnicalReadiness'],
                                'CommercialYear': tech['CommercialYear']
                            })
                    except Exception as e:
                        print(f"      Cost calculation error for {facility_id}-{process_type}-{tech['TechID']}: {e}")
    
    viable_df = pd.DataFrame(viable_options)
    print(f"  • Total viable options: {len(viable_df)}")
    
    return viable_df

def solve_simple_optimization(viable_df, baseline_emissions_df, targets_df, target_year):
    """Solve optimization with simple approach"""
    
    if len(viable_df) == 0:
        print(f"❌ No viable options for {target_year}")
        return pd.DataFrame(), "No viable options"
    
    print(f"\\nSolving optimization for {target_year}...")
    
    # Get emission reduction target
    year_target = targets_df[targets_df['Year'] == target_year]
    if len(year_target) == 0:
        # Interpolate or use default
        if target_year == 2030:
            target_emissions = 12.0  # MtCO2
        elif target_year == 2040:
            target_emissions = 7.5   # MtCO2
        elif target_year == 2050:
            target_emissions = 3.0   # MtCO2
        else:
            target_emissions = 10.0  # MtCO2
    else:
        target_emissions = year_target['Target_MtCO2'].iloc[0]
    
    # Calculate required reduction
    total_baseline_emissions = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    target_ktCO2 = target_emissions * 1000  # Convert to ktCO2
    required_reduction = total_baseline_emissions - target_ktCO2
    reduction_pct = (required_reduction / total_baseline_emissions) * 100
    
    print(f"  • Target: {target_emissions:.1f} MtCO2 ({target_ktCO2:.0f} ktCO2)")
    print(f"  • Required reduction: {required_reduction:.1f} ktCO2/year ({reduction_pct:.1f}%)")
    print(f"  • Available options: {len(viable_df)}")
    
    # Create optimization problem
    prob = pulp.LpProblem("Petrochemical_MACC_Enhanced", pulp.LpMinimize)
    
    # Decision variables
    deploy_vars = {}
    for idx, row in viable_df.iterrows():
        var_name = f"deploy_{idx}"
        deploy_vars[idx] = pulp.LpVariable(var_name, 0, 1, pulp.LpContinuous)
    
    # Objective: minimize total cost
    objective = pulp.lpSum([
        row['AnnualCost_USD'] * deploy_vars[idx]
        for idx, row in viable_df.iterrows()
    ])
    prob += objective, "Total_Cost"
    
    # Constraint: meet emission reduction target
    total_abatement = pulp.lpSum([
        row['AbatementPotential_ktCO2'] * deploy_vars[idx]
        for idx, row in viable_df.iterrows()
    ])
    prob += total_abatement >= required_reduction, "Emission_Target"
    
    # Constraint: At most one technology per facility-process
    facility_process_combos = viable_df.groupby(['FacilityID', 'ProcessType']).groups
    
    for (facility_id, process_type), indices in facility_process_combos.items():
        applicable_vars = [deploy_vars[idx] for idx in indices if idx in deploy_vars]
        if len(applicable_vars) > 1:
            constraint_name = f"Max_One_{facility_id}_{process_type}"
            prob += pulp.lpSum(applicable_vars) <= 1, constraint_name
    
    print(f"  • Constraints: {len(prob.constraints)}")
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    status = pulp.LpStatus[prob.status]
    print(f"  • Solution status: {status}")
    
    if status == 'Optimal':
        # Extract solution
        solution_data = []
        
        for idx, row in viable_df.iterrows():
            if idx in deploy_vars:
                deployment_level = deploy_vars[idx].value()
                if deployment_level is not None and deployment_level > 0.01:
                    solution_data.append({
                        'FacilityID': row['FacilityID'],
                        'Company': row['Company'],
                        'Region': row['Region'],
                        'ProcessType': row['ProcessType'],
                        'TechID': row['TechID'],
                        'TechnologyCategory': row['TechnologyCategory'],
                        'DeploymentLevel': deployment_level,
                        'AbatementAchieved_ktCO2': row['AbatementPotential_ktCO2'] * deployment_level,
                        'AnnualCost_USD': row['AnnualCost_USD'] * deployment_level,
                        'CAPEX_Million_USD': row['CAPEX_Million_USD'] * deployment_level,
                        'LCOA_USD_per_tCO2': row['LCOA_USD_per_tCO2']
                    })
        
        solution_df = pd.DataFrame(solution_data)
        
        if len(solution_df) > 0:
            total_abatement = solution_df['AbatementAchieved_ktCO2'].sum()
            total_cost = solution_df['AnnualCost_USD'].sum()
            print(f"  • Total abatement: {total_abatement:.1f} ktCO2/year")
            print(f"  • Total cost: ${total_cost:,.0f}/year")
            print(f"  • Target achievement: {(total_abatement/required_reduction*100):.1f}%")
        
        return solution_df, status
    
    else:
        print(f"❌ Optimization failed: {status}")
        return pd.DataFrame(), status

def create_investment_analysis(all_results, target_years):
    """Create investment analysis over time"""
    
    investment_data = []
    
    for year in target_years:
        if year in all_results:
            solution_df = all_results[year]
            
            # Calculate investment metrics
            total_capex = solution_df['CAPEX_Million_USD'].sum()
            total_annual_cost = solution_df['AnnualCost_USD'].sum()
            total_abatement = solution_df['AbatementAchieved_ktCO2'].sum()
            
            # Regional breakdown
            regional_investment = solution_df.groupby('Region').agg({
                'CAPEX_Million_USD': 'sum',
                'AnnualCost_USD': 'sum',
                'AbatementAchieved_ktCO2': 'sum'
            })
            
            # Technology breakdown
            tech_investment = solution_df.groupby('TechnologyCategory').agg({
                'CAPEX_Million_USD': 'sum',
                'AnnualCost_USD': 'sum',
                'AbatementAchieved_ktCO2': 'sum'
            })
            
            investment_data.append({
                'Year': year,
                'Total_CAPEX_Million_USD': total_capex,
                'Total_Annual_Cost_Million_USD': total_annual_cost / 1e6,
                'Total_Abatement_ktCO2': total_abatement,
                'Avg_LCOA_USD_per_tCO2': total_annual_cost / (total_abatement * 1000) if total_abatement > 0 else 0,
                'Regional_Investment': regional_investment.to_dict(),
                'Technology_Investment': tech_investment.to_dict()
            })
    
    return pd.DataFrame(investment_data)

def create_pathway_analysis(all_results, baseline_total, target_years):
    """Create emission pathway analysis"""
    
    pathway_data = []
    cumulative_investment = 0
    
    for year in range(2023, 2051):
        if year in all_results:
            solution_df = all_results[year]
            abatement = solution_df['AbatementAchieved_ktCO2'].sum()
            annual_investment = solution_df['CAPEX_Million_USD'].sum()
            cumulative_investment += annual_investment
        else:
            abatement = 0
            annual_investment = 0
        
        remaining_emissions = baseline_total - abatement
        reduction_pct = (abatement / baseline_total) * 100 if baseline_total > 0 else 0
        
        pathway_data.append({
            'Year': year,
            'BaselineEmissions_ktCO2': baseline_total,
            'AbatementAchieved_ktCO2': abatement,
            'RemainingEmissions_ktCO2': remaining_emissions,
            'ReductionPercent': reduction_pct,
            'AnnualInvestment_Million_USD': annual_investment,
            'CumulativeInvestment_Million_USD': cumulative_investment
        })
    
    return pd.DataFrame(pathway_data)

def plot_comprehensive_analysis(pathway_df, investment_df, all_results, baseline_total):
    """Create comprehensive analysis plots"""
    
    fig = plt.figure(figsize=(20, 16))
    
    # Create grid layout
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Emission Pathway (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(pathway_df['Year'], pathway_df['BaselineEmissions_ktCO2']/1000, 
             'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
    ax1.plot(pathway_df['Year'], pathway_df['RemainingEmissions_ktCO2']/1000, 
             'b-', linewidth=3, label='With Optimization')
    ax1.fill_between(pathway_df['Year'], 
                     pathway_df['RemainingEmissions_ktCO2']/1000, 
                     pathway_df['BaselineEmissions_ktCO2']/1000, 
                     alpha=0.3, color='green', label='Emission Reduction')
    
    # Add Korean NDC targets
    baseline_mt = baseline_total / 1000
    targets = {2030: baseline_mt * 0.85, 2040: baseline_mt * 0.50, 2050: baseline_mt * 0.20}
    for year, target in targets.items():
        ax1.scatter(year, target, color='red', s=100, zorder=5)
        reduction_pct = int((baseline_mt - target) / baseline_mt * 100)
        ax1.annotate(f'{reduction_pct}%', (year, target), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2/year)')
    ax1.set_title('Korean Petrochemical Emission Pathway')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Investment Timeline (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(investment_df['Year'], investment_df['Total_CAPEX_Million_USD']/1000, 
            alpha=0.7, color='orange', label='CAPEX')
    ax2.plot(investment_df['Year'], investment_df['Total_Annual_Cost_Million_USD']/1000, 
             'ro-', linewidth=2, label='Annual OPEX')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Investment (Billion USD)')
    ax2.set_title('Investment Requirements by Year')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Technology Shares (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    if len(all_results) > 0:
        # Combine all solutions to see technology shares
        all_solutions = pd.concat(all_results.values(), ignore_index=True)
        tech_shares = all_solutions.groupby('TechnologyCategory')['AbatementAchieved_ktCO2'].sum()
        
        wedges, texts, autotexts = ax3.pie(tech_shares.values, labels=tech_shares.index, 
                                          autopct='%1.1f%%', startangle=90)
        ax3.set_title('Technology Share by Abatement')
    
    # 4. Regional Analysis (middle left)
    ax4 = fig.add_subplot(gs[1, 0])
    if len(all_results) > 0:
        all_solutions = pd.concat(all_results.values(), ignore_index=True)
        regional_data = all_solutions.groupby('Region').agg({
            'AbatementAchieved_ktCO2': 'sum',
            'CAPEX_Million_USD': 'sum'
        })
        
        x = np.arange(len(regional_data.index))
        width = 0.35
        
        ax4_twin = ax4.twinx()
        bars1 = ax4.bar(x - width/2, regional_data['AbatementAchieved_ktCO2']/1000, 
                       width, label='Abatement (MtCO2)', color='green', alpha=0.7)
        bars2 = ax4_twin.bar(x + width/2, regional_data['CAPEX_Million_USD']/1000, 
                            width, label='Investment (B USD)', color='orange', alpha=0.7)
        
        ax4.set_xlabel('Region')
        ax4.set_ylabel('Abatement (MtCO2/year)', color='green')
        ax4_twin.set_ylabel('Investment (Billion USD)', color='orange')
        ax4.set_title('Regional Distribution')
        ax4.set_xticks(x)
        ax4.set_xticklabels(regional_data.index)
        ax4.grid(True, alpha=0.3)
    
    # 5. Cost Evolution (middle middle)
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(investment_df['Year'], investment_df['Avg_LCOA_USD_per_tCO2'], 
             'bo-', linewidth=2, markersize=8)
    ax5.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='$100/tCO2 threshold')
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Average LCOA (USD/tCO2)')
    ax5.set_title('Cost Evolution Over Time')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. MACC Curve for latest year (middle right)
    ax6 = fig.add_subplot(gs[1, 2])
    if len(all_results) > 0:
        latest_year = max(all_results.keys())
        latest_solution = all_results[latest_year].sort_values('LCOA_USD_per_tCO2')
        
        cumulative_abatement = latest_solution['AbatementAchieved_ktCO2'].cumsum() / 1000
        costs = latest_solution['LCOA_USD_per_tCO2']
        
        ax6.step(cumulative_abatement, costs, where='post', linewidth=2, color='darkblue')
        ax6.fill_between(cumulative_abatement, 0, costs, step='post', alpha=0.3, color='lightblue')
        ax6.set_xlabel('Cumulative Abatement (MtCO2/year)')
        ax6.set_ylabel('LCOA (USD/tCO2)')
        ax6.set_title(f'MACC Curve {latest_year}')
        ax6.grid(True, alpha=0.3)
    
    # 7. Cumulative Investment (bottom left)
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(pathway_df['Year'], pathway_df['CumulativeInvestment_Million_USD']/1000, 
             'g-', linewidth=3, marker='o', markersize=4)
    ax7.set_xlabel('Year')
    ax7.set_ylabel('Cumulative Investment (Billion USD)')
    ax7.set_title('Cumulative Investment Over Time')
    ax7.grid(True, alpha=0.3)
    
    # 8. Company Analysis (bottom middle)
    ax8 = fig.add_subplot(gs[2, 1])
    if len(all_results) > 0:
        all_solutions = pd.concat(all_results.values(), ignore_index=True)
        company_data = all_solutions.groupby('Company').agg({
            'AbatementAchieved_ktCO2': 'sum',
            'CAPEX_Million_USD': 'sum'
        }).sort_values('AbatementAchieved_ktCO2', ascending=True)
        
        ax8.barh(range(len(company_data)), company_data['AbatementAchieved_ktCO2']/1000)
        ax8.set_yticks(range(len(company_data)))
        ax8.set_yticklabels(company_data.index, fontsize=8)
        ax8.set_xlabel('Abatement (MtCO2/year)')
        ax8.set_title('Company Participation')
        ax8.grid(True, alpha=0.3, axis='x')
    
    # 9. Summary Stats (bottom right)
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    
    # Create summary text
    if len(investment_df) > 0:
        total_investment = investment_df['Total_CAPEX_Million_USD'].sum() / 1000
        total_abatement = investment_df['Total_Abatement_ktCO2'].sum() / 1000
        avg_cost = investment_df['Avg_LCOA_USD_per_tCO2'].mean()
        
        summary_text = f"""
        📊 OPTIMIZATION SUMMARY
        
        Total Investment: ${total_investment:.1f}B
        
        Total Abatement: {total_abatement:.1f} MtCO2/year
        
        Average Cost: ${avg_cost:.0f}/tCO2
        
        Target Years: {', '.join(map(str, investment_df['Year'].tolist()))}
        
        Technologies: {len(set().union(*[df['TechnologyCategory'].unique() for df in all_results.values()])) if all_results else 0}
        
        Facilities: {len(set().union(*[df['FacilityID'].unique() for df in all_results.values()])) if all_results else 0}
        """
        
        ax9.text(0.1, 0.9, summary_text, transform=ax9.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.suptitle('Korean Petrochemical MACC - Enhanced Optimization Analysis', fontsize=16, y=0.98)
    return fig

def run_enhanced_optimization():
    """Run enhanced optimization with visualization and investment analysis"""
    
    print("KOREAN PETROCHEMICAL MACC - ENHANCED OPTIMIZATION")
    print("=" * 60)
    
    # Load data
    facilities_df, consumption_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, targets_df = load_facility_based_data()
    
    # Calculate baseline emissions
    baseline_emissions_df = calculate_facility_baseline_emissions(consumption_df, emission_factors_ts_df)
    total_baseline = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    print(f"\\nTotal baseline emissions: {total_baseline:.1f} ktCO2/year")
    
    # Test for each target year
    target_years = [2030, 2040, 2050]
    all_results = {}
    
    for target_year in target_years:
        print(f"\\n" + "="*60)
        print(f"OPTIMIZING FOR {target_year}")
        print("="*60)
        
        # Create viable options
        viable_df = create_simple_viable_options(
            facilities_df, consumption_df, technologies_df, costs_df,
            emission_factors_ts_df, fuel_costs_ts_df, target_year
        )
        
        if len(viable_df) > 0:
            # Solve optimization
            solution_df, status = solve_simple_optimization(
                viable_df, baseline_emissions_df, targets_df, target_year
            )
            
            if status == 'Optimal' and len(solution_df) > 0:
                all_results[target_year] = solution_df
                
                # Save results
                solution_df.to_csv(f'outputs/enhanced_optimization_{target_year}.csv', index=False)
                
                # Show top technologies
                print(f"\\nTop technologies deployed:")
                tech_summary = solution_df.groupby('TechnologyCategory').agg({
                    'AbatementAchieved_ktCO2': 'sum',
                    'AnnualCost_USD': 'sum'
                }).sort_values('AbatementAchieved_ktCO2', ascending=False)
                
                for tech_cat, row in tech_summary.head().iterrows():
                    lcoa = row['AnnualCost_USD'] / (row['AbatementAchieved_ktCO2'] * 1000)
                    print(f"  • {tech_cat}: {row['AbatementAchieved_ktCO2']:.1f} ktCO2/year (${lcoa:.0f}/tCO2)")
        else:
            print(f"❌ No viable options found for {target_year}")
    
    if all_results:
        print(f"\\n" + "="*60)
        print("ENHANCED ANALYSIS AND VISUALIZATION")
        print("="*60)
        
        # Create investment analysis
        investment_df = create_investment_analysis(all_results, target_years)
        
        # Create pathway analysis
        pathway_df = create_pathway_analysis(all_results, total_baseline, target_years)
        
        # Save analysis results
        investment_df.to_csv('outputs/investment_analysis.csv', index=False)
        pathway_df.to_csv('outputs/enhanced_pathway_analysis.csv', index=False)
        
        # Create comprehensive visualization
        fig = plot_comprehensive_analysis(pathway_df, investment_df, all_results, total_baseline)
        fig.savefig('outputs/enhanced_optimization_analysis.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # Summary results
        print(f"\\nResults Summary:")
        summary_data = []
        for year, solution_df in all_results.items():
            summary_data.append({
                'Year': year,
                'Total_Abatement_ktCO2': solution_df['AbatementAchieved_ktCO2'].sum(),
                'Total_Cost_Million_USD': solution_df['AnnualCost_USD'].sum() / 1e6,
                'Total_Investment_Million_USD': solution_df['CAPEX_Million_USD'].sum(),
                'Avg_LCOA_USD_per_tCO2': solution_df['AnnualCost_USD'].sum() / (solution_df['AbatementAchieved_ktCO2'].sum() * 1000),
                'Technologies_Deployed': len(solution_df),
                'Facilities_Involved': solution_df['FacilityID'].nunique(),
                'Companies_Involved': solution_df['Company'].nunique()
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False, float_format='%.1f'))
        
        # Save enhanced summary
        summary_df.to_csv('outputs/enhanced_optimization_summary.csv', index=False)
        
        print(f"\\n✅ Enhanced optimization completed successfully!")
        print(f"📊 Comprehensive analysis saved to outputs/enhanced_optimization_analysis.png")
        print(f"📈 Investment analysis saved to outputs/investment_analysis.csv")
        print(f"🔮 Pathway analysis saved to outputs/enhanced_pathway_analysis.csv")
        
    else:
        print(f"\\n❌ OPTIMIZATION FAILED FOR ALL YEARS")

if __name__ == "__main__":
    run_enhanced_optimization()