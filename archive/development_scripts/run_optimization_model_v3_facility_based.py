#!/usr/bin/env python3
"""
Korean Petrochemical MACC Optimization Model V3 - Facility-Based
==============================================================

This version is completely updated for the new facility-based Excel structure.
Optimizes technology deployment across facilities to meet emission reduction targets
while minimizing total system costs.

Key Features:
- Facility-level optimization (8 facilities across 3 regions)
- Time-dynamic emission factors and fuel costs
- Green hydrogen integration with cost learning curves
- Technology readiness constraints
- Regional deployment constraints
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pulp
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

def load_facility_based_data():
    """Load the updated facility-based Excel database"""
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    print("LOADING FACILITY-BASED DATABASE")
    print("=" * 50)
    print(f"Path: {data_file}")
    
    with pd.ExcelFile(data_file) as xls:
        facilities_df = pd.read_excel(xls, sheet_name='RegionalFacilities')
        consumption_df = pd.read_excel(xls, sheet_name='FacilityBaselineConsumption_2023')
        technologies_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
        costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
        emission_factors_ts_df = pd.read_excel(xls, sheet_name='EmissionFactors_TimeSeries')
        fuel_costs_ts_df = pd.read_excel(xls, sheet_name='FuelCosts_TimeSeries')
        targets_df = pd.read_excel(xls, sheet_name='EmissionsTargets')
    
    print(f"\nLoaded sheets:")
    print(f"  • RegionalFacilities: {facilities_df.shape[0]} facilities")
    print(f"  • FacilityBaselineConsumption_2023: {consumption_df.shape[0]} process records")
    print(f"  • AlternativeTechnologies: {technologies_df.shape[0]} technologies")
    print(f"  • AlternativeCosts: {costs_df.shape[0]} cost records")
    print(f"  • EmissionFactors_TimeSeries: {emission_factors_ts_df.shape[0]} years")
    print(f"  • FuelCosts_TimeSeries: {fuel_costs_ts_df.shape[0]} years")
    print(f"  • EmissionsTargets: {targets_df.shape[0]} targets")
    
    return facilities_df, consumption_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, targets_df

def calculate_facility_baseline_emissions(consumption_df, emission_factors_ts_df, year=2023):
    """Calculate baseline emissions for each facility-process combination"""
    
    # Get emission factors for the specified year
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == year].iloc[0]
    
    emissions_data = []
    
    for _, row in consumption_df.iterrows():
        # Calculate emissions by source
        ng_consumption_gj = row['Activity_kt_product'] * row['NaturalGas_GJ_per_t'] * 1000
        ng_emissions = ng_consumption_gj * ef_year['Natural_Gas_tCO2_per_GJ'] / 1000  # ktCO2
        
        fo_consumption_gj = row['Activity_kt_product'] * row['FuelOil_GJ_per_t'] * 1000
        fo_emissions = fo_consumption_gj * ef_year['Fuel_Oil_tCO2_per_GJ'] / 1000
        
        elec_consumption_gj = row['Activity_kt_product'] * row['Electricity_GJ_per_t'] * 1000
        elec_emissions = elec_consumption_gj * ef_year['Electricity_tCO2_per_GJ'] / 1000
        
        # Feedstock emissions
        naphtha_emissions = row['Activity_kt_product'] * row['Naphtha_t_per_t'] * ef_year['Naphtha_tCO2_per_t'] / 1000
        lpg_emissions = row['Activity_kt_product'] * row['LPG_t_per_t'] * ef_year['LPG_tCO2_per_t'] / 1000
        reformate_emissions = row['Activity_kt_product'] * row['Reformate_t_per_t'] * ef_year['Reformate_tCO2_per_t'] / 1000
        
        total_emissions = (ng_emissions + fo_emissions + elec_emissions + 
                          naphtha_emissions + lpg_emissions + reformate_emissions)
        
        emissions_data.append({
            'FacilityID': row['FacilityID'],
            'Company': row['Company'],
            'Region': row['Region'],
            'ProcessType': row['ProcessType'],
            'Capacity_kt_per_year': row['Activity_kt_product'],
            'BaselineEmissions_ktCO2_per_year': total_emissions,
            'EmissionIntensity_tCO2_per_t': total_emissions * 1000 / row['Activity_kt_product']
        })
    
    return pd.DataFrame(emissions_data)

def create_facility_technology_options(facilities_df, consumption_df, technologies_df, costs_df, 
                                      emission_factors_ts_df, fuel_costs_ts_df, target_year):
    """Create technology deployment options for each facility-process combination"""
    
    print(f"\nCreating technology options for {target_year}...")
    
    # Get year-specific factors
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == target_year].iloc[0]
    fc_year = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == target_year].iloc[0]
    
    # Merge technology and cost data
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    
    deployment_options = []
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        
        # Get baseline consumption for this facility
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        for _, process_row in facility_consumption.iterrows():
            process_type = process_row['ProcessType']
            capacity = process_row['Activity_kt_product']
            
            # Get applicable technologies for this process type
            applicable_techs = tech_costs[
                (tech_costs['TechGroup'] == process_type) &
                (tech_costs['CommercialYear'] <= target_year) &
                (tech_costs['TechnicalReadiness'] >= facility['TechnicalReadiness_Level'])
            ]
            
            # Calculate baseline emissions for this process
            baseline_emissions = calculate_process_baseline_emissions(
                process_row, ef_year
            )
            
            for _, tech in applicable_techs.iterrows():
                # Calculate alternative emissions
                alt_emissions = calculate_alternative_emissions(
                    tech, capacity, ef_year
                )
                
                # Calculate costs
                costs_result = calculate_technology_costs(
                    tech, capacity, fc_year, facility
                )
                
                # Calculate abatement potential
                abatement_potential = baseline_emissions - alt_emissions
                abatement_rate = abatement_potential / capacity  # tCO2 per t product
                
                # Calculate LCOA (Levelized Cost of Abatement)
                if abatement_potential > 0:
                    lcoa = costs_result['AnnualCost_USD'] / abatement_potential
                else:
                    lcoa = np.inf
                
                deployment_options.append({
                    'FacilityID': facility_id,
                    'Company': facility['Company'],
                    'Region': facility['Region'],
                    'ProcessType': process_type,
                    'TechID': tech['TechID'],
                    'TechnologyCategory': tech['TechnologyCategory'],
                    'Capacity_kt_per_year': capacity,
                    'BaselineEmissions_ktCO2': baseline_emissions,
                    'AlternativeEmissions_ktCO2': alt_emissions,
                    'AbatementPotential_ktCO2': abatement_potential,
                    'AbatementRate_tCO2_per_t': abatement_rate,
                    'CAPEX_Million_USD': costs_result['CAPEX_Million_USD'],
                    'AnnualCost_USD': costs_result['AnnualCost_USD'],
                    'LCOA_USD_per_tCO2': lcoa,
                    'TechnicalReadiness': tech['TechnicalReadiness'],
                    'CommercialYear': tech['CommercialYear'],
                    'InfrastructureScore': facility['Infrastructure_Score']
                })
    
    deployment_df = pd.DataFrame(deployment_options)
    
    # Filter to positive abatement and reasonable costs
    viable_options = deployment_df[
        (deployment_df['AbatementPotential_ktCO2'] > 0) &
        (deployment_df['LCOA_USD_per_tCO2'] < 25000) &  # Increased threshold for petrochemicals
        (deployment_df['LCOA_USD_per_tCO2'] > 0)
    ].copy()
    
    print(f"  • Total technology options: {len(deployment_df)}")
    print(f"  • Viable options (positive abatement, reasonable cost): {len(viable_options)}")
    
    return viable_options

def calculate_process_baseline_emissions(process_row, ef_year):
    """Calculate baseline emissions for a single process"""
    capacity = process_row['Activity_kt_product']
    
    # Fuel emissions
    ng_consumption = capacity * process_row['NaturalGas_GJ_per_t'] * 1000
    ng_emissions = ng_consumption * ef_year['Natural_Gas_tCO2_per_GJ'] / 1000
    
    fo_consumption = capacity * process_row['FuelOil_GJ_per_t'] * 1000
    fo_emissions = fo_consumption * ef_year['Fuel_Oil_tCO2_per_GJ'] / 1000
    
    elec_consumption = capacity * process_row['Electricity_GJ_per_t'] * 1000
    elec_emissions = elec_consumption * ef_year['Electricity_tCO2_per_GJ'] / 1000
    
    # Feedstock emissions (if columns exist)
    naphtha_emissions = 0
    lpg_emissions = 0
    reformate_emissions = 0
    
    if 'Naphtha_t_per_t' in process_row.index:
        naphtha_emissions = capacity * process_row['Naphtha_t_per_t'] * ef_year['Naphtha_tCO2_per_t'] / 1000
    if 'LPG_t_per_t' in process_row.index:
        lpg_emissions = capacity * process_row['LPG_t_per_t'] * ef_year['LPG_tCO2_per_t'] / 1000
    if 'Reformate_t_per_t' in process_row.index:
        reformate_emissions = capacity * process_row['Reformate_t_per_t'] * ef_year['Reformate_tCO2_per_t'] / 1000
    
    return ng_emissions + fo_emissions + elec_emissions + naphtha_emissions + lpg_emissions + reformate_emissions

def calculate_alternative_emissions(tech, capacity, ef_year):
    """Calculate emissions for alternative technology"""
    # Alternative fuel consumption
    ng_consumption = capacity * tech.get('NaturalGas_GJ_per_t', 0) * 1000
    ng_emissions = ng_consumption * ef_year['Natural_Gas_tCO2_per_GJ'] / 1000
    
    fo_consumption = capacity * tech.get('FuelOil_GJ_per_t', 0) * 1000
    fo_emissions = fo_consumption * ef_year['Fuel_Oil_tCO2_per_GJ'] / 1000
    
    elec_consumption = capacity * tech.get('Electricity_GJ_per_t', 0) * 1000
    elec_emissions = elec_consumption * ef_year['Electricity_tCO2_per_GJ'] / 1000
    
    # Green hydrogen (zero emissions)
    h2_consumption = capacity * tech.get('Hydrogen_GJ_per_t', 0) * 1000
    h2_emissions = h2_consumption * ef_year['Green_Hydrogen_tCO2_per_GJ'] / 1000  # Should be 0
    
    # Alternative feedstock (if columns exist)
    naphtha_emissions = capacity * tech.get('Naphtha_t_per_t', 0) * ef_year['Naphtha_tCO2_per_t'] / 1000
    lpg_emissions = capacity * tech.get('LPG_t_per_t', 0) * ef_year['LPG_tCO2_per_t'] / 1000
    reformate_emissions = capacity * tech.get('Reformate_t_per_t', 0) * ef_year['Reformate_tCO2_per_t'] / 1000
    
    return ng_emissions + fo_emissions + elec_emissions + h2_emissions + naphtha_emissions + lpg_emissions + reformate_emissions

def calculate_technology_costs(tech, capacity, fc_year, facility):
    """Calculate total costs for technology deployment"""
    
    # CAPEX calculation
    capex_per_kt = tech['CAPEX_Million_USD_per_kt_capacity']
    total_capex = capex_per_kt * capacity
    
    # Regional cost adjustment
    regional_multiplier = facility['Labor_Cost_Index'] / 100
    adjusted_capex = total_capex * regional_multiplier
    
    # Annual CAPEX (simplified annualization)
    lifetime = tech['Lifetime_years']
    discount_rate = 0.08  # 8% WACC
    annuity_factor = discount_rate / (1 - (1 + discount_rate) ** (-lifetime))
    annual_capex = adjusted_capex * 1000000 * annuity_factor  # Convert to USD
    
    # OPEX calculation
    annual_opex_delta = tech['OPEX_Delta_USD_per_t'] * capacity * 1000  # USD per year
    
    # Fuel cost delta
    fuel_cost_delta = 0
    
    # Estimate fuel cost impact based on technology type
    if 'Electric' in tech['TechnologyCategory'] or 'E-cracker' in tech['TechnologyCategory']:
        # Electric technologies - electricity cost impact
        elec_consumption_delta = capacity * (tech['Electricity_GJ_per_t'] - 1.8) * 1000  # Assume 1.8 GJ/t baseline
        fuel_cost_delta = elec_consumption_delta * fc_year['Electricity_USD_per_GJ']
    elif 'H2' in tech['TechnologyCategory']:
        # Hydrogen technologies
        h2_consumption = capacity * tech['Hydrogen_GJ_per_t'] * 1000
        fuel_cost_delta = h2_consumption * fc_year['Green_Hydrogen_USD_per_GJ']
    
    # Maintenance costs
    maintenance_cost = adjusted_capex * 1000000 * (tech['MaintenanceCost_Pct'] / 100)
    
    # Total annual cost
    total_annual_cost = annual_capex + annual_opex_delta + fuel_cost_delta + maintenance_cost
    
    return {
        'CAPEX_Million_USD': adjusted_capex,
        'AnnualCAPEX_USD': annual_capex,
        'AnnualOPEX_USD': annual_opex_delta,
        'AnnualFuelCost_USD': fuel_cost_delta,
        'AnnualMaintenance_USD': maintenance_cost,
        'AnnualCost_USD': total_annual_cost
    }

def setup_optimization_problem(viable_options, baseline_emissions_df, targets_df, target_year):
    """Set up the linear programming optimization problem"""
    
    print(f"\nSetting up optimization problem for {target_year}...")
    
    # Get emission reduction target for this year
    year_target = targets_df[targets_df['Year'] == target_year]
    if len(year_target) == 0:
        # Interpolate target if not directly available
        reduction_pct = interpolate_target(targets_df, target_year)
    else:
        reduction_pct = year_target['Reduction_Pct'].iloc[0]
    
    # Calculate required emission reduction
    total_baseline_emissions = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    required_reduction = total_baseline_emissions * (reduction_pct / 100)
    
    print(f"  • Target year: {target_year}")
    print(f"  • Reduction target: {reduction_pct}%")
    print(f"  • Total baseline emissions: {total_baseline_emissions:.1f} ktCO2/year")
    print(f"  • Required reduction: {required_reduction:.1f} ktCO2/year")
    
    # Create optimization problem
    prob = pulp.LpProblem("Korean_Petrochemical_MACC_Optimization", pulp.LpMinimize)
    
    # Decision variables: deployment level (0-1) for each technology option
    deployment_vars = {}
    for idx, row in viable_options.iterrows():
        var_name = f"deploy_{row['FacilityID']}_{row['ProcessType']}_{row['TechID']}"
        deployment_vars[(row['FacilityID'], row['ProcessType'], row['TechID'])] = pulp.LpVariable(
            var_name, 0, 1, pulp.LpContinuous
        )
    
    print(f"  • Decision variables: {len(deployment_vars)}")
    
    # Objective function: minimize total system cost
    objective = pulp.lpSum([
        viable_options.loc[idx, 'AnnualCost_USD'] * 
        deployment_vars[(row['FacilityID'], row['ProcessType'], row['TechID'])]
        for idx, row in viable_options.iterrows()
        if (row['FacilityID'], row['ProcessType'], row['TechID']) in deployment_vars
    ])
    
    prob += objective, "Total_System_Cost"
    
    # Constraint 1: Meet emission reduction target
    total_abatement = pulp.lpSum([
        viable_options.loc[idx, 'AbatementPotential_ktCO2'] * 
        deployment_vars[(row['FacilityID'], row['ProcessType'], row['TechID'])]
        for idx, row in viable_options.iterrows()
        if (row['FacilityID'], row['ProcessType'], row['TechID']) in deployment_vars
    ])
    
    prob += total_abatement >= required_reduction, "Emission_Reduction_Target"
    
    # Constraint 2: At most one technology per facility-process combination
    facility_process_combinations = viable_options[['FacilityID', 'ProcessType']].drop_duplicates()
    
    for _, combo in facility_process_combinations.iterrows():
        facility_id = combo['FacilityID']
        process_type = combo['ProcessType']
        
        # Get all technology options for this facility-process combo
        applicable_vars = [
            deployment_vars[(row['FacilityID'], row['ProcessType'], row['TechID'])]
            for idx, row in viable_options.iterrows()
            if (row['FacilityID'] == facility_id and 
                row['ProcessType'] == process_type and
                (row['FacilityID'], row['ProcessType'], row['TechID']) in deployment_vars)
        ]
        
        if applicable_vars:
            constraint_name = f"Max_One_Tech_{facility_id}_{process_type}"
            prob += pulp.lpSum(applicable_vars) <= 1, constraint_name
    
    # Constraint 3: Technology readiness constraints (higher TRL preferred for early deployment)
    if target_year <= 2030:
        high_trl_vars = [
            deployment_vars[(row['FacilityID'], row['ProcessType'], row['TechID'])]
            for idx, row in viable_options.iterrows()
            if (row['TechnicalReadiness'] >= 7 and
                (row['FacilityID'], row['ProcessType'], row['TechID']) in deployment_vars)
        ]
        
        if high_trl_vars:
            prob += pulp.lpSum(high_trl_vars) >= 0.7 * len(high_trl_vars), "High_TRL_Preference_2030"
    
    print(f"  • Constraints added: {len(prob.constraints)}")
    
    return prob, deployment_vars, required_reduction, total_baseline_emissions

def interpolate_target(targets_df, target_year):
    """Interpolate emission reduction target for years not directly specified"""
    targets_sorted = targets_df.sort_values('Year')
    
    if target_year <= targets_sorted['Year'].min():
        return targets_sorted['Reduction_Pct'].iloc[0]
    elif target_year >= targets_sorted['Year'].max():
        return targets_sorted['Reduction_Pct'].iloc[-1]
    else:
        # Linear interpolation
        return np.interp(target_year, targets_sorted['Year'], targets_sorted['Reduction_Pct'])

def solve_optimization(prob, deployment_vars, viable_options):
    """Solve the optimization problem"""
    
    print("\nSOLVING OPTIMIZATION PROBLEM...")
    
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Check solution status
    status = pulp.LpStatus[prob.status]
    print(f"  • Solution status: {status}")
    
    if status == 'Optimal':
        print(f"  • Optimal objective value: ${prob.objective.value():,.0f} per year")
        
        # Extract solution
        solution_data = []
        
        for idx, row in viable_options.iterrows():
            key = (row['FacilityID'], row['ProcessType'], row['TechID'])
            if key in deployment_vars:
                deployment_level = deployment_vars[key].value()
                if deployment_level is not None and deployment_level > 0.01:  # Only significant deployments
                    solution_data.append({
                        'FacilityID': row['FacilityID'],
                        'Company': row['Company'],
                        'Region': row['Region'],
                        'ProcessType': row['ProcessType'],
                        'TechID': row['TechID'],
                        'TechnologyCategory': row['TechnologyCategory'],
                        'Capacity_kt_per_year': row['Capacity_kt_per_year'],
                        'DeploymentLevel': deployment_level,
                        'DeployedCapacity_kt_per_year': row['Capacity_kt_per_year'] * deployment_level,
                        'AbatementAchieved_ktCO2': row['AbatementPotential_ktCO2'] * deployment_level,
                        'AnnualCost_USD': row['AnnualCost_USD'] * deployment_level,
                        'LCOA_USD_per_tCO2': row['LCOA_USD_per_tCO2']
                    })
        
        solution_df = pd.DataFrame(solution_data)
        
        if len(solution_df) > 0:
            print(f"  • Technologies deployed: {len(solution_df)}")
            print(f"  • Total abatement achieved: {solution_df['AbatementAchieved_ktCO2'].sum():.1f} ktCO2/year")
            print(f"  • Total annual cost: ${solution_df['AnnualCost_USD'].sum():,.0f} per year")
        
        return solution_df, status
    
    else:
        print(f"  ❌ Optimization failed with status: {status}")
        return pd.DataFrame(), status

def analyze_optimization_results(solution_df, target_year, required_reduction, total_baseline_emissions):
    """Analyze and summarize optimization results"""
    
    if len(solution_df) == 0:
        print(f"\n❌ No solution found for {target_year}")
        return {}
    
    print(f"\nOPTIMIZATION RESULTS ANALYSIS - {target_year}")
    print("=" * 50)
    
    # Overall metrics
    total_abatement = solution_df['AbatementAchieved_ktCO2'].sum()
    total_cost = solution_df['AnnualCost_USD'].sum()
    avg_lcoa = solution_df['AnnualCost_USD'].sum() / solution_df['AbatementAchieved_ktCO2'].sum()
    
    reduction_achieved = (total_abatement / total_baseline_emissions) * 100
    
    print(f"\n1. OVERALL PERFORMANCE:")
    print(f"   • Total abatement: {total_abatement:.1f} ktCO2/year")
    print(f"   • Required abatement: {required_reduction:.1f} ktCO2/year")
    print(f"   • Achievement rate: {(total_abatement/required_reduction*100):.1f}%")
    print(f"   • Emission reduction: {reduction_achieved:.1f}% vs baseline")
    print(f"   • Total annual cost: ${total_cost:,.0f} per year")
    print(f"   • Average LCOA: ${avg_lcoa:.0f} per tCO2")
    
    # Technology deployment analysis
    tech_deployment = solution_df.groupby('TechnologyCategory').agg({
        'DeployedCapacity_kt_per_year': 'sum',
        'AbatementAchieved_ktCO2': 'sum',
        'AnnualCost_USD': 'sum'
    }).sort_values('AbatementAchieved_ktCO2', ascending=False)
    
    print(f"\n2. TECHNOLOGY DEPLOYMENT:")
    for tech_cat, row in tech_deployment.iterrows():
        share = row['AbatementAchieved_ktCO2'] / total_abatement * 100
        lcoa = row['AnnualCost_USD'] / row['AbatementAchieved_ktCO2'] if row['AbatementAchieved_ktCO2'] > 0 else 0
        print(f"   • {tech_cat}: {row['AbatementAchieved_ktCO2']:.1f} ktCO2/year ({share:.1f}%) - ${lcoa:.0f}/tCO2")
    
    # Regional deployment
    regional_deployment = solution_df.groupby('Region').agg({
        'DeployedCapacity_kt_per_year': 'sum',
        'AbatementAchieved_ktCO2': 'sum',
        'AnnualCost_USD': 'sum'
    }).sort_values('AbatementAchieved_ktCO2', ascending=False)
    
    print(f"\n3. REGIONAL DEPLOYMENT:")
    for region, row in regional_deployment.iterrows():
        share = row['AbatementAchieved_ktCO2'] / total_abatement * 100
        print(f"   • {region}: {row['AbatementAchieved_ktCO2']:.1f} ktCO2/year ({share:.1f}%)")
    
    # Process deployment
    process_deployment = solution_df.groupby('ProcessType').agg({
        'DeployedCapacity_kt_per_year': 'sum',
        'AbatementAchieved_ktCO2': 'sum'
    }).sort_values('AbatementAchieved_ktCO2', ascending=False)
    
    print(f"\n4. PROCESS TYPE DEPLOYMENT:")
    for process, row in process_deployment.iterrows():
        share = row['AbatementAchieved_ktCO2'] / total_abatement * 100
        print(f"   • {process}: {row['AbatementAchieved_ktCO2']:.1f} ktCO2/year ({share:.1f}%)")
    
    return {
        'Year': target_year,
        'TotalAbatement_ktCO2': total_abatement,
        'RequiredAbatement_ktCO2': required_reduction,
        'AchievementRate_Pct': total_abatement/required_reduction*100,
        'EmissionReduction_Pct': reduction_achieved,
        'TotalAnnualCost_USD': total_cost,
        'AverageLCOA_USD_per_tCO2': avg_lcoa,
        'TechnologiesDeployed': len(solution_df),
        'FacilitiesInvolved': solution_df['FacilityID'].nunique()
    }

def create_optimization_visualizations(all_results, all_solutions):
    """Create comprehensive visualizations of optimization results"""
    
    print("\nCREATING OPTIMIZATION VISUALIZATIONS...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Korean Petrochemical MACC Optimization Results (Facility-Based)', fontsize=16, fontweight='bold')
    
    # 1. Emission reduction pathway
    years = [r['Year'] for r in all_results]
    achieved_reductions = [r['EmissionReduction_Pct'] for r in all_results]
    
    axes[0,0].plot(years, achieved_reductions, 'o-', linewidth=3, markersize=8, color='green')
    axes[0,0].set_title('Emission Reduction Pathway')
    axes[0,0].set_ylabel('Emission Reduction (%)')
    axes[0,0].set_xlabel('Year')
    axes[0,0].grid(True, alpha=0.3)
    
    # Add target line (80% by 2050)
    axes[0,0].axhline(y=80, color='red', linestyle='--', alpha=0.7, label='2050 Target (80%)')
    axes[0,0].legend()
    
    # 2. Total system costs
    total_costs = [r['TotalAnnualCost_USD']/1e9 for r in all_results]  # Billion USD
    
    axes[0,1].bar(years, total_costs, color='steelblue', alpha=0.7)
    axes[0,1].set_title('Total System Costs')
    axes[0,1].set_ylabel('Annual Cost (Billion USD)')
    axes[0,1].set_xlabel('Year')
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. Average LCOA evolution
    avg_lcoa = [r['AverageLCOA_USD_per_tCO2'] for r in all_results]
    
    axes[0,2].plot(years, avg_lcoa, 's-', linewidth=3, markersize=8, color='orange')
    axes[0,2].set_title('Average Cost of Abatement')
    axes[0,2].set_ylabel('LCOA (USD per tCO2)')
    axes[0,2].set_xlabel('Year')
    axes[0,2].grid(True, alpha=0.3)
    
    # 4. Technology deployment over time
    all_tech_deployment = pd.concat([
        df.assign(Year=year) for year, df in all_solutions.items()
    ])
    
    tech_by_year = all_tech_deployment.groupby(['Year', 'TechnologyCategory'])['AbatementAchieved_ktCO2'].sum().unstack(fill_value=0)
    tech_by_year.plot(kind='bar', stacked=True, ax=axes[1,0])
    axes[1,0].set_title('Technology Deployment Evolution')
    axes[1,0].set_ylabel('Abatement (ktCO2/year)')
    axes[1,0].set_xlabel('Year')
    axes[1,0].tick_params(axis='x', rotation=0)
    axes[1,0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 5. Regional deployment distribution (latest year)
    latest_year = max(years)
    latest_solution = all_solutions[latest_year]
    
    regional_dist = latest_solution.groupby('Region')['AbatementAchieved_ktCO2'].sum()
    regional_dist.plot(kind='pie', ax=axes[1,1], autopct='%1.1f%%')
    axes[1,1].set_title(f'Regional Distribution ({latest_year})')
    axes[1,1].set_ylabel('')
    
    # 6. Cost vs abatement efficiency
    facilities_efficiency = latest_solution.groupby('FacilityID').agg({
        'AbatementAchieved_ktCO2': 'sum',
        'AnnualCost_USD': 'sum',
        'Company': 'first'
    }).reset_index()
    
    facilities_efficiency['LCOA'] = facilities_efficiency['AnnualCost_USD'] / facilities_efficiency['AbatementAchieved_ktCO2']
    
    scatter = axes[1,2].scatter(facilities_efficiency['AbatementAchieved_ktCO2'], 
                               facilities_efficiency['LCOA'],
                               s=100, alpha=0.7, c=range(len(facilities_efficiency)), cmap='tab10')
    axes[1,2].set_xlabel('Abatement Achieved (ktCO2/year)')
    axes[1,2].set_ylabel('LCOA (USD per tCO2)')
    axes[1,2].set_title(f'Facility Efficiency ({latest_year})')
    axes[1,2].grid(True, alpha=0.3)
    
    # Add facility labels
    for _, row in facilities_efficiency.iterrows():
        axes[1,2].annotate(row['Company'][:6], 
                          (row['AbatementAchieved_ktCO2'], row['LCOA']),
                          xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('outputs/optimization_results_facility_based.png', dpi=300, bbox_inches='tight')
    plt.show()

def run_facility_based_optimization(target_years=[2030, 2040, 2050]):
    """Run optimization for multiple target years"""
    
    print("KOREAN PETROCHEMICAL MACC FACILITY-BASED OPTIMIZATION")
    print("=" * 70)
    
    # Load data
    facilities_df, consumption_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, targets_df = load_facility_based_data()
    
    # Calculate baseline emissions
    baseline_emissions_df = calculate_facility_baseline_emissions(consumption_df, emission_factors_ts_df)
    
    print(f"\nBaseline Emissions Summary:")
    total_baseline = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    print(f"  • Total baseline emissions: {total_baseline:.1f} ktCO2/year")
    print(f"  • Average emission intensity: {(total_baseline*1000/baseline_emissions_df['Capacity_kt_per_year'].sum()):.1f} tCO2/t")
    
    all_results = []
    all_solutions = {}
    
    for target_year in target_years:
        print(f"\n" + "="*70)
        print(f"OPTIMIZING FOR TARGET YEAR: {target_year}")
        print("="*70)
        
        # Create technology deployment options
        viable_options = create_facility_technology_options(
            facilities_df, consumption_df, technologies_df, costs_df,
            emission_factors_ts_df, fuel_costs_ts_df, target_year
        )
        
        if len(viable_options) == 0:
            print(f"❌ No viable technology options for {target_year}")
            continue
        
        # Set up and solve optimization
        prob, deployment_vars, required_reduction, total_baseline_emissions = setup_optimization_problem(
            viable_options, baseline_emissions_df, targets_df, target_year
        )
        
        solution_df, status = solve_optimization(prob, deployment_vars, viable_options)
        
        if status == 'Optimal' and len(solution_df) > 0:
            # Analyze results
            result_summary = analyze_optimization_results(
                solution_df, target_year, required_reduction, total_baseline_emissions
            )
            
            all_results.append(result_summary)
            all_solutions[target_year] = solution_df
            
            # Save detailed results
            solution_df.to_csv(f'outputs/optimization_solution_{target_year}_facility_based.csv', index=False)
    
    if all_results:
        # Create visualizations
        create_optimization_visualizations(all_results, all_solutions)
        
        # Save summary results
        results_df = pd.DataFrame(all_results)
        results_df.to_csv('outputs/optimization_summary_facility_based.csv', index=False)
        
        print(f"\n" + "="*70)
        print("OPTIMIZATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"📊 Results Summary:")
        print(results_df.to_string(index=False, float_format='%.1f'))
        
        print(f"\n📁 Files Generated:")
        print(f"  • outputs/optimization_results_facility_based.png")
        print(f"  • outputs/optimization_summary_facility_based.csv")
        for year in all_solutions.keys():
            print(f"  • outputs/optimization_solution_{year}_facility_based.csv")
    
    else:
        print(f"\n❌ OPTIMIZATION FAILED - No viable solutions found")

def main():
    """Main execution function"""
    run_facility_based_optimization([2030, 2040, 2050])

if __name__ == "__main__":
    main()