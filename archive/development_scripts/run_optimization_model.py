#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model
Linear Programming optimization to minimize costs while meeting emission targets
Regional facility-level deployment with alternative technologies only
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

def get_emission_factors_for_year(year, emission_factors_ts_df):
    """Get emission factors for a specific year"""
    year_data = emission_factors_ts_df[emission_factors_ts_df['Year'] == year]
    if year_data.empty:
        # Use the closest available year
        closest_year = emission_factors_ts_df.iloc[(emission_factors_ts_df['Year'] - year).abs().argsort()[:1]]['Year'].iloc[0]
        year_data = emission_factors_ts_df[emission_factors_ts_df['Year'] == closest_year]
    
    row = year_data.iloc[0]
    return {
        'Natural_Gas_GJ': row['Natural_Gas_tCO2_per_GJ'],
        'Fuel_Oil_GJ': row['Fuel_Oil_tCO2_per_GJ'],
        'Electricity_GJ': row['Electricity_tCO2_per_GJ'],
        'Green_Hydrogen_GJ': row['Green_Hydrogen_tCO2_per_GJ'],
        'Naphtha_t': row['Naphtha_tCO2_per_t'],
        'LPG_t': row['LPG_tCO2_per_t'],
        'Reformate_t': row['Reformate_tCO2_per_t']
    }

def get_fuel_costs_for_year(year, fuel_costs_ts_df):
    """Get fuel costs for a specific year"""
    year_data = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == year]
    if year_data.empty:
        # Use the closest available year
        closest_year = fuel_costs_ts_df.iloc[(fuel_costs_ts_df['Year'] - year).abs().argsort()[:1]]['Year'].iloc[0]
        year_data = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == closest_year]
    
    row = year_data.iloc[0]
    return {
        'Natural_Gas_USD_per_GJ': row['Natural_Gas_USD_per_GJ'],
        'Fuel_Oil_USD_per_GJ': row['Fuel_Oil_USD_per_GJ'],
        'Electricity_USD_per_GJ': row['Electricity_USD_per_GJ'],
        'Green_Hydrogen_USD_per_GJ': row['Green_Hydrogen_USD_per_GJ'],
        'Naphtha_USD_per_t': row['Naphtha_USD_per_t'],
        'LPG_USD_per_t': row['LPG_USD_per_t'],
        'Reformate_USD_per_t': row['Reformate_USD_per_t']
    }

def calculate_baseline_emissions():
    """Calculate baseline emissions from fuel and feedstock consumption (2023)"""
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    with pd.ExcelFile(data_file) as xls:
        baseline_df = pd.read_excel(xls, sheet_name='BaselineConsumption_2023')
        emission_factors_ts_df = pd.read_excel(xls, sheet_name='EmissionFactors_TimeSeries')
    
    # Get emission factors for 2023
    ef_dict = get_emission_factors_for_year(2023, emission_factors_ts_df)
    
    # Calculate emissions for each process
    total_baseline = 0.0
    baseline_df['Total_Emissions_tCO2'] = 0.0
    
    for idx, row in baseline_df.iterrows():
        activity = row['Activity_kt_product']
        
        # Fuel emissions (GJ-based)
        ng_emissions = activity * row['NaturalGas_GJ_per_t'] * ef_dict['Natural_Gas_GJ']
        oil_emissions = activity * row['FuelOil_GJ_per_t'] * ef_dict['Fuel_Oil_GJ']  
        elec_emissions = activity * row['Electricity_GJ_per_t'] * ef_dict['Electricity_GJ']
        
        # Feedstock emissions (tonne-based)
        naphtha_emissions = activity * row['Naphtha_t_per_t'] * ef_dict['Naphtha_t']
        lpg_emissions = activity * row['LPG_t_per_t'] * ef_dict['LPG_t']
        reformate_emissions = activity * row['Reformate_t_per_t'] * ef_dict['Reformate_t']
        
        total_process_emissions = ng_emissions + oil_emissions + elec_emissions + naphtha_emissions + lpg_emissions + reformate_emissions
        baseline_df.at[idx, 'Total_Emissions_tCO2'] = total_process_emissions
        total_baseline += total_process_emissions
    
    return total_baseline / 1000, baseline_df  # Convert to MtCO2

