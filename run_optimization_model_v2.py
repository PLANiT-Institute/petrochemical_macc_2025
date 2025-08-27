#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model V2
Simplified linear programming optimization to minimize costs while meeting emission targets
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import pulp
from typing import Dict, List, Tuple

def load_regional_data():
    """Load regional facilities and technology data"""
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    with pd.ExcelFile(data_file) as xls:
        facilities_df = pd.read_excel(xls, sheet_name='RegionalFacilities')
        technologies_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
        costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
        emission_factors_ts_df = pd.read_excel(xls, sheet_name='EmissionFactors_TimeSeries')
        fuel_costs_ts_df = pd.read_excel(xls, sheet_name='FuelCosts_TimeSeries')
    
    return facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df

def create_macc_data_for_optimization(facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, target_years=[2030, 2040, 2050]):
    """Create MACC data for key target years"""
    
    # Import functions from simulation model
    import sys
    sys.path.append('.')
    from run_simulation_model import create_facility_technology_matrix, get_emission_factors_for_year, get_fuel_costs_for_year
    
    macc_data = {}
    
    for year in target_years:
        print(f"   - Creating MACC data for {year}...")
        
        # Create deployment matrix for this year
        deployment_df = create_facility_technology_matrix(
            facilities_df, technologies_df, costs_df, 
            emission_factors_ts_df, fuel_costs_ts_df, year
        )
        
        # Filter to only technologies with positive abatement and finite LCOA
        positive_abatement = deployment_df[
            (deployment_df['AbatementPotential_tCO2_per_t'] > 0) & 
            (deployment_df['LCOA_USD_per_tCO2'] < 10000)  # Reasonable cost threshold
        ].copy()
        
        # Sort by cost-effectiveness
        positive_abatement = positive_abatement.sort_values('LCOA_USD_per_tCO2')
        
        macc_data[year] = positive_abatement
        
        print(f"     - {len(positive_abatement)} viable deployment options")
        print(f"     - Total abatement potential: {positive_abatement['TotalAbatementPotential_ktCO2'].sum()/1000:.1f} MtCO2")
    
    return macc_data

def create_simple_optimization_model(macc_data, baseline_emissions_mt, target_years=[2030, 2040, 2050]):
    """Create a simplified optimization model for key years"""
    
    print("\n🔧 Creating simplified optimization model...")
    
    # Emission reduction targets
    targets = {
        2030: baseline_emissions_mt * 0.15,  # 15% reduction
        2040: baseline_emissions_mt * 0.50,  # 50% reduction
        2050: baseline_emissions_mt * 0.80   # 80% reduction
    }
    
    results = {}
    
    for year in target_years:
        if year not in macc_data or year not in targets:
            continue
            
        print(f"\n   📊 Optimizing for {year} (Target: {targets[year]:.1f} MtCO2 reduction)...")
        
        # Create LP problem for this year
        prob = pulp.LpProblem(f"MACC_{year}", pulp.LpMinimize)
        
        # Get deployment options for this year
        options_df = macc_data[year]
        
        # Decision variables: deployment fraction for each option [0,1]
        deployment_vars = {}
        for idx, row in options_df.iterrows():
            var_name = f"x_{idx}"
            deployment_vars[idx] = pulp.LpVariable(var_name, lowBound=0, upBound=1)
        
        # Objective: Minimize total cost
        total_cost = 0
        for idx, row in options_df.iterrows():
            var = deployment_vars[idx]
            # Cost = deployment_fraction * max_capacity * LCOA * abatement_per_t
            annual_cost = (var * row['MaxDeployment_kt'] * 
                          row['LCOA_USD_per_tCO2'] * row['AbatementPotential_tCO2_per_t'] / 1000)  # Million USD
            total_cost += annual_cost
        
        prob += total_cost
        
        # Constraint: Meet emission reduction target
        total_abatement = 0
        for idx, row in options_df.iterrows():
            var = deployment_vars[idx]
            abatement_contribution = var * row['TotalAbatementPotential_ktCO2'] / 1000  # MtCO2
            total_abatement += abatement_contribution
        
        prob += total_abatement >= targets[year], f"EmissionTarget_{year}"
        
        # Solve
        print(f"     - Variables: {len(deployment_vars)}")
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract results
        status = pulp.LpStatus[prob.status]
        print(f"     - Status: {status}")
        
        if status == 'Optimal':
            optimal_cost = prob.objective.value()
            total_achieved_abatement = 0
            total_investment = 0
            
            deployments = []
            for idx, var in deployment_vars.items():
                if var.value() and var.value() > 0.01:  # Meaningful deployment
                    row = options_df.loc[idx]
                    deployment_fraction = var.value()
                    deployed_capacity = deployment_fraction * row['MaxDeployment_kt']
                    abatement = deployment_fraction * row['TotalAbatementPotential_ktCO2'] / 1000
                    investment = deployed_capacity * row['CAPEX_Million_USD'] / row['MaxDeployment_kt']
                    
                    total_achieved_abatement += abatement
                    total_investment += investment
                    
                    deployments.append({
                        'DeploymentID': row['DeploymentID'],
                        'Technology': row['Technology'],
                        'Region': row['Region'],
                        'Company': row['Company'],
                        'TechGroup': row['TechGroup'],
                        'DeploymentFraction': deployment_fraction,
                        'DeployedCapacity_kt': deployed_capacity,
                        'AbatementContribution_MtCO2': abatement,
                        'Investment_Million_USD': investment,
                        'LCOA_USD_per_tCO2': row['LCOA_USD_per_tCO2']
                    })
            
            results[year] = {
                'status': status,
                'optimal_cost': optimal_cost,
                'target_abatement': targets[year],
                'achieved_abatement': total_achieved_abatement,
                'total_investment': total_investment,
                'deployments': pd.DataFrame(deployments)
            }
            
            print(f"     - Optimal cost: ${optimal_cost:.1f} million/year")
            print(f"     - Achieved abatement: {total_achieved_abatement:.1f} MtCO2 (target: {targets[year]:.1f})")
            print(f"     - Total investment: ${total_investment/1000:.1f} billion")
            print(f"     - Number of deployments: {len(deployments)}")
        
        else:
            results[year] = {
                'status': status,
                'optimal_cost': None,
                'target_abatement': targets[year],
                'achieved_abatement': 0,
                'total_investment': 0,
                'deployments': pd.DataFrame()
            }
            print(f"     - ❌ No feasible solution for {year}")
    
    return results

