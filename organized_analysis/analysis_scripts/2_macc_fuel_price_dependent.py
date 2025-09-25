#!/usr/bin/env python3
"""
Script 2: MACC Generation with Fuel Price Dependencies
Generate MACC curves with dynamic fuel pricing for 2030, 2040, 2050
Exclude Energy Efficiency technology as requested
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

class FuelPriceDependentMACCGenerator:
    def __init__(self):
        """Initialize with English Excel file"""
        self.excel_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.target_years = [2030, 2040, 2050]
        self.baseline_emissions_mtco2 = 52.0  # Target baseline

        # Load data
        self.load_facility_data()
        self.create_fuel_cost_projections()
        self.define_macc_technologies()

    def load_facility_data(self):
        """Load facility and emission data"""
        print("📊 Loading facility data...")

        try:
            self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
            self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
            self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)

            print(f"   Loaded {len(self.facilities_df)} facilities")

            # Calculate total baseline emissions
            self.calculate_baseline_emissions()

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

    def calculate_baseline_emissions(self):
        """Calculate baseline emissions for scaling"""
        print("⚡ Calculating baseline emissions...")

        # Clean facility data
        facilities_clean = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        facilities_clean = facilities_clean[facilities_clean['capacity_1000_t'] > 0]

        # Map processes to products
        process_mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam',
            'Aromatics': 'Benzene',
            'Olefins': 'Ethylene'
        }

        facilities_clean['product'] = facilities_clean['process'].map(process_mapping)
        facilities_clean['product'] = facilities_clean['product'].fillna('Ethylene')

        # Calculate emissions
        emission_factors = {col: self.ci2_df.iloc[0][col] for col in self.ci2_df.columns}
        total_emissions = 0

        for idx, facility in facilities_clean.iterrows():
            product = facility['product']
            capacity = facility['capacity_1000_t'] * 1000

            if product in self.ci_df.index:
                product_row = self.ci_df.loc[product]
                facility_emission = 0

                for consumption_col, emission_col in [
                    ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ'),
                    ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ'),
                    ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ'),
                    ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh')
                ]:
                    if consumption_col in product_row.index and emission_col in emission_factors:
                        consumption = product_row[consumption_col]
                        if pd.notna(consumption) and consumption > 0:
                            facility_emission += consumption * capacity * emission_factors[emission_col]

                total_emissions += facility_emission

        self.calculated_baseline = total_emissions / 1e6
        print(f"   Calculated baseline: {self.calculated_baseline:.1f} MtCO₂")

    def create_fuel_cost_projections(self):
        """Create fuel cost projections for 2030, 2040, 2050"""
        print("💰 Creating fuel cost projections...")

        # Fuel cost projections ($/GJ or $/MWh)
        self.fuel_costs = {
            2030: {
                'natural_gas': 12.0,          # $/GJ
                'naphtha': 15.0,              # $/GJ
                'electricity_grid': 80.0,      # $/MWh
                'renewable_electricity': 120.0, # $/MWh
                'green_hydrogen': 6.0,        # $/kg H2
                'bio_naphtha': 25.0,          # $/GJ (premium over fossil)
                'biomass': 8.0,               # $/GJ
                'carbon_price': 85.0          # $/tCO2
            },
            2040: {
                'natural_gas': 14.0,          # $/GJ (increasing due to carbon pricing)
                'naphtha': 18.0,              # $/GJ
                'electricity_grid': 75.0,      # $/MWh (slightly decreasing)
                'renewable_electricity': 90.0,  # $/MWh (major cost reduction)
                'green_hydrogen': 3.5,        # $/kg H2 (significant cost reduction)
                'bio_naphtha': 22.0,          # $/GJ (scale economies)
                'biomass': 9.0,               # $/GJ
                'carbon_price': 120.0         # $/tCO2
            },
            2050: {
                'natural_gas': 16.0,          # $/GJ (high carbon price impact)
                'naphtha': 20.0,              # $/GJ
                'electricity_grid': 70.0,      # $/MWh
                'renewable_electricity': 65.0,  # $/MWh (grid parity achieved)
                'green_hydrogen': 2.0,        # $/kg H2 (mature technology)
                'bio_naphtha': 18.0,          # $/GJ (competitive with fossil)
                'biomass': 10.0,              # $/GJ
                'carbon_price': 150.0         # $/tCO2
            }
        }

        # Convert to DataFrame for easier access
        self.fuel_cost_df = pd.DataFrame(self.fuel_costs).T
        print("   Fuel cost projections created")

    def define_macc_technologies(self):
        """Define MACC technologies excluding Energy Efficiency as requested"""
        print("🔧 Defining MACC technologies (excluding Energy Efficiency)...")

        self.technologies = {
            'Early_Retirement': {
                'description': 'Early retirement of oldest/least efficient facilities',
                'abatement_potential_mtco2': 5.2,  # 10% of baseline
                'base_capex_usd_per_tco2': 0,
                'base_opex_usd_per_tco2': 50,
                'fuel_dependency': None,  # No fuel cost dependency
                'carbon_price_benefit': 0,  # No carbon benefit
                'technology_maturity': 'Commercial'
            },

            'Fuel_Switch_Biomass': {
                'description': 'Switch from fossil fuels to biomass for thermal processes',
                'abatement_potential_mtco2': 8.0,
                'base_capex_usd_per_tco2': 120,
                'base_opex_usd_per_tco2': 25,
                'fuel_dependency': {
                    'fuel_type': 'biomass',
                    'fuel_consumption_gj_per_tco2': 12.0,  # GJ biomass per tCO2 abated
                    'replaced_fuel': 'natural_gas',
                    'replaced_consumption_gj_per_tco2': 12.0
                },
                'carbon_price_benefit': 1.0,  # Full CO2 avoidance benefit
                'technology_maturity': 'Commercial'
            },

            'Electrification_Renewable': {
                'description': 'Electrification with renewable electricity',
                'abatement_potential_mtco2': 12.5,
                'base_capex_usd_per_tco2': 180,
                'base_opex_usd_per_tco2': 30,
                'fuel_dependency': {
                    'fuel_type': 'renewable_electricity',
                    'fuel_consumption_mwh_per_tco2': 2.8,  # MWh per tCO2 abated
                    'replaced_fuel': 'natural_gas',
                    'replaced_consumption_gj_per_tco2': 12.0
                },
                'carbon_price_benefit': 1.0,
                'technology_maturity': 'Demonstration'
            },

            'Bio_Naphtha': {
                'description': 'Replace fossil naphtha with bio-naphtha feedstock',
                'abatement_potential_mtco2': 10.0,
                'base_capex_usd_per_tco2': 80,
                'base_opex_usd_per_tco2': 20,
                'fuel_dependency': {
                    'fuel_type': 'bio_naphtha',
                    'fuel_consumption_gj_per_tco2': 18.0,  # GJ bio-naphtha per tCO2 abated
                    'replaced_fuel': 'naphtha',
                    'replaced_consumption_gj_per_tco2': 18.0
                },
                'carbon_price_benefit': 0.85,  # Partial lifecycle benefit
                'technology_maturity': 'Demonstration'
            },

            'Green_Hydrogen_Thermal': {
                'description': 'Green hydrogen for high-temperature thermal processes',
                'abatement_potential_mtco2': 7.5,
                'base_capex_usd_per_tco2': 200,
                'base_opex_usd_per_tco2': 40,
                'fuel_dependency': {
                    'fuel_type': 'green_hydrogen',
                    'fuel_consumption_kg_per_tco2': 450,  # kg H2 per tCO2 abated
                    'replaced_fuel': 'natural_gas',
                    'replaced_consumption_gj_per_tco2': 15.0
                },
                'carbon_price_benefit': 1.0,
                'technology_maturity': 'Pre-commercial'
            },

            'Process_Replacement_Electric': {
                'description': 'Replace thermal processes with electric alternatives',
                'abatement_potential_mtco2': 6.0,
                'base_capex_usd_per_tco2': 300,
                'base_opex_usd_per_tco2': 50,
                'fuel_dependency': {
                    'fuel_type': 'renewable_electricity',
                    'fuel_consumption_mwh_per_tco2': 4.2,  # MWh per tCO2 abated
                    'replaced_fuel': 'naphtha',
                    'replaced_consumption_gj_per_tco2': 20.0
                },
                'carbon_price_benefit': 1.0,
                'technology_maturity': 'Research'
            }
        }

        print(f"   Defined {len(self.technologies)} technologies (Energy Efficiency excluded)")

    def calculate_technology_costs(self, year):
        """Calculate technology costs including fuel price dependencies"""
        print(f"💰 Calculating technology costs for {year}...")

        fuel_costs_year = self.fuel_costs[year]
        results = []

        for tech_name, tech_data in self.technologies.items():
            # Base costs
            capex = tech_data['base_capex_usd_per_tco2']
            opex = tech_data['base_opex_usd_per_tco2']

            # Fuel cost calculation
            fuel_cost_per_tco2 = 0
            fuel_savings_per_tco2 = 0

            if tech_data['fuel_dependency'] is not None:
                fuel_dep = tech_data['fuel_dependency']

                # Cost of new fuel
                if fuel_dep['fuel_type'] == 'renewable_electricity':
                    new_fuel_cost = (fuel_dep['fuel_consumption_mwh_per_tco2'] *
                                   fuel_costs_year['renewable_electricity'])
                elif fuel_dep['fuel_type'] == 'green_hydrogen':
                    new_fuel_cost = (fuel_dep['fuel_consumption_kg_per_tco2'] *
                                   fuel_costs_year['green_hydrogen'])
                else:
                    # Other fuels (biomass, bio_naphtha) use GJ consumption
                    fuel_consumption_key = [k for k in fuel_dep.keys() if 'consumption_gj' in k][0]
                    consumption = fuel_dep[fuel_consumption_key]
                    new_fuel_cost = consumption * fuel_costs_year[fuel_dep['fuel_type']]

                # Savings from replaced fuel
                replaced_fuel = fuel_dep['replaced_fuel']
                replaced_consumption = fuel_dep['replaced_consumption_gj_per_tco2']
                fuel_cost_map = {
                    'natural_gas': 'natural_gas',
                    'naphtha': 'naphtha'
                }
                replaced_fuel_cost = (replaced_consumption *
                                     fuel_costs_year[fuel_cost_map[replaced_fuel]])

                fuel_cost_per_tco2 = new_fuel_cost
                fuel_savings_per_tco2 = replaced_fuel_cost

            # Carbon price benefit
            carbon_benefit = (tech_data['carbon_price_benefit'] *
                            fuel_costs_year['carbon_price'])

            # Net cost calculation
            net_cost_per_tco2 = (capex + opex + fuel_cost_per_tco2 -
                                fuel_savings_per_tco2 - carbon_benefit)

            # Total costs
            abatement_tco2 = tech_data['abatement_potential_mtco2'] * 1e6
            total_capex = capex * abatement_tco2 / 1e6  # Million USD
            total_fuel_cost = fuel_cost_per_tco2 * abatement_tco2 / 1e6
            total_carbon_benefit = carbon_benefit * abatement_tco2 / 1e6

            results.append({
                'technology': tech_name,
                'year': year,
                'description': tech_data['description'],
                'abatement_potential_mtco2': tech_data['abatement_potential_mtco2'],
                'capex_usd_per_tco2': capex,
                'opex_usd_per_tco2': opex,
                'fuel_cost_usd_per_tco2': fuel_cost_per_tco2,
                'fuel_savings_usd_per_tco2': fuel_savings_per_tco2,
                'carbon_benefit_usd_per_tco2': carbon_benefit,
                'net_cost_usd_per_tco2': net_cost_per_tco2,
                'total_capex_musd': total_capex,
                'total_fuel_cost_musd': total_fuel_cost,
                'total_carbon_benefit_musd': total_carbon_benefit,
                'technology_maturity': tech_data['technology_maturity']
            })

        return pd.DataFrame(results)

    def create_macc_curves(self, year):
        """Create MACC curve for specific year"""
        print(f"📈 Creating MACC curve for {year}...")

        tech_costs = self.calculate_technology_costs(year)

        # Sort by net cost
        tech_costs = tech_costs.sort_values('net_cost_usd_per_tco2')

        # Calculate cumulative abatement
        tech_costs['cumulative_abatement_mtco2'] = tech_costs['abatement_potential_mtco2'].cumsum()
        tech_costs['cumulative_cost_musd'] = (tech_costs['net_cost_usd_per_tco2'] *
                                             tech_costs['abatement_potential_mtco2']).cumsum()

        return tech_costs

    def create_fuel_cost_sheet(self):
        """Create comprehensive fuel cost sheet"""
        print("📊 Creating fuel cost sheet...")

        # Expand fuel cost data with additional details
        fuel_cost_detailed = []

        for year in self.target_years:
            costs = self.fuel_costs[year]
            for fuel, cost in costs.items():
                fuel_cost_detailed.append({
                    'year': year,
                    'fuel_type': fuel,
                    'cost_usd_per_unit': cost,
                    'unit': self.get_fuel_unit(fuel),
                    'cost_category': self.get_cost_category(fuel),
                    'volatility_risk': self.get_volatility_risk(fuel),
                    'supply_security': self.get_supply_security(fuel)
                })

        fuel_cost_df = pd.DataFrame(fuel_cost_detailed)

        # Add cost escalation rates
        fuel_cost_df['escalation_2030_2040'] = fuel_cost_df.apply(
            lambda x: self.calculate_escalation(x['fuel_type'], 2030, 2040), axis=1)
        fuel_cost_df['escalation_2040_2050'] = fuel_cost_df.apply(
            lambda x: self.calculate_escalation(x['fuel_type'], 2040, 2050), axis=1)

        return fuel_cost_df

    def get_fuel_unit(self, fuel):
        """Get appropriate unit for fuel"""
        unit_map = {
            'natural_gas': '$/GJ',
            'naphtha': '$/GJ',
            'electricity_grid': '$/MWh',
            'renewable_electricity': '$/MWh',
            'green_hydrogen': '$/kg',
            'bio_naphtha': '$/GJ',
            'biomass': '$/GJ',
            'carbon_price': '$/tCO2'
        }
        return unit_map.get(fuel, '$/unit')

    def get_cost_category(self, fuel):
        """Get cost category"""
        if 'carbon' in fuel:
            return 'Policy'
        elif 'green' in fuel or 'renewable' in fuel or 'bio' in fuel:
            return 'Low-carbon'
        else:
            return 'Fossil'

    def get_volatility_risk(self, fuel):
        """Get volatility risk assessment"""
        volatility_map = {
            'natural_gas': 'High',
            'naphtha': 'High',
            'electricity_grid': 'Medium',
            'renewable_electricity': 'Low',
            'green_hydrogen': 'Medium',
            'bio_naphtha': 'Medium',
            'biomass': 'Low',
            'carbon_price': 'High'
        }
        return volatility_map.get(fuel, 'Medium')

    def get_supply_security(self, fuel):
        """Get supply security assessment"""
        security_map = {
            'natural_gas': 'Medium',
            'naphtha': 'Medium',
            'electricity_grid': 'High',
            'renewable_electricity': 'High',
            'green_hydrogen': 'Low',
            'bio_naphtha': 'Medium',
            'biomass': 'High',
            'carbon_price': 'High'
        }
        return security_map.get(fuel, 'Medium')

    def calculate_escalation(self, fuel_type, year1, year2):
        """Calculate escalation rate between years"""
        cost1 = self.fuel_costs[year1][fuel_type]
        cost2 = self.fuel_costs[year2][fuel_type]
        years = year2 - year1
        escalation = ((cost2 / cost1) ** (1/years) - 1) * 100
        return round(escalation, 2)

    def create_comprehensive_visualization(self, macc_results):
        """Create comprehensive MACC visualization"""
        print("📊 Creating comprehensive MACC visualization...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical MACC Analysis - Fuel Price Dependent\\n(Energy Efficiency Excluded)',
                    fontsize=16, fontweight='bold')

        # Plot 1: MACC Curves by Year
        ax1 = axes[0, 0]
        colors = {2030: '#d62728', 2040: '#ff7f0e', 2050: '#2ca02c'}

        for year, color in colors.items():
            macc_data = macc_results[year]

            x_vals = [0]
            y_vals = [0]
            cumulative = 0

            for _, tech in macc_data.iterrows():
                x_vals.append(cumulative)
                y_vals.append(tech['net_cost_usd_per_tco2'])
                cumulative += tech['abatement_potential_mtco2']
                x_vals.append(cumulative)
                y_vals.append(tech['net_cost_usd_per_tco2'])

            ax1.step(x_vals, y_vals, where='post', linewidth=2.5,
                    label=f'{year}', color=color)

        ax1.set_xlabel('Cumulative Abatement (MtCO₂/year)')
        ax1.set_ylabel('Cost ($/tCO₂)')
        ax1.set_title('MACC Curves - Fuel Price Impact')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 600)

        # Plot 2: Fuel Cost Evolution
        ax2 = axes[0, 1]

        key_fuels = ['green_hydrogen', 'renewable_electricity', 'bio_naphtha', 'carbon_price']
        for fuel in key_fuels:
            costs = [self.fuel_costs[year][fuel] for year in self.target_years]
            ax2.plot(self.target_years, costs, marker='o', linewidth=2, label=fuel.replace('_', ' ').title())

        ax2.set_xlabel('Year')
        ax2.set_ylabel('Cost ($/unit)')
        ax2.set_title('Key Fuel Cost Projections')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Technology Cost Breakdown (2030)
        ax3 = axes[1, 0]

        macc_2030 = macc_results[2030]
        technologies = macc_2030['technology']
        capex = macc_2030['capex_usd_per_tco2']
        opex = macc_2030['opex_usd_per_tco2']
        fuel_cost = macc_2030['fuel_cost_usd_per_tco2']
        carbon_benefit = -macc_2030['carbon_benefit_usd_per_tco2']  # Negative for benefit

        x_pos = range(len(technologies))

        p1 = ax3.bar(x_pos, capex, label='CAPEX', alpha=0.8, color='steelblue')
        p2 = ax3.bar(x_pos, opex, bottom=capex, label='OPEX', alpha=0.8, color='orange')
        p3 = ax3.bar(x_pos, fuel_cost, bottom=capex + opex, label='Fuel Cost', alpha=0.8, color='red')
        p4 = ax3.bar(x_pos, carbon_benefit, bottom=capex + opex + fuel_cost,
                    label='Carbon Benefit', alpha=0.8, color='green')

        ax3.set_xlabel('Technology')
        ax3.set_ylabel('Cost ($/tCO₂)')
        ax3.set_title('Cost Breakdown by Technology (2030)')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([tech.replace('_', ' ') for tech in technologies], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Abatement Potential vs Cost (2050)
        ax4 = axes[1, 1]

        macc_2050 = macc_results[2050]
        scatter = ax4.scatter(macc_2050['abatement_potential_mtco2'],
                             macc_2050['net_cost_usd_per_tco2'],
                             s=100, alpha=0.7, c=range(len(macc_2050)), cmap='viridis')

        for i, tech in enumerate(macc_2050['technology']):
            ax4.annotate(tech.replace('_', ' '),
                        (macc_2050.iloc[i]['abatement_potential_mtco2'],
                         macc_2050.iloc[i]['net_cost_usd_per_tco2']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax4.set_xlabel('Abatement Potential (MtCO₂/year)')
        ax4.set_ylabel('Net Cost ($/tCO₂)')
        ax4.set_title('Abatement Potential vs Cost (2050)')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save visualization
        output_path = Path("../outputs/macc_fuel_price_dependent.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {output_path}")

        plt.show()

    def export_results(self, macc_results, fuel_cost_sheet):
        """Export comprehensive results"""
        print("💾 Exporting MACC results...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export MACC results for each year
        for year, macc_data in macc_results.items():
            macc_data.to_csv(output_dir / f"macc_fuel_dependent_{year}.csv", index=False)

        # Export fuel cost sheet
        fuel_cost_sheet.to_csv(output_dir / "fuel_cost_projections.csv", index=False)

        # Export technology definitions
        tech_definitions = []
        for tech_name, tech_data in self.technologies.items():
            tech_definitions.append({
                'technology': tech_name,
                'description': tech_data['description'],
                'abatement_potential_mtco2': tech_data['abatement_potential_mtco2'],
                'base_capex_usd_per_tco2': tech_data['base_capex_usd_per_tco2'],
                'base_opex_usd_per_tco2': tech_data['base_opex_usd_per_tco2'],
                'has_fuel_dependency': tech_data['fuel_dependency'] is not None,
                'carbon_price_benefit': tech_data['carbon_price_benefit'],
                'technology_maturity': tech_data['technology_maturity']
            })

        tech_df = pd.DataFrame(tech_definitions)
        tech_df.to_csv(output_dir / "technology_definitions_no_efficiency.csv", index=False)

        # Export summary comparison
        summary_data = []
        for year in self.target_years:
            macc_data = macc_results[year]
            summary_data.append({
                'year': year,
                'total_abatement_mtco2': macc_data['abatement_potential_mtco2'].sum(),
                'total_capex_musd': macc_data['total_capex_musd'].sum(),
                'lowest_cost_usd_per_tco2': macc_data['net_cost_usd_per_tco2'].min(),
                'highest_cost_usd_per_tco2': macc_data['net_cost_usd_per_tco2'].max(),
                'average_cost_usd_per_tco2': (macc_data['net_cost_usd_per_tco2'] *
                                             macc_data['abatement_potential_mtco2']).sum() /
                                            macc_data['abatement_potential_mtco2'].sum(),
                'technologies_count': len(macc_data)
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / "macc_temporal_summary.csv", index=False)

        print(f"   Exported results to: {output_dir}")

    def run_complete_analysis(self):
        """Run complete fuel price dependent MACC analysis"""
        print("🚀 FUEL PRICE DEPENDENT MACC ANALYSIS")
        print("=" * 80)
        print("💰 Dynamic fuel pricing: Green H2, renewable electricity, bio-naphtha")
        print("⚡ Energy Efficiency technology excluded as requested")
        print("📈 Temporal analysis: 2030, 2040, 2050")
        print()

        try:
            # Generate MACC curves for each year
            macc_results = {}
            for year in self.target_years:
                macc_results[year] = self.create_macc_curves(year)

            # Create fuel cost sheet
            fuel_cost_sheet = self.create_fuel_cost_sheet()

            # Create visualizations
            self.create_comprehensive_visualization(macc_results)

            # Export results
            self.export_results(macc_results, fuel_cost_sheet)

            # Print summary
            print("\n🎯 FUEL PRICE DEPENDENT MACC SUMMARY:")
            print(f"   📊 Technologies analyzed: {len(self.technologies)} (Energy Efficiency excluded)")
            print(f"   🎯 Total abatement potential: {sum(tech['abatement_potential_mtco2'] for tech in self.technologies.values()):.1f} MtCO₂")

            for year in self.target_years:
                macc_data = macc_results[year]
                avg_cost = (macc_data['net_cost_usd_per_tco2'] * macc_data['abatement_potential_mtco2']).sum() / macc_data['abatement_potential_mtco2'].sum()
                print(f"   💰 {year}: ${macc_data['net_cost_usd_per_tco2'].min():.0f}-${macc_data['net_cost_usd_per_tco2'].max():.0f}/tCO₂ (avg: ${avg_cost:.0f}/tCO₂)")

            return macc_results, fuel_cost_sheet

        except Exception as e:
            print(f"❌ MACC analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    generator = FuelPriceDependentMACCGenerator()
    macc_results, fuel_costs = generator.run_complete_analysis()

    print("\n✅ FUEL PRICE DEPENDENT MACC ANALYSIS COMPLETE!")
    print("📁 Results exported to organized_analysis/outputs/")