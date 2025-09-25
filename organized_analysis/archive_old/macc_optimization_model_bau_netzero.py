#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model - BAU Baseline with Linear Net-Zero Pathway
Optimizes emission reduction pathways from BAU baseline to achieve linear reduction to net-zero by 2050
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

class MACCOptimizationBAUNetZero:
    def __init__(self, facility_lifetime='30yr'):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load optimization data
        self.data_file = 'data/korean_petrochemical_macc_optimization.xlsx'
        self.tech_options = pd.read_excel(self.data_file, sheet_name='TechOptions')
        self.macc_template = pd.read_excel(self.data_file, sheet_name='MACC_Template')
        self.baseline_assumptions = pd.read_excel(self.data_file, sheet_name='Baseline_Assumptions')
        self.facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        
        # Load BAU emission pathway based on facility lifetime
        self.facility_lifetime = facility_lifetime
        bau_file = f"outputs/bau_emission_pathway_{facility_lifetime}_final.csv"
        self.bau_pathway = pd.read_csv(bau_file)
        
        print(f"✓ Using BAU pathway: {facility_lifetime} facility lifetime")
        
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
        
    def calculate_linear_netzero_targets(self):
        """Calculate linear emission reduction targets from 2025 BAU to net-zero 2050"""
        
        # Get BAU baseline for 2025
        bau_2025 = self.bau_pathway[self.bau_pathway['year'] == 2025]['emissions_mt_co2'].iloc[0]
        
        # Calculate linear reduction pathway
        years = list(range(2025, 2051))  # 2025 to 2050
        netzero_targets = {}
        
        for year in years:
            # Linear interpolation from BAU_2025 to 0 in 2050
            progress = (year - 2025) / (2050 - 2025)  # 0 to 1 progress
            target_emissions = bau_2025 * (1 - progress)  # Linear decrease to 0
            netzero_targets[year] = target_emissions
        
        self.netzero_targets = netzero_targets
        self.bau_2025_baseline = bau_2025
        
        print(f"✓ BAU 2025 baseline: {bau_2025:.1f} Mt CO₂")
        print(f"✓ Linear net-zero pathway: {bau_2025:.1f} Mt (2025) → 0.0 Mt (2050)")
        
        return netzero_targets
    
    def setup_optimization_problem(self, planning_horizon=2050):
        """Setup optimization problem for linear net-zero pathway"""
        
        print(f"\n🎯 Setting up optimization for linear net-zero pathway (2025-{planning_horizon})")
        
        # Calculate targets
        self.calculate_linear_netzero_targets()
        
        # Years from 2025 to planning horizon
        years = list(range(2025, planning_horizon + 1))
        
        # Get available technologies
        available_techs = self.tech_data.copy()
        
        print(f"✓ Planning horizon: 2025-{planning_horizon}")
        print(f"✓ Available technologies: {len(available_techs)}")
        
        # Create optimization problem
        prob = LpProblem("MACC_BAU_NetZero_Optimization", LpMinimize)
        
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
        
        # Objective: Minimize total cost over entire planning horizon
        total_cost = 0
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in years:
                if year >= tech['StartYear_Commercial'] and (tech_id, year) in deployment_vars:
                    # Apply discount factor (3% annual discount rate)
                    discount_factor = 1 / (1.03 ** (year - 2025))
                    annual_cost = (deployment_vars[(tech_id, year)] * 
                                 abatement_potential * cost_per_tco2 * 1_000_000 * discount_factor)
                    total_cost += annual_cost
        
        prob += total_cost
        
        # Constraint 1: Meet emission targets for each year
        for year in years:
            # Get BAU emissions for this year
            bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
            target_emissions = self.netzero_targets[year]
            required_abatement = bau_emissions - target_emissions
            
            # Sum of abatement from all technologies
            year_abatement = 0
            for _, tech in available_techs.iterrows():
                tech_id = tech['TechID']
                if (tech_id, year) in deployment_vars:
                    abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
                    year_abatement += (deployment_vars[(tech_id, year)] * abatement_potential)
            
            prob += year_abatement >= required_abatement, f"EmissionTarget_{year}"
        
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
                        discount_factor = 1 / (1.03 ** (year - 2025))
                        annual_cost = annual_abatement * cost_per_tco2 * 1_000_000 * discount_factor
                        total_cost += annual_cost
                        
                        # Calculate emissions after abatement
                        bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
                        target_emissions = self.netzero_targets[year]
                        
                        results.append({
                            'TechID': tech_id,
                            'Product': product,
                            'Year': year,
                            'DeploymentLevel': deployment_level,
                            'AbatementMtCO2': annual_abatement,
                            'AnnualCostUSD': annual_cost / discount_factor,  # Undiscounted cost
                            'DiscountedCostUSD': annual_cost,
                            'CostPerTonCO2': cost_per_tco2,
                            'StartYear_Commercial': tech['StartYear_Commercial'],
                            'TRL': tech['TRL'],
                            'BAU_Emissions': bau_emissions,
                            'Target_Emissions': target_emissions
                        })
        
        self.results_df = pd.DataFrame(results)
        self.total_optimization_cost = total_cost
        
        print(f"✓ Total discounted optimization cost: ${total_cost/1e9:.2f} billion USD")
        print(f"✓ Deployed technologies: {len(self.results_df['TechID'].unique())}")
        
        return self.results_df
    
    def create_emission_pathway_analysis(self):
        """Create optimized emission pathway vs BAU and targets"""
        
        print("\n📈 Creating emission pathway analysis...")
        
        # Calculate optimized emission pathway
        optimized_pathway = []
        
        for year in self.years:
            # BAU emissions for this year
            bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
            
            # Total abatement from optimization
            year_abatement = self.results_df[self.results_df['Year'] == year]['AbatementMtCO2'].sum()
            
            # Optimized emissions
            optimized_emissions = bau_emissions - year_abatement
            
            # Target emissions
            target_emissions = self.netzero_targets[year]
            
            optimized_pathway.append({
                'Year': year,
                'BAU_Emissions_Mt': bau_emissions,
                'Target_Emissions_Mt': target_emissions,
                'Optimized_Emissions_Mt': optimized_emissions,
                'Total_Abatement_Mt': year_abatement,
                'AbatementGap_Mt': max(0, optimized_emissions - target_emissions)
            })
        
        self.pathway_df = pd.DataFrame(optimized_pathway)
        
        # Save pathway analysis
        self.pathway_df.to_csv(self.output_dir / f"optimized_emission_pathway_{self.facility_lifetime}_netzero.csv", index=False)
        
        return self.pathway_df
    
    def analyze_facility_transitions(self):
        """Analyze facility-level transitions with timeline"""
        
        print("\n🏭 Analyzing facility-level transitions...")
        
        facility_transitions = []
        
        # Get unique technologies and their deployment years
        tech_deployments = self.results_df.groupby('TechID').agg({
            'Year': ['min', 'max'],
            'DeploymentLevel': 'mean',
            'Product': 'first'
        }).reset_index()
        
        tech_deployments.columns = ['TechID', 'StartYear', 'EndYear', 'AvgDeployment', 'Product']
        
        for _, deployment in tech_deployments.iterrows():
            tech_id = deployment['TechID']
            product = deployment['Product']
            avg_deployment = deployment['AvgDeployment']
            
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
            
            # Sort facilities by emission intensity and age (prioritize older, high-intensity facilities)
            eligible_facilities['facility_age_2025'] = 2025 - eligible_facilities['start_year']
            eligible_facilities = eligible_facilities.sort_values(
                ['emission_intensity_t_co2_per_t', 'facility_age_2025'], ascending=[False, False]
            )
            
            # Calculate facilities to transition
            total_capacity = eligible_facilities['capacity_kt'].sum()
            target_capacity = total_capacity * avg_deployment
            
            cumulative_capacity = 0
            
            for _, facility in eligible_facilities.iterrows():
                if cumulative_capacity < target_capacity:
                    facility_capacity = facility['capacity_kt']
                    remaining_capacity = target_capacity - cumulative_capacity
                    
                    if facility_capacity <= remaining_capacity:
                        transition_fraction = 1.0
                        capacity_transitioned = facility_capacity
                    else:
                        transition_fraction = remaining_capacity / facility_capacity
                        capacity_transitioned = remaining_capacity
                    
                    # Get technology cost and abatement
                    tech_data = self.results_df[self.results_df['TechID'] == tech_id].iloc[0]
                    
                    # Calculate annual emissions and cost savings
                    annual_emissions_before = facility['annual_emissions_kt_co2'] * transition_fraction
                    abatement_fraction = tech_data['AbatementMtCO2'] / 52.0  # Approximate abatement rate
                    annual_emissions_after = annual_emissions_before * (1 - abatement_fraction)
                    annual_abatement = (annual_emissions_before - annual_emissions_after) / 1000  # Convert to Mt
                    annual_cost = annual_abatement * tech_data['CostPerTonCO2'] * 1_000_000
                    
                    facility_transitions.append({
                        'FacilityID': facility['facility_id'],
                        'Company': facility['company'],
                        'Location': facility['location'],
                        'Product': facility['product'],
                        'TechID': tech_id,
                        'TransitionYear': deployment['StartYear'],
                        'TransitionFraction': transition_fraction,
                        'CapacityTransitioned_kt': capacity_transitioned,
                        'EmissionsBefore_ktCO2': annual_emissions_before,
                        'EmissionsAfter_ktCO2': annual_emissions_after,
                        'AbatementMtCO2': annual_abatement,
                        'AnnualCostUSD': annual_cost,
                        'CostPerTonCO2': tech_data['CostPerTonCO2'],
                        'FacilityAge_2025': facility['facility_age_2025'],
                        'EmissionIntensity': facility['emission_intensity_t_co2_per_t']
                    })
                    
                    cumulative_capacity += capacity_transitioned
                    
                    if cumulative_capacity >= target_capacity:
                        break
        
        self.facility_transitions_df = pd.DataFrame(facility_transitions)
        
        print(f"✓ Facility transitions identified: {len(self.facility_transitions_df)}")
        
        return self.facility_transitions_df
    
    def create_comprehensive_visualizations(self):
        """Create comprehensive visualization dashboard"""
        
        print("\n📊 Creating comprehensive visualizations...")
        
        # Create large figure with multiple subplots
        fig = plt.figure(figsize=(24, 20))
        
        # 1. Emission pathway comparison (top large panel)
        ax1 = plt.subplot(3, 4, (1, 2))
        
        years = self.pathway_df['Year']
        ax1.plot(years, self.pathway_df['BAU_Emissions_Mt'], 'r-', linewidth=3, 
                label=f'BAU ({self.facility_lifetime})', alpha=0.8)
        ax1.plot(years, self.pathway_df['Target_Emissions_Mt'], 'g--', linewidth=3, 
                label='Linear Net-Zero Target', alpha=0.9)
        ax1.plot(years, self.pathway_df['Optimized_Emissions_Mt'], 'b-', linewidth=3, 
                label='Optimized Pathway', alpha=0.9)
        ax1.fill_between(years, self.pathway_df['BAU_Emissions_Mt'], 
                        self.pathway_df['Optimized_Emissions_Mt'], alpha=0.3, color='blue', 
                        label='Abatement')
        
        ax1.set_title('Optimized Emission Pathway vs BAU and Net-Zero Targets', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (Mt CO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(2025, 2050)
        
        # 2. Technology deployment timeline
        ax2 = plt.subplot(3, 4, (3, 4))
        
        # Pivot deployment data
        deployment_pivot = self.results_df.pivot_table(
            values='DeploymentLevel', index='Year', columns='TechID', fill_value=0
        )
        
        # Create stacked area plot
        ax2.stackplot(deployment_pivot.index, *[deployment_pivot[col] for col in deployment_pivot.columns], 
                     labels=deployment_pivot.columns, alpha=0.8)
        
        ax2.set_title('Technology Deployment Timeline', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Deployment Level')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Cumulative cost analysis
        ax3 = plt.subplot(3, 4, 5)
        
        cost_by_year = self.results_df.groupby('Year')['AnnualCostUSD'].sum() / 1e9
        cumulative_cost = cost_by_year.cumsum()
        
        ax3.bar(cost_by_year.index, cost_by_year.values, alpha=0.7, color='coral')
        ax3_twin = ax3.twinx()
        ax3_twin.plot(cumulative_cost.index, cumulative_cost.values, 'b-', linewidth=2, marker='o')
        
        ax3.set_title('Annual & Cumulative Costs', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Annual Cost (B USD)', color='coral')
        ax3_twin.set_ylabel('Cumulative Cost (B USD)', color='blue')
        
        # 4. Technology cost effectiveness
        ax4 = plt.subplot(3, 4, 6)
        
        tech_summary = self.results_df.groupby('TechID').agg({
            'AbatementMtCO2': 'sum',
            'CostPerTonCO2': 'mean'
        }).reset_index()
        tech_summary = tech_summary.sort_values('CostPerTonCO2')
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(tech_summary)))
        bars = ax4.barh(range(len(tech_summary)), tech_summary['CostPerTonCO2'], 
                       color=colors, alpha=0.8)
        
        ax4.set_title('Technology Cost-Effectiveness', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Cost (USD/tCO₂)')
        ax4.set_yticks(range(len(tech_summary)))
        ax4.set_yticklabels(tech_summary['TechID'], fontsize=8)
        ax4.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        # 5. Abatement by product category
        ax5 = plt.subplot(3, 4, 7)
        
        product_abatement = self.results_df.groupby('Product')['AbatementMtCO2'].sum()
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(product_abatement)))
        
        wedges, texts, autotexts = ax5.pie(product_abatement.values, labels=product_abatement.index, 
                                          autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax5.set_title('Abatement by Product Category', fontsize=12, fontweight='bold')
        
        # 6. Facility transition timeline
        ax6 = plt.subplot(3, 4, 8)
        
        transition_timeline = self.facility_transitions_df.groupby('TransitionYear').agg({
            'CapacityTransitioned_kt': 'sum',
            'AbatementMtCO2': 'sum'
        }).reset_index()
        
        ax6.bar(transition_timeline['TransitionYear'], transition_timeline['CapacityTransitioned_kt'], 
               alpha=0.7, color='lightgreen')
        ax6_twin = ax6.twinx()
        ax6_twin.plot(transition_timeline['TransitionYear'], transition_timeline['AbatementMtCO2'], 
                     'ro-', linewidth=2)
        
        ax6.set_title('Facility Transition Timeline', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Year')
        ax6.set_ylabel('Capacity (kt)', color='green')
        ax6_twin.set_ylabel('Abatement (Mt CO₂)', color='red')
        
        # 7. Company analysis
        ax7 = plt.subplot(3, 4, 9)
        
        company_analysis = self.facility_transitions_df.groupby('Company')['AbatementMtCO2'].sum().sort_values(ascending=False)
        top_companies = company_analysis.head(10)
        
        bars = ax7.bar(range(len(top_companies)), top_companies.values, alpha=0.8)
        ax7.set_title('Top 10 Companies by Abatement', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Company')
        ax7.set_ylabel('Abatement (Mt CO₂)')
        ax7.set_xticks(range(len(top_companies)))
        ax7.set_xticklabels(top_companies.index, rotation=45, ha='right', fontsize=8)
        
        # 8. MACC curve
        ax8 = plt.subplot(3, 4, 10)
        
        macc_data = tech_summary.copy()
        macc_data['CumulativeAbatement'] = macc_data['AbatementMtCO2'].cumsum()
        
        ax8.step(macc_data['CumulativeAbatement'], macc_data['CostPerTonCO2'], 
                where='post', linewidth=2)
        ax8.fill_between(macc_data['CumulativeAbatement'], macc_data['CostPerTonCO2'], 
                        step='post', alpha=0.3)
        
        ax8.set_title('Marginal Abatement Cost Curve', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Cumulative Abatement (Mt CO₂)')
        ax8.set_ylabel('Marginal Cost (USD/tCO₂)')
        ax8.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax8.grid(True, alpha=0.3)
        
        # 9. Target achievement analysis
        ax9 = plt.subplot(3, 4, 11)
        
        target_analysis = self.pathway_df.copy()
        target_analysis['Achievement_%'] = (1 - target_analysis['AbatementGap_Mt'] / 
                                          target_analysis['Target_Emissions_Mt'].replace(0, np.nan)) * 100
        target_analysis['Achievement_%'] = target_analysis['Achievement_%'].fillna(100)
        
        ax9.plot(target_analysis['Year'], target_analysis['Achievement_%'], 'go-', linewidth=2)
        ax9.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Target')
        ax9.fill_between(target_analysis['Year'], 0, target_analysis['Achievement_%'], 
                        alpha=0.3, color='green')
        
        ax9.set_title('Target Achievement Progress', fontsize=12, fontweight='bold')
        ax9.set_xlabel('Year')
        ax9.set_ylabel('Target Achievement (%)')
        ax9.set_ylim(0, 110)
        ax9.legend()
        ax9.grid(True, alpha=0.3)
        
        # 10. Investment breakdown
        ax10 = plt.subplot(3, 4, 12)
        
        investment_breakdown = self.results_df.groupby('TechID')['AnnualCostUSD'].sum() / 1e9
        investment_breakdown = investment_breakdown.sort_values()
        
        colors_inv = ['red' if x < 0 else 'blue' for x in investment_breakdown.values]
        bars = ax10.barh(range(len(investment_breakdown)), investment_breakdown.values, 
                        color=colors_inv, alpha=0.7)
        
        ax10.set_title('Total Investment by Technology', fontsize=12, fontweight='bold')
        ax10.set_xlabel('Total Investment (B USD)')
        ax10.set_yticks(range(len(investment_breakdown)))
        ax10.set_yticklabels(investment_breakdown.index, fontsize=8)
        ax10.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_comprehensive.png", 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Comprehensive visualizations complete")
    
    def save_optimization_results(self):
        """Save all optimization results to files"""
        
        print("\n💾 Saving optimization results...")
        
        # Technology deployment results
        self.results_df.to_csv(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_deployments.csv", index=False)
        
        # Facility transition results
        self.facility_transitions_df.to_csv(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_transitions.csv", index=False)
        
        # Emission pathway results
        self.pathway_df.to_csv(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_pathway.csv", index=False)
        
        # Company analysis
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
        
        company_analysis.to_csv(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_companies.csv", index=False)
        
        # Summary results
        total_abatement = self.results_df['AbatementMtCO2'].sum()
        total_cost = self.results_df['AnnualCostUSD'].sum()
        
        # Calculate key milestones
        milestone_2030 = self.pathway_df[self.pathway_df['Year'] == 2030].iloc[0]
        milestone_2040 = self.pathway_df[self.pathway_df['Year'] == 2040].iloc[0]
        milestone_2050 = self.pathway_df[self.pathway_df['Year'] == 2050].iloc[0]
        
        summary = {
            'Facility_Lifetime': self.facility_lifetime,
            'BAU_2025_Baseline_Mt_CO2': self.bau_2025_baseline,
            'Total_Abatement_Mt_CO2': total_abatement,
            'Total_Cost_USD': total_cost,
            'Total_Discounted_Cost_USD': self.total_optimization_cost,
            'Technologies_Deployed': len(self.results_df['TechID'].unique()),
            'Facilities_Transitioned': len(self.facility_transitions_df),
            'Companies_Affected': len(self.facility_transitions_df['Company'].unique()),
            'Avg_Cost_Effectiveness_USD_per_tCO2': total_cost / (total_abatement * 1000),
            'Emissions_2030_Mt_CO2': milestone_2030['Optimized_Emissions_Mt'],
            'Target_2030_Mt_CO2': milestone_2030['Target_Emissions_Mt'],
            'Achievement_2030_%': (1 - milestone_2030['AbatementGap_Mt'] / milestone_2030['Target_Emissions_Mt']) * 100,
            'Emissions_2040_Mt_CO2': milestone_2040['Optimized_Emissions_Mt'],
            'Target_2040_Mt_CO2': milestone_2040['Target_Emissions_Mt'],
            'Achievement_2040_%': (1 - milestone_2040['AbatementGap_Mt'] / milestone_2040['Target_Emissions_Mt']) * 100,
            'Emissions_2050_Mt_CO2': milestone_2050['Optimized_Emissions_Mt'],
            'Target_2050_Mt_CO2': milestone_2050['Target_Emissions_Mt'],
            'NetZero_Achievement_%': (1 - milestone_2050['AbatementGap_Mt'] / max(0.1, milestone_2050['Target_Emissions_Mt'])) * 100
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / f"optimization_bau_netzero_{self.facility_lifetime}_summary.csv", index=False)
        
        print("✅ All results saved to outputs directory")
        
        return summary
    
    def run_optimization_analysis(self):
        """Run complete BAU to net-zero optimization analysis"""
        
        print("🚀 Starting BAU to Net-Zero MACC optimization analysis...")
        print(f"📊 Facility lifetime: {self.facility_lifetime}")
        
        # 1. Setup and solve optimization
        self.setup_optimization_problem()
        results_df = self.solve_optimization()
        
        if results_df is None:
            return None
        
        # 2. Create emission pathway analysis
        pathway_df = self.create_emission_pathway_analysis()
        
        # 3. Analyze facility transitions
        facility_transitions = self.analyze_facility_transitions()
        
        # 4. Create comprehensive visualizations
        self.create_comprehensive_visualizations()
        
        # 5. Save results
        summary = self.save_optimization_results()
        
        print("\n✅ BAU TO NET-ZERO OPTIMIZATION ANALYSIS COMPLETE")
        print(f"💰 Total cost: ${summary['Total_Cost_USD']/1e9:.2f} billion USD")
        print(f"💰 Discounted cost: ${summary['Total_Discounted_Cost_USD']/1e9:.2f} billion USD")
        print(f"⚡ Cost-effectiveness: ${summary['Avg_Cost_Effectiveness_USD_per_tCO2']:.0f}/tCO₂")
        print(f"🎯 2030 target achievement: {summary['Achievement_2030_%']:.1f}%")
        print(f"🎯 2040 target achievement: {summary['Achievement_2040_%']:.1f}%")
        print(f"🎯 Net-zero achievement: {summary['NetZero_Achievement_%']:.1f}%")
        print(f"🏭 Facilities affected: {summary['Facilities_Transitioned']}")
        print(f"🏢 Companies involved: {summary['Companies_Affected']}")
        
        return {
            'technology_deployments': results_df,
            'emission_pathway': pathway_df,
            'facility_transitions': facility_transitions,
            'summary': summary
        }

if __name__ == "__main__":
    # Test with different facility lifetime scenarios
    for lifetime in ['25yr', '30yr', '40yr', '50yr']:
        print(f"\n{'='*60}")
        print(f"OPTIMIZING FOR {lifetime.upper()} FACILITY LIFETIME")
        print(f"{'='*60}")
        
        # Create optimization model
        optimizer = MACCOptimizationBAUNetZero(facility_lifetime=lifetime)
        
        # Run optimization
        results = optimizer.run_optimization_analysis()
        
        if results:
            print(f"✅ {lifetime} optimization completed successfully")
        else:
            print(f"❌ {lifetime} optimization failed")
        
        print(f"{'='*60}\n")