def create_optimization_pathway(results, baseline_emissions_mt, years=range(2023, 2051)):
    """Create emission pathway from optimization results"""
    
    pathway_data = []
    
    # Interpolate between optimized years
    opt_years = sorted(results.keys())
    
    for year in years:
        # Find the relevant optimization result
        if year <= opt_years[0]:
            # Before first optimization year - use baseline
            emissions = baseline_emissions_mt
            investment = 0
            abatement = 0
        elif year in results:
            # Optimization year
            result = results[year]
            abatement = result['achieved_abatement']
            emissions = baseline_emissions_mt - abatement
            investment = result['total_investment'] / 1000  # Billion USD
        else:
            # Interpolate between optimization years
            # Find surrounding years
            lower_year = max([y for y in opt_years if y <= year])
            upper_year = min([y for y in opt_years if y >= year])
            
            if lower_year == upper_year:
                # Exact match
                result = results[lower_year]
                abatement = result['achieved_abatement']
                investment = result['total_investment'] / 1000
            else:
                # Linear interpolation
                alpha = (year - lower_year) / (upper_year - lower_year)
                lower_abatement = results[lower_year]['achieved_abatement']
                upper_abatement = results[upper_year]['achieved_abatement']
                lower_investment = results[lower_year]['total_investment'] / 1000
                upper_investment = results[upper_year]['total_investment'] / 1000
                
                abatement = lower_abatement + alpha * (upper_abatement - lower_abatement)
                investment = lower_investment + alpha * (upper_investment - lower_investment)
            
            emissions = baseline_emissions_mt - abatement
        
        pathway_data.append({
            'Year': year,
            'BaselineEmissions_MtCO2': baseline_emissions_mt,
            'OptimizedEmissions_MtCO2': emissions,
            'EmissionReduction_MtCO2': abatement,
            'CumulativeInvestment_Billion_USD': investment
        })
    
    return pd.DataFrame(pathway_data)