def create_optimization_data(facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df):
    """Create structured data for optimization model"""
    
    # Load baseline consumption data
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    with pd.ExcelFile(data_file) as xls:
        baseline_df = pd.read_excel(xls, sheet_name='BaselineConsumption_2023')
    
    # Time horizon
    years = list(range(2023, 2051))
    
    # Create facility-technology combinations
    deployment_options = []
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        
        for _, tech in technologies_df.merge(costs_df, on='TechID').iterrows():
            tech_id = tech['TechID']
            tech_group = tech['TechGroup']
            tech_band = tech['Band']
            
            # Get facility capacity for this technology group
            capacity_col = f"{tech_group}_Capacity_kt_per_year"
            if capacity_col in facility.index:
                baseline_capacity = facility[capacity_col]
                
                deployment_options.append({
                    'FacilityID': facility_id,
                    'TechID': tech_id,
                    'TechGroup': tech_group,
                    'Band': tech_band,
                    'Region': facility['Region'],
                    'Company': facility['Company'],
                    'BaselineCapacity_kt': baseline_capacity,
                    'CommercialYear': tech['CommercialYear'],
                    'TRL': tech['TechnicalReadiness'],
                    'Technology': tech['TechnologyCategory'],
                    'Labor_Cost_Index': facility['Labor_Cost_Index'],
                    'Electricity_Price_USD_per_MWh': facility['Electricity_Price_USD_per_MWh'],
                    'CAPEX_Million_USD_per_kt': tech['CAPEX_Million_USD_per_kt_capacity'],
                    'OPEX_Delta_USD_per_t': tech['OPEX_Delta_USD_per_t'],
                    'Lifetime_years': tech['Lifetime_years'],
                    # Fuel consumption profiles
                    'Tech_NaturalGas_GJ_per_t': tech['NaturalGas_GJ_per_t'],
                    'Tech_FuelOil_GJ_per_t': tech['FuelOil_GJ_per_t'], 
                    'Tech_Electricity_GJ_per_t': tech['Electricity_GJ_per_t'],
                    'Tech_Hydrogen_GJ_per_t': tech['Hydrogen_GJ_per_t'],
                    'Tech_Naphtha_t_per_t': tech['Naphtha_t_per_t'],
                    'Tech_LPG_t_per_t': tech['LPG_t_per_t'],
                    'Tech_Reformate_t_per_t': tech['Reformate_t_per_t']
                })
                
                # Get baseline band data
                baseline_band_data = baseline_df[(baseline_df['TechGroup'] == tech_group) & (baseline_df['Band'] == tech_band)]
                if not baseline_band_data.empty:
                    baseline_row = baseline_band_data.iloc[0]
                    deployment_options[-1].update({
                        'Baseline_NaturalGas_GJ_per_t': baseline_row['NaturalGas_GJ_per_t'],
                        'Baseline_FuelOil_GJ_per_t': baseline_row['FuelOil_GJ_per_t'],
                        'Baseline_Electricity_GJ_per_t': baseline_row['Electricity_GJ_per_t'],
                        'Baseline_Naphtha_t_per_t': baseline_row['Naphtha_t_per_t'],
                        'Baseline_LPG_t_per_t': baseline_row['LPG_t_per_t'],
                        'Baseline_Reformate_t_per_t': baseline_row['Reformate_t_per_t']
                    })
    
    return pd.DataFrame(deployment_options), years, baseline_df

