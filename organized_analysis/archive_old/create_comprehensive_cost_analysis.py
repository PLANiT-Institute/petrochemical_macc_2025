#!/usr/bin/env python3
"""
Comprehensive cost analysis: Overall outcomes, stranded assets, timing, emissions, and risk analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set font for Korean text support
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_comprehensive_cost_analysis():
    """Create comprehensive cost analysis covering all required aspects"""
    
    print("💰 COMPREHENSIVE COST ANALYSIS")
    print("="*80)
    
    output_dir = Path("outputs")
    
    # Load data
    try:
        facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
        enhanced_deployments = pd.read_csv(output_dir / "enhanced_optimization_deployments.csv")
        enhanced_pathway = pd.read_csv(output_dir / "enhanced_optimization_achievement.csv")
        facility_transitions = pd.read_csv(output_dir / "detailed_facility_transitions.csv")
        
        print("✓ All data loaded successfully")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load data: {e}")
        return None
    
    # Financial parameters
    financial_params = {
        'discount_rate': 0.06,  # 6% real discount rate
        'analysis_period': 25,  # 2025-2050
        'base_year': 2025,
        'facility_book_life': 25,  # Standard petrochemical facility life
        'carbon_price_scenarios': {
            'Low': {'2025': 30, '2030': 50, '2040': 80, '2050': 100},
            'Central': {'2025': 50, '2030': 75, '2040': 125, '2050': 200},
            'High': {'2025': 75, '2030': 125, '2040': 200, '2050': 350}
        }
    }
    
    # 1. OVERALL COST OUTCOMES
    print(f"\n🔹 1. OVERALL COST OUTCOMES")
    print("="*60)
    
    # Calculate facility commissioning years (assume random distribution over past 25 years)
    np.random.seed(42)
    facility_data['commissioning_year'] = np.random.randint(2000, 2025, len(facility_data))
    facility_data['facility_age'] = 2025 - facility_data['commissioning_year']
    facility_data['remaining_book_life'] = np.maximum(0, financial_params['facility_book_life'] - facility_data['facility_age'])
    
    # Estimate facility book values based on capacity and age
    facility_data['original_capex_million_usd'] = facility_data['capacity_kt'] * 2.5  # $2.5M per kt capacity
    facility_data['current_book_value_million_usd'] = (facility_data['original_capex_million_usd'] * 
                                                      facility_data['remaining_book_life'] / financial_params['facility_book_life'])
    
    # Technology cost parameters (per tCO2 abated)
    tech_costs = {
        'EE_NCC': {'capex_per_tco2': 800, 'opex_per_tco2': 50, 'lifetime': 15},
        'EE_BTX': {'capex_per_tco2': 600, 'opex_per_tco2': 40, 'lifetime': 15},
        'EE_UTL': {'capex_per_tco2': 400, 'opex_per_tco2': 30, 'lifetime': 15},
        'RE_001': {'capex_per_tco2': 1200, 'opex_per_tco2': 60, 'lifetime': 25},
        'RE_002': {'capex_per_tco2': 800, 'opex_per_tco2': 40, 'lifetime': 25},
        'RE_003': {'capex_per_tco2': 200, 'opex_per_tco2': 120, 'lifetime': 20},  # PPA has low CAPEX, higher OPEX
        'HP_001': {'capex_per_tco2': 1000, 'opex_per_tco2': 80, 'lifetime': 20},
        'HP_002': {'capex_per_tco2': 1500, 'opex_per_tco2': 120, 'lifetime': 20},
        'ES_001': {'capex_per_tco2': 2000, 'opex_per_tco2': 100, 'lifetime': 15}
    }
    
    # Calculate detailed costs for optimized pathway
    years = list(range(2025, 2051))
    
    # Carbon price interpolation for central scenario
    carbon_prices = {}
    central_scenario = financial_params['carbon_price_scenarios']['Central']
    for year in years:
        if year <= 2025:
            carbon_prices[year] = central_scenario['2025']
        elif year <= 2030:
            progress = (year - 2025) / (2030 - 2025)
            carbon_prices[year] = central_scenario['2025'] + progress * (central_scenario['2030'] - central_scenario['2025'])
        elif year <= 2040:
            progress = (year - 2030) / (2040 - 2030)
            carbon_prices[year] = central_scenario['2030'] + progress * (central_scenario['2040'] - central_scenario['2030'])
        else:
            progress = (year - 2040) / (2050 - 2040)
            carbon_prices[year] = central_scenario['2040'] + progress * (central_scenario['2050'] - central_scenario['2040'])
    
    # Detailed cost calculation by year
    annual_costs = []
    
    for year in years:
        year_deployments = enhanced_deployments[enhanced_deployments['Year'] == year]
        
        annual_capex = 0
        annual_opex = 0
        annual_carbon_payments = 0
        annual_stranded_value = 0
        
        for _, deployment in year_deployments.iterrows():
            tech_id = deployment['TechID']
            abatement_kt = deployment['AbatementMtCO2'] * 1000  # Convert to kt
            
            if tech_id in tech_costs:
                tech_params = tech_costs[tech_id]
                
                # CAPEX (only in deployment year)
                annual_capex += abatement_kt * tech_params['capex_per_tco2']
                
                # OPEX (ongoing for deployed technologies)
                # Calculate cumulative deployment up to this year
                cumulative_deployment = enhanced_deployments[
                    (enhanced_deployments['TechID'] == tech_id) & 
                    (enhanced_deployments['Year'] <= year)
                ]['AbatementMtCO2'].sum() * 1000
                
                annual_opex += cumulative_deployment * tech_params['opex_per_tco2']
        
        # Carbon payments (BAU emissions - optimized emissions)
        # Interpolate emissions for years not in the pathway data
        pathway_years = enhanced_pathway['Year'].tolist()
        if year in pathway_years:
            bau_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['BAU_Emissions'].iloc[0] * 1000  # kt
            optimized_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['Optimized_Emissions'].iloc[0] * 1000  # kt
        else:
            # Linear interpolation between known points
            if year < min(pathway_years):
                bau_emissions = enhanced_pathway.iloc[0]['BAU_Emissions'] * 1000
                optimized_emissions = enhanced_pathway.iloc[0]['Optimized_Emissions'] * 1000
            elif year > max(pathway_years):
                bau_emissions = enhanced_pathway.iloc[-1]['BAU_Emissions'] * 1000
                optimized_emissions = enhanced_pathway.iloc[-1]['Optimized_Emissions'] * 1000
            else:
                # Find surrounding years
                lower_year = max([y for y in pathway_years if y <= year])
                upper_year = min([y for y in pathway_years if y >= year])
                
                if lower_year == upper_year:
                    bau_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['BAU_Emissions'].iloc[0] * 1000
                    optimized_emissions = enhanced_pathway[enhanced_pathway['Year'] == year]['Optimized_Emissions'].iloc[0] * 1000
                else:
                    # Linear interpolation
                    progress = (year - lower_year) / (upper_year - lower_year)
                    
                    lower_bau = enhanced_pathway[enhanced_pathway['Year'] == lower_year]['BAU_Emissions'].iloc[0]
                    upper_bau = enhanced_pathway[enhanced_pathway['Year'] == upper_year]['BAU_Emissions'].iloc[0]
                    bau_emissions = (lower_bau + progress * (upper_bau - lower_bau)) * 1000
                    
                    lower_opt = enhanced_pathway[enhanced_pathway['Year'] == lower_year]['Optimized_Emissions'].iloc[0]
                    upper_opt = enhanced_pathway[enhanced_pathway['Year'] == upper_year]['Optimized_Emissions'].iloc[0]
                    optimized_emissions = (lower_opt + progress * (upper_opt - lower_opt)) * 1000
        
        annual_carbon_payments = optimized_emissions * carbon_prices[year]
        
        # Stranded value calculation (facilities retired early)
        retirement_rate = 0.02  # 2% annual retirement rate for old facilities
        facilities_at_risk = facility_data[facility_data['facility_age'] >= 20]
        annual_stranded_value = facilities_at_risk['current_book_value_million_usd'].sum() * retirement_rate * 1e6  # Convert to USD
        
        annual_costs.append({
            'Year': year,
            'CAPEX_USD': annual_capex,
            'OPEX_USD': annual_opex, 
            'Carbon_Payments_USD': annual_carbon_payments,
            'Stranded_Value_USD': annual_stranded_value,
            'Total_Cost_USD': annual_capex + annual_opex + annual_carbon_payments + annual_stranded_value,
            'Carbon_Price_USD_per_tCO2': carbon_prices[year],
            'BAU_Emissions_kt': bau_emissions,
            'Optimized_Emissions_kt': optimized_emissions
        })
    
    annual_costs_df = pd.DataFrame(annual_costs)
    
    # Calculate NPV
    def calculate_npv(cost_series, discount_rate, base_year):
        npv = 0
        for i, cost in enumerate(cost_series):
            year = base_year + i
            discount_factor = (1 + discount_rate) ** -(year - base_year)
            npv += cost * discount_factor
        return npv
    
    # NPV calculations
    npv_results = {
        'Total_NPV_Billion_USD': calculate_npv(annual_costs_df['Total_Cost_USD'], financial_params['discount_rate'], 2025) / 1e9,
        'CAPEX_NPV_Billion_USD': calculate_npv(annual_costs_df['CAPEX_USD'], financial_params['discount_rate'], 2025) / 1e9,
        'OPEX_NPV_Billion_USD': calculate_npv(annual_costs_df['OPEX_USD'], financial_params['discount_rate'], 2025) / 1e9,
        'Carbon_NPV_Billion_USD': calculate_npv(annual_costs_df['Carbon_Payments_USD'], financial_params['discount_rate'], 2025) / 1e9,
        'Stranded_NPV_Billion_USD': calculate_npv(annual_costs_df['Stranded_Value_USD'], financial_params['discount_rate'], 2025) / 1e9
    }
    
    # Baseline scenarios for comparison
    baseline_scenarios = {
        'BAU': {
            'description': 'Business as usual - no additional technologies',
            'capex_multiplier': 0.0,
            'opex_multiplier': 0.0,
            'emissions_multiplier': 1.0,
            'stranded_multiplier': 0.5  # Some natural retirement
        },
        'Uniform': {
            'description': 'Uniform technology deployment across all facilities',
            'capex_multiplier': 1.3,  # 30% higher due to poor targeting
            'opex_multiplier': 1.2,
            'emissions_multiplier': 0.7,  # Still achieve some reduction
            'stranded_multiplier': 0.8
        },
        'Age_Blind': {
            'description': 'Technology deployment ignoring facility age',
            'capex_multiplier': 1.5,  # 50% higher due to inefficient retrofit
            'opex_multiplier': 1.4,
            'emissions_multiplier': 0.6,
            'stranded_multiplier': 1.2  # Higher stranding
        }
    }
    
    baseline_npvs = {}
    for scenario_name, params in baseline_scenarios.items():
        scenario_carbon_payments = []
        scenario_capex = []
        scenario_opex = []
        scenario_stranded = []
        
        for _, year_data in annual_costs_df.iterrows():
            # Adjust emissions and carbon payments
            scenario_emissions = year_data['BAU_Emissions_kt'] * params['emissions_multiplier']
            scenario_carbon = scenario_emissions * year_data['Carbon_Price_USD_per_tCO2']
            scenario_carbon_payments.append(scenario_carbon)
            
            # Adjust technology costs
            scenario_capex.append(year_data['CAPEX_USD'] * params['capex_multiplier'])
            scenario_opex.append(year_data['OPEX_USD'] * params['opex_multiplier'])
            scenario_stranded.append(year_data['Stranded_Value_USD'] * params['stranded_multiplier'])
        
        baseline_npvs[scenario_name] = {
            'Total_NPV': (calculate_npv(scenario_carbon_payments, financial_params['discount_rate'], 2025) +
                         calculate_npv(scenario_capex, financial_params['discount_rate'], 2025) +
                         calculate_npv(scenario_opex, financial_params['discount_rate'], 2025) +
                         calculate_npv(scenario_stranded, financial_params['discount_rate'], 2025)) / 1e9,
            'CAPEX_NPV': calculate_npv(scenario_capex, financial_params['discount_rate'], 2025) / 1e9,
            'OPEX_NPV': calculate_npv(scenario_opex, financial_params['discount_rate'], 2025) / 1e9,
            'Carbon_NPV': calculate_npv(scenario_carbon_payments, financial_params['discount_rate'], 2025) / 1e9,
            'Stranded_NPV': calculate_npv(scenario_stranded, financial_params['discount_rate'], 2025) / 1e9
        }
    
    print(f"✓ Optimized Pathway Total NPV: ${npv_results['Total_NPV_Billion_USD']:.1f}B")
    for scenario, results in baseline_npvs.items():
        savings = results['Total_NPV'] - npv_results['Total_NPV_Billion_USD']
        savings_pct = (savings / results['Total_NPV']) * 100
        print(f"  vs {scenario}: ${results['Total_NPV']:.1f}B (savings: ${savings:.1f}B, {savings_pct:.1f}%)")
    
    # 2. STRANDED ASSET RISK
    print(f"\n🔹 2. STRANDED ASSET RISK")
    print("="*60)
    
    # Calculate stranded assets by cohort
    facility_data['age_cohort'] = pd.cut(facility_data['facility_age'], 
                                        bins=[0, 5, 10, 15, 20, 25, 50], 
                                        labels=['0-5yr', '6-10yr', '11-15yr', '16-20yr', '21-25yr', '>25yr'])
    
    stranded_analysis = facility_data.groupby('age_cohort').agg({
        'current_book_value_million_usd': 'sum',
        'facility_id': 'count',
        'annual_emissions_kt_co2': 'sum',
        'capacity_kt': 'sum'
    }).reset_index()
    stranded_analysis.columns = ['Age_Cohort', 'Book_Value_Million_USD', 'Facility_Count', 'Emissions_kt', 'Capacity_kt']
    
    # Risk of stranding by cohort (higher for older facilities)
    stranding_risk = {
        '0-5yr': 0.05, '6-10yr': 0.10, '11-15yr': 0.20, 
        '16-20yr': 0.40, '21-25yr': 0.70, '>25yr': 0.90
    }
    
    stranded_analysis['Stranding_Risk'] = stranded_analysis['Age_Cohort'].astype(str).map(stranding_risk)
    stranded_analysis['Expected_Stranded_Value_Million_USD'] = (stranded_analysis['Book_Value_Million_USD'] * 
                                                               stranded_analysis['Stranding_Risk'])
    
    total_book_value = stranded_analysis['Book_Value_Million_USD'].sum()
    total_stranded_expected = stranded_analysis['Expected_Stranded_Value_Million_USD'].sum()
    stranded_percentage = (total_stranded_expected / total_book_value) * 100
    
    print(f"✓ Total Asset Base: ${total_book_value:,.0f}M")
    print(f"✓ Expected Stranded Value: ${total_stranded_expected:,.0f}M ({stranded_percentage:.1f}%)")
    
    # Stranding timeline
    stranding_timeline = []
    for year in years:
        # Higher stranding in early years as transition accelerates
        if year <= 2030:
            annual_stranding_rate = 0.03  # 3% of at-risk assets
        elif year <= 2040:
            annual_stranding_rate = 0.02  # 2% 
        else:
            annual_stranding_rate = 0.01  # 1%
        
        at_risk_facilities = facility_data[facility_data['facility_age'] >= 15]
        annual_stranded_value = at_risk_facilities['current_book_value_million_usd'].sum() * annual_stranding_rate
        
        stranding_timeline.append({
            'Year': year,
            'Annual_Stranded_Value_Million_USD': annual_stranded_value,
            'Facilities_At_Risk': len(at_risk_facilities)
        })
    
    stranding_timeline_df = pd.DataFrame(stranding_timeline)
    
    # 3. INVESTMENT & RETIREMENT TIMING
    print(f"\n🔹 3. INVESTMENT & RETIREMENT TIMING")
    print("="*60)
    
    # Technology deployment schedule
    tech_deployment_schedule = enhanced_deployments.groupby(['Year', 'TechID']).agg({
        'AbatementMtCO2': 'sum',
        'AnnualCostUSD': 'sum'
    }).reset_index()
    
    # Calculate portfolio shares by technology
    portfolio_shares = []
    for year in years:
        year_deployments = enhanced_deployments[enhanced_deployments['Year'] <= year]
        total_abatement = year_deployments.groupby('TechID')['AbatementMtCO2'].sum()
        total_capacity = total_abatement.sum()
        
        if total_capacity > 0:
            for tech_id, abatement in total_abatement.items():
                portfolio_shares.append({
                    'Year': year,
                    'TechID': tech_id,
                    'Portfolio_Share': abatement / total_capacity,
                    'Cumulative_Abatement_Mt': abatement
                })
    
    portfolio_shares_df = pd.DataFrame(portfolio_shares)
    
    # Asset replacement prioritization
    facility_data['replacement_priority'] = (
        facility_data['facility_age'] * 0.4 +  # Age factor
        facility_data['emission_intensity_t_co2_per_t'] * 20 +  # Emission intensity factor
        (1 / facility_data['capacity_kt']) * 10000  # Size factor (smaller = higher priority)
    )
    
    replacement_timeline = facility_data.nlargest(50, 'replacement_priority')[  # Top 50 priority facilities
        ['facility_id', 'facility_age', 'capacity_kt', 'annual_emissions_kt_co2', 'replacement_priority']
    ]
    
    print(f"✓ Technology deployment spans {years[0]}-{years[-1]}")
    print(f"✓ {len(replacement_timeline)} high-priority facilities identified for early action")
    
    # 4. EMISSIONS PATHWAY
    print(f"\n🔹 4. EMISSIONS PATHWAY")
    print("="*60)
    
    # Calculate cumulative emissions
    enhanced_pathway['Cumulative_BAU_Mt'] = enhanced_pathway['BAU_Emissions'].cumsum()
    enhanced_pathway['Cumulative_Optimized_Mt'] = enhanced_pathway['Optimized_Emissions'].cumsum()
    enhanced_pathway['Annual_Abatement_Mt'] = enhanced_pathway['BAU_Emissions'] - enhanced_pathway['Optimized_Emissions']
    enhanced_pathway['Cumulative_Abatement_Mt'] = enhanced_pathway['Annual_Abatement_Mt'].cumsum()
    
    # Carbon budget analysis (assume linear reduction target)
    baseline_2025 = enhanced_pathway.iloc[0]['BAU_Emissions']
    target_2050 = 2.5  # Net-zero target
    carbon_budget = 0
    
    for _, row in enhanced_pathway.iterrows():
        year = row['Year']
        linear_target = baseline_2025 - (baseline_2025 - target_2050) * (year - 2025) / (2050 - 2025)
        carbon_budget += linear_target
    
    actual_cumulative = enhanced_pathway['Cumulative_Optimized_Mt'].iloc[-1]
    budget_compliance = (carbon_budget - actual_cumulative) / carbon_budget * 100
    
    residual_2050 = enhanced_pathway[enhanced_pathway['Year'] == 2050]['Optimized_Emissions'].iloc[0]
    
    print(f"✓ Cumulative emissions 2025-2050: {actual_cumulative:.1f} Mt CO₂")
    print(f"✓ Carbon budget headroom: {budget_compliance:.1f}%")
    print(f"✓ Residual emissions 2050: {residual_2050:.1f} Mt CO₂")
    
    # 5. RISK & UNCERTAINTY ANALYSIS
    print(f"\n🔹 5. RISK & UNCERTAINTY ANALYSIS")
    print("="*60)
    
    # Monte Carlo simulation for different carbon price scenarios
    scenario_results = {}
    
    for scenario_name, price_path in financial_params['carbon_price_scenarios'].items():
        # Interpolate carbon prices for this scenario
        scenario_carbon_prices = {}
        for year in years:
            if year <= 2025:
                scenario_carbon_prices[year] = price_path['2025']
            elif year <= 2030:
                progress = (year - 2025) / (2030 - 2025)
                scenario_carbon_prices[year] = price_path['2025'] + progress * (price_path['2030'] - price_path['2025'])
            elif year <= 2040:
                progress = (year - 2030) / (2040 - 2030)
                scenario_carbon_prices[year] = price_path['2030'] + progress * (price_path['2040'] - price_path['2030'])
            else:
                progress = (year - 2040) / (2050 - 2040)
                scenario_carbon_prices[year] = price_path['2040'] + progress * (price_path['2050'] - price_path['2040'])
        
        # Calculate scenario costs
        scenario_carbon_costs = []
        for _, year_data in annual_costs_df.iterrows():
            year = int(year_data['Year'])
            carbon_cost = year_data['Optimized_Emissions_kt'] * scenario_carbon_prices[year]
            scenario_carbon_costs.append(carbon_cost)
        
        scenario_total_costs = []
        for i, carbon_cost in enumerate(scenario_carbon_costs):
            total_cost = (annual_costs_df.iloc[i]['CAPEX_USD'] + 
                         annual_costs_df.iloc[i]['OPEX_USD'] + 
                         carbon_cost +
                         annual_costs_df.iloc[i]['Stranded_Value_USD'])
            scenario_total_costs.append(total_cost)
        
        scenario_npv = calculate_npv(scenario_total_costs, financial_params['discount_rate'], 2025) / 1e9
        
        scenario_results[scenario_name] = {
            'NPV_Billion_USD': scenario_npv,
            'Carbon_Costs': scenario_carbon_costs,
            'Total_Costs': scenario_total_costs
        }
    
    # Calculate CVaR (95% Conditional Value at Risk)
    all_npvs = [result['NPV_Billion_USD'] for result in scenario_results.values()]
    cvar_95 = np.percentile(all_npvs, 95)
    
    print(f"✓ Cost range across scenarios: ${min(all_npvs):.1f}B - ${max(all_npvs):.1f}B")
    print(f"✓ CVaR (95%): ${cvar_95:.1f}B")
    
    return {
        'npv_results': npv_results,
        'baseline_npvs': baseline_npvs,
        'annual_costs_df': annual_costs_df,
        'stranded_analysis': stranded_analysis,
        'stranding_timeline_df': stranding_timeline_df,
        'portfolio_shares_df': portfolio_shares_df,
        'enhanced_pathway': enhanced_pathway,
        'scenario_results': scenario_results,
        'financial_params': financial_params
    }

if __name__ == "__main__":
    results = create_comprehensive_cost_analysis()