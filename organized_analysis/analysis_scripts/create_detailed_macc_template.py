#!/usr/bin/env python3
"""
Create MACC Template with Detailed CAPEX and Fuel Costs
Uses 248 facilities data to build comprehensive MACC with temporal projections
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

class DetailedMACCTemplateCreator:
    def __init__(self):
        """Initialize with corrected baseline data"""
        self.excel_path = "../data/Korean_Petrochemical_MACC_Model_Calibrated_52Mt.xlsx"
        self.baseline_year = 2025
        self.target_years = [2030, 2040, 2050]
        self.baseline_emissions_mtco2 = 52.0

        # Load all required data
        self.load_excel_data()
        self.define_detailed_technologies()

    def load_excel_data(self):
        """Load and clean all relevant data from Excel"""
        print("📊 Loading Excel data...")

        # Load facility data
        self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
        print(f"   Loaded {len(self.facilities_df)} facilities")

        # Load consumption intensities
        self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
        print(f"   Loaded CI data: {self.ci_df.shape}")

        # Load emission factors
        self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)
        print(f"   Loaded CI2 data: {self.ci2_df.shape}")

        # Clean and prepare facility data
        self.clean_facility_data()

    def clean_facility_data(self):
        """Clean and prepare 248 facilities data"""
        print("🧹 Cleaning facility data...")

        # Remove facilities with missing critical data
        initial_count = len(self.facilities_df)

        # Remove facilities with invalid capacity or year
        self.facilities_df = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_df = self.facilities_df[self.facilities_df['capacity_1000_t'] > 0]
        self.facilities_df = self.facilities_df[self.facilities_df['year'] > 1900]  # Valid years

        # Calculate facility age and emissions
        self.facilities_df['age_years'] = 2025 - self.facilities_df['year']
        self.facilities_df['capacity_t'] = self.facilities_df['capacity_1000_t'] * 1000

        # Use location column for region if available, otherwise create generic region
        if 'location' in self.facilities_df.columns:
            self.facilities_df['region'] = self.facilities_df['location']
        else:
            self.facilities_df['region'] = 'Unknown'

        # Map process types to products for CI lookup
        process_mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam',
            'Aromatics': 'Benzene',
            'Olefins': 'Ethylene'
        }

        self.facilities_df['product'] = self.facilities_df['process'].map(process_mapping)
        self.facilities_df['product'] = self.facilities_df['product'].fillna('Ethylene')  # Default to Ethylene

        # Calculate facility-level emissions
        self.calculate_facility_emissions()

        # Remove facilities with zero emissions
        self.facilities_df = self.facilities_df[self.facilities_df['emissions_tco2'] > 0]

        print(f"   Cleaned: {initial_count} → {len(self.facilities_df)} facilities")
        print(f"   Total emissions: {self.facilities_df['emissions_tco2'].sum()/1e6:.1f} MtCO₂")

    def calculate_facility_emissions(self):
        """Calculate detailed emissions for each facility"""
        print("⚡ Calculating facility emissions...")

        # Get emission factors from CI2
        emission_factors = {col: self.ci2_df.iloc[0][col] for col in self.ci2_df.columns}

        facility_emissions = []

        for idx, facility in self.facilities_df.iterrows():
            product = facility['product']
            capacity = facility['capacity_t']

            if product not in self.ci_df.index:
                facility_emissions.append(0)
                continue

            product_row = self.ci_df.loc[product]
            facility_emission = 0

            # Calculate emissions from each fuel/feedstock
            fuel_consumptions = {}

            for consumption_col, emission_col in [
                ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ'),
                ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ'),
                ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ'),
                ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh')
            ]:
                if consumption_col in product_row.index and emission_col in emission_factors:
                    consumption = product_row[consumption_col]
                    if pd.notna(consumption) and consumption > 0:
                        fuel_emission = consumption * capacity * emission_factors[emission_col]
                        facility_emission += fuel_emission
                        fuel_consumptions[consumption_col] = consumption * capacity

            facility_emissions.append(facility_emission)

            # Store fuel consumption details for later CAPEX calculations
            self.facilities_df.loc[idx, 'lng_consumption_gj'] = fuel_consumptions.get('LNG_GJ_per_t', 0)
            self.facilities_df.loc[idx, 'naphtha_feedstock_gj'] = fuel_consumptions.get('Naphtha_Feedstock_GJ_per_t', 0)
            self.facilities_df.loc[idx, 'naphtha_thermal_gj'] = fuel_consumptions.get('Naphtha_Thermal_GJ_per_t', 0)
            self.facilities_df.loc[idx, 'electricity_kwh'] = fuel_consumptions.get('Electricity_kWh_per_t', 0)

        self.facilities_df['emissions_tco2'] = facility_emissions

    def define_detailed_technologies(self):
        """Define detailed abatement technologies with CAPEX and fuel costs"""
        print("🔧 Defining detailed abatement technologies...")

        self.technologies = {
            'Early_Retirement': {
                'description': 'Early retirement of oldest/least efficient facilities',
                'capex_usd_per_tco2_abated': 0,  # No CAPEX, just lost production
                'opex_usd_per_tco2_abated': 50,  # Opportunity cost
                'fuel_cost_savings_usd_per_tco2': 0,
                'abatement_potential_pct': 10,  # 10% of baseline
                'applicable_processes': ['All'],
                'min_facility_age': 20,  # Only old facilities
                'temporal_capex_multiplier': {'2030': 1.0, '2040': 1.0, '2050': 1.0}
            },

            'Efficiency_Upgrade': {
                'description': 'Energy efficiency improvements (heat integration, optimization)',
                'capex_usd_per_tco2_abated': 80,  # Equipment upgrades
                'opex_usd_per_tco2_abated': 20,   # Maintenance
                'fuel_cost_savings_usd_per_tco2': 45,  # Reduced fuel consumption
                'abatement_potential_pct': 15,  # 15% reduction potential
                'applicable_processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'],
                'min_facility_age': 5,  # Can upgrade newer facilities
                'temporal_capex_multiplier': {'2030': 1.0, '2040': 0.85, '2050': 0.7}  # Cost reduction over time
            },

            'Fuel_Switch': {
                'description': 'Switch from naphtha/LNG to cleaner fuels (renewable electricity, biomass)',
                'capex_usd_per_tco2_abated': 150,  # New fuel infrastructure
                'opex_usd_per_tco2_abated': 30,    # Higher fuel costs
                'fuel_cost_savings_usd_per_tco2': -20,  # Premium for clean fuels
                'abatement_potential_pct': 25,  # 25% can switch fuels
                'applicable_processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'],
                'min_facility_age': 0,  # All facilities can switch
                'temporal_capex_multiplier': {'2030': 1.2, '2040': 1.0, '2050': 0.8}  # Infrastructure improves
            },

            'Electrification': {
                'description': 'Electrification of thermal processes with renewable electricity',
                'capex_usd_per_tco2_abated': 200,  # Electric equipment
                'opex_usd_per_tco2_abated': 40,    # Higher electricity costs
                'fuel_cost_savings_usd_per_tco2': -10,  # Premium for renewable electricity
                'abatement_potential_pct': 20,  # 20% can be electrified
                'applicable_processes': ['Utility', 'Naphtha Cracker'],
                'min_facility_age': 0,  # All facilities
                'temporal_capex_multiplier': {'2030': 1.3, '2040': 1.0, '2050': 0.7}  # Technology improves rapidly
            },

            'Bio_Naphtha': {
                'description': 'Replace fossil naphtha with bio-based naphtha feedstock',
                'capex_usd_per_tco2_abated': 120,  # Feedstock handling modifications
                'opex_usd_per_tco2_abated': 80,    # Premium for bio-naphtha
                'fuel_cost_savings_usd_per_tco2': -70,  # Much higher feedstock cost
                'abatement_potential_pct': 15,  # 15% of naphtha can be bio
                'applicable_processes': ['Naphtha Cracker'],
                'min_facility_age': 0,  # All crackers can use bio-naphtha
                'temporal_capex_multiplier': {'2030': 1.5, '2040': 1.2, '2050': 1.0}  # Bio-naphtha supply improves
            },

            'Green_Hydrogen': {
                'description': 'Use green hydrogen for high-temperature processes',
                'capex_usd_per_tco2_abated': 250,  # Hydrogen infrastructure
                'opex_usd_per_tco2_abated': 100,   # High hydrogen costs
                'fuel_cost_savings_usd_per_tco2': -50,  # Premium for green H2
                'abatement_potential_pct': 12,  # 12% can use hydrogen
                'applicable_processes': ['Utility', 'Naphtha Cracker'],
                'min_facility_age': 0,  # All facilities
                'temporal_capex_multiplier': {'2030': 2.0, '2040': 1.5, '2050': 1.0}  # H2 costs drop significantly
            },

            'Process_Replacement': {
                'description': 'Replace entire process with low-carbon alternative technology',
                'capex_usd_per_tco2_abated': 350,  # Complete new process
                'opex_usd_per_tco2_abated': 70,    # Different operating costs
                'fuel_cost_savings_usd_per_tco2': 20,   # More efficient processes
                'abatement_potential_pct': 8,   # 8% can replace processes
                'applicable_processes': ['Naphtha Cracker', 'BTX Plant'],
                'min_facility_age': 15,  # Only replace older processes
                'temporal_capex_multiplier': {'2030': 1.8, '2040': 1.3, '2050': 1.0}  # New tech develops
            }
        }

    def calculate_technology_costs_and_abatement(self, year):
        """Calculate detailed costs and abatement for each technology in given year"""
        print(f"💰 Calculating technology costs for {year}...")

        year_str = str(year)
        results = []

        total_baseline_emissions = self.facilities_df['emissions_tco2'].sum()

        for tech_name, tech_data in self.technologies.items():
            # Calculate temporal CAPEX multiplier
            capex_multiplier = tech_data['temporal_capex_multiplier'].get(year_str, 1.0)

            # Base costs
            capex_per_tco2 = tech_data['capex_usd_per_tco2_abated'] * capex_multiplier
            opex_per_tco2 = tech_data['opex_usd_per_tco2_abated']
            fuel_savings_per_tco2 = tech_data['fuel_cost_savings_usd_per_tco2']

            # Net cost per tCO2 (CAPEX + OPEX - Fuel Savings)
            net_cost_per_tco2 = capex_per_tco2 + opex_per_tco2 - fuel_savings_per_tco2

            # Calculate abatement potential
            applicable_facilities = self.facilities_df[
                (self.facilities_df['process'].isin(tech_data['applicable_processes']) |
                 ('All' in tech_data['applicable_processes'])) &
                (self.facilities_df['age_years'] >= tech_data['min_facility_age'])
            ]

            if len(applicable_facilities) == 0:
                continue

            # Abatement potential based on facility emissions
            potential_abatement_tco2 = applicable_facilities['emissions_tco2'].sum() * (tech_data['abatement_potential_pct'] / 100)

            # For early retirement, use facility age prioritization
            if tech_name == 'Early_Retirement':
                # Prioritize oldest facilities
                oldest_facilities = applicable_facilities.nlargest(int(len(applicable_facilities) * 0.1), 'age_years')
                potential_abatement_tco2 = oldest_facilities['emissions_tco2'].sum()

            # Calculate total costs
            total_capex_musd = (capex_per_tco2 * potential_abatement_tco2) / 1e6
            total_opex_musd = (opex_per_tco2 * potential_abatement_tco2) / 1e6
            total_fuel_savings_musd = (fuel_savings_per_tco2 * potential_abatement_tco2) / 1e6
            total_net_cost_musd = total_capex_musd + total_opex_musd - total_fuel_savings_musd

            results.append({
                'technology': tech_name,
                'year': year,
                'description': tech_data['description'],
                'applicable_facilities': len(applicable_facilities),
                'abatement_potential_tco2': potential_abatement_tco2,
                'abatement_potential_mtco2': potential_abatement_tco2 / 1e6,
                'capex_usd_per_tco2': capex_per_tco2,
                'opex_usd_per_tco2': opex_per_tco2,
                'fuel_savings_usd_per_tco2': fuel_savings_per_tco2,
                'net_cost_usd_per_tco2': net_cost_per_tco2,
                'total_capex_musd': total_capex_musd,
                'total_opex_musd': total_opex_musd,
                'total_fuel_savings_musd': total_fuel_savings_musd,
                'total_net_cost_musd': total_net_cost_musd,
                'capex_multiplier': capex_multiplier
            })

        return pd.DataFrame(results)

    def create_macc_curves(self, year):
        """Create MACC curve for specific year"""
        print(f"📈 Creating MACC curve for {year}...")

        tech_df = self.calculate_technology_costs_and_abatement(year)

        # Sort by net cost per tCO2
        tech_df = tech_df.sort_values('net_cost_usd_per_tco2')

        # Calculate cumulative abatement
        tech_df['cumulative_abatement_tco2'] = tech_df['abatement_potential_tco2'].cumsum()
        tech_df['cumulative_abatement_mtco2'] = tech_df['cumulative_abatement_tco2'] / 1e6
        tech_df['cumulative_cost_musd'] = tech_df['total_net_cost_musd'].cumsum()

        return tech_df

    def create_temporal_macc_analysis(self):
        """Create complete temporal MACC analysis"""
        print("🕐 Creating temporal MACC analysis...")

        all_results = {}

        for year in [2030, 2040, 2050]:
            macc_df = self.create_macc_curves(year)
            all_results[year] = macc_df

            # Export detailed results
            output_dir = Path("../outputs")
            output_dir.mkdir(exist_ok=True)

            macc_df.to_csv(output_dir / f"detailed_macc_template_{year}.csv", index=False)
            print(f"   Exported: detailed_macc_template_{year}.csv")

        return all_results

    def create_comprehensive_visualization(self, all_results):
        """Create comprehensive MACC visualization"""
        print("📊 Creating comprehensive visualization...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical MACC Analysis - Detailed Cost Breakdown\\n248 Facilities, Temporal Projections',
                    fontsize=16, fontweight='bold')

        # Plot 1: MACC Curves by Year
        ax1 = axes[0, 0]
        colors = {'2030': '#d62728', '2040': '#ff7f0e', '2050': '#2ca02c'}

        for year, color in colors.items():
            if year in [2030, 2040, 2050]:
                macc_df = all_results[year]

                x_vals = [0]
                y_vals = [0]
                cumulative = 0

                for _, tech in macc_df.iterrows():
                    x_vals.append(cumulative)
                    y_vals.append(tech['net_cost_usd_per_tco2'])
                    cumulative += tech['abatement_potential_mtco2']
                    x_vals.append(cumulative)
                    y_vals.append(tech['net_cost_usd_per_tco2'])

                ax1.step(x_vals, y_vals, where='post', linewidth=2.5, label=f'{year}', color=color)

        ax1.set_xlabel('Cumulative Abatement (MtCO₂/year)')
        ax1.set_ylabel('Cost ($/tCO₂)')
        ax1.set_title('MACC Curves - Temporal Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 500)

        # Plot 2: Technology Cost Breakdown (2030)
        ax2 = axes[0, 1]
        macc_2030 = all_results[2030]

        technologies = macc_2030['technology']
        capex_costs = macc_2030['capex_usd_per_tco2']
        opex_costs = macc_2030['opex_usd_per_tco2']
        fuel_savings = -macc_2030['fuel_savings_usd_per_tco2']  # Negative for savings

        x_pos = range(len(technologies))

        p1 = ax2.bar(x_pos, capex_costs, label='CAPEX', alpha=0.8, color='steelblue')
        p2 = ax2.bar(x_pos, opex_costs, bottom=capex_costs, label='OPEX', alpha=0.8, color='orange')
        p3 = ax2.bar(x_pos, fuel_savings, bottom=capex_costs + opex_costs,
                    label='Fuel Savings', alpha=0.8, color='green')

        ax2.set_xlabel('Technology')
        ax2.set_ylabel('Cost ($/tCO₂)')
        ax2.set_title('Cost Breakdown by Technology (2030)')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([tech.replace('_', ' ') for tech in technologies], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Abatement Potential by Technology
        ax3 = axes[1, 0]

        abatement_2030 = macc_2030['abatement_potential_mtco2']
        abatement_2040 = all_results[2040]['abatement_potential_mtco2']
        abatement_2050 = all_results[2050]['abatement_potential_mtco2']

        x_pos = range(len(technologies))
        width = 0.25

        ax3.bar([x - width for x in x_pos], abatement_2030, width, label='2030', alpha=0.8)
        ax3.bar(x_pos, abatement_2040, width, label='2040', alpha=0.8)
        ax3.bar([x + width for x in x_pos], abatement_2050, width, label='2050', alpha=0.8)

        ax3.set_xlabel('Technology')
        ax3.set_ylabel('Abatement Potential (MtCO₂/year)')
        ax3.set_title('Abatement Potential by Technology')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([tech.replace('_', ' ') for tech in technologies], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Investment Requirements
        ax4 = axes[1, 1]

        years = [2030, 2040, 2050]
        total_investments = []
        capex_investments = []

        for year in years:
            total_investments.append(all_results[year]['total_net_cost_musd'].sum())
            capex_investments.append(all_results[year]['total_capex_musd'].sum())

        x_pos = range(len(years))

        ax4.bar(x_pos, capex_investments, label='CAPEX', alpha=0.8, color='steelblue')
        ax4.bar(x_pos, [total - capex for total, capex in zip(total_investments, capex_investments)],
               bottom=capex_investments, label='Net OPEX', alpha=0.8, color='orange')

        ax4.set_xlabel('Year')
        ax4.set_ylabel('Investment (Million $)')
        ax4.set_title('Total Investment Requirements')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(years)
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save visualization
        output_path = Path("../outputs/detailed_macc_template_comprehensive.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {output_path}")

        plt.show()

    def export_excel_template(self, all_results):
        """Export comprehensive Excel template"""
        print("📁 Exporting comprehensive Excel template...")

        output_path = Path("../outputs/MACC_Template_Corrected_Detailed.xlsx")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Export facility data - use available columns only
            available_cols = ['company', 'region', 'process', 'capacity_1000_t', 'age_years', 'emissions_tco2']

            # Add fuel consumption columns if they exist
            fuel_cols = ['lng_consumption_gj', 'naphtha_feedstock_gj', 'naphtha_thermal_gj', 'electricity_kwh']
            for col in fuel_cols:
                if col in self.facilities_df.columns:
                    available_cols.append(col)

            facility_summary = self.facilities_df[available_cols].copy()
            facility_summary['emissions_mtco2'] = facility_summary['emissions_tco2'] / 1e6
            facility_summary.to_excel(writer, sheet_name='Facilities_248', index=False)

            # Export technology definitions
            tech_definitions = []
            for tech_name, tech_data in self.technologies.items():
                tech_definitions.append({
                    'technology': tech_name,
                    'description': tech_data['description'],
                    'base_capex_usd_per_tco2': tech_data['capex_usd_per_tco2_abated'],
                    'opex_usd_per_tco2': tech_data['opex_usd_per_tco2_abated'],
                    'fuel_savings_usd_per_tco2': tech_data['fuel_cost_savings_usd_per_tco2'],
                    'abatement_potential_pct': tech_data['abatement_potential_pct'],
                    'applicable_processes': ', '.join(tech_data['applicable_processes']),
                    'min_facility_age': tech_data['min_facility_age']
                })

            tech_df = pd.DataFrame(tech_definitions)
            tech_df.to_excel(writer, sheet_name='Technology_Definitions', index=False)

            # Export temporal MACC results
            for year in [2030, 2040, 2050]:
                all_results[year].to_excel(writer, sheet_name=f'MACC_{year}', index=False)

            # Export summary comparison
            summary_data = []
            for year in [2030, 2040, 2050]:
                year_data = all_results[year]
                summary_data.append({
                    'year': year,
                    'total_abatement_mtco2': year_data['abatement_potential_mtco2'].sum(),
                    'total_capex_musd': year_data['total_capex_musd'].sum(),
                    'total_net_cost_musd': year_data['total_net_cost_musd'].sum(),
                    'lowest_cost_usd_per_tco2': year_data['net_cost_usd_per_tco2'].min(),
                    'highest_cost_usd_per_tco2': year_data['net_cost_usd_per_tco2'].max(),
                    'technologies_available': len(year_data)
                })

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Temporal_Summary', index=False)

        print(f"   Exported: {output_path}")

    def run_complete_analysis(self):
        """Run complete detailed MACC template analysis"""
        print("🚀 CREATING DETAILED MACC TEMPLATE WITH CAPEX/FUEL COSTS")
        print("=" * 80)
        print(f"📊 Using 248 facilities from corrected baseline")
        print(f"🎯 Temporal projections: 2030, 2040, 2050")
        print()

        try:
            # Create temporal analysis
            all_results = self.create_temporal_macc_analysis()

            # Create visualizations
            self.create_comprehensive_visualization(all_results)

            # Export Excel template
            self.export_excel_template(all_results)

            # Print summary
            print("\n🎯 DETAILED MACC TEMPLATE SUMMARY:")
            print(f"   📊 Facilities analyzed: {len(self.facilities_df)}")
            print(f"   🏭 Total baseline emissions: {self.facilities_df['emissions_tco2'].sum()/1e6:.1f} MtCO₂")
            print(f"   🔧 Technologies defined: {len(self.technologies)}")
            print(f"   📈 Temporal projections: 2030, 2040, 2050")

            for year in [2030, 2040, 2050]:
                year_data = all_results[year]
                print(f"   💰 {year} total investment: ${year_data['total_net_cost_musd'].sum():.0f}M")
                print(f"   📉 {year} max abatement: {year_data['abatement_potential_mtco2'].sum():.1f} MtCO₂")

            return all_results

        except Exception as e:
            print(f"❌ Error creating detailed MACC template: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    creator = DetailedMACCTemplateCreator()
    results = creator.run_complete_analysis()

    print("\n✅ DETAILED MACC TEMPLATE CREATION COMPLETE!")
    print("📁 All results exported to organized_analysis/outputs/")