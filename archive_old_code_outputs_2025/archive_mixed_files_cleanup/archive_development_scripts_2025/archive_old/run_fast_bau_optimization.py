#!/usr/bin/env python3
"""
Fast BAU to Net-Zero optimization - results only, minimal visualization
"""

import pandas as pd
import numpy as np
from pulp import *
from pathlib import Path

class FastMACCOptimization:
    def __init__(self, facility_lifetime='30yr'):
        self.output_dir = Path("outputs")
        self.facility_lifetime = facility_lifetime
        
        # Load data
        self.data_file = 'data/korean_petrochemical_macc_optimization.xlsx'
        self.tech_options = pd.read_excel(self.data_file, sheet_name='TechOptions')
        self.macc_template = pd.read_excel(self.data_file, sheet_name='MACC_Template')
        
        # Load BAU pathway
        bau_file = f"outputs/bau_emission_pathway_{facility_lifetime}_final.csv"
        self.bau_pathway = pd.read_csv(bau_file)
        
        # Merge tech data
        tech_cols = ['TechID', 'Product', 'StartYear_Commercial', 'MaxPenetration', 'RampUpSharePerYear']
        self.tech_data = self.macc_template.merge(self.tech_options[tech_cols], on='TechID')
        
        print(f"✓ Fast optimization setup for {facility_lifetime}")
        
    def run_optimization(self):
        """Run streamlined optimization"""
        
        # Get BAU baseline and calculate linear targets
        bau_2025 = self.bau_pathway[self.bau_pathway['year'] == 2025]['emissions_mt_co2'].iloc[0]
        
        # Linear reduction targets
        years = list(range(2025, 2051))
        targets = {}
        for year in years:
            progress = (year - 2025) / 25  # 25 years to net-zero
            targets[year] = bau_2025 * (1 - progress)
        
        print(f"✓ BAU 2025: {bau_2025:.1f} Mt CO₂ → Net-zero 2050")
        
        # Setup optimization problem
        prob = LpProblem("Fast_MACC_NetZero", LpMinimize)
        
        # Decision variables
        deployment_vars = {}
        for _, tech in self.tech_data.iterrows():
            tech_id = tech['TechID']
            for year in years:
                if year >= tech['StartYear_Commercial']:
                    deployment_vars[(tech_id, year)] = LpVariable(
                        f"deploy_{tech_id}_{year}", 
                        lowBound=0, 
                        upBound=tech['MaxPenetration']
                    )
        
        # Objective: minimize cost
        total_cost = 0
        for _, tech in self.tech_data.iterrows():
            tech_id = tech['TechID']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in years:
                if (tech_id, year) in deployment_vars:
                    discount_factor = 1 / (1.03 ** (year - 2025))
                    annual_cost = (deployment_vars[(tech_id, year)] * 
                                 abatement_potential * cost_per_tco2 * 1_000_000 * discount_factor)
                    total_cost += annual_cost
        
        prob += total_cost
        
        # Constraints: Meet targets each year
        for year in years:
            bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
            target_emissions = targets[year]
            required_abatement = bau_emissions - target_emissions
            
            year_abatement = 0
            for _, tech in self.tech_data.iterrows():
                tech_id = tech['TechID']
                if (tech_id, year) in deployment_vars:
                    abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
                    year_abatement += (deployment_vars[(tech_id, year)] * abatement_potential)
            
            prob += year_abatement >= required_abatement, f"Target_{year}"
        
        # Solve
        print("🔧 Solving optimization...")
        prob.solve(PULP_CBC_CMD(msg=0))
        
        status = LpStatus[prob.status]
        print(f"✓ Status: {status}")
        
        if status != 'Optimal':
            return None
        
        # Extract results
        results = []
        total_cost_undiscounted = 0
        
        for _, tech in self.tech_data.iterrows():
            tech_id = tech['TechID']
            product = tech['Product']
            cost_per_tco2 = tech['Cost_USD_per_tCO2']
            abatement_potential = tech['Abatement_Potential_MtCO2_per_year']
            
            for year in years:
                if (tech_id, year) in deployment_vars:
                    deployment_level = deployment_vars[(tech_id, year)].varValue or 0
                    
                    if deployment_level > 0.001:
                        annual_abatement = deployment_level * abatement_potential
                        annual_cost = annual_abatement * cost_per_tco2 * 1_000_000
                        total_cost_undiscounted += annual_cost
                        
                        results.append({
                            'TechID': tech_id,
                            'Product': product,
                            'Year': year,
                            'DeploymentLevel': deployment_level,
                            'AbatementMtCO2': annual_abatement,
                            'AnnualCostUSD': annual_cost,
                            'CostPerTonCO2': cost_per_tco2
                        })
        
        results_df = pd.DataFrame(results)
        
        # Create emission pathway
        pathway = []
        for year in years:
            bau_emissions = self.bau_pathway[self.bau_pathway['year'] == year]['emissions_mt_co2'].iloc[0]
            target_emissions = targets[year]
            
            year_abatement = results_df[results_df['Year'] == year]['AbatementMtCO2'].sum()
            optimized_emissions = bau_emissions - year_abatement
            
            pathway.append({
                'Year': year,
                'BAU_Emissions': bau_emissions,
                'Target_Emissions': target_emissions,
                'Optimized_Emissions': optimized_emissions,
                'Abatement': year_abatement,
                'Gap': max(0, optimized_emissions - target_emissions)
            })
        
        pathway_df = pd.DataFrame(pathway)
        
        # Key milestones
        milestone_2030 = pathway_df[pathway_df['Year'] == 2030].iloc[0]
        milestone_2040 = pathway_df[pathway_df['Year'] == 2040].iloc[0]
        milestone_2050 = pathway_df[pathway_df['Year'] == 2050].iloc[0]
        
        # Summary
        summary = {
            'facility_lifetime': self.facility_lifetime,
            'bau_2025_baseline': bau_2025,
            'total_cost_billion_usd': total_cost_undiscounted / 1e9,
            'technologies_deployed': len(results_df['TechID'].unique()),
            'total_abatement_mt': results_df['AbatementMtCO2'].sum(),
            'avg_cost_per_tco2': total_cost_undiscounted / (results_df['AbatementMtCO2'].sum() * 1000),
            'emissions_2030': milestone_2030['Optimized_Emissions'],
            'target_2030': milestone_2030['Target_Emissions'],
            'achievement_2030_pct': (1 - milestone_2030['Gap'] / max(0.1, milestone_2030['Target_Emissions'])) * 100,
            'emissions_2040': milestone_2040['Optimized_Emissions'],
            'target_2040': milestone_2040['Target_Emissions'],
            'achievement_2040_pct': (1 - milestone_2040['Gap'] / max(0.1, milestone_2040['Target_Emissions'])) * 100,
            'emissions_2050': milestone_2050['Optimized_Emissions'],
            'target_2050': milestone_2050['Target_Emissions'],
            'netzero_achievement_pct': (1 - milestone_2050['Gap'] / max(0.1, milestone_2050['Target_Emissions'])) * 100
        }
        
        # Save results
        results_df.to_csv(self.output_dir / f"fast_optimization_{self.facility_lifetime}_deployments.csv", index=False)
        pathway_df.to_csv(self.output_dir / f"fast_optimization_{self.facility_lifetime}_pathway.csv", index=False)
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / f"fast_optimization_{self.facility_lifetime}_summary.csv", index=False)
        
        return summary, pathway_df, results_df

