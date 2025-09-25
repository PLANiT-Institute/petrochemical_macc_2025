#!/usr/bin/env python3
"""
Internalized Naphtha Emission Model
Calculate proper naphtha emission intensities and integrate into MACC model
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class NaphthaEmissionModel:
    """Model for calculating internalized naphtha emission factors"""

    def __init__(self):
        # Base naphtha consumption data (from baseline analysis)
        self.naphtha_consumption = {
            'total_naphtha_mt_per_year': 32.4,  # Million tonnes/year
            'utilization_breakdown': {
                'ethylene_naphtha': 18.9,      # Mt/year (58.3%)
                'propylene_naphtha': 8.6,      # Mt/year (26.5%)
                'btx_naphtha': 3.4,            # Mt/year (10.5%)
                'other_naphtha': 1.5           # Mt/year (4.6%)
            }
        }

        # External GHG factors (from previous analysis)
        self.external_ghg_breakdown = {
            'extraction_production': {
                'factor_tco2_per_t': 0.45,
                'share_percent': 50.0,
                'description': 'Upstream extraction, processing, refining'
            },
            'indirect_emissions': {
                'factor_tco2_per_t': 0.25,
                'share_percent': 27.8,
                'description': 'Indirect emissions from energy use'
            },
            'methane_leaks': {
                'factor_tco2_per_t': 0.12,
                'share_percent': 13.3,
                'description': 'Upstream methane leakage (GWP100)'
            },
            'transportation': {
                'factor_tco2_per_t': 0.08,
                'share_percent': 8.9,
                'description': 'Transportation via pipeline/tanker'
            }
        }

        # Calculate total external GHG factor
        self.total_external_ghg_factor = sum(
            component['factor_tco2_per_t']
            for component in self.external_ghg_breakdown.values()
        )

        print(f"🛢️  Total External GHG Factor: {self.total_external_ghg_factor:.2f} tCO₂e/t naphtha")

    def calculate_facility_level_emission_intensities(self):
        """Calculate emission intensities by facility type based on naphtha usage"""

        print("\n📊 FACILITY-LEVEL NAPHTHA EMISSION INTENSITIES")
        print("=" * 80)

        # Production capacity by facility type (from baseline)
        facility_production = {
            'ncc_ethylene_mt_per_year': 6.1,    # Ethylene from NCC facilities
            'btx_products_mt_per_year': 4.1,    # BTX aromatic products
            'utility_steam_power_mt_per_year': 15.2  # Steam and power equivalent
        }

        # Naphtha consumption ratios by facility type
        naphtha_consumption_ratios = {
            'ncc_facilities': {
                'ethylene_naphtha_ratio': 3.1,  # t naphtha / t ethylene
                'naphtha_per_facility_mt': 18.9 / 41,  # Total ethylene naphtha / 41 NCC facilities
                'primary_use': 'Feedstock cracking to ethylene'
            },
            'btx_facilities': {
                'btx_naphtha_ratio': 1.4,  # t naphtha / t BTX
                'naphtha_per_facility_mt': 3.4 / 47,  # Total BTX naphtha / 47 BTX facilities
                'primary_use': 'Aromatic compound separation'
            },
            'utility_facilities': {
                'utility_naphtha_ratio': 0.1,  # t naphtha / t steam equivalent (minimal)
                'naphtha_per_facility_mt': 1.5 / 160,  # Remaining naphtha / 160 utility facilities
                'primary_use': 'Backup fuel and heating'
            }
        }

        # Calculate emission intensities by facility type
        facility_emission_intensities = {}

        for facility_type, data in naphtha_consumption_ratios.items():
            # Calculate emissions per facility
            naphtha_per_facility = data['naphtha_per_facility_mt']
            emissions_per_facility = naphtha_per_facility * self.total_external_ghg_factor

            facility_emission_intensities[facility_type] = {
                'naphtha_consumption_mt_per_facility': naphtha_per_facility,
                'naphtha_emission_factor_tco2_per_t': self.total_external_ghg_factor,
                'total_emissions_mtco2_per_facility': emissions_per_facility,
                'naphtha_ratio': data.get('ethylene_naphtha_ratio', data.get('btx_naphtha_ratio', data.get('utility_naphtha_ratio', 0))),
                'primary_use': data['primary_use']
            }

            print(f"\n🏭 {facility_type.replace('_', ' ').title()}:")
            print(f"   Naphtha per facility: {naphtha_per_facility:.3f} Mt/year")
            print(f"   Emissions per facility: {emissions_per_facility:.3f} MtCO₂e/year")
            print(f"   Naphtha ratio: {data.get('ethylene_naphtha_ratio', data.get('btx_naphtha_ratio', data.get('utility_naphtha_ratio', 0))):.1f} t naphtha/t product")
            print(f"   Primary use: {data['primary_use']}")

        return facility_emission_intensities

    def calculate_product_specific_emission_factors(self):
        """Calculate emission factors per tonne of final product"""

        print("\n\n🎯 PRODUCT-SPECIFIC NAPHTHA EMISSION FACTORS")
        print("=" * 80)

        # Production and naphtha consumption by product
        product_data = {
            'ethylene': {
                'production_mt_per_year': 6.1,
                'naphtha_consumption_mt_per_year': 18.9,
                'naphtha_ratio_t_per_t': 3.1
            },
            'propylene': {
                'production_mt_per_year': 3.1,
                'naphtha_consumption_mt_per_year': 8.6,
                'naphtha_ratio_t_per_t': 2.8
            },
            'btx_aromatics': {
                'production_mt_per_year': 4.1,
                'naphtha_consumption_mt_per_year': 3.4,
                'naphtha_ratio_t_per_t': 1.4
            },
            'other_products': {
                'production_mt_per_year': 1.8,
                'naphtha_consumption_mt_per_year': 1.5,
                'naphtha_ratio_t_per_t': 1.8
            }
        }

        # Calculate emission factors per tonne product
        product_emission_factors = {}

        for product, data in product_data.items():
            naphtha_ratio = data['naphtha_ratio_t_per_t']
            emission_factor_per_t_product = naphtha_ratio * self.total_external_ghg_factor

            product_emission_factors[product] = {
                'naphtha_ratio_t_per_t_product': naphtha_ratio,
                'external_ghg_factor_tco2_per_t_naphtha': self.total_external_ghg_factor,
                'emission_factor_tco2_per_t_product': emission_factor_per_t_product,
                'annual_production_mt': data['production_mt_per_year'],
                'annual_naphtha_consumption_mt': data['naphtha_consumption_mt_per_year'],
                'annual_emissions_mtco2': (data['naphtha_consumption_mt_per_year'] * self.total_external_ghg_factor)
            }

            print(f"\n📦 {product.replace('_', ' ').title()}:")
            print(f"   Naphtha ratio: {naphtha_ratio:.1f} t naphtha/t product")
            print(f"   Emission factor: {emission_factor_per_t_product:.2f} tCO₂e/t product")
            print(f"   Annual production: {data['production_mt_per_year']:.1f} Mt/year")
            print(f"   Annual naphtha emissions: {data['naphtha_consumption_mt_per_year'] * self.total_external_ghg_factor:.1f} MtCO₂e/year")

        return product_emission_factors

    def create_macc_integration_framework(self):
        """Create framework for integrating naphtha emissions into MACC model"""

        print("\n\n🔧 MACC MODEL INTEGRATION FRAMEWORK")
        print("=" * 80)

        # Get emission data
        facility_intensities = self.calculate_facility_level_emission_intensities()
        product_factors = self.calculate_product_specific_emission_factors()

        # Integration approach
        integration_framework = {
            'baseline_correction': {
                'approach': 'Add naphtha external GHG as separate emission source',
                'implementation': {
                    'ncc_facilities': {
                        'current_scope1_emissions': 'Direct combustion only',
                        'add_naphtha_scope3': f"{self.total_external_ghg_factor:.2f} tCO₂e per t naphtha feedstock",
                        'calculation_method': 'naphtha_consumption_per_facility * external_ghg_factor',
                        'emission_increase_mtco2_per_facility': facility_intensities['ncc_facilities']['total_emissions_mtco2_per_facility']
                    },
                    'btx_facilities': {
                        'current_scope1_emissions': 'Direct combustion only',
                        'add_naphtha_scope3': f"{self.total_external_ghg_factor:.2f} tCO₂e per t naphtha feedstock",
                        'calculation_method': 'naphtha_consumption_per_facility * external_ghg_factor',
                        'emission_increase_mtco2_per_facility': facility_intensities['btx_facilities']['total_emissions_mtco2_per_facility']
                    },
                    'utility_facilities': {
                        'current_scope1_emissions': 'Direct combustion only',
                        'add_naphtha_scope3': f"{self.total_external_ghg_factor:.2f} tCO₂e per t naphtha feedstock",
                        'calculation_method': 'naphtha_consumption_per_facility * external_ghg_factor',
                        'emission_increase_mtco2_per_facility': facility_intensities['utility_facilities']['total_emissions_mtco2_per_facility']
                    }
                }
            },
            'bio_naphtha_abatement': {
                'approach': 'Model bio-naphtha as emission reduction technology',
                'implementation': {
                    'technology_name': 'Bio-Naphtha Feedstock Substitution',
                    'emission_reduction_factor': 0.85,  # 85% reduction vs conventional naphtha
                    'applicable_facilities': ['NCC', 'BTX', 'Utilities'],
                    'cost_structure': {
                        'capex_usd_per_t_capacity': 300,  # Processing facility costs
                        'feedstock_premium_usd_per_t': 200,  # Bio-naphtha vs conventional
                        'deployment_constraints': {
                            'max_share_2030': 0.10,
                            'max_share_2040': 0.25,
                            'max_share_2050': 0.40
                        }
                    }
                }
            },
            'model_parameters': {
                'baseline_update': {
                    'total_baseline_emissions_increase': sum([
                        product_factors[product]['annual_emissions_mtco2']
                        for product in product_factors.keys()
                    ]),
                    'new_baseline_total': '80.0 MtCO₂e/year (50.8 direct + 29.2 naphtha external)',
                    'emission_accounting': 'Scope 1 + material Scope 3 (naphtha lifecycle)'
                },
                'technology_integration': {
                    'bio_naphtha_technology': {
                        'technology_id': 'BIO_NAPHTHA',
                        'applicable_facility_types': ['NCC', 'BTX', 'UTILITY'],
                        'emission_reduction_potential_mtco2': 29.2 * 0.85,  # 85% of naphtha external emissions
                        'cost_calculation': 'CAPEX + (annual_naphtha_consumption * feedstock_premium)',
                        'learning_curve_rate': 0.15  # 15% cost reduction per doubling
                    }
                }
            }
        }

        print("🔧 Integration Framework Components:")

        # Print baseline correction details
        print(f"\n📋 Baseline Correction:")
        print(f"   Total emission increase: {sum([product_factors[product]['annual_emissions_mtco2'] for product in product_factors.keys()]):.1f} MtCO₂e/year")
        print(f"   External GHG factor: {self.total_external_ghg_factor:.2f} tCO₂e/t naphtha")
        print(f"   New baseline total: ~80.0 MtCO₂e/year")

        # Print bio-naphtha abatement details
        print(f"\n🌱 Bio-Naphtha Technology:")
        print(f"   Emission reduction potential: {29.2 * 0.85:.1f} MtCO₂e/year")
        print(f"   Processing CAPEX: $300/t capacity")
        print(f"   Feedstock premium: $200/t bio-naphtha")
        print(f"   Max deployment 2050: 40% of naphtha")

        return integration_framework

    def calculate_marginal_abatement_costs(self):
        """Calculate marginal abatement costs for bio-naphtha technology"""

        print("\n\n💰 BIO-NAPHTHA MARGINAL ABATEMENT COST CALCULATION")
        print("=" * 80)

        # Technology parameters
        bio_naphtha_params = {
            'capex_usd_per_t_annual_capacity': 300,
            'feedstock_premium_usd_per_t': 200,
            'emission_reduction_factor': 0.85,
            'facility_lifetime_years': 25,
            'discount_rate': 0.08,
            'capacity_factor': 0.90
        }

        # Calculate levelized costs
        # CAPEX component
        capex_annualized = bio_naphtha_params['capex_usd_per_t_annual_capacity'] * (
            bio_naphtha_params['discount_rate'] * (1 + bio_naphtha_params['discount_rate'])**bio_naphtha_params['facility_lifetime_years']
        ) / ((1 + bio_naphtha_params['discount_rate'])**bio_naphtha_params['facility_lifetime_years'] - 1)

        # OPEX component (feedstock premium)
        opex_annual = bio_naphtha_params['feedstock_premium_usd_per_t'] * bio_naphtha_params['capacity_factor']

        # Total annual cost per tonne bio-naphtha
        total_annual_cost_per_t = capex_annualized + opex_annual

        # Emission reduction per tonne bio-naphtha
        emission_reduction_per_t = self.total_external_ghg_factor * bio_naphtha_params['emission_reduction_factor']

        # Marginal abatement cost
        marginal_abatement_cost = total_annual_cost_per_t / emission_reduction_per_t

        print(f"📊 Bio-Naphtha Abatement Cost Analysis:")
        print(f"   CAPEX (annualized): ${capex_annualized:.0f}/t capacity/year")
        print(f"   OPEX (feedstock premium): ${opex_annual:.0f}/t/year")
        print(f"   Total annual cost: ${total_annual_cost_per_t:.0f}/t bio-naphtha")
        print(f"   Emission reduction: {emission_reduction_per_t:.2f} tCO₂e/t bio-naphtha")
        print(f"   Marginal abatement cost: ${marginal_abatement_cost:.0f}/tCO₂e")

        # Compare with scenario carbon prices
        scenario_carbon_prices = {
            'conservative_2030': 150,
            'conservative_2050': 400,
            'moderate_2030': 200,
            'moderate_2050': 500,
            'aggressive_2030': 300,
            'aggressive_2050': 750
        }

        print(f"\n💡 Carbon Price Comparison:")
        for scenario, price in scenario_carbon_prices.items():
            if marginal_abatement_cost <= price:
                status = "✅ Economically viable"
            else:
                status = "❌ Too expensive"
            print(f"   {scenario.replace('_', ' ').title()}: ${price}/tCO₂ → {status}")

        return {
            'marginal_abatement_cost_usd_per_tco2': marginal_abatement_cost,
            'total_annual_cost_usd_per_t': total_annual_cost_per_t,
            'emission_reduction_tco2_per_t': emission_reduction_per_t,
            'capex_annualized': capex_annualized,
            'opex_annual': opex_annual
        }

    def create_implementation_code_template(self):
        """Create code template for integrating naphtha emissions into scenario model"""

        print("\n\n💻 IMPLEMENTATION CODE TEMPLATE")
        print("=" * 80)

        # Get calculation results
        facility_intensities = self.calculate_facility_level_emission_intensities()
        product_factors = self.calculate_product_specific_emission_factors()
        abatement_costs = self.calculate_marginal_abatement_costs()

        code_template = f'''
# Naphtha Emission Integration for Scenario-Based MACC Model

class NaphthaEmissionIntegration:
    """Integrate naphtha lifecycle emissions into MACC model"""

    def __init__(self):
        # Naphtha external GHG factor (tCO2e/t naphtha)
        self.naphtha_external_ghg_factor = {self.total_external_ghg_factor:.2f}

        # Facility-level naphtha consumption (Mt/year per facility)
        self.facility_naphtha_consumption = {{
            'ncc': {facility_intensities['ncc_facilities']['naphtha_consumption_mt_per_facility']:.3f},
            'btx': {facility_intensities['btx_facilities']['naphtha_consumption_mt_per_facility']:.3f},
            'utility': {facility_intensities['utility_facilities']['naphtha_consumption_mt_per_facility']:.3f}
        }}

        # Product-specific emission factors (tCO2e/t product)
        self.product_emission_factors = {{
            'ethylene': {product_factors['ethylene']['emission_factor_tco2_per_t_product']:.2f},
            'propylene': {product_factors['propylene']['emission_factor_tco2_per_t_product']:.2f},
            'btx': {product_factors['btx_aromatics']['emission_factor_tco2_per_t_product']:.2f},
            'other': {product_factors['other_products']['emission_factor_tco2_per_t_product']:.2f}
        }}

        # Bio-naphtha technology parameters
        self.bio_naphtha_technology = {{
            'emission_reduction_factor': 0.85,
            'marginal_abatement_cost': {abatement_costs['marginal_abatement_cost_usd_per_tco2']:.0f},  # USD/tCO2e
            'capex_usd_per_t_capacity': 300,
            'feedstock_premium_usd_per_t': 200,
            'max_deployment_share_2050': 0.40
        }}

    def calculate_baseline_naphtha_emissions(self, facility_data):
        """Calculate baseline naphtha emissions for each facility"""
        baseline_emissions = {{}}

        for facility_id, facility in facility_data.items():
            facility_type = facility['type'].lower()
            if facility_type in self.facility_naphtha_consumption:
                naphtha_consumption = self.facility_naphtha_consumption[facility_type]
                naphtha_emissions = naphtha_consumption * self.naphtha_external_ghg_factor

                baseline_emissions[facility_id] = {{
                    'naphtha_consumption_mt': naphtha_consumption,
                    'naphtha_emissions_mtco2': naphtha_emissions,
                    'original_emissions_mtco2': facility.get('baseline_emissions', 0),
                    'corrected_emissions_mtco2': facility.get('baseline_emissions', 0) + naphtha_emissions
                }}

        return baseline_emissions

    def add_bio_naphtha_technology(self, technology_portfolio):
        """Add bio-naphtha as abatement technology"""

        bio_naphtha_tech = {{
            'technology_id': 'BIO_NAPHTHA',
            'name': 'Bio-Naphtha Feedstock Substitution',
            'applicable_facilities': ['NCC', 'BTX', 'UTILITY'],
            'emission_reduction_factor': self.bio_naphtha_technology['emission_reduction_factor'],
            'capex_usd_per_t_capacity': self.bio_naphtha_technology['capex_usd_per_t_capacity'],
            'opex_usd_per_t_annual': self.bio_naphtha_technology['feedstock_premium_usd_per_t'],
            'marginal_cost_usd_per_tco2': self.bio_naphtha_technology['marginal_abatement_cost'],
            'max_penetration_by_year': {{
                2030: 0.10,
                2040: 0.25,
                2050: 0.40
            }},
            'learning_curve_rate': 0.15
        }}

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

        return {{
            'max_deployment_share': max_share,
            'potential_emission_reduction_mtco2': potential_emission_reduction,
            'marginal_cost_usd_per_tco2': self.bio_naphtha_technology['marginal_abatement_cost']
        }}

# Usage in main scenario model:
# 1. Initialize naphtha integration
naphtha_integration = NaphthaEmissionIntegration()

# 2. Update facility baseline emissions
updated_baseline = naphtha_integration.calculate_baseline_naphtha_emissions(facility_data)

# 3. Add bio-naphtha to technology portfolio
updated_technologies = naphtha_integration.add_bio_naphtha_technology(technology_portfolio)

# 4. Include in optimization for each scenario
bio_naphtha_potential = naphtha_integration.calculate_bio_naphtha_deployment(scenario_targets, year)
'''

        print("💻 Code template generated for scenario model integration")
        print("📋 Key integration points:")
        print(f"   • Baseline emission increase: +{sum([product_factors[product]['annual_emissions_mtco2'] for product in product_factors.keys()]):.1f} MtCO₂e/year")
        print(f"   • Bio-naphtha MAC: ${abatement_costs['marginal_abatement_cost_usd_per_tco2']:.0f}/tCO₂e")
        print(f"   • Max emission reduction: {29.2 * 0.85 * 0.40:.1f} MtCO₂e/year (40% deployment)")

        return code_template

def main():
    """Main analysis function"""

    print("🛢️  INTERNALIZED NAPHTHA EMISSION MODEL")
    print("=" * 80)
    print("Objective: Calculate emission intensities and integrate into MACC model")
    print("=" * 80)

    # Initialize model
    naphtha_model = NaphthaEmissionModel()

    # Run all analyses
    facility_intensities = naphtha_model.calculate_facility_level_emission_intensities()
    product_factors = naphtha_model.calculate_product_specific_emission_factors()
    integration_framework = naphtha_model.create_macc_integration_framework()
    abatement_costs = naphtha_model.calculate_marginal_abatement_costs()
    code_template = naphtha_model.create_implementation_code_template()

    # Summary
    total_naphtha_emissions = sum([product_factors[product]['annual_emissions_mtco2'] for product in product_factors.keys()])

    print(f"\n\n📋 INTERNALIZATION SUMMARY:")
    print("=" * 50)
    print(f"✅ External GHG factor calculated: {naphtha_model.total_external_ghg_factor:.2f} tCO₂e/t naphtha")
    print(f"✅ Total naphtha emissions: {total_naphtha_emissions:.1f} MtCO₂e/year")
    print(f"✅ Baseline correction: +{total_naphtha_emissions:.1f} MtCO₂e/year")
    print(f"✅ Bio-naphtha MAC: ${abatement_costs['marginal_abatement_cost_usd_per_tco2']:.0f}/tCO₂e")
    print(f"✅ Max abatement potential: {29.2 * 0.85 * 0.40:.1f} MtCO₂e/year")
    print("✅ Integration framework created")
    print("✅ Implementation code template generated")

if __name__ == "__main__":
    main()