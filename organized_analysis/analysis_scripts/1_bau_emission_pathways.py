#!/usr/bin/env python3
"""
Script 1: BAU Emission Pathways with Facility Retirement Analysis
Generate Business-as-Usual emission projections based on facility retirement schedules
Operation years: 30, 40, 50 years facility lifetimes
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

    def calculate_retirement_schedule(self, lifetime_years):
        """Calculate when each facility retires based on lifetime"""
        retirement_data = []

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
                'age_at_retirement': lifetime_years
            })

        return pd.DataFrame(retirement_data)

    def generate_emission_pathways(self):
        """Generate BAU emission pathways for different facility lifetimes"""
        print("📈 Generating BAU emission pathways...")

        pathway_results = {}

        for lifetime in self.facility_lifetimes:
            print(f"   Calculating {lifetime}-year lifetime scenario...")

            # Get retirement schedule
            retirement_df = self.calculate_retirement_schedule(lifetime)

            # Calculate emissions for each year
            yearly_emissions = []

            for year in self.projection_years:
                # Facilities still operating in this year
                active_facilities = retirement_df[retirement_df['retirement_year'] > year]
                total_emissions = active_facilities['baseline_emissions_tco2'].sum()
                yearly_emissions.append(total_emissions / 1e6)  # Convert to MtCO2

            pathway_results[f'{lifetime}_year'] = {
                'years': self.projection_years,
                'emissions_mtco2': yearly_emissions,
                'retirement_schedule': retirement_df,
                'final_emissions_2050': yearly_emissions[-1],
                'reduction_from_baseline': 100 * (1 - yearly_emissions[-1] / yearly_emissions[0]) if yearly_emissions[0] > 0 else 0
            }

        return pathway_results

    def create_comprehensive_analysis(self, pathway_results):
        """Create comprehensive BAU analysis"""
        print("📊 Creating comprehensive BAU analysis...")

        # Retirement analysis by year
        retirement_by_year = {}
        for lifetime in self.facility_lifetimes:
            retirement_schedule = pathway_results[f'{lifetime}_year']['retirement_schedule']

            yearly_retirements = []
            for year in self.projection_years:
                retiring_facilities = retirement_schedule[retirement_schedule['retirement_year'] == year]
                retired_capacity = retiring_facilities['capacity_1000_t'].sum()
                retired_emissions = retiring_facilities['baseline_emissions_tco2'].sum() / 1e6
                yearly_retirements.append({
                    'year': year,
                    'retired_capacity_kt': retired_capacity,
                    'retired_emissions_mtco2': retired_emissions,
                    'facilities_retired': len(retiring_facilities)
                })

            retirement_by_year[f'{lifetime}_year'] = pd.DataFrame(yearly_retirements)

        # Company-level retirement analysis
        company_analysis = {}
        for lifetime in self.facility_lifetimes:
            retirement_schedule = pathway_results[f'{lifetime}_year']['retirement_schedule']

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

            company_analysis[f'{lifetime}_year'] = company_summary

        return retirement_by_year, company_analysis

    def create_visualizations(self, pathway_results, retirement_by_year):
        """Create comprehensive visualizations"""
        print("📊 Creating BAU pathway visualizations...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical BAU Emission Pathways\\nFacility Retirement Analysis (2025-2050)',
                    fontsize=16, fontweight='bold')

        # Plot 1: BAU Emission Pathways
        ax1 = axes[0, 0]
        colors = {'30_year': '#d62728', '40_year': '#ff7f0e', '50_year': '#2ca02c'}

        for lifetime_key, color in colors.items():
            pathway = pathway_results[lifetime_key]
            ax1.plot(pathway['years'], pathway['emissions_mtco2'],
                    color=color, linewidth=3, label=f'{lifetime_key.replace("_", "-")} lifetime',
                    marker='o', markersize=4)

        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO₂/year)')
        ax1.set_title('BAU Emission Pathways by Facility Lifetime')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(2025, 2050)

        # Add baseline reference line
        baseline_emissions = pathway_results['50_year']['emissions_mtco2'][0]
        ax1.axhline(y=baseline_emissions, color='black', linestyle='--', alpha=0.5, label=f'2025 Baseline: {baseline_emissions:.1f} Mt')

        # Plot 2: Cumulative Retirements
        ax2 = axes[0, 1]

        for lifetime_key, color in colors.items():
            retirement_data = retirement_by_year[lifetime_key]
            cumulative_retirements = retirement_data['retired_emissions_mtco2'].cumsum()
            ax2.plot(retirement_data['year'], cumulative_retirements,
                    color=color, linewidth=3, label=f'{lifetime_key.replace("_", "-")} lifetime')

        ax2.set_xlabel('Year')
        ax2.set_ylabel('Cumulative Retired Emissions (MtCO₂)')
        ax2.set_title('Cumulative Facility Retirements')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Annual Retirement Rates
        ax3 = axes[1, 0]

        years_subset = list(range(2025, 2051, 5))  # Every 5 years for clarity
        width = 0.8
        x_pos = np.arange(len(years_subset))

        for i, (lifetime_key, color) in enumerate(colors.items()):
            retirement_data = retirement_by_year[lifetime_key]
            retirement_subset = retirement_data[retirement_data['year'].isin(years_subset)]

            ax3.bar(x_pos + i*width/3 - width/3, retirement_subset['retired_emissions_mtco2'],
                   width/3, label=f'{lifetime_key.replace("_", "-")} lifetime',
                   color=color, alpha=0.7)

        ax3.set_xlabel('Year')
        ax3.set_ylabel('Annual Retired Emissions (MtCO₂)')
        ax3.set_title('Annual Retirement Rates (5-year intervals)')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(years_subset)
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Emission Reduction Summary
        ax4 = axes[1, 1]

        lifetimes = [30, 40, 50]
        final_emissions = [pathway_results[f'{lt}_year']['final_emissions_2050'] for lt in lifetimes]
        reduction_pcts = [pathway_results[f'{lt}_year']['reduction_from_baseline'] for lt in lifetimes]

        bars = ax4.bar(lifetimes, reduction_pcts, color=['#d62728', '#ff7f0e', '#2ca02c'], alpha=0.7)
        ax4.set_xlabel('Facility Lifetime (years)')
        ax4.set_ylabel('Emission Reduction by 2050 (%)')
        ax4.set_title('2050 Emission Reduction by Lifetime Scenario')
        ax4.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, reduction in zip(bars, reduction_pcts):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{reduction:.1f}%', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        # Save visualization
        output_path = Path("../outputs/bau_emission_pathways_retirement_analysis.png")
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {output_path}")

        plt.show()

    def export_results(self, pathway_results, retirement_by_year, company_analysis):
        """Export comprehensive results"""
        print("💾 Exporting BAU pathway results...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export pathway summary
        summary_data = []
        for lifetime_key, pathway in pathway_results.items():
            summary_data.append({
                'scenario': lifetime_key.replace('_', '-'),
                'baseline_2025_mtco2': pathway['emissions_mtco2'][0],
                'final_2050_mtco2': pathway['final_emissions_2050'],
                'reduction_percentage': pathway['reduction_from_baseline'],
                'total_facilities': len(pathway['retirement_schedule'])
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / "bau_pathway_summary.csv", index=False)

        # Export detailed yearly pathways
        pathway_detailed = pd.DataFrame({
            'year': self.projection_years,
            '30_year_emissions_mtco2': pathway_results['30_year']['emissions_mtco2'],
            '40_year_emissions_mtco2': pathway_results['40_year']['emissions_mtco2'],
            '50_year_emissions_mtco2': pathway_results['50_year']['emissions_mtco2']
        })
        pathway_detailed.to_csv(output_dir / "bau_detailed_pathways.csv", index=False)

        # Export retirement schedules
        for lifetime_key, pathway in pathway_results.items():
            retirement_schedule = pathway['retirement_schedule']
            retirement_schedule.to_csv(
                output_dir / f"retirement_schedule_{lifetime_key}.csv", index=False)

        # Export retirement by year analysis
        for lifetime_key, retirement_data in retirement_by_year.items():
            retirement_data.to_csv(
                output_dir / f"annual_retirements_{lifetime_key}.csv", index=False)

        # Export company analysis
        with pd.ExcelWriter(output_dir / "bau_company_analysis.xlsx") as writer:
            for lifetime_key, company_data in company_analysis.items():
                company_data.to_excel(writer, sheet_name=f'Companies_{lifetime_key}')

        print(f"   Exported results to: {output_dir}")

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
            print(f"   📊 Baseline emissions (2025): {pathway_results['50_year']['emissions_mtco2'][0]:.1f} MtCO₂")
            print(f"   🏭 Total facilities analyzed: {len(self.facilities_df)}")

            for lifetime in self.facility_lifetimes:
                pathway = pathway_results[f'{lifetime}_year']
                print(f"   📉 {lifetime}-year lifetime: {pathway['final_emissions_2050']:.1f} MtCO₂ in 2050 ({pathway['reduction_from_baseline']:.1f}% reduction)")

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