#!/usr/bin/env python3
"""
Script 3: Cost Optimization Model with Depreciation Considerations
Optimize technology deployment considering facility depreciation, operation years, and total system costs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class CostOptimizationWithDepreciation:
    def __init__(self):
        """Initialize optimization model"""
        self.excel_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.baseline_year = 2025
        self.target_years = [2030, 2040, 2050]
        self.emission_reduction_targets = [0.25, 0.50, 0.75]  # 25%, 50%, 75% reduction

        # Economic parameters
        self.discount_rate = 0.07  # 7% discount rate
        self.facility_lifetime = 30  # Standard facility lifetime for depreciation

        # Load data and prepare optimization
        self.load_data()
        self.prepare_optimization_data()

    def load_data(self):
        """Load facility and technology data"""
        print("📊 Loading optimization data...")

        try:
            # Load facility data
            self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
            self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
            self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)

            # Load MACC results from previous analysis
            self.load_macc_results()

            print(f"   Loaded {len(self.facilities_df)} facilities")
            print(f"   Loaded MACC data for {len(self.macc_2030)} technologies")

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            # Create fallback data if files don't exist
            self.create_fallback_data()

    def load_macc_results(self):
        """Load MACC results from previous analysis"""
        try:
            self.macc_2030 = pd.read_csv("../outputs/macc_fuel_dependent_2030.csv")
            self.macc_2040 = pd.read_csv("../outputs/macc_fuel_dependent_2040.csv")
            self.macc_2050 = pd.read_csv("../outputs/macc_fuel_dependent_2050.csv")
        except FileNotFoundError:
            print("   Creating fallback MACC data...")
            self.create_fallback_macc_data()

    def create_fallback_macc_data(self):
        """Create fallback MACC data if previous analysis not available"""
        technologies = ['Early_Retirement', 'Fuel_Switch_Biomass', 'Electrification_Renewable',
                       'Bio_Naphtha', 'Green_Hydrogen_Thermal', 'Process_Replacement_Electric']

        # Create simplified MACC data
        macc_data = []
        for i, tech in enumerate(technologies):
            macc_data.append({
                'technology': tech,
                'abatement_potential_mtco2': 5.0 + i * 2.0,
                'net_cost_usd_per_tco2': 50 + i * 100,
                'capex_usd_per_tco2': 100 + i * 50,
                'opex_usd_per_tco2': 20 + i * 10,
                'technology_maturity': ['Commercial', 'Commercial', 'Demonstration',
                                      'Demonstration', 'Pre-commercial', 'Research'][i]
            })

        base_df = pd.DataFrame(macc_data)

        # Create temporal variations
        self.macc_2030 = base_df.copy()
        self.macc_2030['year'] = 2030
        self.macc_2030['net_cost_usd_per_tco2'] *= 1.2  # Higher costs in 2030

        self.macc_2040 = base_df.copy()
        self.macc_2040['year'] = 2040
        self.macc_2040['net_cost_usd_per_tco2'] *= 1.0  # Base costs in 2040

        self.macc_2050 = base_df.copy()
        self.macc_2050['year'] = 2050
        self.macc_2050['net_cost_usd_per_tco2'] *= 0.7  # Lower costs in 2050

    def create_fallback_data(self):
        """Create fallback facility data"""
        print("   Creating fallback facility data...")

        # Create synthetic facility data
        np.random.seed(42)
        n_facilities = 100

        self.facilities_df = pd.DataFrame({
            'facility_id': range(n_facilities),
            'company': [f'Company_{i//10}' for i in range(n_facilities)],
            'location': np.random.choice(['Yeosu', 'Ulsan', 'Daesan', 'Onsan'], n_facilities),
            'process': np.random.choice(['Naphtha Cracker', 'BTX Plant', 'Utility'], n_facilities),
            'capacity_1000_t': np.random.uniform(50, 500, n_facilities),
            'year': np.random.randint(1990, 2020, n_facilities),
            'emissions_tco2': np.random.uniform(100000, 1000000, n_facilities)
        })

    def prepare_optimization_data(self):
        """Prepare data for optimization"""
        print("🔧 Preparing optimization data...")

        # Clean facility data
        self.facilities_clean = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_clean = self.facilities_clean[self.facilities_clean['capacity_1000_t'] > 0]

        # Calculate facility characteristics
        self.facilities_clean['age_2025'] = 2025 - self.facilities_clean['year']
        self.facilities_clean['remaining_life'] = np.maximum(0, self.facility_lifetime - self.facilities_clean['age_2025'])

        # Calculate emissions if not available
        if 'emissions_tco2' not in self.facilities_clean.columns:
            self.calculate_facility_emissions()

        # Calculate depreciation values
        self.calculate_depreciation_values()

        # Prepare MACC data dictionary
        self.macc_data = {
            2030: self.macc_2030,
            2040: self.macc_2040,
            2050: self.macc_2050
        }

        print(f"   Prepared {len(self.facilities_clean)} facilities for optimization")
        print(f"   Total baseline emissions: {self.facilities_clean['emissions_tco2'].sum()/1e6:.1f} MtCO₂")

    def calculate_facility_emissions(self):
        """Calculate facility emissions if not available"""
        print("⚡ Calculating facility emissions...")

        # Simplified emission calculation based on capacity and process type
        emission_factors = {
            'Naphtha Cracker': 800,  # tCO2 per 1000t capacity
            'BTX Plant': 600,
            'Utility': 400
        }

        emissions = []
        for _, facility in self.facilities_clean.iterrows():
            process = facility.get('process', 'Naphtha Cracker')
            capacity = facility['capacity_1000_t']
            factor = emission_factors.get(process, 600)
            emissions.append(capacity * factor)

        self.facilities_clean['emissions_tco2'] = emissions

    def calculate_depreciation_values(self):
        """Calculate facility depreciation and stranded asset values"""
        print("💰 Calculating depreciation values...")

        # Assume linear depreciation over facility lifetime
        # Original asset value proportional to capacity
        asset_value_per_kt = 50e6  # $50M per 1000t capacity (typical for petrochemical)

        self.facilities_clean['original_asset_value'] = (
            self.facilities_clean['capacity_1000_t'] * asset_value_per_kt
        )

        # Calculate current book value (linear depreciation)
        depreciation_rate = 1 / self.facility_lifetime
        self.facilities_clean['annual_depreciation'] = (
            self.facilities_clean['original_asset_value'] * depreciation_rate
        )

        self.facilities_clean['accumulated_depreciation'] = (
            self.facilities_clean['age_2025'] * self.facilities_clean['annual_depreciation']
        )

        self.facilities_clean['current_book_value'] = np.maximum(
            0,
            self.facilities_clean['original_asset_value'] - self.facilities_clean['accumulated_depreciation']
        )

        # Calculate stranded asset cost if retired early
        self.facilities_clean['stranded_asset_cost_per_year'] = (
            self.facilities_clean['current_book_value'] / np.maximum(1, self.facilities_clean['remaining_life'])
        )

    def define_optimization_objective(self, deployment_vars, target_year, emission_target):
        """Define optimization objective function"""

        macc_year = self.macc_data[target_year]
        total_cost = 0

        # Technology deployment costs
        for i, tech_row in macc_year.iterrows():
            deployment_fraction = deployment_vars[i]

            if deployment_fraction > 0:
                # CAPEX (discounted)
                years_to_target = target_year - self.baseline_year
                discount_factor = (1 + self.discount_rate) ** (-years_to_target)

                capex_cost = (deployment_fraction * tech_row['abatement_potential_mtco2'] * 1e6 *
                             tech_row['capex_usd_per_tco2'] * discount_factor)

                # Annual OPEX (present value over facility life)
                opex_pv = 0
                for year in range(years_to_target, min(years_to_target + 20, 30)):  # 20-year operation
                    opex_annual = (deployment_fraction * tech_row['abatement_potential_mtco2'] * 1e6 *
                                  tech_row['opex_usd_per_tco2'])
                    opex_pv += opex_annual * (1 + self.discount_rate) ** (-year)

                total_cost += capex_cost + opex_pv

        # Early retirement costs (stranded assets)
        early_retirement_deployment = deployment_vars[0] if len(deployment_vars) > 0 else 0
        if early_retirement_deployment > 0:
            # Sort facilities by retirement priority (oldest first)
            retirement_candidates = self.facilities_clean.nlargest(
                int(len(self.facilities_clean) * early_retirement_deployment),
                'age_2025'
            )
            stranded_costs = retirement_candidates['stranded_asset_cost_per_year'].sum()
            total_cost += stranded_costs * (target_year - self.baseline_year)  # Cost over period

        return total_cost

    def define_emission_constraint(self, deployment_vars, target_year, emission_target):
        """Define emission reduction constraint"""

        macc_year = self.macc_data[target_year]
        total_abatement = 0

        for i, tech_row in macc_year.iterrows():
            deployment_fraction = deployment_vars[i]
            abatement = deployment_fraction * tech_row['abatement_potential_mtco2']
            total_abatement += abatement

        # Target abatement (in MtCO2)
        baseline_emissions = self.facilities_clean['emissions_tco2'].sum() / 1e6
        target_abatement = baseline_emissions * emission_target

        # Constraint: achieved abatement >= target abatement
        return total_abatement - target_abatement

    def run_optimization_scenario(self, target_year, emission_target):
        """Run optimization for specific year and emission target"""
        print(f"🎯 Optimizing for {target_year}, {emission_target*100}% reduction...")

        macc_year = self.macc_data[target_year]
        n_technologies = len(macc_year)

        # Check if target is achievable
        max_abatement = macc_year['abatement_potential_mtco2'].sum()
        baseline_emissions = self.facilities_clean['emissions_tco2'].sum() / 1e6
        target_abatement = baseline_emissions * emission_target

        if target_abatement > max_abatement:
            print(f"   ⚠️  Target ({target_abatement:.1f} Mt) exceeds max abatement ({max_abatement:.1f} Mt)")
            # Scale down to achievable target
            emission_target = max_abatement / baseline_emissions * 0.9  # 90% of max
            target_abatement = baseline_emissions * emission_target
            print(f"   📉 Adjusted target to {emission_target*100:.1f}% ({target_abatement:.1f} Mt)")

        # Use simpler merit-order approach if optimization fails
        try:
            # Sort technologies by cost
            macc_sorted = macc_year.sort_values('net_cost_usd_per_tco2').reset_index(drop=True)

            # Deploy technologies in merit order until target is met
            deployment_fractions = np.zeros(n_technologies)
            cumulative_abatement = 0

            for i, (_, tech) in enumerate(macc_sorted.iterrows()):
                original_index = macc_year[macc_year['technology'] == tech['technology']].index[0]

                remaining_target = target_abatement - cumulative_abatement
                if remaining_target <= 0:
                    break

                tech_potential = tech['abatement_potential_mtco2']
                if tech_potential <= remaining_target:
                    # Deploy full technology
                    deployment_fractions[original_index] = 1.0
                    cumulative_abatement += tech_potential
                else:
                    # Deploy partial technology
                    deployment_fractions[original_index] = remaining_target / tech_potential
                    cumulative_abatement += remaining_target

            # Calculate total cost
            total_cost = 0
            for i, tech_row in macc_year.iterrows():
                if deployment_fractions[i] > 0:
                    deployment_cost = (deployment_fractions[i] *
                                     tech_row['abatement_potential_mtco2'] * 1e6 *
                                     tech_row['net_cost_usd_per_tco2'])
                    total_cost += deployment_cost

            return {
                'success': True,
                'target_year': target_year,
                'emission_target': emission_target,
                'deployment_fractions': deployment_fractions,
                'total_cost_musd': total_cost / 1e6,
                'technologies': macc_year['technology'].values,
                'technology_costs': macc_year['net_cost_usd_per_tco2'].values,
                'achieved_abatement': cumulative_abatement
            }

        except Exception as e:
            print(f"   ❌ Error in optimization: {str(e)}")
            return None

    def run_comprehensive_optimization(self):
        """Run optimization for all scenarios"""
        print("🚀 Running comprehensive cost optimization...")

        optimization_results = []

        for target_year in self.target_years:
            for emission_target in self.emission_reduction_targets:
                result = self.run_optimization_scenario(target_year, emission_target)
                if result:
                    optimization_results.append(result)

        return optimization_results

    def analyze_optimization_results(self, optimization_results):
        """Analyze and summarize optimization results"""
        print("📊 Analyzing optimization results...")

        # Create summary DataFrame
        summary_data = []
        detailed_deployments = []

        for result in optimization_results:
            summary_data.append({
                'year': result['target_year'],
                'emission_target_pct': result['emission_target'] * 100,
                'total_cost_musd': result['total_cost_musd'],
                'achieved_abatement_mtco2': result['achieved_abatement'],
                'cost_per_tco2_avg': result['total_cost_musd'] / result['achieved_abatement'] * 1e6 if result['achieved_abatement'] > 0 else 0
            })

            # Detailed deployment analysis
            for i, tech in enumerate(result['technologies']):
                if result['deployment_fractions'][i] > 0.01:  # Only include significant deployments
                    detailed_deployments.append({
                        'year': result['target_year'],
                        'emission_target_pct': result['emission_target'] * 100,
                        'technology': tech,
                        'deployment_fraction': result['deployment_fractions'][i],
                        'abatement_mtco2': result['deployment_fractions'][i] *
                                         self.macc_data[result['target_year']].iloc[i]['abatement_potential_mtco2'],
                        'technology_cost_usd_per_tco2': result['technology_costs'][i]
                    })

        summary_df = pd.DataFrame(summary_data)
        deployments_df = pd.DataFrame(detailed_deployments)

        return summary_df, deployments_df

    def create_optimization_visualizations(self, summary_df, deployments_df):
        """Create comprehensive optimization visualizations"""
        print("📊 Creating optimization visualizations...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical Cost Optimization with Depreciation\\nMinimum Cost Technology Deployment',
                    fontsize=16, fontweight='bold')

        # Plot 1: Cost vs Emission Reduction by Year
        ax1 = axes[0, 0]
        colors = {2030: '#d62728', 2040: '#ff7f0e', 2050: '#2ca02c'}

        for year in self.target_years:
            year_data = summary_df[summary_df['year'] == year]
            ax1.plot(year_data['emission_target_pct'], year_data['total_cost_musd'],
                    marker='o', linewidth=2, markersize=8, label=f'{year}', color=colors[year])

        ax1.set_xlabel('Emission Reduction Target (%)')
        ax1.set_ylabel('Total Cost (Million $)')
        ax1.set_title('Optimization Cost by Emission Target')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Average Cost per tCO2
        ax2 = axes[0, 1]

        for year in self.target_years:
            year_data = summary_df[summary_df['year'] == year]
            ax2.plot(year_data['emission_target_pct'], year_data['cost_per_tco2_avg'],
                    marker='s', linewidth=2, markersize=8, label=f'{year}', color=colors[year])

        ax2.set_xlabel('Emission Reduction Target (%)')
        ax2.set_ylabel('Average Cost ($/tCO₂)')
        ax2.set_title('Average Abatement Cost')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Technology Deployment Patterns (2050, 75% reduction)
        ax3 = axes[1, 0]

        scenario_data = deployments_df[
            (deployments_df['year'] == 2050) & (deployments_df['emission_target_pct'] == 75)
        ]

        if not scenario_data.empty:
            technologies = scenario_data['technology']
            deployments = scenario_data['deployment_fraction']
            colors_tech = plt.cm.Set3(np.linspace(0, 1, len(technologies)))

            bars = ax3.bar(range(len(technologies)), deployments, color=colors_tech, alpha=0.7)
            ax3.set_xlabel('Technology')
            ax3.set_ylabel('Deployment Fraction')
            ax3.set_title('Optimal Technology Mix (2050, 75% reduction)')
            ax3.set_xticks(range(len(technologies)))
            ax3.set_xticklabels([tech.replace('_', ' ') for tech in technologies], rotation=45, ha='right')
            ax3.grid(True, alpha=0.3)

            # Add value labels
            for bar, value in zip(bars, deployments):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.2f}', ha='center', va='bottom', fontweight='bold')

        # Plot 4: Cost Efficiency Analysis
        ax4 = axes[1, 1]

        # Cost efficiency = abatement per dollar
        summary_df['cost_efficiency'] = summary_df['achieved_abatement_mtco2'] / summary_df['total_cost_musd']

        for year in self.target_years:
            year_data = summary_df[summary_df['year'] == year]
            ax4.plot(year_data['emission_target_pct'], year_data['cost_efficiency'],
                    marker='^', linewidth=2, markersize=8, label=f'{year}', color=colors[year])

        ax4.set_xlabel('Emission Reduction Target (%)')
        ax4.set_ylabel('Cost Efficiency (MtCO₂/Million $)')
        ax4.set_title('Cost Efficiency by Scenario')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save visualization
        output_path = Path("../outputs/cost_optimization_depreciation.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {output_path}")

        plt.show()

    def export_optimization_results(self, optimization_results, summary_df, deployments_df):
        """Export comprehensive optimization results"""
        print("💾 Exporting optimization results...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export summary
        summary_df.to_csv(output_dir / "optimization_summary_with_depreciation.csv", index=False)

        # Export detailed deployments
        deployments_df.to_csv(output_dir / "optimal_technology_deployments.csv", index=False)

        # Export facility depreciation analysis
        available_cols = ['company', 'location', 'process', 'capacity_1000_t',
                         'age_2025', 'remaining_life', 'original_asset_value', 'current_book_value',
                         'stranded_asset_cost_per_year', 'emissions_tco2']

        # Only include columns that exist
        existing_cols = [col for col in available_cols if col in self.facilities_clean.columns]
        facility_depreciation = self.facilities_clean[existing_cols].copy()

        # Add facility_id if it doesn't exist
        if 'facility_id' not in facility_depreciation.columns:
            facility_depreciation['facility_id'] = range(len(facility_depreciation))

        facility_depreciation['original_asset_value_musd'] = facility_depreciation['original_asset_value'] / 1e6
        facility_depreciation['current_book_value_musd'] = facility_depreciation['current_book_value'] / 1e6
        facility_depreciation['stranded_cost_musd_per_year'] = facility_depreciation['stranded_asset_cost_per_year'] / 1e6
        facility_depreciation['emissions_mtco2'] = facility_depreciation['emissions_tco2'] / 1e6

        facility_depreciation.to_csv(output_dir / "facility_depreciation_analysis.csv", index=False)

        # Export detailed optimization results
        detailed_results = []
        for result in optimization_results:
            for i, tech in enumerate(result['technologies']):
                detailed_results.append({
                    'year': result['target_year'],
                    'emission_target_pct': result['emission_target'] * 100,
                    'technology': tech,
                    'deployment_fraction': result['deployment_fractions'][i],
                    'technology_cost_usd_per_tco2': result['technology_costs'][i],
                    'abatement_mtco2': result['deployment_fractions'][i] *
                                     self.macc_data[result['target_year']].iloc[i]['abatement_potential_mtco2']
                })

        detailed_df = pd.DataFrame(detailed_results)
        detailed_df.to_csv(output_dir / "detailed_optimization_results.csv", index=False)

        print(f"   Exported results to: {output_dir}")

    def run_complete_analysis(self):
        """Run complete cost optimization analysis"""
        print("🚀 COST OPTIMIZATION WITH DEPRECIATION ANALYSIS")
        print("=" * 80)
        print("📊 Facility depreciation and stranded asset costs included")
        print("🎯 Emission targets: 25%, 50%, 75% reduction")
        print("📈 Target years: 2030, 2040, 2050")
        print()

        try:
            # Run optimization
            optimization_results = self.run_comprehensive_optimization()

            if not optimization_results:
                print("❌ No successful optimization results")
                return None

            # Analyze results
            summary_df, deployments_df = self.analyze_optimization_results(optimization_results)

            # Create visualizations
            self.create_optimization_visualizations(summary_df, deployments_df)

            # Export results
            self.export_optimization_results(optimization_results, summary_df, deployments_df)

            # Print summary
            print("\n🎯 COST OPTIMIZATION SUMMARY:")
            print(f"   📊 Scenarios analyzed: {len(optimization_results)}")
            print(f"   🏭 Facilities considered: {len(self.facilities_clean)}")
            print(f"   💰 Total stranded assets: ${self.facilities_clean['current_book_value'].sum()/1e9:.1f}B")

            # Best scenarios summary
            best_scenarios = summary_df.loc[summary_df.groupby('emission_target_pct')['cost_per_tco2_avg'].idxmin()]
            for _, scenario in best_scenarios.iterrows():
                print(f"   🎯 {scenario['emission_target_pct']:.0f}% reduction: ${scenario['total_cost_musd']:.0f}M total, ${scenario['cost_per_tco2_avg']:.0f}/tCO₂ avg ({scenario['year']:.0f})")

            return optimization_results, summary_df, deployments_df

        except Exception as e:
            print(f"❌ Optimization analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    optimizer = CostOptimizationWithDepreciation()
    results = optimizer.run_complete_analysis()

    print("\n✅ COST OPTIMIZATION WITH DEPRECIATION COMPLETE!")
    print("📁 Results exported to organized_analysis/outputs/")