#!/usr/bin/env python3
"""
Enhanced Korean Petrochemical MACC Optimization Model
Using realistic technology constraints and renewable energy integration
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

class EnhancedMACCOptimization:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load enhanced optimization data
        self.data_file = 'data/korean_petrochemical_macc_enhanced.xlsx'
        self.tech_options = pd.read_excel(self.data_file, sheet_name='TechOptions')
        self.macc_template = pd.read_excel(self.data_file, sheet_name='MACC_Template')
        self.baseline_assumptions = pd.read_excel(self.data_file, sheet_name='Baseline_Assumptions')
        self.facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        
        # Load BAU emission pathway (50yr facility lifetime)
        self.bau_pathway = pd.read_csv("outputs/bau_emission_pathway_50yr_final.csv")
        
        # Load emission targets from sheet
        self.emission_targets = pd.read_excel(self.data_file, sheet_name='Emissions_Target')
        
        # Merge technology data
        tech_cols = ['TechID', 'Product', 'ProcessType', 'StartYear_Commercial', 'MaxPenetration', 'RampUpSharePerYear']
        self.tech_data = self.macc_template.merge(
            self.tech_options[tech_cols], 
            on='TechID'
        )
        
        print(f"✓ Loaded enhanced optimization data: {len(self.tech_data)} technologies")
        print(f"✓ Using 50yr BAU pathway baseline")
        print(f"✓ Technology categories: {self.tech_options['ProcessType'].value_counts().to_dict()}")
        
    def analyze_enhanced_technology_portfolio(self):
        """Analyze the enhanced technology portfolio"""
        
        print("\n🔬 ENHANCED TECHNOLOGY PORTFOLIO ANALYSIS")
        print("="*70)
        
        # Technology overview by category
        tech_summary = self.tech_data.groupby('ProcessType').agg({
            'TechID': 'count',
            'Cost_USD_per_tCO2': ['min', 'max', 'mean'],
            'Abatement_Potential_MtCO2_per_year': 'sum',
            'MaxPenetration': 'mean'
        }).round(2)
        
        tech_summary.columns = ['Count', 'Min_Cost', 'Max_Cost', 'Avg_Cost', 'Total_Abatement', 'Avg_Penetration']
        
        print("Technology Categories:")
        print(tech_summary)
        
        # Process-specific EE analysis
        ee_technologies = self.tech_data[self.tech_data['ProcessType'] == 'Efficiency']
        print(f"\n⚡ ENERGY EFFICIENCY TECHNOLOGIES:")
        for _, tech in ee_technologies.iterrows():
            print(f"  • {tech['TechID']}: {tech['TechName']}")
            print(f"    Cost: ${tech['Cost_USD_per_tCO2']}/tCO₂, Potential: {tech['Abatement_Potential_MtCO2_per_year']:.1f} Mt CO₂")
            print(f"    Max Penetration: {tech['MaxPenetration']:.0%}, Product: {tech['Product']}")
        
        # Renewable energy analysis
        renewable_technologies = self.tech_data[self.tech_data['ProcessType'] == 'Renewable']
        print(f"\n🔋 RENEWABLE ENERGY TECHNOLOGIES:")
        for _, tech in renewable_technologies.iterrows():
            print(f"  • {tech['TechID']}: {tech['TechName']}")
            print(f"    Cost: ${tech['Cost_USD_per_tCO2']}/tCO₂, Potential: {tech['Abatement_Potential_MtCO2_per_year']:.1f} Mt CO₂")
            print(f"    Max Penetration: {tech['MaxPenetration']:.0%}, TRL: {tech['TRL']}")
        
        return tech_summary
    
    def prepare_targets_and_bau(self):
        """Prepare emission targets and BAU pathway alignment"""
        
        print("\n📊 Preparing targets and BAU pathway...")
        
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
        
        self.target_comparison_df = pd.DataFrame(bau_comparison)
        
        print("Enhanced BAU vs Target Comparison:")
        print(self.target_comparison_df.round(1))
        
        return self.target_comparison_df
    
    def setup_enhanced_optimization(self):
        """Setup optimization problem with enhanced technology constraints"""
        
        print("\n🎯 Setting up enhanced optimization...")
        
        # Prepare targets
        self.prepare_targets_and_bau()
        
        # Target years
        target_years = self.emission_targets['Year'].tolist()
        
        # Get available technologies
        available_techs = self.tech_data.copy()
        
        print(f"✓ Target years: {target_years}")
        print(f"✓ Available technologies: {len(available_techs)}")
        
        # Create optimization problem
        prob = LpProblem("Enhanced_MACC_Optimization", LpMinimize)
        
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
        
        # Objective: Minimize total cost with technology risk adjustment
        total_cost = 0
        for _, tech in available_techs.iterrows():
            tech_id = tech['TechID']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            # Apply risk premium based on TRL
            trl_risk_factor = {9: 1.0, 8: 1.1, 7: 1.25, 6: 1.5}.get(tech['TRL'], 2.0)
            adjusted_cost = cost_per_tco2 * trl_risk_factor
            
            for year in target_years:
                if year >= tech['StartYear_Commercial'] and (tech_id, year) in deployment_vars:
                    # Apply discount factor
                    discount_factor = 1 / (1.03 ** (year - 2025))
                    annual_cost = (deployment_vars[(tech_id, year)] * 
                                 abatement_potential * adjusted_cost * 1_000_000 * discount_factor)
                    total_cost += annual_cost
        
        prob += total_cost
        
        # Constraint 1: Meet emission targets for each year
        for year in target_years:
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
        
        # Constraint 2: Technology ramp-up between consecutive target years
        sorted_years = sorted(target_years)
        for i in range(1, len(sorted_years)):
            prev_year = sorted_years[i-1]
            curr_year = sorted_years[i]
            year_gap = curr_year - prev_year
            
            for _, tech in available_techs.iterrows():
                tech_id = tech['TechID']
                ramp_rate = tech['RampUpSharePerYear']
                max_increase = ramp_rate * year_gap
                
                if ((tech_id, prev_year) in deployment_vars and 
                    (tech_id, curr_year) in deployment_vars):
                    prob += (deployment_vars[(tech_id, curr_year)] <= 
                           deployment_vars[(tech_id, prev_year)] + max_increase), f"RampUp_{tech_id}_{prev_year}_{curr_year}"
        
        # Constraint 3: Enhanced technology competition within products
        product_groups = available_techs.groupby('Product')
        for product, product_techs in product_groups:
            if len(product_techs) > 1 and product != 'All_Products':
                for year in target_years:
                    total_penetration = 0
                    for _, tech in product_techs.iterrows():
                        tech_id = tech['TechID']
                        if (tech_id, year) in deployment_vars:
                            total_penetration += deployment_vars[(tech_id, year)]
                    
                    prob += total_penetration <= 1.0, f"ProductCompetition_{product}_{year}"
        
        # Constraint 4: Process-specific EE constraints (implicit in max penetration)
        # Already handled by individual technology max penetrations
        
        # Constraint 5: Renewable energy integration constraints
        renewable_techs = available_techs[available_techs['ProcessType'] == 'Renewable']
        for year in target_years:
            total_renewable_penetration = 0
            for _, tech in renewable_techs.iterrows():
                tech_id = tech['TechID']
                if (tech_id, year) in deployment_vars:
                    total_renewable_penetration += deployment_vars[(tech_id, year)]
            
            # Limit total renewable penetration to avoid grid stability issues
            prob += total_renewable_penetration <= 1.0, f"RenewableLimit_{year}"
        
        self.prob = prob
        self.deployment_vars = deployment_vars
        self.available_techs = available_techs
        self.target_years = target_years
        
        return prob
    
    def solve_enhanced_optimization(self):
        """Solve the enhanced optimization problem"""
        
        print("🔧 Solving enhanced optimization problem...")
        
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
            process_type = tech['ProcessType']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            trl = tech['TRL']
            
            # Apply risk adjustment
            trl_risk_factor = {9: 1.0, 8: 1.1, 7: 1.25, 6: 1.5}.get(trl, 2.0)
            
            for year in self.target_years:
                if (tech_id, year) in self.deployment_vars:
                    deployment_level = self.deployment_vars[(tech_id, year)].varValue or 0
                    
                    if deployment_level > 0.001:
                        annual_abatement = deployment_level * abatement_potential
                        discount_factor = 1 / (1.03 ** (year - 2025))
                        adjusted_cost = cost_per_tco2 * trl_risk_factor
                        annual_cost = annual_abatement * adjusted_cost * 1_000_000 * discount_factor
                        total_cost += annual_cost
                        
                        results.append({
                            'TechID': tech_id,
                            'Product': product,
                            'ProcessType': process_type,
                            'Year': year,
                            'DeploymentLevel': deployment_level,
                            'AbatementMtCO2': annual_abatement,
                            'AnnualCostUSD': annual_cost / discount_factor,
                            'DiscountedCostUSD': annual_cost,
                            'CostPerTonCO2': cost_per_tco2,
                            'AdjustedCostPerTonCO2': adjusted_cost,
                            'TRL': trl,
                            'RiskFactor': trl_risk_factor,
                            'StartYear_Commercial': tech['StartYear_Commercial']
                        })
        
        self.results_df = pd.DataFrame(results)
        self.total_optimization_cost = total_cost
        
        print(f"✓ Total discounted optimization cost: ${total_cost/1e9:.2f} billion USD")
        print(f"✓ Deployed technologies: {len(self.results_df['TechID'].unique())}")
        
        # Technology deployment summary
        tech_deployment_summary = self.results_df.groupby(['ProcessType', 'TechID']).agg({
            'AbatementMtCO2': 'sum',
            'AnnualCostUSD': 'sum',
            'DeploymentLevel': 'mean'
        }).reset_index()
        
        print(f"\n📊 Technology Deployment Summary:")
        for process_type in tech_deployment_summary['ProcessType'].unique():
            process_techs = tech_deployment_summary[tech_deployment_summary['ProcessType'] == process_type]
            total_abatement = process_techs['AbatementMtCO2'].sum()
            total_cost = process_techs['AnnualCostUSD'].sum()
            
            print(f"  {process_type}: {total_abatement:.1f} Mt CO₂, ${total_cost/1e9:.2f}B USD")
            for _, tech in process_techs.iterrows():
                print(f"    • {tech['TechID']}: {tech['AbatementMtCO2']:.1f} Mt CO₂ ({tech['DeploymentLevel']:.1%})")
        
        return self.results_df
    
    def create_enhanced_visualizations(self):
        """Create comprehensive enhanced optimization visualizations"""
        
        print("\n📊 Creating enhanced visualizations...")
        
        # Create achievement analysis
        achievement_analysis = []
        for year in self.target_years:
            year_data = self.target_comparison_df[self.target_comparison_df['Year'] == year].iloc[0]
            year_abatement = self.results_df[self.results_df['Year'] == year]['AbatementMtCO2'].sum()
            
            bau_emissions = year_data['BAU_Emissions']
            target_emissions = year_data['Target_Emissions']
            optimized_emissions = bau_emissions - year_abatement
            
            required_abatement = year_data['Required_Abatement']
            achievement_pct = (year_abatement / required_abatement * 100) if required_abatement > 0 else 100
            
            achievement_analysis.append({
                'Year': year,
                'BAU_Emissions': bau_emissions,
                'Target_Emissions': target_emissions,
                'Optimized_Emissions': optimized_emissions,
                'Achievement_Percent': achievement_pct,
                'Target_Compliance': optimized_emissions <= target_emissions
            })
        
        achievement_df = pd.DataFrame(achievement_analysis)
        
        # Create comprehensive visualization
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Enhanced emission pathway
        ax1 = plt.subplot(3, 3, (1, 3))
        
        years = achievement_df['Year']
        ax1.plot(years, achievement_df['BAU_Emissions'], 'r-', linewidth=3, 
                label='BAU (50yr)', marker='o', markersize=8)
        ax1.plot(years, achievement_df['Target_Emissions'], 'g--', linewidth=3, 
                label='Targets', marker='s', markersize=8)
        ax1.plot(years, achievement_df['Optimized_Emissions'], 'b-', linewidth=3, 
                label='Enhanced Optimization', marker='^', markersize=8)
        
        ax1.fill_between(years, achievement_df['BAU_Emissions'], 
                        achievement_df['Optimized_Emissions'], alpha=0.3, color='blue')
        
        ax1.set_title('Enhanced MACC Optimization Results', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (Mt CO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Technology deployment by process type
        ax2 = plt.subplot(3, 3, 4)
        
        process_deployment = self.results_df.groupby(['Year', 'ProcessType'])['AbatementMtCO2'].sum().unstack(fill_value=0)
        
        bottom = np.zeros(len(years))
        colors = plt.cm.Set2(np.linspace(0, 1, len(process_deployment.columns)))
        
        for i, process_type in enumerate(process_deployment.columns):
            ax2.bar(years, process_deployment[process_type], bottom=bottom, 
                   label=process_type, color=colors[i], alpha=0.8)
            bottom += process_deployment[process_type]
        
        ax2.set_title('Abatement by Process Type', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Abatement (Mt CO₂)')
        ax2.legend()
        
        # 3. Cost-effectiveness analysis
        ax3 = plt.subplot(3, 3, 5)
        
        tech_summary = self.results_df.groupby('TechID').agg({
            'AbatementMtCO2': 'sum',
            'CostPerTonCO2': 'first',
            'ProcessType': 'first'
        }).reset_index()
        tech_summary = tech_summary.sort_values('CostPerTonCO2')
        
        colors_cost = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(tech_summary)))
        bars = ax3.barh(range(len(tech_summary)), tech_summary['CostPerTonCO2'], 
                       color=colors_cost, alpha=0.7)
        
        ax3.set_title('Technology Cost-Effectiveness', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Cost (USD/tCO₂)')
        ax3.set_yticks(range(len(tech_summary)))
        ax3.set_yticklabels(tech_summary['TechID'], fontsize=8)
        ax3.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        # 4. TRL vs deployment analysis
        ax4 = plt.subplot(3, 3, 6)
        
        trl_analysis = self.results_df.groupby('TRL').agg({
            'AbatementMtCO2': 'sum',
            'DeploymentLevel': 'mean'
        }).reset_index()
        
        scatter = ax4.scatter(trl_analysis['TRL'], trl_analysis['DeploymentLevel'], 
                            s=trl_analysis['AbatementMtCO2']*20, alpha=0.7, c=trl_analysis['TRL'], cmap='viridis')
        
        ax4.set_title('Technology Readiness vs Deployment', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Technology Readiness Level')
        ax4.set_ylabel('Average Deployment Level')
        plt.colorbar(scatter, ax=ax4)
        
        # 5. Renewable energy penetration
        ax5 = plt.subplot(3, 3, 7)
        
        renewable_data = self.results_df[self.results_df['ProcessType'] == 'Renewable']
        if len(renewable_data) > 0:
            renewable_by_year = renewable_data.groupby('Year')['DeploymentLevel'].sum()
            ax5.bar(renewable_by_year.index, renewable_by_year.values, alpha=0.7, color='green')
            ax5.set_title('Renewable Energy Penetration', fontsize=12, fontweight='bold')
            ax5.set_xlabel('Year')
            ax5.set_ylabel('Total Renewable Penetration')
        else:
            ax5.text(0.5, 0.5, 'No Renewable\nTechnologies Deployed', 
                    ha='center', va='center', transform=ax5.transAxes)
        
        # 6. Energy efficiency breakdown
        ax6 = plt.subplot(3, 3, 8)
        
        ee_data = self.results_df[self.results_df['ProcessType'] == 'Efficiency']
        if len(ee_data) > 0:
            ee_by_tech = ee_data.groupby('TechID')['AbatementMtCO2'].sum()
            ax6.pie(ee_by_tech.values, labels=ee_by_tech.index, autopct='%1.1f%%', startangle=90)
            ax6.set_title('Energy Efficiency Breakdown', fontsize=12, fontweight='bold')
        else:
            ax6.text(0.5, 0.5, 'No Energy Efficiency\nTechnologies Deployed', 
                    ha='center', va='center', transform=ax6.transAxes)
        
        # 7. Achievement rates
        ax7 = plt.subplot(3, 3, 9)
        
        achievement_pct = achievement_df['Achievement_Percent']
        colors_ach = ['green' if x >= 99.9 else 'orange' for x in achievement_pct]
        
        bars = ax7.bar(years, achievement_pct, color=colors_ach, alpha=0.7)
        ax7.axhline(y=100, color='red', linestyle='--', alpha=0.7)
        ax7.set_title('Target Achievement', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Year')
        ax7.set_ylabel('Achievement (%)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "enhanced_macc_optimization_results.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return achievement_df
    
    def save_enhanced_results(self):
        """Save enhanced optimization results"""
        
        print("\n💾 Saving enhanced results...")
        
        # Technology deployment results
        self.results_df.to_csv(self.output_dir / "enhanced_optimization_deployments.csv", index=False)
        
        # Achievement analysis
        achievement_df = self.create_enhanced_visualizations()
        achievement_df.to_csv(self.output_dir / "enhanced_optimization_achievement.csv", index=False)
        
        # Summary results
        total_abatement = self.results_df['AbatementMtCO2'].sum()
        total_cost = self.results_df['AnnualCostUSD'].sum()
        
        summary = {
            'Model_Version': 'Enhanced MACC with Realistic Constraints',
            'Technologies_Available': len(self.tech_data),
            'Technologies_Deployed': len(self.results_df['TechID'].unique()),
            'Total_Abatement_Mt_CO2': total_abatement,
            'Total_Cost_USD': total_cost,
            'Total_Discounted_Cost_USD': self.total_optimization_cost,
            'Avg_Cost_Effectiveness_USD_per_tCO2': total_cost / (total_abatement * 1000) if total_abatement > 0 else 0,
            'Fully_Compliant': achievement_df['Target_Compliance'].all(),
            'Average_Achievement_Percent': achievement_df['Achievement_Percent'].mean(),
            'EE_Realistic_Constraint': 'Applied process-specific limits',
            'Renewable_Integration': 'Solar PV, Wind, Solar Thermal included',
            'Heat_Pump_Enhancement': 'Split into low/high temperature applications',
            'Technology_Risk_Adjustment': 'TRL-based cost adjustments applied'
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / "enhanced_optimization_summary.csv", index=False)
        
        print("✅ Enhanced results saved")
        
        return summary
    
    def run_enhanced_optimization_analysis(self):
        """Run complete enhanced optimization analysis"""
        
        print("🚀 ENHANCED MACC OPTIMIZATION ANALYSIS")
        print("="*70)
        
        # 1. Analyze technology portfolio
        self.analyze_enhanced_technology_portfolio()
        
        # 2. Setup and solve optimization
        self.setup_enhanced_optimization()
        results_df = self.solve_enhanced_optimization()
        
        if results_df is None:
            return None
        
        # 3. Create visualizations and save results
        summary = self.save_enhanced_results()
        
        print("\n✅ ENHANCED OPTIMIZATION COMPLETE")
        print(f"💰 Total cost: ${summary['Total_Cost_USD']/1e9:.2f} billion USD")
        print(f"💰 Discounted cost: ${summary['Total_Discounted_Cost_USD']/1e9:.2f} billion USD")
        print(f"⚡ Cost-effectiveness: ${summary['Avg_Cost_Effectiveness_USD_per_tCO2']:.0f}/tCO₂")
        print(f"🎯 Target compliance: {summary['Fully_Compliant']}")
        print(f"🎯 Average achievement: {summary['Average_Achievement_Percent']:.1f}%")
        print(f"🔧 Technologies deployed: {summary['Technologies_Deployed']}/{summary['Technologies_Available']}")
        
        return {
            'technology_deployments': results_df,
            'summary': summary
        }

if __name__ == "__main__":
    print("🚀 ENHANCED MACC OPTIMIZATION WITH REALISTIC CONSTRAINTS")
    print("="*80)
    
    # Create enhanced optimization model
    optimizer = EnhancedMACCOptimization()
    
    # Run optimization
    results = optimizer.run_enhanced_optimization_analysis()
    
    if results:
        print("✅ Enhanced optimization completed successfully")
    else:
        print("❌ Enhanced optimization failed")