#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model
Optimizes emission reduction pathways to meet targets with minimum cost
"""

import pandas as pd
import numpy as np
from pulp import *
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set Korean font support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MACCOptimizationModel:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load optimization data
        self.data_file = 'data/korean_petrochemical_macc_optimization.xlsx'
        self.tech_options = pd.read_excel(self.data_file, sheet_name='TechOptions')
        self.macc_template = pd.read_excel(self.data_file, sheet_name='MACC_Template')
        self.baseline_assumptions = pd.read_excel(self.data_file, sheet_name='Baseline_Assumptions')
        self.facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        
        # Get baseline emissions
        self.baseline_emissions = self.baseline_assumptions[
            self.baseline_assumptions['Parameter'] == 'Total_Scope1plus2_MtCO2e_2023'
        ]['Value'].iloc[0]
        
        # Merge technology data
        tech_cols = ['TechID', 'Product', 'StartYear_Commercial', 'MaxPenetration', 'RampUpSharePerYear']
        self.tech_data = self.macc_template.merge(
            self.tech_options[tech_cols], 
            on='TechID'
        )
        # Use TRL from MACC_Template (TRL_x after merge, but we'll keep original name)
        if 'TRL_x' in self.tech_data.columns:
            self.tech_data['TRL'] = self.tech_data['TRL_x']
        
        print(f"✓ Loaded optimization data: {len(self.tech_data)} technologies")
        print(f"✓ Baseline emissions: {self.baseline_emissions:.1f} Mt CO₂")
        
    def setup_optimization_problem(self, target_year=2030, emission_target_mt=26.0, planning_horizon=2050):
        """Setup optimization problem for emission target"""
        
        print(f"\n🎯 Setting up optimization for {emission_target_mt} Mt CO₂ target by {target_year}")
        
        # Years from 2025 to planning horizon
        years = list(range(2025, planning_horizon + 1))
        target_year_idx = target_year - 2025
        
        # Filter technologies available by target year
        available_techs = self.tech_data[self.tech_data['StartYear_Commercial'] <= target_year].copy()
        
        print(f"✓ Available technologies by {target_year}: {len(available_techs)}")
        
        # Create optimization problem
        prob = LpProblem("MACC_Optimization", LpMinimize)
        
        # Decision variables: deployment level for each technology and year
        deployment_vars = {}
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            for year in years:
                if year >= tech['StartYear_Commercial']:
                    var_name = f"deploy_{tech_id}_{year}"
                    deployment_vars[(tech_id, year)] = LpVariable(
                        var_name, 
                        lowBound=0, 
                        upBound=tech['MaxPenetration'],
                        cat='Continuous'
                    )
        
        # Objective: Minimize total cost
        total_cost = 0
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in years:
                if year >= tech['StartYear_Commercial'] and (tech_id, year) in deployment_vars:
                    annual_cost = (deployment_vars[(tech_id, year)] * 
                                 abatement_potential * cost_per_tco2 * 1_000_000)  # Convert to USD
                    total_cost += annual_cost
        
        prob += total_cost
        
        # Constraint 1: Meet emission target by target year
        target_year_abatement = 0
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            if (tech_id, target_year) in deployment_vars:
                abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
                target_year_abatement += (deployment_vars[(tech_id, target_year)] * abatement_potential)
        
        required_abatement = self.baseline_emissions - emission_target_mt
        prob += target_year_abatement >= required_abatement, f"EmissionTarget_{target_year}"
        
        # Constraint 2: Ramp-up constraints
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            ramp_rate = tech['RampUpSharePerYear']
            start_year = tech['StartYear_Commercial']
            
            for year in years:
                if year > start_year and (tech_id, year) in deployment_vars and (tech_id, year-1) in deployment_vars:
                    prob += (deployment_vars[(tech_id, year)] <= 
                           deployment_vars[(tech_id, year-1)] + ramp_rate), f"RampUp_{tech_id}_{year}"
        
        # Constraint 3: Technology competition within products
        product_groups = available_techs.groupby('Product')
        for product, product_techs in product_groups:
            if len(product_techs) > 1 and product != 'All_Products':  # Multiple competing technologies
                for year in years:
                    total_penetration = 0
                    for _, tech in product_techs.iterrows():
                        tech_id = tech['TechID']
                        if (tech_id, year) in deployment_vars:
                            total_penetration += deployment_vars[(tech_id, year)]
                    
                    prob += total_penetration <= 1.0, f"ProductCompetition_{product}_{year}"
        
        self.prob = prob
        self.deployment_vars = deployment_vars
        self.available_techs = available_techs
        self.years = years
        self.target_year = target_year
        self.emission_target = emission_target_mt
        
        return prob
    
    def solve_optimization(self):
        """Solve the optimization problem"""
        
        print("🔧 Solving optimization problem...")
        
        # Solve the problem
        self.prob.solve(PULP_CBC_CMD(msg=0))
        
        # Check solution status
        status = LpStatus[self.prob.status]
        print(f"✓ Optimization Status: {status}")
        
        if status != 'Optimal':
            print("❌ No optimal solution found!")
            return None
        
        # Extract results
        results = []
        total_cost = 0
        
        for _, tech in self.available_techs.iterrows():
            tech_id = tech['TechID']
            product = tech['Product']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in self.years:
                if (tech_id, year) in self.deployment_vars:
                    deployment_level = self.deployment_vars[(tech_id, year)].varValue or 0
                    
                    if deployment_level > 0.001:  # Only record significant deployments
                        annual_abatement = deployment_level * abatement_potential
                        annual_cost = annual_abatement * cost_per_tco2 * 1_000_000  # USD
                        total_cost += annual_cost
                        
                        results.append({
                            'TechID': tech_id,
                            'Product': product,
                            'Year': year,
                            'DeploymentLevel': deployment_level,
                            'AbatementMtCO2': annual_abatement,
                            'AnnualCostUSD': annual_cost,
                            'CostPerTonCO2': cost_per_tco2,
                            'StartYear_Commercial': tech['StartYear_Commercial'],
                            'TRL': tech['TRL']
                        })
        
        self.results_df = pd.DataFrame(results)
        self.total_optimization_cost = total_cost
        
        print(f"✓ Total optimization cost: ${total_cost/1e9:.2f} billion USD")
        print(f"✓ Deployed technologies: {len(self.results_df['TechID'].unique())}")
        
        return self.results_df
    
    def analyze_facility_transitions(self):
        """Analyze which facilities should transition to which technologies"""
        
        print("\n🏭 Analyzing facility-level transitions...")
        
        # Map technologies to facilities based on product matching
        facility_transitions = []
        
        # Get technologies deployed by target year
        target_year_deployments = self.results_df[
            self.results_df['Year'] == self.target_year
        ].copy()
        
        for _, deployment in target_year_deployments.iterrows():
            tech_id = deployment['TechID']
            product = deployment['Product']
            deployment_level = deployment['DeploymentLevel']
            abatement_per_facility = deployment['AbatementMtCO2']
            
            if product == 'All_Products':
                # Cross-cutting technology applies to all facilities
                eligible_facilities = self.facility_data.copy()
            else:
                # Product-specific technology
                eligible_facilities = self.facility_data[
                    self.facility_data['product'] == product
                ].copy()
            
            if len(eligible_facilities) == 0:
                continue
            
            # Sort facilities by emission intensity (prioritize high emitters)
            eligible_facilities = eligible_facilities.sort_values(
                'emission_intensity_t_co2_per_t', ascending=False
            )
            
            # Calculate number of facilities to transition based on deployment level
            total_capacity = eligible_facilities['capacity_kt'].sum()
            target_capacity = total_capacity * deployment_level
            
            cumulative_capacity = 0
            selected_facilities = []
            
            for _, facility in eligible_facilities.iterrows():
                if cumulative_capacity < target_capacity:
                    facility_capacity = facility['capacity_kt']
                    remaining_capacity = target_capacity - cumulative_capacity
                    
                    if facility_capacity <= remaining_capacity:
                        # Full facility transition
                        transition_fraction = 1.0
                        capacity_transitioned = facility_capacity
                    else:
                        # Partial facility transition
                        transition_fraction = remaining_capacity / facility_capacity
                        capacity_transitioned = remaining_capacity
                    
                    # Calculate transition costs and benefits
                    annual_emissions_before = facility['annual_emissions_kt_co2'] * transition_fraction
                    emission_intensity_after = facility['emission_intensity_t_co2_per_t'] * (1 - deployment['AbatementMtCO2'] / 52.0)  # Rough approximation
                    annual_emissions_after = capacity_transitioned * emission_intensity_after
                    
                    annual_abatement = (annual_emissions_before - annual_emissions_after) / 1000  # Convert to Mt
                    annual_cost = annual_abatement * deployment['CostPerTonCO2'] * 1_000_000
                    
                    facility_transitions.append({
                        'FacilityID': facility['facility_id'],
                        'Company': facility['company'],
                        'Location': facility['location'],
                        'Product': facility['product'],
                        'TechID': tech_id,
                        'TransitionFraction': transition_fraction,
                        'CapacityTransitioned_kt': capacity_transitioned,
                        'EmissionsBefore_ktCO2': annual_emissions_before,
                        'EmissionsAfter_ktCO2': annual_emissions_after,
                        'AbatementMtCO2': annual_abatement,
                        'AnnualCostUSD': annual_cost,
                        'CostPerTonCO2': deployment['CostPerTonCO2'],
                        'StartYear': facility['start_year'],
                        'FacilityAge': self.target_year - facility['start_year']
                    })
                    
                    cumulative_capacity += capacity_transitioned
                    
                    if cumulative_capacity >= target_capacity:
                        break
        
        self.facility_transitions_df = pd.DataFrame(facility_transitions)
        
        print(f"✓ Facility transitions identified: {len(self.facility_transitions_df)}")
        
        return self.facility_transitions_df
    
    def analyze_company_cost_effectiveness(self):
        """Analyze cost-effectiveness by company"""
        
        print("\n💰 Analyzing company-level cost-effectiveness...")
        
        # Aggregate transitions by company
        company_analysis = self.facility_transitions_df.groupby('Company').agg({
            'CapacityTransitioned_kt': 'sum',
            'AbatementMtCO2': 'sum',
            'AnnualCostUSD': 'sum',
            'TechID': 'nunique'
        }).reset_index()
        
        company_analysis['CostEffectiveness_USD_per_tCO2'] = (
            company_analysis['AnnualCostUSD'] / (company_analysis['AbatementMtCO2'] * 1000)
        )
        
        company_analysis = company_analysis.sort_values('CostEffectiveness_USD_per_tCO2')
        
        # Add baseline company emissions for context
        company_baseline = self.facility_data.groupby('company')['annual_emissions_kt_co2'].sum().reset_index()
        company_baseline.columns = ['Company', 'BaselineEmissions_ktCO2']
        
        company_analysis = company_analysis.merge(company_baseline, on='Company', how='left')
        company_analysis['EmissionReductionShare'] = (
            company_analysis['AbatementMtCO2'] * 1000 / company_analysis['BaselineEmissions_ktCO2']
        )
        
        self.company_analysis_df = company_analysis
        
        print(f"✓ Company analysis complete: {len(company_analysis)} companies affected")
        
        return company_analysis
    
    def create_optimization_visualizations(self):
        """Create comprehensive optimization result visualizations"""
        
        print("\n📊 Creating optimization visualizations...")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Technology deployment timeline
        ax1 = plt.subplot(3, 3, 1)
        deployment_timeline = self.results_df.pivot_table(
            values='DeploymentLevel', index='Year', columns='TechID', fill_value=0
        )
        
        for tech_id in deployment_timeline.columns:
            ax1.plot(deployment_timeline.index, deployment_timeline[tech_id], 
                    marker='o', linewidth=2, label=tech_id)
        
        ax1.set_title('Technology Deployment Timeline', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Deployment Level')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. Emission pathway with target
        ax2 = plt.subplot(3, 3, 2)
        pathway_emissions = []
        
        for year in self.years:
            year_abatement = self.results_df[self.results_df['Year'] == year]['AbatementMtCO2'].sum()
            remaining_emissions = self.baseline_emissions - year_abatement
            pathway_emissions.append(remaining_emissions)
        
        ax2.plot(self.years, pathway_emissions, 'b-', linewidth=3, label='Optimized Pathway')
        ax2.axhline(y=self.emission_target, color='r', linestyle='--', linewidth=2, 
                   label=f'Target: {self.emission_target} Mt CO₂')
        ax2.axhline(y=self.baseline_emissions, color='gray', linestyle=':', 
                   label=f'Baseline: {self.baseline_emissions} Mt CO₂')
        
        ax2.set_title('Optimized Emission Pathway', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Emissions (Mt CO₂)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Cost breakdown by technology
        ax3 = plt.subplot(3, 3, 3)
        target_year_costs = self.results_df[self.results_df['Year'] == self.target_year].copy()
        target_year_costs = target_year_costs.sort_values('CostPerTonCO2')
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(target_year_costs)))
        bars = ax3.bar(range(len(target_year_costs)), target_year_costs['CostPerTonCO2'], 
                      color=colors, alpha=0.8)
        
        ax3.set_title(f'Technology Costs ({self.target_year})', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Technology')
        ax3.set_ylabel('Cost (USD/tCO₂)')
        ax3.set_xticks(range(len(target_year_costs)))
        ax3.set_xticklabels(target_year_costs['TechID'], rotation=45, ha='right')
        
        # 4. Facility transitions by company
        ax4 = plt.subplot(3, 3, 4)
        company_transitions = self.facility_transitions_df.groupby('Company')['AbatementMtCO2'].sum().sort_values(ascending=False)
        top_companies = company_transitions.head(10)
        
        bars = ax4.bar(range(len(top_companies)), top_companies.values, alpha=0.8)
        ax4.set_title('Top 10 Companies by Abatement', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Company')
        ax4.set_ylabel('Abatement (Mt CO₂)')
        ax4.set_xticks(range(len(top_companies)))
        ax4.set_xticklabels(top_companies.index, rotation=45, ha='right')
        
        # 5. Cost-effectiveness by company
        ax5 = plt.subplot(3, 3, 5)
        top_cost_effective = self.company_analysis_df.head(10)
        
        bars = ax5.bar(range(len(top_cost_effective)), top_cost_effective['CostEffectiveness_USD_per_tCO2'], 
                      alpha=0.8, color='lightcoral')
        ax5.set_title('Most Cost-Effective Companies', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Company')
        ax5.set_ylabel('Cost-Effectiveness (USD/tCO₂)')
        ax5.set_xticks(range(len(top_cost_effective)))
        ax5.set_xticklabels(top_cost_effective['Company'], rotation=45, ha='right')
        
        # 6. Technology readiness vs deployment
        ax6 = plt.subplot(3, 3, 6)
        tech_deployment = self.results_df[self.results_df['Year'] == self.target_year].copy()
        
        scatter = ax6.scatter(tech_deployment['TRL'], tech_deployment['DeploymentLevel'], 
                            s=tech_deployment['AbatementMtCO2']*100, 
                            c=tech_deployment['CostPerTonCO2'], cmap='RdYlGn_r', alpha=0.7)
        
        ax6.set_title('Technology Readiness vs Deployment', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Technology Readiness Level (TRL)')
        ax6.set_ylabel('Deployment Level')
        plt.colorbar(scatter, ax=ax6, label='Cost (USD/tCO₂)')
        
        # 7. Product category abatement
        ax7 = plt.subplot(3, 3, 7)
        product_abatement = self.results_df[self.results_df['Year'] == self.target_year].groupby('Product')['AbatementMtCO2'].sum()
        
        wedges, texts, autotexts = ax7.pie(product_abatement.values, labels=product_abatement.index, 
                                          autopct='%1.1f%%', startangle=90)
        ax7.set_title('Abatement by Product Category', fontsize=12, fontweight='bold')
        
        # 8. Cumulative cost curve
        ax8 = plt.subplot(3, 3, 8)
        cost_curve_data = self.results_df[self.results_df['Year'] == self.target_year].copy()
        cost_curve_data = cost_curve_data.sort_values('CostPerTonCO2')
        cost_curve_data['CumulativeAbatement'] = cost_curve_data['AbatementMtCO2'].cumsum()
        
        ax8.step(cost_curve_data['CumulativeAbatement'], cost_curve_data['CostPerTonCO2'], 
                where='post', linewidth=2)
        ax8.fill_between(cost_curve_data['CumulativeAbatement'], cost_curve_data['CostPerTonCO2'], 
                        step='post', alpha=0.3)
        
        ax8.set_title('Marginal Abatement Cost Curve', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Cumulative Abatement (Mt CO₂)')
        ax8.set_ylabel('Marginal Cost (USD/tCO₂)')
        ax8.grid(True, alpha=0.3)
        
        # 9. Facility age vs transition priority
        ax9 = plt.subplot(3, 3, 9)
        
        scatter = ax9.scatter(self.facility_transitions_df['FacilityAge'], 
                            self.facility_transitions_df['TransitionFraction'],
                            s=self.facility_transitions_df['CapacityTransitioned_kt']/10,
                            c=self.facility_transitions_df['CostPerTonCO2'],
                            cmap='RdYlGn_r', alpha=0.7)
        
        ax9.set_title('Facility Age vs Transition Priority', fontsize=12, fontweight='bold')
        ax9.set_xlabel('Facility Age (years)')
        ax9.set_ylabel('Transition Fraction')
        plt.colorbar(scatter, ax=ax9, label='Cost (USD/tCO₂)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "optimization_results_comprehensive.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Optimization visualizations complete")
    
    def save_optimization_results(self):
        """Save all optimization results to files"""
        
        print("\n💾 Saving optimization results...")
        
        # Technology deployment results
        self.results_df.to_csv(self.output_dir / "optimization_technology_deployments.csv", index=False)
        
        # Facility transition results
        self.facility_transitions_df.to_csv(self.output_dir / "optimization_facility_transitions.csv", index=False)
        
        # Company cost-effectiveness analysis
        self.company_analysis_df.to_csv(self.output_dir / "optimization_company_analysis.csv", index=False)
        
        # Summary results
        summary = {
            'Target_Year': self.target_year,
            'Emission_Target_Mt_CO2': self.emission_target,
            'Baseline_Emissions_Mt_CO2': self.baseline_emissions,
            'Required_Abatement_Mt_CO2': self.baseline_emissions - self.emission_target,
            'Total_Optimization_Cost_USD': self.total_optimization_cost,
            'Technologies_Deployed': len(self.results_df['TechID'].unique()),
            'Facilities_Transitioned': len(self.facility_transitions_df),
            'Companies_Affected': len(self.company_analysis_df),
            'Average_Cost_Effectiveness_USD_per_tCO2': self.total_optimization_cost / ((self.baseline_emissions - self.emission_target) * 1_000_000)
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / "optimization_summary.csv", index=False)
        
        print("✅ All results saved to outputs directory")
        
        return summary
    
    def run_optimization_analysis(self, target_year=2030, emission_target_mt=26.0):
        """Run complete optimization analysis"""
        
        print("🚀 Starting MACC optimization analysis...")
        print(f"🎯 Target: {emission_target_mt} Mt CO₂ by {target_year}")
        print(f"📊 Baseline: {self.baseline_emissions} Mt CO₂")
        print(f"🔽 Required reduction: {self.baseline_emissions - emission_target_mt:.1f} Mt CO₂ ({(self.baseline_emissions - emission_target_mt)/self.baseline_emissions*100:.1f}%)")
        
        # 1. Setup and solve optimization
        self.setup_optimization_problem(target_year, emission_target_mt)
        results_df = self.solve_optimization()
        
        if results_df is None:
            return None
        
        # 2. Analyze facility transitions
        facility_transitions = self.analyze_facility_transitions()
        
        # 3. Analyze company cost-effectiveness
        company_analysis = self.analyze_company_cost_effectiveness()
        
        # 4. Create visualizations
        self.create_optimization_visualizations()
        
        # 5. Save results
        summary = self.save_optimization_results()
        
        print("\n✅ OPTIMIZATION ANALYSIS COMPLETE")
        print(f"💰 Total cost: ${summary['Total_Optimization_Cost_USD']/1e9:.2f} billion USD")
        print(f"⚡ Cost-effectiveness: ${summary['Average_Cost_Effectiveness_USD_per_tCO2']:.0f}/tCO₂")
        print(f"🏭 Facilities affected: {summary['Facilities_Transitioned']}")
        print(f"🏢 Companies involved: {summary['Companies_Affected']}")
        
        return {
            'technology_deployments': results_df,
            'facility_transitions': facility_transitions,
            'company_analysis': company_analysis,
            'summary': summary
        }

if __name__ == "__main__":
    # Create optimization model
    optimizer = MACCOptimizationModel()
    
    # Run optimization for 50% reduction by 2030 (26 Mt CO₂ target)
    results = optimizer.run_optimization_analysis(target_year=2030, emission_target_mt=26.0)