def create_optimization_model(deployment_df, years, emission_factors_ts_df, fuel_costs_ts_df, baseline_emissions_mt):
    """Create the linear programming optimization model"""
    
    print("🔧 Creating optimization model...")
    
    # Create the LP problem
    prob = pulp.LpProblem("Korean_Petrochemical_MACC", pulp.LpMinimize)
    
    # Decision variables: deployment capacity [kt/year] for each facility-tech-year
    deployment_vars = {}
    for _, row in deployment_df.iterrows():
        facility_id = row['FacilityID']
        tech_id = row['TechID']
        for year in years:
            if year >= row['CommercialYear']:  # Only allow deployment after commercial year
                var_name = f"deploy_{facility_id}_{tech_id}_{year}"
                deployment_vars[(facility_id, tech_id, year)] = pulp.LpVariable(
                    var_name, 
                    lowBound=0, 
                    upBound=row['BaselineCapacity_kt']  # Can't exceed baseline capacity
                )
    
    print(f"   - Created {len(deployment_vars)} decision variables")
    
    # Objective function: Minimize total system cost
    total_cost = 0
    
    for _, row in deployment_df.iterrows():
        facility_id = row['FacilityID']
        tech_id = row['TechID']
        
        # Regional cost adjustments
        capex_multiplier = row['Labor_Cost_Index'] / 100
        opex_multiplier = row['Electricity_Price_USD_per_MWh'] / 118  # Baseline price
        
        for year in years:
            if (facility_id, tech_id, year) in deployment_vars:
                var = deployment_vars[(facility_id, tech_id, year)]
                
                # Get fuel costs for this year
                fuel_costs = get_fuel_costs_for_year(year, fuel_costs_ts_df)
                
                # CAPEX (annualized)
                lifetime = row['Lifetime_years']
                discount_rate = 0.05
                crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
                annual_capex_per_kt = row['CAPEX_Million_USD_per_kt'] * capex_multiplier * crf * 1000  # USD/kt
                
                # OPEX (baseline)
                annual_opex_per_kt = row['OPEX_Delta_USD_per_t'] * opex_multiplier * 1000  # USD/kt
                
                # Fuel cost difference (alternative vs baseline)
                if all(col in row.index for col in ['Baseline_NaturalGas_GJ_per_t', 'Tech_NaturalGas_GJ_per_t']):
                    baseline_fuel_cost = (
                        row['Baseline_NaturalGas_GJ_per_t'] * fuel_costs['Natural_Gas_USD_per_GJ'] +
                        row['Baseline_FuelOil_GJ_per_t'] * fuel_costs['Fuel_Oil_USD_per_GJ'] +
                        row['Baseline_Electricity_GJ_per_t'] * fuel_costs['Electricity_USD_per_GJ'] +
                        row['Baseline_Naphtha_t_per_t'] * fuel_costs['Naphtha_USD_per_t'] +
                        row['Baseline_LPG_t_per_t'] * fuel_costs['LPG_USD_per_t'] +
                        row['Baseline_Reformate_t_per_t'] * fuel_costs['Reformate_USD_per_t']
                    )
                    
                    alt_fuel_cost = (
                        row['Tech_NaturalGas_GJ_per_t'] * fuel_costs['Natural_Gas_USD_per_GJ'] +
                        row['Tech_FuelOil_GJ_per_t'] * fuel_costs['Fuel_Oil_USD_per_GJ'] +
                        row['Tech_Electricity_GJ_per_t'] * fuel_costs['Electricity_USD_per_GJ'] +
                        row['Tech_Hydrogen_GJ_per_t'] * fuel_costs['Green_Hydrogen_USD_per_GJ'] +
                        row['Tech_Naphtha_t_per_t'] * fuel_costs['Naphtha_USD_per_t'] +
                        row['Tech_LPG_t_per_t'] * fuel_costs['LPG_USD_per_t'] +
                        row['Tech_Reformate_t_per_t'] * fuel_costs['Reformate_USD_per_t']
                    )
                    
                    fuel_cost_delta_per_kt = (alt_fuel_cost - baseline_fuel_cost) * 1000  # USD/kt
                else:
                    fuel_cost_delta_per_kt = 0
                
                # Total annual cost per kt
                total_annual_cost_per_kt = annual_capex_per_kt + annual_opex_per_kt + fuel_cost_delta_per_kt
                
                # Add to objective function
                total_cost += var * total_annual_cost_per_kt
    
    prob += total_cost
    print("   - Objective function created: Minimize total system cost")
    
    # Constraints
    constraint_count = 0
    
    # 1. Emission target constraints
    emission_targets = {
        2030: baseline_emissions_mt * 0.85,  # 15% reduction
        2035: baseline_emissions_mt * 0.70,  # 30% reduction
        2040: baseline_emissions_mt * 0.50,  # 50% reduction
        2045: baseline_emissions_mt * 0.30,  # 70% reduction
        2050: baseline_emissions_mt * 0.20   # 80% reduction
    }
    
    for target_year, target_emissions in emission_targets.items():
        if target_year in years:
            total_emissions = 0
            
            # Baseline emissions for non-converted capacity
            for _, row in deployment_df.iterrows():
                facility_id = row['FacilityID']
                tech_group = row['TechGroup']
                band = row['Band']
                baseline_capacity = row['BaselineCapacity_kt']
                
                # Calculate baseline emissions for this facility-tech
                ef_dict = get_emission_factors_for_year(target_year, emission_factors_ts_df)
                if all(col in row.index for col in ['Baseline_NaturalGas_GJ_per_t']):
                    baseline_emissions_per_t = (
                        row['Baseline_NaturalGas_GJ_per_t'] * ef_dict['Natural_Gas_GJ'] +
                        row['Baseline_FuelOil_GJ_per_t'] * ef_dict['Fuel_Oil_GJ'] +
                        row['Baseline_Electricity_GJ_per_t'] * ef_dict['Electricity_GJ'] +
                        row['Baseline_Naphtha_t_per_t'] * ef_dict['Naphtha_t'] +
                        row['Baseline_LPG_t_per_t'] * ef_dict['LPG_t'] +
                        row['Baseline_Reformate_t_per_t'] * ef_dict['Reformate_t']
                    )
                    
                    # Calculate alternative emissions for this facility-tech  
                    alt_emissions_per_t = (
                        row['Tech_NaturalGas_GJ_per_t'] * ef_dict['Natural_Gas_GJ'] +
                        row['Tech_FuelOil_GJ_per_t'] * ef_dict['Fuel_Oil_GJ'] +
                        row['Tech_Electricity_GJ_per_t'] * ef_dict['Electricity_GJ'] +
                        row['Tech_Hydrogen_GJ_per_t'] * ef_dict['Green_Hydrogen_GJ'] +
                        row['Tech_Naphtha_t_per_t'] * ef_dict['Naphtha_t'] +
                        row['Tech_LPG_t_per_t'] * ef_dict['LPG_t'] +
                        row['Tech_Reformate_t_per_t'] * ef_dict['Reformate_t']
                    )
                    
                    # Find deployed capacity for this facility-tech in target year
                    deployed_capacity = 0
                    for tech_id_check in deployment_df[deployment_df['FacilityID'] == facility_id]['TechID'].unique():
                        if (facility_id, tech_id_check, target_year) in deployment_vars:
                            deployed_capacity += deployment_vars[(facility_id, tech_id_check, target_year)]
                    
                    # Emissions = baseline_capacity * baseline_emissions - deployed_capacity * (baseline_emissions - alt_emissions)
                    # This accounts for the fact that deployed capacity replaces baseline technology
                    remaining_baseline = baseline_capacity - deployed_capacity
                    total_emissions += remaining_baseline * baseline_emissions_per_t / 1000  # Convert to MtCO2
                    
                    if (facility_id, row['TechID'], target_year) in deployment_vars:
                        var = deployment_vars[(facility_id, row['TechID'], target_year)]
                        total_emissions += var * alt_emissions_per_t / 1000  # Convert to MtCO2
            
            # Add emission target constraint
            prob += total_emissions <= target_emissions, f"EmissionTarget_{target_year}"
            constraint_count += 1
    
    # 2. Capacity constraints - can't deploy more than baseline capacity at each facility
    for facility_id in deployment_df['FacilityID'].unique():
        facility_data = deployment_df[deployment_df['FacilityID'] == facility_id]
        
        for tech_group in facility_data['TechGroup'].unique():
            group_data = facility_data[facility_data['TechGroup'] == tech_group]
            max_capacity = group_data['BaselineCapacity_kt'].iloc[0]  # All should be the same
            
            for year in years:
                # Total deployment for this facility-tech_group cannot exceed baseline capacity
                deployed_capacity = 0
                for _, row in group_data.iterrows():
                    if (row['FacilityID'], row['TechID'], year) in deployment_vars:
                        deployed_capacity += deployment_vars[(row['FacilityID'], row['TechID'], year)]
                
                if deployed_capacity:  # Only add constraint if there are variables
                    prob += deployed_capacity <= max_capacity, f"Capacity_{facility_id}_{tech_group}_{year}"
                    constraint_count += 1
    
    print(f"   - Added {constraint_count} constraints")
    print(f"   - Emission targets: {len(emission_targets)} years")
    
    return prob, deployment_vars, emission_targets