def create_technology_shares_from_optimization(results, years=range(2023, 2051)):
    """Create technology shares over time from optimization results"""
    
    tech_shares_data = []
    opt_years = sorted(results.keys())
    
    for year in years:
        # Find relevant optimization result
        if year <= opt_years[0]:
            # Before first optimization - no deployment
            continue
        elif year in results:
            # Direct optimization result
            result = results[year]
            deployments_df = result['deployments']
        else:
            # Interpolate between years - use closest lower year for technology mix
            lower_year = max([y for y in opt_years if y <= year])
            result = results[lower_year]
            deployments_df = result['deployments']
            
            # Scale deployments based on interpolation
            upper_year = min([y for y in opt_years if y >= year])
            if upper_year != lower_year:
                alpha = (year - lower_year) / (upper_year - lower_year)
                # Simple scaling - can be improved
                deployments_df = deployments_df.copy()
                deployments_df['DeployedCapacity_kt'] *= (1 + alpha * 0.5)  # Gradual increase
        
        if not deployments_df.empty:
            # Calculate total deployment
            total_deployed = deployments_df['DeployedCapacity_kt'].sum()
            
            if total_deployed > 0:
                # Calculate technology shares
                tech_totals = deployments_df.groupby('Technology')['DeployedCapacity_kt'].sum()
                
                for tech, capacity in tech_totals.items():
                    share = capacity / total_deployed
                    tech_shares_data.append({
                        'Year': year,
                        'Technology': tech,
                        'Capacity_kt': capacity,
                        'Share': share
                    })
    
    return pd.DataFrame(tech_shares_data)

