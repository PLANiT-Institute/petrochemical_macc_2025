#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model
Using 50yr BAU baseline with Emissions_Target sheet constraints
"""

import pandas as pd
import numpy as np
from pulp import *
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set font support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MACCOptimizationTargetSheet:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load optimization data
        self.data_file = 'data/korean_petrochemical_macc_optimization.xlsx'
        self.tech_options = pd.read_excel(self.data_file, sheet_name='TechOptions')
        self.macc_template = pd.read_excel(self.data_file, sheet_name='MACC_Template')
        self.baseline_assumptions = pd.read_excel(self.data_file, sheet_name='Baseline_Assumptions')
        self.facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        
        # Load BAU emission pathway (50yr facility lifetime)
        self.bau_pathway = pd.read_csv("outputs/bau_emission_pathway_50yr_final.csv")
        
        # Load emission targets from sheet
        self.emission_targets = pd.read_excel(self.data_file, sheet_name='Emissions_Target')
        
        # Merge technology data
        tech_cols = ['TechID', 'Product', 'StartYear_Commercial', 'MaxPenetration', 'RampUpSharePerYear']
        self.tech_data = self.macc_template.merge(
            self.tech_options[tech_cols], 
            on='TechID'
        )
        # Use TRL from MACC_Template
        if 'TRL_x' in self.tech_data.columns:
            self.tech_data['TRL'] = self.tech_data['TRL_x']
        
        print(f"✓ Loaded optimization data: {len(self.tech_data)} technologies")
        print(f"✓ Using 50yr BAU pathway baseline")
        print(f"✓ Loaded emission targets: {len(self.emission_targets)} target years")
        
    def prepare_targets_and_bau(self):
        """Prepare emission targets and BAU pathway alignment"""
        
        print("\n📊 Preparing targets and BAU pathway...")
        
        # Display targets
        print("Emission Targets from sheet:")
        for _, target in self.emission_targets.iterrows():
            print(f"  {target['Year']}: {target['Target_MtCO2e']:.1f} Mt CO₂ ({target['Source']})")
        
        # Get BAU emissions for target years
        target_years = self.emission_targets['Year'].tolist()
        bau_comparison = []
        
        for year in target_years:
            if year in self.bau_pathway['year'].values:
                bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
                target_emissions = self.emission_targets[self.emission_targets['Year'] == year]['Target_MtCO2e'].iloc[0]
                required_abatement = bau_emissions - target_emissions
                
                bau_comparison.append({
                    'Year': year,
                    'BAU_Emissions': bau_emissions,
                    'Target_Emissions': target_emissions,
                    'Required_Abatement': required_abatement,
                    'Reduction_Percent': (required_abatement / bau_emissions) * 100 if bau_emissions > 0 else 0
                })
            else:
                print(f"⚠️  Warning: BAU data not available for target year {year}")
        
        self.target_comparison_df = pd.DataFrame(bau_comparison)
        
        print("\nBAU vs Target Comparison:")
        print(self.target_comparison_df.round(1))
        
        return self.target_comparison_df
    
    def setup_optimization_problem(self):
        """Setup optimization problem with emission target constraints"""
        
        print("\n🎯 Setting up optimization with emission target constraints...")
        
        # Prepare targets
        self.prepare_targets_and_bau()
        
        # Target years only (not all years 2025-2050)
        target_years = self.emission_targets['Year'].tolist()
        
        # Get available technologies
        available_techs = self.tech_data.copy()
        
        print(f"✓ Target years: {target_years}")
        print(f"✓ Available technologies: {len(available_techs)}")
        
        # Create optimization problem
        prob = LpProblem("MACC_EmissionTargets_Optimization", LpMinimize)
        
        # Decision variables: deployment level for each technology and target year
        deployment_vars = {}
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            for year in target_years:
                if year >= tech['StartYear_Commercial']:
                    var_name = f"deploy_{tech_id}_{year}"
                    deployment_vars[(tech_id, year)] = LpVariable(
                        var_name, 
                        lowBound=0, 
                        upBound=tech['MaxPenetration'],
                        cat='Continuous'
                    )
        
        # Objective: Minimize total cost across all target years
        total_cost = 0
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in target_years:
                if year >= tech['StartYear_Commercial'] and (tech_id, year) in deployment_vars:
                    # Apply discount factor based on year
                    discount_factor = 1 / (1.03 ** (year - 2025))
                    annual_cost = (deployment_vars[(tech_id, year)] * 
                                 abatement_potential * cost_per_tco2 * 1_000_000 * discount_factor)
                    total_cost += annual_cost
        
        prob += total_cost
        
        # Constraint 1: Meet emission targets for each year
        for year in target_years:
            # Get BAU and target for this year
            year_data = self.target_comparison_df[self.target_comparison_df['Year'] == year].iloc[0]
            required_abatement = year_data['Required_Abatement']
            
            # Sum of abatement from all technologies
            year_abatement = 0
            for _, tech in available_techs.iterrows():
                tech_id = tech['TechID']
                if (tech_id, year) in deployment_vars:
                    abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
                    year_abatement += (deployment_vars[(tech_id, year)] * abatement_potential)
            
            prob += year_abatement >= required_abatement, f"EmissionTarget_{year}"
            print(f"✓ Constraint added: {required_abatement:.1f} Mt CO₂ abatement required in {year}")
        
        # Constraint 2: Technology ramp-up between consecutive target years
        sorted_years = sorted(target_years)
        for i in range(1, len(sorted_years)):
            prev_year = sorted_years[i-1]
            curr_year = sorted_years[i]
            year_gap = curr_year - prev_year
            
            for _, tech in available_techs.iterrows():
                tech_id = tech['TechID']
                ramp_rate = tech['RampUpSharePerYear']
                max_increase = ramp_rate * year_gap  # Allow for multi-year gaps
                
                if ((tech_id, prev_year) in deployment_vars and 
                    (tech_id, curr_year) in deployment_vars):
                    prob += (deployment_vars[(tech_id, curr_year)] <= 
                           deployment_vars[(tech_id, prev_year)] + max_increase), f"RampUp_{tech_id}_{prev_year}_{curr_year}"
        
        # Constraint 3: Technology competition within products
        product_groups = available_techs.groupby('Product')
        for product, product_techs in product_groups:
            if len(product_techs) > 1 and product != 'All_Products':  # Multiple competing technologies
                for year in target_years:
                    total_penetration = 0
                    for _, tech in product_techs.iterrows():
                        tech_id = tech['TechID']
                        if (tech_id, year) in deployment_vars:
                            total_penetration += deployment_vars[(tech_id, year)]
                    
                    prob += total_penetration <= 1.0, f"ProductCompetition_{product}_{year}"
        
        self.prob = prob
        self.deployment_vars = deployment_vars
        self.available_techs = available_techs
        self.target_years = target_years
        
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
            
            for year in self.target_years:
                if (tech_id, year) in self.deployment_vars:
                    deployment_level = self.deployment_vars[(tech_id, year)].varValue or 0
                    
                    if deployment_level > 0.001:  # Only record significant deployments
                        annual_abatement = deployment_level * abatement_potential
                        discount_factor = 1 / (1.03 ** (year - 2025))
                        annual_cost = annual_abatement * cost_per_tco2 * 1_000_000 * discount_factor
                        total_cost += annual_cost
                        
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
                            'TRL': tech['TRL']
                        })
        
        self.results_df = pd.DataFrame(results)
        self.total_optimization_cost = total_cost
        
        print(f"✓ Total discounted optimization cost: ${total_cost/1e9:.2f} billion USD")
        print(f"✓ Deployed technologies: {len(self.results_df['TechID'].unique())}")
        
        return self.results_df
    
    def create_results_analysis(self):
        """Create comprehensive results analysis"""
        
        print("\n📈 Creating results analysis...")
        
        # Calculate achievement for each target year
        achievement_analysis = []
        
        for year in self.target_years:
            # Get target data
            year_target_data = self.target_comparison_df[self.target_comparison_df['Year'] == year].iloc[0]
            
            # Get achieved abatement
            year_abatement = self.results_df[self.results_df['Year'] == year]['AbatementMtCO2'].sum()
            
            # Calculate final emissions
            bau_emissions = year_target_data['BAU_Emissions']
            target_emissions = year_target_data['Target_Emissions']
            optimized_emissions = bau_emissions - year_abatement
            
            # Achievement metrics
            required_abatement = year_target_data['Required_Abatement']
            achievement_pct = (year_abatement / required_abatement * 100) if required_abatement > 0 else 100
            target_compliance = optimized_emissions <= target_emissions
            
            achievement_analysis.append({
                'Year': year,
                'BAU_Emissions': bau_emissions,
                'Target_Emissions': target_emissions,
                'Required_Abatement': required_abatement,
                'Achieved_Abatement': year_abatement,
                'Optimized_Emissions': optimized_emissions,
                'Achievement_Percent': achievement_pct,
                'Target_Compliance': target_compliance,
                'Emission_Gap': optimized_emissions - target_emissions
            })
        
        self.achievement_df = pd.DataFrame(achievement_analysis)
        
        print("Target Achievement Analysis:")
        print(self.achievement_df.round(2))
        
        return self.achievement_df
    
    def analyze_facility_transitions(self):
        """Analyze facility-level transitions for target years"""
        
        print("\n🏭 Analyzing facility transitions...")
        
        facility_transitions = []
        
        # Group by technology and analyze facility impact
        tech_deployments = self.results_df.groupby('TechID').agg({
            'DeploymentLevel': 'mean',
            'Product': 'first',
            'Year': ['min', 'max'],
            'AbatementMtCO2': 'mean'
        }).reset_index()
        
        # Flatten column names
        tech_deployments.columns = ['TechID', 'AvgDeployment', 'Product', 'StartYear', 'EndYear', 'AvgAbatement']
        
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
            
            # Sort facilities by emission intensity (prioritize high emitters for transitions)
            eligible_facilities = eligible_facilities.sort_values(
                'emission_intensity_t_co2_per_t', ascending=False
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
                    
                    # Get technology cost and abatement data
                    tech_data = self.results_df[self.results_df['TechID'] == tech_id].iloc[0]
                    
                    # Calculate impact
                    annual_emissions_before = facility['annual_emissions_kt_co2'] * transition_fraction
                    abatement_rate = deployment['AvgAbatement'] / 52.0  # Approximate abatement rate
                    annual_emissions_after = annual_emissions_before * (1 - abatement_rate)
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
                        'FacilityAge_2025': 2025 - facility['start_year'],
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
        
        # Create large figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Emission pathway with targets (large top panel)
        ax1 = plt.subplot(3, 3, (1, 3))
        
        years = self.achievement_df['Year']
        ax1.plot(years, self.achievement_df['BAU_Emissions'], 'r-', linewidth=3, 
                label='BAU (50yr lifetime)', marker='o', markersize=8)
        ax1.plot(years, self.achievement_df['Target_Emissions'], 'g--', linewidth=3, 
                label='Emission Targets', marker='s', markersize=8)
        ax1.plot(years, self.achievement_df['Optimized_Emissions'], 'b-', linewidth=3, 
                label='Optimized Pathway', marker='^', markersize=8)
        
        # Fill area showing abatement
        ax1.fill_between(years, self.achievement_df['BAU_Emissions'], 
                        self.achievement_df['Optimized_Emissions'], alpha=0.3, color='blue', 
                        label='Abatement Achieved')
        
        ax1.set_title('Emission Pathway: BAU vs Targets vs Optimized (50yr Facility Lifetime)', 
                     fontsize=16, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Emissions (Mt CO₂)', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(2024, 2051)
        
        # 2. Technology deployment by year
        ax2 = plt.subplot(3, 3, 4)
        
        tech_deployment = self.results_df.pivot_table(
            values='DeploymentLevel', index='Year', columns='TechID', fill_value=0
        )
        
        bottom = np.zeros(len(tech_deployment.index))
        colors = plt.cm.Set3(np.linspace(0, 1, len(tech_deployment.columns)))
        
        for i, tech_id in enumerate(tech_deployment.columns):
            ax2.bar(tech_deployment.index, tech_deployment[tech_id], 
                   bottom=bottom, label=tech_id, color=colors[i], alpha=0.8)
            bottom += tech_deployment[tech_id]
        
        ax2.set_title('Technology Deployment by Year', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Deployment Level')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        
        # 3. Cost breakdown by technology
        ax3 = plt.subplot(3, 3, 5)
        
        tech_costs = self.results_df.groupby('TechID').agg({
            'AnnualCostUSD': 'sum',
            'CostPerTonCO2': 'first'
        }).reset_index()
        tech_costs = tech_costs.sort_values('CostPerTonCO2')
        
        colors_cost = ['red' if x < 0 else 'blue' for x in tech_costs['CostPerTonCO2']]
        bars = ax3.barh(range(len(tech_costs)), tech_costs['AnnualCostUSD'] / 1e9, 
                       color=colors_cost, alpha=0.7)
        
        ax3.set_title('Total Cost by Technology', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Total Cost (Billion USD)')
        ax3.set_yticks(range(len(tech_costs)))
        ax3.set_yticklabels(tech_costs['TechID'], fontsize=9)
        ax3.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        # 4. Target achievement
        ax4 = plt.subplot(3, 3, 6)
        
        achievement_pct = self.achievement_df['Achievement_Percent']
        colors_ach = ['green' if x >= 100 else 'orange' for x in achievement_pct]
        
        bars = ax4.bar(self.achievement_df['Year'], achievement_pct, 
                      color=colors_ach, alpha=0.7)
        ax4.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Target')
        
        ax4.set_title('Target Achievement by Year', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Achievement (%)')
        ax4.set_ylim(0, max(110, achievement_pct.max() + 10))
        ax4.legend()
        
        # Add percentage labels on bars
        for bar, pct in zip(bars, achievement_pct):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 5. Abatement by product category
        ax5 = plt.subplot(3, 3, 7)
        
        product_abatement = self.results_df.groupby('Product')['AbatementMtCO2'].sum()
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(product_abatement)))
        
        wedges, texts, autotexts = ax5.pie(product_abatement.values, labels=product_abatement.index, 
                                          autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax5.set_title('Abatement by Product Category', fontsize=12, fontweight='bold')
        
        # 6. Company impact analysis
        ax6 = plt.subplot(3, 3, 8)
        
        if len(self.facility_transitions_df) > 0:
            company_impact = self.facility_transitions_df.groupby('Company')['AbatementMtCO2'].sum().sort_values(ascending=False)
            top_companies = company_impact.head(10)
            
            bars = ax6.bar(range(len(top_companies)), top_companies.values, alpha=0.8)
            ax6.set_title('Top 10 Companies by Abatement', fontsize=12, fontweight='bold')
            ax6.set_xlabel('Company')
            ax6.set_ylabel('Abatement (Mt CO₂)')
            ax6.set_xticks(range(len(top_companies)))
            ax6.set_xticklabels(top_companies.index, rotation=45, ha='right', fontsize=8)
        else:
            ax6.text(0.5, 0.5, 'No facility transitions\ndata available', 
                    ha='center', va='center', transform=ax6.transAxes, fontsize=12)
            ax6.set_title('Company Impact Analysis', fontsize=12, fontweight='bold')
        
        # 7. Technology readiness vs deployment
        ax7 = plt.subplot(3, 3, 9)
        
        tech_summary = self.results_df.groupby('TechID').agg({
            'DeploymentLevel': 'mean',
            'AbatementMtCO2': 'sum',
            'CostPerTonCO2': 'first',
            'TRL': 'first'
        }).reset_index()
        
        scatter = ax7.scatter(tech_summary['TRL'], tech_summary['DeploymentLevel'], 
                            s=tech_summary['AbatementMtCO2']*20, 
                            c=tech_summary['CostPerTonCO2'], cmap='RdYlGn_r', alpha=0.7)
        
        ax7.set_title('Technology Readiness vs Deployment', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Technology Readiness Level (TRL)')
        ax7.set_ylabel('Average Deployment Level')
        plt.colorbar(scatter, ax=ax7, label='Cost (USD/tCO₂)')
        
        # Add technology labels
        for _, tech in tech_summary.iterrows():
            ax7.annotate(tech['TechID'], (tech['TRL'], tech['DeploymentLevel']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "optimization_target_sheet_comprehensive.png", 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Comprehensive visualizations complete")
    
    def save_optimization_results(self):
        """Save all optimization results to files"""
        
        print("\n💾 Saving optimization results...")
        
        # Technology deployment results
        self.results_df.to_csv(self.output_dir / "optimization_target_sheet_deployments.csv", index=False)
        
        # Achievement analysis
        self.achievement_df.to_csv(self.output_dir / "optimization_target_sheet_achievement.csv", index=False)
        
        # Target comparison
        self.target_comparison_df.to_csv(self.output_dir / "optimization_target_sheet_comparison.csv", index=False)
        
        # Facility transitions
        if len(self.facility_transitions_df) > 0:
            self.facility_transitions_df.to_csv(self.output_dir / "optimization_target_sheet_transitions.csv", index=False)
            
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
            
            company_analysis.to_csv(self.output_dir / "optimization_target_sheet_companies.csv", index=False)
        
        # Summary results
        total_abatement = self.results_df['AbatementMtCO2'].sum()
        total_cost = self.results_df['AnnualCostUSD'].sum()
        
        # Calculate compliance
        fully_compliant = self.achievement_df['Target_Compliance'].all()
        avg_achievement = self.achievement_df['Achievement_Percent'].mean()
        
        summary = {
            'BAU_Baseline': '50yr facility lifetime',
            'Target_Source': 'Emissions_Target sheet',
            'Total_Abatement_Mt_CO2': total_abatement,
            'Total_Cost_USD': total_cost,
            'Total_Discounted_Cost_USD': self.total_optimization_cost,
            'Technologies_Deployed': len(self.results_df['TechID'].unique()),
            'Target_Years': len(self.target_years),
            'Fully_Compliant': fully_compliant,
            'Average_Achievement_Percent': avg_achievement,
            'Facilities_Transitioned': len(self.facility_transitions_df) if len(self.facility_transitions_df) > 0 else 0,
            'Companies_Affected': len(self.facility_transitions_df['Company'].unique()) if len(self.facility_transitions_df) > 0 else 0,
            'Avg_Cost_Effectiveness_USD_per_tCO2': total_cost / (total_abatement * 1000) if total_abatement > 0 else 0,
            'Target_2030_Achievement': self.achievement_df[self.achievement_df['Year'] == 2030]['Achievement_Percent'].iloc[0] if 2030 in self.achievement_df['Year'].values else 'N/A',
            'Target_2050_Achievement': self.achievement_df[self.achievement_df['Year'] == 2050]['Achievement_Percent'].iloc[0] if 2050 in self.achievement_df['Year'].values else 'N/A'
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / "optimization_target_sheet_summary.csv", index=False)
        
        print("✅ All results saved to outputs directory")
        
        return summary
    
    def run_optimization_analysis(self):
        """Run complete optimization analysis with target sheet constraints"""
        
        print("🚀 Starting MACC optimization with emission target constraints...")
        print(f"📊 BAU baseline: 50yr facility lifetime")
        print(f"🎯 Target source: Emissions_Target sheet")
        
        # 1. Setup and solve optimization
        self.setup_optimization_problem()
        results_df = self.solve_optimization()
        
        if results_df is None:
            return None
        
        # 2. Create results analysis
        achievement_df = self.create_results_analysis()
        
        # 3. Analyze facility transitions
        facility_transitions = self.analyze_facility_transitions()
        
        # 4. Create comprehensive visualizations
        self.create_comprehensive_visualizations()
        
        # 5. Save results
        summary = self.save_optimization_results()
        
        print("\n✅ TARGET SHEET OPTIMIZATION ANALYSIS COMPLETE")
        print(f"💰 Total cost: ${summary['Total_Cost_USD']/1e9:.2f} billion USD")
        print(f"💰 Discounted cost: ${summary['Total_Discounted_Cost_USD']/1e9:.2f} billion USD")
        print(f"⚡ Cost-effectiveness: ${summary['Avg_Cost_Effectiveness_USD_per_tCO2']:.0f}/tCO₂")
        print(f"🎯 Fully compliant: {summary['Fully_Compliant']}")
        print(f"🎯 Average achievement: {summary['Average_Achievement_Percent']:.1f}%")
        print(f"🏭 Facilities affected: {summary['Facilities_Transitioned']}")
        print(f"🏢 Companies involved: {summary['Companies_Affected']}")
        
        return {
            'technology_deployments': results_df,
            'achievement_analysis': achievement_df,
            'facility_transitions': facility_transitions,
            'summary': summary
        }

if __name__ == "__main__":
    print("🚀 MACC Optimization with Emission Target Sheet Constraints")
    print("="*70)
    
    # Create optimization model
    optimizer = MACCOptimizationTargetSheet()
    
    # Run optimization
    results = optimizer.run_optimization_analysis()
    
    if results:
        print("✅ Optimization completed successfully")
    else:
        print("❌ Optimization failed")