#!/usr/bin/env python3
"""
Korean Petrochemical MACC Model - Main execution script
Regional facility-level deployment with alternative technologies only
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def load_regional_data():
    """Load regional facilities and technology data"""
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    with pd.ExcelFile(data_file) as xls:
        facilities_df = pd.read_excel(xls, sheet_name='RegionalFacilities')
        technologies_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
        costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
    
    return facilities_df, technologies_df, costs_df

def create_facility_technology_matrix(facilities_df, technologies_df, costs_df):
    """Create facility-technology deployment matrix"""
    
    # Merge technology data with costs
    tech_data = technologies_df.merge(costs_df, on='TechID')
    
    # Create deployment options matrix
    deployment_options = []
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        
        for _, tech in tech_data.iterrows():
            tech_id = tech['TechID']
            tech_group = tech['TechGroup']
            
            # Get facility capacity for this technology group
            capacity_col = f"{tech_group}_Capacity_kt_per_year"
            if capacity_col in facility.index:
                baseline_capacity = facility[capacity_col]
                
                # Calculate maximum deployment (capacity * max applicability)
                max_deployment = baseline_capacity * tech['MaxApplicability']
                
                # Calculate facility-specific costs (adjust for regional factors)
                facility_capex_multiplier = facility['Labor_Cost_Index'] / 100
                facility_opex_multiplier = facility['Electricity_Price_USD_per_MWh'] / 118  # Baseline price
                
                adjusted_capex = tech['CAPEX_Million_USD_per_kt_capacity'] * facility_capex_multiplier
                adjusted_opex = tech['OPEX_Delta_USD_per_t'] * facility_opex_multiplier
                
                # Calculate LCOA (Levelized Cost of Abatement)
                lifetime = tech['Lifetime_years']
                discount_rate = 0.05
                crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
                
                annual_capex_per_t = (adjusted_capex * 1e6 * crf) / (baseline_capacity * 1000)  # USD/t
                total_annual_cost_per_t = annual_capex_per_t + adjusted_opex
                lcoa = total_annual_cost_per_t / tech['EmissionReduction_tCO2_per_t']
                
                deployment_options.append({
                    'DeploymentID': f"{tech_id}_{facility_id}",
                    'TechID': tech_id,
                    'FacilityID': facility_id,
                    'Region': facility['Region'],
                    'Company': facility['Company'],
                    'TechGroup': tech_group,
                    'Technology': tech['TechnologyCategory'],
                    'BaselineCapacity_kt': baseline_capacity,
                    'MaxDeployment_kt': max_deployment,
                    'AbatementPotential_tCO2_per_t': tech['EmissionReduction_tCO2_per_t'],
                    'TotalAbatementPotential_ktCO2': max_deployment * tech['EmissionReduction_tCO2_per_t'],
                    'LCOA_USD_per_tCO2': lcoa,
                    'CAPEX_Million_USD': max_deployment * adjusted_capex,
                    'CommercialYear': tech['CommercialYear'],
                    'TRL': tech['TechnicalReadiness']
                })
    
    return pd.DataFrame(deployment_options)

def generate_macc_curve(deployment_df, year=2030):
    """Generate MACC curve for given year"""
    
    # Filter technologies available by year
    available_deployments = deployment_df[deployment_df['CommercialYear'] <= year].copy()
    
    # Sort by cost-effectiveness (LCOA)
    available_deployments = available_deployments.sort_values('LCOA_USD_per_tCO2')
    
    # Calculate cumulative abatement
    available_deployments['CumulativeAbatement_MtCO2'] = (
        available_deployments['TotalAbatementPotential_ktCO2'].cumsum() / 1000
    )
    
    return available_deployments

def create_summary_analysis(deployment_df):
    """Create summary analysis by region and technology"""
    
    # Regional summary
    regional_summary = deployment_df.groupby('Region').agg({
        'MaxDeployment_kt': 'sum',
        'TotalAbatementPotential_ktCO2': 'sum',
        'CAPEX_Million_USD': 'sum',
        'LCOA_USD_per_tCO2': 'mean'
    }).round(2)
    
    # Technology summary
    tech_summary = deployment_df.groupby('Technology').agg({
        'MaxDeployment_kt': 'sum',
        'TotalAbatementPotential_ktCO2': 'sum',
        'CAPEX_Million_USD': 'sum',
        'LCOA_USD_per_tCO2': 'mean'
    }).round(2)
    
    # Company summary
    company_summary = deployment_df.groupby('Company').agg({
        'MaxDeployment_kt': 'sum',
        'TotalAbatementPotential_ktCO2': 'sum',
        'CAPEX_Million_USD': 'sum',
        'LCOA_USD_per_tCO2': 'mean'
    }).round(2)
    
    return regional_summary, tech_summary, company_summary

def simulate_technology_deployment(deployment_df, years=range(2023, 2051)):
    """Simulate technology deployment pathway from 2023 to 2050"""
    
    # Calculate baseline emissions (2023)
    baseline_emissions = {
        'NCC': 3500 * 2.85 + 2800 * 1.23 + 1200 * 0.65,  # Activity * EmissionIntensity
        'BTX': 1200 * 1.52 + 800 * 0.89 + 1100 * 0.48,
        'C4': 450 * 2.21 + 350 * 0.98 + 200 * 0.54
    }
    total_baseline = sum(baseline_emissions.values()) / 1000  # Convert to MtCO2
    
    # Simulate deployment pathway
    pathway_data = []
    
    for year in years:
        # Get technologies available by this year
        available_tech = deployment_df[deployment_df['CommercialYear'] <= year].copy()
        
        if available_tech.empty:
            # No technologies available yet - use baseline
            year_data = {
                'Year': year,
                'BaselineEmissions_MtCO2': total_baseline,
                'AlternativeEmissions_MtCO2': 0.0,
                'TotalEmissions_MtCO2': total_baseline,
                'EmissionReduction_MtCO2': 0.0,
                'CumulativeInvestment_Billion_USD': 0.0,
                'TotalProductionCost_Billion_USD': total_baseline * 0.5  # Assume baseline cost
            }
        else:
            # Calculate deployment based on ramp rates and cost-effectiveness
            years_since_start = year - 2023
            deployment_fraction = min(0.8, years_since_start * 0.1)  # Gradual ramp up to 80% by 2030
            
            # Deploy cost-effective technologies first (LCOA < 100 USD/tCO2)
            cost_effective = available_tech[available_tech['LCOA_USD_per_tCO2'] <= 100].copy()
            cost_effective = cost_effective.sort_values('LCOA_USD_per_tCO2')
            
            # Calculate actual deployment
            total_deployment_kt = 0
            total_abatement_kt = 0
            cumulative_investment = 0
            production_cost_premium = 0
            
            for _, tech in cost_effective.iterrows():
                max_deploy = tech['MaxDeployment_kt'] * deployment_fraction
                total_deployment_kt += max_deploy
                total_abatement_kt += max_deploy * tech['AbatementPotential_tCO2_per_t']
                cumulative_investment += max_deploy * tech['CAPEX_Million_USD'] / tech['MaxDeployment_kt']
                
                # Calculate production cost change
                baseline_production = tech['BaselineCapacity_kt']
                opex_change = max_deploy * tech['LCOA_USD_per_tCO2'] * tech['AbatementPotential_tCO2_per_t'] / 1000  # Million USD
                production_cost_premium += opex_change
            
            emission_reduction = total_abatement_kt / 1000  # Convert to MtCO2
            remaining_emissions = max(0, total_baseline - emission_reduction)
            total_production_cost = total_baseline * 0.5 + production_cost_premium / 1000  # Billion USD
            
            year_data = {
                'Year': year,
                'BaselineEmissions_MtCO2': total_baseline,
                'AlternativeEmissions_MtCO2': emission_reduction,
                'TotalEmissions_MtCO2': remaining_emissions,
                'EmissionReduction_MtCO2': emission_reduction,
                'CumulativeInvestment_Billion_USD': cumulative_investment / 1000,
                'TotalProductionCost_Billion_USD': total_production_cost,
                'DeploymentFraction': deployment_fraction
            }
        
        pathway_data.append(year_data)
    
    return pd.DataFrame(pathway_data)

def calculate_technology_shares(deployment_df, pathway_df):
    """Calculate technology shares over time"""
    
    years = pathway_df['Year'].tolist()
    tech_shares = []
    
    for year in years:
        available_tech = deployment_df[deployment_df['CommercialYear'] <= year].copy()
        
        if available_tech.empty:
            continue
            
        # Get deployment fraction for this year
        deployment_fraction = pathway_df[pathway_df['Year'] == year]['DeploymentFraction'].iloc[0]
        
        # Calculate shares by technology
        tech_deployment = available_tech.groupby('Technology').agg({
            'MaxDeployment_kt': 'sum',
            'TotalAbatementPotential_ktCO2': 'sum'
        })
        
        total_deployment = tech_deployment['MaxDeployment_kt'].sum() * deployment_fraction
        
        for tech in tech_deployment.index:
            tech_capacity = tech_deployment.loc[tech, 'MaxDeployment_kt'] * deployment_fraction
            share = tech_capacity / total_deployment if total_deployment > 0 else 0
            
            tech_shares.append({
                'Year': year,
                'Technology': tech,
                'Capacity_kt': tech_capacity,
                'Share': share
            })
    
    return pd.DataFrame(tech_shares)

def plot_comprehensive_analysis(pathway_df, tech_shares_df, deployment_df):
    """Create comprehensive analysis plots"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Emission Pathway
    ax1.plot(pathway_df['Year'], pathway_df['BaselineEmissions_MtCO2'], 
             'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
    ax1.plot(pathway_df['Year'], pathway_df['TotalEmissions_MtCO2'], 
             'b-', linewidth=3, label='With Alternative Technologies')
    ax1.fill_between(pathway_df['Year'], pathway_df['TotalEmissions_MtCO2'], 
                     pathway_df['BaselineEmissions_MtCO2'], alpha=0.3, color='green', label='Emission Reduction')
    
    # Add target lines
    targets = {2030: 15.9, 2035: 13.1, 2040: 9.4, 2045: 5.6, 2050: 3.7}  # 15%, 30%, 50%, 70%, 80% reduction
    for year, target in targets.items():
        ax1.scatter(year, target, color='red', s=100, zorder=5)
        ax1.annotate(f'{int((18.7-target)/18.7*100)}%', (year, target), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2/year)')
    ax1.set_title('Korean Petrochemical Emission Pathway 2023-2050')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 20)
    
    # 2. Technology Share Evolution
    if not tech_shares_df.empty:
        pivot_shares = tech_shares_df.pivot(index='Year', columns='Technology', values='Share').fillna(0)
        
        # Create stacked area plot
        ax2.stackplot(pivot_shares.index, *pivot_shares.T.values, 
                     labels=pivot_shares.columns, alpha=0.8)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Technology Share (%)')
        ax2.set_title('Alternative Technology Deployment Shares')
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
    
    # 3. Cumulative Investment
    ax3.plot(pathway_df['Year'], pathway_df['CumulativeInvestment_Billion_USD'], 
             'g-', linewidth=3, marker='o', markersize=4)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Cumulative Investment (Billion USD)')
    ax3.set_title('Required Investment for Alternative Technologies')
    ax3.grid(True, alpha=0.3)
    
    # Add investment milestones
    milestones = [1000, 2000, 3000, 4000]
    for milestone in milestones:
        if pathway_df['CumulativeInvestment_Billion_USD'].max() >= milestone:
            milestone_year = pathway_df[pathway_df['CumulativeInvestment_Billion_USD'] >= milestone]['Year'].iloc[0]
            ax3.axhline(y=milestone, color='red', linestyle='--', alpha=0.5)
            ax3.annotate(f'${milestone}B', (2025, milestone), fontsize=8)
    
    # 4. Total Production Cost Evolution
    baseline_cost = pathway_df['TotalProductionCost_Billion_USD'].iloc[0]
    ax4.plot(pathway_df['Year'], pathway_df['TotalProductionCost_Billion_USD'] / baseline_cost * 100, 
             'purple', linewidth=3, marker='s', markersize=4)
    ax4.axhline(y=100, color='gray', linestyle='--', alpha=0.7, label='2023 Baseline')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Total Production Cost (% of 2023 baseline)')
    ax4.set_title('Production Cost Evolution (Including Technology Deployment)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_macc_curve(macc_df, year=2030):
    """Plot MACC curve"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # MACC curve
    ax1.step(macc_df['CumulativeAbatement_MtCO2'], macc_df['LCOA_USD_per_tCO2'], 
             where='post', linewidth=2, color='darkblue')
    ax1.fill_between(macc_df['CumulativeAbatement_MtCO2'], 0, macc_df['LCOA_USD_per_tCO2'], 
                     step='post', alpha=0.3, color='lightblue')
    
    ax1.set_xlabel('Cumulative Abatement Potential (MtCO2/year)')
    ax1.set_ylabel('Levelized Cost of Abatement (USD/tCO2)')
    ax1.set_title(f'Korean Petrochemical MACC Curve {year}\n(Regional Facility-Level Alternative Technologies)')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='$100/tCO2 threshold')
    ax1.legend()
    
    # Regional breakdown
    regional_abatement = macc_df.groupby('Region')['TotalAbatementPotential_ktCO2'].sum() / 1000
    colors = {'Yeosu': 'darkgreen', 'Daesan': 'orange', 'Ulsan': 'purple'}
    
    ax2.bar(regional_abatement.index, regional_abatement.values, 
            color=[colors.get(region, 'gray') for region in regional_abatement.index])
    ax2.set_ylabel('Total Abatement Potential (MtCO2/year)')
    ax2.set_title('Abatement Potential by Region')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def main():
    """Main execution function"""
    
    print("🏭 Korean Petrochemical MACC Model (Main)")
    print("=" * 50)
    
    # Load data
    print("📊 Loading regional facilities and technology data...")
    facilities_df, technologies_df, costs_df = load_regional_data()
    
    print(f"   - Facilities: {len(facilities_df)} across {facilities_df['Region'].nunique()} regions")
    print(f"   - Technologies: {len(technologies_df)} alternative technologies")
    print(f"   - Companies: {facilities_df['Company'].nunique()}")
    
    # Create deployment matrix
    print("\n🔧 Creating facility-technology deployment matrix...")
    deployment_df = create_facility_technology_matrix(facilities_df, technologies_df, costs_df)
    
    print(f"   - Total deployment options: {len(deployment_df)}")
    print(f"   - Total abatement potential: {deployment_df['TotalAbatementPotential_ktCO2'].sum()/1000:.1f} MtCO2/year")
    print(f"   - Total investment potential: ${deployment_df['CAPEX_Million_USD'].sum()/1000:.1f} billion")
    
    # Generate MACC curve for 2030
    print("\n📈 Generating MACC curve for 2030...")
    macc_2030 = generate_macc_curve(deployment_df, 2030)
    
    # Create pathway simulation
    print("\n🔮 Simulating technology deployment pathway 2023-2050...")
    pathway_df = simulate_technology_deployment(deployment_df)
    
    # Calculate technology shares over time
    print("\n📊 Calculating technology shares evolution...")
    tech_shares_df = calculate_technology_shares(deployment_df, pathway_df)
    
    # Create summaries
    print("\n📋 Creating summary analyses...")
    regional_summary, tech_summary, company_summary = create_summary_analysis(deployment_df)
    
    # Save outputs
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n💾 Saving outputs to {output_dir}/...")
    
    # Save detailed data
    deployment_df.to_csv(output_dir / "facility_technology_matrix.csv", index=False)
    macc_2030.to_csv(output_dir / "macc_curve_2030.csv", index=False)
    pathway_df.to_csv(output_dir / "emission_pathway_2023_2050.csv", index=False)
    tech_shares_df.to_csv(output_dir / "technology_shares_evolution.csv", index=False)
    
    # Save summaries
    regional_summary.to_csv(output_dir / "regional_summary.csv")
    tech_summary.to_csv(output_dir / "technology_summary.csv") 
    company_summary.to_csv(output_dir / "company_summary.csv")
    
    # Create and save plots
    print("\n📊 Creating comprehensive analysis plots...")
    
    # MACC curve
    fig1 = plot_macc_curve(macc_2030, 2030)
    fig1.savefig(output_dir / "regional_macc_2030.png", dpi=300, bbox_inches='tight')
    
    # Comprehensive analysis plots
    fig2 = plot_comprehensive_analysis(pathway_df, tech_shares_df, deployment_df)
    fig2.savefig(output_dir / "comprehensive_analysis_2023_2050.png", dpi=300, bbox_inches='tight')
    
    # Close figures to free memory
    plt.close(fig1)
    plt.close(fig2)
    
    # Print key results
    print("\n🎯 KEY RESULTS:")
    print(f"   - Available abatement by 2030: {macc_2030['TotalAbatementPotential_ktCO2'].sum()/1000:.1f} MtCO2/year")
    print(f"   - Cost-effective abatement (<$100/tCO2): {macc_2030[macc_2030['LCOA_USD_per_tCO2'] <= 100]['TotalAbatementPotential_ktCO2'].sum()/1000:.1f} MtCO2/year")
    print(f"   - Required investment by 2030: ${pathway_df[pathway_df['Year'] == 2030]['CumulativeInvestment_Billion_USD'].iloc[0]:.1f} billion")
    
    print("\n📈 EMISSION PATHWAY RESULTS:")
    print(f"   - 2023 baseline: {pathway_df[pathway_df['Year'] == 2023]['BaselineEmissions_MtCO2'].iloc[0]:.1f} MtCO2/year")
    print(f"   - 2030 emissions: {pathway_df[pathway_df['Year'] == 2030]['TotalEmissions_MtCO2'].iloc[0]:.1f} MtCO2/year")
    print(f"   - 2050 emissions: {pathway_df[pathway_df['Year'] == 2050]['TotalEmissions_MtCO2'].iloc[0]:.1f} MtCO2/year")
    print(f"   - Total reduction by 2050: {pathway_df[pathway_df['Year'] == 2050]['EmissionReduction_MtCO2'].iloc[0]:.1f} MtCO2/year ({pathway_df[pathway_df['Year'] == 2050]['EmissionReduction_MtCO2'].iloc[0]/pathway_df[pathway_df['Year'] == 2023]['BaselineEmissions_MtCO2'].iloc[0]*100:.0f}%)")
    
    print("\n🌍 REGIONAL BREAKDOWN:")
    for region in regional_summary.index:
        abatement = regional_summary.loc[region, 'TotalAbatementPotential_ktCO2'] / 1000
        investment = regional_summary.loc[region, 'CAPEX_Million_USD'] / 1000
        avg_cost = regional_summary.loc[region, 'LCOA_USD_per_tCO2']
        print(f"   - {region}: {abatement:.1f} MtCO2/year, ${investment:.1f}B, avg ${avg_cost:.0f}/tCO2")
    
    print("\n🔬 TOP TECHNOLOGIES BY ABATEMENT:")
    tech_ranking = tech_summary.sort_values('TotalAbatementPotential_ktCO2', ascending=False).head(5)
    for tech in tech_ranking.index:
        abatement = tech_ranking.loc[tech, 'TotalAbatementPotential_ktCO2'] / 1000
        cost = tech_ranking.loc[tech, 'LCOA_USD_per_tCO2']
        print(f"   - {tech}: {abatement:.1f} MtCO2/year at ${cost:.0f}/tCO2")
    
    print(f"\n✅ Model completed successfully! Check {output_dir}/ for detailed results.")

if __name__ == "__main__":
    main()