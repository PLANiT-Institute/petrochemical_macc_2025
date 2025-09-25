#!/usr/bin/env python3
"""
Create comprehensive cost-benefit analysis for government industrial support policies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set font for Korean text support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_government_cost_benefit_analysis():
    """Create comprehensive cost-benefit analysis for government policy support"""
    
    print("🏛️ CREATING GOVERNMENT COST-BENEFIT ANALYSIS")
    print("="*80)
    
    output_dir = Path("outputs")
    
    # Load all analysis results
    try:
        facility_transitions = pd.read_csv(output_dir / "detailed_facility_transitions.csv")
        company_stats = pd.read_csv(output_dir / "company_baseline_statistics.csv")
        enhanced_summary = pd.read_csv(output_dir / "enhanced_optimization_summary.csv")
        
        print("✓ All analysis results loaded")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load analysis results: {e}")
        return None
    
    # Define policy scenarios
    policy_scenarios = {
        'No Support': {
            'description': 'Market-driven transition only',
            'support_rate': 0.00,
            'implementation_delay': 5,  # years
            'success_probability': 0.60,
            'cost_premium': 1.50  # 50% higher costs without support
        },
        'Minimal Support': {
            'description': 'Tax incentives and regulatory streamlining',
            'support_rate': 0.10,
            'implementation_delay': 3,
            'success_probability': 0.75,
            'cost_premium': 1.25
        },
        'Moderate Support': {
            'description': 'Direct grants + tax incentives + technical assistance',
            'support_rate': 0.35,
            'implementation_delay': 1,
            'success_probability': 0.90,
            'cost_premium': 1.10
        },
        'Full Support': {
            'description': 'Comprehensive support package',
            'support_rate': 0.60,
            'implementation_delay': 0,
            'success_probability': 0.95,
            'cost_premium': 1.00
        }
    }
    
    # Economic parameters
    economic_params = {
        'discount_rate': 0.04,  # 4% real discount rate
        'carbon_price_2025': 50,   # USD per tCO2
        'carbon_price_2050': 150,  # USD per tCO2 (escalating)
        'gdp_growth_rate': 0.025,  # 2.5% annual GDP growth
        'employment_multiplier': 2.1,  # Economic multiplier for employment
        'tax_rate_corporate': 0.25,  # 25% corporate tax rate
        'vat_rate': 0.10,  # 10% VAT on investments
        'health_benefit_per_tco2': 25,  # USD health benefits per tCO2 avoided
        'innovation_spillover_rate': 0.15  # 15% innovation spillover benefits
    }
    
    # Calculate carbon price pathway (linear escalation)
    years = list(range(2025, 2051))
    carbon_prices = {}
    for year in years:
        progress = (year - 2025) / (2050 - 2025)
        carbon_prices[year] = (economic_params['carbon_price_2025'] + 
                              progress * (economic_params['carbon_price_2050'] - economic_params['carbon_price_2025']))
    
    # Scenario analysis
    scenario_results = []
    
    for scenario_name, scenario in policy_scenarios.items():
        print(f"\n📊 Analyzing {scenario_name} scenario...")
        
        # Calculate total investment required
        total_capex = facility_transitions['Total_CAPEX_USD'].sum()
        total_annual_cost = facility_transitions['Annual_Cost_USD'].sum()
        total_emission_reduction = facility_transitions['Emission_Reduction_kt'].sum()
        
        # Adjust for scenario parameters
        adjusted_capex = total_capex * scenario['cost_premium']
        adjusted_annual_cost = total_annual_cost * scenario['cost_premium']
        successful_reduction = total_emission_reduction * scenario['success_probability']
        
        # Government costs
        government_capex_support = adjusted_capex * scenario['support_rate']
        government_annual_support = adjusted_annual_cost * scenario['support_rate'] 
        
        # Implementation timeline adjustment
        implementation_start = 2025 + scenario['implementation_delay']
        
        # Calculate net present values
        npv_costs = 0
        npv_benefits = 0
        
        for year in years:
            if year >= implementation_start:
                years_from_start = year - implementation_start
                discount_factor = (1 + economic_params['discount_rate']) ** -(year - 2025)
                
                # Ramp up implementation (S-curve)
                if years_from_start <= 10:
                    implementation_progress = 1 / (1 + np.exp(-0.5 * (years_from_start - 5)))
                else:
                    implementation_progress = 1.0
                
                annual_reduction = successful_reduction * implementation_progress
                
                # Government costs
                annual_gov_cost = (government_capex_support / 10 +  # Spread CAPEX over 10 years
                                 government_annual_support * implementation_progress)
                
                # Benefits
                # 1. Carbon value
                carbon_benefit = annual_reduction * carbon_prices[year]
                
                # 2. Health benefits  
                health_benefit = annual_reduction * economic_params['health_benefit_per_tco2']
                
                # 3. Tax revenue from increased economic activity
                economic_activity = adjusted_capex * implementation_progress / 10
                tax_revenue = (economic_activity * economic_params['tax_rate_corporate'] +
                             economic_activity * economic_params['vat_rate'])
                
                # 4. Employment benefits (reduced unemployment costs)
                construction_jobs = facility_transitions['Construction_Jobs'].sum() * implementation_progress
                operational_jobs = facility_transitions['Operational_Jobs'].sum() * implementation_progress
                employment_benefit = (construction_jobs + operational_jobs) * 50000  # $50k per job in reduced social costs
                
                # 5. Innovation spillovers
                innovation_benefit = adjusted_capex * implementation_progress * economic_params['innovation_spillover_rate'] / 10
                
                total_annual_benefit = (carbon_benefit + health_benefit + tax_revenue + 
                                      employment_benefit + innovation_benefit)
                
                npv_costs += annual_gov_cost * discount_factor
                npv_benefits += total_annual_benefit * discount_factor
        
        # Calculate scenario metrics
        bcr = npv_benefits / npv_costs if npv_costs > 0 else 0
        net_benefit = npv_benefits - npv_costs
        cost_per_tco2_avoided = npv_costs / (successful_reduction * 25) if successful_reduction > 0 else 0  # 25-year program
        
        # Macroeconomic impact
        gdp_impact = adjusted_capex * 0.8  # 80% of investment contributes to GDP
        
        scenario_result = {
            'Scenario': scenario_name,
            'Description': scenario['description'],
            'Government_Support_Rate': scenario['support_rate'],
            'Total_Government_Cost_NPV_Billion_USD': npv_costs / 1e9,
            'Total_Benefits_NPV_Billion_USD': npv_benefits / 1e9,
            'Net_Benefit_NPV_Billion_USD': net_benefit / 1e9,
            'Benefit_Cost_Ratio': bcr,
            'Cost_per_tCO2_Avoided_USD': cost_per_tco2_avoided,
            'Implementation_Delay_Years': scenario['implementation_delay'],
            'Success_Probability': scenario['success_probability'],
            'Total_Emission_Reduction_Mt': successful_reduction / 1000,
            'GDP_Impact_Billion_USD': gdp_impact / 1e9,
            'Jobs_Created_Peak': (facility_transitions['Construction_Jobs'].sum() + 
                                facility_transitions['Operational_Jobs'].sum()) * scenario['success_probability'],
            'Carbon_Value_NPV_Billion_USD': sum([
                (successful_reduction * carbon_prices[year] * 
                 (1 + economic_params['discount_rate']) ** -(year - 2025)) / 1e9
                for year in years if year >= implementation_start
            ]),
            'Health_Benefits_NPV_Billion_USD': (successful_reduction * 25 * 
                                              economic_params['health_benefit_per_tco2'] / 1e9),
            'Tax_Revenue_NPV_Billion_USD': (adjusted_capex * 
                                          (economic_params['tax_rate_corporate'] + economic_params['vat_rate']) / 1e9)
        }
        scenario_results.append(scenario_result)
    
    scenario_df = pd.DataFrame(scenario_results)
    
    # Company-specific support analysis
    company_support_analysis = []
    
    for company in facility_transitions['Company'].unique():
        company_facilities = facility_transitions[facility_transitions['Company'] == company]
        
        total_investment = company_facilities['Total_CAPEX_USD'].sum()
        total_jobs = company_facilities['Construction_Jobs'].sum() + company_facilities['Operational_Jobs'].sum()
        total_reduction = company_facilities['Emission_Reduction_kt'].sum()
        facilities_count = len(company_facilities)
        
        # Determine optimal support tier
        if total_investment > 2e9:  # >$2B
            recommended_tier = 'Full Support'
            support_rate = 0.60
        elif total_investment > 500e6:  # >$500M
            recommended_tier = 'Moderate Support'
            support_rate = 0.35
        elif total_investment > 100e6:  # >$100M
            recommended_tier = 'Minimal Support'
            support_rate = 0.10
        else:
            recommended_tier = 'No Support'
            support_rate = 0.00
        
        government_support_cost = total_investment * support_rate
        
        # Calculate company-specific benefits
        carbon_value_25yr = total_reduction * np.mean(list(carbon_prices.values())) * 25
        health_benefits = total_reduction * economic_params['health_benefit_per_tco2'] * 25
        economic_impact = company_facilities['Local_Economic_Impact_USD'].sum()
        
        company_analysis = {
            'Company': company,
            'Facilities_Count': facilities_count,
            'Total_Investment_Billion_USD': total_investment / 1e9,
            'Recommended_Support_Tier': recommended_tier,
            'Government_Support_Cost_Million_USD': government_support_cost / 1e6,
            'Jobs_Created': total_jobs,
            'Emission_Reduction_Mt': total_reduction / 1000,
            'Carbon_Value_25yr_Million_USD': carbon_value_25yr / 1e6,
            'Health_Benefits_25yr_Million_USD': health_benefits / 1e6,
            'Local_Economic_Impact_Billion_USD': economic_impact / 1e9,
            'Support_Efficiency_USD_per_tCO2': government_support_cost / total_reduction if total_reduction > 0 else 0,
            'ROI_Ratio': (carbon_value_25yr + health_benefits) / government_support_cost if government_support_cost > 0 else 0
        }
        company_support_analysis.append(company_analysis)
    
    company_support_df = pd.DataFrame(company_support_analysis)
    company_support_df = company_support_df.sort_values('Total_Investment_Billion_USD', ascending=False)
    
    # Create comprehensive visualizations
    fig = plt.figure(figsize=(24, 20))
    gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
    
    # 1. Scenario comparison - Benefit-Cost Ratio
    ax1 = fig.add_subplot(gs[0, 0])
    
    colors = ['red', 'orange', 'green', 'blue']
    bars = ax1.bar(range(len(scenario_df)), scenario_df['Benefit_Cost_Ratio'], 
                  color=colors, alpha=0.8)
    ax1.set_title('Benefit-Cost Ratio by Policy Scenario', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Benefit-Cost Ratio')
    ax1.set_xticks(range(len(scenario_df)))
    ax1.set_xticklabels(scenario_df['Scenario'], rotation=45, ha='right')
    ax1.axhline(y=1.0, color='black', linestyle='--', alpha=0.7, label='Break-even')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend()
    
    # Add value labels
    for bar, value in zip(bars, scenario_df['Benefit_Cost_Ratio']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 2. Government costs vs benefits
    ax2 = fig.add_subplot(gs[0, 1])
    
    x = np.arange(len(scenario_df))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, scenario_df['Total_Government_Cost_NPV_Billion_USD'], width, 
                   label='Government Costs', color='red', alpha=0.8)
    bars2 = ax2.bar(x + width/2, scenario_df['Total_Benefits_NPV_Billion_USD'], width, 
                   label='Total Benefits', color='green', alpha=0.8)
    
    ax2.set_title('Government Costs vs Total Benefits (NPV)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Billion USD (NPV)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenario_df['Scenario'], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Emission reduction by scenario
    ax3 = fig.add_subplot(gs[0, 2])
    
    bars = ax3.bar(range(len(scenario_df)), scenario_df['Total_Emission_Reduction_Mt'], 
                  color='green', alpha=0.8)
    ax3.set_title('Total Emission Reduction by Scenario', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Emission Reduction (Mt CO₂)')
    ax3.set_xticks(range(len(scenario_df)))
    ax3.set_xticklabels(scenario_df['Scenario'], rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, scenario_df['Total_Emission_Reduction_Mt']):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 4. Company investment requirements
    ax4 = fig.add_subplot(gs[1, :])
    
    # Create stacked bar chart showing investment vs support
    company_investment = company_support_df['Total_Investment_Billion_USD']
    government_support = company_support_df['Government_Support_Cost_Million_USD'] / 1000  # Convert to billions
    
    bars1 = ax4.bar(range(len(company_support_df)), government_support, 
                   label='Government Support', color='blue', alpha=0.8)
    bars2 = ax4.bar(range(len(company_support_df)), company_investment - government_support, 
                   bottom=government_support, label='Company Investment', color='orange', alpha=0.8)
    
    ax4.set_title('Investment Requirements by Company (Government Support vs Company Investment)', 
                 fontsize=14, fontweight='bold')
    ax4.set_ylabel('Investment (Billion USD)')
    ax4.set_xlabel('Company')
    ax4.set_xticks(range(len(company_support_df)))
    ax4.set_xticklabels(company_support_df['Company'], rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add total investment labels
    for i, (total, support) in enumerate(zip(company_investment, government_support)):
        ax4.text(i, total + 0.1, f'${total:.1f}B', ha='center', va='bottom', 
                fontweight='bold', fontsize=9)
    
    # 5. ROI analysis by company
    ax5 = fig.add_subplot(gs[2, 0])
    
    roi_data = company_support_df.sort_values('ROI_Ratio', ascending=True)
    bars = ax5.barh(range(len(roi_data)), roi_data['ROI_Ratio'], 
                   color='teal', alpha=0.8)
    ax5.set_title('Return on Investment by Company', fontsize=14, fontweight='bold')
    ax5.set_xlabel('ROI Ratio (Benefits / Government Support)')
    ax5.set_yticks(range(len(roi_data)))
    ax5.set_yticklabels(roi_data['Company'], fontsize=10)
    ax5.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Break-even')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.legend()
    
    # 6. Jobs creation impact
    ax6 = fig.add_subplot(gs[2, 1])
    
    bars = ax6.bar(range(len(scenario_df)), scenario_df['Jobs_Created_Peak'], 
                  color='purple', alpha=0.8)
    ax6.set_title('Peak Employment Impact by Scenario', fontsize=14, fontweight='bold')
    ax6.set_ylabel('Jobs Created')
    ax6.set_xticks(range(len(scenario_df)))
    ax6.set_xticklabels(scenario_df['Scenario'], rotation=45, ha='right')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, scenario_df['Jobs_Created_Peak']):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 1000,
                f'{value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 7. Benefit breakdown for optimal scenario
    ax7 = fig.add_subplot(gs[2, 2])
    
    optimal_scenario = scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax()]
    
    benefit_categories = ['Carbon Value', 'Health Benefits', 'Tax Revenue']
    benefit_values = [
        optimal_scenario['Carbon_Value_NPV_Billion_USD'],
        optimal_scenario['Health_Benefits_NPV_Billion_USD'], 
        optimal_scenario['Tax_Revenue_NPV_Billion_USD']
    ]
    
    colors_pie = ['green', 'red', 'blue']
    wedges, texts, autotexts = ax7.pie(benefit_values, labels=benefit_categories, colors=colors_pie, 
                                      autopct='%1.1f%%', startangle=90)
    ax7.set_title(f'Benefit Breakdown\n({optimal_scenario["Scenario"]} Scenario)', 
                 fontsize=14, fontweight='bold')
    
    # 8. Implementation timeline and costs
    ax8 = fig.add_subplot(gs[3, :])
    
    # Create timeline analysis
    timeline_years = list(range(2025, 2041))  # Focus on first 15 years
    
    for i, (scenario_name, scenario) in enumerate(policy_scenarios.items()):
        annual_costs = []
        cumulative_benefits = []
        
        for year in timeline_years:
            implementation_start = 2025 + scenario['implementation_delay']
            
            if year >= implementation_start:
                years_from_start = year - implementation_start
                if years_from_start <= 10:
                    progress = 1 / (1 + np.exp(-0.5 * (years_from_start - 5)))
                else:
                    progress = 1.0
                
                annual_cost = (facility_transitions['Total_CAPEX_USD'].sum() * 
                             scenario['support_rate'] * progress / 10) / 1e9
                annual_benefit = (facility_transitions['Emission_Reduction_kt'].sum() * 
                                carbon_prices[year] * scenario['success_probability'] * progress) / 1e9
            else:
                annual_cost = 0
                annual_benefit = 0
            
            annual_costs.append(annual_cost)
            if len(cumulative_benefits) == 0:
                cumulative_benefits.append(annual_benefit)
            else:
                cumulative_benefits.append(cumulative_benefits[-1] + annual_benefit)
        
        line_styles = ['-', '--', '-.', ':']
        ax8.plot(timeline_years, cumulative_benefits, label=f'{scenario_name} (Benefits)', 
                linestyle=line_styles[i], linewidth=2, alpha=0.8)
    
    ax8.set_title('Cumulative Benefits Timeline by Policy Scenario', fontsize=14, fontweight='bold')
    ax8.set_xlabel('Year')
    ax8.set_ylabel('Cumulative Benefits (Billion USD)')
    ax8.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax8.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "government_cost_benefit_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed analysis files
    scenario_df.to_csv(output_dir / "policy_scenario_analysis.csv", index=False)
    company_support_df.to_csv(output_dir / "company_support_recommendations.csv", index=False)
    
    # Create policy recommendations
    optimal_scenario_name = scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Scenario']
    
    policy_recommendations = {
        'Recommended_Policy': optimal_scenario_name,
        'Recommended_BCR': scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Benefit_Cost_Ratio'],
        'Total_Government_Investment_Required_Billion_USD': scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Total_Government_Cost_NPV_Billion_USD'],
        'Expected_Net_Benefit_Billion_USD': scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Net_Benefit_NPV_Billion_USD'],
        'Implementation_Priority': 'Immediate start recommended based on economic analysis',
        'Key_Success_Factors': 'Strong government coordination, adequate funding, industry engagement',
        'Risk_Mitigation': 'Phased implementation with milestone-based funding releases'
    }
    
    pd.DataFrame([policy_recommendations]).to_csv(output_dir / "government_policy_recommendations.csv", index=False)
    
    print(f"\n🏛️ GOVERNMENT COST-BENEFIT ANALYSIS COMPLETE:")
    print(f"="*80)
    
    print(f"\n📊 POLICY SCENARIO COMPARISON:")
    for _, scenario in scenario_df.iterrows():
        print(f"  • {scenario['Scenario']}: BCR {scenario['Benefit_Cost_Ratio']:.1f}, "
              f"Net Benefit ${scenario['Net_Benefit_NPV_Billion_USD']:.1f}B")
    
    print(f"\n💰 OPTIMAL POLICY RECOMMENDATION:")
    print(f"  • Recommended: {optimal_scenario_name}")
    print(f"  • Benefit-Cost Ratio: {scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Benefit_Cost_Ratio']:.1f}")
    print(f"  • Government Investment: ${scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Total_Government_Cost_NPV_Billion_USD']:.1f}B")
    print(f"  • Net Economic Benefit: ${scenario_df.loc[scenario_df['Benefit_Cost_Ratio'].idxmax(), 'Net_Benefit_NPV_Billion_USD']:.1f}B")
    
    print(f"\n🏭 COMPANY SUPPORT PRIORITIES:")
    for _, company in company_support_df.head(5).iterrows():
        print(f"  • {company['Company']}: {company['Recommended_Support_Tier']} "
              f"(${company['Government_Support_Cost_Million_USD']:.0f}M, ROI: {company['ROI_Ratio']:.1f})")
    
    print(f"\n📋 FILES GENERATED:")
    print(f"  📊 government_cost_benefit_analysis.png")
    print(f"  📄 policy_scenario_analysis.csv")
    print(f"  📄 company_support_recommendations.csv")
    print(f"  📄 government_policy_recommendations.csv")
    
    return scenario_df, company_support_df, policy_recommendations

if __name__ == "__main__":
    scenarios, company_support, recommendations = create_government_cost_benefit_analysis()