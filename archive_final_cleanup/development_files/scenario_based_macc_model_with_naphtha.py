#!/usr/bin/env python3
"""
Scenario-Based MACC Model with Internalized Naphtha Emissions
Korean Petrochemical Industry with corrected emission baseline
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
from pathlib import Path

class NaphthaEmissionIntegration:
    """Integrate naphtha lifecycle emissions into MACC model"""

    def __init__(self):
        # Naphtha external GHG factor (tCO2e/t naphtha)
        self.naphtha_external_ghg_factor = 0.90

        # Facility-level naphtha consumption (Mt/year per facility)
        self.facility_naphtha_consumption = {
            'ncc': 0.461,
            'btx': 0.072,
            'utility': 0.009
        }

        # Product-specific emission factors (tCO2e/t product)
        self.product_emission_factors = {
            'ethylene': 2.79,
            'propylene': 2.52,
            'btx': 1.26,
            'other': 1.62
        }

        # Bio-naphtha technology parameters
        self.bio_naphtha_technology = {
            'emission_reduction_factor': 0.85,
            'marginal_abatement_cost': 272,  # USD/tCO2e
            'capex_usd_per_t_capacity': 300,
            'feedstock_premium_usd_per_t': 200,
            'max_deployment_share_2050': 0.40
        }

    def calculate_baseline_naphtha_emissions(self, facility_data):
        """Calculate baseline naphtha emissions for each facility"""
        baseline_emissions = {}

        for facility_id, facility in facility_data.items():
            facility_type = facility['type'].lower()
            if facility_type in self.facility_naphtha_consumption:
                naphtha_consumption = self.facility_naphtha_consumption[facility_type]
                naphtha_emissions = naphtha_consumption * self.naphtha_external_ghg_factor

                baseline_emissions[facility_id] = {
                    'naphtha_consumption_mt': naphtha_consumption,
                    'naphtha_emissions_mtco2': naphtha_emissions,
                    'original_emissions_mtco2': facility.get('baseline_emissions', 0),
                    'corrected_emissions_mtco2': facility.get('baseline_emissions', 0) + naphtha_emissions
                }

        return baseline_emissions

    def add_bio_naphtha_technology(self, technology_portfolio):
        """Add bio-naphtha as abatement technology"""

        bio_naphtha_tech = {
            'technology_id': 'BIO_NAPHTHA',
            'name': 'Bio-Naphtha Feedstock Substitution',
            'applicable_facilities': ['NCC', 'BTX', 'UTILITY'],
            'emission_reduction_factor': self.bio_naphtha_technology['emission_reduction_factor'],
            'capex_usd_per_t_capacity': self.bio_naphtha_technology['capex_usd_per_t_capacity'],
            'opex_usd_per_t_annual': self.bio_naphtha_technology['feedstock_premium_usd_per_t'],
            'marginal_cost_usd_per_tco2': self.bio_naphtha_technology['marginal_abatement_cost'],
            'max_penetration_by_year': {
                2030: 0.10,
                2040: 0.25,
                2050: 0.40
            },
            'learning_curve_rate': 0.15
        }

        technology_portfolio['BIO_NAPHTHA'] = bio_naphtha_tech
        return technology_portfolio

    def calculate_bio_naphtha_deployment(self, scenario_targets, year):
        """Calculate optimal bio-naphtha deployment for scenario"""

        # Get deployment constraint for year
        max_share = self.bio_naphtha_technology['max_deployment_share_2050']
        if year <= 2030:
            max_share = 0.10
        elif year <= 2040:
            max_share = 0.25

        # Calculate emission reduction potential
        total_naphtha_consumption = 32.4  # Mt/year
        potential_emission_reduction = (
            total_naphtha_consumption * max_share *
            self.naphtha_external_ghg_factor *
            self.bio_naphtha_technology['emission_reduction_factor']
        )

        return {
            'max_deployment_share': max_share,
            'potential_emission_reduction_mtco2': potential_emission_reduction,
            'marginal_cost_usd_per_tco2': self.bio_naphtha_technology['marginal_abatement_cost']
        }

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
                'electricity_learning_rate': 0.02,
                'hydrogen_learning_rate': 0.03,
                'gas_price_growth': 0.015,
                'bio_naphtha_learning': 0.025
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

class CorrectedIndustryBaseline:
    """Industry baseline with corrected naphtha emissions"""

    def __init__(self):
        # Initialize naphtha integration
        self.naphtha_integration = NaphthaEmissionIntegration()

        # Facility data with corrected emissions
        self.facilities = {
            'ncc': {
                'count': 41,
                'capacity_mt_per_facility': 0.15,  # Mt/year ethylene equivalent
                'original_emissions_mtco2_per_facility': 1.24,  # Without naphtha external
                'corrected_emissions_mtco2_per_facility': 1.24 + 0.415,  # With naphtha external
                'primary_product': 'ethylene',
                'applicable_technologies': ['NCC_Hydrogen_Retrofit', 'Renewable_Energy', 'Energy_Efficiency', 'BIO_NAPHTHA']
            },
            'btx': {
                'count': 47,
                'capacity_mt_per_facility': 0.087,  # Mt/year BTX equivalent
                'original_emissions_mtco2_per_facility': 0.68,
                'corrected_emissions_mtco2_per_facility': 0.68 + 0.065,
                'primary_product': 'aromatics',
                'applicable_technologies': ['BTX_Electrification', 'Renewable_Energy', 'Energy_Efficiency', 'BIO_NAPHTHA']
            },
            'utility': {
                'count': 160,
                'capacity_mt_per_facility': 0.059,  # Mt/year steam equivalent
                'original_emissions_mtco2_per_facility': 0.32,
                'corrected_emissions_mtco2_per_facility': 0.32 + 0.008,
                'primary_product': 'utilities',
                'applicable_technologies': ['Renewable_Energy', 'Energy_Efficiency', 'Heat_Recovery', 'BIO_NAPHTHA']
            }
        }

        # Calculate totals
        self.total_facilities = sum([data['count'] for data in self.facilities.values()])
        self.original_total_emissions = sum([
            data['count'] * data['original_emissions_mtco2_per_facility']
            for data in self.facilities.values()
        ])
        self.corrected_total_emissions = sum([
            data['count'] * data['corrected_emissions_mtco2_per_facility']
            for data in self.facilities.values()
        ])
        self.naphtha_emission_increase = self.corrected_total_emissions - self.original_total_emissions

        print(f"🏭 Industry Baseline (Corrected):")
        print(f"   Total facilities: {self.total_facilities}")
        print(f"   Original emissions: {self.original_total_emissions:.1f} MtCO₂e/year")
        print(f"   Naphtha external emissions: {self.naphtha_emission_increase:.1f} MtCO₂e/year")
        print(f"   Corrected total emissions: {self.corrected_total_emissions:.1f} MtCO₂e/year")

class TechnologyCostModel:
    """Model technology costs with bio-naphtha integration"""

    def __init__(self, energy_model, naphtha_integration):
        self.energy_model = energy_model
        self.naphtha_integration = naphtha_integration

        # Enhanced technology specifications including bio-naphtha
        self.technologies = {
            'NCC_Hydrogen_Retrofit': {
                'capex_usd_per_tonne_capacity': 800,
                'hydrogen_consumption_kg_per_tonne': 120,
                'electricity_consumption_kwh_per_tonne': 150,
                'maintenance_cost_fraction': 0.04,
                'lifetime_years': 25,
                'emission_reduction_factor': 0.75,
                'applicable_facilities': ['ncc']
            },
            'BTX_Electrification': {
                'capex_usd_per_tonne_capacity': 400,
                'electricity_consumption_kwh_per_tonne': 800,
                'maintenance_cost_fraction': 0.03,
                'lifetime_years': 20,
                'emission_reduction_factor': 0.60,
                'applicable_facilities': ['btx']
            },
            'Renewable_Solar': {
                'capex_usd_per_kw': 1200,
                'capacity_factor': 0.18,
                'maintenance_cost_fraction': 0.025,
                'lifetime_years': 25,
                'learning_rate': 0.15,
                'applicable_facilities': ['ncc', 'btx', 'utility']
            },
            'Renewable_Wind': {
                'capex_usd_per_kw': 1800,
                'capacity_factor': 0.35,
                'maintenance_cost_fraction': 0.03,
                'lifetime_years': 25,
                'learning_rate': 0.12,
                'applicable_facilities': ['ncc', 'btx', 'utility']
            },
            'Green_Hydrogen_Electrolysis': {
                'capex_usd_per_kg_day_capacity': 1200,
                'electricity_consumption_kwh_per_kg': 50,
                'maintenance_cost_fraction': 0.04,
                'lifetime_years': 20,
                'learning_rate': 0.18,
                'applicable_facilities': ['ncc']
            },
            'Energy_Efficiency': {
                'capex_usd_per_tonne_capacity': 100,
                'maintenance_cost_fraction': 0.02,
                'lifetime_years': 15,
                'emission_reduction_factor': 0.15,
                'applicable_facilities': ['ncc', 'btx', 'utility']
            },
            'Heat_Recovery': {
                'capex_usd_per_tonne_capacity': 150,
                'maintenance_cost_fraction': 0.025,
                'lifetime_years': 20,
                'emission_reduction_factor': 0.20,
                'applicable_facilities': ['utility']
            },
            'BIO_NAPHTHA': {
                'capex_usd_per_t_capacity': 300,
                'feedstock_premium_usd_per_t': 200,
                'maintenance_cost_fraction': 0.03,
                'lifetime_years': 25,
                'emission_reduction_factor': 0.85,  # 85% reduction vs conventional naphtha
                'marginal_cost_usd_per_tco2': 272,  # From naphtha integration
                'applicable_facilities': ['ncc', 'btx', 'utility'],
                'max_penetration_by_year': {
                    2030: 0.10,
                    2040: 0.25,
                    2050: 0.40
                }
            }
        }

    def calculate_levelized_cost(self, technology, year, scenario='moderate', capacity_tonnes=1.0):
        """Calculate levelized cost per tonne capacity per year"""
        tech_data = self.technologies[technology]

        # Basic cost components
        capex = tech_data.get('capex_usd_per_tonne_capacity', 0)
        if capex == 0:
            capex = tech_data.get('capex_usd_per_t_capacity', 0)  # For BIO_NAPHTHA

        maintenance_rate = tech_data.get('maintenance_cost_fraction', 0.03)
        lifetime = tech_data.get('lifetime_years', 20)

        # Apply learning curves if applicable
        if 'learning_rate' in tech_data:
            years_from_base = max(0, year - 2024)
            # Assume cumulative deployment doubles every 3 years
            doublings = years_from_base / 3
            cost_reduction = (1 - tech_data['learning_rate']) ** doublings
            capex *= cost_reduction

        # Annualize CAPEX
        discount_rate = 0.08
        annualized_capex = capex * (
            discount_rate * (1 + discount_rate)**lifetime
        ) / ((1 + discount_rate)**lifetime - 1)

        # Calculate operating costs
        annual_opex = capex * maintenance_rate

        # Add energy costs for specific technologies
        if technology == 'NCC_Hydrogen_Retrofit':
            h2_consumption = tech_data['hydrogen_consumption_kg_per_tonne']
            h2_price = self.energy_model.get_price('hydrogen_electrolysis', year, scenario)
            annual_opex += h2_consumption * h2_price

            elec_consumption = tech_data['electricity_consumption_kwh_per_tonne']
            elec_price = self.energy_model.get_price('electricity_grid', year, scenario)
            annual_opex += elec_consumption * elec_price

        elif technology == 'BTX_Electrification':
            elec_consumption = tech_data['electricity_consumption_kwh_per_tonne']
            elec_price = self.energy_model.get_price('electricity_grid', year, scenario)
            annual_opex += elec_consumption * elec_price

        elif technology == 'BIO_NAPHTHA':
            # Bio-naphtha feedstock premium
            feedstock_premium = tech_data['feedstock_premium_usd_per_t']
            # Assume 3.0 tonnes average naphtha per tonne product capacity
            annual_opex += feedstock_premium * 3.0

        total_levelized_cost = annualized_capex + annual_opex

        return total_levelized_cost

    def calculate_marginal_abatement_cost(self, technology, year, scenario='moderate',
                                        facility_type='ncc'):
        """Calculate marginal abatement cost ($/tCO2e)"""

        tech_data = self.technologies[technology]

        # Get levelized cost
        levelized_cost = self.calculate_levelized_cost(technology, year, scenario)

        # Get emission reduction
        emission_reduction_factor = tech_data.get('emission_reduction_factor', 0)

        # Get baseline emissions for facility type
        baseline = CorrectedIndustryBaseline()
        facility_baseline_emissions = baseline.facilities[facility_type]['corrected_emissions_mtco2_per_facility']

        # Calculate emission reduction per facility
        if technology == 'BIO_NAPHTHA':
            # For bio-naphtha, calculate reduction based on naphtha consumption
            naphtha_consumption = self.naphtha_integration.facility_naphtha_consumption[facility_type]
            naphtha_emission_reduction = (
                naphtha_consumption *
                self.naphtha_integration.naphtha_external_ghg_factor *
                emission_reduction_factor
            )
            emissions_reduced_per_facility = naphtha_emission_reduction
        else:
            emissions_reduced_per_facility = facility_baseline_emissions * emission_reduction_factor

        # Convert to emissions reduced per tonne capacity
        facility_capacity = baseline.facilities[facility_type]['capacity_mt_per_facility']
        emissions_reduced_per_tonne_capacity = emissions_reduced_per_facility / facility_capacity * 1000  # Convert to tCO2e

        # Calculate marginal abatement cost
        if emissions_reduced_per_tonne_capacity > 0:
            marginal_cost = levelized_cost / emissions_reduced_per_tonne_capacity
        else:
            marginal_cost = float('inf')

        return {
            'marginal_cost_usd_per_tco2': marginal_cost,
            'levelized_cost_usd_per_tonne': levelized_cost,
            'emissions_reduced_tco2_per_tonne': emissions_reduced_per_tonne_capacity,
            'emission_reduction_factor': emission_reduction_factor
        }

class ScenarioMACCModel:
    """Main MACC model with scenario analysis and corrected naphtha emissions"""

    def __init__(self):
        self.naphtha_integration = NaphthaEmissionIntegration()
        self.energy_model = EnergyPriceModel()
        self.cost_model = TechnologyCostModel(self.energy_model, self.naphtha_integration)
        self.baseline = CorrectedIndustryBaseline()

        # Emission reduction scenarios
        self.scenarios = {
            'conservative': {
                'targets': {
                    2030: 0.15,  # 15% reduction from corrected baseline
                    2040: 0.50,  # 50% reduction
                    2050: 0.85   # 85% reduction
                },
                'description': 'Gradual transition with proven technologies'
            },
            'moderate': {
                'targets': {
                    2030: 0.25,  # 25% reduction from corrected baseline
                    2040: 0.65,  # 65% reduction
                    2050: 0.90   # 90% reduction
                },
                'description': 'Balanced approach with accelerated deployment'
            },
            'aggressive': {
                'targets': {
                    2030: 0.35,  # 35% reduction from corrected baseline
                    2040: 0.80,  # 80% reduction
                    2050: 0.95   # 95% reduction
                },
                'description': 'Maximum feasible deployment'
            }
        }

        print(f"🎯 Scenario Targets (from corrected baseline of {self.baseline.corrected_total_emissions:.1f} MtCO₂e):")
        for scenario_name, scenario in self.scenarios.items():
            print(f"   {scenario_name.title()}:")
            for year, target in scenario['targets'].items():
                emission_target = self.baseline.corrected_total_emissions * (1 - target)
                reduction_needed = self.baseline.corrected_total_emissions * target
                print(f"     {year}: {target:.0%} reduction → {emission_target:.1f} MtCO₂e target ({reduction_needed:.1f} MtCO₂e reduction)")

    def calculate_technology_macc_curve(self, scenario='moderate', year=2050):
        """Calculate MACC curve for all technologies in given scenario and year"""

        print(f"\n📊 CALCULATING MACC CURVE: {scenario.title()} Scenario, {year}")
        print("=" * 80)

        macc_data = []

        # Calculate costs for each technology-facility combination
        for tech_name, tech_data in self.cost_model.technologies.items():
            applicable_facilities = tech_data.get('applicable_facilities', ['ncc', 'btx', 'utility'])

            for facility_type in applicable_facilities:
                # Skip if facility type doesn't exist
                if facility_type not in self.baseline.facilities:
                    continue

                # Calculate marginal abatement cost
                try:
                    mac_result = self.cost_model.calculate_marginal_abatement_cost(
                        tech_name, year, scenario, facility_type
                    )

                    # Calculate potential deployment and emission reduction
                    facility_data = self.baseline.facilities[facility_type]
                    total_facilities = facility_data['count']
                    capacity_per_facility = facility_data['capacity_mt_per_facility']

                    # Apply deployment constraints for bio-naphtha
                    if tech_name == 'BIO_NAPHTHA':
                        max_penetration = tech_data['max_penetration_by_year'].get(year, 0.40)
                        deployment_factor = max_penetration
                    else:
                        # Assume 80% max penetration for other technologies
                        deployment_factor = 0.80

                    # Calculate total emission reduction potential
                    total_capacity = total_facilities * capacity_per_facility
                    total_emission_reduction = (
                        mac_result['emissions_reduced_tco2_per_tonne'] *
                        total_capacity *
                        deployment_factor *
                        1000  # Convert to ktCO2e
                    )

                    macc_data.append({
                        'technology': tech_name,
                        'facility_type': facility_type,
                        'marginal_cost_usd_per_tco2': mac_result['marginal_cost_usd_per_tco2'],
                        'emission_reduction_potential_ktco2': total_emission_reduction,
                        'levelized_cost_usd_per_tonne': mac_result['levelized_cost_usd_per_tonne'],
                        'deployment_factor': deployment_factor,
                        'applicable_facilities': total_facilities
                    })

                    print(f"   {tech_name} ({facility_type}): ${mac_result['marginal_cost_usd_per_tco2']:.0f}/tCO₂e, {total_emission_reduction:.0f} ktCO₂e potential")

                except Exception as e:
                    print(f"   Warning: Could not calculate MAC for {tech_name} ({facility_type}): {e}")
                    continue

        # Convert to DataFrame and sort by marginal cost
        macc_df = pd.DataFrame(macc_data)
        if len(macc_df) > 0:
            macc_df = macc_df[macc_df['marginal_cost_usd_per_tco2'] != float('inf')]
            macc_df = macc_df.sort_values('marginal_cost_usd_per_tco2')
            macc_df['cumulative_emission_reduction'] = macc_df['emission_reduction_potential_ktco2'].cumsum()

        return macc_df

    def determine_carbon_price_for_target(self, scenario='moderate', year=2050):
        """Determine endogenous carbon price needed to meet emission target"""

        print(f"\n💰 CARBON PRICE DETERMINATION: {scenario.title()} {year}")
        print("=" * 80)

        # Get emission target
        target_reduction_fraction = self.scenarios[scenario]['targets'].get(year, 0.90)
        target_emissions = self.baseline.corrected_total_emissions * (1 - target_reduction_fraction)
        required_reduction = self.baseline.corrected_total_emissions - target_emissions

        print(f"   Baseline emissions: {self.baseline.corrected_total_emissions:.1f} MtCO₂e")
        print(f"   Target emissions: {target_emissions:.1f} MtCO₂e")
        print(f"   Required reduction: {required_reduction:.1f} MtCO₂e")

        # Get MACC curve
        macc_df = self.calculate_technology_macc_curve(scenario, year)

        if len(macc_df) == 0:
            print("   ❌ No technologies available")
            return None

        # Find carbon price where cumulative reduction meets target
        required_reduction_ktco2 = required_reduction * 1000  # Convert to ktCO2e

        # Find the marginal cost at target reduction
        available_reduction = macc_df['cumulative_emission_reduction'].iloc[-1]

        if available_reduction < required_reduction_ktco2:
            print(f"   ⚠️  Target not achievable with available technologies")
            print(f"   Available reduction: {available_reduction:.0f} ktCO₂e")
            print(f"   Required reduction: {required_reduction_ktco2:.0f} ktCO₂e")
            carbon_price = macc_df['marginal_cost_usd_per_tco2'].iloc[-1]  # Highest cost technology
            achievable_reduction = available_reduction
        else:
            # Find where cumulative reduction exceeds target
            target_row = macc_df[macc_df['cumulative_emission_reduction'] >= required_reduction_ktco2].iloc[0]
            carbon_price = target_row['marginal_cost_usd_per_tco2']
            achievable_reduction = required_reduction_ktco2

        print(f"   💡 Carbon price needed: ${carbon_price:.0f}/tCO₂e")
        print(f"   Achievable reduction: {achievable_reduction/1000:.1f} MtCO₂e")

        return {
            'carbon_price_usd_per_tco2': carbon_price,
            'target_reduction_mtco2': required_reduction,
            'achievable_reduction_mtco2': achievable_reduction / 1000,
            'target_achievable': achievable_reduction >= required_reduction_ktco2,
            'macc_curve': macc_df
        }

    def run_all_scenarios(self):
        """Run analysis for all scenarios and years"""

        print(f"\n\n🚀 RUNNING ALL SCENARIOS WITH CORRECTED NAPHTHA EMISSIONS")
        print("=" * 80)

        results = {}
        years = [2030, 2040, 2050]

        for scenario_name in self.scenarios.keys():
            print(f"\n📊 Scenario: {scenario_name.title()}")
            print(f"   Description: {self.scenarios[scenario_name]['description']}")

            scenario_results = {}

            for year in years:
                print(f"\n   📅 Year {year}:")
                result = self.determine_carbon_price_for_target(scenario_name, year)
                scenario_results[year] = result

                if result:
                    print(f"      Carbon Price: ${result['carbon_price_usd_per_tco2']:.0f}/tCO₂e")
                    print(f"      Target achievable: {'✅ Yes' if result['target_achievable'] else '❌ No'}")
                    print(f"      Reduction achieved: {result['achievable_reduction_mtco2']:.1f} MtCO₂e")

            results[scenario_name] = scenario_results

        return results

    def create_comprehensive_visualization(self, results):
        """Create comprehensive visualization of results"""

        print(f"\n\n📊 CREATING COMPREHENSIVE VISUALIZATION")
        print("=" * 80)

        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))

        # 1. Carbon Price Trajectories
        ax1 = plt.subplot(2, 3, 1)

        years = [2030, 2040, 2050]
        for scenario_name, scenario_results in results.items():
            prices = [scenario_results[year]['carbon_price_usd_per_tco2'] if scenario_results[year] else 0
                     for year in years]
            ax1.plot(years, prices, 'o-', linewidth=2, label=scenario_name.title(), alpha=0.8)

        ax1.set_xlabel('Year')
        ax1.set_ylabel('Carbon Price (USD/tCO₂e)')
        ax1.set_title('Endogenous Carbon Price Trajectories\n(With Corrected Naphtha Emissions)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, None)

        # 2. Emission Reduction Achievements
        ax2 = plt.subplot(2, 3, 2)

        x = np.arange(len(years))
        width = 0.25

        for i, (scenario_name, scenario_results) in enumerate(results.items()):
            reductions = [scenario_results[year]['achievable_reduction_mtco2'] if scenario_results[year] else 0
                         for year in years]
            ax2.bar(x + i*width, reductions, width, label=scenario_name.title(), alpha=0.8)

        ax2.set_xlabel('Year')
        ax2.set_ylabel('Emission Reduction (MtCO₂e/year)')
        ax2.set_title('Achievable Emission Reductions by Scenario')
        ax2.set_xticks(x + width)
        ax2.set_xticklabels(years)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # 3. MACC Curve for 2050 Moderate Scenario
        ax3 = plt.subplot(2, 3, 3)

        if 'moderate' in results and 2050 in results['moderate'] and results['moderate'][2050]:
            macc_df = results['moderate'][2050]['macc_curve']
            if len(macc_df) > 0:
                ax3.step(macc_df['cumulative_emission_reduction']/1000,
                        macc_df['marginal_cost_usd_per_tco2'],
                        where='post', linewidth=2, alpha=0.8)
                ax3.fill_between(macc_df['cumulative_emission_reduction']/1000,
                               macc_df['marginal_cost_usd_per_tco2'],
                               step='post', alpha=0.3)

        ax3.set_xlabel('Cumulative Emission Reduction (MtCO₂e/year)')
        ax3.set_ylabel('Marginal Abatement Cost (USD/tCO₂e)')
        ax3.set_title('MACC Curve: Moderate Scenario 2050')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 1000)

        # 4. Baseline Comparison: Original vs Corrected
        ax4 = plt.subplot(2, 3, 4)

        categories = ['Original\nBaseline', 'Naphtha\nExternal GHG', 'Corrected\nBaseline']
        values = [self.baseline.original_total_emissions,
                 self.baseline.naphtha_emission_increase,
                 self.baseline.corrected_total_emissions]
        colors = ['#FF9999', '#FF6666', '#FF3333']

        bars = ax4.bar(categories, values, color=colors, alpha=0.8)
        ax4.set_ylabel('Emissions (MtCO₂e/year)')
        ax4.set_title('Baseline Emission Correction')

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')

        ax4.grid(True, alpha=0.3, axis='y')

        # 5. Technology Contribution (2050 Moderate)
        ax5 = plt.subplot(2, 3, 5)

        if 'moderate' in results and 2050 in results['moderate'] and results['moderate'][2050]:
            macc_df = results['moderate'][2050]['macc_curve']
            if len(macc_df) > 0:
                # Group by technology
                tech_contribution = macc_df.groupby('technology')['emission_reduction_potential_ktco2'].sum()

                wedges, texts, autotexts = ax5.pie(tech_contribution.values,
                                                  labels=[t.replace('_', ' ') for t in tech_contribution.index],
                                                  autopct='%1.1f%%', startangle=90)
                ax5.set_title('Technology Contribution to Emission Reduction\n(Moderate 2050)')

        # 6. Investment Requirements Comparison
        ax6 = plt.subplot(2, 3, 6)

        # Calculate investment requirements (simplified)
        scenario_names = list(results.keys())
        investment_2050 = []

        for scenario_name in scenario_names:
            if scenario_name in results and 2050 in results[scenario_name] and results[scenario_name][2050]:
                # Estimate investment based on emission reduction and average technology cost
                reduction = results[scenario_name][2050]['achievable_reduction_mtco2']
                # Assume average investment of $500M per MtCO2e reduction capacity
                estimated_investment = reduction * 500  # Million USD
                investment_2050.append(estimated_investment)
            else:
                investment_2050.append(0)

        bars = ax6.bar([s.title() for s in scenario_names], investment_2050,
                      color=['#90EE90', '#FFD700', '#FF6347'], alpha=0.8)
        ax6.set_ylabel('Investment Requirement (Billion USD)')
        ax6.set_title('Estimated Investment Requirements (2050)')

        # Convert to billions and add labels
        for bar, value in zip(bars, investment_2050):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 10,
                    f'${value/1000:.1f}B', ha='center', va='bottom', fontweight='bold')

        ax6.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Korean Petrochemical MACC Analysis with Corrected Naphtha Emissions',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('scenario_macc_analysis_with_naphtha.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("✅ Comprehensive visualization saved: scenario_macc_analysis_with_naphtha.png")

def main():
    """Main analysis function"""

    print("🛢️  SCENARIO-BASED MACC MODEL WITH CORRECTED NAPHTHA EMISSIONS")
    print("=" * 80)
    print("Korean Petrochemical Industry Decarbonization Analysis")
    print("Baseline corrected for naphtha lifecycle emissions")
    print("=" * 80)

    # Initialize and run model
    model = ScenarioMACCModel()

    # Run all scenarios
    results = model.run_all_scenarios()

    # Create visualization
    model.create_comprehensive_visualization(results)

    # Generate summary
    print(f"\n\n📋 ANALYSIS SUMMARY WITH CORRECTED NAPHTHA EMISSIONS")
    print("=" * 80)
    print(f"✅ Baseline corrected: +{model.baseline.naphtha_emission_increase:.1f} MtCO₂e/year from naphtha")
    print(f"✅ New baseline total: {model.baseline.corrected_total_emissions:.1f} MtCO₂e/year")
    print(f"✅ Bio-naphtha technology integrated: ${model.naphtha_integration.bio_naphtha_technology['marginal_abatement_cost']}/tCO₂e")
    print(f"✅ Scenarios analyzed with corrected baseline")
    print(f"✅ Endogenous carbon prices determined")
    print(f"✅ Technology MACC curves generated")

    # Save results
    with open('scenario_results_with_naphtha.json', 'w') as f:
        # Convert results for JSON serialization
        json_results = {}
        for scenario, scenario_data in results.items():
            json_results[scenario] = {}
            for year, year_data in scenario_data.items():
                if year_data:
                    json_results[scenario][year] = {
                        'carbon_price_usd_per_tco2': year_data['carbon_price_usd_per_tco2'],
                        'target_reduction_mtco2': year_data['target_reduction_mtco2'],
                        'achievable_reduction_mtco2': year_data['achievable_reduction_mtco2'],
                        'target_achievable': year_data['target_achievable']
                    }
        json.dump(json_results, f, indent=2)

    print("✅ Results saved: scenario_results_with_naphtha.json")

if __name__ == "__main__":
    main()