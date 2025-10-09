#!/usr/bin/env python3
"""
Create detailed company-level transition analysis for government industrial support policy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set font for Korean text support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_company_transition_analysis():
    """Create comprehensive company and facility-level transition analysis"""
    
    print("🏭 CREATING COMPANY TRANSITION ANALYSIS FOR GOVERNMENT REPORT")
    print("="*80)
    
    output_dir = Path("outputs")
    
    # Load facility data and optimization results
    try:
        facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        enhanced_deployments = pd.read_csv(output_dir / "enhanced_optimization_deployments.csv")
        enhanced_pathway = pd.read_csv(output_dir / "enhanced_optimization_achievement.csv")
        
        print("✓ Facility data and optimization results loaded")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load data: {e}")
        return None
    
    # Create company mapping and analysis
    facility_data['company'] = facility_data['facility_id'].str.extract(r'([A-Z]+)_')
    facility_data['company'] = facility_data['company'].fillna('OTHER')
    
    # Map facility IDs to companies for better analysis
    company_mapping = {
        'LG': 'LG Chem',
        'SK': 'SK Chemicals', 
        'HD': 'HD Hyundai Chemical',
        'LC': 'Lotte Chemical',
        'HAN': 'Hanwha Solutions',
        'KUM': 'Kumho Petrochemical',
        'OCI': 'OCI Company',
        'OTHER': 'Other Companies'
    }
    
    facility_data['company_name'] = facility_data['company'].map(company_mapping).fillna('Other Companies')
    
    # Calculate company-level baseline emissions
    company_baseline = facility_data.groupby(['company_name', 'process']).agg({
        'annual_emissions_kt_co2': 'sum',
        'capacity_kt': 'sum',
        'facility_id': 'count'
    }).reset_index()
    company_baseline.columns = ['Company', 'Process', 'Baseline_Emissions_kt', 'Total_Capacity_kt', 'Facility_Count']
    
    print(f"✓ Identified {len(company_baseline['Company'].unique())} companies")
    print(f"✓ Covering {company_baseline['Facility_Count'].sum()} facilities")
    
    # Create emission reduction pathway by company
    years = [2025, 2030, 2035, 2040, 2045, 2050]
    reduction_factors = {}
    
    for year in years:
        bau_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['BAU_Emissions'].iloc[0]
        optimized_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['Optimized_Emissions'].iloc[0]
        reduction_factors[year] = optimized_emissions / bau_emissions
    
    # Calculate company emission pathways
    company_pathways = []
    
    for company in company_baseline['Company'].unique():
        company_data = company_baseline[company_baseline['Company'] == company]
        baseline_total = company_data['Baseline_Emissions_kt'].sum()
        
        for year in years:
            pathway_record = {
                'Company': company,
                'Year': year,
                'Baseline_Emissions_kt': baseline_total,
                'Target_Emissions_kt': baseline_total * reduction_factors[year],
                'Reduction_Required_kt': baseline_total * (1 - reduction_factors[year]),
                'Reduction_Percent': (1 - reduction_factors[year]) * 100
            }
            company_pathways.append(pathway_record)
    
    company_pathway_df = pd.DataFrame(company_pathways)
    
    # Technology deployment by company and process
    technology_deployment = []
    
    # Map technologies to applicable processes
    tech_process_mapping = {
        'EE_NCC': ['Naphtha Cracker'],
        'EE_BTX': ['BTX Plant'], 
        'EE_UTL': ['Utility'],
        'RE_001': ['All'],  # Solar thermal applicable to all
        'RE_002': ['All'],  # Solar PV applicable to all
        'RE_003': ['All'],  # Wind PPA applicable to all
        'HP_001': ['All'],  # Heat pumps applicable to all
        'HP_002': ['All'],
        'ES_001': ['All']   # Energy storage applicable to all
    }
    
    # Calculate technology investment by company
    for _, deployment in enhanced_deployments.iterrows():
        tech_id = deployment['TechID']
        year = deployment['Year']
        deployment_level = deployment['DeploymentLevel']
        annual_cost = deployment['AnnualCostUSD']
        abatement = deployment['AbatementMtCO2']
        
        # Determine applicable processes
        applicable_processes = tech_process_mapping.get(tech_id, ['All'])
        
        for company in company_baseline['Company'].unique():
            company_data = company_baseline[company_baseline['Company'] == company]
            
            # Calculate company share of applicable processes
            if 'All' in applicable_processes:
                company_share = company_data['Baseline_Emissions_kt'].sum() / facility_data['annual_emissions_kt_co2'].sum()
            else:
                applicable_emissions = company_data[company_data['Process'].isin(applicable_processes)]['Baseline_Emissions_kt'].sum()
                total_applicable = company_baseline[company_baseline['Process'].isin(applicable_processes)]['Baseline_Emissions_kt'].sum()
                company_share = applicable_emissions / total_applicable if total_applicable > 0 else 0
            
            if company_share > 0:
                tech_deployment = {
                    'Company': company,
                    'TechID': tech_id,
                    'Year': year,
                    'DeploymentLevel': deployment_level,
                    'Company_Share': company_share,
                    'Annual_Cost_USD': annual_cost * company_share,
                    'Abatement_kt_CO2': abatement * 1000 * company_share,
                    'Applicable_Processes': ', '.join(applicable_processes) if applicable_processes != ['All'] else 'All Processes'
                }
                technology_deployment.append(tech_deployment)
    
    tech_deployment_df = pd.DataFrame(technology_deployment)
    
    # Calculate facility-level transitions
    facility_transitions = []
    
    for _, facility in facility_data.iterrows():
        facility_id = facility['facility_id']
        company = facility['company_name']
        process = facility['process']
        baseline_emissions = facility['annual_emissions_kt_co2']
        capacity = facility['capacity_kt']
        
        # Determine applicable technologies for this facility
        applicable_techs = []
        
        # Process-specific EE
        if process == 'Naphtha Cracker':
            applicable_techs.append(('EE_NCC', 0.10, 'Energy Efficiency - NCC'))
        elif process == 'BTX Plant':
            applicable_techs.append(('EE_BTX', 0.20, 'Energy Efficiency - BTX'))
        elif process == 'Utility':
            applicable_techs.append(('EE_UTL', 0.35, 'Energy Efficiency - Utility'))
        
        # Universal technologies
        universal_techs = [
            ('RE_002', 0.40, 'Solar PV Systems'),
            ('RE_003', 0.60, 'Wind Power PPAs'),
            ('HP_001', 0.50, 'Heat Pumps (Low-Med Temp)'),
            ('RE_001', 0.25, 'Solar Thermal'),
            ('HP_002', 0.30, 'Heat Pumps (High Temp)'),
            ('ES_001', 0.20, 'Battery Storage')
        ]
        applicable_techs.extend(universal_techs)
        
        # Calculate emission reduction potential
        total_reduction_potential = 0
        technologies_applied = []
        
        for tech_id, max_penetration, tech_name in applicable_techs:
            # Get deployment level from optimization results
            tech_deployments = tech_deployment_df[
                (tech_deployment_df['TechID'] == tech_id) & 
                (tech_deployment_df['Company'] == company)
            ]
            
            if not tech_deployments.empty:
                avg_deployment = tech_deployments['DeploymentLevel'].mean()
                reduction_factor = min(avg_deployment, max_penetration)
                
                # Estimate emission reduction (simplified calculation)
                if tech_id.startswith('EE_'):
                    emission_reduction = baseline_emissions * reduction_factor
                elif tech_id.startswith('RE_'):
                    # Renewable energy reduces grid emissions
                    emission_reduction = baseline_emissions * reduction_factor * 0.5  # Partial substitution
                elif tech_id.startswith('HP_'):
                    # Heat pumps reduce fuel consumption
                    emission_reduction = baseline_emissions * reduction_factor * 0.3
                elif tech_id.startswith('ES_'):
                    # Energy storage enables renewable integration
                    emission_reduction = baseline_emissions * reduction_factor * 0.1
                else:
                    emission_reduction = 0
                
                if reduction_factor > 0.01:  # Only include significant deployments
                    technologies_applied.append({
                        'TechID': tech_id,
                        'TechName': tech_name,
                        'DeploymentLevel': reduction_factor,
                        'EmissionReduction_kt': emission_reduction
                    })
                    total_reduction_potential += emission_reduction
        
        # Cap total reduction at reasonable limits
        total_reduction_potential = min(total_reduction_potential, baseline_emissions * 0.90)
        
        facility_transition = {
            'FacilityID': facility_id,
            'Company': company,
            'Process': process,
            'Capacity_kt': capacity,
            'Baseline_Emissions_kt': baseline_emissions,
            'Total_Reduction_Potential_kt': total_reduction_potential,
            'Final_Emissions_kt': baseline_emissions - total_reduction_potential,
            'Reduction_Percent': (total_reduction_potential / baseline_emissions * 100) if baseline_emissions > 0 else 0,
            'Technologies_Count': len(technologies_applied),
            'Technologies_Applied': '; '.join([f"{t['TechName']} ({t['DeploymentLevel']:.1%})" for t in technologies_applied[:3]])  # Top 3
        }
        facility_transitions.append(facility_transition)
    
    facility_transition_df = pd.DataFrame(facility_transitions)
    
    # Create comprehensive visualizations
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(20, 18))
    
    # 1. Company emission pathways
    for company in company_pathway_df['Company'].unique():
        company_data = company_pathway_df[company_pathway_df['Company'] == company]
        ax1.plot(company_data['Year'], company_data['Target_Emissions_kt'], 
                marker='o', linewidth=2, label=company, markersize=6)
    
    ax1.set_title('Company Emission Pathways (2025-2050)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (kt CO₂)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. Company baseline emissions comparison
    company_totals = company_baseline.groupby('Company')['Baseline_Emissions_kt'].sum().sort_values(ascending=True)
    
    bars = ax2.barh(range(len(company_totals)), company_totals.values, color='skyblue', alpha=0.8)
    ax2.set_title('Company Baseline Emissions', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Baseline Emissions (kt CO₂)')
    ax2.set_yticks(range(len(company_totals)))
    ax2.set_yticklabels(company_totals.index, fontsize=10)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, value in zip(bars, company_totals.values):
        ax2.text(value + 50, bar.get_y() + bar.get_height()/2,
                f'{value:.0f}', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 3. Technology investment by company
    tech_investment = tech_deployment_df.groupby('Company')['Annual_Cost_USD'].sum().sort_values(ascending=True)
    
    bars = ax3.barh(range(len(tech_investment)), tech_investment.values / 1e6, color='lightgreen', alpha=0.8)
    ax3.set_title('Annual Technology Investment by Company', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Annual Investment (Million USD)')
    ax3.set_yticks(range(len(tech_investment)))
    ax3.set_yticklabels(tech_investment.index, fontsize=10)
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, value in zip(bars, tech_investment.values):
        ax3.text(value/1e6 + 1, bar.get_y() + bar.get_height()/2,
                f'${value/1e6:.1f}M', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 4. Facility transition distribution
    transition_bins = [0, 20, 40, 60, 80, 100]
    transition_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    facility_transition_df['Reduction_Category'] = pd.cut(facility_transition_df['Reduction_Percent'], 
                                                         bins=transition_bins, labels=transition_labels)
    
    transition_counts = facility_transition_df['Reduction_Category'].value_counts()
    
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    bars = ax4.bar(range(len(transition_counts)), transition_counts.values, 
                  color=colors[:len(transition_counts)], alpha=0.8)
    
    ax4.set_title('Facility Emission Reduction Distribution', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Emission Reduction Range')
    ax4.set_ylabel('Number of Facilities')
    ax4.set_xticks(range(len(transition_counts)))
    ax4.set_xticklabels(transition_counts.index, rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, transition_counts.values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 5. Process-specific transition impact
    process_transition = facility_transition_df.groupby('Process').agg({
        'Baseline_Emissions_kt': 'sum',
        'Total_Reduction_Potential_kt': 'sum',
        'FacilityID': 'count'
    }).reset_index()
    process_transition['Reduction_Percent'] = (process_transition['Total_Reduction_Potential_kt'] / 
                                              process_transition['Baseline_Emissions_kt'] * 100)
    
    x = np.arange(len(process_transition))
    width = 0.35
    
    bars1 = ax5.bar(x - width/2, process_transition['Baseline_Emissions_kt'], width, 
                   label='Baseline Emissions', color='red', alpha=0.7)
    bars2 = ax5.bar(x + width/2, process_transition['Total_Reduction_Potential_kt'], width, 
                   label='Reduction Potential', color='green', alpha=0.7)
    
    ax5.set_title('Process-Specific Emission Reduction Impact', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Process Type')
    ax5.set_ylabel('Emissions (kt CO₂)')
    ax5.set_xticks(x)
    ax5.set_xticklabels(process_transition['Process'], rotation=45, ha='right')
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Technology deployment heatmap by company
    tech_company_matrix = tech_deployment_df.pivot_table(
        index='TechID', columns='Company', values='DeploymentLevel', aggfunc='mean'
    ).fillna(0)
    
    # Filter to show only most significant technologies
    tech_totals = tech_company_matrix.sum(axis=1).sort_values(ascending=False)
    top_techs = tech_totals.head(8).index
    
    sns.heatmap(tech_company_matrix.loc[top_techs], annot=True, fmt='.2f', cmap='Blues', 
               ax=ax6, cbar_kws={'label': 'Deployment Level'})
    ax6.set_title('Technology Deployment by Company', fontsize=14, fontweight='bold')
    ax6.set_xlabel('Company')
    ax6.set_ylabel('Technology')
    
    plt.tight_layout()
    plt.savefig(output_dir / "company_transition_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed data files
    company_pathway_df.to_csv(output_dir / "company_emission_pathways.csv", index=False)
    tech_deployment_df.to_csv(output_dir / "company_technology_deployment.csv", index=False)
    facility_transition_df.to_csv(output_dir / "facility_transition_analysis.csv", index=False)
    
    # Create government policy analysis
    policy_analysis = create_policy_support_analysis(company_pathway_df, tech_deployment_df, facility_transition_df)
    
    print(f"\n🏭 COMPANY TRANSITION ANALYSIS COMPLETE:")
    print(f"="*80)
    
    print(f"\n📊 COMPANY COVERAGE:")
    for company in company_baseline['Company'].unique():
        company_data = company_baseline[company_baseline['Company'] == company]
        total_emissions = company_data['Baseline_Emissions_kt'].sum()
        facility_count = company_data['Facility_Count'].sum()
        print(f"  • {company}: {total_emissions:,.0f} kt CO₂, {facility_count} facilities")
    
    print(f"\n🎯 TRANSITION IMPACT BY PROCESS:")
    for _, process in process_transition.iterrows():
        print(f"  • {process['Process']}: {process['Reduction_Percent']:.1f}% reduction")
        print(f"    - Baseline: {process['Baseline_Emissions_kt']:,.0f} kt CO₂")
        print(f"    - Reduction: {process['Total_Reduction_Potential_kt']:,.0f} kt CO₂")
        print(f"    - Facilities: {process['FacilityID']} facilities affected")
    
    print(f"\n💰 INVESTMENT REQUIREMENTS:")
    total_investment = tech_deployment_df['Annual_Cost_USD'].sum() / 1e9
    companies_with_investment = len(tech_investment[tech_investment > 0])
    print(f"  • Total Annual Investment: ${total_investment:.2f} billion USD")
    print(f"  • Companies Requiring Investment: {companies_with_investment}")
    print(f"  • Average per Company: ${total_investment/companies_with_investment:.2f} billion USD")
    
    print(f"\n📋 FILES GENERATED:")
    print(f"  📊 company_transition_analysis.png")
    print(f"  📄 company_emission_pathways.csv")
    print(f"  📄 company_technology_deployment.csv")
    print(f"  📄 facility_transition_analysis.csv")
    print(f"  📄 government_policy_support_analysis.csv")
    
    return company_pathway_df, tech_deployment_df, facility_transition_df, policy_analysis

def create_policy_support_analysis(company_pathways, tech_deployments, facility_transitions):
    """Create detailed policy support analysis for government"""
    
    print(f"\n🏛️ CREATING GOVERNMENT POLICY SUPPORT ANALYSIS")
    
    # Calculate support requirements by company
    company_support = []
    
    for company in company_pathways['Company'].unique():
        company_pathway = company_pathways[company_pathways['Company'] == company]
        company_tech = tech_deployments[tech_deployments['Company'] == company]
        company_facilities = facility_transitions[facility_transitions['Company'] == company]
        
        # Financial metrics
        total_investment = company_tech['Annual_Cost_USD'].sum()
        total_abatement = company_tech['Abatement_kt_CO2'].sum()
        
        # Facility impact
        facilities_affected = len(company_facilities[company_facilities['Technologies_Count'] > 0])
        total_facilities = len(company_facilities)
        
        # Baseline emissions
        baseline_2025 = company_pathway[company_pathway['Year'] == 2025]['Baseline_Emissions_kt'].iloc[0]
        target_2050 = company_pathway[company_pathway['Year'] == 2050]['Target_Emissions_kt'].iloc[0]
        
        # Support categorization
        if total_investment > 500e6:  # >$500M
            support_tier = 'Tier 1 - Major Support Required'
        elif total_investment > 100e6:  # >$100M
            support_tier = 'Tier 2 - Moderate Support Required'
        elif total_investment > 10e6:   # >$10M
            support_tier = 'Tier 3 - Limited Support Required'
        else:
            support_tier = 'Tier 4 - Minimal Support'
        
        # Technology diversity
        tech_diversity = len(company_tech['TechID'].unique())
        
        # Risk assessment
        high_risk_techs = company_tech[company_tech['TechID'].isin(['HP_002', 'ES_001', 'RE_001'])]
        risk_investment = high_risk_techs['Annual_Cost_USD'].sum()
        risk_score = 'High' if risk_investment > 50e6 else 'Medium' if risk_investment > 10e6 else 'Low'
        
        support_record = {
            'Company': company,
            'Support_Tier': support_tier,
            'Total_Annual_Investment_USD': total_investment,
            'Investment_per_Facility_USD': total_investment / total_facilities if total_facilities > 0 else 0,
            'Facilities_Affected': facilities_affected,
            'Total_Facilities': total_facilities,
            'Facility_Impact_Percent': (facilities_affected / total_facilities * 100) if total_facilities > 0 else 0,
            'Baseline_Emissions_2025_kt': baseline_2025,
            'Target_Emissions_2050_kt': target_2050,
            'Emission_Reduction_Required_kt': baseline_2025 - target_2050,
            'Technology_Diversity_Score': tech_diversity,
            'Risk_Assessment': risk_score,
            'High_Risk_Investment_USD': risk_investment,
            'Cost_Effectiveness_USD_per_tCO2': total_investment / (total_abatement) if total_abatement > 0 else 0
        }
        company_support.append(support_record)
    
    policy_support_df = pd.DataFrame(company_support)
    
    # Policy recommendations by tier
    policy_recommendations = {
        'Tier 1 - Major Support Required': {
            'Financial_Support': 'Direct grants up to 50% of investment + low-interest loans',
            'Technical_Support': 'Dedicated government technical assistance team',
            'Regulatory_Support': 'Fast-track permitting and regulatory streamlining',
            'Timeline': 'Immediate engagement with 2-year implementation support',
            'Monitoring': 'Quarterly progress reviews and milestone-based funding'
        },
        'Tier 2 - Moderate Support Required': {
            'Financial_Support': 'Grants up to 30% of investment + tax incentives',
            'Technical_Support': 'Access to government R&D facilities and expertise',
            'Regulatory_Support': 'Expedited permitting process',
            'Timeline': '6-month planning period with annual reviews',
            'Monitoring': 'Semi-annual progress assessments'
        },
        'Tier 3 - Limited Support Required': {
            'Financial_Support': 'Tax credits and accelerated depreciation',
            'Technical_Support': 'Information sharing and best practice guidance',
            'Regulatory_Support': 'Standard regulatory pathway with guidance',
            'Timeline': 'Self-directed with government consultation available',
            'Monitoring': 'Annual compliance reporting'
        },
        'Tier 4 - Minimal Support': {
            'Financial_Support': 'Standard tax incentives only',
            'Technical_Support': 'Industry association resources',
            'Regulatory_Support': 'Standard compliance requirements',
            'Timeline': 'Market-driven implementation',
            'Monitoring': 'Standard environmental reporting'
        }
    }
    
    # Create detailed government briefing
    total_government_investment = policy_support_df['Total_Annual_Investment_USD'].sum()
    
    # Estimate government support costs
    policy_support_df['Estimated_Government_Support_USD'] = 0
    
    for idx, row in policy_support_df.iterrows():
        tier = row['Support_Tier']
        investment = row['Total_Annual_Investment_USD']
        
        if 'Tier 1' in tier:
            support_amount = investment * 0.50  # 50% support
        elif 'Tier 2' in tier:
            support_amount = investment * 0.30  # 30% support
        elif 'Tier 3' in tier:
            support_amount = investment * 0.15  # 15% support (tax credits)
        else:
            support_amount = investment * 0.05  # 5% support (standard incentives)
        
        policy_support_df.at[idx, 'Estimated_Government_Support_USD'] = support_amount
    
    # Save policy analysis
    output_dir = Path("outputs")
    policy_support_df.to_csv(output_dir / "government_policy_support_analysis.csv", index=False)
    
    # Create policy summary
    tier_summary = policy_support_df.groupby('Support_Tier').agg({
        'Company': 'count',
        'Total_Annual_Investment_USD': 'sum',
        'Estimated_Government_Support_USD': 'sum',
        'Facilities_Affected': 'sum',
        'Emission_Reduction_Required_kt': 'sum'
    }).reset_index()
    
    tier_summary['Support_Efficiency_USD_per_tCO2'] = (tier_summary['Estimated_Government_Support_USD'] / 
                                                      tier_summary['Emission_Reduction_Required_kt'])
    
    tier_summary.to_csv(output_dir / "government_support_tier_summary.csv", index=False)
    
    print(f"✓ Policy support analysis complete")
    print(f"  • Total government support estimated: ${policy_support_df['Estimated_Government_Support_USD'].sum()/1e9:.2f}B USD")
    print(f"  • Companies requiring Tier 1 support: {len(policy_support_df[policy_support_df['Support_Tier'].str.contains('Tier 1')])}")
    
    return policy_support_df

if __name__ == "__main__":
    pathways, deployments, transitions, policy = create_company_transition_analysis()