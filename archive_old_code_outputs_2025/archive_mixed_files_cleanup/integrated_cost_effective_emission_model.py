#!/usr/bin/env python3
"""
Integrated Cost-Effective Emission Path Model
Shows facility-level technology implementation and cost-effective pathways
Compares BAU, emission targets, and optimized pathways in comprehensive Excel output
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class IntegratedEmissionPathModel:
    def __init__(self):
        """Initialize integrated model with corrected baseline"""
        self.excel_path = "organized_analysis/data/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.baseline_year = 2025
        self.target_years = [2030, 2040, 2050]
        self.projection_years = list(range(2025, 2051))

        # Emission reduction targets (from guidance)
        self.emission_targets = {
            2030: 0.25,   # 25% reduction by 2030
            2040: 0.50,   # 50% reduction by 2040
            2050: 0.75    # 75% reduction by 2050
        }

        # Target baseline: 52 MtCO2 (from fundamental guidance)
        self.target_baseline_mtco2 = 52.0

        # Load and process data
        self.load_and_process_data()
        self.define_technologies()
        self.calculate_baseline_emissions()

    def load_and_process_data(self):
        """Load and process facility data"""
        print("📊 Loading and processing facility data...")

        # Load facility data
        self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
        self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
        self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)

        # Clean facility data
        self.facilities_df = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_df = self.facilities_df[self.facilities_df['capacity_1000_t'] > 0]
        self.facilities_df = self.facilities_df[self.facilities_df['year'] > 1900]

        # Map processes to products
        process_mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam',
            'Aromatics': 'Benzene',
            'Olefins': 'Ethylene'
        }

        self.facilities_df['product'] = self.facilities_df['process'].map(process_mapping)
        self.facilities_df['product'] = self.facilities_df['product'].fillna('Ethylene')
        self.facilities_df['capacity_t'] = self.facilities_df['capacity_1000_t'] * 1000
        self.facilities_df['age_2025'] = 2025 - self.facilities_df['year']

        print(f"   Loaded {len(self.facilities_df)} valid facilities")

    def define_technologies(self):
        """Define low-carbon technologies with specifications from guidance"""
        print("🔧 Defining low-carbon technologies...")

        self.technologies = {
            'Bio_Naphtha': {
                'name': 'Bio-Naphtha',
                'description': '10% energy reduction through bio-naphtha feedstock',
                'applicable_processes': ['Naphtha Cracker'],
                'energy_reduction': 0.10,  # 10% energy reduction (from guidance)
                'emission_reduction': 0.85,  # 85% emission reduction
                'capex_usd_per_t_capacity': 300,  # $/tonne capacity
                'opex_usd_per_t_product': 50,   # $/tonne product
                'deployment_limit': 0.6,  # Max 60% deployment by 2050
                'technology_maturity': 'Commercial',
                'learning_rate': 0.12  # 12% cost reduction per doubling
            },

            'NCC_Hydrogen': {
                'name': 'NCC Hydrogen',
                'description': 'Hydrogen for naphtha cracking processes',
                'applicable_processes': ['Naphtha Cracker'],
                'energy_reduction': 0.05,  # 5% energy reduction
                'emission_reduction': 0.75,  # 75% emission reduction
                'capex_usd_per_t_capacity': 800,  # $/tonne capacity
                'opex_usd_per_t_product': 100,   # $/tonne product
                'deployment_limit': 0.8,  # Max 80% deployment
                'technology_maturity': 'Demonstration',
                'learning_rate': 0.15  # 15% cost reduction
            },

            'NCC_Electricity': {
                'name': 'NCC Electricity',
                'description': 'Electrification of naphtha cracking',
                'applicable_processes': ['Naphtha Cracker'],
                'energy_reduction': 0.08,  # 8% energy reduction
                'emission_reduction': 0.60,  # 60% emission reduction
                'capex_usd_per_t_capacity': 400,  # $/tonne capacity
                'opex_usd_per_t_product': 30,   # $/tonne product
                'deployment_limit': 0.25,  # Max 25% deployment (limited by process constraints)
                'technology_maturity': 'Demonstration',
                'learning_rate': 0.18  # 18% cost reduction
            },

            'Heat_Pump': {
                'name': 'Heat Pump',
                'description': 'Industrial heat pumps for process heating',
                'applicable_processes': ['BTX Plant', 'Utility'],
                'energy_reduction': 0.15,  # 15% energy reduction
                'emission_reduction': 0.40,  # 40% emission reduction
                'capex_usd_per_t_capacity': 150,  # $/tonne capacity
                'opex_usd_per_t_product': 20,   # $/tonne product
                'deployment_limit': 0.5,  # Max 50% deployment
                'technology_maturity': 'Commercial',
                'learning_rate': 0.10  # 10% cost reduction
            },

            'Renewable_Energy': {
                'name': 'Renewable Energy',
                'description': 'Solar and wind for electricity supply',
                'applicable_processes': ['BTX Plant', 'Utility'],
                'energy_reduction': 0.05,  # 5% energy reduction (efficiency)
                'emission_reduction': 0.90,  # 90% emission reduction for electricity
                'capex_usd_per_t_capacity': 200,  # $/tonne capacity
                'opex_usd_per_t_product': 15,   # $/tonne product
                'deployment_limit': 0.8,  # Max 80% deployment
                'technology_maturity': 'Commercial',
                'learning_rate': 0.08  # 8% cost reduction
            },

            'Early_Retirement': {
                'name': 'Early Retirement',
                'description': 'Early retirement of high-emission facilities',
                'applicable_processes': ['Naphtha Cracker', 'BTX Plant', 'Utility'],
                'energy_reduction': 1.0,  # 100% energy reduction (facility closed)
                'emission_reduction': 1.0,  # 100% emission reduction
                'capex_usd_per_t_capacity': 0,   # No CAPEX
                'opex_usd_per_t_product': -50,  # Savings from no operation
                'deployment_limit': 0.3,  # Max 30% of capacity
                'technology_maturity': 'Commercial',
                'learning_rate': 0.0   # No learning effects
            }
        }

        # Cost evolution factors by year
        self.cost_factors = {
            2025: 1.0,
            2030: 0.9,   # 10% cost reduction by 2030
            2040: 0.75,  # 25% cost reduction by 2040
            2050: 0.6    # 40% cost reduction by 2050
        }

    def calculate_baseline_emissions(self):
        """Calculate baseline emissions and calibrate to 52 MtCO2 target"""
        print("⚡ Calculating baseline emissions...")

        # Get emission factors
        emission_factors = {col: self.ci2_df.iloc[0][col] for col in self.ci2_df.columns}

        baseline_emissions = []
        energy_consumption = []

        for idx, facility in self.facilities_df.iterrows():
            product = facility['product']
            capacity = facility['capacity_t']

            if product not in self.ci_df.index:
                baseline_emissions.append(0)
                energy_consumption.append(0)
                continue

            product_row = self.ci_df.loc[product]
            facility_emission = 0
            facility_energy = 0

            # Calculate emissions from each source
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

                        # Convert electricity to GJ for energy consumption
                        if 'kWh' in consumption_col:
                            facility_energy += consumption * capacity * 3.6 / 1000  # Convert kWh to GJ
                        else:
                            facility_energy += consumption * capacity

            baseline_emissions.append(facility_emission)
            energy_consumption.append(facility_energy)

        self.facilities_df['baseline_emissions_tco2'] = baseline_emissions
        self.facilities_df['energy_consumption_gj'] = energy_consumption

        # Calculate total baseline
        total_baseline = sum(baseline_emissions) / 1e6  # Convert to MtCO2

        # Calibration factor to reach 52 MtCO2 target
        self.calibration_factor = self.target_baseline_mtco2 / total_baseline

        # Apply calibration
        self.facilities_df['calibrated_emissions_tco2'] = self.facilities_df['baseline_emissions_tco2'] * self.calibration_factor
        self.facilities_df['calibrated_energy_gj'] = self.facilities_df['energy_consumption_gj'] * self.calibration_factor

        print(f"   Original baseline: {total_baseline:.1f} MtCO₂")
        print(f"   Calibration factor: {self.calibration_factor:.3f}")
        print(f"   Calibrated baseline: {self.target_baseline_mtco2:.1f} MtCO₂")

        # Remove facilities with zero emissions
        self.facilities_df = self.facilities_df[self.facilities_df['calibrated_emissions_tco2'] > 0].copy()
        print(f"   Final facility count: {len(self.facilities_df)}")

    def generate_bau_pathway(self):
        """Generate BAU pathway with facility retirement (50-year lifetime)"""
        print("📈 Generating BAU emission pathway...")

        facility_lifetime = 50  # Standard 50-year lifetime
        bau_pathway = []

        for year in self.projection_years:
            # Facilities still operating in this year
            active_facilities = self.facilities_df[
                (self.facilities_df['year'] + facility_lifetime) > year
            ].copy()

            if len(active_facilities) > 0:
                total_emissions = active_facilities['calibrated_emissions_tco2'].sum() / 1e6
            else:
                total_emissions = 0

            bau_pathway.append({
                'year': year,
                'emissions_mtco2': total_emissions,
                'active_facilities': len(active_facilities),
                'retired_facilities': len(self.facilities_df) - len(active_facilities)
            })

        return pd.DataFrame(bau_pathway)

    def calculate_technology_costs(self, year, cumulative_deployment_mt=0):
        """Calculate technology costs with learning curves"""
        tech_costs = {}

        base_factor = self.cost_factors.get(year, 0.6)

        for tech_name, tech_spec in self.technologies.items():
            # Learning curve effect
            learning_factor = (1 + cumulative_deployment_mt) ** (-tech_spec['learning_rate'])

            # Combined cost factor
            cost_factor = base_factor * learning_factor

            capex = tech_spec['capex_usd_per_t_capacity'] * cost_factor
            opex = tech_spec['opex_usd_per_t_product'] * cost_factor

            tech_costs[tech_name] = {
                'capex_usd_per_t': capex,
                'opex_usd_per_t': opex,
                'total_cost_usd_per_t': capex * 0.1 + opex,  # Annualized CAPEX (10% discount)
                'abatement_cost_usd_per_tco2': 0  # Will calculate based on emission reduction
            }

            # Calculate abatement cost
            emission_reduction = tech_spec['emission_reduction']
            if emission_reduction > 0:
                # Estimate annual emission reduction per tonne capacity
                avg_emission_intensity = 0.8  # tCO2/tonne capacity (approximate)
                annual_abatement_tco2 = avg_emission_intensity * emission_reduction

                if annual_abatement_tco2 > 0:
                    tech_costs[tech_name]['abatement_cost_usd_per_tco2'] = \
                        tech_costs[tech_name]['total_cost_usd_per_t'] / annual_abatement_tco2

        return tech_costs

    def optimize_technology_deployment(self, target_year, emission_reduction_target):
        """Optimize technology deployment for given target"""
        print(f"⚖️ Optimizing for {target_year} with {emission_reduction_target*100:.0f}% reduction target...")

        # Get technology costs for target year
        tech_costs = self.calculate_technology_costs(target_year)

        # Facilities available for deployment
        active_facilities = self.facilities_df[
            (self.facilities_df['year'] + 50) > target_year  # Still operating
        ].copy()

        if len(active_facilities) == 0:
            return pd.DataFrame(), pd.DataFrame(), 0

        # Calculate target emission reduction
        baseline_emissions = active_facilities['calibrated_emissions_tco2'].sum()
        target_reduction_tco2 = baseline_emissions * emission_reduction_target

        # Create deployment optimization
        deployment_results = []
        facility_deployments = []

        # Sort technologies by cost-effectiveness
        tech_order = sorted(self.technologies.keys(),
                          key=lambda x: tech_costs[x]['abatement_cost_usd_per_tco2'])

        remaining_reduction = target_reduction_tco2
        total_cost = 0

        for tech_name in tech_order:
            if remaining_reduction <= 0:
                break

            tech_spec = self.technologies[tech_name]
            tech_cost = tech_costs[tech_name]

            # Find applicable facilities
            applicable_facilities = active_facilities[
                active_facilities['process'].isin(tech_spec['applicable_processes'])
            ].copy()

            if len(applicable_facilities) == 0:
                continue

            # Calculate potential deployment
            total_capacity = applicable_facilities['capacity_t'].sum()
            max_deployment = total_capacity * tech_spec['deployment_limit']

            # Calculate potential emission reduction
            total_emissions = applicable_facilities['calibrated_emissions_tco2'].sum()
            potential_reduction = total_emissions * tech_spec['emission_reduction']

            # Deploy as much as needed/possible
            actual_deployment = min(max_deployment,
                                  remaining_reduction / tech_spec['emission_reduction'] *
                                  (applicable_facilities['capacity_t'].sum() / total_capacity))
            actual_deployment = min(actual_deployment, total_capacity)

            if actual_deployment > 0:
                deployment_fraction = actual_deployment / total_capacity
                actual_reduction = potential_reduction * deployment_fraction
                cost = actual_deployment * tech_cost['total_cost_usd_per_t']

                deployment_results.append({
                    'technology': tech_name,
                    'deployment_capacity_t': actual_deployment,
                    'deployment_fraction': deployment_fraction,
                    'emission_reduction_tco2': actual_reduction,
                    'total_cost_usd': cost,
                    'cost_per_tco2_abated': cost / actual_reduction if actual_reduction > 0 else 0,
                    'facilities_affected': len(applicable_facilities)
                })

                # Record facility-level deployments
                for idx, facility in applicable_facilities.iterrows():
                    facility_deployment = facility['capacity_t'] * deployment_fraction

                    facility_deployments.append({
                        'facility_id': idx,
                        'company': facility['company'],
                        'location': facility.get('location', 'Unknown'),
                        'process': facility['process'],
                        'capacity_t': facility['capacity_t'],
                        'technology': tech_name,
                        'deployment_capacity_t': facility_deployment,
                        'deployment_fraction': deployment_fraction,
                        'facility_emission_reduction_tco2': facility['calibrated_emissions_tco2'] *
                                                          tech_spec['emission_reduction'] * deployment_fraction,
                        'facility_cost_usd': facility_deployment * tech_cost['total_cost_usd_per_t'],
                        'target_year': target_year
                    })

                remaining_reduction -= actual_reduction
                total_cost += cost

        deployment_summary = pd.DataFrame(deployment_results)
        facility_deployment_details = pd.DataFrame(facility_deployments)

        achieved_reduction = target_reduction_tco2 - remaining_reduction
        print(f"   Target: {target_reduction_tco2/1e6:.2f} MtCO₂ reduction")
        print(f"   Achieved: {achieved_reduction/1e6:.2f} MtCO₂ reduction")
        print(f"   Total cost: ${total_cost/1e9:.1f}B")

        return deployment_summary, facility_deployment_details, total_cost

    def generate_cost_effective_pathway(self):
        """Generate cost-effective emission pathway by optimizing for each target year"""
        print("🎯 Generating cost-effective emission pathway...")

        pathway_results = []
        all_deployments = []
        all_facility_deployments = []

        for year in self.target_years:
            target_reduction = self.emission_targets[year]

            # Optimize deployment
            deployment_summary, facility_details, total_cost = \
                self.optimize_technology_deployment(year, target_reduction)

            # Calculate resulting emissions
            active_facilities = self.facilities_df[
                (self.facilities_df['year'] + 50) > year
            ].copy()

            baseline_emissions = active_facilities['calibrated_emissions_tco2'].sum() if len(active_facilities) > 0 else 0
            achieved_reduction = deployment_summary['emission_reduction_tco2'].sum() if not deployment_summary.empty else 0
            final_emissions = (baseline_emissions - achieved_reduction) / 1e6

            pathway_results.append({
                'year': year,
                'baseline_emissions_mtco2': baseline_emissions / 1e6,
                'target_reduction_pct': target_reduction * 100,
                'achieved_reduction_mtco2': achieved_reduction / 1e6,
                'final_emissions_mtco2': final_emissions,
                'total_cost_billion_usd': total_cost / 1e9,
                'technologies_deployed': len(deployment_summary),
                'facilities_affected': facility_details['facility_id'].nunique() if not facility_details.empty else 0
            })

            # Store deployment details
            if not deployment_summary.empty:
                deployment_summary['target_year'] = year
                all_deployments.append(deployment_summary)

            if not facility_details.empty:
                all_facility_deployments.append(facility_details)

        pathway_df = pd.DataFrame(pathway_results)
        deployments_df = pd.concat(all_deployments, ignore_index=True) if all_deployments else pd.DataFrame()
        facility_deployments_df = pd.concat(all_facility_deployments, ignore_index=True) if all_facility_deployments else pd.DataFrame()

        return pathway_df, deployments_df, facility_deployments_df

    def generate_comprehensive_analysis(self):
        """Generate comprehensive analysis with all pathways"""
        print("\n🚀 GENERATING COMPREHENSIVE COST-EFFECTIVE ANALYSIS")
        print("=" * 80)

        # 1. Generate BAU pathway
        bau_pathway = self.generate_bau_pathway()

        # 2. Generate cost-effective pathway
        cost_effective_pathway, technology_deployments, facility_deployments = \
            self.generate_cost_effective_pathway()

        # 3. Create emission target pathway (linear interpolation)
        target_pathway = []
        baseline_2025 = self.target_baseline_mtco2

        for year in self.projection_years:
            if year <= 2030:
                target_emissions = baseline_2025 * (1 - self.emission_targets[2030] * (year - 2025) / 5)
            elif year <= 2040:
                target_2030 = baseline_2025 * (1 - self.emission_targets[2030])
                target_emissions = target_2030 * (1 - (self.emission_targets[2040] - self.emission_targets[2030]) * (year - 2030) / 10)
            else:
                target_2040 = baseline_2025 * (1 - self.emission_targets[2040])
                target_emissions = target_2040 * (1 - (self.emission_targets[2050] - self.emission_targets[2040]) * (year - 2040) / 10)

            target_pathway.append({
                'year': year,
                'target_emissions_mtco2': max(target_emissions, 0)
            })

        target_pathway_df = pd.DataFrame(target_pathway)

        # 4. Create comparison summary
        comparison_data = []
        for year in [2030, 2040, 2050]:
            bau_emissions = bau_pathway[bau_pathway['year'] == year]['emissions_mtco2'].iloc[0]
            target_emissions = target_pathway_df[target_pathway_df['year'] == year]['target_emissions_mtco2'].iloc[0]

            # Find cost-effective emissions
            cost_effective_row = cost_effective_pathway[cost_effective_pathway['year'] == year]
            cost_effective_emissions = cost_effective_row['final_emissions_mtco2'].iloc[0] if not cost_effective_row.empty else bau_emissions
            cost_effective_cost = cost_effective_row['total_cost_billion_usd'].iloc[0] if not cost_effective_row.empty else 0

            comparison_data.append({
                'year': year,
                'bau_emissions_mtco2': bau_emissions,
                'target_emissions_mtco2': target_emissions,
                'cost_effective_emissions_mtco2': cost_effective_emissions,
                'cost_billion_usd': cost_effective_cost,
                'target_achievement_pct': min(100, (1 - cost_effective_emissions / target_emissions) * 100) if target_emissions > 0 else 100
            })

        comparison_df = pd.DataFrame(comparison_data)

        return {
            'bau_pathway': bau_pathway,
            'target_pathway': target_pathway_df,
            'cost_effective_pathway': cost_effective_pathway,
            'technology_deployments': technology_deployments,
            'facility_deployments': facility_deployments,
            'pathway_comparison': comparison_df,
            'facilities_master': self.facilities_df,
            'technologies_master': pd.DataFrame.from_dict(self.technologies, orient='index')
        }

    def export_to_excel(self, results, filename="Integrated_Cost_Effective_Emission_Analysis.xlsx"):
        """Export all results to comprehensive Excel file"""
        print(f"💾 Exporting comprehensive analysis to {filename}...")

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:

            # Executive Summary
            executive_summary = pd.DataFrame([
                ['Baseline Emissions (2025)', f"{self.target_baseline_mtco2:.1f} MtCO₂"],
                ['BAU Emissions (2050)', f"{results['bau_pathway'][results['bau_pathway']['year']==2050]['emissions_mtco2'].iloc[0]:.1f} MtCO₂"],
                ['Target Emissions (2050)', f"{results['target_pathway'][results['target_pathway']['year']==2050]['target_emissions_mtco2'].iloc[0]:.1f} MtCO₂"],
                ['Cost-Effective Emissions (2050)', f"{results['cost_effective_pathway'][results['cost_effective_pathway']['year']==2050]['final_emissions_mtco2'].iloc[0]:.1f} MtCO₂"],
                ['Total Investment (2025-2050)', f"${results['cost_effective_pathway']['total_cost_billion_usd'].sum():.1f}B"],
                ['Technologies Deployed', f"{len(results['technology_deployments'])}"],
                ['Facilities Affected', f"{results['facility_deployments']['facility_id'].nunique() if not results['facility_deployments'].empty else 0}"],
                ['Target Achievement (2050)', f"{results['pathway_comparison'][results['pathway_comparison']['year']==2050]['target_achievement_pct'].iloc[0]:.1f}%"]
            ], columns=['Metric', 'Value'])
            executive_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)

            # Pathway Comparison
            results['pathway_comparison'].to_excel(writer, sheet_name='Pathway_Comparison', index=False)

            # BAU Analysis
            results['bau_pathway'].to_excel(writer, sheet_name='BAU_Pathway', index=False)

            # Target Pathway
            results['target_pathway'].to_excel(writer, sheet_name='Target_Pathway', index=False)

            # Cost-Effective Pathway
            results['cost_effective_pathway'].to_excel(writer, sheet_name='Cost_Effective_Pathway', index=False)

            # Technology Deployments
            if not results['technology_deployments'].empty:
                results['technology_deployments'].to_excel(writer, sheet_name='Technology_Deployments', index=False)

            # Facility-Level Deployments
            if not results['facility_deployments'].empty:
                results['facility_deployments'].to_excel(writer, sheet_name='Facility_Deployments', index=False)

            # Master Data
            results['facilities_master'].to_excel(writer, sheet_name='Facilities_Master', index=False)
            results['technologies_master'].to_excel(writer, sheet_name='Technologies_Master', index=True)

        print(f"   ✅ Exported to {filename}")
        return filename

    def create_summary_visualization(self, results):
        """Create comprehensive visualization"""
        print("📊 Creating summary visualization...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Integrated Cost-Effective Emission Path Analysis', fontsize=16, fontweight='bold')

        # 1. Pathway comparison
        ax1 = axes[0,0]
        comparison = results['pathway_comparison']

        years = comparison['year']
        ax1.plot(years, comparison['bau_emissions_mtco2'], 'o-', label='BAU', linewidth=2, color='red')
        ax1.plot(years, comparison['target_emissions_mtco2'], 's--', label='Target', linewidth=2, color='blue')
        ax1.plot(years, comparison['cost_effective_emissions_mtco2'], '^-', label='Cost-Effective', linewidth=2, color='green')

        ax1.set_title('Emission Pathways Comparison')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Technology deployment
        ax2 = axes[0,1]
        if not results['technology_deployments'].empty:
            tech_summary = results['technology_deployments'].groupby('technology')['emission_reduction_tco2'].sum() / 1e6
            tech_summary.plot(kind='bar', ax=ax2, color='skyblue')
            ax2.set_title('Emission Reduction by Technology')
            ax2.set_ylabel('Emission Reduction (MtCO₂)')
            ax2.tick_params(axis='x', rotation=45)

        # 3. Cost analysis
        ax3 = axes[1,0]
        costs = results['pathway_comparison']['cost_billion_usd']
        cumulative_cost = costs.cumsum()
        ax3.bar(years, costs, alpha=0.7, color='orange', label='Annual')
        ax3.plot(years, cumulative_cost, 'ro-', label='Cumulative')
        ax3.set_title('Investment Requirements')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cost (Billion USD)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Facility impact
        ax4 = axes[1,1]
        if not results['facility_deployments'].empty:
            facility_impact = results['facility_deployments'].groupby('target_year')['facility_id'].nunique()
            ax4.bar(facility_impact.index, facility_impact.values, color='lightgreen')
            ax4.set_title('Facilities Affected by Year')
            ax4.set_xlabel('Year')
            ax4.set_ylabel('Number of Facilities')
            ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('Integrated_Cost_Effective_Analysis.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved visualization: Integrated_Cost_Effective_Analysis.png")

        return 'Integrated_Cost_Effective_Analysis.png'

def main():
    """Main execution function"""

    # Initialize and run analysis
    model = IntegratedEmissionPathModel()
    results = model.generate_comprehensive_analysis()

    # Export to Excel
    excel_file = model.export_to_excel(results)

    # Create visualization
    viz_file = model.create_summary_visualization(results)

    # Print summary
    print("\n🎯 INTEGRATED ANALYSIS COMPLETE!")
    print("=" * 50)
    print(f"📊 Excel Report: {excel_file}")
    print(f"📈 Visualization: {viz_file}")
    print(f"🏭 Facilities analyzed: {len(results['facilities_master'])}")
    print(f"🔧 Technologies available: {len(results['technologies_master'])}")

    # Key results
    comparison = results['pathway_comparison']
    print(f"\n🎯 KEY RESULTS (2050):")
    print(f"   BAU Emissions: {comparison[comparison['year']==2050]['bau_emissions_mtco2'].iloc[0]:.1f} MtCO₂")
    print(f"   Target Emissions: {comparison[comparison['year']==2050]['target_emissions_mtco2'].iloc[0]:.1f} MtCO₂")
    print(f"   Cost-Effective: {comparison[comparison['year']==2050]['cost_effective_emissions_mtco2'].iloc[0]:.1f} MtCO₂")
    print(f"   Total Investment: ${comparison['cost_billion_usd'].sum():.1f}B")
    print(f"   Target Achievement: {comparison[comparison['year']==2050]['target_achievement_pct'].iloc[0]:.1f}%")

if __name__ == "__main__":
    main()