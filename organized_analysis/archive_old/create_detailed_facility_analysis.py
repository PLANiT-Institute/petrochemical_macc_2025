#!/usr/bin/env python3
"""
Create detailed facility-level transition analysis with enhanced company mapping
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set font for Korean text support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_detailed_facility_analysis():
    """Create comprehensive facility-level analysis with realistic company mapping"""
    
    print("🏭 CREATING DETAILED FACILITY-LEVEL TRANSITION ANALYSIS")
    print("="*80)
    
    output_dir = Path("outputs")
    
    # Load facility data
    try:
        facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        enhanced_deployments = pd.read_csv(output_dir / "enhanced_optimization_deployments.csv")
        enhanced_pathway = pd.read_csv(output_dir / "enhanced_optimization_achievement.csv")
        
        print("✓ Facility data and optimization results loaded")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load data: {e}")
        return None
    
    # Enhanced company mapping based on Korean petrochemical industry
    # Assign companies based on facility characteristics and regional distribution
    np.random.seed(42)  # For consistent results
    
    # Major Korean petrochemical companies and their typical characteristics
    major_companies = {
        'LG Chem': {'weight': 0.25, 'processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'], 'regions': ['Daesan', 'Ulsan']},
        'Lotte Chemical': {'weight': 0.20, 'processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'], 'regions': ['Daesan', 'Ulsan']},
        'SK Chemicals': {'weight': 0.18, 'processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'], 'regions': ['Ulsan', 'Incheon']},
        'Hanwha Solutions': {'weight': 0.12, 'processes': ['BTX Plant', 'Utility'], 'regions': ['Daesan', 'Ulsan']},
        'HD Hyundai Chemical': {'weight': 0.10, 'processes': ['BTX Plant', 'Utility'], 'regions': ['Ulsan', 'Daesan']},
        'Kumho Petrochemical': {'weight': 0.08, 'processes': ['BTX Plant', 'Utility'], 'regions': ['Ulsan', 'Yeosu']},
        'OCI Company': {'weight': 0.04, 'processes': ['Utility'], 'regions': ['Gunsan', 'Pohang']},
        'Other Companies': {'weight': 0.03, 'processes': ['Utility'], 'regions': ['Various']}
    }
    
    # Assign companies to facilities based on process type and capacity
    facility_assignments = []
    
    for _, facility in facility_data.iterrows():
        process = facility['process']
        capacity = facility['capacity_kt']
        emissions = facility['annual_emissions_kt_co2']
        
        # Weight companies based on process fit and size
        company_scores = {}
        
        for company, info in major_companies.items():
            # Base score from company weight
            score = info['weight']
            
            # Bonus for process compatibility
            if process in info['processes']:
                score *= 3.0
            
            # Larger companies more likely to have larger facilities
            if company in ['LG Chem', 'Lotte Chemical', 'SK Chemicals']:
                if capacity > 500:  # Large facilities
                    score *= 2.0
                elif capacity < 100:  # Small facilities
                    score *= 0.5
            
            # Smaller companies more likely to have smaller facilities
            if company in ['OCI Company', 'Other Companies']:
                if capacity < 200:
                    score *= 2.0
                elif capacity > 1000:
                    score *= 0.3
            
            company_scores[company] = score
        
        # Normalize scores and make random selection
        total_score = sum(company_scores.values())
        probabilities = [score/total_score for score in company_scores.values()]
        selected_company = np.random.choice(list(company_scores.keys()), p=probabilities)
        
        facility_assignments.append({
            'facility_id': facility['facility_id'],
            'company': selected_company,
            'process': process,
            'capacity_kt': capacity,
            'emissions_kt': emissions,
            'emission_intensity': facility['emission_intensity_t_co2_per_t']
        })
    
    facility_company_df = pd.DataFrame(facility_assignments)
    
    # Calculate company-level statistics
    company_stats = facility_company_df.groupby('company').agg({
        'facility_id': 'count',
        'capacity_kt': 'sum',
        'emissions_kt': 'sum',
        'emission_intensity': 'mean'
    }).reset_index()
    company_stats.columns = ['Company', 'Facilities', 'Total_Capacity_kt', 'Total_Emissions_kt', 'Avg_Intensity']
    company_stats = company_stats.sort_values('Total_Emissions_kt', ascending=False)
    
    print(f"✓ Enhanced company mapping complete:")
    for _, company in company_stats.iterrows():
        print(f"  • {company['Company']}: {company['Facilities']} facilities, {company['Total_Emissions_kt']:,.0f} kt CO₂")
    
    # Create detailed facility transition analysis
    facility_transitions = []
    
    # Technology cost and abatement factors
    tech_parameters = {
        'EE_NCC': {'cost_per_kt': 50000, 'max_reduction': 0.10, 'capex_factor': 2.0},
        'EE_BTX': {'cost_per_kt': 40000, 'max_reduction': 0.20, 'capex_factor': 1.8},
        'EE_UTL': {'cost_per_kt': 30000, 'max_reduction': 0.35, 'capex_factor': 1.5},
        'RE_001': {'cost_per_kt': 80000, 'max_reduction': 0.15, 'capex_factor': 5.0},  # Solar thermal
        'RE_002': {'cost_per_kt': 45000, 'max_reduction': 0.25, 'capex_factor': 4.0},  # Solar PV
        'RE_003': {'cost_per_kt': 35000, 'max_reduction': 0.30, 'capex_factor': 0.5},  # Wind PPA
        'HP_001': {'cost_per_kt': 60000, 'max_reduction': 0.20, 'capex_factor': 3.0},  # Heat pumps
        'HP_002': {'cost_per_kt': 120000, 'max_reduction': 0.15, 'capex_factor': 4.0}, # High-temp HP
        'ES_001': {'cost_per_kt': 100000, 'max_reduction': 0.08, 'capex_factor': 6.0}  # Battery storage
    }
    
    # Get deployment levels from optimization
    deployment_by_tech = enhanced_deployments.groupby('TechID')['DeploymentLevel'].mean().to_dict()
    
    for _, facility in facility_company_df.iterrows():
        facility_id = facility['facility_id']
        company = facility['company']
        process = facility['process']
        capacity = facility['capacity_kt']
        baseline_emissions = facility['emissions_kt']
        
        # Determine applicable technologies
        applicable_techs = []
        
        # Process-specific EE
        if process == 'Naphtha Cracker':
            if 'EE_NCC' in deployment_by_tech:
                applicable_techs.append('EE_NCC')
        elif process == 'BTX Plant':
            if 'EE_BTX' in deployment_by_tech:
                applicable_techs.append('EE_BTX')
        elif process == 'Utility':
            if 'EE_UTL' in deployment_by_tech:
                applicable_techs.append('EE_UTL')
        
        # Universal technologies (applicable to all)
        universal_techs = ['RE_002', 'RE_003', 'HP_001']  # Most widely applicable
        
        # Advanced technologies for larger facilities
        if capacity > 300:  # Larger facilities
            universal_techs.extend(['RE_001', 'HP_002', 'ES_001'])
        
        applicable_techs.extend(universal_techs)
        
        # Calculate facility-specific deployment and costs
        total_emission_reduction = 0
        total_annual_cost = 0
        total_capex = 0
        technologies_deployed = []
        
        for tech_id in applicable_techs:
            if tech_id in tech_parameters and tech_id in deployment_by_tech:
                params = tech_parameters[tech_id]
                deployment_level = deployment_by_tech[tech_id]
                
                # Apply deployment level and facility-specific factors
                effective_deployment = min(deployment_level, params['max_reduction'])
                
                # Scale by facility size (larger facilities can achieve better deployment)
                if capacity > 500:
                    size_factor = 1.1
                elif capacity < 100:
                    size_factor = 0.8
                else:
                    size_factor = 1.0
                
                effective_deployment *= size_factor
                effective_deployment = min(effective_deployment, params['max_reduction'])
                
                if effective_deployment > 0.01:  # Only include meaningful deployments
                    # Calculate emission reduction
                    emission_reduction = baseline_emissions * effective_deployment
                    
                    # Calculate costs
                    annual_cost = emission_reduction * params['cost_per_kt']
                    capex = annual_cost * params['capex_factor']
                    
                    technologies_deployed.append({
                        'TechID': tech_id,
                        'DeploymentLevel': effective_deployment,
                        'EmissionReduction_kt': emission_reduction,
                        'AnnualCost_USD': annual_cost,
                        'CAPEX_USD': capex
                    })
                    
                    total_emission_reduction += emission_reduction
                    total_annual_cost += annual_cost
                    total_capex += capex
        
        # Cap total reduction at 90% (technical/economic feasibility)
        max_reduction = baseline_emissions * 0.90
        if total_emission_reduction > max_reduction:
            scale_factor = max_reduction / total_emission_reduction
            total_emission_reduction = max_reduction
            total_annual_cost *= scale_factor
            total_capex *= scale_factor
            
            for tech in technologies_deployed:
                tech['EmissionReduction_kt'] *= scale_factor
                tech['AnnualCost_USD'] *= scale_factor
                tech['CAPEX_USD'] *= scale_factor
        
        # Employment impact estimation
        construction_jobs = total_capex / 200000  # $200k per construction job-year
        operational_jobs = total_annual_cost / 150000  # $150k per operational job
        
        # Economic impact (multiplier effects)
        local_economic_impact = total_capex * 1.8  # 1.8x multiplier for local economic activity
        
        facility_transition = {
            'FacilityID': facility_id,
            'Company': company,
            'Process': process,
            'Capacity_kt': capacity,
            'Baseline_Emissions_kt': baseline_emissions,
            'Emission_Reduction_kt': total_emission_reduction,
            'Final_Emissions_kt': baseline_emissions - total_emission_reduction,
            'Reduction_Percent': (total_emission_reduction / baseline_emissions * 100) if baseline_emissions > 0 else 0,
            'Technologies_Count': len(technologies_deployed),
            'Annual_Cost_USD': total_annual_cost,
            'Total_CAPEX_USD': total_capex,
            'Cost_per_tCO2_Avoided': total_annual_cost / total_emission_reduction if total_emission_reduction > 0 else 0,
            'Construction_Jobs': construction_jobs,
            'Operational_Jobs': operational_jobs,
            'Local_Economic_Impact_USD': local_economic_impact,
            'Technology_Details': '; '.join([f"{t['TechID']}({t['DeploymentLevel']:.1%},{t['EmissionReduction_kt']:.1f}kt)" 
                                           for t in technologies_deployed[:5]])  # Top 5 technologies
        }
        facility_transitions.append(facility_transition)
    
    facility_transition_df = pd.DataFrame(facility_transitions)
    
    # Create comprehensive visualizations
    fig = plt.figure(figsize=(24, 20))
    gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
    
    # 1. Company emission comparison (baseline vs final)
    ax1 = fig.add_subplot(gs[0, :])
    
    company_emissions = facility_transition_df.groupby('Company').agg({
        'Baseline_Emissions_kt': 'sum',
        'Final_Emissions_kt': 'sum',
        'Emission_Reduction_kt': 'sum'
    }).reset_index()
    company_emissions = company_emissions.sort_values('Baseline_Emissions_kt', ascending=True)
    
    x = np.arange(len(company_emissions))
    width = 0.35
    
    bars1 = ax1.barh(x - width/2, company_emissions['Baseline_Emissions_kt'], width, 
                    label='Baseline Emissions', color='red', alpha=0.8)
    bars2 = ax1.barh(x + width/2, company_emissions['Final_Emissions_kt'], width, 
                    label='Final Emissions', color='green', alpha=0.8)
    
    ax1.set_title('Company Emission Transitions', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Emissions (kt CO₂)')
    ax1.set_ylabel('Company')
    ax1.set_yticks(x)
    ax1.set_yticklabels(company_emissions['Company'])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add reduction percentages
    for i, (baseline, final) in enumerate(zip(company_emissions['Baseline_Emissions_kt'], 
                                            company_emissions['Final_Emissions_kt'])):
        reduction_pct = (1 - final/baseline) * 100 if baseline > 0 else 0
        ax1.text(max(baseline, final) + 500, i, f'-{reduction_pct:.1f}%', 
                va='center', fontweight='bold', fontsize=10)
    
    # 2. Investment requirements by company
    ax2 = fig.add_subplot(gs[1, 0])
    
    company_investment = facility_transition_df.groupby('Company')['Total_CAPEX_USD'].sum().sort_values()
    
    bars = ax2.barh(range(len(company_investment)), company_investment.values / 1e9, 
                   color='blue', alpha=0.7)
    ax2.set_title('CAPEX Investment by Company', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Investment (Billion USD)')
    ax2.set_yticks(range(len(company_investment)))
    ax2.set_yticklabels(company_investment.index, fontsize=10)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, value in zip(bars, company_investment.values):
        ax2.text(value/1e9 + 0.05, bar.get_y() + bar.get_height()/2,
                f'${value/1e9:.2f}B', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 3. Facility size distribution and transition impact
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Create capacity bins
    capacity_bins = [0, 100, 300, 500, 1000, float('inf')]
    capacity_labels = ['<100', '100-300', '300-500', '500-1000', '>1000']
    facility_transition_df['CapacityCategory'] = pd.cut(facility_transition_df['Capacity_kt'], 
                                                       bins=capacity_bins, labels=capacity_labels)
    
    capacity_analysis = facility_transition_df.groupby('CapacityCategory').agg({
        'FacilityID': 'count',
        'Emission_Reduction_kt': 'sum',
        'Total_CAPEX_USD': 'sum'
    }).reset_index()
    
    bars = ax3.bar(range(len(capacity_analysis)), capacity_analysis['Emission_Reduction_kt'], 
                  color='green', alpha=0.7)
    ax3.set_title('Emission Reduction by Facility Size', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Facility Capacity (kt)')
    ax3.set_ylabel('Total Emission Reduction (kt CO₂)')
    ax3.set_xticks(range(len(capacity_analysis)))
    ax3.set_xticklabels(capacity_analysis['CapacityCategory'])
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add facility count labels
    for bar, facilities, reduction in zip(bars, capacity_analysis['FacilityID'], capacity_analysis['Emission_Reduction_kt']):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'{facilities} facilities\n{reduction:.0f} kt', ha='center', va='bottom', 
                fontweight='bold', fontsize=9)
    
    # 4. Employment impact by company
    ax4 = fig.add_subplot(gs[1, 2])
    
    company_jobs = facility_transition_df.groupby('Company').agg({
        'Construction_Jobs': 'sum',
        'Operational_Jobs': 'sum'
    }).reset_index()
    company_jobs = company_jobs.sort_values('Construction_Jobs', ascending=True)
    
    x = np.arange(len(company_jobs))
    width = 0.35
    
    bars1 = ax4.barh(x - width/2, company_jobs['Construction_Jobs'], width, 
                    label='Construction Jobs', color='orange', alpha=0.8)
    bars2 = ax4.barh(x + width/2, company_jobs['Operational_Jobs'], width, 
                    label='Operational Jobs', color='purple', alpha=0.8)
    
    ax4.set_title('Employment Impact by Company', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Jobs Created')
    ax4.set_yticks(x)
    ax4.set_yticklabels(company_jobs['Company'], fontsize=10)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='x')
    
    # 5. Technology deployment heatmap
    ax5 = fig.add_subplot(gs[2, :2])
    
    # Create technology deployment matrix
    tech_deployment_matrix = []
    
    for _, facility in facility_transition_df.iterrows():
        if facility['Technology_Details']:
            tech_details = facility['Technology_Details'].split('; ')
            for tech_detail in tech_details:
                if '(' in tech_detail:
                    tech_id = tech_detail.split('(')[0]
                    deployment_str = tech_detail.split('(')[1].split(',')[0]
                    deployment_val = float(deployment_str.rstrip('%')) / 100
                    
                    tech_deployment_matrix.append({
                        'FacilityID': facility['FacilityID'],
                        'Company': facility['Company'],
                        'Process': facility['Process'],
                        'TechID': tech_id,
                        'DeploymentLevel': deployment_val
                    })
    
    if tech_deployment_matrix:
        tech_matrix_df = pd.DataFrame(tech_deployment_matrix)
        
        # Create pivot table for heatmap
        tech_company_pivot = tech_matrix_df.pivot_table(
            index='TechID', columns='Company', values='DeploymentLevel', aggfunc='mean'
        ).fillna(0)
        
        # Filter to most significant technologies
        tech_totals = tech_company_pivot.sum(axis=1).sort_values(ascending=False)
        top_techs = tech_totals.head(8).index
        
        sns.heatmap(tech_company_pivot.loc[top_techs], annot=True, fmt='.2f', cmap='YlOrRd', 
                   ax=ax5, cbar_kws={'label': 'Deployment Level'})
        ax5.set_title('Technology Deployment by Company', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Company')
        ax5.set_ylabel('Technology')
    
    # 6. Cost effectiveness by process
    ax6 = fig.add_subplot(gs[2, 2])
    
    process_cost_eff = facility_transition_df.groupby('Process').agg({
        'Cost_per_tCO2_Avoided': 'mean',
        'Emission_Reduction_kt': 'sum',
        'FacilityID': 'count'
    }).reset_index()
    process_cost_eff = process_cost_eff.sort_values('Cost_per_tCO2_Avoided')
    
    bars = ax6.bar(range(len(process_cost_eff)), process_cost_eff['Cost_per_tCO2_Avoided'], 
                  color=['red', 'orange', 'green'], alpha=0.8)
    ax6.set_title('Cost Effectiveness by Process', fontsize=14, fontweight='bold')
    ax6.set_xlabel('Process Type')
    ax6.set_ylabel('Cost per tCO₂ Avoided (USD)')
    ax6.set_xticks(range(len(process_cost_eff)))
    ax6.set_xticklabels(process_cost_eff['Process'], rotation=45, ha='right')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, process_cost_eff['Cost_per_tCO2_Avoided']):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 1000,
                f'${value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 7. Regional economic impact
    ax7 = fig.add_subplot(gs[3, 0])
    
    regional_impact = facility_transition_df.groupby('Company')['Local_Economic_Impact_USD'].sum().sort_values()
    
    bars = ax7.barh(range(len(regional_impact)), regional_impact.values / 1e9, 
                   color='teal', alpha=0.7)
    ax7.set_title('Local Economic Impact by Company', fontsize=14, fontweight='bold')
    ax7.set_xlabel('Economic Impact (Billion USD)')
    ax7.set_yticks(range(len(regional_impact)))
    ax7.set_yticklabels(regional_impact.index, fontsize=10)
    ax7.grid(True, alpha=0.3, axis='x')
    
    # 8. Transition timeline and phases
    ax8 = fig.add_subplot(gs[3, 1:])
    
    # Estimate implementation timeline based on technology complexity
    timeline_phases = {
        'Phase 1 (2025-2027)': ['EE_UTL', 'RE_003', 'RE_002'],  # Immediate deployment
        'Phase 2 (2028-2032)': ['EE_BTX', 'HP_001', 'RE_001'],  # Medium-term
        'Phase 3 (2033-2040)': ['EE_NCC', 'HP_002', 'ES_001']   # Long-term
    }
    
    phase_impact = {}
    for phase, tech_list in timeline_phases.items():
        phase_facilities = facility_transition_df[
            facility_transition_df['Technology_Details'].str.contains('|'.join(tech_list), na=False)
        ]
        phase_impact[phase] = {
            'facilities': len(phase_facilities),
            'emission_reduction': phase_facilities['Emission_Reduction_kt'].sum(),
            'investment': phase_facilities['Total_CAPEX_USD'].sum() / 1e9
        }
    
    phases = list(phase_impact.keys())
    facilities = [phase_impact[p]['facilities'] for p in phases]
    reductions = [phase_impact[p]['emission_reduction'] for p in phases]
    investments = [phase_impact[p]['investment'] for p in phases]
    
    x = np.arange(len(phases))
    width = 0.25
    
    ax8_twin = ax8.twinx()
    
    bars1 = ax8.bar(x - width, facilities, width, label='Facilities', color='blue', alpha=0.7)
    bars2 = ax8.bar(x, [r/100 for r in reductions], width, label='Emission Reduction (100s kt)', color='green', alpha=0.7)
    bars3 = ax8_twin.bar(x + width, investments, width, label='Investment (Billion USD)', color='red', alpha=0.7)
    
    ax8.set_title('Implementation Timeline and Impact', fontsize=14, fontweight='bold')
    ax8.set_xlabel('Implementation Phase')
    ax8.set_ylabel('Facilities / Emission Reduction')
    ax8_twin.set_ylabel('Investment (Billion USD)')
    ax8.set_xticks(x)
    ax8.set_xticklabels(phases, rotation=45, ha='right')
    
    # Combine legends
    lines1, labels1 = ax8.get_legend_handles_labels()
    lines2, labels2 = ax8_twin.get_legend_handles_labels()
    ax8.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax8.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "detailed_facility_transition_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed datasets
    facility_transition_df.to_csv(output_dir / "detailed_facility_transitions.csv", index=False)
    company_stats.to_csv(output_dir / "company_baseline_statistics.csv", index=False)
    
    return facility_transition_df, company_stats, phase_impact

if __name__ == "__main__":
    facilities, companies, timeline = create_detailed_facility_analysis()