def solve_optimization_model(prob, deployment_vars, deployment_df, years):
    """Solve the optimization model and extract results"""
    
    print("\n🔍 Solving optimization model...")
    
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=1))
    
    # Check the solution status
    status = pulp.LpStatus[prob.status]
    print(f"   - Solution Status: {status}")
    
    if status != 'Optimal':
        print(f"   - ⚠️ Warning: Solution is not optimal!")
        return None, None
    
    # Extract solution
    results = []
    total_cost = 0
    
    for (facility_id, tech_id, year), var in deployment_vars.items():
        if var.value() and var.value() > 0.1:  # Only include meaningful deployments
            
            # Find the corresponding row in deployment_df
            row_data = deployment_df[
                (deployment_df['FacilityID'] == facility_id) & 
                (deployment_df['TechID'] == tech_id)
            ]
            
            if not row_data.empty:
                row = row_data.iloc[0]
                deployment_kt = var.value()
                
                results.append({
                    'Year': year,
                    'FacilityID': facility_id,
                    'TechID': tech_id,
                    'Technology': row['Technology'],
                    'Region': row['Region'],
                    'Company': row['Company'],
                    'TechGroup': row['TechGroup'],
                    'DeploymentCapacity_kt': deployment_kt,
                    'BaselineCapacity_kt': row['BaselineCapacity_kt']
                })
        
        # Note: Total cost is already calculated by the solver and available as prob.objective.value()
    
    results_df = pd.DataFrame(results)
    
    # Get optimal objective value from the problem
    optimal_cost = prob.objective.value()
    
    print(f"   - Optimal objective value: ${optimal_cost/1e9:.2f} billion")
    print(f"   - Number of deployments: {len(results_df)}")
    
    return results_df, optimal_cost

