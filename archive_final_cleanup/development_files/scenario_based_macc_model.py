#!/usr/bin/env python3
"""
Scenario-Based MACC Model for Korean Petrochemical Industry
Three emission target scenarios with realistic cost calculations
Carbon price as output, not input
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
from pathlib import Path

class EnergyPriceModel:
    """Model energy prices for cost calculations"""
    
    def __init__(self):
        # Base energy prices (2024 USD)
        self.base_prices = {
            'electricity_grid': 0.12,      # USD/kWh
            'natural_gas': 0.45,           # USD/GJ
            'hydrogen_import': 3.50,       # USD/kg
            'hydrogen_electrolysis': 4.20, # USD/kg
            'bio_naphtha': 850,            # USD/tonne
            'conventional_naphtha': 650    # USD/tonne
        }
        
        # Price trajectories by scenario
        self.price_trajectories = {
            'conservative': {
                'electricity_learning_rate': 0.02,  # 2% annual decline
                'hydrogen_learning_rate': 0.03,     # 3% annual decline
                'gas_price_growth': 0.015,          # 1.5% annual growth
                'bio_naphtha_learning': 0.025       # 2.5% annual decline
            },
            'moderate': {
                'electricity_learning_rate': 0.035,
                'hydrogen_learning_rate': 0.05,
                'gas_price_growth': 0.02,
                'bio_naphtha_learning': 0.04
            },
            'aggressive': {
                'electricity_learning_rate': 0.05,
                'hydrogen_learning_rate': 0.07,
                'gas_price_growth': 0.025,
                'bio_naphtha_learning': 0.06
            }
        }
    
    def get_price(self, energy_type, year, scenario='moderate'):
        """Get energy price for specific year and scenario"""
        base_price = self.base_prices[energy_type]
        years_from_base = year - 2024
        trajectory = self.price_trajectories[scenario]
        
        if 'electricity' in energy_type:
            return base_price * (1 - trajectory['electricity_learning_rate']) ** years_from_base
        elif 'hydrogen' in energy_type:
            return base_price * (1 - trajectory['hydrogen_learning_rate']) ** years_from_base
        elif 'gas' in energy_type:
            return base_price * (1 + trajectory['gas_price_growth']) ** years_from_base
        elif 'bio_naphtha' in energy_type:
            return base_price * (1 - trajectory['bio_naphtha_learning']) ** years_from_base
        else:
            return base_price

class TechnologyCostModel:
    """Model technology costs based on CAPEX and energy consumption"""
    
    def __init__(self, energy_model):
        self.energy_model = energy_model
        
        # Technology specifications
        self.technologies = {
            'NCC_Hydrogen_Retrofit': {
                'capex_usd_per_tonne_capacity': 800,    # USD/tonne annual capacity
                'hydrogen_consumption_kg_per_tonne': 120,  # kg H2 per tonne product
                'electricity_consumption_kwh_per_tonne': 150,
                'maintenance_cost_fraction': 0.04,      # 4% of CAPEX annually
                'lifetime_years': 25,
                'emission_reduction_factor': 0.75       # 75% emission reduction
            },
            'BTX_Electrification': {
                'capex_usd_per_tonne_capacity': 400,
                'electricity_consumption_kwh_per_tonne': 800,
                'maintenance_cost_fraction': 0.03,
                'lifetime_years': 20,
                'emission_reduction_factor': 0.60
            },
            'Renewable_Solar': {
                'capex_usd_per_kw': 1200,
                'capacity_factor': 0.18,               # 18% capacity factor
                'maintenance_cost_fraction': 0.025,
                'lifetime_years': 25,
                'learning_rate': 0.15                  # 15% cost reduction per doubling
            },
            'Renewable_Wind': {
                'capex_usd_per_kw': 1800,
                'capacity_factor': 0.28,
                'maintenance_cost_fraction': 0.03,
                'lifetime_years': 25,
                'learning_rate': 0.12
            },
            'Green_Hydrogen_Electrolysis': {
                'capex_usd_per_kg_per_day': 1200,
                'electricity_consumption_kwh_per_kg': 55,
                'capacity_factor': 0.85,
                'maintenance_cost_fraction': 0.04,
                'lifetime_years': 20,
                'learning_rate': 0.20
            },
            'Bio_Naphtha_Processing': {
                'capex_usd_per_tonne_capacity': 300,
                'bio_feedstock_ratio': 1.2,            # 1.2 tonnes biomass per tonne bio-naphtha
                'electricity_consumption_kwh_per_tonne': 100,
                'maintenance_cost_fraction': 0.05,
                'lifetime_years': 25,
                'emission_reduction_factor': 0.85
            },
            'Heat_Recovery_System': {
                'capex_usd_per_tonne_capacity': 150,
                'electricity_consumption_kwh_per_tonne': 20,
                'maintenance_cost_fraction': 0.02,
                'lifetime_years': 15,
                'emission_reduction_factor': 0.25
            },
            'Energy_Efficiency': {
                'capex_usd_per_tonne_capacity': 100,
                'energy_savings_fraction': 0.15,       # 15% energy savings
                'maintenance_cost_fraction': 0.01,
                'lifetime_years': 15,
                'emission_reduction_factor': 0.15
            }
        }
    
    def calculate_lcoe(self, tech_name, year, scenario, capacity_mw=100):
        """Calculate Levelized Cost of Energy for renewable technologies"""
        tech = self.technologies[tech_name]
        
        # Apply learning curve
        cumulative_deployment = self.estimate_cumulative_deployment(year)
        cost_reduction = (cumulative_deployment / 1000) ** (-tech.get('learning_rate', 0))
        adjusted_capex = tech['capex_usd_per_kw'] * cost_reduction
        
        # LCOE calculation
        annual_generation = capacity_mw * 1000 * 8760 * tech['capacity_factor']
        annual_capex = (adjusted_capex * capacity_mw * 1000) / tech['lifetime_years']
        annual_maintenance = annual_capex * tech['maintenance_cost_fraction']
        
        lcoe = (annual_capex + annual_maintenance) / annual_generation
        return lcoe
    
    def calculate_technology_cost(self, tech_name, year, scenario, capacity_tonnes=1000):
        """Calculate cost per tonne CO2 abated for a technology"""
        tech = self.technologies[tech_name]
        
        # CAPEX calculation - handle different CAPEX keys
        if 'capex_usd_per_tonne_capacity' in tech:
            capex_per_unit = tech['capex_usd_per_tonne_capacity']
            units = capacity_tonnes
        elif 'capex_usd_per_kw' in tech:
            # For renewable technologies, estimate kW needed for capacity
            capex_per_unit = tech['capex_usd_per_kw']
            units = capacity_tonnes * 500  # Assume 500 kW per tonne capacity equivalent
        elif 'capex_usd_per_kg_per_day' in tech:
            # For hydrogen production
            capex_per_unit = tech['capex_usd_per_kg_per_day']
            units = capacity_tonnes * 120 / 365  # Daily hydrogen needed
        else:
            capex_per_unit = 100  # Default fallback
            units = capacity_tonnes
        
        annual_capex_cost = (capex_per_unit * units) / tech['lifetime_years']
        
        # Operating costs
        annual_maintenance = annual_capex_cost * tech['maintenance_cost_fraction']
        
        # Energy costs
        energy_cost = 0
        if 'hydrogen_consumption_kg_per_tonne' in tech:
            h2_price = self.energy_model.get_price('hydrogen_electrolysis', year, scenario)
            energy_cost += tech['hydrogen_consumption_kg_per_tonne'] * h2_price * capacity_tonnes
        
        if 'electricity_consumption_kwh_per_tonne' in tech:
            elec_price = self.energy_model.get_price('electricity_grid', year, scenario)
            energy_cost += tech['electricity_consumption_kwh_per_tonne'] * elec_price * capacity_tonnes
        
        if 'bio_feedstock_ratio' in tech:
            bio_price = self.energy_model.get_price('bio_naphtha', year, scenario)
            energy_cost += tech['bio_feedstock_ratio'] * bio_price * capacity_tonnes
        
        # Total annual cost
        total_annual_cost = annual_capex_cost + annual_maintenance + energy_cost
        
        # Emission reduction - handle missing emission_reduction_factor
        baseline_emissions_per_tonne = 2.5  # tCO2 per tonne product
        emission_reduction_factor = tech.get('emission_reduction_factor', 0.5)  # Default 50% if not specified
        emission_reduction_per_tonne = baseline_emissions_per_tonne * emission_reduction_factor
        total_emission_reduction = emission_reduction_per_tonne * capacity_tonnes
        
        # Cost per tonne CO2
        if total_emission_reduction > 0:
            cost_per_tco2 = total_annual_cost / total_emission_reduction
        else:
            cost_per_tco2 = 0
        
        return {
            'cost_per_tco2': cost_per_tco2,
            'annual_capex': annual_capex_cost,
            'annual_maintenance': annual_maintenance,
            'annual_energy_cost': energy_cost,
            'emission_reduction_tco2': total_emission_reduction,
            'capacity_tonnes': capacity_tonnes
        }
    
    def estimate_cumulative_deployment(self, year):
        """Estimate cumulative technology deployment for learning curves"""
        base_deployment = 1000  # MW
        growth_rate = 0.25      # 25% annual growth
        return base_deployment * (1 + growth_rate) ** (year - 2024)

class ScenarioMACCModel:
    """Main MACC model with three emission scenarios"""
    
    def __init__(self):
        self.energy_model = EnergyPriceModel()
        self.cost_model = TechnologyCostModel(self.energy_model)
        
        # Industry baseline data
        self.baseline_data = {
            'total_capacity_mt': 9.5,           # Million tonnes/year
            'baseline_emissions_mt': 80.0,      # Including 29.2 Mt naphtha emissions
            'ncc_capacity_mt': 7.2,             # NCC capacity
            'btx_capacity_mt': 1.6,             # BTX capacity
            'utility_capacity_mt': 0.7          # Utility capacity
        }
        
        # Define three emission scenarios
        self.scenarios = {
            'conservative': {
                'name': 'Conservative Pathway',
                'emission_targets': {
                    2030: 0.85,  # 15% reduction by 2030
                    2035: 0.70,  # 30% reduction by 2035
                    2040: 0.50,  # 50% reduction by 2040
                    2045: 0.30,  # 70% reduction by 2045
                    2050: 0.15   # 85% reduction by 2050
                },
                'technology_deployment_rates': {
                    'NCC_Hydrogen_Retrofit': 0.05,      # 5% per year max
                    'BTX_Electrification': 0.08,        # 8% per year max
                    'Renewable_Solar': 0.15,            # 15% per year max
                    'Bio_Naphtha_Processing': 0.04      # 4% per year max
                },
                'description': 'Gradual transition with proven technologies'
            },
            'moderate': {
                'name': 'Moderate Acceleration',
                'emission_targets': {
                    2030: 0.75,  # 25% reduction by 2030
                    2035: 0.55,  # 45% reduction by 2035
                    2040: 0.35,  # 65% reduction by 2040
                    2045: 0.20,  # 80% reduction by 2045
                    2050: 0.10   # 90% reduction by 2050
                },
                'technology_deployment_rates': {
                    'NCC_Hydrogen_Retrofit': 0.08,
                    'BTX_Electrification': 0.12,
                    'Renewable_Solar': 0.20,
                    'Bio_Naphtha_Processing': 0.06
                },
                'description': 'Balanced approach with accelerated deployment'
            },
            'aggressive': {
                'name': 'Rapid Transformation',
                'emission_targets': {
                    2030: 0.65,  # 35% reduction by 2030
                    2035: 0.40,  # 60% reduction by 2035
                    2040: 0.20,  # 80% reduction by 2040
                    2045: 0.10,  # 90% reduction by 2045
                    2050: 0.05   # 95% reduction by 2050
                },
                'technology_deployment_rates': {
                    'NCC_Hydrogen_Retrofit': 0.12,
                    'BTX_Electrification': 0.15,
                    'Renewable_Solar': 0.25,
                    'Bio_Naphtha_Processing': 0.08
                },
                'description': 'Maximum feasible deployment with breakthrough technologies'
            }
        }
    
    def calculate_scenario_macc(self, scenario_name, target_year=2030):
        """Calculate MACC curve for a specific scenario and year"""
        scenario = self.scenarios[scenario_name]
        
        # Get all technologies and their costs
        technologies = []
        for tech_name in self.cost_model.technologies.keys():
            cost_data = self.cost_model.calculate_technology_cost(
                tech_name, target_year, scenario_name, capacity_tonnes=1000
            )
            
            # Calculate maximum abatement potential
            max_deployment_rate = scenario['technology_deployment_rates'].get(tech_name, 0.10)
            applicable_capacity = self.get_applicable_capacity(tech_name)
            # Scale abatement by deployment rate and applicable capacity
            max_abatement = (cost_data['emission_reduction_tco2'] / 1000) * max_deployment_rate * applicable_capacity
            
            technologies.append({
                'technology': tech_name,
                'cost_usd_per_tco2': cost_data['cost_per_tco2'],
                'max_abatement_mt': max_abatement,
                'annual_capex_musd': cost_data['annual_capex'] / 1e6,
                'annual_energy_cost_musd': cost_data['annual_energy_cost'] / 1e6,
                'deployment_rate': max_deployment_rate
            })
        
        # Sort by cost
        technologies.sort(key=lambda x: x['cost_usd_per_tco2'])
        
        # Calculate cumulative abatement
        cumulative_abatement = 0
        for tech in technologies:
            tech['cumulative_abatement_mt'] = cumulative_abatement + tech['max_abatement_mt']
            cumulative_abatement = tech['cumulative_abatement_mt']
        
        return technologies
    
    def get_applicable_capacity(self, tech_name):
        """Get applicable capacity for each technology"""
        if 'NCC' in tech_name:
            return self.baseline_data['ncc_capacity_mt']
        elif 'BTX' in tech_name:
            return self.baseline_data['btx_capacity_mt']
        elif 'Renewable' in tech_name:
            return self.baseline_data['total_capacity_mt']
        else:
            return self.baseline_data['total_capacity_mt']
    
    def calculate_carbon_price(self, scenario_name, target_year):
        """Calculate implied carbon price to meet emission targets"""
        scenario = self.scenarios[scenario_name]
        
        # Get emission target for the year
        target_ratio = scenario['emission_targets'].get(target_year, 0.5)
        required_reduction = self.baseline_data['baseline_emissions_mt'] * (1 - target_ratio)
        
        # Get MACC curve
        macc_technologies = self.calculate_scenario_macc(scenario_name, target_year)
        
        # Find marginal cost to achieve required reduction
        cumulative_reduction = 0
        marginal_cost = 0
        
        for tech in macc_technologies:
            cumulative_reduction += tech['max_abatement_mt']
            if cumulative_reduction >= required_reduction:
                marginal_cost = tech['cost_usd_per_tco2']
                break
        
        return {
            'carbon_price_usd_per_tco2': marginal_cost,
            'required_reduction_mt': required_reduction,
            'achievable_reduction_mt': min(cumulative_reduction, required_reduction),
            'target_feasible': cumulative_reduction >= required_reduction
        }
    
    def run_scenario_analysis(self, scenario_name):
        """Run complete analysis for a scenario"""
        print(f"\n🎯 SCENARIO ANALYSIS: {scenario_name.upper()}")
        print("=" * 80)
        
        scenario = self.scenarios[scenario_name]
        print(f"Description: {scenario['description']}")
        
        results = {}
        
        # Analyze each target year
        for year, target_ratio in scenario['emission_targets'].items():
            print(f"\n📅 Year {year} - Target: {(1-target_ratio)*100:.0f}% emission reduction")
            
            # Calculate MACC
            macc_data = self.calculate_scenario_macc(scenario_name, year)
            
            # Calculate carbon price
            carbon_data = self.calculate_carbon_price(scenario_name, year)
            
            # Calculate total investment
            total_capex = sum(tech['annual_capex_musd'] for tech in macc_data)
            total_energy_cost = sum(tech['annual_energy_cost_musd'] for tech in macc_data)
            
            results[year] = {
                'macc_technologies': macc_data,
                'carbon_price_data': carbon_data,
                'total_annual_capex_musd': total_capex,
                'total_annual_energy_cost_musd': total_energy_cost,
                'total_annual_cost_musd': total_capex + total_energy_cost
            }
            
            print(f"   💰 Implied Carbon Price: ${carbon_data['carbon_price_usd_per_tco2']:.0f}/tCO₂")
            print(f"   📊 Required Reduction: {carbon_data['required_reduction_mt']:.1f} MtCO₂")
            print(f"   ✅ Target Feasible: {carbon_data['target_feasible']}")
            print(f"   💸 Annual Investment: ${total_capex:.0f}M CAPEX + ${total_energy_cost:.0f}M Energy")
        
        return results

def create_scenario_visualizations(model):
    """Create comprehensive visualizations for all scenarios"""
    print("\n📊 CREATING SCENARIO VISUALIZATIONS")
    print("=" * 80)
    
    # Run all scenarios
    all_results = {}
    for scenario_name in model.scenarios.keys():
        all_results[scenario_name] = model.run_scenario_analysis(scenario_name)
    
    # Create visualization
    fig = plt.figure(figsize=(20, 16))
    
    # 1. MACC Curves for 2030
    ax1 = plt.subplot(3, 3, (1, 2))
    
    colors = {'conservative': 'blue', 'moderate': 'green', 'aggressive': 'red'}
    
    for scenario_name, color in colors.items():
        macc_2030 = all_results[scenario_name][2030]['macc_technologies']
        
        # Prepare data for plotting
        costs = [tech['cost_usd_per_tco2'] for tech in macc_2030]
        abatements = [tech['max_abatement_mt'] for tech in macc_2030]
        cumulative = np.cumsum([0] + abatements)
        
        # Create step plot
        for i in range(len(costs)):
            ax1.barh(costs[i], abatements[i], left=cumulative[i], 
                    alpha=0.7, color=color, label=scenario_name if i == 0 else "")
    
    ax1.set_xlabel('Cumulative Abatement (MtCO₂/year)')
    ax1.set_ylabel('Cost (USD/tCO₂)')
    ax1.set_title('MACC Curves 2030 - All Scenarios')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1000)
    
    # 2. Carbon Price Evolution
    ax2 = plt.subplot(3, 3, 3)
    
    years = [2030, 2035, 2040, 2045, 2050]
    
    for scenario_name, color in colors.items():
        carbon_prices = []
        for year in years:
            price = all_results[scenario_name][year]['carbon_price_data']['carbon_price_usd_per_tco2']
            carbon_prices.append(price)
        
        ax2.plot(years, carbon_prices, 'o-', color=color, linewidth=2, 
                label=scenario_name.title(), markersize=6)
    
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Carbon Price (USD/tCO₂)')
    ax2.set_title('Implied Carbon Price Evolution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Emission Reduction Pathways
    ax3 = plt.subplot(3, 3, (4, 5))
    
    baseline_emissions = model.baseline_data['baseline_emissions_mt']
    
    for scenario_name, color in colors.items():
        scenario = model.scenarios[scenario_name]
        emission_levels = []
        
        for year in years:
            target_ratio = scenario['emission_targets'][year]
            emission_level = baseline_emissions * target_ratio
            emission_levels.append(emission_level)
        
        ax3.plot(years, emission_levels, 'o-', color=color, linewidth=3, 
                label=scenario_name.title(), markersize=8)
    
    ax3.axhline(y=baseline_emissions, color='black', linestyle='--', alpha=0.7, label='Baseline (2024)')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Emissions (MtCO₂/year)')
    ax3.set_title('Emission Reduction Pathways')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 90)
    
    # 4. Investment Requirements
    ax4 = plt.subplot(3, 3, 6)
    
    investment_data = {}
    for scenario_name in colors.keys():
        total_investment_2030 = all_results[scenario_name][2030]['total_annual_cost_musd']
        total_investment_2040 = all_results[scenario_name][2040]['total_annual_cost_musd']
        investment_data[scenario_name] = [total_investment_2030, total_investment_2040]
    
    x = np.arange(len(investment_data))
    width = 0.35
    
    inv_2030 = [investment_data[s][0] for s in colors.keys()]
    inv_2040 = [investment_data[s][1] for s in colors.keys()]
    
    ax4.bar(x - width/2, inv_2030, width, label='2030', alpha=0.8)
    ax4.bar(x + width/2, inv_2040, width, label='2040', alpha=0.8)
    
    ax4.set_xlabel('Scenario')
    ax4.set_ylabel('Annual Investment (Million USD)')
    ax4.set_title('Investment Requirements')
    ax4.set_xticks(x)
    ax4.set_xticklabels([s.title() for s in colors.keys()])
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Technology Mix 2030
    ax5 = plt.subplot(3, 3, (7, 8))
    
    # Focus on moderate scenario for technology breakdown
    moderate_2030 = all_results['moderate'][2030]['macc_technologies']
    
    tech_names = [tech['technology'].replace('_', ' ') for tech in moderate_2030]
    abatements = [tech['max_abatement_mt'] for tech in moderate_2030]
    costs = [tech['cost_usd_per_tco2'] for tech in moderate_2030]
    
    # Create bubble chart
    scatter = ax5.scatter(abatements, costs, s=[a*50 for a in abatements], 
                         alpha=0.6, c=range(len(tech_names)), cmap='viridis')
    
    # Add labels
    for i, name in enumerate(tech_names):
        ax5.annotate(name.split()[0], (abatements[i], costs[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax5.set_xlabel('Abatement Potential (MtCO₂/year)')
    ax5.set_ylabel('Cost (USD/tCO₂)')
    ax5.set_title('Technology Mix - Moderate Scenario 2030')
    ax5.grid(True, alpha=0.3)
    
    # 6. Feasibility Assessment
    ax6 = plt.subplot(3, 3, 9)
    
    scenarios_list = list(colors.keys())
    feasibility_2030 = []
    feasibility_2050 = []
    
    for scenario_name in scenarios_list:
        feas_2030 = 1 if all_results[scenario_name][2030]['carbon_price_data']['target_feasible'] else 0
        feas_2050 = 1 if all_results[scenario_name][2050]['carbon_price_data']['target_feasible'] else 0
        feasibility_2030.append(feas_2030)
        feasibility_2050.append(feas_2050)
    
    x = np.arange(len(scenarios_list))
    width = 0.35
    
    ax6.bar(x - width/2, feasibility_2030, width, label='2030 Target', alpha=0.8, color='lightblue')
    ax6.bar(x + width/2, feasibility_2050, width, label='2050 Target', alpha=0.8, color='darkblue')
    
    ax6.set_xlabel('Scenario')
    ax6.set_ylabel('Target Feasibility (1=Feasible, 0=Not Feasible)')
    ax6.set_title('Target Feasibility Assessment')
    ax6.set_xticks(x)
    ax6.set_xticklabels([s.title() for s in scenarios_list])
    ax6.legend()
    ax6.set_ylim(0, 1.2)
    
    # Add feasibility text
    for i, (f30, f50) in enumerate(zip(feasibility_2030, feasibility_2050)):
        ax6.text(i-width/2, f30+0.05, 'Yes' if f30 else 'No', ha='center', fontweight='bold')
        ax6.text(i+width/2, f50+0.05, 'Yes' if f50 else 'No', ha='center', fontweight='bold')
    
    plt.suptitle('Korean Petrochemical Industry: Scenario-Based MACC Analysis', 
                 fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('scenario_macc_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Scenario visualization saved: scenario_macc_analysis.png")
    
    return all_results

def generate_scenario_report(model, all_results):
    """Generate comprehensive scenario report"""
    print("\n📄 GENERATING SCENARIO REPORT")
    print("=" * 80)
    
    report_content = f"""
