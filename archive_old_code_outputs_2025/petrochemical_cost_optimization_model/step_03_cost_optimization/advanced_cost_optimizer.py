#!/usr/bin/env python3
"""
STEP 3: ADVANCED COST OPTIMIZATION MODEL
Deep cost optimization with facility-level deployment, temporal dynamics, and timeline analysis
Includes stranded asset analysis, technology pathway optimization, and comprehensive reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.optimize import minimize, differential_evolution
import warnings
warnings.filterwarnings('ignore')

class AdvancedCostOptimizer:
    def __init__(self):
        """Initialize advanced cost optimization model"""
        print("⚖️ STEP 3: ADVANCED COST OPTIMIZATION MODEL")
        print("=" * 70)

        # Load data from previous steps
        self.data_path = "../data_sources/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.load_previous_results()

        # Optimization parameters
        self.discount_rate = 0.08  # 8% corporate discount rate
        self.carbon_price_trajectory = {
            2025: 50, 2030: 120, 2040: 200, 2050: 350  # USD/tCO2
        }

        # Timeline parameters
        self.analysis_years = list(range(2025, 2051))
        self.deployment_phases = {
            'Phase_1_Foundation': (2025, 2030),
            'Phase_2_Acceleration': (2030, 2040),
            'Phase_3_Completion': (2040, 2050)
        }

        # Initialize model components
        self.setup_technology_definitions()
        self.setup_facility_data()
        self.setup_stranded_asset_framework()

    def load_previous_results(self):
        """Load results from baseline and MACC analysis"""
        print("📊 Loading previous analysis results...")

        try:
            # Load facilities data
            self.facilities_df = pd.read_excel(self.data_path, sheet_name='source_Original')
            self.ci_df = pd.read_excel(self.data_path, sheet_name='CI_Corrected', index_col=0)
            self.ci2_df = pd.read_excel(self.data_path, sheet_name='CI2_Corrected', index_col=0)

            print("   ✅ Loaded facility and emission data")
        except Exception as e:
            print(f"   ⚠️ Error loading data: {e}")
            self.create_synthetic_data()

    def create_synthetic_data(self):
        """Create synthetic data for demonstration"""
        # Create sample facility data for demonstration
        np.random.seed(42)
        companies = ['Lotte Chemical', 'LG Chem', 'SK Innovation', 'Hanwha Solutions', 'S-Oil', 'GS Caltex']
        processes = ['Naphtha Cracker', 'BTX Plant', 'Utility']

        facilities_data = []
        for i in range(80):
            facilities_data.append({
                'company': np.random.choice(companies),
                'process': np.random.choice(processes),
                'capacity_1000_t': np.random.randint(200, 2000),
                'year': np.random.randint(1995, 2020),
                'location': np.random.choice(['Ulsan', 'Yeosu', 'Daesan'])
            })

        self.facilities_df = pd.DataFrame(facilities_data)
        print("   ✅ Created synthetic data for demonstration")

    def setup_technology_definitions(self):
        """Define comprehensive technology specifications with temporal dynamics"""
        print("🔧 Setting up advanced technology definitions...")

        self.technologies = {
            'Bio_Naphtha': {
                'name': 'Bio-Naphtha Feedstock',
                'description': 'Replace petroleum naphtha with bio-based feedstock',
                'applicable_processes': ['Naphtha Cracker'],
                'deployment_constraints': {
                    'max_annual_deployment_rate': 0.15,  # 15% per year max
                    'technology_readiness_year': 2026,
                    'supply_chain_limit_2030': 0.3,     # 30% supply availability by 2030
                    'supply_chain_limit_2050': 0.7      # 70% supply availability by 2050
                },
                'costs': {
                    2025: {'capex_usd_per_t': 400, 'opex_usd_per_t_year': 80, 'learning_rate': 0.15},
                    2030: {'capex_usd_per_t': 320, 'opex_usd_per_t_year': 65, 'learning_rate': 0.12},
                    2040: {'capex_usd_per_t': 240, 'opex_usd_per_t_year': 50, 'learning_rate': 0.10},
                    2050: {'capex_usd_per_t': 180, 'opex_usd_per_t_year': 35, 'learning_rate': 0.08}
                },
                'performance': {
                    'energy_efficiency_gain': 0.10,  # 10% energy reduction
                    'emission_reduction': 0.85,      # 85% emission reduction
                    'capacity_factor_impact': 0.98   # 2% capacity loss
                },
                'risk_factors': {
                    'technology_risk': 0.15,         # 15% technology risk premium
                    'supply_risk': 0.20,             # 20% supply chain risk
                    'regulatory_risk': 0.10          # 10% regulatory risk
                }
            },

            'NCC_Hydrogen': {
                'name': 'NCC Hydrogen Integration',
                'description': 'Hydrogen-based heating for naphtha cracking',
                'applicable_processes': ['Naphtha Cracker'],
                'deployment_constraints': {
                    'max_annual_deployment_rate': 0.12,
                    'technology_readiness_year': 2028,
                    'infrastructure_requirement': 'hydrogen_pipeline',
                    'min_facility_scale': 500000  # Minimum 500kt capacity
                },
                'costs': {
                    2025: {'capex_usd_per_t': 1000, 'opex_usd_per_t_year': 150, 'learning_rate': 0.18},
                    2030: {'capex_usd_per_t': 750, 'opex_usd_per_t_year': 120, 'learning_rate': 0.15},
                    2040: {'capex_usd_per_t': 500, 'opex_usd_per_t_year': 85, 'learning_rate': 0.12},
                    2050: {'capex_usd_per_t': 350, 'opex_usd_per_t_year': 60, 'learning_rate': 0.10}
                },
                'performance': {
                    'energy_efficiency_gain': 0.05,
                    'emission_reduction': 0.75,
                    'capacity_factor_impact': 0.95
                },
                'risk_factors': {
                    'technology_risk': 0.25,
                    'supply_risk': 0.30,
                    'regulatory_risk': 0.15
                }
            },

            'NCC_Electricity': {
                'name': 'NCC Electrification',
                'description': 'Electric heating for cracking processes',
                'applicable_processes': ['Naphtha Cracker'],
                'deployment_constraints': {
                    'max_annual_deployment_rate': 0.08,
                    'technology_readiness_year': 2027,
                    'grid_capacity_requirement': True,
                    'temperature_limit': 850  # Celsius, limited high-temp applications
                },
                'costs': {
                    2025: {'capex_usd_per_t': 600, 'opex_usd_per_t_year': 45, 'learning_rate': 0.20},
                    2030: {'capex_usd_per_t': 480, 'opex_usd_per_t_year': 38, 'learning_rate': 0.18},
                    2040: {'capex_usd_per_t': 350, 'opex_usd_per_t_year': 28, 'learning_rate': 0.15},
                    2050: {'capex_usd_per_t': 250, 'opex_usd_per_t_year': 20, 'learning_rate': 0.12}
                },
                'performance': {
                    'energy_efficiency_gain': 0.08,
                    'emission_reduction': 0.65,
                    'capacity_factor_impact': 0.97
                },
                'risk_factors': {
                    'technology_risk': 0.20,
                    'supply_risk': 0.10,
                    'regulatory_risk': 0.05
                }
            },

            'Heat_Pump': {
                'name': 'Industrial Heat Pump',
                'description': 'High-temperature heat pumps for process heating',
                'applicable_processes': ['BTX Plant', 'Utility'],
                'deployment_constraints': {
                    'max_annual_deployment_rate': 0.20,
                    'technology_readiness_year': 2025,
                    'temperature_range': (80, 200),  # Celsius operating range
                    'electricity_infrastructure': True
                },
                'costs': {
                    2025: {'capex_usd_per_t': 200, 'opex_usd_per_t_year': 25, 'learning_rate': 0.12},
                    2030: {'capex_usd_per_t': 170, 'opex_usd_per_t_year': 22, 'learning_rate': 0.10},
                    2040: {'capex_usd_per_t': 140, 'opex_usd_per_t_year': 18, 'learning_rate': 0.08},
                    2050: {'capex_usd_per_t': 120, 'opex_usd_per_t_year': 15, 'learning_rate': 0.06}
                },
                'performance': {
                    'energy_efficiency_gain': 0.15,
                    'emission_reduction': 0.45,
                    'capacity_factor_impact': 0.99
                },
                'risk_factors': {
                    'technology_risk': 0.10,
                    'supply_risk': 0.08,
                    'regulatory_risk': 0.05
                }
            },

            'Renewable_Energy': {
                'name': 'Renewable Energy Integration',
                'description': 'On-site solar and wind power generation',
                'applicable_processes': ['BTX Plant', 'Utility'],
                'deployment_constraints': {
                    'max_annual_deployment_rate': 0.25,
                    'technology_readiness_year': 2025,
                    'land_requirement_per_mw': 2.5,  # Hectares per MW
                    'grid_integration_limit': 0.4    # 40% renewable penetration limit
                },
                'costs': {
                    2025: {'capex_usd_per_t': 250, 'opex_usd_per_t_year': 20, 'learning_rate': 0.10},
                    2030: {'capex_usd_per_t': 200, 'opex_usd_per_t_year': 18, 'learning_rate': 0.08},
                    2040: {'capex_usd_per_t': 150, 'opex_usd_per_t_year': 15, 'learning_rate': 0.06},
                    2050: {'capex_usd_per_t': 120, 'opex_usd_per_t_year': 12, 'learning_rate': 0.05}
                },
                'performance': {
                    'energy_efficiency_gain': 0.02,
                    'emission_reduction': 0.80,
                    'capacity_factor_impact': 1.0
                },
                'risk_factors': {
                    'technology_risk': 0.08,
                    'supply_risk': 0.12,
                    'regulatory_risk': 0.05
                }
            },

            'Early_Retirement': {
                'name': 'Early Facility Retirement',
                'description': 'Strategic early retirement of high-emission facilities',
                'applicable_processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'],
                'deployment_constraints': {
                    'max_annual_retirement_rate': 0.05,  # 5% per year max
                    'min_facility_age': 20,              # Must be at least 20 years old
                    'replacement_capacity_required': 0.8  # 80% replacement needed
                },
                'costs': {
                    2025: {'capex_usd_per_t': 0, 'opex_usd_per_t_year': -30, 'learning_rate': 0},
                    2030: {'capex_usd_per_t': 0, 'opex_usd_per_t_year': -35, 'learning_rate': 0},
                    2040: {'capex_usd_per_t': 0, 'opex_usd_per_t_year': -40, 'learning_rate': 0},
                    2050: {'capex_usd_per_t': 0, 'opex_usd_per_t_year': -45, 'learning_rate': 0}
                },
                'performance': {
                    'energy_efficiency_gain': 0,
                    'emission_reduction': 1.0,
                    'capacity_factor_impact': 0  # Facility closed
                },
                'stranded_asset_impact': {
                    'asset_write_off_rate': 1.0,
                    'employee_impact_per_1000t': 0.8,
                    'supply_chain_impact': 0.15
                }
            }
        }

        print(f"   ✅ Configured {len(self.technologies)} advanced technologies")

    def setup_facility_data(self):
        """Setup facility-level data with enhanced attributes"""
        print("🏭 Processing facility data with optimization attributes...")

        # Clean and process facilities
        self.facilities_df = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_df = self.facilities_df[self.facilities_df['capacity_1000_t'] > 0]

        # Add optimization-relevant attributes
        self.facilities_df['capacity_t'] = self.facilities_df['capacity_1000_t'] * 1000
        self.facilities_df['age_2025'] = 2025 - self.facilities_df['year']
        self.facilities_df['facility_id'] = range(len(self.facilities_df))

        # Calculate facility-level emissions and costs
        baseline_emission_intensity = {
            'Naphtha Cracker': 0.8,  # tCO2/t capacity
            'BTX Plant': 0.5,
            'Utility': 0.3
        }

        baseline_operating_cost = {
            'Naphtha Cracker': 800,  # USD/t capacity/year
            'BTX Plant': 600,
            'Utility': 400
        }

        self.facilities_df['baseline_emissions_tco2_per_year'] = \
            self.facilities_df.apply(lambda x: x['capacity_t'] *
                                   baseline_emission_intensity.get(x['process'], 0.5), axis=1)

        self.facilities_df['baseline_operating_cost_usd_per_year'] = \
            self.facilities_df.apply(lambda x: x['capacity_t'] *
                                   baseline_operating_cost.get(x['process'], 600), axis=1)

        # Asset value estimation
        self.facilities_df['asset_value_usd'] = \
            self.facilities_df['capacity_t'] * 2000  # $2000 per tonne capacity

        # Remaining economic life
        standard_lifetime = 40
        self.facilities_df['remaining_life_years'] = np.maximum(
            0, standard_lifetime - self.facilities_df['age_2025']
        )

        # Technology applicability scoring
        for tech_name in self.technologies.keys():
            tech_spec = self.technologies[tech_name]
            applicable_processes = tech_spec['applicable_processes']

            self.facilities_df[f'{tech_name}_applicable'] = \
                self.facilities_df['process'].isin(applicable_processes)

            # Additional constraints
            constraints = tech_spec.get('deployment_constraints', {})

            if 'min_facility_scale' in constraints:
                self.facilities_df[f'{tech_name}_applicable'] &= \
                    (self.facilities_df['capacity_t'] >= constraints['min_facility_scale'])

            if tech_name == 'Early_Retirement':
                self.facilities_df[f'{tech_name}_applicable'] &= \
                    (self.facilities_df['age_2025'] >= constraints['min_facility_age'])

        print(f"   ✅ Processed {len(self.facilities_df)} facilities with optimization attributes")

    def setup_stranded_asset_framework(self):
        """Setup comprehensive stranded asset analysis framework"""
        print("🏗️ Setting up stranded asset analysis framework...")

        self.stranded_asset_parameters = {
            'discount_rate_stranded': 0.12,  # Higher discount rate for stranded asset analysis
            'asset_depreciation_method': 'straight_line',
            'salvage_value_ratio': 0.1,      # 10% salvage value
            'write_off_triggers': {
                'carbon_price_threshold': 150,  # USD/tCO2
                'regulation_compliance': True,
                'technology_obsolescence': True,
                'economic_unviability': True
            },
            'impact_categories': {
                'financial': ['asset_write_offs', 'lost_revenue', 'cleanup_costs'],
                'operational': ['capacity_loss', 'supply_chain_disruption'],
                'social': ['job_losses', 'community_impact'],
                'environmental': ['emission_reductions', 'avoided_externalities']
            }
        }

        # Calculate baseline stranded asset risk
        current_year = 2025
        for idx, facility in self.facilities_df.iterrows():
            remaining_life = facility['remaining_life_years']
            asset_value = facility['asset_value_usd']

            # Simple stranded asset risk calculation
            if remaining_life <= 10:
                stranded_risk = 0.8  # High risk for old facilities
            elif remaining_life <= 20:
                stranded_risk = 0.4  # Medium risk
            else:
                stranded_risk = 0.1  # Low risk for new facilities

            # Adjust for process type (some processes more at risk)
            if facility['process'] == 'Naphtha Cracker':
                stranded_risk *= 1.5  # Higher risk for carbon-intensive processes

            self.facilities_df.loc[idx, 'stranded_asset_risk'] = stranded_risk
            self.facilities_df.loc[idx, 'potential_stranded_value_usd'] = asset_value * stranded_risk

        print("   ✅ Configured stranded asset analysis framework")

    def calculate_technology_costs_dynamic(self, tech_name, year, cumulative_deployment_mt=0):
        """Calculate dynamic technology costs with learning curves and market effects"""

        tech_spec = self.technologies[tech_name]

        # Get base costs for the year
        year_costs = tech_spec['costs']

        # Find closest year in cost data
        available_years = sorted(year_costs.keys())
        if year <= available_years[0]:
            cost_data = year_costs[available_years[0]]
        elif year >= available_years[-1]:
            cost_data = year_costs[available_years[-1]]
        else:
            # Interpolate between years
            for i in range(len(available_years)-1):
                if available_years[i] <= year <= available_years[i+1]:
                    y1, y2 = available_years[i], available_years[i+1]
                    c1, c2 = year_costs[y1], year_costs[y2]

                    # Linear interpolation
                    weight = (year - y1) / (y2 - y1)
                    cost_data = {
                        'capex_usd_per_t': c1['capex_usd_per_t'] * (1-weight) + c2['capex_usd_per_t'] * weight,
                        'opex_usd_per_t_year': c1['opex_usd_per_t_year'] * (1-weight) + c2['opex_usd_per_t_year'] * weight,
                        'learning_rate': c1['learning_rate'] * (1-weight) + c2['learning_rate'] * weight
                    }
                    break

        # Apply learning curve effects
        learning_rate = cost_data['learning_rate']
        if cumulative_deployment_mt > 0:
            learning_factor = (cumulative_deployment_mt + 1) ** (-learning_rate)
        else:
            learning_factor = 1.0

        # Apply risk premium
        risk_factors = tech_spec.get('risk_factors', {})
        total_risk_premium = sum(risk_factors.values())

        # Calculate final costs
        capex = cost_data['capex_usd_per_t'] * learning_factor * (1 + total_risk_premium * 0.5)
        opex = cost_data['opex_usd_per_t_year'] * learning_factor * (1 + total_risk_premium * 0.3)

        return {
            'capex_usd_per_t': capex,
            'opex_usd_per_t_year': opex,
            'learning_factor': learning_factor,
            'risk_premium': total_risk_premium,
            'total_annual_cost_usd_per_t': capex * 0.1 + opex  # Annualized CAPEX + OPEX
        }

    def optimize_facility_technology_deployment(self):
        """Advanced optimization of technology deployment across facilities and time"""
        print("🎯 Running advanced facility-level technology optimization...")

        optimization_results = []
        deployment_timeline = []
        stranded_asset_analysis = []

        # Optimization for each time period
        for phase_name, (start_year, end_year) in self.deployment_phases.items():
            print(f"   Optimizing {phase_name}: {start_year}-{end_year}")

            phase_results = self.optimize_phase_deployment(
                start_year, end_year, phase_name
            )
            optimization_results.extend(phase_results['deployments'])
            deployment_timeline.extend(phase_results['timeline'])
            stranded_asset_analysis.extend(phase_results['stranded_analysis'])

        # Compile comprehensive results
        deployment_df = pd.DataFrame(optimization_results)
        timeline_df = pd.DataFrame(deployment_timeline)
        stranded_df = pd.DataFrame(stranded_asset_analysis)

        return {
            'facility_deployments': deployment_df,
            'deployment_timeline': timeline_df,
            'stranded_asset_analysis': stranded_df,
            'optimization_summary': self.create_optimization_summary(deployment_df, timeline_df)
        }

    def optimize_phase_deployment(self, start_year, end_year, phase_name):
        """Optimize technology deployment for a specific phase"""

        phase_years = list(range(start_year, end_year + 1))
        deployments = []
        timeline = []
        stranded_analysis = []

        # Cumulative deployment tracking
        cumulative_deployment = {tech: 0 for tech in self.technologies.keys()}

        for year in phase_years:
            print(f"     Optimizing year {year}...")

            # Get carbon price for the year
            carbon_price = self.interpolate_carbon_price(year)

            # Optimize for current year
            year_results = self.optimize_single_year(
                year, carbon_price, cumulative_deployment, phase_name
            )

            deployments.extend(year_results['deployments'])
            timeline.extend(year_results['timeline'])
            stranded_analysis.extend(year_results['stranded'])

            # Update cumulative deployment
            for tech in cumulative_deployment:
                tech_deployments = [d for d in year_results['deployments'] if d['technology'] == tech]
                cumulative_deployment[tech] += sum([d['capacity_deployed_t'] for d in tech_deployments])

        return {
            'deployments': deployments,
            'timeline': timeline,
            'stranded_analysis': stranded_analysis
        }

    def optimize_single_year(self, year, carbon_price, cumulative_deployment, phase_name):
        """Optimize technology deployment for a single year"""

        deployments = []
        timeline = []
        stranded_analysis = []

        # Calculate emission reduction target for the year
        target_reduction = self.calculate_emission_target(year)

        # Evaluate each facility for technology deployment
        for idx, facility in self.facilities_df.iterrows():
            facility_results = self.optimize_facility_deployment(
                facility, year, carbon_price, cumulative_deployment, target_reduction
            )

            if facility_results:
                deployments.extend(facility_results['deployments'])
                timeline.extend(facility_results['timeline'])
                stranded_analysis.extend(facility_results['stranded'])

        return {
            'deployments': deployments,
            'timeline': timeline,
            'stranded': stranded_analysis
        }

    def optimize_facility_deployment(self, facility, year, carbon_price, cumulative_deployment, target_reduction):
        """Optimize technology deployment for a single facility"""

        facility_id = facility['facility_id']
        capacity = facility['capacity_t']
        process_type = facility['process']

        # Find applicable technologies
        applicable_techs = []
        for tech_name in self.technologies.keys():
            if facility[f'{tech_name}_applicable']:
                applicable_techs.append(tech_name)

        if not applicable_techs:
            return None

        # Calculate costs and benefits for each technology
        technology_options = []

        for tech_name in applicable_techs:
            tech_costs = self.calculate_technology_costs_dynamic(
                tech_name, year, cumulative_deployment.get(tech_name, 0) / 1000000  # Convert to Mt
            )

            tech_spec = self.technologies[tech_name]
            performance = tech_spec['performance']

            # Calculate emission reduction
            baseline_emissions = facility['baseline_emissions_tco2_per_year']
            emission_reduction = baseline_emissions * performance['emission_reduction']

            # Calculate economic benefits
            carbon_benefit = emission_reduction * carbon_price
            operating_savings = capacity * tech_costs['opex_usd_per_t_year']
            total_annual_benefit = carbon_benefit - operating_savings

            # Calculate NPV (simplified)
            project_life = min(15, facility['remaining_life_years'])  # Max 15 years or remaining life
            capex = capacity * tech_costs['capex_usd_per_t']

            if project_life > 0:
                npv = -capex + sum([total_annual_benefit / (1 + self.discount_rate)**t
                                  for t in range(1, project_life + 1)])
            else:
                npv = -float('inf')  # Not viable

            technology_options.append({
                'technology': tech_name,
                'capex_usd': capex,
                'annual_benefit_usd': total_annual_benefit,
                'emission_reduction_tco2': emission_reduction,
                'npv_usd': npv,
                'cost_per_tco2_abated': capex / emission_reduction if emission_reduction > 0 else float('inf'),
                'project_life_years': project_life
            })

        # Select best technology (highest NPV)
        if not technology_options:
            return None

        # Filter viable options (positive NPV)
        viable_options = [opt for opt in technology_options if opt['npv_usd'] > 0]

        if not viable_options:
            # Check for early retirement if no viable options
            if facility['age_2025'] >= 20:
                return self.evaluate_early_retirement(facility, year, carbon_price)
            return None

        # Select technology with highest NPV
        best_option = max(viable_options, key=lambda x: x['npv_usd'])

        # Check deployment constraints
        tech_spec = self.technologies[best_option['technology']]
        constraints = tech_spec.get('deployment_constraints', {})

        # Technology readiness
        if year < constraints.get('technology_readiness_year', 2025):
            return None

        # Create deployment record
        deployments = [{
            'facility_id': facility_id,
            'company': facility['company'],
            'location': facility.get('location', 'Unknown'),
            'process': process_type,
            'capacity_t': capacity,
            'technology': best_option['technology'],
            'deployment_year': year,
            'capacity_deployed_t': capacity,  # Full facility deployment
            'capex_usd': best_option['capex_usd'],
            'annual_operating_impact_usd': best_option['annual_benefit_usd'],
            'emission_reduction_tco2_per_year': best_option['emission_reduction_tco2'],
            'npv_usd': best_option['npv_usd'],
            'project_life_years': best_option['project_life_years'],
            'carbon_price_usd_per_tco2': carbon_price
        }]

        # Create timeline record
        timeline = [{
            'year': year,
            'facility_id': facility_id,
            'technology': best_option['technology'],
            'milestone': 'deployment',
            'capacity_affected_t': capacity,
            'investment_usd': best_option['capex_usd'],
            'emission_impact_tco2': best_option['emission_reduction_tco2']
        }]

        # Stranded asset analysis
        stranded = self.analyze_facility_stranded_assets(facility, best_option, year)

        return {
            'deployments': deployments,
            'timeline': timeline,
            'stranded': stranded
        }

    def evaluate_early_retirement(self, facility, year, carbon_price):
        """Evaluate early retirement option for a facility"""

        facility_id = facility['facility_id']
        capacity = facility['capacity_t']

        # Calculate stranded asset cost
        asset_value = facility['asset_value_usd']
        remaining_life = facility['remaining_life_years']

        # Calculate annual depreciation
        annual_depreciation = asset_value / 40  # 40-year standard life
        remaining_book_value = annual_depreciation * remaining_life

        # Calculate ongoing emissions and carbon costs
        annual_emissions = facility['baseline_emissions_tco2_per_year']
        annual_carbon_cost = annual_emissions * carbon_price

        # Calculate ongoing operating losses (if carbon cost > operating margin)
        operating_margin_ratio = 0.15  # Assume 15% operating margin
        annual_revenue = capacity * 1200  # $1200/tonne revenue
        operating_margin = annual_revenue * operating_margin_ratio

        if annual_carbon_cost > operating_margin:
            # Facility is uneconomical - retirement makes sense
            annual_loss_avoided = annual_carbon_cost - operating_margin

            # NPV of avoided losses
            npv_avoided_losses = sum([annual_loss_avoided / (1 + self.discount_rate)**t
                                    for t in range(1, remaining_life + 1)])

            # Net benefit of retirement
            net_retirement_benefit = npv_avoided_losses - remaining_book_value

            if net_retirement_benefit > 0:
                return {
                    'deployments': [{
                        'facility_id': facility_id,
                        'company': facility['company'],
                        'location': facility.get('location', 'Unknown'),
                        'process': facility['process'],
                        'capacity_t': capacity,
                        'technology': 'Early_Retirement',
                        'deployment_year': year,
                        'capacity_deployed_t': capacity,
                        'capex_usd': 0,
                        'annual_operating_impact_usd': -annual_loss_avoided,
                        'emission_reduction_tco2_per_year': annual_emissions,
                        'npv_usd': net_retirement_benefit,
                        'project_life_years': 0,  # Immediate retirement
                        'carbon_price_usd_per_tco2': carbon_price
                    }],
                    'timeline': [{
                        'year': year,
                        'facility_id': facility_id,
                        'technology': 'Early_Retirement',
                        'milestone': 'retirement',
                        'capacity_affected_t': capacity,
                        'investment_usd': 0,
                        'emission_impact_tco2': annual_emissions
                    }],
                    'stranded': [{
                        'facility_id': facility_id,
                        'stranded_asset_value_usd': remaining_book_value,
                        'retirement_year': year,
                        'reason': 'carbon_cost_unviability',
                        'job_impact': capacity * 0.5 / 1000,  # 0.5 jobs per 1000t capacity
                        'community_impact_score': min(10, capacity / 100000)  # Scale 1-10
                    }]
                }

        return None

    def analyze_facility_stranded_assets(self, facility, deployment_option, year):
        """Analyze stranded asset implications of technology deployment"""

        facility_id = facility['facility_id']
        technology = deployment_option['technology']

        stranded_analysis = []

        # If early retirement, full asset stranding
        if technology == 'Early_Retirement':
            stranded_value = facility['asset_value_usd']
            stranding_reason = 'early_retirement'
        else:
            # Partial stranding due to technology transition
            capex_investment = deployment_option['capex_usd']
            existing_asset_value = facility['asset_value_usd']

            # Estimate stranded portion (simplified)
            stranding_ratio = min(0.3, capex_investment / existing_asset_value)  # Max 30% stranding
            stranded_value = existing_asset_value * stranding_ratio
            stranding_reason = 'technology_transition'

        # Calculate impact metrics
        capacity = facility['capacity_t']
        job_impact = capacity * 0.3 / 1000  # Estimated job impact per 1000t capacity

        stranded_analysis.append({
            'facility_id': facility_id,
            'company': facility['company'],
            'stranding_year': year,
            'stranded_asset_value_usd': stranded_value,
            'stranding_reason': stranding_reason,
            'associated_technology': technology,
            'job_impact': job_impact,
            'capacity_impact_t': capacity if technology == 'Early_Retirement' else 0,
            'mitigation_possible': stranding_reason != 'early_retirement',
            'mitigation_cost_usd': stranded_value * 0.2 if stranding_reason != 'early_retirement' else 0
        })

        return stranded_analysis

    def interpolate_carbon_price(self, year):
        """Interpolate carbon price for any year"""
        trajectory = self.carbon_price_trajectory

        years = sorted(trajectory.keys())
        if year <= years[0]:
            return trajectory[years[0]]
        elif year >= years[-1]:
            return trajectory[years[-1]]
        else:
            # Linear interpolation
            for i in range(len(years)-1):
                if years[i] <= year <= years[i+1]:
                    y1, y2 = years[i], years[i+1]
                    p1, p2 = trajectory[y1], trajectory[y2]
                    return p1 + (p2 - p1) * (year - y1) / (y2 - y1)

    def calculate_emission_target(self, year):
        """Calculate emission reduction target for a given year"""
        # Linear interpolation between key targets
        if year <= 2030:
            return 0.25 * (year - 2025) / 5  # 25% by 2030
        elif year <= 2040:
            return 0.25 + 0.25 * (year - 2030) / 10  # 50% by 2040
        else:
            return 0.50 + 0.25 * (year - 2040) / 10  # 75% by 2050

    def create_optimization_summary(self, deployment_df, timeline_df):
        """Create comprehensive optimization summary"""

        if deployment_df.empty:
            return {
                'total_investment_usd': 0,
                'total_emission_reduction_mtco2': 0,
                'facilities_affected': 0,
                'technologies_deployed': 0
            }

        summary = {
            # Financial metrics
            'total_investment_usd': deployment_df['capex_usd'].sum(),
            'total_npv_usd': deployment_df['npv_usd'].sum(),
            'average_cost_per_tco2_abated': (deployment_df['capex_usd'].sum() /
                                           deployment_df['emission_reduction_tco2_per_year'].sum()
                                           if deployment_df['emission_reduction_tco2_per_year'].sum() > 0 else 0),

            # Emission metrics
            'total_emission_reduction_mtco2': deployment_df['emission_reduction_tco2_per_year'].sum() / 1000000,
            'emission_reduction_by_2030': deployment_df[deployment_df['deployment_year'] <= 2030]['emission_reduction_tco2_per_year'].sum() / 1000000,
            'emission_reduction_by_2040': deployment_df[deployment_df['deployment_year'] <= 2040]['emission_reduction_tco2_per_year'].sum() / 1000000,

            # Deployment metrics
            'facilities_affected': deployment_df['facility_id'].nunique(),
            'technologies_deployed': deployment_df['technology'].nunique(),
            'companies_affected': deployment_df['company'].nunique(),

            # Timeline metrics
            'deployment_start_year': deployment_df['deployment_year'].min() if not deployment_df.empty else None,
            'deployment_end_year': deployment_df['deployment_year'].max() if not deployment_df.empty else None,
            'peak_investment_year': deployment_df.groupby('deployment_year')['capex_usd'].sum().idxmax() if not deployment_df.empty else None,

            # Technology breakdown
            'technology_distribution': deployment_df.groupby('technology').agg({
                'capex_usd': 'sum',
                'emission_reduction_tco2_per_year': 'sum',
                'facility_id': 'count'
            }).to_dict('index') if not deployment_df.empty else {}
        }

        return summary

    def export_comprehensive_results(self, optimization_results):
        """Export comprehensive optimization results with timelines"""
        print("💾 Exporting comprehensive cost optimization results...")

        output_file = "advanced_cost_optimization_results.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

            # Executive Summary
            summary = optimization_results['optimization_summary']
            exec_data = [
                ['Analysis Date', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')],
                ['Optimization Period', '2025-2050'],
                ['Total Investment Required', f"${summary['total_investment_usd']/1e9:.1f}B"],
                ['Total NPV', f"${summary['total_npv_usd']/1e9:.1f}B"],
                ['Total Emission Reduction', f"{summary['total_emission_reduction_mtco2']:.1f} MtCO₂/year"],
                ['Facilities Affected', f"{summary['facilities_affected']}"],
                ['Technologies Deployed', f"{summary['technologies_deployed']}"],
                ['Companies Involved', f"{summary['companies_affected']}"],
                ['Average Abatement Cost', f"${summary['average_cost_per_tco2_abated']:.0f}/tCO₂"],
                ['Peak Investment Year', f"{summary.get('peak_investment_year', 'N/A')}"],
                ['Deployment Timeline', f"{summary.get('deployment_start_year', 'N/A')}-{summary.get('deployment_end_year', 'N/A')}"]
            ]
            exec_df = pd.DataFrame(exec_data, columns=['Metric', 'Value'])
            exec_df.to_excel(writer, sheet_name='Executive_Summary', index=False)

            # Facility Deployments
            if not optimization_results['facility_deployments'].empty:
                optimization_results['facility_deployments'].to_excel(
                    writer, sheet_name='Facility_Deployments', index=False)

            # Deployment Timeline
            if not optimization_results['deployment_timeline'].empty:
                optimization_results['deployment_timeline'].to_excel(
                    writer, sheet_name='Deployment_Timeline', index=False)

            # Stranded Asset Analysis
            if not optimization_results['stranded_asset_analysis'].empty:
                optimization_results['stranded_asset_analysis'].to_excel(
                    writer, sheet_name='Stranded_Asset_Analysis', index=False)

            # Technology Summary
            if summary['technology_distribution']:
                tech_summary = pd.DataFrame.from_dict(
                    summary['technology_distribution'], orient='index')
                tech_summary.to_excel(writer, sheet_name='Technology_Summary', index=True)

            # Timeline Analysis
            timeline_analysis = self.create_timeline_analysis(optimization_results)
            timeline_analysis.to_excel(writer, sheet_name='Timeline_Analysis', index=False)

            # Annual Investment Profile
            investment_profile = self.create_investment_profile(optimization_results)
            investment_profile.to_excel(writer, sheet_name='Annual_Investment_Profile', index=False)

        print(f"   ✅ Exported to: {output_file}")
        return output_file

    def create_timeline_analysis(self, optimization_results):
        """Create detailed timeline analysis"""

        deployment_df = optimization_results['facility_deployments']

        if deployment_df.empty:
            return pd.DataFrame()

        # Annual aggregation
        annual_analysis = []

        for year in range(2025, 2051):
            year_deployments = deployment_df[deployment_df['deployment_year'] == year]

            if not year_deployments.empty:
                annual_data = {
                    'year': year,
                    'facilities_deployed': len(year_deployments),
                    'total_investment_billion_usd': year_deployments['capex_usd'].sum() / 1e9,
                    'total_capacity_deployed_mt': year_deployments['capacity_deployed_t'].sum() / 1e6,
                    'total_emission_reduction_mtco2': year_deployments['emission_reduction_tco2_per_year'].sum() / 1e6,
                    'cumulative_investment_billion_usd': deployment_df[deployment_df['deployment_year'] <= year]['capex_usd'].sum() / 1e9,
                    'cumulative_emission_reduction_mtco2': deployment_df[deployment_df['deployment_year'] <= year]['emission_reduction_tco2_per_year'].sum() / 1e6,
                    'carbon_price_usd_per_tco2': self.interpolate_carbon_price(year),
                    'dominant_technology': year_deployments.groupby('technology')['capacity_deployed_t'].sum().idxmax() if len(year_deployments) > 0 else None
                }
            else:
                annual_data = {
                    'year': year,
                    'facilities_deployed': 0,
                    'total_investment_billion_usd': 0,
                    'total_capacity_deployed_mt': 0,
                    'total_emission_reduction_mtco2': 0,
                    'cumulative_investment_billion_usd': deployment_df[deployment_df['deployment_year'] <= year]['capex_usd'].sum() / 1e9 if not deployment_df.empty else 0,
                    'cumulative_emission_reduction_mtco2': deployment_df[deployment_df['deployment_year'] <= year]['emission_reduction_tco2_per_year'].sum() / 1e6 if not deployment_df.empty else 0,
                    'carbon_price_usd_per_tco2': self.interpolate_carbon_price(year),
                    'dominant_technology': None
                }

            annual_analysis.append(annual_data)

        return pd.DataFrame(annual_analysis)

    def create_investment_profile(self, optimization_results):
        """Create detailed investment profile by technology and phase"""

        deployment_df = optimization_results['facility_deployments']

        if deployment_df.empty:
            return pd.DataFrame()

        investment_profile = []

        # By phase
        for phase_name, (start_year, end_year) in self.deployment_phases.items():
            phase_deployments = deployment_df[
                (deployment_df['deployment_year'] >= start_year) &
                (deployment_df['deployment_year'] <= end_year)
            ]

            if not phase_deployments.empty:
                for tech in phase_deployments['technology'].unique():
                    tech_deployments = phase_deployments[phase_deployments['technology'] == tech]

                    profile_data = {
                        'phase': phase_name,
                        'start_year': start_year,
                        'end_year': end_year,
                        'technology': tech,
                        'facilities_count': len(tech_deployments),
                        'total_investment_billion_usd': tech_deployments['capex_usd'].sum() / 1e9,
                        'total_capacity_mt': tech_deployments['capacity_deployed_t'].sum() / 1e6,
                        'total_emission_reduction_mtco2': tech_deployments['emission_reduction_tco2_per_year'].sum() / 1e6,
                        'average_cost_per_tco2_abated': (tech_deployments['capex_usd'].sum() /
                                                       tech_deployments['emission_reduction_tco2_per_year'].sum()
                                                       if tech_deployments['emission_reduction_tco2_per_year'].sum() > 0 else 0),
                        'companies_involved': tech_deployments['company'].nunique()
                    }

                    investment_profile.append(profile_data)

        return pd.DataFrame(investment_profile)

    def create_comprehensive_visualizations(self, optimization_results):
        """Create comprehensive visualizations with timelines"""
        print("📊 Creating comprehensive optimization visualizations...")

        # Create comprehensive figure
        fig, axes = plt.subplots(3, 3, figsize=(24, 18))
        fig.suptitle('STEP 3: Advanced Cost Optimization Results with Timeline Analysis',
                    fontsize=16, fontweight='bold')

        deployment_df = optimization_results['facility_deployments']
        timeline_df = optimization_results['deployment_timeline']
        summary = optimization_results['optimization_summary']

        # 1. Investment timeline
        ax1 = axes[0,0]
        if not deployment_df.empty:
            annual_investment = deployment_df.groupby('deployment_year')['capex_usd'].sum() / 1e9
            ax1.bar(annual_investment.index, annual_investment.values, alpha=0.7, color='steelblue')
            ax1.set_title('Annual Investment Profile')
            ax1.set_xlabel('Year')
            ax1.set_ylabel('Investment (Billion USD)')
            ax1.grid(True, alpha=0.3)

        # 2. Cumulative emission reduction
        ax2 = axes[0,1]
        if not deployment_df.empty:
            timeline_analysis = self.create_timeline_analysis(optimization_results)
            ax2.plot(timeline_analysis['year'], timeline_analysis['cumulative_emission_reduction_mtco2'],
                    'g-', linewidth=3, marker='o', markersize=4)
            ax2.set_title('Cumulative Emission Reduction')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Cumulative Reduction (MtCO₂/year)')
            ax2.grid(True, alpha=0.3)

        # 3. Technology deployment by phase
        ax3 = axes[0,2]
        if not deployment_df.empty:
            tech_counts = deployment_df.groupby('technology')['facility_id'].count()
            ax3.pie(tech_counts.values, labels=tech_counts.index, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Technology Deployment Distribution')

        # 4. Carbon price vs deployment
        ax4 = axes[1,0]
        if not deployment_df.empty:
            years = sorted(deployment_df['deployment_year'].unique())
            carbon_prices = [self.interpolate_carbon_price(year) for year in years]
            deployments_per_year = [len(deployment_df[deployment_df['deployment_year'] == year]) for year in years]

            ax4_twin = ax4.twinx()
            ax4.plot(years, carbon_prices, 'r-', linewidth=2, label='Carbon Price')
            ax4_twin.bar(years, deployments_per_year, alpha=0.3, color='blue', label='Deployments')

            ax4.set_xlabel('Year')
            ax4.set_ylabel('Carbon Price (USD/tCO₂)', color='red')
            ax4_twin.set_ylabel('Facilities Deployed', color='blue')
            ax4.set_title('Carbon Price Impact on Deployment')
            ax4.grid(True, alpha=0.3)

        # 5. Stranded asset analysis
        ax5 = axes[1,1]
        stranded_df = optimization_results['stranded_asset_analysis']
        if not stranded_df.empty:
            stranded_by_reason = stranded_df.groupby('stranding_reason')['stranded_asset_value_usd'].sum() / 1e9
            bars = ax5.bar(range(len(stranded_by_reason)), stranded_by_reason.values,
                          color=['red', 'orange', 'yellow'][:len(stranded_by_reason)])
            ax5.set_title('Stranded Assets by Reason')
            ax5.set_ylabel('Stranded Value (Billion USD)')
            ax5.set_xticks(range(len(stranded_by_reason)))
            ax5.set_xticklabels(stranded_by_reason.index, rotation=45, ha='right')

            # Add value labels
            for bar, value in zip(bars, stranded_by_reason.values):
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'${value:.1f}B', ha='center', va='bottom', fontweight='bold')

        # 6. Company investment distribution
        ax6 = axes[1,2]
        if not deployment_df.empty:
            company_investment = deployment_df.groupby('company')['capex_usd'].sum() / 1e9
            top_companies = company_investment.nlargest(8)

            bars = ax6.barh(range(len(top_companies)), top_companies.values)
            ax6.set_yticks(range(len(top_companies)))
            ax6.set_yticklabels([comp[:15] + '...' if len(comp) > 15 else comp for comp in top_companies.index])
            ax6.set_xlabel('Investment (Billion USD)')
            ax6.set_title('Top Companies: Investment Requirements')

        # 7. Phase-based deployment timeline
        ax7 = axes[2,0]
        if not deployment_df.empty:
            phase_data = {}
            for phase_name, (start_year, end_year) in self.deployment_phases.items():
                phase_deployments = deployment_df[
                    (deployment_df['deployment_year'] >= start_year) &
                    (deployment_df['deployment_year'] <= end_year)
                ]
                phase_data[phase_name] = {
                    'investment': phase_deployments['capex_usd'].sum() / 1e9,
                    'facilities': len(phase_deployments),
                    'emissions': phase_deployments['emission_reduction_tco2_per_year'].sum() / 1e6
                }

            phases = list(phase_data.keys())
            investments = [phase_data[p]['investment'] for p in phases]

            bars = ax7.bar(phases, investments, color=['lightblue', 'lightgreen', 'lightcoral'])
            ax7.set_title('Investment by Deployment Phase')
            ax7.set_ylabel('Investment (Billion USD)')
            ax7.tick_params(axis='x', rotation=45)

        # 8. Cost-effectiveness analysis
        ax8 = axes[2,1]
        if not deployment_df.empty:
            # Calculate cost per tCO2 for each technology
            tech_cost_effectiveness = []
            for tech in deployment_df['technology'].unique():
                tech_data = deployment_df[deployment_df['technology'] == tech]
                total_cost = tech_data['capex_usd'].sum()
                total_reduction = tech_data['emission_reduction_tco2_per_year'].sum()
                if total_reduction > 0:
                    cost_per_tco2 = total_cost / total_reduction
                    tech_cost_effectiveness.append((tech, cost_per_tco2))

            if tech_cost_effectiveness:
                tech_cost_effectiveness.sort(key=lambda x: x[1])
                techs, costs = zip(*tech_cost_effectiveness)

                bars = ax8.barh(range(len(techs)), costs, color='skyblue')
                ax8.set_yticks(range(len(techs)))
                ax8.set_yticklabels(techs)
                ax8.set_xlabel('Cost per tCO₂ Abated (USD)')
                ax8.set_title('Technology Cost-Effectiveness')

        # 9. Deployment success metrics
        ax9 = axes[2,2]
        success_metrics = {
            'Facilities\nDeployed': summary['facilities_affected'],
            'Technologies\nUsed': summary['technologies_deployed'],
            'Companies\nInvolved': summary['companies_affected'],
            'Emission Reduction\n(MtCO₂)': summary['total_emission_reduction_mtco2']
        }

        bars = ax9.bar(range(len(success_metrics)), list(success_metrics.values()),
                      color=['gold', 'lightgreen', 'lightblue', 'lightcoral'])
        ax9.set_xticks(range(len(success_metrics)))
        ax9.set_xticklabels(success_metrics.keys())
        ax9.set_title('Optimization Success Metrics')
        ax9.tick_params(axis='x', rotation=45)

        # Add value labels
        for i, (metric, value) in enumerate(success_metrics.items()):
            ax9.text(i, value + value*0.01, f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        # Save visualization
        viz_file = "advanced_cost_optimization_visualization.png"
        plt.savefig(viz_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   ✅ Saved: {viz_file}")

        return viz_file

    def run_complete_optimization(self):
        """Run complete advanced cost optimization analysis"""
        print("\n🚀 RUNNING COMPLETE ADVANCED COST OPTIMIZATION")
        print("=" * 80)

        try:
            # Run optimization
            optimization_results = self.optimize_facility_technology_deployment()

            # Export results
            excel_file = self.export_comprehensive_results(optimization_results)

            # Create visualizations
            viz_file = self.create_comprehensive_visualizations(optimization_results)

            # Print summary
            summary = optimization_results['optimization_summary']

            print(f"\n✅ ADVANCED COST OPTIMIZATION COMPLETE!")
            print("=" * 60)
            print(f"📊 Excel Report: {excel_file}")
            print(f"📈 Visualization: {viz_file}")
            print(f"💰 Total Investment: ${summary['total_investment_usd']/1e9:.1f}B")
            print(f"📉 Emission Reduction: {summary['total_emission_reduction_mtco2']:.1f} MtCO₂/year")
            print(f"🏭 Facilities Affected: {summary['facilities_affected']}")
            print(f"🔧 Technologies Deployed: {summary['technologies_deployed']}")
            print(f"🏢 Companies Involved: {summary['companies_affected']}")
            print(f"💵 Average Abatement Cost: ${summary['average_cost_per_tco2_abated']:.0f}/tCO₂")

            return optimization_results

        except Exception as e:
            print(f"❌ Optimization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

def main():
    """Main execution function"""
    optimizer = AdvancedCostOptimizer()
    results = optimizer.run_complete_optimization()

if __name__ == "__main__":
    main()