def analyze_optimization_results(results_df, deployment_df, years, emission_factors_ts_df, baseline_emissions_mt):
    """Analyze optimization results and create pathway data"""
    
    print("\n📊 Analyzing optimization results...")
    
    pathway_data = []
    
    for year in years:
        year_results = results_df[results_df['Year'] == year] if not results_df.empty else pd.DataFrame()
        
        # Calculate emissions for this year
        ef_dict = get_emission_factors_for_year(year, emission_factors_ts_df)
        
        total_emissions = 0
        total_investment = 0
        total_deployed_capacity = 0
        
        # Calculate emissions from deployed technologies
        for _, deployment in year_results.iterrows():
            facility_id = deployment['FacilityID']
            tech_id = deployment['TechID']
            deployed_capacity = deployment['DeploymentCapacity_kt']
            
            # Find technology data
            tech_data = deployment_df[
                (deployment_df['FacilityID'] == facility_id) & 
                (deployment_df['TechID'] == tech_id)
            ]
            
            if not tech_data.empty:
                row = tech_data.iloc[0]
                
                # Calculate alternative technology emissions
                if all(col in row.index for col in ['Tech_NaturalGas_GJ_per_t']):
                    alt_emissions_per_t = (
                        row['Tech_NaturalGas_GJ_per_t'] * ef_dict['Natural_Gas_GJ'] +
                        row['Tech_FuelOil_GJ_per_t'] * ef_dict['Fuel_Oil_GJ'] +
                        row['Tech_Electricity_GJ_per_t'] * ef_dict['Electricity_GJ'] +
                        row['Tech_Hydrogen_GJ_per_t'] * ef_dict['Green_Hydrogen_GJ'] +
                        row['Tech_Naphtha_t_per_t'] * ef_dict['Naphtha_t'] +
                        row['Tech_LPG_t_per_t'] * ef_dict['LPG_t'] +
                        row['Tech_Reformate_t_per_t'] * ef_dict['Reformate_t']
                    )
                    
                    total_emissions += deployed_capacity * alt_emissions_per_t / 1000  # MtCO2
                
                # Calculate investment
                capex_multiplier = row['Labor_Cost_Index'] / 100
                total_investment += deployed_capacity * row['CAPEX_Million_USD_per_kt'] * capex_multiplier / 1000  # Billion USD
                
                total_deployed_capacity += deployed_capacity
        
        # Add baseline emissions for non-deployed capacity
        # Approximate by assuming total baseline minus deployed gets baseline emissions
        remaining_baseline_fraction = 1.0 - min(0.8, total_deployed_capacity / 25000)  # Rough approximation
        baseline_emissions_year = baseline_emissions_mt * remaining_baseline_fraction
        
        total_emissions += baseline_emissions_year
        
        emission_reduction = baseline_emissions_mt - total_emissions
        
        pathway_data.append({
            'Year': year,
            'BaselineEmissions_MtCO2': baseline_emissions_mt,
            'OptimizedEmissions_MtCO2': total_emissions,
            'EmissionReduction_MtCO2': emission_reduction,
            'CumulativeInvestment_Billion_USD': total_investment,
            'TotalDeployedCapacity_kt': total_deployed_capacity
        })
    
    pathway_df = pd.DataFrame(pathway_data)
    
    print(f"   - 2030 optimized emissions: {pathway_df[pathway_df['Year'] == 2030]['OptimizedEmissions_MtCO2'].iloc[0]:.1f} MtCO2")
    print(f"   - 2050 optimized emissions: {pathway_df[pathway_df['Year'] == 2050]['OptimizedEmissions_MtCO2'].iloc[0]:.1f} MtCO2")
    print(f"   - Total investment by 2050: ${pathway_df['CumulativeInvestment_Billion_USD'].max():.1f} billion")
    
    return pathway_df