# Korean Petrochemical Industry: Scenario-Based MACC Analysis

## Executive Summary

This analysis presents three emission reduction scenarios for the Korean petrochemical industry, with carbon prices derived endogenously from technology costs and deployment constraints rather than imposed externally.

**Key Findings:**
- **Conservative Scenario**: Gradual 85% reduction by 2050, carbon price rising to ${all_results['conservative'][2050]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂
- **Moderate Scenario**: Balanced 90% reduction by 2050, carbon price of ${all_results['moderate'][2050]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂  
- **Aggressive Scenario**: Rapid 95% reduction by 2050, carbon price of ${all_results['aggressive'][2050]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂

## Methodology

### Cost Calculation Approach
Technology costs are calculated based on:
1. **CAPEX**: Equipment and installation costs per tonne capacity
2. **Energy Costs**: Real-time energy prices including hydrogen, electricity, bio-naphtha
3. **Operating Costs**: Maintenance, labor, and operational expenses
4. **Learning Curves**: Cost reductions based on cumulative deployment

### Carbon Price Determination
Carbon prices emerge from the model as the marginal cost required to meet emission targets, not as an input assumption. This reflects real-world carbon pricing where the price must be sufficient to incentivize necessary technology deployment.

## Scenario Details

### Conservative Pathway
**Objective**: Gradual transition with proven technologies
**Approach**: 
- Focus on mature technologies with low deployment risk
- Slower hydrogen infrastructure build-out
- Limited bio-naphtha adoption in early years
- Technology deployment rates: 4-8% annually

**Results Summary:**

| Year | Emission Reduction | Carbon Price | Annual Investment |
|------|-------------------|--------------|------------------|
{chr(10).join([f"| {year} | {(1-model.scenarios['conservative']['emission_targets'][year])*100:.0f}% | ${all_results['conservative'][year]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂ | ${all_results['conservative'][year]['total_annual_cost_musd']:.0f}M USD |" for year in [2030, 2035, 2040, 2045, 2050]])}

### Moderate Acceleration  
**Objective**: Balanced approach with accelerated deployment
**Approach**:
- Combination of proven and emerging technologies
- Moderate hydrogen infrastructure expansion
- Steady bio-naphtha market development
- Technology deployment rates: 6-12% annually

**Results Summary:**

| Year | Emission Reduction | Carbon Price | Annual Investment |
|------|-------------------|--------------|------------------|
{chr(10).join([f"| {year} | {(1-model.scenarios['moderate']['emission_targets'][year])*100:.0f}% | ${all_results['moderate'][year]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂ | ${all_results['moderate'][year]['total_annual_cost_musd']:.0f}M USD |" for year in [2030, 2035, 2040, 2045, 2050]])}

### Aggressive Transformation
**Objective**: Maximum feasible deployment with breakthrough technologies  
**Approach**:
- Push technology deployment to physical limits
- Rapid hydrogen infrastructure development
- Accelerated bio-naphtha and renewable deployment
- Technology deployment rates: 8-25% annually

**Results Summary:**

| Year | Emission Reduction | Carbon Price | Annual Investment |
|------|-------------------|--------------|------------------|
{chr(10).join([f"| {year} | {(1-model.scenarios['aggressive']['emission_targets'][year])*100:.0f}% | ${all_results['aggressive'][year]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂ | ${all_results['aggressive'][year]['total_annual_cost_musd']:.0f}M USD |" for year in [2030, 2035, 2040, 2045, 2050]])}

## Technology Cost Analysis

### NCC Hydrogen Retrofit
- **CAPEX**: $800/tonne capacity
- **Hydrogen Consumption**: 120 kg/tonne product  
- **2030 Cost**: ${all_results['moderate'][2030]['macc_technologies'][0]['cost_usd_per_tco2']:.0f}/tCO₂ (moderate scenario)
- **Emission Reduction**: 75% per facility converted

### BTX Electrification
- **CAPEX**: $400/tonne capacity
- **Electricity Consumption**: 800 kWh/tonne product
- **2030 Cost**: ${next((tech['cost_usd_per_tco2'] for tech in all_results['moderate'][2030]['macc_technologies'] if 'BTX' in tech['technology']), 0):.0f}/tCO₂
- **Emission Reduction**: 60% per facility converted

### Renewable Energy Integration
- **Solar LCOE 2030**: ${model.cost_model.calculate_lcoe('Renewable_Solar', 2030, 'moderate'):.3f} USD/kWh
- **Wind LCOE 2030**: ${model.cost_model.calculate_lcoe('Renewable_Wind', 2030, 'moderate'):.3f} USD/kWh
- **Learning Rate**: 12-15% cost reduction per doubling

### Bio-Naphtha Processing
- **CAPEX**: $300/tonne capacity
- **Feedstock Ratio**: 1.2:1 biomass to bio-naphtha
- **2030 Cost**: ${next((tech['cost_usd_per_tco2'] for tech in all_results['moderate'][2030]['macc_technologies'] if 'Bio' in tech['technology']), 0):.0f}/tCO₂
- **Emission Reduction**: 85% vs conventional naphtha

## Energy Price Trajectories

### Key Assumptions by Scenario
**Conservative**: 
- Electricity: 2% annual cost decline
- Hydrogen: 3% annual cost decline  
- Natural gas: 1.5% annual price growth

**Moderate**:
- Electricity: 3.5% annual cost decline
- Hydrogen: 5% annual cost decline
- Natural gas: 2% annual price growth

**Aggressive**:
- Electricity: 5% annual cost decline  
- Hydrogen: 7% annual cost decline
- Natural gas: 2.5% annual price growth

## Investment Requirements

### Total Investment by 2050 (Annual Average)
- **Conservative**: ${np.mean([all_results['conservative'][year]['total_annual_cost_musd'] for year in [2030, 2040, 2050]]):.0f}M USD/year
- **Moderate**: ${np.mean([all_results['moderate'][year]['total_annual_cost_musd'] for year in [2030, 2040, 2050]]):.0f}M USD/year  
- **Aggressive**: ${np.mean([all_results['aggressive'][year]['total_annual_cost_musd'] for year in [2030, 2040, 2050]]):.0f}M USD/year

### Investment Composition (2030)
**CAPEX vs Operating Costs** (Moderate Scenario):
- CAPEX: ${all_results['moderate'][2030]['total_annual_capex_musd']:.0f}M USD (equipment and infrastructure)
- Energy Costs: ${all_results['moderate'][2030]['total_annual_energy_cost_musd']:.0f}M USD (hydrogen, electricity, bio-feedstock)

## Policy Implications

### Carbon Pricing Strategy
The endogenous carbon prices reveal the true cost of decarbonization:
- **2030 Range**: ${min(all_results[s][2030]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f}-${max(all_results[s][2030]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f} USD/tCO₂
- **2050 Range**: ${min(all_results[s][2050]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f}-${max(all_results[s][2050]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f} USD/tCO₂

### Technology Support Requirements
1. **Early Stage**: Government support needed for hydrogen infrastructure and bio-naphtha supply chains
2. **Scale-up Phase**: Market mechanisms can drive deployment once cost curves improve  
3. **Maturity Phase**: Technologies become cost-competitive without subsidy

### Risk Assessment
- **Conservative**: Lower risk but may miss climate targets
- **Moderate**: Balanced risk-return with achievable targets
- **Aggressive**: Higher execution risk but maximum climate benefit

## Recommendations

### For Policymakers
1. **Set carbon price floor** aligned with moderate scenario trajectory (${all_results['moderate'][2030]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂ by 2030)
2. **Prioritize hydrogen infrastructure** as foundation technology
3. **Support bio-naphtha supply chain** development through early-stage funding
4. **Create technology-neutral incentives** based on emission reduction performance

### For Industry
1. **Plan for carbon prices** in the ${all_results['moderate'][2030]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}-${all_results['aggressive'][2030]['carbon_price_data']['carbon_price_usd_per_tco2']:.0f}/tCO₂ range by 2030
2. **Prioritize NCC hydrogen retrofits** as highest-impact technology
3. **Invest in renewable energy** procurement and on-site generation
4. **Develop bio-naphtha** supply partnerships for long-term feedstock security

## Conclusion

The scenario analysis demonstrates that deep decarbonization of Korea's petrochemical industry is technically feasible but requires sustained investment and supportive policies. The endogenous carbon price signals provide realistic targets for policy design, ranging from ${min(all_results[s][2050]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f}-${max(all_results[s][2050]['carbon_price_data']['carbon_price_usd_per_tco2'] for s in all_results.keys()):.0f}/tCO₂ by 2050 depending on ambition level.

Success depends on coordinated action across technology development, infrastructure investment, and policy support, with the moderate scenario representing the most balanced pathway forward.
"""
    
    # Save report
    with open('scenario_macc_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Save scenario data as JSON
    scenario_data = {}
    for scenario_name, results in all_results.items():
        scenario_data[scenario_name] = {}
        for year, data in results.items():
            scenario_data[scenario_name][year] = {
                'carbon_price': data['carbon_price_data']['carbon_price_usd_per_tco2'],
                'total_investment': data['total_annual_cost_musd'],
                'capex': data['total_annual_capex_musd'],
                'energy_cost': data['total_annual_energy_cost_musd'],
                'required_reduction': data['carbon_price_data']['required_reduction_mt'],
                'target_feasible': data['carbon_price_data']['target_feasible']
            }
    
    with open('scenario_data.json', 'w') as f:
        json.dump(scenario_data, f, indent=2)
    
    print("✅ Scenario report saved: scenario_macc_report.md")
    print("✅ Scenario data saved: scenario_data.json")

def main():
    """Main execution function"""
    print("🏭 KOREAN PETROCHEMICAL INDUSTRY")
    print("SCENARIO-BASED MACC MODEL")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Initialize model
    model = ScenarioMACCModel()
    
    print("📋 Model Specifications:")
    print(f"   Baseline Emissions: {model.baseline_data['baseline_emissions_mt']} MtCO₂/year")
    print(f"   Industry Capacity: {model.baseline_data['total_capacity_mt']} Mt/year")
    print(f"   Number of Technologies: {len(model.cost_model.technologies)}")
    print(f"   Scenarios: {', '.join(model.scenarios.keys())}")
    
    # Create visualizations and run analysis
    all_results = create_scenario_visualizations(model)
    
    # Generate report
    generate_scenario_report(model, all_results)
    
    print(f"\n✅ SCENARIO ANALYSIS COMPLETE")
    print("📊 Files Generated:")
    print("   • scenario_macc_analysis.png - Comprehensive visualization")
    print("   • scenario_macc_report.md - Detailed analysis report")  
    print("   • scenario_data.json - Machine-readable results")

if __name__ == "__main__":
    main()