if __name__ == "__main__":
    # Run for all facility lifetimes
    all_results = {}
    
    for lifetime in ['25yr', '30yr', '40yr', '50yr']:
        print(f"\n{'='*50}")
        print(f"OPTIMIZING {lifetime.upper()} FACILITY LIFETIME")
        print(f"{'='*50}")
        
        optimizer = FastMACCOptimization(facility_lifetime=lifetime)
        results = optimizer.run_optimization()
        
        if results:
            summary, pathway, deployments = results
            all_results[lifetime] = summary
            
            print(f"✅ {lifetime} RESULTS:")
            print(f"💰 Total cost: ${summary['total_cost_billion_usd']:.2f}B USD")
            print(f"⚡ Cost-effectiveness: ${summary['avg_cost_per_tco2']:.0f}/tCO₂")
            print(f"🎯 2030 achievement: {summary['achievement_2030_pct']:.1f}%")
            print(f"🎯 2040 achievement: {summary['achievement_2040_pct']:.1f}%")
            print(f"🎯 Net-zero achievement: {summary['netzero_achievement_pct']:.1f}%")
        else:
            print(f"❌ {lifetime} optimization failed")
    
    # Create comparison summary
    comparison_df = pd.DataFrame.from_dict(all_results, orient='index')
    comparison_df.to_csv("outputs/fast_optimization_comparison_all_lifetimes.csv")
    
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(comparison_df[['total_cost_billion_usd', 'achievement_2030_pct', 'achievement_2040_pct', 'netzero_achievement_pct']].round(1))