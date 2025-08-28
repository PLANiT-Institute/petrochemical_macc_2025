#!/usr/bin/env python3
"""
Corrected Korean Petrochemical MACC Optimization Model
======================================================

Fixed model with:
1. Low-carbon naphtha option (70% reduction from 2030)
2. Unlimited technology deployment (no facility limits)
3. Regional-technology-band level optimization
4. Dual decarbonization pathways: fuel reduction + feedstock switching
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

def load_corrected_data():
    """Load corrected database with low-carbon feedstock"""
    
    print("LOADING CORRECTED KOREAN PETROCHEMICAL MACC DATABASE")
    print("=" * 60)
    
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    # Load key sheets
    facilities_df = excel_data['RegionalFacilities']
    consumption_df = excel_data['FacilityBaselineConsumption_202']  # Corrected sheet name
    technologies_df = excel_data['AlternativeTechnologies']
    costs_df = excel_data['AlternativeCosts']
    emission_factors_df = excel_data['EmissionFactors_TimeSeries']
    fuel_costs_df = excel_data['FuelCosts_TimeSeries']
    targets_df = excel_data['EmissionsTargets']
    
    print(f"✅ Loaded database:")
    print(f"  • Facilities: {len(facilities_df)} across {facilities_df['Region'].nunique()} regions")
    print(f"  • Technologies: {len(technologies_df)} alternative technologies")
    print(f"  • Consumption records: {len(consumption_df)} facility-process combinations")
    print(f"  • Time series: {len(emission_factors_df)} years")
    
    return facilities_df, consumption_df, technologies_df, costs_df, emission_factors_df, fuel_costs_df, targets_df

def create_regional_technology_bands(facilities_df, technologies_df, target_year):
    """Create regional-technology-band combinations (unlimited deployment)"""
    
    print(f"\\nCreating regional-technology-band combinations for {target_year}...")
    
    # Get available technologies for target year
    available_techs = technologies_df[technologies_df['CommercialYear'] <= target_year]
    
    # Create all region-technology-process combinations
    regional_bands = []
    
    for _, facility in facilities_df.iterrows():
        region = facility['Region']
        
        for _, tech in available_techs.iterrows():
            tech_group = tech['TechGroup']  # NCC, BTX, C4
            
            regional_bands.append({
                'Region': region,
                'TechGroup': tech_group,
                'TechID': tech['TechID'],
                'TechnologyCategory': tech['TechnologyCategory'],
                'TechReadiness': tech['TechnicalReadiness'],
                'CommercialYear': tech['CommercialYear']
            })
    
    regional_bands_df = pd.DataFrame(regional_bands)
    
    print(f"  • Available technologies: {len(available_techs)}")
    print(f"  • Regions: {facilities_df['Region'].nunique()}")
    print(f"  • Process types: {technologies_df['TechGroup'].nunique()}")
    print(f"  • Total combinations: {len(regional_bands_df)}")
    
    return regional_bands_df

def calculate_facility_baseline_emissions(facilities_df, consumption_df, emission_factors_df, target_year):
    """Calculate baseline emissions by individual facility-process (not aggregated)"""
    
    print(f"\\nCalculating facility-level baseline emissions for {target_year}...")
    
    # Get emission factors for target year
    ef_year = emission_factors_df[emission_factors_df['Year'] == target_year]
    if len(ef_year) == 0:
        ef_year = emission_factors_df[emission_factors_df['Year'] == 2023]  # Fallback
    ef = ef_year.iloc[0]
    
    facility_baseline = []
    
    # Process each facility individually (not aggregated by region)
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        region = facility['Region']
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        for _, process in facility_consumption.iterrows():
            process_type = process['ProcessType']
            capacity = process['Activity_kt_product']
            
            if capacity > 0:
                # Individual facility consumption rates
                ng = process['NaturalGas_GJ_per_t']
                fo = process['FuelOil_GJ_per_t']
                elec = process['Electricity_GJ_per_t']
                naphtha = process.get('Naphtha_t_per_t', 0)
                lpg = process.get('LPG_t_per_t', 0)
                reformate = process.get('Reformate_t_per_t', 0)
                
                # Calculate baseline emissions per tonne
                baseline_emissions_per_t = (
                    ng * ef['Natural_Gas_tCO2_per_GJ'] +
                    fo * ef['Fuel_Oil_tCO2_per_GJ'] +
                    elec * ef['Electricity_tCO2_per_GJ'] +
                    naphtha * ef['Naphtha_tCO2_per_t'] +
                    lpg * ef['LPG_tCO2_per_t'] +
                    reformate * ef['Reformate_tCO2_per_t']
                )
                
                # Total emissions for this facility-process
                total_emissions = capacity * baseline_emissions_per_t / 1000  # ktCO2/year
                    
                facility_baseline.append({
                    'FacilityID': facility_id,
                    'Region': region,
                    'ProcessType': process_type,
                    'Capacity_kt_per_year': capacity,
                    'BaselineEmissions_tCO2_per_t': baseline_emissions_per_t,
                    'TotalBaselineEmissions_ktCO2_per_year': total_emissions
                })
    
    facility_baseline_df = pd.DataFrame(facility_baseline)
    
    # Create regional summaries for optimization (but maintain facility-level detail)
    regional_baseline = facility_baseline_df.groupby(['Region', 'ProcessType']).agg({
        'Capacity_kt_per_year': 'sum',
        'TotalBaselineEmissions_ktCO2_per_year': 'sum'
    }).reset_index()
    
    # Calculate weighted average emission intensity by region-process
    regional_baseline['BaselineEmissions_tCO2_per_t'] = (
        regional_baseline['TotalBaselineEmissions_ktCO2_per_year'] * 1000 / 
        regional_baseline['Capacity_kt_per_year']
    )
    
    total_baseline = facility_baseline_df['TotalBaselineEmissions_ktCO2_per_year'].sum()
    
    print(f"  • Facility-process combinations: {len(facility_baseline_df)}")  
    print(f"  • Regional-process aggregates: {len(regional_baseline)}")
    print(f"  • Total baseline emissions: {total_baseline:.1f} ktCO2/year")
    
    return facility_baseline_df, regional_baseline

def calculate_technology_abatement_unlimited(regional_bands_df, regional_baseline_df, technologies_df, 
                                           emission_factors_df, target_year):
    """Calculate abatement potential with unlimited deployment"""
    
    print(f"\\nCalculating unlimited technology abatement potential for {target_year}...")
    
    # Get emission factors
    ef_year = emission_factors_df[emission_factors_df['Year'] == target_year]
    if len(ef_year) == 0:
        ef_year = emission_factors_df[emission_factors_df['Year'] == 2023]
    ef = ef_year.iloc[0]
    
    abatement_options = []
    
    for _, band in regional_bands_df.iterrows():
        region = band['Region']
        tech_id = band['TechID']
        tech_group = band['TechGroup']
        
        # Get baseline for this region-process
        baseline_match = regional_baseline_df[
            (regional_baseline_df['Region'] == region) & 
            (regional_baseline_df['ProcessType'] == tech_group)
        ]
        
        if len(baseline_match) > 0:
            baseline_row = baseline_match.iloc[0]
            baseline_emissions_per_t = baseline_row['BaselineEmissions_tCO2_per_t']
            baseline_capacity = baseline_row['Capacity_kt_per_year']
            
            # Get technology data
            tech_data = technologies_df[technologies_df['TechID'] == tech_id].iloc[0]
            
            # Calculate alternative technology emissions per tonne
            alt_emissions_per_t = (
                tech_data['NaturalGas_GJ_per_t'] * ef['Natural_Gas_tCO2_per_GJ'] +
                tech_data['FuelOil_GJ_per_t'] * ef['Fuel_Oil_tCO2_per_GJ'] +
                tech_data['Electricity_GJ_per_t'] * ef['Electricity_tCO2_per_GJ'] +
                tech_data['Hydrogen_GJ_per_t'] * ef['Green_Hydrogen_tCO2_per_GJ'] +
                tech_data.get('Naphtha_t_per_t', 0) * ef['Naphtha_tCO2_per_t'] +
                tech_data.get('LPG_t_per_t', 0) * ef['LPG_tCO2_per_t'] +
                tech_data.get('Reformate_t_per_t', 0) * ef['Reformate_tCO2_per_t']
            )
            
            # Calculate abatement per tonne
            abatement_per_t = baseline_emissions_per_t - alt_emissions_per_t
            
            if abatement_per_t > 0:  # Only positive abatement
                # UNLIMITED DEPLOYMENT - use full baseline capacity
                max_abatement_potential = baseline_capacity * abatement_per_t / 1000  # ktCO2/year
                
                abatement_options.append({
                    'Region': region,
                    'TechGroup': tech_group,
                    'TechID': tech_id,
                    'TechnologyCategory': tech_data['TechnologyCategory'],
                    'BaselineCapacity_kt_per_year': baseline_capacity,
                    'MaxDeployment_kt_per_year': baseline_capacity,  # UNLIMITED
                    'BaselineEmissions_tCO2_per_t': baseline_emissions_per_t,
                    'AlternativeEmissions_tCO2_per_t': alt_emissions_per_t,
                    'AbatementPerTonne_tCO2': abatement_per_t,
                    'MaxAbatementPotential_ktCO2_per_year': max_abatement_potential,
                    'TechReadiness': tech_data['TechnicalReadiness'],
                    'CommercialYear': tech_data['CommercialYear']
                })
    
    abatement_df = pd.DataFrame(abatement_options)
    
    if len(abatement_df) > 0:
        total_potential = abatement_df['MaxAbatementPotential_ktCO2_per_year'].sum()
        print(f"  • Viable technology options: {len(abatement_df)}")
        print(f"  • Total abatement potential (unlimited): {total_potential:.1f} ktCO2/year")
        
        # Show top technologies
        top_techs = abatement_df.groupby('TechnologyCategory')['MaxAbatementPotential_ktCO2_per_year'].sum().sort_values(ascending=False).head(5)
        print(f"  • Top abatement technologies:")
        for tech, potential in top_techs.items():
            print(f"    - {tech}: {potential:.1f} ktCO2/year")
    
    return abatement_df

def calculate_technology_costs_regional(abatement_df, technologies_df, costs_df, fuel_costs_df, target_year):
    """Calculate technology costs for regional deployment"""
    
    print(f"\\nCalculating regional technology costs for {target_year}...")
    
    # Get fuel costs for target year
    fc_year = fuel_costs_df[fuel_costs_df['Year'] == target_year]
    if len(fc_year) == 0:
        fc_year = fuel_costs_df[fuel_costs_df['Year'] == 2023]
    fc = fc_year.iloc[0]
    
    cost_results = []
    
    for _, option in abatement_df.iterrows():
        tech_id = option['TechID']
        capacity = option['MaxDeployment_kt_per_year']
        
        # Get cost data
        tech_data = technologies_df[technologies_df['TechID'] == tech_id].iloc[0]
        cost_data = costs_df[costs_df['TechID'] == tech_id].iloc[0]
        
        # Calculate costs
        capex_per_kt = cost_data['CAPEX_Million_USD_per_kt_capacity']
        total_capex = capacity * capex_per_kt  # Million USD
        
        # Annualized CAPEX
        lifetime = tech_data['Lifetime_years']
        discount_rate = 0.05
        crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
        annual_capex = total_capex * crf  # Million USD/year
        
        # OPEX
        opex_delta_per_t = cost_data['OPEX_Delta_USD_per_t']
        annual_opex_delta = capacity * 1000 * opex_delta_per_t / 1e6  # Million USD/year
        
        # Fuel cost changes
        baseline_fuel_cost = 0  # Simplified - assume included in OPEX delta
        alt_fuel_cost = 0
        fuel_cost_delta = 0
        
        # Total annual cost
        total_annual_cost = annual_capex + annual_opex_delta + fuel_cost_delta  # Million USD/year
        
        # LCOA
        abatement_ktCO2_per_year = option['MaxAbatementPotential_ktCO2_per_year']
        if abatement_ktCO2_per_year > 0:
            lcoa = total_annual_cost * 1e6 / (abatement_ktCO2_per_year * 1000)  # USD/tCO2
        else:
            lcoa = float('inf')
        
        cost_results.append({
            'Region': option['Region'],
            'TechGroup': option['TechGroup'],
            'TechID': tech_id,
            'TechnologyCategory': option['TechnologyCategory'],
            'MaxAbatementPotential_ktCO2_per_year': abatement_ktCO2_per_year,
            'TotalCAPEX_Million_USD': total_capex,
            'AnnualCost_Million_USD': total_annual_cost,
            'LCOA_USD_per_tCO2': lcoa
        })
    
    cost_df = pd.DataFrame(cost_results)
    
    if len(cost_df) > 0:
        cost_df = cost_df[cost_df['LCOA_USD_per_tCO2'] < 25000]  # Filter reasonable costs
        print(f"  • Cost-effective options: {len(cost_df)} (LCOA < $25,000/tCO2)")
        
        if len(cost_df) > 0:
            avg_lcoa = (cost_df['AnnualCost_Million_USD'] * 1e6 / (cost_df['MaxAbatementPotential_ktCO2_per_year'] * 1000)).mean()
            print(f"  • Average LCOA: ${avg_lcoa:.0f}/tCO2")
    
    return cost_df

def solve_corrected_optimization(cost_df, targets_df, baseline_total, target_year):
    """Solve optimization with corrected structure (unlimited deployment)"""
    
    if len(cost_df) == 0:
        print(f"❌ No cost-effective options for {target_year}")
        return pd.DataFrame(), "No options"
    
    print(f"\\n" + "="*60)
    print(f"SOLVING CORRECTED OPTIMIZATION FOR {target_year}")
    print("="*60)
    
    # Get emission target
    year_target = targets_df[targets_df['Year'] == target_year]
    if len(year_target) > 0:
        target_emissions = year_target['Target_MtCO2'].iloc[0] * 1000  # Convert to ktCO2
    else:
        # Default targets
        target_map = {2030: 34600, 2040: 20400, 2050: 8100}
        target_emissions = target_map.get(target_year, baseline_total * 0.8)
    
    required_reduction = baseline_total - target_emissions
    reduction_pct = (required_reduction / baseline_total) * 100
    
    print(f"Target: {target_emissions/1000:.1f} MtCO2")
    print(f"Required reduction: {required_reduction:.1f} ktCO2/year ({reduction_pct:.1f}%)")
    print(f"Available abatement potential: {cost_df['MaxAbatementPotential_ktCO2_per_year'].sum():.1f} ktCO2/year")
    print(f"Available options: {len(cost_df)}")
    
    # Create optimization problem
    prob = pulp.LpProblem(f"Petrochemical_MACC_Corrected_{target_year}", pulp.LpMinimize)
    
    # Decision variables - deployment level for each option (0-1)
    deploy_vars = {}
    for idx, row in cost_df.iterrows():
        var_name = f"deploy_{idx}"
        deploy_vars[idx] = pulp.LpVariable(var_name, 0, 1, pulp.LpContinuous)
    
    # Objective: minimize total cost
    total_cost = pulp.lpSum([
        row['AnnualCost_Million_USD'] * deploy_vars[idx]
        for idx, row in cost_df.iterrows()
    ])
    prob += total_cost, "Total_Annual_Cost_Million_USD"
    
    # Constraint: meet emission reduction target
    total_abatement = pulp.lpSum([
        row['MaxAbatementPotential_ktCO2_per_year'] * deploy_vars[idx]
        for idx, row in cost_df.iterrows()
    ])
    prob += total_abatement >= required_reduction, "Emission_Reduction_Target"
    
    # NO OTHER CONSTRAINTS - UNLIMITED DEPLOYMENT
    
    print(f"Problem constraints: {len(prob.constraints)}")
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    status = pulp.LpStatus[prob.status]
    print(f"Solution status: {status}")
    
    if status == 'Optimal':
        # Extract solution
        solution_data = []
        total_abatement_achieved = 0
        total_cost_achieved = 0
        
        for idx, row in cost_df.iterrows():
            if idx in deploy_vars:
                deployment_level = deploy_vars[idx].value()
                if deployment_level is not None and deployment_level > 0.01:
                    abatement_achieved = row['MaxAbatementPotential_ktCO2_per_year'] * deployment_level
                    cost_achieved = row['AnnualCost_Million_USD'] * deployment_level
                    
                    solution_data.append({
                        'Region': row['Region'],
                        'TechGroup': row['TechGroup'],
                        'TechID': row['TechID'],
                        'TechnologyCategory': row['TechnologyCategory'],
                        'DeploymentLevel': deployment_level,
                        'AbatementAchieved_ktCO2_per_year': abatement_achieved,
                        'AnnualCost_Million_USD': cost_achieved,
                        'LCOA_USD_per_tCO2': row['LCOA_USD_per_tCO2']
                    })
                    
                    total_abatement_achieved += abatement_achieved
                    total_cost_achieved += cost_achieved
        
        solution_df = pd.DataFrame(solution_data)
        
        if len(solution_df) > 0:
            avg_lcoa = total_cost_achieved * 1e6 / (total_abatement_achieved * 1000) if total_abatement_achieved > 0 else 0
            achievement_pct = (total_abatement_achieved / required_reduction) * 100 if required_reduction > 0 else 100
            
            print(f"✅ OPTIMIZATION SUCCESSFUL:")
            print(f"  • Total abatement: {total_abatement_achieved:.1f} ktCO2/year")
            print(f"  • Total cost: ${total_cost_achieved:.1f} million/year")
            print(f"  • Average LCOA: ${avg_lcoa:.0f}/tCO2")
            print(f"  • Target achievement: {achievement_pct:.1f}%")
            print(f"  • Technologies deployed: {len(solution_df)}")
        
        return solution_df, status
    
    else:
        print(f"❌ Optimization failed: {status}")
        return pd.DataFrame(), status

def run_corrected_optimization():
    """Run the corrected optimization model"""
    
    print("CORRECTED KOREAN PETROCHEMICAL MACC OPTIMIZATION")
    print("=" * 60)
    print("🔧 Fixed Issues:")
    print("  • Low-carbon naphtha (70% reduction from 2030)")
    print("  • Unlimited technology deployment")
    print("  • Regional-technology-band level")
    print("  • Dual decarbonization pathways")
    print()
    
    # Load data
    facilities_df, consumption_df, technologies_df, costs_df, emission_factors_df, fuel_costs_df, targets_df = load_corrected_data()
    
    # Test years
    target_years = [2030, 2040, 2050]
    all_results = {}
    
    for target_year in target_years:
        print(f"\\n" + "="*60)
        print(f"ANALYZING {target_year}")
        print("="*60)
        
        try:
            # Create regional-technology bands
            regional_bands_df = create_regional_technology_bands(facilities_df, technologies_df, target_year)
            
            # Calculate regional baseline
            facility_baseline_df, regional_baseline_df = calculate_facility_baseline_emissions(facilities_df, consumption_df, emission_factors_df, target_year)
            baseline_total = regional_baseline_df['TotalBaselineEmissions_ktCO2_per_year'].sum()
            
            # Calculate abatement potential (unlimited)
            abatement_df = calculate_technology_abatement_unlimited(regional_bands_df, regional_baseline_df, 
                                                                 technologies_df, emission_factors_df, target_year)
            
            if len(abatement_df) > 0:
                # Calculate costs
                cost_df = calculate_technology_costs_regional(abatement_df, technologies_df, costs_df, fuel_costs_df, target_year)
                
                if len(cost_df) > 0:
                    # Solve optimization
                    solution_df, status = solve_corrected_optimization(cost_df, targets_df, baseline_total, target_year)
                    
                    if status == 'Optimal' and len(solution_df) > 0:
                        all_results[target_year] = solution_df
                        
                        # Save results
                        solution_df.to_csv(f'outputs/corrected_optimization_{target_year}.csv', index=False)
                        
                        # Show top technologies
                        tech_summary = solution_df.groupby('TechnologyCategory').agg({
                            'AbatementAchieved_ktCO2_per_year': 'sum',
                            'AnnualCost_Million_USD': 'sum'
                        }).sort_values('AbatementAchieved_ktCO2_per_year', ascending=False)
                        
                        print(f"\\nTop technologies deployed:")
                        for tech_cat, row in tech_summary.head().iterrows():
                            lcoa = row['AnnualCost_Million_USD'] * 1e6 / (row['AbatementAchieved_ktCO2_per_year'] * 1000)
                            print(f"  • {tech_cat}: {row['AbatementAchieved_ktCO2_per_year']:.1f} ktCO2/year (${lcoa:.0f}/tCO2)")
                
        except Exception as e:
            print(f"❌ Error analyzing {target_year}: {e}")
    
    # Summary
    if all_results:
        print(f"\\n" + "="*60)
        print("CORRECTED OPTIMIZATION RESULTS SUMMARY")
        print("="*60)
        
        summary_data = []
        for year, solution_df in all_results.items():
            summary_data.append({
                'Year': year,
                'Total_Abatement_ktCO2_per_year': solution_df['AbatementAchieved_ktCO2_per_year'].sum(),
                'Total_Cost_Million_USD_per_year': solution_df['AnnualCost_Million_USD'].sum(),
                'Avg_LCOA_USD_per_tCO2': (solution_df['AnnualCost_Million_USD'].sum() * 1e6 / 
                                         (solution_df['AbatementAchieved_ktCO2_per_year'].sum() * 1000)),
                'Technologies_Deployed': len(solution_df),
                'Regions_Involved': solution_df['Region'].nunique()
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False, float_format='%.1f'))
        
        summary_df.to_csv('outputs/corrected_optimization_summary.csv', index=False)
        
        print(f"\\n✅ CORRECTED OPTIMIZATION COMPLETED")
        print(f"📊 Results show impact of unlimited deployment + low-carbon feedstock")
        
    else:
        print(f"\\n❌ NO SUCCESSFUL OPTIMIZATIONS")

if __name__ == "__main__":
    run_corrected_optimization()