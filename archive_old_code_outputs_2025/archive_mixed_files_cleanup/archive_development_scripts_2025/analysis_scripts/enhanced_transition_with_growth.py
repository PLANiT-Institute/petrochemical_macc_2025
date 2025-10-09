#!/usr/bin/env python3
"""
Enhanced Transition Logic with Capacity Growth Scenarios
Integrates energy-intensity methodology with capacity growth projections
for Korean Petrochemical Industry MACC Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedTransitionWithGrowth:
    def __init__(self, data_path="../data/Korean_Petrochemical_MACC_Model_English.xlsx"):
        """Initialize Enhanced Transition Model with Growth Scenarios"""
        self.data_path = data_path
        self.output_dir = Path("../outputs/enhanced_transition_analysis")
        self.output_dir.mkdir(exist_ok=True)

        # Base parameters
        self.base_year = 2025
        self.projection_years = [2030, 2035, 2040, 2045, 2050]

        # Load baseline data
        self.source_df = None
        self.ci_df = None
        self.merged_df = None

        print("🚀 ENHANCED PETROCHEMICAL TRANSITION MODEL")
        print("=" * 80)
        print("🎯 Features: Energy-intensity methodology + Capacity growth scenarios")
        print()

    def load_baseline_data(self):
        """Load baseline data consistent with baseline analysis"""
        print("📁 Loading baseline data...")

        self.source_df = pd.read_excel(self.data_path, sheet_name='source_Original')
        self.ci_df = pd.read_excel(self.data_path, sheet_name='CI_Corrected')

        # Merge for energy intensities
        self.merged_df = self.source_df.merge(
            self.ci_df,
            left_on=['products', 'process'],
            right_on=['Product', 'Process'],
            how='left'
        )

        print(f"✅ Facilities: {len(self.merged_df)} records")
        print(f"✅ Companies: {self.merged_df['company'].nunique()} companies")
        print(f"✅ Processes: {self.merged_df['process'].nunique()} process types")

        return self

    def define_capacity_growth_scenarios(self):
        """Define comprehensive capacity growth scenarios"""
        print("\n📈 Defining capacity growth scenarios...")

        # Overall industry scenarios
        self.capacity_scenarios = {
            'Conservative_Growth': {
                'description': 'Slow growth due to environmental constraints and market maturity',
                'overall_rate': 0.005,  # 0.5% annual
                'process_multipliers': {
                    'Naphtha Cracker': 0.0,    # No new crackers
                    'BTX Plant': 1.0,          # Normal growth
                    'Utility': 1.5            # Higher utility growth
                },
                'regional_multipliers': {
                    'Ulsan': 0.8,    # Mature region
                    'Yeosu': 1.0,    # Balanced growth
                    'Daesan': 1.2    # Higher growth potential
                },
                'drivers': ['Environmental regulations', 'Market saturation', 'Energy transition pressure']
            },

            'Moderate_Growth': {
                'description': 'Balanced growth with green technology integration',
                'overall_rate': 0.015,  # 1.5% annual
                'process_multipliers': {
                    'Naphtha Cracker': 0.5,   # Limited expansion
                    'BTX Plant': 1.2,         # Above average
                    'Utility': 1.3
                },
                'regional_multipliers': {
                    'Ulsan': 0.9,
                    'Yeosu': 1.0,
                    'Daesan': 1.1
                },
                'drivers': ['Steady chemical demand', 'Green product premium', 'Export competitiveness']
            },

            'High_Growth': {
                'description': 'Aggressive expansion driven by green chemicals demand',
                'overall_rate': 0.025,  # 2.5% annual
                'process_multipliers': {
                    'Naphtha Cracker': 0.8,   # Some expansion with green tech
                    'BTX Plant': 1.5,         # Strong aromatics demand
                    'Utility': 1.4
                },
                'regional_multipliers': {
                    'Ulsan': 1.0,
                    'Yeosu': 1.1,
                    'Daesan': 1.3    # Major expansion
                },
                'drivers': ['Strong export demand', 'Green chemical premiums', 'Government incentives']
            },

            'Industry_Decline': {
                'description': 'Contraction due to global competition and regulation',
                'overall_rate': -0.010,  # -1% annual
                'process_multipliers': {
                    'Naphtha Cracker': 1.0,   # Natural decline
                    'BTX Plant': 0.8,         # Faster decline
                    'Utility': 0.9
                },
                'regional_multipliers': {
                    'Ulsan': 1.2,    # Less decline (integrated)
                    'Yeosu': 1.0,
                    'Daesan': 0.8    # More decline
                },
                'drivers': ['Import competition', 'Strict carbon regulations', 'High energy costs']
            }
        }

        print(f"✅ Defined {len(self.capacity_scenarios)} growth scenarios")
        for scenario, data in self.capacity_scenarios.items():
            print(f"   {scenario}: {data['overall_rate']*100:+.1f}% annual - {data['description']}")

        return self

    def calculate_capacity_projections(self):
        """Calculate capacity projections for each scenario and year"""
        print("\n⚙️ Calculating capacity projections...")

        self.capacity_projections = {}

        for scenario_name, scenario_data in self.capacity_scenarios.items():
            scenario_projections = {}

            for year in self.projection_years:
                years_elapsed = year - self.base_year

                # Calculate facility-level projections
                facility_projections = self.merged_df.copy()

                for idx, facility in facility_projections.iterrows():
                    process = facility['process']
                    location = facility['location']
                    base_capacity = facility['capacity_1000_t']

                    # Apply scenario-specific growth
                    overall_growth = scenario_data['overall_rate']
                    process_multiplier = scenario_data['process_multipliers'].get(process, 1.0)
                    regional_multiplier = scenario_data['regional_multipliers'].get(location, 1.0)

                    # Combined growth rate
                    effective_rate = overall_growth * process_multiplier * regional_multiplier

                    # Calculate new capacity
                    growth_factor = (1 + effective_rate) ** years_elapsed
                    new_capacity = base_capacity * growth_factor

                    facility_projections.loc[idx, 'capacity_1000_t'] = new_capacity
                    facility_projections.loc[idx, 'capacity_growth_factor'] = growth_factor

                scenario_projections[year] = facility_projections

            self.capacity_projections[scenario_name] = scenario_projections

            # Print scenario summary
            total_base_capacity = self.merged_df['capacity_1000_t'].sum()
            total_2050_capacity = scenario_projections[2050]['capacity_1000_t'].sum()
            growth_factor_2050 = total_2050_capacity / total_base_capacity

            print(f"   {scenario_name}:")
            print(f"     2025 capacity: {total_base_capacity:,.0f} kt/year")
            print(f"     2050 capacity: {total_2050_capacity:,.0f} kt/year")
            print(f"     Total growth factor: {growth_factor_2050:.2f}x")

        return self

    def calculate_energy_intensive_transitions(self):
        """Calculate transitions using energy-intensity methodology"""
        print("\n⚡ Calculating energy-intensive transitions...")

        # Energy source parameters (consistent with baseline analysis)
        self.energy_sources = {
            'Naphtha_Feedstock': {'intensity_col': 'Naphtha_Feedstock_GJ_per_t', 'ef': 70.5, 'price_gj': 18.0},
            'Naphtha_Thermal': {'intensity_col': 'Naphtha_Thermal_GJ_per_t', 'ef': 70.5, 'price_gj': 18.0},
            'LNG': {'intensity_col': 'LNG_GJ_per_t', 'ef': 56.1, 'price_gj': 12.0},
            'LPG_Propane': {'intensity_col': 'LPG_Propane_GJ_per_t', 'ef': 63.1, 'price_gj': 15.0},
            'LPG_Butane': {'intensity_col': 'LPG_Butane_GJ_per_t', 'ef': 64.2, 'price_gj': 15.0},
            'Fuel_Gas_Mix': {'intensity_col': 'Fuel_Gas_Mix_GJ_per_t', 'ef': 60.0, 'price_gj': 10.0},
            'Electricity': {'intensity_col': 'Electricity_kWh_per_t', 'ef': 466.0, 'price_kwh': 0.12}
        }

        # Future energy sources (post-transition)
        self.future_energy_sources = {
            'Green_Hydrogen': {'ef': 0.0, 'price_gj': 35.0, 'price_kwh': None},     # Green hydrogen
            'Blue_Hydrogen': {'ef': 15.0, 'price_gj': 25.0, 'price_kwh': None},     # Blue hydrogen (with CCUS)
            'Bio_Naphtha': {'ef': 20.0, 'price_gj': 25.0, 'price_kwh': None},       # Bio-based naphtha
            'Renewable_Electricity': {'ef': 50.0, 'price_gj': None, 'price_kwh': 0.08},  # Renewable grid
            'Electrification': {'ef': 50.0, 'price_gj': None, 'price_kwh': 0.10}    # Direct electrification
        }

        # Technology transition pathways by process
        self.transition_pathways = {
            'Naphtha Cracker': {
                'energy_substitutions': {
                    'Naphtha_Feedstock': [
                        {'technology': 'Bio_Naphtha', 'substitution_rate': 0.30, 'capex_per_kt': 500},
                        {'technology': 'Green_Hydrogen', 'substitution_rate': 0.50, 'capex_per_kt': 800}
                    ],
                    'Naphtha_Thermal': [
                        {'technology': 'Green_Hydrogen', 'substitution_rate': 0.70, 'capex_per_kt': 600},
                        {'technology': 'Renewable_Electricity', 'substitution_rate': 0.25, 'capex_per_kt': 400}
                    ]
                }
            },
            'BTX Plant': {
                'energy_substitutions': {
                    'LNG': [
                        {'technology': 'Green_Hydrogen', 'substitution_rate': 0.60, 'capex_per_kt': 700}
                    ],
                    'Electricity': [
                        {'technology': 'Renewable_Electricity', 'substitution_rate': 0.90, 'capex_per_kt': 200}
                    ]
                }
            },
            'Utility': {
                'energy_substitutions': {
                    'LNG': [
                        {'technology': 'Green_Hydrogen', 'substitution_rate': 0.40, 'capex_per_kt': 300},
                        {'technology': 'Electrification', 'substitution_rate': 0.45, 'capex_per_kt': 250}
                    ],
                    'Electricity': [
                        {'technology': 'Renewable_Electricity', 'substitution_rate': 0.95, 'capex_per_kt': 100}
                    ]
                }
            }
        }

        print("✅ Energy transition pathways defined")
        return self

    def calculate_scenario_transitions(self):
        """Calculate transitions for each capacity growth scenario"""
        print("\n🔄 Calculating transitions for all scenarios...")

        self.transition_results = {}

        for scenario_name in self.capacity_scenarios.keys():
            print(f"\n   Processing {scenario_name}...")

            scenario_results = {}

            for year in self.projection_years:
                year_facilities = self.capacity_projections[scenario_name][year].copy()

                # Calculate baseline emissions with grown capacity
                baseline_emissions = {}
                baseline_costs = {}

                for idx, facility in year_facilities.iterrows():
                    capacity_t = facility['capacity_1000_t'] * 1000
                    process = facility['process']

                    facility_emissions = 0
                    facility_costs = 0

                    # Calculate current energy use and emissions
                    for energy_source, config in self.energy_sources.items():
                        intensity_col = config['intensity_col']
                        ef = config['ef']

                        if intensity_col in facility.index and not pd.isna(facility[intensity_col]):
                            if energy_source == 'Electricity':
                                energy_consumption = facility[intensity_col] * capacity_t  # kWh
                                emissions = energy_consumption * ef / 1000  # Convert to tCO2
                                costs = energy_consumption * config['price_kwh']
                            else:
                                energy_consumption = facility[intensity_col] * capacity_t  # GJ
                                emissions = energy_consumption * ef / 1000  # Convert to tCO2
                                costs = energy_consumption * config['price_gj']

                            facility_emissions += emissions
                            facility_costs += costs

                    baseline_emissions[idx] = facility_emissions
                    baseline_costs[idx] = facility_costs

                # Calculate post-transition emissions and costs
                transition_emissions = {}
                transition_costs = {}
                capex_costs = {}

                for idx, facility in year_facilities.iterrows():
                    capacity_t = facility['capacity_1000_t'] * 1000
                    process = facility['process']

                    new_emissions = 0
                    new_opex = 0
                    total_capex = 0

                    if process in self.transition_pathways:
                        pathway = self.transition_pathways[process]

                        for energy_source, substitutions in pathway['energy_substitutions'].items():
                            # Get original energy consumption
                            intensity_col = self.energy_sources[energy_source]['intensity_col']

                            if intensity_col in facility.index and not pd.isna(facility[intensity_col]):
                                if energy_source == 'Electricity':
                                    original_energy = facility[intensity_col] * capacity_t  # kWh
                                else:
                                    original_energy = facility[intensity_col] * capacity_t  # GJ

                                # Apply substitutions
                                for substitution in substitutions:
                                    technology = substitution['technology']
                                    rate = substitution['substitution_rate']
                                    capex_per_kt = substitution['capex_per_kt']

                                    substituted_energy = original_energy * rate

                                    # Calculate new emissions and costs
                                    if technology in self.future_energy_sources:
                                        future_source = self.future_energy_sources[technology]

                                        if 'kwh' in technology.lower() or technology == 'Renewable_Electricity' or technology == 'Electrification':
                                            emissions = substituted_energy * future_source['ef'] / 1000
                                            if future_source['price_kwh'] is not None:
                                                opex = substituted_energy * future_source['price_kwh']
                                            else:
                                                opex = 0
                                        else:
                                            emissions = substituted_energy * future_source['ef'] / 1000
                                            if future_source['price_gj'] is not None:
                                                opex = substituted_energy * future_source['price_gj']
                                            else:
                                                opex = 0

                                        new_emissions += emissions
                                        new_opex += opex
                                        total_capex += (capacity_t / 1000) * capex_per_kt

                    transition_emissions[idx] = new_emissions
                    transition_costs[idx] = new_opex
                    capex_costs[idx] = total_capex

                # Calculate abatement and costs
                total_baseline_emissions = sum(baseline_emissions.values())
                total_transition_emissions = sum(transition_emissions.values())
                total_abatement = total_baseline_emissions - total_transition_emissions

                total_baseline_opex = sum(baseline_costs.values())
                total_transition_opex = sum(transition_costs.values())
                opex_delta = total_transition_opex - total_baseline_opex

                total_capex = sum(capex_costs.values())

                # Store year results
                scenario_results[year] = {
                    'total_capacity_kt': year_facilities['capacity_1000_t'].sum(),
                    'baseline_emissions_Mt': total_baseline_emissions / 1e6,
                    'transition_emissions_Mt': total_transition_emissions / 1e6,
                    'abatement_Mt': total_abatement / 1e6,
                    'abatement_rate': total_abatement / total_baseline_emissions if total_baseline_emissions > 0 else 0,
                    'baseline_opex_M_USD': total_baseline_opex / 1e6,
                    'transition_opex_M_USD': total_transition_opex / 1e6,
                    'opex_delta_M_USD': opex_delta / 1e6,
                    'capex_M_USD': total_capex / 1e6,
                    'abatement_cost_USD_per_tCO2': (opex_delta + total_capex * 0.1) / total_abatement if total_abatement > 0 else 0  # Assume 10% capital recovery
                }

            self.transition_results[scenario_name] = scenario_results

            # Print scenario summary
            results_2050 = scenario_results[2050]
            print(f"     2050 Results:")
            print(f"       Capacity: {results_2050['total_capacity_kt']:,.0f} kt/year")
            print(f"       Baseline emissions: {results_2050['baseline_emissions_Mt']:.1f} Mt/year")
            print(f"       Abatement: {results_2050['abatement_Mt']:.1f} Mt/year ({results_2050['abatement_rate']*100:.1f}%)")
            print(f"       Abatement cost: ${results_2050['abatement_cost_USD_per_tCO2']:.0f}/tCO2")

        return self

    def create_growth_scenario_visualization(self):
        """Create comprehensive visualization of growth scenarios"""
        print("\n📊 Creating growth scenario visualizations...")

        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('Korean Petrochemical Industry: Capacity Growth & Transition Scenarios',
                     fontsize=18, fontweight='bold', y=0.98)

        # Color scheme for scenarios
        scenario_colors = {
            'Conservative_Growth': '#1f77b4',
            'Moderate_Growth': '#2ca02c',
            'High_Growth': '#ff7f0e',
            'Industry_Decline': '#d62728'
        }

        # 1. Capacity Growth Trajectories
        ax1 = plt.subplot(2, 3, 1)
        for scenario in self.capacity_scenarios.keys():
            capacities = [self.transition_results[scenario][year]['total_capacity_kt']
                         for year in self.projection_years]
            ax1.plot(self.projection_years, capacities,
                    marker='o', linewidth=2.5, markersize=6,
                    color=scenario_colors[scenario],
                    label=scenario.replace('_', ' '))

        ax1.set_title('Total Industry Capacity Growth', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Capacity (kt/year)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Baseline Emissions Growth
        ax2 = plt.subplot(2, 3, 2)
        for scenario in self.capacity_scenarios.keys():
            emissions = [self.transition_results[scenario][year]['baseline_emissions_Mt']
                        for year in self.projection_years]
            ax2.plot(self.projection_years, emissions,
                    marker='o', linewidth=2.5, markersize=6,
                    color=scenario_colors[scenario],
                    label=scenario.replace('_', ' '))

        ax2.set_title('Baseline Emissions Growth', fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Emissions (MtCO₂e/year)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Total Abatement Potential
        ax3 = plt.subplot(2, 3, 3)
        for scenario in self.capacity_scenarios.keys():
            abatement = [self.transition_results[scenario][year]['abatement_Mt']
                        for year in self.projection_years]
            ax3.plot(self.projection_years, abatement,
                    marker='o', linewidth=2.5, markersize=6,
                    color=scenario_colors[scenario],
                    label=scenario.replace('_', ' '))

        ax3.set_title('Total Abatement Potential', fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Abatement (MtCO₂e/year)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Abatement Cost Evolution
        ax4 = plt.subplot(2, 3, 4)
        for scenario in self.capacity_scenarios.keys():
            costs = [self.transition_results[scenario][year]['abatement_cost_USD_per_tCO2']
                    for year in self.projection_years]
            ax4.plot(self.projection_years, costs,
                    marker='o', linewidth=2.5, markersize=6,
                    color=scenario_colors[scenario],
                    label=scenario.replace('_', ' '))

        ax4.set_title('Abatement Cost Evolution', fontweight='bold')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Cost ($/tCO₂e)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # 5. Investment Requirements (2050)
        ax5 = plt.subplot(2, 3, 5)
        scenarios = list(self.capacity_scenarios.keys())
        capex_2050 = [self.transition_results[scenario][2050]['capex_M_USD'] for scenario in scenarios]

        bars = ax5.bar(range(len(scenarios)), capex_2050,
                      color=[scenario_colors[s] for s in scenarios])
        ax5.set_title('Capital Investment Requirements (2050)', fontweight='bold')
        ax5.set_ylabel('Investment (Million USD)')
        ax5.set_xticks(range(len(scenarios)))
        ax5.set_xticklabels([s.replace('_', ' ') for s in scenarios], rotation=45)

        # Add value labels
        for bar, value in zip(bars, capex_2050):
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(capex_2050)*0.01,
                    f'${value:,.0f}M', ha='center', va='bottom', fontweight='bold')

        # 6. Cumulative Impact Comparison (2050)
        ax6 = plt.subplot(2, 3, 6)
        capacity_2050 = [self.transition_results[scenario][2050]['total_capacity_kt']/1000 for scenario in scenarios]
        abatement_2050 = [self.transition_results[scenario][2050]['abatement_Mt'] for scenario in scenarios]

        scatter = ax6.scatter(capacity_2050, abatement_2050,
                             s=[c*20 for c in capex_2050],
                             c=[scenario_colors[s] for s in scenarios],
                             alpha=0.7)

        ax6.set_title('Capacity vs Abatement (2050)', fontweight='bold')
        ax6.set_xlabel('Total Capacity (Mt/year)')
        ax6.set_ylabel('Abatement Potential (MtCO₂e/year)')

        # Add scenario labels
        for i, scenario in enumerate(scenarios):
            ax6.annotate(scenario.replace('_', ' '),
                        (capacity_2050[i], abatement_2050[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)

        ax6.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save visualization
        viz_path = self.output_dir / "capacity_growth_scenarios.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"✅ Growth scenario visualization saved: {viz_path}")
        return viz_path

    def save_scenario_reports(self):
        """Save detailed scenario analysis reports"""
        print("\n📋 Saving scenario reports...")

        # Create comprehensive results DataFrame
        results_data = []

        for scenario_name, scenario_results in self.transition_results.items():
            for year, results in scenario_results.items():
                results_data.append({
                    'Scenario': scenario_name,
                    'Year': year,
                    'Total_Capacity_kt': results['total_capacity_kt'],
                    'Baseline_Emissions_Mt': results['baseline_emissions_Mt'],
                    'Transition_Emissions_Mt': results['transition_emissions_Mt'],
                    'Abatement_Mt': results['abatement_Mt'],
                    'Abatement_Rate_Percent': results['abatement_rate'] * 100,
                    'Baseline_OPEX_M_USD': results['baseline_opex_M_USD'],
                    'Transition_OPEX_M_USD': results['transition_opex_M_USD'],
                    'OPEX_Delta_M_USD': results['opex_delta_M_USD'],
                    'CAPEX_M_USD': results['capex_M_USD'],
                    'Abatement_Cost_USD_per_tCO2': results['abatement_cost_USD_per_tCO2']
                })

        results_df = pd.DataFrame(results_data)

        # Save main results
        results_path = self.output_dir / "capacity_growth_scenario_results.csv"
        results_df.to_csv(results_path, index=False)

        # Save scenario definitions
        scenario_def_path = self.output_dir / "scenario_definitions.csv"
        scenario_def_data = []

        for scenario_name, scenario_data in self.capacity_scenarios.items():
            scenario_def_data.append({
                'Scenario': scenario_name,
                'Description': scenario_data['description'],
                'Overall_Growth_Rate': scenario_data['overall_rate'],
                'Key_Drivers': '; '.join(scenario_data['drivers'])
            })

        pd.DataFrame(scenario_def_data).to_csv(scenario_def_path, index=False)

        print(f"✅ Reports saved:")
        print(f"   Main results: {results_path}")
        print(f"   Scenario definitions: {scenario_def_path}")

        return {'results': results_path, 'definitions': scenario_def_path}

    def print_scenario_summary(self):
        """Print executive summary of scenario analysis"""
        print(f"\n{'='*80}")
        print("🎯 CAPACITY GROWTH SCENARIO ANALYSIS SUMMARY")
        print(f"{'='*80}")

        print(f"\n📊 SCENARIO OVERVIEW:")
        for scenario_name, scenario_data in self.capacity_scenarios.items():
            print(f"   {scenario_name}: {scenario_data['overall_rate']*100:+.1f}% annual growth")
            print(f"     {scenario_data['description']}")

        print(f"\n📈 2050 PROJECTIONS COMPARISON:")
        base_capacity = self.merged_df['capacity_1000_t'].sum()

        for scenario_name in self.capacity_scenarios.keys():
            results_2050 = self.transition_results[scenario_name][2050]
            capacity_growth = (results_2050['total_capacity_kt'] / base_capacity) - 1

            print(f"   {scenario_name}:")
            print(f"     Capacity growth: {capacity_growth*100:+.1f}% ({results_2050['total_capacity_kt']:,.0f} kt)")
            print(f"     Baseline emissions: {results_2050['baseline_emissions_Mt']:.1f} MtCO₂e/year")
            print(f"     Abatement potential: {results_2050['abatement_Mt']:.1f} MtCO₂e/year")
            print(f"     Investment required: ${results_2050['capex_M_USD']:,.0f} million")
            print(f"     Abatement cost: ${results_2050['abatement_cost_USD_per_tCO2']:.0f}/tCO₂e")

        print(f"\n🎯 KEY INSIGHTS:")

        # Find best and worst scenarios
        scenarios_2050 = {name: self.transition_results[name][2050] for name in self.capacity_scenarios.keys()}
        best_abatement = max(scenarios_2050, key=lambda x: scenarios_2050[x]['abatement_Mt'])
        lowest_cost = min(scenarios_2050, key=lambda x: scenarios_2050[x]['abatement_cost_USD_per_tCO2'])

        print(f"   • {best_abatement} offers highest abatement potential: {scenarios_2050[best_abatement]['abatement_Mt']:.1f} MtCO₂e")
        print(f"   • {lowest_cost} has lowest abatement cost: ${scenarios_2050[lowest_cost]['abatement_cost_USD_per_tCO2']:.0f}/tCO₂e")
        print(f"   • Capacity growth significantly impacts both emissions and abatement potential")
        print(f"   • Energy-intensive transition methodology provides detailed technology-specific insights")

    def run_full_analysis(self):
        """Run complete enhanced transition analysis with growth scenarios"""
        print("🚀 Starting enhanced transition analysis with growth scenarios...")

        # Execute all analysis steps
        self.load_baseline_data()
        self.define_capacity_growth_scenarios()
        self.calculate_capacity_projections()
        self.calculate_energy_intensive_transitions()
        self.calculate_scenario_transitions()

        # Create visualizations and reports
        viz_path = self.create_growth_scenario_visualization()
        report_paths = self.save_scenario_reports()

        # Print summary
        self.print_scenario_summary()

        print(f"\n✅ ENHANCED TRANSITION ANALYSIS COMPLETE!")
        print(f"📊 Main visualization: {viz_path}")
        print(f"📋 Reports: {report_paths}")
        print(f"\n🔄 Ready for policy scenario integration and optimization")

        return {
            'visualization': viz_path,
            'reports': report_paths,
            'capacity_scenarios': self.capacity_scenarios,
            'transition_results': self.transition_results
        }

if __name__ == "__main__":
    # Run the complete enhanced analysis
    enhanced_analysis = EnhancedTransitionWithGrowth()
    results = enhanced_analysis.run_full_analysis()