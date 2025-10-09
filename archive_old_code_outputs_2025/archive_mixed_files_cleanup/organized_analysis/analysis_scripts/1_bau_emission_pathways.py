#!/usr/bin/env python3
"""
Script 1: BAU Emission Pathways with Facility Retirement and Growth Scenarios Analysis
Generate Business-as-Usual emission projections based on:
- Facility retirement schedules: 30, 40, 50 years facility lifetimes
- Capacity growth scenarios: +0.2%, 0.0%, -0.2% annual growth rates
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

class BAUEmissionPathwayAnalyzer:
    def __init__(self):
        """Initialize with English Excel file"""
        self.excel_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.baseline_year = 2025
        self.projection_years = list(range(2025, 2051))  # 2025-2050
        self.facility_lifetimes = [30, 40, 50]  # Years

        # Growth rate scenarios (annual rates)
        self.growth_scenarios = {
            'positive_growth': {'rate': 0.002, 'name': '+0.2% Growth'},  # +0.2% per year
            'zero_growth': {'rate': 0.0, 'name': 'Zero Growth'},         # 0.0% per year
            'negative_growth': {'rate': -0.002, 'name': '-0.2% Growth'}  # -0.2% per year
        }

        # Load data
        self.load_facility_data()

    def load_facility_data(self):
        """Load and prepare facility data"""
        print("📊 Loading facility data from English Excel file...")

        try:
            # Load facility data
            self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')

            # Load consumption intensities and emission factors
            self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
            self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)

            print(f"   Loaded {len(self.facilities_df)} facilities")
            print(f"   CI data: {self.ci_df.shape}")
            print(f"   Emission factors: {self.ci2_df.shape}")

            # Clean and prepare data
            self.prepare_facility_data()

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

    def prepare_facility_data(self):
        """Clean and prepare facility data for analysis"""
        print("🔧 Preparing facility data...")

        # Remove invalid entries
        initial_count = len(self.facilities_df)
        self.facilities_df = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_df = self.facilities_df[self.facilities_df['capacity_1000_t'] > 0]
        self.facilities_df = self.facilities_df[self.facilities_df['year'] > 1900]

        # Calculate facility characteristics
        self.facilities_df['age_2025'] = 2025 - self.facilities_df['year']
        self.facilities_df['capacity_t'] = self.facilities_df['capacity_1000_t'] * 1000

        # Map process types to products for emission calculation
        process_mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam',
            'Aromatics': 'Benzene',
            'Olefins': 'Ethylene'
        }

        self.facilities_df['product'] = self.facilities_df['process'].map(process_mapping)
        self.facilities_df['product'] = self.facilities_df['product'].fillna('Ethylene')

        # Calculate baseline emissions for each facility
        self.calculate_facility_emissions()

        # Remove facilities with zero emissions
        self.facilities_df = self.facilities_df[self.facilities_df['baseline_emissions_tco2'] > 0]

        print(f"   Cleaned: {initial_count} → {len(self.facilities_df)} facilities")
        print(f"   Total baseline emissions: {self.facilities_df['baseline_emissions_tco2'].sum()/1e6:.1f} MtCO₂")

    def calculate_facility_emissions(self):
        """Calculate baseline emissions for each facility"""
        print("⚡ Calculating facility baseline emissions...")

        # Get emission factors
        emission_factors = {col: self.ci2_df.iloc[0][col] for col in self.ci2_df.columns}

        baseline_emissions = []

        for idx, facility in self.facilities_df.iterrows():
            product = facility['product']
            capacity = facility['capacity_t']

            if product not in self.ci_df.index:
                baseline_emissions.append(0)
                continue

            product_row = self.ci_df.loc[product]
            facility_emission = 0

            # Calculate emissions from each fuel/feedstock source
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

            baseline_emissions.append(facility_emission)

        self.facilities_df['baseline_emissions_tco2'] = baseline_emissions

    def calculate_retirement_schedule(self, lifetime_years, growth_scenario_key):
        """Calculate when each facility retires based on lifetime and apply growth scenario"""
        retirement_data = []
        growth_rate = self.growth_scenarios[growth_scenario_key]['rate']

        for idx, facility in self.facilities_df.iterrows():
            startup_year = facility['year']
            retirement_year = startup_year + lifetime_years

            # If facility is already beyond retirement age in 2025, it retires immediately
            if retirement_year <= 2025:
                retirement_year = 2025

            retirement_data.append({
                'facility_id': idx,
                'company': facility['company'],
                'location': facility.get('location', 'Unknown'),
                'process': facility['process'],
                'capacity_1000_t': facility['capacity_1000_t'],
                'startup_year': startup_year,
                'retirement_year': retirement_year,
                'baseline_emissions_tco2': facility['baseline_emissions_tco2'],
                'age_at_retirement': lifetime_years,
                'growth_rate': growth_rate
            })

        return pd.DataFrame(retirement_data)

    def generate_emission_pathways(self):
        """Generate BAU emission pathways for different facility lifetimes and growth scenarios"""
        print("📈 Generating BAU emission pathways with growth scenarios...")

        pathway_results = {}

        for growth_key, growth_data in self.growth_scenarios.items():
            growth_name = growth_data['name']
            growth_rate = growth_data['rate']

            print(f"   Processing {growth_name} scenario...")

            for lifetime in self.facility_lifetimes:
                scenario_key = f'{growth_key}_{lifetime}year'
                print(f"     {lifetime}-year lifetime with {growth_name}...")

                # Get retirement schedule for this growth scenario
                retirement_df = self.calculate_retirement_schedule(lifetime, growth_key)

                # Calculate emissions for each year with capacity growth
                yearly_emissions = []

                for year in self.projection_years:
                    years_elapsed = year - self.baseline_year
                    growth_factor = (1 + growth_rate) ** years_elapsed

                    # Facilities still operating in this year
                    active_facilities = retirement_df[retirement_df['retirement_year'] > year].copy()

                    if len(active_facilities) > 0:
                        # Apply growth factor to emissions
                        adjusted_emissions = active_facilities['baseline_emissions_tco2'] * growth_factor
                        total_emissions = adjusted_emissions.sum()
                    else:
                        total_emissions = 0

                    yearly_emissions.append(total_emissions / 1e6)  # Convert to MtCO2

                pathway_results[scenario_key] = {
                    'years': self.projection_years,
                    'emissions_mtco2': yearly_emissions,
                    'retirement_schedule': retirement_df,
                    'growth_scenario': growth_key,
                    'growth_rate': growth_rate,
                    'growth_name': growth_name,
                    'lifetime': lifetime,
                    'final_emissions_2050': yearly_emissions[-1] if yearly_emissions else 0,
                    'reduction_from_baseline': 100 * (1 - yearly_emissions[-1] / yearly_emissions[0]) if yearly_emissions and yearly_emissions[0] > 0 else 0
                }

        return pathway_results

    def create_comprehensive_analysis(self, pathway_results):
        """Create comprehensive BAU analysis with growth scenarios"""
        print("📊 Creating comprehensive BAU analysis with growth scenarios...")

        # Retirement analysis by year and growth scenario
        retirement_by_year = {}
        company_analysis = {}

        for scenario_key, pathway_data in pathway_results.items():
            retirement_schedule = pathway_data['retirement_schedule']
            growth_rate = pathway_data['growth_rate']

            # Yearly retirement analysis
            yearly_retirements = []
            for year in self.projection_years:
                years_elapsed = year - self.baseline_year
                growth_factor = (1 + growth_rate) ** years_elapsed

                retiring_facilities = retirement_schedule[retirement_schedule['retirement_year'] == year]
                retired_capacity = retiring_facilities['capacity_1000_t'].sum()
                retired_emissions = retiring_facilities['baseline_emissions_tco2'].sum() / 1e6

                yearly_retirements.append({
                    'year': year,
                    'retired_capacity_kt': retired_capacity,
                    'retired_emissions_mtco2': retired_emissions,
                    'adjusted_retired_emissions_mtco2': retired_emissions * growth_factor,
                    'facilities_retired': len(retiring_facilities),
                    'growth_factor': growth_factor
                })

            retirement_by_year[scenario_key] = pd.DataFrame(yearly_retirements)

            # Company-level retirement analysis
            company_summary = retirement_schedule.groupby('company').agg({
                'capacity_1000_t': 'sum',
                'baseline_emissions_tco2': 'sum',
                'retirement_year': ['min', 'max', 'mean'],
                'facility_id': 'count'
            }).round(2)

            company_summary.columns = ['total_capacity_kt', 'total_emissions_tco2',
                                     'first_retirement', 'last_retirement', 'avg_retirement', 'facility_count']
            company_summary['total_emissions_mtco2'] = company_summary['total_emissions_tco2'] / 1e6
            company_summary = company_summary.sort_values('total_emissions_mtco2', ascending=False)

            company_analysis[scenario_key] = company_summary

        return retirement_by_year, company_analysis

    def create_visualizations(self, pathway_results, retirement_by_year):
        """Create comprehensive visualizations with growth scenarios"""
        print("📊 Creating BAU pathway visualizations with growth scenarios...")

        # Create comprehensive figure with growth scenarios
        fig, axes = plt.subplots(3, 3, figsize=(20, 16))
        fig.suptitle('Korean Petrochemical BAU Emission Pathways\nFacility Retirement Analysis with Growth Scenarios (2025-2050)',
                    fontsize=16, fontweight='bold')

        # Color schemes for growth scenarios and lifetimes
        growth_colors = {'positive_growth': '#e74c3c', 'zero_growth': '#2c3e50', 'negative_growth': '#27ae60'}
        lifetime_styles = {30: '-', 40: '--', 50: ':'}
        lifetime_markers = {30: 'o', 40: 's', 50: '^'}

        # Plot emission pathways for each growth scenario
        for i, (growth_key, growth_data) in enumerate(self.growth_scenarios.items()):
            ax = axes[0, i]
            growth_name = growth_data['name']

            # Plot all lifetime scenarios for this growth rate
            for lifetime in self.facility_lifetimes:
                scenario_key = f'{growth_key}_{lifetime}year'
                if scenario_key in pathway_results:
                    pathway = pathway_results[scenario_key]
                    ax.plot(pathway['years'], pathway['emissions_mtco2'],
                           color=growth_colors[growth_key], linestyle=lifetime_styles[lifetime],
                           marker=lifetime_markers[lifetime], linewidth=2, markersize=4,
                           label=f'{lifetime}-year lifetime')

            ax.set_xlabel('Year')
            ax.set_ylabel('Emissions (MtCO₂/year)')
            ax.set_title(f'{growth_name}\nEmission Pathways')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xlim(2025, 2050)

        # Comparison plots - all scenarios on one chart
        ax_comp = axes[1, :]
        ax_comp = plt.subplot2grid((3, 3), (1, 0), colspan=3)

        for growth_key, growth_data in self.growth_scenarios.items():
            for lifetime in self.facility_lifetimes:
                scenario_key = f'{growth_key}_{lifetime}year'
                if scenario_key in pathway_results:
                    pathway = pathway_results[scenario_key]
                    label = f'{growth_data["name"]} ({lifetime}yr)'
                    ax_comp.plot(pathway['years'], pathway['emissions_mtco2'],
                               color=growth_colors[growth_key], linestyle=lifetime_styles[lifetime],
                               marker=lifetime_markers[lifetime], linewidth=2, markersize=3,
                               label=label, alpha=0.8)

        ax_comp.set_xlabel('Year')
        ax_comp.set_ylabel('Emissions (MtCO₂/year)')
        ax_comp.set_title('All Growth & Lifetime Scenarios Comparison')
        ax_comp.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax_comp.grid(True, alpha=0.3)
        ax_comp.set_xlim(2025, 2050)

        # Summary bar charts for 2050 emissions
        for i, (growth_key, growth_data) in enumerate(self.growth_scenarios.items()):
            ax = axes[2, i]
            lifetimes = []
            final_emissions = []
            reduction_pcts = []

            for lifetime in self.facility_lifetimes:
                scenario_key = f'{growth_key}_{lifetime}year'
                if scenario_key in pathway_results:
                    pathway = pathway_results[scenario_key]
                    lifetimes.append(lifetime)
                    final_emissions.append(pathway['final_emissions_2050'])
                    reduction_pcts.append(pathway.get('reduction_from_baseline', 0))

            if lifetimes:
                bars = ax.bar(lifetimes, final_emissions, color=growth_colors[growth_key], alpha=0.7,
                             width=5)
                ax.set_xlabel('Facility Lifetime (years)')
                ax.set_ylabel('2050 Emissions (MtCO₂)')
                ax.set_title(f'{growth_data["name"]}\n2050 Final Emissions')
                ax.grid(True, alpha=0.3)

                # Add value labels on bars
                for bar, emission in zip(bars, final_emissions):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{emission:.1f}', ha='center', va='bottom', fontweight='bold',
                           fontsize=9)

        plt.tight_layout()

        # Save visualization
        output_path = Path("../outputs/bau_emission_pathways_with_growth_scenarios.png")
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {output_path}")

        plt.show()

    def export_results(self, pathway_results, retirement_by_year, company_analysis):
        """Export comprehensive results with growth scenarios"""
        print("💾 Exporting BAU pathway results with growth scenarios...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export pathway summary with growth scenarios
        summary_data = []
        for scenario_key, pathway in pathway_results.items():
            summary_data.append({
                'scenario': scenario_key,
                'growth_scenario': pathway['growth_name'],
                'growth_rate': pathway['growth_rate'],
                'facility_lifetime': pathway['lifetime'],
                'baseline_2025_mtco2': pathway['emissions_mtco2'][0],
                'final_2050_mtco2': pathway['final_emissions_2050'],
                'reduction_percentage': pathway['reduction_from_baseline'],
                'total_facilities': len(pathway['retirement_schedule'])
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / "bau_pathway_summary_with_growth.csv", index=False)

        # Export detailed yearly pathways for all scenarios
        pathway_detailed_data = {'year': self.projection_years}
        for scenario_key, pathway in pathway_results.items():
            pathway_detailed_data[f'{scenario_key}_emissions_mtco2'] = pathway['emissions_mtco2']

        pathway_detailed = pd.DataFrame(pathway_detailed_data)
        pathway_detailed.to_csv(output_dir / "bau_detailed_pathways_with_growth.csv", index=False)

        # Export growth scenario comparison (just 50-year lifetime for simplicity)
        growth_comparison_data = {'year': self.projection_years}
        for growth_key, growth_data in self.growth_scenarios.items():
            scenario_key = f'{growth_key}_50year'
            if scenario_key in pathway_results:
                growth_comparison_data[f'{growth_data["name"]}_mtco2'] = pathway_results[scenario_key]['emissions_mtco2']

        growth_comparison_df = pd.DataFrame(growth_comparison_data)
        growth_comparison_df.to_csv(output_dir / "growth_scenario_comparison_50yr.csv", index=False)

        # Export retirement schedules for each scenario
        for scenario_key, pathway in pathway_results.items():
            retirement_schedule = pathway['retirement_schedule']
            retirement_schedule.to_csv(
                output_dir / f"retirement_schedule_{scenario_key}.csv", index=False)

        # Export retirement by year analysis
        for scenario_key, retirement_data in retirement_by_year.items():
            retirement_data.to_csv(
                output_dir / f"annual_retirements_{scenario_key}.csv", index=False)

        # Export company analysis
        with pd.ExcelWriter(output_dir / "bau_company_analysis_with_growth.xlsx") as writer:
            for scenario_key, company_data in company_analysis.items():
                sheet_name = scenario_key[:31]  # Excel sheet name limit
                company_data.to_excel(writer, sheet_name=sheet_name)

        print(f"   Exported results to: {output_dir}")
        print(f"   📊 Summary: {len(pathway_results)} scenarios exported")
        print(f"   📈 Growth scenarios: {list(self.growth_scenarios.keys())}")
        print(f"   🏭 Facility lifetimes: {self.facility_lifetimes} years")

    def run_complete_analysis(self):
        """Run complete BAU emission pathway analysis"""
        print("🚀 BAU EMISSION PATHWAY ANALYSIS")
        print("=" * 80)
        print("📊 Facility retirement scenarios: 30, 40, 50 year lifetimes")
        print("📈 Projection period: 2025-2050")
        print()

        try:
            # Generate pathways
            pathway_results = self.generate_emission_pathways()

            # Create comprehensive analysis
            retirement_by_year, company_analysis = self.create_comprehensive_analysis(pathway_results)

            # Create visualizations
            self.create_visualizations(pathway_results, retirement_by_year)

            # Export results
            self.export_results(pathway_results, retirement_by_year, company_analysis)

            # Print summary
            print("\n🎯 BAU PATHWAY ANALYSIS SUMMARY:")

            # Get baseline from zero growth, 50-year scenario
            baseline_scenario = 'zero_growth_50year'
            if baseline_scenario in pathway_results:
                baseline_emissions = pathway_results[baseline_scenario]['emissions_mtco2'][0]
                print(f"   📊 Baseline emissions (2025): {baseline_emissions:.1f} MtCO₂")
            print(f"   🏭 Total facilities analyzed: {len(self.facilities_df)}")
            print(f"   📈 Growth scenarios: {len(self.growth_scenarios)}")
            print(f"   🏗️ Facility lifetimes: {len(self.facility_lifetimes)}")
            print(f"   🎯 Total scenarios analyzed: {len(pathway_results)}")

            print("\n📉 2050 EMISSIONS BY SCENARIO:")
            for growth_key, growth_data in self.growth_scenarios.items():
                print(f"\n   {growth_data['name']} ({growth_data['rate']*100:+.1f}% annually):")
                for lifetime in self.facility_lifetimes:
                    scenario_key = f'{growth_key}_{lifetime}year'
                    if scenario_key in pathway_results:
                        pathway = pathway_results[scenario_key]
                        print(f"     {lifetime}-year lifetime: {pathway['final_emissions_2050']:.1f} MtCO₂")

            return pathway_results

        except Exception as e:
            print(f"❌ BAU analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    analyzer = BAUEmissionPathwayAnalyzer()
    results = analyzer.run_complete_analysis()

    print("\n✅ BAU EMISSION PATHWAY ANALYSIS COMPLETE!")
    print("📁 Results exported to organized_analysis/outputs/")