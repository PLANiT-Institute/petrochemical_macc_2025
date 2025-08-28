#!/usr/bin/env python3
"""
Simplified Korean Petrochemical MACC Optimization Model
======================================================

A simplified version that focuses on getting the optimization working.
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

from run_optimization_model_v3_facility_based import (
    load_facility_based_data, 
    calculate_facility_baseline_emissions,
    calculate_process_baseline_emissions,
    calculate_alternative_emissions, 
    calculate_technology_costs
)

def create_simple_viable_options(facilities_df, consumption_df, technologies_df, costs_df, 
                                emission_factors_ts_df, fuel_costs_ts_df, target_year):
    """Create viable options using simpler logic"""
    
    print(f"Creating viable options for {target_year}...")
    
    # Get year-specific factors
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == target_year].iloc[0]
    fc_year = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == target_year].iloc[0]
    
    # Merge technology and cost data
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    
    viable_options = []
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        
        # Get baseline consumption for this facility
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        for _, process_row in facility_consumption.iterrows():
            process_type = process_row['ProcessType']
            capacity = process_row['Activity_kt_product']
            
            # Get applicable technologies
            applicable_techs = tech_costs[
                (tech_costs['TechGroup'] == process_type) &
                (tech_costs['CommercialYear'] <= target_year) &
                (tech_costs['TechnicalReadiness'] >= facility['TechnicalReadiness_Level'])
            ]
            
            # Calculate baseline emissions
            baseline_emissions = calculate_process_baseline_emissions(process_row, ef_year)
            
            for _, tech in applicable_techs.iterrows():
                # Calculate alternative emissions
                alt_emissions = calculate_alternative_emissions(tech, capacity, ef_year)
                
                # Calculate abatement
                abatement_potential = baseline_emissions - alt_emissions
                
                if abatement_potential > 0:  # Only positive abatement
                    # Calculate costs
                    try:
                        costs_result = calculate_technology_costs(tech, capacity, fc_year, facility)
                        annual_cost = costs_result['AnnualCost_USD']
                        lcoa = annual_cost / (abatement_potential * 1000)
                        
                        if 0 < lcoa < 25000:  # Reasonable cost threshold
                            viable_options.append({
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
                                'LCOA_USD_per_tCO2': lcoa,
                                'AnnualCost_USD': annual_cost,
                                'TechnicalReadiness': tech['TechnicalReadiness'],
                                'CommercialYear': tech['CommercialYear']
                            })
                    except Exception as e:
                        print(f"      Cost calculation error for {facility_id}-{process_type}-{tech['TechID']}: {e}")
    
    viable_df = pd.DataFrame(viable_options)
    print(f"  • Total viable options: {len(viable_df)}")
    
    return viable_df

def solve_simple_optimization(viable_df, baseline_emissions_df, targets_df, target_year):
    """Solve optimization with simple approach"""
    
    if len(viable_df) == 0:
        print(f"❌ No viable options for {target_year}")
        return pd.DataFrame(), "No viable options"
    
    print(f"\nSolving optimization for {target_year}...")
    
    # Get emission reduction target
    year_target = targets_df[targets_df['Year'] == target_year]
    if len(year_target) == 0:
        # Interpolate or use default
        if target_year == 2030:
            target_emissions = 12.0  # MtCO2
        elif target_year == 2040:
            target_emissions = 7.5   # MtCO2
        elif target_year == 2050:
            target_emissions = 3.0   # MtCO2
        else:
            target_emissions = 10.0  # MtCO2
    else:
        target_emissions = year_target['Target_MtCO2'].iloc[0]
    
    # Calculate required reduction
    total_baseline_emissions = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    target_ktCO2 = target_emissions * 1000  # Convert to ktCO2
    required_reduction = total_baseline_emissions - target_ktCO2
    reduction_pct = (required_reduction / total_baseline_emissions) * 100
    
    print(f"  • Target: {target_emissions:.1f} MtCO2 ({target_ktCO2:.0f} ktCO2)")
    print(f"  • Required reduction: {required_reduction:.1f} ktCO2/year ({reduction_pct:.1f}%)")
    print(f"  • Available options: {len(viable_df)}")
    
    # Create optimization problem
    prob = pulp.LpProblem("Petrochemical_MACC_Simple", pulp.LpMinimize)
    
    # Decision variables
    deploy_vars = {}
    for idx, row in viable_df.iterrows():
        var_name = f"deploy_{idx}"
        deploy_vars[idx] = pulp.LpVariable(var_name, 0, 1, pulp.LpContinuous)
    
    # Objective: minimize total cost
    objective = pulp.lpSum([
        row['AnnualCost_USD'] * deploy_vars[idx]
        for idx, row in viable_df.iterrows()
    ])
    prob += objective, "Total_Cost"
    
    # Constraint: meet emission reduction target
    total_abatement = pulp.lpSum([
        row['AbatementPotential_ktCO2'] * deploy_vars[idx]
        for idx, row in viable_df.iterrows()
    ])
    prob += total_abatement >= required_reduction, "Emission_Target"
    
    # Constraint: At most one technology per facility-process
    facility_process_combos = viable_df.groupby(['FacilityID', 'ProcessType']).groups
    
    for (facility_id, process_type), indices in facility_process_combos.items():
        applicable_vars = [deploy_vars[idx] for idx in indices if idx in deploy_vars]
        if len(applicable_vars) > 1:
            constraint_name = f"Max_One_{facility_id}_{process_type}"
            prob += pulp.lpSum(applicable_vars) <= 1, constraint_name
    
    print(f"  • Constraints: {len(prob.constraints)}")
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    status = pulp.LpStatus[prob.status]
    print(f"  • Solution status: {status}")
    
    if status == 'Optimal':
        # Extract solution
        solution_data = []
        
        for idx, row in viable_df.iterrows():
            if idx in deploy_vars:
                deployment_level = deploy_vars[idx].value()
                if deployment_level is not None and deployment_level > 0.01:
                    solution_data.append({
                        'FacilityID': row['FacilityID'],
                        'Company': row['Company'],
                        'Region': row['Region'],
                        'ProcessType': row['ProcessType'],
                        'TechID': row['TechID'],
                        'TechnologyCategory': row['TechnologyCategory'],
                        'DeploymentLevel': deployment_level,
                        'AbatementAchieved_ktCO2': row['AbatementPotential_ktCO2'] * deployment_level,
                        'AnnualCost_USD': row['AnnualCost_USD'] * deployment_level,
                        'LCOA_USD_per_tCO2': row['LCOA_USD_per_tCO2']
                    })
        
        solution_df = pd.DataFrame(solution_data)
        
        if len(solution_df) > 0:
            total_abatement = solution_df['AbatementAchieved_ktCO2'].sum()
            total_cost = solution_df['AnnualCost_USD'].sum()
            print(f"  • Total abatement: {total_abatement:.1f} ktCO2/year")
            print(f"  • Total cost: ${total_cost:,.0f}/year")
            print(f"  • Target achievement: {(total_abatement/required_reduction*100):.1f}%")
        
        return solution_df, status
    
    else:
        print(f"❌ Optimization failed: {status}")
        return pd.DataFrame(), status

def run_simple_optimization():
    """Run simplified optimization"""
    
    print("KOREAN PETROCHEMICAL MACC - SIMPLIFIED OPTIMIZATION")
    print("=" * 60)
    
    # Load data
    facilities_df, consumption_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, targets_df = load_facility_based_data()
    
    # Calculate baseline emissions
    baseline_emissions_df = calculate_facility_baseline_emissions(consumption_df, emission_factors_ts_df)
    total_baseline = baseline_emissions_df['BaselineEmissions_ktCO2_per_year'].sum()
    print(f"\nTotal baseline emissions: {total_baseline:.1f} ktCO2/year")
    
    # Test for each target year
    target_years = [2030, 2040, 2050]
    all_results = {}
    
    for target_year in target_years:
        print(f"\n" + "="*60)
        print(f"OPTIMIZING FOR {target_year}")
        print("="*60)
        
        # Create viable options
        viable_df = create_simple_viable_options(
            facilities_df, consumption_df, technologies_df, costs_df,
            emission_factors_ts_df, fuel_costs_ts_df, target_year
        )
        
        if len(viable_df) > 0:
            # Solve optimization
            solution_df, status = solve_simple_optimization(
                viable_df, baseline_emissions_df, targets_df, target_year
            )
            
            if status == 'Optimal' and len(solution_df) > 0:
                all_results[target_year] = solution_df
                
                # Save results
                solution_df.to_csv(f'outputs/simple_optimization_{target_year}.csv', index=False)
                
                # Show top technologies
                print(f"\nTop technologies deployed:")
                tech_summary = solution_df.groupby('TechnologyCategory').agg({
                    'AbatementAchieved_ktCO2': 'sum',
                    'AnnualCost_USD': 'sum'
                }).sort_values('AbatementAchieved_ktCO2', ascending=False)
                
                for tech_cat, row in tech_summary.head().iterrows():
                    lcoa = row['AnnualCost_USD'] / (row['AbatementAchieved_ktCO2'] * 1000)
                    print(f"  • {tech_cat}: {row['AbatementAchieved_ktCO2']:.1f} ktCO2/year (${lcoa:.0f}/tCO2)")
        else:
            print(f"❌ No viable options found for {target_year}")
    
    if all_results:
        print(f"\n" + "="*60)
        print("OPTIMIZATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
        # Summary table
        summary_data = []
        for year, solution_df in all_results.items():
            summary_data.append({
                'Year': year,
                'Total_Abatement_ktCO2': solution_df['AbatementAchieved_ktCO2'].sum(),
                'Total_Cost_Million_USD': solution_df['AnnualCost_USD'].sum() / 1e6,
                'Avg_LCOA_USD_per_tCO2': solution_df['AnnualCost_USD'].sum() / (solution_df['AbatementAchieved_ktCO2'].sum() * 1000),
                'Technologies_Deployed': len(solution_df),
                'Facilities_Involved': solution_df['FacilityID'].nunique()
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(f"\nResults Summary:")
        print(summary_df.to_string(index=False, float_format='%.1f'))
        
        # Save summary
        summary_df.to_csv('outputs/simple_optimization_summary.csv', index=False)
        
    else:
        print(f"\n❌ OPTIMIZATION FAILED FOR ALL YEARS")

if __name__ == "__main__":
    run_simple_optimization()