def plot_optimization_comparison(opt_pathway_df, baseline_emissions_mt):
    """Create comparison plots for optimization results"""
    
    # Also load simulation results for comparison
    sim_pathway_file = Path("outputs/emission_pathway_2023_2050.csv")
    if sim_pathway_file.exists():
        sim_pathway_df = pd.read_csv(sim_pathway_file)
        has_simulation = True
    else:
        has_simulation = False
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Emission Pathway Comparison
    ax1.plot(opt_pathway_df['Year'], opt_pathway_df['BaselineEmissions_MtCO2'], 
             'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
    ax1.plot(opt_pathway_df['Year'], opt_pathway_df['OptimizedEmissions_MtCO2'], 
             'r-', linewidth=3, label='Optimization Model', marker='o', markersize=4)
    
    if has_simulation:
        ax1.plot(sim_pathway_df['Year'], sim_pathway_df['TotalEmissions_MtCO2'], 
                 'b-', linewidth=3, label='Simulation Model', alpha=0.7)
    
    # Add target lines
    targets = {
        2030: baseline_emissions_mt * 0.85,  # 15% reduction
        2040: baseline_emissions_mt * 0.50,  # 50% reduction
        2050: baseline_emissions_mt * 0.20   # 80% reduction
    }
    
    for year, target in targets.items():
        ax1.scatter(year, target, color='blue', s=100, zorder=5)
        reduction_pct = int((baseline_emissions_mt - target) / baseline_emissions_mt * 100)
        ax1.annotate(f'{reduction_pct}%', (year, target), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2/year)')
    ax1.set_title('Korean Petrochemical Emission Pathways: Optimization vs Simulation')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 26)
    
    # 2. Emission Reduction Achievement
    ax2.plot(opt_pathway_df['Year'], opt_pathway_df['EmissionReduction_MtCO2'], 
             'r-', linewidth=3, marker='o', markersize=4, label='Optimization')
    if has_simulation:
        ax2.plot(sim_pathway_df['Year'], sim_pathway_df['EmissionReduction_MtCO2'], 
                 'b-', linewidth=3, alpha=0.7, label='Simulation')
    
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Emission Reduction (MtCO2/year)')
    ax2.set_title('Emission Reduction Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Investment Comparison
    ax3.plot(opt_pathway_df['Year'], opt_pathway_df['CumulativeInvestment_Billion_USD'], 
             'r-', linewidth=3, marker='s', markersize=4, label='Optimization')
    if has_simulation:
        ax3.plot(sim_pathway_df['Year'], sim_pathway_df['CumulativeInvestment_Billion_USD'], 
                 'b-', linewidth=3, alpha=0.7, label='Simulation')
    
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Cumulative Investment (Billion USD)')
    ax3.set_title('Investment Requirements Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Cost-effectiveness (Investment per MtCO2 reduced)
    opt_cost_effectiveness = []
    for _, row in opt_pathway_df.iterrows():
        if row['EmissionReduction_MtCO2'] > 0:
            cost_per_mtco2 = row['CumulativeInvestment_Billion_USD'] / row['EmissionReduction_MtCO2']
            opt_cost_effectiveness.append(cost_per_mtco2)
        else:
            opt_cost_effectiveness.append(0)
    
    ax4.plot(opt_pathway_df['Year'], opt_cost_effectiveness, 
             'r-', linewidth=3, marker='^', markersize=4, label='Optimization')
    
    if has_simulation:
        sim_cost_effectiveness = []
        for _, row in sim_pathway_df.iterrows():
            if row['EmissionReduction_MtCO2'] > 0:
                cost_per_mtco2 = row['CumulativeInvestment_Billion_USD'] / row['EmissionReduction_MtCO2']
                sim_cost_effectiveness.append(cost_per_mtco2)
            else:
                sim_cost_effectiveness.append(0)
        
        ax4.plot(sim_pathway_df['Year'], sim_cost_effectiveness, 
                 'b-', linewidth=3, alpha=0.7, label='Simulation')
    
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Investment per MtCO2 Reduced (Billion USD/MtCO2)')
    ax4.set_title('Cost-Effectiveness Comparison')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_optimization_analysis(opt_pathway_df, tech_shares_df, baseline_emissions_mt):
    """Create optimization analysis plots similar to simulation model"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Emission Pathway
    ax1.plot(opt_pathway_df['Year'], opt_pathway_df['BaselineEmissions_MtCO2'], 
             'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
    ax1.plot(opt_pathway_df['Year'], opt_pathway_df['OptimizedEmissions_MtCO2'], 
             'r-', linewidth=3, label='Optimized Pathway')
    ax1.fill_between(opt_pathway_df['Year'], opt_pathway_df['OptimizedEmissions_MtCO2'], 
                     opt_pathway_df['BaselineEmissions_MtCO2'], alpha=0.3, color='red', label='Emission Reduction')
    
    # Add target lines
    targets = {
        2030: baseline_emissions_mt * 0.85,  # 15% reduction
        2035: baseline_emissions_mt * 0.70,  # 30% reduction  
        2040: baseline_emissions_mt * 0.50,  # 50% reduction
        2045: baseline_emissions_mt * 0.30,  # 70% reduction
        2050: baseline_emissions_mt * 0.20   # 80% reduction
    }
    
    for year, target in targets.items():
        ax1.scatter(year, target, color='blue', s=100, zorder=5)
        reduction_pct = int((baseline_emissions_mt - target) / baseline_emissions_mt * 100)
        ax1.annotate(f'{reduction_pct}%', (year, target), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2/year)')
    ax1.set_title('Korean Petrochemical Optimized Emission Pathway 2023-2050')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 26)
    
    # 2. Technology Share Evolution (like simulation model)
    if not tech_shares_df.empty:
        pivot_shares = tech_shares_df.pivot(index='Year', columns='Technology', values='Share').fillna(0)
        
        # Create stacked area plot
        ax2.stackplot(pivot_shares.index, *pivot_shares.T.values, 
                     labels=pivot_shares.columns, alpha=0.8)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Technology Share (%)')
        ax2.set_title('Optimized Technology Deployment Shares')
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
    else:
        ax2.text(0.5, 0.5, 'No technology share data available', 
                transform=ax2.transAxes, ha='center', va='center')
        ax2.set_title('Optimized Technology Deployment Shares')
    
    # 3. Cumulative Investment
    ax3.plot(opt_pathway_df['Year'], opt_pathway_df['CumulativeInvestment_Billion_USD'], 
             'r-', linewidth=3, marker='o', markersize=4)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Cumulative Investment (Billion USD)')
    ax3.set_title('Required Investment for Optimized Technologies')
    ax3.grid(True, alpha=0.3)
    
    # 4. Emission Reduction Progress
    ax4.plot(opt_pathway_df['Year'], opt_pathway_df['EmissionReduction_MtCO2'], 
             'g-', linewidth=3, marker='s', markersize=4)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Emission Reduction (MtCO2/year)')
    ax4.set_title('Emission Reduction Achievement')
    ax4.grid(True, alpha=0.3)
    
    # Add reduction targets
    for year, target in targets.items():
        target_reduction = baseline_emissions_mt - target
        ax4.scatter(year, target_reduction, color='red', s=100, zorder=5, alpha=0.7)
    
    plt.tight_layout()
    return fig

def main():
    """Main execution function for optimization model V2"""
    
    print("🏭 Korean Petrochemical MACC Optimization Model V2")
    print("=" * 60)
    
    # Load data
    print("📊 Loading regional facilities and technology data...")
    facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df = load_regional_data()
    
    print(f"   - Facilities: {len(facilities_df)} across {facilities_df['Region'].nunique()} regions")
    print(f"   - Technologies: {len(technologies_df)} alternative technologies (Green H2 only)")
    print(f"   - Time series data: 2023-2050 emission factors and fuel costs")
    
    # Calculate baseline
    import sys
    sys.path.append('.')
    from run_simulation_model import calculate_baseline_emissions
    
    baseline_emissions_mt, _ = calculate_baseline_emissions()
    print(f"   - 2023 baseline emissions: {baseline_emissions_mt:.1f} MtCO2/year")
    
    # Create MACC data for optimization
    print("\n🔧 Creating MACC data for key years...")
    target_years = [2030, 2040, 2050]
    macc_data = create_macc_data_for_optimization(
        facilities_df, technologies_df, costs_df, 
        emission_factors_ts_df, fuel_costs_ts_df, target_years
    )
    
    # Run optimization for key years
    print("\n🎯 Running optimization for target years...")
    results = create_simple_optimization_model(macc_data, baseline_emissions_mt, target_years)
    
    # Create emission pathway
    print("\n📈 Creating optimized emission pathway...")
    opt_pathway_df = create_optimization_pathway(results, baseline_emissions_mt)
    
    # Create technology shares
    print("📊 Creating technology shares from optimization results...")
    tech_shares_df = create_technology_shares_from_optimization(results)
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n💾 Saving optimization outputs to {output_dir}/...")
    
    # Save pathway
    opt_pathway_df.to_csv(output_dir / "optimization_pathway_v2.csv", index=False)
    
    # Save technology shares
    if not tech_shares_df.empty:
        tech_shares_df.to_csv(output_dir / "optimization_technology_shares.csv", index=False)
    
    # Save detailed deployments for each year
    for year, result in results.items():
        if not result['deployments'].empty:
            result['deployments'].to_csv(output_dir / f"optimization_deployments_{year}.csv", index=False)
    
    # Create optimization analysis plots (similar to simulation model)
    print("\n📊 Creating optimization analysis plots...")
    fig1 = plot_optimization_analysis(opt_pathway_df, tech_shares_df, baseline_emissions_mt)
    fig1.savefig(output_dir / "optimization_analysis_v2_2023_2050.png", dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    # Create comparison plots
    print("📊 Creating optimization vs simulation comparison plots...")
    fig2 = plot_optimization_comparison(opt_pathway_df, baseline_emissions_mt)
    fig2.savefig(output_dir / "model_comparison_optimization_vs_simulation.png", dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    # Print summary results
    print("\n🎯 OPTIMIZATION MODEL V2 RESULTS:")
    print("=" * 50)
    
    for year in target_years:
        if year in results:
            result = results[year]
            reduction_pct = (result['achieved_abatement'] / baseline_emissions_mt * 100)
            emissions = baseline_emissions_mt - result['achieved_abatement']
            
            print(f"\n📅 {year} Results:")
            print(f"   - Status: {result['status']}")
            print(f"   - Target reduction: {result['target_abatement']:.1f} MtCO2 ({result['target_abatement']/baseline_emissions_mt*100:.0f}%)")
            print(f"   - Achieved reduction: {result['achieved_abatement']:.1f} MtCO2 ({reduction_pct:.0f}%)")
            print(f"   - Final emissions: {emissions:.1f} MtCO2/year")
            print(f"   - Investment required: ${result['total_investment']/1000:.1f} billion")
            print(f"   - Annual cost: ${result['optimal_cost']:.1f} million/year")
            if len(result['deployments']) > 0:
                top_techs = result['deployments'].nlargest(3, 'AbatementContribution_MtCO2')
                print(f"   - Top technologies:")
                for _, tech in top_techs.iterrows():
                    print(f"     * {tech['Technology']}: {tech['AbatementContribution_MtCO2']:.1f} MtCO2 at ${tech['LCOA_USD_per_tCO2']:.0f}/tCO2")
    
    print(f"\n✅ Optimization Model V2 completed! Check {output_dir}/ for detailed results.")

if __name__ == "__main__":
    main()