def plot_optimization_results(pathway_df, baseline_emissions_mt):
    """Create plots for optimization results"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Optimized Emission Pathway
    ax1.plot(pathway_df['Year'], pathway_df['BaselineEmissions_MtCO2'], 
             'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
    ax1.plot(pathway_df['Year'], pathway_df['OptimizedEmissions_MtCO2'], 
             'r-', linewidth=3, label='Optimized Pathway')
    ax1.fill_between(pathway_df['Year'], pathway_df['OptimizedEmissions_MtCO2'], 
                     pathway_df['BaselineEmissions_MtCO2'], alpha=0.3, color='red', label='Emission Reduction')
    
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
    
    # 2. Emission Reduction Progress
    ax2.plot(pathway_df['Year'], pathway_df['EmissionReduction_MtCO2'], 
             'g-', linewidth=3, marker='o', markersize=4)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Emission Reduction (MtCO2/year)')
    ax2.set_title('Emission Reduction Achievement')
    ax2.grid(True, alpha=0.3)
    
    # 3. Cumulative Investment
    ax3.plot(pathway_df['Year'], pathway_df['CumulativeInvestment_Billion_USD'], 
             'b-', linewidth=3, marker='s', markersize=4)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Cumulative Investment (Billion USD)')
    ax3.set_title('Required Investment for Optimized Pathway')
    ax3.grid(True, alpha=0.3)
    
    # 4. Deployment Capacity
    ax4.plot(pathway_df['Year'], pathway_df['TotalDeployedCapacity_kt'], 
             'purple', linewidth=3, marker='^', markersize=4)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Total Deployed Capacity (kt/year)')
    ax4.set_title('Technology Deployment Evolution')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def main():
    """Main execution function for optimization model"""
    
    print("🏭 Korean Petrochemical MACC Optimization Model")
    print("=" * 55)
    
    # Load data
    print("📊 Loading regional facilities and technology data...")
    facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df = load_regional_data()
    
    print(f"   - Facilities: {len(facilities_df)} across {facilities_df['Region'].nunique()} regions")
    print(f"   - Technologies: {len(technologies_df)} alternative technologies (Green H2 only)")
    print(f"   - Companies: {facilities_df['Company'].nunique()}")
    print(f"   - Time series data: 2023-2050 emission factors and fuel costs")
    
    # Calculate baseline
    baseline_emissions_mt, baseline_df = calculate_baseline_emissions()
    print(f"   - 2023 baseline emissions: {baseline_emissions_mt:.1f} MtCO2/year")
    
    # Create optimization data
    print("\n🔧 Preparing optimization data...")
    deployment_df, years, baseline_df = create_optimization_data(facilities_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df)
    
    print(f"   - Deployment options: {len(deployment_df)}")
    print(f"   - Time horizon: {len(years)} years ({min(years)}-{max(years)})")
    
    # Create and solve optimization model
    prob, deployment_vars, emission_targets = create_optimization_model(deployment_df, years, emission_factors_ts_df, fuel_costs_ts_df, baseline_emissions_mt)
    
    # Solve the model
    results_df, total_cost = solve_optimization_model(prob, deployment_vars, deployment_df, years)
    
    if results_df is not None:
        # Analyze results
        pathway_df = analyze_optimization_results(results_df, deployment_df, years, emission_factors_ts_df, baseline_emissions_mt)
        
        # Save outputs
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving optimization outputs to {output_dir}/...")
        
        # Save detailed results
        results_df.to_csv(output_dir / "optimization_deployments.csv", index=False)
        pathway_df.to_csv(output_dir / "optimization_pathway_2023_2050.csv", index=False)
        
        # Create and save plots
        print("\n📊 Creating optimization analysis plots...")
        fig = plot_optimization_results(pathway_df, baseline_emissions_mt)
        fig.savefig(output_dir / "optimization_analysis_2023_2050.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # Print key results
        print("\n🎯 OPTIMIZATION RESULTS:")
        print(f"   - Total system cost: ${total_cost/1e9:.2f} billion")
        print(f"   - 2030 optimized emissions: {pathway_df[pathway_df['Year'] == 2030]['OptimizedEmissions_MtCO2'].iloc[0]:.1f} MtCO2/year")
        print(f"   - 2050 optimized emissions: {pathway_df[pathway_df['Year'] == 2050]['OptimizedEmissions_MtCO2'].iloc[0]:.1f} MtCO2/year")
        print(f"   - Total reduction by 2050: {pathway_df[pathway_df['Year'] == 2050]['EmissionReduction_MtCO2'].iloc[0]:.1f} MtCO2/year")
        
        print("\n🏆 EMISSION TARGETS ACHIEVEMENT:")
        for year, target in emission_targets.items():
            if year in pathway_df['Year'].values:
                actual = pathway_df[pathway_df['Year'] == year]['OptimizedEmissions_MtCO2'].iloc[0]
                status = "✅ Met" if actual <= target else "❌ Missed"
                print(f"   - {year}: Target {target:.1f}, Actual {actual:.1f} MtCO2/year {status}")
        
        print(f"\n✅ Optimization Model completed successfully! Check {output_dir}/ for detailed results.")
        
    else:
        print("\n❌ Optimization failed. Check model constraints and data.")

if __name__ == "__main__":
    main()